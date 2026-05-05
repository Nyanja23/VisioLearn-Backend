from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional, Literal
from datetime import datetime
import re

# Valid user roles
UserRole = Literal["admin", "teacher", "student"]

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
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserRegisterTeacher(BaseModel):
    """Teacher self-registration. System auto-generates class_code."""
    email: EmailStr
    full_name: str
    password: str
    role: Literal["teacher"] = "teacher"
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserRegisterStudent(BaseModel):
    """Student self-registration. Must provide valid teacher class_code."""
    email: EmailStr
    full_name: str
    password: str
    class_code: str
    role: Literal["student"] = "student"
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('class_code')
    @classmethod
    def validate_class_code_format(cls, v: str) -> str:
        if not re.match(r'^[A-Z]{2}-\d{4}$', v):
            raise ValueError('Class code must be in format XX-XXXX (e.g., AB-1234)')
        return v

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    is_deleted: bool
    class_code: Optional[str] = None
    teacher_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# --- Lesson Notes Schemas (Phase 2) ---
class LessonNoteCreate(BaseModel):
    title: str
    subject: str
    grade_level: str

class LessonNoteUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None

class LessonNoteResponse(LessonNoteCreate):
    id: UUID
    teacher_id: UUID
    file_url: str
    original_file_name: str
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
    original_file_name: str
    status: str
    created_at: datetime
    teacher_id: UUID

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
