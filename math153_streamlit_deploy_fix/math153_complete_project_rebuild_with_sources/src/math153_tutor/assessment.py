from __future__ import annotations

import random
from collections import Counter
from datetime import UTC, datetime
from typing import Literal

from .calculation import complete_multiple_choice
from .complexity import diversity_report, normalized_prompt_structure
from .config import validate_question_count
from .distractors import meaningful_distractors
from .models import (
    AssessmentBlueprint,
    AssessmentQuestionResult,
    AssessmentRecord,
    DifficultyLayer,
    PracticeProblem,
)
from .practice_catalog import FAMILY_SPECS, families_for_scope, generate_practice_problem
from .validation import validate_practice_answer


AssessmentType = Literal["Quiz", "Test", "Exam"]

# Assessment UI policy: the internal answer type remains mathematically precise, but
# Quiz/Test/Exam should be click-to-answer whenever the correct answer can be validated.
# Only genuinely open verbal responses stay as text entry.
OPEN_RESPONSE_TYPES = {"text", "table"}


ASSESSMENT_PRESETS: dict[str, dict[str, tuple[str, ...]]] = {
    "Quiz": {
        "Quiz 1 pattern": ("CH1-RADICAL-PRODUCT","CH1-RATIONAL-DIVIDE","CH1-FACTOR-GROUPING","CH1-FACTOR-QUADRATIC"),
        "Quiz 2 pattern": ("CH1-RADICAL-PRODUCT","CH1-RATIONAL-SIMPLIFY","CH1-RATIONAL-COMBINE","CH1-RATIONALIZE-DENOMINATOR"),
        "Quiz 3 pattern": ("CH2-COMPLETING-SQUARE","CH2-COMPLEX-QUOTIENT","CH2-ABS-EQUATIONS","CH2-RATE-MOTION-WORK"),
        "Quiz 4 pattern": ("CH2-ABS-INEQUALITY","CH2-RATIONAL-INEQUALITY","CH3-DISTANCE-MIDPOINT","CH3-PERP-BISECTOR"),
        "Quiz 5 pattern": ("CH3-CIRCLE-CENTER-RADIUS","CH3-LINE-EQUATION","CH3-DOMAIN-FORMULA","CH3-GRAPH-DOMAIN-RANGE-BEHAVIOR"),
        "Quiz 6 pattern": ("CH3-CIRCLE-INTERCEPTS","CH3-FUNCTION-QUOTIENT-DOMAIN","CH3-FUNCTION-COMPOSITION"),
    },
    "Test": {
        "Test 1 pattern": tuple(fid for fid in FAMILY_SPECS if FAMILY_SPECS[fid].group == "Unit 1 — Chapters 1–2"),
        "Unit 2 test pattern": tuple(fid for fid in FAMILY_SPECS if FAMILY_SPECS[fid].group == "Unit 2 — Chapter 3"),
        "Test 3 review pattern": tuple(fid for fid in FAMILY_SPECS if FAMILY_SPECS[fid].group == "Unit 3 — Chapters 4–5"),
    },
    "Exam": {
        "Practice Final Version 1 pattern": tuple(FAMILY_SPECS),
        "Practice Final Version 2 pattern": tuple(FAMILY_SPECS),
        "Practice Final Version 3 pattern": tuple(FAMILY_SPECS),
        "Cumulative final challenge": tuple(FAMILY_SPECS),
    },
}


def assessment_presets(assessment_type: AssessmentType) -> list[str]:
    return list(ASSESSMENT_PRESETS[assessment_type])


def preset_families(assessment_type: AssessmentType, preset: str) -> list[str]:
    return list(ASSESSMENT_PRESETS[assessment_type].get(preset, ()))


