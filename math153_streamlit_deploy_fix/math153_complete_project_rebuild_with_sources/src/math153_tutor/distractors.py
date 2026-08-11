from __future__ import annotations

from dataclasses import dataclass

import sympy

from .course_content import PROBLEM_FAMILY_INDEX
from .models import PracticeProblem
from .validation import validate_practice_answer


@dataclass(frozen=True)
class Distractor:
    answer: str
    error_pattern: str


def _unique(values: list[Distractor], correct: str) -> list[Distractor]:
    out: list[Distractor] = []
    seen = {correct.strip().casefold()}
    for d in values:
        key = d.answer.strip().casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def _numeric_candidates(problem: PracticeProblem) -> list[Distractor]:
    try:
        value = sympy.sympify(problem.expected_answer.replace("^","**").replace("i","I"))
    except Exception:
        return []
    if getattr(value, "free_symbols", set()):
        return []
    try:
        return [
            Distractor(str(sympy.simplify(-value)).replace("I","i"), "sign error"),
            Distractor(str(sympy.simplify(value + 1)).replace("I","i"), "off-by-one / arithmetic slip"),
            Distractor(str(sympy.simplify(value - 1)).replace("I","i"), "off-by-one / arithmetic slip"),
            Distractor(str(sympy.simplify(1/value)).replace("I","i"), "reciprocal used incorrectly") if value != 0 else Distractor("1","zero-handling error"),
        ]
    except Exception:
        return []


def _family_candidates(problem: PracticeProblem) -> list[Distractor]:
    fid = problem.family_id
    expected = problem.expected_answer
    values: list[Distractor] = []
    if problem.wrong_answer:
        values.append(Distractor(problem.wrong_answer, "known source-family misconception"))
    if problem.answer_type in {"interval","domain","range"}:
        # Endpoint/open-closed and complement mistakes are much more meaningful here than random numbers.
        swapped = expected.translate(str.maketrans({"[":"(", "]":")"}))
        values.append(Distractor(swapped, "endpoint inclusion/exclusion error"))
    if "LOG" in fid:
        values.extend([
            Distractor("0", "ignored logarithm domain/property"),
            Distractor("1", "treated logarithm as an ordinary factor"),
        ])
    if "COMPLEX" in fid:
        values.append(Distractor(expected.replace("+","-",1) if "+" in expected else expected.replace("-","+",1),
                                 "conjugate/sign error"))
    if "RATIONAL" in fid:
        values.append(Distractor("0", "canceled terms or lost a restriction"))
    if "QUADRATIC" in fid or "ABS-EQUATIONS" in fid:
        values.append(Distractor(expected.split(",")[0], "kept only one branch/root"))
    if "LINE" in fid:
        values.append(Distractor(expected.replace("+","-",1) if "+" in expected else expected,
                                 "slope/intercept sign error"))
    return values


def meaningful_distractors(problem: PracticeProblem, limit: int = 3) -> list[Distractor]:
    """
    Build distractors from actual mathematical error patterns. A distractor is only kept
    when the validator confirms it is not equivalent to the correct answer.
    """
    candidates = _family_candidates(problem) + _numeric_candidates(problem)
    family = PROBLEM_FAMILY_INDEX.get(problem.family_id)
    if family:
        # Preserve the source-derived mistake descriptions even when no deterministic wrong
        # numerical answer can be synthesized from them.
        candidates.extend(
            Distractor(problem.wrong_answer, mistake)
            for mistake in family.common_mistakes
            if problem.wrong_answer
        )
    result: list[Distractor] = []
    for candidate in _unique(candidates, problem.expected_answer):
        if validate_practice_answer(problem, candidate.answer).correct:
            continue
        result.append(candidate)
        if len(result) >= limit:
            break
    return result
