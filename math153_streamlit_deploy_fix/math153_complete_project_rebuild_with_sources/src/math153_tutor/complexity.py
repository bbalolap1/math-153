from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .course_content import PROBLEM_FAMILY_INDEX, problem_family_by_id
from .models import ComplexityEvidence, DifficultyLayer, PracticeProblem


@dataclass(frozen=True)
class ComplexityProfile:
    name: str
    weights: dict[DifficultyLayer, int]
    min_structural_score: int
    description: str


PROFILES: dict[str, ComplexityProfile] = {
    "Foundation": ComplexityProfile(
        "Foundation",
        {DifficultyLayer.FOUNDATION: 35, DifficultyLayer.DIRECT: 40, DifficultyLayer.GUIDED: 25},
        6,
        "Prerequisite fluency with minimal disguise.",
    ),
    "Direct Practice": ComplexityProfile(
        "Direct Practice",
        {DifficultyLayer.DIRECT: 55, DifficultyLayer.GUIDED: 30, DifficultyLayer.REPRESENTATION: 15},
        7,
        "Direct execution with enough variation to prevent memorizing a single surface form.",
    ),
    "Mixed Practice": ComplexityProfile(
        "Mixed Practice",
        {
            DifficultyLayer.GUIDED: 15, DifficultyLayer.REPRESENTATION: 25,
            DifficultyLayer.MIXED: 35, DifficultyLayer.PROFESSOR: 25,
        },
        11,
        "Mixed representations, prerequisites, and method decisions.",
    ),
    "Professor Mode": ComplexityProfile(
        "Professor Mode",
        {
            DifficultyLayer.REPRESENTATION: 10, DifficultyLayer.MIXED: 25,
            DifficultyLayer.PROFESSOR: 45, DifficultyLayer.TIMED: 20,
        },
        14,
        "Source-faithful professor grammar with hidden recognition and method selection.",
    ),
    "Final Exam Challenge": ComplexityProfile(
        "Final Exam Challenge",
        {
            DifficultyLayer.MIXED: 20, DifficultyLayer.PROFESSOR: 30,
            DifficultyLayer.TIMED: 25, DifficultyLayer.CUMULATIVE: 25,
        },
        16,
        "Cumulative transfer: unfamiliar surface, multiple prerequisites, decisions, and checks.",
    ),
}


# Deterministic variant numbers used by legacy callers. They are deliberately spread
# across structural, representation, and cumulative variants rather than 0..n numeric clones.
LAYER_VARIANTS: dict[DifficultyLayer, tuple[int, ...]] = {
    DifficultyLayer.FOUNDATION: (0, 10, 20),
    DifficultyLayer.DIRECT: (1, 11, 21),
    DifficultyLayer.GUIDED: (2, 12, 22),
    DifficultyLayer.REPRESENTATION: (3, 13, 23),
    DifficultyLayer.MIXED: (4, 14, 24),
    DifficultyLayer.PROFESSOR: (5, 15, 25),
    DifficultyLayer.TIMED: (6, 16, 26),
    DifficultyLayer.CUMULATIVE: (7, 17, 27),
}


def profile_layers(profile_name: str) -> list[DifficultyLayer]:
    profile = PROFILES.get(profile_name, PROFILES["Mixed Practice"])
    layers: list[DifficultyLayer] = []
    for layer, weight in profile.weights.items():
        # Repeating by weight keeps random.choice simple while making the weights explicit.
        layers.extend([layer] * max(1, weight))
    return layers


_NUMERIC = re.compile(r"(?<![A-Za-z])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?![A-Za-z])")
_VAR = re.compile(r"\b[a-zA-Z]\b")
_WHITESPACE = re.compile(r"\s+")


def normalized_prompt_structure(prompt: str) -> str:
    """
    Normalize superficial numeric/variable changes while preserving mathematical and
    instructional structure. This is intentionally stricter than visible-text uniqueness.
    """
    text = prompt.casefold()
    text = _NUMERIC.sub("<n>", text)
    # Preserve common function/log tokens; normalize isolated variable names only.
    text = re.sub(r"\b(?!log\b|ln\b|sin\b|cos\b|tan\b)[a-z]\b", "<v>", text)
    text = re.sub(r"\$|\\left|\\right", "", text)
    text = re.sub(r"\s*([=+\-*/^(),;:{}\[\]])\s*", r"\1", text)
    return _WHITESPACE.sub(" ", text).strip()


def structural_signature(
    family_id: str,
    variant_type: str,
    representation: str,
    prerequisite_count: int,
    decision_count: int,
    *,
    method_count: int = 1,
    answer_form: str = "",
) -> str:
    """Stable signature for novelty gates across an assessment."""
    return "|".join(
        [
            family_id,
            variant_type or "unspecified",
            representation or "symbolic",
            f"p{prerequisite_count}",
            f"d{decision_count}",
            f"m{method_count}",
            answer_form or "answer",
        ]
    )


