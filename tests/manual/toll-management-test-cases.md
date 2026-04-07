# Toll Management Service Test Cases (Manual)

## TC-TMS-001: Transaction Creation

**Objective**: Verify new toll transactions can be created via API.

**Steps**:
1. POST `/api/transacoes` with valid transaction payload
2. Verify 201 Created response
3. Verify transaction persisted in PostgreSQL
4. Verify transaction cached in Redis

**Expected Result**: Transaction created and accessible via cache and database.

---

## TC-TMS-002: Transaction Correction

**Objective**: Verify transaction correction updates both database and cache.

**Steps**:
1. Create a pending transaction
2. PUT `/api/transacoes/{id}/corrigir`
3. Verify `corrigida = true` in PostgreSQL
4. Verify cache entry invalidated in Redis

**Expected Result**: Transaction marked as corrected in all data layers.

---

## TC-TMS-003: Cache Miss → Database Fallback

**Objective**: Verify system falls back to PostgreSQL when cache is empty.

**Steps**:
1. Flush Redis cache
2. GET `/api/transacoes/{id}`
3. Verify data returned from PostgreSQL
4. Verify data now populated in Redis

**Expected Result**: Data served from database and cached for subsequent requests.
