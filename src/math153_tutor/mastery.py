from __future__ import annotations

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
    return {
        "recognition": sum(value is True for value in recognition) / len(recognition) if recognition else 0.0,
        "first_decision": (
            sum(value is True for value in first_decisions) / len(first_decisions)
            if first_decisions
            else 0.0
        ),
        "procedure": sum(a.correct for a in attempts) / len(attempts),
        "mastered": False,
    }
