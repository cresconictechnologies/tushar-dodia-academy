"""
Tushar Dodia Academy - Multi-Backend Persistent Database Engine
Supports Cloud PostgreSQL (Render / Supabase / Neon via DATABASE_URL)
and Local SQLite with WAL mode, with automatic JSON mirror synchronization.
"""

import os
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger("dodia.database")

BASE_DIR = Path(__file__).resolve().parent.parent
DOSSIER_DIR = BASE_DIR / "dossier"
DOSSIER_DIR.mkdir(exist_ok=True)

SQLITE_DB_PATH = DOSSIER_DIR / "academy.db"
SUBMISSIONS_JSON = DOSSIER_DIR / "submissions.json"
INQUIRIES_JSON = DOSSIER_DIR / "inquiries.json"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Try importing psycopg2 for Postgres support
HAS_PSYCOPG2 = False
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

def is_postgres_configured() -> bool:
    """Returns True if a valid PostgreSQL DATABASE_URL is provided and psycopg2 is available."""
    return bool(DATABASE_URL and HAS_PSYCOPG2 and (
        DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")
    ))

def get_pg_connection():
    """Establishes a connection to PostgreSQL with SSL handling."""
    conn_url = DATABASE_URL
    if conn_url.startswith("postgres://"):
        conn_url = conn_url.replace("postgres://", "postgresql://", 1)
    
    # Auto-add sslmode=require for cloud instances if not specified and not local
    if "sslmode=" not in conn_url and "localhost" not in conn_url and "127.0.0.1" not in conn_url:
        sep = "&" if "?" in conn_url else "?"
        conn_url = f"{conn_url}{sep}sslmode=require"

    return psycopg2.connect(conn_url, cursor_factory=RealDictCursor, connect_timeout=15)

def get_sqlite_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection to SQLite with WAL mode."""
    conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Compatibility alias for legacy callers
get_db_connection = get_sqlite_connection

def get_database_status() -> Dict[str, Any]:
    """Returns the active database engine type and connectivity status."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            conn.close()
            return {"engine": "PostgreSQL (Cloud Managed)", "connected": True, "ssl": True}
        except Exception as e:
            logger.warning("PostgreSQL ping failed, falling back to SQLite: %s", e)
    
    return {"engine": "SQLite (Local WAL)", "connected": True, "path": str(SQLITE_DB_PATH.name)}

def init_db():
    """Initializes schema on whichever database is active, and syncs initial data."""
    if is_postgres_configured():
        try:
            _init_pg_schema()
            return
        except Exception as e:
            logger.error("Failed to initialize PostgreSQL schema, falling back to SQLite: %s", e)

    _init_sqlite_schema()

