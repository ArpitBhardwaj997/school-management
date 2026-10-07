# create_admin.py -- run ONCE from the project root:  python create_admin.py
# Creates the single admin account (or resets its password if one exists).
import getpass

from sqlalchemy import select

from src.auth.security import MAX_PASSWORD_BYTES, hash_password
from src.database.database import SessionLocal
from src.models.model import Admin

MIN_PASSWORD_LENGTH = 10


def ask_password() -> str:
    while True:
        password = getpass.getpass(f"Password (min {MIN_PASSWORD_LENGTH} characters): ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"Too short. Use at least {MIN_PASSWORD_LENGTH} characters.")
        elif len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
            print(f"Too long. Maximum is {MAX_PASSWORD_BYTES} bytes.")
        elif password != getpass.getpass("Repeat password: "):
            print("Passwords do not match.")
        else:
            return password


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(Admin).order_by(Admin.admin_id))

        if existing:
            print(f"An admin already exists (username: {existing.username}).")
            if input("Reset its password? (y/n): ").strip().lower() != "y":
                print("Nothing changed.")
                return
            existing.password_hash = hash_password(ask_password())
            db.commit()
            print("Password updated.")
            return

        username = input("Admin username (3-50 characters): ").strip()
        email = input("Admin email: ").strip()
        if not 3 <= len(username) <= 50 or "@" not in email or len(email) > 100:
            print("Invalid username or email. Nothing created.")
            return

        db.add(Admin(username=username, email=email, password_hash=hash_password(ask_password())))
        db.commit()
        print(f"Admin '{username}' created. You can now log in at POST /auth/login")
    finally:
        db.close()


if __name__ == "__main__":
    main()