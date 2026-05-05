import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(50), nullable=False) # admin, class_teacher, subject_teacher, student
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships for class-based system
    classes_managed = relationship("Class", back_populates="class_teacher", foreign_keys="Class.class_teacher_id")
    class_subjects = relationship("ClassSubject", back_populates="subject_teacher", foreign_keys="ClassSubject.subject_teacher_id")
    class_memberships = relationship("ClassMembership", back_populates="student", foreign_keys="ClassMembership.student_id")
    notes_uploaded = relationship("LessonNote", back_populates="teacher", foreign_keys="LessonNote.teacher_id")
    progress_records = relationship("ContentProgress", back_populates="student", foreign_keys="ContentProgress.student_id")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# ============= NEW CLASS-BASED MODELS =============

class Class(Base):
    """Represents a class managed by a class teacher"""
    __tablename__ = "classes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_name = Column(String(255), nullable=False)
    class_teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    student_code = Column(String(10), unique=True, nullable=False)  # e.g., "SC-9FX2" for students to join
    teacher_code = Column(String(10), unique=True, nullable=False)  # e.g., "TC-5MK8" for subject teachers to join
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)
    
    class_teacher = relationship("User", back_populates="classes_managed", foreign_keys=[class_teacher_id])
    subjects = relationship("ClassSubject", back_populates="class_obj", cascade="all, delete-orphan")
    memberships = relationship("ClassMembership", back_populates="class_obj", cascade="all, delete-orphan")

class ClassSubject(Base):
    """Represents a subject taught by a subject teacher within a class"""
    __tablename__ = "class_subjects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    subject_name = Column(String(100), nullable=False)
    subject_teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # NOTE: subject_teacher_id has NO UNIQUE constraint - teachers can teach multiple subjects
    
    class_obj = relationship("Class", back_populates="subjects", foreign_keys=[class_id])
    subject_teacher = relationship("User", back_populates="class_subjects", foreign_keys=[subject_teacher_id])
    notes = relationship("LessonNote", back_populates="class_subject")

class ClassMembership(Base):
    """Links students to classes"""
    __tablename__ = "class_memberships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), default=utc_now)
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    class_obj = relationship("Class", back_populates="memberships", foreign_keys=[class_id])
    student = relationship("User", back_populates="class_memberships", foreign_keys=[student_id])

# ============= END CLASS-BASED MODELS =============


class LessonNote(Base):
    __tablename__ = "lesson_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("class_subjects.id"), nullable=False, index=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For audio content duration
    file_url = Column(String(512), nullable=True)  # Optional for metadata-only notes
    original_file_name = Column(String(255), nullable=True)
    status = Column(String(50), default="PENDING_PROCESSING") # PENDING_PROCESSING, READY, ERROR
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False)

    class_obj = relationship("Class", foreign_keys=[class_id])
    class_subject = relationship("ClassSubject", back_populates="notes", foreign_keys=[subject_id])
    teacher = relationship("User", back_populates="notes_uploaded", foreign_keys=[teacher_id])
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

    student = relationship("User")
    unit = relationship("LearningUnit", back_populates="progress_records")

class ContentProgress(Base):
    """Tracks student engagement with lesson content (listening, playback position, completion)"""
    __tablename__ = "content_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    note_id = Column(UUID(as_uuid=True), ForeignKey("lesson_notes.id"), nullable=False, index=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("class_subjects.id"), nullable=False, index=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    last_position_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    student = relationship("User", back_populates="progress_records", foreign_keys=[student_id])
    note = relationship("LessonNote", foreign_keys=[note_id])
    class_obj = relationship("Class", foreign_keys=[class_id])
    subject = relationship("ClassSubject", foreign_keys=[subject_id])
    teacher = relationship("User", foreign_keys=[teacher_id])

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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
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

# Create specific needed indexes for refactored class-based design
Index('idx_class_teacher', Class.class_teacher_id)
Index('idx_class_subject_class', ClassSubject.class_id)
Index('idx_class_subject_teacher', ClassSubject.subject_teacher_id)
Index('idx_class_membership_class_student', ClassMembership.class_id, ClassMembership.student_id)
Index('idx_notes_class_subject_teacher', LessonNote.class_id, LessonNote.subject_id, LessonNote.teacher_id)
Index('idx_units_note_seq', LearningUnit.note_id, LearningUnit.sequence_number)
Index('idx_progress_student_unit', StudentProgress.student_id, StudentProgress.unit_id)
Index('idx_content_progress_student_class_subject', ContentProgress.student_id, ContentProgress.class_id, ContentProgress.subject_id)
Index('idx_voice_interactions_session', VoiceInteraction.session_id, VoiceInteraction.sequence_number)
