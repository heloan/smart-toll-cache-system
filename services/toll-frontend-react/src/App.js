import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TransacoesPage from './pages/TransacoesPage';
import CorrecoesPage from './pages/CorrecoesPage';
import PracasPage from './pages/PracasPage';
import PerformancePage from './pages/PerformancePage';

function App() {
  return (
    <Router>
      <div style={{ fontFamily: 'sans-serif' }}>
        <nav style={{ background: '#1a237e', padding: '12px 24px', display: 'flex', gap: '20px' }}>
          <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>
            Smart Toll
          </Link>
          <Link to="/transacoes" style={{ color: '#cfd8dc', textDecoration: 'none' }}>Transações</Link>
          <Link to="/correcoes" style={{ color: '#cfd8dc', textDecoration: 'none' }}>Correções</Link>
          <Link to="/pracas" style={{ color: '#cfd8dc', textDecoration: 'none' }}>Praças</Link>
          <Link to="/performance" style={{ color: '#cfd8dc', textDecoration: 'none' }}>Performance</Link>
        </nav>
        <main style={{ padding: '24px' }}>
          <Routes>
            <Route path="/" element={<TransacoesPage />} />
            <Route path="/transacoes" element={<TransacoesPage />} />
            <Route path="/correcoes" element={<CorrecoesPage />} />
            <Route path="/pracas" element={<PracasPage />} />
            <Route path="/performance" element={<PerformancePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
