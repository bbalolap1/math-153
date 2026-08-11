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
from datetime import UTC, datetime

import streamlit as st

from math153_tutor.assessment import (
    assessment_choices,
    assessment_presets,
    build_assessment,
    complete_assessment,
    grade_question,
    should_use_multiple_choice,
)
from math153_tutor.complexity import normalized_prompt_structure
from math153_tutor.course_content import COURSE_UNITS, MATH153_COURSE, PROBLEM_FAMILY_INDEX, sections_for_unit
from math153_tutor.math_display import answer_to_latex, display_choices, prompt_parts
from math153_tutor.mastery import assessment_evidence_status
from math153_tutor.models import PracticeAttempt, PracticeProblem
from math153_tutor.paths import learner_data_root
from math153_tutor.practice_catalog import generate_practice_problem
from math153_tutor.solution_detail import teaching_solution
from math153_tutor.storage import LearningRecordRepository, PracticeAttemptRepository
from math153_tutor.validation import validate_practice_answer
from math153_tutor.config import DEFAULT_EXAM_COUNT, DEFAULT_QUIZ_COUNT, DEFAULT_TEST_COUNT, QUESTION_COUNT_OPTIONS

st.set_page_config(page_title="Math 153 Method Navigator", page_icon="∑", layout="wide")

DATA_ROOT=learner_data_root()
LEARNING_DB=DATA_ROOT/"learning_records.sqlite3"
PRACTICE_DB=DATA_ROOT/"practice_attempts.sqlite3"
RECENT_ASSESSMENT_WINDOW=8

NAVIGATION=["Dashboard","Course Review","Professor Mode","Quiz","Test","Exam","Mistake Repair","Progress"]


