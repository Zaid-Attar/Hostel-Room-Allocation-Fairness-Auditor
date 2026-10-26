"""
Database CRUD operations for Students, Rooms, Allocations, Policy Rules, and Audit Results.
Uses SQLAlchemy session and parameterized SQL queries to maintain clarity and inspectability.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd


# ---------------------------------------------------------------------------
# Students CRUD
# ---------------------------------------------------------------------------
def get_students(
    db: Session,
    category: Optional[str] = None,
    year: Optional[int] = None,
    gender: Optional[str] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    special_needs: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Retrieves students with optional filters, search, and pagination."""
    query = "SELECT s.*, a.room_id AS allocated_room_id FROM students s LEFT JOIN allocations a ON s.student_id = a.student_id WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM students s WHERE 1=1"
    params: Dict[str, Any] = {}

    if category:
        query += " AND s.category = :category"
        count_query += " AND s.category = :category"
        params["category"] = category
    if year is not None:
        query += " AND s.year = :year"
        count_query += " AND s.year = :year"
        params["year"] = year
    if gender:
        query += " AND s.gender = :gender"
        count_query += " AND s.gender = :gender"
        params["gender"] = gender
    if min_distance is not None:
        query += " AND s.distance_km >= :min_dist"
        count_query += " AND s.distance_km >= :min_dist"
        params["min_dist"] = min_distance
    if max_distance is not None:
        query += " AND s.distance_km <= :max_dist"
        count_query += " AND s.distance_km <= :max_dist"
        params["max_dist"] = max_distance
    if special_needs is not None:
        query += " AND s.special_needs = :special_needs"
        count_query += " AND s.special_needs = :special_needs"
        params["special_needs"] = special_needs
    if search:
        query += " AND (s.name LIKE :search OR s.student_id LIKE :search)"
        count_query += " AND (s.name LIKE :search OR s.student_id LIKE :search)"
        params["search"] = f"%{search}%"

    total = db.execute(text(count_query), params).scalar() or 0

    query += " ORDER BY s.student_id ASC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    rows = db.execute(text(query), params).mappings().all()
    students_list = [dict(row) for row in rows]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": students_list
    }


def get_student_by_id(db: Session, student_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT s.*, a.room_id AS allocated_room_id FROM students s LEFT JOIN allocations a ON s.student_id = a.student_id WHERE s.student_id = :sid"),
        {"sid": student_id}
    ).mappings().first()
    return dict(row) if row else None


