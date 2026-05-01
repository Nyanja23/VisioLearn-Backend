#!/usr/bin/env python
"""
Comprehensive verification script for admin account creation - FIXED VERSION.
Tests all admin endpoints and error handling.
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestRunner:
    def __init__(self):
        self.results = []
        self.admin_email = "admin@visiolearn.org"
        self.admin_password = "AdminPass123!@"
        self.admin_token = None
        self.school_id = None
        
    def log(self, test_name, status, details=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = "[+]" if status else "[-]"
        print(f"[{timestamp}] {symbol} {test_name}")
        if details:
            print(f"         {details}")
        self.results.append({"test": test_name, "passed": status, "details": details})
    
    def test_server_health(self):
        """Test if server is running"""
        print("\n=== SERVER HEALTH ===\n")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            self.log("Server is running", response.status_code == 200)
            return response.status_code == 200
        except Exception as e:
            self.log("Server health check", False, str(e))
            return False
    
    def test_create_bootstrap_admin(self):
        """Create a bootstrap admin for testing"""
        print("\n=== TEST 1: CREATE BOOTSTRAP ADMIN ===\n")
        
        test_email = f"testadmin_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": test_email,
            "full_name": "Test Admin",
            "password": self.admin_password,
            "role": "admin",
            "school_id": None
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/users/bootstrap", json=payload, timeout=10)
            
            if response.status_code == 201:
                user = response.json()
                self.admin_email = user['email']
                self.log("Bootstrap admin created", True, f"Email: {user['email']}")
                return True
            elif response.status_code == 403:
                self.log("Bootstrap admin exists", True, "Users already exist (will login to existing)")
                # If bootstrap already used, keep the default admin email set in __init__
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Create bootstrap admin", False, f"Status {response.status_code}: {error_msg}")
                return False
        except Exception as e:
            self.log("Bootstrap creation error", False, str(e))
            return False
    
    def test_admin_login(self):
        """Test POST /auth/login for admin"""
        print("\n=== TEST 2: ADMIN LOGIN ===\n")
        
        if not self.admin_email:
            # If bootstrap failed, skip login
            self.log("Admin login", False, "No admin email available")
            return False
        
        payload = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("Admin login successful", True, f"Token received (length: {len(self.admin_token)})")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Admin login", False, f"Status {response.status_code}: {error_msg}")
                return False
        except Exception as e:
            self.log("Admin login error", False, str(e))
            return False
    
    def test_create_school(self):
        """Test POST /schools (admin-only)"""
        print("\n=== TEST 3: CREATE SCHOOL ===\n")
        
        if not self.admin_token:
            self.log("Create school", False, "No admin token available")
            return False
        
        payload = {
            "name": f"Test School {uuid.uuid4().hex[:4]}",
            "region": "Test Region"
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/schools", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 201:
                school = response.json()
                self.school_id = school.get("id")
                self.log("School created", True, f"School ID: {str(school['id'])[:8]}...")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Create school", False, f"Status {response.status_code}: {error_msg}")
                print(f"         Full response: {response.text}")
                return False
        except Exception as e:
            self.log("Create school error", False, str(e))
            return False
    
    def test_create_admin_via_users(self):
        """Test POST /users to create another admin"""
        print("\n=== TEST 4: CREATE ADMIN VIA /users ===\n")
        
        if not self.admin_token:
            self.log("Create admin via /users", False, "No admin token available")
            return False
        
        new_email = f"newadmin_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": new_email,
            "full_name": "New Admin",
            "password": "NewAdminPass123!@",
            "role": "admin",
            "school_id": None
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/users/", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 201:
                user = response.json()
                self.log("New admin created", True, f"Email: {user['email']}, Role: {user['role']}")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Create admin via /users", False, f"Status {response.status_code}: {error_msg}")
                print(f"         Full response: {response.text}")
                return False
        except Exception as e:
            self.log("Create admin via /users error", False, str(e))
            return False
    
    def test_create_teacher_via_users(self):
        """Test POST /users to create teacher (admin-only)"""
        print("\n=== TEST 5: CREATE TEACHER VIA /users ===\n")
        
        if not self.admin_token:
            self.log("Create teacher via /users", False, "No admin token available")
            return False
        
        if not self.school_id:
            self.log("Create teacher via /users", False, "No school ID available")
            return False
        
        new_email = f"teacher_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": new_email,
            "full_name": "Admin-Created Teacher",
            "password": "AdminTeacher123!@",
            "role": "teacher",
            "school_id": str(self.school_id)
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/users/", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 201:
                user = response.json()
                self.log("Teacher created (via admin)", True, f"Email: {user['email']}, Role: {user['role']}")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Create teacher via /users", False, f"Status {response.status_code}: {error_msg}")
                print(f"         Full response: {response.text}")
                return False
        except Exception as e:
            self.log("Create teacher via /users error", False, str(e))
            return False
    
    def test_public_registration(self):
        """Test POST /auth/register for teacher"""
        print("\n=== TEST 6: PUBLIC REGISTRATION ===\n")
        
        if not self.school_id:
            self.log("Public registration", False, "No school ID available")
            return False
        
        new_email = f"selfreg_teacher_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": new_email,
            "full_name": "Self-Registered Teacher",
            "password": "SelfRegPass123!@",
            "role": "teacher",
            "school_id": str(self.school_id)
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=payload, timeout=10)
            
            if response.status_code == 201:
                user = response.json()
                self.log("Teacher self-registered", True, f"Email: {user['email']}, Role: {user['role']}")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Public registration", False, f"Status {response.status_code}: {error_msg}")
                print(f"         Full response: {response.text}")
                return False
        except Exception as e:
            self.log("Public registration error", False, str(e))
            return False
    
    def test_public_school_listing(self):
        """Test GET /schools/public"""
        print("\n=== TEST 7: PUBLIC SCHOOL LISTING ===\n")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/schools/public", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                schools = data.get("schools", [])
                if schools:
                    self.log("Public school listing", True, f"Found {len(schools)} schools")
                else:
                    self.log("Public school listing", True, "Found 0 schools (maybe created in this run)")
                return True
            else:
                error_msg = response.json().get("detail", response.text)
                self.log("Public school listing", False, f"Status {response.status_code}: {error_msg}")
                return False
        except Exception as e:
            self.log("Public school listing error", False, str(e))
            return False
    
    def test_admin_cant_register(self):
        """Test that public registration rejects admin role"""
        print("\n=== TEST 8: ADMIN ROLE REJECTION ===\n")
        
        payload = {
            "email": f"fake_admin_{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Fake Admin",
            "password": "FakeAdminPass123!@",
            "role": "admin",  # Try to create admin via public
            "school_id": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=payload, timeout=10)
            
            if response.status_code == 422:  # Validation error
                self.log("Admin role correctly rejected", True, "Public registration rejected admin role")
                return True
            else:
                self.log("Admin role rejection", False, f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log("Admin role rejection error", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("\n" + "="*70)
        print("VISIOLEARN ADMIN ACCOUNT CREATION - VERIFICATION SUITE")
        print("="*70)
        
        # Check server health first
        if not self.test_server_health():
            print("\n[-] SERVER NOT RUNNING - Cannot proceed with tests")
            return False
        
        # Run all tests
        self.test_create_bootstrap_admin()
        self.test_admin_login()
        self.test_create_school()
        self.test_create_admin_via_users()
        self.test_create_teacher_via_users()
        self.test_public_registration()
        self.test_public_school_listing()
        self.test_admin_cant_register()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n[+] ALL TESTS PASSED - System is ready for production!\n")
            return True
        else:
            print(f"\n[-] {total - passed} test(s) failed - See details above\n")
            return False

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    exit(0 if success else 1)
