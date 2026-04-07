let pracas = [];
let rodovias = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarRodovias();
    carregarPracas();
    
    document.getElementById('pracaForm').addEventListener('submit', salvarPraca);
});

async function carregarRodovias() {
    try {
        rodovias = await fetchAPI('/rodovias');
        const select = document.getElementById('rodoviaId');
        select.innerHTML = '<option value="">Selecione...</option>' +
            rodovias.map(r => `<option value="${r.id}">${r.codigo} - ${r.nome || r.codigo}</option>`).join('');
    } catch (error) {
        showAlert('Erro ao carregar rodovias: ' + error.message, 'danger');
    }
}

async function carregarPracas() {
    toggleLoading(true);
    try {
        pracas = await fetchAPI('/pracas');
        renderizarTabela();
    } catch (error) {
        showAlert('Erro ao carregar praças: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabela() {
    const tbody = document.getElementById('pracaTableBody');
    
    if (pracas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">Nenhuma praça cadastrada</td></tr>';
        return;
    }

    tbody.innerHTML = pracas.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.nome}</td>
            <td>${p.rodoviaNome}</td>
            <td>${p.km}</td>
            <td>${p.sentido || '-'}</td>
            <td><span class="badge ${p.ativa ? 'badge-success' : 'badge-danger'}">${p.ativa ? 'Ativa' : 'Inativa'}</span></td>
            <td>
                <button class="btn btn-small btn-secondary" onclick="editarPraca(${p.id})">Editar</button>
                <button class="btn btn-small btn-danger" onclick="excluirPraca(${p.id})">Excluir</button>
            </td>
        </tr>
    `).join('');
}

async function salvarPraca(e) {
    e.preventDefault();
    
    const id = document.getElementById('pracaId').value;
    const dados = {
        rodoviaId: parseInt(document.getElementById('rodoviaId').value),
        nome: document.getElementById('nome').value,
        km: parseFloat(document.getElementById('km').value),
        sentido: document.getElementById('sentido').value || null,
        ativa: document.getElementById('ativa').checked
    };

    toggleLoading(true);
    try {
        if (id) {
            showAlert('Função de atualização não implementada ainda', 'info');
        } else {
            await fetchAPI('/pracas', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Praça cadastrada com sucesso!', 'success');
        }
        
        clearForm('pracaForm');
        await carregarPracas();
    } catch (error) {
        showAlert('Erro ao salvar praça: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function editarPraca(id) {
    const praca = pracas.find(p => p.id === id);
    if (!praca) return;

    document.getElementById('formTitle').textContent = 'Editar Praça de Pedágio';
    document.getElementById('pracaId').value = praca.id;
    document.getElementById('rodoviaId').value = praca.rodoviaId;
    document.getElementById('nome').value = praca.nome;
    document.getElementById('km').value = praca.km;
    document.getElementById('sentido').value = praca.sentido || '';
    document.getElementById('ativa').checked = praca.ativa;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Nova Praça de Pedágio';
    clearForm('pracaForm');
    document.getElementById('pracaId').value = '';
}

async function excluirPraca(id) {
    if (!confirmDelete('Tem certeza que deseja excluir esta praça?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/pracas/${id}`, {
            method: 'DELETE'
        });
        showAlert('Praça excluída com sucesso!', 'success');
        await carregarPracas();
    } catch (error) {
        showAlert('Erro ao excluir praça: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
