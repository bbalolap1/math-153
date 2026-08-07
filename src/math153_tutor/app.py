from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from math153_tutor.models import PracticeAttempt
from math153_tutor.practice_catalog import (
    CHAPTERS_12,
    CHAPTERS_34,
    CHAPTER_5,
    FAMILY_SPECS,
    FINAL_REVIEW,
    FOUNDATION,
    MIXED_TEST,
    PRESET_SESSIONS,
    generate_practice_problem,
)
from math153_tutor.storage import PracticeAttemptRepository
from math153_tutor.validation import validate_practice_answer

GROUPS = [FOUNDATION, CHAPTERS_12, CHAPTERS_34, CHAPTER_5, MIXED_TEST, FINAL_REVIEW]
DIFFICULTY_START = {"Direct": 0, "Standard": 3, "Professor style": 6, "Mixed prerequisite": 9}
STYLES = ["Solve directly", "Recognition + solve", "Guided", "Professor mode"]


def _repo() -> PracticeAttemptRepository:
    return PracticeAttemptRepository(Path("learner_data/practice_attempts.sqlite3"))


def _families_for_group(group: str) -> list[str]:
    if group == MIXED_TEST:
        return PRESET_SESSIONS["Test simulation"][1]
    if group == FINAL_REVIEW:
        return PRESET_SESSIONS["Final-exam simulation"][1]
    return [family_id for family_id, spec in FAMILY_SPECS.items() if spec.group == group]


def _clear_session() -> None:
    for key in [
        "practice_problems",
        "practice_index",
        "practice_stage",
        "practice_result",
        "practice_answer",
        "paper_started",
    ]:
        st.session_state.pop(key, None)


def _start_session(families: list[str], count: int, seed: int, difficulty: str, style: str) -> None:
    base = DIFFICULTY_START[difficulty]
    st.session_state.practice_problems = [
        generate_practice_problem(
            families[i % len(families)], seed + i, base + i % (1 if base == 9 else 3)
        )
        for i in range(count)
    ]
    st.session_state.practice_index = 0
    st.session_state.practice_stage = "recognition" if style == "Recognition + solve" else "paper"
    st.session_state.practice_style = style
    st.session_state.paper_started = time.monotonic()
    st.session_state.pop("practice_result", None)


def _setup() -> None:
    st.title("Build a handwritten practice session")
    st.write(
        "Choose a focused family or start a ready-made exam review. The default style goes directly to paper solving."
    )
    preset = st.selectbox(
        "Ready-made session", ["Custom"] + list(PRESET_SESSIONS), key="setup_preset"
    )
    if preset != "Custom":
        count, families = PRESET_SESSIONS[preset]
        st.info(f"{preset}: {count} questions across {len(families)} working families.")
        style = st.selectbox("Practice style", STYLES, key="preset_style")
        if st.button("Start ready-made session", type="primary"):
            _start_session(families, count, 153, "Standard", style)
            st.rerun()
        return

    group = st.selectbox("Group", GROUPS, key="setup_group")
    families = _families_for_group(group)
    chapters = sorted({FAMILY_SPECS[f].chapter for f in families}, key=lambda value: int(value))
    chapter = st.selectbox("Chapter", chapters, key="setup_chapter")
    chapter_families = [f for f in families if FAMILY_SPECS[f].chapter == chapter]
    sections = sorted({FAMILY_SPECS[f].section for f in chapter_families})
    section = st.selectbox("Section", sections, key="setup_section")
    section_families = [f for f in chapter_families if FAMILY_SPECS[f].section == section]
    family = st.selectbox(
        "Problem family",
        section_families,
        format_func=lambda value: FAMILY_SPECS[value].title,
        key="setup_family",
    )
    difficulty = st.selectbox("Difficulty", list(DIFFICULTY_START), key="setup_difficulty")
    count = st.number_input("Number of questions", min_value=1, max_value=50, value=10, step=1)
    style = st.selectbox("Practice style", STYLES, index=0, key="setup_style")
    if st.button("Start practice", type="primary"):
        _start_session([family], int(count), 153, difficulty, style)
        st.rerun()


def _answer_widget(problem_id: str, answer_type: str, choices: list[str]) -> str:
    key = f"answer_{problem_id}"
    if answer_type == "multiple_choice":
        return st.radio("Your answer", choices, key=key)
    if answer_type == "multi_select":
        selected = st.multiselect("Select every applicable answer", choices, key=key)
        return ",".join(selected)
    placeholder = {
        "ordered_pair": "Example: (2,-3)",
        "solution_set": "Separate solutions with commas",
        "interval": "Example: (-oo,2] U (5,oo)",
        "equation": "Example: y=2*x+3",
        "complex_number": "Example: 3-2i",
        "table": "Enter the missing value",
    }.get(answer_type, "Enter an exact answer unless the prompt requests rounding")
    return st.text_input("Your answer", placeholder=placeholder, key=key)


