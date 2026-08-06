from __future__ import annotations

from .models import Attempt


def progress(attempts: list[Attempt]) -> dict[str, float | bool]:
    """Summarize distinct evidence; never infer full mastery from a short session."""
    if not attempts:
        return {"recognition": 0.0, "first_decision": 0.0, "procedure": 0.0, "mastered": False}
    count = len(attempts)
    return {
        "recognition": sum(a.recognition_correct is True for a in attempts) / count,
        "first_decision": sum(a.first_decision_correct is True for a in attempts) / count,
        "procedure": sum(a.correct for a in attempts) / count,
        "mastered": False,
    }
