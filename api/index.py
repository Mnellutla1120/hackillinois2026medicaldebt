"""
Vercel serverless entry — API only. Frontend is served as static.
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import stripe
from fastapi import FastAPI, Request

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import debts
from app.routers import stripe_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        from app.database import migrate_sqlite_add_repayment_columns
        migrate_sqlite_add_repayment_columns()
    except Exception:
        pass  # Don't crash on DB init (e.g. no Postgres configured)
    yield


app = FastAPI(
    title="MediPay API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# Mount under /api so frontend can call /api/debts, /api/stripe, etc.
app.include_router(debts.router, prefix="/api")
app.include_router(stripe_router.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
