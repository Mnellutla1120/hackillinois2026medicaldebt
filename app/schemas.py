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

    @field_validator("patient_name", "provider")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v


class DebtUpdate(BaseModel):
    """Schema for partial update (PATCH) of a debt record."""
    patient_name: Optional[str] = Field(None, min_length=1, max_length=255)
    income: Optional[float] = Field(None, gt=0)
    debt_amount: Optional[float] = Field(None, gt=0)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    provider: Optional[str] = Field(None, min_length=1, max_length=255)


# --- Response Schemas ---

class DebtResponse(BaseModel):
    """Full debt record response."""
    id: int
    patient_name: str
    income: float
    debt_amount: float
    credit_score: int
    provider: str
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DebtCreateResponse(BaseModel):
    """Response for newly created debt (201 Created)."""
    id: int
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float

    model_config = {"from_attributes": True}


class DebtSummary(BaseModel):
    """Summary view for GET /debts/{id}/summary."""
    id: int
    patient_name: str
    provider: str
    debt_amount: float
    risk_level: str
    recommended_monthly_payment: float
    estimated_payoff_months: int

    model_config = {"from_attributes": True}


class DebtListResponse(BaseModel):
    """Paginated list response."""
    items: list[DebtResponse]
    total: int
    limit: int
    offset: int
