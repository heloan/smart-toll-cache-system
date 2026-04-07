import React, { useState, useEffect } from 'react';
import { pracaApi } from '../services/api';

function PracasPage() {
  const [pracas, setPracas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await pracaApi.listar();
        setPracas(response.data);
      } catch (error) {
        console.error('Erro ao carregar praças:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Praças de Pedágio</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#e8f5e9', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Nome</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>KM</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Sentido</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Ativa</th>
            </tr>
          </thead>
          <tbody>
            {pracas.map((p) => (
              <tr key={p.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.nome}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.km}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.sentido}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{p.ativa ? 'Sim' : 'Não'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PracasPage;
