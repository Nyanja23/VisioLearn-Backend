from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta
import jwt

from .. import schemas, models, security
from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..utils import generate_student_code, generate_teacher_code

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register/class-teacher", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_class_teacher(user: schemas.UserRegisterClassTeacher, db: Session = Depends(get_db)):
    """
    Class teacher registration endpoint.
    Creates both the user and a new class with auto-generated codes.
    
    Request body:
    - email: Class teacher's email address
    - full_name: Class teacher's full name
    - password: Strong password (12+ chars, uppercase, lowercase, digit, special char)
    - class_name: Name of the class (e.g., "Year 9 Science")
    
    Response:
    - User object with role=class_teacher
    - Also returns: class_id, student_code, teacher_code (via headers or extended response)
    """
    # Normalize email to lowercase
    normalized_email = user.email.lower()
    
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create class teacher user
    db_teacher = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="class_teacher",
        hashed_password=hashed_password
    )
    
    db.add(db_teacher)
    try:
        db.flush()  # Flush to get the ID without committing
        
        # Generate unique codes for the class
        student_code = generate_student_code()
        teacher_code = generate_teacher_code()
        
        # Ensure codes are unique (retry up to 5 times each)
        max_retries = 5
        for _ in range(max_retries):
            existing_student_code = db.query(models.Class).filter(models.Class.student_code == student_code).first()
            if not existing_student_code:
                break
            student_code = generate_student_code()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique student code. Please try again."
            )
        
        for _ in range(max_retries):
            existing_teacher_code = db.query(models.Class).filter(models.Class.teacher_code == teacher_code).first()
            if not existing_teacher_code:
                break
            teacher_code = generate_teacher_code()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique teacher code. Please try again."
            )
        
        # Create the class
        db_class = models.Class(
            class_name=user.class_name,
            class_teacher_id=db_teacher.id,
            student_code=student_code,
            teacher_code=teacher_code
        )
        
        db.add(db_class)
        db.commit()
        db.refresh(db_teacher)
        
        print(f"[+] Class teacher registered: {db_teacher.email}, Class: {user.class_name}, Student Code: {student_code}, Teacher Code: {teacher_code}")
        
    except Exception as e:
        db.rollback()
        print(f"[!] Error creating class teacher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create class teacher account. Please try again."
        )
    
    return db_teacher


@router.post("/register/subject-teacher", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_subject_teacher(user: schemas.UserRegisterSubjectTeacher, db: Session = Depends(get_db)):
    """
    Subject teacher registration endpoint.
    Creates a user and optionally adds them to a class with a subject assignment.
    
    Request body:
    - email: Subject teacher's email address
    - full_name: Subject teacher's full name
    - password: Strong password (12+ chars, uppercase, lowercase, digit, special char)
    - teacher_code: Valid class teacher code (format: TC-XXXX, optional for now)
    - subject_name: Subject to teach (optional, can be added later via class management endpoint)
    
    Response:
    - User object with role=subject_teacher
    """
    # Normalize email to lowercase
    normalized_email = user.email.lower()
    
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # If teacher_code provided, validate it
    if user.teacher_code:
        if len(user.teacher_code) != 7 or not user.teacher_code.startswith("TC-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher code format. Expected format: TC-XXXX"
            )
        
        # Find class with this teacher code
        class_obj = db.query(models.Class).filter(
            and_(
                models.Class.teacher_code == user.teacher_code,
                models.Class.is_deleted == False
            )
        ).first()
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher code not found. Please verify the code with your class teacher."
            )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create subject teacher user
    db_subject_teacher = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="subject_teacher",
        hashed_password=hashed_password
    )
    
    db.add(db_subject_teacher)
    try:
        db.flush()
        
        # If teacher_code and subject_name provided, create ClassSubject entry
        if user.teacher_code and user.subject_name:
            class_obj = db.query(models.Class).filter(models.Class.teacher_code == user.teacher_code).first()
            
            db_class_subject = models.ClassSubject(
                class_id=class_obj.id,
                subject_name=user.subject_name,
                subject_teacher_id=db_subject_teacher.id
            )
            db.add(db_class_subject)
        
        db.commit()
        db.refresh(db_subject_teacher)
        
        print(f"[+] Subject teacher registered: {db_subject_teacher.email}")
        
    except Exception as e:
        db.rollback()
        print(f"[!] Error creating subject teacher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subject teacher account. Please try again."
        )
    
    return db_subject_teacher


