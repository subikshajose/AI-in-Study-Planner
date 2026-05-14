"""
database.py - Handles all data storage using SQLite
Stores: streak count, points, last study date, schedule, completed tasks
"""

import sqlite3  # Built-in Python library, no installation needed
import json
from datetime import date

# Name of our database file
DB_NAME = "study_planner.db"
DB_PATH = DB_NAME


def get_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def initialize_db():
    """
    Create all required tables if they don't already exist.
    This runs every time the app starts — it's safe to call multiple times.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: User progress (streak, points, dates)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            streak INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            last_study_date TEXT DEFAULT '',
            cheat_day_used INTEGER DEFAULT 0
        )
    """)

    # Table 2: Study schedule (list of subjects with details)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            difficulty TEXT,
            days_left INTEGER,
            hours_allocated REAL,
            priority_score REAL,
            status TEXT DEFAULT 'pending'
        )
    """)

    # Table 3: Session history (log of completed/missed sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subject TEXT,
            status TEXT
        )
    """)

    # Insert default user progress row if none exists
    cursor.execute("SELECT COUNT(*) FROM user_progress")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO user_progress (streak, points, last_study_date) VALUES (0, 0, '')")

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# USER PROGRESS FUNCTIONS
# ─────────────────────────────────────────────

def get_user_progress():
    """Fetch the current user's streak, points, and last study date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT streak, points, last_study_date, cheat_day_used FROM user_progress WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "streak": row[0],
            "points": row[1],
            "last_study_date": row[2],
            "cheat_day_used": row[3]
        }
    return {"streak": 0, "points": 0, "last_study_date": "", "cheat_day_used": 0}


def update_user_progress(streak, points, last_study_date, cheat_day_used=0):
    """Update the user's streak, points, and last study date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_progress
        SET streak = ?, points = ?, last_study_date = ?, cheat_day_used = ?
        WHERE id = 1
    """, (streak, points, last_study_date, cheat_day_used))
    conn.commit()
    conn.close()


def reset_progress():
    """Reset all user progress (streak, points, schedule)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_progress SET streak=0, points=0, last_study_date='', cheat_day_used=0 WHERE id=1")
    cursor.execute("DELETE FROM schedule")
    cursor.execute("DELETE FROM session_history")
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# SCHEDULE FUNCTIONS
# ─────────────────────────────────────────────

def save_schedule(schedule_list):
    """
    Save a new schedule to the database.
    schedule_list: list of dicts with keys: subject, difficulty, days_left, hours_allocated, priority_score
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing schedule before saving new one
    cursor.execute("DELETE FROM schedule")

    for item in schedule_list:
        cursor.execute("""
            INSERT INTO schedule (subject, difficulty, days_left, hours_allocated, priority_score, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            item["subject"],
            item["difficulty"],
            item["days_left"],
            item["hours_allocated"],
            item["priority_score"]
        ))

    conn.commit()
    conn.close()


def get_schedule():
    """Retrieve all schedule items from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, subject, difficulty, days_left, hours_allocated, priority_score, status
        FROM schedule
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_task_status(task_id, status):
    """Update the status of a specific task (pending / completed / missed)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE schedule SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


def reschedule_missed_tasks():
    """
    Adaptive rescheduling: If a task is missed, increase its priority
    by reducing its effective days_left (makes it more urgent).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get all missed tasks
    cursor.execute("SELECT id, days_left, priority_score FROM schedule WHERE status = 'missed'")
    missed = cursor.fetchall()

    for task in missed:
        task_id = task[0]
        days_left = max(1, task[1] - 1)  # Reduce days left (increase urgency), minimum 1
        new_priority = task[2] * 1.2  # Boost priority by 20%
        cursor.execute("""
            UPDATE schedule SET days_left = ?, priority_score = ?, status = 'pending'
            WHERE id = ?
        """, (days_left, new_priority, task_id))

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# SESSION HISTORY FUNCTIONS
# ─────────────────────────────────────────────

def log_session(subject, status):
    """Log a study session as completed or missed."""
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute("INSERT INTO session_history (date, subject, status) VALUES (?, ?, ?)",
                   (today, subject, status))
    conn.commit()
    conn.close()


def get_session_history():
    """Get all past session history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, subject, status FROM session_history ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"date": r[0], "subject": r[1], "status": r[2]} for r in rows]
# ─────────────────────────────────────────────
# COMPATIBILITY FUNCTIONS (for main.py)
# ─────────────────────────────────────────────

def log_study_session(subject, hours, status):
    """Wrapper for logging study sessions with hours."""
    log_session(subject, status)


def get_study_log():
    """Return study log in format expected by main.py."""
    history = get_session_history()
    return [
        (item["date"], item["subject"], 0, item["status"])  # hours = 0 (placeholder)
        for item in history
    ]


def reset_all_data():
    """Reset all app data."""
    reset_progress()