School Management System

A full-stack web-based School Management System developed to help a school administrator manage student records, classes, fee structures, payments, and reports from a centralized admin interface.

The system is designed as an admin-only application, where the administrator controls the complete workflow. There are no separate teacher or student accounts.

Live Testing

Live Testing Environment:

https://school-management-ajqd.onrender.com/app/login.html

This deployment is intended for testing. Do not enter real student information or other sensitive personal data.

Project Overview

The School Management System provides a centralized platform for handling common administrative tasks related to students and school fees.

The administrator can:

Log in securely

Manage student records

Manage school classes

Configure class-wise fee structures

Record student payments

Track payment history

Calculate pending fees

View reports and administrative information

The application uses FastAPI for the backend, PostgreSQL for data storage, SQLAlchemy for database interaction, and HTML/CSS/JavaScript for the frontend.

Main Objective

The main objective of this project is to replace manual student and fee record management with a centralized digital system.

The application keeps student information, class information, fee structures, and payment records organized in a relational database and provides an admin interface for managing the complete workflow.

Key Features

Admin Authentication

Admin login

JWT-based authentication

Protected API routes

Password hashing

Secure configuration through environment variables

Student Management

The administrator can:

Add students

View students

Update student information

Delete students

Assign students to classes

Store parent/guardian information

Store contact information

Store address and date of birth

Store enrollment information

Manage student sections

Class Management

The system supports:

Nursery

LKG

UKG

Class 1

Class 2

Class 3

Class 4

Class 5

Class 6

Class 7

Class 8

Class 9

Class 10

Class 11

Class 12

Each student is linked to a class through a database relationship.

Fee Management

The administrator can:

Create class-wise fee structures

Set total fees

Set fee due dates

View fee structures

Track student payments

Track payment history

Calculate remaining/pending fees

Pending fees are calculated using:

Pending Fee = Total Class Fee - Total Amount Paid

The pending amount is calculated instead of being stored separately in the database.

Payment Management

Each payment record stores:

Student

Amount paid

Payment method

Payment date

A student can have multiple payment records.

Reports and Dashboard

The application provides administrative information related to:

Total students

Student records

Fee structures

Payment records

Pending fees

Administrative reports

Technology Stack

Frontend

HTML5

CSS3

JavaScript

Backend

Python

FastAPI

SQLAlchemy

Pydantic

JWT Authentication

Database

PostgreSQL

Neon PostgreSQL for cloud deployment

pgAdmin for local database management

Deployment

Render

Neon PostgreSQL

Development Tools

Visual Studio Code

Git

GitHub

PostgreSQL

pgAdmin

System Architecture

                    Admin User
                        |
                        v
              +-------------------+
              |   HTML / CSS / JS  |
              |      Frontend      |
              +---------+---------+
                        |
                        | HTTP Requests
                        v
              +-------------------+
              |      FastAPI      |
              |      Backend      |
              +---------+---------+
                        |
              +---------+---------+
              |                   |
              v                   v
       +-------------+     +---------------+
       |  SQLAlchemy |     | JWT Security  |
       +------+------+     +---------------+
              |
              v
       +-------------+
       | PostgreSQL  |
       |  Database   |
       +-------------+

Application Flow

Admin Login
     |
     v
Authentication
     |
     v
Admin Dashboard
     |
     +-------------------+
     |                   |
     v                   v
Student Management   Class Management
     |                   |
     +---------+---------+
               |
               v
        Fee Management
               |
               v
       Payment Management
               |
               v
        Reports / Dashboard

Student Fee Flow

Class
  |
  v
Class Fee Structure
  |
  v
Student Assigned to Class
  |
  v
Student Makes Payment
  |
  v
Payment Stored in Database
  |
  v
Total Payments Calculated
  |
  v
Pending Fee Calculated

Database Design

The application uses PostgreSQL with five main tables.

1. Admin

Stores administrator account information.

admin
├── admin_id
├── username
├── email
├── password_hash
└── created_at

2. Classes

Stores the available school classes.

classes
├── class_id
└── class_name

3. Students

Stores student information.

students
├── student_id
├── first_name
├── last_name
├── parent_name
├── phone
├── address
├── date_of_birth
├── class_id
├── section
└── enrollment_date

4. Fee Structure

Stores the fee structure for each class.

fee_structure
├── fee_id
├── class_id
├── total_amount
└── due_date

5. Payments

Stores student payment transactions.

payments
├── payment_id
├── student_id
├── amount_paid
├── payment_method
└── payment_date

Database Relationships

                 +----------+
                 |  Classes |
                 +----+-----+
                      |
             +--------+--------+
             |                 |
             v                 v
       +-----------+    +---------------+
       | Students  |    | Fee Structure |
       +-----+-----+    +---------------+
             |
             v
       +-----------+
       | Payments  |
       +-----------+

Relationships

One class can have many students.

One class has one fee structure.

One student can have multiple payments.

Each payment belongs to one student.

Students reference their class using class_id.

Fee structures reference classes using class_id.

Payments reference students using student_id.

Project Structure

school-management/
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── login.html
│   ├── login.js
│   └── style.css
│
├── src/
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── dtos/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── model.py
│   │
│   ├── router/
│   │   ├── __init__.py
│   │   ├── auth_router.py
│   │   ├── class_router.py
│   │   ├── fee_router.py
│   │   ├── payment_router.py
│   │   ├── report_router.py
│   │   └── student_router.py
│   │
│   └── settings/
│       ├── __init__.py
│       └── settings.py
│
├── app.py
├── check_api.py
├── create_admin.py
├── requirements.txt
├── .gitignore
└── README.md

