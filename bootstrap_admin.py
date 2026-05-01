#!/usr/bin/env python
"""
Manual bootstrap script to create admin user on Render or any PostgreSQL instance.
Run this if the admin wasn't created automatically during startup.

Usage: python bootstrap_admin.py
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL (from Render environment or use SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[!] DATABASE_URL not set. Using SQLite fallback.")
    DATABASE_URL = "sqlite:///./visiolearn.db"
else:
    print(f"[*] Using PostgreSQL database from Render")

# Import models AFTER setting up the database
from app.database import Base
from app.models import User
from app.security import get_password_hash

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print(f"[*] Database URL: {DATABASE_URL.split('@')[0]}...")
print("[*] Connecting to database...")

try:
    db = SessionLocal()
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@visiolearn.org").first()
    
    if existing_admin:
        print(f"[!] Admin already exists!")
        print(f"    Email: {existing_admin.email}")
        print(f"    Role: {existing_admin.role}")
        print(f"    ID: {existing_admin.id}")
        db.close()
        sys.exit(0)
    
    # Create admin user
    print("[*] Creating bootstrap admin user...")
    admin = User(
        email="admin@visiolearn.org",
        full_name="System Administrator",
        role="admin",
        hashed_password=get_password_hash("AdminPass123!@"),
        school_id=None
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"[+] SUCCESS! Admin user created:")
    print(f"    Email: {admin.email}")
    print(f"    Role: {admin.role}")
    print(f"    ID: {admin.id}")
    print(f"\n    Login credentials:")
    print(f"    Email: admin@visiolearn.org")
    print(f"    Password: AdminPass123!@")
    
    db.close()
    
except Exception as e:
    print(f"[!] ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
