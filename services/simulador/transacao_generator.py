# transacao_generator.py
import random
import hashlib
from datetime import datetime
from faker import Faker
from models import TransacaoPedagioKafkaDTO, TipoVeiculoEnum, StatusTransacaoEnum
from config import Config

fake = Faker('pt_BR')

class TransacaoGenerator:
    """Gerador de transações de pedágio"""
    
    def __init__(self):
        self.config = Config()
        self.error_types = [
            'placa_invalida',
            'valor_errado',
            'tag_duplicada',
            'horario_inconsistente'
        ]
    
    def gerar_placa(self) -> str:
        """Gera uma placa brasileira (formato antigo ou Mercosul)"""
        if random.choice([True, False]):
            # Formato antigo: ABC-1234
            return f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}-{random.randint(1000, 9999)}"
        else:
            # Formato Mercosul: ABC1D23
            return f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{random.randint(1, 9)}{fake.random_uppercase_letter()}{random.randint(10, 99)}"
    
    def gerar_tag_id(self) -> str:
        """Gera um ID de tag único"""
        return f"TAG{random.randint(100000, 999999)}"
    
    def calcular_hash(self, transacao_data: str) -> str:
        """Calcula hash de integridade da transação"""
        return hashlib.sha256(transacao_data.encode()).hexdigest()
    
    def introduzir_erro(self, transacao: TransacaoPedagioKafkaDTO, tipo_erro: str) -> TransacaoPedagioKafkaDTO:
        """Introduz um erro específico na transação"""
        transacao.statusTransacao = StatusTransacaoEnum.OCORRENCIA.value
        
        if tipo_erro == 'placa_invalida':
            # Placa com formato inválido
            transacao.placa = f"INV{random.randint(100, 999)}"
        
        elif tipo_erro == 'valor_errado':
            # Valor incorreto (muito alto ou muito baixo)
            if random.choice([True, False]):
                transacao.valorOriginal = transacao.valorOriginal * random.uniform(2.0, 5.0)
            else:
                transacao.valorOriginal = transacao.valorOriginal * random.uniform(0.1, 0.5)
        
        elif tipo_erro == 'tag_duplicada':
            # Tag duplicada (usa uma tag fixa)
            transacao.tagId = "TAG999999"
        
        elif tipo_erro == 'horario_inconsistente':
            # Horário futuro ou muito no passado
            pass  # O horário já foi gerado, apenas marca como ocorrência
        
        return transacao
    
    def gerar_transacao(self, com_erro: bool = False) -> TransacaoPedagioKafkaDTO:
        """Gera uma transação de pedágio"""
        # Seleciona tipo de veículo aleatório
        tipo_veiculo = random.choice(list(TipoVeiculoEnum)).value
        
        # Dados básicos da transação
        praca_id = random.choice(self.config.PRACA_IDS)
        pista_id = random.choice(self.config.PISTA_IDS)
        tarifa_id = random.choice(self.config.TARIFA_IDS)
        data_hora = datetime.now().isoformat()
        placa = self.gerar_placa()
        tag_id = self.gerar_tag_id() if random.random() > 0.1 else None  # 90% com tag
        valor_original = self.config.TARIFAS[tipo_veiculo]
        status = StatusTransacaoEnum.OK.value
        
        # Cria dados para hash
        transacao_data = f"{praca_id}{pista_id}{data_hora}{placa}{valor_original}"
        hash_integridade = self.calcular_hash(transacao_data)
        
        # Cria transação
        transacao = TransacaoPedagioKafkaDTO(
            pracaId=praca_id,
            pistaId=pista_id,
            tarifaId=tarifa_id,
            dataHoraPassagem=data_hora,
            placa=placa,
            tagId=tag_id,
            tipoVeiculo=tipo_veiculo,
            valorOriginal=valor_original,
            statusTransacao=status,
            hashIntegridade=hash_integridade
        )
        
        # Introduz erro se solicitado
        if com_erro:
            tipo_erro = random.choice(self.error_types)
            transacao = self.introduzir_erro(transacao, tipo_erro)
        
        return transacao