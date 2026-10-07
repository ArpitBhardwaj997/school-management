# src/models/model.py
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from src.database.database import Base


class SchoolClass(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(20), unique=True, nullable=False)

    students = relationship("Student", back_populates="school_class")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    parent_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(Text)
    date_of_birth = Column(Date)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    section = Column(String(10))
    enrollment_date = Column(Date, server_default=func.current_date())

    school_class = relationship("SchoolClass", back_populates="students")
    # No relationship to Payment on purpose: the database deletes payments
    # itself (ON DELETE CASCADE), so SQLAlchemy must not touch them.


class FeeStructure(Base):
    __tablename__ = "fee_structure"

    fee_id = Column(Integer, primary_key=True, index=True)
    # UNIQUE in the table: one fee structure per class
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False, unique=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    payment_date = Column(DateTime, server_default=func.now())


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())