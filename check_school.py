#!/usr/bin/env python
"""Check and assign school to user"""
from app.database import SessionLocal
from app import models
from uuid import uuid4

db = SessionLocal()

try:
    # Get your user (the one you logged in with - appears to be admin)
    user = db.query(models.User).filter(models.User.role == "admin").first()

    if user:
        print(f"✓ Found user: {user.full_name} ({user.email})")
        print(f"  ID: {user.id}")
        print(f"  Role: {user.role}")
        print(f"  School ID: {user.school_id}")
        
        if not user.school_id:
            print("\n⚠️ User has no school assigned!")
            
            # Check if any schools exist
            schools = db.query(models.School).all()
            if schools:
                print(f"\n✓ Found {len(schools)} existing schools:")
                for school in schools:
                    print(f"  - {school.name} (ID: {school.id})")
                # Assign to first school
                user.school_id = schools[0].id
                db.commit()
                print(f"\n✓ Assigned user to: {schools[0].name}")
            else:
                print("\n✗ No schools exist. Creating default school...")
                school = models.School(
                    id=uuid4(),
                    name="Default School",
                    region="Unknown"
                )
                db.add(school)
                db.commit()
                print(f"✓ Created school: {school.name} (ID: {school.id})")
                user.school_id = school.id
                db.commit()
                print(f"✓ Assigned user to school: {school.name}")
        else:
            school = db.query(models.School).filter(models.School.id == user.school_id).first()
            if school:
                print(f"  School: {school.name}")
                print("\n✓ User is properly configured for uploading!")
    else:
        print("✗ No admin user found")

finally:
    db.close()
