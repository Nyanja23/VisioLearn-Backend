from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, models
from ..database import get_db
from ..dependencies import require_admin

router = APIRouter(prefix="/api/v1/schools", tags=["schools"])

@router.get("/public", response_model=dict)
def list_schools_public(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Deprecated: Schools model has been removed. 
    Use /api/v1/auth/register/teacher to create a teacher class instead.
    Teachers automatically get a unique class code for students to join.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated. Use teacher registration with auto-generated class codes instead."
    )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_school(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deprecated: Schools model has been removed.
    Teachers now manage their own classes with auto-generated class codes.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated. Teachers auto-generate class codes upon registration."
    )

@router.get("/", response_model=dict)
def list_schools(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deprecated: Schools model has been removed.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated."
    )

@router.get("/{school_id}", response_model=dict)
def get_school(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deprecated: Schools model has been removed.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated."
    )

@router.put("/{school_id}", response_model=dict)
def update_school(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deprecated: Schools model has been removed.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated."
    )

@router.delete("/{school_id}")
def delete_school(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deprecated: Schools model has been removed.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Schools endpoint deprecated."
    )
