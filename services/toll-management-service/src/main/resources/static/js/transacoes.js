let transacoes = [];
let pendentes = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarTransacoes();
    carregarPendentes();
    
    // Verificar se há parâmetro ID na URL
    const urlParams = new URLSearchParams(window.location.search);
    const transacaoId = urlParams.get('id');
    if (transacaoId) {
        setTimeout(() => verDetalhes(parseInt(transacaoId)), 500);
    }
});

async function carregarTransacoes() {
    toggleLoading(true);
    try {
        const limite = document.getElementById('limiteTransacoes').value || 500;
        const status = document.getElementById('statusFiltro').value;
        
        let url = `/transacoes?limite=${limite}`;
        if (status) {
            url = `/transacoes/status/${status}`;
        }
        
        transacoes = await fetchAPI(url);
        renderizarTabelaTransacoes();
        atualizarEstatisticas();
        showAlert(`${transacoes.length} transações carregadas com sucesso!`, 'success');
    } catch (error) {
        showAlert('Erro ao carregar transações: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

async function carregarPendentes() {
    try {
        const limite = document.getElementById('limitePendentes').value || 50;
        const horas = document.getElementById('horasPendentes').value || 48;
        const origemDados = document.getElementById('origemDadosPendentes').value;
        
        let url = `/transacoes/ocorrencias/pendentes?limite=${limite}&horas=${horas}`;
        if (origemDados) {
            url += `&origemDados=${origemDados}`;
        }
        
        pendentes = await fetchAPI(url);
        renderizarTabelaPendentes();
    } catch (error) {
        console.error('Erro ao carregar pendentes:', error);
        showAlert('Erro ao carregar transações pendentes: ' + error.message, 'danger');
    }
}

async function buscarPorId() {
    const id = document.getElementById('buscaId').value;
    if (!id) {
        showAlert('Digite um ID para buscar', 'warning');
        return;
    }
    
    toggleLoading(true);
    try {
        const transacao = await fetchAPI(`/transacoes/${id}`);
        mostrarDetalhes(transacao);
    } catch (error) {
        showAlert('Transação não encontrada', 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabelaPendentes() {
    const tbody = document.getElementById('pendentesTableBody');
    
    if (pendentes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center">Nenhuma transação pendente de correção</td></tr>';
        return;
    }

    tbody.innerHTML = pendentes.map(t => {
        const tipoVeiculoIcon = {
            'MOTO': '🏍️',
            'CARRO': '🚗',
            'CAMINHAO': '🚚'
        };
        
        return `
            <tr style="background-color: #fff3cd;">
                <td>${t.id}</td>
                <td>${formatDateTime(t.dataHoraPassagem)}</td>
                <td>${t.pracaNome}</td>
                <td>Pista ${t.pistaNumeroPista}</td>
                <td><strong>${t.placa}</strong></td>
                <td>${tipoVeiculoIcon[t.tipoVeiculo] || ''} ${t.tipoVeiculo}</td>
                <td style="font-weight: bold;">R$ ${t.valorOriginal.toFixed(2)}</td>
                <td>${formatStatus(t.statusTransacao)}</td>
                <td><span class="badge badge-danger">${t.quantidadeOcorrencias || 0}</span></td>
                <td>
                    <button class="btn btn-small btn-secondary" onclick="verDetalhes(${t.id})">Ver Detalhes</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarTabelaTransacoes() {
    const tbody = document.getElementById('transacoesTableBody');
    
    if (transacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center">Nenhuma transação encontrada</td></tr>';
        return;
    }

    tbody.innerHTML = transacoes.map(t => {
        const tipoVeiculoIcon = {
            'MOTO': '🏍️',
            'CARRO': '🚗',
            'CAMINHAO': '🚚'
        };
        
        return `
            <tr>
                <td>${t.id}</td>
                <td>${formatDateTime(t.dataHoraPassagem)}</td>
                <td>${t.pracaNome}</td>
                <td>Pista ${t.pistaNumeroPista}</td>
                <td><strong>${t.placa}</strong></td>
                <td>${t.tagId || '-'}</td>
                <td>${tipoVeiculoIcon[t.tipoVeiculo] || ''} ${t.tipoVeiculo}</td>
                <td>R$ ${t.valorOriginal.toFixed(2)}</td>
                <td>${formatStatus(t.statusTransacao)}</td>
                <td>${t.quantidadeOcorrencias > 0 ? `<span class="badge badge-danger">${t.quantidadeOcorrencias}</span>` : '-'}</td>
                <td>${t.quantidadeCorrecoes > 0 ? `<span class="badge badge-success">${t.quantidadeCorrecoes}</span>` : '-'}</td>
                <td>
                    <button class="btn btn-small btn-secondary" onclick="verDetalhes(${t.id})">Detalhes</button>
                </td>
            </tr>
        `;
    }).join('');
}

function formatStatus(status) {
    const statusConfig = {
        'OK': '<span class="badge badge-success">✓ OK</span>',
        'OCORRENCIA': '<span class="badge badge-danger">⚠ Ocorrência</span>',
        'CORRIGIDA': '<span class="badge" style="background: #d1ecf1; color: #0c5460;">✓ Corrigida</span>'
    };
    return statusConfig[status] || status;
}

async function verDetalhes(id) {
    toggleLoading(true);
    try {
        const transacao = await fetchAPI(`/transacoes/${id}`);
        mostrarDetalhes(transacao);
    } catch (error) {
        showAlert('Erro ao carregar detalhes: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function mostrarDetalhes(transacao) {
    document.getElementById('modalTransacaoId').textContent = transacao.id;
    document.getElementById('detailDataHora').textContent = formatDateTime(transacao.dataHoraPassagem);
    document.getElementById('detailStatus').innerHTML = formatStatus(transacao.statusTransacao);
    document.getElementById('detailPraca').textContent = transacao.pracaNome;
    document.getElementById('detailPista').textContent = `Pista ${transacao.pistaNumeroPista}`;
    document.getElementById('detailPlaca').textContent = transacao.placa;
    document.getElementById('detailTagId').textContent = transacao.tagId || 'Não informado';
    document.getElementById('detailTipoVeiculo').textContent = transacao.tipoVeiculo;
    document.getElementById('detailValor').innerHTML = `<strong style="color: #28a745;">R$ ${transacao.valorOriginal.toFixed(2)}</strong>`;
    document.getElementById('detailHash').textContent = transacao.hashIntegridade;
    document.getElementById('detailCriadoEm').textContent = formatDateTime(transacao.criadoEm);
    
    // Renderizar ocorrências
    const ocorrenciasList = document.getElementById('ocorrenciasList');
    if (transacao.ocorrencias && transacao.ocorrencias.length > 0) {
        ocorrenciasList.innerHTML = `
            <h3>⚠️ Ocorrências (${transacao.ocorrencias.length})</h3>
            ${transacao.ocorrencias.map(o => `
                <div class="ocorrencia-card">
                    <div><strong>Tipo:</strong> ${o.tipoOcorrencia}</div>
                    <div><strong>Observação:</strong> ${o.observacao || 'Sem observação'}</div>
                    <div><strong>Detectada Automaticamente:</strong> ${o.detectadaAutomaticamente ? 'Sim' : 'Não'}</div>
                    <div><strong>Data:</strong> ${formatDateTime(o.criadoEm)}</div>
                </div>
            `).join('')}
        `;
    } else {
        ocorrenciasList.innerHTML = '<p>Nenhuma ocorrência registrada</p>';
    }
    
    document.getElementById('detalhesModal').style.display = 'block';
}

function fecharModal() {
    document.getElementById('detalhesModal').style.display = 'none';
}

function limparFiltros() {
    document.getElementById('limiteTransacoes').value = 500;
    document.getElementById('statusFiltro').value = '';
    document.getElementById('buscaId').value = '';
    carregarTransacoes();
}

function atualizarEstatisticas() {
    document.getElementById('totalTransacoes').textContent = transacoes.length;
    
    const comOcorrencias = transacoes.filter(t => t.quantidadeOcorrencias > 0).length;
    document.getElementById('transacoesComOcorrencias').textContent = comOcorrencias;
    
    const ok = transacoes.filter(t => t.statusTransacao === 'OK').length;
    document.getElementById('transacoesOK').textContent = ok;
    
    const corrigidas = transacoes.filter(t => t.statusTransacao === 'CORRIGIDA').length;
    document.getElementById('transacoesCorrigidas').textContent = corrigidas;
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('detalhesModal');
    if (event.target == modal) {
        fecharModal();
    }
}
