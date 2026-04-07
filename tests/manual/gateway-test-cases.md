# Gateway Test Cases (Manual)

## TC-GW-001: Request Forwarding

**Objective**: Verify NGINX correctly forwards API requests to backend instances.

**Steps**:
1. Send GET `/api/pracas` through NGINX (port 80)
2. Verify response contains plaza data from backend

**Expected Result**: Request forwarded and response returned successfully.

---

## TC-GW-002: Load Balancing Distribution

**Objective**: Verify requests are distributed among available backend instances.

**Steps**:
1. Send 10 sequential requests to NGINX
2. Check backend logs to verify distribution

**Expected Result**: Requests distributed according to configured algorithm (round-robin).

---

## TC-GW-003: Health Check

**Objective**: Verify health check endpoint is accessible through gateway.

**Steps**:
1. GET `/actuator/health` through NGINX

**Expected Result**: 200 OK with health status from backend.
