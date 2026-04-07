# 🚀 Início Rápido - Simulador de Pedágio

## Executar Agora

### Linux/Mac
```bash
./run_gui.sh
```

### Windows
```batch
run_gui.bat
```

Ou clique duplo no arquivo!

## Primeira Execução

1. **Certifique-se que o Kafka está rodando**
   ```bash
   # Verificar se Kafka está ativo
   nc -zv localhost 9092
   ```

2. **Abra a interface gráfica**
   - Linux/Mac: `./run_gui.sh`
   - Windows: `run_gui.bat`

3. **Configure os parâmetros**
   - Servidor Kafka: `localhost:9092` (padrão)
   - Tópico: `transacao-pedagio` (padrão)
   - Taxa: `10` transações/segundo
   - Taxa de erro: `15%`

4. **Inicie a simulação**
   - Clique em **▶ Iniciar Simulação**
   - Acompanhe as estatísticas em tempo real
   - Veja o log de transações

5. **Pare quando quiser**
   - Clique em **⏹ Parar Simulação**
   - Ou defina limites antes (duração/quantidade)

## Modo Console (Sem Interface)

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Executar simulador
python main.py
```

## Cenários de Teste

### Teste Básico (1 minuto)
```bash
python main.py --duration 60
```

### Teste de Carga (100 TPS por 5 minutos)
```bash
python main.py --rate 100 --duration 300
```

### Stress Test (1000 TPS)
```bash
python main.py --stress --count 10000
```

### Alta Taxa de Erro (50%)
```bash
python main.py --error-rate 0.50 --duration 120
```

## Verificar se Funcionou

### No Console do Kafka
```bash
# Consumir mensagens do tópico
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic transacao-pedagio \
  --from-beginning
```

### Na Interface
- Veja "Total enviadas" aumentando
- Monitore a taxa de erro (~15%)
- Confira o log de transações

## Problemas Comuns

### "Cannot connect to Kafka"
```bash
# Iniciar Kafka (Docker)
docker-compose up -d

# Ou verificar se está rodando
docker ps | grep kafka
```

### "Module not found: tkinter"
```bash
# Linux
sudo apt install python3-tk

# Mac
brew install python-tk
```

### "Module not found: faker/kafka"
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Interface não abre no Linux
```bash
# Dar permissão ao script
chmod +x run_gui.sh

# Executar
./run_gui.sh
```

## Próximos Passos

1. ✅ Rode o simulador
2. 📊 Monitore as estatísticas
3. 🔍 Verifique mensagens no Kafka
4. 🧪 Teste diferentes cenários
5. 📦 Gere um executável (BUILD.md)

## Links Úteis

- [README.md](README_NEW.md) - Documentação completa
- [BUILD.md](BUILD.md) - Gerar executável
- Kafka: http://localhost:9092

## Suporte Rápido

**Interface não abre?**
```bash
# Verificar dependências
python3 -c "import tkinter; print('Tkinter OK')"
python3 -c "import faker; print('Faker OK')"
python3 -c "import kafka; print('Kafka OK')"
```

**Kafka não conecta?**
```bash
# Testar conexão
telnet localhost 9092
# ou
nc -zv localhost 9092
```

**Ver logs detalhados?**
```bash
# Executar com log detalhado
python main.py --rate 1  # Bem devagar para ver tudo
```

---

💡 **Dica**: Use a interface gráfica para configuração rápida e o console para automação/scripts!

🎯 **Meta**: Gere milhares de transações, teste o sistema de correção e valide a arquitetura!
