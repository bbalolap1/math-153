from __future__ import annotations

from .models import ExecutionStep, PracticeProblem, TeachingSolution


def _step(title: str, before: str, operation: str, why: str, after: str) -> ExecutionStep:
    return ExecutionStep(
        step_title=title,
        before_expression=before,
        operation=operation,
        why=why,
        after_expression=after,
    )


def teaching_solution(problem: PracticeProblem) -> TeachingSolution:
    """
    Convert the authored WorkedSolution into learner-facing execution detail without
    inventing a different mathematical method.
    """
    calc=problem.worked_solution.calculation
    before=problem.worked_solution.setup
    steps=[]
    for i,after in enumerate(calc,1):
        steps.append(_step(
            f"Step {i}",
            before,
            after,
            problem.reasoning_checkpoints[min(i-1,len(problem.reasoning_checkpoints)-1)]
            if problem.reasoning_checkpoints else problem.worked_solution.rule,
            after,
        ))
        before=after
    quality="detailed" if len(steps) >= max(1, problem.estimated_solution_steps - 1) else "insufficient_step_detail"
    return TeachingSolution(
        recognize=f"{problem.family_title}: {problem.worked_solution.family_reason}",
        decide=problem.worked_solution.inference,
        original_rule_or_formula=problem.worked_solution.rule,
        execute=steps,
        verify=problem.worked_solution.check,
        final_answer=problem.expected_answer,
        quality_status=quality,
    )


def detailed_solution_status(problem: PracticeProblem) -> str:
    return teaching_solution(problem).quality_status
