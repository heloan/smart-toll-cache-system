# UML Diagrams

All diagrams are rendered using [Mermaid](https://mermaid.js.org/) syntax.

---

## 1. Component Diagram

```mermaid
graph TB
    subgraph Client Layer
        FE[React Frontend<br/>Operator Dashboard]
        SIM[Simulador<br/>Python CLI + GUI<br/>Kafka Producer]
    end

    subgraph Gateway Layer
        NGINX[NGINX<br/>Reverse Proxy + Load Balancer<br/>Port 80]
    end

    subgraph Application Layer
        SB1[Rodovia Instance 1<br/>L1 Cache - ConcurrentHashMap<br/>Port 9080]
        SB2[Rodovia Instance 2<br/>L1 Cache - ConcurrentHashMap<br/>Port 9080]
        SBN[Rodovia Instance N<br/>L1 Cache - ConcurrentHashMap<br/>Port 9080]
    end

    subgraph Messaging Layer
        KAFKA[Apache Kafka<br/>Topic: transacao-pedagio<br/>Port 9092]
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
    SIM --> KAFKA
    KAFKA --> SB1
    KAFKA --> SB2
    KAFKA --> SBN
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
    participant SB as Rodovia Service
    participant L1 as L1 Cache (ConcurrentHashMap)
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
    participant SB as Rodovia Service
    participant L1 as L1 Cache (ConcurrentHashMap)
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
    participant SB as Rodovia Service
    participant REDIS as Redis (L2 Cache)
    participant PG as PostgreSQL

    Operator->>FE: Submit correction for transaction #100
    FE->>NGINX: PUT /api/correcoes/transacao/100
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
    class Concessionaria {
        -Long id
        -String nomeFantasia
        -String razaoSocial
        -String cnpj
        -String contratoConcessao
        -LocalDate dataInicioContrato
        -LocalDate dataFimContrato
        -Boolean ativo
        -LocalDateTime criadoEm
        +getRodovias() List~Rodovia~
    }

    class Rodovia {
        -Long id
        -String codigo
        -String nome
        -String uf
        -BigDecimal extensaoKm
        -Boolean ativa
        -LocalDateTime criadoEm
        +getPracasPedagio() List~PracaPedagio~
    }

    class PracaPedagio {
        -Long id
        -String nome
        -BigDecimal km
        -String sentido
        -Boolean ativa
        -LocalDateTime criadoEm
        +getPistas() List~PistaPedagio~
        +getTransacoes() List~TransacaoPedagio~
    }

    class PistaPedagio {
        -Long id
        -Integer numeroPista
        -TipoPistaEnum tipoPista
        -String sentido
        -Boolean ativa
        -LocalDateTime criadoEm
        +getTransacoes() List~TransacaoPedagio~
    }

    class TarifaPedagio {
        -Long id
        -TipoVeiculoEnum tipoVeiculo
        -BigDecimal valor
        -LocalDate vigenciaInicio
        -LocalDate vigenciaFim
        -LocalDateTime criadoEm
    }

    class TransacaoPedagio {
        -Long id
        -LocalDateTime dataHoraPassagem
        -String placa
        -String tagId
        -TipoVeiculoEnum tipoVeiculo
        -BigDecimal valorOriginal
        -StatusTransacaoEnum statusTransacao
        -String hashIntegridade
        -LocalDateTime criadoEm
        +getOcorrencias() List~OcorrenciaTransacao~
        +getCorrecoes() List~CorrecaoTransacao~
    }

    class OcorrenciaTransacao {
        -Long id
        -TipoOcorrenciaEnum tipoOcorrencia
        -String observacao
        -Boolean detectadaAutomaticamente
        -LocalDateTime criadoEm
    }

    class CorrecaoTransacao {
        -Long id
        -String motivo
        -BigDecimal valorAnterior
        -BigDecimal valorCorrigido
        -TipoCorrecaoEnum tipoCorrecao
        -LocalDateTime criadoEm
    }

    class Operador {
        -Long id
        -String username
        -String password
        -String nomeCompleto
        -String email
        -String telefone
        -Boolean ativo
        -LocalDateTime criadoEm
        +getCorrecoes() List~CorrecaoTransacao~
    }

    class RegistroPerformance {
        -Long id
        -String endpoint
        -String metodoHttp
        -Long tempoProcessamentoMs
        -Double memoriaUsadaMb
        -Double usoCpuProcesso
        -Integer statusHttp
        -OrigemDadosEnum origemDados
        -LocalDateTime criadoEm
    }

    Concessionaria "1" --> "*" Rodovia : manages
    Rodovia "1" --> "*" PracaPedagio : contains
    PracaPedagio "1" --> "*" PistaPedagio : has
    PracaPedagio "1" --> "*" TransacaoPedagio : processes
    PistaPedagio "1" --> "*" TransacaoPedagio : processes
    TarifaPedagio "1" --> "*" TransacaoPedagio : applies
    TransacaoPedagio "1" --> "*" OcorrenciaTransacao : has
    TransacaoPedagio "1" --> "*" CorrecaoTransacao : has
    Operador "1" --> "*" CorrecaoTransacao : performs
```

---

## 6. Deployment Diagram

```mermaid
graph LR
    subgraph Docker Host
        subgraph Containers
            NGINX[NGINX :80]
            SB1[Rodovia :9080]
            SB2[Rodovia :9080]
            SB3[Rodovia :9080]
            KAFKA[Kafka :9092]
            ZK[Zookeeper :2181]
            REDIS[Redis :6379]
            PG[PostgreSQL :5432]
            FE[React :3000]
            SIM[Simulador]
            PROM[Prometheus :9090]
            GRAF[Grafana :3001]
        end
    end

    SB1 --> REDIS
    SB2 --> REDIS
    SB3 --> REDIS
    SB1 --> PG
    SB2 --> PG
    SB3 --> PG
    KAFKA --> SB1
    KAFKA --> SB2
    KAFKA --> SB3
    SIM --> KAFKA
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
    A[Request Received] --> B{Check L1 Cache<br/>ConcurrentHashMap}
    B -->|HIT| C[Return Cached Data]
    B -->|MISS| D{Check L2 Cache<br/>Redis}
    D -->|HIT| E[Populate L1 Cache]
    E --> C
    D -->|MISS| F[Query PostgreSQL]
    F --> G[Populate L2 Cache<br/>Redis]
    G --> H[Populate L1 Cache<br/>ConcurrentHashMap]
    H --> C
```
