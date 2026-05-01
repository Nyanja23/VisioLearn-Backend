"""
Internal admin creation endpoint for Render free tier deployment.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from .. import schemas, models, security
from ..database import get_db

router = APIRouter(prefix="/internal", tags=["internal"])


class AdminCreationRequest(BaseModel):
    email: str
    password: str
    secret: str


@router.post("/create-admin", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_admin_internal(
    request: AdminCreationRequest,
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
    if request.secret != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret"
        )
    
    # Validate inputs
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Normalize email
    normalized_email = request.email.lower().strip()
    
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
            hashed_password=security.get_password_hash(request.password),
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
            detail=f"Error creating admin: {str(e)}"
        )
