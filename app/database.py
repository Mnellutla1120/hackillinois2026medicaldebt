
"""
Database configuration with SQLite (local) and optional PostgreSQL support.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

# HARDCODED for Vercel deployment
database_url = "postgresql+pg8000://neondb_owner:npg_NaW3DJQvP5Ge@ep-proud-dust-aigbi3mu-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Fix postgresql:// to postgresql
connect_args = {}

engine = create_engine(database_url, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Settings(BaseSettings):
    stripe_secret_key: str = ""
    class Config:
        env_file = ".env"

settings = Settings()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# """
# Database configuration with SQLite (local) and optional PostgreSQL support.
# """
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from pydantic_settings import BaseSettings


# # class Settings(BaseSettings):
# #     """Application settings with environment variable support."""
# #     database_url: str = "sqlite:///./medical_debt.db"
# #     stripe_secret_key: str= ""
# #     class Config:
# #         env_file = ".env"
# #         env_file_encoding = "utf-8"
# "

# settings = Settings()

# # Use DATABASE_URL from env for PostgreSQL, otherwise SQLite
# #database_url = os.getenv("DATABASE_URL", settings.database_url)

# # SQLite needs special config for async-like behavior (check_same_thread=False)
# connect_args = {}
# if database_url.startswith("sqlite"):
#     connect_args = {"check_same_thread": False}

# engine = create_engine(
#     database_url,
#     connect_args=connect_args,
#     echo=False,  # Set True for SQL debugging
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# def get_db():
#     """Dependency for FastAPI - yields database session."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
