from __future__ import annotations

import re
from dataclasses import dataclass

import sympy


TEXT_ANSWERS = {"no solution", "all real numbers", "none of these"}


@dataclass(frozen=True)
class DisplayChoice:
    letter: str
    raw_answer: str
    latex: str


def _expression_latex(value: str) -> str:
    expression = sympy.sympify(value.replace("^", "**").replace("i", "I"))
    return sympy.latex(expression)


def answer_to_latex(answer: str, answer_type: str) -> str:
    """Convert stored validator syntax into familiar learner-facing mathematics."""
    text = answer.strip()
    if text.casefold() in TEXT_ANSWERS:
        return rf"\text{{{text.capitalize()}}}"
    try:
        if answer_type == "multi_select":
            return r"\text{" + ", ".join(part.strip() for part in text.split(",")) + "}"
        if answer_type in {"ordered_pair", "ordered_pairs"}:
            pairs = text.split(";")
            rendered = []
            for pair in pairs:
                x_value, y_value = pair.strip().strip("()").split(",", 1)
                rendered.append(rf"\left({_expression_latex(x_value)},\,{_expression_latex(y_value)}\right)")
            return r",\;".join(rendered)
        if answer_type in {"interval", "domain", "range"}:
            return text.replace("-oo", r"-\infty").replace("oo", r"\infty").replace("U", r"\cup")
        if answer_type == "equation" and "=" in text:
            left, right = text.split("=", 1)
            return rf"{_expression_latex(left)}={_expression_latex(right)}"
        if answer_type == "solution_set":
            values = [part.strip() for part in text.strip("{}").split(",") if part.strip()]
            return r"\left\{" + r",\;".join(_expression_latex(value) for value in values) + r"\right\}"
        return _expression_latex(text)
    except (TypeError, ValueError, SyntaxError, sympy.SympifyError):
        return normalize_math_fragment(text)


def normalize_math_fragment(fragment: str) -> str:
    """Make template/SymPy syntax readable without changing the underlying stored answer."""
    value = fragment.strip()
    value = re.sub(r"\+\(\s*(-[^)]+)\)", r"\1", value)
    value = re.sub(r"-\(\s*(-[^)]+)\)", r"+\1", value)
    value = value.replace("**", "^")
    value = value.replace(">=", r"\ge ").replace("<=", r"\le ").replace("!=", r"\ne ")
    value = re.sub(r"sqrt\(([^()]+)\)", r"\\sqrt{\1}", value)
    value = re.sub(r"\blog\(([^()]+)\)", r"\\log\\left(\1\\right)", value)
    value = value.replace("*", r"\,")
    return value


def readable_prompt(prompt: str) -> str:
    """Normalize only inline/display math segments while preserving the authored wording."""
    pieces = re.split(r"(\$\$.*?\$\$|\$.*?\$)", prompt, flags=re.DOTALL)
    rendered: list[str] = []
    for piece in pieces:
        if piece.startswith("$$") and piece.endswith("$$"):
            rendered.append("$$" + normalize_math_fragment(piece[2:-2]) + "$$")
        elif piece.startswith("$") and piece.endswith("$"):
            rendered.append("$" + normalize_math_fragment(piece[1:-1]) + "$")
        else:
            rendered.append(piece)
    return "".join(rendered)


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [
        DisplayChoice(letter=letters[index], raw_answer=answer, latex=answer_to_latex(answer, answer_type))
        for index, answer in enumerate(choices)
    ]
