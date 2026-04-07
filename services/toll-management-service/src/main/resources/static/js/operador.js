let operadores = [];

document.addEventListener('DOMContentLoaded', () => {
    carregarOperadores();
    
    document.getElementById('operadorForm').addEventListener('submit', salvarOperador);
});

async function carregarOperadores() {
    toggleLoading(true);
    try {
        // Como não há endpoint para listar todos, vamos usar um array vazio por enquanto
        // Você pode implementar GET /api/operadores no backend
        operadores = [];
        renderizarTabela();
        showAlert('Endpoint de listagem de operadores não implementado ainda. Apenas cadastro disponível.', 'info');
    } catch (error) {
        showAlert('Erro ao carregar operadores: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function renderizarTabela() {
    const tbody = document.getElementById('operadorTableBody');
    
    if (operadores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center">Nenhum operador cadastrado ou listagem não disponível</td></tr>';
        return;
    }

    tbody.innerHTML = operadores.map(o => `
        <tr>
            <td>${o.id}</td>
            <td>${o.username}</td>
            <td>${o.nomeCompleto}</td>
            <td>${o.email}</td>
            <td>${o.telefone || '-'}</td>
            <td><span class="badge ${o.ativo ? 'badge-success' : 'badge-danger'}">${o.ativo ? 'Ativo' : 'Inativo'}</span></td>
            <td>${formatDateTime(o.criadoEm)}</td>
            <td>
                <button class="btn btn-small btn-secondary" onclick="editarOperador(${o.id})">Editar</button>
                <button class="btn btn-small btn-danger" onclick="excluirOperador(${o.id})">Excluir</button>
            </td>
        </tr>
    `).join('');
}

async function salvarOperador(e) {
    e.preventDefault();
    
    const id = document.getElementById('operadorId').value;
    const dados = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        nomeCompleto: document.getElementById('nomeCompleto').value,
        email: document.getElementById('email').value,
        telefone: document.getElementById('telefone').value || null,
        ativo: document.getElementById('ativo').checked
    };

    // Validação de email
    if (!validarEmail(dados.email)) {
        showAlert('Email inválido', 'danger');
        return;
    }

    toggleLoading(true);
    try {
        if (id) {
            showAlert('Função de atualização não implementada ainda', 'info');
        } else {
            await fetchAPI('/operadores', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            showAlert('Operador cadastrado com sucesso!', 'success');
        }
        
        clearForm('operadorForm');
        // Limpar senha por segurança
        document.getElementById('password').value = '';
        await carregarOperadores();
    } catch (error) {
        showAlert('Erro ao salvar operador: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

function editarOperador(id) {
    const op = operadores.find(o => o.id === id);
    if (!op) return;

    document.getElementById('formTitle').textContent = 'Editar Operador';
    document.getElementById('operadorId').value = op.id;
    document.getElementById('username').value = op.username;
    document.getElementById('nomeCompleto').value = op.nomeCompleto;
    document.getElementById('email').value = op.email;
    document.getElementById('telefone').value = op.telefone || '';
    document.getElementById('ativo').checked = op.ativo;
    
    // Senha não é preenchida por segurança
    document.getElementById('password').value = '';
    document.getElementById('password').placeholder = 'Deixe em branco para manter a atual';

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelarEdicao() {
    document.getElementById('formTitle').textContent = 'Novo Operador';
    clearForm('operadorForm');
    document.getElementById('operadorId').value = '';
    document.getElementById('password').placeholder = '';
}

async function excluirOperador(id) {
    if (!confirmDelete('Tem certeza que deseja excluir este operador?')) {
        return;
    }

    toggleLoading(true);
    try {
        await fetchAPI(`/operadores/${id}`, {
            method: 'DELETE'
        });
        showAlert('Operador excluído com sucesso!', 'success');
        await carregarOperadores();
    } catch (error) {
        showAlert('Erro ao excluir operador: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}
