# src/router/fee_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dtos.schemas import FeeCreate, FeeResponse, FeeUpdate
from src.models.model import FeeStructure, SchoolClass

router = APIRouter(prefix="/fees", tags=["Fee Structure"])


def get_fee_or_404(db: Session, fee_id: int) -> FeeStructure:
    fee = db.get(FeeStructure, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail=f"Fee structure with ID {fee_id} not found.")
    return fee


# POST /fees   (one fee structure per class)
@router.post("", response_model=FeeResponse, status_code=status.HTTP_201_CREATED)
def create_fee(data: FeeCreate, db: Session = Depends(get_db)):
    if not db.get(SchoolClass, data.class_id):
        raise HTTPException(status_code=404, detail=f"Class ID {data.class_id} does not exist.")

    new_fee = FeeStructure(**data.model_dump())
    try:
        db.add(new_fee)
        db.commit()
        db.refresh(new_fee)
    except IntegrityError:
        db.rollback()
        # class_id is UNIQUE in fee_structure -> this class already has a fee structure
        raise HTTPException(status_code=409, detail=f"Class ID {data.class_id} already has a fee structure.")
    return new_fee


# GET /fees?skip=0&limit=50
@router.get("", response_model=list[FeeResponse])
def list_fees(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(FeeStructure).order_by(FeeStructure.fee_id).offset(skip).limit(limit)
    return db.scalars(query).all()


# GET /fees/{fee_id}
@router.get("/{fee_id}", response_model=FeeResponse)
def get_fee(fee_id: int, db: Session = Depends(get_db)):
    return get_fee_or_404(db, fee_id)


# PUT /fees/{fee_id}
@router.put("/{fee_id}", response_model=FeeResponse)
def update_fee(fee_id: int, data: FeeUpdate, db: Session = Depends(get_db)):
    fee = get_fee_or_404(db, fee_id)
    fee.total_amount = data.total_amount
    fee.due_date = data.due_date
    db.commit()
    db.refresh(fee)
    return fee


# DELETE /fees/{fee_id}
@router.delete("/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee(fee_id: int, db: Session = Depends(get_db)):
    fee = get_fee_or_404(db, fee_id)
    db.delete(fee)
    db.commit()
    return None