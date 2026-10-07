# src/auth/security.py  -- password hashing + JWT (no database code here)
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from src.settings.settings import Settings

settings = Settings()

MAX_PASSWORD_BYTES = 72  # bcrypt only uses the first 72 bytes


def _to_bytes(password: str) -> bytes:
    data = password.encode("utf-8")
    if len(data) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Password too long (max {MAX_PASSWORD_BYTES} bytes).")
    return data


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(password), password_hash.encode("utf-8"))
    except ValueError:  # too-long password or a malformed hash in the database
        return False


# Used when the username does not exist, so a wrong username takes as long
# to answer as a wrong password (stops attackers from guessing usernames).
DUMMY_HASH = hash_password("dummy-password-for-timing")


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> tuple[str, int]:
    """Return (token, seconds_until_expiry). Every token is unique (jti) and expires (exp)."""
    minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES if expires_minutes is None else expires_minutes
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,                          # who the token belongs to (admin_id)
        "iat": now,                              # issued at
        "exp": now + timedelta(minutes=minutes), # expires at
        "jti": uuid.uuid4().hex,                 # unique id -> new token on every login
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, minutes * 60


def decode_access_token(token: str) -> dict:
    """Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],  # fixed list: blocks the "alg: none" trick
        options={"require": ["exp", "iat", "sub"]},
    )