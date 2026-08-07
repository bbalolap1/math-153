from math153_tutor.assessment import (
    assessment_choices,
    build_assessment,
    complete_assessment,
    grade_question,
)
from math153_tutor.practice_catalog import CHAPTERS_12
from math153_tutor.storage import LearningRecordRepository
from math153_tutor.models import RepairRecord


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
