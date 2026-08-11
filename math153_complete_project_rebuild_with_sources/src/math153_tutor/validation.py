from __future__ import annotations

import re
from dataclasses import dataclass

import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from .models import GeneratedProblem, PracticeProblem


@dataclass(frozen=True)
class ValidationResult:
    correct: bool
    error_code: str | None = None


class AnswerParseError(ValueError):
    pass


TRANSFORMS = standard_transformations + (convert_xor, implicit_multiplication_application,)
SAFE_NAMES = {
    "x": sympy.Symbol("x"),
    "y": sympy.Symbol("y"),
    "z": sympy.Symbol("z"),
    "t": sympy.Symbol("t"),
    "h": sympy.Symbol("h"),
    "A": sympy.Symbol("A"),
    "P": sympy.Symbol("P"),
    "r": sympy.Symbol("r"),
    "n": sympy.Symbol("n"),
    "I": sympy.I,
    "i": sympy.I,
    "pi": sympy.pi,
    "e": sympy.E,
    "E": sympy.E,
    "sqrt": sympy.sqrt,
    "Abs": sympy.Abs,
    "abs": sympy.Abs,
    "log": sympy.log,
    "ln": sympy.log,
}


def _normalize_expression_text(value: str) -> str:
    value = value.strip()
    value = value.replace("−", "-").replace("×", "*").replace("÷", "/")
    value = value.replace("∞", "oo").replace("√", "sqrt")
    value = value.replace("^", "**")
    return value


def _expression(value: str) -> sympy.Expr:
    text = _normalize_expression_text(value)
    if not text:
        raise AnswerParseError("Enter a mathematical expression.")
    # Reject obvious code/file syntax while allowing normal math identifiers.
    if any(token in text for token in ("__", "import", "exec", "eval", "[", "]", "{", "}")):
        raise AnswerParseError("Unsupported notation.")
    try:
        return parse_expr(
            text,
            local_dict=SAFE_NAMES,
            transformations=TRANSFORMS,
            evaluate=True,
        )
    except Exception as exc:
        raise AnswerParseError("The answer could not be parsed. Check the notation.") from exc


def _solution_set(value: str) -> set[sympy.Expr]:
    cleaned = value.strip().strip("{}")
    if cleaned.casefold() in {"no solution", "empty", "∅", "none"}:
        return set()
    if cleaned.casefold() in {"all real numbers", "all reals", "r"}:
        return {sympy.Symbol("__ALL_REALS__")}
    return {_expression(item.strip()) for item in cleaned.split(",") if item.strip()}


def _equation(value: str) -> sympy.Expr:
    if "=" not in value:
        raise AnswerParseError("Enter an equation containing an equals sign.")
    left, right = value.split("=", 1)
    return sympy.expand(_expression(left) - _expression(right))


def _pair(value: str) -> tuple[sympy.Expr, sympy.Expr]:
    cleaned = value.strip()
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = cleaned[1:-1]
    parts = cleaned.split(",")
    if len(parts) != 2:
        raise AnswerParseError("Enter an ordered pair as (x,y).")
    return _expression(parts[0]), _expression(parts[1])


def _interval(value: str) -> sympy.Set:
    text = value.replace(" ", "").replace("∞", "oo").replace("∪", "U")
    pieces = re.split(r"U", text, flags=re.IGNORECASE)
    result: sympy.Set = sympy.EmptySet
    for piece in pieces:
        match = re.fullmatch(r"([\[(])([^,]+),([^\])]+)([\])])", piece)
        if not match:
            raise AnswerParseError("Use interval notation such as (-oo,3] U (5,oo).")
        ltxt, rtxt = match.group(2), match.group(3)
        left = -sympy.oo if ltxt in {"-oo", "-inf"} else _expression(ltxt)
        right = sympy.oo if rtxt in {"oo", "inf", "+oo"} else _expression(rtxt)
        result = result.union(
            sympy.Interval(
                left, right,
                left_open=match.group(1) == "(",
                right_open=match.group(4) == ")",
            )
        )
    return result


