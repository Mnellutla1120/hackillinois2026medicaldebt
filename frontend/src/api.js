/**
 * API client for Medical Debt Risk & Repayment Planning API
 */
// DEV: Vite proxy to backend. Production: same origin when served from FastAPI
const API_BASE = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '');

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const msg = Array.isArray(err.detail)
      ? err.detail.map((e) => e.msg || JSON.stringify(e)).join('. ')
      : (typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
    throw new Error(msg || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  createDebt: (data) => request('/debts', { method: 'POST', body: JSON.stringify(data) }),
  getDebts: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/debts${q ? `?${q}` : ''}`);
  },
  getDebt: (id) => request(`/debts/${id}`),
  getDebtSummary: (id) => request(`/debts/${id}/summary`),
  updateDebt: (id, data) => request(`/debts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteDebt: (id) => request(`/debts/${id}`, { method: 'DELETE' }),
  createCheckoutSession: (debtId, successUrl, cancelUrl, amount, paymentType) =>
    request('/stripe/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({
        debt_id: debtId,
        success_url: successUrl,
        cancel_url: cancelUrl,
        ...(amount != null && { amount: Number(amount) }),
        ...(paymentType && { payment_type: paymentType }),
      }),
    }),
};
