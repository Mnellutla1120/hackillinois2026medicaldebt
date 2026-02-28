import { useState, useEffect } from 'react';
import { api } from '../api';
import './DebtDetail.css';

export function DebtDetail({ debtId, onClose, onDeleted }) {
  const [debt, setDebt] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [debtRes, summaryRes] = await Promise.all([
          api.getDebt(debtId),
          api.getDebtSummary(debtId),
        ]);
        setDebt(debtRes);
        setSummary(summaryRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [debtId]);

  const handleDelete = async () => {
    if (!confirm('Delete this debt record?')) return;
    try {
      await api.deleteDebt(debtId);
      onDeleted?.();
    } catch (err) {
      alert(err.message);
    }
  };

  const handlePay = async (amount, paymentType) => {
    setPaying(true);
    try {
      const base = window.location.origin;
      const { url } = await api.createCheckoutSession(
        debtId,
        `${base}/?payment=success`,
        `${base}/?payment=cancelled`,
        amount,
        paymentType
      );
      if (url) window.location.href = url;
    } catch (err) {
      alert(err.message);
    } finally {
      setPaying(false);
    }
  };

  return (

    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>
        {loading ? (
          <p className="loading">Loading…</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : debt && summary ? (
          <div className="debt-detail">
            <h2>{debt.patient_name}</h2>
            <span className={`risk-badge risk-${debt.risk_level.toLowerCase()}`}>
              {debt.risk_level} Risk
            </span>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="label">Provider</span>
                <span className="value">{debt.provider}</span>
              </div>
              <div className="detail-item">
                <span className="label">Debt Amount</span>
                <span className="value">${debt.debt_amount.toLocaleString()}</span>
              </div>
              <div className="detail-item">
                <span className="label">Annual Income</span>
                <span className="value">${debt.income.toLocaleString()}</span>
              </div>
              <div className="detail-item">
                <span className="label">Credit Score</span>
                <span className="value">{debt.credit_score}</span>
              </div>
              <div className="detail-item">
                <span className="label">Risk Score</span>
                <span className="value">{debt.risk_score}</span>
              </div>
              {(debt.interest_rate ?? 0) > 0 && (
                <div className="detail-item">
                  <span className="label">Interest rate / Total interest</span>
                  <span className="value">{(debt.interest_rate * 100).toFixed(1)}% / ${(debt.total_interest ?? summary.total_interest ?? 0).toLocaleString()}</span>
                </div>
              )}
              {(debt.down_payment ?? 0) > 0 && (
                <div className="detail-item">
                  <span className="label">Down payment / Amount remaining</span>
                  <span className="value">${(debt.down_payment ?? 0).toLocaleString()} / ${(summary.amount_remaining ?? debt.debt_amount).toLocaleString()}</span>
                </div>
              )}
              <div className="detail-item highlight">
                <span className="label">Recommended Monthly Payment</span>
                <span className="value">${debt.recommended_monthly_payment.toLocaleString()}</span>
              </div>
              <div className="detail-item">
                <span className="label">Estimated Payoff</span>
                <span className="value">{summary.estimated_payoff_months} months</span>
              </div>
            </div>
            <div className="detail-actions">
              {(debt.down_payment ?? 0) > 0 && (
                <button
                  className="btn-pay btn-pay-down"
                  onClick={() => handlePay(debt.down_payment, 'down_payment')}
                  disabled={paying || debt.down_payment < 0.5}
                >
                  {paying ? '…' : `Pay down $${(debt.down_payment ?? 0).toLocaleString()}`}
                </button>
              )}
              <button
                className="btn-pay"
                onClick={() => handlePay(null, 'monthly')}
                disabled={paying || debt.recommended_monthly_payment < 0.5}
              >
                {paying ? 'Redirecting…' : `Pay $${debt.recommended_monthly_payment.toLocaleString()} (monthly)`}
              </button>
              <button className="btn-danger" onClick={handleDelete}>
                Delete Record
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
