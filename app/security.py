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

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    try:
        normalized = _normalize_password_for_bcrypt(plain_password)
        return pwd_context.verify(normalized, hashed_password)
    except Exception as e:
        print(f"[!] Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        normalized = _normalize_password_for_bcrypt(password)
        return pwd_context.hash(normalized)
    except Exception as e:
        print(f"[!] Password hashing error: {e}")
        # Fallback: return a placeholder hash (this shouldn't happen in production)
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
