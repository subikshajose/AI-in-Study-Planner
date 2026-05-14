"""
main.py - AI Study Planner | Streamlit App Entry Point
Run with: streamlit run main.py
"""

import streamlit as st
import pandas as pd
from datetime import date

# ─── Import project modules ────────────────────────────────────────────────────
from database import (
    initialize_db, save_schedule, get_schedule,
    update_task_status, reschedule_missed_tasks,
    log_study_session, get_study_log, reset_all_data
)
from scheduler import generate_schedule, get_pomodoro_sessions
from streak import (
    get_streak_info, mark_day_completed, mark_day_missed,
    can_use_cheat_day, get_motivational_message, get_streak_badge
)
from quiz import get_quiz_questions, calculate_score, get_quiz_result_message
from utils import (
    format_hours, get_difficulty_emoji, get_status_emoji,
    generate_pomodoro_plan, validate_subject_inputs, progress_bar_value
)
# ─── NEW FEATURE IMPORTS ───────────────────────────────────────────────────────
from pdf_flashcard import (
    extract_text_from_pdf, clean_text, generate_flashcards,
    generate_definition_cards, get_text_stats
)
from resources import (
    get_recommendations, get_all_exam_types, get_all_subjects, get_resource_summary
)
from ml_performance import (
    initialize_ml_tables, log_quiz_result, log_study_hours,
    predict_exam_readiness, get_performance_chart_data,
    identify_weak_subjects, get_score_trend, add_sample_data_for_demo
)

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS (dark academic theme) ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
    }
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #e2c97e !important;
        font-size: 2.8rem;
        margin: 0;
    }
    .main-header p {
        color: #a8b2d8;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e2c97e;
    }
    .stat-card .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .subject-card {
        background: #1e293b;
        border-left: 4px solid #e2c97e;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #e2c97e;
        border-bottom: 2px solid #334155;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    .pomodoro-study {
        background: #1e3a5f;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        color: #93c5fd;
    }
    .pomodoro-break {
        background: #1a3a2a;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        color: #86efac;
    }
    .reward-box {
        background: linear-gradient(135deg, #2d1b69, #1e1b4b);
        border: 2px solid #7c3aed;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .quiz-question {
        background: #1e293b;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .tip-box {
        background: #1a2f1a;
        border-left: 3px solid #4ade80;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        color: #86efac;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── INITIALIZE DATABASE ───────────────────────────────────────────────────────
initialize_db()
try:
    initialize_ml_tables()
except Exception:
    pass

# ─── SESSION STATE SETUP ──────────────────────────────────────────────────────
# These persist within one browser session

if "subjects_list" not in st.session_state:
    st.session_state.subjects_list = []  # List of subject dicts

if "schedule_df" not in st.session_state:
    st.session_state.schedule_df = None

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_subject" not in st.session_state:
    st.session_state.quiz_subject = "General"

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📚 AI Study Planner</h1>
    <p>Smart scheduling · Streak tracking · Rewards · Quizzes</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "📅 Schedule", "🔥 Streak & Rewards", "🧠 Quiz",
         "📖 Study Log", "📄 PDF Flashcards", "🔗 Resources", "📊 Performance"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Fetch streak info for sidebar
    progress = get_streak_info()
    streak = progress['streak']
    points = progress['points']

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">🔥 {streak}</div>
        <div class="stat-label">Current Streak</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-card" style="margin-top:0.5rem">
        <div class="stat-value">⭐ {points}</div>
        <div class="stat-label">Total Points</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"**Badge:** {get_streak_badge(streak)}")
    st.markdown(f"*{get_motivational_message(streak)}*")

    st.markdown("---")
    if st.button("🗑️ Reset All Data", use_container_width=True):
        reset_all_data()
        st.session_state.subjects_list = []
        st.session_state.schedule_df = None
        st.success("All data reset!")
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":

    st.markdown('<h2 class="section-header">Today\'s Overview</h2>', unsafe_allow_html=True)

    # Top Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">🔥 {streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">⭐ {points}</div>
            <div class="stat-label">Points</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        schedule_rows = get_schedule()
        completed = len([r for r in schedule_rows if r[6] == 'completed'])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">✅ {completed}</div>
            <div class="stat-label">Tasks Done</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        cheat_available = "Yes 😎" if can_use_cheat_day(points) else "No"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{cheat_available}</div>
            <div class="stat-label">Cheat Day</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Streak Progress Bar
    st.markdown("#### 📊 Progress to Next Milestone (every 10 days)")
    progress_val = progress_bar_value(streak)
    days_to_next = 10 - (streak % 10)
    st.progress(progress_val)
    st.caption(f"{streak % 10}/10 days — {days_to_next} more day(s) to earn +2 points!")

    # Motivational Banner
    st.info(f"💡 {get_motivational_message(streak)}")

    # Quick Schedule Preview
    st.markdown('<h3 class="section-header">📋 Current Schedule (Quick View)</h3>', unsafe_allow_html=True)

    schedule_rows = get_schedule()
    if schedule_rows:
        for row in schedule_rows[:5]:  # Show first 5
            task_id, subject, difficulty, days_left, priority, daily_hours, status = row
            diff_emoji = get_difficulty_emoji(difficulty)
            status_emoji = get_status_emoji(status)
            st.markdown(f"""
            <div class="subject-card">
                {status_emoji} <strong>{subject}</strong> &nbsp;|&nbsp;
                {diff_emoji} {difficulty} &nbsp;|&nbsp;
                ⏰ {format_hours(daily_hours)}/day &nbsp;|&nbsp;
                📅 {days_left} days left
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="tip-box">
            👉 No schedule yet! Go to <strong>📅 Schedule</strong> to add subjects and generate your plan.
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Schedule":

    st.markdown('<h2 class="section-header">📅 Build Your Study Schedule</h2>', unsafe_allow_html=True)

    # ─── Step 1: Add Subjects ─────────────────────────────────────────────────
    st.markdown("### Step 1: Add Your Subjects")

    with st.form("add_subject_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            subject_name = st.text_input("📖 Subject Name", placeholder="e.g. Mathematics")
        with col2:
            difficulty = st.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard"])
        with col3:
            days_left = st.number_input("📅 Days Until Deadline", min_value=1, max_value=365, value=7)

        submitted = st.form_submit_button("➕ Add Subject", use_container_width=True)

        if submitted:
            if subject_name.strip():
                st.session_state.subjects_list.append({
                    "subject": subject_name.strip(),
                    "difficulty": difficulty,
                    "days_left": int(days_left)
                })
                st.success(f"✅ Added: {subject_name}")
            else:
                st.error("Please enter a subject name.")

    # Show current subjects list
    if st.session_state.subjects_list:
        st.markdown("### Current Subjects:")
        for i, s in enumerate(st.session_state.subjects_list):
            col1, col2 = st.columns([6, 1])
            with col1:
                emoji = get_difficulty_emoji(s['difficulty'])
                st.markdown(f"""
                <div class="subject-card">
                    {emoji} <strong>{s['subject']}</strong> —
                    {s['difficulty']} — ⏰ {s['days_left']} days left
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.subjects_list.pop(i)
                    st.rerun()

    # ─── Step 2: Set Daily Hours & Generate ───────────────────────────────────
    st.markdown("### Step 2: Set Available Hours & Generate Schedule")

    total_hours = st.slider(
        "⏰ How many hours can you study per day?",
        min_value=1.0, max_value=12.0, value=4.0, step=0.5
    )

    if st.button("🚀 Generate Smart Schedule", use_container_width=True, type="primary"):
        is_valid, error_msg = validate_subject_inputs(st.session_state.subjects_list)
        if not is_valid:
            st.error(error_msg)
        else:
            df = generate_schedule(st.session_state.subjects_list, total_hours)
            df['status'] = 'pending'
            st.session_state.schedule_df = df
            save_schedule(df)
            st.success("✅ Schedule generated and saved!")
            st.rerun()

    # ─── Step 3: View & Manage Schedule ──────────────────────────────────────
    st.markdown('<h3 class="section-header">📋 Your Study Schedule</h3>', unsafe_allow_html=True)

    schedule_rows = get_schedule()
    if schedule_rows:
        for row in schedule_rows:
            task_id, subject, difficulty, days_left, priority, daily_hours, status = row
            diff_emoji = get_difficulty_emoji(difficulty)
            status_emoji = get_status_emoji(status)
            pomodoro = get_pomodoro_sessions(daily_hours)

            with st.expander(f"{status_emoji} {diff_emoji} {subject} — {format_hours(daily_hours)}/day | Priority: {round(priority, 2)}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Difficulty", f"{diff_emoji} {difficulty}")
                with col2:
                    st.metric("Days Left", f"📅 {days_left}")
                with col3:
                    st.metric("Pomodoros", f"🍅 {pomodoro['num_sessions']}")

                st.markdown("**⏱️ Pomodoro Plan:**")
                plan = generate_pomodoro_plan(daily_hours)
                for block in plan[:6]:  # Show first 6 blocks
                    if block['type'] == 'study':
                        st.markdown(f'<div class="pomodoro-study">{block["label"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="pomodoro-break">{block["label"]}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Action buttons (only show if pending)
                if status == 'pending':
                    col_done, col_miss = st.columns(2)
                    with col_done:
                        if st.button(f"✅ Mark Completed", key=f"done_{task_id}"):
                            update_task_status(task_id, 'completed')
                            log_study_session(subject, daily_hours, 'completed')
                            result = mark_day_completed()
                            st.success(result['message'])
                            # Start quiz for this subject
                            st.session_state.quiz_subject = subject
                            st.session_state.quiz_questions = get_quiz_questions(subject, 5)
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
                    with col_miss:
                        if st.button(f"❌ Mark Missed", key=f"miss_{task_id}"):
                            if can_use_cheat_day(points):
                                use_cheat = st.checkbox(
                                    "🎲 Use cheat day? (costs 20 pts)",
                                    key=f"cheat_{task_id}"
                                )
                                result = mark_day_missed(use_cheat_day=use_cheat)
                            else:
                                result = mark_day_missed(use_cheat_day=False)
                            update_task_status(task_id, 'missed')
                            log_study_session(subject, daily_hours, 'missed')
                            reschedule_missed_tasks()
                            st.warning(result['message'])
                            st.rerun()
                else:
                    st.markdown(f"**Status:** {status_emoji} {status.capitalize()}")
    else:
        st.info("👆 Add subjects above and click **Generate Smart Schedule**.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: STREAK & REWARDS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔥 Streak & Rewards":

    st.markdown('<h2 class="section-header">🔥 Streak & Rewards</h2>', unsafe_allow_html=True)

    progress = get_streak_info()
    streak = progress['streak']
    points = progress['points']
    last_date = progress['last_study_date'] or "Not started yet"
    cheat_days_used = progress['cheat_days_used']

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">🔥 {streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">⭐ {points}</div>
            <div class="stat-label">Total Points</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">😎 {cheat_days_used}</div>
            <div class="stat-label">Cheat Days Used</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"**Last Study Date:** {last_date}")
    st.markdown(f"**Badge:** {get_streak_badge(streak)}")

    # Progress to next milestone
    st.markdown("#### 📊 Streak Progress")
    current_in_cycle = streak % 10
    st.progress(progress_bar_value(streak))
    st.caption(f"{current_in_cycle}/10 days in current cycle — {10 - current_in_cycle} days to +2 points")

    # Reward System Info
    st.markdown('<h3 class="section-header">🎁 Reward System</h3>', unsafe_allow_html=True)

    st.markdown("""
    <div class="reward-box">
        <h4 style="color:#c4b5fd; margin:0 0 0.5rem 0">🏆 How Rewards Work</h4>
        <p style="color:#e2e8f0; margin:0.3rem 0">📅 Every <strong>10-day streak</strong> → earn <strong>+2 points</strong></p>
        <p style="color:#e2e8f0; margin:0.3rem 0">⭐ Reach <strong>20 points</strong> → unlock a <strong>Cheat Day</strong></p>
        <p style="color:#e2e8f0; margin:0.3rem 0">😎 Cheat Day = skip 1 study day without breaking your streak</p>
        <p style="color:#e2e8f0; margin:0.3rem 0">💸 Using a Cheat Day costs <strong>20 points</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Cheat Day Status
    st.markdown("#### 😎 Cheat Day Status")
    if can_use_cheat_day(points):
        st.success(f"🎉 You have enough points ({points} pts) to use a Cheat Day!")
        st.markdown("Use it on the **📅 Schedule** page when marking a task as missed.")
    else:
        pts_needed = 20 - points
        st.warning(f"You need {pts_needed} more point(s) to unlock a Cheat Day. Keep studying! 💪")

    # Manual test buttons (for demo/testing)
    st.markdown('<h3 class="section-header">🧪 Test Streak (Demo)</h3>', unsafe_allow_html=True)
    st.caption("Use these buttons to simulate study days for testing purposes.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Simulate Study Day", use_container_width=True):
            result = mark_day_completed()
            st.success(result['message'])
            if result['milestone_reached']:
                st.balloons()
            st.rerun()
    with col2:
        if st.button("❌ Simulate Missed Day", use_container_width=True):
            result = mark_day_missed(use_cheat_day=False)
            st.warning(result['message'])
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Quiz":

    st.markdown('<h2 class="section-header">🧠 Knowledge Quiz</h2>', unsafe_allow_html=True)

    st.info("📝 Test yourself after each study session! Questions are matched to your subject.")

    # Subject selector for quiz
    available_subjects = ["General", "Math", "Science", "History", "English"]
    # Also include scheduled subjects
    schedule_rows = get_schedule()
    scheduled_subjects = [row[1] for row in schedule_rows]
    all_subjects = list(set(available_subjects + scheduled_subjects))

    quiz_subject = st.selectbox("📚 Choose a subject:", all_subjects, index=0)
    num_questions = st.slider("❓ Number of questions:", 3, 5, 5)

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎲 Start New Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_questions = get_quiz_questions(quiz_subject, num_questions)
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_subject = quiz_subject

    # Show quiz questions
    if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        st.markdown(f"### 📋 Quiz: {st.session_state.quiz_subject}")

        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"""
            <div class="quiz-question">
                <strong>Q{i+1}: {q['question']}</strong>
            </div>
            """, unsafe_allow_html=True)

            selected = st.radio(
                f"Choose your answer for Q{i+1}:",
                q['options'],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[i] = selected

        if st.button("📤 Submit Quiz", use_container_width=True, type="primary"):
            if len(st.session_state.quiz_answers) == len(st.session_state.quiz_questions):
                st.session_state.quiz_submitted = True
                st.rerun()
            else:
                st.error("Please answer all questions before submitting.")

    # Show quiz results
    elif st.session_state.quiz_submitted and st.session_state.quiz_questions:
        answers_list = [st.session_state.quiz_answers[i] for i in range(len(st.session_state.quiz_questions))]
        result = calculate_score(st.session_state.quiz_questions, answers_list)

        # Score display
        score_pct = result['percentage']
        st.markdown(f"""
        <div class="stat-card" style="margin: 1rem 0">
            <div class="stat-value">{result['score']}/{result['total']}</div>
            <div class="stat-label">{score_pct}% Score</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### {get_quiz_result_message(score_pct)}")
        st.progress(score_pct / 100)

        # Detailed feedback
        st.markdown("#### 📝 Answer Review:")
        for fb in result['feedback']:
            if "✅" in fb['result']:
                st.success(f"**{fb['question']}**\n\n{fb['result']}")
            else:
                st.error(f"**{fb['question']}**\n\nYour answer: {fb['your_answer']}\n\n{fb['result']}")

        if st.button("🔄 Try Another Quiz", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers = {}
            st.rerun()

    elif not st.session_state.quiz_questions:
        st.markdown("""
        <div class="tip-box">
            👆 Select a subject and click <strong>Start New Quiz</strong> to begin!
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: STUDY LOG
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Study Log":

    st.markdown('<h2 class="section-header">📖 Study History Log</h2>', unsafe_allow_html=True)

    study_log = get_study_log()

    if study_log:
        # Convert to DataFrame for display
        log_df = pd.DataFrame(study_log, columns=["Date", "Subject", "Hours", "Status"])
        log_df["Hours"] = log_df["Hours"].apply(format_hours)
        log_df["Status"] = log_df["Status"].apply(lambda s: f"{get_status_emoji(s)} {s.capitalize()}")

        # Summary stats
        col1, col2, col3 = st.columns(3)
        total_sessions = len(study_log)
        completed_sessions = len([r for r in study_log if r[3] == 'completed'])
        missed_sessions = len([r for r in study_log if r[3] == 'missed'])

        with col1:
            st.metric("📚 Total Sessions", total_sessions)
        with col2:
            st.metric("✅ Completed", completed_sessions)
        with col3:
            st.metric("❌ Missed", missed_sessions)

        if total_sessions > 0:
            completion_rate = round((completed_sessions / total_sessions) * 100, 1)
            st.markdown(f"**Completion Rate:** {completion_rate}%")
            st.progress(completion_rate / 100)

        # Full log table
        st.markdown("### 📊 All Study Sessions")
        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📭 No study sessions recorded yet. Start studying to see your history here!")

    st.markdown("---")
    st.markdown("""
    <div class="tip-box">
        💡 <strong>Tip:</strong> Study consistently to build your streak.
        Missing a day resets your streak — but you can protect it with a Cheat Day if you have 20+ points!
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: PDF FLASHCARDS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 PDF Flashcards":

    st.markdown('<h2 class="section-header">📄 PDF Flashcard Generator</h2>', unsafe_allow_html=True)
    st.info("📤 Upload any study material PDF — the AI will extract key concepts and auto-generate MCQ flashcards for you!")

    # ─── File Upload ──────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"],
        help="Supports textbooks, notes, NCERT books, question banks"
    )

    col1, col2 = st.columns(2)
    with col1:
        num_flashcards = st.slider("🃏 Number of Flashcards", min_value=5, max_value=20, value=10)
    with col2:
        include_definitions = st.checkbox("📖 Include Definition Cards", value=True)

    if uploaded_file is not None:
        with st.spinner("🔍 Extracting text from PDF..."):
            raw_text = extract_text_from_pdf(uploaded_file)

        if raw_text.startswith("ERROR:"):
            st.error(raw_text)
            st.info("💡 Make sure PyMuPDF is installed: `pip install pymupdf`")
        else:
            # Clean and analyze text
            clean = clean_text(raw_text)
            stats = get_text_stats(clean)

            # Show PDF stats
            st.markdown("### 📊 Document Analysis")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📝 Words", f"{stats['total_words']:,}")
            c2.metric("📄 Est. Pages", stats['estimated_pages'])
            c3.metric("🔢 Sentences", stats['total_sentences'])
            c4.metric("⏱️ Read Time", f"{stats['reading_time_minutes']} min")

            # Top keywords
            if stats['top_keywords']:
                st.markdown("**🔑 Top Keywords Detected:**")
                kw_display = " &nbsp;|&nbsp; ".join(
                    [f"`{kw}`" for kw in stats['top_keywords'][:10]]
                )
                st.markdown(kw_display)

            st.markdown("---")

            # ─── Generate Flashcards Button ───────────────────────────────────
            if st.button("⚡ Generate Flashcards", use_container_width=True, type="primary"):
                with st.spinner("🧠 Generating MCQ flashcards..."):
                    # Generate fill-in-blank cards
                    fib_cards = generate_flashcards(clean, num_cards=num_flashcards)

                    # Generate definition cards if enabled
                    def_cards = []
                    if include_definitions:
                        def_cards = generate_definition_cards(clean, num_cards=5)

                    all_cards = fib_cards + def_cards

                st.session_state['flashcards'] = all_cards
                st.session_state['flashcard_answers'] = {}
                st.session_state['flashcard_submitted'] = False
                st.success(f"✅ Generated {len(all_cards)} flashcards!")
                st.rerun()

    # ─── Show Flashcards ──────────────────────────────────────────────────────
    if 'flashcards' in st.session_state and st.session_state['flashcards']:
        cards = st.session_state['flashcards']
        submitted = st.session_state.get('flashcard_submitted', False)

        st.markdown(f"### 🃏 Your Flashcards ({len(cards)} cards)")

        if not submitted:
            for i, card in enumerate(cards):
                with st.expander(f"Card {i+1} — {card['question'][:60]}...", expanded=(i == 0)):
                    st.markdown(f"**❓ {card['question']}**")

                    selected = st.radio(
                        "Choose your answer:",
                        card['options'],
                        key=f"fc_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state['flashcard_answers'][i] = selected

                    # Show hint
                    if st.checkbox("💡 Show Hint", key=f"hint_{i}"):
                        st.info(f"Hint: {card['hint']}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📤 Submit All Flashcards", use_container_width=True, type="primary"):
                st.session_state['flashcard_submitted'] = True
                st.rerun()

        else:
            # Show results
            answers = st.session_state.get('flashcard_answers', {})
            correct = 0
            for i, card in enumerate(cards):
                user_ans = answers.get(i, "")
                is_correct = user_ans == card['answer']
                if is_correct:
                    correct += 1

                with st.expander(
                    f"{'✅' if is_correct else '❌'} Card {i+1}",
                    expanded=not is_correct
                ):
                    st.markdown(f"**{card['question']}**")
                    if is_correct:
                        st.success(f"Your answer: {user_ans} ✅")
                    else:
                        st.error(f"Your answer: {user_ans} ❌")
                        st.info(f"Correct answer: **{card['answer']}**")

            # Summary
            pct = round((correct / len(cards)) * 100, 1) if cards else 0
            st.markdown(f"### 🎯 Score: {correct}/{len(cards)} ({pct}%)")
            st.progress(pct / 100)

            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state['flashcard_submitted'] = False
                st.session_state['flashcard_answers'] = {}
                st.rerun()

    elif 'flashcards' not in st.session_state:
        st.markdown("""
        <div class="tip-box">
            👆 Upload a PDF above and click <strong>Generate Flashcards</strong> to start!<br><br>
            💡 Works best with: NCERT textbooks, notes, question banks, study guides.
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7: RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Resources":

    st.markdown('<h2 class="section-header">🔗 Study Resource Recommender</h2>', unsafe_allow_html=True)
    st.info("🎯 Get curated YouTube channels and websites based on your subject and exam type — all free!")

    # ─── Filters ─────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        exam_options = ["(Any Exam)"] + get_all_exam_types()
        selected_exam = st.selectbox("🏆 Exam Type", exam_options)
        selected_exam = None if selected_exam == "(Any Exam)" else selected_exam

    with col2:
        subject_options = ["(Any Subject)"] + get_all_subjects()
        selected_subject = st.selectbox("📚 Subject", subject_options)
        selected_subject = None if selected_subject == "(Any Subject)" else selected_subject

    with col3:
        res_type = st.selectbox("📺 Resource Type", ["Both", "YouTube Only", "Websites Only"])
        res_type_filter = None
        if res_type == "YouTube Only":
            res_type_filter = "youtube"
        elif res_type == "Websites Only":
            res_type_filter = "website"

    # ─── Get Recommendations ─────────────────────────────────────────────────
    recommendations = get_recommendations(
        subject=selected_subject,
        exam_type=selected_exam,
        resource_type=res_type_filter,
        top_n=12
    )

    summary = get_resource_summary(recommendations)

    # Stats bar
    c1, c2, c3 = st.columns(3)
    c1.metric("📺 YouTube Channels", summary['youtube_channels'])
    c2.metric("🌐 Websites", summary['websites'])
    c3.metric("🆓 Free Resources", summary['free_resources'])

    st.markdown("---")

    if not recommendations:
        st.warning("No resources found for this combination. Try broader filters.")
    else:
        # ─── YouTube Channels Section ─────────────────────────────────────────
        yt_resources = [r for r in recommendations if r['type'] == 'youtube']
        web_resources = [r for r in recommendations if r['type'] == 'website']

        if yt_resources and res_type_filter != "website":
            st.markdown("### 📺 YouTube Channels")
            for i in range(0, len(yt_resources), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(yt_resources):
                        r = yt_resources[i + j]
                        with col:
                            lang_badge = "🇮🇳" if r['language'] == "Hindi" else ("🌍" if r['language'] == "Both" else "🇬🇧")
                            free_badge = "🆓 Free" if r['free'] else "💰 Paid"
                            st.markdown(f"""
                            <div class="subject-card" style="min-height:130px">
                                <div style="font-size:1.1rem; font-weight:700; color:#e2c97e">{r['icon']} {r['name']}</div>
                                <div style="color:#94a3b8; font-size:0.8rem; margin:0.3rem 0">{lang_badge} {r['language']} &nbsp;|&nbsp; {free_badge}</div>
                                <div style="color:#cbd5e1; font-size:0.85rem">{r['description']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.link_button(f"▶️ Open {r['name']}", r['url'], use_container_width=True)

        # ─── Websites Section ─────────────────────────────────────────────────
        if web_resources and res_type_filter != "youtube":
            st.markdown("### 🌐 Recommended Websites")
            for i in range(0, len(web_resources), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(web_resources):
                        r = web_resources[i + j]
                        with col:
                            free_badge = "🆓 Free" if r['free'] else "💰 Paid"
                            st.markdown(f"""
                            <div class="subject-card" style="min-height:130px">
                                <div style="font-size:1.1rem; font-weight:700; color:#e2c97e">{r['icon']} {r['name']}</div>
                                <div style="color:#94a3b8; font-size:0.8rem; margin:0.3rem 0">{free_badge}</div>
                                <div style="color:#cbd5e1; font-size:0.85rem">{r['description']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.link_button(f"🌐 Visit {r['name']}", r['url'], use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="tip-box">
        💡 <strong>Tip:</strong> Combine a YouTube channel for concept learning with a website for
        practice tests. Example: Physics Wallah (concepts) + Testbook (mock tests) = 🔥
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8: ML PERFORMANCE MONITOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Performance":

    st.markdown('<h2 class="section-header">📊 AI Performance Monitor</h2>', unsafe_allow_html=True)
    st.info("🤖 ML-powered analysis of your study patterns, quiz trends, and exam readiness prediction.")

    # Demo data button
    col_demo, col_space = st.columns([2, 5])
    with col_demo:
        if st.button("🧪 Load Demo Data (14 days)", help="Populate with sample data to see all charts"):
            with st.spinner("Loading demo data..."):
                add_sample_data_for_demo()
            st.success("Demo data loaded! Scroll down to see insights.")
            st.rerun()

    st.markdown("---")

    # ─── LOG TODAY'S STUDY SESSION ────────────────────────────────────────────
    with st.expander("➕ Log Today's Study Hours", expanded=False):
        with st.form("log_hours_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                log_subject = st.text_input("Subject", placeholder="e.g. Physics")
            with c2:
                hours_studied = st.number_input("Hours Studied", min_value=0.0, max_value=16.0,
                                                 value=2.0, step=0.5)
            with c3:
                target_hrs = st.number_input("Target Hours", min_value=0.5, max_value=16.0,
                                              value=3.0, step=0.5)
            if st.form_submit_button("📝 Log Session", use_container_width=True):
                if log_subject.strip():
                    log_study_hours(log_subject.strip(), hours_studied, target_hrs)
                    st.success(f"Logged {hours_studied}h for {log_subject}!")
                    st.rerun()
                else:
                    st.error("Please enter a subject name.")

    # ─── EXAM READINESS SCORE ────────────────────────────────────────────────
    st.markdown("### 🎯 Exam Readiness Prediction")

    with st.spinner("🤖 Running ML model..."):
        readiness = predict_exam_readiness()

    score = readiness['readiness_score']
    grade = readiness['grade']
    breakdown = readiness['breakdown']

    # Big score display
    score_color = "#4ade80" if score >= 70 else ("#facc15" if score >= 50 else "#f87171")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                border: 2px solid {score_color}; border-radius: 16px;
                padding: 2rem; text-align: center; margin: 1rem 0">
        <div style="font-size: 4rem; font-weight: 700; color: {score_color}">{score}%</div>
        <div style="font-size: 1.3rem; color: #e2e8f0; margin-top: 0.5rem">{grade}</div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.3rem">
            {'Using scikit-learn Linear Regression' if readiness.get('ml_available') else 'Using weighted formula (install scikit-learn for ML mode)'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(score / 100)

    # Breakdown metrics
    st.markdown("#### 📐 Score Breakdown")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Quiz Score", f"{breakdown['avg_quiz_score']}%", help="Average score across all quizzes")
    b2.metric("Hours Met", f"{breakdown['hours_completion_rate']}%", help="Study hours vs target")
    b3.metric("Consistency", f"{breakdown['streak_consistency']}%", help="Based on your study streak")
    b4.metric("Weak Penalty", f"-{breakdown['weak_subject_penalty']}%", help="Deducted for weak subjects")

    # Improvement tips
    st.markdown("#### 💡 Personalized Improvement Tips")
    for tip in readiness['improvement_tips']:
        st.markdown(f"""
        <div class="tip-box" style="margin: 0.4rem 0">{tip}</div>
        """, unsafe_allow_html=True)

    # ─── WEAK SUBJECT ANALYSIS ────────────────────────────────────────────────
    st.markdown("### 🔬 Subject-Wise Analysis")
    weak_data = identify_weak_subjects()

    if weak_data:
        for subject, info in weak_data.items():
            status = info['status']
            avg = info['avg_score']
            quizzes = info['total_quizzes']
            rec = info['recommendation']

            # Color based on status
            if "Weak" in status:
                bg = "#3b1515"
                border = "#ef4444"
            elif "Improvement" in status:
                bg = "#2d2410"
                border = "#f59e0b"
            else:
                bg = "#0f2918"
                border = "#22c55e"

            st.markdown(f"""
            <div style="background:{bg}; border-left:4px solid {border};
                        border-radius:8px; padding:1rem; margin:0.5rem 0">
                <div style="font-weight:700; color:#e2e8f0; font-size:1rem">
                    {status} &nbsp;|&nbsp; {subject}
                </div>
                <div style="color:#94a3b8; font-size:0.85rem; margin:0.2rem 0">
                    Avg Score: <strong style="color:#e2e8f0">{avg}%</strong>
                    &nbsp;|&nbsp; Quizzes taken: <strong style="color:#e2e8f0">{quizzes}</strong>
                </div>
                <div style="color:#cbd5e1; font-size:0.85rem; margin-top:0.3rem">💡 {rec}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No quiz data yet. Take some quizzes to see subject analysis!")
        st.markdown("""
        <div class="tip-box">
            👉 Go to <strong>🧠 Quiz</strong> page → take quizzes → come back here for analysis.
        </div>
        """, unsafe_allow_html=True)

    # ─── PERFORMANCE CHARTS ───────────────────────────────────────────────────
    st.markdown("### 📈 Performance Charts")
    chart_data = get_performance_chart_data()

    tab1, tab2, tab3 = st.tabs(["📈 Quiz Scores Over Time", "⏰ Study Hours vs Target", "📚 Subject Comparison"])

    with tab1:
        score_df = chart_data['score_over_time']
        if not score_df.empty and len(score_df) > 0:
            score_df = score_df.set_index('date')
            st.line_chart(score_df['avg_score'], use_container_width=True)
            st.caption("Average quiz score per day. Upward trend = improving! 📈")
        else:
            st.info("Take quizzes to see your score trend here.")

    with tab2:
        hours_df = chart_data['hours_vs_target']
        if not hours_df.empty:
            hours_chart = hours_df.set_index('date')[['hours_studied', 'target_hours']]
            st.bar_chart(hours_chart, use_container_width=True)
            st.caption("Blue = hours studied | Red = target. Aim for blue ≥ red every day! 🎯")
        else:
            st.info("Log study hours to see your hours vs target chart.")

    with tab3:
        subj_df = chart_data['subject_scores']
        if not subj_df.empty:
            subj_chart = subj_df.set_index('subject')
            st.bar_chart(subj_chart['avg_score'], use_container_width=True)
            st.caption("Shorter bars = subjects that need more attention. 🔴")
        else:
            st.info("Take quizzes across multiple subjects to see comparison.")

    st.markdown("---")
    st.markdown("""
    <div class="tip-box">
        🤖 <strong>How the ML model works:</strong> The readiness score uses
        <strong>Linear Regression</strong> (scikit-learn) trained on reference student profiles.
        It weighs your quiz scores (40%), study hours completion (30%),
        streak consistency (20%), and weak subject penalty (10%).
        The more data you log, the more accurate the prediction!
    </div>
    """, unsafe_allow_html=True)