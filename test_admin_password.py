from app.database import SessionLocal, engine
from app.models import User, School, RefreshToken, LessonNote, LearningUnit, StudentProgress
from app.security import verify_password, get_password_hash

# Create tables
print("[*] Creating tables...")
tables_to_create = [
    School,
    User,
    RefreshToken,
    LessonNote,
    LearningUnit,
    StudentProgress,
]

for table_class in tables_to_create:
    table_class.__table__.create(bind=engine, checkfirst=True)
    print(f"  [+] {table_class.__tablename__}")

print("[+] Tables created\n")

# Test admin creation
db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@visiolearn.org').first()

if not admin:
    print("[*] Creating admin...")
    admin = User(
        email='admin@visiolearn.org',
        full_name='System Administrator',
        role='admin',
        hashed_password=get_password_hash('AdminPass123!@'),
        school_id=None
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"[+] Admin created with email: {admin.email}\n")
else:
    print(f"[+] Admin already exists: {admin.email}\n")

# Test password verification
password = 'AdminPass123!@'
is_valid = verify_password(password, admin.hashed_password)
print(f"[*] Testing password verification for '{password}'")
print(f"  Result: {is_valid}")
print(f"  Stored hash: {admin.hashed_password[:60]}...")

db.close()
print("\n[+] Test complete")

