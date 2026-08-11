from __future__ import annotations

# Streamlit Cloud executes this file directly by path. In that launch mode Python
# places this package directory on sys.path, not its parent ``src`` directory, so
# absolute imports such as ``from math153_tutor...`` would otherwise fail.
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import random
import time
from datetime import UTC, datetime

import streamlit as st

from math153_tutor.assessment import (
    assessment_blueprint,
    assessment_choices,
    assessment_presets,
    build_assessment,
    complete_assessment,
    grade_question,
)
from math153_tutor.complexity import diversity_report
from math153_tutor.course_content import (
    COURSE_UNITS,
    MATH153_COURSE,
    PROBLEM_FAMILY_INDEX,
    SECTION_INDEX,
    sections_for_unit,
)
from math153_tutor.math_display import answer_to_latex, display_choices, readable_prompt
from math153_tutor.mastery import assessment_evidence_status
from math153_tutor.models import PracticeAttempt, PracticeProblem
from math153_tutor.paths import learner_data_root
from math153_tutor.practice_catalog import (
    FAMILY_SPECS,
    families_for_scope,
    generate_practice_problem,
)
from math153_tutor.solution_detail import teaching_solution
from math153_tutor.storage import LearningRecordRepository, PracticeAttemptRepository
from math153_tutor.validation import validate_practice_answer
from math153_tutor.config import (
    DEFAULT_EXAM_COUNT,
    DEFAULT_QUIZ_COUNT,
    DEFAULT_TEST_COUNT,
    QUESTION_COUNT_OPTIONS,
)


st.set_page_config(page_title="Math 153 Method Navigator", page_icon="∑", layout="wide")

DATA_ROOT=learner_data_root()
LEARNING_DB=DATA_ROOT/"learning_records.sqlite3"
PRACTICE_DB=DATA_ROOT/"practice_attempts.sqlite3"

NAVIGATION=[
    "Dashboard",
    "Course Review",
    "Professor Mode",
    "Quiz",
    "Test",
    "Exam",
    "Mistake Repair",
    "Progress",
]


