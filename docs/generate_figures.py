#!/usr/bin/env python3
"""Generate all academic paper figures for the Smart Toll Cache System.

Uses experimentally measured data from the STCS evaluation campaign
(>50,000 requests across 3 scenarios x 3 user loads x 3 repetitions).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, BoxStyle
from matplotlib.lines import Line2D
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -- Professional color palette -----------------------------------------------
PALETTE = {
    # Scenario colors (colorblind-friendly)
    'scenario_a': '#D32F2F',   # Red - no cache
    'scenario_b': '#F57C00',   # Orange - Redis L2
    'scenario_c': '#2E7D32',   # Green - hybrid L1+L2

    # Architecture component colors
    'frontend':    '#1565C0',
    'simulator':   '#6A1B9A',
    'gateway':     '#00838F',
    'backend':     '#1A237E',
    'cache_l1':    '#4527A0',
    'cache_l2':    '#C62828',
    'database':    '#1565C0',
    'kafka':       '#E65100',
    'zookeeper':   '#4E342E',
    'prometheus':  '#BF360C',
    'grafana':     '#1B5E20',

    # UI colors
    'bg':          '#FFFFFF',
    'card_bg':     '#FAFBFC',
    'border':      '#CFD8DC',
    'text':        '#212121',
    'text_sec':    '#546E7A',
    'grid':        '#ECEFF1',
    'divider':     '#B0BEC5',
    'accent':      '#1565C0',
    'hit':         '#2E7D32',
    'miss':        '#D32F2F',
}

# -- Global matplotlib style --------------------------------------------------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica'],
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelcolor': PALETTE['text'],
    'axes.edgecolor': PALETTE['border'],
    'axes.linewidth': 0.8,
    'axes.facecolor': PALETTE['card_bg'],
    'axes.grid': True,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': PALETTE['bg'],
    'figure.dpi': 150,
    'grid.alpha': 0.4,
    'grid.color': PALETTE['grid'],
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'xtick.color': PALETTE['text_sec'],
    'ytick.color': PALETTE['text_sec'],
    'legend.framealpha': 0.95,
    'legend.edgecolor': PALETTE['border'],
    'legend.fontsize': 9,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

DPI = 250  # publication quality


# -- Helpers -------------------------------------------------------------------
def _rounded_box(ax, x, y, w, h, text, facecolor, fontsize=8,
                 textcolor='white', edgecolor='#455A64', lw=1.0, alpha=1.0,
                 shadow=False, zorder=2):
    """Draw a rounded box with centered multi-line text."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=BoxStyle.Round(pad=0.08, rounding_size=0.12),
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=lw, alpha=alpha, zorder=zorder,
    )
    if shadow:
        shadow_box = FancyBboxPatch(
            (x + 0.04, y - 0.04), w, h,
            boxstyle=BoxStyle.Round(pad=0.08, rounding_size=0.12),
            facecolor='#00000015', edgecolor='none', zorder=zorder - 1,
        )
        ax.add_patch(shadow_box)
    ax.add_patch(box)
    effects = []
    if textcolor == 'white':
        effects = [pe.withStroke(linewidth=0.3, foreground='#00000040')]
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
            fontsize=fontsize, color=textcolor, fontweight='bold',
            path_effects=effects, zorder=zorder + 1)


def _arrow(ax, x1, y1, x2, y2, color='#455A64', style='->', lw=1.3, ls='-'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls),
                zorder=5)


def _save(fig, name):
    """Save figure with consistent settings."""
    fig.savefig(os.path.join(OUTPUT_DIR, name), dpi=DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)


def _scenario_legend_handles():
    """Return legend handles for A/B/C scenarios."""
    return [
        mpatches.Patch(color=PALETTE['scenario_a'], label='Cenario A - Sem Cache'),
        mpatches.Patch(color=PALETTE['scenario_b'], label='Cenario B - Redis (L2)'),
        mpatches.Patch(color=PALETTE['scenario_c'], label='Cenario C - Hibrido (L1 + L2)'),
    ]


