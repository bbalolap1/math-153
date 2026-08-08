from __future__ import annotations

import re
import time

import streamlit as st

from math153_tutor.assessment import (
    assessment_choices,
    build_assessment,
    complete_assessment,
    grade_question,
)
from math153_tutor.course_content import COURSE_LESSONS
from math153_tutor.course_materials import (
    list_course_materials,
    save_course_material,
    search_course_materials,
)
from math153_tutor.corpus import ingest_source_corpus
from math153_tutor.markdown_loader import load_question_family
from math153_tutor.math_display import (
    answer_to_latex,
    display_choices,
    normalize_math_fragment,
    readable_prompt,
)
from math153_tutor.mastery import assessment_evidence_status
from math153_tutor.graph_questions import (
    INTERCEPT_QUESTION,
    GraphPoint,
    validate_graph_points,
)
from math153_tutor.models import PracticeAttempt, PracticeProblem, RepairRecord
from math153_tutor.practice_catalog import (
    CHAPTERS_12,
    CHAPTERS_34,
    CHAPTER_5,
    FAMILY_SPECS,
    FOUNDATION,
    generate_practice_problem,
)
from math153_tutor.paths import content_root, learner_data_root, source_manifest_path, source_root
from math153_tutor.source_manifest import read_manifest
from math153_tutor.storage import (
    LearningRecordRepository,
    PracticeAttemptRepository,
)
from math153_tutor.step_engine import check_step, solution_steps
from math153_tutor.validation import validate_practice_answer


DATA_ROOT = learner_data_root()
ADDED_MATERIALS = DATA_ROOT / "course_materials"
LEARNING_DB = DATA_ROOT / "learning_records.sqlite3"
PRACTICE_DB = DATA_ROOT / "practice_attempts.sqlite3"

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
SCOPE_GROUP = {
    "Foundation": FOUNDATION,
    "Chapters 1–2": CHAPTERS_12,
    "Chapters 3–4": CHAPTERS_34,
    "Chapter 5": CHAPTER_5,
}

