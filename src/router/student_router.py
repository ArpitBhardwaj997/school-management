# src/router/student_router.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dtos.schemas import StudentCreate, StudentResponse
from src.models.model import SchoolClass, Student

router = APIRouter(prefix="/students", tags=["Students"])


# ---------- helpers ----------
def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")
    return student


def ensure_class_exists(db: Session, class_id: int) -> None:
    if not db.get(SchoolClass, class_id):
        raise HTTPException(status_code=404, detail=f"Class ID {class_id} does not exist.")


# ---------- routes ----------
# POST /students   (class_id comes in the body)
@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def register_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    ensure_class_exists(db, student_data.class_id)
    # exclude_none: omitted optional fields are left out so DB defaults apply
    new_student = Student(**student_data.model_dump(exclude_none=True))
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="The database rejected this data (constraint violation).")
    return new_student


# GET /students?skip=0&limit=50&class_id=1
@router.get("", response_model=list[StudentResponse])
def get_all_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = select(Student).order_by(Student.student_id)
    if class_id is not None:
        query = query.where(Student.class_id == class_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


# GET /students/{student_id}
@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    return get_student_or_404(db, student_id)


# PUT /students/{student_id}
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentCreate, db: Session = Depends(get_db)):
    student = get_student_or_404(db, student_id)
    ensure_class_exists(db, student_data.class_id)

    # exclude_unset: fields the client did not send are left unchanged
    for field, value in student_data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="The database rejected this data (constraint violation).")
    return student


# DELETE /students/{student_id}
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = get_student_or_404(db, student_id)
    # WARNING: payments.student_id is ON DELETE CASCADE, so this also
    # permanently deletes all payment records of this student.
    db.delete(student)
    db.commit()
    return None