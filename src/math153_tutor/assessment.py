from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import Literal

from .models import AssessmentQuestionResult, AssessmentRecord, PracticeProblem
from .distractors import meaningful_distractors
from .practice_catalog import FAMILY_SPECS, build_session
from .validation import validate_practice_answer


def assessment_choices(problem: PracticeProblem) -> list[str]:
    """Return four deterministic choices including one validator-confirmed answer."""
    candidates = [problem.expected_answer, *problem.choices]
    candidates.extend(item.answer for item in meaningful_distractors(problem))
    candidates.extend(["No solution", "None of these", "0", "1"])
    unique = list(dict.fromkeys(str(value) for value in candidates if str(value).strip()))
    choices = unique[:4]
    if problem.expected_answer not in choices:
        choices[-1] = problem.expected_answer
    random.Random(problem.problem_id).shuffle(choices)
    return choices


def build_assessment(
    scopes: list[str], count: int, seed: int, family_ids: list[str] | None = None
) -> list[PracticeProblem]:
    eligible = [family_id for family_id, spec in FAMILY_SPECS.items() if spec.group in set(scopes)]
    family_ids = eligible if family_ids is None else [item for item in family_ids if item in eligible]
    if not family_ids:
        raise ValueError("Choose at least one course scope with available questions.")
    return build_session(family_ids, count, seed)


def grade_question(problem: PracticeProblem, selected_answer: str) -> AssessmentQuestionResult:
    result = validate_practice_answer(problem, selected_answer)
    error_category = next(
        (
            distractor.error_pattern
            for distractor in meaningful_distractors(problem)
            if distractor.answer == selected_answer
        ),
        None,
    )
    return AssessmentQuestionResult(
        problem=problem,
        selected_answer=selected_answer,
        correct=result.correct,
        error_code=result.error_code,
        error_category=None if result.correct else error_category or "unclassified answer error",
    )


def complete_assessment(
    assessment_type: Literal["Quiz", "Test", "Exam"],
    scopes: list[str],
    results: list[AssessmentQuestionResult],
    duration_seconds: int,
) -> AssessmentRecord:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    completed_at = datetime.now(UTC)
    return AssessmentRecord(
        assessment_id=f"{assessment_type.lower()}-{stamp}",
        assessment_type=assessment_type,
        scopes=scopes,
        question_results=results,
        duration_seconds=duration_seconds,
        started_at=completed_at - timedelta(seconds=duration_seconds),
        completed_at=completed_at,
    )
