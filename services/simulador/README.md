# README.md
# Simulador de Transações de Pedágio

Simulador em Python para gerar transações de pedágio e enviá-las para um broker Kafka. 
O simulador introduz erros aleatórios nas transações para testar o sistema de correções.

## Requisitos

- Python 3.8+
- Kafka rodando em localhost:9092 (ou configure o .env)
- Banco de dados com praças, pistas e tarifas cadastradas

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt