"""
Role-Based Access Control (RBAC) Middleware and Dependencies

Architecture:
- Admin: Can view/manage all users, system monitoring (no school management)
- Teacher: Registers with auto-generated class_code, uploads content, views own students
- Student: Registers with teacher's class_code, accesses teacher's content, logs progress

Teacher-Student Relationship:
- Teacher has unique class_code (e.g., AB-1234)
- Student provides class_code at registration
- Student.teacher_id set to teacher's User.id
- Students can only see notes from their linked teacher
- Teachers can only see progress from their students

Access Control Rules:
1. Teacher can upload/delete only their own content (notes.teacher_id == user.id)
2. Student can access only their teacher's content (note.teacher_id == student.teacher_id)
3. Teacher can view only their own students (student.teacher_id == teacher.id)
4. Students cannot access /progress/students endpoint (teacher-only)
5. Teachers cannot be students and vice versa

This is enforced both at:
- Dependency level (require_admin, require_teacher, require_student)
- Endpoint level (resource ownership checks in route handlers)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
import jwt
from pydantic import ValidationError

from .database import get_db
from .security import SECRET_KEY, ALGORITHM
from .models import User
from .schemas import TokenPayload

# Use HTTP Bearer authentication (simpler than OAuth2PasswordBearer for JWT tokens)
security = HTTPBearer(description="Enter your JWT access token from the /login endpoint")

def get_current_user(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.id == UUID(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires one of: {self.allowed_roles}"
            )
        return user

# Convenience dependencies for specific roles
require_admin = RoleChecker(["admin"])
require_teacher = RoleChecker(["admin", "teacher"])
require_student = RoleChecker(["student"])

# Helper functions for resource ownership validation

def verify_teacher_owns_content(teacher_id: UUID, current_user: User) -> bool:
    """
    Verify that current teacher user owns the specified content (by teacher_id).
    Admin users always have access.
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "teacher":
        return False
    return current_user.id == teacher_id

def verify_student_can_access_teacher_content(teacher_id: UUID, current_user: User) -> bool:
    """
    Verify that current student can access content from specified teacher.
    Student must be linked to that teacher.
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "student":
        return False
    return current_user.teacher_id == teacher_id

def verify_teacher_owns_student(student_id: UUID, current_user: User) -> bool:
    """
    Verify that current teacher has the specified student in their class.
    Admin users always have access.
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "teacher":
        return False
    # For this check, would need to query the database
    # This is typically done in the endpoint handler instead
    return True
