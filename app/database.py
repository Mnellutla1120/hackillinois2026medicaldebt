"""
Database configuration with SQLite (local) and optional PostgreSQL support.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application settings with environment variable support."""
#     database_url: str = "sqlite:///./medical_debt.db"
#     stripe_secret_key: str= ""
#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"

class Settings(BaseSettings):
    database_url: str = "sqlite:///./medical_debt.db"
    stripe_secret_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""

settings = Settings()

# Use DATABASE_URL from env for PostgreSQL, otherwise SQLite
#database_url = os.getenv("DATABASE_URL", settings.database_url)
database_url = os.environ.get("DATABASE_URL") or settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# SQLite needs special config for async-like behavior (check_same_thread=False)
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False,  # Set True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI - yields database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
