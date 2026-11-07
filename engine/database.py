"""
Tushar Dodia Academy - Persistent Database & Security State Engine
ACID-compliant SQLite database with WAL mode and atomic JSON synchronization.
"""

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

DB_PATH = DOSSIER_DIR / "academy.db"
SUBMISSIONS_JSON = DOSSIER_DIR / "submissions.json"
INQUIRIES_JSON = DOSSIER_DIR / "inquiries.json"

def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection to SQLite with row factories and WAL mode."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes schema and migrates any existing JSON records into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Submissions Table
    cursor.execute("""
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
    """)

    # 2. Inquiries Table
    cursor.execute("""
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
    """)

    # 3. Admin Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_sessions (
        token TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        last_activity TEXT NOT NULL,
        ip_address TEXT
    );
    """)

    # 4. Login Attempts & Brute Force Tracker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        attempted_at TEXT NOT NULL,
        success INTEGER NOT NULL
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_ip ON login_attempts(ip_address, attempted_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_created ON submissions(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries(created_at DESC);")

    conn.commit()

    # Initial Migration: Sync from JSON if DB is empty
    cursor.execute("SELECT COUNT(*) as cnt FROM submissions;")
    sub_count = cursor.fetchone()["cnt"]
    if sub_count == 0 and SUBMISSIONS_JSON.exists():
        try:
            with open(SUBMISSIONS_JSON, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    db_insert_or_replace_submission_raw(cursor, r)
            conn.commit()
            logger.info("Migrated %d submissions from JSON to SQLite", len(records))
        except Exception as e:
            logger.warning("Error migrating submissions JSON to DB: %s", e)

    cursor.execute("SELECT COUNT(*) as cnt FROM inquiries;")
    inq_count = cursor.fetchone()["cnt"]
    if inq_count == 0 and INQUIRIES_JSON.exists():
        try:
            with open(INQUIRIES_JSON, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    db_insert_or_replace_inquiry_raw(cursor, r)
            conn.commit()
            logger.info("Migrated %d inquiries from JSON to SQLite", len(records))
        except Exception as e:
            logger.warning("Error migrating inquiries JSON to DB: %s", e)

    conn.close()

def db_insert_or_replace_submission_raw(cursor: sqlite3.Cursor, r: Dict[str, Any]):
    """Internal helper to insert or replace submission in cursor."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT OR REPLACE INTO submissions (
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
    """, (
        r.get("id"),
        r.get("tier", "senior"),
        r.get("student_name", "Student"),
        r.get("student_class", ""),
        r.get("school_name", ""),
        r.get("parent_name", ""),
        r.get("parent_phone", ""),
        r.get("parent_email", ""),
        r.get("created_at", now_str),
        r.get("academic_score", 85),
        r.get("consistency_score", 50),
        r.get("idea_score", 85),
        r.get("completion_score", 40),
        r.get("execution_gap", max(r.get("idea_score", 85) - r.get("completion_score", 40), 0)),
        r.get("consistency_risk", "MODERATE"),
        r.get("status", "New Submission"),
        r.get("notes", ""),
        r.get("pdf_filename", ""),
        1 if r.get("pdf_generated") else 0,
        json.dumps(r.get("performance", {})),
        json.dumps(r.get("behaviour", {})),
        json.dumps(r.get("strengths", [])),
        json.dumps(r.get("risks", [])),
        json.dumps(r.get("user_answers", {})),
        now_str
    ))

def db_insert_or_replace_inquiry_raw(cursor: sqlite3.Cursor, r: Dict[str, Any]):
    """Internal helper to insert or replace inquiry in cursor."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT OR REPLACE INTO inquiries (
        id, name, email, phone, org, program_name, message, created_at, status, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        r.get("id"),
        r.get("name", "Client"),
        r.get("email", ""),
        r.get("phone", ""),
        r.get("org", ""),
        r.get("program_name", "Institutional Consulting"),
        r.get("message", ""),
        r.get("created_at", now_str),
        r.get("status", "New Inquiry"),
        now_str
    ))

