# Toll Management Service (Java / Spring Boot)

## Overview

Core microservice responsible for managing toll plazas, lanes, and transactions. Implements multi-layer caching (L1 Caffeine + L2 Redis) with Cache-Aside strategy for optimized data access in real-time toll transaction correction scenarios.

## Responsibilities

- CRUD operations for toll plazas (`Praca`), lanes (`Pista`), and transactions (`Transacao`)
- Real-time transaction correction workflow
- Multi-layer cache management (L1 In-App Caffeine + L2 Redis)
- Performance metrics collection via custom interceptors
- RESTful API exposure with Spring Boot Actuator for monitoring

## Tech Stack

| Technology    | Version | Purpose                                |
|---------------|---------|----------------------------------------|
| Java          | 17      | Runtime                                |
| Spring Boot   | 3.x     | Application framework                  |
| Spring Cache  | —       | Cache abstraction (Caffeine + Redis)   |
| Caffeine      | —       | L1 in-app local cache                  |
| Redis         | 7.x     | L2 distributed cache                   |
| PostgreSQL    | 14      | Relational persistence (SSOT)          |
| Spring Actuator | —     | Health checks and Prometheus metrics   |
| Maven         | —       | Build tool                             |

## Architecture (Clean Architecture)

```
src/main/java/
├── controller/        # REST API controllers (Presentation layer)
├── service/           # Business logic (Application layer)
├── repository/        # Data access (Infrastructure layer)
├── model/             # Domain entities
├── config/            # Cache, Redis, and application configuration
├── interceptor/       # Performance metrics interceptors
└── dto/               # Data Transfer Objects
```

## Cache Configuration

```java
@Configuration
@EnableCaching
public class CacheConfig {
    @Bean
    public RedisCacheConfiguration cacheConfiguration() {
        return RedisCacheConfiguration.defaultCacheConfig()
          .entryTtl(Duration.ofMinutes(10))
          .disableCachingNullValues();
    }
}
```

## How to Run

```bash
# Via Docker Compose (recommended)
docker-compose -f infrastructure/docker-compose.yml up toll-service-1

# Local development
cd services/toll-management-service-java
./mvnw spring-boot:run

# Build
./mvnw clean package -DskipTests
```

## API Endpoints (Planned)

| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/api/pracas`                     | List all toll plazas           |
| GET    | `/api/pracas/{id}`                | Get plaza by ID                |
| GET    | `/api/pistas`                     | List all lanes                 |
| GET    | `/api/pistas/{id}`                | Get lane by ID                 |
| GET    | `/api/transacoes`                 | List transactions              |
| GET    | `/api/transacoes/{id}`            | Get transaction by ID          |
| PUT    | `/api/transacoes/{id}/corrigir`   | Correct a transaction          |
| GET    | `/actuator/prometheus`            | Prometheus metrics endpoint    |
| GET    | `/actuator/health`                | Health check                   |

## Ports

| Port | Protocol | Description             |
|------|----------|-------------------------|
| 8080 | HTTP     | Application API         |
