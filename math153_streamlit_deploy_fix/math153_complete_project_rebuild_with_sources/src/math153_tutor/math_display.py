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


TEXT_ANSWERS = {"no solution", "all real numbers", "none of these", "yes", "no"}
TRANSFORMS = standard_transformations + (convert_xor, implicit_multiplication_application)
SAFE_NAMES = {
    "x": sympy.Symbol("x"),
    "y": sympy.Symbol("y"),
    "z": sympy.Symbol("z"),
    "t": sympy.Symbol("t"),
    "h": sympy.Symbol("h"),
    "k": sympy.Symbol("k"),
    "a": sympy.Symbol("a"),
    "b": sympy.Symbol("b"),
    "c": sympy.Symbol("c"),
    "A": sympy.Symbol("A"),
    "P": sympy.Symbol("P"),
    "r": sympy.Symbol("r"),
    "n": sympy.Symbol("n"),
    "i": sympy.I,
    "I": sympy.I,
    "pi": sympy.pi,
    "e": sympy.E,
    "sqrt": sympy.sqrt,
    "Abs": sympy.Abs,
    "ln": sympy.log,
    "log": sympy.log,
}


@dataclass(frozen=True)
class DisplayChoice:
    letter: str
    raw_answer: str
    latex: str


def _strip_markdown_emphasis(text: str) -> str:
    """Remove accidental Markdown emphasis around math tokens without deleting multiplication."""
    # *x*, *frac*, *52* -> x, frac, 52.  Keep ordinary 2*x multiplication untouched.
    return re.sub(r"\*([A-Za-z0-9_\\]+)\*", r"\1", text)


def _repair_flattened_fraction(text: str) -> str:
    """Repair legacy flattened `frac` tokens produced by older prompt generators."""
    # Preserve correct LaTeX first.
    text = re.sub(r"(?<!\\)frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"\\frac{\1}{\2}", text)
    # Common old outputs seen in the deployed app.
    text = re.sub(r"(?<![A-Za-z])frac1x(?![A-Za-z])", r"\\frac{1}{x}", text)
    text = re.sub(r"(?<![A-Za-z])frac52(?![0-9])", r"\\frac{5}{2}", text)
    # Conservative number/variable and single-digit/single-digit forms.
    text = re.sub(r"(?<![A-Za-z])frac([0-9]+)([A-Za-z])(?![A-Za-z])", r"\\frac{\1}{\2}", text)
    text = re.sub(r"(?<![A-Za-z])frac([0-9])([0-9])(?![0-9])", r"\\frac{\1}{\2}", text)
    return text


def normalize_math_fragment(value: str) -> str:
    """
    Convert storage-oriented notation into canonical LaTeX for student display.

    This function is intentionally display-only.  It never changes the mathematical
    answer stored by the generator/validator.
    """
    text = str(value).strip()
    if not text:
        return ""

    text = _strip_markdown_emphasis(text)
    text = text.replace("−", "-").replace("–", "-")
    text = text.replace("×", r"\times ").replace("÷", r"\div ")
    text = text.replace("≥", r"\ge ").replace("≤", r"\le ")
    text = text.replace("≠", r"\ne ").replace("≈", r"\approx ")
    text = text.replace("±", r"\pm ").replace("∓", r"\mp ")
    text = text.replace("∞", r"\infty")
    text = text.replace("∪", r"\cup ")
    text = _repair_flattened_fraction(text)

    # If it is already LaTeX after the repairs, preserve it.
    if "\\" in text:
        return text

    # Normalize a few human/storage spellings before SymPy conversion.
    text = re.sub(r"\bln\s*\(", "log(", text)
    text = re.sub(r"\bln\s+([A-Za-z0-9_(])", r"log(\1", text)

    # Convert parseable algebra to LaTeX so *, /, ** and sqrt(...) never leak to the UI.
    try:
        expr = parse_expr(
            text.replace("^", "**"),
            local_dict=SAFE_NAMES,
            transformations=TRANSFORMS,
            evaluate=False,
        )
        return sympy.latex(expr)
    except Exception:
        # Final typography-only cleanup for fragments that are not full SymPy expressions.
        text = text.replace("**", "^")
        text = re.sub(r"(?<!\\)\bsqrt\s*\(([^()]+)\)", r"\\sqrt{\1}", text)
        text = re.sub(r"(?<!\\)\bln\b", r"\\ln", text)
        text = re.sub(r"(?<!\\)\blog\b", r"\\log", text)
        text = text.replace("*", r"\cdot ")
        return text


def _expression_latex(value: str) -> str:
    raw = str(value).strip()
    if not raw:
        return ""
    repaired = normalize_math_fragment(raw)
    return repaired


def answer_to_latex(answer: str, answer_type: str) -> str:
    raw = str(answer).strip()
    if raw.casefold() in TEXT_ANSWERS:
        return rf"\text{{{raw}}}"
    if answer_type in {"interval", "domain", "range"}:
        return (
            raw.replace("oo", r"\infty")
            .replace("∞", r"\infty")
            .replace(" U ", r"\cup ")
            .replace("∪", r"\cup ")
        )
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


def _looks_like_standalone_math(text: str) -> bool:
    """Identify a legacy prompt that is almost entirely one mathematical expression."""
    candidate = text.strip()
    if not candidate:
        return False
    if len(candidate.split()) > 8:
        return False
    markers = ("=", "<", ">", "frac", "sqrt", "^", "**", "ln", "log", "±", "≤", "≥")
    return any(marker in candidate for marker in markers)


def prompt_parts(prompt: str) -> list[tuple[str, str]]:
    """
    Split a prompt into prose and mathematical regions.

    Preferred input uses `$...$` or `$$...$$`.  Legacy prompts without delimiters are
    repaired only when the whole fragment is clearly mathematics.  We do not guess at
    arbitrary prose, which prevents word problems from being chopped into pieces.
    """
    text = re.sub(r"\s+", " ", str(prompt)).strip()
    if not text:
        return []

    parts: list[tuple[str, str]] = []
    pattern = re.compile(r"(\$\$.*?\$\$|\$.*?\$)")
    cursor = 0
    for match in pattern.finditer(text):
        prose = text[cursor:match.start()].strip()
        if prose:
            parts.append(("text", prose))
        token = match.group(0)
        math = token[2:-2] if token.startswith("$$") else token[1:-1]
        parts.append(("math", normalize_math_fragment(math)))
        cursor = match.end()

    tail = text[cursor:].strip()
    if tail:
        parts.append(("text", tail))

    if parts:
        return parts

    # Handle common legacy pattern: "instruction: x+frac1x=frac52".
    if ":" in text:
        left, right = text.rsplit(":", 1)
        if left.strip() and _looks_like_standalone_math(right):
            return [("text", left.strip() + ":"), ("math", normalize_math_fragment(right))]

    if _looks_like_standalone_math(text):
        return [("math", normalize_math_fragment(text))]

    return [("text", _strip_markdown_emphasis(text))]


def readable_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", _strip_markdown_emphasis(str(prompt))).strip()


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [
        DisplayChoice(letter=letters[i], raw_answer=choice, latex=answer_to_latex(choice, answer_type))
        for i, choice in enumerate(choices)
    ]
