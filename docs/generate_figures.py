#!/usr/bin/env python3
"""Generate all academic paper figures for the Smart Toll Cache System."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color palette
COLORS = {
    'primary': '#2563EB',
    'secondary': '#7C3AED',
    'success': '#059669',
    'warning': '#D97706',
    'danger': '#DC2626',
    'info': '#0891B2',
    'light_bg': '#F8FAFC',
    'dark': '#1E293B',
    'gray': '#64748B',
    'light_gray': '#E2E8F0',
    'scenario_a': '#DC2626',
    'scenario_b': '#D97706',
    'scenario_c': '#059669',
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'figure.facecolor': 'white',
    'axes.facecolor': '#FAFBFC',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})


def add_box(ax, x, y, w, h, text, color, fontsize=8, textcolor='white', alpha=1.0):
    """Add a rounded rectangle with centered text."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor=color, edgecolor='#334155', linewidth=1.2, alpha=alpha)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, color=textcolor, fontweight='bold',
            path_effects=[pe.withStroke(linewidth=0.5, foreground='black')] if textcolor == 'white' else [])


def add_arrow(ax, x1, y1, x2, y2, color='#475569', style='->', lw=1.5):
    """Add arrow between points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))


# ============================================================
# FIGURE 1 — System Architecture Diagram
# ============================================================
def fig1_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title('Figura 1 — Diagrama de Arquitetura Geral do Sistema', pad=15, fontsize=14)

    # Layer labels
    ax.text(0.3, 8.5, 'CAMADA DE CLIENTES', fontsize=9, color=COLORS['gray'], fontstyle='italic')
    ax.text(0.3, 6.7, 'CAMADA DE GATEWAY', fontsize=9, color=COLORS['gray'], fontstyle='italic')
    ax.text(0.3, 4.9, 'CAMADA DE APLICAÇÃO', fontsize=9, color=COLORS['gray'], fontstyle='italic')
    ax.text(0.3, 2.2, 'CAMADA DE DADOS', fontsize=9, color=COLORS['gray'], fontstyle='italic')
    ax.text(0.3, 0.5, 'OBSERVABILIDADE', fontsize=9, color=COLORS['gray'], fontstyle='italic')

    # Horizontal separators
    for y_pos in [6.6, 4.8, 2.1, 0.4]:
        ax.axhline(y=y_pos, xmin=0.02, xmax=0.98, color=COLORS['light_gray'], lw=1, ls='--')

    # Client Layer
    add_box(ax, 2, 7.5, 3, 0.8, 'Frontend React\n(Porta 3000)', '#3B82F6', fontsize=9)
    add_box(ax, 7, 7.5, 3, 0.8, 'Simulador Python\n(CLI + GUI)', '#8B5CF6', fontsize=9)

    # Gateway Layer
    add_box(ax, 4, 5.5, 4.5, 1.0, 'NGINX API Gateway\n(Porta 80)\nRate Limit · CORS · Security Headers', '#0EA5E9', fontsize=9)

    # Application Layer — 3 instances
    for i, (x_pos, name) in enumerate([(1.5, 'Instância 1'), (5.25, 'Instância 2'), (9, 'Instância 3')]):
        add_box(ax, x_pos, 3.0, 3.2, 1.6, '', '#1E40AF', alpha=0.15, textcolor='black')
        add_box(ax, x_pos + 0.1, 3.9, 3.0, 0.6, f'Spring Boot :9080\n{name}', '#1E40AF', fontsize=8)
        add_box(ax, x_pos + 0.1, 3.1, 3.0, 0.6, 'Cache L1\nConcurrentHashMap', '#6366F1', fontsize=7)

    # Kafka
    add_box(ax, 10.5, 5.5, 2.5, 1.0, 'Apache Kafka\ntransacao-pedagio', '#F59E0B', fontsize=9, textcolor='#1E293B')

    # Data Layer
    add_box(ax, 1.5, 1.0, 3, 0.9, 'Redis 7 (Cache L2)\nTTL 60min · LRU', '#EF4444', fontsize=9)
    add_box(ax, 5.5, 1.0, 3, 0.9, 'PostgreSQL 15\n(SSOT)', '#3B82F6', fontsize=9)
    add_box(ax, 9.5, 1.0, 3.2, 0.9, 'Zookeeper\n(Kafka Metadata)', '#78716C', fontsize=9)

    # Observability
    add_box(ax, 2.5, -0.3, 2.5, 0.6, 'Prometheus', '#E85D04', fontsize=9)
    add_box(ax, 6.5, -0.3, 2.5, 0.6, 'Grafana', '#22C55E', fontsize=9)

    # Arrows — Clients to Gateway
    add_arrow(ax, 3.5, 7.5, 5.5, 6.5, COLORS['primary'])
    add_arrow(ax, 8.5, 7.5, 7.5, 6.5, COLORS['secondary'])

    # Gateway to Backend instances
    add_arrow(ax, 5.0, 5.5, 3.1, 4.6, COLORS['info'])
    add_arrow(ax, 6.25, 5.5, 6.85, 4.6, COLORS['info'])
    add_arrow(ax, 7.5, 5.5, 10.6, 4.6, COLORS['info'])

    # Kafka to Backend instances
    add_arrow(ax, 10.5, 5.7, 4.7, 4.2, COLORS['warning'], style='->')
    add_arrow(ax, 10.5, 5.7, 8.45, 4.2, COLORS['warning'], style='->')
    add_arrow(ax, 11.0, 5.5, 12.1, 4.2, COLORS['warning'], style='->')

    # Simulator to Kafka
    add_arrow(ax, 10, 7.9, 10.5, 6.5, COLORS['warning'])

    # Backend to Data layer
    for x_pos in [3.1, 6.85, 10.6]:
        add_arrow(ax, x_pos, 3.0, 3.0, 1.9, '#EF4444', lw=1)
        add_arrow(ax, x_pos, 3.0, 7.0, 1.9, '#3B82F6', lw=1)

    # Prometheus arrows
    for x_pos in [3.1, 6.85, 10.6]:
        add_arrow(ax, x_pos, 3.0, 3.75, 0.3, '#E85D04', lw=0.8, style='->')

    # Prometheus to Grafana
    add_arrow(ax, 5.0, 0.0, 6.5, 0.0, '#E85D04')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1-architecture.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 1 — Architecture Diagram')


# ============================================================
# FIGURE 2 — Sequence Diagram (Cache-Aside)
# ============================================================
def fig2_sequence():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Figura 2 — Diagrama de Sequência: Correção de Transação com Cache-Aside', pad=15, fontsize=13)

    # Lifeline positions
    actors = [
        (1.5, 'Operador'),
        (3.5, 'NGINX'),
        (5.5, 'Backend\n(Spring Boot)'),
        (7.5, 'Cache L1\n(ConcurrentHashMap)'),
        (9.5, 'Cache L2\n(Redis)'),
        (11.5, 'PostgreSQL'),
    ]

    # Draw actor boxes and lifelines
    for x, name in actors:
        add_box(ax, x - 0.6, 9.0, 1.2, 0.7, name, COLORS['primary'], fontsize=7)
        ax.plot([x, x], [0.5, 9.0], color=COLORS['light_gray'], lw=1.5, ls='--')

    # Messages
    y = 8.5
    messages = [
        (1.5, 3.5, 'GET /api/transacoes/{id}', 0),
        (3.5, 5.5, 'proxy_pass (round-robin)', 0),
        (5.5, 7.5, 'localCache.get(key)', 0),
        (7.5, 5.5, 'MISS (null / expired)', 1),
        (5.5, 9.5, 'redisTemplate.get(key)', 0),
        (9.5, 5.5, 'MISS (null)', 1),
        (5.5, 11.5, 'JPA findById(id)', 0),
        (11.5, 5.5, 'TransacaoPedagio entity', 1),
        (5.5, 9.5, 'redisTemplate.set(key, val, 60min)', 0),
        (5.5, 7.5, 'localCache.put(key, CacheEntry)', 0),
        (5.5, 5.5, 'origemDados = BANCO_DADOS', 2),
        (5.5, 3.5, 'HTTP 200 + JSON', 1),
        (3.5, 1.5, 'Response', 1),
    ]

    step_h = 0.55
    for i, (x1, x2, label, msg_type) in enumerate(messages):
        y_pos = 8.3 - i * step_h
        color = COLORS['danger'] if msg_type == 1 else ('#059669' if msg_type == 2 else COLORS['dark'])
        style = '<-' if msg_type == 1 else '->'
        ls = '--' if msg_type == 1 else '-'

        ax.annotate('', xy=(x2, y_pos), xytext=(x1, y_pos),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.3, ls=ls))

        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y_pos + 0.12, label, ha='center', va='bottom',
                fontsize=7, color=color, fontstyle='italic' if msg_type == 2 else 'normal',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.85))

    # Activation boxes
    for x, y_start, y_end in [(5.5, 8.2, 2.0), (11.5, 4.9, 4.4)]:
        rect = FancyBboxPatch((x - 0.15, y_end), 0.3, y_start - y_end,
                              boxstyle="round,pad=0.02", facecolor=COLORS['primary'], alpha=0.15, edgecolor=COLORS['primary'])
        ax.add_patch(rect)

    # Legend
    ax.text(0.5, 0.3, '→ Requisição    - - → Resposta    → set = Populate cache', fontsize=8, color=COLORS['gray'])

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2-sequence.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 2 — Sequence Diagram')


# ============================================================
# FIGURE 3 — ER Diagram
# ============================================================
def fig3_er_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Figura 3 — Diagrama Entidade-Relacionamento (10 Tabelas)', pad=15, fontsize=14)

    tables = {
        'concessionaria': (0.5, 7.5, ['PK id', 'nome', 'cnpj (UNIQUE)', 'contrato']),
        'rodovia': (4, 7.5, ['PK id', 'FK concessionaria_id', 'codigo', 'nome', 'uf', 'extensao_km']),
        'praca_pedagio': (8, 7.5, ['PK id', 'FK rodovia_id', 'nome', 'km', 'sentido', 'ativa']),
        'pista_pedagio': (12, 7.5, ['PK id', 'FK praca_id', 'numero_pista', 'tipo']),
        'tarifa_pedagio': (0.5, 4.0, ['PK id', 'tipo_veiculo', 'valor', 'vigencia_inicio']),
        'transacao_pedagio': (4, 4.0, ['PK id', 'FK praca_id', 'FK pista_id', 'FK tarifa_id', 'placa', 'tag', 'hash_integridade', 'status']),
        'ocorrencia_transacao': (8.5, 4.0, ['PK id', 'FK transacao_id', 'tipo', 'descricao']),
        'correcao_transacao': (12, 4.0, ['PK id', 'FK transacao_id', 'FK operador_id', 'tipo_correcao']),
        'operador': (12, 1.0, ['PK id', 'username (UNIQUE)', 'email (UNIQUE)', 'senha_hash']),
        'registro_performance': (0.5, 1.0, ['PK id', 'endpoint', 'tempo_processamento', 'origem_dados', 'cpu_uso']),
    }

    table_colors = {
        'concessionaria': '#3B82F6', 'rodovia': '#3B82F6', 'praca_pedagio': '#3B82F6',
        'pista_pedagio': '#3B82F6', 'tarifa_pedagio': '#8B5CF6',
        'transacao_pedagio': '#059669', 'ocorrencia_transacao': '#D97706',
        'correcao_transacao': '#D97706', 'operador': '#EF4444',
        'registro_performance': '#64748B',
    }

    for name, (x, y, cols) in tables.items():
        w = 3.2
        h_header = 0.4
        h_row = 0.22
        h_total = h_header + h_row * len(cols) + 0.1
        color = table_colors[name]

        # Background
        rect = FancyBboxPatch((x, y - h_total + h_header), w, h_total,
                              boxstyle="round,pad=0.05", facecolor='white',
                              edgecolor=color, linewidth=1.5)
        ax.add_patch(rect)

        # Header
        header = FancyBboxPatch((x, y), w, h_header,
                                boxstyle="round,pad=0.05", facecolor=color,
                                edgecolor=color, linewidth=1.5)
        ax.add_patch(header)
        ax.text(x + w/2, y + h_header/2, name, ha='center', va='center',
                fontsize=7.5, color='white', fontweight='bold')

        # Columns
        for i, col in enumerate(cols):
            cy = y - (i + 1) * h_row
            col_color = COLORS['danger'] if col.startswith('PK') else (COLORS['primary'] if col.startswith('FK') else COLORS['dark'])
            ax.text(x + 0.15, cy, col, fontsize=6, color=col_color, va='center')

    # Relationships (arrows)
    relationships = [
        # (from_table_right_x, from_y, to_table_left_x, to_y)
        (3.7, 7.7, 4.0, 7.7),        # concessionaria -> rodovia
        (7.2, 7.7, 8.0, 7.7),        # rodovia -> praca_pedagio
        (11.2, 7.7, 12.0, 7.7),      # praca -> pista
        (9.6, 7.1, 9.6, 4.4),        # praca -> transacao (down)
        (3.7, 4.2, 4.0, 4.2),        # tarifa -> transacao
        (7.2, 4.2, 8.5, 4.2),        # transacao -> ocorrencia
        (7.2, 3.8, 12.0, 4.0),       # transacao -> correcao
        (13.6, 3.6, 13.6, 1.4),      # correcao -> operador
    ]

    for x1, y1, x2, y2 in relationships:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#475569', lw=1.2))

    # Legend
    legend_y = 0.2
    ax.text(4, legend_y, 'PK', fontsize=7, color=COLORS['danger'], fontweight='bold')
    ax.text(4.5, legend_y, '= Primary Key', fontsize=7, color=COLORS['gray'])
    ax.text(6.5, legend_y, 'FK', fontsize=7, color=COLORS['primary'], fontweight='bold')
    ax.text(7.0, legend_y, '= Foreign Key', fontsize=7, color=COLORS['gray'])
    ax.text(9, legend_y, '→ = Relacionamento 1:N', fontsize=7, color=COLORS['gray'])

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3-er-diagram.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 3 — ER Diagram')


# ============================================================
# FIGURE 4 — Cache-Aside Flow
# ============================================================
def fig4_cache_aside():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('Figura 4 — Fluxo da Estratégia Cache-Aside em Duas Camadas', pad=15, fontsize=14)

    # Application
    add_box(ax, 0.3, 2.3, 2.0, 1.4, 'Aplicação\n(CacheService)', COLORS['primary'], fontsize=9)

    # L1 Cache
    add_box(ax, 3.5, 3.5, 2.2, 1.5, 'Cache L1\nConcurrentHashMap\nTTL: 30min\nMax: 1000', '#6366F1', fontsize=8)

    # L2 Cache
    add_box(ax, 6.8, 3.5, 2.2, 1.5, 'Cache L2\nRedis\nTTL: 60min\nLRU', '#EF4444', fontsize=8)

    # Database
    add_box(ax, 10.0, 3.5, 1.7, 1.5, 'PostgreSQL\n(SSOT)', '#3B82F6', fontsize=8)

    # Decision diamonds
    def diamond(ax, cx, cy, size, text, color):
        pts = np.array([[cx, cy + size], [cx + size, cy], [cx, cy - size], [cx - size, cy]])
        poly = plt.Polygon(pts, facecolor=color, edgecolor='#334155', lw=1.2, alpha=0.9)
        ax.add_patch(poly)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    diamond(ax, 4.6, 2.0, 0.5, 'L1\nHIT?', '#6366F1')
    diamond(ax, 7.9, 2.0, 0.5, 'L2\nHIT?', '#EF4444')

    # Result boxes
    add_box(ax, 3.5, 0.2, 2.2, 0.7, 'Retorna dados\norigem: CACHE_LOCAL', '#059669', fontsize=7)
    add_box(ax, 6.8, 0.2, 2.2, 0.7, 'Retorna dados\norigem: CACHE_REDIS', '#059669', fontsize=7)
    add_box(ax, 10.0, 0.2, 1.7, 0.7, 'Retorna dados\norigem: BANCO_DADOS', '#059669', fontsize=7)

    # Arrows
    add_arrow(ax, 2.3, 3.0, 3.5, 4.0, COLORS['dark'])  # App -> L1
    add_arrow(ax, 2.3, 3.0, 4.6, 2.5, COLORS['dark'])   # App -> L1 decision

    add_arrow(ax, 4.6, 1.5, 4.6, 0.9, '#059669')  # L1 HIT -> return
    ax.text(4.2, 1.2, 'SIM', fontsize=7, color='#059669', fontweight='bold')

    add_arrow(ax, 5.1, 2.0, 6.8, 4.0, COLORS['dark'])  # L1 MISS -> L2
    add_arrow(ax, 5.1, 2.0, 7.4, 2.0, COLORS['dark'])   # L1 MISS -> L2 decision
    ax.text(5.5, 2.2, 'NÃO', fontsize=7, color=COLORS['danger'], fontweight='bold')

    add_arrow(ax, 7.9, 1.5, 7.9, 0.9, '#059669')  # L2 HIT -> return
    ax.text(7.5, 1.2, 'SIM', fontsize=7, color='#059669', fontweight='bold')

    add_arrow(ax, 8.4, 2.0, 10.0, 4.0, COLORS['dark'])  # L2 MISS -> DB
    ax.text(8.8, 2.4, 'NÃO', fontsize=7, color=COLORS['danger'], fontweight='bold')

    add_arrow(ax, 10.8, 3.5, 10.8, 0.9, '#059669')  # DB -> return

    # Populate arrows (dotted)
    ax.annotate('', xy=(8.0, 3.5), xytext=(10.8, 1.0),
                arrowprops=dict(arrowstyle='->', color='#6366F1', lw=1, ls='--'))
    ax.text(9.8, 2.0, 'popula\nL2', fontsize=6, color='#6366F1', fontstyle='italic')

    ax.annotate('', xy=(4.6, 3.5), xytext=(7.9, 1.0),
                arrowprops=dict(arrowstyle='->', color='#6366F1', lw=1, ls='--'))
    ax.text(5.8, 1.8, 'popula\nL1', fontsize=6, color='#6366F1', fontstyle='italic')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4-cache-aside.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 4 — Cache-Aside Flow')


# ============================================================
# FIGURE 5 — Request Pipeline
# ============================================================
def fig5_pipeline():
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title('Figura 5 — Pipeline de Processamento de Requisições', pad=15, fontsize=14)

    # Pipeline stages
    stages = [
        (0.3, 'Entrada\n(React / Python)', '#64748B'),
        (2.3, 'NGINX\nBalanceamento\nRate Limit\nCORS', '#0EA5E9'),
        (4.8, 'Performance\nInterceptor', '#D97706'),
        (6.8, 'Controller\nREST API', '#7C3AED'),
        (8.8, 'CacheService\nL1 → L2 → BD', '#059669'),
        (11.3, 'Resposta\norigem_dados\n+ métricas', '#059669'),
    ]

    y_center = 2.5
    for x, label, color in stages:
        add_box(ax, x, y_center - 0.7, 1.8, 1.4, label, color, fontsize=8)

    # Arrows between stages
    for i in range(len(stages) - 1):
        x1 = stages[i][0] + 1.8
        x2 = stages[i+1][0]
        add_arrow(ax, x1, y_center, x2, y_center, COLORS['dark'], lw=2)

    # Kafka pipeline (below)
    add_box(ax, 0.3, 0.3, 1.8, 0.8, 'Simulador\nPython', '#8B5CF6', fontsize=8)
    add_box(ax, 3.0, 0.3, 2.0, 0.8, 'Kafka\ntransacao-pedagio', '#F59E0B', fontsize=8, textcolor='#1E293B')
    add_box(ax, 6.0, 0.3, 2.3, 0.8, 'KafkaConsumer\n@Transactional', '#D97706', fontsize=8)
    add_box(ax, 9.3, 0.3, 2.0, 0.8, 'PostgreSQL\nPersistência', '#3B82F6', fontsize=8)

    add_arrow(ax, 2.1, 0.7, 3.0, 0.7, COLORS['dark'], lw=1.5)
    add_arrow(ax, 5.0, 0.7, 6.0, 0.7, COLORS['dark'], lw=1.5)
    add_arrow(ax, 8.3, 0.7, 9.3, 0.7, COLORS['dark'], lw=1.5)

    ax.text(7.0, 4.3, 'Pipeline de Requisição HTTP (síncrono)', fontsize=10, ha='center',
            color=COLORS['dark'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['light_gray'], edgecolor='none'))
    ax.text(5.5, 1.3, 'Pipeline de Ingestão Kafka (assíncrono)', fontsize=10, ha='center',
            color=COLORS['dark'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF3C7', edgecolor='none'))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5-pipeline.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 5 — Request Pipeline')


# ============================================================
# FIGURE 6 — Latency Distribution Comparison
# ============================================================
def fig6_latency():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    np.random.seed(42)
    # Simulate latency distributions
    data_a = np.random.lognormal(mean=4.3, sigma=0.5, size=2000)  # ~80-120ms center
    data_b = np.random.lognormal(mean=2.8, sigma=0.6, size=2000)  # ~10-25ms center
    data_c = np.random.lognormal(mean=1.2, sigma=0.8, size=2000)  # ~2-8ms center

    bins = np.logspace(np.log10(0.5), np.log10(500), 60)

    ax.hist(data_a, bins=bins, alpha=0.6, color=COLORS['scenario_a'], label='Cenário A (Sem Cache)', density=True)
    ax.hist(data_b, bins=bins, alpha=0.6, color=COLORS['scenario_b'], label='Cenário B (Redis L2)', density=True)
    ax.hist(data_c, bins=bins, alpha=0.6, color=COLORS['scenario_c'], label='Cenário C (L1 + L2 Híbrido)', density=True)

    ax.set_xscale('log')
    ax.set_xlabel('Latência (ms) — escala logarítmica', fontsize=11)
    ax.set_ylabel('Densidade de Frequência', fontsize=11)
    ax.set_title('Figura 6 — Comparação de Distribuição de Latência Entre Cenários\n(250 usuários simultâneos — dados projetados)', fontsize=12)
    ax.legend(fontsize=10, loc='upper right')

    # Annotate medians
    for data, color, label in [(data_a, COLORS['scenario_a'], 'A'),
                                (data_b, COLORS['scenario_b'], 'B'),
                                (data_c, COLORS['scenario_c'], 'C')]:
        median = np.median(data)
        ax.axvline(median, color=color, ls='--', lw=1.5, alpha=0.8)
        ax.text(median * 1.1, ax.get_ylim()[1] * 0.85, f'Md({label})={median:.0f}ms',
                fontsize=8, color=color, rotation=0)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig6-latency.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 6 — Latency Distribution')


# ============================================================
# FIGURE 7 — Throughput vs Concurrent Users
# ============================================================
def fig7_throughput():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    users = [100, 250, 500]
    # Midpoints of projected ranges
    tps_a = [275, 200, 115]
    tps_b = [1000, 850, 650]
    tps_c = [2000, 1800, 1600]

    # Error bars (range width / 2)
    err_a = [75, 50, 35]
    err_b = [200, 150, 150]
    err_c = [500, 400, 400]

    x = np.arange(len(users))
    w = 0.25

    bars_a = ax.bar(x - w, tps_a, w, yerr=err_a, color=COLORS['scenario_a'], alpha=0.85,
                    label='Cenário A (Sem Cache)', capsize=5, edgecolor='white', linewidth=0.5)
    bars_b = ax.bar(x, tps_b, w, yerr=err_b, color=COLORS['scenario_b'], alpha=0.85,
                    label='Cenário B (Redis L2)', capsize=5, edgecolor='white', linewidth=0.5)
    bars_c = ax.bar(x + w, tps_c, w, yerr=err_c, color=COLORS['scenario_c'], alpha=0.85,
                    label='Cenário C (L1 + L2)', capsize=5, edgecolor='white', linewidth=0.5)

    # Value labels on bars
    for bars in [bars_a, bars_b, bars_c]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 80, f'{int(h)}',
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xlabel('Usuários Simultâneos', fontsize=11)
    ax.set_ylabel('Throughput (TPS)', fontsize=11)
    ax.set_title('Figura 7 — Throughput vs. Usuários Simultâneos\n(dados projetados)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(users)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 3000)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig7-throughput.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 7 — Throughput Chart')


# ============================================================
# FIGURE 8 — CPU & Memory Under Load
# ============================================================
def fig8_resources():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    scenarios = ['Cenário A\n(Sem Cache)', 'Cenário B\n(Redis L2)', 'Cenário C\n(L1 + L2)']
    colors = [COLORS['scenario_a'], COLORS['scenario_b'], COLORS['scenario_c']]

    # CPU Usage (%) at 500 concurrent users
    cpu = [78, 45, 32]
    bars1 = ax1.bar(scenarios, cpu, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax1.set_ylabel('Utilização de CPU (%)', fontsize=11)
    ax1.set_title('Utilização de CPU\n(500 usuários simultâneos)', fontsize=11)
    ax1.set_ylim(0, 100)
    for bar, val in zip(bars1, cpu):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 2, f'{val}%',
                ha='center', fontsize=11, fontweight='bold')

    # Memory Usage (MB) at 500 concurrent users
    heap_used = [380, 310, 340]
    heap_free = [132, 202, 172]
    x = np.arange(len(scenarios))
    ax2.bar(x, heap_used, 0.5, label='Heap Usada', color='#3B82F6', alpha=0.85)
    ax2.bar(x, heap_free, 0.5, bottom=heap_used, label='Heap Livre', color='#93C5FD', alpha=0.85)
    ax2.set_ylabel('Memória Heap JVM (MB)', fontsize=11)
    ax2.set_title('Consumo de Memória\n(500 usuários simultâneos)', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios)
    ax2.legend(fontsize=9)
    for i, (used, free) in enumerate(zip(heap_used, heap_free)):
        ax2.text(i, used / 2, f'{used} MB', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax2.text(i, used + free / 2, f'{free} MB', ha='center', va='center', fontsize=9, fontweight='bold', color='#1E40AF')

    fig.suptitle('Figura 8 — Consumo de CPU e Memória Sob Carga (dados projetados)', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig8-resources.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 8 — CPU & Memory Chart')


# ============================================================
# FIGURE 9 — Radar Chart (Strategy Comparison)
# ============================================================
def fig9_radar():
    categories = ['Latência', 'Throughput', 'Consistência',
                  'Eficiência\nde Memória', 'Simplicidade', 'Resiliência']
    N = len(categories)

    # Scores (0-10 scale): higher = better
    scenario_a = [2, 2, 10, 9, 10, 3]
    scenario_b = [7, 7, 7, 6, 6, 6]
    scenario_c = [10, 10, 5, 7, 3, 9]

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    for s in [scenario_a, scenario_b, scenario_c]:
        s += s[:1]

    fig, ax = plt.subplots(1, 1, figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_title('Figura 9 — Comparação Multidimensional\ndas Estratégias de Cache\n(dados projetados)',
                 fontsize=13, fontweight='bold', pad=25)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(30)

    plt.xticks(angles[:-1], categories, fontsize=10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=8, color=COLORS['gray'])
    ax.set_ylim(0, 10)

    ax.plot(angles, scenario_a, 'o-', linewidth=2, color=COLORS['scenario_a'], label='Cenário A (Sem Cache)')
    ax.fill(angles, scenario_a, alpha=0.1, color=COLORS['scenario_a'])

    ax.plot(angles, scenario_b, 's-', linewidth=2, color=COLORS['scenario_b'], label='Cenário B (Redis L2)')
    ax.fill(angles, scenario_b, alpha=0.1, color=COLORS['scenario_b'])

    ax.plot(angles, scenario_c, 'D-', linewidth=2, color=COLORS['scenario_c'], label='Cenário C (L1 + L2)')
    ax.fill(angles, scenario_c, alpha=0.15, color=COLORS['scenario_c'])

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig9-radar.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print('✓ Figure 9 — Radar Chart')


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f'Generating figures in {OUTPUT_DIR}...\n')
    fig1_architecture()
    fig2_sequence()
    fig3_er_diagram()
    fig4_cache_aside()
    fig5_pipeline()
    fig6_latency()
    fig7_throughput()
    fig8_resources()
    fig9_radar()
    print(f'\nAll 9 figures generated in {OUTPUT_DIR}/')
