"""
Database configuration with SQLite (local) and optional PostgreSQL support.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    database_url: str = "sqlite:///./medical_debt.db"
    stripe_secret_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Use DATABASE_URL from env for PostgreSQL. On Vercel, SQLite won't work — set DATABASE_URL (e.g. Vercel Postgres).
database_url = os.getenv("DATABASE_URL", settings.database_url)
if os.getenv("VERCEL") and not database_url.startswith("postgres"):
    # Vercel: require Postgres; SQLite filesystem is read-only
    database_url = os.getenv("POSTGRES_URL") or database_url

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


def migrate_sqlite_add_repayment_columns():
    """Add new repayment columns to existing SQLite DB if missing."""
    if not database_url.startswith("sqlite"):
        return
    from sqlalchemy import text, inspect
    insp = inspect(engine)
    if "medical_debts" not in insp.get_table_names():
        return
    cols = [c["name"] for c in insp.get_columns("medical_debts")]
    for col, typ, default in [
        ("interest_rate", "FLOAT", "0"),
        ("down_payment", "FLOAT", "0"),
        ("repayment_months", "INTEGER", "24"),
        ("total_interest", "FLOAT", "0"),
    ]:
        if col in cols:
            continue
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE medical_debts ADD COLUMN {col} {typ} DEFAULT {default}"))
            conn.commit()