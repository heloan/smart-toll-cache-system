import React, { useState, useEffect } from 'react';
import { transacaoApi } from '../services/api';

function TransacoesPage() {
  const [transacoes, setTransacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroPlaca, setFiltroPlaca] = useState('');

  useEffect(() => {
    carregarTransacoes();
  }, []);

  const carregarTransacoes = async () => {
    setLoading(true);
    try {
      const response = await transacaoApi.listar({ limite: 100 });
      setTransacoes(response.data);
    } catch (error) {
      console.error('Erro ao carregar transações:', error);
    } finally {
      setLoading(false);
    }
  };

  const transacoesFiltradas = filtroPlaca
    ? transacoes.filter((t) => t.placa?.toLowerCase().includes(filtroPlaca.toLowerCase()))
    : transacoes;

  return (
    <div>
      <h1>Transações de Pedágio</h1>
      <div style={{ marginBottom: '16px' }}>
        <input
          type="text"
          placeholder="Filtrar por placa..."
          value={filtroPlaca}
          onChange={(e) => setFiltroPlaca(e.target.value)}
          style={{ padding: '8px', width: '250px', marginRight: '8px' }}
        />
        <button onClick={carregarTransacoes} style={{ padding: '8px 16px' }}>
          Atualizar
        </button>
      </div>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#e3f2fd', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Placa</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Tipo Veículo</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Valor</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Status</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Data/Hora</th>
            </tr>
          </thead>
          <tbody>
            {transacoesFiltradas.map((t) => (
              <tr key={t.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.placa}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.tipoVeiculo}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>R$ {t.valorOriginal?.toFixed(2)}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      background:
                        t.statusTransacao === 'OK' ? '#c8e6c9' : t.statusTransacao === 'CORRIGIDA' ? '#fff9c4' : '#ffcdd2',
                    }}
                  >
                    {t.statusTransacao}
                  </span>
                </td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.dataHoraPassagem}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TransacoesPage;
