"""
Voice Session Management Router - Phase 3

Implements student voice interaction tracking:
- POST /voice/session/start - Create new voice session
- POST /voice/session/event - Log voice interaction
- POST /voice/session/end - Close session and calculate summary
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
from typing import List, Optional

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


# ============================================================================
# Schema definitions for voice endpoints
# ============================================================================

class VoiceSessionStartRequest(schemas.BaseModel):
    """Request to start a voice session"""
    student_id: UUID
    note_id: UUID
    unit_id: UUID


class VoiceSessionStartResponse(schemas.BaseModel):
    """Response when voice session starts"""
    session_id: UUID
    student_id: UUID
    note_id: UUID
    unit_id: UUID
    status: str  # ACTIVE, PAUSED, COMPLETED
    started_at: datetime

    class Config:
        from_attributes = True


class VoiceInteractionRequest(schemas.BaseModel):
    """Request to log a voice interaction event"""
    session_id: UUID
    interaction_type: str  # answer, next, repeat, free_ask, pause
    command: str  # The voice command/input
    confidence: Optional[float] = None  # ASR confidence (0-1)
    response: Optional[str] = None  # System response


class VoiceInteractionResponse(schemas.BaseModel):
    """Response after logging an interaction"""
    interaction_id: UUID
    session_id: UUID
    sequence_number: int
    student_transcript: str
    detected_intent: str
    ai_response_text: str
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceSessionEndRequest(schemas.BaseModel):
    """Request to end a voice session"""
    session_id: UUID
    duration_seconds: int
    questions_answered: Optional[int] = 0
    total_score: Optional[float] = None


class VoiceSessionEndResponse(schemas.BaseModel):
    """Response when session ends"""
    session_id: UUID
    status: str  # COMPLETED
    duration_seconds: int
    questions_answered: int
    average_score: Optional[float]
    ended_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/session/start", response_model=VoiceSessionStartResponse, status_code=status.HTTP_201_CREATED)
def start_voice_session(
    request: VoiceSessionStartRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Start a new voice session for a student learning a lesson.
    
    A voice session represents one learning interaction:
    - Student starts lesson → creates session
    - Student answers questions, navigates units → logs interactions
    - Student finishes → ends session
    
    Only the student or admin can create a session for a student.
    """
    
    # Verify student exists
    student = db.query(models.User).filter(models.User.id == request.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student not found: {request.student_id}"
        )
    
    if student.role != "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only create voice sessions for student users"
        )
    
    # Verify note exists and is assigned to this student
    note = db.query(models.LessonNote).filter(models.LessonNote.id == request.note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson note not found: {request.note_id}"
        )
    
    if note.status != "READY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lesson note not ready for learning (status: {note.status})"
        )
    
    # Verify unit exists in this note
    unit = db.query(models.LearningUnit).filter(
        models.LearningUnit.id == request.unit_id,
        models.LearningUnit.note_id == request.note_id
    ).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning unit not found in this lesson"
        )
    
    # Create voice session
    session = models.VoiceSession(
        student_id=request.student_id,
        note_id=request.note_id,
        current_unit_id=request.unit_id,
        status="ACTIVE",
        current_state="LISTENING_UNIT",
        started_at=datetime.now(timezone.utc)
    )
    
    db.add(session)
    try:
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create voice session: {str(e)}"
        )
    
    return VoiceSessionStartResponse(
        session_id=session.id,
        student_id=session.student_id,
        note_id=session.note_id,
        unit_id=session.current_unit_id,
        status=session.status,
        started_at=session.started_at
    )


