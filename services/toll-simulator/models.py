from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum
import json

class TipoVeiculoEnum(Enum):
    MOTO = "MOTO"
    CARRO = "CARRO"
    CAMINHAO = "CAMINHAO"

class StatusTransacaoEnum(Enum):
    OK = "OK"
    OCORRENCIA = "OCORRENCIA"
    CORRIGIDA = "CORRIGIDA"

@dataclass
class TransacaoPedagioKafkaDTO:
    pracaId: int
    pistaId: int
    tarifaId: int
    dataHoraPassagem: str
    placa: str
    tagId: Optional[str]
    tipoVeiculo: str
    valorOriginal: float
    statusTransacao: str
    hashIntegridade: str
    
    def to_json(self) -> str:
        """Converte o DTO para JSON"""
        data = asdict(self)
        return json.dumps(data)
    
    def to_dict(self) -> dict:
        """Converte o DTO para dicionário"""
        return asdict(self)