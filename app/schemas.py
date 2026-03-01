"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# --- Request Schemas ---

class DebtCreate(BaseModel):
    """Schema for creating a medical debt record."""
    patient_name: str = Field(..., min_length=1, max_length=255)
    income: float = Field(..., gt=0, description="Annual income in USD")
    debt_amount: float = Field(..., gt=0, description="Total medical debt in USD")
    credit_score: int = Field(..., ge=300, le=850)
    provider: str = Field(..., min_length=1, max_length=255)
    interest_rate: float = Field(0.0, ge=0, le=0.5, description="Annual interest rate (e.g. 0.05 = 5%)")
    down_payment: float = Field(0.0, ge=0, description="Initial down payment in USD")
    repayment_months: int = Field(24, ge=1, le=120, description="Repayment term in months")

    @field_validator("patient_name", "provider")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v

    @field_validator("down_payment")
    @classmethod
    def down_payment_less_than_debt(cls, v: float, info) -> float:
        if "debt_amount" in info.data and v >= info.data["debt_amount"]:
            raise ValueError("Down payment must be less than debt amount")
        return v


class DebtUpdate(BaseModel):
    """Schema for partial update (PATCH) of a debt record."""
    patient_name: Optional[str] = Field(None, min_length=1, max_length=255)
    income: Optional[float] = Field(None, gt=0)
    debt_amount: Optional[float] = Field(None, gt=0)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    interest_rate: Optional[float] = Field(None, ge=0, le=0.5)
    down_payment: Optional[float] = Field(None, ge=0)
    repayment_months: Optional[int] = Field(None, ge=1, le=120)


# --- Response Schemas ---

class DebtResponse(BaseModel):
    """Full debt record response."""
    id: int
    patient_name: str
    income: float
    debt_amount: float
    credit_score: int
    provider: str
    interest_rate: float
    down_payment: float
    repayment_months: int
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float
    total_interest: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DebtCreateResponse(BaseModel):
    """Response for newly created debt (201 Created)."""
    id: int
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float
    total_interest: float
    amount_after_down_payment: float
    estimated_payoff_months: int

    model_config = {"from_attributes": True}


class DebtSummary(BaseModel):
    """Summary view for GET /debts/{id}/summary."""
    id: int
    patient_name: str
    provider: str
    debt_amount: float
    down_payment: float
    amount_remaining: float
    risk_level: str
    recommended_monthly_payment: float
    total_interest: float
    estimated_payoff_months: int

    model_config = {"from_attributes": True}


class DebtListResponse(BaseModel):
    """Paginated list response."""
    items: list[DebtResponse]
    total: int
    limit: int
    offset: int
