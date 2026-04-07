# Mensageria com Apache Kafka - Sistema de Rodovia

Este documento descreve a implementação de mensageria usando Apache Kafka para processar transações de pedágio de forma assíncrona.

## 📋 Visão Geral

A implementação utiliza Kafka para desacoplar o recebimento de transações (API REST) do processamento e persistência no banco de dados, permitindo:

- **Processamento Assíncrono**: As transações são enviadas para o Kafka e processadas em paralelo
- **Alta Disponibilidade**: O Kafka mantém as mensagens até serem processadas
- **Escalabilidade**: Múltiplos consumidores podem processar transações em paralelo
- **Resiliência**: Em caso de falha, as mensagens podem ser reprocessadas

## 🏗️ Arquitetura

```
┌─────────────┐      POST      ┌──────────────────┐
│   Cliente   │ ───────────────>│   Controller     │
└─────────────┘                 │  (REST API)      │
                                └────────┬─────────┘
                                         │
                                         v
                                ┌────────────────┐
                                │    Producer    │
                                │   (Kafka)      │
                                └────────┬───────┘
                                         │
                                         v
                                  ╔═══════════╗
                                  ║   KAFKA   ║
                                  ║  Topic:   ║
                                  ║ transacao ║
                                  ║ -pedagio  ║
                                  ╚═══════════╝
                                         │
                                         v
                                ┌────────────────┐
                                │   Consumer     │
                                │   (Listener)   │
                                └────────┬───────┘
                                         │
                                         v
                                ┌────────────────┐
                                │   Banco de     │
                                │     Dados      │
                                └────────────────┘
```

## 🔧 Componentes Implementados

### 1. Configuração do Kafka (`KafkaConfig.java`)
- Configuração do Producer e Consumer
- Criação automática do tópico `transacao-pedagio`
- 3 partições para processamento paralelo
- Serialização JSON para as mensagens

### 2. Producer (`TransacaoKafkaProducer.java`)
- **Envio Assíncrono**: `enviarTransacao()` - retorna imediatamente
- **Envio Síncrono**: `enviarTransacaoSync()` - aguarda confirmação
- Usa a placa do veículo como chave de particionamento
- Logs detalhados de sucesso e erro

### 3. Consumer (`TransacaoKafkaConsumer.java`)
- Escuta o tópico `transacao-pedagio`
- Valida e busca entidades relacionadas (Praça, Pista, Tarifa)
- Persiste a transação no banco de dados
- Tratamento de erros com logging

### 4. DTOs
- `TransacaoPedagioRequestDTO`: Recebe dados da API
- `TransacaoPedagioKafkaDTO`: Formato de mensagem no Kafka

### 5. Controller (`TransacaoPedagioController.java`)
- `POST /api/transacoes` - Envio assíncrono (retorna HTTP 202)
- `POST /api/transacoes/sync` - Envio síncrono (retorna HTTP 201)

## 🚀 Como Usar

### 1. Iniciar os Serviços

```bash
# Iniciar PostgreSQL, Redis, Zookeeper e Kafka
docker-compose up -d

# Verificar se os serviços estão rodando
docker ps
```

### 2. Verificar o Kafka

```bash
# Acessar o container do Kafka
docker exec -it rodovia-kafka bash

# Listar tópicos
kafka-topics --bootstrap-server localhost:9092 --list

# Ver detalhes do tópico
kafka-topics --bootstrap-server localhost:9092 --describe --topic transacao-pedagio

# Consumir mensagens (para debug)
kafka-console-consumer --bootstrap-server localhost:9092 --topic transacao-pedagio --from-beginning
```

### 3. Enviar Transações via API

#### Envio Assíncrono (Recomendado)
```bash
curl -X POST http://localhost:9080/api/transacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 1,
    "dataHoraPassagem": "2026-01-27T10:30:00",
    "placa": "ABC1D23",
    "tagId": "TAG123456",
    "tipoVeiculo": "PASSEIO",
    "valorOriginal": 8.50,
    "statusTransacao": "PROCESSADA",
    "hashIntegridade": "abc123..."
  }'
```

**Resposta:**
```
HTTP/1.1 202 Accepted
Transação enviada para processamento - Placa: ABC1D23
```

