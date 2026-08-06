from math153_tutor.generation import generate_problem
from math153_tutor.mastery import progress
from math153_tutor.sessions import submit_attempt
from math153_tutor.storage import AttemptRepository


def test_complete_attempt_is_stored_and_updates_evidence(tmp_path) -> None:
    problem = generate_problem("CH5-EXP-EQUATIONS", 10)
    repository = AttemptRepository(tmp_path / "attempts.sqlite3")
    attempt, result = submit_attempt(
        repository, problem, problem.correct_recognition, problem.correct_first_decision,
        problem.expected_answer, 4, 90,
    )
    assert result.correct
    assert repository.list() == [attempt]
    scores = progress(repository.list())
    assert scores["recognition"] == 1
    assert scores["first_decision"] == 1
    assert scores["procedure"] == 1
    assert scores["mastered"] is False
