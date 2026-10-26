"""
Database connection and session management module using SQLAlchemy.
Reads DATABASE_URL from .env with automatic SQLite fallback if MySQL is unreachable.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///hostel_auditor.db")
FALLBACK_TO_SQLITE = os.getenv("FALLBACK_TO_SQLITE", "true").lower() in ("true", "1", "yes")

def get_engine():
    """Initializes SQLAlchemy engine with fallback logic."""
    target_url = DATABASE_URL
    try:
        if target_url.startswith("mysql"):
            # Test quick connection to see if MySQL is actually listening
            engine = create_engine(target_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        else:
            return create_engine(target_url, connect_args={"check_same_thread": False})
    except Exception as exc:
        if FALLBACK_TO_SQLITE:
            sqlite_path = ROOT_DIR / "hostel_auditor.db"
            sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
            print(f"[DB Warning] Could not connect to {target_url} ({exc}). Using SQLite fallback: {sqlite_url}")
            return create_engine(sqlite_url, connect_args={"check_same_thread": False})
        raise exc

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
