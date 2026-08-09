from __future__ import annotations

import re

from .models import ExecutionStep, PracticeProblem, TeachingSolution


def _step(title: str, before: str, operation: str, why: str, after: str) -> ExecutionStep:
    return ExecutionStep(
        step_title=title,
        before_expression=before,
        operation=operation,
        why=why,
        after_expression=after,
    )


def _difference_quotient(problem: PracticeProblem) -> list[ExecutionStep]:
    match = re.search(r"f\(x\)=([+-]?\d+)x\^2\+([+-]?\d+)x\+([+-]?\d+)", problem.prompt)
    if not match:
        return []
    a, b, c = map(int, match.groups())
    f = f"{a}x^2+({b})x+({c})"
    substituted = f"{a}(x+h)^2+({b})(x+h)+({c})"
    square_expanded = f"{a}(x^2+2xh+h^2)+({b})(x+h)+({c})"
    distributed = f"{a}x^2+{2*a}xh+{a}h^2+({b})x+({b})h+({c})"
    quotient = rf"\frac{{({distributed})-({f})}}{{h}}"
    signs = rf"\frac{{{distributed}-{a}x^2-({b})x-({c})}}{{h}}"
    combined = rf"\frac{{{2*a}xh+{a}h^2+({b})h}}{{h}}"
    factored = rf"\frac{{h({2*a}x+{a}h+({b}))}}{{h}}"
    answer = f"{2*a}x+{a}h+({b})"
    return [
        _step("Write the original function", "f(x)", "Copy the given function exactly.", "The difference quotient uses both f(x+h) and f(x).", f),
        _step("Substitute x+h", f, "Replace every x by (x+h).", "Function substitution requires the entire input to replace x.", substituted),
        _step("Expand the square", substituted, "Use (x+h)^2=x^2+2xh+h^2.", "The binomial-square identity expands one grouped power.", square_expanded),
        _step("Distribute coefficients", square_expanded, f"Multiply {a} and {b} through their parentheses.", "The distributive property applies a coefficient to every enclosed term.", distributed),
        _step("Substitute into the quotient", "[f(x+h)-f(x)]/h", "Insert the expanded f(x+h) and the original f(x).", "Both function values must be present before subtraction.", quotient),
        _step("Distribute the subtraction sign", quotient, "Multiply every term of f(x) by -1.", "A minus sign outside parentheses changes every enclosed sign.", signs),
        _step("Combine like terms", signs, "Cancel opposite x², x, and constant terms.", "Only terms with identical variable factors may combine.", combined),
        _step("Factor h", combined, "Factor h from every numerator term.", "Each numerator term contains a common factor h.", factored),
        _step("Cancel h", factored, "Cancel the common nonzero factor h.", "The difference quotient assumes h≠0, so division by h is allowed.", answer),
    ]


def _generic_steps(problem: PracticeProblem) -> list[ExecutionStep]:
    solution = problem.worked_solution
    calculations = solution.calculation or [solution.final_answer]
    steps = [
        _step(
            "State the original rule or formula",
            problem.prompt,
            "Identify the family rule before changing the expression.",
            "Naming the rule prevents an unsupported algebraic move.",
            solution.rule,
        ),
        _step(
            "Substitute the given values",
            solution.rule,
            "Replace the rule's variables with the values or expressions from the prompt.",
            "Substitution preserves equality when every occurrence is replaced consistently.",
            solution.setup,
        ),
    ]
    before = solution.setup
    for index, calculation in enumerate(calculations, 1):
        steps.append(
            _step(
                f"Perform algebraic transformation {index}",
                before,
                "Apply one indicated arithmetic, algebraic, factoring, or simplification operation.",
                "The family rule permits this transformation while preserving the requested value or solution set.",
                calculation,
            )
        )
        before = calculation
    steps.append(
        _step(
            "Check restrictions and requested form",
            before,
            "Check the original prompt, domain restrictions, endpoint types, and required answer form.",
            "A transformed expression is acceptable only when it remains valid in the original problem.",
            solution.check,
        )
    )
    return steps


def teaching_solution(problem: PracticeProblem) -> TeachingSolution:
    steps = _difference_quotient(problem) if problem.family_id == "CH34-DIFFERENCE-QUOTIENT" else _generic_steps(problem)
    status = detailed_solution_status(steps)
    return TeachingSolution(
        recognize=problem.worked_solution.family_reason,
        decide=problem.worked_solution.rule,
        original_rule_or_formula=problem.worked_solution.rule,
        execute=steps,
        verify=problem.worked_solution.check,
        final_answer=problem.expected_answer,
        quality_status=status,
    )


def detailed_solution_status(steps: list[ExecutionStep]) -> str:
    if len(steps) < 4:
        return "insufficient_step_detail"
    for step in steps:
        if not all(
            value.strip()
            for value in (
                step.step_title,
                step.before_expression,
                step.operation,
                step.why,
                step.after_expression,
            )
        ):
            return "insufficient_step_detail"
    return "detailed"
