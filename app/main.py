"""
Medical Debt Risk & Repayment Planning API
FastAPI application with REST endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import engine, Base, get_db
from app.models import MedicalDebt
from app.routers import debts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown cleanup if needed


app = FastAPI(
    title="Medical Debt Risk & Repayment Planning API",
    description="""
    A REST API for assessing medical debt risk and generating repayment plans.
    
    ## Features
    - **Create** debt records with automatic risk scoring
    - **List** debts with filtering (risk level, provider, patient name) and pagination
    - **Retrieve** full records or summary views
    - **Update** (PATCH) and **Delete** records
    
    ## Risk Scoring
    Risk is computed from debt-to-income ratio and credit score.
    - **Low**: &lt; 0.2
    - **Medium**: 0.2 - 0.5  
    - **High**: ≥ 0.5
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- Custom Exception Handlers ---

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation/value errors with 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# --- Routes ---

app.include_router(debts.router)


@app.get("/", tags=["root"])
def root():
    """Health check and API info."""
    return {
        "name": "Medical Debt Risk & Repayment Planning API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "POST /debts": "Create debt record",
            "GET /debts": "List debts (filter by risk_level, provider, patient_name)",
            "GET /debts/{id}": "Get debt by ID",
            "GET /debts/{id}/summary": "Get debt summary",
            "PATCH /debts/{id}": "Update debt",
            "DELETE /debts/{id}": "Delete debt",
        },
    }


@app.get("/health", tags=["root"])
def health():
    """Health check for load balancers."""
    return {"status": "ok"}
