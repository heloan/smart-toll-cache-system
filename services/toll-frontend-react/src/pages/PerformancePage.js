import React, { useState, useEffect } from 'react';
import { performanceApi } from '../services/api';

function PerformancePage() {
  const [registros, setRegistros] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await performanceApi.listar({ limite: 50 });
        setRegistros(response.data);
      } catch (error) {
        console.error('Erro ao carregar performance:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Registros de Performance</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: '#ede7f6', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Endpoint</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Método</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Tempo (ms)</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Status</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Origem Dados</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Memória Usada (MB)</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>CPU (%)</th>
            </tr>
          </thead>
          <tbody>
            {registros.map((r) => (
              <tr key={r.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.endpoint}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.metodoHttp}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.tempoProcessamentoMs}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.statusHttp}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.origemDados}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{r.memoriaUsadaMb?.toFixed(1)}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{(r.usoCpuProcesso * 100)?.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PerformancePage;
