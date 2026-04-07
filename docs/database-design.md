# Database Design

## Overview

The data model supports real-time toll transaction management with a rich domain model covering concessionaires, highways, toll plazas, lanes, tariffs, transactions, occurrences, corrections, operators, and performance metrics. PostgreSQL 15 serves as the **Single Source of Truth (SSOT)**, with Redis providing a distributed cache layer for frequently accessed data.

---

## Entity-Relationship Diagram

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Concessionaria  │      │     Rodovia       │      │  PracaPedagio    │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│ PK id            │──┐   │ PK id            │──┐   │ PK id            │──┐
│    nome_fantasia │  │   │ FK concess._id   │◀─┘   │ FK rodovia_id    │◀─┘
│    razao_social  │  │   │    codigo        │      │    nome          │
│    cnpj (UNIQUE) │  │   │    nome          │      │    km            │
│    contrato      │  │   │    uf            │      │    sentido       │
│    data_inicio   │  │   │    extensao_km   │      │    ativa         │
│    data_fim      │  │   │    ativa         │      │    criado_em     │
│    ativo         │  │   │    criado_em     │      └────────┬─────────┘
│    criado_em     │  │   └──────────────────┘               │
└──────────────────┘  │            1:N                 ┌─────┴──────────┐
         1:N          └────────────────────────────────┤                │
                                                       ▼                ▼
┌──────────────────┐                        ┌──────────────────┐  ┌──────────────────┐
│  TarifaPedagio   │                        │  PistaPedagio    │  │ TransacaoPedagio │
├──────────────────┤                        ├──────────────────┤  ├──────────────────┤
│ PK id            │──┐                     │ PK id            │──│ PK id            │
│    tipo_veiculo  │  │                     │ FK praca_id      │  │ FK praca_id      │
│    valor         │  │                     │    numero_pista  │  │ FK pista_id      │
│    vigencia_ini  │  │                     │    tipo_pista    │  │ FK tarifa_id     │◀─┘
│    vigencia_fim  │  │                     │    sentido       │  │    data_hora     │
│    criado_em     │  │                     │    ativa         │  │    placa         │
└──────────────────┘  │                     │    criado_em     │  │    tag_id        │
                      │                     │ UK(praca,numero) │  │    tipo_veiculo  │
                      │                     └──────────────────┘  │    valor_original│
                      │                              1:N          │    status_trans.  │
                      └───────────────────────────────────────────│    hash_integrid.│
                                                                  │    criado_em     │
                                                                  └────────┬─────────┘
                                                                           │
                                                              ┌────────────┼────────────┐
                                                              ▼                         ▼
                                                   ┌──────────────────┐      ┌──────────────────┐
                                                   │ OcorrenciaTransa │      │ CorrecaoTransacao │
                                                   ├──────────────────┤      ├──────────────────┤
                                                   │ PK id            │      │ PK id            │
                                                   │ FK transacao_id  │      │ FK transacao_id  │
                                                   │    tipo_ocorr.   │      │ FK operador_id   │
                                                   │    observacao    │      │    motivo        │
                                                   │    detectada_aut │      │    valor_anterior│
                                                   │    criado_em     │      │    valor_corrig. │
                                                   └──────────────────┘      │    tipo_correcao │
                                                                             │    criado_em     │
┌──────────────────┐      ┌──────────────────┐                               └────────┬─────────┘
│    Operador      │      │ RegistroPerform. │                                        │
├──────────────────┤      ├──────────────────┤                                        │
│ PK id            │──────│ PK id            │                                        │
│    username (UQ) │      │    endpoint      │                               ◀────────┘
│    password      │      │    metodo_http   │
│    nome_completo │      │    tempo_proc_ms │
│    email (UQ)    │      │    memoria_usada │
│    telefone      │      │    memoria_livre │
│    ativo         │      │    uso_cpu       │
│    criado_em     │      │    threads_ativas│
│    atualizado_em │      │    status_http   │
└──────────────────┘      │    origem_dados  │
                          │    criado_em     │
                          └──────────────────┘
