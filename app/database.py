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

# Use DATABASE_URL or POSTGRES_URL. On Vercel, SQLite won't work — use Postgres or /tmp (ephemeral).
database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or settings.database_url
if os.getenv("VERCEL") and database_url.startswith("sqlite"):
    # Vercel: use /tmp (ephemeral) if no Postgres — app won't crash, but data won't persist
    database_url = "sqlite:////tmp/medical_debt.db"

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