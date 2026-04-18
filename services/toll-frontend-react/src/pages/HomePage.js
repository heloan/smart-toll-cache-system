import React from 'react';
import { Link } from 'react-router-dom';

const cards = [
  { icon: '🏢', title: 'Concessionárias', desc: 'Cadastre e gerencie empresas concessionárias', to: '/concessionarias' },
  { icon: '🛣️', title: 'Rodovias', desc: 'Cadastre rodovias vinculadas às concessionárias', to: '/rodovias' },
  { icon: '🏪', title: 'Praças de Pedágio', desc: 'Gerencie praças de pedágio nas rodovias', to: '/pracas' },
  { icon: '🚧', title: 'Pistas', desc: 'Configure pistas das praças de pedágio', to: '/pistas' },
  { icon: '💰', title: 'Tarifas de Pedágio', desc: 'Gerencie tarifas por tipo de veículo', to: '/tarifas' },
  { icon: '👤', title: 'Operadores', desc: 'Cadastre operadores do sistema', to: '/operadores' },
  { icon: '💳', title: 'Transações de Pedágio', desc: 'Visualize e gerencie transações', to: '/transacoes' },
  { icon: '🔧', title: 'Correções de Transação', desc: 'Histórico de correções realizadas', to: '/correcoes' },
  { icon: '📊', title: 'Análise de Performance', desc: 'Monitore métricas e desempenho do sistema', to: '/performance' },
];

const styles = {
  hero: {
    textAlign: 'center',
    marginBottom: '3rem',
  },
  heroTitle: {
    fontSize: '2.5rem',
    color: '#667eea',
    marginBottom: '1rem',
  },
  heroDesc: {
    fontSize: '1.2rem',
    color: '#666',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '2rem',
    marginBottom: '3rem',
  },
  card: {
    background: '#fff',
    padding: '2rem',
    borderRadius: '10px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    textAlign: 'center',
    transition: 'transform 0.3s, box-shadow 0.3s',
    cursor: 'pointer',
  },
  cardIcon: {
    fontSize: '3rem',
    marginBottom: '1rem',
  },
  cardTitle: {
    color: '#667eea',
    marginBottom: '0.5rem',
  },
  cardDesc: {
    color: '#666',
    marginBottom: '1.5rem',
  },
  btn: {
    display: 'inline-block',
    padding: '0.6rem 1.5rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: '#fff',
    textDecoration: 'none',
    border: 'none',
    borderRadius: '5px',
    fontSize: '1rem',
  },
  footer: {
    textAlign: 'center',
    padding: '2rem',
    background: '#2c3e50',
    color: '#fff',
    marginTop: '3rem',
    borderRadius: '10px',
  },
};

function HomePage() {
  return (
    <div>
      <div style={styles.hero}>
        <h2 style={styles.heroTitle}>Bem-vindo ao Sistema de Gestão</h2>
        <p style={styles.heroDesc}>
          Gerencie concessionárias, rodovias, praças de pedágio, pistas e operadores
        </p>
      </div>

      <div style={styles.grid}>
        {cards.map((c) => (
          <div
            key={c.to}
            style={styles.card}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-5px)'; e.currentTarget.style.boxShadow = '0 8px 15px rgba(0,0,0,0.2)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)'; }}
          >
            <div style={styles.cardIcon}>{c.icon}</div>
            <h3 style={styles.cardTitle}>{c.title}</h3>
            <p style={styles.cardDesc}>{c.desc}</p>
            <Link to={c.to} style={styles.btn}>Acessar</Link>
          </div>
        ))}
      </div>

      <div style={styles.footer}>
        <p>&copy; 2026 Sistema de Gestão Rodoviária — TCC</p>
      </div>
    </div>
  );
}

export default HomePage;
