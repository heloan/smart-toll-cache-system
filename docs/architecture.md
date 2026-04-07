# Architecture

## High-Level Architecture

The Smart Toll Cache System follows a **distributed microservices architecture** with multi-layer caching and load balancing designed for real-time toll transaction management under high concurrency.

```
                    ┌──────────────────────────────┐
                    │        Client Layer           │
                    │                               │
                    │  ┌────────────┐ ┌──────────┐  │
                    │  │   React    │ │ Simulador │  │
                    │  │  Frontend  │ │ (Python)  │  │
                    │  └─────┬──────┘ └─────┬─────┘  │
                    └────────┼──────────────┼────────┘
                             │              │
                             │              ▼
                             │     ┌──────────────────┐
                             │     │   Apache Kafka    │
                             │     │ (Async Messaging) │
                             │     └────────┬─────────┘
                             ▼               │
                    ┌──────────────────────────────┐
                    │       Gateway Layer           │
                    │                               │
                    │  ┌──────────────────────────┐ │
                    │  │         NGINX             │ │
                    │  │   Reverse Proxy + LB      │ │
                    │  │      (Port 80)            │ │
                    │  └────┬──────┬──────┬───────┘ │
                    └───────┼──────┼──────┼─────────┘
                            │      │      │
               ┌────────────┘      │      └────────────┐
               ▼                   ▼                    ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │  Rodovia #1      │ │  Rodovia #2      │ │  Rodovia #N      │
    │  (Spring Boot)   │ │  (Spring Boot)   │ │  (Spring Boot)   │
    │  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
    │  │ L1 Cache   │  │ │  │ L1 Cache   │  │ │  │ L1 Cache   │  │
    │  │ (HashMap)  │  │ │  │ (HashMap)  │  │ │  │ (HashMap)  │  │
    │  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
    │  Port 9080       │ │  Port 9080       │ │  Port 9080       │
    │  Kafka Consumer  │ │  Kafka Consumer  │ │  Kafka Consumer  │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                     │
             └────────────┬───────┘─────────────────────┘
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
    ┌──────────────────┐ ┌──────────────────┐
    │      Redis       │ │   PostgreSQL     │
    │   (L2 Cache)     │ │    (SSOT)        │
    │                  │ │                  │
    │  - Key-Value     │ │  - Concessionaria│
    │  - TTL: 60min    │ │  - Rodovia       │
    │  - LRU eviction  │ │  - PracaPedagio  │
    │                  │ │  - PistaPedagio  │
    │                  │ │  - TransacaoPed. │
    │                  │ │  - + 5 more      │
    └──────────────────┘ └──────────────────┘
```

---

## Component Descriptions

### 1. NGINX — API Gateway / Load Balancer

- **Role**: Entry point for all client requests
- **Responsibilities**:
  - Reverse proxy routing to backend instances
  - Load balancing (round-robin, least connections, IP hash)
  - SSL termination (production)
  - Static content serving for React frontend
- **Port**: 80 (HTTP)

### 2. Rodovia Service — Spring Boot 4.0.3 (Java 21)

- **Role**: Core business logic microservice (`com.tcc.rodovia`)
- **Responsibilities**:
  - Full CRUD for Rodovia, Concessionaria, PracaPedagio, PistaPedagio, TarifaPedagio, Operador
  - Transaction ingestion via Kafka consumer (topic: `transacao-pedagio`)
  - Real-time transaction correction workflow (OcorrenciaTransacao, CorrecaoTransacao)
  - Multi-layer cache management (L1 ConcurrentHashMap + L2 Redis)
  - Performance metrics collection via interceptors (RegistroPerformance)
  - RESTful API exposure on port **9080**
- **Cache Strategy**: Cache-Aside with TTL-based expiration (L1: 30min, L2: 60min)
- **Scaling**: Horizontal — multiple instances behind NGINX
- **Security**: Spring Security configured via SecurityConfig

### 3. React Frontend

- **Role**: Operator dashboard for toll booth management
- **Responsibilities**:
  - Transaction search and correction interface
  - Real-time status display
  - Communication with backend via REST API through NGINX

### 4. Redis — Distributed Cache (L2)

