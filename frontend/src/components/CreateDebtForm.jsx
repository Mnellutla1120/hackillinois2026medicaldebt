import { useState } from 'react';
import { api } from '../api';
import './CreateDebtForm.css';

export function CreateDebtForm({ onCreated }) {
  const [form, setForm] = useState({
    patient_name: '',
    income: '',
    debt_amount: '',
    credit_score: '',
    provider: '',
    interest_rate: '',
    down_payment: '',
    repayment_months: '24',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = {
        patient_name: form.patient_name.trim(),
        income: parseFloat(form.income),
        debt_amount: parseFloat(form.debt_amount),
        credit_score: parseInt(form.credit_score, 10),
        provider: form.provider.trim(),
        interest_rate: form.interest_rate ? parseFloat(form.interest_rate) : 0,
        down_payment: form.down_payment ? parseFloat(form.down_payment) : 0,
        repayment_months: form.repayment_months ? parseInt(form.repayment_months, 10) : 24,
      };
      const res = await api.createDebt(data);
      setResult(res);
      setForm({ patient_name: '', income: '', debt_amount: '', credit_score: '', provider: '', interest_rate: '', down_payment: '', repayment_months: '24' });
      onCreated?.(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="create-debt-form">
      <h2>Add Medical Debt</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <label>
            Patient Name
            <input
              type="text"
              name="patient_name"
              value={form.patient_name}
              onChange={handleChange}
              required
              placeholder="Jane Doe"
            />
          </label>
          <label>
            Provider
            <input
              type="text"
              name="provider"
              value={form.provider}
              onChange={handleChange}
              required
              placeholder="Carle Hospital"
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Annual Income ($)
            <input
              type="number"
              name="income"
              value={form.income}
              onChange={handleChange}
              required
              min="0"  
              step="any"
              placeholder="55000"
            />
          </label>
          <label>
            Debt Amount ($)
            <input
              type="number"
              name="debt_amount"
              value={form.debt_amount}
              onChange={handleChange}
              required
              min="0"
              step="any"
              placeholder="12000"
            />
          </label>
          <label>
            Credit Score
            <input
              type="number"
              name="credit_score"
              value={form.credit_score}
              onChange={handleChange}
              required
              min="300"
              max="850"
              placeholder="640"
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Interest rate (annual, e.g. 0.05 = 5%)
            <input
              type="number"
              name="interest_rate"
              value={form.interest_rate}
              onChange={handleChange}
              min="0"
              max="0.5"
              step="0.01"
              placeholder="0"
            />
          </label>
          <label>
            Down payment ($)
            <input
              type="number"
              name="down_payment"
              value={form.down_payment}
              onChange={handleChange}
              min="0"
              step="100"
              placeholder="0"
            />
          </label>
          <label>
            Repayment term (months)
            <input
              type="number"
              name="repayment_months"
              value={form.repayment_months}
              onChange={handleChange}
              min="1"
              max="120"
              placeholder="24"
            />
          </label>
        </div>
        {error && <p className="error">{error}</p>}
        {result && (
          <div className="result-card">
            <p className="result-title">Assessment complete</p>
            <p className="risk-level" data-level={result.risk_level.toLowerCase()}>
              {result.risk_level} Risk
            </p>
            <p>Monthly payment: <strong>${(result.recommended_monthly_payment ?? 0).toLocaleString()}</strong></p>
            {result.total_interest > 0 && <p>Total interest: ${result.total_interest.toLocaleString()}</p>}
            {result.amount_after_down_payment != null && result.amount_after_down_payment > 0 && (
              <p>After down payment: ${result.amount_after_down_payment.toLocaleString()} over {result.estimated_payoff_months} months</p>
            )}
            <p className="risk-score">Score: {result.risk_score}</p>
          </div>
        )}
        <button type="submit" disabled={loading}>
          {loading ? 'Assessing…' : 'Assess & Submit'}
        </button>
      </form>
    </section>
  );
}
