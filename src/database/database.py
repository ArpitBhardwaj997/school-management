# src/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.settings.settings import Settings

# 1. Load your settings object
settings = Settings()

# 2. Create the database engine from the configuration string
engine = create_engine(settings.DB_CONNECTION)

# 3. Create the Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declare the single Base mapping object for models to inherit from
Base = declarative_base()

# 5. Database session context generator for your FastAPI routers
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
