from __future__ import annotations

import re
from dataclasses import dataclass

import sympy


TEXT_ANSWERS = {"no solution", "all real numbers", "none of these", "yes", "no"}


@dataclass(frozen=True)
class DisplayChoice:
    letter: str
    raw_answer: str
    latex: str


def normalize_math_fragment(value: str) -> str:
    """Normalize a mathematical fragment for display without rewriting prose."""
    text = value.strip().replace("−", "-")
    # Preserve already-valid LaTeX.
    if "\\" in text:
        return text
    # Legacy flattened tokens from older generated prompts.
    text = re.sub(r"\bfrac1x\b", r"\\frac{1}{x}", text)
    text = re.sub(r"\bfrac52\b", r"\\frac{5}{2}", text)
    text = re.sub(r"\bfrac([0-9]+)([A-Za-z])\b", r"\\frac{\1}{\2}", text)
    text = re.sub(r"\bfrac([0-9])([0-9])\b", r"\\frac{\1}{\2}", text)
    text = re.sub(r"(?<!\\)\bln\b", r"\\ln", text)
    text = re.sub(r"(?<!\\)\blog\b", r"\\log", text)
    return text


def _expression_latex(value: str) -> str:
    raw = value.strip().replace("−", "-")
    if "\\" in raw:
        return raw
    try:
        expr = sympy.sympify(
            raw.replace("^", "**").replace("i", "I"),
            locals={"ln": sympy.log, "log": sympy.log, "sqrt": sympy.sqrt, "Abs": sympy.Abs},
        )
        return sympy.latex(expr)
    except Exception:
        return normalize_math_fragment(raw)


def answer_to_latex(answer: str, answer_type: str) -> str:
    raw = answer.strip()
    if raw.casefold() in TEXT_ANSWERS:
        return rf"\text{{{raw}}}"
    if answer_type in {"interval", "domain", "range"}:
        return raw.replace("oo", r"\infty").replace(" U ", r"\cup ")
    if answer_type == "ordered_pair":
        return raw if raw.startswith("(") else f"({raw})"
    if answer_type == "ordered_pairs":
        return r",\ ".join(part.strip() for part in raw.split(";"))
    if answer_type == "equation" and "=" in raw:
        left, right = raw.split("=", 1)
        return f"{_expression_latex(left)}={_expression_latex(right)}"
    if answer_type in {"text", "multi_select"}:
        return rf"\text{{{raw}}}"
    return _expression_latex(raw)


def prompt_parts(prompt: str) -> list[tuple[str, str]]:
    """
    Preserve a word problem as continuous prose while extracting only explicit $...$ or $$...$$
    regions as mathematical display fragments.

    Generated prompts are expected to put mathematics inside dollar delimiters. This function
    deliberately avoids guessing that ordinary prose fragments are math; that guessing was the
    cause of chopped word problems and malformed fractions.
    """
    text = re.sub(r"\s+", " ", prompt).strip()
    if not text:
        return []

    parts: list[tuple[str, str]] = []
    pattern = re.compile(r"(\$\$.*?\$\$|\$.*?\$)")
    cursor = 0
    for match in pattern.finditer(text):
        prose = text[cursor:match.start()]
        if prose:
            parts.append(("text", prose.strip()))
        token = match.group(0)
        math = token[2:-2] if token.startswith("$$") else token[1:-1]
        parts.append(("math", normalize_math_fragment(math)))
        cursor = match.end()

    tail = text[cursor:]
    if tail:
        parts.append(("text", tail.strip()))

    if not parts:
        # Legacy fallback: keep the whole sentence readable instead of splitting it into guessed pieces.
        cleaned = text.replace("*", "")
        cleaned = cleaned.replace("frac1x", "1/x").replace("frac52", "5/2")
        return [("text", cleaned)]
    return parts


def readable_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt).strip()


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [
        DisplayChoice(letter=letters[i], raw_answer=choice, latex=answer_to_latex(choice, answer_type))
        for i, choice in enumerate(choices)
    ]
