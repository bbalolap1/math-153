from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from math153_tutor.generation import FAMILIES, generate_problem
from math153_tutor.mastery import progress
from math153_tutor.models import ErrorCategory
from math153_tutor.sessions import submit_attempt
from math153_tutor.storage import AttemptRepository

COURSE_SCOPE = {
    "Foundation / Chapters 1–2": [
        "Real-number operations", "Algebraic expressions", "Linear equations",
        "Factoring", "Rational expressions", "Radicals and rational exponents",
        "Quadratic equations", "Complex numbers", "Absolute value", "Inequalities",
    ],
    "Chapters 3–4": [
        "Coordinate plane", "Distance and midpoint", "Slopes and line equations",
        "Parallel and perpendicular lines", "Graphs", "Domain and range", "Functions",
        "Function notation", "Compositions", "Inverse functions", "Difference quotient",
        "Polynomial and rational graphs",
    ],
    "Chapter 5": [
        "Exponential functions", "Exponential models", "Compound interest",
        "Natural exponential function", "Logarithms", "Logarithm properties",
        "Logarithmic equations", "Exponential equations", "Domain and extraneous checks",
    ],
}

FAMILY_CHAPTER = {
    "CH1-LINEAR-EQUATIONS": "Foundation / Chapters 1–2",
    "CH4-FUNCTION-COMPOSITION": "Chapters 3–4",
    "CH5-EXP-EQUATIONS": "Chapter 5",
    "CH5-LOG-EQUATIONS": "Chapter 5",
}


def _reset_problem(family_id: str) -> None:
    st.session_state.seed = st.session_state.get("seed", 152) + 1
    st.session_state.problem = generate_problem(family_id, st.session_state.seed)
    st.session_state.stage = "recognition"
    st.session_state.started = time.monotonic()
    st.session_state.pop("result", None)


def _sidebar() -> tuple[str, str]:
    st.sidebar.title("Math 153")
    page = st.sidebar.radio(
        "Go to",
        ["Practice Session", "Course Map", "Source Library", "Progress"],
        key="navigation_page",
    )
    chapter = st.sidebar.selectbox("Review group", COURSE_SCOPE, key="navigation_chapter")
    st.sidebar.divider()
    st.sidebar.caption("Training modes")
    st.sidebar.markdown(
        "✅ Handwritten Practice  \n"
        "◻ Foundation Mode  \n◻ Bridge Mode  \n◻ Next-Line Coach  \n"
        "◻ Professor Mode  \n◻ Quiz/Test Builder  \n◻ Final Exam"
    )
    st.sidebar.caption("◻ = specified but not implemented yet")
    return page, chapter


def _course_map() -> None:
    st.title("Course Map")
    st.write("This is the requested course scope—not a claim that every family is implemented.")
    for group, topics in COURSE_SCOPE.items():
        with st.expander(group, expanded=True):
            for topic in topics:
                available = any(
                    FAMILY_CHAPTER[family_id] == group and topic.lower() in title.lower()
                    for family_id, title in FAMILIES.items()
                )
                st.markdown(f"{'✅' if available else '◻'} {topic}")


def _source_library() -> None:
    st.title("Source Library")
    st.warning(
        "The repository contains filename inventories, but not the PDF/image binaries. "
        "Those filenames cannot be opened, copied, or mathematically reviewed from this deployment."
    )
    root = Path(__file__).parents[2]
    for inventory in sorted((root / "data/source_registry").glob("*_inventory.txt")):
        entries = [line for line in inventory.read_text(encoding="utf-8").splitlines() if "." in line]
        with st.expander(f"{inventory.name} — {len(entries)} listed files"):
            st.code("\n".join(entries), language=None)


def _progress_page() -> None:
    st.title("Progress")
    attempts = AttemptRepository("learner_data/attempts.sqlite3").list()
    if not attempts:
        st.info("Complete a practice problem to begin recording progress.")
        return
    for family_id, title in FAMILIES.items():
        scores = progress([attempt for attempt in attempts if attempt.family_id == family_id])
        if any(attempt.family_id == family_id for attempt in attempts):
            st.subheader(title)
            columns = st.columns(3)
            for column, label, key in zip(
                columns,
                ["Recognition", "First decision", "Procedure"],
                ["recognition", "first_decision", "procedure"],
                strict=True,
            ):
                column.metric(label, f"{scores[key]:.0%}")


def _practice(chapter: str) -> None:
    st.title("Handwritten Practice")
    st.caption("Recognize → choose the first decision → solve on paper → submit and diagnose")
    available_families = [
        family_id for family_id in FAMILIES if FAMILY_CHAPTER[family_id] == chapter
    ]
    if not available_families:
        st.error("No reviewed runtime family is available for this group yet.")
        return
    family_id = st.selectbox(
        "Problem family",
        available_families,
        format_func=lambda value: FAMILIES[value],
        disabled=st.session_state.get("stage") not in {None, "complete"},
    )
    if "problem" not in st.session_state:
        _reset_problem(family_id)
    problem = st.session_state.problem
    if problem.family_id != family_id:
        _reset_problem(family_id)
        problem = st.session_state.problem

    st.divider()
    st.markdown("### Problem")
    st.markdown(problem.prompt)
    st.caption("Construction provenance: model inference pending course-source review")

    if st.session_state.stage == "recognition":
        with st.form("recognition_form"):
            recognition = st.radio(
                "What family does this structure belong to?",
                problem.recognition_options,
                key="recognition_widget",
            )
            confidence = st.slider("Recognition confidence", 1, 5, 3, key="confidence_widget")
            if st.form_submit_button("Lock recognition"):
                st.session_state.recognition_answer = recognition
                st.session_state.confidence_answer = confidence
                st.session_state.stage = "decision"
                st.rerun()

    elif st.session_state.stage == "decision":
        with st.form("decision_form"):
            decision = st.radio(
                "What should you do first?",
                problem.first_decision_options,
                key="decision_widget",
            )
            if st.form_submit_button("Lock first decision"):
                st.session_state.decision_answer = decision
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
        with st.form("answer_form"):
            answer = st.text_input(
                "Final answer",
                placeholder="For multiple solutions, separate values with commas",
                key="final_answer_widget",
            )
            uncertain = st.selectbox(
                "Which stage felt most uncertain?",
                ["none"] + [item.value for item in ErrorCategory],
                key="uncertain_stage_widget",
            )
            if st.form_submit_button("Submit answer", type="primary"):
                repository = AttemptRepository(Path("learner_data/attempts.sqlite3"))
                reported = None if uncertain == "none" else ErrorCategory(uncertain)
                attempt, result = submit_attempt(
                    repository, problem, st.session_state.recognition_answer,
                    st.session_state.decision_answer, answer,
                    st.session_state.confidence_answer,
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


def main() -> None:
    """Render navigation and the first complete paper-first learning loop."""
    st.set_page_config(page_title="Math 153", page_icon="✎", layout="wide")
    page, chapter = _sidebar()
    if page == "Course Map":
        _course_map()
    elif page == "Source Library":
        _source_library()
    elif page == "Progress":
        _progress_page()
    else:
        _practice(chapter)


if __name__ == "__main__":
    main()