def _style() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1220px; padding-top: 1.5rem;}
        div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.25); padding:.7rem; border-radius:.55rem;}
        .mn-source {font-size:.85rem; opacity:.75;}
        .mn-question {font-size:1.08rem; line-height:1.65;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sidebar() -> str:
    st.sidebar.title("Math 153")
    st.sidebar.caption("SOURCE-GROUNDED REVIEW")
    page=st.sidebar.radio("Navigate",NAVIGATION,label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.caption("COURSE")
    st.sidebar.write("Foundation")
    st.sidebar.write("Unit 1 — Chapters 1–2")
    st.sidebar.write("Unit 2 — Chapter 3")
    st.sidebar.write("Unit 3 — Chapters 4–5")
    return page


def _unit_label(unit_id: str) -> str:
    return next(u.title for u in COURSE_UNITS if u.id==unit_id)


def _dashboard() -> None:
    st.title("Math 153")
    st.caption("What do you need to work on today?")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Sections",len(MATH153_COURSE.sections))
    c2.metric("Problem families",len(PROBLEM_FAMILY_INDEX))
    c3.metric("Units",len(COURSE_UNITS))
    c4.metric("Assessment max","50 questions")

    st.subheader("Jump to course")
    cols=st.columns(4)
    for col,unit in zip(cols,COURSE_UNITS,strict=True):
        with col:
            st.markdown(f"### {unit.title}")
            st.caption(unit.purpose)
            if st.button("Open course review",key=f"open-{unit.id}",use_container_width=True):
                st.session_state.review_unit=unit.id
                st.session_state.page_override="Course Review"
                st.rerun()

    st.subheader("Study modes")
    a,b,c,d=st.columns(4)
    a.markdown("**Professor Mode**\n\nSource-grounded novel practice with recognition and method-selection pressure.")
    b.markdown("**Quiz**\n\nFocused, shorter assessment from a section or unit.")
    c.markdown("**Test**\n\nBroader coverage with stronger structural and method-selection requirements.")
    d.markdown("**Exam**\n\nCumulative challenge with strict novelty and complexity gates.")


def _render_sources(refs) -> None:
    if not refs: return
    with st.expander("Source evidence"):
        for ref in refs:
            if hasattr(ref,"document"):
                st.markdown(f"- `{ref.document}` — {ref.locator} ({ref.role})")
            else:
                st.markdown(f"- `{ref}`")


def _course_review() -> None:
    st.title("Course Review")
    unit_ids=[u.id for u in COURSE_UNITS]
    default_id=st.session_state.get("review_unit","FOUNDATION")
    unit_id=st.selectbox(
        "Unit",
        unit_ids,
        index=unit_ids.index(default_id) if default_id in unit_ids else 0,
        format_func=_unit_label,
    )
    sections=sections_for_unit(unit_id)
    section=st.selectbox(
        "Section",
        sections,
        format_func=lambda s:f"{s.id} — {s.title}",
    )

    st.markdown(f"## {section.id} — {section.title}")
    st.write(section.summary)

    left,right=st.columns([1,1])
    with left:
        st.markdown("### Learning objectives")
        for item in section.learning_objectives: st.markdown(f"- {item}")
        st.markdown("### Concepts")
        st.write(" · ".join(section.concepts))
        st.markdown("### Vocabulary")
        st.write(" · ".join(section.vocabulary))
    with right:
        st.markdown("### Rules")
        for item in section.rules: st.markdown(f"- {item}")
        st.markdown("### Connections")
        for item in section.connections: st.markdown(f"- {item}")

    st.markdown("### Formulas")
    if section.formulas:
        for formula in section.formulas:
            st.markdown(f"**{formula.meaning}**")
            st.latex(formula.expression)
            if formula.conditions: st.caption("Conditions: "+"; ".join(formula.conditions))
    else:
        st.caption("This section is procedure/concept driven; no standalone formula is required.")

    st.markdown("### Procedures")
    for procedure in section.procedures:
        with st.expander(procedure.name,expanded=False):
            st.write(procedure.objective)
            st.markdown("**Prerequisites**")
            for x in procedure.prerequisites: st.markdown(f"- {x}")
            st.markdown("**Procedure**")
            for i,x in enumerate(procedure.steps,1): st.markdown(f"{i}. {x}")
            if procedure.decision_points:
                st.markdown("**Decision points**")
                for x in procedure.decision_points: st.markdown(f"- {x}")
            if procedure.verification_steps:
                st.markdown("**Verification**")
                for x in procedure.verification_steps: st.markdown(f"- {x}")
            _render_sources(procedure.source_refs)

    st.markdown("### Problem families")
    for family in section.problem_families:
        with st.expander(f"{family.title}  ·  `{family.id}`"):
            st.markdown("**What you must recognize**")
            for x in family.recognition_features: st.markdown(f"- {x}")
            st.markdown("**Required concepts / procedures**")
            st.write("Concepts: "+", ".join(family.required_concepts))
            st.write("Procedures: "+(", ".join(family.required_procedures) if family.required_procedures else "conceptual reasoning"))
            st.markdown("**Professor wording / expected answers**")
            st.write("Instruction verbs: "+", ".join(family.professor_verbs))
            st.write("Answer forms: "+", ".join(family.expected_answer_forms))
            st.markdown("**Structural variations**")
            for x in family.structural_variants: st.markdown(f"- {x}")
            st.markdown("**Common mistakes**")
            for x in family.common_mistakes: st.markdown(f"- {x}")
            if family.verification_methods:
                st.markdown("**Required checks**")
                for x in family.verification_methods: st.markdown(f"- {x}")
            if family.application_contexts:
                st.markdown("**Application contexts**")
                st.write(", ".join(family.application_contexts))
            _render_sources(family.source_refs)

    if section.worked_examples:
        st.markdown("### Worked examples")
        for ex in section.worked_examples:
            with st.expander(ex.prompt):
                for i,step in enumerate(ex.steps,1):
                    st.markdown(f"{i}.")
                    st.latex(step)
                st.markdown("**Answer**")
                st.latex(ex.answer)
                _render_sources(ex.source_refs)
    _render_sources(section.source_refs)


def _family_select(scope: str, key: str) -> str:
    families=families_for_scope(scope)
    return st.selectbox(
        "Problem family",
        families,
        key=key,
        format_func=lambda fid:f"{FAMILY_SPECS[fid].section} — {FAMILY_SPECS[fid].title}",
    )


def _render_answer_widget(problem: PracticeProblem, key: str) -> str:
    choices=assessment_choices(problem)
    if problem.answer_type in {"multiple_choice","multi_select"} or choices:
        displayed=display_choices(choices,problem.answer_type)
        labels=[f"{c.letter}.  {c.raw_answer}" for c in displayed]
        if problem.answer_type=="multi_select":
            selected=st.multiselect("Answer",labels,key=f"{key}-multi")
            raws=[displayed[labels.index(v)].raw_answer for v in selected]
            return ",".join(raws)
        chosen=st.radio("Answer",labels,index=None,key=f"{key}-radio")
        if chosen is None: return ""
        return displayed[labels.index(chosen)].raw_answer
    return st.text_input(
        "Final answer",
        key=f"{key}-answer",
        placeholder="Use the requested answer form.",
    )


def _show_solution(problem: PracticeProblem) -> None:
    solution=teaching_solution(problem)
    st.markdown("### Solution")
    st.markdown(f"**Recognize:** {solution.recognize}")
    st.markdown(f"**First decision:** {solution.decide}")
    st.markdown(f"**Rule / formula:** {solution.original_rule_or_formula}")
    for step in solution.execute:
        st.markdown(f"**{step.step_title}** — {step.why}")
        st.code(step.after_expression,language=None)
    st.markdown(f"**Verify:** {solution.verify}")
    st.markdown("**Final answer**")
    st.latex(answer_to_latex(problem.expected_answer,problem.answer_type))


def _professor_mode() -> None:
    st.title("Professor Mode")
    st.write(
        "Practice is generated from a canonical source-supported family. "
        "Repeated clicks advance structural variants rather than intentionally repeating one numeric template."
    )
    unit=st.selectbox("Unit",[u.id for u in COURSE_UNITS],format_func=_unit_label,key="prof-unit")
    sections=sections_for_unit(unit)
    section=st.selectbox("Section",sections,format_func=lambda s:f"{s.id} — {s.title}",key="prof-section")
    fid=st.selectbox(
        "Problem family",
        [f.id for f in section.problem_families],
        format_func=lambda x:PROBLEM_FAMILY_INDEX[x].title,
        key="prof-family",
    )
    if "prof_variant" not in st.session_state: st.session_state.prof_variant=4
    if "prof_seed" not in st.session_state: st.session_state.prof_seed=random.randint(1,10_000_000)
    if st.button("New problem",type="primary"):
        st.session_state.prof_variant+=1
        st.session_state.prof_seed+=7919
        st.session_state.pop("prof_feedback",None)

    problem=generate_practice_problem(fid,st.session_state.prof_seed,st.session_state.prof_variant)
    st.caption(
        f"{problem.complexity_level.value} · {problem.representation_type} · "
        f"{problem.structural_variant_type} · structural score {problem.complexity_evidence.structural_score}"
    )
    st.markdown(f"<div class='mn-question'>{readable_prompt(problem.prompt)}</div>",unsafe_allow_html=True)
    work=st.text_area(
        "Show your work",
        height=180,
        key=f"prof-work-{problem.problem_id}",
        placeholder="Write the steps you would put on paper. This is saved separately from the final answer.",
    )
    answer=_render_answer_widget(problem,f"prof-{problem.problem_id}")
    if st.button("Check answer",key=f"prof-submit-{problem.problem_id}"):
        result=validate_practice_answer(problem,answer)
        PracticeAttemptRepository(PRACTICE_DB).add(
            PracticeAttempt(
                problem_id=problem.problem_id,family_id=problem.family_id,
                answer=answer,correct=result.correct,answer_type=problem.answer_type,shown_work=work,
            )
        )
        st.session_state.prof_feedback=(result.correct,result.error_code)
    if feedback:=st.session_state.get("prof_feedback"):
        if feedback[0]: st.success("Correct.")
        else: st.error("Not correct yet. Review the structure and your written work.")
        _show_solution(problem)
    _render_sources(problem.source_refs)


def _scope_controls(prefix: str):
    unit=st.selectbox(
        "Coverage",
        ["Math 153",*[u.title for u in COURSE_UNITS]],
        key=f"{prefix}-coverage",
    )
    if unit=="Math 153":
        return ["Math 153"]
    unit_id=next(u.id for u in COURSE_UNITS if u.title==unit)
    section_options=["Whole unit",*[s.id for s in sections_for_unit(unit_id)]]
    section=st.selectbox("Narrow to section",section_options,key=f"{prefix}-section")
    return [unit if section=="Whole unit" else section]


def _assessment_page(kind: str, default_count: int) -> None:
    st.title(kind)
    source_mode=st.selectbox(
        f"{kind} source pattern",
        ["Custom coverage",*assessment_presets(kind)],
        key=f"{kind}-preset",
        help="Presets use the family mix evidenced by the corresponding source assessment/review.",
    )
    if source_mode=="Custom coverage":
        scopes=_scope_controls(kind)
    else:
        scopes=[f"preset:{kind}:{source_mode}"]
        st.caption(f"Using the source-supported family mix for **{source_mode}**.")
    count=st.selectbox(
        "Question count",
        QUESTION_COUNT_OPTIONS,
        index=QUESTION_COUNT_OPTIONS.index(default_count),
        key=f"{kind}-count",
    )
    blueprint=assessment_blueprint(kind,scopes,count)
    with st.expander("Assessment quality requirements"):
        st.json(blueprint.model_dump())
    if st.button(f"Build {kind.lower()}",type="primary",key=f"{kind}-build"):
        seed=random.randint(1,2_000_000_000)
        try:
            questions=build_assessment(scopes,count,seed,assessment_type=kind)
        except ValueError as exc:
            st.error(str(exc))
            st.info(
                "The system did not pad this assessment with number-only duplicates. "
                "Choose fewer questions or broader coverage until additional source-supported constructions are authored."
            )
            return
        st.session_state[f"{kind}-questions"]=questions
        st.session_state[f"{kind}-index"]=0
        st.session_state[f"{kind}-results"]=[]
        st.session_state[f"{kind}-start"]=datetime.now(UTC)
        st.session_state[f"{kind}-scopes"]=scopes
        st.rerun()

    questions=st.session_state.get(f"{kind}-questions")
    if not questions: return
    index=st.session_state.get(f"{kind}-index",0)
    if index>=len(questions):
        results=st.session_state[f"{kind}-results"]
        started=st.session_state[f"{kind}-start"]
        record=complete_assessment(
            kind,st.session_state.get(f"{kind}-scopes",scopes),results,
            int((datetime.now(UTC)-started).total_seconds()),started
        )
        LearningRecordRepository(LEARNING_DB).add_assessment(record)
        st.success(f"{kind} complete: {record.correct_count}/{len(results)} ({record.accuracy:.0%})")
        st.json(diversity_report([r.problem for r in results]))
        if st.button("Start another",key=f"{kind}-again"):
            for k in (f"{kind}-questions",f"{kind}-index",f"{kind}-results",f"{kind}-start",f"{kind}-scopes"):
                st.session_state.pop(k,None)
            st.rerun()
        return

    problem=questions[index]
    st.progress((index+1)/len(questions))
    st.caption(
        f"Question {index+1} of {len(questions)} · {problem.section} · "
        f"{problem.complexity_level.value} · {problem.representation_type}"
    )
    st.markdown(f"<div class='mn-question'>{readable_prompt(problem.prompt)}</div>",unsafe_allow_html=True)
    work=st.text_area(
        "Show your work",
        height=200,
        key=f"{kind}-work-{problem.problem_id}",
        placeholder="Write calculations, substitutions, restrictions, sign chart notes, or reasoning here.",
    )
    answer=_render_answer_widget(problem,f"{kind}-{problem.problem_id}")
    if st.button("Submit and continue",key=f"{kind}-submit-{problem.problem_id}",type="primary"):
        if not answer.strip():
            st.warning("Enter or select an answer first.")
            return
        result=grade_question(problem,answer,shown_work=work)
        st.session_state[f"{kind}-results"].append(result)
        st.session_state[f"{kind}-index"]=index+1
        st.rerun()


def _mistake_repair() -> None:
    st.title("Mistake Repair")
    records=LearningRecordRepository(LEARNING_DB).list_assessments()
    wrong=[
        (record,result)
        for record in records
        for result in record.question_results
        if not result.correct
    ]
    if not wrong:
        st.info("No incorrect assessment items are stored yet.")
        return
    labels=[
        f"{record.assessment_type} · {result.problem.section} · {result.problem.family_title} · {record.completed_at:%Y-%m-%d}"
        for record,result in wrong
    ]
    selected=st.selectbox("Choose a mistake",range(len(wrong)),format_func=lambda i:labels[i])
    record,result=wrong[selected]; problem=result.problem
    st.markdown(readable_prompt(problem.prompt))
    if result.shown_work:
        st.markdown("### Your work")
        st.code(result.shown_work,language=None)
    st.markdown(f"**Your answer:** {result.selected_answer}")
    st.markdown("### Source-specific mistake patterns")
    family=PROBLEM_FAMILY_INDEX[problem.family_id]
    for item in family.common_mistakes: st.markdown(f"- {item}")
    _show_solution(problem)
    st.info(
        "Repair is complete only after you solve a new transfer variant. "
        "Return to Professor Mode and generate the same family at a new structural variant."
    )


def _progress() -> None:
    st.title("Progress")
    records=LearningRecordRepository(LEARNING_DB).list_assessments()
    status=assessment_evidence_status(records)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Assessment items",status.get("attempts",0))
    c2.metric("Accuracy",f"{status.get('accuracy',0):.0%}")
    c3.metric("Distinct correct structures",status.get("distinct_correct_structures",0))
    c4.metric("Professor+ correct",status.get("professor_or_higher_correct",0))
    st.info(status.get("message",""))
    if records:
        rows=[]
        for r in records:
            rows.append({
                "type":r.assessment_type,
                "date":r.completed_at.isoformat(timespec="minutes"),
                "score":f"{r.correct_count}/{len(r.question_results)}",
                "accuracy":round(r.accuracy,3),
            })
        st.dataframe(rows,use_container_width=True)


def main() -> None:
    _style()
    page=st.session_state.pop("page_override",None) or _sidebar()
    handlers={
        "Dashboard":_dashboard,
        "Course Review":_course_review,
        "Professor Mode":_professor_mode,
        "Quiz":lambda:_assessment_page("Quiz",DEFAULT_QUIZ_COUNT),
        "Test":lambda:_assessment_page("Test",DEFAULT_TEST_COUNT),
        "Exam":lambda:_assessment_page("Exam",DEFAULT_EXAM_COUNT),
        "Mistake Repair":_mistake_repair,
        "Progress":_progress,
    }
    handlers[page]()


if __name__=="__main__":
    main()
