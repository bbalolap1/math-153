from __future__ import annotations

import random
from collections.abc import Callable

from .models import DifficultyLayer, ErrorCategory, GeneratedProblem
from .practice_catalog import family_source_refs

FAMILIES = {
    "CH1-LINEAR-EQUATIONS": "Linear equations",
    "CH4-FUNCTION-COMPOSITION": "Function composition",
    "CH5-EXP-EQUATIONS": "Exponential equations",
    "CH5-LOG-EQUATIONS": "Logarithmic equations",
}


def _common(
    family_id: str, seed: int, prompt: str, answer: str, first: str, skills: list[str]
) -> GeneratedProblem:
    options = list(FAMILIES.values())
    rng = random.Random(seed)
    rng.shuffle(options)
    catalog_family = {
        "CH1-LINEAR-EQUATIONS": "CH12-LINEAR-EQUATIONS",
        "CH4-FUNCTION-COMPOSITION": "CH34-COMPOSITION",
        "CH5-EXP-EQUATIONS": "CH5-EXP-EQUATIONS-FULL",
        "CH5-LOG-EQUATIONS": "CH5-LOG-EQUATIONS-FULL",
    }[family_id]
    source_refs = family_source_refs().get(catalog_family, [])
    return GeneratedProblem(
        problem_id=f"{family_id}-{seed}",
        family_id=family_id,
        construction_id=f"{family_id}-MODEL-01",
        difficulty_layer=DifficultyLayer.GUIDED,
        prompt=prompt,
        expected_answer=answer,
        validator="solution_set",
        recognition_options=options,
        correct_recognition=FAMILIES[family_id],
        first_decision_options=[first, "Expand every expression", "Convert to a decimal"],
        correct_first_decision=first,
        source_refs=source_refs,
        source_construction_refs=source_refs,
        source_concept_refs=source_refs,
        parameter_seed=seed,
        required_skills=skills,
        variant_reason="Controlled parameter change for a related handwritten retry.",
        reasoning_checkpoints=[first, "Solve the resulting equation", "Check the original prompt"],
        critical_checks=["domain"] if "LOG" in family_id else [],
        targeted_feedback={
            ErrorCategory.RECOGNITION: "Compare the visible notation with the family clues.",
            ErrorCategory.FIRST_STEP: f"Focus only on the opening decision: {first}",
            ErrorCategory.ALGEBRA: "Recheck one algebraic line at a time on paper.",
            ErrorCategory.DOMAIN: "Test every candidate in each original logarithm argument.",
        },
    )


def _linear(seed: int) -> GeneratedProblem:
    rng = random.Random(seed)
    solution, a, b = rng.randint(-5, 8), rng.randint(2, 6), rng.randint(-8, 8)
    c = a * solution + b
    return _common(
        "CH1-LINEAR-EQUATIONS", seed, f"Solve: ${a}x + {b} = {c}$", str(solution),
        "Undo the constant term while preserving equality", ["algebraic rearrangement", "signed numbers"]
    )


def _composition(seed: int) -> GeneratedProblem:
    rng = random.Random(seed)
    m, b, n = rng.randint(2, 5), rng.randint(-4, 4), rng.randint(-3, 5)
    return _common(
        "CH4-FUNCTION-COMPOSITION", seed,
        f"Let $f(x)={m}x+{b}$ and $g(x)=x^2$. Find $(f\\circ g)({n})$.",
        str(m * n * n + b), "Evaluate the inner function first", ["function notation", "substitution"]
    )


def _exponential(seed: int) -> GeneratedProblem:
    rng = random.Random(seed)
    base, solution = rng.choice([2, 3, 5]), rng.randint(2, 5)
    return _common(
        "CH5-EXP-EQUATIONS", seed, f"Solve exactly: ${base}^x={base ** solution}$.",
        str(solution), "Rewrite both sides with the same base", ["exponent rules", "one-to-one property"]
    )


def _logarithmic(seed: int) -> GeneratedProblem:
    rng = random.Random(seed)
    solution, shift = rng.randint(3, 9), rng.randint(1, 4)
    value = solution + shift
    return _common(
        "CH5-LOG-EQUATIONS", seed,
        f"Solve and check the original domain: $\\ln(x+{shift})=\\ln({value})$.",
        str(solution), "State the argument restriction, then compare arguments",
        ["logarithm domain", "linear equations", "extraneous-solution check"]
    )


GENERATORS: dict[str, Callable[[int], GeneratedProblem]] = {
    "CH1-LINEAR-EQUATIONS": _linear,
    "CH4-FUNCTION-COMPOSITION": _composition,
    "CH5-EXP-EQUATIONS": _exponential,
    "CH5-LOG-EQUATIONS": _logarithmic,
}


def generate_problem(family_id: str, seed: int) -> GeneratedProblem:
    """Build a reproducible problem from a bounded, human-reviewed template."""
    try:
        return GENERATORS[family_id](seed)
    except KeyError as exc:
        raise ValueError(f"Unknown family: {family_id}") from exc
