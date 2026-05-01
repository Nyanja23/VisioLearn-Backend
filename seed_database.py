#!/usr/bin/env python3
"""
Database seed script to initialize production database with test data.
Run this after migrations: python seed_database.py
"""

import os
import sys



from sqlalchemy.orm import Session
from app.security import get_password_hash

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models

# Use central password hashing helper for consistent behavior

def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(models.User).first()
        if existing_users:
            print("❌ Database already seeded. Aborting to prevent duplicates.")
            return
        
        print("🌱 Seeding database...")
        print()
        
        # Create a school (admin doesn't need a school, but teachers do)
        school = models.School(
            id="f5c8f3b1-2a4c-4d6e-8f0a-1b3c5d7e9f1a",
            name="Demo School",
            region="Demo Region"
        )
        db.add(school)
        print("✓ Created demo school")
        
        # Create admin user
        admin_password = "AdminPass123!@"
        admin = models.User(
            email="admin@visiolearn.org",
            full_name="System Administrator",
            role="admin",
            hashed_password=get_password_hash(admin_password),
            school_id=None  # Admin doesn't belong to a school
        )
        db.add(admin)
        print(f"✓ Created admin user: admin@visiolearn.org")
        
        # Create test teacher
        teacher_password = "TeacherPass123!@"
        teacher = models.User(
            email="teacher@visiolearn.org",
            full_name="Demo Teacher",
            role="teacher",
            hashed_password=get_password_hash(teacher_password),
            school_id="f5c8f3b1-2a4c-4d6e-8f0a-1b3c5d7e9f1a"
        )
        db.add(teacher)
        print(f"✓ Created teacher user: teacher@visiolearn.org")
        
        # Create test student
        student_password = "StudentPass123!@"
        student = models.User(
            email="student@visiolearn.org",
            full_name="Demo Student",
            role="student",
            hashed_password=get_password_hash(student_password),
            school_id="f5c8f3b1-2a4c-4d6e-8f0a-1b3c5d7e9f1a"
        )
        db.add(student)
        print(f"✓ Created student user: student@visiolearn.org")
        
        # Commit all changes
        db.commit()
        print()
        print("✅ Database seeded successfully!")
        print()
        print("Test Credentials:")
        print("─" * 60)
        print(f"Admin:")
        print(f"  Email: admin@visiolearn.org")
        print(f"  Password: {admin_password}")
        print()
        print(f"Teacher:")
        print(f"  Email: teacher@visiolearn.org")
        print(f"  Password: {teacher_password}")
        print()
        print(f"Student:")
        print(f"  Email: student@visiolearn.org")
        print(f"  Password: {student_password}")
        print("─" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("VisioLearn Database Seeder")
    print("=" * 60)
    print()
    seed_database()
