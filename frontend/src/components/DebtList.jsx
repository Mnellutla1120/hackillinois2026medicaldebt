import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import { DebtCard } from './DebtCard';
import './DebtList.css';

export function DebtList({ refreshTrigger }) {
  const [debts, setDebts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    risk_level: '',
    provider: '',
    patient_name: '',
    limit: 20,
    offset: 0,
  });

  const fetchDebts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filters.risk_level) params.risk_level = filters.risk_level;
      if (filters.provider) params.provider = filters.provider;
      if (filters.patient_name) params.patient_name = filters.patient_name;
      params.limit = filters.limit;
      params.offset = filters.offset;
      const res = await api.getDebts(params);
      setDebts(res.items);
      setTotal(res.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDebts();
  }, [fetchDebts, refreshTrigger]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value, offset: 0 }));
  };

  const handleDelete = (id) => {
    setDebts((prev) => prev.filter((d) => d.id !== id));
    setTotal((t) => Math.max(0, t - 1));
  };

  const pages = Math.ceil(total / filters.limit);
  const currentPage = Math.floor(filters.offset / filters.limit) + 1;

  return (
    <section className="debt-list">
      <div className="debt-list-header">
        <h2>Debt Records</h2>
        <div className="filters">
          <select
            value={filters.risk_level}
            onChange={(e) => handleFilterChange('risk_level', e.target.value)}
          >
            <option value="">All risk levels</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
          <input
            type="text"
            placeholder="Filter by provider"
            value={filters.provider}
            onChange={(e) => handleFilterChange('provider', e.target.value)}
          />
          <input
            type="text"
            placeholder="Search patient"
            value={filters.patient_name}
            onChange={(e) => handleFilterChange('patient_name', e.target.value)}
          />
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p className="loading">Loading…</p>
      ) : debts.length === 0 ? (
        <p className="empty">No debt records found.</p>
      ) : (
        <>
          <p className="count">Showing {debts.length} of {total}</p>
          <div className="debt-grid">
            {debts.map((debt) => (
              <DebtCard key={debt.id} debt={debt} onDelete={handleDelete} />
            ))}
          </div>
          {pages > 1 && (
            <div className="pagination">
              <button
                disabled={filters.offset === 0}
                onClick={() => handleFilterChange('offset', filters.offset - filters.limit)}
              >
                Previous
              </button>
              <span>Page {currentPage} of {pages}</span>
              <button
                disabled={filters.offset + filters.limit >= total}
                onClick={() => handleFilterChange('offset', filters.offset + filters.limit)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