def _init_pg_schema():
    """Initializes tables on PostgreSQL."""
    conn = get_pg_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id VARCHAR(64) PRIMARY KEY,
        tier VARCHAR(32) NOT NULL,
        student_name VARCHAR(255) NOT NULL,
        student_class VARCHAR(128),
        school_name VARCHAR(255),
        parent_name VARCHAR(255),
        parent_phone VARCHAR(64) NOT NULL,
        parent_email VARCHAR(255),
        created_at VARCHAR(64) NOT NULL,
        academic_score INT DEFAULT 85,
        consistency_score INT DEFAULT 50,
        idea_score INT DEFAULT 85,
        completion_score INT DEFAULT 40,
        execution_gap INT DEFAULT 45,
        consistency_risk VARCHAR(64) DEFAULT 'MODERATE',
        status VARCHAR(128) DEFAULT 'New Submission',
        notes TEXT DEFAULT '',
        pdf_filename VARCHAR(255),
        pdf_generated INT DEFAULT 0,
        performance_json TEXT,
        behaviour_json TEXT,
        strengths_json TEXT,
        risks_json TEXT,
        user_answers_json TEXT,
        updated_at VARCHAR(64)
    );
    CREATE TABLE IF NOT EXISTS inquiries (
        id VARCHAR(64) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        phone VARCHAR(64) NOT NULL,
        org VARCHAR(255),
        program_name VARCHAR(255),
        message TEXT,
        created_at VARCHAR(64) NOT NULL,
        status VARCHAR(128) DEFAULT 'New Inquiry',
        updated_at VARCHAR(64)
    );
    CREATE TABLE IF NOT EXISTS admin_sessions (
        token VARCHAR(255) PRIMARY KEY,
        username VARCHAR(128) NOT NULL,
        created_at VARCHAR(64) NOT NULL,
        expires_at VARCHAR(64) NOT NULL,
        last_activity VARCHAR(64) NOT NULL,
        ip_address VARCHAR(64)
    );
    CREATE TABLE IF NOT EXISTS login_attempts (
        id SERIAL PRIMARY KEY,
        ip_address VARCHAR(64) NOT NULL,
        attempted_at VARCHAR(64) NOT NULL,
        success INT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_pg_attempts_ip ON login_attempts(ip_address, attempted_at);
    CREATE INDEX IF NOT EXISTS idx_pg_submissions_created ON submissions(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_pg_inquiries_created ON inquiries(created_at DESC);
    """)
    conn.commit()
    conn.close()
    logger.info("Initialized Cloud PostgreSQL database tables successfully.")

def _init_sqlite_schema():
    """Initializes tables on SQLite."""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS submissions (
        id TEXT PRIMARY KEY,
        tier TEXT NOT NULL,
        student_name TEXT NOT NULL,
        student_class TEXT,
        school_name TEXT,
        parent_name TEXT,
        parent_phone TEXT NOT NULL,
        parent_email TEXT,
        created_at TEXT NOT NULL,
        academic_score INTEGER DEFAULT 85,
        consistency_score INTEGER DEFAULT 50,
        idea_score INTEGER DEFAULT 85,
        completion_score INTEGER DEFAULT 40,
        execution_gap INTEGER DEFAULT 45,
        consistency_risk TEXT DEFAULT 'MODERATE',
        status TEXT DEFAULT 'New Submission',
        notes TEXT DEFAULT '',
        pdf_filename TEXT,
        pdf_generated INTEGER DEFAULT 0,
        performance_json TEXT,
        behaviour_json TEXT,
        strengths_json TEXT,
        risks_json TEXT,
        user_answers_json TEXT,
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS inquiries (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT NOT NULL,
        org TEXT,
        program_name TEXT,
        message TEXT,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'New Inquiry',
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS admin_sessions (
        token TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        last_activity TEXT NOT NULL,
        ip_address TEXT
    );
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        attempted_at TEXT NOT NULL,
        success INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_attempts_ip ON login_attempts(ip_address, attempted_at);
    CREATE INDEX IF NOT EXISTS idx_submissions_created ON submissions(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries(created_at DESC);
    """)
    conn.commit()
    conn.close()
    logger.info("Initialized SQLite database tables successfully.")

def _row_to_submission(row: Any) -> Dict[str, Any]:
    """Converts a database row into a full Submission dictionary."""
    def safe_json(val, default):
        if not val:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

    # Handles both sqlite3.Row and psycopg2 dict
    return {
        "id": row["id"],
        "tier": row["tier"],
        "student_name": row["student_name"],
        "student_class": row["student_class"] or "",
        "school_name": row["school_name"] or "",
        "parent_name": row["parent_name"] or "",
        "parent_phone": row["parent_phone"] or "",
        "parent_email": row["parent_email"] or "",
        "created_at": row["created_at"],
        "academic_score": row["academic_score"],
        "consistency_score": row["consistency_score"],
        "idea_score": row["idea_score"],
        "completion_score": row["completion_score"],
        "execution_gap": row["execution_gap"],
        "consistency_risk": row["consistency_risk"],
        "status": row["status"] or "New Submission",
        "notes": row["notes"] or "",
        "pdf_filename": row["pdf_filename"] or "",
        "pdf_generated": bool(row["pdf_generated"]),
        "performance": safe_json(row["performance_json"], {}),
        "behaviour": safe_json(row["behaviour_json"], {}),
        "strengths": safe_json(row["strengths_json"], []),
        "risks": safe_json(row["risks_json"], []),
        "user_answers": safe_json(row["user_answers_json"], {})
    }

def _row_to_inquiry(row: Any) -> Dict[str, Any]:
    """Converts a database row into an Inquiry dictionary."""
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"] or "",
        "phone": row["phone"] or "",
        "org": row["org"] or "",
        "program_name": row["program_name"] or "Institutional Consulting",
        "message": row["message"] or "",
        "created_at": row["created_at"],
        "status": row["status"] or "New Inquiry"
    }

