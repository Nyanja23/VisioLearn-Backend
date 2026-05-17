#!/usr/bin/env python3
"""Test the bcrypt password hashing fix."""

from app.security import get_password_hash, verify_password

# Test with the exact password from the error
test_password = 'StrongPass1%'
print(f'[*] Testing with password: {test_password}')
byte_len = len(test_password.encode('utf-8'))
print(f'[*] Password length: {len(test_password)} chars, {byte_len} bytes')

try:
    hashed = get_password_hash(test_password)
    print(f'[+] Hash succeeded: {hashed[:50]}...')
    
    # Verify it works
    is_valid = verify_password(test_password, hashed)
    print(f'[+] Verification: {is_valid}')
    print('[+] Password hashing test PASSED!')
except Exception as e:
    print(f'[!] Error: {e}')
    import traceback
    traceback.print_exc()
