"""
Risk scoring and repayment planning engine for medical debt.
Supports interest, down payment, and flexible term.
"""
import math
from dataclasses import dataclass


@dataclass
class RiskResult:
    """Result of risk calculation."""
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float
    total_interest: float
    amount_after_down_payment: float
    estimated_payoff_months: int


def calculate_risk(
    debt_amount: float,
    income: float,
    credit_score: int,
    repayment_months: int = 24,
    interest_rate: float = 0.0,
    down_payment: float = 0.0,
) -> RiskResult:
    """
    Calculate medical debt risk score and recommended payment.

    Risk formula: risk_score = (debt_amount / income) * (700 - credit_score) / 700

    Repayment:
    - Principal = debt_amount - down_payment (min 0)
    - If interest_rate > 0: amortization formula (monthly payment so loan pays off in n months)
    - If interest_rate == 0: monthly_payment = principal / months

    Risk levels: Low < 0.2, Medium 0.2-0.5, High >= 0.5
    """
    if income <= 0:
        raise ValueError("Income must be greater than 0")
    if down_payment >= debt_amount:
        raise ValueError("Down payment must be less than debt amount")
    if down_payment < 0:
        raise ValueError("Down payment cannot be negative")

    amount_after_down_payment = max(0.0, debt_amount - down_payment)

    # Risk (based on full debt amount and income)
    dti = debt_amount / income
    credit_factor = (700 - min(credit_score, 700)) / 700
    risk_score = dti * credit_factor
    risk_score = min(max(risk_score, 0.0), 1.0)

    if risk_score < 0.2:
        risk_level = "Low"
    elif risk_score < 0.5:
        risk_level = "Medium"
    else:
        risk_level = "High"

    months = max(1, min(repayment_months, 120))
    total_interest = 0.0

    if amount_after_down_payment <= 0:
        recommended_monthly_payment = 0.0
        estimated_payoff_months = 0
    elif interest_rate <= 0:
        recommended_monthly_payment = round(amount_after_down_payment / months, 2)
        estimated_payoff_months = months
    else:
        # Amortization: P * (r(1+r)^n) / ((1+r)^n - 1)
        r = interest_rate / 12.0  # monthly rate
        n = months
        if r <= 0 or n <= 0:
            recommended_monthly_payment = round(amount_after_down_payment / months, 2)
            estimated_payoff_months = months
        else:
            factor = (r * (1 + r) ** n) / ((1 + r) ** n - 1)
            recommended_monthly_payment = round(amount_after_down_payment * factor, 2)
            total_paid = recommended_monthly_payment * n
            total_interest = round(total_paid - amount_after_down_payment, 2)
            estimated_payoff_months = n

    return RiskResult(
        risk_score=round(risk_score, 4),
        risk_level=risk_level,
        recommended_monthly_payment=recommended_monthly_payment,
        total_interest=total_interest,
        amount_after_down_payment=round(amount_after_down_payment, 2),
        estimated_payoff_months=estimated_payoff_months,
    )
