let pistas = [];
let pracas = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarPracas();
    carregarPistas();
    
    document.getElementById('pistaForm').addEventListener('submit', salvarPista);
});

async function carregarPracas() {
    try {
        pracas = await fetchAPI('/pracas');
        const select = document.getElementById('pracaId');
        select.innerHTML = '<option value="">Selecione...</option>' +
            pracas.map(p => `<option value="${p.id}">${p.nome} (${p.rodoviaNome})</option>`).join('');
    } catch (error) {
        showAlert('Erro ao carregar praças: ' + error.message, 'danger');
    }
}

async function carregarPistas() {
    toggleLoading(true);
    try {
        pistas = await fetchAPI('/pistas');
        renderizarTabela();
    } catch (error) {
        showAlert('Erro ao carregar pistas: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabela() {
    const tbody = document.getElementById('pistaTableBody');
    
    if (pistas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">Nenhuma pista cadastrada</td></tr>';
        return;
    }

    tbody.innerHTML = pistas.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.pracaNome}</td>
            <td>${p.numeroPista}</td>
            <td>${p.tipoPista}</td>
            <td>${p.sentido || '-'}</td>
            <td><span class="badge ${p.ativa ? 'badge-success' : 'badge-danger'}">${p.ativa ? 'Ativa' : 'Inativa'}</span></td>
            <td>
                <button class="btn btn-small btn-secondary" onclick="editarPista(${p.id})">Editar</button>
                <button class="btn btn-small btn-danger" onclick="excluirPista(${p.id})">Excluir</button>
            </td>
        </tr>
    `).join('');
}

async function salvarPista(e) {
    e.preventDefault();
    
    const id = document.getElementById('pistaId').value;
    const dados = {
        pracaId: parseInt(document.getElementById('pracaId').value),
        numeroPista: parseInt(document.getElementById('numeroPista').value),
        tipoPista: document.getElementById('tipoPista').value,
        sentido: document.getElementById('sentido').value || null,
        ativa: document.getElementById('ativa').checked
    };

    toggleLoading(true);
    try {
        if (id) {
            showAlert('Função de atualização não implementada ainda', 'info');
        } else {
            await fetchAPI('/pistas', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Pista cadastrada com sucesso!', 'success');
        }
        
        clearForm('pistaForm');
        await carregarPistas();
    } catch (error) {
        showAlert('Erro ao salvar pista: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function editarPista(id) {
    const pista = pistas.find(p => p.id === id);
    if (!pista) return;

    document.getElementById('formTitle').textContent = 'Editar Pista de Pedágio';
    document.getElementById('pistaId').value = pista.id;
    document.getElementById('pracaId').value = pista.pracaId;
    document.getElementById('numeroPista').value = pista.numeroPista;
    document.getElementById('tipoPista').value = pista.tipoPista;
    document.getElementById('sentido').value = pista.sentido || '';
    document.getElementById('ativa').checked = pista.ativa;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Nova Pista de Pedágio';
    clearForm('pistaForm');
    document.getElementById('pistaId').value = '';
}

async function excluirPista(id) {
    if (!confirmDelete('Tem certeza que deseja excluir esta pista?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/pistas/${id}`, {
            method: 'DELETE'
        });
        showAlert('Pista excluída com sucesso!', 'success');
        await carregarPistas();
    } catch (error) {
        showAlert('Erro ao excluir pista: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
