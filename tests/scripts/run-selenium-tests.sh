#!/usr/bin/env bash
# run-selenium-tests.sh — Run Selenium UI tests
set -e

echo "=== Running Selenium Tests ==="
cd tests/selenium && python -m pytest -v
echo "=== Selenium Tests Complete ==="
