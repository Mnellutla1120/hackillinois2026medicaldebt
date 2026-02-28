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
      };
      const res = await api.createDebt(data);
      setResult(res);
      setForm({ patient_name: '', income: '', debt_amount: '', credit_score: '', provider: '' });
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
              min="1"
              step="1000"
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
              min="1"
              step="100"
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
        {error && <p className="error">{error}</p>}
        {result && (
          <div className="result-card">
            <p className="result-title">Assessment complete</p>
            <p className="risk-level" data-level={result.risk_level.toLowerCase()}>
              {result.risk_level} Risk
            </p>
            <p>Monthly payment: <strong>${result.recommended_monthly_payment.toLocaleString()}</strong></p>
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
