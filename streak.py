"""
streak.py - Streak Tracking & Reward System
============================================
This file manages:
- Daily study streak counter
- Points reward system
- Cheat day feature (skip one day without losing streak)

Rules:
- Complete study → streak increases
- Miss study → streak resets (unless cheat day used)
- Every 10-day streak → +2 bonus points
- 20+ points → unlock one cheat day
"""

from datetime import date, timedelta
from database import get_user_progress, update_user_progress


# ─────────────────────────────────────────────
# STREAK FUNCTIONS
# ─────────────────────────────────────────────

def get_today():
    """Return today's date as a string (YYYY-MM-DD)."""
    return str(date.today())


def get_yesterday():
    """Return yesterday's date as a string."""
    return str(date.today() - timedelta(days=1))


def check_and_update_streak(completed=True, use_cheat_day=False):
    """
    Main function to update streak after a study session.
    
    Logic (Rule-Based IF-ELSE):
    - If completed today: streak += 1
    - If missed and cheat day available + user chooses to use it: streak stays, cheat day used
    - If missed and no cheat day: streak resets to 0
    - Every 10 streaks: +2 points bonus
    - If points >= 20: cheat day unlocked
    
    Args:
        completed (bool): True if study was completed, False if missed
        use_cheat_day (bool): True if user wants to spend their cheat day
    
    Returns:
        dict: Updated progress info and any messages
    """

    # Get current progress from database
    progress = get_user_progress()
    streak = progress["streak"]
    points = progress["points"]
    last_date = progress["last_study_date"]
    cheat_used = progress["cheat_day_used"]

    today = get_today()
    yesterday = get_yesterday()

    messages = []

    # ── Case 1: Study COMPLETED ──────────────────────
    if completed:
        # Only count streak if not already updated today
        if last_date != today:
            streak += 1
            messages.append(f"🔥 Great job! Streak is now {streak} days!")

            # Bonus points for every 10-day streak milestone
            if streak % 10 == 0:
                points += 2
                messages.append(f"🎉 Milestone! {streak}-day streak! You earned +2 bonus points!")

            # Update last study date
            last_date = today

        else:
            messages.append("✅ You already completed today's session!")

    # ── Case 2: Study MISSED ─────────────────────────
    else:
        # Check if user wants to use cheat day
        if use_cheat_day and points >= 20 and cheat_used == 0:
            # Spend cheat day: keep streak, deduct 20 points
            points -= 20
            cheat_used = 1
            messages.append("😮‍💨 Cheat day used! Streak saved. 20 points deducted.")
        else:
            # No cheat day — reset streak
            if streak > 0:
                messages.append(f"💔 Streak reset! You had a {streak}-day streak. Stay consistent!")
            streak = 0
            cheat_used = 0  # Reset cheat day usage for next cycle
            messages.append("Don't give up! Start fresh tomorrow. 💪")

    # ── Update database ───────────────────────────────
    update_user_progress(streak, points, last_date, cheat_used)

    # Return result summary
    return {
        "streak": streak,
        "points": points,
        "last_study_date": last_date,
        "cheat_day_available": points >= 20 and cheat_used == 0,
        "messages": messages
    }


def get_streak_status():
    """
    Get current streak status without modifying anything.
    Used to display current status in the UI.
    
    Returns:
        dict: Current streak, points, and status messages
    """
    progress = get_user_progress()
    streak = progress["streak"]
    points = progress["points"]
    cheat_used = progress["cheat_day_used"]

    # Determine cheat day availability
    cheat_available = points >= 20 and cheat_used == 0

    # Motivational messages based on streak (rule-based)
    if streak == 0:
        motivation = "🌱 Start your streak today! Every journey begins with a single step."
    elif streak < 5:
        motivation = f"🔥 {streak}-day streak! You're building momentum. Keep going!"
    elif streak < 10:
        motivation = f"⚡ {streak}-day streak! You're on fire! Almost at the 10-day milestone!"
    elif streak < 20:
        motivation = f"🏆 {streak}-day streak! Incredible consistency! You're a study champion!"
    else:
        motivation = f"🌟 {streak}-day streak! LEGENDARY! You're an absolute study machine!"

    # Points status message
    points_to_next = 20 - (points % 20) if points < 20 else 0
    if cheat_available:
        points_msg = f"🎁 You have a CHEAT DAY available! ({points} points)"
    elif points >= 20:
        points_msg = f"✨ {points} points total. Cheat day ready!"
    else:
        points_msg = f"💰 {points} points. Need {points_to_next} more for a cheat day!"

    return {
        "streak": streak,
        "points": points,
        "cheat_available": cheat_available,
        "motivation": motivation,
        "points_msg": points_msg,
        "next_milestone": 10 - (streak % 10) if streak % 10 != 0 else 10
    }


def get_reward_info():
    """
    Return information about the reward system rules.
    Used to display rules in the UI.
    
    Returns:
        list of str: Reward rules
    """
    return [
        "🔥 Study every day to build your streak",
        "🏅 Every 10-day streak earns +2 bonus points",
        "🎁 Reach 20 points to unlock a Cheat Day",
        "😮‍💨 Use a Cheat Day to skip one session without losing your streak",
        "💡 A cheat day costs 20 points — use wisely!"
    ]


def calculate_progress_to_milestone(streak):
    """
    Calculate progress percentage toward the next 10-day milestone.
    
    Args:
        streak (int): Current streak count
    
    Returns:
        dict: Progress info
    """
    current_in_cycle = streak % 10
    progress_pct = (current_in_cycle / 10) * 100

    return {
        "days_in_current_cycle": current_in_cycle,
        "days_to_next_milestone": 10 - current_in_cycle,
        "progress_percentage": progress_pct
    }
