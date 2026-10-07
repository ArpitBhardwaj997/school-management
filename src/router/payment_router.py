# src/router/payment_router.py
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dtos.schemas import FeeSummary, PaymentCreate, PaymentResponse, PaymentUpdate
from src.models.model import FeeStructure, Payment, Student

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_or_404(db: Session, payment_id: int) -> Payment:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} not found.")
    return payment


# POST /payments
@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    if not db.get(Student, data.student_id):
        raise HTTPException(status_code=404, detail=f"Student ID {data.student_id} does not exist.")

    # exclude_none: if payment_date is omitted the database sets the current time
    new_payment = Payment(**data.model_dump(exclude_none=True))
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


# GET /payments?student_id=1&skip=0&limit=50
@router.get("", response_model=list[PaymentResponse])
def list_payments(
    student_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Payment).order_by(Payment.payment_id.desc())
    if student_id is not None:
        query = query.where(Payment.student_id == student_id)
    return db.scalars(query.offset(skip).limit(limit)).all()


# GET /payments/student/{student_id}/summary  -> total fee, total paid, balance due
@router.get("/student/{student_id}/summary", response_model=FeeSummary)
def get_fee_summary(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID {student_id} does not exist.")

    fee = db.scalar(select(FeeStructure).where(FeeStructure.class_id == student.class_id))
    if not fee:
        raise HTTPException(status_code=404, detail="No fee structure is set for this student's class.")

    total_paid = db.scalar(
        select(func.coalesce(func.sum(Payment.amount_paid), 0)).where(Payment.student_id == student_id)
    )
    total_paid = Decimal(str(total_paid))

    return FeeSummary(
        student_id=student_id,
        class_id=student.class_id,
        total_fee=fee.total_amount,
        total_paid=total_paid,
        balance_due=fee.total_amount - total_paid,
        due_date=fee.due_date,
    )


# GET /payments/{payment_id}
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return get_payment_or_404(db, payment_id)


# PUT /payments/{payment_id}   (correct a mistake)
@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    payment = get_payment_or_404(db, payment_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)
    db.commit()
    db.refresh(payment)
    return payment


# DELETE /payments/{payment_id}
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = get_payment_or_404(db, payment_id)
    db.delete(payment)
    db.commit()
    return None