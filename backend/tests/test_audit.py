"""
Unit tests for Pure Audit Engine (backend/app/audit.py).
Tests the 4 required cases using a 6-student & 6-room hand-made dataset.
"""

import pytest
import pandas as pd
from backend.app.audit import run_audit, explain_student, DEFAULT_POLICY_WEIGHTS


@pytest.fixture
def base_data():
    """Hand-crafted 6 students and 6 rooms fixture in a single pool."""
    students = pd.DataFrame([
        {"student_id": "S1", "name": "Student One", "gender": "M", "year": 4, "cgpa": 9.8, "category": "General", "distance_km": 800, "special_needs": 0},
        {"student_id": "S2", "name": "Student Two", "gender": "M", "year": 4, "cgpa": 9.0, "category": "General", "distance_km": 600, "special_needs": 0},
        {"student_id": "S3", "name": "Student Three", "gender": "M", "year": 3, "cgpa": 8.5, "category": "General", "distance_km": 500, "special_needs": 0},
        {"student_id": "S4", "name": "Student Four", "gender": "M", "year": 2, "cgpa": 7.5, "category": "General", "distance_km": 300, "special_needs": 0},
        {"student_id": "S5", "name": "Student Five", "gender": "M", "year": 1, "cgpa": 7.0, "category": "General", "distance_km": 200, "special_needs": 0},
        {"student_id": "S6", "name": "Student Six", "gender": "M", "year": 1, "cgpa": 6.0, "category": "General", "distance_km": 100, "special_needs": 0},
    ])

    rooms = pd.DataFrame([
        {"room_id": "R1", "hostel": "Block Alpha", "gender": "M", "floor": 0, "mess_distance_m": 20, "accessible": 1},
        {"room_id": "R2", "hostel": "Block Alpha", "gender": "M", "floor": 1, "mess_distance_m": 50, "accessible": 0},
        {"room_id": "R3", "hostel": "Block Alpha", "gender": "M", "floor": 2, "mess_distance_m": 80, "accessible": 0},
        {"room_id": "R4", "hostel": "Block Alpha", "gender": "M", "floor": 3, "mess_distance_m": 120, "accessible": 0},
        {"room_id": "R5", "hostel": "Block Alpha", "gender": "M", "floor": 4, "mess_distance_m": 150, "accessible": 0},
        {"room_id": "R6", "hostel": "Block Alpha", "gender": "M", "floor": 4, "mess_distance_m": 200, "accessible": 0},
    ])

    return students, rooms


def test_perfect_allocation(base_data):
    """Case 1: A perfect allocation gives zero flagged students and rho of 1."""
    students, rooms = base_data
    # Exact 1-to-1 matching from highest to lowest
    allocations = pd.DataFrame([
        {"student_id": "S1", "room_id": "R1"},
        {"student_id": "S2", "room_id": "R2"},
        {"student_id": "S3", "room_id": "R3"},
        {"student_id": "S4", "room_id": "R4"},
        {"student_id": "S5", "room_id": "R5"},
        {"student_id": "S6", "room_id": "R6"},
    ])

    results = run_audit(students, rooms, allocations)
    summary = results["summary"]

    assert summary["flagged_count"] == 0, f"Expected 0 flagged, got {summary['flagged_count']}"
    assert summary["spearman_rho"] == 1.0, f"Expected rho 1.0, got {summary['spearman_rho']}"
    assert summary["fairness_score"] == 100
    assert summary["compliance_rate"] == 100.0


def test_swapping_top_and_bottom_flags_both(base_data):
    """Case 2: Swapping the top and bottom students flags both."""
    students, rooms = base_data
    # S1 gets R6 (worst room), S6 gets R1 (best room)
    allocations = pd.DataFrame([
        {"student_id": "S1", "room_id": "R6"},
        {"student_id": "S2", "room_id": "R2"},
        {"student_id": "S3", "room_id": "R3"},
        {"student_id": "S4", "room_id": "R4"},
        {"student_id": "S5", "room_id": "R5"},
        {"student_id": "S6", "room_id": "R1"},
    ])

    results = run_audit(students, rooms, allocations)
    student_lookup = {s["student_id"]: s for s in results["students"]}

    assert student_lookup["S1"]["is_flagged"] is True or student_lookup["S1"]["status"] == "UNDER_SERVED"
    assert student_lookup["S6"]["is_flagged"] is True or student_lookup["S6"]["status"] == "OVER_FAVORED"
    assert student_lookup["S1"]["deviation"] > 0  # Under-served got worse room
    assert student_lookup["S6"]["deviation"] < 0  # Over-favored got better room
    assert len(results["displacement_pairs"]) >= 1


def test_special_needs_in_non_accessible_triggers_hard_rule(base_data):
    """Case 3: A special-needs student in a non-accessible room triggers the hard rule."""
    students = base_data[0].copy()
    rooms = base_data[1].copy()
    # Mark S3 as special needs
    students.loc[students["student_id"] == "S3", "special_needs"] = 1

    # Place S3 in R2 (floor 1, accessible = 0)
    allocations = pd.DataFrame([
        {"student_id": "S1", "room_id": "R1"},
        {"student_id": "S2", "room_id": "R3"},
        {"student_id": "S3", "room_id": "R2"},  # Non-accessible!
        {"student_id": "S4", "room_id": "R4"},
        {"student_id": "S5", "room_id": "R5"},
        {"student_id": "S6", "room_id": "R6"},
    ])

    results = run_audit(students, rooms, allocations)
    student_lookup = {s["student_id"]: s for s in results["students"]}

    s3 = student_lookup["S3"]
    assert s3["hard_rule_violation"] == 1
    assert s3["violation_type"] == "SPECIAL_NEEDS_NOT_ACCESSIBLE"
    assert s3["is_flagged"] is True
    assert results["summary"]["hard_rule_violations"] >= 1


def test_missing_student_is_unallocated(base_data):
    """Case 4: A student missing from the allocation is UNALLOCATED."""
    students, rooms = base_data
    # Omit S5 from allocations
    allocations = pd.DataFrame([
        {"student_id": "S1", "room_id": "R1"},
        {"student_id": "S2", "room_id": "R2"},
        {"student_id": "S3", "room_id": "R3"},
        {"student_id": "S4", "room_id": "R4"},
        {"student_id": "S6", "room_id": "R5"},
    ])

    results = run_audit(students, rooms, allocations)
    student_lookup = {s["student_id"]: s for s in results["students"]}

    assert "S5" in student_lookup
    s5 = student_lookup["S5"]
    assert s5["actual_room_id"] is None
    assert s5["status"] == "UNALLOCATED"
    assert s5["is_flagged"] is True


def test_explainability_breakdown(base_data):
    """Bonus: Verify explain_student provides weighted factors and plain English reason."""
    students, rooms = base_data
    allocations = pd.DataFrame([
        {"student_id": "S1", "room_id": "R1"},
        {"student_id": "S2", "room_id": "R2"},
    ])

    results = run_audit(students, rooms, allocations)
    s1 = results["students"][0]
    explanation = explain_student(s1, max_distance=800.0, weights=DEFAULT_POLICY_WEIGHTS)

    assert explanation["student_id"] == "S1"
    assert "factors" in explanation
    assert "cgpa" in explanation["factors"]
    assert "reason" in explanation
