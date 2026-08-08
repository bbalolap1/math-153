from __future__ import annotations

import random
import time
from pathlib import Path

import streamlit as st

from math153_tutor.course_materials import list_course_materials, save_course_material
from math153_tutor.generation import FAMILIES, generate_problem
from math153_tutor.markdown_loader import load_question_family
from math153_tutor.mastery import progress
from math153_tutor.models import ErrorCategory, GeneratedProblem
from math153_tutor.sessions import submit_assessment_attempt
from math153_tutor.storage import AttemptRepository


ROOT = Path(__file__).parents[2]
ATTEMPT_DB = Path("learner_data/attempts.sqlite3")
ADDED_MATERIALS = Path("learner_data/course_materials")

NAVIGATION = ["Dashboard", "Course Review", "Learning Tools", "Quiz / Test / Exam", "Progress"]
COURSES = ["Math 153", "07"]
COURSE_SCOPE = {
    "Foundation": [
        "Real numbers", "Signed arithmetic", "Fractions", "Algebra vocabulary",
        "Order of operations", "Exponent rules", "Equation language", "Calculator entry",
    ],
    "Chapters 1–2": [
        "Linear equations", "Factoring", "Rational expressions", "Radicals",
        "Rational exponents", "Quadratics", "Complex numbers", "Inequalities",
    ],
    "Chapters 3–4": [
        "Coordinate plane", "Slope and lines", "Circles", "Functions", "Domain and range",
        "Composition and inverse", "Transformations", "Polynomial and rational functions",
    ],
    "Chapter 5": [
        "Exponential functions", "Compound interest", "Logarithms", "Log properties",
        "Exponential equations", "Logarithmic equations", "Domain checks",
    ],
}

FAMILY_GROUP = {
    "CH1-LINEAR-EQUATIONS": "Chapters 1–2",
    "CH4-FUNCTION-COMPOSITION": "Chapters 3–4",
    "CH5-EXP-EQUATIONS": "Chapter 5",
    "CH5-LOG-EQUATIONS": "Chapter 5",
}

COURSE_GUIDE = {
    "Foundation": [
        ("Real numbers", "Real numbers contain the numbers you place on the number line. Natural numbers and whole numbers sit inside the integers; integers sit inside the rational numbers; rational and irrational numbers together make the real numbers."),
        ("Signed arithmetic and fractions", "Track the sign separately from the size of the number. For fractions, use a common denominator for addition/subtraction and reduce only after the operation is mathematically valid."),
        ("Algebra language", "A term is a piece separated by addition or subtraction. A factor is multiplied. A coefficient multiplies a variable. An expression has no equality sign; an equation states that two expressions are equal."),
        ("Exponents and order", "Read exponents as repeated multiplication before applying exponent rules. Grouping symbols, exponents, multiplication/division, then addition/subtraction control the order of evaluation."),
    ],
    "Chapters 1–2": [
        ("Equations", "Preserve equality by applying the same reversible operation to both sides. Check the result in the original equation."),
        ("Factoring and rational expressions", "Factoring exposes multiplicative structure. Before cancelling a factor in a rational expression, record values excluded by the original denominator."),
        ("Radicals and rational exponents", "Radicals and fractional exponents are two representations of the same structure. Preserve domain restrictions when an even root is involved."),
        ("Quadratics and inequalities", "Choose a method from the equation's structure—factoring, square-root property, completing the square, or the quadratic formula. Inequalities require extra care when multiplying or dividing by a negative number."),
    ],
    "Chapters 3–4": [
        ("Lines and the coordinate plane", "Slope measures vertical change over horizontal change. Line forms encode the same geometric object in different ways; choose the form that matches the given information."),
        ("Functions", "A function assigns each allowed input exactly one output. Domain and range describe allowed inputs and resulting outputs, while notation such as f(x) names the output produced by x."),
        ("Composition and inverse", "For a composition, evaluate the inner function first. An inverse reverses the input-output relationship and is verified by composition."),
        ("Graph behavior", "Intercepts, turning behavior, domain, range, and end behavior are evidence about a function. Read them from both algebraic and graphical representations."),
    ],
    "Chapter 5": [
        ("Exponentials", "Exponential functions model repeated multiplication. A growth factor is 1+r and a decay factor is 1-r when r is written as a decimal."),
        ("Compound interest", "Identify the principal, rate, compounding frequency, and time before selecting a compound-interest or continuous-growth model."),
        ("Logarithms", "A logarithm answers an exponent question. Logarithmic and exponential forms are inverse representations, so converting between them is a core solving move."),
        ("Exponential and logarithmic equations", "Seek a common base when possible; otherwise use logarithms. For logarithmic equations, enforce positive arguments and check proposed answers in the original equation."),
    ],
}


def _style() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 2.4rem; padding-bottom: 4rem;}
        [data-testid="stSidebar"] {background: #f5f5f5;}
        h1, h2, h3 {letter-spacing: -0.02em;}
        .math153-card {border: 1px solid #d9d9d9; border-radius: 10px; padding: 18px 20px; min-height: 118px; background: white;}
        .math153-eyebrow {font-size: 0.78rem; font-weight: 700; color: #474d57; letter-spacing: .06em;}
        .math153-muted {color: #5b616b; font-size: .9rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _go(page: str) -> None:
    st.session_state.navigation_page = page
    st.rerun()


def _sidebar() -> str:
    st.sidebar.caption("COURSES")
    st.sidebar.radio("Course", COURSES, key="course_choice", label_visibility="collapsed")
    st.sidebar.caption("NAVIGATE")
    page = st.sidebar.radio("Navigate", NAVIGATION, key="navigation_page", label_visibility="collapsed")
    if st.session_state.course_choice == "07":
        st.sidebar.info("07 is reserved in the approved Figma navigation. Math 153 is the active course content in this build.")
    return page


def _dashboard() -> None:
    st.title("Math 153 — Welcome")
    st.subheader("How can I help you today?")
    query = st.text_input("Search", placeholder="Search a topic, note, example, or skill…")
    jump = st.selectbox("Jump to course section", list(COURSE_SCOPE), key="dashboard_jump")
    if query:
        matches = [
            f"{group} · {topic}" for group, topics in COURSE_SCOPE.items()
            for topic in topics if query.lower() in topic.lower()
        ]
        st.caption("Search results")
        st.write("\n".join(f"- {match}" for match in matches) if matches else "No indexed topic matched yet.")
    if st.button(f"Open {jump}", key="dashboard_open_section"):
        st.session_state.review_group = jump
        _go("Course Review")

    st.markdown("### Choose where you want to go")
    columns = st.columns(3)
    cards = [
        ("Course Review", "Browse the course like a digital textbook: explanations, examples, learning notes, and added material."),
        ("Learning Tools", "Paper Answer Mode, Next-Line Coach, Professor Mode, Quiz Review, and Mistake Repair."),
        ("Quiz / Test / Exam", "Choose scope and assessment type first. Nothing starts until you launch it."),
    ]
    for column, (title, body) in zip(columns, cards, strict=True):
        with column:
            st.markdown(f'<div class="math153-card"><b>{title}</b><br><span class="math153-muted">{body}</span></div>', unsafe_allow_html=True)
            if st.button(f"Open {title}", key=f"dashboard_{title}", use_container_width=True):
                _go(title)


def _family_pages(group: str):
    for path in sorted((ROOT / "content").glob("chapter_*/*.md")):
        family = load_question_family(path)
        if FAMILY_GROUP.get(family.family_id) == group:
            yield family


def _course_review() -> None:
    st.title("Math 153 — Course Review")
    st.write("Read this area like your course binder or textbook. Pick a section to open the content itself.")
    group = st.radio(
        "Course section", list(COURSE_SCOPE), horizontal=True,
        key="review_group",
    )
    st.caption("Topics: " + " • ".join(COURSE_SCOPE[group]))
    st.divider()
    st.markdown(f"## {group}")
    st.caption("Course review guide · system-authored until the referenced professor/source binaries are ingested")
    for title, body in COURSE_GUIDE[group]:
        st.markdown(f"### {title}")
        st.write(body)

    families = list(_family_pages(group))
    if families:
        st.markdown("## Authored family notes already in the repository")
        for family in families:
            with st.expander(f"{family.title} · {family.section}"):
                st.markdown("**Underlying mathematical structure**")
                st.write(family.underlying_mathematical_structure)
                st.markdown("**Hidden prerequisites**")
                st.write(family.hidden_prerequisites)
                st.markdown("**First decision**")
                st.write(family.first_decision)
                st.markdown("**Expected answer presentation**")
                st.write(family.expected_answer_presentation)

    added = [item for item in list_course_materials(ADDED_MATERIALS) if item.section == group]
    if added:
        st.markdown("## Added course material")
        for item in added:
            with st.expander(f"{item.title} · {item.source_type}"):
                st.markdown(item.body)

    if st.button("Add Course Material", type="primary"):
        st.session_state.show_add_material = True
    if st.session_state.get("show_add_material"):
        _add_course_material(group)


def _add_course_material(default_group: str) -> None:
    st.divider()
    st.markdown("## Add Course Material")
    st.write("Paste a lecture transcript, class notes, textbook notes, or other Math 153 material and keep it attached to the section where it belongs.")
    with st.form("add_course_material"):
        title = st.text_input("Title", placeholder="Lecture transcript — Week 3")
        body = st.text_area("Transcript or notes", height=220, placeholder="Paste lecture transcript, textbook notes, or your own notes…")
        section = st.selectbox("Add to", list(COURSE_SCOPE), index=list(COURSE_SCOPE).index(default_group))
        source_type = st.selectbox("Source type", ["Transcript", "Notes", "Textbook", "Other"])
        submitted = st.form_submit_button("Add to Course Review", type="primary")
    if submitted:
        try:
            save_course_material(
                ADDED_MATERIALS, title=title.strip() or "Untitled course material",
                section=section, source_type=source_type, body=body,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(f"Added to {section}. It will remain visible in Course Review.")
            st.session_state.show_add_material = False
            st.rerun()


def _active_problem() -> GeneratedProblem:
    if "tool_problem" not in st.session_state:
        st.session_state.tool_problem = generate_problem("CH5-EXP-EQUATIONS", 153)
    return st.session_state.tool_problem


def _answer_choices(problem: GeneratedProblem) -> list[str]:
    try:
        value = int(problem.expected_answer)
        candidates = [value, value + 1, value - 1, -value]
        unique = list(dict.fromkeys(candidates))
        candidate = value + 2
        while len(unique) < 4:
            if candidate not in unique:
                unique.append(candidate)
            candidate += 1
        choices = [str(item) for item in unique[:4]]
    except ValueError:
        choices = [problem.expected_answer, "0", "1", "No solution"]
        choices = list(dict.fromkeys(choices))[:4]
    random.Random(problem.parameter_seed).shuffle(choices)
    return choices


def _learning_tools() -> None:
    st.title("Learning Tools")
    st.write("Open a tool when you need help learning or repairing a specific problem. These are separate from taking a new quiz.")
    tools = [
        ("Paper Answer Mode", "Solve by hand, then submit the final result by selection instead of retyping your work."),
        ("Next-Line Coach", "Show one line at a time and get feedback on only the next mathematical move."),
        ("Professor Mode", "Teach the current problem in context and explain why the construction works."),
        ("Quiz Review", "Review completed assessment evidence question by question."),
        ("Mistake Repair", "Diagnose one mistake, reteach the missing rule, then test transfer."),
    ]
    columns = st.columns(2)
    for index, (title, body) in enumerate(tools):
        with columns[index % 2]:
            st.markdown(f'<div class="math153-card"><b>{title}</b><br><span class="math153-muted">{body}</span></div>', unsafe_allow_html=True)
            if st.button(f"Open {title}", key=f"tool_{title}", use_container_width=True):
                st.session_state.tool_view = title
    view = st.session_state.get("tool_view")
    if view:
        st.divider()
        {
            "Paper Answer Mode": _paper_answer_mode,
            "Next-Line Coach": _next_line_coach,
            "Professor Mode": _professor_mode,
            "Quiz Review": _quiz_review,
            "Mistake Repair": _mistake_repair,
        }[view]()


def _paper_answer_mode() -> None:
    problem = _active_problem()
    st.header("Paper Answer Mode")
    st.info("Solve this on paper. You do not need to type your handwritten work back into the app.")
    st.markdown(problem.prompt)
    st.markdown("**Your paper:** recognize the structure → solve → check → select the result you got.")
    answer = st.radio("What answer did you get on paper?", _answer_choices(problem), key="paper_answer_choice")
    if st.button("Submit selected answer", type="primary", key="paper_submit"):
        result = submit_assessment_attempt(AttemptRepository(ATTEMPT_DB), problem, answer, 0)[1]
        if result.correct:
            st.success("Final answer validated.")
        else:
            st.error("Not yet correct. Open Mistake Repair to work only on the weak step.")


def _professor_mode() -> None:
    problem = _active_problem()
    st.header("Professor Mode")
    left, main = st.columns([1, 2])
    with left:
        st.markdown("### Problem in context")
        st.markdown(problem.prompt)
        st.caption("Your unsent quiz answer is not changed while Professor Mode is open.")
    with main:
        st.markdown("### Teach me what this problem is asking")
        st.write("Start with the structure, not the calculator.")
        st.markdown(f"**1 · Recognize** — {problem.correct_recognition}")
        st.markdown(f"**2 · First move** — {problem.correct_first_decision}")
        st.markdown(f"**3 · Prerequisites** — {' • '.join(problem.required_skills)}")
        depth = st.radio("What do you want from me next?", ["Give one hint", "Explain this concept deeper", "Work a parallel example", "Full walkthrough"], horizontal=True)
        if depth:
            st.info(problem.reasoning_checkpoints[min(len(problem.reasoning_checkpoints) - 1, ["Give one hint", "Explain this concept deeper", "Work a parallel example", "Full walkthrough"].index(depth))])
        st.caption("Teaching depth uses the current QuestionFamily/GeneratedProblem. A conversational Professor service is still a specified backend, not yet a finished engine.")


def _next_line_coach() -> None:
    problem = _active_problem()
    st.header("Next-Line Coach")
    st.write("The coach responds to the line you are on. It does not jump ahead and dump the full solution.")
    st.markdown(problem.prompt)
    line = st.text_input("Your next line", placeholder="Enter only the next mathematical line")
    if st.button("Check this line", type="primary", key="check_line"):
        if not line.strip():
            st.warning("Enter one line first.")
        else:
            st.info(f"Next-decision boundary: {problem.correct_first_decision}. I’m stopping there so you still make the next mathematical move.")
    st.caption("Exact symbolic step validation requires the specified StepEngine/NextLineCoach backend. This build preserves the one-line boundary without claiming that engine exists.")


def _quiz_review() -> None:
    st.header("Quiz / Test Review")
    attempts = AttemptRepository(ATTEMPT_DB).list()
    assessment_attempts = [attempt for attempt in attempts if attempt.mode == "assessment"]
    if not assessment_attempts:
        st.info("Complete a quiz question first. Your assessment evidence will appear here question by question.")
        return
    correct = sum(attempt.correct for attempt in assessment_attempts)
    st.metric("Answer accuracy", f"{correct / len(assessment_attempts):.0%}", f"{correct} / {len(assessment_attempts)} correct")
    for index, attempt in enumerate(reversed(assessment_attempts[-10:]), 1):
        with st.expander(f"{'✓' if attempt.correct else '✕'} {FAMILIES.get(attempt.family_id, attempt.family_id)} · {attempt.problem_id}"):
            st.write(f"Your answer: {attempt.final_answer}")
            st.write("Validation: correct" if attempt.correct else "Validation: needs repair")
            if attempt.error_categories:
                st.write("Error category: " + ", ".join(item.value for item in attempt.error_categories))


def _mistake_repair() -> None:
    st.header("Mistake Repair")
    attempts = [attempt for attempt in AttemptRepository(ATTEMPT_DB).list() if not attempt.correct]
    if not attempts:
        st.info("No recorded incorrect attempt is available yet. Missed quiz questions will enter this repair queue.")
        return
    attempt = attempts[-1]
    problem = generate_problem(attempt.family_id, int(attempt.problem_id.rsplit("-", 1)[-1]))
    category = attempt.error_categories[0] if attempt.error_categories else ErrorCategory.ALGEBRA
    st.markdown("### 1 · Diagnose the mistake")
    st.write(f"You submitted **{attempt.final_answer}** for **{FAMILIES[attempt.family_id]}**.")
    st.write(problem.targeted_feedback.get(category, "Recheck the decision that failed."))
    st.markdown("### 2 · Repair only the weak step")
    st.info(problem.correct_first_decision)
    check = st.radio("Which first move matches this family?", problem.first_decision_options, key="repair_check")
    if st.button("Check repair", type="primary", key="repair_submit"):
        if check == problem.correct_first_decision:
            st.success("Repair check passed. Next, prove transfer on a later independent problem.")
        else:
            st.warning(problem.targeted_feedback[ErrorCategory.FIRST_STEP])


def _assessment_launcher() -> None:
    st.title("Quiz / Test / Exam")
    st.write("Choose what you want to take. The assessment does not begin until you press Launch Assessment.")
    if st.session_state.get("assessment_active"):
        _active_assessment()
        return
    assessment_type = st.selectbox("Assessment type", ["Quiz", "Test", "Exam"])
    scope = st.selectbox("Course scope", ["All Math 153"] + list(COURSE_SCOPE))
    st.selectbox("Answer format", ["Multiple choice"], disabled=True)
    length = st.selectbox("Length", [5, 10, 20], format_func=lambda value: f"{value} questions")
    st.caption("Formula questions render with math notation. Graph questions use an interactive coordinate-plane contract rather than code-style coordinate text.")
    if st.button("Launch Assessment", type="primary"):
        families = [family for family in FAMILIES if scope == "All Math 153" or FAMILY_GROUP[family] == scope]
        if not families:
            st.error("No reviewed runtime problem family exists for that scope yet.")
        else:
            st.session_state.assessment_problems = [
                generate_problem(families[index % len(families)], 200 + index)
                for index in range(length)
            ]
            st.session_state.assessment_index = 0
            st.session_state.assessment_started = time.monotonic()
            st.session_state.assessment_active = True
            st.session_state.assessment_type = assessment_type
            st.session_state.assessment_scope = scope
            st.rerun()
    with st.expander("Preview the interactive graph question design"):
        _interactive_graph_demo()


def _active_assessment() -> None:
    problems: list[GeneratedProblem] = st.session_state.assessment_problems
    index = st.session_state.assessment_index
    if index >= len(problems):
        st.session_state.assessment_active = False
        st.success("Assessment complete. Open Learning Tools → Quiz Review to inspect the recorded evidence.")
        return
    problem = problems[index]
    st.caption(f"{st.session_state.assessment_type.upper()} · {st.session_state.assessment_scope} · Question {index + 1} of {len(problems)}")
    st.markdown(f"## {FAMILIES[problem.family_id]}")
    st.markdown(problem.prompt)
    st.caption("Fractions, exponents, radicals, roots, set notation, and symbols are rendered as mathematics—not programming syntax.")
    choice = st.radio("Select the answer you got", _answer_choices(problem), key=f"assessment_answer_{index}")
    if st.button("Submit Answer", type="primary", key=f"assessment_submit_{index}"):
        elapsed = int(time.monotonic() - st.session_state.assessment_started)
        attempt, result = submit_assessment_attempt(AttemptRepository(ATTEMPT_DB), problem, choice, elapsed)
        st.session_state.last_attempt = attempt
        if result.correct:
            st.success("Correct.")
        else:
            st.error("Incorrect. This question is now available in Quiz Review and Mistake Repair.")
        st.session_state.assessment_index += 1
        st.rerun()
    if st.button("Exit assessment", key="exit_assessment"):
        st.session_state.assessment_active = False
        st.rerun()


def _interactive_graph_demo() -> None:
    values = [{"x": x / 10, "y": (x / 10) ** 2 - 4} for x in range(-50, 51)]
    intercepts = [{"x": -2, "y": 0, "kind": "intercept"}, {"x": 2, "y": 0, "kind": "intercept"}]
    spec = {
        "layer": [
            {
                "data": {"values": values},
                "mark": {"type": "line", "color": "#2563eb", "strokeWidth": 3},
                "encoding": {
                    "x": {"field": "x", "type": "quantitative", "scale": {"domain": [-5, 5]}},
                    "y": {"field": "y", "type": "quantitative", "scale": {"domain": [-5, 8]}},
                    "tooltip": [{"field": "x", "type": "quantitative"}, {"field": "y", "type": "quantitative"}],
                },
            },
            {
                "data": {"values": intercepts},
                "params": [{"name": "intercepts", "select": {"type": "point", "on": "click"}}],
                "mark": {"type": "point", "filled": True, "size": 170, "color": "#111827"},
                "encoding": {
                    "x": {"field": "x", "type": "quantitative"},
                    "y": {"field": "y", "type": "quantitative"},
                    "tooltip": [{"field": "x", "type": "quantitative"}, {"field": "y", "type": "quantitative"}],
                },
            },
        ],
        "height": 420,
    }
    st.markdown(r"**Click both x-intercepts of** $y=x^2-4$.")
    st.vega_lite_chart(spec, use_container_width=True)
    st.caption("Hover exposes exact coordinates. The two intercept targets are clickable in the rendered Vega-Lite surface; scored point-selection is the next backend adapter for graph-family questions.")


def _progress_page() -> None:
    st.title("Progress")
    attempts = AttemptRepository(ATTEMPT_DB).list()
    if not attempts:
        st.info("Complete a learning-tool or assessment problem to begin recording progress.")
        return
    overall = progress(attempts)
    columns = st.columns(3)
    for column, label, key in zip(columns, ["Recognition", "First decision", "Answer / procedure"], ["recognition", "first_decision", "procedure"], strict=True):
        column.metric(label, f"{overall[key]:.0%}")
    st.caption("Recognition and first-decision percentages use only attempts that actually collected that evidence. Assessment-only submissions do not fabricate those scores.")
    st.markdown("### By problem family")
    for family_id, title in FAMILIES.items():
        family_attempts = [attempt for attempt in attempts if attempt.family_id == family_id]
        if family_attempts:
            scores = progress(family_attempts)
            st.write(f"**{title}** — answer/procedure {scores['procedure']:.0%} · {len(family_attempts)} attempts")


def main() -> None:
    """Render the Figma-approved dashboard-first Math 153 application shell."""
    st.set_page_config(page_title="Math 153", page_icon="∑", layout="wide")
    _style()
    page = _sidebar()
    {
        "Dashboard": _dashboard,
        "Course Review": _course_review,
        "Learning Tools": _learning_tools,
        "Quiz / Test / Exam": _assessment_launcher,
        "Progress": _progress_page,
    }[page]()


if __name__ == "__main__":
    main()
