import React, { useState, useEffect } from 'react';
import { operadorApi } from '../services/api';

function OperadoresPage() {
  const [operadores, setOperadores] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await operadorApi.listar();
        setOperadores(response.data);
      } catch (error) {
        console.error('Erro ao carregar operadores:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Operadores</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#e0f2f1', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Username</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Nome Completo</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Email</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Ativo</th>
            </tr>
          </thead>
          <tbody>
            {operadores.map((o) => (
              <tr key={o.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{o.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{o.username}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{o.nomeCompleto}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{o.email}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: o.ativo ? '#c8e6c9' : '#ffcdd2',
                    color: o.ativo ? '#2e7d32' : '#c62828',
                    fontWeight: 'bold',
                    fontSize: '12px'
                  }}>
                    {o.ativo ? 'Sim' : 'Não'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default OperadoresPage;
