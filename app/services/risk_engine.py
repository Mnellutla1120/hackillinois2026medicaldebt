"""
Risk scoring and repayment planning engine for medical debt.
"""
from dataclasses import dataclass


@dataclass
class RiskResult:
    """Result of risk calculation."""
    risk_score: float
    risk_level: str
    recommended_monthly_payment: float


def calculate_risk(
    debt_amount: float,
    income: float,
    credit_score: int,
    repayment_months: int = 24,
) -> RiskResult:
    """
    Calculate medical debt risk score and recommended payment.
    
    Formula: risk_score = (debt_amount / income) * (700 - credit_score) / 700
    - Higher debt-to-income ratio = higher risk
    - Lower credit score = higher risk
    
    Risk levels:
    - Low:   < 0.2
    - Medium: 0.2 - 0.5
    - High:   >= 0.5
    """
    if income <= 0:
        raise ValueError("Income must be greater than 0")
    
    # Debt-to-income component (0 to ~inf, typically 0-2)
    dti = debt_amount / income
    
    # Credit score component: 300-850 maps to (700-0)/700 = 0.57 to 0
    # Lower score = higher multiplier
    credit_factor = (700 - min(credit_score, 700)) / 700
    
    risk_score = dti * credit_factor
    
    # Clamp to [0, 1] for interpretability
    risk_score = min(max(risk_score, 0.0), 1.0)
    
    # Classify risk level
    if risk_score < 0.2:
        risk_level = "Low"
    elif risk_score < 0.5:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    # Recommended monthly payment: debt / repayment_months
    # Minimum 1 month, cap at 24 months for high-risk
    months = max(1, min(repayment_months, 36))
    recommended_monthly_payment = round(debt_amount / months, 2)
    
    return RiskResult(
        risk_score=round(risk_score, 4),
        risk_level=risk_level,
        recommended_monthly_payment=recommended_monthly_payment,
    )
