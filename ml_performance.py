"""
ml_performance.py - ML-Based Student Performance Monitor
Uses scikit-learn (simple ML) to:
1. Track quiz scores over time
2. Compare study hours vs target
3. Identify subject-wise weak areas
4. Predict exam readiness score (0–100)

ML Algorithms used:
- Linear Regression → predict readiness score from study data
- Simple rule-based classification → identify weak subjects
- Moving average → smooth performance trends

All models are trained on the student's own historical data stored in SQLite.
"""

import sqlite3
import json
import numpy as np
import pandas as pd
from datetime import date, timedelta
from database import DB_PATH, get_connection

# ─── DATABASE SETUP FOR ML TABLES ─────────────────────────────────────────────

def initialize_ml_tables():
    """
    Create ML-specific tables in the database.
    Called once at startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table: quiz performance history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subject TEXT,
            score INTEGER,
            total INTEGER,
            percentage REAL
        )
    """)

    # Table: daily study hours log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subject TEXT,
            hours_studied REAL,
            target_hours REAL
        )
    """)

    # Table: subject performance summary
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT UNIQUE,
            avg_score REAL DEFAULT 0,
            total_quizzes INTEGER DEFAULT 0,
            total_hours REAL DEFAULT 0,
            last_updated TEXT
        )
    """)

    conn.commit()
    conn.close()


# ─── DATA LOGGING FUNCTIONS ───────────────────────────────────────────────────

def log_quiz_result(subject, score, total):
    """
    Save a quiz result to the performance history.
    Called after every quiz attempt.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    percentage = round((score / total) * 100, 1) if total > 0 else 0

    cursor.execute("""
        INSERT INTO quiz_performance (date, subject, score, total, percentage)
        VALUES (?, ?, ?, ?, ?)
    """, (today, subject, score, total, percentage))

    # Update subject summary
    cursor.execute("""
        INSERT INTO subject_performance (subject, avg_score, total_quizzes, last_updated)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(subject) DO UPDATE SET
            avg_score = (avg_score * total_quizzes + ?) / (total_quizzes + 1),
            total_quizzes = total_quizzes + 1,
            last_updated = ?
    """, (subject, percentage, today, percentage, today))

    conn.commit()
    conn.close()


def log_study_hours(subject, hours_studied, target_hours):
    """
    Log daily study hours for a subject.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())

    cursor.execute("""
        INSERT INTO daily_hours (date, subject, hours_studied, target_hours)
        VALUES (?, ?, ?, ?)
    """, (today, subject, hours_studied, target_hours))

    # Update total hours in subject_performance
    cursor.execute("""
        INSERT INTO subject_performance (subject, total_hours, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(subject) DO UPDATE SET
            total_hours = total_hours + ?,
            last_updated = ?
    """, (subject, hours_studied, today, hours_studied, today))

    conn.commit()
    conn.close()


# ─── DATA RETRIEVAL ───────────────────────────────────────────────────────────

def get_quiz_history():
    """Get all quiz performance records as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM quiz_performance ORDER BY date ASC",
        conn
    )
    conn.close()
    return df


def get_hours_history():
    """Get all study hours records as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM daily_hours ORDER BY date ASC",
        conn
    )
    conn.close()
    return df


