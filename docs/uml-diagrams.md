# UML Diagrams

All diagrams are rendered using [Mermaid](https://mermaid.js.org/) syntax.

---

## 1. Component Diagram

```mermaid
graph TB
    subgraph Client Layer
        FE[React Frontend<br/>Operator Dashboard]
        SIM[Python Simulator<br/>Load Generator]
    end

    subgraph Gateway Layer
        NGINX[NGINX<br/>Reverse Proxy + Load Balancer<br/>Port 80]
    end

    subgraph Application Layer
        SB1[Spring Boot Instance 1<br/>L1 Cache - Caffeine]
        SB2[Spring Boot Instance 2<br/>L1 Cache - Caffeine]
        SBN[Spring Boot Instance N<br/>L1 Cache - Caffeine]
    end

    subgraph Data Layer
        REDIS[(Redis<br/>L2 Distributed Cache<br/>Port 6379)]
        PG[(PostgreSQL<br/>SSOT - Relational DB<br/>Port 5432)]
    end

    subgraph Observability Layer
        PROM[Prometheus<br/>Metrics Scraper<br/>Port 9090]
        GRAF[Grafana<br/>Dashboards<br/>Port 3001]
    end

    FE --> NGINX
    SIM --> NGINX
    NGINX --> SB1
    NGINX --> SB2
    NGINX --> SBN
    SB1 --> REDIS
    SB2 --> REDIS
    SBN --> REDIS
    SB1 --> PG
    SB2 --> PG
    SBN --> PG
    PROM --> SB1
    PROM --> SB2
    PROM --> SBN
    GRAF --> PROM
```

---

## 2. Sequence Diagram — Transaction Correction (Cache Hit on Redis)

```mermaid
sequenceDiagram
    actor Operator
    participant FE as React Frontend
    participant NGINX as NGINX LB
    participant SB as Spring Boot
    participant L1 as L1 Cache (Caffeine)
    participant REDIS as Redis (L2 Cache)
    participant PG as PostgreSQL

    Operator->>FE: Search transaction by plate
    FE->>NGINX: GET /api/transacoes?placa=ABC1234
    NGINX->>SB: Forward request (round-robin)
    SB->>L1: Check L1 cache
    L1-->>SB: MISS
    SB->>REDIS: Check L2 cache
    REDIS-->>SB: HIT (cached transaction data)
    SB->>L1: Populate L1 cache
    SB-->>NGINX: 200 OK (transaction data)
    NGINX-->>FE: Response
    FE-->>Operator: Display transaction details
```

---

## 3. Sequence Diagram — Transaction Correction (Cache Miss — Full Path)

```mermaid
sequenceDiagram
    actor Operator
    participant FE as React Frontend
    participant NGINX as NGINX LB
    participant SB as Spring Boot
    participant L1 as L1 Cache (Caffeine)
    participant REDIS as Redis (L2 Cache)
    participant PG as PostgreSQL

    Operator->>FE: Search transaction by tag
    FE->>NGINX: GET /api/transacoes?tag=TAG001
    NGINX->>SB: Forward request
    SB->>L1: Check L1 cache
    L1-->>SB: MISS
    SB->>REDIS: Check L2 cache
    REDIS-->>SB: MISS
    SB->>PG: SELECT * FROM transacao WHERE tag = 'TAG001'
    PG-->>SB: Result set
    SB->>REDIS: SET transacao:tag:TAG001 (TTL 5min)
    SB->>L1: Populate L1 cache
    SB-->>NGINX: 200 OK (transaction data)
    NGINX-->>FE: Response
    FE-->>Operator: Display transaction details
```

---

## 4. Sequence Diagram — Transaction Correction Write

```mermaid
sequenceDiagram
    actor Operator
    participant FE as React Frontend
    participant NGINX as NGINX LB
    participant SB as Spring Boot
    participant REDIS as Redis (L2 Cache)
    participant PG as PostgreSQL

    Operator->>FE: Submit correction for transaction #100
    FE->>NGINX: PUT /api/transacoes/100/corrigir
    NGINX->>SB: Forward request
    SB->>PG: UPDATE transacao SET corrigida=true, status='CORRIGIDA' WHERE id=100
    PG-->>SB: Updated
    SB->>REDIS: DEL transacao:100
    SB->>REDIS: DEL transacao:pendentes:pista:{pistaId}
    SB-->>NGINX: 200 OK (correction confirmed)
    NGINX-->>FE: Response
    FE-->>Operator: Correction confirmed
```

---

## 5. Class Diagram — Domain Model

```mermaid
classDiagram
    class Praca {
        -Long id
        -String nome
        -String rodovia
        -BigDecimal km
        -String uf
        -LocalDateTime createdAt
        -LocalDateTime updatedAt
        +getPistas() List~Pista~
    }

    class Pista {
        -Long id
        -Integer numero
        -String tipo
        -String status
        -Long pracaId
        -LocalDateTime createdAt
        -LocalDateTime updatedAt
        +getTransacoes() List~Transacao~
    }

    class Transacao {
        -Long id
        -String tipo
        -String status
        -BigDecimal valor
        -String placa
        -String tag
        -LocalDateTime dataHora
        -Boolean corrigida
        -Long pistaId
        -LocalDateTime createdAt
        -LocalDateTime updatedAt
        +corrigir() void
    }

    Praca "1" --> "*" Pista : contains
    Pista "1" --> "*" Transacao : processes
```

---

## 6. Deployment Diagram

```mermaid
graph LR
    subgraph Docker Host
        subgraph Containers
            NGINX[NGINX :80]
            SB1[Spring Boot :8080]
            SB2[Spring Boot :8081]
            SB3[Spring Boot :8082]
            REDIS[Redis :6379]
            PG[PostgreSQL :5432]
            FE[React :3000]
            PROM[Prometheus :9090]
            GRAF[Grafana :3001]
        end
    end

    NGINX --> SB1
    NGINX --> SB2
    NGINX --> SB3
    SB1 --> REDIS
    SB2 --> REDIS
    SB3 --> REDIS
    SB1 --> PG
    SB2 --> PG
    SB3 --> PG
    PROM --> SB1
    PROM --> SB2
    PROM --> SB3
    GRAF --> PROM
    FE --> NGINX
```

---

## 7. Activity Diagram — Cache Lookup Flow

```mermaid
flowchart TD
    A[Request Received] --> B{Check L1 Cache<br/>Caffeine}
    B -->|HIT| C[Return Cached Data]
    B -->|MISS| D{Check L2 Cache<br/>Redis}
    D -->|HIT| E[Populate L1 Cache]
    E --> C
    D -->|MISS| F[Query PostgreSQL]
    F --> G[Populate L2 Cache<br/>Redis]
    G --> H[Populate L1 Cache<br/>Caffeine]
    H --> C
```
