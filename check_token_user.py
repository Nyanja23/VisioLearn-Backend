#!/usr/bin/env python
"""Check token user and assign school"""
import jwt
from app.security import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
from app import models
from uuid import uuid4

# Your token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzY1OTkwOTYsInN1YiI6ImE2YjgzMzQyLTk0ZjktNGYxZC1hMGYwLTI2ZWZjNzk0MjI3NyIsInJvbGUiOiJhZG1pbiJ9.3fbeq-Ekfu84nq1LVNQXl0NccGFwcaKe-xXQdlbTG9w"

try:
    # Decode token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('sub')
    print(f"✓ Token belongs to user ID: {user_id}")
    
    db = SessionLocal()
    
    # Get that user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user:
        print(f"✓ Found user: {user.full_name} ({user.email})")
        print(f"  Role: {user.role}")
        print(f"  School ID: {user.school_id}")
        
        if not user.school_id:
            print("\n⚠️ This user has no school assigned!")
            
            # Check if any schools exist
            schools = db.query(models.School).all()
            if schools:
                print(f"✓ Found {len(schools)} schools:")
                for school in schools:
                    print(f"  - {school.name}")
                # Assign to first school
                user.school_id = schools[0].id
                db.commit()
                print(f"\n✓ Assigned user to: {schools[0].name}")
            else:
                print("✗ No schools exist!")
        else:
            school = db.query(models.School).filter(models.School.id == user.school_id).first()
            if school:
                print(f"  School: {school.name}")
                print("\n✓ User is ready for upload!")
    else:
        print(f"✗ User not found: {user_id}")
    
    db.close()

except jwt.InvalidTokenError as e:
    print(f"✗ Invalid token: {e}")