def assessment_blueprint(assessment_type: AssessmentType, scopes: list[str], count: int) -> AssessmentBlueprint:
    validate_question_count(count)
    if assessment_type == "Quiz":
        return AssessmentBlueprint(
            assessment_type="Quiz", scopes=scopes, question_count=count,
            min_l4=max(0, count // 5), min_l6=0,
            min_structural_signatures=max(1, int(count * 0.8)),
            min_families=min(count, max(2, count // 3)),
            min_multi_method=max(0, count // 6),
            max_per_family=max(2, (count + 3) // 4), require_no_near_duplicates=True,
        )
    if assessment_type == "Test":
        return AssessmentBlueprint(
            assessment_type="Test", scopes=scopes, question_count=count,
            min_l4=max(2, count // 2), min_l6=max(1, count // 6),
            min_structural_signatures=max(1, int(count * 0.9)),
            min_families=min(count, max(4, count // 2)),
            min_multi_method=max(1, count // 4), max_per_family=3, require_no_near_duplicates=True,
        )
    return AssessmentBlueprint(
        assessment_type="Exam", scopes=scopes, question_count=count,
        min_l4=max(3, count // 2), min_l6=max(2, count // 5),
        min_structural_signatures=count,
        min_families=min(count, max(8, count // 2)),
        min_multi_method=max(2, count // 3), max_per_family=2 if count >= 20 else 3,
        require_no_near_duplicates=True,
    )


def candidate_families(scopes: list[str]) -> list[str]:
    pool: list[str] = []
    for scope in scopes:
        if scope.startswith("preset:"):
            _, kind, preset = scope.split(":", 2)
            pool.extend(preset_families(kind, preset))
        else:
            pool.extend(families_for_scope(scope))
    return list(dict.fromkeys(pool)) or list(FAMILY_SPECS)


def _variant_priority(assessment_type: AssessmentType) -> tuple[int, ...]:
    if assessment_type == "Quiz": return (1, 2, 3, 4, 5, 0, 6, 7)
    if assessment_type == "Test": return (4, 5, 3, 6, 2, 7, 1, 0)
    return (5, 6, 7, 4, 3, 5, 6, 7, 2, 4)


def _candidate_pool(scopes: list[str], count: int, seed: int, assessment_type: AssessmentType) -> list[PracticeProblem]:
    families = candidate_families(scopes)
    rng = random.Random(seed)
    rng.shuffle(families)
    priorities = _variant_priority(assessment_type)
    target = max(count * 14, len(families) * 16)
    candidates: list[PracticeProblem] = []
    for round_index in range(max(16, (target // max(1, len(families))) + 1)):
        for family_index, family in enumerate(families):
            if len(candidates) >= target: break
            base_variant = priorities[round_index % len(priorities)]
            variant = base_variant + round_index
            try:
                candidates.append(generate_practice_problem(
                    family, seed + round_index * 7919 + family_index * 104729, variant,
                ))
            except ValueError:
                continue
    return candidates


def _layer_targets(assessment_type: str, count: int) -> list[DifficultyLayer]:
    if assessment_type == "Quiz":
        pattern=[DifficultyLayer.GUIDED,DifficultyLayer.GUIDED,DifficultyLayer.REPRESENTATION,DifficultyLayer.MIXED,DifficultyLayer.PROFESSOR]
    elif assessment_type == "Test":
        pattern=[DifficultyLayer.REPRESENTATION,DifficultyLayer.MIXED,DifficultyLayer.MIXED,DifficultyLayer.PROFESSOR,DifficultyLayer.PROFESSOR,DifficultyLayer.TIMED]
    else:
        pattern=[DifficultyLayer.MIXED,DifficultyLayer.MIXED,DifficultyLayer.PROFESSOR,DifficultyLayer.PROFESSOR,DifficultyLayer.PROFESSOR,DifficultyLayer.TIMED,DifficultyLayer.TIMED,DifficultyLayer.CUMULATIVE]
    return [pattern[i % len(pattern)] for i in range(count)]


def _select(candidates: list[PracticeProblem], blueprint: AssessmentBlueprint,
            excluded_problem_ids: set[str] | None = None,
            excluded_normalized_prompts: set[str] | None = None,
            excluded_structural_signatures: set[str] | None = None) -> list[PracticeProblem]:
    excluded_problem_ids = excluded_problem_ids or set()
    excluded_normalized_prompts = excluded_normalized_prompts or set()
    excluded_structural_signatures = excluded_structural_signatures or set()
    selected: list[PracticeProblem]=[]
    exact:set[str]=set(); normalized:set[str]=set(); structural:set[str]=set()
    family_counts:Counter[str]=Counter()
    buckets:dict[DifficultyLayer,list[PracticeProblem]]={layer:[] for layer in DifficultyLayer}
    for p in candidates: buckets[p.complexity_level].append(p)
    for bucket in buckets.values():
        bucket.sort(key=lambda p:(p.complexity_evidence.structural_score,p.requires_multiple_methods,p.requires_interpretation),reverse=True)

    def acceptable(problem:PracticeProblem, strict_structure:bool=True)->bool:
        visible=" ".join(problem.prompt.split()).casefold()
        near=normalized_prompt_structure(problem.prompt)
        if problem.problem_id in excluded_problem_ids: return False
        if near in excluded_normalized_prompts: return False
        if problem.structural_signature in excluded_structural_signatures: return False
        if visible in exact or near in normalized: return False
        if strict_structure and problem.structural_signature in structural: return False
        if family_counts[problem.family_id] >= blueprint.max_per_family: return False
        return True

    def take(problem:PracticeProblem)->None:
        selected.append(problem)
        exact.add(" ".join(problem.prompt.split()).casefold())
        normalized.add(normalized_prompt_structure(problem.prompt))
        structural.add(problem.structural_signature)
        family_counts[problem.family_id]+=1

    for target_layer in _layer_targets(blueprint.assessment_type,blueprint.question_count):
        order=sorted(DifficultyLayer,key=lambda layer:abs(int(layer.value[1])-int(target_layer.value[1])))
        chosen=None
        for layer in order:
            chosen=next((p for p in buckets[layer] if acceptable(p,True)),None)
            if chosen is not None: break
        if chosen is not None: take(chosen)

    if len(selected)<blueprint.question_count:
        for problem in candidates:
            if len(selected)>=blueprint.question_count: break
            if acceptable(problem,True): take(problem)

    if len(selected)<blueprint.question_count:
        for problem in candidates:
            if len(selected)>=blueprint.question_count: break
            if acceptable(problem,False): take(problem)

    if len(selected)!=blueprint.question_count:
        raise ValueError(
            f"Could produce only {len(selected)} fresh, non-duplicate questions for requested "
            f"{blueprint.question_count}. Broaden coverage or allow older questions to leave the recent-history window."
        )
    return selected


def _assert_blueprint(problems: list[PracticeProblem], blueprint: AssessmentBlueprint) -> None:
    report = diversity_report(problems)
    failures: list[str] = []
    if report["exact_duplicates"]: failures.append(f"exact duplicates={report['exact_duplicates']}")
    if blueprint.require_no_near_duplicates and report["near_duplicates"]: failures.append(f"near duplicates={report['near_duplicates']}")
    if report["unique_structural_signatures"] < blueprint.min_structural_signatures: failures.append(f"structures={report['unique_structural_signatures']}<{blueprint.min_structural_signatures}")
    if report["family_count"] < blueprint.min_families: failures.append(f"families={report['family_count']}<{blueprint.min_families}")
    if report["l4_or_higher"] < blueprint.min_l4: failures.append(f"L4+={report['l4_or_higher']}<{blueprint.min_l4}")
    if report["l6_or_l7"] < blueprint.min_l6: failures.append(f"L6/L7={report['l6_or_l7']}<{blueprint.min_l6}")
    if report["multi_method"] < blueprint.min_multi_method: failures.append(f"multi-method={report['multi_method']}<{blueprint.min_multi_method}")
    if failures: raise ValueError("Assessment fidelity/complexity gates failed: " + "; ".join(failures))


def build_assessment(scopes: list[str], count: int, seed: int,
                     complexity_profile: str = "Mixed Practice",
                     assessment_type: AssessmentType | None = None,
                     excluded_problem_ids: set[str] | None = None,
                     excluded_normalized_prompts: set[str] | None = None,
                     excluded_structural_signatures: set[str] | None = None) -> list[PracticeProblem]:
    """Build a fresh structurally novel assessment; source questions are grammar exemplars, not literal bank items."""
    if assessment_type is None:
        name = complexity_profile.casefold()
        assessment_type = "Exam" if "final" in name or "exam" in name else "Test" if "test" in name or "professor" in name else "Quiz"
    blueprint = assessment_blueprint(assessment_type, scopes, count)
    candidates = _candidate_pool(scopes, count, seed, assessment_type)
    problems = _select(candidates, blueprint, excluded_problem_ids, excluded_normalized_prompts, excluded_structural_signatures)
    _assert_blueprint(problems, blueprint)
    return problems


def should_use_multiple_choice(problem: PracticeProblem) -> bool:
    """Assessments are click-to-answer unless the source genuinely calls for open verbal entry."""
    if problem.answer_type == "multi_select":
        return False
    return problem.answer_type not in OPEN_RESPONSE_TYPES


def assessment_choices(problem: PracticeProblem, *, force_multiple_choice: bool = False) -> list[str]:
    """Return exactly four unique validated choices when the UI requests choice presentation."""
    use_choice = force_multiple_choice or problem.answer_type == "multiple_choice" or bool(problem.choices)
    if not use_choice:
        return []
    candidates = list(problem.choices)
    candidates.extend(d.answer for d in meaningful_distractors(problem))
    return complete_multiple_choice(problem, candidates, seed=problem.parameter_seed)


def grade_question(problem: PracticeProblem, answer: str, shown_work: str = "") -> AssessmentQuestionResult:
    result = validate_practice_answer(problem, answer)
    return AssessmentQuestionResult(problem=problem,selected_answer=answer,shown_work=shown_work,correct=result.correct,error_code=result.error_code)


def complete_assessment(assessment_type: AssessmentType, scopes: list[str], results: list[AssessmentQuestionResult], duration_seconds: int, started_at: datetime) -> AssessmentRecord:
    blueprint = assessment_blueprint(assessment_type, scopes, len(results)) if results else None
    return AssessmentRecord(
        assessment_id=f"{assessment_type.lower()}-{int(started_at.timestamp())}", assessment_type=assessment_type,
        scopes=scopes, question_results=results, duration_seconds=duration_seconds,
        started_at=started_at, completed_at=datetime.now(UTC), blueprint=blueprint,
    )