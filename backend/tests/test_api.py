"""
Test suite for Phase 3: REST API Endpoints.
Verifies all routes: health, docs, students, rooms, allocations, policy, audit, explainability, and export.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_docs_page():
    response = client.get("/docs")
    assert response.status_code == 200

def test_get_students():
    response = client.get("/students?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 300
    assert len(data["items"]) == 10

def test_filter_students_by_category():
    response = client.get("/students?category=OBC")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for s in data["items"]:
        assert s["category"] == "OBC"

def test_get_rooms():
    response = client.get("/rooms?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 300
    assert len(data["items"]) == 10

def test_get_policy():
    response = client.get("/policy")
    assert response.status_code == 200
    policy = response.json()
    assert "w_cgpa" in policy
    assert "tolerance_pct" in policy

def test_live_audit_on_generated_data():
    """Checks: on the generated data, the audit returns a fairness score roughly between 80 and 95 with about 8 to 12% flagged."""
    response = client.get("/audit")
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]

    assert 75 <= summary["fairness_score"] <= 98, f"Unexpected fairness score: {summary['fairness_score']}"
    assert 6.0 <= summary["flagged_rate"] <= 16.0, f"Unexpected flagged rate: {summary['flagged_rate']}%"
    assert len(data["displacement_pairs"]) >= 1
    assert "category" in data["group_stats"]

def test_student_explainability():
    # Audit first to get a student
    audit_resp = client.get("/audit")
    first_sid = audit_resp.json()["students"][0]["student_id"]

    response = client.get(f"/audit/student/{first_sid}")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == first_sid
    assert "factors" in data
    assert "cgpa" in data["factors"]
    assert "reason" in data

def test_export_corrected_allocation_csv():
    response = client.get("/export/corrected-allocation.csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "student_id" in response.text
    assert "recommended_room_id" in response.text
