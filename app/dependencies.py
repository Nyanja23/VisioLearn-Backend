"""
Role-Based Access Control (RBAC) Middleware and Dependencies

Class-Based Multi-Subject Architecture:
- Admin: System administrator, full access to all resources
- ClassTeacher: Manages one class, has two auto-generated codes (student_code, teacher_code)
  - Views all students in their class
  - Views all subject teachers in their class
  - Sees matrix view of student progress across all subjects
- SubjectTeacher: Teaches one or more subjects in classes (joined via teacher_code)
  - Uploads content for their subject(s) only
  - Sees progress only for their subject(s)
  - Can teach multiple subjects (not restricted to 1 subject)
- Student: Member of a class (joined via student_code), has multiple subject teachers
  - Views and accesses content from all subject teachers in their class
  - Logs progress for each content item
  - Sees their own progress across all subjects

Access Control Rules:
1. ClassTeacher can upload/delete content only for classes they manage
2. SubjectTeacher can upload/delete content only for their subject in assigned classes
3. Student can access only content from subjects in their class
4. ClassTeacher can view all students and all subject progress in their class
5. SubjectTeacher can view only progress for their subject
6. Student cannot view other students' progress

This is enforced both at:
- Dependency level (require_admin, require_class_teacher, require_subject_teacher, require_student)
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
from .models import User, Class, ClassSubject
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
require_class_teacher = RoleChecker(["admin", "class_teacher"])
require_subject_teacher = RoleChecker(["admin", "subject_teacher"])
require_student = RoleChecker(["student"])

# Backward compatibility aliases (deprecated)
require_teacher = require_class_teacher  # Maps old "teacher" role to "class_teacher"

# Helper functions for resource ownership validation

def verify_class_teacher_owns_class(class_id: UUID, current_user: User, db: Session) -> bool:
    """
    Verify that current user is the class teacher for the specified class.
    Admin users always have access.
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "class_teacher":
        return False
    
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        return False
    return class_obj.class_teacher_id == current_user.id

def verify_subject_teacher_can_teach_subject(subject_id: UUID, current_user: User, db: Session) -> bool:
    """
    Verify that current user (subject teacher) can teach the specified subject.
    Admin users always have access.
    Subject teachers can teach multiple subjects (not restricted to 1).
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "subject_teacher":
        return False
    
    subject = db.query(ClassSubject).filter(ClassSubject.id == subject_id).first()
    if not subject:
        return False
    return subject.subject_teacher_id == current_user.id

def verify_student_in_class(class_id: UUID, current_user: User, db: Session) -> bool:
    """
    Verify that current student is a member of the specified class.
    Admin users always have access.
    """
    if current_user.role == "admin":
        return True
    if current_user.role != "student":
        return False
    
    from .models import ClassMembership
    membership = db.query(ClassMembership).filter(
        ClassMembership.class_id == class_id,
        ClassMembership.student_id == current_user.id,
        ClassMembership.left_at == None  # Still a member (not left)
    ).first()
    return membership is not None

def verify_student_can_access_content(class_id: UUID, subject_id: UUID, current_user: User, db: Session) -> bool:
    """
    Verify that current student can access content in the specified class and subject.
    Student must be in the class and the subject must exist in that class.
    """
    if not verify_student_in_class(class_id, current_user, db):
        return False
    
    subject = db.query(ClassSubject).filter(
        ClassSubject.id == subject_id,
        ClassSubject.class_id == class_id
    ).first()
    return subject is not None
