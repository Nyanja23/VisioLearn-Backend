from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta
import jwt

from .. import schemas, models, security
from ..database import get_db
from ..dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    Public registration endpoint for teachers and students.
    Admin accounts cannot be created via this endpoint.
    Requires valid school_id.
    """
    # Normalize email to lowercase
    normalized_email = user.email.lower()
    
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate school exists and is not deleted
    school = db.query(models.School).filter(
        and_(
            models.School.id == user.school_id,
            models.School.is_deleted == False
        )
    ).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School not found or has been deactivated"
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create user (role is already restricted to teacher|student by schema)
    db_user = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role=user.role,
        school_id=user.school_id,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again."
        )
    
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Normalize email to lowercase for case-insensitive comparison
    normalized_email = request.email.lower()
    user = db.query(models.User).filter(models.User.email == normalized_email).first()
    
    if not user or not security.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
        
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    
    access_token = security.create_access_token(subject=user.id, role=user.role)
    refresh_token = security.create_refresh_token(subject=user.id)
    
    # Store refresh token in DB with transaction handling
    db_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to store refresh token: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete login. Please try again."
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # Use SELECT FOR UPDATE to prevent race conditions during token rotation
    # Also check expires_at to ensure token hasn't expired in database
    db_token = db.query(models.RefreshToken).filter(
        and_(
            models.RefreshToken.token == request.refresh_token,
            models.RefreshToken.revoked == False,
            models.RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    ).with_for_update().first()
    
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked, expired, or not found")

    # Revoke old refresh token (Token rotation strategy)
    db_token.revoked = True
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
        
    access_token = security.create_access_token(subject=user.id, role=user.role)
    new_refresh_token = security.create_refresh_token(subject=user.id)
    
    # Store new token
    new_db_token = models.RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_db_token)
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token. Please try again."
        )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(request: schemas.RefreshRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Revoke the given refresh token (only if it belongs to current user)
    db_token = db.query(models.RefreshToken).filter(
        and_(
            models.RefreshToken.token == request.refresh_token,
            models.RefreshToken.user_id == current_user.id
        )
    ).first()
    
    if db_token:
        db_token.revoked = True
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout. Please try again."
            )
    
    return {"success": True, "message": "Successfully logged out"}


# ============================================================================
# TEMPORARY ADMIN CREATION ENDPOINT - FOR RENDER FREE TIER ONLY
# ============================================================================
# WARNING: This endpoint must be REMOVED or DISABLED after creating the admin!
# It bypasses normal authentication to allow initial admin setup on Render's
# free tier which has no shell access. 
# 
# To disable: Delete this endpoint or set ADMIN_SECRET=""
# ============================================================================

import os

@router.post("/internal/create-admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_admin_internal(
    email: str,
    password: str,
    secret: str,
    db: Session = Depends(get_db)
):
    """
    TEMPORARY INTERNAL ENDPOINT - Creates an admin user for initial setup.
    
    ⚠️ WARNING: This endpoint MUST be removed or disabled after first use!
    
    Protected by ADMIN_SECRET environment variable.
    
    Parameters:
    - email: Admin email address
    - password: Admin password (will be hashed with bcrypt)
    - secret: Must match ADMIN_SECRET environment variable
    
    Returns:
    - 201: Admin created successfully
    - 400: Admin already exists, or invalid parameters
    - 403: Invalid or missing secret
    - 500: Database error
    """
    
    # Get the secret from environment
    admin_secret = os.getenv("ADMIN_SECRET", "")
    
    # If no secret configured, endpoint is disabled
    if not admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin creation endpoint is disabled"
        )
    
    # Verify the provided secret matches
    if secret != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret"
        )
    
    # Validate inputs
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Normalize email
    normalized_email = email.lower().strip()
    
    # Check if email is valid
    if "@" not in normalized_email or "." not in normalized_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    try:
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == normalized_email
        ).first()
        
        if existing_user:
            return {
                "status": "exists",
                "message": "Admin user already exists",
                "email": existing_user.email,
                "role": existing_user.role
            }
        
        # Create new admin user
        admin_user = models.User(
            email=normalized_email,
            full_name="System Administrator",
            role="admin",
            hashed_password=security.get_password_hash(password),
            school_id=None
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return {
            "status": "created",
            "message": "Admin user created successfully",
            "email": admin_user.email,
            "role": admin_user.role,
            "id": str(admin_user.id),
            "warning": "DELETE OR DISABLE THIS ENDPOINT AFTER FIRST USE"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin: {str(e)}"
        )
