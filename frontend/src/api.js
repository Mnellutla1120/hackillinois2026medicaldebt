/**
 * API client for Medical Debt Risk & Repayment Planning API
 */
const API_BASE = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
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
};
