# src/auth/dependencies.py  -- the guard that protects routes
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.auth.security import decode_access_token
from src.database.database import get_db
from src.models.model import Admin

# tokenUrl makes the "Authorize" button in /docs work
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid token.")

    try:
        admin_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise _unauthorized("Invalid token.")

    admin = db.get(Admin, admin_id)
    if not admin:  # e.g. the admin row was deleted after the token was issued
        raise _unauthorized("Invalid token.")
    return admin