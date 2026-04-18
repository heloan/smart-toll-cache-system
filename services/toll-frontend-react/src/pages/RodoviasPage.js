import React, { useState, useEffect } from 'react';
import { rodoviaApi } from '../services/api';

function RodoviasPage() {
  const [rodovias, setRodovias] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await rodoviaApi.listar();
        setRodovias(response.data);
      } catch (error) {
        console.error('Erro ao carregar rodovias:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Rodovias</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#e3f2fd', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Código</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Nome</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>UF</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Extensão (km)</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Concessionária</th>
            </tr>
          </thead>
          <tbody>
            {rodovias.map((r) => (
              <tr key={r.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.codigo}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.nome}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.uf}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.extensaoKm}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.concessionariaNome || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default RodoviasPage;
