# Smart Toll Cache System

![Java](https://img.shields.io/badge/Java-17-orange?logo=openjdk)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-brightgreen?logo=springboot)
![Redis](https://img.shields.io/badge/Redis-7.x-red?logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue?logo=postgresql)
![NGINX](https://img.shields.io/badge/NGINX-latest-green?logo=nginx)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Distributed microservices architecture with in-memory caching (Redis), load balancing (NGINX), and performance benchmarking for high-demand toll management systems.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Services](#services)
- [Getting Started](#getting-started)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

This project implements a **distributed microservices-based architecture** designed to optimize the performance and scalability of a real-time toll transaction management system. The system handles toll booth transaction corrections in real-time, where operators must quickly resolve issues such as missing tags, blocked tags, or closed lanes — minimizing queue formation, user stress, and traffic safety risks.

The architecture leverages **multi-layer in-memory caching** (In-App L1 + Redis L2), **load balancing** (NGINX), and **synchronization between cache and relational database** (PostgreSQL) to achieve low latency, high availability, and data consistency under high-concurrency scenarios.

### Problem Statement

In real-time toll management, operators need to correct transactions in seconds to avoid:
- Queue formation at toll booths
- Increased user stress and dissatisfaction
- Traffic flow disruptions and accident risks during peak hours

Traditional monolithic architectures cannot handle the high volume of concurrent requests and strict latency requirements demanded by such critical systems.

### Solution

A distributed system with:
- **Cache-Aside strategy** with two-layer caching (L1 In-App + L2 Redis)
- **NGINX load balancing** across multiple Spring Boot backend instances
- **PostgreSQL** as the single source of truth
- **Python-based load simulators** for realistic benchmarking
- **Prometheus + Grafana** for observability and performance monitoring

---

## Architecture

```
                        ┌─────────────────┐
                        │   React Frontend │
                        │  (Operator UI)   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │      NGINX       │
                        │  Load Balancer   │
                        │    (Port 80)     │
                        └──┬─────┬─────┬──┘
                           │     │     │
              ┌────────────┘     │     └────────────┐
              ▼                  ▼                   ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │  Spring Boot  │  │  Spring Boot  │  │  Spring Boot  │
     │  Instance 1   │  │  Instance 2   │  │  Instance N   │
     │  (L1 Cache)   │  │  (L1 Cache)   │  │  (L1 Cache)   │
     └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
            │                  │                  │
            └──────────┬───────┘──────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
     ┌──────────────┐  ┌──────────────┐
     │    Redis      │  │  PostgreSQL   │
     │  (L2 Cache)   │  │   (SSOT)      │
     └──────────────┘  └──────────────┘
```

> For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

---

## Tech Stack

| Layer              | Technology         | Purpose                                       |
|--------------------|--------------------|-----------------------------------------------|
| Frontend           | React 18           | Toll booth operator interface                 |
| API Gateway        | NGINX              | Reverse proxy and load balancer               |
| Backend            | Spring Boot (Java 17) | Toll management microservice               |
| L1 Cache           | Caffeine (In-App)  | Local in-memory cache per instance            |
| L2 Cache           | Redis 7.x          | Distributed shared cache                      |
| Database           | PostgreSQL 14      | Relational persistence (single source of truth)|
| Load Simulation    | Python 3.10        | Concurrent transaction simulation scripts     |
| Monitoring         | Prometheus + Grafana | Metrics collection and visualization        |
| Containerization   | Docker Compose     | Service orchestration                         |
| CI/CD              | Jenkins            | Continuous integration and delivery           |

---

## Services

| Service                            | Tech              | Description                                                |
|------------------------------------|-------------------|------------------------------------------------------------|
| `toll-api-gateway`                 | NGINX             | Reverse proxy, load balancing across backend instances      |
| `toll-management-service-java`     | Spring Boot       | Core toll transaction CRUD, cache integration, metrics      |
| `toll-frontend-react`              | React             | Operator dashboard for real-time transaction correction     |
| `toll-simulator-python`            | Python            | Load testing scripts simulating toll booth traffic          |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Java 17+ (for local development)
- Node.js 18+ (for frontend development)
- Python 3.10+ (for simulators)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/smart-toll-cache-system.git
cd smart-toll-cache-system

# Start the full stack
./scripts/start.sh

# View logs
./scripts/logs.sh

# Stop all services
./scripts/stop.sh
```

### Build All Services

```bash
./scripts/build.sh
```

### Access Points

| Service          | URL                          |
|------------------|------------------------------|
| Frontend (React) | http://localhost:3000         |
| API Gateway      | http://localhost:80           |
| Grafana          | http://localhost:3001         |
| Prometheus       | http://localhost:9090         |

---

## Testing

The project includes multiple testing layers:

- **Unit Tests**: Per-service (JUnit for Java, Jest for React)
- **Integration Tests**: Python-based (pytest) cross-service tests
- **End-to-End Tests**: Full transaction flow validation
- **Robot Framework**: Acceptance testing
- **Selenium**: UI testing (Grafana dashboards, Swagger)

```bash
# Run all tests
./tests/scripts/run-all-tests.sh

# Run integration tests only
./tests/scripts/run-integration-tests.sh

# Run E2E tests only
./tests/scripts/run-e2e-tests.sh
```

> See [tests/README.md](tests/README.md) for the full testing strategy.

---

## Documentation

| Document                                             | Description                                    |
|------------------------------------------------------|------------------------------------------------|
| [System Overview](docs/system-overview.md)           | Problem statement, workflows, solution design  |
| [Architecture](docs/architecture.md)                 | High-level architecture and component diagrams |
| [Database Design](docs/database-design.md)           | ERD, schemas, data model                       |
| [UML Diagrams](docs/uml-diagrams.md)                | Sequence, component, and class diagrams        |
| [CI/CD Pipeline](docs/ci-cd-pipeline.md)             | Pipeline stages and quality gates              |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
