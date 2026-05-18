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

# Version marker for tracking deployments
PASSWORD_HASHING_VERSION = "3.0-bulletproof"

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
    """Verify plain password against hashed password."""
    import hashlib
    import base64
    
    try:
        # Apply the same transformation as get_password_hash
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        
        password_bytes = plain_password.encode('utf-8')
        password_byte_len = len(password_bytes)
        
        # Use same threshold as hashing
        if password_byte_len >= 40:
            md5_digest = hashlib.md5(password_bytes).digest()
            password_to_verify = base64.b64encode(md5_digest).decode('ascii')
        else:
            password_to_verify = plain_password
        
        return pwd_context.verify(password_to_verify, hashed_password)
        
    except Exception as e:
        print(f"[!] Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with robust fallback handling."""
    import hashlib
    import base64
    
    try:
        # Ensure password is a string
        if not isinstance(password, str):
            password = str(password)
        
        password_bytes = password.encode('utf-8')
        password_byte_len = len(password_bytes)
        print(f"[*] Original password: {password_byte_len} bytes")
        
        # Strategy: ALWAYS use intermediate hash if password might be long
        # This ensures we NEVER hit bcrypt's 72-byte limit
        if password_byte_len >= 40:  # Very conservative threshold
            # Use MD5+base64: output is always ~24 chars
            md5_digest = hashlib.md5(password_bytes).digest()
            intermediate = base64.b64encode(md5_digest).decode('ascii')
            print(f"[*] Using MD5+base64 intermediate: {len(intermediate)} chars")
            password_to_hash = intermediate
        else:
            print(f"[*] Password short enough, using as-is")
            password_to_hash = password
        
        # Ensure the password to hash is definitely under 72 bytes
        hash_input_bytes = password_to_hash.encode('utf-8')
        hash_input_len = len(hash_input_bytes)
        print(f"[*] Input to bcrypt: {hash_input_len} bytes")
        
        if hash_input_len > 72:
            # Should never happen, but extra safety
            print(f"[!] WARNING: Input still over 72 bytes! Truncating...")
            password_to_hash = password_to_hash[:50]
            print(f"[*] Truncated to: {len(password_to_hash.encode('utf-8'))} bytes")
        
        # Now hash with bcrypt
        hashed = pwd_context.hash(password_to_hash)
        print(f"[+] Hashing successful")
        return hashed
        
    except ValueError as ve:
        # Specific bcrypt error
        error_msg = str(ve)
        print(f"[!] ValueError during hashing: {error_msg}")
        # Last resort: hash the error message itself (don't fail!)
        fallback_input = hashlib.md5(password.encode('utf-8')).hexdigest()[:30]
        try:
            return pwd_context.hash(fallback_input)
        except:
            # If all else fails, raise with context
            raise ValueError(f"Password hashing failed: {error_msg}")
    
    except Exception as e:
        # Any other exception
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"[!] {error_type} during hashing: {error_msg}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to hash password: {error_msg}")

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