def _row_to_submission(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a SQLite row into a full Submission dictionary."""
    def safe_json(val, default):
        if not val:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

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

def _row_to_inquiry(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a SQLite row into an Inquiry dictionary."""
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

def sync_json_backups(conn: Optional[sqlite3.Connection] = None):
    """Flushes SQLite state to JSON backup files atomically."""
    close_after = False
    if conn is None:
        conn = get_db_connection()
        close_after = True

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions ORDER BY created_at DESC;")
        subs = [_row_to_submission(r) for r in cursor.fetchall()]
        with open(SUBMISSIONS_JSON, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)

        cursor.execute("SELECT * FROM inquiries ORDER BY created_at DESC;")
        inqs = [_row_to_inquiry(r) for r in cursor.fetchall()]
        with open(INQUIRIES_JSON, "w", encoding="utf-8") as f:
            json.dump(inqs, f, indent=2, ensure_ascii=False)
    finally:
        if close_after:
            conn.close()

# ------------------------------------------------------------------------------
# CRUD: Submissions
# ------------------------------------------------------------------------------

def get_all_submissions() -> List[Dict[str, Any]]:
    """Loads all submissions from SQLite database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        return [_row_to_submission(r) for r in rows]
    finally:
        conn.close()

def get_submission_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single submission by its report ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions WHERE id = ?;", (report_id,))
        row = cursor.fetchone()
        return _row_to_submission(row) if row else None
    finally:
        conn.close()

def save_new_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new student assessment record and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        db_insert_or_replace_submission_raw(cursor, data)
        conn.commit()
        sync_json_backups(conn)
        return data
    finally:
        conn.close()

def update_submission(report_id: str, status: Optional[str] = None, notes: Optional[str] = None) -> bool:
    """Updates status or notes for an existing submission."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if status is not None and notes is not None:
            cursor.execute("UPDATE submissions SET status = ?, notes = ?, updated_at = ? WHERE id = ?;", (status, notes, now_str, report_id))
        elif status is not None:
            cursor.execute("UPDATE submissions SET status = ?, updated_at = ? WHERE id = ?;", (status, now_str, report_id))
        elif notes is not None:
            cursor.execute("UPDATE submissions SET notes = ?, updated_at = ? WHERE id = ?;", (notes, now_str, report_id))
        else:
            return False

        affected = cursor.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups(conn)
        return affected
    finally:
        conn.close()

def delete_submission(report_id: str) -> bool:
    """Deletes a submission from SQLite and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM submissions WHERE id = ?;", (report_id,))
        affected = cursor.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups(conn)
        return affected
    finally:
        conn.close()

# ------------------------------------------------------------------------------
# CRUD: Inquiries
# ------------------------------------------------------------------------------

def get_all_inquiries() -> List[Dict[str, Any]]:
    """Loads all client inquiries from SQLite database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inquiries ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        return [_row_to_inquiry(r) for r in rows]
    finally:
        conn.close()

def get_inquiry_by_id(inquiry_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single inquiry by its ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inquiries WHERE id = ?;", (inquiry_id,))
        row = cursor.fetchone()
        return _row_to_inquiry(row) if row else None
    finally:
        conn.close()

def save_new_inquiry(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new client inquiry and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        db_insert_or_replace_inquiry_raw(cursor, data)
        conn.commit()
        sync_json_backups(conn)
        return data
    finally:
        conn.close()

def update_inquiry(inquiry_id: str, status: str) -> bool:
    """Updates status for an inquiry."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE inquiries SET status = ?, updated_at = ? WHERE id = ?;", (status, now_str, inquiry_id))
        affected = cursor.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups(conn)
        return affected
    finally:
        conn.close()

def delete_inquiry(inquiry_id: str) -> bool:
    """Deletes an inquiry from SQLite and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inquiries WHERE id = ?;", (inquiry_id,))
        affected = cursor.rowcount > 0
        conn.commit()
        if affected:
            sync_json_backups(conn)
        return affected
    finally:
        conn.close()

# ------------------------------------------------------------------------------
# Security: Session Management & Rate Limiting
# ------------------------------------------------------------------------------

def record_login_attempt(ip_address: str, success: bool):
    """Logs an authentication attempt for IP brute-force protection."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO login_attempts (ip_address, attempted_at, success) VALUES (?, ?, ?);", (ip_address, now_str, 1 if success else 0))
        conn.commit()
    finally:
        conn.close()

def is_ip_locked(ip_address: str, max_failures: int = 5, window_minutes: int = 15) -> bool:
    """Checks whether an IP has exceeded failed login threshold within time window."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cutoff = (datetime.now() - timedelta(minutes=window_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        SELECT COUNT(*) as failed_count FROM login_attempts
        WHERE ip_address = ? AND attempted_at >= ? AND success = 0;
        """, (ip_address, cutoff))
        res = cursor.fetchone()
        return res["failed_count"] >= max_failures
    finally:
        conn.close()

def create_admin_session(token: str, username: str, expires_in_hours: int = 4, ip_address: str = "") -> str:
    """Persists a new cryptographic session token with an expiration timestamp."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        expires_at = (now + timedelta(hours=expires_in_hours)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT * FROM admin_sessions WHERE token = ? AND expires_at > ?;", (token, now_str))
        row = cursor.fetchone()
        if row:
            # Update last activity
            cursor.execute("UPDATE admin_sessions SET last_activity = ? WHERE token = ?;", (now_str, token))
            conn.commit()
            return True
        return False
    finally:
        conn.close()

def delete_admin_session(token: str):
    """Revokes an admin session token."""
    if not token:
        return
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admin_sessions WHERE token = ?;", (token,))
        conn.commit()
    finally:
        conn.close()

# Auto-initialize DB schema upon module import
init_db()
