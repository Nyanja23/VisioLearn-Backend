import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.now(timezone.utc)

class School(Base):
    __tablename__ = "schools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    region = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)
    
    users = relationship("User", back_populates="school")
    notes = relationship("LessonNote", back_populates="school")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True)
    role = Column(String(50), nullable=False) # admin, teacher, student
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    school = relationship("School", back_populates="users")
    notes_uploaded = relationship("LessonNote", back_populates="teacher")
    progress_records = relationship("StudentProgress", back_populates="student")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class LessonNote(Base):
    __tablename__ = "lesson_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    file_url = Column(String(512), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING_PROCESSING") # PENDING_PROCESSING, READY, ERROR
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)

    teacher = relationship("User", back_populates="notes_uploaded")
    school = relationship("School", back_populates="notes")
    units = relationship("LearningUnit", back_populates="note")

class LearningUnit(Base):
    __tablename__ = "learning_units"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("lesson_notes.id"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    content_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    note = relationship("LessonNote", back_populates="units")
    artefacts = relationship("AiArtefact", back_populates="unit")
    progress_records = relationship("StudentProgress", back_populates="unit")

class AiArtefact(Base):
    __tablename__ = "ai_artefacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("learning_units.id"), nullable=False, index=True)
    artefact_type = Column(String(50), nullable=False) # MCQ, SHORT_ANSWER, SUMMARY
    content = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    unit = relationship("LearningUnit", back_populates="artefacts")

class StudentProgress(Base):
    __tablename__ = "student_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("learning_units.id"), nullable=False, index=True)
    artefact_id = Column(UUID(as_uuid=True), ForeignKey("ai_artefacts.id"), nullable=True, index=True)
    status = Column(String(50), nullable=False) # COMPLETED, ATTEMPTED
    score = Column(Float, nullable=True)
    student_response = Column(Text, nullable=True)
    offline_recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now) # When synced

    student = relationship("User", back_populates="progress_records")
    unit = relationship("LearningUnit", back_populates="progress_records")

class NoteAssignment(Base):
    __tablename__ = "note_assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("lesson_notes.id"), nullable=False, index=True)
    target_type = Column(String(50), nullable=False) # STUDENT, GRADE_GROUP
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# --- VOICE INTERACTION ENTITIES (Amendment A) ---

class VoiceSession(Base):
    __tablename__ = "voice_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("lesson_notes.id"), nullable=False, index=True)
    status = Column(String(50), default="ACTIVE") # ACTIVE, COMPLETED, ABANDONED
    current_unit_id = Column(UUID(as_uuid=True), ForeignKey("learning_units.id"), nullable=True)
    current_state = Column(String(50), nullable=False) # LISTENING_UNIT, ANSWERING_MCQ, FREE_ASK, etc.
    started_at = Column(DateTime(timezone=True), default=utc_now)
    last_activity_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class VoiceInteraction(Base):
    __tablename__ = "voice_interactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("voice_sessions.id"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    student_transcript = Column(Text, nullable=False)
    detected_intent = Column(String(100), nullable=False)
    ai_response_text = Column(Text, nullable=False)
    audio_file_url = Column(String(512), nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class FreeAskExchange(Base):
    __tablename__ = "free_ask_exchanges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("voice_sessions.id"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("learning_units.id"), nullable=True, index=True)
    student_question = Column(Text, nullable=False)
    retrieved_context_text = Column(Text, nullable=True)
    ai_answer = Column(Text, nullable=False)
    was_helpful = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# Create specific needed indexes mapping to PRD design
Index('idx_notes_school_subject', LessonNote.school_id, LessonNote.subject)
Index('idx_units_note_seq', LearningUnit.note_id, LearningUnit.sequence_number)
Index('idx_progress_student_unit', StudentProgress.student_id, StudentProgress.unit_id)
Index('idx_voice_interactions_session', VoiceInteraction.session_id, VoiceInteraction.sequence_number)
