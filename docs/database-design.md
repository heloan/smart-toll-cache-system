# Database Design

## Overview

The data model supports real-time toll transaction management, including toll plazas, lanes, and vehicle transactions. PostgreSQL serves as the **Single Source of Truth (SSOT)**, with Redis providing a distributed cache layer for frequently accessed data.

---

## Entity-Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────────┐
│       Praca          │       │       Pista          │       │       Transacao           │
│  (Toll Plaza)        │       │   (Toll Lane)        │       │    (Transaction)          │
├─────────────────────┤       ├─────────────────────┤       ├─────────────────────────┤
│ PK  id        BIGINT │──┐   │ PK  id        BIGINT │──┐   │ PK  id          BIGINT   │
│     nome      VARCHAR│  │   │     numero    INT     │  │   │     tipo        VARCHAR  │
│     rodovia   VARCHAR│  │   │     tipo      VARCHAR │  │   │     status      VARCHAR  │
│     km        DECIMAL│  │   │     status    VARCHAR │  │   │     valor       DECIMAL  │
│     uf        CHAR(2)│  │   │ FK  praca_id  BIGINT  │◀─┘   │     placa       VARCHAR  │
│     created_at TIMESTAMP│  │     created_at TIMESTAMP│      │     tag         VARCHAR  │
│     updated_at TIMESTAMP│  │     updated_at TIMESTAMP│      │     data_hora   TIMESTAMP│
└─────────────────────┘  │   └─────────────────────┘  │      │     corrigida   BOOLEAN  │
                          │              ▲              │      │ FK  pista_id    BIGINT   │◀─┘
                          │              │              │      │     created_at  TIMESTAMP│
                          └──────────────┘ 1:N          └─────│     updated_at  TIMESTAMP│
                                                              └─────────────────────────┘
                                    1:N
```

### Relationships

- **Praca → Pista**: One-to-Many (1:N) — A toll plaza has many lanes
- **Pista → Transacao**: One-to-Many (1:N) — A lane processes many transactions

---

## Schema Definitions

### Table: `praca` (Toll Plaza)

| Column      | Type          | Constraints          | Description                    |
|-------------|---------------|----------------------|--------------------------------|
| `id`        | BIGINT        | PK, AUTO_INCREMENT   | Unique plaza identifier        |
| `nome`      | VARCHAR(255)  | NOT NULL             | Plaza name                     |
| `rodovia`   | VARCHAR(100)  | NOT NULL             | Highway name/code              |
| `km`        | DECIMAL(10,2) |                      | Kilometer position on highway  |
| `uf`        | CHAR(2)       | NOT NULL             | State code (e.g., SP, RJ)     |
| `created_at`| TIMESTAMP     | DEFAULT NOW()        | Record creation timestamp      |
| `updated_at`| TIMESTAMP     | DEFAULT NOW()        | Last update timestamp          |

### Table: `pista` (Toll Lane)

| Column      | Type          | Constraints          | Description                    |
|-------------|---------------|----------------------|--------------------------------|
| `id`        | BIGINT        | PK, AUTO_INCREMENT   | Unique lane identifier         |
| `numero`    | INTEGER       | NOT NULL             | Lane number within the plaza   |
| `tipo`      | VARCHAR(50)   | NOT NULL             | Lane type (manual, automatic, mixed) |
| `status`    | VARCHAR(20)   | NOT NULL, DEFAULT 'ATIVA' | Lane status (ATIVA, FECHADA, MANUTENCAO) |
| `praca_id`  | BIGINT        | FK → praca(id), NOT NULL | Parent plaza reference     |
| `created_at`| TIMESTAMP     | DEFAULT NOW()        | Record creation timestamp      |
| `updated_at`| TIMESTAMP     | DEFAULT NOW()        | Last update timestamp          |

### Table: `transacao` (Transaction)

| Column      | Type          | Constraints          | Description                    |
|-------------|---------------|----------------------|--------------------------------|
| `id`        | BIGINT        | PK, AUTO_INCREMENT   | Unique transaction identifier  |
| `tipo`      | VARCHAR(50)   | NOT NULL             | Transaction type (NORMAL, EVASAO, TAG_BLOQUEADA, PISTA_FECHADA) |
| `status`    | VARCHAR(20)   | NOT NULL, DEFAULT 'PENDENTE' | Status (PENDENTE, CORRIGIDA, CANCELADA) |
| `valor`     | DECIMAL(10,2) | NOT NULL             | Transaction amount             |
| `placa`     | VARCHAR(10)   |                      | Vehicle license plate          |
| `tag`       | VARCHAR(50)   |                      | Electronic toll tag identifier |
| `data_hora` | TIMESTAMP     | NOT NULL             | Transaction date/time          |
| `corrigida` | BOOLEAN       | DEFAULT FALSE        | Whether transaction was corrected |
| `pista_id`  | BIGINT        | FK → pista(id), NOT NULL | Lane where transaction occurred |
| `created_at`| TIMESTAMP     | DEFAULT NOW()        | Record creation timestamp      |
| `updated_at`| TIMESTAMP     | DEFAULT NOW()        | Last update timestamp          |

---

## Indexes

| Table      | Index Name                  | Columns                  | Purpose                            |
|------------|-----------------------------|--------------------------|------------------------------------|
| `praca`    | `idx_praca_uf`              | `uf`                     | Filter plazas by state             |
| `pista`    | `idx_pista_praca_id`        | `praca_id`               | Join optimization                  |
| `pista`    | `idx_pista_status`          | `status`                 | Filter active lanes                |
| `transacao`| `idx_transacao_pista_id`    | `pista_id`               | Join optimization                  |
| `transacao`| `idx_transacao_status`      | `status`                 | Filter pending transactions        |
| `transacao`| `idx_transacao_data_hora`   | `data_hora`              | Time-range queries                 |
| `transacao`| `idx_transacao_placa`       | `placa`                  | Vehicle plate lookups              |
| `transacao`| `idx_transacao_tag`         | `tag`                    | Tag-based lookups                  |

---

## Cache Key Strategy (Redis)

Data cached in Redis uses the following key naming conventions:

| Pattern                          | Example                          | TTL      | Description                     |
|----------------------------------|----------------------------------|----------|---------------------------------|
| `praca:{id}`                     | `praca:1`                        | 10 min   | Single plaza by ID              |
| `praca:list`                     | `praca:list`                     | 10 min   | All plazas                      |
| `pista:{id}`                     | `pista:42`                       | 10 min   | Single lane by ID               |
| `pista:praca:{pracaId}`          | `pista:praca:1`                  | 10 min   | All lanes for a plaza           |
| `transacao:{id}`                 | `transacao:100`                  | 5 min    | Single transaction by ID        |
| `transacao:pista:{pistaId}`      | `transacao:pista:42`             | 5 min    | Transactions for a lane         |
| `transacao:pendentes:pista:{id}` | `transacao:pendentes:pista:42`   | 2 min    | Pending transactions per lane   |

---

## Data Synchronization Strategy

### Write Operations

1. **Create/Update** → Write to PostgreSQL first → Invalidate related Redis keys
2. **Transaction Correction** → Update PostgreSQL → Update Redis cache → Return confirmation

### Read Operations (Cache-Aside)

1. Check L1 cache (Caffeine, in-app)
2. Check L2 cache (Redis)
3. Query PostgreSQL on cache miss
4. Populate L1 and L2 caches with result

### Cache Invalidation

- **TTL-based**: Automatic expiry (configurable per entity type)
- **Event-driven**: Explicit invalidation on write operations
- **Null value filtering**: Null values are not cached (`disableCachingNullValues()`)
