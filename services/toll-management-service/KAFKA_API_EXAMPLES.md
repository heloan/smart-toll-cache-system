# Exemplos de Uso da API com Kafka

## 📡 Endpoints Disponíveis

### 1. Criar Transação (Assíncrono)
**POST** `/api/transacoes`

Envia a transação para o Kafka e retorna imediatamente (HTTP 202 Accepted).

```bash
curl -X POST http://localhost:9080/api/transacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 1,
    "dataHoraPassagem": "2026-01-27T14:30:00",
    "placa": "ABC1D23",
    "tagId": "TAG12345678",
    "tipoVeiculo": "CARRO",
    "valorOriginal": 8.50,
    "statusTransacao": "OK",
    "hashIntegridade": "abc123def456"
  }'
```

**Resposta:**
```
HTTP/1.1 202 Accepted
Transação enviada para processamento - Placa: ABC1D23
```

---

### 2. Criar Transação (Síncrono)
**POST** `/api/transacoes/sync`

Aguarda a confirmação do Kafka antes de retornar (HTTP 201 Created).

```bash
curl -X POST http://localhost:9080/api/transacoes/sync \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 1,
    "dataHoraPassagem": "2026-01-27T14:35:00",
    "placa": "XYZ9A88",
    "tipoVeiculo": "CAMINHAO",
    "valorOriginal": 25.00
  }'
```

---

### 3. Listar Transações
**GET** `/api/transacoes?limite=10`

```bash
curl http://localhost:9080/api/transacoes?limite=10
```

---

## 🎯 Tipos de Veículo

Os valores aceitos para `tipoVeiculo`:
- `CARRO` - Carros de passeio (R$ 8,50)
- `MOTO` - Motocicletas (R$ 4,25)
- `CAMINHAO` - Caminhões (R$ 25,00)

---

## 🚗 Status da Transação

Valores aceitos para `statusTransacao`:
- `OK` - Transação processada com sucesso
- `OCORRENCIA` - Com problemas que precisam correção
- `CORRIGIDA` - Foi corrigida após uma ocorrência

---

## 📋 Validações

### Formato da Placa
- Padrão Mercosul: `ABC1D23`
- 3 letras, 1 número, 1 letra, 2 números
- Exemplo: `ABC1D23`, `XYZ9W88`

### Campos Obrigatórios
- `pracaId` (positivo)
- `pistaId` (positivo)
- `tarifaId` (positivo)
- `dataHoraPassagem` (formato ISO: YYYY-MM-DDTHH:mm:ss)
- `placa` (formato Mercosul)
- `tipoVeiculo`
- `valorOriginal` (positivo)

### Campos Opcionais
- `tagId` - Identificador da tag eletrônica
- `statusTransacao` (padrão: PROCESSADA)
- `hashIntegridade` - Hash para validação de integridade

---

## 🧪 Exemplos de Teste

### Exemplo 1: Transação Simples (Mínimo necessário)
```bash
curl -X POST http://localhost:9080/api/transacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 1,
    "dataHoraPassagem": "2026-01-27T10:00:00",
    "placa": "ABC1234",
    "tipoVeiculo": "CARRO",
    "valorOriginal": 8.50
  }'
```

### Exemplo 2: Caminhão com Tag
```bash
curl -X POST http://localhost:9080/api/transacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 2,
    "tarifaId": 2,
    "dataHoraPassagem": "2026-01-27T11:15:00",
    "placa": "DEF5G67",
    "tagId": "TAG87654321",
    "tipoVeiculo": "CAMINHAO",
    "valorOriginal": 25.00,
    "statusTransacao": "OK",
    "hashIntegridade": "hash_caminhao_001"
  }'
```

### Exemplo 3: Moto sem Tag
```bash
curl -X POST http://localhost:9080/api/transacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 3,
    "dataHoraPassagem": "2026-01-27T12:30:00",
    "placa": "MOT1A23",
    "tipoVeiculo": "MOTO",
    "valorOriginal": 4.25
  }'
```

---

## 🔄 Teste de Carga

### Enviar 100 transações
```bash
for i in {1..100}; do
  placa=$(printf "TST%04d" $i)
  curl -X POST http://localhost:9080/api/transacoes \
    -H "Content-Type: application/json" \
    -d "{
      \"pracaId\": 1,
      \"pistaId\": 1,
      \"tarifaId\": 1,
      \"dataHoraPassagem\": \"$(date -u +"%Y-%m-%dT%H:%M:%S")\",
      \"placa\": \"$placa\",
      \"tipoVeiculo\": \"CARRO\",
      \"valorOriginal\": 8.50
    }"
  sleep 0.1
done
```

### Usando o script de teste
```bash
./test-kafka.sh
# Escolha opção 3 e informe a quantidade
```

---

## ⚠️ Tratamento de Erros

### Erro: Praça não encontrada
```json
{
  "error": "Praça não encontrada: 999"
}
```

**Solução**: Verificar se a praça existe no banco de dados.

### Erro: Placa inválida
```json
{
  "error": "Placa inválida (formato: ABC1D23)"
}
```

**Solução**: Usar o formato Mercosul: 3 letras + 1 número + 1 letra + 2 números

### Erro: Valor inválido
```json
{
  "error": "Valor original deve ser positivo"
}
```

**Solução**: Informar um valor maior que zero.

---

## 📊 Monitoramento

### Verificar se as transações foram processadas
```bash
# Ver logs da aplicação
docker logs -f rodovia-app

# Verificar consumer group
docker exec rodovia-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group rodovia-transacao-consumer-group

# Listar transações no banco
curl http://localhost:9080/api/transacoes?limite=20
```

---

## 🐛 Debug

### Consumir mensagens do Kafka diretamente
```bash
docker exec -it rodovia-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic transacao-pedagio \
  --from-beginning
```

### Verificar partições
```bash
docker exec rodovia-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe --topic transacao-pedagio
```

---

## 🚀 Teste Programático (Java)

Para gerar transações de teste automaticamente, inicie a aplicação com o profile `kafka-test`:

```bash
java -jar target/rodovia.jar --spring.profiles.active=kafka-test 10
```

Isso irá gerar 10 transações aleatórias e enviá-las para o Kafka.

---

## 📝 Notas Importantes

1. **Performance**: Use o endpoint assíncrono (`/api/transacoes`) para melhor performance
2. **Ordem**: Transações com a mesma placa são enviadas para a mesma partição, garantindo ordem
3. **Retry**: O consumer fará retry automático em caso de erro
4. **Idempotência**: O producer está configurado para evitar duplicatas
5. **Timeout**: O envio síncrono pode demorar até 30 segundos em caso de problemas
