#!/usr/bin/env bash
# logs.sh — Tail logs from all containers
set -e

echo "=== Tailing logs from all containers ==="
docker-compose -f infrastructure/docker-compose.yml logs -f
