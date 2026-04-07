let registros = [];
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    carregarDados();
    
    // Atualizar automaticamente a cada 30 segundos
    setInterval(carregarDados, 30000);
});

async function carregarDados() {
    const limite = document.getElementById('limiteRegistros').value;
    toggleLoading(true);
    
    try {
        // Endpoint fictício - você precisa criar GET /api/performance no backend
        registros = await fetchAPI(`/performance?limit=${limite}`);
        
        atualizarKPIs();
        renderizarGraficos();
        renderizarTabela();
        renderizarEndpointsLentos();
        
    } catch (error) {
        // Se o endpoint não existir, usar dados de exemplo
        console.error('Erro ao carregar dados:', error);
        gerarDadosExemplo();
        showAlert('Endpoint de performance não disponível. Exibindo dados de exemplo.', 'info');
    } finally {
        toggleLoading(false);
    }
}

function gerarDadosExemplo() {
    // Gerar dados de exemplo para demonstração
    const endpoints = ['/api/concessionarias', '/api/rodovias', '/api/pracas', '/api/pistas', '/api/operadores'];
    const metodos = ['GET', 'POST', 'PUT', 'DELETE'];
    const agora = new Date();
    
    registros = Array.from({ length: 100 }, (_, i) => {
        const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
        const metodo = metodos[Math.floor(Math.random() * metodos.length)];
        const tempo = new Date(agora.getTime() - i * 60000); // 1 minuto de diferença
        
        return {
            id: i + 1,
            endpoint: endpoint,
            metodoHttp: metodo,
            tempoProcessamentoMs: Math.floor(Math.random() * 500) + 10,
            memoriaUsadaMb: Math.random() * 100 + 200,
            memoriaLivreMb: Math.random() * 100 + 100,
            memoriaTotalMb: 512,
            usoCpuProcesso: Math.random() * 50,
            threadsAtivas: Math.floor(Math.random() * 20) + 10,
            statusHttp: [200, 201, 204, 400, 404, 500][Math.floor(Math.random() * 6)],
            ipCliente: `192.168.1.${Math.floor(Math.random() * 255)}`,
            userAgent: 'Mozilla/5.0',
            parametros: null,
            erro: null,
            origemDados: ['BANCO_DADOS', 'CACHE_LOCAL', 'CACHE_REDIS', 'NAO_APLICAVEL'][Math.floor(Math.random() * 4)],
            criadoEm: tempo.toISOString()
        };
    });
    
    atualizarKPIs();
    renderizarGraficos();
    renderizarTabela();
    renderizarEndpointsLentos();
}

function atualizarKPIs() {
    if (registros.length === 0) {
        document.getElementById('kpiTempoMedio').textContent = '0';
        document.getElementById('kpiTotalRequisicoes').textContent = '0';
        document.getElementById('kpiMemoriaMedia').textContent = '0';
        document.getElementById('kpiCpuMedia').textContent = '0';
        return;
    }
    
    const tempoMedio = registros.reduce((sum, r) => sum + r.tempoProcessamentoMs, 0) / registros.length;
    const memoriaMedia = registros.reduce((sum, r) => sum + r.memoriaUsadaMb, 0) / registros.length;
    const cpuMedia = registros.reduce((sum, r) => sum + r.usoCpuProcesso, 0) / registros.length;
    
    document.getElementById('kpiTempoMedio').textContent = Math.round(tempoMedio);
    document.getElementById('kpiTotalRequisicoes').textContent = registros.length;
    document.getElementById('kpiMemoriaMedia').textContent = memoriaMedia.toFixed(1);
    document.getElementById('kpiCpuMedia').textContent = cpuMedia.toFixed(1);
}

function renderizarGraficos() {
    renderChartTempoPorEndpoint();
    renderChartStatusHttp();
    renderChartMemoria();
    renderChartCpu();
    renderChartThreads();
    renderChartRequisicoes();
    renderChartOrigemDados();
}