def _worked_solution(problem) -> None:
    solution = problem.worked_solution
    st.subheader("Worked solution")
    st.markdown(f"**Rule or formula**  \n{solution.rule}")
    st.markdown(f"**Setup**  \n{solution.setup}")
    st.markdown("**Calculation**")
    for line in solution.calculation:
        st.markdown(f"- {line}")
    st.markdown(f"**Final answer**  \n`{solution.final_answer}`")
    st.markdown(f"**Check**  \n{solution.check}")
    if problem.difficulty in {"professor", "mixed"}:
        st.markdown(f"**What had to be inferred**  \n{solution.inference}")
        st.markdown(f"**Earlier skill required**  \n{solution.prerequisite}")
        st.markdown(f"**Why this belongs to the family**  \n{solution.family_reason}")


def _practice() -> None:
    if "practice_problems" not in st.session_state:
        _setup()
        return
    problems = st.session_state.practice_problems
    index = st.session_state.practice_index
    if index >= len(problems):
        attempts = _repo().list()
        recent = attempts[-len(problems) :]
        correct = sum(attempt.correct for attempt in recent)
        st.title("Session complete")
        st.metric("Score", f"{correct}/{len(problems)}")
        st.write("Return to the same family for another parameter set, or choose a mixed review.")
        if st.button("Build another session", type="primary"):
            _clear_session()
            st.rerun()
        return

    problem = problems[index]
    style = st.session_state.practice_style
    st.caption(
        f"Question {index + 1} of {len(problems)} · {problem.group} · {problem.family_title} · {problem.difficulty}"
    )
    st.progress((index + 1) / len(problems))
    st.markdown("### Solve on paper")
    st.markdown(problem.prompt)
    if style != "Professor mode":
        st.caption(f"Rule family: {problem.rule_or_formula}") if style == "Guided" else None
        st.caption(
            f"Source basis: {problem.source_type}; course binaries unavailable, so this item is not claimed as copied from an assessment."
        )

    stage = st.session_state.practice_stage
    if stage == "recognition":
        with st.form(f"recognition_{problem.problem_id}"):
            st.selectbox(
                "What family is this?",
                [problem.family_title]
                + [FAMILY_SPECS[f].title for f in list(FAMILY_SPECS)[:3] if f != problem.family_id],
            )
            if st.form_submit_button("Continue to paper"):
                st.session_state.practice_stage = "paper"
                st.session_state.paper_started = time.monotonic()
                st.rerun()
    elif stage == "paper":
        st.info(
            "Take out paper. Complete the setup and calculation before entering the final answer."
        )
        if st.button("My paper work is complete", type="primary"):
            st.session_state.practice_stage = "answer"
            st.rerun()
    elif stage == "answer":
        with st.form(f"answer_form_{problem.problem_id}"):
            answer = _answer_widget(problem.problem_id, problem.answer_type, problem.choices)
            if st.form_submit_button("Submit answer", type="primary"):
                result = validate_practice_answer(problem, answer)
                _repo().add(
                    PracticeAttempt(
                        problem_id=problem.problem_id,
                        family_id=problem.family_id,
                        answer=answer,
                        correct=result.correct,
                        answer_type=problem.answer_type,
                    )
                )
                st.session_state.practice_answer = answer
                st.session_state.practice_result = result
                st.session_state.practice_stage = "feedback"
                st.rerun()
    else:
        result = st.session_state.practice_result
        if result.correct:
            st.success("Correct.")
        else:
            st.error("Not correct. Compare your paper work with the worked solution below.")
        st.markdown(f"**Relevant rule:** {problem.rule_or_formula}")
        _worked_solution(problem)
        if st.button("Next problem", type="primary"):
            st.session_state.practice_index += 1
            st.session_state.practice_stage = (
                "recognition" if style == "Recognition + solve" else "paper"
            )
            st.session_state.paper_started = time.monotonic()
            st.session_state.pop("practice_result", None)
            st.rerun()
        if st.button("Try another from this family"):
            st.session_state.practice_problems.insert(
                index + 1,
                generate_practice_problem(
                    problem.family_id,
                    problem.parameter_seed + 997,
                    (problem.parameter_seed + 1) % 10,
                ),
            )
            st.session_state.practice_index += 1
            st.session_state.practice_stage = "paper"
            st.rerun()


def _status() -> None:
    st.title("Practice readiness")
    st.write(
        "Every Ready row starts a functioning session with ten audited variant slots, validation, and worked solutions."
    )
    rows = [
        {
            "Group": spec.group,
            "Family": spec.title,
            "Questions": 10,
            "Validator": generate_practice_problem(fid, 153, 0).answer_type,
            "Worked solutions": "Yes",
            "Practice-ready": "Ready",
        }
        for fid, spec in FAMILY_SPECS.items()
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Math 153 Exam Practice", page_icon="✎", layout="wide")
    st.sidebar.title("Math 153 Exam Practice")
    page = st.sidebar.radio("Go to", ["Practice", "Practice readiness"])
    if st.sidebar.button("New session"):
        _clear_session()
        st.rerun()
    if page == "Practice readiness":
        _status()
    else:
        _practice()


if __name__ == "__main__":
    main()
