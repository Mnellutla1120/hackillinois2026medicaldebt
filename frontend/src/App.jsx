import { useState, useEffect } from 'react';
import { CreateDebtForm } from './components/CreateDebtForm';
import { DebtList } from './components/DebtList';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [paymentStatus, setPaymentStatus] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const status = params.get('payment');
    if (status === 'success' || status === 'cancelled') {
      setPaymentStatus(status);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const handleCreated = () => {
    setRefreshTrigger((t) => t + 1);
  };

  return (
    <div className="app">
      {paymentStatus && (
        <div className={`payment-banner ${paymentStatus}`}>
          {paymentStatus === 'success' ? '✓ Payment successful!' : 'Payment cancelled.'}
          <button onClick={() => setPaymentStatus(null)}>×</button>
        </div>
      )}
      <header className="header">
        <h1>MediPay</h1>
        <p>Assess financial risk and plan repayment for medical debt.</p>
      </header>
      <main className="main">
        <CreateDebtForm onCreated={handleCreated} />
        <DebtList refreshTrigger={refreshTrigger} />
      </main>
    </div>
  );
}

export default App;
