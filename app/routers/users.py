from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models, security
from ..database import get_db
from ..dependencies import require_admin, get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/bootstrap", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create the first admin account. Only works when no users exist in the database.
    This endpoint is for initial system setup only.
    """
    # Check if any users exist
    existing_users = db.query(models.User).first()
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap not allowed - users already exist. Use POST /users with admin authentication."
        )
    
    # Force role to admin for bootstrap
    normalized_email = user.email.lower()
    hashed_password = security.get_password_hash(user.password)
    
    db_user = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="admin",  # Force admin role for bootstrap
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
            detail="Failed to create user. Please try again."
        )
    
    return db_user

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Create a new user. Requires admin authentication.
    """
    # Normalize email to lowercase
    normalized_email = user.email.lower()
    
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = security.get_password_hash(user.password)
    
    db_user = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role=user.role,
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
            detail="Failed to create user. Please try again."
        )
    
    return db_user
