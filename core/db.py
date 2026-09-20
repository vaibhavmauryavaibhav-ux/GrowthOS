"""
Database Manager for Cognitive Growth OS
Handles SQLite storage for Targets, Mistake Ledger, FSRS Recall Cards, Sessions, and Telemetry.
"""

import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(os.getenv("GROWTH_OS_DB_PATH", Path.home() / ".growth_os" / "growth_os.db"))

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables with full relational schemas."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Generic Targets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        target_type TEXT NOT NULL, -- 'percent', 'count', 'time_minutes'
        target_val REAL NOT NULL,
        current_val REAL DEFAULT 0.0,
        unit TEXT DEFAULT '',
        date_created TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
    """)

    # 2. Spaced Repetition Cards (FSRS compatible)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recall_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        prompt_text TEXT,
        image_path TEXT,
        answer_text TEXT,
        card_type TEXT DEFAULT 'card', -- 'card', 'mistake', 'formula', 'diagram'
        difficulty REAL DEFAULT 5.0,   -- FSRS Difficulty (1-10)
        stability REAL DEFAULT 0.5,    -- FSRS Memory Stability (in days)
        reps INTEGER DEFAULT 0,
        lapses INTEGER DEFAULT 0,
        state TEXT DEFAULT 'new',      -- 'new', 'learning', 'review'
        last_review TEXT,
        next_review TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # 3. Mistake Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        error_type TEXT NOT NULL, -- 'concept_gap', 'calculation_slip', 'misread', 'panic', 'other'
        notes TEXT,
        screenshot_path TEXT,
        recall_card_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (recall_card_id) REFERENCES recall_cards (id)
    )
    """)

    # 4. Study Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mode TEXT NOT NULL, -- 'auto', 'manual', 'war_mode'
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration_seconds REAL DEFAULT 0.0,
        questions_solved INTEGER DEFAULT 0,
        matched_pattern TEXT,
        notes TEXT
    )
    """)

    # 5. Timed Question Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question_number INTEGER NOT NULL,
        time_spent_seconds REAL NOT NULL,
        is_correct INTEGER DEFAULT 1,
        notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    """)

    # 6. Telemetry Table (Activity Tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        window_title TEXT,
        app_name TEXT,
        matched_pattern TEXT,
        is_productive INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()

# ----------------- Target Operations -----------------

def add_target(title: str, target_type: str, target_val: float, unit: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO targets (title, target_type, target_val, current_val, unit, date_created, completed)
        VALUES (?, ?, ?, 0.0, ?, ?, 0)
    """, (title, target_type, target_val, unit, now))
    target_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return target_id

def update_target_progress(target_id: int, increment: float) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets WHERE id = ?", (target_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    new_val = row["current_val"] + increment
    completed = 1 if new_val >= row["target_val"] else 0
    cursor.execute("""
        UPDATE targets SET current_val = ?, completed = ? WHERE id = ?
    """, (new_val, completed, target_id))
    conn.commit()
    
    cursor.execute("SELECT * FROM targets WHERE id = ?", (target_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    return updated

def get_active_targets() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets WHERE completed = 0 ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# ----------------- Recall Cards & Spaced Repetition -----------------

def add_recall_card(title: str, prompt_text: str = "", image_path: str = "", 
                    answer_text: str = "", card_type: str = "card", 
                    initial_next_review_iso: Optional[str] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    next_review = initial_next_review_iso or now_iso
    
    cursor.execute("""
        INSERT INTO recall_cards 
        (title, prompt_text, image_path, answer_text, card_type, difficulty, stability, reps, lapses, state, next_review, created_at)
        VALUES (?, ?, ?, ?, ?, 5.0, 0.5, 0, 0, 'new', ?, ?)
    """, (title, prompt_text, image_path, answer_text, card_type, next_review, now_iso))
    card_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return card_id

def get_due_recall_cards() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        SELECT * FROM recall_cards 
        WHERE next_review <= ? 
        ORDER BY next_review ASC
    """, (now_iso,))
    cards = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return cards

def get_all_recall_cards() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recall_cards ORDER BY id DESC")
    cards = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return cards

def update_card_fsrs(card_id: int, difficulty: float, stability: float, 
                     reps: int, lapses: int, state: str, next_review_iso: str):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE recall_cards 
        SET difficulty = ?, stability = ?, reps = ?, lapses = ?, state = ?, 
            last_review = ?, next_review = ?
        WHERE id = ?
    """, (difficulty, stability, reps, lapses, state, now_iso, next_review_iso, card_id))
    conn.commit()
    conn.close()

# ----------------- Mistake Ledger -----------------

def log_mistake(subject: str, topic: str, error_type: str, notes: str = "", 
                screenshot_path: str = "") -> int:
    """Logs mistake and automatically creates a recall card for future spaced testing."""
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Create recall card first
    card_title = f"[Mistake Drill] {subject}: {topic}"
    prompt_text = f"Mistake in {subject} ({topic}):\nReason: {error_type}\nNotes: {notes}"
    cursor.execute("""
        INSERT INTO recall_cards 
        (title, prompt_text, image_path, answer_text, card_type, difficulty, stability, reps, lapses, state, next_review, created_at)
        VALUES (?, ?, ?, ?, 'mistake', 6.0, 0.3, 0, 0, 'new', ?, ?)
    """, (card_title, prompt_text, screenshot_path, notes, now_iso, now_iso))
    card_id = cursor.lastrowid

    # 2. Insert mistake
    cursor.execute("""
        INSERT INTO mistakes (subject, topic, error_type, notes, screenshot_path, recall_card_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (subject, topic, error_type, notes, screenshot_path, card_id, now_iso))
    mistake_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return mistake_id

def get_mistakes(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mistakes ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# ----------------- Sessions & Telemetry -----------------

def start_session(mode: str, matched_pattern: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO sessions (mode, start_time, duration_seconds, questions_solved, matched_pattern)
        VALUES (?, ?, 0.0, 0, ?)
    """, (mode, now_iso, matched_pattern))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def end_session(session_id: int, duration_seconds: float, questions_solved: int, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE sessions 
        SET end_time = ?, duration_seconds = ?, questions_solved = ?, notes = ?
        WHERE id = ?
    """, (now_iso, duration_seconds, questions_solved, notes, session_id))
    conn.commit()
    conn.close()

def log_question_solved(session_id: Optional[int], question_number: int, time_spent_seconds: float, 
                        is_correct: bool = True, notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO question_logs (session_id, question_number, time_spent_seconds, is_correct, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, question_number, time_spent_seconds, 1 if is_correct else 0, notes, now_iso))
    log_id = cursor.lastrowid

    if session_id:
        cursor.execute("""
            UPDATE sessions 
            SET questions_solved = questions_solved + 1 
            WHERE id = ?
        """, (session_id,))

    conn.commit()
    conn.close()
    return log_id

def log_telemetry(window_title: str, app_name: str, matched_pattern: str, is_productive: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO telemetry (timestamp, window_title, app_name, matched_pattern, is_productive)
        VALUES (?, ?, ?, ?, ?)
    """, (now_iso, window_title, app_name, matched_pattern, 1 if is_productive else 0))
    conn.commit()
    conn.close()

# Auto-initialize on module load
init_db()
