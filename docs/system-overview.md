# System Overview

## Project Objective

Design and evaluate a **distributed microservices-based architecture** using in-memory caching, load balancing, and synchronization between cache and relational database to optimize performance and scalability in a real-time toll management system.

### Specific Objectives

1. Model a real-time toll transaction correction system based on a distributed architecture
2. Implement caching mechanisms at different architectural layers (L1 In-App, L2 Redis)
3. Simulate representative operational loads, including request peaks of up to 500 concurrent users
4. Collect and analyze performance metrics (response time, memory usage, CPU utilization)
5. Compare results across different data access strategies, highlighting gains and limitations

---

## Problem Statement

In modern toll management, operators at toll booths must correct transactions in real-time when issues arise, such as:

- **Tag evasion**: vehicle passes without a valid tag
- **Blocked tag**: tag is deactivated or flagged
- **Closed lane access**: vehicle enters a closed or restricted lane

These corrections must happen within seconds to prevent:

- Queue buildup at toll plazas
- Elevated user stress and dissatisfaction
- Negative impacts on traffic flow
- Increased accident risk, especially during peak hours

Traditional monolithic systems fail to meet these requirements under high concurrency, making a distributed architecture essential.

---

## Solution

The proposed solution implements a **distributed toll management system** with the following core strategies:

### Multi-Layer Cache Architecture

| Layer | Technology | Scope | Latency |
|-------|-----------|-------|---------|
| L1 — In-App Cache | Caffeine / HashMap | Per-instance, local memory | Ultra-low (~μs) |
| L2 — Distributed Cache | Redis | Shared across all instances | Low (~ms) |
| L3 — Persistent Storage | PostgreSQL | Single source of truth | Higher (~10ms+) |

### Cache-Aside Strategy

1. Application checks **L1 cache** (in-app) first
2. On miss, checks **L2 cache** (Redis)
3. On miss, queries **PostgreSQL** and populates both cache layers
4. Write operations update the database and invalidate/update cache entries

### Load Balancing

**NGINX** distributes incoming requests across multiple Spring Boot instances using configurable algorithms:
- Round-robin (default)
- Least connections
- IP hash

### Data Synchronization

Cache-database consistency is maintained through:
- **Cache-Aside**: read-through pattern with lazy population
- **Write-Through**: simultaneous writes to cache and database
- **TTL-based expiration**: automatic cache invalidation after configurable intervals

---

## System Workflow

### Toll Transaction Correction Flow

```
1. Vehicle encounters issue at toll booth
   ↓
2. Operator opens React dashboard
   ↓
3. Operator searches for transaction by vehicle/tag/plaza
   ↓
4. Request hits NGINX load balancer (Port 80)
   ↓
5. NGINX forwards to available Spring Boot instance
   ↓
6. Backend checks L1 In-App Cache (Caffeine)
   ├── HIT → Return cached data immediately
   └── MISS → Check L2 Redis Cache
               ├── HIT → Return data, populate L1
               └── MISS → Query PostgreSQL
                          ├── Return data
                          ├── Populate L2 (Redis)
                          └── Populate L1 (In-App)
   ↓
7. Operator corrects transaction
   ↓
8. Correction persisted to PostgreSQL
   ↓
9. Cache entries invalidated/updated
   ↓
10. Confirmation returned to operator
```

### Toll Transaction Simulation Flow

```
1. Python simulator generates concurrent toll passage events
   ↓
2. Transactions sent to API gateway (NGINX)
   ↓
3. Backend processes and persists transactions
   ↓
4. Metrics collected (latency, throughput, cache hit rate)
   ↓
5. Results available in Grafana dashboard
```

---

## Test Scenarios

### Scenario A — Direct Database Access (No Cache)

All requests query PostgreSQL directly. Establishes the performance baseline.

### Scenario B — Distributed Cache (Redis Only)

Requests check Redis before falling back to PostgreSQL. Evaluates the impact of a shared distributed cache.

### Scenario C — Hybrid Cache (L1 In-App + L2 Redis)

Requests check local in-app cache first, then Redis, then PostgreSQL. Evaluates the full multi-layer caching strategy.

---

## Performance Metrics

| Metric | Description | Tool |
|--------|-------------|------|
| Response Latency | Average, p95, p99 response times (ms) | JMeter, Spring Interceptors |
| Throughput (TPS) | Transactions processed per second | JMeter |
| Cache Hit Rate | % of requests served from cache | Redis stats, custom interceptors |
| CPU Usage | Container CPU consumption | `docker stats`, Prometheus |
| Memory Usage | Container RAM consumption | `docker stats`, Prometheus |
| Data Consistency | Cache-DB synchronization integrity | Custom validation scripts |
