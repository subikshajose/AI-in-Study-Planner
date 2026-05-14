"""
quiz.py - Quiz Feature After Study Sessions
============================================
This file handles:
- Loading quiz questions from JSON file
- Randomly selecting 3-5 questions
- Evaluating user answers
- Showing score and feedback

Questions are stored in: data/questions.json
"""

import json
import random
import os


# ─────────────────────────────────────────────
# LOAD QUESTIONS
# ─────────────────────────────────────────────

def load_questions(filepath="data/questions.json"):
    """
    Load quiz questions from the JSON file.
    
    Args:
        filepath (str): Path to the questions JSON file
    
    Returns:
        list: List of question dictionaries, or empty list if file not found
    """
    try:
        # Build absolute path relative to this file's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filepath)

        with open(full_path, "r") as f:
            data = json.load(f)
        return data.get("questions", [])

    except FileNotFoundError:
        print(f"Warning: Questions file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print("Warning: Questions file has invalid JSON format.")
        return []


def get_random_questions(num_questions=5):
    """
    Get a random selection of quiz questions.
    
    Args:
        num_questions (int): How many questions to pick (3 to 5 recommended)
    
    Returns:
        list: Randomly selected questions
    """
    all_questions = load_questions()

    if not all_questions:
        return []

    # Pick random questions (or all if fewer than requested)
    count = min(num_questions, len(all_questions))
    selected = random.sample(all_questions, count)

    return selected


# ─────────────────────────────────────────────
# QUIZ EVALUATION
# ─────────────────────────────────────────────

def check_answer(question, user_answer):
    """
    Check if the user's answer is correct.
    
    Args:
        question (dict): Question dictionary with 'answer' key
        user_answer (str): User's selected option letter (e.g., "A", "B", "C", "D")
    
    Returns:
        bool: True if correct, False if wrong
    """
    correct = question.get("answer", "").strip().upper()
    given = user_answer.strip().upper()
    return correct == given


def calculate_score(questions, user_answers):
    """
    Calculate quiz score based on answers.
    
    Args:
        questions (list): List of question dicts
        user_answers (dict): {question_id: selected_answer}
    
    Returns:
        dict: Score breakdown and feedback
    """
    correct_count = 0
    total = len(questions)
    results = []

    for q in questions:
        qid = q["id"]
        user_ans = user_answers.get(qid, "")
        is_correct = check_answer(q, user_ans)

        if is_correct:
            correct_count += 1

        results.append({
            "question": q["question"],
            "your_answer": user_ans,
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    # Calculate percentage
    percentage = (correct_count / total * 100) if total > 0 else 0

    # Rule-based feedback message
    feedback = get_score_feedback(percentage)

    return {
        "score": correct_count,
        "total": total,
        "percentage": round(percentage, 1),
        "results": results,
        "feedback": feedback
    }


def get_score_feedback(percentage):
    """
    Return motivational feedback based on quiz score percentage.
    Uses rule-based IF-ELSE logic.
    
    Args:
        percentage (float): Score percentage (0-100)
    
    Returns:
        str: Feedback message
    """
    if percentage == 100:
        return "🏆 Perfect Score! You're absolutely crushing it! Incredible work!"
    elif percentage >= 80:
        return "🌟 Excellent! You know your material really well! Keep it up!"
    elif percentage >= 60:
        return "👍 Good job! You're on the right track. Review the missed questions."
    elif percentage >= 40:
        return "📝 Fair attempt. Spend more time on the topics you missed."
    else:
        return "💪 Don't get discouraged! Review your notes and try again. You've got this!"


# ─────────────────────────────────────────────
# QUIZ FORMATTING HELPERS
# ─────────────────────────────────────────────

def format_question_for_display(question, question_number):
    """
    Format a question nicely for Streamlit display.
    
    Args:
        question (dict): Question dictionary
        question_number (int): Display number (1, 2, 3...)
    
    Returns:
        str: Formatted question text
    """
    return f"**Question {question_number}: {question['question']}**"


def get_option_labels():
    """Return list of option letters for radio buttons."""
    return ["A", "B", "C", "D"]
# ─────────────────────────────────────────────
# COMPATIBILITY FUNCTIONS (for main.py)
# ─────────────────────────────────────────────

def get_quiz_questions(subject="General", num_questions=5):
    """
    Wrapper to match main.py expectation.
    Ignores subject for now (can improve later).
    """
    questions = get_random_questions(num_questions)

    # Convert format for main.py
    formatted = []
    for q in questions:
        formatted.append({
            "question": q["question"],
            "options": q["options"],
            "answer": q["answer"]
        })

    return formatted


def calculate_score(questions, answers):
    """
    Wrapper to match main.py expected format.
    """
    score = 0
    feedback = []

    for i, q in enumerate(questions):
        user_ans = answers[i]
        correct_ans = q["answer"]

        if user_ans == correct_ans:
            score += 1
            result = "✅ Correct"
        else:
            result = f"❌ Wrong. Correct answer: {correct_ans}"

        feedback.append({
            "question": q["question"],
            "your_answer": user_ans,
            "correct_answer": correct_ans,
            "result": result
        })

    total = len(questions)
    percentage = round((score / total) * 100, 1) if total > 0 else 0

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "feedback": feedback
    }


def get_quiz_result_message(score_pct):
    """Wrapper for feedback message."""
    return get_score_feedback(score_pct)