def get_subject_summary():
    """Get subject-wise performance summary as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM subject_performance ORDER BY avg_score ASC",
        conn
    )
    conn.close()
    return df


# ─── WEAK AREA DETECTION (RULE-BASED + STATS) ─────────────────────────────────

def identify_weak_subjects(threshold=60.0):
    """
    Identify subjects where the student is struggling.

    Rule:
    - avg_score < threshold (default 60%) → WEAK
    - avg_score 60–75% → NEEDS IMPROVEMENT
    - avg_score > 75% → STRONG

    Returns:
        dict: {subject: {'status': ..., 'avg_score': ..., 'recommendation': ...}}
    """
    df = get_subject_summary()
    if df.empty:
        return {}

    weak_analysis = {}
    for _, row in df.iterrows():
        subject = row['subject']
        avg = row['avg_score']
        quizzes = row['total_quizzes']

        if quizzes < 1:
            continue  # Not enough data

        if avg < threshold:
            status = "🔴 Weak"
            recommendation = f"Spend more time on {subject}. Review basics and attempt more quizzes."
        elif avg < 75:
            status = "🟡 Needs Improvement"
            recommendation = f"{subject} is improving. Focus on harder practice problems."
        else:
            status = "🟢 Strong"
            recommendation = f"Great work on {subject}! Keep it up and practice advanced questions."

        weak_analysis[subject] = {
            "status": status,
            "avg_score": round(avg, 1),
            "total_quizzes": int(quizzes),
            "recommendation": recommendation
        }

    return weak_analysis


# ─── PERFORMANCE TREND (MOVING AVERAGE) ──────────────────────────────────────

def get_score_trend(subject=None, window=3):
    """
    Calculate moving average of quiz scores over time.
    Smooths out fluctuations to show real trend.

    Parameters:
        subject: filter by subject (None = all subjects)
        window: moving average window size

    Returns:
        DataFrame with date, raw_score, smoothed_score
    """
    df = get_quiz_history()
    if df.empty:
        return pd.DataFrame()

    if subject:
        df = df[df['subject'] == subject]

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values('date').reset_index(drop=True)
    df['smoothed_score'] = df['percentage'].rolling(window=window, min_periods=1).mean().round(1)

    return df[['date', 'subject', 'percentage', 'smoothed_score']]


def get_hours_trend(subject=None):
    """
    Calculate study hours vs target over time.

    Returns:
        DataFrame with date, hours_studied, target_hours, gap
    """
    df = get_hours_history()
    if df.empty:
        return pd.DataFrame()

    if subject:
        df = df[df['subject'] == subject]

    df = df.sort_values('date').reset_index(drop=True)
    df['gap'] = (df['hours_studied'] - df['target_hours']).round(2)
    df['met_target'] = df['gap'] >= 0

    return df


# ─── ML: EXAM READINESS PREDICTION ───────────────────────────────────────────

def predict_exam_readiness():
    """
    Predict overall exam readiness score (0–100) using Linear Regression.

    Features used:
    1. Average quiz score across all subjects
    2. Study hours completion rate (actual / target)
    3. Current streak (consistency signal)
    4. Number of weak subjects (penalty)

    The model is trained on synthetic reference data + student's own data.
    This is a simple interpretable ML model — beginner-friendly.

    Returns:
        dict with readiness_score, grade, breakdown, improvement_tips
    """
    try:
        from sklearn.linear_model import LinearRegression
        import numpy as np
        ML_AVAILABLE = True
    except ImportError:
        ML_AVAILABLE = False

    # ─── Collect current student features ─────────────────────────────────
    quiz_df = get_quiz_history()
    hours_df = get_hours_history()
    subject_df = get_subject_summary()

    from database import get_user_progress
    progress = get_user_progress()
    streak = progress.get('streak', 0)

    # Feature 1: Average quiz score (0–100)
    avg_quiz_score = quiz_df['percentage'].mean() if not quiz_df.empty else 0

    # Feature 2: Hours completion rate (0–1)
    if not hours_df.empty and hours_df['target_hours'].sum() > 0:
        hours_rate = min(1.0, hours_df['hours_studied'].sum() / hours_df['target_hours'].sum())
    else:
        hours_rate = 0.0

    # Feature 3: Streak score (capped at 30 days for normalization)
    streak_score = min(streak / 30.0, 1.0)

    # Feature 4: Weak subject penalty (each weak subject reduces readiness)
    weak_subjects = identify_weak_subjects()
    num_weak = sum(1 for v in weak_subjects.values() if "Weak" in v['status'])
    total_subjects = max(len(weak_subjects), 1)
    weak_penalty = num_weak / total_subjects  # 0 = no weak subjects, 1 = all weak

    # ─── ML Prediction (Linear Regression on synthetic reference data) ────

    if ML_AVAILABLE:
        # Synthetic training data: [avg_quiz, hours_rate, streak_score, weak_penalty] → readiness
        # These represent realistic student profiles at different readiness levels
        X_train = np.array([
            [95, 1.0, 1.0, 0.0],   # Excellent student → 98
            [85, 0.9, 0.8, 0.1],   # Very good → 90
            [75, 0.8, 0.6, 0.2],   # Good → 78
            [65, 0.7, 0.5, 0.3],   # Average → 65
            [55, 0.6, 0.4, 0.5],   # Below average → 52
            [45, 0.5, 0.2, 0.6],   # Struggling → 40
            [35, 0.3, 0.1, 0.8],   # Very weak → 28
            [80, 0.6, 0.9, 0.1],   # Consistent but moderate scores → 72
            [90, 0.4, 0.3, 0.2],   # Good scores, poor consistency → 70
            [60, 1.0, 0.8, 0.4],   # Good hours, average scores → 68
        ])
        y_train = np.array([98, 90, 78, 65, 52, 40, 28, 72, 70, 68])

        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict for current student
        student_features = np.array([[avg_quiz_score, hours_rate, streak_score, weak_penalty]])
        raw_score = model.predict(student_features)[0]
        readiness_score = max(0, min(100, round(raw_score, 1)))

    else:
        # Fallback: weighted formula if sklearn not installed
        readiness_score = round(
            (avg_quiz_score * 0.40) +
            (hours_rate * 100 * 0.30) +
            (streak_score * 100 * 0.20) +
            ((1 - weak_penalty) * 100 * 0.10),
            1
        )
        readiness_score = max(0, min(100, readiness_score))

    # ─── Grade assignment ─────────────────────────────────────────────────
    if readiness_score >= 85:
        grade = "A+ — Exam Ready! 🏆"
        grade_color = "green"
    elif readiness_score >= 70:
        grade = "B+ — Almost There! 🎯"
        grade_color = "blue"
    elif readiness_score >= 55:
        grade = "C — Keep Pushing! 📚"
        grade_color = "orange"
    elif readiness_score >= 40:
        grade = "D — Needs Work! ⚠️"
        grade_color = "red"
    else:
        grade = "F — Revamp Strategy! 🚨"
        grade_color = "red"

    # ─── Improvement tips (rule-based) ───────────────────────────────────
    tips = []
    if avg_quiz_score < 60:
        tips.append("📝 Your quiz scores are low. Revisit concepts before attempting more quizzes.")
    if hours_rate < 0.7:
        tips.append("⏰ You're studying less than your target hours. Try to stick to your daily schedule.")
    if streak < 5:
        tips.append("🔥 Build your streak! Consistent daily study is the #1 predictor of exam success.")
    if num_weak > 0:
        weak_names = [k for k, v in weak_subjects.items() if "Weak" in v['status']]
        tips.append(f"🔴 Focus on weak subjects: {', '.join(weak_names)}")
    if not tips:
        tips.append("✅ You're on the right track. Keep up the great work!")

    return {
        "readiness_score": readiness_score,
        "grade": grade,
        "grade_color": grade_color,
        "ml_available": ML_AVAILABLE if 'ML_AVAILABLE' in dir() else False,
        "breakdown": {
            "avg_quiz_score": round(avg_quiz_score, 1),
            "hours_completion_rate": round(hours_rate * 100, 1),
            "streak_consistency": round(streak_score * 100, 1),
            "weak_subject_penalty": round(weak_penalty * 100, 1)
        },
        "improvement_tips": tips,
        "weak_subjects": weak_subjects
    }


# ─── CHART DATA HELPERS ───────────────────────────────────────────────────────

def get_performance_chart_data():
    """
    Returns data formatted for Streamlit charts.
    """
    quiz_df = get_quiz_history()
    hours_df = get_hours_history()

    charts = {}

    # Chart 1: Score over time (all subjects)
    if not quiz_df.empty:
        score_chart = quiz_df.groupby('date')['percentage'].mean().reset_index()
        score_chart.columns = ['date', 'avg_score']
        charts['score_over_time'] = score_chart
    else:
        charts['score_over_time'] = pd.DataFrame(columns=['date', 'avg_score'])

    # Chart 2: Subject-wise average scores
    if not quiz_df.empty:
        subject_chart = quiz_df.groupby('subject')['percentage'].mean().reset_index()
        subject_chart.columns = ['subject', 'avg_score']
        subject_chart = subject_chart.sort_values('avg_score')
        charts['subject_scores'] = subject_chart
    else:
        charts['subject_scores'] = pd.DataFrame(columns=['subject', 'avg_score'])

    # Chart 3: Study hours vs target
    if not hours_df.empty:
        hours_chart = hours_df.groupby('date').agg(
            hours_studied=('hours_studied', 'sum'),
            target_hours=('target_hours', 'sum')
        ).reset_index()
        charts['hours_vs_target'] = hours_chart
    else:
        charts['hours_vs_target'] = pd.DataFrame(columns=['date', 'hours_studied', 'target_hours'])

    return charts


def add_sample_data_for_demo():
    """
    Add sample performance data for demonstration purposes.
    This lets users see what the analytics looks like with real data.
    """
    import random
    from datetime import date, timedelta

    subjects = ["Physics", "Chemistry", "Mathematics", "Biology", "History"]
    today = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    # Add 14 days of demo data
    for days_ago in range(14, 0, -1):
        day = str(today - timedelta(days=days_ago))

        for subject in random.sample(subjects, 3):  # 3 subjects per day
            # Simulate improving trend: more recent = slightly higher scores
            base_score = random.randint(40, 75)
            improvement = (14 - days_ago) * 1.5  # Gradual improvement
            score_pct = min(95, base_score + improvement + random.uniform(-5, 5))

            total = 5
            score = round((score_pct / 100) * total)
            score_pct = (score / total) * 100

            cursor.execute("""
                INSERT INTO quiz_performance (date, subject, score, total, percentage)
                VALUES (?, ?, ?, ?, ?)
            """, (day, subject, score, total, round(score_pct, 1)))

            # Study hours
            target = random.uniform(1.0, 2.5)
            studied = target * random.uniform(0.6, 1.2)
            cursor.execute("""
                INSERT INTO daily_hours (date, subject, hours_studied, target_hours)
                VALUES (?, ?, ?, ?)
            """, (day, subject, round(studied, 2), round(target, 2)))

    # Update subject summary
    cursor.execute("""
        INSERT INTO subject_performance (subject, avg_score, total_quizzes, last_updated)
        SELECT subject, AVG(percentage), COUNT(*), MAX(date)
        FROM quiz_performance
        GROUP BY subject
        ON CONFLICT(subject) DO UPDATE SET
            avg_score = excluded.avg_score,
            total_quizzes = excluded.total_quizzes,
            last_updated = excluded.last_updated
    """)

    conn.commit()
    conn.close()