#!/usr/bin/env bash
# run-integration-tests.sh — Run integration tests
set -e

echo "=== Running Integration Tests ==="
cd tests/integration && python -m pytest -v
echo "=== Integration Tests Complete ==="
