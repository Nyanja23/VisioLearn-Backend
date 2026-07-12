import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_dev_only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 90))

# A guessable signing key makes every JWT forgeable. Refuse to boot in
# production without a real one; the dev fallback stays for local SQLite runs.
if os.getenv("ENVIRONMENT") == "production" and not os.getenv("SECRET_KEY"):
    raise RuntimeError(
        "SECRET_KEY environment variable must be set in production"
    )

# Version marker for tracking deployments
PASSWORD_HASHING_VERSION = "3.2-md5-intermediate-clean"


def _bcrypt_input(password: str) -> bytes:
    """The exact bytes fed to bcrypt for a given password.

    Every password is first reduced to its MD5 hex digest (32 ASCII chars).
    MD5 here is NOT the password hash — bcrypt is — it only maps arbitrary
    length input to a fixed size below bcrypt's hard 72-byte limit, so long
    passwords and multi-byte characters never truncate silently.

    This transformation is baked into every hash already stored in the
    production database. Changing it (e.g. to SHA-256) would lock out all
    existing accounts unless a rehash-on-login migration ships with it.
    """
    password = str(password) if not isinstance(password, str) else password
    password_bytes = password.encode("utf-8", errors="replace")
    return hashlib.md5(password_bytes).hexdigest().encode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        hashed_bytes = (
            hashed_password.encode("utf-8")
            if isinstance(hashed_password, str)
            else hashed_password
        )
        return bcrypt.checkpw(_bcrypt_input(plain_password), hashed_bytes)
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(_bcrypt_input(password), salt).decode("utf-8")


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