def _equivalent_expr(actual: str, expected: str) -> bool:
    a, e = _expression(actual), _expression(expected)
    return bool(sympy.simplify(a - e) == 0)


def validate_answer(problem: GeneratedProblem, learner_answer: str) -> ValidationResult:
    try:
        if problem.validator == "solution_set":
            actual, expected = _solution_set(learner_answer), _solution_set(problem.expected_answer)
            correct = actual == expected or (
                len(actual) == len(expected)
                and all(any(sympy.simplify(a-e) == 0 for e in expected) for a in actual)
            )
            return ValidationResult(bool(correct), None if correct else "solution_set_mismatch")
        correct = _equivalent_expr(learner_answer, problem.expected_answer)
        if correct and problem.exact_form_required and bool(_expression(learner_answer).atoms(sympy.Float)):
            return ValidationResult(False, "exact_form_required")
        return ValidationResult(correct, None if correct else "not_equivalent")
    except AnswerParseError:
        return ValidationResult(False, "parse_error")


def validate_practice_answer(problem: PracticeProblem, learner_answer: str) -> ValidationResult:
    """Validate all learner-facing answer forms without weakening source-required answer form."""
    try:
        kind = problem.answer_type
        if kind == "multiple_choice":
            correct = learner_answer.strip().casefold() == problem.expected_answer.strip().casefold()
        elif kind == "multi_select":
            actual = {v.strip().casefold() for v in learner_answer.split(",") if v.strip()}
            expected = {v.strip().casefold() for v in problem.expected_answer.split(",") if v.strip()}
            correct = actual == expected
        elif kind in {"interval", "domain", "range"}:
            correct = _interval(learner_answer) == _interval(problem.expected_answer)
        elif kind == "ordered_pair":
            actual, expected = _pair(learner_answer), _pair(problem.expected_answer)
            correct = all(sympy.simplify(a-e) == 0 for a,e in zip(actual, expected, strict=True))
        elif kind == "ordered_pairs":
            actual = {_pair(v) for v in learner_answer.split(";") if v.strip()}
            expected = {_pair(v) for v in problem.expected_answer.split(";") if v.strip()}
            correct = actual == expected
        elif kind == "equation":
            actual, expected = _equation(learner_answer), _equation(problem.expected_answer)
            if expected == 0:
                correct = actual == 0
            else:
                ratio = sympy.simplify(actual / expected)
                correct = bool(ratio != 0 and not ratio.free_symbols)
        elif kind == "solution_set":
            actual, expected = _solution_set(learner_answer), _solution_set(problem.expected_answer)
            if actual == expected:
                correct = True
            elif any(str(v) == "__ALL_REALS__" for v in actual | expected):
                correct = False
            else:
                correct = len(actual) == len(expected) and all(
                    any(sympy.simplify(a-e) == 0 for e in expected) for a in actual
                )
        elif kind == "complex_number":
            correct = _equivalent_expr(learner_answer.replace("i","I"), problem.expected_answer.replace("i","I"))
        elif kind == "decimal":
            actual_decimal = float(_expression(learner_answer))
            expected_decimal = float(_expression(problem.expected_answer))
            places = len(problem.expected_answer.partition(".")[2])
            correct = abs(actual_decimal - expected_decimal) <= 0.5 * 10 ** (-places)
        elif kind in {
            "integer","fraction","expression","radical","logarithmic_expression","table"
        }:
            correct = _equivalent_expr(learner_answer, problem.expected_answer)
            if correct and kind == "radical":
                for radicand in re.findall(r"sqrt\((\d+)\)", learner_answer.replace(" ","")):
                    if any(exp >= 2 for exp in sympy.factorint(int(radicand)).values()):
                        correct = False
        elif kind == "text":
            norm = lambda s: re.sub(r"\s+","",s).casefold()
            correct = norm(learner_answer) == norm(problem.expected_answer)
        else:
            return ValidationResult(False, "unsupported_validator")
        return ValidationResult(bool(correct), None if correct else "not_equivalent")
    except (AnswerParseError, TypeError, ValueError, ZeroDivisionError):
        return ValidationResult(False, "parse_error")
