#!/usr/bin/env bash
# start.sh — Start full stack via Docker Compose
set -e

echo "=== Starting Smart Toll Cache System ==="
docker-compose -f infrastructure/docker-compose.yml up -d

echo ""
echo "Services:"
echo "  Frontend:   http://localhost:3000"
echo "  API Gateway: http://localhost:80"
echo "  Toll Management API: http://localhost:9080/api"
echo "  Kafka:      localhost:9092"
echo "  Grafana:    http://localhost:3001"
echo "  Prometheus: http://localhost:9090"
echo ""
echo "=== Stack started ==="