@router.post("/register/student", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(user: schemas.UserRegisterStudent, db: Session = Depends(get_db)):
    """
    Student registration endpoint.
    Links student to a class via the student code.
    
    Request body:
    - email: Student's email address
    - full_name: Student's full name
    - password: Strong password (12+ chars, uppercase, lowercase, digit, special char)
    - student_code: Valid student code (format: SC-XXXX)
    
    Response:
    - User object with role=student
    
    Errors:
    - 400: Email already registered
    - 400: Invalid student code format
    - 404: Student code not found (class doesn't exist)
    """
    # Normalize email to lowercase
    normalized_email = user.email.lower()
    
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate student code format (SC-XXXX)
    if not user.student_code or len(user.student_code) != 7 or not user.student_code.startswith("SC-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid student code format. Expected format: SC-XXXX"
        )
    
    # Find class with this student code
    class_obj = db.query(models.Class).filter(
        and_(
            models.Class.student_code == user.student_code,
            models.Class.is_deleted == False
        )
    ).first()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student code not found. Please verify the code with your class teacher."
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user.password)
    
    # Create student user
    db_student = models.User(
        email=normalized_email,
        full_name=user.full_name,
        role="student",
        hashed_password=hashed_password
    )
    
    db.add(db_student)
    try:
        db.flush()
        
        # Create ClassMembership to link student to class
        db_membership = models.ClassMembership(
            class_id=class_obj.id,
            student_id=db_student.id
        )
        db.add(db_membership)
        db.commit()
        db.refresh(db_student)
        
        print(f"[+] Student registered: {db_student.email}, Class: {class_obj.class_name}")
        
    except Exception as e:
        db.rollback()
        print(f"[!] Error creating student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student account. Please try again."
        )
    
    return db_student


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
def register_legacy(user: schemas.UserRegisterClassTeacher, db: Session = Depends(get_db)):
    """
    Deprecated: Use /register/class-teacher, /register/subject-teacher, or /register/student instead.
    This endpoint is kept for backward compatibility only.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint deprecated. Use /api/v1/auth/register/class-teacher, /api/v1/auth/register/subject-teacher, or /api/v1/auth/register/student"
    )


@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Normalize email to lowercase for case-insensitive comparison
    normalized_email = request.email.lower()
    user = db.query(models.User).filter(models.User.email == normalized_email).first()
    
    if not user or not security.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
        
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    
    access_token = security.create_access_token(subject=user.id, role=user.role)
    refresh_token = security.create_refresh_token(subject=user.id)
    
    # Store refresh token in DB with transaction handling
    db_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to store refresh token: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete login. Please try again."
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # Use SELECT FOR UPDATE to prevent race conditions during token rotation
    # Also check expires_at to ensure token hasn't expired in database
    db_token = db.query(models.RefreshToken).filter(
        and_(
            models.RefreshToken.token == request.refresh_token,
            models.RefreshToken.revoked == False,
            models.RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    ).with_for_update().first()
    
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked, expired, or not found")

    # Revoke old refresh token (Token rotation strategy)
    db_token.revoked = True
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
        
    access_token = security.create_access_token(subject=user.id, role=user.role)
    new_refresh_token = security.create_refresh_token(subject=user.id)
    
    # Store new token
    new_db_token = models.RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_db_token)
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token. Please try again."
        )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(request: schemas.RefreshRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Revoke the given refresh token (only if it belongs to current user)
    db_token = db.query(models.RefreshToken).filter(
        and_(
            models.RefreshToken.token == request.refresh_token,
            models.RefreshToken.user_id == current_user.id
        )
    ).first()
    
    if db_token:
        db_token.revoked = True
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout. Please try again."
            )
    
    return {"success": True, "message": "Successfully logged out"}
