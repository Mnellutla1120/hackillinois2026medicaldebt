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
    
    # Computed fields (stored for querying/filtering)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False, index=True)
    recommended_monthly_payment = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_debts_risk_provider", "risk_level", "provider"),
    )
