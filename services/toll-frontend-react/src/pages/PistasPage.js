import React, { useState, useEffect } from 'react';
import { pistaApi } from '../services/api';

function PistasPage() {
  const [pistas, setPistas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await pistaApi.listar();
        setPistas(response.data);
      } catch (error) {
        console.error('Erro ao carregar pistas:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Pistas de Pedágio</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3e5f5', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Nº Pista</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Tipo</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Sentido</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Praça</th>
            </tr>
          </thead>
          <tbody>
            {pistas.map((p) => (
              <tr key={p.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.numeroPista}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.tipoPista}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.sentido}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.pracaNome || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PistasPage;
