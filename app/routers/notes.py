"""
Lesson Notes Router - File Upload & Management

Implements PRD Section 6.2 endpoints for lesson note management.
Teachers can upload lesson content (PDF, DOCX, TXT) for processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from .. import models, schemas, security
from ..database import get_db
from ..dependencies import get_current_user, require_teacher
from ..storage import FileManager, FileStorageError

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.post(
    "/upload",
    response_model=schemas.LessonNoteResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_lesson_note(
    file: UploadFile = File(...),
    title: str = None,
    subject_id: str = None,  # Now requires class subject ID
    grade_level: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """
    Upload a lesson note file (PDF, DOCX, or TXT) for a specific class+subject.
    
    Only subject_teachers can upload files.
    File will be validated, stored, and queued for async processing.
    
    Args:
        file: The lesson file (PDF, DOCX, or TXT)
        title: Lesson title
        subject_id: UUID of the ClassSubject (required)
        grade_level: Target grade level
        
    Returns:
        LessonNoteResponse with upload status
    """
    
    # Validate subject_id is provided
    if not subject_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="subject_id (ClassSubject UUID) is required"
        )
    
    # Get the ClassSubject to verify it exists and user teaches it
    try:
        class_subject = db.query(models.ClassSubject).filter(
            models.ClassSubject.id == UUID(subject_id)
        ).first()
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subject_id format. Must be a valid UUID."
        )
    
    if not class_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Verify current user is the subject teacher for this subject
    if current_user.role == "subject_teacher" and class_subject.subject_teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload content for this subject"
        )
    
    # Use filename as title if not provided
    if not title:
        title = file.filename.replace(".pdf", "").replace(".docx", "").replace(".txt", "")
    
    if not grade_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade level is required"
        )
    
    # Create LessonNote record with class and subject IDs
    note_id = models.uuid.uuid4()
    
    db_note = models.LessonNote(
        id=note_id,
        class_id=class_subject.class_id,
        subject_id=class_subject.id,
        teacher_id=current_user.id,
        title=title,
        subject=class_subject.subject_name,  # Use actual subject name
        grade_level=grade_level,
        original_file_name=file.filename,
        status="PENDING_PROCESSING"
    )
    
    # Save file to disk
    try:
        file_path = await FileManager.save_upload_file(file, str(note_id))
        db_note.file_url = file_path
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File storage error: {str(e)}"
        )
    
    # Save to database
    db.add(db_note)
    try:
        db.commit()
        db.refresh(db_note)
    except Exception as e:
        db.rollback()
        # Try to cleanup file
        try:
            FileManager.delete_file(file_path)
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lesson note record"
        )
    
    # Queue async processing task with Celery
    from ..tasks.process_note import process_note_task
    process_note_task.delay(str(note_id))
    
    return db_note



@router.get("", response_model=List[schemas.LessonNoteListResponse])
def list_lesson_notes(
    skip: int = 0,
    limit: int = 50,
    subject_id: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List lesson notes based on user role and class+subject scoping.
    
    - Admins: See all notes
    - Subject Teachers: See only notes they uploaded
    - Students: See only notes from subjects in their class (via ClassMembership)
    
    Args:
        skip: Pagination offset
        limit: Pagination limit (max 100)
        subject_id: Filter by ClassSubject UUID
        status: Filter by status (PENDING_PROCESSING, READY, ERROR)
    """
    
    if limit > 100:
        limit = 100
    
    query = db.query(models.LessonNote).filter(
        models.LessonNote.is_deleted == False
    )
    
    # Role-based filtering with class+subject scoping
    if current_user.role == "admin":
        # Admins see all notes
        pass
    elif current_user.role == "subject_teacher":
        # Subject teachers see only notes they uploaded
        query = query.filter(models.LessonNote.teacher_id == current_user.id)
    elif current_user.role == "student":
        # Students see notes from subjects in their class
        # First, find all classes student is member of
        student_classes = db.query(models.ClassMembership.class_id).filter(
            models.ClassMembership.student_id == current_user.id,
            models.ClassMembership.left_at == None
        ).all()
        
        class_ids = [c[0] for c in student_classes]
        
        if not class_ids:
            # Student not in any class, return no notes
            query = query.filter(models.LessonNote.id == None)
        else:
            # Get all subjects in student's classes
            subject_ids = db.query(models.ClassSubject.id).filter(
                models.ClassSubject.class_id.in_(class_ids)
            ).all()
            
            subject_list = [s[0] for s in subject_ids]
            
            if subject_list:
                query = query.filter(models.LessonNote.subject_id.in_(subject_list))
            else:
                query = query.filter(models.LessonNote.id == None)
    
    # Filter by subject if specified
    if subject_id:
        try:
            subject_uuid = UUID(subject_id)
            query = query.filter(models.LessonNote.subject_id == subject_uuid)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subject_id format"
            )
    
    # Filter by status
    if status:
        query = query.filter(models.LessonNote.status == status)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    notes = query.offset(skip).limit(limit).all()
    
    return notes



