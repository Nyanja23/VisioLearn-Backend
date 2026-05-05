"""
Class Management Router

Endpoints for managing classes, subjects, and class memberships.
- Class teachers can create classes and manage subject teachers
- Subject teachers can join classes using teacher_code
- Students can view their class and subjects
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from uuid import UUID

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user, require_class_teacher, require_student, verify_class_teacher_owns_class, verify_student_in_class

router = APIRouter(prefix="/api/v1/classes", tags=["classes"])


@router.get("/{class_id}", response_model=schemas.ClassResponse)
def get_class_details(
    class_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get class details.
    Accessible to: class_teacher (owner), subject_teachers (if teaching in class), students (if member), admin
    """
    class_obj = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not class_obj or class_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Check access permissions
    if current_user.role == "admin":
        pass  # Admin can see all classes
    elif current_user.role == "class_teacher":
        if class_obj.class_teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this class"
            )
    elif current_user.role == "subject_teacher":
        # Check if user teaches any subject in this class
        subject = db.query(models.ClassSubject).filter(
            and_(
                models.ClassSubject.class_id == class_id,
                models.ClassSubject.subject_teacher_id == current_user.id
            )
        ).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this class"
            )
    elif current_user.role == "student":
        if not verify_student_in_class(class_id, current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this class"
            )
    
    return class_obj


@router.get("/{class_id}/subjects", response_model=List[schemas.ClassSubjectResponse])
def get_class_subjects(
    class_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all subjects in a class.
    Accessible to: class_teacher (owner), subject_teachers (if teaching in class), students (if member), admin
    """
    # First verify class exists and user has access
    class_obj = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not class_obj or class_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Check access permissions
    if current_user.role == "admin":
        pass
    elif current_user.role == "class_teacher":
        if class_obj.class_teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this class"
            )
    elif current_user.role == "subject_teacher":
        subject = db.query(models.ClassSubject).filter(
            and_(
                models.ClassSubject.class_id == class_id,
                models.ClassSubject.subject_teacher_id == current_user.id
            )
        ).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this class"
            )
    elif current_user.role == "student":
        if not verify_student_in_class(class_id, current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this class"
            )
    
    subjects = db.query(models.ClassSubject).filter(
        models.ClassSubject.class_id == class_id
    ).all()
    
    return subjects


@router.post("/{class_id}/subjects", response_model=schemas.ClassSubjectResponse, status_code=status.HTTP_201_CREATED)
def add_subject_to_class(
    class_id: UUID,
    subject_data: dict,  # Will accept subject_name and subject_teacher_id
    current_user: models.User = Depends(require_class_teacher),
    db: Session = Depends(get_db)
):
    """
    Add a subject (and its teacher) to a class.
    Only the class teacher can add subjects.
    
    Note: A subject_teacher can teach multiple subjects in the same class.
    """
    # Verify class exists and user owns it
    if not verify_class_teacher_owns_class(class_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to manage this class"
        )
    
    class_obj = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not class_obj or class_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # The subject_teacher should already exist and be a subject_teacher role
    # This is typically called after a subject_teacher has already registered
    # For now, we expect subject_teacher_id to be provided
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Subject assignment endpoint under development. Subject teachers are automatically assigned during registration."
    )


@router.get("/{class_id}/students", response_model=List[dict])
def get_class_students(
    class_id: UUID,
    current_user: models.User = Depends(require_class_teacher),
    db: Session = Depends(get_db)
):
    """
    Get all students in a class (class_teacher only).
    Returns list of students with basic info.
    """
    # Verify class exists and user owns it
    if not verify_class_teacher_owns_class(class_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this class"
        )
    
    # Get all memberships for this class
    memberships = db.query(models.ClassMembership).filter(
        and_(
            models.ClassMembership.class_id == class_id,
            models.ClassMembership.left_at == None  # Only active members
        )
    ).all()
    
    # Build response with student info
    students = []
    for membership in memberships:
        students.append({
            "id": membership.student_id,
            "email": membership.student.email,
            "full_name": membership.student.full_name,
            "joined_at": membership.joined_at
        })
    
    return students


@router.get("/{class_id}/matrix")
def get_class_progress_matrix(
    class_id: UUID,
    current_user: models.User = Depends(require_class_teacher),
    db: Session = Depends(get_db)
):
    """
    Get matrix view of student progress across all subjects in the class.
    Rows: Students in class
    Columns: Subjects in class
    Values: Completion percentage for each student-subject combination
    
    Only class_teacher can access (they manage the class).
    """
    # Verify class exists and user owns it
    if not verify_class_teacher_owns_class(class_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this class"
        )
    
    # Get all students in class
    memberships = db.query(models.ClassMembership).filter(
        and_(
            models.ClassMembership.class_id == class_id,
            models.ClassMembership.left_at == None
        )
    ).all()
    
    student_ids = [m.student_id for m in memberships]
    
    # Get all subjects in class
    subjects = db.query(models.ClassSubject).filter(
        models.ClassSubject.class_id == class_id
    ).all()
    
    # Build matrix
    matrix = {
        "class_id": class_id,
        "class_name": db.query(models.Class).filter(models.Class.id == class_id).first().class_name,
        "subjects": [{"id": str(s.id), "name": s.subject_name} for s in subjects],
        "students": []
    }
    
    for membership in memberships:
        student_data = {
            "id": str(membership.student_id),
            "email": membership.student.email,
            "full_name": membership.student.full_name,
            "progress_by_subject": {}
        }
        
        # Get progress for each subject
        for subject in subjects:
            # Calculate average completion percentage for this student-subject
            progress_records = db.query(models.ContentProgress).filter(
                and_(
                    models.ContentProgress.student_id == membership.student_id,
                    models.ContentProgress.subject_id == subject.id,
                    models.ContentProgress.class_id == class_id
                )
            ).all()
            
            if progress_records:
                avg_completion = sum(p.completion_percentage for p in progress_records) / len(progress_records)
                completed_count = sum(1 for p in progress_records if p.completed)
            else:
                avg_completion = 0
                completed_count = 0
            
            student_data["progress_by_subject"][str(subject.id)] = {
                "subject_name": subject.subject_name,
                "completion_percentage": avg_completion,
                "items_completed": completed_count,
                "total_items": len(progress_records)
            }
        
        matrix["students"].append(student_data)
    
    return matrix
