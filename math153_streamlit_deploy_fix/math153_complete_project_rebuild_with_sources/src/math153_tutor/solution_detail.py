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
    if "=" in text:
        text=text.split("=",1)[1]
    text=text.replace("^","**")
    try:
        return sympy.expand(sympy.sympify(text,locals={"x":_X}))
    except Exception:
        return None


def formula_hint(problem: PracticeProblem) -> tuple[str, str, str]:
    """Return a non-answer-revealing (title, formula/rule, first cue) hint."""
    text=" ".join((problem.family_id,problem.family_title,problem.prompt,problem.rule_or_formula)).casefold()

    if "quadratic" in text and any(w in text for w in ("maximum","minimum","optimization","vertex")):
        return (
            "Vertex formula",
            r"x_{\text{vertex}}=\frac{-b}{2a}",
            "Rewrite the model as ax² + bx + c, identify a and b, then use the vertex x-value before evaluating the function.",
        )
    if "quadratic" in text:
        return (
            "Quadratic formula",
            r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
            "First put the equation in ax² + bx + c = 0 form. If it factors cleanly, factoring may be faster.",
        )
    if "difference quotient" in text:
        return (
            "Difference quotient",
            r"\frac{f(x+h)-f(x)}{h}",
            "Compute f(x+h) carefully first, then subtract f(x), combine, and simplify before canceling h.",
        )
    if "slope" in text or "line equation" in text or "parallel" in text or "perpendicular" in text:
        return (
            "Slope / line formulas",
            r"m=\frac{y_2-y_1}{x_2-x_1},\qquad y-y_1=m(x-x_1)",
            "Find the required slope first. For perpendicular lines, use the negative reciprocal slope.",
        )
    if "distance" in text or "midpoint" in text:
        return (
            "Coordinate formulas",
            r"d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2},\qquad M=\left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)",
            "Identify the two points and substitute coordinates in the same order throughout.",
        )
    if "circle" in text:
        return (
            "Circle equation",
            r"(x-h)^2+(y-k)^2=r^2",
            "Identify the center (h,k) and radius r, or complete the square if the equation is expanded.",
        )
    if "composition" in text:
        return (
            "Function composition",
            r"(f\circ g)(x)=f(g(x))",
            "Evaluate or substitute into the inner function first, then use that result as the input of the outer function.",
        )
    if "exponential" in text or "interest" in text or "compound" in text:
        return (
            "Exponential model",
            r"A=P\left(1+\frac{r}{n}\right)^{nt}\quad\text{or}\quad A=Pe^{rt}",
            "Identify the initial amount, rate, compounding frequency, and time before choosing the model.",
        )
    if "log" in text:
        return (
            "Logarithm properties",
            r"\log_b(MN)=\log_bM+\log_bN,\quad \log_b\left(\frac{M}{N}\right)=\log_bM-\log_bN,\quad p\log_bM=\log_b(M^p)",
            "Match addition, subtraction, and coefficients to the product, quotient, and power rules. Keep log arguments positive.",
        )
    if "rational" in text and "equation" in text:
        return (
            "Rational-equation rule",
            r"\text{LCD}\times(\text{both sides})",
            "State excluded denominator values first, then multiply every term by the least common denominator.",
        )
    if "absolute" in text and "inequal" in text:
        return (
            "Absolute-value inequality",
            r"|u|<a\Rightarrow -a<u<a,\qquad |u|>a\Rightarrow u<-a\text{ or }u>a",
            "Isolate the absolute value first, then choose the AND or OR pattern from the inequality direction.",
        )

    rule=(problem.rule_or_formula or problem.worked_solution.rule or "Use the source-supported procedure for this problem family.").strip()
    return (
        "Rule / method cue",
        rule,
        problem.worked_solution.inference or "Identify the mathematical structure, then apply the matching procedure.",
    )


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
    """Build a learner-facing solution that exposes the transitions the learner must reproduce."""
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
