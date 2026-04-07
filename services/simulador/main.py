# main.py
#!/usr/bin/env python3
"""
Simulador de Transações de Pedágio

Este simulador gera transações de veículos passando por pedágios e envia
para um broker Kafka. Algumas transações são geradas com erros propositalmente
para testar o sistema de correções.

Uso:
    python main.py [opções]

Opções:
    --duration SEGUNDOS     Duração da simulação em segundos
    --count NUMERO          Número total de transações a gerar
    --rate TPS              Taxa de transações por segundo (padrão: 10)
    --error-rate PERCENTUAL Taxa de erro (0.0 a 1.0, padrão: 0.15)
    --stress                Modo stress test (taxa alta de transações)
"""

import argparse
import sys
from simulator import PedagioSimulator
from config import Config

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Simulador de Transações de Pedágio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Duração da simulação em segundos'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        help='Número total de transações a gerar'
    )
    
    parser.add_argument(
        '--rate',
        type=int,
        help='Taxa de transações por segundo (padrão: 10)'
    )
    
    parser.add_argument(
        '--error-rate',
        type=float,
        help='Taxa de erro de 0.0 a 1.0 (padrão: 0.15)'
    )
    
    parser.add_argument(
        '--stress',
        action='store_true',
        help='Modo stress test (1000 transações/segundo)'
    )
    
    return parser.parse_args()

def main():
    """Função principal"""
    args = parse_args()
    
    # Atualiza configurações se fornecidas
    config = Config()
    
    if args.rate:
        config.SIMULATION_RATE = args.rate
    
    if args.error_rate is not None:
        if 0.0 <= args.error_rate <= 1.0:
            config.ERROR_RATE = args.error_rate
        else:
            print("Erro: --error-rate deve estar entre 0.0 e 1.0")
            sys.exit(1)
    
    if args.stress:
        config.SIMULATION_RATE = 1000
        print("Modo STRESS TEST ativado: 1000 transações/segundo")
    
    # Cria e executa o simulador
    simulator = PedagioSimulator()
    
    try:
        simulator.executar(
            duracao_segundos=args.duration,
            total_transacoes=args.count
        )
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()