def _style() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1080px; padding-top: 1.5rem;}
        div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.20); padding:.7rem; border-radius:.55rem;}
        .mn-question-text {font-size:1.15rem; line-height:1.7; margin:.35rem 0 .55rem 0;}
        .mn-choice {font-size:1.05rem; line-height:1.55;}
        </style>
        """, unsafe_allow_html=True,
    )


def _sidebar() -> str:
    st.sidebar.title("Math 153")
    page=st.sidebar.radio("Navigate",NAVIGATION,label_visibility="collapsed")
    st.sidebar.divider(); st.sidebar.caption("COURSE")
    for label in ("Foundation","Unit 1 — Chapters 1–2","Unit 2 — Chapter 3","Unit 3 — Chapters 4–5"):
        st.sidebar.write(label)
    return page


def _unit_label(unit_id: str) -> str:
    return next(u.title for u in COURSE_UNITS if u.id==unit_id)


def _render_prompt(prompt: str) -> None:
    for kind,content in prompt_parts(prompt):
        if kind=="math": st.latex(content)
        else: st.markdown(f"<div class='mn-question-text'>{content}</div>",unsafe_allow_html=True)


def _render_answer_widget(problem: PracticeProblem, key: str, *, assessment_mode: bool = False) -> str:
    """
    Assessment mode is click-to-answer by default.  The problem keeps its true
    mathematical answer type internally so validation/review remains exact.
    """
    if problem.answer_type == "multi_select":
        choices=assessment_choices(problem)
        displayed=display_choices(choices,problem.answer_type)
        labels=[f"**{c.letter}.**  ${c.latex}$" for c in displayed]
        selected=st.multiselect("Choose all that apply",labels,key=f"{key}-multi")
        raws=[displayed[labels.index(v)].raw_answer for v in selected]
        return ",".join(raws)

    force_choice = assessment_mode and should_use_multiple_choice(problem)
    choices=assessment_choices(problem,force_multiple_choice=force_choice)
    if choices:
        displayed=display_choices(choices,problem.answer_type)
        labels=[f"**{c.letter}.**  ${c.latex}$" for c in displayed]
        chosen=st.radio("Choose an answer",labels,index=None,key=f"{key}-radio")
        if chosen is None: return ""
        return displayed[labels.index(chosen)].raw_answer

    # Only genuinely open/verbal responses fall back to typing.
    return st.text_area(
        "Answer",
        key=f"{key}-answer",
        height=90,
        placeholder="Type the short wording/explanation requested by the question.",
    )


def _render_solution_expression(expression: str) -> None:
    for kind,content in prompt_parts(expression):
        if kind=="math": st.latex(content)
        else:
            try: st.latex(answer_to_latex(content,"expression"))
            except Exception: st.write(content)


def _show_solution(problem: PracticeProblem) -> None:
    solution=teaching_solution(problem)
    st.markdown("#### Worked solution")
    if solution.recognize: st.markdown(f"**Recognize:** {solution.recognize}")
    if solution.decide: st.markdown(f"**Method:** {solution.decide}")
    if solution.original_rule_or_formula:
        st.markdown("**Rule / formula**"); _render_solution_expression(solution.original_rule_or_formula)
    for i,step in enumerate(solution.execute,1):
        st.markdown(f"**Step {i}: {step.step_title}**")
        if step.why: st.caption(step.why)
        _render_solution_expression(step.after_expression)
    if solution.verify: st.markdown(f"**Check:** {solution.verify}")
    st.markdown("**Correct answer**"); st.latex(answer_to_latex(problem.expected_answer,problem.answer_type))


def _recent_assessment_exclusions() -> tuple[set[str],set[str],set[str]]:
    records=LearningRecordRepository(LEARNING_DB).list_assessments()[:RECENT_ASSESSMENT_WINDOW]
    ids:set[str]=set(); prompts:set[str]=set(); signatures:set[str]=set()
    for record in records:
        for result in record.question_results:
            ids.add(result.problem.problem_id)
            prompts.add(normalized_prompt_structure(result.problem.prompt))
            signatures.add(result.problem.structural_signature)
    return ids,prompts,signatures


def _dashboard() -> None:
    st.title("Math 153"); st.caption("What do you need to work on today?")
    c1,c2,c3=st.columns(3)
    c1.metric("Sections",len(MATH153_COURSE.sections)); c2.metric("Problem families",len(PROBLEM_FAMILY_INDEX)); c3.metric("Units",len(COURSE_UNITS))
    st.subheader("Jump to course")
    cols=st.columns(4)
    for col,unit in zip(cols,COURSE_UNITS,strict=True):
        with col:
            st.markdown(f"### {unit.title}"); st.caption(unit.purpose)
            if st.button("Open course review",key=f"open-{unit.id}",use_container_width=True):
                st.session_state.review_unit=unit.id; st.session_state.page_override="Course Review"; st.rerun()


def _render_sources(refs) -> None:
    if not refs: return
    with st.expander("Source evidence"):
        for ref in refs:
            if hasattr(ref,"document"): st.markdown(f"- `{ref.document}` — {ref.locator} ({ref.role})")
            else: st.markdown(f"- `{ref}`")


def _course_review() -> None:
    st.title("Course Review")
    unit_ids=[u.id for u in COURSE_UNITS]
    default_id=st.session_state.get("review_unit","FOUNDATION")
    unit_id=st.selectbox("Unit",unit_ids,index=unit_ids.index(default_id) if default_id in unit_ids else 0,format_func=_unit_label)
    section=st.selectbox("Section",sections_for_unit(unit_id),format_func=lambda s:f"{s.id} — {s.title}")
    st.markdown(f"## {section.id} — {section.title}"); st.write(section.summary)
    st.markdown("### Learning objectives")
    for item in section.learning_objectives: st.markdown(f"- {item}")
    st.markdown("### Rules")
    for item in section.rules: st.markdown(f"- {item}")
    st.markdown("### Formulas")
    if section.formulas:
        for formula in section.formulas:
            st.markdown(f"**{formula.meaning}**"); st.latex(formula.expression)
            if formula.conditions: st.caption("Conditions: "+"; ".join(formula.conditions))
    else: st.caption("No standalone formula is required for this section.")
    st.markdown("### Procedures")
    for procedure in section.procedures:
        with st.expander(procedure.name):
            st.write(procedure.objective)
            for i,x in enumerate(procedure.steps,1): st.markdown(f"{i}. {x}")
    st.markdown("### Problem families")
    for family in section.problem_families:
        with st.expander(family.title):
            st.markdown("**What to recognize**")
            for item in family.recognition_features: st.markdown(f"- {item}")
            st.markdown("**Common mistakes**")
            for item in family.common_mistakes: st.markdown(f"- {item}")
            _render_sources(family.source_refs)


def _professor_mode() -> None:
    st.title("Professor Mode")
    unit=st.selectbox("Unit",[u.id for u in COURSE_UNITS],format_func=_unit_label,key="prof-unit")
    section=st.selectbox("Section",sections_for_unit(unit),format_func=lambda s:f"{s.id} — {s.title}",key="prof-section")
    fid=st.selectbox("Problem family",[f.id for f in section.problem_families],format_func=lambda x:PROBLEM_FAMILY_INDEX[x].title,key="prof-family")
    if "prof_variant" not in st.session_state: st.session_state.prof_variant=4
    if "prof_seed" not in st.session_state: st.session_state.prof_seed=random.randint(1,10_000_000)
    if st.button("New problem",type="primary"):
        st.session_state.prof_variant+=1; st.session_state.prof_seed+=7919; st.session_state.pop("prof_feedback",None)
    problem=generate_practice_problem(fid,st.session_state.prof_seed,st.session_state.prof_variant)
    _render_prompt(problem.prompt); answer=_render_answer_widget(problem,f"prof-{problem.problem_id}",assessment_mode=True)
    if st.button("Check answer",key=f"prof-submit-{problem.problem_id}",type="primary"):
        result=validate_practice_answer(problem,answer)
        PracticeAttemptRepository(PRACTICE_DB).add(PracticeAttempt(problem_id=problem.problem_id,family_id=problem.family_id,answer=answer,correct=result.correct,answer_type=problem.answer_type,shown_work=""))
        st.session_state.prof_feedback=(result.correct,result.error_code)
    if feedback:=st.session_state.get("prof_feedback"):
        st.success("Correct.") if feedback[0] else st.error("Incorrect.")
        _show_solution(problem)


def _scope_controls(prefix: str):
    unit=st.selectbox("Coverage",["Math 153",*[u.title for u in COURSE_UNITS]],key=f"{prefix}-coverage")
    if unit=="Math 153": return ["Math 153"]
    unit_id=next(u.id for u in COURSE_UNITS if u.title==unit)
    section=st.selectbox("Narrow to section",["Whole unit",*[s.id for s in sections_for_unit(unit_id)]],key=f"{prefix}-section")
    return [unit if section=="Whole unit" else section]


def _assessment_review(kind: str, results) -> None:
    correct=sum(1 for r in results if r.correct); total=len(results)
    st.success(f"{kind} complete: {correct}/{total} ({correct/total:.0%})" if total else f"{kind} complete")
    st.markdown("## Review Answers")
    for i,result in enumerate(results,1):
        problem=result.problem; status="✓ Correct" if result.correct else "✗ Incorrect"
        with st.expander(f"Question {i} — {status}",expanded=not result.correct):
            _render_prompt(problem.prompt)
            st.markdown("**Your answer**")
            st.latex(answer_to_latex(result.selected_answer,problem.answer_type)) if result.selected_answer else st.write("No answer recorded.")
            st.markdown("**Correct answer**"); st.latex(answer_to_latex(problem.expected_answer,problem.answer_type)); _show_solution(problem)
    if st.button("Start another",key=f"{kind}-again"):
        for k in (f"{kind}-questions",f"{kind}-index",f"{kind}-results",f"{kind}-start",f"{kind}-scopes",f"{kind}-saved"):
            st.session_state.pop(k,None)
        st.rerun()


def _assessment_page(kind: str, default_count: int) -> None:
    st.title(kind)
    source_mode=st.selectbox(f"{kind} source pattern",["Custom coverage",*assessment_presets(kind)],key=f"{kind}-preset")
    scopes=_scope_controls(kind) if source_mode=="Custom coverage" else [f"preset:{kind}:{source_mode}"]
    if source_mode!="Custom coverage": st.caption(f"Using the source-supported pattern for **{source_mode}**.")
    count=st.selectbox("Question count",QUESTION_COUNT_OPTIONS,index=QUESTION_COUNT_OPTIONS.index(default_count),key=f"{kind}-count")
    if st.button(f"Build {kind.lower()}",type="primary",key=f"{kind}-build"):
        seed=random.randint(1,2_000_000_000)
        recent_ids,recent_prompts,recent_signatures=_recent_assessment_exclusions()
        try:
            questions=build_assessment(scopes,count,seed,assessment_type=kind,
                excluded_problem_ids=recent_ids,
                excluded_normalized_prompts=recent_prompts,
                excluded_structural_signatures=recent_signatures)
        except ValueError as exc:
            st.error(str(exc)); st.info("This assessment was not padded with recently seen or number-swapped clones. Broaden the coverage or reduce the question count."); return
        st.session_state[f"{kind}-questions"]=questions; st.session_state[f"{kind}-index"]=0; st.session_state[f"{kind}-results"]=[]
        st.session_state[f"{kind}-start"]=datetime.now(UTC); st.session_state[f"{kind}-scopes"]=scopes; st.session_state[f"{kind}-saved"]=False; st.rerun()
    questions=st.session_state.get(f"{kind}-questions")
    if not questions: return
    index=st.session_state.get(f"{kind}-index",0)
    if index>=len(questions):
        results=st.session_state[f"{kind}-results"]; started=st.session_state[f"{kind}-start"]
        record=complete_assessment(kind,st.session_state.get(f"{kind}-scopes",scopes),results,int((datetime.now(UTC)-started).total_seconds()),started)
        if not st.session_state.get(f"{kind}-saved",False):
            LearningRecordRepository(LEARNING_DB).add_assessment(record); st.session_state[f"{kind}-saved"]=True
        _assessment_review(kind,results); return
    problem=questions[index]; st.progress((index+1)/len(questions)); st.caption(f"Question {index+1} of {len(questions)}")
    _render_prompt(problem.prompt); answer=_render_answer_widget(problem,f"{kind}-{problem.problem_id}",assessment_mode=True)
    if st.button("Submit and continue",key=f"{kind}-submit-{problem.problem_id}",type="primary"):
        if not answer.strip(): st.warning("Select or enter an answer first."); return
        st.session_state[f"{kind}-results"].append(grade_question(problem,answer,shown_work="")); st.session_state[f"{kind}-index"]=index+1; st.rerun()


def _mistake_repair() -> None:
    st.title("Mistake Repair")
    records=LearningRecordRepository(LEARNING_DB).list_assessments()
    wrong=[(record,result) for record in records for result in record.question_results if not result.correct]
    if not wrong: st.info("No incorrect assessment items are stored yet."); return
    labels=[f"{record.assessment_type} · {result.problem.section} · {result.problem.family_title} · {record.completed_at:%Y-%m-%d}" for record,result in wrong]
    selected=st.selectbox("Choose a mistake",range(len(wrong)),format_func=lambda i:labels[i]); _,result=wrong[selected]; problem=result.problem
    _render_prompt(problem.prompt); st.markdown("**Your answer**"); st.latex(answer_to_latex(result.selected_answer,problem.answer_type)) if result.selected_answer else st.write("No answer recorded.")
    st.markdown("**Correct answer**"); st.latex(answer_to_latex(problem.expected_answer,problem.answer_type))
    st.markdown("### Common mistake patterns")
    for item in PROBLEM_FAMILY_INDEX[problem.family_id].common_mistakes: st.markdown(f"- {item}")
    _show_solution(problem)


def _progress() -> None:
    st.title("Progress")
    records=LearningRecordRepository(LEARNING_DB).list_assessments(); status=assessment_evidence_status(records)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Assessment items",status.get("attempts",0)); c2.metric("Accuracy",f"{status.get('accuracy',0):.0%}")
    c3.metric("Distinct correct structures",status.get("distinct_correct_structures",0)); c4.metric("Professor+ correct",status.get("professor_or_higher_correct",0))
    if records:
        rows=[{"type":r.assessment_type,"date":r.completed_at.isoformat(timespec="minutes"),"score":f"{r.correct_count}/{len(r.question_results)}","accuracy":round(r.accuracy,3)} for r in records]
        st.dataframe(rows,use_container_width=True)


def main() -> None:
    _style(); page=st.session_state.pop("page_override",None) or _sidebar()
    handlers={"Dashboard":_dashboard,"Course Review":_course_review,"Professor Mode":_professor_mode,
              "Quiz":lambda:_assessment_page("Quiz",DEFAULT_QUIZ_COUNT),"Test":lambda:_assessment_page("Test",DEFAULT_TEST_COUNT),
              "Exam":lambda:_assessment_page("Exam",DEFAULT_EXAM_COUNT),"Mistake Repair":_mistake_repair,"Progress":_progress}
    handlers[page]()


if __name__=="__main__":
    main()
