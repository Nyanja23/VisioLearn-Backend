from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, models
from ..database import get_db
from ..dependencies import require_admin

router = APIRouter(prefix="/api/v1/schools", tags=["schools"])

@router.post("/", response_model=schemas.SchoolResponse, status_code=status.HTTP_201_CREATED)
def create_school(
    school: schemas.SchoolCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Create a new school. Requires admin authentication.
    """
    db_school = models.School(
        name=school.name,
        region=school.region
    )
    
    db.add(db_school)
    try:
        db.commit()
        db.refresh(db_school)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create school"
        )
    
    return db_school

@router.get("/", response_model=dict)
def list_schools(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    List all schools. Requires admin authentication.
    """
    schools = db.query(models.School).filter(
        models.School.is_deleted == False
    ).offset(skip).limit(limit).all()
    
    total = db.query(models.School).filter(
        models.School.is_deleted == False
    ).count()
    
    return {
        "schools": schools,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{school_id}", response_model=schemas.SchoolResponse)
def get_school(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Get school details. Requires admin authentication.
    """
    school = db.query(models.School).filter(
        models.School.id == school_id,
        models.School.is_deleted == False
    ).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    return school

@router.put("/{school_id}", response_model=schemas.SchoolResponse)
def update_school(
    school_id: UUID,
    school_update: schemas.SchoolCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Update school details. Requires admin authentication.
    """
    school = db.query(models.School).filter(
        models.School.id == school_id,
        models.School.is_deleted == False
    ).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    school.name = school_update.name
    school.region = school_update.region
    
    try:
        db.commit()
        db.refresh(school)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update school"
        )
    
    return school

@router.delete("/{school_id}")
def delete_school(
    school_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Soft delete a school. Requires admin authentication.
    """
    school = db.query(models.School).filter(
        models.School.id == school_id,
        models.School.is_deleted == False
    ).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    school.is_deleted = True
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete school"
        )
    
    return {"message": "School deleted successfully"}
