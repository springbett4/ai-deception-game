#!/usr/bin/env python3
"""Streamlit front-end for Class D Deception.

Reuses all game logic (students, questions, scoring) from game.py.
This file is purely a UI layer - no student data or scoring rules live here.
"""

import streamlit as st

from game import (
    QUESTION_BANK,
    QUESTIONS_PER_STUDENT,
    STUDENTS,
    evaluate,
)

st.set_page_config(page_title="Class D Deception", page_icon="🏫", layout="centered")

# ---------------------------------------------------------------------------
# Theme - Classroom of the Elite inspired: near-black background, crimson and
# gold accents, a "class ranking" monospace feel for system-y text.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0b0c10 0%, #14141a 100%);
        color: #e8e6e3;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        letter-spacing: 0.03em;
    }
    .coe-title {
        text-align: center;
        color: #d4af37;
        font-family: 'Georgia', serif;
        letter-spacing: 0.15em;
        border-bottom: 2px solid #7a1f2b;
        padding-bottom: 0.4em;
        margin-bottom: 0.6em;
    }
    .coe-card {
        background: #1a1b22;
        border: 1px solid #3a3b46;
        border-left: 4px solid #7a1f2b;
        border-radius: 6px;
        padding: 1.1em 1.4em;
        margin-bottom: 1em;
    }
    .coe-class-tag {
        display: inline-block;
        color: #0b0c10;
        background: #d4af37;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.08em;
        padding: 0.15em 0.6em;
        border-radius: 3px;
        margin-bottom: 0.5em;
    }
    .coe-log {
        background: #101014;
        border: 1px solid #2c2d36;
        border-radius: 6px;
        padding: 0.9em 1.2em;
        margin-bottom: 0.4em;
    }
    .coe-you {
        color: #d4af37;
        font-weight: 600;
    }
    .coe-them {
        color: #e8e6e3;
    }
    .coe-verdict-correct {
        color: #4caf6d;
        font-weight: 700;
    }
    .coe-verdict-wrong {
        color: #c0384a;
        font-weight: 700;
    }
    .coe-tell {
        color: #cfa8ad;
    }
    div.stButton > button {
        background: #1a1b22;
        color: #e8e6e3;
        border: 1px solid #7a1f2b;
        border-radius: 4px;
    }
    div.stButton > button:hover {
        border-color: #d4af37;
        color: #d4af37;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "intro"
        st.session_state.student_idx = 0
        # conversation[name] = list of (question_text, answer_text)
        st.session_state.conversation = {s.name: [] for s in STUDENTS}
        st.session_state.asked_ids = {s.name: [] for s in STUDENTS}
        st.session_state.guesses = {}


def current_student():
    return STUDENTS[st.session_state.student_idx]


def render_header():
    st.markdown('<h1 class="coe-title">CLASS D DECEPTION</h1>', unsafe_allow_html=True)


def render_intro():
    render_header()
    st.markdown(
        """
        <div class="coe-card">
        You've been assigned to figure out which of your classmates are
        genuine, and which are AI plants running on borrowed personalities.
        <br><br>
        Ask each student <b>3 questions</b>. Watch for anything that sounds
        off - canned disclaimers, weirdly perfect structure, or an AI
        slipping out of character entirely.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Begin Interrogation", type="primary"):
        st.session_state.phase = "interrogate"
        st.rerun()


def render_interrogate():
    render_header()
    student = current_student()
    total = len(STUDENTS)
    idx = st.session_state.student_idx + 1

    st.markdown(f"### Student {idx}/{total}: {student.name}")
    st.markdown(
        f"""
        <div class="coe-card">
        <span class="coe-class-tag">{student.class_name}</span><br>
        {student.background}
        </div>
        """,
        unsafe_allow_html=True,
    )

    asked = st.session_state.asked_ids[student.name]
    convo = st.session_state.conversation[student.name]

    for q_text, a_text in convo:
        st.markdown(
            f"""
            <div class="coe-log">
            <span class="coe-you">You:</span> {q_text}<br>
            <span class="coe-them">{student.name}:</span> {a_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    remaining = QUESTIONS_PER_STUDENT - len(asked)

    if remaining > 0:
        st.markdown(f"**Choose a question ({remaining} left to ask {student.name}):**")
        for qid, qtext in QUESTION_BANK:
            if qid in asked:
                continue
            if st.button(qtext, key=f"{student.name}-{qid}"):
                answer = student.answer(qid)
                st.session_state.asked_ids[student.name].append(qid)
                st.session_state.conversation[student.name].append((qtext, answer))
                st.rerun()
    else:
        st.success(f"You've asked {student.name} enough questions.")
        label = "Next Student" if idx < total else "Proceed to Final Verdict"
        if st.button(label, type="primary"):
            if idx < total:
                st.session_state.student_idx += 1
            else:
                st.session_state.phase = "guessing"
            st.rerun()


def render_guessing():
    render_header()
    st.markdown("### Final Verdict")
    st.markdown(
        '<div class="coe-card">You\'ve spoken to all the students. '
        "Now decide: who's really an AI?</div>",
        unsafe_allow_html=True,
    )

    with st.form("guess_form"):
        choices = {}
        for student in STUDENTS:
            choices[student.name] = st.radio(
                f"Is **{student.name}** ({student.class_name}) AI-powered?",
                options=["Not AI", "AI-powered"],
                index=None,
                key=f"guess-{student.name}",
                horizontal=True,
            )
        submitted = st.form_submit_button("Submit Verdict", type="primary")

    if submitted:
        if any(v is None for v in choices.values()):
            st.warning("Give a verdict for every student before submitting.")
        else:
            st.session_state.guesses = {
                name: (v == "AI-powered") for name, v in choices.items()
            }
            st.session_state.phase = "reveal"
            st.rerun()


def render_reveal():
    render_header()
    summary = evaluate(STUDENTS, st.session_state.guesses)

    st.markdown(
        f"## Final score: {summary['correct']}/{summary['total']}"
    )
    st.markdown(f"*{summary['verdict']}*")

    for result in summary["results"]:
        verdict_class = "coe-verdict-correct" if result["correct"] else "coe-verdict-wrong"
        verdict_text = "CORRECT" if result["correct"] else "WRONG"
        actually = "AI-powered" if result["actually_ai"] else "Rule-based (human-like) bot"
        guessed = "AI-powered" if result["guessed_ai"] else "Not AI"

        tells_html = ""
        if result["actually_ai"]:
            tell_items = "".join(f'<li class="coe-tell">{t}</li>' for t in result["tells"])
            tells_html = f"<b>Tells you could have caught:</b><ul>{tell_items}</ul>"
        else:
            tells_html = "<i>No red flags - consistent personality, grounded verifiable details.</i>"

        st.markdown(
            f"""
            <div class="coe-card">
            <h4>{result['name']} <span class="coe-class-tag">{result['class_name']}</span></h4>
            Actually: {actually}<br>
            Your guess: {guessed} &rarr; <span class="{verdict_class}">{verdict_text}</span>
            <br><br>
            {tells_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Play Again"):
        for key in ("phase", "student_idx", "conversation", "asked_ids", "guesses"):
            del st.session_state[key]
        st.rerun()


def main():
    init_state()
    phase = st.session_state.phase
    if phase == "intro":
        render_intro()
    elif phase == "interrogate":
        render_interrogate()
    elif phase == "guessing":
        render_guessing()
    elif phase == "reveal":
        render_reveal()


if __name__ == "__main__":
    main()