FAMILY_GROUP = {
    "CH1-LINEAR-EQUATIONS": "Chapters 1–2",
    "CH4-FUNCTION-COMPOSITION": "Chapters 3–4",
    "CH34-DOMAIN-RADICAL-RATIONAL": "Chapters 3–4",
    "CH5-EXP-EQUATIONS": "Chapter 5",
    "CH5-LOG-EQUATIONS": "Chapter 5",
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
    """Queue navigation for the next rerun instead of mutating an instantiated widget."""
    if page not in NAVIGATION:
        raise ValueError(f"Unknown navigation destination: {page}")
    st.session_state.pending_navigation = page
    st.rerun()


def _navigation_changed() -> None:
    st.session_state.navigation_page = st.session_state.navigation_selector


def _sidebar() -> str:
    if "navigation_page" not in st.session_state:
        st.session_state.navigation_page = "Dashboard"
    if "pending_navigation" in st.session_state:
        # Streamlit forbids changing a widget-backed key after that widget is rendered.
        # This synchronization happens before navigation_selector is instantiated.
        st.session_state.navigation_page = st.session_state.pop("pending_navigation")
        st.session_state.navigation_selector = st.session_state.navigation_page
    st.sidebar.caption("COURSES")
    st.sidebar.radio("Course", COURSES, key="course_choice", label_visibility="collapsed")
    st.sidebar.caption("NAVIGATE")
    st.sidebar.radio(
        "Navigate",
        NAVIGATION,
        key="navigation_selector",
        label_visibility="collapsed",
        on_change=_navigation_changed,
    )
    if st.session_state.course_choice == "07":
        st.sidebar.info("07 is reserved in the approved Figma navigation. Math 153 is the active course content in this build.")
    return st.session_state.navigation_page


def _dashboard() -> None:
    st.title("Math 153 — Welcome")
    st.subheader("How can I help you today?")
    query = st.text_input("Search", placeholder="Search a topic, note, example, or skill…")
    jump = st.selectbox("Jump to course section", list(COURSE_SCOPE), key="dashboard_jump")
    if query:
        matches = [
            (group, topic)
            for group, topics in COURSE_SCOPE.items()
            for topic in topics
            if query.casefold() in topic.casefold()
        ]
        st.caption("Search results")
        if matches:
            for group, topic in matches:
                if st.button(f"{group} · {topic}", key=f"search_{group}_{topic}"):
                    st.session_state.review_group = group
                    st.session_state.review_topic = topic
                    _go("Course Review")
        else:
            st.write("No indexed topic matched yet.")
        material_matches = search_course_materials(list_course_materials(ADDED_MATERIALS), query)
        if material_matches:
            st.caption("Added material results")
            for material in material_matches:
                if st.button(
                    f"{material.section} · {material.title}", key=f"material_{material.source_id}"
                ):
                    st.session_state.review_group = material.section
                    st.session_state.review_material_id = material.source_id
                    _go("Course Review")
    if st.button(f"Open {jump}", key="dashboard_open_section"):
        st.session_state.review_group = jump
        _go("Course Review")

    st.markdown("### Choose where you want to go")
    columns = st.columns(4)
    cards = [
        ("Course Review", "Browse the course like a digital textbook: explanations, examples, learning notes, and added material."),
        ("Learning Tools", "Paper Answer Mode, Next-Line Coach, Professor Mode, Quiz Review, and Mistake Repair."),
        ("Quiz / Test / Exam", "Choose scope and assessment type first. Nothing starts until you launch it."),
        ("Progress", "See completed assessments, real accuracy, weak families, and repaired mistakes."),
    ]
    for column, (title, body) in zip(columns, cards, strict=True):
        with column:
            st.markdown(f'<div class="math153-card"><b>{title}</b><br><span class="math153-muted">{body}</span></div>', unsafe_allow_html=True)
            if st.button(f"Open {title}", key=f"dashboard_{title}", width="stretch"):
                _go(title)


def _family_pages(group: str):
    for path in sorted(content_root().glob("chapter_*/*.md")):
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
    if st.session_state.get("review_topic"):
        st.info(f"Opened from search: {st.session_state.pop('review_topic')}")
    for lesson in COURSE_LESSONS[group]:
        st.markdown(f"### {lesson.title}")
        st.write(lesson.explanation)
        for formula in lesson.formulas:
            st.latex(formula)
        st.markdown("**Worked example**")
        st.latex(lesson.example_prompt)
        for step in lesson.example_steps:
            st.latex(step)
        st.markdown("**Common mistakes**")
        for mistake in lesson.common_mistakes:
            st.markdown(f"- {mistake}")
        st.markdown(f"**Connection:** {lesson.connections}")
        st.caption("Source references: " + " • ".join(lesson.source_refs))

    families = list(_family_pages(group))
    if families:
        st.markdown("## Authored family notes already in the repository")
        for family in families:
            with st.expander(f"{family.title} · {family.section}"):
                st.markdown("**Source map**")
                st.write(" • ".join(family.source_refs))
                st.markdown("**Underlying mathematical structure**")
                st.write(family.underlying_mathematical_structure)
                st.markdown("**Hidden prerequisites**")
                st.write(family.hidden_prerequisites)
                st.markdown("**First decision**")
                st.write(family.first_decision)
                st.markdown("**Expected answer presentation**")
                st.write(family.expected_answer_presentation)
                st.markdown("**Professor traps (model-inferred pending review)**")
                st.write(family.professor_traps)

    added = [item for item in list_course_materials(ADDED_MATERIALS) if item.section == group]
    if added:
        st.markdown("## Added course material")
        for item in added:
            expanded = st.session_state.get("review_material_id") == item.source_id
            with st.expander(f"{item.title} · {item.source_type}", expanded=expanded):
                st.caption(
                    f"{item.topic} · learner-added/unverified · source ID {item.source_id}"
                )
                st.markdown(item.body)
        st.session_state.pop("review_material_id", None)

    with st.expander("What this section can teach and test"):
        catalog_rows = []
        for family_id, spec in FAMILY_SPECS.items():
            if spec.group != SCOPE_GROUP[group]:
                continue
            variants = [generate_practice_problem(family_id, 15300 + index, index) for index in range(10)]
            catalog_rows.append(
                {
                    "Section": spec.section,
                    "Topic": spec.title,
                    "Family ID": family_id,
                    "Layers": ", ".join(layer.value for layer in spec.available_layers),
                    "Representations": ", ".join(sorted({item.representation for item in variants})),
                    "Validator": ", ".join(sorted({item.answer_type for item in variants})),
                    "Prerequisites": ", ".join(spec.skills),
                    "Source grounding": spec.source_grounding,
                }
            )
        st.dataframe(catalog_rows, hide_index=True, width="stretch")

    with st.expander("Source availability"):
        manifest = read_manifest(source_manifest_path())
        present = sum(item.binary_present for item in manifest)
        st.write(f"{len(manifest)} inventoried source filenames · {present} binaries present")
        st.caption(
            "Inventory-only records establish filenames and likely source roles, not mathematical "
            "content or professor verification."
        )

    _source_inspector()

    if st.button("Add Course Material", type="primary"):
        st.session_state.show_add_material = True
    if st.session_state.get("show_add_material"):
        _add_course_material(group)


def _source_inspector() -> None:
    with st.expander("Source Inspector — corpus evidence"):
        sources = ingest_source_corpus(source_root())
        manifest = read_manifest(source_manifest_path())
        if not source_root().is_dir():
            st.error(
                "The authoritative source/ directory is absent from this checkout. The filename "
                "inventory is not a substitute for source content."
            )
            st.metric("Inventoried but unavailable", len(manifest))
            st.dataframe(
                [
                    {
                        "File": item.filename,
                        "Type": item.source_kind,
                        "Extraction": item.extraction_status,
                        "Reason": item.unresolved_items or item.notes,
                    }
                    for item in manifest
                ],
                hide_index=True,
                width="stretch",
            )
            return

        complete = sum(item.manifest.extraction_status == "complete" for item in sources)
        question_count = sum(len(item.questions) for item in sources)
        formula_count = sum(len(item.formulas) for item in sources)
        metrics = st.columns(4)
        metrics[0].metric("Source files", len(sources))
        metrics[1].metric("Bodies read", complete)
        metrics[2].metric("Extracted questions", question_count)
        metrics[3].metric("Extracted formulas", formula_count)
        selected = st.selectbox(
            "Inspect source file",
            [item.manifest.relative_path for item in sources],
            key="source_inspector_file",
        )
        item = next(source for source in sources if source.manifest.relative_path == selected)
        st.json(item.manifest.model_dump(mode="json"))
        st.markdown("#### Extracted topics")
        st.write(item.topics or "No heading-derived topics found.")
        st.markdown("#### Extracted questions")
        st.write(item.questions or "No question blocks detected.")
        st.markdown("#### Extracted formulas")
        for formula in item.formulas:
            st.latex(formula)
        st.markdown("#### Original Markdown body")
        st.code(item.raw_text or "No text body is available.", language="markdown")


def _add_course_material(default_group: str) -> None:
    st.divider()
    st.markdown("## Add Course Material")
    st.write("Paste a lecture transcript, class notes, textbook notes, or other Math 153 material and keep it attached to the section where it belongs.")
    with st.form("add_course_material"):
        title = st.text_input("Title", placeholder="Lecture transcript — Week 3")
        body = st.text_area("Transcript or notes", height=220, placeholder="Paste lecture transcript, textbook notes, or your own notes…")
        section = st.selectbox("Add to", list(COURSE_SCOPE), index=list(COURSE_SCOPE).index(default_group))
        topic = st.text_input("Topic", placeholder="Example: compound interest")
        source_type = st.selectbox("Source type", ["Transcript", "Notes", "Textbook", "Other"])
        submitted = st.form_submit_button("Add to Course Review", type="primary")
    if submitted:
        try:
            save_course_material(
                ADDED_MATERIALS, title=title.strip() or "Untitled course material",
                section=section,
                source_type=source_type,
                body=body,
                topic=topic.strip() or "General",
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(f"Added to {section}. It will remain visible in Course Review.")
            st.session_state.show_add_material = False
            st.rerun()


def _active_practice_problem() -> PracticeProblem:
    if "practice_tool_problem" not in st.session_state:
        st.session_state.practice_tool_problem = generate_practice_problem(
            "CH34-DOMAIN-RADICAL-RATIONAL", 153, 8
        )
    return st.session_state.practice_tool_problem


def _practice_solution(problem: PracticeProblem, mode: str = "full_solution") -> None:
    solution = problem.worked_solution
    if mode == "teaching_solution":
        st.markdown("### Recognition")
        st.write(solution.family_reason)
        st.markdown("### First decision")
        st.write(solution.inference)
    if mode == "answer_only":
        st.markdown("**Final answer**")
        st.latex(r"\boxed{" + answer_to_latex(solution.final_answer, problem.answer_type) + "}")
        return
    st.markdown(f"**Rule:** {solution.rule}")
    st.markdown("**Setup**")
    st.latex(normalize_math_fragment(solution.setup))
    st.markdown("**Worked steps**")
    calculation = solution.calculation if mode != "key_steps" else solution.calculation[:2]
    for number, line in enumerate(calculation, 1):
        st.markdown(f"**Step {number}**")
        st.latex(normalize_math_fragment(line))
    if mode == "key_steps":
        st.caption("Key-steps mode stops before displaying every intermediate checkpoint.")
        return
    st.markdown("### Verify")
    st.write(solution.check)
    st.markdown("**Final answer**")
    st.latex(r"\boxed{" + answer_to_latex(solution.final_answer, problem.answer_type) + "}")


def _render_practice_problem(problem: PracticeProblem) -> None:
    st.markdown(readable_prompt(problem.prompt))
    if problem.family_id != "CH34-QUADRATIC-FUNCTIONS":
        return
    h_text, k_text = problem.expected_answer.strip("()").split(",")
    coefficient = re.search(r"y=([+-]?\d+)", problem.prompt)
    if coefficient is None:
        return
    h, k, a = float(h_text), float(k_text), float(coefficient.group(1))
    values = [
        {"x": h + offset / 10, "y": a * (offset / 10) ** 2 + k}
        for offset in range(-50, 51)
    ]
    spec = {
        "data": {"values": values},
        "mark": {"type": "line", "color": "#2563eb", "strokeWidth": 3},
        "encoding": {
            "x": {
                "field": "x",
                "type": "quantitative",
                "axis": {"title": "x", "grid": True},
            },
            "y": {
                "field": "y",
                "type": "quantitative",
                "axis": {"title": "y", "grid": True},
            },
            "tooltip": [
                {"field": "x", "type": "quantitative", "format": ".2f"},
                {"field": "y", "type": "quantitative", "format": ".2f"},
            ],
        },
        "height": 360,
    }
    st.vega_lite_chart(spec, width="stretch")
    st.caption("Use the plotted coordinates to select the vertex from the answer choices.")


def _readable_answer_radio(
    label: str,
    problem: PracticeProblem,
    choices: list[str],
    *,
    key: str,
    index: int | None = 0,
) -> str | None:
    presentations = display_choices(choices, problem.answer_type)
    st.markdown("**Answer choices**")
    for position, presentation in enumerate(presentations):
        st.markdown(f"**{presentation.letter}.**")
        st.latex(presentation.latex)
    letter_by_answer = {item.raw_answer: item.letter for item in presentations}
    return st.radio(
        label,
        choices,
        format_func=letter_by_answer.__getitem__,
        key=key,
        index=index,
    )


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
            if st.button(f"Open {title}", key=f"tool_{title}", width="stretch"):
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
    problem = _active_practice_problem()
    st.header("Paper Answer Mode")
    st.info("Solve this on paper. You do not need to type your handwritten work back into the app.")
    _render_practice_problem(problem)
    st.caption(
        f"{problem.family_title} · {problem.difficulty_layer.value} · "
        f"source style: {problem.source_type}"
    )
    actions = st.columns(3)
    if actions[0].button("Show hint", key="paper_hint"):
        st.session_state.paper_hint_problem_id = problem.problem_id
    solution_mode = st.selectbox(
        "Solution detail",
        ["full_solution", "answer_only", "key_steps", "teaching_solution"],
        format_func=lambda value: value.replace("_", " ").title(),
        index=0,
        key="paper_solution_mode",
    )
    if actions[1].button("Show solution", key="paper_solution"):
        st.session_state.paper_solution_problem_id = problem.problem_id
    if actions[2].button("New variation", key="paper_variation"):
        variant = int(problem.problem_id.rsplit("-", 1)[-1])
        st.session_state.practice_tool_problem = generate_practice_problem(
            problem.family_id, problem.parameter_seed + 1, variant
        )
        st.session_state.pop("paper_result", None)
        st.session_state.pop("paper_hint_problem_id", None)
        st.session_state.pop("paper_solution_problem_id", None)
        st.rerun()
    if st.session_state.get("paper_hint_problem_id") == problem.problem_id:
        st.markdown("### Hint — recognize, then decide")
        st.write(problem.worked_solution.family_reason)
        st.latex(normalize_math_fragment(problem.worked_solution.setup))
    if st.session_state.get("paper_solution_problem_id") == problem.problem_id:
        st.markdown("### Requested solution")
        _practice_solution(problem, solution_mode)
    st.markdown("**Your paper:** recognize the structure → solve → check → select the result you got.")
    answer = _readable_answer_radio(
        "What answer did you get on paper?",
        problem,
        assessment_choices(problem),
        key=f"paper_answer_choice_{problem.problem_id}",
    )
    if st.button("Submit selected answer", type="primary", key="paper_submit"):
        if answer is None:
            st.warning("Select the answer you reached on paper before submitting.")
            return
        result = validate_practice_answer(problem, answer)
        PracticeAttemptRepository(PRACTICE_DB).add(
            PracticeAttempt(
                problem_id=problem.problem_id,
                family_id=problem.family_id,
                answer=answer,
                correct=result.correct,
                answer_type=problem.answer_type,
            )
        )
        st.session_state.paper_result = result.correct
    if "paper_result" in st.session_state:
        if st.session_state.paper_result:
            st.success("Final answer validated.")
        else:
            st.error("Not yet correct. Compare your result with the validated answer below.")
            st.latex(answer_to_latex(problem.expected_answer, problem.answer_type))
            st.info(problem.worked_solution.check)
        if st.button("Try another paper problem", key="paper_another"):
            variant = int(problem.problem_id.rsplit("-", 1)[-1])
            st.session_state.practice_tool_problem = generate_practice_problem(
                problem.family_id, problem.parameter_seed + 1, variant
            )
            st.session_state.pop("paper_result", None)
            st.session_state.coach_step = 0
            st.rerun()


def _professor_mode() -> None:
    problem = _active_practice_problem()
    st.header("Professor Mode")
    if st.session_state.get("professor_return_to_assessment") and st.button(
        "Return to active assessment"
    ):
        st.session_state.professor_return_to_assessment = False
        _go("Quiz / Test / Exam")
    left, main = st.columns([1, 2])
    with left:
        st.markdown("### Problem in context")
        _render_practice_problem(problem)
        st.caption("Your unsent quiz answer is not changed while Professor Mode is open.")
    with main:
        st.markdown("### Teach me what this problem is asking")
        st.write("Start with the structure, not the calculator.")
        st.markdown(f"**1 · Recognize** — {problem.family_title}")
        st.markdown(f"**2 · Relevant rule** — {problem.worked_solution.rule}")
        st.markdown(f"**3 · Prerequisites** — {' • '.join(problem.required_skills)}")
        depth = st.radio(
            "What do you want from me next?",
            ["Give one hint", "Explain this concept deeper", "Work a parallel example", "Full walkthrough"],
            horizontal=True,
        )
        if depth == "Give one hint":
            st.info("Use this setup, then make only the next mathematical move:")
            st.latex(normalize_math_fragment(problem.worked_solution.setup))
        elif depth == "Explain this concept deeper":
            st.write(problem.worked_solution.family_reason)
            st.write(problem.worked_solution.inference)
        elif depth == "Work a parallel example":
            parallel = generate_practice_problem(
                problem.family_id, problem.parameter_seed + 97, (problem.parameter_seed + 1) % 10
            )
            _render_practice_problem(parallel)
            st.markdown("**Start with**")
            st.latex(normalize_math_fragment(parallel.worked_solution.setup))
            with st.expander("Show the parallel example solution"):
                _practice_solution(parallel)
        else:
            _practice_solution(problem)
        st.caption("This explanation is generated from the model-inferred runtime template; it is not professor-verified source material.")
        display_group = next(
            (label for label, catalog_group in SCOPE_GROUP.items() if catalog_group == problem.group),
            None,
        )
        related = search_course_materials(
            list_course_materials(ADDED_MATERIALS),
            " ".join(problem.required_skills),
            section=display_group,
        )
        if not related and display_group:
            related = search_course_materials(
                list_course_materials(ADDED_MATERIALS), "", section=display_group
            )[:3]
        if related:
            st.markdown("### Related learner material")
            st.caption("These notes are learner-added and unverified, not professor-verified sources.")
            for material in related[:3]:
                with st.expander(f"{material.title} · {material.topic}"):
                    st.markdown(material.body)


def _next_line_coach() -> None:
    problem = _active_practice_problem()
    st.header("Next-Line Coach")
    st.write("The coach responds to the line you are on. It does not jump ahead and dump the full solution.")
    _render_practice_problem(problem)
    steps = solution_steps(problem)
    step_index = st.session_state.get("coach_step", 0)
    if step_index:
        st.markdown("**Accepted work so far**")
        for accepted in steps[:step_index]:
            st.markdown(f"- ${accepted}$")
    line = st.text_input("Your current line", placeholder="Enter only the mathematical line you reached")
    if st.button("Check this line", type="primary", key="check_line"):
        if not line.strip():
            st.warning("Enter one line first.")
        else:
            check = check_step(problem, line, step_index)
            if check.valid:
                st.session_state.coach_step = check.step_index
                if check.next_guidance:
                    st.success("That line is mathematically consistent with this solution path.")
                    st.info(f"Next focus: {check.next_guidance}")
                else:
                    st.success("The solution path is complete. Now verify the final answer.")
            else:
                st.warning(check.explanation)
                st.info(f"Keep the next move bounded to: {check.next_guidance}")
    if st.button("Reset coach", key="coach_reset"):
        st.session_state.coach_step = 0
        st.rerun()
    st.caption("Version 0 checks normalized equations/expressions against the authored worked-solution path and stops at the next line.")


def _quiz_review() -> None:
    st.header("Quiz / Test Review")
    repository = LearningRecordRepository(LEARNING_DB)
    assessments = repository.list_assessments()
    if not assessments:
        st.info("Complete an assessment first. Its questions and explanations will appear here.")
        return
    selected_id = st.selectbox(
        "Completed assessment",
        [record.assessment_id for record in assessments],
        format_func=lambda value: next(
            f"{record.assessment_type} · {record.completed_at:%Y-%m-%d %H:%M} · "
            f"{record.correct_count}/{len(record.question_results)}"
            for record in assessments
            if record.assessment_id == value
        ),
    )
    record = next(item for item in assessments if item.assessment_id == selected_id)
    st.metric(
        "Score",
        f"{record.accuracy:.0%}",
        f"{record.correct_count} / {len(record.question_results)}",
    )
    for index, result in enumerate(record.question_results, 1):
        problem = result.problem
        with st.expander(
            f"{'✓' if result.correct else '✕'} Question {index} · {problem.family_title}",
            expanded=not result.correct,
        ):
            _render_practice_problem(problem)
            answer_columns = st.columns(2)
            with answer_columns[0]:
                st.markdown("**Your answer**")
                st.latex(answer_to_latex(result.selected_answer, problem.answer_type))
            with answer_columns[1]:
                st.markdown("**Correct answer**")
                st.latex(answer_to_latex(problem.expected_answer, problem.answer_type))
            if result.error_category:
                st.write(f"Likely error pattern: **{result.error_category}**")
            _practice_solution(problem)
            if not result.correct and st.button(
                "Repair this mistake", key=f"repair_{record.assessment_id}_{problem.problem_id}"
            ):
                st.session_state.repair_assessment_id = record.assessment_id
                st.session_state.repair_problem_id = problem.problem_id
                st.session_state.tool_view = "Mistake Repair"
                st.rerun()


def _mistake_repair() -> None:
    st.header("Mistake Repair")
    repository = LearningRecordRepository(LEARNING_DB)
    incorrect = [
        (record, result)
        for record in repository.list_assessments()
        for result in record.question_results
        if not result.correct
    ]
    if not incorrect:
        st.info("No recorded incorrect attempt is available yet. Missed quiz questions will enter this repair queue.")
        return
    requested = (
        st.session_state.get("repair_assessment_id"),
        st.session_state.get("repair_problem_id"),
    )
    position = next(
        (
            index
            for index, (record, result) in enumerate(incorrect)
            if (record.assessment_id, result.problem.problem_id) == requested
        ),
        0,
    )
    labels = [
        f"{record.assessment_type} · {result.problem.family_title} · {result.problem.problem_id}"
        for record, result in incorrect
    ]
    selected = st.selectbox(
        "Mistake to repair", range(len(incorrect)), index=position, format_func=labels.__getitem__
    )
    record, result = incorrect[selected]
    problem = result.problem
    st.markdown("### 1 · Diagnose the mistake")
    _render_practice_problem(problem)
    answer_columns = st.columns(2)
    with answer_columns[0]:
        st.markdown("**You submitted**")
        st.latex(answer_to_latex(result.selected_answer, problem.answer_type))
    with answer_columns[1]:
        st.markdown("**Validated answer**")
        st.latex(answer_to_latex(problem.expected_answer, problem.answer_type))
    st.write(f"Likely weak area: {', '.join(problem.required_skills)}.")
    st.markdown("### 2 · Repair only the weak step")
    st.info(problem.worked_solution.rule)
    rule_choices = [
        problem.worked_solution.setup,
        "Convert every value to a decimal before choosing a rule.",
        "Ignore restrictions until after accepting the answer.",
    ]
    st.markdown("**Setup choices**")
    for letter, rule_choice in zip("ABC", rule_choices, strict=True):
        st.markdown(f"**{letter}.**")
        if rule_choice == problem.worked_solution.setup:
            st.latex(normalize_math_fragment(rule_choice))
        else:
            st.write(rule_choice)
    rule_letters = {choice: letter for letter, choice in zip("ABC", rule_choices, strict=True)}
    check = st.radio(
        "Which setup begins the repair?",
        rule_choices,
        format_func=rule_letters.__getitem__,
        key=f"repair_check_{problem.problem_id}",
    )
    if st.button("Check repair", type="primary", key="repair_submit"):
        passed = check == problem.worked_solution.setup
        st.session_state.repair_passed_problem_id = problem.problem_id if passed else None
        if passed:
            st.success("Repair check passed. Now prove transfer on a related problem.")
        else:
            st.warning(f"Return to the authored setup: {problem.worked_solution.setup}")
    if st.session_state.get("repair_passed_problem_id") == problem.problem_id:
        transfer = generate_practice_problem(
            problem.family_id, problem.parameter_seed + 503, (problem.parameter_seed + 1) % 10
        )
        st.markdown("### 3 · Transfer check")
        _render_practice_problem(transfer)
        transfer_answer = _readable_answer_radio(
            "Select the transfer answer",
            transfer,
            assessment_choices(transfer),
            key=f"transfer_{problem.problem_id}",
        )
        if st.button("Submit transfer", type="primary", key="transfer_submit"):
            if transfer_answer is None:
                st.warning("Select a transfer answer before submitting.")
                return
            transfer_correct = validate_practice_answer(transfer, transfer_answer).correct
            repository.add_repair(
                RepairRecord(
                    assessment_id=record.assessment_id,
                    problem_id=problem.problem_id,
                    family_id=problem.family_id,
                    rule_check_correct=True,
                    transfer_problem_id=transfer.problem_id,
                    transfer_correct=transfer_correct,
                )
            )
            if transfer_correct:
                st.success("Transfer confirmed and repair recorded.")
            else:
                st.error("Transfer is not secure yet. The validated answer is shown below.")
                st.latex(answer_to_latex(transfer.expected_answer, transfer.answer_type))
                _practice_solution(transfer)


def _assessment_launcher() -> None:
    st.title("Quiz / Test / Exam")
    st.write("Choose what you want to take. The assessment does not begin until you press Launch Assessment.")
    if st.session_state.get("assessment_complete"):
        _assessment_results()
        return
    if st.session_state.get("assessment_active"):
        _active_assessment()
        return
    assessment_type = st.selectbox("Assessment type", ["Quiz", "Test", "Exam"])
    scopes = st.multiselect(
        "Course scope",
        list(COURSE_SCOPE),
        default=["Chapters 1–2"],
        help="Select one or several course groups.",
    )
    eligible_families = [
        family_id
        for family_id, spec in FAMILY_SPECS.items()
        if spec.group in {SCOPE_GROUP[scope] for scope in scopes}
    ]
    selected_families = st.multiselect(
        "Topics",
        eligible_families,
        default=eligible_families,
        format_func=lambda family_id: (
            f"{FAMILY_SPECS[family_id].section} · {FAMILY_SPECS[family_id].title}"
        ),
        help="Narrow the selected course groups to specific sections or topics.",
    )
    st.selectbox("Answer format", ["Multiple choice"], disabled=True)
    difficulty = st.selectbox(
        "Question progression",
        [
            "Professor / timed / transfer (L5–L7)",
            "Bridge progression (L2–L4)",
            "Full progression (L0–L7)",
            "Foundation / direct (L0–L1)",
        ],
        help=(
            "Professor/transfer questions reduce scaffolding or mix prerequisites. "
            "Use Bridge progression when learning the representation first."
        ),
    )
    variant_pools = {
        "Professor / timed / transfer (L5–L7)": [8, 6, 7, 9],
        "Bridge progression (L2–L4)": [2, 3, 4],
        "Full progression (L0–L7)": list(range(10)),
        "Foundation / direct (L0–L1)": [0, 1],
    }
    length = st.selectbox("Length", [5, 10, 20], format_func=lambda value: f"{value} questions")
    st.caption("Formula questions render with math notation. Graph questions use an interactive coordinate-plane contract rather than code-style coordinate text.")
    if st.button("Launch Assessment", type="primary"):
        try:
            st.session_state.assessment_problems = build_assessment(
                [SCOPE_GROUP[scope] for scope in scopes],
                length,
                seed=200,
                family_ids=selected_families,
                variant_pool=variant_pools[difficulty],
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.assessment_index = 0
            st.session_state.assessment_results = []
            st.session_state.assessment_draft_answers = {}
            st.session_state.assessment_started = time.monotonic()
            st.session_state.assessment_active = True
            st.session_state.assessment_type = assessment_type
            st.session_state.assessment_scopes = scopes
            st.rerun()
    with st.expander("Preview the interactive graph question design"):
        _interactive_graph_demo()


def _active_assessment() -> None:
    problems: list[PracticeProblem] = st.session_state.assessment_problems
    index = st.session_state.assessment_index
    if index >= len(problems):
        record = complete_assessment(
            st.session_state.assessment_type,
            st.session_state.assessment_scopes,
            st.session_state.assessment_results,
            int(time.monotonic() - st.session_state.assessment_started),
        )
        LearningRecordRepository(LEARNING_DB).add_assessment(record)
        st.session_state.completed_assessment_id = record.assessment_id
        st.session_state.assessment_active = False
        st.session_state.assessment_complete = True
        st.rerun()
        return
    problem = problems[index]
    st.caption(
        f"{st.session_state.assessment_type.upper()} · "
        f"{' + '.join(st.session_state.assessment_scopes)} · Question {index + 1} of {len(problems)}"
    )
    st.progress(index / len(problems))
    st.markdown(f"## {problem.family_title}")
    st.caption(
        f"{problem.difficulty_layer.value} · {problem.representation} · "
        f"source style: {problem.source_type}"
    )
    _render_practice_problem(problem)
    st.caption("Fractions, exponents, radicals, roots, set notation, and symbols are rendered as mathematics—not programming syntax.")
    answer_key = f"assessment_answer_{index}"
    draft_answers = st.session_state.get("assessment_draft_answers", {})
    if answer_key not in st.session_state and index in draft_answers:
        st.session_state[answer_key] = draft_answers[index]
    choice = _readable_answer_radio(
        "Select one answer",
        problem,
        assessment_choices(problem),
        key=answer_key,
        index=None,
    )
    if st.button("Submit Answer", type="primary", key=f"assessment_submit_{index}"):
        if choice is None:
            st.warning("Select an answer before continuing.")
        else:
            st.session_state.assessment_results.append(grade_question(problem, choice))
            st.session_state.assessment_index += 1
            st.rerun()
    if st.button("Ask Professor Mode", key=f"assessment_professor_{index}"):
        if choice is not None:
            st.session_state.assessment_draft_answers[index] = choice
        st.session_state.practice_tool_problem = problem
        st.session_state.tool_view = "Professor Mode"
        st.session_state.professor_return_to_assessment = True
        _go("Learning Tools")
    if st.button("Exit assessment", key="exit_assessment"):
        st.session_state.assessment_active = False
        st.rerun()


def _assessment_results() -> None:
    record = LearningRecordRepository(LEARNING_DB).get_assessment(
        st.session_state.completed_assessment_id
    )
    if record is None:
        st.error("The completed assessment could not be reloaded.")
        st.session_state.assessment_complete = False
        return
    st.success("Assessment complete and saved.")
    st.metric(
        "Score",
        f"{record.correct_count}/{len(record.question_results)}",
        f"{record.accuracy:.0%}",
    )
    st.write("Open Quiz Review for every answer, explanation, and repair route.")
    if st.button("Open Quiz Review", type="primary"):
        st.session_state.pending_navigation = "Learning Tools"
        st.session_state.tool_view = "Quiz Review"
        st.session_state.assessment_complete = False
        st.rerun()
    if st.button("Build another assessment"):
        st.session_state.assessment_complete = False
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
    st.latex(INTERCEPT_QUESTION.prompt_latex)
    st.vega_lite_chart(spec, width="stretch")
    selected = st.multiselect(
        "Select the plotted intercept coordinates",
        ["(-2, 0)", "(0, -4)", "(2, 0)", "(0, 4)"],
        key="graph_points",
    )
    if st.button("Check graph selection", key="graph_submit"):
        point_map = {
            "(-2, 0)": GraphPoint(x=-2, y=0),
            "(0, -4)": GraphPoint(x=0, y=-4),
            "(2, 0)": GraphPoint(x=2, y=0),
            "(0, 4)": GraphPoint(x=0, y=4),
        }
        correct = validate_graph_points(
            INTERCEPT_QUESTION, {point_map[coordinate] for coordinate in selected}
        )
        PracticeAttemptRepository(PRACTICE_DB).add(
            PracticeAttempt(
                problem_id=INTERCEPT_QUESTION.problem_id,
                family_id=INTERCEPT_QUESTION.family_id,
                answer=",".join(sorted(selected)),
                correct=correct,
                answer_type="graph_points",
            )
        )
        if correct:
            st.success(r"Correct: $x^2-4=0$ at $x=-2$ and $x=2$.")
        else:
            st.error("Select exactly the two points where the graph crosses the x-axis.")
    st.caption("Hover exposes coordinates; the submitted coordinate selection is validated against the plotted intercepts.")


def _progress_page() -> None:
    st.title("Progress")
    repository = LearningRecordRepository(LEARNING_DB)
    assessments = repository.list_assessments()
    paper_attempts = PracticeAttemptRepository(PRACTICE_DB).list()
    repairs = repository.list_repairs()
    if not assessments and not paper_attempts:
        st.info("Complete a learning-tool or assessment problem to begin recording progress.")
        return
    results = [result for assessment in assessments for result in assessment.question_results]
    total = len(results) + len(paper_attempts)
    correct = sum(result.correct for result in results) + sum(item.correct for item in paper_attempts)
    columns = st.columns(4)
    columns[0].metric("Completed assessments", len(assessments))
    columns[1].metric("Recorded answers", total)
    columns[2].metric("Answer accuracy", f"{correct / total:.0%}" if total else "No evidence")
    columns[3].metric("Repair checks", len(repairs))
    if assessments:
        st.markdown("### Assessment history")
        rows = [
            {
                "Completed": record.completed_at.strftime("%Y-%m-%d %H:%M"),
                "Type": record.assessment_type,
                "Scope": ", ".join(record.scopes),
                "Score": f"{record.correct_count}/{len(record.question_results)}",
                "Accuracy": f"{record.accuracy:.0%}",
            }
            for record in assessments
        ]
        st.dataframe(rows, hide_index=True, width="stretch")
    st.markdown("### Performance by topic")
    family_ids = {result.problem.family_id for result in results} | {
        attempt.family_id for attempt in paper_attempts
    }
    topic_rows = []
    for family_id in sorted(family_ids):
        family_results = [result for result in results if result.problem.family_id == family_id]
        family_paper = [attempt for attempt in paper_attempts if attempt.family_id == family_id]
        family_total = len(family_results) + len(family_paper)
        family_correct = sum(item.correct for item in family_results) + sum(
            item.correct for item in family_paper
        )
        spec = FAMILY_SPECS.get(family_id)
        topic_rows.append(
            {
                "Topic": spec.title if spec else family_id,
                "Group": spec.group if spec else "Learning tool",
                "Attempts": family_total,
                "Accuracy": f"{family_correct / family_total:.0%}",
                "Needs attention": "Yes" if family_correct / family_total < 0.7 else "No",
                "Evidence status": assessment_evidence_status(
                    correct_variants=len(
                        {item.problem.problem_id for item in family_results if item.correct}
                    ),
                    representations=len(
                        {item.problem.representation for item in family_results if item.correct}
                    ),
                    successful_repairs=sum(
                        repair.transfer_correct is True
                        for repair in repairs
                        if repair.family_id == family_id
                    ),
                ),
            }
        )
    st.dataframe(topic_rows, hide_index=True, width="stretch")
    if repairs:
        successful = sum(record.transfer_correct is True for record in repairs)
        st.write(f"**Mistake repair:** {successful} of {len(repairs)} transfer checks confirmed.")
    st.caption("Only submitted answers and completed repair checks are counted; recognition and first-decision evidence are not inferred from assessments.")


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
