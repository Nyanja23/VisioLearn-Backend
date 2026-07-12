"""
Lesson Notes Router - File Upload & Management

Implements PRD Section 6.2 endpoints for lesson note management.
Teachers can upload lesson content (PDF, DOCX, TXT) for processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from uuid import UUID

from .. import models, schemas, security
from ..database import get_db
from ..dependencies import get_current_user, require_teacher
from ..storage import FileManager, FileStorageError

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


def _ensure_can_upload(
    current_user: models.User,
    class_subject: models.ClassSubject,
    db: Session,
) -> None:
    """Uploads are allowed for: the subject's own teacher, the CLASS teacher
    of the class the subject belongs to, and admins. Class teachers were
    previously locked out entirely, which made a one-teacher school unable to
    publish notes without creating a second account."""
    if current_user.role == "admin":
        return
    if current_user.role == "subject_teacher":
        if class_subject.subject_teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to upload content for this subject"
            )
        return
    if current_user.role == "class_teacher":
        class_obj = db.query(models.Class).filter(
            models.Class.id == class_subject.class_id
        ).first()
        if not class_obj or class_obj.class_teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload to subjects in your own class"
            )
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only teachers can upload content"
    )


def _resolve_subject(
    current_user: models.User,
    subject_id: str,
    subject_name: str,
    db: Session,
) -> models.ClassSubject:
    """Find the ClassSubject a note files under, without demanding a UUID.

    Priority: explicit subject_id → subject_name within the caller's own
    class (auto-created for class teachers) → the caller's only subject.
    A teacher should be able to go from account to published lesson in one
    upload call; hunting for internal UUIDs was the main point of friction.
    """
    if subject_id:
        try:
            subject_uuid = UUID(subject_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subject_id format. Must be a valid UUID."
            )
        class_subject = db.query(models.ClassSubject).filter(
            models.ClassSubject.id == subject_uuid
        ).first()
        if not class_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        return class_subject

    name = (subject_name or "").strip()

    if current_user.role == "class_teacher":
        class_obj = db.query(models.Class).filter(
            and_(
                models.Class.class_teacher_id == current_user.id,
                models.Class.is_deleted == False,
            )
        ).first()
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You don't have a class yet. Register as a class teacher first."
            )
        if not name:
            name = "General"
        subject = db.query(models.ClassSubject).filter(
            and_(
                models.ClassSubject.class_id == class_obj.id,
                models.ClassSubject.subject_name.ilike(name),
            )
        ).first()
        if subject:
            return subject
        subject = models.ClassSubject(
            class_id=class_obj.id,
            subject_name=name,
            subject_teacher_id=current_user.id,
        )
        db.add(subject)
        db.flush()  # committed together with the note
        return subject

    if current_user.role == "subject_teacher":
        query = db.query(models.ClassSubject).filter(
            models.ClassSubject.subject_teacher_id == current_user.id
        )
        if name:
            subject = query.filter(
                models.ClassSubject.subject_name.ilike(name)
            ).first()
            if not subject:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"You don't teach a subject called '{name}'"
                )
            return subject
        subjects = query.all()
        if len(subjects) == 1:
            return subjects[0]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You teach more than one subject — pass subject_name or subject_id"
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Pass subject_id to upload as an admin"
    )


@router.post(
    "/upload",
    response_model=schemas.LessonNoteResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_lesson_note(
    upload_data: schemas.LessonNoteUpload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload a lesson note with audio metadata (class+subject scoped).
    
    For audio content, this creates a metadata record without requiring file upload.
    Audio files are managed separately through the content storage system.
    
    Only subject_teachers can upload content.
    
    Request body:
    - title: Lesson title
    - subject_id: UUID of the ClassSubject (required)
    - grade_level: Target grade level
    - description: Optional description
    - duration_seconds: Duration of audio in seconds
        
    Returns:
        LessonNoteResponse with note metadata
    """
    
    # Subject teachers, class teachers (for their own class), and admins may
    # upload. The per-subject ownership check runs below, once the subject
    # has been resolved.
    if current_user.role not in ["subject_teacher", "class_teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can upload content"
        )
    
    # Get the ClassSubject to verify it exists and user teaches it
    try:
        class_subject = db.query(models.ClassSubject).filter(
            models.ClassSubject.id == UUID(upload_data.subject_id)
        ).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subject_id format. Must be a valid UUID."
        )
    
    if not class_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Verify per-subject/per-class upload permission.
    _ensure_can_upload(current_user, class_subject, db)
    
    # Create LessonNote record with class and subject IDs
    note_id = models.uuid.uuid4()
    
    db_note = models.LessonNote(
        id=note_id,
        class_id=class_subject.class_id,
        subject_id=class_subject.id,
        teacher_id=current_user.id,
        title=upload_data.title,
        subject=class_subject.subject_name,  # Use actual subject name
        grade_level=upload_data.grade_level,
        description=upload_data.description,
        duration_seconds=upload_data.duration_seconds,
        status="READY"  # For metadata-only notes, mark as ready
    )
    
    # Save to database
    db.add(db_note)
    try:
        db.commit()
        db.refresh(db_note)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lesson note record"
        )
    
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

    # Students may only receive teacher-approved MCQs. Non-MCQ artefacts
    # (e.g. summaries) are not gated. Teachers review/approve via the
    # /api/v1/notes/{note_id}/questions endpoints.
    visible = [
        a for a in artefacts
        if a.artefact_type != "MCQ" or getattr(a, "approved", False)
    ]

    return visible


