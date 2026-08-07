from __future__ import annotations

import re
from dataclasses import dataclass

import sympy
from sympy.parsing.sympy_parser import parse_expr

from .models import GeneratedProblem, PracticeProblem


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


def _equation(value: str) -> sympy.Expr:
    if "=" not in value:
        raise AnswerParseError("Enter an equation containing an equals sign.")
    left, right = value.split("=", 1)
    return sympy.expand(_expression(left) - _expression(right))


def _pair(value: str) -> tuple[sympy.Expr, sympy.Expr]:
    cleaned = value.strip().strip("()")
    parts = cleaned.split(",")
    if len(parts) != 2:
        raise AnswerParseError("Enter an ordered pair as (x,y).")
    return _expression(parts[0]), _expression(parts[1])


def _interval(value: str) -> sympy.Set:
    text = value.replace(" ", "").replace("∞", "oo")
    pieces = re.split(r"(?:U|∪)", text)
    result: sympy.Set = sympy.EmptySet
    for piece in pieces:
        match = re.fullmatch(r"([\[(])([^,]+),([^\])]+)([\])])", piece)
        if not match:
            raise AnswerParseError("Use interval notation such as (-oo,3] U (5,oo).")
        left = -sympy.oo if match.group(2) in {"-oo", "-inf"} else _expression(match.group(2))
        right = sympy.oo if match.group(3) in {"oo", "inf", "+oo"} else _expression(match.group(3))
        result = result.union(
            sympy.Interval(
                left, right, left_open=match.group(1) == "(", right_open=match.group(4) == ")"
            )
        )
    return result


def validate_practice_answer(problem: PracticeProblem, learner_answer: str) -> ValidationResult:
    """Dispatch every exam-practice answer form through project validators."""
    try:
        kind = problem.answer_type
        if kind in {"multiple_choice"}:
            correct = learner_answer.strip().casefold() == problem.expected_answer.casefold()
        elif kind == "multi_select":
            actual_selections = {
                item.strip().casefold() for item in learner_answer.split(",") if item.strip()
            }
            expected_selections = {
                item.strip().casefold() for item in problem.expected_answer.split(",")
            }
            correct = actual_selections == expected_selections
        elif kind in {"interval", "domain", "range"}:
            correct = _interval(learner_answer) == _interval(problem.expected_answer)
        elif kind == "ordered_pair":
            actual_pair, expected_pair = _pair(learner_answer), _pair(problem.expected_answer)
            correct = all(
                sympy.simplify(a - e) == 0 for a, e in zip(actual_pair, expected_pair, strict=True)
            )
        elif kind == "ordered_pairs":
            actual_pairs = {_pair(item) for item in learner_answer.split(";")}
            expected_pairs = {_pair(item) for item in problem.expected_answer.split(";")}
            correct = actual_pairs == expected_pairs
        elif kind == "equation":
            actual_equation = _equation(learner_answer)
            expected_equation = _equation(problem.expected_answer)
            if expected_equation == 0:
                correct = actual_equation == 0
            else:
                ratio = sympy.simplify(actual_equation / expected_equation)
                correct = bool(ratio != 0 and not ratio.free_symbols)
        elif kind == "solution_set":
            actual_solutions = _solution_set(learner_answer)
            expected_solutions = _solution_set(problem.expected_answer)
            correct = len(actual_solutions) == len(expected_solutions) and all(
                any(sympy.simplify(a - e) == 0 for e in expected_solutions)
                for a in actual_solutions
            )
        elif kind == "complex_number":
            actual_complex = _expression(learner_answer.replace("i", "I"))
            expected_complex = _expression(problem.expected_answer.replace("i", "I"))
            correct = sympy.simplify(actual_complex - expected_complex) == 0
        elif kind == "decimal":
            actual_decimal = float(_expression(learner_answer))
            expected_decimal = float(_expression(problem.expected_answer))
            decimal_places = len(problem.expected_answer.partition(".")[2])
            correct = abs(actual_decimal - expected_decimal) <= 0.5 * 10 ** (-decimal_places)
        elif kind in {
            "integer",
            "fraction",
            "expression",
            "radical",
            "logarithmic_expression",
            "table",
        }:
            actual_expression = _expression(learner_answer)
            expected_expression = _expression(problem.expected_answer)
            correct = sympy.simplify(actual_expression - expected_expression) == 0
            if correct and problem.family_id == "CH12-FACTORING":
                correct = learner_answer.count("(") >= 2 and ")" in learner_answer
            if correct and kind == "radical":
                for radicand in re.findall(r"sqrt\((\d+)\)", learner_answer.replace(" ", "")):
                    factors = sympy.factorint(int(radicand))
                    if any(exponent >= 2 for exponent in factors.values()):
                        correct = False
        else:  # pragma: no cover - Pydantic prevents unsupported declarations
            return ValidationResult(False, "unsupported_validator")
        return ValidationResult(bool(correct), None if correct else "not_equivalent")
    except (AnswerParseError, TypeError, ValueError, ZeroDivisionError):
        return ValidationResult(False, "parse_error")
