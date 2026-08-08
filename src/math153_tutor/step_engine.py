from __future__ import annotations

import re

import sympy
from pydantic import BaseModel

from .models import PracticeProblem


class StepCheck(BaseModel):
    valid: bool
    step_index: int
    normalized_line: str = ""
    error_code: str | None = None
    explanation: str
    next_guidance: str | None = None


def solution_steps(problem: PracticeProblem) -> list[str]:
    return [problem.worked_solution.setup, *problem.worked_solution.calculation]


def _clean(value: str) -> str:
    return value.strip().strip("$").replace(" ", "").replace("^", "**")


def _equivalent(actual: str, expected: str) -> bool:
    if actual.casefold() == expected.casefold():
        return True
    if "=" in actual and "=" in expected:
        actual_left, actual_right = actual.split("=", 1)
        expected_left, expected_right = expected.split("=", 1)
        actual_expr = sympy.expand(sympy.sympify(actual_left) - sympy.sympify(actual_right))
        expected_expr = sympy.expand(sympy.sympify(expected_left) - sympy.sympify(expected_right))
        if expected_expr == 0:
            return bool(actual_expr == 0)
        ratio = sympy.simplify(actual_expr / expected_expr)
        return bool(ratio != 0 and not ratio.free_symbols)
    return bool(sympy.simplify(sympy.sympify(actual) - sympy.sympify(expected)) == 0)


def check_step(problem: PracticeProblem, learner_line: str, step_index: int) -> StepCheck:
    """Validate one line against the controlled family path and return bounded feedback."""
    steps = solution_steps(problem)
    index = min(max(step_index, 0), len(steps) - 1)
    actual, expected = _clean(learner_line), _clean(steps[index])
    if not actual:
        return StepCheck(
            valid=False,
            step_index=index,
            error_code="empty_line",
            explanation="Enter one mathematical line before asking for a check.",
            next_guidance=steps[index],
        )
    if "LOG" in problem.family_id and index == 0 and "restriction" in steps[index].casefold():
        if not re.search(r">\s*0", learner_line):
            return StepCheck(
                valid=False,
                step_index=index,
                normalized_line=actual,
                error_code="domain_check_missing",
                explanation="A logarithm argument must be positive before transformations are used.",
                next_guidance=steps[index],
            )
    try:
        valid = _equivalent(actual, expected)
    except (TypeError, ValueError, SyntaxError, sympy.SympifyError):
        return StepCheck(
            valid=False,
            step_index=index,
            normalized_line=actual,
            error_code="parse_error",
            explanation=(
                "The line could not be parsed as the expected expression/equation. "
                "Use explicit multiplication such as 2*x and one equals sign."
            ),
            next_guidance=steps[index],
        )
    if not valid:
        return StepCheck(
            valid=False,
            step_index=index,
            normalized_line=actual,
            error_code="invalid_transformation",
            explanation=(
                f"This line is not equivalent to checkpoint {index + 1}. "
                f"Reapply: {problem.worked_solution.rule}"
            ),
            next_guidance=steps[index],
        )
    next_index = index + 1
    return StepCheck(
        valid=True,
        step_index=next_index,
        normalized_line=actual,
        explanation="The line is equivalent to the expected checkpoint.",
        next_guidance=steps[next_index] if next_index < len(steps) else None,
    )
