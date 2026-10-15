from __future__ import annotations

import random
from typing import Iterable

import sympy

from .models import PracticeProblem
from .validation import validate_practice_answer


def _sympify(value: str):
    return sympy.sympify(value.replace("^", "**").replace("i", "I"), locals={"ln": sympy.log, "log": sympy.log})


def verified_correct_answer(problem: PracticeProblem) -> str:
    """Return the authored expected answer only after the canonical validator accepts it."""
    if not validate_practice_answer(problem, problem.expected_answer).correct:
        raise ValueError(f"Expected answer failed validation for {problem.problem_id}")
    return problem.expected_answer


def deterministic_distractors(problem: PracticeProblem) -> list[str]:
    """Generate mathematically wrong but plausible alternatives from the computed answer."""
    correct = verified_correct_answer(problem)
    out: list[str] = []

    try:
        value = _sympify(correct)
        if not getattr(value, "free_symbols", set()):
            candidates = [
                -value,
                value + 1,
                value - 1,
                sympy.Rational(1, 1) / value if value != 0 else sympy.Integer(1),
            ]
            out.extend(str(sympy.simplify(v)).replace("I", "i") for v in candidates)
    except Exception:
        pass

    if problem.answer_type in {"expression", "equation", "logarithmic_expression", "radical"}:
        raw = correct
        out.extend([
            raw.replace("+", "-", 1) if "+" in raw else raw.replace("-", "+", 1),
            raw.replace("*", "", 1) if "*" in raw else f"-({raw})",
        ])

    if problem.answer_type in {"interval", "domain", "range"}:
        out.extend([
            correct.translate(str.maketrans({"[": "(", "]": ")"})),
            correct.translate(str.maketrans({"(": "[", ")": "]"})),
        ])

    return out


def complete_multiple_choice(problem: PracticeProblem, choices: Iterable[str], *, seed: int | None = None) -> list[str]:
    """Return exactly four unique choices containing one validated correct answer."""
    correct = verified_correct_answer(problem)
    candidates = [*choices, *deterministic_distractors(problem)]
    unique: list[str] = []
    seen: set[str] = set()

    for value in [correct, *candidates]:
        text = str(value).strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        if text != correct and validate_practice_answer(problem, text).correct:
            continue
        unique.append(text)
        if len(unique) == 4:
            break

    if len(unique) < 4:
        # Deterministic generic fallbacks are only used after mathematical distractors are exhausted.
        for suffix in ("0", "1", "-1", "none of these"):
            if suffix.casefold() in seen:
                continue
            if validate_practice_answer(problem, suffix).correct:
                continue
            seen.add(suffix.casefold())
            unique.append(suffix)
            if len(unique) == 4:
                break

    if len(unique) != 4:
        raise ValueError(f"Could not build four distinct answer choices for {problem.problem_id}")

    rng = random.Random(seed if seed is not None else problem.parameter_seed)
    rng.shuffle(unique)
    return unique
