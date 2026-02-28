#!/usr/bin/env python3
"""
Seed the database with sample medical debt records for testing.
Run from project root: python scripts/seed_data.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine
from app.models import Base, MedicalDebt
from app.services.risk_engine import calculate_risk

SAMPLE_DEBTS = [
    {"patient_name": "Jane Doe", "income": 55000, "debt_amount": 12000, "credit_score": 640, "provider": "Carle Hospital"},
    {"patient_name": "John Smith", "income": 42000, "debt_amount": 8500, "credit_score": 720, "provider": "OSF Healthcare"},
    {"patient_name": "Maria Garcia", "income": 38000, "debt_amount": 22000, "credit_score": 580, "provider": "Carle Hospital"},
    {"patient_name": "Robert Johnson", "income": 95000, "debt_amount": 5000, "credit_score": 780, "provider": "Christie Clinic"},
    {"patient_name": "Emily Chen", "income": 62000, "debt_amount": 18500, "credit_score": 590, "provider": "OSF Healthcare"},
    {"patient_name": "David Wilson", "income": 45000, "debt_amount": 3200, "credit_score": 650, "provider": "Carle Hospital"},
    {"patient_name": "Sarah Brown", "income": 28000, "debt_amount": 15000, "credit_score": 520, "provider": "Memorial Health"},
    {"patient_name": "Michael Davis", "income": 78000, "debt_amount": 9500, "credit_score": 710, "provider": "Christie Clinic"},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(MedicalDebt).count()
        if count > 0:
            print(f"Database already has {count} records. Skipping seed.")
            return
        for data in SAMPLE_DEBTS:
            result = calculate_risk(
                debt_amount=data["debt_amount"],
                income=data["income"],
                credit_score=data["credit_score"],
            )
            record = MedicalDebt(
                patient_name=data["patient_name"],
                income=data["income"],
                debt_amount=data["debt_amount"],
                credit_score=data["credit_score"],
                provider=data["provider"],
                risk_score=result.risk_score,
                risk_level=result.risk_level,
                recommended_monthly_payment=result.recommended_monthly_payment,
            )
            db.add(record)
        db.commit()
        print(f"Seeded {len(SAMPLE_DEBTS)} medical debt records.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