#### Envio Síncrono
```bash
curl -X POST http://localhost:9080/api/transacoes/sync \
  -H "Content-Type: application/json" \
  -d '{
    "pracaId": 1,
    "pistaId": 1,
    "tarifaId": 1,
    "dataHoraPassagem": "2026-01-27T10:35:00",
    "placa": "XYZ9A88",
    "tipoVeiculo": "CAMINHAO",
    "valorOriginal": 25.00
  }'
```

### 4. Monitorar o Processamento

Os logs da aplicação mostrarão:

**Producer:**
```
Enviando transação para Kafka - Placa: ABC1D23, Praça: 1, Pista: 1
Transação enviada com sucesso - Placa: ABC1D23, Offset: 42, Partition: 2
```

**Consumer:**
```
Recebida transação do Kafka - Placa: ABC1D23, Partition: 2, Offset: 42
Transação processada e salva com sucesso - ID: 156, Placa: ABC1D23, Praça: Praça Teste
```

## 📊 Monitoramento e Performance

### Métricas do Kafka

```bash
# Ver o consumer group
docker exec rodovia-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group rodovia-transacao-consumer-group
```

### Verificar Lag (Atraso no Processamento)
O comando acima mostra:
- **CURRENT-OFFSET**: Última mensagem processada
- **LOG-END-OFFSET**: Última mensagem no tópico
- **LAG**: Diferença entre os dois (idealmente 0 ou próximo)

## ⚙️ Configurações

### application.properties

```properties
# Kafka Configuration
spring.kafka.bootstrap-servers=localhost:9092

# Producer
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer

# Consumer
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.group-id=rodovia-transacao-consumer-group
spring.kafka.consumer.auto-offset-reset=earliest

# Topic
kafka.topic.transacao-pedagio=transacao-pedagio
kafka.topic.transacao-pedagio.partitions=3
kafka.topic.transacao-pedagio.replication=1
```

### Ajustes de Performance

Para aumentar o throughput, você pode:

1. **Aumentar o número de partições**:
```properties
kafka.topic.transacao-pedagio.partitions=10
```

2. **Aumentar a concorrência do consumer** em `KafkaConfig.java`:
```java
factory.setConcurrency(10); // Número de threads
```

3. **Batch Processing**: Configurar o consumer para processar em lote

## 🔍 Troubleshooting

### Problema: Mensagens não são consumidas

1. Verificar se o consumer está rodando:
```bash
docker logs -f rodovia-kafka
```

2. Verificar se o tópico existe:
```bash
docker exec rodovia-kafka kafka-topics --bootstrap-server localhost:9092 --list
```

3. Verificar o consumer group:
```bash
docker exec rodovia-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 --list
```

### Problema: Erros de serialização

Verificar se os DTOs têm:
- Construtor sem argumentos
- Getters e Setters
- Anotação `@Data` do Lombok

### Problema: Kafka não conecta

1. Verificar se o Kafka está rodando:
```bash
docker ps | grep kafka
```

2. Verificar logs do Kafka:
```bash
docker logs rodovia-kafka
```

3. Verificar se o Zookeeper está rodando:
```bash
docker ps | grep zookeeper
docker logs rodovia-zookeeper
```

## 🎯 Boas Práticas

1. **Use envio assíncrono** para alta performance
2. **Implemente retry** para falhas transientes
3. **Configure Dead Letter Queue (DLQ)** para mensagens com erro
4. **Monitore o lag** do consumer regularmente
5. **Use a placa como chave** para garantir ordem por veículo
6. **Implemente idempotência** no consumer para evitar duplicatas

## 📝 Próximos Passos

Para produção, considere implementar:

- ✅ Dead Letter Queue (DLQ) para mensagens com erro
- ✅ Retry automático com backoff exponencial
- ✅ Monitoramento com Prometheus + Grafana
- ✅ Alertas para lag alto do consumer
- ✅ Compactação de logs do Kafka
- ✅ Replicação multi-broker (alta disponibilidade)
- ✅ Schema Registry (Avro) para versionamento de mensagens

## 📚 Referências

- [Spring for Apache Kafka](https://spring.io/projects/spring-kafka)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Best Practices](https://kafka.apache.org/documentation/#bestpractices)
