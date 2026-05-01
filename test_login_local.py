import requests
import json

BASE = "http://localhost:8000"

print("[*] Testing login with bootstrap admin credentials...\n")

# Test 1: Check if admin exists in database
print("[1] Checking database...")
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@visiolearn.org").first()
if admin:
    print(f"    [+] Admin found in database")
    print(f"       Email: {admin.email}")
    print(f"       Role: {admin.role}")
    print(f"       Hash (first 50 chars): {admin.hashed_password[:50]}")
else:
    print(f"    [-] Admin NOT found in database!")
    all_users = db.query(User).all()
    print(f"    Total users: {len(all_users)}")
    for u in all_users:
        print(f"       - {u.email} ({u.role})")
db.close()

# Test 2: Try login via API
print("\n[2] Testing login via API...")
response = requests.post(
    f"{BASE}/api/v1/auth/login",
    json={"email": "admin@visiolearn.org", "password": "AdminPass123!@"},
    timeout=10
)

print(f"    Status: {response.status_code}")
print(f"    Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Try with different passwords to debug
if response.status_code != 200:
    print("\n[3] Trying to understand the issue...")
    
    # Test with wrong password
    response2 = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"email": "admin@visiolearn.org", "password": "WRONGPASSWORD"},
        timeout=10
    )
    print(f"    Wrong password status: {response2.status_code}")
    print(f"    Wrong password response: {response2.json()}")
    
    # Test with wrong email
    response3 = requests.post(
        f"{BASE}/api/v1/auth/login",
        json={"email": "notexist@test.com", "password": "AdminPass123!@"},
        timeout=10
    )
    print(f"    Wrong email status: {response3.status_code}")
    print(f"    Wrong email response: {response3.json()}")
