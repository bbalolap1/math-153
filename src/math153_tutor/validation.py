from __future__ import annotations

import re
from dataclasses import dataclass

import sympy
from sympy.parsing.sympy_parser import parse_expr

from .models import GeneratedProblem


@dataclass(frozen=True)
class ValidationResult:
    correct: bool
    error_code: str | None = None


class AnswerParseError(ValueError):
    """Raised when learner input cannot be interpreted safely."""


def _expression(value: str) -> sympy.Expr:
    if not value.strip() or not re.fullmatch(r"[0-9A-Za-z_+\-*/^(). ]+", value):
        raise AnswerParseError("Enter a mathematical expression using numbers and symbols.")
    try:
        return parse_expr(value.replace("^", "**"), evaluate=True)
    except (SyntaxError, TypeError, ValueError) as exc:
        raise AnswerParseError("The answer could not be parsed. Check the notation.") from exc


def _solution_set(value: str) -> set[sympy.Expr]:
    cleaned = value.strip().strip("{}")
    if cleaned.lower() in {"no solution", "empty", "∅"}:
        return set()
    return {_expression(item.strip()) for item in cleaned.split(",") if item.strip()}


def validate_answer(problem: GeneratedProblem, learner_answer: str) -> ValidationResult:
    """Validate an answer without leaking raw SymPy errors to the UI."""
    try:
        if problem.validator == "solution_set":
            actual = _solution_set(learner_answer)
            expected = _solution_set(problem.expected_answer)
            correct = len(actual) == len(expected) and all(
                any(sympy.simplify(a - e) == 0 for e in expected) for a in actual
            )
            return ValidationResult(correct, None if correct else "solution_set_mismatch")
        actual = _expression(learner_answer)
        expected = _expression(problem.expected_answer)
        equivalent = sympy.simplify(actual - expected) == 0
        if equivalent and problem.exact_form_required and bool(actual.atoms(sympy.Float)):
            return ValidationResult(False, "exact_form_required")
        return ValidationResult(equivalent, None if equivalent else "not_equivalent")
    except AnswerParseError:
        return ValidationResult(False, "parse_error")
