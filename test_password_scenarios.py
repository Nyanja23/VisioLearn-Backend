#!/usr/bin/env python3
"""Test teacher registration with password hashing fix."""

import asyncio
from app.security import get_password_hash, verify_password

async def test_teacher_registration():
    """Test the exact scenario from the error."""
    print("[*] Testing teacher registration scenario...")
    print()
    
    # Test passwords from different scenarios
    test_cases = [
        ("StrongPass1%", "Original error password"),
        ("AdminPass123!@", "Admin creation password"),
        ("a" * 60, "60-character password"),
        ("a" * 72, "72-character password"),
        ("a" * 80, "80-character password (should truncate)"),
    ]
    
    for password, description in test_cases:
        print(f"[*] Testing: {description}")
        print(f"    Password: {password[:30]}{'...' if len(password) > 30 else ''}")
        byte_len = len(password.encode('utf-8'))
        print(f"    Length: {len(password)} chars, {byte_len} bytes")
        
        try:
            hashed = get_password_hash(password)
            is_valid = verify_password(password, hashed)
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"    {status}: Hash succeeded and verification works")
        except Exception as e:
            print(f"    ✗ FAIL: {e}")
        print()
    
    print("[+] All password hashing tests completed!")

if __name__ == "__main__":
    asyncio.run(test_teacher_registration())
