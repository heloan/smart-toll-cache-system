let rodovias = [];
let concessionarias = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarConcessionarias();
    carregarRodovias();
    
    document.getElementById('rodoviaForm').addEventListener('submit', salvarRodovia);
});

async function carregarConcessionarias() {
    try {
        concessionarias = await fetchAPI('/concessionarias');
        const select = document.getElementById('concessionariaId');
        select.innerHTML = '<option value="">Selecione...</option>' +
            concessionarias.map(c => `<option value="${c.id}">${c.nomeFantasia}</option>`).join('');
    } catch (error) {
        showAlert('Erro ao carregar concessionárias: ' + error.message, 'danger');
    }
}

async function carregarRodovias() {
    toggleLoading(true);
    try {
        rodovias = await fetchAPI('/rodovias');
        renderizarTabela();
    } catch (error) {
        showAlert('Erro ao carregar rodovias: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabela() {
    const tbody = document.getElementById('rodoviaTableBody');
    
    if (rodovias.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center">Nenhuma rodovia cadastrada</td></tr>';
        return;
    }

    tbody.innerHTML = rodovias.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.codigo}</td>
            <td>${r.nome || '-'}</td>
            <td>${r.concessionariaNome}</td>
            <td>${r.uf}</td>
            <td>${r.extensaoKm || '-'}</td>
            <td><span class="badge ${r.ativa ? 'badge-success' : 'badge-danger'}">${r.ativa ? 'Ativa' : 'Inativa'}</span></td>
            <td>
                <button class="btn btn-small btn-secondary" onclick="editarRodovia(${r.id})">Editar</button>
                <button class="btn btn-small btn-danger" onclick="excluirRodovia(${r.id})">Excluir</button>
            </td>
        </tr>
    `).join('');
}

async function salvarRodovia(e) {
    e.preventDefault();
    
    const id = document.getElementById('rodoviaId').value;
    const dados = {
        concessionariaId: parseInt(document.getElementById('concessionariaId').value),
        codigo: document.getElementById('codigo').value.toUpperCase(),
        nome: document.getElementById('nome').value || null,
        uf: document.getElementById('uf').value.toUpperCase(),
        extensaoKm: document.getElementById('extensaoKm').value ? parseFloat(document.getElementById('extensaoKm').value) : null,
        ativa: document.getElementById('ativa').checked
    };

    toggleLoading(true);
    try {
        if (id) {
            showAlert('Função de atualização não implementada ainda', 'info');
        } else {
            await fetchAPI('/rodovias', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Rodovia cadastrada com sucesso!', 'success');
        }
        
        clearForm('rodoviaForm');
        await carregarRodovias();
    } catch (error) {
        showAlert('Erro ao salvar rodovia: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function editarRodovia(id) {
    const rod = rodovias.find(r => r.id === id);
    if (!rod) return;

    document.getElementById('formTitle').textContent = 'Editar Rodovia';
    document.getElementById('rodoviaId').value = rod.id;
    document.getElementById('concessionariaId').value = rod.concessionariaId;
    document.getElementById('codigo').value = rod.codigo;
    document.getElementById('nome').value = rod.nome || '';
    document.getElementById('uf').value = rod.uf;
    document.getElementById('extensaoKm').value = rod.extensaoKm || '';
    document.getElementById('ativa').checked = rod.ativa;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Nova Rodovia';
    clearForm('rodoviaForm');
    document.getElementById('rodoviaId').value = '';
}

async function excluirRodovia(id) {
    if (!confirmDelete('Tem certeza que deseja excluir esta rodovia?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/rodovias/${id}`, {
            method: 'DELETE'
        });
        showAlert('Rodovia excluída com sucesso!', 'success');
        await carregarRodovias();
    } catch (error) {
        showAlert('Erro ao excluir rodovia: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
