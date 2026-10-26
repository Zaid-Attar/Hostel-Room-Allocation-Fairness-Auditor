"""
CSV Data Loader and Database Initializer.
Loads data/students.csv, data/rooms.csv, and data/allocation.csv into the database
after running strict validation checks from backend.app.validation.
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT_DIR))

from backend.app.db import engine, get_engine
from backend.app.validation import validate_datasets

DATA_DIR = ROOT_DIR / "data"
SCHEMA_PATH = CURRENT_DIR / "schema.sql"

DEFAULT_POLICY_RULES = [
    ("w_cgpa", 0.35),
    ("w_distance", 0.20),
    ("w_year", 0.20),
    ("w_category", 0.10),
    ("w_special_needs", 0.15),
    ("w_room_mess", 0.60),
    ("w_room_floor", 0.40),
    ("tolerance_pct", 10.0),
]

def run_loader():
    print("=" * 60)
    print("Hostel Room Allocation Fairness Auditor - Database Loader")
    print("=" * 60)

    # 1. Check CSV files exist
    students_file = DATA_DIR / "students.csv"
    rooms_file = DATA_DIR / "rooms.csv"
    alloc_file = DATA_DIR / "allocation.csv"

    for f in [students_file, rooms_file, alloc_file]:
        if not f.exists():
            print(f"[FATAL ERROR] Required input file not found: {f}")
            print("Please run python backend/scripts/generate_data.py first.")
            sys.exit(1)

    print(f"Reading CSVs from: {DATA_DIR}")
    students_df = pd.read_csv(students_file)
    rooms_df = pd.read_csv(rooms_file)
    alloc_df = pd.read_csv(alloc_file)

    print(f"Loaded: {len(students_df)} students, {len(rooms_df)} rooms, {len(alloc_df)} allocations.")

    # 2. Run data validation checks
    print("\n--- Running Section 7 Data Checks ---")
    errors, warnings = validate_datasets(students_df, rooms_df, alloc_df)

    if warnings:
        print(f"[WARNINGS] ({len(warnings)} found):")
        for w in warnings:
            print(f"  * {w}")
    else:
        print("[OK] No data warnings.")

    if errors:
        print(f"\n[ERRORS] ({len(errors)} critical errors found! Loading aborted):")
        for e in errors:
            print(f"  ! {e}")
        sys.exit(1)
    else:
        print("[OK] All data integrity checks PASSED.")

    # 3. Create database tables from schema.sql
    print("\n--- Initializing Relational Database Tables ---")
    active_engine = get_engine()

    with active_engine.begin() as conn:
        # Drop existing tables to ensure clean update from previous schemas
        for tbl in ["audit_results", "allocations", "students", "rooms", "policy_rules"]:
            conn.execute(text(f"DROP TABLE IF EXISTS {tbl}"))

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Split and execute each statement
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        for stmt in statements:
            conn.execute(text(stmt))

    print("[OK] Tables created and cleared.")

    # 4. Insert data using pandas to_sql
    print("\n--- Loading Data into Database ---")
    students_df.to_sql("students", con=active_engine, if_exists="append", index=False)
    rooms_df.to_sql("rooms", con=active_engine, if_exists="append", index=False)
    alloc_df.to_sql("allocations", con=active_engine, if_exists="append", index=False)

    # Insert default policy rules
    policy_df = pd.DataFrame(DEFAULT_POLICY_RULES, columns=["rule_key", "value"])
    policy_df.to_sql("policy_rules", con=active_engine, if_exists="append", index=False)

    # 5. Verify row counts
    with active_engine.connect() as conn:
        std_count = conn.execute(text("SELECT COUNT(*) FROM students")).scalar()
        rm_count = conn.execute(text("SELECT COUNT(*) FROM rooms")).scalar()
        alloc_count = conn.execute(text("SELECT COUNT(*) FROM allocations")).scalar()
        policy_count = conn.execute(text("SELECT COUNT(*) FROM policy_rules")).scalar()

    print("\n--- Database Row Count Verification ---")
    print(f"  * students:     {std_count} rows")
    print(f"  * rooms:        {rm_count} rows")
    print(f"  * allocations:  {alloc_count} rows")
    print(f"  * policy_rules: {policy_count} rows")
    print("=" * 60)
    print("[SUCCESS] Phase 1 database load complete.")
    print("=" * 60)

if __name__ == "__main__":
    run_loader()
