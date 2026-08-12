from __future__ import annotations

import re
import sympy
from pydantic import BaseModel

from .models import PracticeProblem


class StepCheck(BaseModel):
    valid: bool
    step_index: int
    normalized_line: str=""
    error_code: str|None=None
    explanation: str
    next_guidance: str|None=None


def solution_steps(problem: PracticeProblem) -> list[str]:
    return [problem.worked_solution.setup,*problem.worked_solution.calculation]


def _clean(value: str) -> str:
    return value.strip().strip("$").replace("^","**").replace("−","-")


def _equivalent(left: str, right: str) -> bool:
    try:
        if "=" in left and "=" in right:
            l1,l2=left.split("=",1); r1,r2=right.split("=",1)
            le=sympy.expand(sympy.sympify(_clean(l1))-sympy.sympify(_clean(l2)))
            rexp=sympy.expand(sympy.sympify(_clean(r1))-sympy.sympify(_clean(r2)))
            if rexp==0: return le==0
            ratio=sympy.simplify(le/rexp)
            return bool(ratio!=0 and not ratio.free_symbols)
        return sympy.simplify(sympy.sympify(_clean(left))-sympy.sympify(_clean(right)))==0
    except Exception:
        return re.sub(r"\s+","",left)==re.sub(r"\s+","",right)


def check_step(problem: PracticeProblem, learner_line: str, step_index: int) -> StepCheck:
    steps=solution_steps(problem)
    if not learner_line.strip():
        return StepCheck(valid=False,step_index=step_index,error_code="empty_step",
                         explanation="Write the mathematical line you reached.",
                         next_guidance=problem.worked_solution.inference)
    # Do not require the learner to copy the official path exactly. Accept equivalence
    # with the target step, while giving source-grounded next guidance when it differs.
    target_index=min(max(step_index,0),len(steps)-1)
    target=steps[target_index]
    valid=_equivalent(learner_line,target)
    return StepCheck(
        valid=bool(valid),
        step_index=target_index,
        normalized_line=_clean(learner_line),
        error_code=None if valid else "not_equivalent_to_expected_checkpoint",
        explanation="Equivalent step." if valid else "This line does not match the expected mathematical state for this checkpoint.",
        next_guidance=None if valid else (
            problem.reasoning_checkpoints[target_index]
            if target_index < len(problem.reasoning_checkpoints)
            else problem.worked_solution.rule
        ),
    )
