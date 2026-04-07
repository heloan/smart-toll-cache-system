let concessionarias = [];

// Carregar concessionárias ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    carregarConcessionarias();
    
    document.getElementById('concessionariaForm').addEventListener('submit', salvarConcessionaria);
});

// Carregar lista de concessionárias
async function carregarConcessionarias() {
    toggleLoading(true);
    try {
        concessionarias = await fetchAPI('/concessionarias');
        renderizarTabela();
    } catch (error) {
        showAlert('Erro ao carregar concessionárias: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

// Renderizar tabela
function renderizarTabela() {
    const tbody = document.getElementById('concessionariaTableBody');
    
    if (concessionarias.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center">Nenhuma concessionária cadastrada</td></tr>';
        return;
    }

    tbody.innerHTML = concessionarias.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.nomeFantasia}</td>
            <td>${formatCNPJ(c.cnpj)}</td>
            <td>${c.razaoSocial}</td>
            <td>${c.contratoConcessao || '-'}</td>
            <td>${formatDate(c.dataInicioContrato)}</td>
            <td>${formatDate(c.dataFimContrato)}</td>
            <td><span class="badge ${c.ativo ? 'badge-success' : 'badge-danger'}">${c.ativo ? 'Ativo' : 'Inativo'}</span></td>
            <td>
                <button class="btn btn-small btn-secondary" onclick="editarConcessionaria(${c.id})">Editar</button>
                <button class="btn btn-small btn-danger" onclick="excluirConcessionaria(${c.id})">Excluir</button>
            </td>
        </tr>
    `).join('');
}

// Salvar concessionária
async function salvarConcessionaria(e) {
    e.preventDefault();
    
    const id = document.getElementById('concessionariaId').value;
    const dados = {
        nomeFantasia: document.getElementById('nomeFantasia').value,
        razaoSocial: document.getElementById('razaoSocial').value,
        cnpj: document.getElementById('cnpj').value.replace(/\D/g, ''),
        contratoConcessao: document.getElementById('contratoConcessao').value || null,
        dataInicioContrato: document.getElementById('dataInicioContrato').value,
        dataFimContrato: document.getElementById('dataFimContrato').value || null,
        ativo: document.getElementById('ativo').checked
    };

    // Validação CNPJ
    if (!validarCNPJ(dados.cnpj)) {
        showAlert('CNPJ inválido', 'danger');
        return;
    }

    toggleLoading(true);
    try {
        if (id) {
            // Atualizar (implementar endpoint PUT se necessário)
            showAlert('Função de atualização não implementada ainda', 'info');
        } else {
            // Criar
            await fetchAPI('/concessionarias', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Concessionária cadastrada com sucesso!', 'success');
        }
        
        clearForm('concessionariaForm');
        await carregarConcessionarias();
    } catch (error) {
        showAlert('Erro ao salvar concessionária: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

// Editar concessionária
function editarConcessionaria(id) {
    const conc = concessionarias.find(c => c.id === id);
    if (!conc) return;

    document.getElementById('formTitle').textContent = 'Editar Concessionária';
    document.getElementById('concessionariaId').value = conc.id;
    document.getElementById('nomeFantasia').value = conc.nomeFantasia;
    document.getElementById('razaoSocial').value = conc.razaoSocial;
    document.getElementById('cnpj').value = conc.cnpj;
    document.getElementById('contratoConcessao').value = conc.contratoConcessao || '';
    document.getElementById('dataInicioContrato').value = conc.dataInicioContrato;
    document.getElementById('dataFimContrato').value = conc.dataFimContrato || '';
    document.getElementById('ativo').checked = conc.ativo;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Cancelar edição
function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Nova Concessionária';
    clearForm('concessionariaForm');
    document.getElementById('concessionariaId').value = '';
}

// Excluir concessionária
async function excluirConcessionaria(id) {
    if (!confirmDelete('Tem certeza que deseja excluir esta concessionária?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/concessionarias/${id}`, {
            method: 'DELETE'
        });
        showAlert('Concessionária excluída com sucesso!', 'success');
        await carregarConcessionarias();
    } catch (error) {
        showAlert('Erro ao excluir concessionária: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