function renderChartTempoPorEndpoint() {
    const ctx = document.getElementById('chartTempoPorEndpoint');
    
    // Agrupar por endpoint e calcular média
    const groupedData = {};
    registros.forEach(r => {
        if (!groupedData[r.endpoint]) {
            groupedData[r.endpoint] = { total: 0, count: 0 };
        }
        groupedData[r.endpoint].total += r.tempoProcessamentoMs;
        groupedData[r.endpoint].count++;
    });
    
    const endpoints = Object.keys(groupedData);
    const tempos = endpoints.map(e => (groupedData[e].total / groupedData[e].count).toFixed(2));
    
    destroyChart('chartTempoPorEndpoint');
    
    charts.tempoPorEndpoint = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: endpoints.map(e => e.substring(e.lastIndexOf('/') + 1) || e),
            datasets: [{
                label: 'Tempo Médio (ms)',
                data: tempos,
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderChartStatusHttp() {
    const ctx = document.getElementById('chartStatusHttp');
    
    // Contar status
    const statusCount = {};
    registros.forEach(r => {
        statusCount[r.statusHttp] = (statusCount[r.statusHttp] || 0) + 1;
    });
    
    const labels = Object.keys(statusCount).sort();
    const data = labels.map(s => statusCount[s]);
    
    destroyChart('chartStatusHttp');
    
    charts.statusHttp = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(40, 167, 69, 0.7)',    // 2xx - verde
                    'rgba(23, 162, 184, 0.7)',   // 3xx - azul
                    'rgba(255, 193, 7, 0.7)',    // 4xx - amarelo
                    'rgba(220, 53, 69, 0.7)'     // 5xx - vermelho
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function renderChartMemoria() {
    const ctx = document.getElementById('chartMemoria');
    
    const ultimos = registros.slice(0, 50).reverse();
    const labels = ultimos.map((r, i) => i + 1);
    
    destroyChart('chartMemoria');
    
    charts.memoria = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Memória Usada (MB)',
                    data: ultimos.map(r => r.memoriaUsadaMb.toFixed(2)),
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.3
                },
                {
                    label: 'Memória Livre (MB)',
                    data: ultimos.map(r => r.memoriaLivreMb.toFixed(2)),
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderChartCpu() {
    const ctx = document.getElementById('chartCpu');
    
    const ultimos = registros.slice(0, 50).reverse();
    const labels = ultimos.map((r, i) => i + 1);
    
    destroyChart('chartCpu');
    
    charts.cpu = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Uso CPU (%)',
                data: ultimos.map(r => r.usoCpuProcesso.toFixed(2)),
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function renderChartThreads() {
    const ctx = document.getElementById('chartThreads');
    
    const ultimos = registros.slice(0, 50).reverse();
    const labels = ultimos.map((r, i) => i + 1);
    
    destroyChart('chartThreads');
    
    charts.threads = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Threads Ativas',
                data: ultimos.map(r => r.threadsAtivas),
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderChartRequisicoes() {
    const ctx = document.getElementById('chartRequisicoes');
    
    // Agrupar por minuto
    const porMinuto = {};
    registros.forEach(r => {
        const data = new Date(r.criadoEm);
        const minuto = `${data.getHours()}:${String(data.getMinutes()).padStart(2, '0')}`;
        porMinuto[minuto] = (porMinuto[minuto] || 0) + 1;
    });
    
    const labels = Object.keys(porMinuto).slice(0, 30).reverse();
    const data = labels.map(l => porMinuto[l]);
    
    destroyChart('chartRequisicoes');
    
    charts.requisicoes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Requisições',
                data: data,
                backgroundColor: 'rgba(118, 75, 162, 0.7)',
                borderColor: 'rgba(118, 75, 162, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderChartOrigemDados() {
    const ctx = document.getElementById('chartOrigemDados');
    
    // Contar origens
    const origemCount = {
        'BANCO_DADOS': 0,
        'CACHE_LOCAL': 0,
        'CACHE_REDIS': 0,
        'NAO_APLICAVEL': 0
    };
    
    registros.forEach(r => {
        if (r.origemDados && origemCount.hasOwnProperty(r.origemDados)) {
            origemCount[r.origemDados]++;
        }
    });
    
    const labels = ['🗄️ Banco de Dados', '💾 Cache Local', '🔴 Redis', 'N/A'];
    const data = [
        origemCount.BANCO_DADOS,
        origemCount.CACHE_LOCAL,
        origemCount.CACHE_REDIS,
        origemCount.NAO_APLICAVEL
    ];
    
    destroyChart('chartOrigemDados');
    
    charts.origemDados = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 193, 7, 0.7)',    // Banco - amarelo
                    'rgba(40, 167, 69, 0.7)',    // Cache Local - verde
                    'rgba(220, 53, 69, 0.7)',    // Redis - vermelho
                    'rgba(108, 117, 125, 0.7)'   // N/A - cinza
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function destroyChart(chartId) {
    const chartName = chartId.replace('chart', '').charAt(0).toLowerCase() + chartId.replace('chart', '').slice(1);
    if (charts[chartName]) {
        charts[chartName].destroy();
    }
}

function renderizarTabela() {
    const tbody = document.getElementById('performanceTableBody');
    
    if (registros.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center">Nenhum registro encontrado</td></tr>';
        return;
    }
    
    const ultimos20 = registros.slice(0, 20);
    
    tbody.innerHTML = ultimos20.map(r => {
        const tempoClass = r.tempoProcessamentoMs < 100 ? 'tempo-rapido' : 
                          r.tempoProcessamentoMs < 300 ? 'tempo-medio' : 'tempo-lento';
        const statusClass = r.statusHttp >= 200 && r.statusHttp < 300 ? 'status-success' :
                           r.statusHttp >= 300 && r.statusHttp < 400 ? 'status-info' :
                           r.statusHttp >= 400 && r.statusHttp < 500 ? 'status-warning' : 'status-error';
        
        // Formatação da origem dos dados
        const origemTexto = {
            'BANCO_DADOS': '🗄️ Banco',
            'CACHE_LOCAL': '💾 Cache Local',
            'CACHE_REDIS': '🔴 Redis',
            'NAO_APLICAVEL': '-'
        };
        const origemClass = {
            'BANCO_DADOS': 'origem-banco',
            'CACHE_LOCAL': 'origem-cache-local',
            'CACHE_REDIS': 'origem-cache-redis',
            'NAO_APLICAVEL': ''
        };
        
        return `
            <tr>
                <td>${formatDateTime(r.criadoEm)}</td>
                <td>${r.endpoint}</td>
                <td>${r.metodoHttp}</td>
                <td class="${tempoClass}">${r.tempoProcessamentoMs}</td>
                <td>${r.memoriaUsadaMb.toFixed(1)}</td>
                <td>${r.usoCpuProcesso.toFixed(1)}</td>
                <td>${r.threadsAtivas}</td>
                <td><span class="badge ${origemClass[r.origemDados] || ''}">${origemTexto[r.origemDados] || r.origemDados || '-'}</span></td>
                <td><span class="${statusClass}">${r.statusHttp}</span></td>
                <td>${r.ipCliente || '-'}</td>
            </tr>
        `;
    }).join('');
}

function renderizarEndpointsLentos() {
    const tbody = document.getElementById('endpointsLentosTableBody');
    
    // Agrupar por endpoint + método
    const grouped = {};
    registros.forEach(r => {
        const key = `${r.endpoint}|${r.metodoHttp}`;
        if (!grouped[key]) {
            grouped[key] = {
                endpoint: r.endpoint,
                metodo: r.metodoHttp,
                tempos: [],
                count: 0
            };
        }
        grouped[key].tempos.push(r.tempoProcessamentoMs);
        grouped[key].count++;
    });
    
    // Calcular médias e máximos
    const endpointsData = Object.values(grouped).map(g => {
        const tempoMedio = g.tempos.reduce((a, b) => a + b, 0) / g.tempos.length;
        const tempoMax = Math.max(...g.tempos);
        return {
            endpoint: g.endpoint,
            metodo: g.metodo,
            tempoMedio: tempoMedio,
            tempoMax: tempoMax,
            count: g.count
        };
    });
    
    // Ordenar por tempo médio (decrescente)
    endpointsData.sort((a, b) => b.tempoMedio - a.tempoMedio);
    
    const top10 = endpointsData.slice(0, 10);
    
    if (top10.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Nenhum dado disponível</td></tr>';
        return;
    }
    
    tbody.innerHTML = top10.map(e => `
        <tr>
            <td>${e.endpoint}</td>
            <td>${e.metodo}</td>
            <td>${e.tempoMedio.toFixed(2)}</td>
            <td>${e.tempoMax}</td>
            <td>${e.count}</td>
        </tr>
    `).join('');
}
