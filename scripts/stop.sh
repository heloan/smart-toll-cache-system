#!/usr/bin/env bash
# stop.sh — Stop and clean up containers
set -e

echo "=== Stopping Smart Toll Cache System ==="
docker-compose -f infrastructure/docker-compose.yml down

echo "=== Stack stopped ==="
