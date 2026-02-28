import { useState } from 'react';
import { api } from '../api';
import { DebtDetail } from './DebtDetail';
import './DebtCard.css';

export function DebtCard({ debt, onDelete }) {
  const [showDetail, setShowDetail] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!confirm('Delete this debt record?')) return;
    setDeleting(true);
    try {
      await api.deleteDebt(debt.id);
      onDelete?.(debt.id);
    } catch (err) {
      alert(err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <article
        className="debt-card"
        onClick={() => setShowDetail(true)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setShowDetail(true)}
      >
        <div className="debt-card-header">
          <span className="patient">{debt.patient_name}</span>
          <span className={`risk-badge risk-${debt.risk_level.toLowerCase()}`}>
            {debt.risk_level}
          </span>
        </div>
        <p className="provider">{debt.provider}</p>
        <p className="amount">${debt.debt_amount.toLocaleString()} debt</p>
        <p className="payment">${debt.recommended_monthly_payment.toLocaleString()}/mo</p>
        <button
          className="delete-btn"
          onClick={handleDelete}
          disabled={deleting}
          aria-label="Delete"
        >
          {deleting ? '…' : '×'}
        </button>
      </article>
      {showDetail && (
        <DebtDetail
          debtId={debt.id}
          onClose={() => setShowDetail(false)}
          onDeleted={() => {
            setShowDetail(false);
            onDelete?.(debt.id);
          }}
        />
      )}
    </>
  );
}
