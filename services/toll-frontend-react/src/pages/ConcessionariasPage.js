import React, { useState, useEffect } from 'react';
import { concessionariaApi } from '../services/api';

function ConcessionariasPage() {
  const [concessionarias, setConcessionarias] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      try {
        const response = await concessionariaApi.listar();
        setConcessionarias(response.data);
      } catch (error) {
        console.error('Erro ao carregar concessionárias:', error);
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  return (
    <div>
      <h1>Concessionárias</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#fce4ec', textAlign: 'left' }}>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Nome Fantasia</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Razão Social</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>CNPJ</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Contrato</th>
              <th style={{ padding: '8px', border: '1px solid #ccc' }}>Início Contrato</th>
            </tr>
          </thead>
          <tbody>
            {concessionarias.map((c) => (
              <tr key={c.id}>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.id}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.nomeFantasia}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.razaoSocial}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.cnpj}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.contratoConcessao}</td>
                <td style={{ padding: '8px', border: '1px solid #ccc' }}>{c.dataInicioContrato}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ConcessionariasPage;
