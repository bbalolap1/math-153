from __future__ import annotations

import random
from datetime import UTC, datetime

from .models import AssessmentQuestionResult, AssessmentRecord, PracticeProblem
from .practice_catalog import FAMILY_SPECS, build_session
from .validation import validate_practice_answer


def assessment_choices(problem: PracticeProblem) -> list[str]:
    """Return four deterministic choices including one validator-confirmed answer."""
    candidates = [problem.expected_answer, problem.wrong_answer, *problem.choices]
    numeric = None
    try:
        numeric = int(problem.expected_answer)
    except ValueError:
        pass
    if numeric is not None:
        candidates.extend([str(numeric + 1), str(numeric - 1), str(-numeric)])
    candidates.extend(["0", "1", "No solution", "None of these"])
    unique = list(dict.fromkeys(str(value) for value in candidates if str(value).strip()))
    choices = unique[:4]
    if problem.expected_answer not in choices:
        choices[-1] = problem.expected_answer
    random.Random(problem.problem_id).shuffle(choices)
    return choices


def build_assessment(scopes: list[str], count: int, seed: int) -> list[PracticeProblem]:
    family_ids = [
        family_id for family_id, spec in FAMILY_SPECS.items() if spec.group in set(scopes)
    ]
    if not family_ids:
        raise ValueError("Choose at least one course scope with available questions.")
    return build_session(family_ids, count, seed)


def grade_question(problem: PracticeProblem, selected_answer: str) -> AssessmentQuestionResult:
    result = validate_practice_answer(problem, selected_answer)
    return AssessmentQuestionResult(
        problem=problem,
        selected_answer=selected_answer,
        correct=result.correct,
        error_code=result.error_code,
    )


def complete_assessment(
    assessment_type: str,
    scopes: list[str],
    results: list[AssessmentQuestionResult],
    duration_seconds: int,
) -> AssessmentRecord:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return AssessmentRecord(
        assessment_id=f"{assessment_type.lower()}-{stamp}",
        assessment_type=assessment_type,
        scopes=scopes,
        question_results=results,
        duration_seconds=duration_seconds,
    )
