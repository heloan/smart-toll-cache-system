let correcoes = [];
let operadores = [];
let correcoesFiltradas = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarOperadores();
    carregarCorrecoes();
});

async function carregarOperadores() {
    try {
        operadores = await fetchAPI('/operadores');
        const select = document.getElementById('operadorFiltro');
        
        operadores.forEach(op => {
            const option = document.createElement('option');
            option.value = op.id;
            option.textContent = op.nomeCompleto;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar operadores:', error);
    }
}

async function carregarCorrecoes() {
    toggleLoading(true);
    try {
        correcoes = await fetchAPI('/correcoes');
        correcoesFiltradas = [...correcoes];
        renderizarTabelaCorrecoes();
        atualizarEstatisticas();
        showAlert(`${correcoes.length} correções carregadas com sucesso!`, 'success');
    } catch (error) {
        showAlert('Erro ao carregar correções: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabelaCorrecoes() {
    const tbody = document.getElementById('correcoesTableBody');
    
    if (correcoesFiltradas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center">Nenhuma correção encontrada</td></tr>';
        return;
    }

    tbody.innerHTML = correcoesFiltradas.map(c => {
        const diferenca = c.valorCorrigido - c.valorAnterior;
        const diferencaBadge = diferenca > 0 
            ? `<span class="valor-badge valor-aumentou">+R$ ${diferenca.toFixed(2)}</span>`
            : diferenca < 0
            ? `<span class="valor-badge valor-diminuiu">R$ ${diferenca.toFixed(2)}</span>`
            : '<span>R$ 0,00</span>';
        
        return `
            <tr>
                <td>${c.id}</td>
                <td><a href="#" onclick="verTransacao(${c.transacaoId}); return false;">#${c.transacaoId}</a></td>
                <td>${formatDateTime(c.criadoEm)}</td>
                <td>${c.operadorNome}</td>
                <td>${formatTipoCorrecao(c.tipoCorrecao)}</td>
                <td>R$ ${c.valorAnterior.toFixed(2)}</td>
                <td style="font-weight: bold; color: #28a745;">R$ ${c.valorCorrigido.toFixed(2)}</td>
                <td>${diferencaBadge}</td>
                <td style="max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" 
                    title="${c.motivo}">${c.motivo}</td>
            </tr>
        `;
    }).join('');
}

function formatTipoCorrecao(tipo) {
    const tipos = {
        'TARIFA_ERRADA': '<span class="badge" style="background: #ffc107; color: #000;">Tarifa Errada</span>',
        'STATUS_ERRADO': '<span class="badge" style="background: #17a2b8; color: #fff;">Status Errado</span>',
        'FRAUDE_DETECTADA': '<span class="badge badge-danger">Fraude Detectada</span>',
        'AJUSTE_MANUAL': '<span class="badge" style="background: #6c757d; color: #fff;">Ajuste Manual</span>'
    };
    return tipos[tipo] || tipo;
}

async function aplicarFiltros() {
    const operadorId = document.getElementById('operadorFiltro').value;
    const tipoCorrecao = document.getElementById('tipoCorrecaoFiltro').value;
    
    if (operadorId) {
        await carregarCorrecoesPorOperador(operadorId);
    } else {
        correcoesFiltradas = [...correcoes];
    }
    
    if (tipoCorrecao) {
        correcoesFiltradas = correcoesFiltradas.filter(c => c.tipoCorrecao === tipoCorrecao);
    }
    
    renderizarTabelaCorrecoes();
    atualizarEstatisticas();
}

async function carregarCorrecoesPorOperador(operadorId) {
    toggleLoading(true);
    try {
        const correcoesOperador = await fetchAPI(`/correcoes/operador/${operadorId}`);
        correcoesFiltradas = correcoesOperador;
        
        const operador = operadores.find(op => op.id == operadorId);
        if (operador) {
            document.getElementById('nomeOperadorSelecionado').textContent = operador.nomeCompleto;
            document.getElementById('correcoesPorOperadorSection').style.display = 'block';
            
            const tbody = document.getElementById('correcoesPorOperadorTableBody');
            tbody.innerHTML = correcoesOperador.map(c => {
                const diferenca = c.valorCorrigido - c.valorAnterior;
                const diferencaBadge = diferenca > 0 
                    ? `<span class="valor-badge valor-aumentou">+R$ ${diferenca.toFixed(2)}</span>`
                    : diferenca < 0
                    ? `<span class="valor-badge valor-diminuiu">R$ ${diferenca.toFixed(2)}</span>`
                    : '<span>R$ 0,00</span>';
                
                return `
                    <tr>
                        <td>${c.id}</td>
                        <td><a href="#" onclick="verTransacao(${c.transacaoId}); return false;">#${c.transacaoId}</a></td>
                        <td>${formatDateTime(c.criadoEm)}</td>
                        <td>${formatTipoCorrecao(c.tipoCorrecao)}</td>
                        <td>R$ ${c.valorAnterior.toFixed(2)}</td>
                        <td style="font-weight: bold; color: #28a745;">R$ ${c.valorCorrigido.toFixed(2)}</td>
                        <td>${diferencaBadge}</td>
                        <td>${c.motivo}</td>
                    </tr>
                `;
            }).join('');
        }
    } catch (error) {
        showAlert('Erro ao carregar correções do operador: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function limparFiltros() {
    document.getElementById('operadorFiltro').value = '';
    document.getElementById('tipoCorrecaoFiltro').value = '';
    document.getElementById('correcoesPorOperadorSection').style.display = 'none';
    correcoesFiltradas = [...correcoes];
    renderizarTabelaCorrecoes();
    atualizarEstatisticas();
}

function atualizarEstatisticas() {
    document.getElementById('totalCorrecoes').textContent = correcoesFiltradas.length;
    
    const tarifaErrada = correcoesFiltradas.filter(c => c.tipoCorrecao === 'TARIFA_ERRADA').length;
    document.getElementById('correcoesTarifaErrada').textContent = tarifaErrada;
    
    const statusErrado = correcoesFiltradas.filter(c => c.tipoCorrecao === 'STATUS_ERRADO').length;
    document.getElementById('correcoesStatusErrado').textContent = statusErrado;
    
    const fraude = correcoesFiltradas.filter(c => c.tipoCorrecao === 'FRAUDE_DETECTADA').length;
    document.getElementById('correcoesFraude').textContent = fraude;
}

function verTransacao(transacaoId) {
    // Redirecionar para a página de transações com o ID
    window.location.href = `/pages/transacoes.html?id=${transacaoId}`;
}
