"""
Data validation module for student, room, and allocation datasets.
Called by backend/scripts/load_csv.py before loading data into the database.
"""

from typing import Dict, List, Tuple
import pandas as pd

VALID_GENDERS = {"M", "F"}
VALID_CATEGORIES = {"General", "OBC", "SC", "ST", "EWS"}

def validate_datasets(
    students_df: pd.DataFrame,
    rooms_df: pd.DataFrame,
    allocation_df: pd.DataFrame
) -> Tuple[List[str], List[str]]:
    """
    Validates the 3 input DataFrames according to Section 7 validation rules.
    Returns:
        errors: List of critical error messages that should stop data loading.
        warnings: List of non-critical warning messages that still allow loading.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Check duplicate student IDs
    dup_students = students_df[students_df.duplicated("student_id", keep=False)]
    if not dup_students.empty:
        errors.append(f"Duplicate student_id found: {dup_students['student_id'].unique().tolist()}")

    # 2. Check duplicate room IDs
    dup_rooms = rooms_df[rooms_df.duplicated("room_id", keep=False)]
    if not dup_rooms.empty:
        errors.append(f"Duplicate room_id found: {dup_rooms['room_id'].unique().tolist()}")

    # 3. Check CGPA within [0, 10]
    invalid_cgpa = students_df[(students_df["cgpa"] < 0.0) | (students_df["cgpa"] > 10.0)]
    if not invalid_cgpa.empty:
        errors.append(f"Invalid CGPA values outside [0, 10] for students: {invalid_cgpa['student_id'].tolist()}")

    # 4. Check valid genders in students and rooms
    invalid_std_gender = students_df[~students_df["gender"].isin(VALID_GENDERS)]
    if not invalid_std_gender.empty:
        errors.append(f"Invalid gender in students: {invalid_std_gender['student_id'].tolist()}")

    invalid_room_gender = rooms_df[~rooms_df["gender"].isin(VALID_GENDERS)]
    if not invalid_room_gender.empty:
        errors.append(f"Invalid gender in rooms: {invalid_room_gender['room_id'].tolist()}")

    # 5. Check valid categories in students
    invalid_cat = students_df[~students_df["category"].isin(VALID_CATEGORIES)]
    if not invalid_cat.empty:
        errors.append(f"Invalid category in students: {invalid_cat['student_id'].tolist()}")

    # 6. Check allocations referencing unknown students or rooms
    std_id_set = set(students_df["student_id"])
    room_id_set = set(rooms_df["room_id"])

    unknown_std = allocation_df[~allocation_df["student_id"].isin(std_id_set)]
    if not unknown_std.empty:
        errors.append(f"Allocation references unknown student_ids: {unknown_std['student_id'].tolist()}")

    unknown_room = allocation_df[~allocation_df["room_id"].isin(room_id_set)]
    if not unknown_room.empty:
        errors.append(f"Allocation references unknown room_ids: {unknown_room['room_id'].tolist()}")

    # 7. Check room assigned to more than one student
    dup_alloc_rooms = allocation_df[allocation_df.duplicated("room_id", keep=False)]
    if not dup_alloc_rooms.empty:
        errors.append(f"Room assigned to multiple students: {dup_alloc_rooms['room_id'].unique().tolist()}")

    # 8. Check student assigned multiple rooms
    dup_alloc_std = allocation_df[allocation_df.duplicated("student_id", keep=False)]
    if not dup_alloc_std.empty:
        errors.append(f"Student assigned multiple rooms: {dup_alloc_std['student_id'].unique().tolist()}")

    # 9. Check student placed in room of opposite gender
    student_gender_map = dict(zip(students_df["student_id"], students_df["gender"]))
    room_gender_map = dict(zip(rooms_df["room_id"], rooms_df["gender"]))

    gender_mismatches = []
    for _, row in allocation_df.iterrows():
        sid = row["student_id"]
        rid = row["room_id"]
        s_gender = student_gender_map.get(sid)
        r_gender = room_gender_map.get(rid)
        if s_gender and r_gender and s_gender != r_gender:
            gender_mismatches.append(f"Student {sid} ({s_gender}) placed in Room {rid} ({r_gender})")

    if gender_mismatches:
        errors.append(f"Gender mismatch violations ({len(gender_mismatches)} instances): {gender_mismatches[:5]}")

    # --- Warnings that still load ---
    allocated_std_set = set(allocation_df["student_id"])
    allocated_room_set = set(allocation_df["room_id"])

    unallocated_students = [sid for sid in std_id_set if sid not in allocated_std_set]
    if unallocated_students:
        warnings.append(f"{len(unallocated_students)} student(s) have no allocation: {unallocated_students[:5]}")

    empty_rooms = [rid for rid in room_id_set if rid not in allocated_room_set]
    if empty_rooms:
        warnings.append(f"{len(empty_rooms)} room(s) have no allocated student: {empty_rooms[:5]}")

    return errors, warnings
