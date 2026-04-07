let tarifas = [];
let tarifasVigentes = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarTarifas();
    carregarTarifasVigentes();
    
    document.getElementById('tarifaForm').addEventListener('submit', salvarTarifa);
});

async function carregarTarifas() {
    toggleLoading(true);
    try {
        tarifas = await fetchAPI('/tarifas');
        renderizarTabela();
    } catch (error) {
        showAlert('Erro ao carregar tarifas: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

async function carregarTarifasVigentes() {
    try {
        tarifasVigentes = await fetchAPI('/tarifas/vigentes');
        renderizarTabelaVigentes();
    } catch (error) {
        console.error('Erro ao carregar tarifas vigentes:', error);
    }
}

function renderizarTabelaVigentes() {
    const tbody = document.getElementById('tarifasVigentesTableBody');
    
    if (tarifasVigentes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">Nenhuma tarifa vigente</td></tr>';
        return;
    }

    tbody.innerHTML = tarifasVigentes.map(t => {
        const tipoVeiculoTexto = {
            'MOTO': '🏍️ Moto',
            'CARRO': '🚗 Carro',
            'CAMINHAO': '🚚 Caminhão'
        };
        
        return `
            <tr>
                <td>${t.id}</td>
                <td>${tipoVeiculoTexto[t.tipoVeiculo] || t.tipoVeiculo}</td>
                <td style="font-weight: bold; color: #28a745;">R$ ${t.valor.toFixed(2)}</td>
                <td>${formatDate(t.vigenciaInicio)}</td>
                <td>${formatDate(t.vigenciaFim)}</td>
                <td><span class="badge badge-success">Vigente</span></td>
                <td>
                    <button class="btn btn-small btn-secondary" onclick="editarTarifa(${t.id})">Editar</button>
                    <button class="btn btn-small btn-danger" onclick="excluirTarifa(${t.id})">Excluir</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarTabela() {
    const tbody = document.getElementById('tarifaTableBody');
    
    if (tarifas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center">Nenhuma tarifa cadastrada</td></tr>';
        return;
    }

    tbody.innerHTML = tarifas.map(t => {
        const tipoVeiculoTexto = {
            'MOTO': '🏍️ Moto',
            'CARRO': '🚗 Carro',
            'CAMINHAO': '🚚 Caminhão'
        };
        
        const statusBadge = t.vigente 
            ? '<span class="badge badge-success">Vigente</span>' 
            : '<span class="badge badge-danger">Expirada</span>';
        
        return `
            <tr>
                <td>${t.id}</td>
                <td>${tipoVeiculoTexto[t.tipoVeiculo] || t.tipoVeiculo}</td>
                <td>R$ ${t.valor.toFixed(2)}</td>
                <td>${formatDate(t.vigenciaInicio)}</td>
                <td>${formatDate(t.vigenciaFim)}</td>
                <td>${statusBadge}</td>
                <td>${formatDateTime(t.criadoEm)}</td>
                <td>
                    <button class="btn btn-small btn-secondary" onclick="editarTarifa(${t.id})">Editar</button>
                    <button class="btn btn-small btn-danger" onclick="excluirTarifa(${t.id})">Excluir</button>
                </td>
            </tr>
        `;
    }).join('');
}

async function salvarTarifa(e) {
    e.preventDefault();
    
    const id = document.getElementById('tarifaId').value;
    const dados = {
        tipoVeiculo: document.getElementById('tipoVeiculo').value,
        valor: parseFloat(document.getElementById('valor').value),
        vigenciaInicio: document.getElementById('vigenciaInicio').value,
        vigenciaFim: document.getElementById('vigenciaFim').value || null
    };

    // Validação de datas
    if (dados.vigenciaFim && dados.vigenciaFim < dados.vigenciaInicio) {
        showAlert('Data de fim da vigência deve ser posterior à data de início', 'danger');
        return;
    }

    toggleLoading(true);
    try {
        if (id) {
            // Atualizar
            await fetchAPI(`/tarifas/${id}`, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
            showAlert('Tarifa atualizada com sucesso!', 'success');
        } else {
            // Criar
            await fetchAPI('/tarifas', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Tarifa cadastrada com sucesso!', 'success');
        }
        
        clearForm('tarifaForm');
        await carregarTarifas();
        await carregarTarifasVigentes();
        cancelarEdicao();
    } catch (error) {
        showAlert('Erro ao salvar tarifa: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function editarTarifa(id) {
    const tarifa = tarifas.find(t => t.id === id);
    if (!tarifa) return;

    document.getElementById('formTitle').textContent = 'Editar Tarifa de Pedágio';
    document.getElementById('tarifaId').value = tarifa.id;
    document.getElementById('tipoVeiculo').value = tarifa.tipoVeiculo;
    document.getElementById('valor').value = tarifa.valor;
    document.getElementById('vigenciaInicio').value = tarifa.vigenciaInicio;
    document.getElementById('vigenciaFim').value = tarifa.vigenciaFim || '';

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Nova Tarifa de Pedágio';
    clearForm('tarifaForm');
    document.getElementById('tarifaId').value = '';
}

async function excluirTarifa(id) {
    if (!confirmDelete('Tem certeza que deseja excluir esta tarifa?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/tarifas/${id}`, {
            method: 'DELETE'
        });
        showAlert('Tarifa excluída com sucesso!', 'success');
        await carregarTarifas();
        await carregarTarifasVigentes();
    } catch (error) {
        showAlert('Erro ao excluir tarifa: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
