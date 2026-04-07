# Testing Strategy

## Overview

The Smart Toll Cache System employs a multi-layered testing strategy to ensure correctness, performance, and reliability of the distributed toll management architecture.

---

## Testing Layers

### 1. Unit Tests

Per-service unit tests verifying individual components in isolation.

| Service                       | Framework | Location                                        |
|-------------------------------|-----------|------------------------------------------------|
| rodovia                       | JUnit 5   | `services/rodovia/src/test/java/`              |
| toll-frontend-react           | Jest      | `services/toll-frontend-react/src/`            |

### 2. Integration Tests

Cross-service integration tests using Python (pytest) against containerized services.

- **Location**: `tests/integration/`
- **Infrastructure**: `tests/docker-compose.test.yml`
- **Categories**:
  - `gateway/` — NGINX load balancing and request forwarding
  - `rodovia/` — Transaction CRUD, cache behavior, Kafka ingestion
  - `end-to-end/` — Full transaction correction flow (Kafka → rodovia → DB)
  - `cache-service/` — Redis cache consistency and invalidation

### 3. End-to-End Tests

Full workflow validation covering the complete transaction correction pipeline from frontend through NGINX to backend, cache, and database.

- **Location**: `tests/integration/end-to-end/`
- **Scenarios**:
  - Complete transaction flow (creation → correction → verification)
  - Cache consistency across multiple backend instances
  - Performance under concurrent load

### 4. Robot Framework Tests

Acceptance and keyword-driven tests for business-level scenarios.

- **Location**: `tests/robot/`
- **Categories**: gateway, rodovia, end-to-end

### 5. Selenium Tests

Browser-based UI tests for the React frontend and monitoring dashboards.

- **Location**: `tests/selenium/`
- **Targets**: Grafana dashboards, Swagger UI

### 6. Manual Test Cases

Documented manual test procedures for exploratory testing.

- **Location**: `tests/manual/`

---

## Running Tests

```bash
# All tests
./tests/scripts/run-all-tests.sh

# Integration tests only
./tests/scripts/run-integration-tests.sh

# End-to-end tests only
./tests/scripts/run-e2e-tests.sh

# Robot Framework tests
./tests/scripts/run-robot-tests.sh

# Selenium UI tests
./tests/scripts/run-selenium-tests.sh
```

---

## Test Metrics

| Metric              | Target   |
|---------------------|----------|
| Unit test coverage  | ≥ 80%   |
| Integration pass    | 100%     |
| E2E pass            | 100%     |
| Performance (p99)   | ≤ 200ms |
