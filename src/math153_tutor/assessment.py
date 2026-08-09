from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import Literal

from .models import AssessmentQuestionResult, AssessmentRecord, PracticeProblem
from .distractors import meaningful_distractors
from .practice_catalog import FAMILY_SPECS, generate_practice_problem
from .validation import validate_practice_answer
from .config import validate_question_count
from .complexity import LAYER_VARIANTS, profile_layers


def _unique_problem(
    family_id: str, seed: int, variant: int, seen: set[str]
) -> PracticeProblem:
    """Generate a source-grounded problem whose visible prompt is unique in this set."""
    for offset in range(200):
        problem = generate_practice_problem(family_id, seed + offset * 997, variant)
        signature = " ".join(problem.prompt.split()).casefold()
        if signature not in seen:
            seen.add(signature)
            return problem
    raise ValueError(
        "The selected families do not have enough distinct controlled variations for this count. "
        "Choose more families or a smaller question count."
    )


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
    scopes: list[str],
    count: int,
    seed: int,
    family_ids: list[str] | None = None,
    variant_pool: list[int] | None = None,
    complexity_profile: str | None = None,
) -> list[PracticeProblem]:
    eligible = [family_id for family_id, spec in FAMILY_SPECS.items() if spec.group in set(scopes)]
    family_ids = eligible if family_ids is None else [item for item in family_ids if item in eligible]
    if not family_ids:
        raise ValueError("Choose at least one course scope with available questions.")
    validate_question_count(count)
    if complexity_profile is not None:
        layers = profile_layers(complexity_profile, count)
        variants = [
            LAYER_VARIANTS[layer][index % len(LAYER_VARIANTS[layer])]
            for index, layer in enumerate(layers)
        ]
    else:
        variants = variant_pool or list(range(10))
    if not variants:
        raise ValueError("Choose at least one difficulty layer.")
    seen: set[str] = set()
    return [
        _unique_problem(
            family_ids[index % len(family_ids)],
            seed + index,
            variants[index] if complexity_profile is not None else variants[index % len(variants)],
            seen,
        )
        for index in range(count)
    ]


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
