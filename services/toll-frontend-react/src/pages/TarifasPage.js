import React, { useState, useEffect } from 'react';
import { tarifaApi } from '../services/api';

function TarifasPage() {
  const [tarifas, setTarifas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await tarifaApi.listar();
        setTarifas(response.data);
      } catch (error) {
        console.error('Erro ao carregar tarifas:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Tarifas de Pedágio</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#fff3e0', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Tipo Veículo</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Valor (R$)</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Vigência Início</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Vigência Fim</th>
            </tr>
          </thead>
          <tbody>
            {tarifas.map((t) => (
              <tr key={t.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.tipoVeiculo}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>
                  {t.valor != null ? `R$ ${Number(t.valor).toFixed(2)}` : '—'}
                </td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.vigenciaInicio || '—'}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.vigenciaFim || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TarifasPage;
