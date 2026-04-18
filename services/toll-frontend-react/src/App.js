import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import TransacoesPage from './pages/TransacoesPage';
import CorrecoesPage from './pages/CorrecoesPage';
import PracasPage from './pages/PracasPage';
import PistasPage from './pages/PistasPage';
import RodoviasPage from './pages/RodoviasPage';
import ConcessionariasPage from './pages/ConcessionariasPage';
import TarifasPage from './pages/TarifasPage';
import OperadoresPage from './pages/OperadoresPage';
import PerformancePage from './pages/PerformancePage';

const navStyle = {
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  padding: '1rem 2rem',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
};

const linkStyle = { color: '#fff', textDecoration: 'none', padding: '0.5rem 1rem', borderRadius: '5px', transition: 'background 0.3s' };

function App() {
  return (
    <Router>
      <div style={{ fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", background: '#f5f7fa', minHeight: '100vh' }}>
        <nav style={navStyle}>
          <div style={{ marginBottom: '0.5rem' }}>
            <Link to="/" style={{ color: '#fff', textDecoration: 'none', fontSize: '1.5rem', fontWeight: 'bold' }}>
              🛣️ Sistema de Gestão Rodoviária
            </Link>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <Link to="/" style={linkStyle}>Início</Link>
            <Link to="/concessionarias" style={linkStyle}>Concessionárias</Link>
            <Link to="/rodovias" style={linkStyle}>Rodovias</Link>
            <Link to="/pracas" style={linkStyle}>Praças</Link>
            <Link to="/pistas" style={linkStyle}>Pistas</Link>
            <Link to="/tarifas" style={linkStyle}>Tarifas</Link>
            <Link to="/operadores" style={linkStyle}>Operadores</Link>
            <Link to="/transacoes" style={linkStyle}>Transações</Link>
            <Link to="/correcoes" style={linkStyle}>Correções</Link>
            <Link to="/performance" style={linkStyle}>Performance</Link>
          </div>
        </nav>
        <main style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 2rem' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/transacoes" element={<TransacoesPage />} />
            <Route path="/correcoes" element={<CorrecoesPage />} />
            <Route path="/concessionarias" element={<ConcessionariasPage />} />
            <Route path="/rodovias" element={<RodoviasPage />} />
            <Route path="/pracas" element={<PracasPage />} />
            <Route path="/pistas" element={<PistasPage />} />
            <Route path="/tarifas" element={<TarifasPage />} />
            <Route path="/operadores" element={<OperadoresPage />} />
            <Route path="/performance" element={<PerformancePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
