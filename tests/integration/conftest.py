# conftest.py — Shared pytest fixtures for integration tests
import pytest
import os

TOLL_MANAGEMENT_BASE_URL = os.getenv("TOLL_MANAGEMENT_BASE_URL", "http://localhost:9080")
GATEWAY_BASE_URL = os.getenv("GATEWAY_BASE_URL", "http://localhost:80")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@pytest.fixture
def toll_management_url():
    return TOLL_MANAGEMENT_BASE_URL


@pytest.fixture
def gateway_url():
    return GATEWAY_BASE_URL
