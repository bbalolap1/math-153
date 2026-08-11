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


def _repair_common_storage_math(value: str) -> str:
    """Repair common generated/storage notation before display; never changes the intended operation."""
    text=value.strip()
    # Strip markdown emphasis markers that were accidentally used around variables/tokens.
    text=text.replace("*", "")
    text=text.replace("**", "^")
    text=text.replace("−", "-")
    # Normalize common function names.
    text=re.sub(r"(?<!\\)\bln\b", r"\\ln", text)
    text=re.sub(r"(?<!\\)\blog\b", r"\\log", text)
    text=re.sub(r"(?<!\\)\bsqrt\b", r"\\sqrt", text)
    # Repair the common flattened frac pattern: frac{a}{b} or fracab where braces survived poorly.
    text=text.replace("\\frac", "frac")
    text=re.sub(r"\bfrac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"\\frac{\1}{\2}", text)
    # Very conservative repair for patterns like frac1x and frac52.
    text=re.sub(r"\bfrac\s*([A-Za-z0-9]+)\s*([A-Za-z])\b", r"\\frac{\1}{\2}", text)
    text=re.sub(r"\bfrac\s*([0-9])\s*([0-9])\b", r"\\frac{\1}{\2}", text)
    text=text.replace("oo", r"\infty")
    return text


def normalize_math_fragment(value: str) -> str:
    return _repair_common_storage_math(value)


def _expression_latex(value: str) -> str:
    repaired=_repair_common_storage_math(value)
    # SymPy expects Python syntax, not LaTeX. Only send plain algebraic strings through sympify.
    if "\\" in repaired:
        return repaired
    expr=sympy.sympify(repaired.replace("^","**").replace("i","I"),locals={"ln":sympy.log,"log":sympy.log})
    return sympy.latex(expr)


def answer_to_latex(answer: str, answer_type: str) -> str:
    raw=answer.strip()
    if raw.casefold() in TEXT_ANSWERS:
        return rf"\text{{{raw}}}"
    if answer_type in {"interval","domain","range"}:
        return _repair_common_storage_math(raw).replace(" U ",r"\cup ")
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
    value=_repair_common_storage_math(fragment)
    if not value:
        return False
    math_markers=("\\frac","\\sqrt","\\log","\\ln","\\left","\\right","\\circ","\\pm","\\le","\\ge","^","_","=","<",">")
    return any(marker in value for marker in math_markers)


def prompt_parts(prompt: str) -> list[tuple[str,str]]:
    """Split professor wording from mathematics and repair display-only storage notation."""
    text=re.sub(r"\s+"," ",prompt).strip()
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
        parts.append(("math",_repair_common_storage_math(content)))
        cursor=match.end()
    tail=text[cursor:].strip()
    if tail:
        parts.extend(_split_colon_math(tail))
    return parts


def _split_colon_math(text: str) -> list[tuple[str,str]]:
    if ":" in text:
        left,right=text.rsplit(":",1)
        if left.strip() and _looks_like_math(right):
            return [("text",left.strip()+":"),("math",_repair_common_storage_math(right))]
    if _looks_like_math(text) and not re.search(r"[A-Za-z]{4,}\s+[A-Za-z]{4,}",text):
        return [("math",_repair_common_storage_math(text))]
    return [("text",text.replace("*", ""))]


def readable_prompt(prompt: str) -> str:
    return re.sub(r"\s+"," ",prompt.replace("*","")).strip()


def display_choices(choices: list[str], answer_type: str) -> list[DisplayChoice]:
    letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [DisplayChoice(letter=letters[i],raw_answer=choice,latex=answer_to_latex(choice,answer_type)) for i,choice in enumerate(choices)]
