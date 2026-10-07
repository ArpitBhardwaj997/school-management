# src/router/class_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dtos.schemas import ClassCreate, ClassResponse, ClassUpdate
from src.models.model import SchoolClass

router = APIRouter(prefix="/classes", tags=["Classes"])


def get_class_or_404(db: Session, class_id: int) -> SchoolClass:
    school_class = db.get(SchoolClass, class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail=f"Class with ID {class_id} not found.")
    return school_class


# POST /classes
@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(data: ClassCreate, db: Session = Depends(get_db)):
    new_class = SchoolClass(class_name=data.class_name)
    try:
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
    except IntegrityError:
        db.rollback()
        # class_name is the only UNIQUE column, so a duplicate name is the cause
        raise HTTPException(status_code=409, detail=f"Class '{data.class_name}' already exists.")
    return new_class


# GET /classes?skip=0&limit=50
@router.get("", response_model=list[ClassResponse])
def list_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(SchoolClass).order_by(SchoolClass.class_id).offset(skip).limit(limit)
    return db.scalars(query).all()


# GET /classes/{class_id}
@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    return get_class_or_404(db, class_id)


# PUT /classes/{class_id}
@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, data: ClassUpdate, db: Session = Depends(get_db)):
    school_class = get_class_or_404(db, class_id)
    school_class.class_name = data.class_name
    try:
        db.commit()
        db.refresh(school_class)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Class '{data.class_name}' already exists.")
    return school_class


# DELETE /classes/{class_id}
@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    school_class = get_class_or_404(db, class_id)
    try:
        db.delete(school_class)
        db.commit()
    except IntegrityError:
        # Students / fee_structure rows still point to this class.
        # (With students loaded, SQLAlchemy tries to set their class_id to NULL,
        # which the NOT NULL rule rejects -- either way it is an IntegrityError.)
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this class: students or fee structures still use it.",
        )
    return None