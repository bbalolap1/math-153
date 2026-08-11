from __future__ import annotations

import re
from dataclasses import dataclass

import sympy


TEXT_ANSWERS={"no solution","all real numbers","none of these","yes","no"}


@dataclass(frozen=True)
class DisplayChoice:
    letter: str
    raw_answer: str
    latex: str


def normalize_math_fragment(value: str) -> str:
    """Convert storage syntax to familiar mathematical typography without changing meaning."""
    text=value.strip()
    text=text.replace("**","^")
    text=text.replace("oo",r"\infty")
    return text


def _expression_latex(value: str) -> str:
    expr=sympy.sympify(value.replace("^","**").replace("i","I"),locals={"log":sympy.log})
    return sympy.latex(expr)


def answer_to_latex(answer: str, answer_type: str) -> str:
    raw=answer.strip()
    if raw.casefold() in TEXT_ANSWERS:
        return rf"\text{{{raw}}}"
    if answer_type in {"interval","domain","range"}:
        return raw.replace("oo",r"\infty").replace(" U ",r"\cup ")
    if answer_type=="ordered_pair":
        return raw if raw.startswith("(") else f"({raw})"
    if answer_type=="ordered_pairs":
        return r",\ ".join(part.strip() for part in raw.split(";"))
    if answer_type=="equation" and "=" in raw:
        left,right=raw.split("=",1)
        try:
            return f"{_expression_latex(left)}={_expression_latex(right)}"
        except Exception:
            return normalize_math_fragment(raw)
    if answer_type=="multi_select":
        return rf"\text{{{raw}}}"
    try:
        return _expression_latex(raw)
    except Exception:
        return normalize_math_fragment(raw)


def _looks_like_math(fragment: str) -> bool:
    """Conservative test used to decide whether a prompt fragment should be rendered as LaTeX."""
    value=fragment.strip()
    if not value:
        return False
    math_markers=("\\frac","\\sqrt","\\log","\\ln","\\left","\\right","\\circ","\\pm","\\le","\\ge","^","_","=","<",">")
    return any(marker in value for marker in math_markers)


def prompt_parts(prompt: str) -> list[tuple[str,str]]:
    """
    Split professor wording from mathematical notation.

    Returns ordered (kind, content) pairs where kind is ``text`` or ``math``.
    Existing $...$/$$...$$ regions are preserved as math.  A trailing expression after a
    colon is also treated as math when it contains recognizable mathematical syntax.
    """
    text=re.sub(r"\s+"," ",prompt.replace("**","^")).strip()
    if not text:
        return []

    parts: list[tuple[str,str]]=[]
    pattern=re.compile(r"(\$\$.*?\$\$|\$.*?\$)")
    cursor=0
    for match in pattern.finditer(text):
        before=text[cursor:match.start()].strip()
        if before:
            parts.extend(_split_colon_math(before))
        token=match.group(0)
        content=token[2:-2] if token.startswith("$$") else token[1:-1]
        parts.append(("math",content.strip()))
        cursor=match.end()
    tail=text[cursor:].strip()
    if tail:
        parts.extend(_split_colon_math(tail))
    return parts


def _split_colon_math(text: str) -> list[tuple[str,str]]:
    if ":" in text:
        left,right=text.rsplit(":",1)
        if left.strip() and _looks_like_math(right):
            return [("text",left.strip()+":"),("math",right.strip())]
    if _looks_like_math(text) and not re.search(r"[A-Za-z]{4,}\s+[A-Za-z]{4,}",text):
        return [("math",text)]
    return [("text",text)]


def readable_prompt(prompt: str) -> str:
    """Plain-text fallback for logs/debugging. Student UI should use ``prompt_parts``."""
    return re.sub(r"\s+"," ",prompt.replace("**","^")).strip()


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [
        DisplayChoice(letter=letters[i],raw_answer=choice,latex=answer_to_latex(choice,answer_type))
        for i,choice in enumerate(choices)
    ]
