# src/database/errors.py
from typing import Optional

from sqlalchemy.exc import IntegrityError

# PostgreSQL error code (SQLSTATE) for "duplicate value in a UNIQUE column"
UNIQUE_VIOLATION = "23505"


def pg_error_code(error: IntegrityError) -> Optional[str]:
    """Return the PostgreSQL error code behind a SQLAlchemy IntegrityError.

    psycopg2 exposes it as .pgcode, psycopg (v3) as .sqlstate.
    """
    original = error.orig
    return getattr(original, "pgcode", None) or getattr(original, "sqlstate", None)