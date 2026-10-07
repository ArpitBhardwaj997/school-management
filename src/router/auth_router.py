# src/router/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_admin
from src.auth.security import DUMMY_HASH, create_access_token, verify_password
from src.database.database import get_db
from src.dtos.schemas import AdminResponse, TokenResponse
from src.models.model import Admin

router = APIRouter(prefix="/auth", tags=["Auth"])


# POST /auth/login   (form fields: username, password)
@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.scalar(select(Admin).where(Admin.username == form.username))

    # Always run one bcrypt check, even for an unknown username (same timing)
    password_ok = verify_password(form.password, admin.password_hash if admin else DUMMY_HASH)

    if not admin or not password_ok:
        # Same message for wrong username and wrong password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(subject=str(admin.admin_id))
    return TokenResponse(access_token=token, token_type="bearer", expires_in=expires_in)


# GET /auth/me   (needs a valid token)
@router.get("/me", response_model=AdminResponse)
def me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin