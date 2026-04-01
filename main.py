"""
main.py - Streamlit UI and App Entry Point
==========================================
This is the main file that runs the entire Study Planner app.
Run it with: streamlit run main.py

The UI is divided into tabs:
1. 📅 Schedule Generator
2. 📋 My Schedule
3. 🏆 Streak & Rewards
4. 🧠 Quiz
5. 📜 History
"""

import streamlit as st
import pandas as pd

# Import our custom modules
from database import initialize_db, save_schedule, get_schedule, update_task_status, reschedule_missed_tasks, log_session
from scheduler import generate_schedule, get_pomodoro_plan, get_difficulty_tips, get_urgency_message, schedule_to_dataframe
from streak import check_and_update_streak, get_streak_status, get_reward_info, calculate_progress_to_milestone
from quiz import get_random_questions, calculate_score, format_question_for_display
from utils import get_greeting, get_motivational_quote, get_break_suggestion, format_hours, get_difficulty_emoji, get_status_emoji, validate_subject_input, summarize_schedule


# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4A90D9;
        text-align: center;
        padding: 10px;
    }
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    /* Success box */
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        border-radius: 5px;
    }
    /* Warning box */
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INITIALIZE DATABASE
# ─────────────────────────────────────────────

# This runs once when the app starts
initialize_db()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/color/96/book.png", width=80)
    st.title("📚 Study Planner")
    st.markdown("---")

    # Show greeting
    st.markdown(f"### {get_greeting()}")
    st.markdown(f"*{get_motivational_quote()}*")
    st.markdown("---")

    # Show quick stats from streak
    status = get_streak_status()
    st.markdown("### 📊 Quick Stats")
    st.metric("🔥 Current Streak", f"{status['streak']} days")
    st.metric("💰 Points", status["points"])

    if status["cheat_available"]:
        st.success("🎁 Cheat Day Available!")

    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown("""
    1. Go to **Schedule** tab
    2. Add your subjects
    3. Generate your plan
    4. Mark tasks as done
    5. Take the **Quiz**!
    """)


# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────

st.markdown('<h1 class="main-header">🤖 AI-Based Study Planner</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Smart scheduling powered by rule-based AI 🧠</p>", unsafe_allow_html=True)
st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Create Schedule",
    "📋 My Schedule",
    "🏆 Streak & Rewards",
    "🧠 Quiz Time",
    "📜 Session History"
])


# ════════════════════════════════════════════════════════
# TAB 1: CREATE SCHEDULE
# ════════════════════════════════════════════════════════

with tab1:
    st.header("📅 Create Your Study Schedule")
    st.markdown("Add your subjects below and let the AI build your smart schedule!")

    # ── Available study hours ──
    st.subheader("⏰ Your Available Hours")
    daily_hours = st.slider(
        "How many hours can you study per day?",
        min_value=1.0,
        max_value=12.0,
        value=4.0,
        step=0.5,
        help="Total hours available for all subjects combined"
    )
    st.info(f"You'll study for **{format_hours(daily_hours)}** per day, split across your subjects.")

    st.markdown("---")

    # ── Subject Input Section ──
    st.subheader("📚 Add Your Subjects")

    # Number of subjects slider
    num_subjects = st.number_input("How many subjects do you want to schedule?", min_value=1, max_value=8, value=3)

    subjects_data = []

    # Create input fields for each subject
    for i in range(int(num_subjects)):
        st.markdown(f"##### Subject {i + 1}")
        col1, col2, col3 = st.columns(3)

        with col1:
            subject_name = st.text_input(
                f"Subject Name",
                placeholder="e.g., Mathematics",
                key=f"subject_{i}"
            )

        with col2:
            difficulty = st.selectbox(
                f"Difficulty",
                options=["Easy", "Medium", "Hard"],
                key=f"difficulty_{i}",
                help="Easy=1, Medium=2, Hard=3 (affects priority)"
            )

        with col3:
            days_left = st.number_input(
                f"Days Until Deadline",
                min_value=1,
                max_value=365,
                value=7,
                key=f"days_{i}",
                help="Fewer days = higher urgency"
            )

        # Only add if subject name is provided
        if subject_name.strip():
            subjects_data.append({
                "subject": subject_name.strip(),
                "difficulty": difficulty,
                "days_left": int(days_left)
            })

    st.markdown("---")

    # ── Generate Button ──
    if st.button("🚀 Generate Smart Schedule", type="primary", use_container_width=True):
        # Validate input
        is_valid, error_msg = validate_subject_input(subjects_data)

        if not is_valid:
            st.error(f"❌ {error_msg}")
        else:
            # Generate schedule using scheduler.py
            with st.spinner("🤖 AI is building your schedule..."):
                schedule = generate_schedule(subjects_data, daily_hours)

            if schedule:
                # Save to database
                save_schedule(schedule)

                st.success("✅ Schedule generated and saved!")
                st.balloons()

                # Show summary
                st.markdown(summarize_schedule(schedule))

                st.markdown("---")
                st.subheader("📊 Your Prioritized Schedule")

                # Display as table
                df = schedule_to_dataframe(schedule)
                st.dataframe(df, use_container_width=True)

                # Show tips for each subject
                st.markdown("---")
                st.subheader("💡 Study Tips & Urgency Alerts")

                for item in schedule:
                    with st.expander(f"📚 {item['subject']} — Tips & Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Difficulty:** {get_difficulty_emoji(item['difficulty'])}")
                            st.markdown(f"**Priority Score:** `{item['priority_score']}`")
                            st.markdown(f"**Allocated:** {format_hours(item['hours_allocated'])} per day")
                        with col2:
                            st.markdown(get_urgency_message(item["days_left"]))
                            st.markdown(get_difficulty_tips(item["difficulty"]))

                        # Pomodoro Plan
                        st.markdown("**🍅 Pomodoro Plan:**")
                        pomodoro = get_pomodoro_plan(item["hours_allocated"])
                        st.markdown(f"- {pomodoro['total_cycles']} study cycle(s)")
                        st.markdown(f"- {pomodoro['total_study_minutes']} min studying + {pomodoro['total_break_minutes']} min breaks")
                        for session in pomodoro["sessions"]:
                            st.markdown(f"  - Session {session['session']}: {session['study_time']} study → {session['break_time']} break")

                st.info(f"☕ Break tip: {get_break_suggestion()}")

            else:
                st.warning("No schedule could be generated. Please check your input.")


# ════════════════════════════════════════════════════════
# TAB 2: MY SCHEDULE
# ════════════════════════════════════════════════════════

with tab2:
    st.header("📋 My Current Schedule")
    st.markdown("Mark tasks as completed or missed. The AI will adapt your schedule accordingly!")

    schedule = get_schedule()

    if not schedule:
        st.info("📭 No schedule yet! Go to **Create Schedule** tab to generate one.")
    else:
        # Show schedule status counts
        completed = sum(1 for t in schedule if t["status"] == "completed")
        missed = sum(1 for t in schedule if t["status"] == "missed")
        pending = sum(1 for t in schedule if t["status"] == "pending")

        col1, col2, col3 = st.columns(3)
        col1.metric("⏳ Pending", pending)
        col2.metric("✅ Completed", completed)
        col3.metric("❌ Missed", missed)

        st.markdown("---")

        # Show each task with action buttons
        for task in schedule:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

                with col1:
                    st.markdown(f"**📚 {task['subject']}**  \n"
                               f"{get_difficulty_emoji(task['difficulty'])} | "
                               f"⏰ {format_hours(task['hours_allocated'])}/day | "
                               f"📅 {task['days_left']} days left")

                with col2:
                    if task["status"] != "completed":
                        if st.button("✅ Done", key=f"done_{task['id']}"):
                            update_task_status(task["id"], "completed")
                            log_session(task["subject"], "completed")
                            # Update streak
                            result = check_and_update_streak(completed=True)
                            for msg in result["messages"]:
                                st.success(msg)
                            st.rerun()

                with col3:
                    if task["status"] == "pending":
                        if st.button("❌ Missed", key=f"miss_{task['id']}"):
                            update_task_status(task["id"], "missed")
                            log_session(task["subject"], "missed")
                            result = check_and_update_streak(completed=False)
                            for msg in result["messages"]:
                                st.warning(msg)
                            st.rerun()

                with col4:
                    status_badge = get_status_emoji(task["status"])
                    if task["status"] == "completed":
                        st.success(status_badge)
                    elif task["status"] == "missed":
                        st.error(status_badge)
                    else:
                        st.info(status_badge)

                st.markdown("---")

        # Reschedule button
        if missed > 0:
            st.warning(f"⚠️ You have {missed} missed task(s). Want the AI to reschedule them?")
            if st.button("🔄 Reschedule Missed Tasks", type="secondary"):
                reschedule_missed_tasks()
                st.success("✅ Missed tasks have been rescheduled with higher priority!")
                st.rerun()


# ════════════════════════════════════════════════════════
# TAB 3: STREAK & REWARDS
# ════════════════════════════════════════════════════════

with tab3:
    st.header("🏆 Streak & Reward System")

    status = get_streak_status()

    # ── Streak Display ──
    st.subheader("🔥 Your Study Streak")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Current Streak", f"{status['streak']} days")
    col2.metric("💰 Total Points", status["points"])
    col3.metric("🎯 Days to Milestone", status["next_milestone"])

    st.markdown(f"### {status['motivation']}")
    st.markdown(status["points_msg"])

    # ── Progress Bar ──
    milestone_data = calculate_progress_to_milestone(status["streak"])
    st.markdown(f"**Progress to next 10-day milestone:** {milestone_data['days_in_current_cycle']}/10 days")
    st.progress(milestone_data["progress_percentage"] / 100)

    st.markdown("---")

    # ── Cheat Day Section ──
    st.subheader("😮‍💨 Cheat Day")

    if status["cheat_available"]:
        st.success("🎁 You have a Cheat Day available! (20 points earned)")
        st.markdown("A cheat day lets you skip one study session **without losing your streak!**")

        if st.button("🛌 Use Cheat Day Now", type="primary"):
            result = check_and_update_streak(completed=False, use_cheat_day=True)
            for msg in result["messages"]:
                st.info(msg)
            st.rerun()
    else:
        points_needed = 20 - status["points"] if status["points"] < 20 else 0
        if points_needed > 0:
            st.info(f"💡 Earn {points_needed} more points to unlock a Cheat Day!")
        else:
            st.info("🔒 Cheat day already used this cycle. Keep studying to earn more points!")

    st.markdown("---")

    # ── Reward Rules ──
    st.subheader("📜 Reward System Rules")
    for rule in get_reward_info():
        st.markdown(f"- {rule}")