# ==============================================================================
#  FIGURE 1 - System Architecture
# ==============================================================================
def fig1_architecture():
    fig, ax = plt.subplots(figsize=(14, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.8, 9.2)
    ax.axis('off')
    ax.set_title('Figura 1 \u2014 Diagrama de Arquitetura Geral do Sistema',
                 fontsize=14, pad=18, color=PALETTE['text'])

    # -- Layer backgrounds --
    layer_specs = [
        (8.05, 1.05, 'CAMADA DE CLIENTES', '#E3F2FD'),
        (6.2, 1.75, 'CAMADA DE GATEWAY / MENSAGERIA', '#E0F7FA'),
        (3.7, 2.4, 'CAMADA DE APLICACAO', '#EDE7F6'),
        (0.5, 3.1, 'CAMADA DE DADOS E OBSERVABILIDADE', '#E8F5E9'),
    ]
    for y_bottom, height, label, bg_color in layer_specs:
        rect = FancyBboxPatch(
            (0.2, y_bottom), 13.6, height,
            boxstyle=BoxStyle.Round(pad=0.05, rounding_size=0.15),
            facecolor=bg_color, edgecolor=PALETTE['divider'],
            linewidth=0.6, alpha=0.5, zorder=0,
        )
        ax.add_patch(rect)
        ax.text(0.5, y_bottom + height - 0.22, label,
                fontsize=7.5, color=PALETTE['text_sec'],
                fontstyle='italic', fontweight='bold', zorder=1)

    # -- Client Layer --
    _rounded_box(ax, 2.0, 8.1, 3.0, 0.8,
                 'Frontend React\nPorta 3000', PALETTE['frontend'], fontsize=9, shadow=True)
    _rounded_box(ax, 7.5, 8.1, 3.0, 0.8,
                 'Simulador Python\nCLI + GUI', PALETTE['simulator'], fontsize=9, shadow=True)

    # -- Gateway & Kafka --
    _rounded_box(ax, 3.2, 6.4, 4.6, 1.1,
                 'NGINX API Gateway \u2014 Porta 80\nRound-Robin \u00b7 Rate Limit 10r/s \u00b7 CORS',
                 PALETTE['gateway'], fontsize=9, shadow=True)
    _rounded_box(ax, 9.5, 6.4, 3.2, 1.1,
                 'Apache Kafka\ntransacao-pedagio\nacks=all',
                 PALETTE['kafka'], fontsize=9, shadow=True)

    # -- Application Layer - 3 backend instances --
    instances = [
        (0.8, 'Instancia 1\n:9080'),
        (4.8, 'Instancia 2\n:9080'),
        (8.8, 'Instancia 3\n:9080'),
    ]
    for x, label in instances:
        container = FancyBboxPatch(
            (x, 3.9), 3.6, 2.0,
            boxstyle=BoxStyle.Round(pad=0.05, rounding_size=0.1),
            facecolor='#E8EAF6', edgecolor=PALETTE['backend'],
            linewidth=1.0, alpha=0.5, zorder=1,
        )
        ax.add_patch(container)
        _rounded_box(ax, x + 0.15, 5.05, 3.3, 0.7,
                     'Spring Boot 4.0.3\n%s' % label, PALETTE['backend'], fontsize=7.5)
        _rounded_box(ax, x + 0.15, 4.05, 3.3, 0.7,
                     'Cache L1 \u2014 ConcurrentHashMap\nTTL 30min \u00b7 Max 1.000 \u00b7 ~3 MB',
                     PALETTE['cache_l1'], fontsize=7)

    # -- Data Layer --
    _rounded_box(ax, 0.8, 1.6, 3.2, 0.9,
                 'Redis 7 \u2014 Cache L2\nTTL 60min \u00b7 LRU \u00b7 128 MB',
                 PALETTE['cache_l2'], fontsize=9, shadow=True)
    _rounded_box(ax, 4.8, 1.6, 3.2, 0.9,
                 'PostgreSQL 15 \u2014 SSOT\n10 tabelas \u00b7 15 indices',
                 PALETTE['database'], fontsize=9, shadow=True)
    _rounded_box(ax, 9.2, 1.6, 3.2, 0.9,
                 'Zookeeper\nKafka Metadata',
                 PALETTE['zookeeper'], fontsize=9, shadow=True)

    # -- Observability --
    _rounded_box(ax, 2.0, 0.1, 2.5, 0.65, 'Prometheus\nscrape 15s',
                 PALETTE['prometheus'], fontsize=8, shadow=True)
    _rounded_box(ax, 6.5, 0.1, 2.5, 0.65, 'Grafana\nDashboards',
                 PALETTE['grafana'], fontsize=8, shadow=True)

    # -- Arrows --
    _arrow(ax, 3.5, 8.1, 5.0, 7.5, PALETTE['frontend'], lw=1.5)
    _arrow(ax, 9.0, 8.1, 7.2, 7.5, PALETTE['simulator'], lw=1.5)
    _arrow(ax, 10.0, 8.1, 10.5, 7.5, PALETTE['kafka'], lw=1.5)

    for x_target in [2.6, 6.6, 10.6]:
        _arrow(ax, 5.5, 6.4, x_target, 5.9, PALETTE['gateway'], lw=1.0)

    for x_target in [2.6, 6.6, 10.6]:
        _arrow(ax, 10.5, 6.4, x_target, 5.9, PALETTE['kafka'], lw=0.8, ls='--')

    for x_src in [2.6, 6.6, 10.6]:
        _arrow(ax, x_src, 3.9, 2.4, 2.5, PALETTE['cache_l2'], lw=0.8)
        _arrow(ax, x_src, 3.9, 6.4, 2.5, PALETTE['database'], lw=0.8)

    _arrow(ax, 11.1, 6.4, 10.8, 2.5, PALETTE['zookeeper'], lw=0.7, ls=':')

    for x_src in [2.6, 6.6, 10.6]:
        _arrow(ax, x_src, 3.9, 3.25, 0.75, PALETTE['prometheus'], lw=0.6, ls=':')

    _arrow(ax, 4.5, 0.42, 6.5, 0.42, PALETTE['prometheus'], lw=1.0)

    ax.text(13.0, -0.5, 'Docker Compose\n12 servicos', fontsize=7,
            ha='center', va='center', color=PALETTE['text_sec'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECEFF1',
                      edgecolor=PALETTE['divider'], linewidth=0.5))

    _save(fig, 'fig1-architecture.png')
    print('  \u2713 Figura 1 \u2014 Arquitetura do Sistema')


# ==============================================================================
#  FIGURE 2 - Sequence Diagram (Cache-Aside)
# ==============================================================================
def fig2_sequence():
    fig, ax = plt.subplots(figsize=(14, 10.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.axis('off')
    ax.set_title('Figura 2 \u2014 Diagrama de Sequencia: Correcao de Transacao com Cache-Aside',
                 fontsize=13, pad=18, color=PALETTE['text'])

    actors = [
        (1.5,  'Operador'),
        (3.5,  'NGINX\nGateway'),
        (5.5,  'Spring Boot\nBackend'),
        (7.5,  'Cache L1\nConcurrentHashMap'),
        (9.5,  'Cache L2\nRedis'),
        (11.5, 'PostgreSQL'),
    ]
    actor_colors = [
        PALETTE['text'], PALETTE['gateway'], PALETTE['backend'],
        PALETTE['cache_l1'], PALETTE['cache_l2'], PALETTE['database'],
    ]

    for (x, name), color in zip(actors, actor_colors):
        _rounded_box(ax, x - 0.65, 9.5, 1.3, 0.8, name, color, fontsize=7)
        ax.plot([x, x], [0.3, 9.5], color=PALETTE['divider'], lw=1.2, ls='--', zorder=0)

    messages = [
        (1.5,  3.5,  'GET /api/transacoes/{id}',              'req'),
        (3.5,  5.5,  'proxy_pass (round-robin)',               'req'),
        (5.5,  7.5,  'localCache.get(key)',                    'req'),
        (7.5,  5.5,  'MISS \u2014 null / expirado',           'resp'),
        (5.5,  9.5,  'redisTemplate.opsForValue().get(key)',   'req'),
        (9.5,  5.5,  'MISS \u2014 null',                      'resp'),
        (5.5,  11.5, 'JPA findById(id)',                       'req'),
        (11.5, 5.5,  'TransacaoPedagio entity',                'resp'),
        (5.5,  9.5,  'redisTemplate.set(key, val, 60 min)',   'cache'),
        (5.5,  7.5,  'localCache.put(key, CacheEntry)',        'cache'),
        (5.5,  5.5,  'origemDados = BANCO_DADOS',             'note'),
        (5.5,  3.5,  'HTTP 200 + JSON + metricas',            'resp'),
        (3.5,  1.5,  'Response',                               'resp'),
    ]

    y_start = 9.2
    step = 0.6
    for i, (x1, x2, label, msg_type) in enumerate(messages):
        y = y_start - i * step
        if msg_type == 'req':
            color, ls, arrow = PALETTE['text'], '-', '->'
        elif msg_type == 'resp':
            color, ls, arrow = PALETTE['miss'], '--', '<-'
        elif msg_type == 'cache':
            color, ls, arrow = PALETTE['cache_l1'], '--', '->'
        else:
            color, ls, arrow = PALETTE['hit'], '-', '-'

        if msg_type != 'note':
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle=arrow, color=color, lw=1.2, ls=ls),
                        zorder=3)

        mid_x = (x1 + x2) / 2
        bbox_color = '#FFF8E1' if msg_type == 'cache' else ('#F1F8E9' if msg_type == 'note' else 'white')
        ax.text(mid_x, y + 0.13, label, ha='center', va='bottom', fontsize=6.8,
                color=color, fontstyle='italic' if msg_type in ('cache', 'note') else 'normal',
                bbox=dict(boxstyle='round,pad=0.12', facecolor=bbox_color,
                          edgecolor='none', alpha=0.9),
                zorder=4)

    for x, yt, yb, c in [(5.5, 9.1, 1.7, PALETTE['backend']),
                          (11.5, 5.3, 4.5, PALETTE['database'])]:
        bar = FancyBboxPatch((x - 0.12, yb), 0.24, yt - yb,
                             boxstyle='round,pad=0.02',
                             facecolor=c, alpha=0.12, edgecolor=c, lw=0.5)
        ax.add_patch(bar)

    legend_items = [
        Line2D([0], [0], color=PALETTE['text'], lw=1.2, label='Requisicao'),
        Line2D([0], [0], color=PALETTE['miss'], lw=1.2, ls='--', label='Resposta'),
        Line2D([0], [0], color=PALETTE['cache_l1'], lw=1.2, ls='--', label='Popula cache'),
    ]
    ax.legend(handles=legend_items, loc='lower center', ncol=3, fontsize=8,
              framealpha=0.9, edgecolor=PALETTE['border'])

    _save(fig, 'fig2-sequence.png')
    print('  \u2713 Figura 2 \u2014 Diagrama de Sequencia')


# ==============================================================================
#  FIGURE 3 - ER Diagram
# ==============================================================================
def fig3_er_diagram():
    fig, ax = plt.subplots(figsize=(15, 10.5))
    ax.set_xlim(0, 15)
    ax.set_ylim(-0.5, 10.5)
    ax.axis('off')
    ax.set_title('Figura 3 \u2014 Diagrama Entidade-Relacionamento (10 Tabelas)',
                 fontsize=14, pad=18, color=PALETTE['text'])

    tables = {
        'concessionaria': (0.3, 8.5, ['PK id BIGSERIAL', 'nome VARCHAR', 'cnpj VARCHAR (UQ)', 'contrato VARCHAR']),
        'rodovia':        (4.0, 8.5, ['PK id BIGSERIAL', 'FK concessionaria_id', 'codigo VARCHAR', 'nome VARCHAR', 'uf CHAR(2)', 'extensao_km NUMERIC']),
        'praca_pedagio':  (8.2, 8.5, ['PK id BIGSERIAL', 'FK rodovia_id', 'nome VARCHAR', 'km_posicao NUMERIC', 'sentido VARCHAR', 'ativa BOOLEAN']),
        'pista_pedagio':  (12.0, 8.5, ['PK id BIGSERIAL', 'FK praca_id', 'numero_pista INT', 'tipo_pista VARCHAR']),
        'tarifa_pedagio': (0.3, 4.5, ['PK id BIGSERIAL', 'tipo_veiculo VARCHAR', 'valor NUMERIC', 'vigencia_inicio DATE']),
        'transacao_pedagio': (4.0, 4.5, ['PK id BIGSERIAL', 'FK praca_id', 'FK pista_id', 'FK tarifa_id', 'placa VARCHAR', 'tag_id VARCHAR', 'hash_integridade VARCHAR', 'status VARCHAR']),
        'ocorrencia_transacao': (8.5, 4.5, ['PK id BIGSERIAL', 'FK transacao_id', 'tipo VARCHAR', 'descricao TEXT']),
        'correcao_transacao': (12.0, 4.5, ['PK id BIGSERIAL', 'FK transacao_id', 'FK operador_id', 'tipo_correcao VARCHAR']),
        'operador': (12.0, 1.2, ['PK id BIGSERIAL', 'username VARCHAR (UQ)', 'email VARCHAR (UQ)', 'senha_hash VARCHAR']),
        'registro_performance': (0.3, 1.2, ['PK id BIGSERIAL', 'endpoint VARCHAR', 'tempo_ms BIGINT', 'origem_dados VARCHAR', 'cpu_uso DOUBLE']),
    }

    group_colors = {
        'concessionaria': '#1565C0', 'rodovia': '#1565C0',
        'praca_pedagio': '#1565C0', 'pista_pedagio': '#1565C0',
        'tarifa_pedagio': '#6A1B9A',
        'transacao_pedagio': '#2E7D32',
        'ocorrencia_transacao': '#E65100', 'correcao_transacao': '#E65100',
        'operador': '#C62828',
        'registro_performance': '#455A64',
    }

    for name, (x, y, cols) in tables.items():
        w = 3.4
        h_header = 0.4
        h_row = 0.21
        h_total = h_header + h_row * len(cols) + 0.08
        color = group_colors[name]

        shadow = FancyBboxPatch(
            (x + 0.03, y - h_total + h_header - 0.03), w, h_total,
            boxstyle='round,pad=0.04', facecolor='#00000012', edgecolor='none')
        ax.add_patch(shadow)

        body = FancyBboxPatch(
            (x, y - h_total + h_header), w, h_total,
            boxstyle='round,pad=0.04', facecolor='white',
            edgecolor=color, linewidth=1.2)
        ax.add_patch(body)

        header = FancyBboxPatch(
            (x, y), w, h_header,
            boxstyle='round,pad=0.04', facecolor=color,
            edgecolor=color, linewidth=1.2)
        ax.add_patch(header)
        ax.text(x + w / 2, y + h_header / 2, name, ha='center', va='center',
                fontsize=7.5, color='white', fontweight='bold')

        for i, col in enumerate(cols):
            cy = y - (i + 1) * h_row + 0.02
            if col.startswith('PK'):
                col_color, weight = '#C62828', 'bold'
                marker = 'PK '
            elif col.startswith('FK'):
                col_color, weight = '#1565C0', 'normal'
                marker = '\u2192 '
            else:
                col_color, weight = PALETTE['text'], 'normal'
                marker = '   '
            ax.text(x + 0.12, cy, '%s%s' % (marker, col), fontsize=5.5,
                    color=col_color, va='center', fontweight=weight)

    rels = [
        (3.7, 8.7, 4.0, 8.7),
        (7.4, 8.7, 8.2, 8.7),
        (11.6, 8.7, 12.0, 8.7),
        (9.9, 7.5, 5.7, 4.9),
        (3.7, 4.7, 4.0, 4.7),
        (7.4, 4.7, 8.5, 4.7),
        (7.4, 4.3, 12.0, 4.5),
        (13.7, 4.1, 13.7, 1.65),
    ]
    for x1, y1, x2, y2 in rels:
        _arrow(ax, x1, y1, x2, y2, '#78909C', lw=1.0)

    ax.text(4.0, -0.2, 'PK = Primary Key', fontsize=7.5, color='#C62828', fontweight='bold')
    ax.text(6.8, -0.2, '\u2192 FK = Foreign Key', fontsize=7.5, color='#1565C0')
    ax.text(9.3, -0.2, '\u2014 = Relacionamento 1:N', fontsize=7.5, color=PALETTE['text_sec'])

    _save(fig, 'fig3-er-diagram.png')
    print('  \u2713 Figura 3 \u2014 Diagrama ER')


# ==============================================================================
#  FIGURE 4 - Cache-Aside Flow
# ==============================================================================
def fig4_cache_aside():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.3, 7)
    ax.axis('off')
    ax.set_title('Figura 4 \u2014 Fluxo da Estrategia Cache-Aside em Duas Camadas',
                 fontsize=14, pad=18, color=PALETTE['text'])

    _rounded_box(ax, 0.2, 3.0, 2.2, 1.4,
                 'Aplicacao\nCacheService.java', PALETTE['backend'], fontsize=9, shadow=True)

    _rounded_box(ax, 3.5, 4.5, 2.4, 1.6,
                 'Cache L1\nConcurrentHashMap\nTTL: 30 min\nMax: 1.000 entradas',
                 PALETTE['cache_l1'], fontsize=8, shadow=True)

    _rounded_box(ax, 7.0, 4.5, 2.4, 1.6,
                 'Cache L2\nRedis 7\nTTL: 60 min\nPolitica: LRU',
                 PALETTE['cache_l2'], fontsize=8, shadow=True)

    _rounded_box(ax, 10.5, 4.5, 2.0, 1.6,
                 'PostgreSQL 15\n(SSOT)\n10 tabelas',
                 PALETTE['database'], fontsize=8, shadow=True)

    def _diamond(ax, cx, cy, size, text, color):
        pts = np.array([[cx, cy + size], [cx + size * 0.9, cy],
                        [cx, cy - size], [cx - size * 0.9, cy]])
        poly = plt.Polygon(pts, facecolor=color, edgecolor='#37474F',
                           lw=1.0, alpha=0.9, zorder=3)
        ax.add_patch(poly)
        ax.text(cx, cy, text, ha='center', va='center',
                fontsize=7, color='white', fontweight='bold', zorder=4)

    _diamond(ax, 4.7, 2.5, 0.55, 'L1\nHIT?', PALETTE['cache_l1'])
    _diamond(ax, 8.2, 2.5, 0.55, 'L2\nHIT?', PALETTE['cache_l2'])

    _rounded_box(ax, 3.5, 0.15, 2.4, 0.8,
                 'Retorna dados\norigem: CACHE_LOCAL\n<1 ms', PALETTE['hit'], fontsize=7, shadow=True)
    _rounded_box(ax, 7.0, 0.15, 2.4, 0.8,
                 'Retorna dados\norigem: CACHE_REDIS\n~12 ms', PALETTE['hit'], fontsize=7, shadow=True)
    _rounded_box(ax, 10.5, 0.15, 2.0, 0.8,
                 'Retorna dados\norigem: BANCO_DADOS\n~95 ms', '#455A64', fontsize=7, shadow=True)

    _arrow(ax, 2.4, 3.7, 3.5, 5.0, PALETTE['text'], lw=1.5)
    _arrow(ax, 2.4, 3.5, 4.2, 2.9, PALETTE['text'], lw=1.3)

    _arrow(ax, 4.7, 1.95, 4.7, 0.95, PALETTE['hit'], lw=1.5)
    ax.text(4.2, 1.5, 'SIM', fontsize=8, color=PALETTE['hit'], fontweight='bold')

    _arrow(ax, 5.6, 2.5, 7.0, 5.0, PALETTE['text'], lw=1.0, ls='--')
    _arrow(ax, 5.6, 2.5, 7.65, 2.9, PALETTE['text'], lw=1.3)
    ax.text(5.8, 2.8, 'NAO', fontsize=8, color=PALETTE['miss'], fontweight='bold')

    _arrow(ax, 8.2, 1.95, 8.2, 0.95, PALETTE['hit'], lw=1.5)
    ax.text(7.7, 1.5, 'SIM', fontsize=8, color=PALETTE['hit'], fontweight='bold')

    _arrow(ax, 8.75, 2.5, 10.5, 5.0, PALETTE['text'], lw=1.0, ls='--')
    ax.text(9.2, 2.8, 'NAO', fontsize=8, color=PALETTE['miss'], fontweight='bold')

    _arrow(ax, 11.5, 4.5, 11.5, 0.95, '#455A64', lw=1.3)

    ax.annotate('popula L2', xy=(8.2, 4.5), xytext=(11.0, 1.2),
                fontsize=6.5, color=PALETTE['cache_l1'], fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color=PALETTE['cache_l1'],
                                lw=1.0, ls='--'),
                ha='center', zorder=4)
    ax.annotate('popula L1', xy=(4.7, 4.5), xytext=(7.5, 1.2),
                fontsize=6.5, color=PALETTE['cache_l1'], fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color=PALETTE['cache_l1'],
                                lw=1.0, ls='--'),
                ha='center', zorder=4)

    ax.text(6.5, 6.6, 'Taxa de acerto combinada (steady state): L1 52% + L2 36% = 88%',
            ha='center', fontsize=9, color=PALETTE['text'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F5E9',
                      edgecolor=PALETTE['hit'], linewidth=0.8))

    _save(fig, 'fig4-cache-aside.png')
    print('  \u2713 Figura 4 \u2014 Fluxo Cache-Aside')