- **Role**: Shared in-memory data store
- **Responsibilities**:
  - Distributed cache accessible by all backend instances
  - Key-value storage with automatic TTL expiration (10 minutes)
  - LRU eviction policy for memory management
  - Support for clustering and sharding at scale
- **Configuration**: Standalone (dev) / Cluster with sharding (production)

### 5. PostgreSQL — Relational Database

- **Role**: Single Source of Truth (SSOT)
- **Responsibilities**:
  - Persistent storage for all toll management data (10 tables)
  - Relational integrity (foreign keys, constraints)
  - Indexed queries for transaction lookups
  - Entities: `concessionaria`, `rodovia`, `praca_pedagio`, `pista_pedagio`, `tarifa_pedagio`, `transacao_pedagio`, `ocorrencia_transacao`, `correcao_transacao`, `operador`, `registro_performance`

### 6. Apache Kafka — Async Messaging

- **Role**: Decoupled transaction ingestion pipeline
- **Responsibilities**:
  - Producer: simulador sends `TransacaoPedagioKafkaDTO` to topic `transacao-pedagio`
  - Consumer: rodovia's `TransacaoKafkaConsumer` persists transactions to PostgreSQL
  - Guarantees: `acks=all`, ordered delivery, auto-create topics

### 7. Simulador (Python CLI + GUI)

- **Role**: Toll transaction simulation and load testing
- **Responsibilities**:
  - Generate realistic toll transactions via `TransacaoGenerator` (uses Faker)
  - Produce transactions to Kafka with configurable rate (`--rate`) and error rate (`--error-rate`)
  - Intentional error injection (invalid plates, wrong values, duplicate tags, time inconsistencies)
  - CLI mode (`main.py`) and GUI mode (`gui.py` — tkinter)
  - Stress test mode (`--stress`) for high-throughput scenarios
  - Statistics tracking and reporting

### 7. Prometheus + Grafana — Observability Stack

- **Role**: Monitoring and visualization
- **Responsibilities**:
  - Prometheus: scrape metrics from Spring Boot Actuator endpoints
  - Grafana: dashboards for latency, throughput, cache hit rate, resource usage
  - Alerting on performance degradation thresholds

---

## Data Flow — Cache-Aside Pattern

```
┌─────────┐      ┌───────────┐      ┌─────────┐      ┌────────────┐
│  Client  │─────▶│   NGINX   │─────▶│ Rodovia │─────▶│ L1 Cache   │
│          │      │           │      │ Service │      │ (HashMap)  │
└─────────┘      └───────────┘      └────┬────┘      └─────┬──────┘
                                         │                  │
                                         │            HIT? ─┤
                                         │           YES    │ NO
                                         │            ▼     ▼
                                         │     ┌────────────────┐
                                         │     │  L2 Cache      │
                                         │     │  (Redis)       │
                                         │     └───────┬────────┘
                                         │             │
                                         │       HIT? ─┤
                                         │      YES    │ NO
                                         │       ▼     ▼
                                         │     ┌────────────────┐
                                         │     │  PostgreSQL    │
                                         │     │  (Database)    │
                                         │     └───────┬────────┘
                                         │             │
                                         ◀─────────────┘
                                    Populate L1 + L2
```

---

## Deployment Architecture

All services are containerized with Docker and orchestrated via Docker Compose:

| Container                  | Image              | Port(s)    |
|----------------------------|--------------------|------------|
| `nginx`                    | nginx:latest       | 80         |
| `rodovia-1..N`             | rodovia            | 9080       |
| `redis`                    | redis:7-alpine     | 6379       |
| `postgres`                 | postgres:15-alpine | 5432       |
| `zookeeper`                | cp-zookeeper:7.5.0 | 2181       |
| `kafka`                    | cp-kafka:7.5.0     | 9092       |
| `simulador`                | simulador          | —          |
| `toll-frontend`            | toll-frontend      | 3000       |
| `prometheus`               | prom/prometheus    | 9090       |
| `grafana`                  | grafana/grafana    | 3001       |

---

## Scaling Strategy

- **Horizontal scaling**: Add more Spring Boot instances; update NGINX upstream configuration
- **Cache scaling**: Redis cluster with sharding for large-scale deployments
- **Database scaling**: Read replicas for PostgreSQL (future enhancement)
- **Load balancing algorithms**: Configurable per deployment (round-robin, least-connections, IP-hash)
