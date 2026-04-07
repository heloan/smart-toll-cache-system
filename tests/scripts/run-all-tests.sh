#!/usr/bin/env bash
# run-all-tests.sh — Run all test suites
set -e

echo "=== Running All Tests ==="

./tests/scripts/run-integration-tests.sh
./tests/scripts/run-e2e-tests.sh
./tests/scripts/run-robot-tests.sh
./tests/scripts/run-selenium-tests.sh

echo "=== All Tests Complete ==="
