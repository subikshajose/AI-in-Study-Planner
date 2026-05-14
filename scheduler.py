"""
scheduler.py - Rule-Based AI Scheduling Logic
==============================================
This file contains the brain of the study planner.
It takes subject inputs and generates a smart, prioritized study schedule
using simple rule-based logic (no machine learning needed!).
"""

import pandas as pd  # Used for organizing schedule data in a table format

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# Map difficulty words to numeric values
DIFFICULTY_MAP = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}


# ─────────────────────────────────────────────
# CORE SCHEDULING FUNCTION
# ─────────────────────────────────────────────

def calculate_priority(difficulty_str, days_left):
    """
    Calculate priority score for a subject using rule-based formula.
    
    Formula: priority = (difficulty * 2) + (1 / days_left)
    
    - Higher difficulty → higher priority
    - Fewer days left → higher priority (urgency)
    
    Args:
        difficulty_str (str): "Easy", "Medium", or "Hard"
        days_left (int): Number of days until deadline
    
    Returns:
        float: Priority score (higher = more urgent)
    """
    # Convert difficulty to number
    difficulty_num = DIFFICULTY_MAP.get(difficulty_str, 1)

    # Avoid division by zero
    if days_left <= 0:
        days_left = 0.1  # Treat as extremely urgent

    # Rule-based priority formula
    priority = (difficulty_num * 2) + (1 / days_left)

    return round(priority, 4)


def generate_schedule(subjects_data, total_hours_per_day):
    """
    Generate a smart study schedule from a list of subjects.
    
    Steps:
    1. Calculate priority score for each subject
    2. Sort by priority (highest first)
    3. Allocate study hours proportionally based on priority
    
    Args:
        subjects_data (list of dicts): Each dict has:
            - subject (str): Name of subject
            - difficulty (str): "Easy", "Medium", or "Hard"
            - days_left (int): Days until deadline
        total_hours_per_day (float): How many hours student can study per day
    
    Returns:
        list of dicts: Sorted schedule with allocated hours
    """

    if not subjects_data:
        return []

    # Step 1: Calculate priority for each subject
    for item in subjects_data:
        item["priority_score"] = calculate_priority(item["difficulty"], item["days_left"])

    # Step 2: Sort subjects by priority score (highest first)
    sorted_subjects = sorted(subjects_data, key=lambda x: x["priority_score"], reverse=True)

    # Step 3: Calculate total priority to find proportions
    total_priority = sum(item["priority_score"] for item in sorted_subjects)

    # Step 4: Allocate hours proportionally
    schedule = []
    for item in sorted_subjects:
        # Proportion of total hours this subject gets
        proportion = item["priority_score"] / total_priority
        hours = round(proportion * total_hours_per_day, 2)

        # Minimum 0.5 hours per subject
        hours = max(0.5, hours)

        schedule.append({
            "subject": item["subject"],
            "difficulty": item["difficulty"],
            "days_left": item["days_left"],
            "priority_score": item["priority_score"],
            "hours_allocated": hours
        })

    return schedule


def get_pomodoro_plan(hours_allocated):
    """
    Generate a Pomodoro plan for a given number of study hours.
    
    Pomodoro Technique:
    - 50 minutes of focused study
    - 10 minutes break
    - Each cycle = 1 hour total
    
    Args:
        hours_allocated (float): Hours to study for this subject
    
    Returns:
        dict: Pomodoro session breakdown
    """
    # Each Pomodoro cycle = 50 min study + 10 min break = 60 min = 1 hour
    num_cycles = max(1, round(hours_allocated))

    sessions = []
    for i in range(1, num_cycles + 1):
        sessions.append({
            "session": i,
            "study_time": "50 minutes",
            "break_time": "10 minutes"
        })

    return {
        "total_cycles": num_cycles,
        "total_study_minutes": num_cycles * 50,
        "total_break_minutes": num_cycles * 10,
        "sessions": sessions
    }


def get_difficulty_tips(difficulty):
    """
    Return study tips based on difficulty level.
    Rule-based advice using IF-ELSE logic.
    
    Args:
        difficulty (str): "Easy", "Medium", or "Hard"
    
    Returns:
        str: Study tip message
    """
    if difficulty == "Easy":
        return "✅ Quick review is enough. Focus on memorizing key facts and formulas."
    elif difficulty == "Medium":
        return "📝 Practice problems and summaries will help. Spend time on weak areas."
    elif difficulty == "Hard":
        return "🔥 Deep focus required! Break into small topics, use flashcards, and revise daily."
    else:
        return "📚 Study consistently and take good notes."


def get_urgency_message(days_left):
    """
    Return urgency message based on days left.
    Rule-based logic using IF-ELSE.
    
    Args:
        days_left (int): Days until deadline
    
    Returns:
        str: Urgency level message
    """
    if days_left <= 1:
        return "🚨 CRITICAL: Deadline is today or tomorrow! Start immediately!"
    elif days_left <= 3:
        return "⚠️ HIGH URGENCY: Very little time left. Prioritize this subject!"
    elif days_left <= 7:
        return "📅 MODERATE: You have a week. Stay consistent!"
    else:
        return "😊 LOW URGENCY: Good amount of time. Don't procrastinate!"


def schedule_to_dataframe(schedule):
    """
    Convert schedule list to a pandas DataFrame for display.
    
    Args:
        schedule (list): List of schedule dicts
    
    Returns:
        pd.DataFrame: Formatted schedule table
    """
    if not schedule:
        return pd.DataFrame()

    df = pd.DataFrame(schedule)

    # Rename columns to be more readable
    df = df.rename(columns={
        "subject": "📚 Subject",
        "difficulty": "⚡ Difficulty",
        "days_left": "📅 Days Left",
        "priority_score": "🎯 Priority Score",
        "hours_allocated": "⏰ Hours/Day"
    })

    return df
def get_pomodoro_sessions(hours):
    """
    Convert study hours into Pomodoro sessions.
    1 Pomodoro = 25 minutes study + 5 minutes break
    """
    total_minutes = int(hours * 60)
    num_sessions = max(1, total_minutes // 25)

    study_minutes = num_sessions * 25
    break_minutes = max(0, (num_sessions - 1) * 5)

    return {
        "num_sessions": num_sessions,
        "study_minutes": study_minutes,
        "break_minutes": break_minutes,
        "total_minutes": study_minutes + break_minutes
    }