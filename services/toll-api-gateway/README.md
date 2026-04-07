# Toll API Gateway (NGINX)

## Overview

NGINX-based reverse proxy and load balancer that serves as the entry point for all client requests to the Smart Toll Cache System.

## Responsibilities

- Reverse proxy routing to backend Spring Boot instances
- Load balancing using configurable algorithms (round-robin, least connections, IP hash)
- SSL termination (production)
- Request rate limiting and connection management

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| NGINX      | latest  | Reverse proxy and load balancer |

## Configuration

The main NGINX configuration is in `nginx.conf`, with additional site configurations in `conf.d/`.

### Load Balancing Algorithms

- **Round-robin** (default): Sequential distribution across backend instances
- **Least connections**: Routes to the instance with fewest active connections
- **IP hash**: Consistent routing based on client IP address

## How to Run

```bash
# Via Docker Compose (recommended)
docker-compose -f infrastructure/docker-compose.yml up nginx

# Standalone
docker build -t toll-api-gateway .
docker run -p 80:80 toll-api-gateway
```

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 80   | HTTP     | Client-facing gateway |
