"""
utils.py - Helper / Utility Functions
=======================================
This file contains small helper functions used across the project.
Think of it as a toolbox for common tasks.
"""

from datetime import date, datetime


# ─────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────

def get_today_str():
    """Return today's date as a formatted string."""
    return date.today().strftime("%B %d, %Y")  # e.g., "January 15, 2025"


def get_greeting():
    """
    Return a time-based greeting.
    Rule-based using current hour.
    """
    hour = datetime.now().hour

    if hour < 12:
        return "Good Morning! ☀️"
    elif hour < 17:
        return "Good Afternoon! 🌤️"
    elif hour < 21:
        return "Good Evening! 🌆"
    else:
        return "Good Night! 🌙 (Late night studying — respect!)"


# ─────────────────────────────────────────────
# FORMATTING HELPERS
# ─────────────────────────────────────────────

def format_hours(hours):
    """
    Convert decimal hours to a readable format.
    e.g., 1.5 → "1h 30min"
    
    Args:
        hours (float): Hours in decimal
    
    Returns:
        str: Readable time string
    """
    h = int(hours)
    m = int((hours - h) * 60)

    if h == 0:
        return f"{m} min"
    elif m == 0:
        return f"{h}h"
    else:
        return f"{h}h {m}min"


def get_difficulty_emoji(difficulty):
    """Return an emoji for difficulty level."""
    mapping = {
        "Easy": "🟢 Easy",
        "Medium": "🟡 Medium",
        "Hard": "🔴 Hard"
    }
    return mapping.get(difficulty, difficulty)


def get_status_emoji(status):
    """Return emoji for task status."""
    mapping = {
        "pending": "⏳ Pending",
        "completed": "✅ Completed",
        "missed": "❌ Missed"
    }
    return mapping.get(status, status)


# ─────────────────────────────────────────────
# MOTIVATIONAL MESSAGES
# ─────────────────────────────────────────────

def get_motivational_quote():
    """
    Return a random motivational quote for students.
    Uses a static list (no randomness dependency needed).
    """
    import random
    quotes = [
        "📖 'The secret of getting ahead is getting started.' — Mark Twain",
        "💡 'An investment in knowledge pays the best interest.' — Benjamin Franklin",
        "🎯 'Success is the sum of small efforts repeated day in and day out.' — Robert Collier",
        "🔥 'Don't watch the clock; do what it does. Keep going.' — Sam Levenson",
        "🌟 'Believe you can and you're halfway there.' — Theodore Roosevelt",
        "🚀 'The future belongs to those who learn more skills and combine them.' — Robert Greene",
        "📚 'Education is the most powerful weapon to change the world.' — Nelson Mandela",
        "💪 'Push yourself, because no one else is going to do it for you.'",
        "🎓 'Study hard, for the well is deep and our brains are shallow.'",
        "⚡ 'Little by little, a little becomes a lot.'"
    ]
    return random.choice(quotes)


def get_break_suggestion():
    """
    Return a fun break activity suggestion during Pomodoro break.
    Rule-based — returns from a list.
    """
    import random
    suggestions = [
        "🚶 Take a short walk around the room",
        "💧 Drink a glass of water — stay hydrated!",
        "🧘 Do 5 deep breaths to refresh your mind",
        "👀 Look away from the screen — 20-20-20 rule!",
        "🤸 Do 10 jumping jacks to wake up your body",
        "☕ Make yourself a cup of tea or coffee",
        "🎵 Listen to one song to reset your mood",
        "🪟 Look outside and give your eyes a break"
    ]
    return random.choice(suggestions)


# ─────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────

def validate_subject_input(subjects_data):
    """
    Validate the subject input list before scheduling.
    
    Args:
        subjects_data (list): List of subject dicts
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not subjects_data:
        return False, "Please add at least one subject."

    for item in subjects_data:
        if not item.get("subject", "").strip():
            return False, "Subject name cannot be empty."
        if item.get("days_left", 0) <= 0:
            return False, f"Days left for '{item['subject']}' must be at least 1."
        if item.get("difficulty") not in ["Easy", "Medium", "Hard"]:
            return False, f"Invalid difficulty for '{item['subject']}'."

    return True, ""


def summarize_schedule(schedule):
    """
    Create a quick text summary of the generated schedule.
    
    Args:
        schedule (list): List of scheduled items
    
    Returns:
        str: Summary text
    """
    if not schedule:
        return "No schedule generated yet."

    total_hours = sum(item["hours_allocated"] for item in schedule)
    subject_count = len(schedule)
    top_priority = schedule[0]["subject"] if schedule else "N/A"

    summary = (
        f"📊 **Schedule Summary**\n"
        f"- Total subjects: {subject_count}\n"
        f"- Total daily hours: {format_hours(total_hours)}\n"
        f"- Highest priority subject: {top_priority}"
    )
    return summary
# ─────────────────────────────────────────────
# POMODORO PLAN GENERATOR (for main.py)
# ─────────────────────────────────────────────

def generate_pomodoro_plan(hours):
    """
    Generate Pomodoro study plan based on hours.

    1 session = 25 min study + 5 min break
    Every 4 sessions → long break (15 min)
    """
    plan = []
    total_minutes = int(hours * 60)

    num_sessions = max(1, total_minutes // 25)

    for i in range(num_sessions):
        # Study session
        plan.append({
            "type": "study",
            "label": f"📖 Study Session {i+1} (25 min)"
        })

        # Break session
        if (i + 1) % 4 == 0:
            plan.append({
                "type": "break",
                "label": "☕ Long Break (15 min)"
            })
        else:
            plan.append({
                "type": "break",
                "label": "🧘 Short Break (5 min)"
            })

    return plan
# ─────────────────────────────────────────────
# COMPATIBILITY FIX (for main.py)
# ─────────────────────────────────────────────

def validate_subject_inputs(subjects_data):
    return validate_subject_input(subjects_data)
def progress_bar_value(streak):
    """
    Return progress value between 0 and 1 for Streamlit progress bar.
    Milestone cycle = every 10 days.
    """
    return (streak % 10) / 10