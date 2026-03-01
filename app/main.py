"""
MediPay — FastAPI application with REST endpoints + React frontend.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import debts
from app.routers import stripe_router
import os
from dotenv import load_dotenv
import stripe

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup; migrate existing DBs for new columns."""
    Base.metadata.create_all(bind=engine)
    from app.database import migrate_sqlite_add_repayment_columns
    migrate_sqlite_add_repayment_columns()
    yield
    # Shutdown cleanup if needed


app = FastAPI(
    title="MediPay",
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

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(stripe_router.router)

# Serve React frontend (built from frontend/)
_frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/", tags=["root"])
    def serve_app():
        return FileResponse(_frontend_dist / "index.html")

    @app.get("/{path:path}", tags=["root"])
    def serve_spa(path: str):
        """Serve index.html for SPA client-side routes (API routes take precedence)."""
        return FileResponse(_frontend_dist / "index.html")
else:
    @app.get("/", tags=["root"])
    def root():
        return {
            "name": "MediPay",
            "version": "1.0.0",
            "docs": "/docs",
            "message": "Run 'cd frontend && npm run build' to serve the React app",
        }


@app.get("/health", tags=["root"])
def health():
    """Health check for load balancers."""
    return {"status": "ok"}

from fastapi import APIRouter
import stripe
import os

router = APIRouter()

@router.post("/create-payment-intent")
def create_payment(amount: int):
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        automatic_payment_methods={"enabled": True},
    )
    return {"client_secret": intent.client_secret}