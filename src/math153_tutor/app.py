from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from math153_tutor.generation import FAMILIES, generate_problem
from math153_tutor.mastery import progress
from math153_tutor.models import ErrorCategory
from math153_tutor.sessions import submit_attempt
from math153_tutor.storage import AttemptRepository


def _reset_problem(family_id: str) -> None:
    st.session_state.seed = st.session_state.get("seed", 152) + 1
    st.session_state.problem = generate_problem(family_id, st.session_state.seed)
    st.session_state.stage = "recognition"
    st.session_state.started = time.monotonic()
    st.session_state.pop("result", None)


def main() -> None:
    """Render the first complete paper-first learning loop."""
    st.set_page_config(page_title="Math 153 Handwritten Training", page_icon="✎", layout="centered")
    st.title("Math 153 Handwritten Training")
    st.caption("Student solves. Computer coaches and evaluates.")
    family_id = st.selectbox(
        "Review group / problem family",
        FAMILIES,
        format_func=lambda value: FAMILIES[value],
        disabled=st.session_state.get("stage") not in {None, "complete"},
    )
    if "problem" not in st.session_state:
        _reset_problem(family_id)
    problem = st.session_state.problem
    if problem.family_id != family_id and st.session_state.stage == "complete":
        _reset_problem(family_id)
        problem = st.session_state.problem

    st.divider()
    st.markdown("### Problem")
    st.markdown(problem.prompt)
    st.caption("Construction provenance: model inference pending course-source review")

    if st.session_state.stage == "recognition":
        with st.form("recognition"):
            recognition = st.radio("What family does this structure belong to?", problem.recognition_options)
            confidence = st.slider("Recognition confidence", 1, 5, 3)
            if st.form_submit_button("Lock recognition"):
                st.session_state.recognition = recognition
                st.session_state.confidence = confidence
                st.session_state.stage = "decision"
                st.rerun()

    elif st.session_state.stage == "decision":
        with st.form("decision"):
            decision = st.radio("What should you do first?", problem.first_decision_options)
            if st.form_submit_button("Lock first decision"):
                st.session_state.decision = decision
                st.session_state.stage = "paper"
                st.rerun()

    elif st.session_state.stage == "paper":
        st.info("**Take out paper.** Solve the problem by hand. Do not type the final answer until your written work is complete.")
        elapsed = int(time.monotonic() - st.session_state.started)
        st.caption(f"Voluntary paper timer: {elapsed // 60}:{elapsed % 60:02d} (never auto-submits)")
        if st.button("My paper work is complete", type="primary"):
            st.session_state.stage = "answer"
            st.rerun()

    elif st.session_state.stage == "answer":
        with st.form("answer"):
            answer = st.text_input("Final answer", placeholder="For multiple solutions, separate values with commas")
            uncertain = st.selectbox("Which stage felt most uncertain?", ["none"] + [item.value for item in ErrorCategory])
            if st.form_submit_button("Submit answer", type="primary"):
                repository = AttemptRepository(Path("learner_data/attempts.sqlite3"))
                reported = None if uncertain == "none" else ErrorCategory(uncertain)
                attempt, result = submit_attempt(
                    repository, problem, st.session_state.recognition, st.session_state.decision,
                    answer, st.session_state.confidence,
                    int(time.monotonic() - st.session_state.started), reported,
                )
                st.session_state.result = (attempt, result)
                st.session_state.stage = "complete"
                st.rerun()

    else:
        attempt, result = st.session_state.result
        if result.correct:
            st.success("Final answer validated.")
        else:
            st.error("Not yet correct. The full solution remains hidden.")
        if not attempt.recognition_correct:
            st.warning(problem.targeted_feedback[ErrorCategory.RECOGNITION])
        if not attempt.first_decision_correct:
            st.warning(problem.targeted_feedback[ErrorCategory.FIRST_STEP])
        if not result.correct:
            category = ErrorCategory.DOMAIN if problem.critical_checks else ErrorCategory.ALGEBRA
            st.info(problem.targeted_feedback[category])
        st.markdown("#### Skill evidence")
        scores = progress(AttemptRepository("learner_data/attempts.sqlite3").list(problem.family_id))
        cols = st.columns(3)
        for column, label, key in zip(cols, ["Recognition", "First decision", "Procedure"], ["recognition", "first_decision", "procedure"], strict=True):
            column.metric(label, f"{scores[key]:.0%}")
        st.caption("Full mastery is intentionally blocked until varied, delayed, hint-free transfer evidence exists.")
        if st.button("Try a related problem", type="primary"):
            _reset_problem(problem.family_id)
            st.rerun()


if __name__ == "__main__":
    main()
