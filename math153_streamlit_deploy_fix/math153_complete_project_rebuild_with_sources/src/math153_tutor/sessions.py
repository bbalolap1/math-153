from __future__ import annotations

from .models import Attempt, ErrorCategory, GeneratedProblem
from .storage import AttemptRepository
from .validation import ValidationResult, validate_answer


def submit_attempt(
    repository: AttemptRepository,
    problem: GeneratedProblem,
    recognition: str,
    first_decision: str,
    final_answer: str,
    confidence: int,
    duration_seconds: int,
    self_reported_error: ErrorCategory|None=None,
) -> tuple[Attempt,ValidationResult]:
    result=validate_answer(problem,final_answer)
    recognition_correct=recognition==problem.correct_recognition
    first_correct=first_decision==problem.correct_first_decision
    inferred=[]
    if not recognition_correct: inferred.append(ErrorCategory.RECOGNITION)
    if not first_correct: inferred.append(ErrorCategory.FIRST_STEP)
    if not result.correct:
        inferred.append(ErrorCategory.DOMAIN if problem.critical_checks else ErrorCategory.ALGEBRA)
    attempt=Attempt(
        problem_id=problem.problem_id,family_id=problem.family_id,layer=problem.difficulty_layer,
        correct=result.correct,recognition_correct=recognition_correct,
        first_decision_correct=first_correct,critical_check_correct=None,
        error_categories=list(dict.fromkeys(inferred)),duration_seconds=duration_seconds,
        mode="professor",recognition_answer=recognition,first_decision_answer=first_decision,
        final_answer=final_answer,confidence=confidence,self_reported_error=self_reported_error,
    )
    repository.add(attempt)
    return attempt,result


def submit_assessment_attempt(
    repository: AttemptRepository,
    problem: GeneratedProblem,
    final_answer: str,
    duration_seconds: int,
) -> tuple[Attempt,ValidationResult]:
    result=validate_answer(problem,final_answer)
    inferred=[] if result.correct else [ErrorCategory.DOMAIN if problem.critical_checks else ErrorCategory.ALGEBRA]
    attempt=Attempt(
        problem_id=problem.problem_id,family_id=problem.family_id,layer=problem.difficulty_layer,
        correct=result.correct,error_categories=inferred,duration_seconds=duration_seconds,
        mode="assessment",final_answer=final_answer,
    )
    repository.add(attempt)
    return attempt,result