def sync_json_backups():
    """Flushes active database state to JSON backup files for portability."""
    try:
        subs = get_all_submissions()
        with open(SUBMISSIONS_JSON, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)

        inqs = get_all_inquiries()
        with open(INQUIRIES_JSON, "w", encoding="utf-8") as f:
            json.dump(inqs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Could not sync JSON backups: %s", e)

# ------------------------------------------------------------------------------
# CRUD: Submissions
# ------------------------------------------------------------------------------

def get_all_submissions() -> List[Dict[str, Any]]:
    """Loads all submissions ordered by creation timestamp."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM submissions ORDER BY created_at DESC;")
            rows = cur.fetchall()
            conn.close()
            return [_row_to_submission(r) for r in rows]
        except Exception as e:
            logger.error("Postgres get_all_submissions failed, falling back: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM submissions ORDER BY created_at DESC;")
        rows = cur.fetchall()
        return [_row_to_submission(r) for r in rows]
    finally:
        conn.close()

def get_submission_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single submission by its report ID."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM submissions WHERE id = %s;", (report_id,))
            row = cur.fetchone()
            conn.close()
            return _row_to_submission(row) if row else None
        except Exception as e:
            logger.error("Postgres get_submission_by_id failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM submissions WHERE id = ?;", (report_id,))
        row = cur.fetchone()
        return _row_to_submission(row) if row else None
    finally:
        conn.close()

def save_new_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts or replaces an assessment record and updates mirror."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vals = (
        data.get("id"),
        data.get("tier", "senior"),
        data.get("student_name", "Student"),
        data.get("student_class", ""),
        data.get("school_name", ""),
        data.get("parent_name", ""),
        data.get("parent_phone", ""),
        data.get("parent_email", ""),
        data.get("created_at", now_str),
        data.get("academic_score", 85),
        data.get("consistency_score", 50),
        data.get("idea_score", 85),
        data.get("completion_score", 40),
        data.get("execution_gap", max(data.get("idea_score", 85) - data.get("completion_score", 40), 0)),
        data.get("consistency_risk", "MODERATE"),
        data.get("status", "New Submission"),
        data.get("notes", ""),
        data.get("pdf_filename", ""),
        1 if data.get("pdf_generated") else 0,
        json.dumps(data.get("performance", {})),
        json.dumps(data.get("behaviour", {})),
        json.dumps(data.get("strengths", [])),
        json.dumps(data.get("risks", [])),
        json.dumps(data.get("user_answers", {})),
        now_str
    )

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM submissions WHERE id = %s;", (data.get("id"),))
            cur.execute("""
            INSERT INTO submissions (
                id, tier, student_name, student_class, school_name,
                parent_name, parent_phone, parent_email, created_at,
                academic_score, consistency_score, idea_score, completion_score,
                execution_gap, consistency_risk, status, notes,
                pdf_filename, pdf_generated,
                performance_json, behaviour_json, strengths_json, risks_json,
                user_answers_json, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s
            );
            """, vals)
            conn.commit()
            conn.close()
            sync_json_backups()
            return data
        except Exception as e:
            logger.error("Postgres save_new_submission failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM submissions WHERE id = ?;", (data.get("id"),))
        cur.execute("""
        INSERT INTO submissions (
            id, tier, student_name, student_class, school_name,
            parent_name, parent_phone, parent_email, created_at,
            academic_score, consistency_score, idea_score, completion_score,
            execution_gap, consistency_risk, status, notes,
            pdf_filename, pdf_generated,
            performance_json, behaviour_json, strengths_json, risks_json,
            user_answers_json, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?,
            ?, ?
        );
        """, vals)
        conn.commit()
        sync_json_backups()
        return data
    finally:
        conn.close()

def update_submission(report_id: str, status: Optional[str] = None, notes: Optional[str] = None) -> bool:
    """Updates status or mentorship notes for a submission."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            if status is not None and notes is not None:
                cur.execute("UPDATE submissions SET status = %s, notes = %s, updated_at = %s WHERE id = %s;", (status, notes, now_str, report_id))
            elif status is not None:
                cur.execute("UPDATE submissions SET status = %s, updated_at = %s WHERE id = %s;", (status, now_str, report_id))
            elif notes is not None:
                cur.execute("UPDATE submissions SET notes = %s, updated_at = %s WHERE id = %s;", (notes, now_str, report_id))
            affected = cur.rowcount > 0
            conn.commit()
            conn.close()
            if affected:
                sync_json_backups()
            return affected
        except Exception as e:
            logger.error("Postgres update_submission failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        if status is not None and notes is not None:
            cur.execute("UPDATE submissions SET status = ?, notes = ?, updated_at = ? WHERE id = ?;", (status, notes, now_str, report_id))
        elif status is not None:
            cur.execute("UPDATE submissions SET status = ?, updated_at = ? WHERE id = ?;", (status, now_str, report_id))
        elif notes is not None:
            cur.execute("UPDATE submissions SET notes = ?, updated_at = ? WHERE id = ?;", (notes, now_str, report_id))
        affected = cur.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups()
        return affected
    finally:
        conn.close()

def update_submission_pdf(report_id: str, pdf_filename: str) -> bool:
    """Updates the generated PDF filename and flag for a submission."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("UPDATE submissions SET pdf_filename = %s, pdf_generated = 1, updated_at = %s WHERE id = %s;", (pdf_filename, now_str, report_id))
            affected = cur.rowcount > 0
            conn.commit()
            conn.close()
            if affected:
                sync_json_backups()
            return affected
        except Exception as e:
            logger.error("Postgres update_submission_pdf failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE submissions SET pdf_filename = ?, pdf_generated = 1, updated_at = ? WHERE id = ?;", (pdf_filename, now_str, report_id))
        affected = cur.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups()
        return affected
    finally:
        conn.close()

def db_insert_or_replace_submission_raw(cursor: Any, r: Dict[str, Any]):
    """Compatibility helper to insert or replace submission using an existing cursor."""
    save_new_submission(r)

def db_insert_or_replace_inquiry_raw(cursor: Any, r: Dict[str, Any]):
    """Compatibility helper to insert or replace inquiry using an existing cursor."""
    save_new_inquiry(r)

def delete_submission(report_id: str) -> bool:
    """Permanently deletes a submission."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM submissions WHERE id = %s;", (report_id,))
            affected = cur.rowcount > 0
            conn.commit()
            conn.close()
            if affected:
                sync_json_backups()
            return affected
        except Exception as e:
            logger.error("Postgres delete_submission failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM submissions WHERE id = ?;", (report_id,))
        affected = cur.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups()
        return affected
    finally:
        conn.close()

# ------------------------------------------------------------------------------
# CRUD: Inquiries
# ------------------------------------------------------------------------------

def get_all_inquiries() -> List[Dict[str, Any]]:
    """Loads all client and institutional inquiries."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inquiries ORDER BY created_at DESC;")
            rows = cur.fetchall()
            conn.close()
            return [_row_to_inquiry(r) for r in rows]
        except Exception as e:
            logger.error("Postgres get_all_inquiries failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM inquiries ORDER BY created_at DESC;")
        rows = cur.fetchall()
        return [_row_to_inquiry(r) for r in rows]
    finally:
        conn.close()

def get_inquiry_by_id(inquiry_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single inquiry by its ID."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inquiries WHERE id = %s;", (inquiry_id,))
            row = cur.fetchone()
            conn.close()
            return _row_to_inquiry(row) if row else None
        except Exception as e:
            logger.error("Postgres get_inquiry_by_id failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM inquiries WHERE id = ?;", (inquiry_id,))
        row = cur.fetchone()
        return _row_to_inquiry(row) if row else None
    finally:
        conn.close()

def save_new_inquiry(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new client inquiry and updates mirrors."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vals = (
        data.get("id"),
        data.get("name", "Client"),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("org", ""),
        data.get("program_name", "Institutional Consulting"),
        data.get("message", ""),
        data.get("created_at", now_str),
        data.get("status", "New Inquiry"),
        now_str
    )

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM inquiries WHERE id = %s;", (data.get("id"),))
            cur.execute("""
            INSERT INTO inquiries (
                id, name, email, phone, org, program_name, message, created_at, status, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, vals)
            conn.commit()
            conn.close()
            sync_json_backups()
            return data
        except Exception as e:
            logger.error("Postgres save_new_inquiry failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM inquiries WHERE id = ?;", (data.get("id"),))
        cur.execute("""
        INSERT INTO inquiries (
            id, name, email, phone, org, program_name, message, created_at, status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, vals)
        conn.commit()
        sync_json_backups()
        return data
    finally:
        conn.close()

def update_inquiry(inquiry_id: str, status: str) -> bool:
    """Updates status for an inquiry."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("UPDATE inquiries SET status = %s, updated_at = %s WHERE id = %s;", (status, now_str, inquiry_id))
            affected = cur.rowcount > 0
            conn.commit()
            conn.close()
            if affected:
                sync_json_backups()
            return affected
        except Exception as e:
            logger.error("Postgres update_inquiry failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE inquiries SET status = ?, updated_at = ? WHERE id = ?;", (status, now_str, inquiry_id))
        affected = cur.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups()
        return affected
    finally:
        conn.close()

def delete_inquiry(inquiry_id: str) -> bool:
    """Permanently deletes an inquiry."""
    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM inquiries WHERE id = %s;", (inquiry_id,))
            affected = cur.rowcount > 0
            conn.commit()
            conn.close()
            if affected:
                sync_json_backups()
            return affected
        except Exception as e:
            logger.error("Postgres delete_inquiry failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM inquiries WHERE id = ?;", (inquiry_id,))
        affected = cur.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups()
        return affected
    finally:
        conn.close()

# ------------------------------------------------------------------------------
# Security: Session Management & Rate Limiting
# ------------------------------------------------------------------------------

def record_login_attempt(ip_address: str, success: bool):
    """Logs an authentication attempt for IP brute-force protection."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO login_attempts (ip_address, attempted_at, success) VALUES (%s, %s, %s);", (ip_address, now_str, 1 if success else 0))
            conn.commit()
            conn.close()
            return
        except Exception as e:
            logger.error("Postgres record_login_attempt failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO login_attempts (ip_address, attempted_at, success) VALUES (?, ?, ?);", (ip_address, now_str, 1 if success else 0))
        conn.commit()
    finally:
        conn.close()

def is_ip_locked(ip_address: str, max_failures: int = 5, window_minutes: int = 15) -> bool:
    """Checks whether an IP has exceeded failed login threshold within time window."""
    cutoff = (datetime.now() - timedelta(minutes=window_minutes)).strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as failed_count FROM login_attempts WHERE ip_address = %s AND attempted_at >= %s AND success = 0;", (ip_address, cutoff))
            res = cur.fetchone()
            conn.close()
            return res["failed_count"] >= max_failures
        except Exception as e:
            logger.error("Postgres is_ip_locked failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as failed_count FROM login_attempts WHERE ip_address = ? AND attempted_at >= ? AND success = 0;", (ip_address, cutoff))
        res = cur.fetchone()
        return res["failed_count"] >= max_failures
    finally:
        conn.close()

def create_admin_session(token: str, username: str, expires_in_hours: int = 4, ip_address: str = "") -> str:
    """Persists a new cryptographic session token with an expiration timestamp."""
    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    expires_at = (now + timedelta(hours=expires_in_hours)).strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM admin_sessions WHERE token = %s;", (token,))
            cur.execute("""
            INSERT INTO admin_sessions (token, username, created_at, expires_at, last_activity, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s);
            """, (token, username, created_at, expires_at, created_at, ip_address))
            conn.commit()
            conn.close()
            return token
        except Exception as e:
            logger.error("Postgres create_admin_session failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO admin_sessions (token, username, created_at, expires_at, last_activity, ip_address)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (token, username, created_at, expires_at, created_at, ip_address))
        conn.commit()
        return token
    finally:
        conn.close()

def validate_admin_session(token: str) -> bool:
    """Validates session token existence and verifies it has not expired."""
    if not token:
        return False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM admin_sessions WHERE token = %s AND expires_at > %s;", (token, now_str))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE admin_sessions SET last_activity = %s WHERE token = %s;", (now_str, token))
                conn.commit()
                conn.close()
                return True
            conn.close()
            return False
        except Exception as e:
            logger.error("Postgres validate_admin_session failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin_sessions WHERE token = ? AND expires_at > ?;", (token, now_str))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE admin_sessions SET last_activity = ? WHERE token = ?;", (now_str, token))
            conn.commit()
            return True
        return False
    finally:
        conn.close()

def delete_admin_session(token: str):
    """Revokes an admin session token."""
    if not token:
        return

    if is_postgres_configured():
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM admin_sessions WHERE token = %s;", (token,))
            conn.commit()
            conn.close()
            return
        except Exception as e:
            logger.error("Postgres delete_admin_session failed: %s", e)

    conn = get_sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM admin_sessions WHERE token = ?;", (token,))
        conn.commit()
    finally:
        conn.close()

# Auto-initialize database schema on startup
init_db()
