import { useState } from 'react';
import { CreateDebtForm } from './components/CreateDebtForm';
import { DebtList } from './components/DebtList';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleCreated = () => {
    setRefreshTrigger((t) => t + 1);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Medical Debt Risk & Repayment</h1>
        <p>Assess risk and plan repayments for medical debt</p>
      </header>
      <main className="main">
        <CreateDebtForm onCreated={handleCreated} />
        <DebtList refreshTrigger={refreshTrigger} />
      </main>
    </div>
  );
}

export default App;
