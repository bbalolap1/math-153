from __future__ import annotations

import re

import sympy

from .models import ExecutionStep, PracticeProblem, TeachingSolution


_X = sympy.Symbol("x")


def _step(title: str, before: str, operation: str, why: str, after: str) -> ExecutionStep:
    return ExecutionStep(
        step_title=title,
        before_expression=before,
        operation=operation,
        why=why,
        after_expression=after,
    )


def _strip_math_text(value: str) -> str:
    return value.strip().strip("$").rstrip(".").replace("−", "-")


def _parse_expression(value: str):
    text=_strip_math_text(value)
    # Pull the right side from strings such as A(x)=-x^2+20x.
    if "=" in text:
        text=text.split("=",1)[1]
    text=text.replace("^","**")
    try:
        return sympy.expand(sympy.sympify(text,locals={"x":_X}))
    except Exception:
        return None


def _quadratic_optimization_steps(problem: PracticeProblem) -> list[ExecutionStep] | None:
    """Expand a quadratic maximum/minimum solution without skipping the vertex algebra."""
    searchable=" ".join([
        problem.prompt,
        problem.family_title,
        problem.worked_solution.rule,
        *problem.worked_solution.calculation,
    ]).casefold()
    if "quadratic" not in searchable or not any(word in searchable for word in ("maximum","minimum","vertex")):
        return None

    expr=None
    source_line=""
    for candidate in [problem.worked_solution.setup,*problem.worked_solution.calculation]:
        parsed=_parse_expression(candidate)
        if parsed is not None and sympy.Poly(parsed,_X).degree()==2:
            expr=parsed; source_line=candidate; break
    if expr is None:
        return None

    poly=sympy.Poly(expr,_X)
    a=poly.coeff_monomial(_X**2)
    b=poly.coeff_monomial(_X)
    c=poly.coeff_monomial(1)
    xv=sympy.simplify(-b/(2*a))
    yv=sympy.simplify(expr.subs(_X,xv))
    direction="downward" if a < 0 else "upward"
    optimum="maximum" if a < 0 else "minimum"

    # Prefer the named function used by the authored work, otherwise f(x).
    name_match=re.search(r"([A-Za-z])\s*\(x\)\s*=", source_line)
    fname=name_match.group(1) if name_match else "f"
    standard=f"{fname}(x)={sympy.sstr(expr).replace('**','^')}"

    return [
        _step(
            "Write the quadratic in standard form",
            problem.worked_solution.setup,
            "Expand or rewrite the model as ax^2+bx+c.",
            "The vertex formula uses the coefficients a and b from standard form.",
            standard,
        ),
        _step(
            "Identify the coefficients",
            standard,
            "Match the quadratic with ax^2+bx+c.",
            "These coefficient values are what go into the vertex formula.",
            f"a={a}, b={b}, c={c}",
        ),
        _step(
            "Choose the vertex because this is an optimization problem",
            f"a={a}",
            f"Read the sign of a: a={a}.",
            f"Because a is {'negative' if a < 0 else 'positive'}, the parabola opens {direction}; its vertex gives the {optimum} value.",
            f"x_vertex=-b/(2a)",
        ),
        _step(
            "Substitute a and b into the vertex formula",
            "x_vertex=-b/(2a)",
            f"Replace b with {b} and a with {a}.",
            "Do the substitution before simplifying so every number has a visible origin.",
            f"x_vertex=-({b})/(2({a}))",
        ),
        _step(
            "Simplify the vertex x-value",
            f"x_vertex=-({b})/(2({a}))",
            "Simplify the numerator and denominator, then divide.",
            "This gives the input where the quadratic reaches its optimum.",
            f"x_vertex={xv}",
        ),
        _step(
            "Substitute the vertex input back into the model",
            standard,
            f"Replace x with {xv}.",
            f"The question asks for the {optimum} output, not only the x-coordinate of the vertex.",
            f"{fname}({xv})=({sympy.sstr(expr).replace('**','^')})|x={xv}",
        ),
        _step(
            "Evaluate the quadratic",
            f"{fname}({xv})=({sympy.sstr(expr).replace('**','^')})|x={xv}",
            "Carry out the exponent, multiplication, and addition/subtraction in order.",
            "This produces the requested maximum or minimum quantity.",
            f"{fname}({xv})={yv}",
        ),
        _step(
            "Interpret the result in the original question",
            f"{fname}({xv})={yv}",
            "Attach the meaning and units from the context.",
            f"The model reaches its {optimum} when x={xv}; the requested {optimum} value is {yv}.",
            str(yv),
        ),
    ]


def _split_chain(value: str) -> list[str]:
    """Split authored equality chains into visible intermediate lines when safe."""
    text=value.strip()
    if text.count("=") < 2:
        return [text]
    parts=[p.strip() for p in text.split("=")]
    if any(not p for p in parts):
        return [text]
    left=parts[0]
    return [f"{left}={part}" for part in parts[1:]]


def _generic_steps(problem: PracticeProblem) -> list[ExecutionStep]:
    calc=problem.worked_solution.calculation
    before=problem.worked_solution.setup
    steps: list[ExecutionStep]=[]
    number=1
    for i,authored_after in enumerate(calc,1):
        checkpoint=(
            problem.reasoning_checkpoints[min(i-1,len(problem.reasoning_checkpoints)-1)]
            if problem.reasoning_checkpoints
            else problem.worked_solution.rule
        )
        for after in _split_chain(authored_after):
            steps.append(_step(
                f"Work line {number}",
                before,
                after,
                checkpoint,
                after,
            ))
            before=after
            number+=1
    return steps


def teaching_solution(problem: PracticeProblem) -> TeachingSolution:
    """
    Build a learner-facing solution that exposes the transitions the learner must reproduce.

    Source-authored work remains authoritative, but common structures are expanded when the
    authored calculation jumps over formula substitution or arithmetic that a learner needs
    to see.  The review screen should teach the path, not merely restate the final lines.
    """
    steps=_quadratic_optimization_steps(problem) or _generic_steps(problem)
    expected=max(1,problem.estimated_solution_steps)
    quality="detailed" if len(steps) >= expected else "insufficient_step_detail"
    return TeachingSolution(
        recognize=problem.family_title,
        decide=problem.worked_solution.inference,
        original_rule_or_formula=problem.worked_solution.rule,
        execute=steps,
        verify=problem.worked_solution.check,
        final_answer=problem.expected_answer,
        quality_status=quality,
    )


def detailed_solution_status(problem: PracticeProblem) -> str:
    return teaching_solution(problem).quality_status