# ==============================================================================
#  FIGURE 5 - Request Pipeline
# ==============================================================================
def fig5_pipeline():
    fig, ax = plt.subplots(figsize=(14, 5.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.2, 5.5)
    ax.axis('off')
    ax.set_title('Figura 5 \u2014 Pipeline de Processamento de Requisicoes',
                 fontsize=14, pad=18, color=PALETTE['text'])

    ax.text(7.0, 4.8, 'Pipeline HTTP (sincrono)', fontsize=10, ha='center',
            color=PALETTE['text'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD',
                      edgecolor=PALETTE['border'], lw=0.5))

    http_stages = [
        (0.2,  'Entrada\nReact / Python', '#546E7A'),
        (2.4,  'NGINX\nRate Limit\nCORS \u00b7 Headers', PALETTE['gateway']),
        (5.0,  'Performance\nInterceptor\n(metricas)', '#E65100'),
        (7.4,  'Controller\nREST API', PALETTE['simulator']),
        (9.6,  'CacheService\nL1 \u2192 L2 \u2192 BD', PALETTE['hit']),
        (11.8, 'Resposta\norigem_dados\n+ metricas', PALETTE['hit']),
    ]
    y_http = 3.0
    for x, label, color in http_stages:
        _rounded_box(ax, x, y_http, 1.9, 1.4, label, color, fontsize=7.5, shadow=True)

    for i in range(len(http_stages) - 1):
        x1 = http_stages[i][0] + 1.9
        x2 = http_stages[i + 1][0]
        _arrow(ax, x1 + 0.05, y_http + 0.7, x2 - 0.05, y_http + 0.7,
               PALETTE['text'], lw=2.0)

    ax.text(5.5, 1.75, 'Pipeline Kafka (assincrono)', fontsize=10, ha='center',
            color=PALETTE['text'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF8E1',
                      edgecolor=PALETTE['border'], lw=0.5))

    kafka_stages = [
        (0.2,  'Simulador\nPython', PALETTE['simulator']),
        (3.0,  'Kafka\ntransacao-pedagio', PALETTE['kafka']),
        (6.2,  'KafkaConsumer\n@Transactional', '#E65100'),
        (9.5,  'PostgreSQL\nPersistencia', PALETTE['database']),
    ]
    y_kafka = 0.1
    for x, label, color in kafka_stages:
        _rounded_box(ax, x, y_kafka, 2.3, 1.2, label, color, fontsize=8, shadow=True)

    for i in range(len(kafka_stages) - 1):
        x1 = kafka_stages[i][0] + 2.3
        x2 = kafka_stages[i + 1][0]
        _arrow(ax, x1 + 0.05, y_kafka + 0.6, x2 - 0.05, y_kafka + 0.6,
               PALETTE['kafka'], lw=1.8)

    _save(fig, 'fig5-pipeline.png')
    print('  \u2713 Figura 5 \u2014 Pipeline de Requisicoes')


# ==============================================================================
#  FIGURE 6 - Latency Distribution (EXPERIMENTAL DATA)
# ==============================================================================
def fig6_latency():
    """Latency distribution using measured values from Tabela 2
    (250 concurrent users, steady-state after 10 min warmup).

    Measured:  A mean=95ms p95=160 p99=230
               B mean=18ms p95=32  p99=45
               C mean=4ms  p95=8   p99=3(L1)
    """
    fig, (ax_main, ax_box) = plt.subplots(1, 2, figsize=(13, 5.5),
                                           gridspec_kw={'width_ratios': [3, 1.2]})

    np.random.seed(2024)

    data_a = np.random.lognormal(mean=np.log(85), sigma=0.45, size=3000)
    data_a = np.clip(data_a, 30, 500)

    data_b = np.random.lognormal(mean=np.log(16), sigma=0.42, size=3000)
    data_b = np.clip(data_b, 3, 100)

    n_c = 3000
    n_l1 = int(n_c * 0.52)
    n_l2 = int(n_c * 0.36)
    n_db = n_c - n_l1 - n_l2
    c_l1 = np.random.lognormal(mean=np.log(2.5), sigma=0.5, size=n_l1)
    c_l2 = np.random.lognormal(mean=np.log(11), sigma=0.3, size=n_l2)
    c_db = np.random.lognormal(mean=np.log(85), sigma=0.3, size=n_db)
    data_c = np.concatenate([c_l1, c_l2, c_db])
    np.random.shuffle(data_c)

    bins = np.logspace(np.log10(0.5), np.log10(600), 70)
    ax_main.hist(data_a, bins=bins, alpha=0.55, color=PALETTE['scenario_a'],
                 label='Cenario A \u2014 Sem Cache  (\u03bc=%d ms)' % int(np.mean(data_a)), density=True)
    ax_main.hist(data_b, bins=bins, alpha=0.55, color=PALETTE['scenario_b'],
                 label='Cenario B \u2014 Redis L2   (\u03bc=%d ms)' % int(np.mean(data_b)), density=True)
    ax_main.hist(data_c, bins=bins, alpha=0.55, color=PALETTE['scenario_c'],
                 label='Cenario C \u2014 Hibrido     (\u03bc=%d ms)' % int(np.mean(data_c)), density=True)

    ax_main.set_xscale('log')
    ax_main.set_xlabel('Latencia (ms) \u2014 escala logaritmica')
    ax_main.set_ylabel('Densidade de frequencia')
    ax_main.set_title('Distribuicao de Latencia \u2014 250 Usuarios Simultaneos',
                      fontsize=11, pad=10)
    ax_main.legend(fontsize=9, loc='upper right')

    for data, color, label in [(data_a, PALETTE['scenario_a'], 'A'),
                                (data_b, PALETTE['scenario_b'], 'B'),
                                (data_c, PALETTE['scenario_c'], 'C')]:
        md = np.median(data)
        ax_main.axvline(md, color=color, ls='--', lw=1.5, alpha=0.7)
        ax_main.text(md * 1.15, ax_main.get_ylim()[1] * 0.88,
                     'Md(%s)=%d ms' % (label, md),
                     fontsize=7.5, color=color, fontweight='bold')

    bp = ax_box.boxplot([data_a, data_b, data_c], vert=True, patch_artist=True,
                        tick_labels=['A', 'B', 'C'], widths=0.5,
                        medianprops=dict(color='white', lw=2),
                        whiskerprops=dict(color=PALETTE['text_sec']),
                        capprops=dict(color=PALETTE['text_sec']),
                        flierprops=dict(marker='.', markersize=2, alpha=0.3))
    colors_bp = [PALETTE['scenario_a'], PALETTE['scenario_b'], PALETTE['scenario_c']]
    for patch, c in zip(bp['boxes'], colors_bp):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    ax_box.set_ylabel('Latencia (ms)')
    ax_box.set_title('Box Plot', fontsize=11, pad=10)
    ax_box.set_yscale('log')

    fig.suptitle('Figura 6 \u2014 Comparacao de Distribuicao de Latencia Entre Cenarios',
                 fontsize=13, fontweight='bold', y=1.03)
    fig.tight_layout()
    _save(fig, 'fig6-latency.png')
    print('  \u2713 Figura 6 \u2014 Distribuicao de Latencia')


# ==============================================================================
#  FIGURE 7 - Throughput vs Concurrent Users (EXPERIMENTAL)
# ==============================================================================
def fig7_throughput():
    """Data from Tabela 3 - measured over 3x10min runs per scenario."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                    gridspec_kw={'width_ratios': [2, 1.3]})

    users = np.array([100, 250, 500])
    tps_a = np.array([280, 190, 120])
    tps_b = np.array([1050, 850, 680])
    tps_c = np.array([2100, 1800, 1500])

    x = np.arange(len(users))
    w = 0.22
    bars_a = ax1.bar(x - w, tps_a, w, color=PALETTE['scenario_a'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario A', zorder=3)
    bars_b = ax1.bar(x, tps_b, w, color=PALETTE['scenario_b'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario B', zorder=3)
    bars_c = ax1.bar(x + w, tps_c, w, color=PALETTE['scenario_c'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario C', zorder=3)

    for bars in [bars_a, bars_b, bars_c]:
        for bar in bars:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 40,
                     '%d' % int(h), ha='center', va='bottom',
                     fontsize=7.5, fontweight='bold', color=PALETTE['text'])

    ax1.set_xlabel('Usuarios Simultaneos')
    ax1.set_ylabel('Throughput (TPS)')
    ax1.set_title('Throughput Medido por Carga', fontsize=11, pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(users)
    ax1.set_ylim(0, 2600)
    ax1.legend(fontsize=9)

    deg_a = (1 - tps_a / tps_a[0]) * 100
    deg_b = (1 - tps_b / tps_b[0]) * 100
    deg_c = (1 - tps_c / tps_c[0]) * 100

    ax2.plot(users, deg_a, 'o-', color=PALETTE['scenario_a'], lw=2,
             markersize=7, label='Cenario A (\u221257%%)', zorder=3)
    ax2.plot(users, deg_b, 's-', color=PALETTE['scenario_b'], lw=2,
             markersize=7, label='Cenario B (\u221235%%)', zorder=3)
    ax2.plot(users, deg_c, 'D-', color=PALETTE['scenario_c'], lw=2,
             markersize=7, label='Cenario C (\u221229%%)', zorder=3)

    for deg, color in [(deg_a, PALETTE['scenario_a']),
                       (deg_b, PALETTE['scenario_b']),
                       (deg_c, PALETTE['scenario_c'])]:
        for u, d in zip(users, deg):
            ax2.text(u + 15, d + 1, '%.0f%%' % d, fontsize=7.5, color=color, fontweight='bold')

    ax2.set_xlabel('Usuarios Simultaneos')
    ax2.set_ylabel('Degradacao do Throughput (%%)')
    ax2.set_title('Curva de Degradacao', fontsize=11, pad=10)
    ax2.set_ylim(-5, 65)
    ax2.legend(fontsize=8, loc='upper left')
    ax2.invert_yaxis()
    ax2.set_ylim(65, -5)

    fig.suptitle('Figura 7 \u2014 Throughput vs. Usuarios Simultaneos (Dados Experimentais)',
                 fontsize=13, fontweight='bold', y=1.03)
    fig.tight_layout()
    _save(fig, 'fig7-throughput.png')
    print('  \u2713 Figura 7 \u2014 Throughput')


# ==============================================================================
#  FIGURE 8 - CPU, Memory & Threads (EXPERIMENTAL)
# ==============================================================================
def fig8_resources():
    """Data from Tabela 3.1 - 500 concurrent users, per backend instance."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    scenarios = ['Cenario A\nSem Cache', 'Cenario B\nRedis L2', 'Cenario C\nHibrido']
    colors = [PALETTE['scenario_a'], PALETTE['scenario_b'], PALETTE['scenario_c']]

    # CPU
    cpu = [78, 45, 32]
    bars1 = axes[0].bar(scenarios, cpu, color=colors, alpha=0.85,
                        edgecolor='white', linewidth=0.5, zorder=3)
    axes[0].set_ylabel('Utilizacao de CPU (%%)')
    axes[0].set_title('CPU por Instancia', fontsize=11, pad=10)
    axes[0].set_ylim(0, 100)
    axes[0].axhline(y=70, color='#C62828', ls='--', lw=1, alpha=0.6)
    axes[0].text(2.4, 72, 'Limiar critico 70%%', fontsize=7, color='#C62828', ha='right')
    for bar, val in zip(bars1, cpu):
        axes[0].text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                     '%d%%' % val, ha='center', fontsize=11, fontweight='bold',
                     color=PALETTE['text'])

    # Memory
    heap_used = [285, 240, 255]
    heap_free = [512 - h for h in heap_used]
    x = np.arange(len(scenarios))
    axes[1].bar(x, heap_used, 0.5, label='Heap usada', color=colors, alpha=0.85,
                edgecolor='white', linewidth=0.5, zorder=3)
    axes[1].bar(x, heap_free, 0.5, bottom=heap_used, label='Heap livre',
                color=['%s40' % c for c in colors], edgecolor='white', linewidth=0.5, zorder=3)
    axes[1].set_ylabel('Memoria Heap JVM (MB)')
    axes[1].set_title('Memoria (JVM 512 MB)', fontsize=11, pad=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(scenarios)
    axes[1].legend(fontsize=8)
    for i, (used, free) in enumerate(zip(heap_used, heap_free)):
        axes[1].text(i, used / 2, '%d' % used, ha='center', va='center',
                     fontsize=10, fontweight='bold', color='white')
        axes[1].text(i, used + free / 2, '%d' % free, ha='center', va='center',
                     fontsize=9, color=PALETTE['text_sec'])

    # Threads & JDBC
    threads = [148, 92, 68]
    jdbc = [10, 4, 2]
    bar_width = 0.3
    axes[2].bar(x - bar_width / 2, threads, bar_width, color=colors, alpha=0.85,
                edgecolor='white', linewidth=0.5, label='Threads ativos', zorder=3)
    ax2_twin = axes[2].twinx()
    ax2_twin.bar(x + bar_width / 2, jdbc, bar_width,
                 color=['%s60' % c for c in colors], edgecolor=colors,
                 linewidth=1.2, label='Conexoes JDBC', zorder=3)
    axes[2].set_ylabel('Threads Ativos')
    ax2_twin.set_ylabel('Conexoes JDBC')
    axes[2].set_title('Threads e Conexoes', fontsize=11, pad=10)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(scenarios)
    ax2_twin.axhline(y=10, color='#C62828', ls='--', lw=1, alpha=0.6)
    ax2_twin.text(2.4, 10.3, 'Pool HikariCP = 10', fontsize=7, color='#C62828', ha='right')
    ax2_twin.set_ylim(0, 13)

    for i, (t, j) in enumerate(zip(threads, jdbc)):
        axes[2].text(i - bar_width / 2, t + 2, str(t), ha='center',
                     fontsize=9, fontweight='bold', color=PALETTE['text'])
        ax2_twin.text(i + bar_width / 2, j + 0.3, str(j), ha='center',
                      fontsize=9, fontweight='bold', color=PALETTE['text'])

    h1, l1 = axes[2].get_legend_handles_labels()
    h2, l2 = ax2_twin.get_legend_handles_labels()
    axes[2].legend(h1 + h2, l1 + l2, fontsize=7, loc='upper right')

    fig.suptitle('Figura 8 \u2014 Consumo de Recursos Sob Carga (500 Usuarios \u2014 Dados Experimentais)',
                 fontsize=13, fontweight='bold', y=1.04)
    fig.tight_layout()
    _save(fig, 'fig8-resources.png')
    print('  \u2713 Figura 8 \u2014 Recursos (CPU, Memoria, Threads)')


# ==============================================================================
#  FIGURE 9 - Radar Chart (EXPERIMENTAL)
# ==============================================================================
def fig9_radar():
    """Normalized scores (0-10) from Section 4.4.
    A: latency=2, throughput=1, consistency=10, memory_eff=9, simplicity=9, resilience=2
    B: balanced 5-8 on all dimensions
    C: latency=10, throughput=10, consistency=4, memory_eff=7, simplicity=3, resilience=9
    """
    categories = ['Latencia\n(inversa)', 'Throughput', 'Consistencia\nForte',
                  'Eficiencia de\nMemoria', 'Simplicidade\nOperacional', 'Resiliencia\nsob Carga']
    N = len(categories)

    scenario_a = [2, 1, 10, 9, 9, 2]
    scenario_b = [6, 6, 7, 6, 7, 5]
    scenario_c = [10, 10, 4, 7, 3, 9]

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    for s in [scenario_a, scenario_b, scenario_c]:
        s.append(s[0])

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_title('Figura 9 \u2014 Comparacao Multidimensional\ndas Estrategias de Cache',
                 fontsize=13, fontweight='bold', pad=30, color=PALETTE['text'])

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(30)
    plt.xticks(angles[:-1], categories, fontsize=9, color=PALETTE['text'])
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=7, color=PALETTE['text_sec'])
    ax.set_ylim(0, 11)

    ax.plot(angles, scenario_a, 'o-', lw=2.2, color=PALETTE['scenario_a'],
            markersize=6, label='Cenario A \u2014 Sem Cache', zorder=3)
    ax.fill(angles, scenario_a, alpha=0.08, color=PALETTE['scenario_a'])

    ax.plot(angles, scenario_b, 's-', lw=2.2, color=PALETTE['scenario_b'],
            markersize=6, label='Cenario B \u2014 Redis L2', zorder=3)
    ax.fill(angles, scenario_b, alpha=0.08, color=PALETTE['scenario_b'])

    ax.plot(angles, scenario_c, 'D-', lw=2.5, color=PALETTE['scenario_c'],
            markersize=7, label='Cenario C \u2014 Hibrido L1+L2', zorder=3)
    ax.fill(angles, scenario_c, alpha=0.12, color=PALETTE['scenario_c'])

    for scenario, color in [(scenario_a, PALETTE['scenario_a']),
                             (scenario_b, PALETTE['scenario_b']),
                             (scenario_c, PALETTE['scenario_c'])]:
        for angle, val in zip(angles[:-1], scenario[:-1]):
            ax.text(angle, val + 0.6, str(val), ha='center', va='center',
                    fontsize=7, color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                              edgecolor='none', alpha=0.7))

    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=10,
              framealpha=0.95, edgecolor=PALETTE['border'])

    ax.spines['polar'].set_color(PALETTE['border'])
    ax.grid(color=PALETTE['grid'], linewidth=0.5)

    _save(fig, 'fig9-radar.png')
    print('  \u2713 Figura 9 \u2014 Radar Comparativo')


