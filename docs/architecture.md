# Architecture

## High-Level Architecture

The Smart Toll Cache System follows a **distributed microservices architecture** with multi-layer caching and load balancing designed for real-time toll transaction management under high concurrency.

```
                    ┌──────────────────────────────┐
                    │        Client Layer           │
                    │                               │
                    │  ┌────────────┐ ┌──────────┐  │
                    │  │   React    │ │  Python   │  │
                    │  │  Frontend  │ │ Simulator │  │
                    │  └─────┬──────┘ └─────┬─────┘  │
                    └────────┼──────────────┼────────┘
                             │              │
                             ▼              ▼
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
    │  Spring Boot #1  │ │  Spring Boot #2  │ │  Spring Boot #N  │
    │                  │ │                  │ │                  │
    │  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
    │  │ L1 Cache   │  │ │  │ L1 Cache   │  │ │  │ L1 Cache   │  │
    │  │ (Caffeine) │  │ │  │ (Caffeine) │  │ │  │ (Caffeine) │  │
    │  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
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
    │  - Key-Value     │ │  - Praca         │
    │  - TTL: 10min    │ │  - Pista         │
    │  - LRU eviction  │ │  - Transacao     │
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

### 2. Toll Management Service — Spring Boot (Java 17)

- **Role**: Core business logic microservice
- **Responsibilities**:
  - Toll plaza, lane, and transaction CRUD operations
  - Real-time transaction correction workflow
  - Multi-layer cache management (L1 Caffeine + L2 Redis)
  - Performance metrics collection via interceptors
  - RESTful API exposure
- **Cache Strategy**: Cache-Aside with TTL-based expiration
- **Scaling**: Horizontal — multiple instances behind NGINX

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
  - Persistent storage for all toll management data
  - Relational integrity (foreign keys, constraints)
  - Indexed queries for transaction lookups
  - Entities: `Praca` (Plaza), `Pista` (Lane), `Transacao` (Transaction)

### 6. Python Simulators

- **Role**: Load testing and scenario simulation
- **Responsibilities**:
  - Simulate toll booth transaction flow at scale
  - Simulate transaction correction operations under concurrency
  - Generate up to 500 concurrent users for stress testing
  - Produce metrics for comparative analysis

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
│  Client  │─────▶│   NGINX   │─────▶│ Spring  │─────▶│ L1 Cache   │
│          │      │           │      │  Boot   │      │ (Caffeine) │
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
| `toll-service-1..N`        | toll-management    | 8080       |
| `redis`                    | redis:7-alpine     | 6379       |
| `postgres`                 | postgres:14-alpine | 5432       |
| `toll-frontend`            | toll-frontend      | 3000       |
| `prometheus`               | prom/prometheus    | 9090       |
| `grafana`                  | grafana/grafana    | 3001       |

---

## Scaling Strategy

- **Horizontal scaling**: Add more Spring Boot instances; update NGINX upstream configuration
- **Cache scaling**: Redis cluster with sharding for large-scale deployments
- **Database scaling**: Read replicas for PostgreSQL (future enhancement)
- **Load balancing algorithms**: Configurable per deployment (round-robin, least-connections, IP-hash)
