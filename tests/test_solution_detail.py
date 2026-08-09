import pytest

from math153_tutor.practice_catalog import FAMILY_SPECS, generate_practice_problem
from math153_tutor.solution_detail import detailed_solution_status, teaching_solution


@pytest.mark.parametrize("family_id", FAMILY_SPECS)
def test_every_family_has_detailed_teaching_execution(family_id: str) -> None:
    problem = generate_practice_problem(family_id, 81000, 0)
    solution = teaching_solution(problem)
    assert solution.quality_status == "detailed"
    assert len(solution.execute) >= 4
    assert solution.final_answer == problem.expected_answer


def test_quality_check_flags_hidden_or_missing_execution() -> None:
    assert detailed_solution_status([]) == "insufficient_step_detail"
