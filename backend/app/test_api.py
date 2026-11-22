"""Automated test suite verifying all 11 PreBurn API endpoints."""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

# Initialize database before running tests
init_db()

client = TestClient(app)


def run_tests():
    print("==================================================")
    print("  PREBURN BACKEND API VERIFICATION SUITE")
    print("==================================================")
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name} {details}")
        else:
            print(f"  [FAIL] {name} - FAILED {details}")

    # 1. Health check
    res = client.get("/health")
    assert_test("Health Check", res.status_code == 200, f"Status: {res.status_code}")

    # 2. GET /api/v1/geo/states-districts
    res = client.get("/api/v1/geo/states-districts")
    data = res.json()
    states = data.get("states", [])
    assert_test(
        "GET /api/v1/geo/states-districts",
        res.status_code == 200 and len(states) == 2,
        f"Found {len(states)} states (Punjab & Haryana)"
    )

    # 3. GET /api/v1/geo/districts
    res = client.get("/api/v1/geo/districts?state=Punjab")
    data = res.json()
    assert_test(
        "GET /api/v1/geo/districts",
        res.status_code == 200 and len(data) > 0,
        f"Found {len(data)} districts in Punjab"
    )

    # 4. GET /api/v1/analytics/overview-stats
    res = client.get("/api/v1/analytics/overview-stats")
    data = res.json()
    assert_test(
        "GET /api/v1/analytics/overview-stats",
        res.status_code == 200 and "high_risk_districts" in data,
        f"High: {data.get('high_risk_districts')}, Med: {data.get('medium_risk_districts')}, Low: {data.get('low_risk_districts')}, Active Fires (7d): {data.get('active_fire_detections_7d')}"
    )

    # 5. GET /api/v1/analytics/fire-trends
    res = client.get("/api/v1/analytics/fire-trends?days=7")
    data = res.json()
    assert_test(
        "GET /api/v1/analytics/fire-trends",
        res.status_code == 200 and len(data.get("labels", [])) == 7,
        f"Labels: {data.get('labels')}, Total fires: {sum(data.get('total', []))}"
    )

    # 6. GET /api/v1/predictions/latest
    res = client.get("/api/v1/predictions/latest?horizon_days=3")
    data = res.json()
    preds = data.get("predictions", [])
    top_pred = preds[0] if preds else {}
    assert_test(
        "GET /api/v1/predictions/latest",
        res.status_code == 200 and len(preds) > 0,
        f"Top predicted risk: {top_pred.get('district')} ({top_pred.get('probability')}%)"
    )

    # 7. POST /api/v1/predictions/predict
    res = client.post("/api/v1/predictions/predict", json={
        "district_name": "Ludhiana",
        "state_name": "Punjab",
        "horizon_days": 4
    })
    data = res.json()
    assert_test(
        "POST /api/v1/predictions/predict",
        res.status_code == 200 and data.get("risk_level") in ["High", "Medium", "Low"],
        f"Predicted: {data.get('probability')}% ({data.get('risk_level')}) for 4-day horizon"
    )

    # 8. GET /api/v1/fires
    res = client.get("/api/v1/fires?limit=10")
    data = res.json()
    fires = data.get("fires", [])
    assert_test(
        "GET /api/v1/fires",
        res.status_code == 200 and len(fires) > 0,
        f"Retrieved {len(fires)} detections (Total in DB: {data.get('total')})"
    )

    # 8b. GET /api/v1/fires with CSV export
    res_csv = client.get("/api/v1/fires?export_csv=true")
    assert_test(
        "GET /api/v1/fires (CSV Export)",
        res_csv.status_code == 200 and "text/csv" in res_csv.headers.get("content-type", ""),
        f"CSV exported with {len(res_csv.text.splitlines())} lines"
    )

    # 9. GET /api/v1/weather/{district_id}
    # Grab Ludhiana's district ID
    dist_res = client.get("/api/v1/geo/districts?state=Punjab")
    dist_list = dist_res.json()
    ludhiana_id = dist_list[0]["id"] if dist_list else 1

    res = client.get(f"/api/v1/weather/{ludhiana_id}")
    data = res.json()
    forecasts = data.get("forecasts", [])
    assert_test(
        f"GET /api/v1/weather/{ludhiana_id}",
        res.status_code == 200 and len(forecasts) >= 4,
        f"District: {data.get('district_name')}, 4-day temps: {[f['temperature'] for f in forecasts]}"
    )

    # 10. GET /api/v1/alerts
    res = client.get("/api/v1/alerts")
    data = res.json()
    alerts = data.get("alerts", [])
    first_alert_id = alerts[0]["id"] if alerts else 1
    assert_test(
        "GET /api/v1/alerts",
        res.status_code == 200 and len(alerts) > 0,
        f"Total alerts: {data.get('total')}, Unread: {data.get('unread_count')}"
    )

    # 11. PATCH /api/v1/alerts/{id}/read
    res = client.patch(f"/api/v1/alerts/{first_alert_id}/read")
    data = res.json()
    assert_test(
        f"PATCH /api/v1/alerts/{first_alert_id}/read",
        res.status_code == 200 and data.get("is_read") is True,
        f"Alert {first_alert_id} marked as read"
    )

    # 12. POST /api/v1/alerts/mark-all-read
    res = client.post("/api/v1/alerts/mark-all-read")
    data = res.json()
    assert_test(
        "POST /api/v1/alerts/mark-all-read",
        res.status_code == 200 and "updated_count" in data,
        f"Updated: {data.get('updated_count')} alerts"
    )

    print("==================================================")
    print(f"  TEST RESULTS: {passed}/{total} PASSED")
    print("==================================================")

    if passed == total:
        print("  All API endpoints verified successfully!")
        return 0
    else:
        print("  Some tests failed!")
        return 1


if __name__ == "__main__":
    code = run_tests()
    sys.exit(code)
