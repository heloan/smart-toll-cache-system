# Toll Simulator (Python)

## Overview

Python-based load simulation scripts for benchmarking the Smart Toll Cache System. Simulates concurrent toll booth transaction flows and transaction correction operations under high load conditions.

## Responsibilities

- Simulate toll booth transaction flow (vehicle passages)
- Simulate transaction correction operations (operator actions)
- Generate controlled concurrent load (up to 500 simultaneous users)
- Produce metrics data for comparative analysis across test scenarios

## Tech Stack

| Technology        | Version | Purpose                              |
|-------------------|---------|--------------------------------------|
| Python            | 3.10+   | Runtime                              |
| requests          | —       | HTTP client for API calls            |
| concurrent.futures| —       | Thread/process-based concurrency     |

## Test Scenarios

| Scenario | Description                              | Cache Strategy          |
|----------|------------------------------------------|-------------------------|
| A        | Direct PostgreSQL access (no cache)      | None                    |
| B        | Distributed cache (Redis only)           | L2 Redis                |
| C        | Hybrid cache (L1 In-App + L2 Redis)     | L1 Caffeine + L2 Redis  |

## How to Run

```bash
# Install dependencies
cd services/toll-simulator-python
pip install -r requirements.txt

# Run transaction simulation
# python src/simulate_transactions.py --concurrent-users 100

# Run correction simulation
# python src/simulate_corrections.py --concurrent-users 500
```

## Metrics Collected

- Response latency (average, p95, p99)
- Throughput (transactions per second)
- Cache hit rate
- Error rate
