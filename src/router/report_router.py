# src/router/report_router.py
from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dtos.schemas import ClassReport, DashboardResponse
from src.models.model import FeeStructure, Payment, SchoolClass, Student

router = APIRouter(prefix="/reports", tags=["Reports"])

D = lambda v: Decimal(str(v or 0))  # noqa: E731  (safe Decimal from DB number)


# GET /reports/dashboard  -> totals + one row per class
@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    paid = (
        select(Payment.student_id, func.sum(Payment.amount_paid).label("paid"))
        .group_by(Payment.student_id)
        .subquery()
    )
    # one row per student whose class has a fee structure
    fee_rows = db.execute(
        select(Student.class_id, FeeStructure.total_amount, func.coalesce(paid.c.paid, 0))
        .select_from(Student)
        .join(FeeStructure, FeeStructure.class_id == Student.class_id)
        .outerjoin(paid, paid.c.student_id == Student.student_id)
    ).all()

    expected, collected, pending = defaultdict(Decimal), defaultdict(Decimal), defaultdict(Decimal)
    for class_id, fee, paid_amount in fee_rows:
        fee, paid_amount = D(fee), D(paid_amount)
        expected[class_id] += fee
        collected[class_id] += paid_amount
        pending[class_id] += max(fee - paid_amount, Decimal(0))

    counts = dict(db.execute(select(Student.class_id, func.count()).group_by(Student.class_id)).all())
    classes = db.execute(
        select(SchoolClass.class_id, SchoolClass.class_name, FeeStructure.total_amount)
        .outerjoin(FeeStructure, FeeStructure.class_id == SchoolClass.class_id)
        .order_by(SchoolClass.class_id)
    ).all()

    return DashboardResponse(
        total_classes=len(classes),
        total_students=sum(counts.values()),
        total_collected=D(db.scalar(select(func.coalesce(func.sum(Payment.amount_paid), 0)))),
        total_expected=sum(expected.values(), Decimal(0)),
        total_pending=sum(pending.values(), Decimal(0)),
        classes=[
            ClassReport(
                class_id=cid, class_name=name, students=counts.get(cid, 0),
                fee_per_student=None if fee is None else D(fee),
                expected=expected[cid], collected=collected[cid], pending=pending[cid],
            )
            for cid, name, fee in classes
        ],
    )