@router.get("/{note_id}", response_model=schemas.LessonNoteDetailResponse)
def get_lesson_note_details(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get detailed information about a lesson note with class+subject context.
    
    Includes teacher name, class info, subject info, and processing status.
    Access control based on class membership and subject enrollment.
    """
    
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == note_id,
        models.LessonNote.is_deleted == False
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson note not found"
        )
    
    # Access control by role
    if current_user.role == "admin":
        pass  # Admin can access all
    elif current_user.role == "subject_teacher":
        # Subject teacher can only access their own notes
        if current_user.id != note.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this note"
            )
    elif current_user.role == "student":
        # Student can access if they're in the class AND subject
        is_member = db.query(models.ClassMembership).filter(
            models.ClassMembership.class_id == note.class_id,
            models.ClassMembership.student_id == current_user.id,
            models.ClassMembership.left_at == None
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You're not a member of the class containing this content"
            )
        
        # Verify the subject exists in their class
        subject_in_class = db.query(models.ClassSubject).filter(
            models.ClassSubject.id == note.subject_id,
            models.ClassSubject.class_id == note.class_id
        ).first()
        
        if not subject_in_class:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This subject is not available in your class"
            )
    
    # Build response
    teacher = note.teacher
    class_obj = note.class_obj
    subject = note.class_subject
    
    response = schemas.LessonNoteDetailResponse.from_orm(note)
    response.teacher_name = teacher.full_name if teacher else "Unknown"
    
    return response



@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_teacher)
):
    """
    Delete a lesson note (soft delete)
    
    Only the note owner or admins can delete notes.
    Deletes the file from disk and marks as deleted in database.
    """
    
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == note_id,
        models.LessonNote.is_deleted == False
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson note not found"
        )
    
    # Check ownership
    if current_user.role == "teacher" and current_user.id != note.teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own notes"
        )
    
    # Delete file from disk
    try:
        FileManager.delete_file(note.file_url)
    except FileStorageError as e:
        # Log warning but continue with soft delete
        print(f"Warning: Could not delete file {note.file_url}: {e}")
    
    # Soft delete: mark as deleted
    note.is_deleted = True
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lesson note"
        )


@router.get("/{note_id}/units", response_model=List[schemas.LearningUnitResponse])
def get_lesson_units(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all learning units generated from a lesson note
    
    Units are created during the content processing phase.
    """
    
    # Verify note exists and user has access
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == note_id,
        models.LessonNote.is_deleted == False
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson note not found"
        )
    
    # Get units
    units = db.query(models.LearningUnit).filter(
        models.LearningUnit.note_id == note_id
    ).order_by(models.LearningUnit.sequence_number).all()
    
    return units


@router.get("/{note_id}/units/{unit_id}/artefacts", response_model=List[schemas.AIArtefactResponse])
def get_unit_artefacts(
    note_id: UUID,
    unit_id: UUID,
    artefact_type: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get AI-generated artefacts (questions, summaries) for a learning unit
    
    Args:
        note_id: Lesson note ID
        unit_id: Learning unit ID
        artefact_type: Filter by type (MCQ, SHORT_ANSWER, SUMMARY)
    """
    
    # Verify unit exists and belongs to note
    unit = db.query(models.LearningUnit).filter(
        models.LearningUnit.id == unit_id,
        models.LearningUnit.note_id == note_id
    ).first()
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning unit not found"
        )
    
    # Get artefacts
    query = db.query(models.AiArtefact).filter(
        models.AiArtefact.unit_id == unit_id
    )
    
    if artefact_type:
        query = query.filter(models.AiArtefact.artefact_type == artefact_type)
    
    artefacts = query.all()
    
    return artefacts
