from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


# =====================================================
# -------------------- DEBT MODEL ---------------------
# =====================================================

class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    original_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    status = Column(String, default="active", nullable=False)

    # Relationship to payments
    payments = relationship(
        "Payment",
        back_populates="debt",
        cascade="all, delete-orphan"
    )


# =====================================================
# ------------------- PAYMENT MODEL -------------------
# =====================================================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer, ForeignKey("debts.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)

    debt = relationship("Debt", back_populates="payments")


# =====================================================
# --------------- INSURANCE DATA MODEL ----------------
# =====================================================

class InsuranceRecord(Base):
    __tablename__ = "insurance_records"

    id = Column(Integer, primary_key=True, index=True)

    age = Column(Integer, nullable=False, index=True)
    sex = Column(String, nullable=False)
    bmi = Column(Float, nullable=False)
    children = Column(Integer, nullable=False)
    smoker = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    charges = Column(Float, nullable=False)