# ════════════════════════════════════════════════════════
# TAB 4: QUIZ TIME
# ════════════════════════════════════════════════════════

with tab4:
    st.header("🧠 Quiz Time!")
    st.markdown("Test your knowledge after your study session. Good luck! 🍀")

    # Number of questions selector
    num_q = st.selectbox("How many questions?", options=[3, 4, 5], index=2)

    # Initialize quiz state in session_state
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    # Start Quiz Button
    if st.button("🎯 Start New Quiz", type="primary"):
        st.session_state.quiz_questions = get_random_questions(num_q)
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False

    # Display Questions
    if st.session_state.quiz_questions:
        st.markdown("---")
        st.subheader("📝 Answer the Questions Below")

        for idx, question in enumerate(st.session_state.quiz_questions):
            st.markdown(format_question_for_display(question, idx + 1))

            # Show options as radio buttons
            selected = st.radio(
                f"Choose your answer:",
                options=question["options"],
                key=f"q_{question['id']}",
                index=None,
                label_visibility="collapsed"
            )

            # Save answer if selected (extract just the letter)
            if selected:
                # Option format is "A) option text" — extract the letter
                letter = selected.split(")")[0].strip()
                st.session_state.quiz_answers[question["id"]] = letter

            st.markdown("---")

        # Submit Button
        all_answered = len(st.session_state.quiz_answers) == len(st.session_state.quiz_questions)

        if not all_answered:
            st.warning(f"Please answer all {len(st.session_state.quiz_questions)} questions to submit.")

        if st.button("📊 Submit Quiz", disabled=not all_answered, type="primary"):
            st.session_state.quiz_submitted = True

        # Show Results
        if st.session_state.quiz_submitted:
            results = calculate_score(st.session_state.quiz_questions, st.session_state.quiz_answers)

            st.markdown("---")
            st.subheader("🏆 Quiz Results")

            # Score display
            col1, col2 = st.columns(2)
            col1.metric("✅ Score", f"{results['score']} / {results['total']}")
            col2.metric("📊 Percentage", f"{results['percentage']}%")

            # Score progress bar
            st.progress(results["percentage"] / 100)

            # Feedback
            st.markdown(f"### {results['feedback']}")

            # Detailed results
            st.markdown("---")
            st.subheader("📋 Detailed Results")
            for res in results["results"]:
                if res["is_correct"]:
                    st.success(f"✅ {res['question']}")
                else:
                    st.error(f"❌ {res['question']}  \n"
                            f"Your answer: **{res['your_answer']}** | "
                            f"Correct answer: **{res['correct_answer']}**")

            # Break suggestion
            st.markdown("---")
            st.info(f"🍅 Quiz done! Time for a short break: {get_break_suggestion()}")

    else:
        st.info("👆 Click **Start New Quiz** to begin!")


# ════════════════════════════════════════════════════════
# TAB 5: SESSION HISTORY
# ════════════════════════════════════════════════════════

with tab5:
    st.header("📜 Session History")
    st.markdown("Track all your past study sessions.")

    from database import get_session_history, reset_progress

    history = get_session_history()

    if not history:
        st.info("📭 No session history yet. Complete or miss a study task to see it here!")
    else:
        # Summary stats
        completed_sessions = [h for h in history if h["status"] == "completed"]
        missed_sessions = [h for h in history if h["status"] == "missed"]

        col1, col2, col3 = st.columns(3)
        col1.metric("📅 Total Sessions", len(history))
        col2.metric("✅ Completed", len(completed_sessions))
        col3.metric("❌ Missed", len(missed_sessions))

        # Completion rate
        if history:
            rate = round(len(completed_sessions) / len(history) * 100, 1)
            st.markdown(f"**📊 Completion Rate: {rate}%**")
            st.progress(rate / 100)

        st.markdown("---")

        # History table using pandas
        df = pd.DataFrame(history)
        df["status"] = df["status"].apply(lambda x: "✅ Completed" if x == "completed" else "❌ Missed")
        df.columns = ["📅 Date", "📚 Subject", "Status"]
        st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Danger Zone
    with st.expander("⚠️ Reset All Data"):
        st.warning("This will delete ALL your progress, schedule, and history!")
        if st.button("🗑️ Reset Everything", type="secondary"):
            reset_progress()
            st.success("All data has been reset. Fresh start! 🌱")
            st.rerun()