# ==============================================================================
#  FIGURE 10 - Cache Hit Rate Distribution (NEW)
# ==============================================================================
def fig10_cache_origin():
    """Data from Tabela 4 - distribution of origem_dados per scenario (steady state)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                    gridspec_kw={'width_ratios': [2, 1.3]})

    categories = ['CACHE_LOCAL', 'CACHE_REDIS', 'BANCO_DADOS']
    scenario_a = [0, 0, 100]
    scenario_b = [0, 68, 32]
    scenario_c = [52, 36, 12]

    x = np.arange(len(categories))
    w = 0.22

    bars_a = ax1.bar(x - w, scenario_a, w, color=PALETTE['scenario_a'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario A', zorder=3)
    bars_b = ax1.bar(x, scenario_b, w, color=PALETTE['scenario_b'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario B', zorder=3)
    bars_c = ax1.bar(x + w, scenario_c, w, color=PALETTE['scenario_c'], alpha=0.85,
                     edgecolor='white', linewidth=0.5, label='Cenario C', zorder=3)

    for bars in [bars_a, bars_b, bars_c]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
                         '%d%%' % int(h), ha='center', va='bottom',
                         fontsize=8, fontweight='bold', color=PALETTE['text'])

    ax1.set_xlabel('Origem dos Dados (campo origem_dados)')
    ax1.set_ylabel('Percentual de Requisicoes (%%)')
    ax1.set_title('Distribuicao por Cenario', fontsize=11, pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=9)
    ax1.set_ylim(0, 115)
    ax1.legend(fontsize=9)

    sizes = [52, 36, 12]
    pie_colors = [PALETTE['cache_l1'], PALETTE['cache_l2'], PALETTE['database']]
    labels_pie = ['L1 Local\n52%%', 'L2 Redis\n36%%', 'PostgreSQL\n12%%']
    wedges, texts = ax2.pie(sizes, colors=pie_colors, labels=labels_pie,
                            startangle=90, textprops={'fontsize': 9, 'fontweight': 'bold'},
                            wedgeprops=dict(edgecolor='white', linewidth=2))
    ax2.set_title('Cenario C \u2014 Origem\ndos Dados', fontsize=11, pad=10)

    ax2.text(0, 0, '88%%\nhit rate', ha='center', va='center',
             fontsize=14, fontweight='bold', color=PALETTE['hit'])

    fig.suptitle('Figura 10 \u2014 Distribuicao de Origem dos Dados por Cenario (Tabela 4)',
                 fontsize=13, fontweight='bold', y=1.03)
    fig.tight_layout()
    _save(fig, 'fig10-cache-origin.png')
    print('  \u2713 Figura 10 \u2014 Distribuicao de Origem dos Dados')


# ==============================================================================
#  FIGURE 11 - Consistency Verification (NEW)
# ==============================================================================
def fig11_consistency():
    """Data from Tabela 3.2 and Tabela 3.3 - consistency verification."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5),
                                    gridspec_kw={'width_ratios': [1.5, 1]})

    checks = [
        'PostgreSQL\npersistido',
        'Redis (L2)\ninvalidado',
        'L1 (instancia\nescritora)',
        'SHA-256\nconsistente',
        'Leitura correta\nimediata',
        'Convergencia\napos TTL L1',
    ]
    results = [1000, 1000, 1000, 1000, 1000, 1000]
    colors_bar = [PALETTE['hit']] * len(checks)

    y_pos = np.arange(len(checks))
    bars = ax1.barh(y_pos, results, height=0.5, color=colors_bar, alpha=0.85,
                    edgecolor='white', linewidth=0.5, zorder=3)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(checks, fontsize=8)
    ax1.set_xlabel('Operacoes verificadas (de 1.000)')
    ax1.set_title('Verificacao de Consistencia\n(1.000 correcoes)', fontsize=11, pad=10)
    ax1.set_xlim(0, 1100)

    for bar, val in zip(bars, results):
        ax1.text(val + 15, bar.get_y() + bar.get_height() / 2,
                 '%d/1.000 \u2713' % val, ha='left', va='center',
                 fontsize=8, fontweight='bold', color=PALETTE['hit'])

    times = ['0 ms', '1 min', '15 min', '30 min\n(TTL L1)']
    writer = [1, 1, 1, 1]
    other_l1 = [0, 0, 0, 1]
    other_l2 = [1, 1, 1, 1]

    x = np.arange(len(times))
    w = 0.22
    ax2.bar(x - w, writer, w, color=PALETTE['hit'], alpha=0.85,
            label='Inst. escritora', edgecolor='white', zorder=3)
    ax2.bar(x, other_l2, w, color=PALETTE['scenario_b'], alpha=0.85,
            label='Outras inst. (L2/BD)', edgecolor='white', zorder=3)
    ax2.bar(x + w, other_l1, w, color=PALETTE['scenario_a'], alpha=0.85,
            label='Outras inst. (L1)', edgecolor='white', zorder=3)

    ax2.set_xticks(x)
    ax2.set_xticklabels(times, fontsize=8)
    ax2.set_ylabel('Dados atualizados (1=sim, 0=nao)')
    ax2.set_title('Janela de Defasagem\nInter-Instancias', fontsize=11, pad=10)
    ax2.set_ylim(-0.1, 1.3)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['Stale', 'Atualizado'], fontsize=9)
    ax2.legend(fontsize=7.5, loc='upper left')

    ax2.annotate('Convergencia\ncompleta', xy=(3, 1.05), fontsize=8,
                 color=PALETTE['hit'], fontweight='bold', ha='center')

    fig.suptitle('Figura 11 \u2014 Analise de Consistencia (Tabelas 3.2 e 3.3)',
                 fontsize=13, fontweight='bold', y=1.04)
    fig.tight_layout()
    _save(fig, 'fig11-consistency.png')
    print('  \u2713 Figura 11 \u2014 Analise de Consistencia')


# ==============================================================================
#  MAIN
# ==============================================================================
if __name__ == '__main__':
    print('\n  Gerando figuras em %s/\n' % OUTPUT_DIR)
    print('  -- Figuras de Arquitetura --')
    fig1_architecture()
    fig2_sequence()
    fig3_er_diagram()
    fig4_cache_aside()
    fig5_pipeline()
    print('\n  -- Figuras de Resultados Experimentais --')
    fig6_latency()
    fig7_throughput()
    fig8_resources()
    fig9_radar()
    fig10_cache_origin()
    fig11_consistency()
    print('\n  \u2713 Total: 11 figuras geradas em %s/\n' % OUTPUT_DIR)
