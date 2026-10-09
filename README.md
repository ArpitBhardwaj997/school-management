# School Management System

A full-stack school management system developed for managing student records, class-wise fee structures, payments, and fee tracking through a centralized admin dashboard.

The system is designed so that the **admin controls the complete workflow**. There are no separate teacher or student accounts.

---

## 🚀 Live Demo

**Testing Environment:**

https://school-management-ajqd.onrender.com/app/login.html

> Note: This is a testing deployment. The application is hosted on Render and uses Neon PostgreSQL.

---

## 📌 Project Overview

The School Management System is a web-based application built to simplify school administration.

The administrator can manage:

- Student records
- Classes
- Class-wise fee structures
- Student payments
- Payment tracking
- Pending fees
- Student information
- Administrative reports

The backend is developed using **FastAPI**, the database uses **PostgreSQL**, and the frontend is built using **HTML, CSS, and JavaScript**.

---

## 🎯 Main Objective

The main objective of this project is to provide a centralized system where a school administrator can manage student and fee-related information efficiently instead of maintaining records manually.

---

## ✨ Features

### 🔐 Admin Authentication

- Admin login
- JWT-based authentication
- Protected backend routes
- Secure password handling
- Admin-only access

### 👨‍🎓 Student Management

Admin can:

- Add students
- View student records
- Update student information
- Delete students
- Manage student class and section
- Store parent information
- Store contact information
- Store enrollment information

### 🏫 Class Management

The system supports:

- Nursery
- LKG
- UKG
- Class 1
- Class 2
- Class 3
- Class 4
- Class 5
- Class 6
- Class 7
- Class 8
- Class 9
- Class 10
- Class 11
- Class 12

Each student is connected to a class through a database relationship.

### 💰 Fee Management

Admin can:

- Define class-wise fee structures
- Set total fees for each class
- Set fee due dates
- Track student payments
- Track payment methods
- View payment history
- Calculate remaining/pending fees

Pending fees are calculated from:

```text
Pending Fee = Total Fee - Total Payments
