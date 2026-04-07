# Simulador de Transações de Pedágio

Simulador em Python para gerar transações de pedágio e enviá-las para um broker Kafka. 
O simulador introduz erros aleatórios nas transações para testar o sistema de correções.

## Recursos

- 🖥️ **Interface Gráfica Intuitiva** - GUI com Tkinter para fácil operação
- ⚙️ **Configuração Flexível** - Ajuste taxa de transações, taxa de erro e mais
- 📊 **Estatísticas em Tempo Real** - Monitor estatísticas durante a execução
- 🚀 **Modo Stress Test** - Teste com até 1000 transações/segundo
- 📝 **Log Detalhado** - Acompanhe cada transação enviada
- 💾 **Executável Standalone** - Gere .exe ou binário sem precisar de Python
- ⌨️ **Interface CLI** - Automação via linha de comando

## Requisitos

- Python 3.8+
- Kafka rodando em localhost:9092 (ou configure o .env)
- Banco de dados com praças, pistas e tarifas cadastradas

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### 🖥️ Interface Gráfica (Recomendado)

Execute a interface gráfica intuitiva:

```bash
python gui.py
```

**Recursos da Interface:**
- ⚙️ Configuração visual de todos os parâmetros
- 📊 Estatísticas em tempo real
- 📝 Log de execução com scroll
- ▶️ Controles de iniciar/parar
- 🎯 Modo Stress Test com um clique

![Interface](https://via.placeholder.com/800x600?text=Interface+Gr%C3%A1fica)

### ⌨️ Linha de Comando

Execute via terminal com opções personalizadas:

```bash
# Uso básico (10 TPS, 15% erro, infinito)
python main.py

# Com duração limitada (60 segundos)
python main.py --duration 60

# Com número específico de transações
python main.py --count 1000

# Taxa customizada (50 transações/segundo)
python main.py --rate 50

# Taxa de erro específica (20%)
python main.py --error-rate 0.20

# Modo stress test (1000 TPS)
python main.py --stress

# Combinando opções
python main.py --duration 300 --rate 100 --error-rate 0.25
```

## 💾 Gerando Executável

Para criar um executável standalone (não precisa Python instalado):

```bash
# Linux/Mac
chmod +x build_linux.sh
./build_linux.sh

# Windows
build_windows.bat
```

O executável será criado em `dist/Simulador-Pedagio` (ou `.exe` no Windows).

📖 **Documentação completa de build**: Veja [BUILD.md](BUILD.md) para instruções detalhadas.

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=transacao-pedagio

# Simulação
SIMULATION_RATE=10
ERROR_RATE=0.15
```

Ou configure via interface gráfica ou argumentos de linha de comando.

## Estrutura do Projeto

```
simulador/
├── gui.py                  # 🖥️ Interface gráfica
├── main.py                 # ⌨️ CLI principal
├── simulator.py            # 🎯 Lógica do simulador
├── kafka_producer.py       # 📤 Produtor Kafka
├── transacao_generator.py  # 🎲 Gerador de transações
├── models.py               # 📋 Modelos de dados
├── config.py               # ⚙️ Configurações
├── requirements.txt        # 📦 Dependências
├── build_linux.sh          # 🐧 Build Linux/Mac
├── build_windows.bat       # 🪟 Build Windows
├── BUILD.md                # 📖 Doc de build
├── README.md               # 📄 Este arquivo
└── .env                    # 🔐 Variáveis de ambiente
```

## Exemplos de Uso

### Teste Rápido (1 minuto, 10 TPS)
```bash
python main.py --duration 60 --rate 10
```

### Carga Média (5 minutos, 100 TPS)
```bash
python main.py --duration 300 --rate 100
```

### Stress Test (1000 TPS até 10.000 transações)
```bash
python main.py --stress --count 10000
```

### Teste de Alta Taxa de Erro
```bash
python main.py --duration 120 --error-rate 0.50
```

## Tipos de Erros Gerados

O simulador gera os seguintes tipos de erro intencionalmente:

1. **Placa Inválida** - Formato INV seguido de números
2. **Tarifa Incorreta** - Valor de tarifa errado para o tipo de veículo
3. **Pista Inválida** - ID de pista que não existe
4. **Praça Inválida** - ID de praça que não existe

Esses erros são úteis para testar sistemas de correção e validação.

## Estatísticas Fornecidas

Durante e ao final da execução, o simulador exibe:

- **Total de Transações Enviadas**
- **Transações OK** (sem erro intencional)
- **Transações com Erro** (erro intencional)
- **Erros de Envio** (falhas ao enviar para Kafka)
- **Taxa de Erro** (percentual)
- **Taxa Real de Envio** (TPS efetivo)
- **Tempo Total de Simulação**

## Troubleshooting

### Erro: "Cannot connect to Kafka"
```bash
# Verifique se o Kafka está rodando
docker ps | grep kafka

# Teste a conexão
nc -zv localhost 9092
```

### Erro: "Module 'kafka' not found"
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

### Interface gráfica não abre
```bash
# Linux: Instale tkinter
sudo apt install python3-tk

# Teste o tkinter
python3 -c "import tkinter; print('OK')"
```

### Taxa de envio baixa
- Verifique latência de rede com Kafka
- Reduza o intervalo de log (modifique `simulator.py`)
- Use modo `--stress` para máxima performance

## Performance

### Capacidade Testada

- **Taxa Máxima**: 1000 transações/segundo (modo stress)
- **Taxa Recomendada**: 10-100 TPS para uso normal
- **Overhead**: ~10ms por transação em rede local

### Otimizações

- Usa batch sending do Kafka para melhor throughput
- Thread separada na GUI para não travar interface
- Logging assíncrono para não impactar performance

## Desenvolvimento

### Adicionando Novos Tipos de Erro

Edite `transacao_generator.py`:

```python
def gerar_transacao(self, com_erro=False):
    # ... código existente ...
    
    if com_erro:
        erro = random.choice(['placa', 'tarifa', 'pista', 'praca', 'novo_erro'])
        
        if erro == 'novo_erro':
            # Sua lógica aqui
            pass
```

### Modificando a Interface

A interface está em `gui.py` e usa Tkinter. Para adicionar novos campos:

1. Adicione widgets em `criar_widgets()`
2. Crie variáveis de controle (`tk.StringVar`, etc)
3. Use os valores em `iniciar_simulacao()`

## Licença

Este projeto faz parte do TCC sobre Sistema de Pedágio.

## Suporte

Para problemas ou dúvidas:
1. Verifique a documentação em [BUILD.md](BUILD.md)
2. Consulte os logs de execução
3. Revise as configurações do Kafka

## Changelog

### v1.1.0 (atual)
- ✨ Adicionada interface gráfica com Tkinter
- ✨ Scripts de build para executável
- ✨ Método `parar()` no simulador
- ✨ Documentação BUILD.md
- 🐛 Fix: Compatibilidade com Python 3.12 (kafka-python-ng)

### v1.0.0
- 🎉 Versão inicial
- ⚙️ CLI funcional
- 📤 Integração com Kafka
- 🎲 Geração de erros aleatórios
