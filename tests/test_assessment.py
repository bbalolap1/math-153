import pytest

from math153_tutor.assessment import (
    assessment_choices,
    build_assessment,
    complete_assessment,
    grade_question,
)
from math153_tutor.practice_catalog import CHAPTERS_12, CHAPTERS_34, CHAPTER_5, FOUNDATION
from math153_tutor.storage import LearningRecordRepository
from math153_tutor.models import RepairRecord
from math153_tutor.validation import validate_practice_answer


def test_assessment_build_grade_complete_and_reload(tmp_path) -> None:
    problems = build_assessment([CHAPTERS_12], count=5, seed=200)
    assert len(problems) == 5
    results = []
    for problem in problems:
        choices = assessment_choices(problem)
        assert len(choices) == 4
        assert problem.expected_answer in choices
        results.append(grade_question(problem, problem.expected_answer))

    record = complete_assessment("Quiz", ["Chapters 1–2"], results, duration_seconds=42)
    repository = LearningRecordRepository(tmp_path / "learning.sqlite3")
    repository.add_assessment(record)

    loaded = repository.get_assessment(record.assessment_id)
    assert loaded == record
    assert loaded.correct_count == 5
    assert loaded.accuracy == 1


def test_assessment_can_start_at_professor_and_transfer_layers() -> None:
    problems = build_assessment(
        [CHAPTERS_12], count=5, seed=200, variant_pool=[8, 6, 7, 9]
    )
    assert {problem.difficulty_layer.value for problem in problems} <= {"L5", "L6", "L7"}
    assert {problem.difficulty_layer.value for problem in problems} >= {"L5", "L6", "L7"}


def test_incorrect_question_retains_problem_answer_and_explanation() -> None:
    problem = build_assessment([CHAPTERS_12], count=1, seed=300)[0]
    result = grade_question(problem, problem.wrong_answer)

    assert result.correct is False
    assert result.selected_answer == problem.wrong_answer
    assert result.problem.expected_answer == problem.expected_answer
    assert result.problem.worked_solution.calculation


def test_repair_record_is_persistent(tmp_path) -> None:
    repository = LearningRecordRepository(tmp_path / "learning.sqlite3")
    repair = RepairRecord(
        assessment_id="quiz-1",
        problem_id="problem-1",
        family_id="CH12-LINEAR-EQUATIONS",
        rule_check_correct=True,
        transfer_problem_id="problem-2",
        transfer_correct=True,
    )

    repository.add_repair(repair)

    assert repository.list_repairs() == [repair]


@pytest.mark.parametrize("count", [1, 20, 21, 50])
def test_assessment_accepts_supported_question_counts(count: int) -> None:
    problems = build_assessment(
        [FOUNDATION, CHAPTERS_12, CHAPTERS_34, CHAPTER_5], count=count, seed=700
    )
    assert len(problems) == count
    assert len({problem.prompt for problem in problems}) == count
    assert all(problem.source_refs for problem in problems)
    assert all(validate_practice_answer(problem, problem.expected_answer).correct for problem in problems)
    assert all(problem.worked_solution.calculation for problem in problems)


def test_assessment_rejects_question_count_above_limit() -> None:
    with pytest.raises(ValueError, match="between 1 and 50"):
        build_assessment([CHAPTERS_12], count=51, seed=700)


def test_choice_display_order_is_stable_abcd() -> None:
    problem = build_assessment([CHAPTERS_12], count=1, seed=701)[0]
    from math153_tutor.math_display import display_choices

    displayed = display_choices(assessment_choices(problem), problem.answer_type)
    assert [choice.letter for choice in displayed] == ["A", "B", "C", "D"]