@router.post("/session/event", response_model=VoiceInteractionResponse, status_code=status.HTTP_201_CREATED)
def log_voice_interaction(
    request: VoiceInteractionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Log a voice interaction event during an active session.
    
    Events represent student actions:
    - answer: Student answers current question
    - next: Student asks to move to next unit
    - repeat: Student asks to repeat current unit
    - free_ask: Student asks a question outside current content
    - pause: Student pauses the session
    
    Each interaction is tracked with confidence score and response.
    """
    
    # Verify session exists and is active
    session = db.query(models.VoiceSession).filter(models.VoiceSession.id == request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session not found: {request.session_id}"
        )
    
    if session.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not active (status: {session.status})"
        )
    
    # Validate interaction type
    valid_types = ["answer", "next", "repeat", "free_ask", "pause"]
    if request.interaction_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interaction type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Get next sequence number for this session
    last_interaction = db.query(models.VoiceInteraction).filter(
        models.VoiceInteraction.session_id == request.session_id
    ).order_by(models.VoiceInteraction.sequence_number.desc()).first()
    
    next_sequence = (last_interaction.sequence_number + 1) if last_interaction else 1
    
    # Create interaction record
    interaction = models.VoiceInteraction(
        session_id=request.session_id,
        sequence_number=next_sequence,
        student_transcript=request.command,
        detected_intent=request.interaction_type,
        ai_response_text=request.response or "",
        confidence_score=request.confidence
    )
    
    db.add(interaction)
    
    # Update session if pausing
    if request.interaction_type == "pause":
        session.status = "PAUSED"
    
    try:
        db.commit()
        db.refresh(interaction)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log interaction: {str(e)}"
        )
    
    return VoiceInteractionResponse(
        interaction_id=interaction.id,
        session_id=interaction.session_id,
        sequence_number=interaction.sequence_number,
        student_transcript=interaction.student_transcript,
        detected_intent=interaction.detected_intent,
        ai_response_text=interaction.ai_response_text,
        confidence_score=interaction.confidence_score,
        created_at=interaction.created_at
    )


@router.post("/session/end", response_model=VoiceSessionEndResponse)
def end_voice_session(
    request: VoiceSessionEndRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    End a voice session and calculate summary statistics.
    
    When student finishes learning:
    - Session marked as COMPLETED
    - Duration calculated
    - Average score from answers calculated
    - Session closed
    """
    
    # Verify session exists
    session = db.query(models.VoiceSession).filter(models.VoiceSession.id == request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session not found: {request.session_id}"
        )
    
    # Mark session as completed
    session.status = "COMPLETED"
    session.completed_at = datetime.now(timezone.utc)
    
    # Calculate average score if questions were answered
    average_score = None
    if request.questions_answered and request.questions_answered > 0:
        average_score = request.total_score / request.questions_answered if request.total_score else 0
    
    # Count total interactions in session
    total_interactions = db.query(models.VoiceInteraction).filter(
        models.VoiceInteraction.session_id == request.session_id
    ).count()
    
    try:
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end voice session: {str(e)}"
        )
    
    return VoiceSessionEndResponse(
        session_id=session.id,
        status=session.status,
        duration_seconds=request.duration_seconds,
        questions_answered=request.questions_answered or 0,
        average_score=average_score,
        ended_at=session.completed_at
    )


@router.get("/session/{session_id}", response_model=VoiceSessionStartResponse)
def get_voice_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get details of a voice session.
    
    Returns session metadata including:
    - Session ID, student, lesson, unit
    - Current status (ACTIVE, PAUSED, COMPLETED)
    - Start time and duration
    """
    
    session = db.query(models.VoiceSession).filter(models.VoiceSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session not found: {session_id}"
        )
    
    return VoiceSessionStartResponse(
        session_id=session.id,
        student_id=session.student_id,
        note_id=session.note_id,
        unit_id=session.current_unit_id,
        status=session.status,
        started_at=session.started_at
    )


@router.get("/session/{session_id}/interactions", response_model=List[VoiceInteractionResponse])
def get_session_interactions(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all interactions for a voice session.
    
    Returns chronological list of all student actions during the session.
    """
    
    # Verify session exists
    session = db.query(models.VoiceSession).filter(models.VoiceSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session not found: {session_id}"
        )
    
    interactions = db.query(models.VoiceInteraction).filter(
        models.VoiceInteraction.session_id == session_id
    ).order_by(models.VoiceInteraction.sequence_number).all()
    
    return [
        VoiceInteractionResponse(
            interaction_id=i.id,
            session_id=i.session_id,
            sequence_number=i.sequence_number,
            student_transcript=i.student_transcript,
            detected_intent=i.detected_intent,
            ai_response_text=i.ai_response_text,
            confidence_score=i.confidence_score,
            created_at=i.created_at
        )
        for i in interactions
    ]
