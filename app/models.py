"""
SQLAlchemy models for medical debt records.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base


class MedicalDebt(Base):
    """Medical debt record with computed risk and repayment fields."""
    __tablename__ = "medical_debts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Input fields
    patient_name = Column(String(255), nullable=False, index=True)
    income = Column(Float, nullable=False)
    debt_amount = Column(Float, nullable=False)
    credit_score = Column(Integer, nullable=False)
    provider = Column(String(255), nullable=False, index=True)
    # Repayment options (optional)
    interest_rate = Column(Float, default=0.0, nullable=False)  # e.g. 0.05 = 5% annual
    down_payment = Column(Float, default=0.0, nullable=False)
    repayment_months = Column(Integer, default=24, nullable=False)

    # Computed fields (stored for querying/filtering)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False, index=True)
    recommended_monthly_payment = Column(Float, nullable=False)
    total_interest = Column(Float, default=0.0, nullable=False)  # total interest over life of plan
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_debts_risk_provider", "risk_level", "provider"),
    )
