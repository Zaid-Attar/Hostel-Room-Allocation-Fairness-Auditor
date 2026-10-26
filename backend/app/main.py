"""
Hostel Room Allocation Fairness Auditor (HRAFA)
FastAPI Backend Application - REST API Endpoints
"""

import io
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import pandas as pd

from backend.app.db import get_db
from backend.app import crud
from backend.app.audit import run_audit, explain_student, DEFAULT_POLICY_WEIGHTS

app = FastAPI(
    title="Hostel Room Allocation Fairness Auditor",
    description="Backend API for auditing institutional hostel room allocations against statutory merit and reservation policies.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas for Request Payloads
# ---------------------------------------------------------------------------
class StudentCreate(BaseModel):
    student_id: str
    name: str
    gender: str = Field(..., pattern="^(M|F)$")
    year: int = Field(..., ge=1, le=4)
    cgpa: float = Field(..., ge=0.0, le=10.0)
    category: str
    distance_km: int = Field(..., ge=0)
    special_needs: int = Field(0, ge=0, le=1)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(M|F)$")
    year: Optional[int] = Field(None, ge=1, le=4)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    category: Optional[str] = None
    distance_km: Optional[int] = Field(None, ge=0)
    special_needs: Optional[int] = Field(None, ge=0, le=1)

class RoomCreate(BaseModel):
    room_id: str
    hostel: str
    gender: str = Field(..., pattern="^(M|F)$")
    floor: int = Field(..., ge=0)
    mess_distance_m: int = Field(..., ge=0)
    accessible: int = Field(0, ge=0, le=1)

class RoomUpdate(BaseModel):
    hostel: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(M|F)$")
    floor: Optional[int] = Field(None, ge=0)
    mess_distance_m: Optional[int] = Field(None, ge=0)
    accessible: Optional[int] = Field(None, ge=0, le=1)

class AllocationUpdate(BaseModel):
    room_id: Optional[str] = None

class PolicyUpdate(BaseModel):
    w_cgpa: Optional[float] = None
    w_distance: Optional[float] = None
    w_year: Optional[float] = None
    w_category: Optional[float] = None
    w_special_needs: Optional[float] = None
    w_room_mess: Optional[float] = None
    w_room_floor: Optional[float] = None
    tolerance_pct: Optional[float] = None


# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Returns ok status to verify backend health."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Students Endpoints
# ---------------------------------------------------------------------------
@app.get("/students")
def list_students(
    category: Optional[str] = None,
    year: Optional[int] = None,
    gender: Optional[str] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    special_needs: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return crud.get_students(
        db, category=category, year=year, gender=gender,
        min_distance=min_distance, max_distance=max_distance,
        special_needs=special_needs, search=search, page=page, page_size=page_size
    )

@app.post("/students", status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    existing = crud.get_student_by_id(db, payload.student_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{payload.student_id}' already exists")
    return crud.create_student(db, payload.model_dump())

@app.get("/students/{student_id}")
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}")
def update_student(student_id: str, payload: StudentUpdate, db: Session = Depends(get_db)):
    updated = crud.update_student(db, student_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated

@app.delete("/students/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"status": "deleted", "student_id": student_id}


# ---------------------------------------------------------------------------
# Rooms Endpoints
# ---------------------------------------------------------------------------
@app.get("/rooms")
def list_rooms(
    hostel: Optional[str] = None,
    gender: Optional[str] = None,
    floor: Optional[int] = None,
    accessible: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return crud.get_rooms(
        db, hostel=hostel, gender=gender, floor=floor,
        accessible=accessible, search=search, page=page, page_size=page_size
    )

@app.post("/rooms", status_code=201)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    existing = crud.get_room_by_id(db, payload.room_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Room ID '{payload.room_id}' already exists")
    return crud.create_room(db, payload.model_dump())

@app.get("/rooms/{room_id}")
def get_room(room_id: str, db: Session = Depends(get_db)):
    room = crud.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@app.put("/rooms/{room_id}")
def update_room(room_id: str, payload: RoomUpdate, db: Session = Depends(get_db)):
    updated = crud.update_room(db, room_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated

@app.delete("/rooms/{room_id}")
def delete_room(room_id: str, db: Session = Depends(get_db)):
    success = crud.delete_room(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"status": "deleted", "room_id": room_id}


# ---------------------------------------------------------------------------
# Allocations Endpoints
# ---------------------------------------------------------------------------
@app.get("/allocations")
def list_allocations(db: Session = Depends(get_db)):
    return crud.get_all_allocations(db)

@app.put("/allocations/{student_id}")
def update_student_allocation(student_id: str, payload: AllocationUpdate, db: Session = Depends(get_db)):
    crud.update_allocation(db, student_id, payload.room_id)
    return {"status": "updated", "student_id": student_id, "room_id": payload.room_id}


# ---------------------------------------------------------------------------
# Policy Rules Endpoints
# ---------------------------------------------------------------------------
@app.get("/policy")
def get_policy(db: Session = Depends(get_db)):
    policy = crud.get_policy_rules(db)
    if not policy:
        return DEFAULT_POLICY_WEIGHTS
    return policy

@app.put("/policy")
def update_policy(payload: PolicyUpdate, db: Session = Depends(get_db)):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    return crud.update_policy_rules(db, updates)


# ---------------------------------------------------------------------------
# Audit & Analytics Endpoints
# ---------------------------------------------------------------------------
@app.get("/audit")
def perform_audit(
    w_cgpa: Optional[float] = None,
    w_distance: Optional[float] = None,
    w_year: Optional[float] = None,
    w_category: Optional[float] = None,
    w_special_needs: Optional[float] = None,
    w_room_mess: Optional[float] = None,
    w_room_floor: Optional[float] = None,
    tolerance_pct: Optional[float] = None,
    save: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Executes algorithmic fairness audit live.
    Optional query parameters override the policy weights dynamically without saving.
    If save=True, the results are written to the database audit_results table.
    """
    db_policy = crud.get_policy_rules(db)
    active_weights = dict(DEFAULT_POLICY_WEIGHTS)
    active_weights.update(db_policy)

    # Apply overrides from query params
    overrides = {
        "w_cgpa": w_cgpa,
        "w_distance": w_distance,
        "w_year": w_year,
        "w_category": w_category,
        "w_special_needs": w_special_needs,
        "w_room_mess": w_room_mess,
        "w_room_floor": w_room_floor,
        "tolerance_pct": tolerance_pct,
    }
    for k, v in overrides.items():
        if v is not None:
            active_weights[k] = float(v)

    students_df, rooms_df, alloc_df = crud.get_audit_cohort_data(db)

    results = run_audit(students_df, rooms_df, alloc_df, policy_overrides=active_weights)

    if save:
        crud.save_audit_results(db, results["students"])

    return {
        "summary": results["summary"],
        "policy_used": active_weights,
        "students": results["students"],
        "displacement_pairs": results["displacement_pairs"],
        "group_stats": results["group_stats"]
    }


@app.get("/audit/student/{student_id}")
def student_explainability(student_id: str, db: Session = Depends(get_db)):
    """Provides deep mathematical breakdown and plain English reasoning for a student."""
    students_df, rooms_df, alloc_df = crud.get_audit_cohort_data(db)
    db_policy = crud.get_policy_rules(db)
    active_weights = dict(DEFAULT_POLICY_WEIGHTS)
    active_weights.update(db_policy)

    results = run_audit(students_df, rooms_df, alloc_df, policy_overrides=active_weights)

    target_student = next((s for s in results["students"] if s["student_id"] == student_id), None)
    if not target_student:
        raise HTTPException(status_code=404, detail="Student not found in audit cohort")

    max_dist = float(students_df["distance_km"].max()) if not students_df.empty else 1.0
    return explain_student(target_student, max_distance=max_dist, weights=active_weights)


@app.get("/export/corrected-allocation.csv")
def export_corrected_allocation(db: Session = Depends(get_db)):
    """Exports fair, corrected allocation as downloadable CSV."""
    students_df, rooms_df, alloc_df = crud.get_audit_cohort_data(db)
    db_policy = crud.get_policy_rules(db)
    active_weights = dict(DEFAULT_POLICY_WEIGHTS)
    active_weights.update(db_policy)

    results = run_audit(students_df, rooms_df, alloc_df, policy_overrides=active_weights)
    corrected = results["corrected_allocations"]

    df_out = pd.DataFrame(corrected)
    # Rename columns for clarity in CSV export
    df_out = df_out.rename(columns={
        "student_id": "student_id",
        "expected_room_id": "recommended_room_id",
        "priority_rank": "policy_priority_rank",
        "priority_score": "composite_priority_score"
    })

    buffer = io.StringIO()
    df_out.to_csv(buffer, index=False)
    csv_bytes = buffer.getvalue().encode("utf-8")

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=corrected_allocation.csv"}
    )
