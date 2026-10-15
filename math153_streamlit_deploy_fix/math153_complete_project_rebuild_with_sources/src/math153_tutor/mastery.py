from __future__ import annotations

from collections import Counter
from datetime import timedelta

from .models import Attempt, AssessmentRecord


def progress(attempts: list[Attempt]) -> dict[str, float | bool | int]:
    """Mastery requires transfer across distinct evidence, not repetition of one problem."""
    if not attempts:
        return {
            "recognition":0.0,"first_decision":0.0,"procedure":0.0,"mastered":False,
            "distinct_problems":0,"distinct_families":0,"professor_level_successes":0,
        }
    recognition=[a.recognition_correct for a in attempts if a.recognition_correct is not None]
    decisions=[a.first_decision_correct for a in attempts if a.first_decision_correct is not None]
    correct=[a for a in attempts if a.correct]
    distinct_problems={a.problem_id for a in correct}
    distinct_families={a.family_id for a in correct}
    professor_success={
        a.problem_id for a in correct if int(a.layer.value[1]) >= 5
    }
    rec=sum(bool(v) for v in recognition)/len(recognition) if recognition else 0.0
    dec=sum(bool(v) for v in decisions)/len(decisions) if decisions else 0.0
    proc=len(distinct_problems)/len({a.problem_id for a in attempts}) if attempts else 0.0
    mastered=(
        rec>=0.8 and dec>=0.8 and proc>=0.8
        and len(distinct_problems)>=5
        and len(professor_success)>=2
    )
    return {
        "recognition":rec,"first_decision":dec,"procedure":proc,"mastered":mastered,
        "distinct_problems":len(distinct_problems),
        "distinct_families":len(distinct_families),
        "professor_level_successes":len(professor_success),
    }


def assessment_evidence_status(records: list[AssessmentRecord]) -> dict[str, object]:
    if not records:
        return {"attempts":0,"mastered":False,"message":"No assessment evidence yet."}
    results=[r for record in records for r in record.question_results]
    correct=[r for r in results if r.correct]
    structures={r.problem.structural_signature for r in correct}
    families={r.problem.family_id for r in correct}
    high={r.problem.problem_id for r in correct if int(r.problem.complexity_level.value[1])>=5}
    accuracy=len(correct)/len(results) if results else 0.0
    mastered=accuracy>=0.8 and len(structures)>=8 and len(families)>=4 and len(high)>=3
    return {
        "attempts":len(results),
        "accuracy":accuracy,
        "distinct_correct_structures":len(structures),
        "distinct_correct_families":len(families),
        "professor_or_higher_correct":len(high),
        "mastered":mastered,
        "message":(
            "Mastery evidence is structurally diverse."
            if mastered else
            "More correct transfer across distinct structures/representations is required."
        ),
    }
