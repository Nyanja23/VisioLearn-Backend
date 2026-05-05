"""
Progress Tracking Router - Student content engagement tracking

Tracks when students play audio notes, their progress, and completion status.
Teachers can view their students' progress summaries.
Students can view their own progress reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user, require_student, require_teacher

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])


@router.post(
    "",
    response_model=schemas.ContentProgressResponse,
    status_code=status.HTTP_201_CREATED
)
def log_progress(
    progress: schemas.ContentProgressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student)
):
    """
    Log student's progress on a content item.
    
    Called when student plays/listens to a lesson note.
    Tracks: position, completion status, and timestamps.
    
    Args:
        progress: ContentProgressCreate with note_id, position, completed flag
        
    Returns:
        ContentProgressResponse with updated progress record
        
    Raises:
        404: Note not found or not accessible to student
        403: Student trying to access another student's notes
    """
    
    # Verify note exists and belongs to student's teacher
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == progress.note_id,
        models.LessonNote.is_deleted == False
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Verify student's teacher matches note's teacher
    if current_user.teacher_id != note.teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This content is not available to you"
        )
    
    # Check if progress record exists
    existing = db.query(models.ContentProgress).filter(
        models.ContentProgress.student_id == current_user.id,
        models.ContentProgress.note_id == progress.note_id
    ).first()
    
    if existing:
        # Update existing progress record
        existing.last_position_seconds = progress.last_position_seconds
        existing.completed = progress.completed
        existing.updated_at = datetime.utcnow()
        
        # Calculate completion percentage
        # (assume average note length is ~1800 seconds = 30 minutes)
        if existing.last_position_seconds > 0:
            existing.completion_percentage = min(
                100.0,
                (existing.last_position_seconds / 1800.0) * 100
            )
        
        db_progress = existing
    else:
        # Create new progress record
        db_progress = models.ContentProgress(
            student_id=current_user.id,
            note_id=progress.note_id,
            started_at=datetime.utcnow(),
            last_position_seconds=progress.last_position_seconds,
            completed=progress.completed,
            completion_percentage=min(
                100.0,
                (progress.last_position_seconds / 1800.0) * 100
            ) if progress.last_position_seconds > 0 else 0.0
        )
        db.add(db_progress)
    
    try:
        db.commit()
        db.refresh(db_progress)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save progress"
        )
    
    return db_progress


@router.get("/me", response_model=schemas.StudentProgressSummary)
def get_my_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student)
):
    """
    Get student's overall progress summary.
    
    Shows: total notes accessed, completed notes count, average completion %.
    
    Returns:
        StudentProgressSummary with aggregate statistics
    """
    
    # Count total notes from student's teacher
    total_notes = db.query(models.LessonNote).filter(
        models.LessonNote.teacher_id == current_user.teacher_id,
        models.LessonNote.is_deleted == False
    ).count()
    
    # Get student's progress records
    progress_records = db.query(models.ContentProgress).filter(
        models.ContentProgress.student_id == current_user.id
    ).all()
    
    # Calculate statistics
    completed_count = sum(1 for p in progress_records if p.completed)
    avg_completion = (
        sum(p.completion_percentage for p in progress_records) / len(progress_records)
        if progress_records
        else 0.0
    )
    
    last_updated = (
        max(p.updated_at for p in progress_records)
        if progress_records
        else None
    )
    
    return schemas.StudentProgressSummary(
        total_notes=total_notes,
        completed_notes=completed_count,
        avg_completion_percentage=avg_completion,
        last_updated=last_updated
    )


@router.get("/students", response_model=List[schemas.TeacherStudentSummary])
def get_teacher_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """
    Get list of students enrolled in teacher's class.
    
    Returns student info and progress statistics for each student.
    
    Only teachers can access this endpoint.
    
    Returns:
        List of TeacherStudentSummary objects for each student
    """
    
    # Get all students linked to this teacher
    students = db.query(models.User).filter(
        models.User.teacher_id == current_user.id,
        models.User.role == "student",
        models.User.is_deleted == False
    ).all()
    
    result = []
    
    for student in students:
        # Get student's progress records
        progress_records = db.query(models.ContentProgress).filter(
            models.ContentProgress.student_id == student.id
        ).all()
        
        # Calculate statistics
        total_accessed = len(progress_records)
        avg_completion = (
            sum(p.completion_percentage for p in progress_records) / total_accessed
            if progress_records
            else 0.0
        )
        last_access = (
            max(p.updated_at for p in progress_records)
            if progress_records
            else None
        )
        
        result.append(schemas.TeacherStudentSummary(
            id=student.id,
            full_name=student.full_name,
            email=student.email,
            total_content_accessed=total_accessed,
            avg_completion_percentage=avg_completion,
            last_access=last_access
        ))
    
    return result


@router.get("/students/{student_id}", response_model=List[schemas.ContentProgressResponse])
def get_student_progress_details(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """
    Get detailed progress records for a specific student.
    
    Shows all content accessed by student with completion details.
    
    Args:
        student_id: UUID of the student
        
    Returns:
        List of ContentProgressResponse objects
        
    Raises:
        404: Student not found or not in teacher's class
        403: Teacher trying to access another teacher's students
    """
    
    # Verify student exists and belongs to this teacher
    student = db.query(models.User).filter(
        models.User.id == student_id,
        models.User.role == "student",
        models.User.teacher_id == current_user.id,
        models.User.is_deleted == False
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or not in your class"
        )
    
    # Get all progress records for this student
    progress_records = db.query(models.ContentProgress).filter(
        models.ContentProgress.student_id == student_id
    ).order_by(models.ContentProgress.updated_at.desc()).all()
    
    return progress_records
