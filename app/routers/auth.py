from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta
import jwt

from .. import schemas, models, security
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

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
    except Exception:
        db.rollback()
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
