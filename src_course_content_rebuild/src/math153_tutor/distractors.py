from __future__ import annotations

from dataclasses import dataclass

import sympy

from .models import PracticeProblem
from .validation import validate_practice_answer


@dataclass(frozen=True)
class Distractor:
    answer: str
    error_pattern: str


def _numeric_candidates(problem: PracticeProblem) -> list[Distractor]:
    try:
        value = sympy.sympify(problem.expected_answer)
    except (sympy.SympifyError, TypeError):
        return []
    if value.free_symbols:
        return []
    if "EXPONENT" in problem.family_id or "LOG" in problem.family_id:
        return [
            Distractor(str(-value), "sign or inverse-direction error"),
            Distractor(str(value + 1), "off-by-one exponent/logarithm error"),
            Distractor("No solution", "incorrectly rejected a valid domain value"),
        ]
    if "LINEAR" in problem.family_id:
        return [
            Distractor(str(-value), "sign error while moving a term"),
            Distractor("0", "stopped after cancelling variable terms"),
            Distractor("No solution", "misclassified the resulting equation"),
        ]
    return [
        Distractor(str(-value), "sign error"),
        Distractor(str(sympy.simplify(1 / value)) if value else "1", "used a reciprocal"),
        Distractor("0", "dropped a nonzero term"),
    ]


def meaningful_distractors(problem: PracticeProblem) -> list[Distractor]:
    """Create bounded, family/answer-form-aware errors; never use arbitrary sentinel values."""
    candidates = [Distractor(problem.wrong_answer, "authored common error")]
    if problem.answer_type == "solution_set" and "," in problem.expected_answer:
        parts = problem.expected_answer.split(",")
        candidates.extend(
            [
                Distractor(parts[0], "kept only the first solution"),
                Distractor(parts[-1], "kept only the second solution"),
                Distractor("No solution", "discarded every candidate"),
            ]
        )
    elif problem.answer_type == "ordered_pair":
        x_value, y_value = problem.expected_answer.strip("()").split(",")
        candidates.extend(
            [
                Distractor(f"({y_value},{x_value})", "reversed the coordinates"),
                Distractor(f"({x_value},{sympy.sstr(-sympy.sympify(y_value))})", "y-sign error"),
                Distractor(f"({sympy.sstr(-sympy.sympify(x_value))},{y_value})", "x-sign error"),
            ]
        )
    elif problem.answer_type in {"integer", "solution_set", "fraction", "decimal", "table"}:
        candidates.extend(_numeric_candidates(problem))
    elif problem.answer_type == "interval":
        candidates.extend(
            [
                Distractor(problem.expected_answer.translate(str.maketrans("()[]", "][)(")), "endpoint inclusion error"),
                Distractor("No solution", "discarded the valid interval"),
            ]
        )
    elif problem.answer_type == "equation":
        candidates.extend(
            [
                Distractor(problem.expected_answer.replace("+", "-", 1), "sign error in equation form"),
                Distractor("y=0", "lost slope/center information"),
            ]
        )
    elif problem.answer_type in {"expression", "radical", "logarithmic_expression"}:
        candidates.extend(
            [
                Distractor("0", "dropped the expression"),
                Distractor("1", "misapplied an identity rule"),
            ]
        )
    elif problem.answer_type == "complex_number":
        candidates.extend(
            [
                Distractor(problem.expected_answer.replace("+", "-"), "imaginary-part sign error"),
                Distractor("0", "treated the imaginary terms as cancelling"),
            ]
        )
    unique: list[Distractor] = []
    for candidate in candidates:
        if candidate.answer and all(item.answer != candidate.answer for item in unique):
            if not validate_practice_answer(problem, candidate.answer).correct:
                unique.append(candidate)
    return unique[:3]
