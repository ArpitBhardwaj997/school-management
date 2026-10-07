# app.py  (run with: fastapi dev app.py)
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_admin
from src.database.database import get_db
from src.router import auth_router, class_router, fee_router, payment_router, student_router

app = FastAPI(
    title="School Management System",
    description="API for managing school data",
    version="1.0.0",
)

# Only needed if you open the frontend from another address (e.g. VS Code Live Server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Open routes: /auth/login, /health, /
app.include_router(auth_router.router)

# Every route below needs a valid admin token
protected = [Depends(get_current_admin)]
app.include_router(class_router.router, dependencies=protected)
app.include_router(student_router.router, dependencies=protected)
app.include_router(fee_router.router, dependencies=protected)
app.include_router(payment_router.router, dependencies=protected)


@app.get("/")
def read_root():
    return {"message": "School Management System API"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "healthy"}


# Frontend: open http://127.0.0.1:8000/app/   (keep this LAST, after all routes)
app.mount("/app", StaticFiles(directory=Path(__file__).parent / "frontend", html=True), name="frontend")