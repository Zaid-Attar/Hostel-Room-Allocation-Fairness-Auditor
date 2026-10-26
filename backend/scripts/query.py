"""
Interactive SQL Query Runner for VS Code Terminal.
Allows running arbitrary SQL commands against the project database with pretty table output.

Usage:
  python backend/scripts/query.py "SELECT * FROM students LIMIT 5;"
  python backend/scripts/query.py "SELECT category, count(*), round(avg(cgpa), 2) FROM students GROUP BY category;"
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.db import get_engine

def run_query(sql: str):
    engine = get_engine()
    # Configure pandas display
    pd.set_option('display.max_columns', 15)
    pd.set_option('display.width', 120)
    
    try:
        with engine.connect() as conn:
            # Check if it's a SELECT query
            if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("PRAGMA") or sql.strip().upper().startswith("EXPLAIN"):
                df = pd.read_sql(text(sql), conn)
                print("\nQuery Result:")
                print("=" * 70)
                if df.empty:
                    print("(Empty result set)")
                else:
                    print(df.to_string(index=False))
                print("=" * 70)
                print(f"Total Rows: {len(df)}\n")
            else:
                result = conn.execute(text(sql))
                conn.commit()
                print(f"\n[OK] Statement executed successfully. Rows affected: {result.rowcount}\n")
    except Exception as e:
        print(f"\n[SQL Error] {e}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/query.py \"<SQL_STATEMENT>\"")
        print("Example: python backend/scripts/query.py \"SELECT student_id, name, cgpa, category FROM students LIMIT 5;\"")
        sys.exit(0)
    
    query_str = " ".join(sys.argv[1:])
    run_query(query_str)
