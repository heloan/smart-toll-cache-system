# End-to-End Test Cases (Manual)

## TC-E2E-001: Full Transaction Correction Flow

**Objective**: Validate the complete transaction correction flow from operator search to database persistence.

**Preconditions**:
- All services running (NGINX, Spring Boot, Redis, PostgreSQL)
- Test data populated in database

**Steps**:
1. Open React frontend at http://localhost:3000
2. Search for a pending transaction by vehicle plate
3. Verify transaction details are displayed
4. Apply correction to the transaction
5. Verify confirmation is returned
6. Verify PostgreSQL record is updated (`corrigida = true`, `status = 'CORRIGIDA'`)
7. Verify Redis cache is invalidated/updated

**Expected Result**: Transaction corrected, database updated, cache consistent.

---

## TC-E2E-002: Cache Hit Behavior

**Objective**: Verify data is served from cache on subsequent requests.

**Steps**:
1. Query a transaction (cold start — cache miss)
2. Query the same transaction again
3. Monitor Redis to confirm cache hit

**Expected Result**: Second request served from Redis cache with lower latency.

---

## TC-E2E-003: Load Balancing Verification

**Objective**: Verify NGINX distributes requests across backend instances.

**Steps**:
1. Send multiple sequential requests through NGINX
2. Check response headers or logs to identify which backend instance handled each request

**Expected Result**: Requests distributed across available backend instances.
