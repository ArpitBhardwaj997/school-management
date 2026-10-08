# src/router/auth_router.py
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_admin
from src.auth.security import DUMMY_HASH, create_access_token, hash_password, settings, verify_password
from src.database.database import get_db
from src.dtos.schemas import AdminResponse, AdminSetup, TokenResponse
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


def _setup_open(db: Session) -> bool:
    """First-run setup is open only if SETUP_KEY is configured AND no admin exists yet."""
    return bool(settings.SETUP_KEY) and db.scalar(select(func.count(Admin.admin_id))) == 0


# GET /auth/setup-status   (lets the login page know whether to show "create admin")
@router.get("/setup-status")
def setup_status(db: Session = Depends(get_db)):
    return {"needs_setup": _setup_open(db)}


# POST /auth/setup   (creates the FIRST admin, then closes forever)
@router.post("/setup", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def setup_admin(data: AdminSetup, db: Session = Depends(get_db)):
    if not _setup_open(db):
        raise HTTPException(status_code=404, detail="Not found.")
    if not secrets.compare_digest(data.setup_key.encode(), settings.SETUP_KEY.encode()):
        raise HTTPException(status_code=403, detail="Invalid setup key.")
    try:
        admin = Admin(username=data.username, email=data.email, password_hash=hash_password(data.password))
    except ValueError:
        raise HTTPException(status_code=422, detail="Password too long.")
    try:
        db.add(admin)
        db.commit()
        db.refresh(admin)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists.")
    return admin