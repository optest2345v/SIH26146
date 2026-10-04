import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

print("[*] Testing all endpoints for edge cases and errors...")

# 1. Health
r = client.get("/api/health")
assert r.status_code == 200, f"Health check failed: {r.status_code}"
print("  [+] /api/health OK")

# 2. Overview
r = client.get("/api/overview")
assert r.status_code == 200, f"Overview failed: {r.status_code}"
print("  [+] /api/overview OK")

# 3. Alerts
r = client.get("/api/alerts")
assert r.status_code == 200, f"Alerts failed: {r.status_code}"
alerts = r.json()
print(f"  [+] /api/alerts OK (count={len(alerts)})")

# 4. Scenarios
r = client.get("/api/scenarios")
assert r.status_code == 200, f"Scenarios failed: {r.status_code}"
scenarios = r.json()
print(f"  [+] /api/scenarios OK (count={len(scenarios)})")

# Test loading each scenario
for s in scenarios:
    sid = s.get("id") or s.get("scenario_id")
    r = client.post(f"/api/scenarios/{sid}/load")
    assert r.status_code == 200, f"Scenario load {sid} failed: {r.status_code}"
    print(f"    - Scenario {sid} loaded OK")

# 5. Entity dossier on existing and non-existing entities
if alerts:
    target = alerts[0]["target_id"]
    r = client.get(f"/api/entity/{target}/dossier")
    assert r.status_code == 200, f"Dossier failed: {r.status_code}"
    print(f"  [+] /api/entity/{target}/dossier OK")

r = client.get("/api/entity/NONEXISTENT_WALLET_123/dossier")
assert r.status_code == 200, f"Nonexistent dossier failed: {r.status_code}"
print("  [+] /api/entity/NONEXISTENT/dossier handled gracefully OK")

# 6. Graph path endpoint
r = client.get("/api/graph/path?source=WALLET:nonexistent1&target=WALLET:nonexistent2")
assert r.status_code == 200, f"Graph path failed: {r.status_code}"
print("  [+] /api/graph/path non-existing handled gracefully OK")

# 7. Annotations
r = client.get("/api/investigation/annotations")
assert r.status_code == 200, f"Annotations GET failed: {r.status_code}"
r = client.post("/api/investigation/annotations", json={
    "target_id": "WALLET:test1234",
    "alert_id": "ALT-TEST-001",
    "disposition": "FLAG_FOR_SEIZURE",
    "notes": "Test note",
    "analyst_id": "ANALYST-TEST"
})
assert r.status_code == 200, f"Annotations POST failed: {r.status_code}"
print("  [+] /api/investigation/annotations GET/POST OK")

# 8. Export formats: json, txt, brief, custody package
r = client.get("/api/export?format=json")
assert r.status_code == 200, f"Export json failed: {r.status_code}"
r = client.get("/api/export?format=txt")
assert r.status_code == 200, f"Export txt failed: {r.status_code}"
r = client.get("/api/export/intelligence-brief")
assert r.status_code == 200, f"Intelligence brief failed: {r.status_code}"
r = client.get("/api/export/custody-package")
assert r.status_code == 200, f"Custody package failed: {r.status_code}"
print("  [+] /api/export (json, txt, brief, custody-package) all OK")

# 9. Syndicates
r = client.get("/api/graph/syndicates")
assert r.status_code == 200, f"Syndicates failed: {r.status_code}"
print(f"  [+] /api/graph/syndicates OK (count={len(r.json())})")

# 10. Taint on invalid/valid nodes
r = client.get("/api/graph/WALLET:nonexistent/taint")
assert r.status_code == 200, f"Taint failed: {r.status_code}"
print("  [+] /api/graph/{id}/taint OK")

print("\n[*] All backend tests completed without exceptions!")
