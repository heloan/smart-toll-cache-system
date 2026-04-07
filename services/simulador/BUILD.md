# Simulador de Transações de Pedágio - Executável

## Pré-requisitos para Gerar o Executável

### Linux/Mac
```bash
# Instalar Python 3.8 ou superior
sudo apt install python3 python3-pip python3-venv  # Ubuntu/Debian
# ou
brew install python3  # macOS

# Instalar dependências do sistema (necessário para tkinter)
sudo apt install python3-tk  # Ubuntu/Debian
```

### Windows
- Instalar Python 3.8 ou superior de [python.org](https://www.python.org/downloads/)
- Marcar a opção "Add Python to PATH" durante a instalação

## Gerando o Executável

### Linux/Mac
```bash
# Dar permissão de execução ao script
chmod +x build_linux.sh

# Executar o script de build
./build_linux.sh
```

### Windows
```batch
# Executar o script de build
build_windows.bat
```

## Após a Geração

O executável será criado na pasta `dist/`:
- **Linux/Mac**: `dist/Simulador-Pedagio`
- **Windows**: `dist\Simulador-Pedagio.exe`

## Executando o Simulador

### Modo Gráfico (Interface)
```bash
# Linux/Mac
./dist/Simulador-Pedagio

# Windows
dist\Simulador-Pedagio.exe
```

Ou simplesmente execute com Python:
```bash
python gui.py
```

### Modo Console (Linha de Comando)
```bash
python main.py [opções]

# Exemplos:
python main.py --duration 60                    # Rodar por 60 segundos
python main.py --count 1000                     # Gerar 1000 transações
python main.py --rate 50                        # 50 transações/segundo
python main.py --error-rate 0.20                # 20% de taxa de erro
python main.py --stress                         # Modo stress test (1000 TPS)
python main.py --duration 300 --rate 100        # Combinar opções
```

## Recursos da Interface Gráfica

### Configurações
- **Servidor Kafka**: Endereço do broker Kafka (padrão: localhost:9092)
- **Tópico Kafka**: Nome do tópico (padrão: transacao-pedagio)
- **Transações/segundo**: Taxa de geração (1-1000 TPS)
- **Taxa de erro (%)**: Percentual de transações com erro intencional (0-100%)

### Controle de Execução
- **Duração**: Limitar tempo de execução em segundos
- **Total de transações**: Limitar quantidade de transações
- **Modo Stress Test**: Ativa 1000 transações/segundo

### Botões
- **▶ Iniciar Simulação**: Inicia a geração de transações
- **⏹ Parar Simulação**: Para a execução em andamento
- **🗑 Limpar Log**: Limpa o histórico de logs

### Estatísticas em Tempo Real
- Status da simulação
- Total de transações enviadas
- Transações OK vs. com erro
- Taxa de erro atual

### Log de Execução
Exibe em tempo real:
- Transações enviadas
- Partições e offsets do Kafka
- Estatísticas periódicas
- Erros e avisos

## Distribuindo o Executável

### Arquivos Necessários
O executável gerado é standalone, mas precisa:
1. Arquivo `.env` com configurações (ou definir variáveis de ambiente)
2. Acesso ao Kafka (servidor deve estar acessível)

### Exemplo de .env
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=transacao-pedagio
SIMULATION_RATE=10
ERROR_RATE=0.15
```

## Dicas de Uso

### Performance
- Para testes de carga, use Modo Stress Test
- Para testes longos, defina limite de duração
- Monitor estatísticas para avaliar taxa de erro

### Troubleshooting

**Erro: "Cannot connect to Kafka"**
- Verifique se o Kafka está rodando
- Confirme o endereço do servidor
- Verifique firewall/portas

**Erro: "Module not found"**
- Reinstale dependências: `pip install -r requirements.txt`
- No executável, refaça o build

**Interface não abre**
- Verifique se tkinter está instalado: `python -c "import tkinter"`
- Linux: `sudo apt install python3-tk`

## Customização

### Modificar Configurações Padrão
Edite `config.py` antes de gerar o executável.

### Adicionar Ícone ao Executável
1. Crie ou obtenha um ícone (.ico para Windows, .icns para Mac)
2. Modifique o script de build:
   ```bash
   --icon=caminho/para/icone.ico
   ```

### Build para Outras Plataformas
O executável gerado é específico para a plataforma onde foi compilado:
- Windows: gera .exe
- Linux: gera binário Linux
- macOS: gera app macOS

Para distribuir em múltiplas plataformas, compile em cada sistema operacional.

## Estrutura de Arquivos

```
simulador/
├── gui.py                  # Interface gráfica
├── main.py                 # CLI principal
├── simulator.py            # Lógica do simulador
├── kafka_producer.py       # Produtor Kafka
├── transacao_generator.py  # Gerador de transações
├── models.py               # Modelos de dados
├── config.py               # Configurações
├── requirements.txt        # Dependências Python
├── build_linux.sh          # Script build Linux/Mac
├── build_windows.bat       # Script build Windows
├── .env                    # Variáveis de ambiente
└── dist/                   # Executáveis gerados
    └── Simulador-Pedagio
```

## Licença e Suporte

Para mais informações, consulte o README.md principal do projeto.
