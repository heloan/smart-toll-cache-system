import React, { useState, useEffect } from 'react';
import { transacaoApi, correcaoApi, operadorApi } from '../services/api';

function CorrecoesPage() {
  const [transacoesComOcorrencia, setTransacoesComOcorrencia] = useState([]);
  const [operadores, setOperadores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [correcaoForm, setCorrecaoForm] = useState({ transacaoId: null, operadorId: '', motivo: '', valorCorrigido: '' });

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    setLoading(true);
    try {
      const [transRes, opRes] = await Promise.all([
        transacaoApi.listarOcorrencias({ limite: 50 }),
        operadorApi.listar(),
      ]);
      setTransacoesComOcorrencia(transRes.data);
      setOperadores(opRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrigir = async (e) => {
    e.preventDefault();
    try {
      await correcaoApi.criar(correcaoForm.transacaoId, {
        operadorId: parseInt(correcaoForm.operadorId),
        motivo: correcaoForm.motivo,
        valorCorrigido: parseFloat(correcaoForm.valorCorrigido),
        tipoCorrecao: 'MANUAL',
      });
      setCorrecaoForm({ transacaoId: null, operadorId: '', motivo: '', valorCorrigido: '' });
      carregarDados();
    } catch (error) {
      console.error('Erro ao corrigir transação:', error);
    }
  };

  return (
    <div>
      <h1>Correção de Transações</h1>
      {correcaoForm.transacaoId && (
        <form onSubmit={handleCorrigir} style={{ background: '#fff3e0', padding: '16px', marginBottom: '16px', borderRadius: '8px' }}>
          <h3>Corrigir Transação #{correcaoForm.transacaoId}</h3>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <select value={correcaoForm.operadorId} onChange={(e) => setCorrecaoForm({ ...correcaoForm, operadorId: e.target.value })} required style={{ padding: '8px' }}>
              <option value="">Selecione operador</option>
              {operadores.map((op) => (<option key={op.id} value={op.id}>{op.nomeCompleto}</option>))}
            </select>
            <input type="number" step="0.01" placeholder="Valor corrigido" value={correcaoForm.valorCorrigido} onChange={(e) => setCorrecaoForm({ ...correcaoForm, valorCorrigido: e.target.value })} required style={{ padding: '8px' }} />
            <input type="text" placeholder="Motivo da correção" value={correcaoForm.motivo} onChange={(e) => setCorrecaoForm({ ...correcaoForm, motivo: e.target.value })} required style={{ padding: '8px', flex: 1 }} />
            <button type="submit" style={{ padding: '8px 16px', background: '#4caf50', color: '#fff', border: 'none', borderRadius: '4px' }}>Confirmar</button>
            <button type="button" onClick={() => setCorrecaoForm({ transacaoId: null, operadorId: '', motivo: '', valorCorrigido: '' })} style={{ padding: '8px 16px' }}>Cancelar</button>
          </div>
        </form>
      )}
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#fce4ec', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Placa</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Valor Original</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Status</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Data/Hora</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Ação</th>
            </tr>
          </thead>
          <tbody>
            {transacoesComOcorrencia.map((t) => (
              <tr key={t.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.placa}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>R$ {t.valorOriginal?.toFixed(2)}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.statusTransacao}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{t.dataHoraPassagem}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>
                  {t.statusTransacao === 'OCORRENCIA' && (
                    <button onClick={() => setCorrecaoForm({ ...correcaoForm, transacaoId: t.id })} style={{ padding: '4px 12px', background: '#ff9800', color: '#fff', border: 'none', borderRadius: '4px' }}>
                      Corrigir
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CorrecoesPage;