Backend Architecture

The backend is organized into separate modules according to responsibility.

auth

Handles authentication-related functionality such as:

JWT security

Authentication dependencies

Password/security operations

database

Handles:

PostgreSQL connection

SQLAlchemy engine

Database sessions

Base model configuration

dtos

Contains Pydantic schemas used for:

Request validation

Response validation

Data transfer between API layers

models

Contains SQLAlchemy database models.

router

Contains API routes separated by functionality:

Authentication

Students

Classes

Fees

Payments

Reports

settings

Handles application configuration and environment variables.

Authentication Flow

Admin Login
     |
     v
Username / Email + Password
     |
     v
Backend Validation
     |
     v
JWT Access Token
     |
     v
Protected API Requests

Protected endpoints require a valid authentication token.

Pending Fee Calculation

The system does not store pending fees as a separate database value.

Instead, the application calculates the amount dynamically:

Total Class Fee
       -
Total Amount Paid
       =
Pending Fee

For example:

Total Fee       = ₹50,000
Amount Paid     = ₹30,000
----------------------------
Pending Fee     = ₹20,000

This approach avoids storing duplicate calculated information that could become outdated.

API Documentation

FastAPI automatically provides interactive API documentation.

After running the application locally, open:

http://127.0.0.1:8000/docs

The Swagger UI can be used to:

View available API endpoints

Check request parameters

Check response schemas

Test API requests

Test authenticated endpoints

Local Setup

Prerequisites

Make sure the following are installed:

Python 3.x

PostgreSQL

Git

Visual Studio Code

1. Clone the Repository

git clone https://github.com/ArpitBhardwaj997/school-management.git

Move into the project directory:

cd school-management

2. Create a Virtual Environment

Windows:

python -m venv .venv

Activate the virtual environment:

.venv\Scripts\activate

3. Install Dependencies

The project includes a requirements.txt file containing the required Python packages.

Install them using:

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the project root.

Example:

DB_CONNECTION=your_database_connection_string
SECRET_KEY=your_secret_key
SETUP_KEY=your_setup_key

Replace the placeholder values with your own configuration.

Never commit the .env file to GitHub.

5. Configure PostgreSQL

Create a PostgreSQL database and configure its connection string in the .env file.

Example format:

postgresql://username:password@host:port/database

The application uses SQLAlchemy to connect the FastAPI backend with PostgreSQL.

6. Start the FastAPI Server

Run:

uvicorn app:app --reload

The application will be available at:

http://127.0.0.1:8000/

API documentation:

http://127.0.0.1:8000/docs

Environment Variables

The application uses environment variables for sensitive configuration.

Variable

Purpose

DB_CONNECTION

PostgreSQL database connection

SECRET_KEY

JWT signing/security key

SETUP_KEY

Optional initial admin setup key

Sensitive values should never be hard-coded or committed to GitHub.

Deployment

The testing version of this project is deployed using Render and Neon PostgreSQL.

Render

Render hosts the FastAPI web service.

Build Command

pip install -r requirements.txt

Start Command

uvicorn app:app --host 0.0.0.0 --port $PORT

The application receives the database connection and security configuration through Render environment variables.

Neon PostgreSQL

Neon provides the cloud PostgreSQL database used by the deployed application.

The backend connects to Neon using the DB_CONNECTION environment variable.

GitHub and Deployment Workflow

The project uses GitHub for source-code management.

The general workflow is:

Local Development
       |
       v
Git
       |
       v
GitHub
       |
       v
Render
       |
       v
Live Testing Application

When changes are pushed to GitHub, Render can automatically deploy the updated application.

Security

The project follows basic security practices for development and testing.

Implemented / Used

JWT authentication

Password hashing

Protected API routes

Environment variables for secrets

PostgreSQL database

.env excluded from Git

Database backup excluded from Git

Files that should not be committed

.env
.venv/
__pycache__/
school_management_backup.sql

Do not upload:

Database passwords

JWT secret keys

Setup keys

Admin passwords

Real student information

Private client information

Testing Environment

The project has a live testing environment so that the application can be tested without setting up the project locally.

Testing URL:

https://school-management-ajqd.onrender.com/app/login.html

The testing deployment is intended for development/client testing purposes.

Client Project

This project was developed as a paid freelance/client project.

The application was designed according to the client's requirement for an admin-controlled school management system.

The project demonstrates experience in:

Backend development

Database design

API development

Authentication

Frontend-backend integration

Cloud database integration

Deployment

Debugging and maintenance

Public sharing of client-specific information, screenshots, real data, or credentials should only be done with the client's permission.

Future Improvements

Possible future improvements include:

Automated fee reminders

Email notifications

SMS notifications

PDF payment receipts

Excel/PDF report export

Advanced dashboard analytics

Student search and filtering

Payment receipt generation

Automated database backups

Audit logs

Custom production domain

Production-grade hosting

Additional user roles if required

Learning Outcomes

This project provided practical experience with:

Python backend development

FastAPI

REST APIs

PostgreSQL

SQLAlchemy

Pydantic

JWT authentication

Password security

Relational database design

Foreign key relationships

HTML/CSS/JavaScript

Git and GitHub

Environment variables

Cloud databases

Render deployment

Debugging deployment issues

Full-stack application architecture

Developer

Arpit Bhardwaj

B.Tech Computer Science and Engineering

GitHub:
https://github.com/ArpitBhardwaj997

LinkedIn:
https://linkedin.com/in/arpitbhardwaj614

License

This project is developed for educational, development, and client-project purposes.
