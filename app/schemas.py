from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional, Literal
from datetime import datetime
import re

# Valid user roles for new class-based system
UserRole = Literal["admin", "class_teacher", "subject_teacher", "student"]

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Relaxed, human-friendly policy: short and memorable, but not blank.
        # At least 6 characters with a letter and a number; no uppercase or
        # special-character requirement (those drove forgotten passwords).
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserRegisterClassTeacher(BaseModel):
    """Class teacher registration. System auto-generates student_code and teacher_code for class."""
    email: EmailStr
    full_name: str
    password: str
    class_name: str
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Relaxed, human-friendly policy: short and memorable, but not blank.
        # At least 6 characters with a letter and a number; no uppercase or
        # special-character requirement (those drove forgotten passwords).
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserRegisterSubjectTeacher(BaseModel):
    """Subject teacher registration. Optionally joins class using teacher_code."""
    email: EmailStr
    full_name: str
    password: str
    teacher_code: Optional[str] = None
    subject_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Relaxed, human-friendly policy: short and memorable, but not blank.
        # At least 6 characters with a letter and a number; no uppercase or
        # special-character requirement (those drove forgotten passwords).
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserRegisterStudent(BaseModel):
    """Student self-registration. Must provide valid student code to join class."""
    email: EmailStr
    full_name: str
    password: str
    student_code: str
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Relaxed, human-friendly policy: short and memorable, but not blank.
        # At least 6 characters with a letter and a number; no uppercase or
        # special-character requirement (those drove forgotten passwords).
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @field_validator('student_code')
    @classmethod
    def validate_student_code_format(cls, v: str) -> str:
        # Either class code joins the class (both identify it uniquely), and
        # codes arrive from voice capture / hand-typing, so normalise case
        # and whitespace here instead of bouncing the student.
        v = (v or '').strip().upper()
        if not re.match(r'^(SC|TC)-[A-Z0-9]{4}$', v):
            raise ValueError(
                'Class code must be in format SC-XXXX or TC-XXXX (e.g., SC-9FX2)')
        return v

# --- Legacy schemas (deprecated, kept for reference) ---
class UserRegisterTeacher(BaseModel):
    """DEPRECATED: Use UserRegisterClassTeacher instead."""
    email: EmailStr
    full_name: str
    password: str
    role: Literal["teacher"] = "teacher"
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Relaxed, human-friendly policy (see other registration schemas):
        # at least 6 characters with a letter and a number.
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    full_name: str
    role: UserRole
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

# --- Class-Based System Schemas ---
class ClassResponse(BaseModel):
    id: UUID
    class_name: str
    class_teacher_id: UUID
    student_code: str
    teacher_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassSubjectResponse(BaseModel):
    id: UUID
    class_id: UUID
    subject_name: str
    subject_teacher_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassMembershipResponse(BaseModel):
    id: UUID
    class_id: UUID
    student_id: UUID
    joined_at: datetime
    left_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- Registration Response Schemas ---
class ClassTeacherRegistrationResponse(BaseModel):
    """Response when class teacher registers. Includes class codes."""
    user_id: UUID
    email: str
    full_name: str
    role: str
    class_id: UUID
    student_code: str
    teacher_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubjectTeacherRegistrationResponse(BaseModel):
    """Response when subject teacher registers. Includes subject if joined class."""
    user_id: UUID
    email: str
    full_name: str
    role: str
    subject_id: Optional[UUID] = None
    subject_name: Optional[str] = None
    class_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentRegistrationResponse(BaseModel):
    """Response when student registers. Includes class info."""
    user_id: UUID
    email: str
    full_name: str
    role: str
    class_id: UUID
    class_name: str
    student_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Lesson Notes Schemas (Phase 2) ---
class LessonNoteCreate(BaseModel):
    title: str
    subject: str
    grade_level: str

class LessonNoteUpload(BaseModel):
    """Upload lesson note with metadata"""
    title: str
    subject_id: str  # ClassSubject UUID as string
    grade_level: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = None

class LessonNoteUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None

class LessonNoteResponse(BaseModel):
    id: UUID
    title: str
    subject: str
    grade_level: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    teacher_id: UUID
    class_id: UUID
    subject_id: UUID
    file_url: Optional[str] = None
    original_file_name: Optional[str] = None
    status: str  # PENDING_PROCESSING, READY, ERROR
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LessonNoteListResponse(BaseModel):
    id: UUID
    title: str
    subject: str
    grade_level: str
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    original_file_name: Optional[str] = None
    status: str
    created_at: datetime
    teacher_id: UUID
    class_id: UUID
    subject_id: UUID
    
    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

class LessonNoteDetailResponse(LessonNoteResponse):
    teacher_name: Optional[str] = None

# --- Learning Unit Schemas ---
class LearningUnitResponse(BaseModel):
    id: UUID
    note_id: UUID
    sequence_number: int
    content_text: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- AI Artefact Schemas ---
class AIArtefactResponse(BaseModel):
    id: UUID
    unit_id: UUID
    artefact_type: str  # MCQ, SHORT_ANSWER, SUMMARY
    content: dict
    created_at: datetime

    class Config:
        from_attributes = True

# --- Progress Schemas ---
class ContentProgressCreate(BaseModel):
    """Log content progress when student plays audio"""
    note_id: UUID
    last_position_seconds: int
    completed: bool

class ContentProgressResponse(BaseModel):
    id: UUID
    student_id: UUID
    note_id: UUID
    started_at: datetime
    last_position_seconds: int
    completed: bool
    completion_percentage: float
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StudentProgressSummary(BaseModel):
    """Summary of student's progress across all content"""
    total_notes: int
    completed_notes: int
    avg_completion_percentage: float
    last_updated: Optional[datetime] = None

class TeacherStudentSummary(BaseModel):
    """Summary of a teacher's student with progress"""
    id: UUID
    full_name: str
    email: str
    total_content_accessed: int
    avg_completion_percentage: float
    last_access: Optional[datetime] = None