def family_complexity_evidence(
    family_id: str,
    layer: DifficultyLayer,
    *,
    representation: str = "symbolic",
    variant_index: int = 0,
    solution_steps: int | None = None,
) -> ComplexityEvidence:
    """Derive difficulty from the canonical family, not from an arbitrary label."""
    family = problem_family_by_id(family_id)
    prereq = max(1, len(family.required_concepts))
    methods = max(1, len(family.required_procedures))
    decisions = max(1, methods)
    concepts = max(1, len(family.required_concepts))
    verification = 1 if family.verification_methods else 0
    interpretation = 1 if representation in {"context", "graph", "table", "multipart", "verbal"} else 0

    # Variant tiers intentionally alter structure/surface/representation rather than only numbers.
    tier = variant_index % 4
    wording = 0 if tier == 0 else 1 if tier == 1 else 2
    rep_shift = 1 if tier >= 2 or representation != "symbolic" else 0
    if layer in {DifficultyLayer.MIXED, DifficultyLayer.PROFESSOR, DifficultyLayer.TIMED, DifficultyLayer.CUMULATIVE}:
        decisions += 1
    if layer in {DifficultyLayer.PROFESSOR, DifficultyLayer.TIMED, DifficultyLayer.CUMULATIVE}:
        interpretation += 1
        wording = max(wording, 2)
    if layer == DifficultyLayer.CUMULATIVE:
        prereq += 1
        methods += 1
    return ComplexityEvidence(
        numeric_variation=1,
        wording_variation=min(3, wording),
        representation_shift=min(3, rep_shift),
        prerequisite_depth=prereq,
        decision_points=decisions,
        reasoning_steps=max(solution_steps or 3, 2 + decisions + methods),
        concept_count=concepts,
        method_count=methods,
        verification_burden=min(3, verification + (1 if layer.value >= "L5" else 0)),
        interpretation_burden=min(3, interpretation),
        time_pressure=1 if layer in {DifficultyLayer.TIMED, DifficultyLayer.CUMULATIVE} else 0,
        source_style_distance=0 if layer in {DifficultyLayer.PROFESSOR, DifficultyLayer.TIMED} else 1,
    )


def complexity_layer(evidence: ComplexityEvidence) -> DifficultyLayer:
    """Map multidimensional evidence to a calibrated layer; simple multi-concept items are not automatically 'exam hard'."""
    score = evidence.structural_score
    if score <= 8:
        return DifficultyLayer.FOUNDATION
    if score <= 11:
        return DifficultyLayer.DIRECT
    if score <= 14:
        return DifficultyLayer.GUIDED
    if score <= 17:
        return DifficultyLayer.REPRESENTATION
    if score <= 20:
        return DifficultyLayer.MIXED
    if score <= 24:
        return DifficultyLayer.PROFESSOR
    if score <= 28:
        return DifficultyLayer.TIMED
    return DifficultyLayer.CUMULATIVE


def audit_problem(problem: PracticeProblem) -> dict[str, object]:
    e = problem.complexity_evidence
    return {
        "family_id": problem.family_id,
        "layer": problem.complexity_level.value,
        "structural_score": e.structural_score,
        "structural_signature": problem.structural_signature,
        "normalized_prompt": normalized_prompt_structure(problem.prompt),
        "representation": problem.representation_type,
        "prerequisites": problem.prerequisite_count,
        "decisions": problem.decision_count,
        "steps": problem.estimated_solution_steps,
        "multiple_methods": problem.requires_multiple_methods,
        "domain_check": problem.requires_domain_check,
        "extraneous_check": problem.requires_extraneous_check,
        "interpretation": problem.requires_interpretation,
    }


def diversity_report(problems: list[PracticeProblem]) -> dict[str, object]:
    normalized = [normalized_prompt_structure(p.prompt) for p in problems]
    signatures = [p.structural_signature for p in problems]
    families = Counter(p.family_id for p in problems)
    return {
        "questions": len(problems),
        "unique_visible_prompts": len({p.prompt for p in problems}),
        "unique_normalized_structures": len(set(normalized)),
        "unique_structural_signatures": len(set(signatures)),
        "exact_duplicates": len(problems) - len({p.prompt for p in problems}),
        "near_duplicates": len(problems) - len(set(normalized)),
        "family_count": len(families),
        "max_from_single_family": max(families.values(), default=0),
        "l4_or_higher": sum(int(p.complexity_level.value[1]) >= 4 for p in problems),
        "l6_or_l7": sum(int(p.complexity_level.value[1]) >= 6 for p in problems),
        "multi_method": sum(p.requires_multiple_methods for p in problems),
        "multiple_prerequisites": sum(p.prerequisite_count > 1 for p in problems),
        "method_selection": sum(p.decision_count > 1 for p in problems),
        "verification_required": sum(bool(p.worked_solution.check) for p in problems),
        "family_distribution": dict(sorted(families.items())),
    }


def application_context(family_id: str, variant: int) -> str:
    family = PROBLEM_FAMILY_INDEX.get(family_id)
    if not family or not family.application_contexts:
        return "none"
    return family.application_contexts[variant % len(family.application_contexts)]
