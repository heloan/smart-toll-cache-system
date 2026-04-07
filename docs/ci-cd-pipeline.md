# CI/CD Pipeline

## Overview

The Smart Toll Cache System uses a **Jenkins-based CI/CD pipeline** to automate building, testing, and deploying the distributed microservices architecture. The pipeline ensures code quality through automated testing and quality gates before deployment.

---

## Pipeline Stages

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Checkout │──▶│  Build   │──▶│  Test    │──▶│ Quality  │──▶│  Docker  │──▶│  Deploy  │
│          │   │          │   │          │   │  Gates   │   │  Build   │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Stage 1: Checkout

- Clone repository from version control
- Resolve branch and commit metadata

### Stage 2: Build

- **toll-management-service**: `mvn clean package -DskipTests` (Spring Boot 4.0.3, Java 21)
- **toll-frontend-react**: `npm ci && npm run build`
- **toll-simulator**: `pip install -r requirements.txt`

### Stage 3: Test

- **Unit Tests**: JUnit (Java), Jest (React)
- **Integration Tests**: pytest (Python) against containerized services
- **End-to-End Tests**: Full transaction flow validation
- **Robot Framework**: Acceptance tests
- **Selenium**: UI smoke tests

### Stage 4: Quality Gates

Defined in `jenkins/quality-gates.yml`:

| Metric                  | Threshold | Action on Failure |
|-------------------------|-----------|-------------------|
| Unit Test Coverage      | ≥ 80%     | Block deployment  |
| Integration Test Pass   | 100%      | Block deployment  |
| Lint Errors             | 0         | Block deployment  |
| Build Warnings          | ≤ 10      | Warning           |
| Security Vulnerabilities| 0 Critical| Block deployment  |

### Stage 5: Docker Build

- Build Docker images for each service
- Tag images with build number and `latest`
- Push images to container registry

### Stage 6: Deploy

- Deploy via `docker-compose` to target environment
- Run health checks on all services
- Notify team on success/failure

---

## Jenkins Configuration

### Controller

- Defined in `jenkins/Dockerfile.controller`
- Pre-configured with required plugins

### Agent

- Defined in `jenkins/Dockerfile.agent`
- Includes Java 21, Node.js, Python 3.10, Docker CLI
- Python dependencies in `jenkins/agent-requirements.txt`

### Shared Pipeline Utilities

- `jenkins/pipeline-helpers.groovy`: Reusable Groovy functions for notifications, artifact publishing, and environment setup

---

## Environment Matrix

| Environment  | Trigger            | Infrastructure          |
|--------------|--------------------|-------------------------|
| Development  | Push to `develop`  | Local Docker Compose    |
| Staging      | PR to `main`       | Docker Compose (remote) |
| Production   | Merge to `main`    | Docker Compose / K8s    |
