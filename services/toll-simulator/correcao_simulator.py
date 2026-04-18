#!/usr/bin/env python3
"""
Simulador de Correções de Transações de Pedágio
Busca transações com ocorrência pendente via API REST e aplica correções automáticas.
"""

import time
import random
import logging
import argparse
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração padrão
API_BASE_URL = 'http://localhost:80/api'
OPERADOR_ID = 1
INTERVALO_SEGUNDOS = 2.0

# Tarifas corretas por tipo de veículo (devem refletir config do simulador de transações)
TARIFAS_CORRETAS = {
    'MOTO': 5.00,
    'CARRO': 10.00,
    'CAMINHAO': 20.00,
}

# Motivos de correção mapeados por tipo de ocorrência
MOTIVOS_CORRECAO = {
    'VALOR_DIVERGENTE': 'Valor divergente corrigido para tarifa vigente do tipo de veículo.',
    'PLACA_INVALIDA': 'Placa corrigida após verificação no sistema de câmeras.',
    'TAG_DUPLICADA': 'Tag duplicada resolvida após conferência de registros.',
    'HORARIO_INCONSISTENTE': 'Horário ajustado com base no log do sensor da pista.',
    'DEFAULT': 'Correção automática aplicada pelo simulador.',
}


def buscar_ocorrencias_pendentes(base_url, limite=50):
    """Busca transações com status OCORRENCIA que ainda não foram corrigidas."""
    url = f'{base_url}/transacoes/ocorrencias/pendentes'
    params = {'limite': limite, 'horas': 720}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f'Erro ao buscar ocorrências pendentes: {e}')
        return []


def determinar_motivo(transacao):
    """Determina o motivo da correção com base nas ocorrências da transação."""
    ocorrencias = transacao.get('ocorrencias') or []
    if ocorrencias:
        tipo = ocorrencias[0].get('tipoOcorrencia', '')
        return MOTIVOS_CORRECAO.get(tipo, MOTIVOS_CORRECAO['DEFAULT'])
    return MOTIVOS_CORRECAO['DEFAULT']


def calcular_valor_corrigido(transacao):
    """Calcula o valor correto com base no tipo de veículo."""
    tipo_veiculo = transacao.get('tipoVeiculo', 'CARRO')
    return TARIFAS_CORRETAS.get(tipo_veiculo, 10.00)


def aplicar_correcao(base_url, transacao_id, operador_id, motivo, valor_corrigido):
    """Envia POST para criar a correção de uma transação."""
    url = f'{base_url}/correcoes/transacao/{transacao_id}'
    payload = {
        'operadorId': operador_id,
        'motivo': motivo,
        'valorCorrigido': valor_corrigido,
        'tipoCorrecao': 'AUTOMATICA',
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f'Erro ao corrigir transação {transacao_id}: {e}')
        return None


def executar(base_url, operador_id, intervalo, ciclos=None):
    """Loop principal do simulador de correções."""
    logger.info('=' * 70)
    logger.info('SIMULADOR DE CORREÇÕES DE PEDÁGIO')
    logger.info(f'API: {base_url}')
    logger.info(f'Operador ID: {operador_id}')
    logger.info(f'Intervalo entre correções: {intervalo}s')
    if ciclos:
        logger.info(f'Ciclos máximos: {ciclos}')
    logger.info('=' * 70)

    stats = {'total': 0, 'sucesso': 0, 'erro': 0, 'ciclos': 0}

    try:
        while True:
            if ciclos and stats['ciclos'] >= ciclos:
                break

            pendentes = buscar_ocorrencias_pendentes(base_url)
            if not pendentes:
                logger.info('Nenhuma ocorrência pendente encontrada. Aguardando...')
                time.sleep(intervalo * 5)
                stats['ciclos'] += 1
                continue

            logger.info(f'{len(pendentes)} ocorrência(s) pendente(s) encontrada(s)')

            for transacao in pendentes:
                tid = transacao.get('id')
                placa = transacao.get('placa', '?')
                valor_original = transacao.get('valorOriginal', 0)
                tipo_veiculo = transacao.get('tipoVeiculo', '?')

                motivo = determinar_motivo(transacao)
                valor_corrigido = calcular_valor_corrigido(transacao)

                logger.info(
                    f'Corrigindo transação #{tid} | placa={placa} | '
                    f'tipo={tipo_veiculo} | valor={valor_original} -> {valor_corrigido}'
                )

                resultado = aplicar_correcao(base_url, tid, operador_id, motivo, valor_corrigido)
                stats['total'] += 1

                if resultado:
                    stats['sucesso'] += 1
                    logger.info(f'  -> Correção #{resultado.get("id")} criada com sucesso')
                else:
                    stats['erro'] += 1

                time.sleep(intervalo)

            stats['ciclos'] += 1

            if stats['total'] > 0 and stats['total'] % 10 == 0:
                logger.info(
                    f'[Estatísticas] total={stats["total"]} '
                    f'sucesso={stats["sucesso"]} erro={stats["erro"]}'
                )

    except KeyboardInterrupt:
        logger.info('\nSimulação interrompida pelo usuário')

    logger.info('=' * 70)
    logger.info('RESULTADO FINAL')
    logger.info(f'Total de correções tentadas: {stats["total"]}')
    logger.info(f'Sucesso: {stats["sucesso"]}')
    logger.info(f'Erro: {stats["erro"]}')
    logger.info(f'Ciclos executados: {stats["ciclos"]}')
    logger.info('=' * 70)


def main():
    parser = argparse.ArgumentParser(description='Simulador de Correções de Transações de Pedágio')
    parser.add_argument('--url', default=API_BASE_URL, help='URL base da API (padrão: http://localhost:80/api)')
    parser.add_argument('--operador', type=int, default=OPERADOR_ID, help='ID do operador (padrão: 1)')
    parser.add_argument('--intervalo', type=float, default=INTERVALO_SEGUNDOS, help='Intervalo entre correções em segundos (padrão: 2.0)')
    parser.add_argument('--ciclos', type=int, default=None, help='Número máximo de ciclos (padrão: infinito)')
    args = parser.parse_args()

    executar(args.url, args.operador, args.intervalo, args.ciclos)


if __name__ == '__main__':
    main()
