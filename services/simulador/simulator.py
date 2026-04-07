# simulator.py
import time
import random
import logging
from datetime import datetime
from transacao_generator import TransacaoGenerator
from kafka_producer import TransacaoKafkaProducer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PedagioSimulator:
    """Simulador de transações de pedágio"""
    
    def __init__(self):
        self.config = Config()
        self.generator = TransacaoGenerator()
        self.producer = TransacaoKafkaProducer()
        self.estatisticas = {
            'total_enviadas': 0,
            'total_com_erro': 0,
            'total_ok': 0,
            'erros_envio': 0
        }
        self.parar_simulacao = False
    
    def simular_transacao(self):
        """Simula uma única transação"""
        # Decide se a transação terá erro
        com_erro = random.random() < self.config.ERROR_RATE
        
        # Gera a transação
        transacao = self.generator.gerar_transacao(com_erro=com_erro)
        
        # Envia para o Kafka
        sucesso = self.producer.enviar_transacao(
            transacao.to_dict(),
            key=transacao.placa
        )
        
        # Atualiza estatísticas
        if sucesso:
            self.estatisticas['total_enviadas'] += 1
            if com_erro:
                self.estatisticas['total_com_erro'] += 1
            else:
                self.estatisticas['total_ok'] += 1
        else:
            self.estatisticas['erros_envio'] += 1
    
    def exibir_estatisticas(self):
        """Exibe estatísticas do simulador"""
        logger.info("=" * 80)
        logger.info("ESTATÍSTICAS DA SIMULAÇÃO")
        logger.info(f"Total de transações enviadas: {self.estatisticas['total_enviadas']}")
        logger.info(f"Transações OK: {self.estatisticas['total_ok']}")
        logger.info(f"Transações com erro: {self.estatisticas['total_com_erro']}")
        logger.info(f"Erros de envio: {self.estatisticas['erros_envio']}")
        
        if self.estatisticas['total_enviadas'] > 0:
            taxa_erro = (self.estatisticas['total_com_erro'] / self.estatisticas['total_enviadas']) * 100
            logger.info(f"Taxa de erro: {taxa_erro:.2f}%")
        
        logger.info("=" * 80)
    
    def parar(self):
        """Para a simulação"""
        self.parar_simulacao = True
        logger.info("Solicitação de parada recebida...")
    
    def executar(self, duracao_segundos: int = None, total_transacoes: int = None):
        """
        Executa o simulador
        
        Args:
            duracao_segundos: Duração da simulação em segundos (None = infinito)
            total_transacoes: Total de transações a gerar (None = infinito)
        """
        logger.info("=" * 80)
        logger.info("INICIANDO SIMULADOR DE PEDÁGIO")
        logger.info(f"Taxa de simulação: {self.config.SIMULATION_RATE} transações/segundo")
        logger.info(f"Taxa de erro: {self.config.ERROR_RATE * 100}%")
        logger.info(f"Tópico Kafka: {self.config.KAFKA_TOPIC}")
        
        if duracao_segundos:
            logger.info(f"Duração: {duracao_segundos} segundos")
        if total_transacoes:
            logger.info(f"Total de transações: {total_transacoes}")
        
        logger.info("=" * 80)
        
        intervalo = 1.0 / self.config.SIMULATION_RATE
        inicio = time.time()
        
        try:
            while True:
                # Verifica condições de parada
                if self.parar_simulacao:
                    logger.info("Parando simulação...")
                    break
                if duracao_segundos and (time.time() - inicio) >= duracao_segundos:
                    break
                if total_transacoes and self.estatisticas['total_enviadas'] >= total_transacoes:
                    break
                
                # Simula transação
                self.simular_transacao()
                
                # Aguarda intervalo
                time.sleep(intervalo)
                
                # Exibe estatísticas a cada 100 transações
                if self.estatisticas['total_enviadas'] % 100 == 0:
                    self.exibir_estatisticas()
        
        except KeyboardInterrupt:
            logger.info("\nSimulação interrompida pelo usuário")
        
        finally:
            # Garante envio de todas as mensagens pendentes
            self.producer.flush()
            self.producer.close()
            
            # Exibe estatísticas finais
            self.exibir_estatisticas()
            
            tempo_total = time.time() - inicio
            logger.info(f"Tempo total de simulação: {tempo_total:.2f} segundos")
            
            if tempo_total > 0:
                taxa_real = self.estatisticas['total_enviadas'] / tempo_total
                logger.info(f"Taxa real de envio: {taxa_real:.2f} transações/segundo")