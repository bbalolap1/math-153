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
    text=text.replace("**","^").replace("*","\\,")
    text=text.replace("oo",r"\infty")
    text=text.replace("Abs(",r"\left|")
    # Do not attempt lossy full prompt parsing here; math regions are rendered separately by the app.
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
    if answer_type=="equation":
        if "=" in raw:
            left,right=raw.split("=",1)
            try: return f"{_expression_latex(left)}={_expression_latex(right)}"
            except Exception: return normalize_math_fragment(raw)
    if answer_type=="multi_select":
        return rf"\text{{{raw}}}"
    try:
        return _expression_latex(raw)
    except Exception:
        return normalize_math_fragment(raw)


def readable_prompt(prompt: str) -> str:
    """
    Keep professor wording intact while cleaning storage-only syntax.
    Streamlit can render embedded $...$ LaTeX directly.
    """
    text=prompt.replace("**","^")
    text=re.sub(r"\s+"," ",text).strip()
    text=text.replace("\\text{",r"\text{")
    return text


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [
        DisplayChoice(letter=letters[i],raw_answer=choice,latex=answer_to_latex(choice,answer_type))
        for i,choice in enumerate(choices)
    ]
