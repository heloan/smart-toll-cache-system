#!/usr/bin/env bash
# build.sh — Build all services for Smart Toll Cache System
set -e

echo "=== Building Smart Toll Cache System ==="

echo "[1/3] Building rodovia service..."
cd services/rodovia && ./mvnw clean package -DskipTests && cd ../..

echo "[2/3] Building toll-frontend-react..."
cd services/toll-frontend-react && npm ci && npm run build && cd ../..

echo "[3/3] Building Docker images..."
docker-compose -f infrastructure/docker-compose.yml build

echo "=== Build complete ==="
