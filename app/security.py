import os
import hashlib
import base64
import uuid
import traceback
import bcrypt
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
PASSWORD_HASHING_VERSION = "3.1-always-intermediate"

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
    """Verify password using bcrypt directly with same MD5 hex transformation."""
    try:
        # Apply same transformation as get_password_hash()
        plain_password = str(plain_password) if not isinstance(plain_password, str) else plain_password
        password_bytes = plain_password.encode('utf-8', errors='replace')
        
        md5_hex = hashlib.md5(password_bytes).hexdigest()
        md5_hex_bytes = md5_hex.encode('utf-8')
        
        # Verify directly with bcrypt (bypass passlib)
        hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
        return bcrypt.checkpw(md5_hex_bytes, hashed_bytes)
    except Exception as e:
        print(f"[!] Verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly with MD5 hex intermediate."""
    print(f"[*] get_password_hash: START")
    
    try:
        # Convert to string and encode
        print(f"[*] get_password_hash: Converting to string")
        password = str(password) if not isinstance(password, str) else password
        password_bytes = password.encode('utf-8', errors='replace')
        print(f"[*] get_password_hash: Encoded to {len(password_bytes)} bytes")
        
        # Create MD5 hex intermediate
        print(f"[*] get_password_hash: Computing MD5 hash")
        md5_hex = hashlib.md5(password_bytes).hexdigest()
        print(f"[*] get_password_hash: MD5 hex created: {len(md5_hex)} chars")
        
        # Hash directly with bcrypt (bypass passlib)
        print(f"[*] get_password_hash: Encoding MD5 hex to bytes")
        md5_hex_bytes = md5_hex.encode('utf-8')
        print(f"[*] get_password_hash: MD5 hex encoded: {len(md5_hex_bytes)} bytes")
        
        print(f"[*] get_password_hash: Generating salt with bcrypt.gensalt()")
        salt = bcrypt.gensalt(rounds=12)
        print(f"[*] get_password_hash: Salt generated")
        
        print(f"[*] get_password_hash: Calling bcrypt.hashpw()")
        bcrypt_hash = bcrypt.hashpw(md5_hex_bytes, salt)
        print(f"[*] get_password_hash: Bcrypt hash created")
        
        # Return as string
        result = bcrypt_hash.decode('utf-8')
        print(f"[+] get_password_hash: SUCCESS, hash length: {len(result)}")
        return result
    except Exception as e:
        print(f"[!] get_password_hash: ERROR - {e}")
        raise

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
