from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta
import jwt

from .. import schemas, models, security
from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..utils import generate_class_code

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register/teacher", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_teacher(user: schemas.UserRegisterTeacher, db: Session = Depends(get_db)):
    """
    Teacher registration endpoint.
    Automatically generates a unique class code for the teacher.
    
    Request body:
    - email: Teacher's email address
    - full_name: Teacher's full name
    - password: Strong password (12+ chars, uppercase, lowercase, digit, special char)
    - role: Fixed to "teacher"
    
    Response:
    - User object with auto-generated class_code
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
    
    # Generate unique class code
    class_code = generate_class_code()
    
    # Ensure generated class code is unique (retry up to 5 times, highly unlikely to collide)
    max_retries = 5
    for attempt in range(max_retries):
        existing_code = db.query(models.User).filter(models.User.class_code == class_code).first()
        if not existing_code:
            break
        class_code = generate_class_code()
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique class code. Please try again."
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create teacher user
    db_teacher = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="teacher",
        class_code=class_code,
        hashed_password=hashed_password
    )
    
    db.add(db_teacher)
    try:
        db.commit()
        db.refresh(db_teacher)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create teacher account. Please try again."
        )
    
    return db_teacher

@router.post("/register/student", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(user: schemas.UserRegisterStudent, db: Session = Depends(get_db)):
    """
    Student registration endpoint.
    Links student to a teacher via the teacher's class code.
    
    Request body:
    - email: Student's email address
    - full_name: Student's full name
    - password: Strong password (12+ chars, uppercase, lowercase, digit, special char)
    - class_code: Valid teacher class code (format: XX-XXXX)
    - role: Fixed to "student"
    
    Response:
    - User object with teacher_id populated
    
    Errors:
    - 400: Email already registered
    - 400: Invalid class code (wrong format)
    - 404: Class code not found (teacher doesn't exist)
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
    
    # Validate class code format (XX-XXXX)
    if not user.class_code or len(user.class_code) != 7 or user.class_code[2] != '-':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid class code format. Expected format: XX-XXXX (e.g., AB-1234)"
        )
    
    # Find teacher with this class code
    teacher = db.query(models.User).filter(
        and_(
            models.User.class_code == user.class_code,
            models.User.role == "teacher",
            models.User.is_deleted == False
        )
    ).first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class code not found. Please verify the code with your teacher."
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create student user
    db_student = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="student",
        teacher_id=teacher.id,
        hashed_password=hashed_password
    )
    
    db.add(db_student)
    try:
        db.commit()
        db.refresh(db_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student account. Please try again."
        )
    
    return db_student

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
def register_legacy(user: schemas.UserRegisterTeacher, db: Session = Depends(get_db)):
    """
    Deprecated: Use /register/teacher or /register/student instead.
    This endpoint is kept for backward compatibility only.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint deprecated. Use /api/v1/auth/register/teacher or /api/v1/auth/register/student"
    )

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
