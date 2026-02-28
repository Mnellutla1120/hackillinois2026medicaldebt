from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, database
import pandas as pd
import os

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="MedLedger API")


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Load insurance.csv into DB
# -----------------------------
def load_insurance_csv(db: Session):
    # Prevent duplicate loading
    if db.query(models.InsuranceRecord).first():
        return

    csv_path = os.path.join(os.path.dirname(__file__), "..", "insurance.csv")

    if not os.path.exists(csv_path):
        print("insurance.csv not found. Skipping CSV load.")
        return

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        record = models.InsuranceRecord(
            age=int(row["age"]),
            sex=row["sex"],
            bmi=float(row["bmi"]),
            children=int(row["children"]),
            smoker=row["smoker"],
            region=row["region"],
            charges=float(row["charges"]),
        )
        db.add(record)

    db.commit()
    print("Insurance CSV loaded successfully.")


@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    load_insurance_csv(db)
    db.close()


# ============================================================
# DEBT ENDPOINTS
# ============================================================

@app.post("/debts", response_model=schemas.DebtResponse, status_code=201)
def create_debt(debt: schemas.DebtCreate, db: Session = Depends(get_db)):
    db_debt = models.Debt(**debt.model_dump())
    db.add(db_debt)
    db.commit()
    db.refresh(db_debt)
    return db_debt


@app.get("/debts", response_model=List[schemas.DebtResponse])
def list_debts(
    skip: int = 0,
    limit: int = Query(10, le=100),
    patient_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Debt)

    if patient_name:
        query = query.filter(models.Debt.patient_name == patient_name)

    return query.offset(skip).limit(limit).all()


@app.get("/debts/{debt_id}", response_model=schemas.DebtResponse)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(models.Debt).filter(models.Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt


@app.patch("/debts/{debt_id}", response_model=schemas.DebtResponse)
def update_debt(debt_id: int, update: schemas.DebtUpdate, db: Session = Depends(get_db)):
    debt = db.query(models.Debt).filter(models.Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    if update.status is not None:
        debt.status = update.status

    db.commit()
    db.refresh(debt)
    return debt


@app.delete("/debts/{debt_id}", status_code=204)
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(models.Debt).filter(models.Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    db.delete(debt)
    db.commit()
    return


@app.post("/debts/{debt_id}/payments", response_model=schemas.PaymentResponse)
def add_payment(debt_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    debt = db.query(models.Debt).filter(models.Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    new_payment = models.Payment(debt_id=debt_id, amount=payment.amount)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    debts = db.query(models.Debt).all()
    total_original = sum(d.original_amount for d in debts)
    total_paid = sum(p.amount for d in debts for p in d.payments)

    return {
        "total_original": total_original,
        "total_paid": total_paid,
        "total_remaining": total_original - total_paid
    }


# ============================================================
# INSURANCE DATA ENDPOINTS
# ============================================================

@app.get("/insurance")
def get_insurance_records(
    skip: int = 0,
    limit: int = Query(10, le=100),
    smoker: Optional[str] = None,
    region: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.InsuranceRecord)

    if smoker:
        query = query.filter(models.InsuranceRecord.smoker == smoker)

    if region:
        query = query.filter(models.InsuranceRecord.region == region)

    return query.offset(skip).limit(limit).all()


@app.get("/analytics/average-cost-by-region")
def average_cost_by_region(db: Session = Depends(get_db)):
    records = db.query(models.InsuranceRecord).all()

    if not records:
        return {"message": "No insurance data found"}

    region_totals = {}
    region_counts = {}

    for r in records:
        region_totals[r.region] = region_totals.get(r.region, 0) + r.charges
        region_counts[r.region] = region_counts.get(r.region, 0) + 1

    averages = {
        region: region_totals[region] / region_counts[region]
        for region in region_totals
    }

    return averages