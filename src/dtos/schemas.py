# src/dtos/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Classes ----------
class ClassCreate(BaseModel):
    class_name: str = Field(min_length=1, max_length=20)


class ClassUpdate(BaseModel):
    class_name: str = Field(min_length=1, max_length=20)


class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class_id: int
    class_name: str


# ---------- Students ----------
class StudentCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    parent_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(max_length=15, pattern=r"^\+?\d{7,15}$")
    class_id: int = Field(gt=0)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    section: Optional[str] = Field(default=None, max_length=10)
    enrollment_date: Optional[date] = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    first_name: str
    last_name: str
    parent_name: str
    phone: str
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    class_id: int
    section: Optional[str] = None
    enrollment_date: Optional[date] = None


# ---------- Fee structure ----------
class FeeCreate(BaseModel):
    class_id: int = Field(gt=0)
    total_amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)  # numeric(10,2)
    due_date: date


class FeeUpdate(BaseModel):  # the class of a fee structure cannot be changed
    total_amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    due_date: date


class FeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fee_id: int
    class_id: int
    total_amount: Decimal
    due_date: date


# ---------- Payments ----------
class PaymentCreate(BaseModel):
    student_id: int = Field(gt=0)
    amount_paid: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    payment_method: str = Field(min_length=1, max_length=30)
    payment_date: Optional[datetime] = None  # database fills "now" if omitted


class PaymentUpdate(BaseModel):  # the student of a payment cannot be changed
    amount_paid: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    payment_method: str = Field(min_length=1, max_length=30)
    payment_date: Optional[datetime] = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    student_id: int
    amount_paid: Decimal
    payment_method: str
    payment_date: Optional[datetime] = None


class FeeSummary(BaseModel):
    student_id: int
    class_id: int
    total_fee: Decimal
    total_paid: Decimal
    balance_due: Decimal
    due_date: date


# ---------- Auth ----------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int  # seconds until the token expires


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    admin_id: int
    username: str
    email: str


class AdminSetup(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=10, max_length=72)
    setup_key: str


# ---------- Reports ----------
class ClassReport(BaseModel):
    class_id: int
    class_name: str
    students: int
    fee_per_student: Optional[Decimal] = None
    expected: Decimal
    collected: Decimal
    pending: Decimal


class DashboardResponse(BaseModel):
    total_classes: int
    total_students: int
    total_collected: Decimal
    total_expected: Decimal
    total_pending: Decimal
    classes: List[ClassReport]