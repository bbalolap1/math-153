from __future__ import annotations

from datetime import timedelta

from .models import Attempt


def progress(attempts: list[Attempt]) -> dict[str, float | bool]:
    """Summarize distinct evidence; never infer full mastery from a short session."""
    if not attempts:
        return {"recognition": 0.0, "first_decision": 0.0, "procedure": 0.0, "mastered": False}
    recognition = [attempt.recognition_correct for attempt in attempts if attempt.recognition_correct is not None]
    first_decisions = [
        attempt.first_decision_correct
        for attempt in attempts
        if attempt.first_decision_correct is not None
    ]
    recognized_problems = {
        attempt.problem_id for attempt in attempts if attempt.recognition_correct is True
    }
    professor_decision = any(
        attempt.first_decision_correct is True and attempt.layer.value in {"L5", "L6", "L7"}
        for attempt in attempts
    )
    correct_variants = {attempt.problem_id for attempt in attempts if attempt.correct}
    critical_failure = any(attempt.critical_check_correct is False for attempt in attempts)
    earliest = min(attempt.created_at for attempt in attempts)
    delayed_timed_success = any(
        attempt.correct
        and attempt.layer.value == "L6"
        and attempt.created_at - earliest >= timedelta(days=1)
        for attempt in attempts
    )
    mastered = (
        len(recognized_problems) >= 3
        and professor_decision
        and len(correct_variants) >= 2
        and not critical_failure
        and delayed_timed_success
    )
    return {
        "recognition": sum(value is True for value in recognition) / len(recognition) if recognition else 0.0,
        "first_decision": (
            sum(value is True for value in first_decisions) / len(first_decisions)
            if first_decisions
            else 0.0
        ),
        "procedure": sum(a.correct for a in attempts) / len(attempts),
        "mastered": mastered,
    }


def assessment_evidence_status(
    *, correct_variants: int, representations: int, successful_repairs: int
) -> str:
    """Describe observed procedure/transfer evidence without inventing recognition mastery."""
    if correct_variants >= 2 and representations >= 2 and successful_repairs >= 1:
        return "transfer_ready; full mastery still needs recognition and first-decision evidence"
    if correct_variants >= 2:
        return "procedure_developing"
    return "insufficient_evidence"
