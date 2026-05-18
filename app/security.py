import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_dev_only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 90))

# Initialize CryptContext with explicit bcrypt configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)


def _normalize_password_for_bcrypt(password: str) -> str:
    """Normalize a password for bcrypt: ensure it's at most 72 bytes.

    Bcrypt limits input to 72 bytes. To behave deterministically across
    hashing and verification, cut the UTF-8 encoded bytes to 72 and
    decode back to a string ignoring partial multi-byte sequences.

    Returns the (possibly truncated) string to use for hashing/verification.
    """
    if password is None:
        return ""
    try:
        raw = password.encode("utf-8")
    except Exception:
        # If encoding fails for some reason, fall back to the original string
        return password

    if len(raw) <= 72:
        return password

    truncated = raw[:72]
    safe = truncated.decode("utf-8", errors="ignore")
    print("[!] Password longer than 72 bytes — truncating to bcrypt limit")
    return safe


def _hash_long_password(password: str) -> str:
    """Pre-hash long passwords to ensure bcrypt compatibility.
    
    Uses MD5 + base64 encoding to create a fixed-length, safe input
    for bcrypt that's guaranteed to be well under 72 bytes.
    """
    import hashlib
    import base64
    
    password_bytes = password.encode('utf-8')
    
    # If password is already short enough, return as-is (simple case)
    if len(password_bytes) <= 50:  # Conservative: 50 bytes of margin
        return password
    
    # For longer passwords, use MD5 + base64 (compact representation)
    # MD5 is 16 bytes -> base64 is ~24 chars, very safe for bcrypt
    try:
        md5_hash = hashlib.md5(password_bytes).digest()
        b64_hash = base64.b64encode(md5_hash).decode('ascii')
        print(f"[!] Password too long ({len(password_bytes)} bytes) - using MD5+base64 intermediate")
        return b64_hash
    except Exception as e:
        print(f"[!] Intermediate hashing failed: {e}")
        # Fallback: truncate directly
        return password[:50]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password.
    
    Handles both:
    1. Passwords hashed with SHA256 intermediate (for >72 byte passwords)
    2. Regular passwords (for <=72 byte passwords)
    """
    try:
        # Apply the same intermediate hashing as get_password_hash
        # This handles both short and long passwords consistently
        intermediate = _hash_long_password(plain_password)
        normalized = _normalize_password_for_bcrypt(intermediate)
        
        return pwd_context.verify(normalized, hashed_password)
        
    except Exception as e:
        print(f"[!] Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with intermediate hashing for safety."""
    try:
        # Step 1: Apply intermediate hashing if needed
        intermediate = _hash_long_password(password)
        print(f"[*] Intermediate hash length: {len(intermediate)} chars, {len(intermediate.encode('utf-8'))} bytes")
        
        # Step 2: Normalize for bcrypt (max 72 bytes)
        normalized = _normalize_password_for_bcrypt(intermediate)
        print(f"[*] Normalized length: {len(normalized)} chars, {len(normalized.encode('utf-8'))} bytes")
        
        # Step 3: Hash with bcrypt
        try:
            hash_result = pwd_context.hash(normalized)
            print(f"[+] Password hashing succeeded")
            return hash_result
        except Exception as bcrypt_error:
            print(f"[!] Bcrypt error: {bcrypt_error}")
            # If still failing, force truncate to 50 bytes
            truncated = normalized[:50]
            print(f"[!] Force truncating to 50 chars: {len(truncated)} chars, {len(truncated.encode('utf-8'))} bytes")
            return pwd_context.hash(truncated)
        
    except Exception as e:
        print(f"[!] Password hashing error: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to hash password: {e}")

def create_access_token(subject: Union[str, Any], role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
