"""
Stripe Checkout integration for medical debt payments.
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import stripe

from app.database import get_db

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
from app.models import MedicalDebt

router = APIRouter(prefix="/stripe", tags=["stripe"])


class CreateCheckoutRequest(BaseModel):
    debt_id: int
    success_url: str | None = None
    cancel_url: str | None = None


@router.post("/create-checkout-session")
def create_checkout_session(
    payload: CreateCheckoutRequest,
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout session for a debt's recommended monthly payment.
    Returns a URL to redirect the user to Stripe's hosted payment page.
    """
    if not stripe.api_key:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY in environment.",
        )

    record = db.query(MedicalDebt).filter(MedicalDebt.id == payload.debt_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Debt not found")

    amount_cents = int(record.recommended_monthly_payment * 100)
    if amount_cents < 50:  # Stripe minimum
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be at least $0.50",
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Medical debt payment - {record.provider}",
                            "description": f"Monthly payment for {record.patient_name}",
                            "images": [],
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=payload.success_url or "http://localhost:8000/?payment=success",
            cancel_url=payload.cancel_url or "http://localhost:8000/?payment=cancelled",
            metadata={
                "debt_id": str(record.id),
                "patient_name": record.patient_name,
            },
        )
        return {"url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
