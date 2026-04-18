import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export const transacaoApi = {
  listar: (params) => api.get('/transacoes', { params }),
  buscarPorId: (id) => api.get(`/transacoes/${id}`),
  criar: (data) => api.post('/transacoes', data),
  listarOcorrencias: (params) => api.get('/transacoes/ocorrencias/pendentes', { params }),
};

export const correcaoApi = {
  listar: (params) => api.get('/correcoes', { params }),
  criar: (transacaoId, data) => api.post(`/correcoes/transacao/${transacaoId}`, data),
};

export const pracaApi = {
  listar: () => api.get('/pracas'),
  buscarPorId: (id) => api.get(`/pracas/${id}`),
};

export const pistaApi = {
  listar: () => api.get('/pistas'),
};

export const tarifaApi = {
  listar: () => api.get('/tarifas'),
};

export const operadorApi = {
  listar: () => api.get('/operadores'),
};

export const rodoviaApi = {
  listar: () => api.get('/rodovias'),
};

export const concessionariaApi = {
  listar: () => api.get('/concessionarias'),
};

export const performanceApi = {
  listar: (params) => api.get('/performance', { params }),
};

export default api;