```

### Relationships

- **Concessionaria → Rodovia**: One-to-Many (1:N) — A concessionaire manages many highways
- **Rodovia → PracaPedagio**: One-to-Many (1:N) — A highway has many toll plazas
- **PracaPedagio → PistaPedagio**: One-to-Many (1:N) — A plaza has many lanes
- **PracaPedagio → TransacaoPedagio**: One-to-Many (1:N) — A plaza processes many transactions
- **PistaPedagio → TransacaoPedagio**: One-to-Many (1:N) — A lane processes many transactions
- **TarifaPedagio → TransacaoPedagio**: One-to-Many (1:N) — A tariff applies to many transactions
- **TransacaoPedagio → OcorrenciaTransacao**: One-to-Many (1:N) — A transaction can have many occurrences
- **TransacaoPedagio → CorrecaoTransacao**: One-to-Many (1:N) — A transaction can have many corrections
- **Operador → CorrecaoTransacao**: One-to-Many (1:N) — An operator performs many corrections

---

## Schema Definitions

### Table: `concessionaria`

| Column               | Type          | Constraints          | Description                         |
|----------------------|---------------|----------------------|-------------------------------------|
| `id`                 | BIGINT        | PK, AUTO_INCREMENT   | Unique identifier                   |
| `nome_fantasia`      | VARCHAR(120)  | NOT NULL             | Trade name                          |
| `razao_social`       | VARCHAR(160)  | NOT NULL             | Legal company name                  |
| `cnpj`               | VARCHAR(14)   | NOT NULL, UNIQUE     | Tax ID                              |
| `contrato_concessao` | VARCHAR(60)   |                      | Concession contract reference       |
| `data_inicio_contrato`| DATE         | NOT NULL             | Contract start date                 |
| `data_fim_contrato`  | DATE          |                      | Contract end date                   |
| `ativo`              | BOOLEAN       | NOT NULL, DEFAULT TRUE| Active status                      |
| `criado_em`          | TIMESTAMP     | NOT NULL, DEFAULT NOW| Record creation timestamp           |

### Table: `rodovia` (Highway)

| Column               | Type          | Constraints          | Description                         |
|----------------------|---------------|----------------------|-------------------------------------|
| `id`                 | BIGINT        | PK, AUTO_INCREMENT   | Unique identifier                   |
| `concessionaria_id`  | BIGINT        | FK → concessionaria(id), NOT NULL | Parent concessionaire  |
| `codigo`             | VARCHAR(20)   | NOT NULL             | Highway code (e.g., BR-101)        |
| `nome`               | VARCHAR(120)  |                      | Highway name                        |
| `uf`                 | VARCHAR(2)    | NOT NULL             | State code (e.g., SP)              |
| `extensao_km`        | DECIMAL(8,2)  |                      | Highway length in km               |
| `ativa`              | BOOLEAN       | NOT NULL, DEFAULT TRUE| Active status                      |
| `criado_em`          | TIMESTAMP     | NOT NULL, DEFAULT NOW| Record creation timestamp           |

### Table: `praca_pedagio` (Toll Plaza)

| Column      | Type          | Constraints                    | Description                    |
|-------------|---------------|--------------------------------|--------------------------------|
| `id`        | BIGINT        | PK, AUTO_INCREMENT             | Unique plaza identifier        |
| `rodovia_id`| BIGINT        | FK → rodovia(id), NOT NULL     | Parent highway                 |
| `nome`      | VARCHAR(120)  |                                | Plaza name                     |
| `km`        | DECIMAL(8,3)  | NOT NULL                       | Kilometer position on highway  |
| `sentido`   | VARCHAR(20)   |                                | Direction (NORTE, SUL, AMBOS)  |
| `ativa`     | BOOLEAN       | NOT NULL, DEFAULT TRUE         | Active status                  |
| `criado_em` | TIMESTAMP     | NOT NULL, DEFAULT NOW()        | Record creation timestamp      |

### Table: `pista_pedagio` (Toll Lane)

| Column        | Type          | Constraints                          | Description                    |
|---------------|---------------|--------------------------------------|--------------------------------|
| `id`          | BIGINT        | PK, AUTO_INCREMENT                   | Unique lane identifier         |
| `praca_id`    | BIGINT        | FK → praca_pedagio(id), NOT NULL     | Parent plaza                   |
| `numero_pista`| INTEGER       | NOT NULL                             | Lane number within the plaza   |
| `tipo_pista`  | VARCHAR(20)   | NOT NULL                             | Lane type: MANUAL, TAG, MISTA  |
| `sentido`     | VARCHAR(20)   |                                      | Direction                      |
| `ativa`       | BOOLEAN       | NOT NULL, DEFAULT TRUE               | Active status                  |
| `criado_em`   | TIMESTAMP     | NOT NULL, DEFAULT NOW()              | Record creation timestamp      |
| —             | —             | UNIQUE(praca_id, numero_pista)       | No duplicate lane per plaza    |

### Table: `tarifa_pedagio` (Toll Rate)

| Column           | Type          | Constraints          | Description                    |
|------------------|---------------|----------------------|--------------------------------|
| `id`             | BIGINT        | PK, AUTO_INCREMENT   | Unique tariff identifier       |
| `tipo_veiculo`   | VARCHAR(20)   | NOT NULL             | Vehicle type: MOTO, CARRO, CAMINHAO |
| `valor`          | DECIMAL(10,2) | NOT NULL             | Tariff amount                  |
| `vigencia_inicio`| DATE          | NOT NULL             | Effective start date           |
| `vigencia_fim`   | DATE          |                      | Effective end date             |
| `criado_em`      | TIMESTAMP     | NOT NULL, DEFAULT NOW| Record creation timestamp      |

### Table: `operador` (Operator)

| Column           | Type          | Constraints          | Description                    |
|------------------|---------------|----------------------|--------------------------------|
| `id`             | BIGINT        | PK, AUTO_INCREMENT   | Unique operator identifier     |
| `username`       | VARCHAR(50)   | NOT NULL, UNIQUE     | Login username                 |
| `password`       | VARCHAR(255)  | NOT NULL             | Hashed password                |
| `nome_completo`  | VARCHAR(100)  | NOT NULL             | Full name                      |
| `email`          | VARCHAR(100)  | NOT NULL, UNIQUE     | Email address                  |
| `telefone`       | VARCHAR(20)   |                      | Phone number                   |
| `ativo`          | BOOLEAN       | NOT NULL, DEFAULT TRUE| Active status                 |
| `criado_em`      | TIMESTAMP     | NOT NULL, DEFAULT NOW| Record creation timestamp      |
| `atualizado_em`  | TIMESTAMP     |                      | Last update timestamp          |

### Table: `transacao_pedagio` (Toll Transaction)

| Column             | Type          | Constraints                          | Description                          |
|--------------------|---------------|--------------------------------------|--------------------------------------|
| `id`               | BIGINT        | PK, AUTO_INCREMENT                   | Unique transaction identifier        |
| `praca_id`         | BIGINT        | FK → praca_pedagio(id), NOT NULL     | Plaza where transaction occurred     |
| `pista_id`         | BIGINT        | FK → pista_pedagio(id), NOT NULL     | Lane where transaction occurred      |
| `tarifa_id`        | BIGINT        | FK → tarifa_pedagio(id), NOT NULL    | Applied tariff                       |
| `data_hora_passagem`| TIMESTAMP    | NOT NULL                             | Passage date/time                    |
| `placa`            | VARCHAR(10)   | NOT NULL                             | Vehicle license plate                |
| `tag_id`           | VARCHAR(40)   |                                      | Electronic toll tag identifier       |
| `tipo_veiculo`     | VARCHAR(20)   | NOT NULL                             | Vehicle type: MOTO, CARRO, CAMINHAO  |
| `valor_original`   | DECIMAL(10,2) | NOT NULL                             | Original transaction amount          |
| `status_transacao` | VARCHAR(20)   | NOT NULL                             | Status: OK, OCORRENCIA, CORRIGIDA    |
| `hash_integridade` | VARCHAR(128)  | NOT NULL                             | Integrity hash (SHA-256)             |
| `criado_em`        | TIMESTAMP     | NOT NULL, DEFAULT NOW()              | Record creation timestamp            |

### Table: `ocorrencia_transacao` (Transaction Occurrence)

| Column                     | Type          | Constraints                            | Description                          |
|----------------------------|---------------|----------------------------------------|--------------------------------------|
| `id`                       | BIGINT        | PK, AUTO_INCREMENT                     | Unique identifier                    |
| `transacao_id`             | BIGINT        | FK → transacao_pedagio(id), NOT NULL   | Parent transaction                   |
| `tipo_ocorrencia`          | VARCHAR(30)   | NOT NULL                               | Type: EVASAO, TAG_BLOQUEADA, SEM_SALDO, FALHA_LEITURA |
| `observacao`               | TEXT          |                                        | Additional notes                     |
| `detectada_automaticamente`| BOOLEAN       | NOT NULL, DEFAULT TRUE                 | Whether auto-detected                |
| `criado_em`                | TIMESTAMP     | NOT NULL, DEFAULT NOW()                | Record creation timestamp            |

### Table: `correcao_transacao` (Transaction Correction)

| Column           | Type          | Constraints                            | Description                          |
|------------------|---------------|----------------------------------------|--------------------------------------|
| `id`             | BIGINT        | PK, AUTO_INCREMENT                     | Unique identifier                    |
| `transacao_id`   | BIGINT        | FK → transacao_pedagio(id), NOT NULL   | Parent transaction                   |
| `operador_id`    | BIGINT        | FK → operador(id), NOT NULL            | Operator who performed correction    |
| `motivo`         | TEXT          | NOT NULL                               | Correction reason                    |
| `valor_anterior` | DECIMAL(10,2) | NOT NULL                               | Previous amount                      |
| `valor_corrigido`| DECIMAL(10,2) | NOT NULL                               | Corrected amount                     |
| `tipo_correcao`  | VARCHAR(20)   | NOT NULL                               | Type: MANUAL, AUTOMATICA             |
| `criado_em`      | TIMESTAMP     | NOT NULL, DEFAULT NOW()                | Record creation timestamp            |

### Table: `registro_performance` (Performance Metrics)

| Column                  | Type             | Constraints          | Description                          |
|-------------------------|------------------|----------------------|--------------------------------------|
| `id`                    | BIGINT           | PK, AUTO_INCREMENT   | Unique identifier                    |
| `endpoint`              | VARCHAR(255)     | NOT NULL             | API endpoint path                    |
| `metodo_http`           | VARCHAR(10)      | NOT NULL             | HTTP method                          |
| `tempo_processamento_ms`| BIGINT           | NOT NULL             | Processing time in milliseconds      |
| `memoria_usada_mb`      | DOUBLE PRECISION | NOT NULL             | Used memory in MB                    |
| `memoria_livre_mb`      | DOUBLE PRECISION | NOT NULL             | Free memory in MB                    |
| `memoria_total_mb`      | DOUBLE PRECISION | NOT NULL             | Total memory in MB                   |
| `uso_cpu_processo`      | DOUBLE PRECISION | NOT NULL             | CPU usage ratio                      |
| `threads_ativas`        | INTEGER          | NOT NULL             | Active thread count                  |
| `status_http`           | INTEGER          | NOT NULL             | HTTP response status code            |
| `ip_cliente`            | VARCHAR(45)      |                      | Client IP address                    |
| `user_agent`            | VARCHAR(255)     |                      | Client user agent                    |
| `parametros`            | TEXT             |                      | Request parameters                   |
| `erro`                  | TEXT             |                      | Error details (if any)               |
| `origem_dados`          | VARCHAR(20)      |                      | Data source: BANCO_DADOS, CACHE_LOCAL, CACHE_REDIS, NAO_APLICAVEL |
| `criado_em`             | TIMESTAMP        | NOT NULL, DEFAULT NOW| Record creation timestamp            |

---

## Indexes

| Table                | Index Name                     | Columns                 | Purpose                            |
|----------------------|--------------------------------|-------------------------|------------------------------------|
| `rodovia`            | `idx_rodovia_concessionaria`   | `concessionaria_id`     | Join optimization                  |
| `rodovia`            | `idx_rodovia_uf`               | `uf`                    | Filter highways by state           |
| `praca_pedagio`      | `idx_praca_rodovia`            | `rodovia_id`            | Join optimization                  |
| `pista_pedagio`      | `idx_pista_praca`              | `praca_id`              | Join optimization                  |
| `transacao_pedagio`  | `idx_transacao_praca`          | `praca_id`              | Join optimization                  |
| `transacao_pedagio`  | `idx_transacao_pista`          | `pista_id`              | Join optimization                  |
| `transacao_pedagio`  | `idx_transacao_tarifa`         | `tarifa_id`             | Join optimization                  |
| `transacao_pedagio`  | `idx_transacao_status`         | `status_transacao`      | Filter by transaction status       |
| `transacao_pedagio`  | `idx_transacao_placa`          | `placa`                 | Vehicle plate lookups              |
| `transacao_pedagio`  | `idx_transacao_data`           | `data_hora_passagem`    | Time-range queries                 |
| `ocorrencia_transacao`| `idx_ocorrencia_transacao`    | `transacao_id`          | Join optimization                  |
| `correcao_transacao` | `idx_correcao_transacao`       | `transacao_id`          | Join optimization                  |
| `correcao_transacao` | `idx_correcao_operador`        | `operador_id`           | Join optimization                  |
| `registro_performance`| `idx_performance_endpoint`    | `endpoint`              | Filter by endpoint                 |
| `registro_performance`| `idx_performance_criado`      | `criado_em`             | Time-range queries                 |

---

## Cache Key Strategy (Redis)

Data cached in Redis uses the following key naming conventions:

| Pattern                                    | Example                               | TTL      | Description                     |
|--------------------------------------------|---------------------------------------|----------|---------------------------------|
| `transacoes:ocorrencias:{limite}:{horas}`  | `transacoes:ocorrencias:100:24`       | 60 min   | Transactions with occurrences   |
| `praca:{id}`                               | `praca:1`                             | 60 min   | Single plaza by ID              |
| `pista:{id}`                               | `pista:42`                            | 60 min   | Single lane by ID               |
| `transacao:{id}`                           | `transacao:100`                       | 60 min   | Single transaction by ID        |

---

## Data Synchronization Strategy

### Write Operations

1. **Kafka Ingestion** → Toll Simulator produces `TransacaoPedagioKafkaDTO` → Kafka consumer persists to PostgreSQL
2. **Transaction Correction** → Update PostgreSQL → Invalidate Redis cache → Return confirmation

### Read Operations (Cache-Aside with OrigemDados Tracking)

1. Check L1 cache (ConcurrentHashMap, in-app) → marks `CACHE_LOCAL`
2. Check L2 cache (Redis) → marks `CACHE_REDIS`
3. Query PostgreSQL on cache miss → marks `BANCO_DADOS`
4. Populate L1 and L2 caches with result
5. Record performance metrics in `registro_performance` via `PerformanceInterceptor`

### Cache Invalidation

- **TTL-based**: Automatic expiry (L1: 30 min, L2: 60 min — configurable)
- **Event-driven**: Explicit invalidation on write operations
- **Max size**: L1 local cache limited to 1000 entries (configurable)
