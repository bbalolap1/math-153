from datetime import UTC, datetime, timedelta

from math153_tutor.distractors import meaningful_distractors
from math153_tutor.graph_questions import INTERCEPT_QUESTION, GraphPoint, validate_graph_points
from math153_tutor.mastery import progress
from math153_tutor.models import Attempt, DifficultyLayer
from math153_tutor.practice_catalog import generate_practice_problem
from math153_tutor.step_engine import check_step


def test_distractors_are_meaningful_and_validator_rejects_them() -> None:
    problem = generate_practice_problem("CH34-QUADRATIC-FUNCTIONS", 153, 0)
    distractors = meaningful_distractors(problem)
    assert {item.error_pattern for item in distractors} >= {
        "reversed the coordinates",
        "y-sign error",
    }
    assert all("999999" not in item.answer for item in distractors)


def test_step_engine_accepts_equivalent_equation_and_rejects_invalid_line() -> None:
    problem = generate_practice_problem("CH5-EXP-EQUATIONS-FULL", 153, 3)
    accepted = check_step(problem, "3^x=3^2", 0)
    rejected = check_step(problem, "x=999", 0)
    assert accepted.valid
    assert accepted.next_guidance == "x=2"
    assert not rejected.valid
    assert rejected.error_code == "invalid_transformation"


def test_graph_point_validator_requires_exact_coordinate_set() -> None:
    correct = {GraphPoint(x=-2, y=0), GraphPoint(x=2, y=0)}
    assert validate_graph_points(INTERCEPT_QUESTION, correct)
    assert not validate_graph_points(INTERCEPT_QUESTION, {GraphPoint(x=0, y=-4)})


def test_mastery_can_be_earned_only_with_complete_delayed_evidence() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    attempts = []
    for index in range(3):
        attempts.append(
            Attempt(
                problem_id=f"p-{index}",
                family_id="family",
                layer=DifficultyLayer.PROFESSOR,
                correct=True,
                recognition_correct=True,
                first_decision_correct=True,
                duration_seconds=30,
                recognition_answer="family",
                first_decision_answer="valid",
                final_answer="1",
                confidence=4,
                created_at=start + timedelta(hours=index),
            )
        )
    attempts.append(
        attempts[0].model_copy(
            update={
                "problem_id": "timed-delayed",
                "layer": DifficultyLayer.TIMED,
                "created_at": start + timedelta(days=2),
            }
        )
    )
    assert progress(attempts)["mastered"] is True
