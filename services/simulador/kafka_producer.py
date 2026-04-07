# kafka_producer.py
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransacaoKafkaProducer:
    """Producer Kafka para enviar transações"""
    
    def __init__(self):
        self.config = Config()
        self.producer = self._create_producer()
    
    def _create_producer(self) -> KafkaProducer:
        """Cria o producer Kafka"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Aguarda confirmação de todas as réplicas
                retries=3,
                max_in_flight_requests_per_connection=1  # Garante ordem
            )
            logger.info(f"Producer Kafka conectado: {self.config.KAFKA_BOOTSTRAP_SERVERS}")
            return producer
        except Exception as e:
            logger.error(f"Erro ao criar producer Kafka: {e}")
            raise
    
    def enviar_transacao(self, transacao: dict, key: str = None) -> bool:
        """Envia uma transação para o Kafka"""
        try:
            future = self.producer.send(
                self.config.KAFKA_TOPIC,
                value=transacao,
                key=key
            )
            
            # Aguarda confirmação
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Transação enviada - Tópico: {record_metadata.topic}, "
                f"Partição: {record_metadata.partition}, "
                f"Offset: {record_metadata.offset}, "
                f"Placa: {transacao.get('placa')}"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Erro Kafka ao enviar transação: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar transação: {e}")
            return False
    
    def flush(self):
        """Força o envio de todas as mensagens pendentes"""
        self.producer.flush()
    
    def close(self):
        """Fecha o producer"""
        self.producer.close()
        logger.info("Producer Kafka fechado")