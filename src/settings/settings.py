# src/settings/settings.py
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_CONNECTION: str

    # --- JWT / admin login ---
    SECRET_KEY: str = Field(min_length=32)  # app refuses to start with a weak key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    # Optional: lets the FIRST admin be created from the login page. Leave unset to disable.
    SETUP_KEY: Optional[str] = Field(default=None, min_length=16)