@router.post(
    "/upload-with-file",
    response_model=schemas.LessonNoteResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_lesson_note_with_file(
    title: str,
    grade_level: str,
    subject_id: str = None,
    subject_name: str = None,
    file: UploadFile = File(...),
    description: str = None,
    duration_seconds: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Upload a lesson note WITH an actual file (PDF, DOCX, TXT).
    THIS is the primary way teachers publish lessons.

    The file's text is extracted on the server at upload time and becomes the
    lesson content students receive. No subject UUID scavenger hunt needed:

    - Pass `subject_name` (e.g. "Mathematics") and the subject is found — or,
      for a class teacher, created — in your own class automatically.
    - Pass `subject_id` only if you already know the exact subject UUID.
    - A subject teacher with exactly one subject can omit both.

    Args:
        title: Lesson title
        grade_level: Target grade level (e.g. "P.6")
        subject_id: Optional UUID of the ClassSubject
        subject_name: Optional subject name, resolved in your class
        file: The lesson file (PDF, DOCX, or TXT)
        description: Optional fallback text if extraction fails
        duration_seconds: Optional duration in seconds

    Returns:
        LessonNoteResponse with file metadata
    """

    # Subject teachers, class teachers (for their own class), and admins may
    # upload. The per-subject ownership check runs below, once the subject
    # has been resolved.
    if current_user.role not in ["subject_teacher", "class_teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can upload content"
        )

    # Resolve which subject this note files under (may auto-create for a
    # class teacher), then verify permission.
    class_subject = _resolve_subject(current_user, subject_id, subject_name, db)
    _ensure_can_upload(current_user, class_subject, db)
    
    # Create LessonNote record first (to get ID for file storage)
    note_id = models.uuid.uuid4()
    
    # Validate and store file with note_id
    try:
        file_path = await FileManager.save_upload_file(file, str(note_id))
        print(f"[+] File saved: {file_path}")
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)[:100]}"
        )
    
    # Extract the lesson text from the file NOW, synchronously. The student
    # app builds the spoken lesson from `description`, so without this step a
    # file upload reached phones as the literal text "File: notes.pdf".
    # Extraction of txt/docx/pdf is fast and needs no Celery worker — the
    # heavyweight AI pipeline stays optional; content flows regardless.
    extracted_text = ""
    try:
        import re as _re
        from ..processing.text_extractor import extract_from_file
        raw_text = extract_from_file(file_path) or ""
        # NOTE: deliberately NOT sanitize_text() — it flattens every newline
        # into a space, and the app's lesson segmenter (spoken pauses) and
        # question generator (heading/label detection) both depend on the
        # note's line structure. Clean whitespace but keep the lines.
        cleaned = _re.sub(r'[ \t]+', ' ', raw_text)
        cleaned = _re.sub(r' ?\n ?', '\n', cleaned)
        extracted_text = _re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        if extracted_text:
            print(f"[+] Extracted {len(extracted_text)} chars from {file.filename}")
    except Exception as e:
        print(f"[!] Text extraction failed for {file.filename}: {e}")

    # Create LessonNote record with file information
    db_note = models.LessonNote(
        id=note_id,
        class_id=class_subject.class_id,
        subject_id=class_subject.id,
        teacher_id=current_user.id,
        title=title,
        subject=class_subject.subject_name,
        grade_level=grade_level,
        description=extracted_text or description or f"File: {file.filename}",
        duration_seconds=duration_seconds,
        file_url=file_path,
        original_file_name=file.filename,
        status="READY"  # File is stored, ready for processing
    )
    
    # Save to database
    db.add(db_note)
    try:
        db.commit()
        db.refresh(db_note)
        print(f"[+] Lesson note created: {db_note.id}, File: {file.filename}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save lesson note: {str(e)[:100]}"
        )
    
    return db_note