def create_student(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
    db.execute(
        text("""
            INSERT INTO students (student_id, name, gender, year, cgpa, category, distance_km, special_needs)
            VALUES (:student_id, :name, :gender, :year, :cgpa, :category, :distance_km, :special_needs)
        """),
        data
    )
    db.commit()
    return get_student_by_id(db, data["student_id"])


def update_student(db: Session, student_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    updates = []
    params = {"sid": student_id}
    for k, v in data.items():
        if k != "student_id":
            updates.append(f"{k} = :{k}")
            params[k] = v

    if updates:
        db.execute(
            text(f"UPDATE students SET {', '.join(updates)} WHERE student_id = :sid"),
            params
        )
        db.commit()
    return get_student_by_id(db, student_id)


def delete_student(db: Session, student_id: str) -> bool:
    res = db.execute(text("DELETE FROM students WHERE student_id = :sid"), {"sid": student_id})
    db.commit()
    return res.rowcount > 0


# ---------------------------------------------------------------------------
# Rooms CRUD
# ---------------------------------------------------------------------------
def get_rooms(
    db: Session,
    hostel: Optional[str] = None,
    gender: Optional[str] = None,
    floor: Optional[int] = None,
    accessible: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Retrieves rooms with optional filters, search, and pagination."""
    query = "SELECT r.*, a.student_id AS allocated_student_id FROM rooms r LEFT JOIN allocations a ON r.room_id = a.room_id WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM rooms r WHERE 1=1"
    params: Dict[str, Any] = {}

    if hostel:
        query += " AND r.hostel = :hostel"
        count_query += " AND r.hostel = :hostel"
        params["hostel"] = hostel
    if gender:
        query += " AND r.gender = :gender"
        count_query += " AND r.gender = :gender"
        params["gender"] = gender
    if floor is not None:
        query += " AND r.floor = :floor"
        count_query += " AND r.floor = :floor"
        params["floor"] = floor
    if accessible is not None:
        query += " AND r.accessible = :accessible"
        count_query += " AND r.accessible = :accessible"
        params["accessible"] = accessible
    if search:
        query += " AND (r.room_id LIKE :search OR r.hostel LIKE :search)"
        count_query += " AND (r.room_id LIKE :search OR r.hostel LIKE :search)"
        params["search"] = f"%{search}%"

    total = db.execute(text(count_query), params).scalar() or 0

    query += " ORDER BY r.room_id ASC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    rows = db.execute(text(query), params).mappings().all()
    rooms_list = [dict(row) for row in rows]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": rooms_list
    }


def get_room_by_id(db: Session, room_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT r.*, a.student_id AS allocated_student_id FROM rooms r LEFT JOIN allocations a ON r.room_id = a.room_id WHERE r.room_id = :rid"),
        {"rid": room_id}
    ).mappings().first()
    return dict(row) if row else None


def create_room(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
    db.execute(
        text("""
            INSERT INTO rooms (room_id, hostel, gender, floor, mess_distance_m, accessible)
            VALUES (:room_id, :hostel, :gender, :floor, :mess_distance_m, :accessible)
        """),
        data
    )
    db.commit()
    return get_room_by_id(db, data["room_id"])


def update_room(db: Session, room_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    updates = []
    params = {"rid": room_id}
    for k, v in data.items():
        if k != "room_id":
            updates.append(f"{k} = :{k}")
            params[k] = v

    if updates:
        db.execute(
            text(f"UPDATE rooms SET {', '.join(updates)} WHERE room_id = :rid"),
            params
        )
        db.commit()
    return get_room_by_id(db, room_id)


def delete_room(db: Session, room_id: str) -> bool:
    res = db.execute(text("DELETE FROM rooms WHERE room_id = :rid"), {"rid": room_id})
    db.commit()
    return res.rowcount > 0


# ---------------------------------------------------------------------------
# Allocations CRUD
# ---------------------------------------------------------------------------
def get_all_allocations(db: Session) -> List[Dict[str, Any]]:
    rows = db.execute(text("SELECT student_id, room_id FROM allocations")).mappings().all()
    return [dict(row) for row in rows]


def update_allocation(db: Session, student_id: str, room_id: Optional[str]) -> bool:
    """Assigns, swaps, or unallocates a room for a student."""
    if not room_id:
        db.execute(text("DELETE FROM allocations WHERE student_id = :sid"), {"sid": student_id})
        db.commit()
        return True

    # If room is already occupied, remove old occupant
    db.execute(text("DELETE FROM allocations WHERE room_id = :rid"), {"rid": room_id})
    # If student had prior room, remove
    db.execute(text("DELETE FROM allocations WHERE student_id = :sid"), {"sid": student_id})
    # Insert new allocation
    db.execute(
        text("INSERT INTO allocations (student_id, room_id) VALUES (:sid, :rid)"),
        {"sid": student_id, "rid": room_id}
    )
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Policy Rules CRUD
# ---------------------------------------------------------------------------
def get_policy_rules(db: Session) -> Dict[str, float]:
    rows = db.execute(text("SELECT rule_key, value FROM policy_rules")).mappings().all()
    return {row["rule_key"]: float(row["value"]) for row in rows}


def update_policy_rules(db: Session, rules: Dict[str, float]) -> Dict[str, float]:
    for k, v in rules.items():
        exists = db.execute(text("SELECT 1 FROM policy_rules WHERE rule_key = :k"), {"k": k}).first()
        if exists:
            db.execute(text("UPDATE policy_rules SET value = :v WHERE rule_key = :k"), {"k": k, "v": float(v)})
        else:
            db.execute(text("INSERT INTO policy_rules (rule_key, value) VALUES (:k, :v)"), {"k": k, "v": float(v)})
    db.commit()
    return get_policy_rules(db)


# ---------------------------------------------------------------------------
# Bulk Data for Live Audit
# ---------------------------------------------------------------------------
def get_audit_cohort_data(db: Session) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetches all students, rooms, and allocations as DataFrames for audit computations."""
    students_rows = db.execute(text("SELECT * FROM students")).mappings().all()
    rooms_rows = db.execute(text("SELECT * FROM rooms")).mappings().all()
    alloc_rows = db.execute(text("SELECT * FROM allocations")).mappings().all()

    df_students = pd.DataFrame([dict(r) for r in students_rows])
    df_rooms = pd.DataFrame([dict(r) for r in rooms_rows])
    df_alloc = pd.DataFrame([dict(r) for r in alloc_rows])

    return df_students, df_rooms, df_alloc


def save_audit_results(db: Session, audited_students: List[Dict[str, Any]]) -> None:
    """Persists audit outcomes into the audit_results table."""
    db.execute(text("DELETE FROM audit_results"))
    for s in audited_students:
        db.execute(
            text("""
                INSERT INTO audit_results (
                    student_id, priority_score, expected_room_id, actual_room_id,
                    deviation, status, hard_rule_violation
                ) VALUES (
                    :student_id, :priority_score, :expected_room_id, :actual_room_id,
                    :deviation, :status, :hard_rule_violation
                )
            """),
            {
                "student_id": s["student_id"],
                "priority_score": s["priority_score"],
                "expected_room_id": s["expected_room_id"],
                "actual_room_id": s["actual_room_id"],
                "deviation": s["deviation"],
                "status": s["status"],
                "hard_rule_violation": s["hard_rule_violation"],
            }
        )
    db.commit()
