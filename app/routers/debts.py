"""
Debt API endpoints - RESTful CRUD with filtering and pagination.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MedicalDebt
from app.schemas import (
    DebtCreate,
    DebtUpdate,
    DebtResponse,
    DebtCreateResponse,
    DebtSummary,
    DebtListResponse,
)
from app.services.risk_engine import calculate_risk

router = APIRouter(prefix="/debts", tags=["debts"])


@router.post(
    "",
    response_model=DebtCreateResponse,
    status_code=201,
    summary="Create medical debt record",
    description="Submit a new medical debt for risk assessment and repayment planning.",
)
def create_debt(debt: DebtCreate, db: Session = Depends(get_db)):
    """Create a medical debt record with computed risk and repayment plan."""
    result = calculate_risk(
        debt_amount=debt.debt_amount,
        income=debt.income,
        credit_score=debt.credit_score,
        repayment_months=debt.repayment_months,
        interest_rate=debt.interest_rate,
        down_payment=debt.down_payment,
    )
    record = MedicalDebt(
        patient_name=debt.patient_name,
        income=debt.income,
        debt_amount=debt.debt_amount,
        credit_score=debt.credit_score,
        provider=debt.provider,
        interest_rate=debt.interest_rate,
        down_payment=debt.down_payment,
        repayment_months=debt.repayment_months,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        recommended_monthly_payment=result.recommended_monthly_payment,
        total_interest=result.total_interest,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return DebtCreateResponse(
        id=record.id,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        recommended_monthly_payment=record.recommended_monthly_payment,
        total_interest=record.total_interest,
        amount_after_down_payment=result.amount_after_down_payment,
        estimated_payoff_months=result.estimated_payoff_months,
    )


@router.get(
    "/{debt_id}",
    response_model=DebtResponse,
    summary="Get debt by ID",
    responses={404: {"description": "Debt not found"}},
)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    """Retrieve a single debt record by ID."""
    record = db.query(MedicalDebt).filter(MedicalDebt.id == debt_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Debt not found")
    return record


@router.get(
    "",
    response_model=DebtListResponse,
    summary="List debts with filtering and pagination",
)
def list_debts(
    db: Session = Depends(get_db),
    risk_level: str | None = Query(None, description="Filter by risk level (Low, Medium, High)"),
    provider: str | None = Query(None, description="Filter by provider name (partial match)"),
    patient_name: str | None = Query(None, description="Search by patient name (partial match)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List debt records with optional filters and pagination."""
    query = db.query(MedicalDebt)
    
    if risk_level:
        query = query.filter(MedicalDebt.risk_level == risk_level)
    if provider:
        query = query.filter(MedicalDebt.provider.ilike(f"%{provider}%"))
    if patient_name:
        query = query.filter(MedicalDebt.patient_name.ilike(f"%{patient_name}%"))
    
    total = query.count()
    items = query.order_by(MedicalDebt.created_at.desc()).offset(offset).limit(limit).all()
    
    return DebtListResponse(items=items, total=total, limit=limit, offset=offset)


@router.patch(
    "/{debt_id}",
    response_model=DebtResponse,
    summary="Update debt (partial)",
    responses={404: {"description": "Debt not found"}},
)
def update_debt(debt_id: int, payload: DebtUpdate, db: Session = Depends(get_db)):
    """Partially update a debt record. Recomputes risk if financial fields change."""
    record = db.query(MedicalDebt).filter(MedicalDebt.id == debt_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    # Recompute risk/repayment if any financial or plan fields changed
    recompute_keys = ("income", "debt_amount", "credit_score", "interest_rate", "down_payment", "repayment_months")
    needs_recompute = any(k in update_data for k in recompute_keys)
    if needs_recompute:
        income = update_data.get("income", record.income)
        debt_amount = update_data.get("debt_amount", record.debt_amount)
        credit_score = update_data.get("credit_score", record.credit_score)
        interest_rate = update_data.get("interest_rate", record.interest_rate)
        down_payment = update_data.get("down_payment", record.down_payment)
        repayment_months = update_data.get("repayment_months", record.repayment_months)
        if down_payment >= debt_amount:
            raise HTTPException(status_code=400, detail="Down payment must be less than debt amount")
        result = calculate_risk(
            debt_amount=debt_amount,
            income=income,
            credit_score=credit_score,
            repayment_months=repayment_months,
            interest_rate=interest_rate,
            down_payment=down_payment,
        )
        update_data["risk_score"] = result.risk_score
        update_data["risk_level"] = result.risk_level
        update_data["recommended_monthly_payment"] = result.recommended_monthly_payment
        update_data["total_interest"] = result.total_interest
    
    for key, value in update_data.items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete(
    "/{debt_id}",
    status_code=204,
    summary="Delete debt",
    responses={404: {"description": "Debt not found"}},
)
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    """Delete a debt record. Idempotent: returns 204 even if already deleted."""
    record = db.query(MedicalDebt).filter(MedicalDebt.id == debt_id).first()
    if record:
        db.delete(record)
        db.commit()
    return None


@router.get(
    "/{debt_id}/summary",
    response_model=DebtSummary,
    summary="Get debt summary",
    responses={404: {"description": "Debt not found"}},
)
def get_debt_summary(debt_id: int, db: Session = Depends(get_db)):
    """Get a concise summary with estimated payoff timeline."""
    record = db.query(MedicalDebt).filter(MedicalDebt.id == debt_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Debt not found")

    amount_remaining = max(0.0, record.debt_amount - record.down_payment)
    estimated_months = record.repayment_months
    if record.recommended_monthly_payment > 0 and amount_remaining > 0:
        estimated_months = max(1, int(round(amount_remaining / record.recommended_monthly_payment)))

    return DebtSummary(
        id=record.id,
        patient_name=record.patient_name,
        provider=record.provider,
        debt_amount=record.debt_amount,
        down_payment=record.down_payment,
        amount_remaining=amount_remaining,
        risk_level=record.risk_level,
        recommended_monthly_payment=record.recommended_monthly_payment,
        total_interest=getattr(record, "total_interest", 0) or 0,
        estimated_payoff_months=estimated_months,
    )
