import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'transacao-pedagio')
    
    # Simulation Configuration
    SIMULATION_RATE = int(os.getenv('SIMULATION_RATE', '10'))  # Transações por segundo
    ERROR_RATE = float(os.getenv('ERROR_RATE', '0.15'))  # 15% das transações com erro
    
    # IDs das entidades (devem existir no banco de dados)
    PRACA_IDS = [1, 2, 3]
    PISTA_IDS = [1, 2, 3, 4, 5, 6]
    TARIFA_IDS = [1, 2, 3]
    
    # Valores de tarifa por tipo de veículo
    TARIFAS = {
        'MOTO': 5.00,
        'CARRO': 10.00,
        'CAMINHAO': 20.00
    }