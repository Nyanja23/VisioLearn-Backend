import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Login
print("[*] Testing login...")
login_resp = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"email": "admin@visiolearn.org", "password": "AdminPass123!@"},
    timeout=10
)
print(f"  Status: {login_resp.status_code}")
if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    print(f"  [+] Token received: {token[:50]}...")
else:
    print(f"  [-] Error: {login_resp.text}")
    exit(1)

# Test 2: Create school with trailing slash
print("\n[*] Testing POST /api/v1/schools/ (with trailing slash)...")
school_resp = requests.post(
    f"{BASE_URL}/api/v1/schools/",
    json={"name": "Test School 1", "region": "Region 1"},
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
    allow_redirects=False
)
print(f"  Status: {school_resp.status_code}")
if school_resp.status_code == 307:
    print(f"  Location: {school_resp.headers.get('location')}")
    # Follow redirect
    school_resp = requests.post(
        f"{BASE_URL}/api/v1/schools/",
        json={"name": "Test School 1", "region": "Region 1"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        allow_redirects=True
    )
    print(f"  After redirect status: {school_resp.status_code}")
    print(f"  Response: {school_resp.text[:200]}")
elif school_resp.status_code == 200:
    print(f"  [+] School created: {school_resp.json()}")
else:
    print(f"  [-] Error: {school_resp.text[:200]}")

# Test 3: Create school without trailing slash
print("\n[*] Testing POST /api/v1/schools (no trailing slash)...")
school_resp2 = requests.post(
    f"{BASE_URL}/api/v1/schools",
    json={"name": "Test School 2", "region": "Region 2"},
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
    allow_redirects=False
)
print(f"  Status: {school_resp2.status_code}")
if school_resp2.status_code == 307:
    print(f"  Location: {school_resp2.headers.get('location')}")
elif school_resp2.status_code == 200:
    print(f"  [+] School created: {school_resp2.json()}")
else:
    print(f"  [-] Error: {school_resp2.text[:200]}")

# Test 4: List public schools
print("\n[*] Testing GET /api/v1/schools/public...")
public_resp = requests.get(f"{BASE_URL}/api/v1/schools/public", timeout=10)
print(f"  Status: {public_resp.status_code}")
print(f"  Response: {public_resp.json()}")
