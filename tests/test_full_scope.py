import pytest
import sympy

from math153_tutor.models import PracticeProblem
from math153_tutor.practice_catalog import (
    FAMILY_SPECS,
    PRESET_SESSIONS,
    build_session,
    family_variants,
    generate_practice_problem,
)
from math153_tutor.validation import validate_practice_answer


@pytest.mark.parametrize("family_id", FAMILY_SPECS)
def test_every_family_has_ten_working_variants(family_id: str) -> None:
    problems = family_variants(family_id)
    assert len(problems) == 10
    assert {problem.difficulty for problem in problems} == {
        "direct",
        "standard",
        "professor",
        "mixed",
    }
    assert len({problem.problem_id for problem in problems}) == 10
    for problem in problems:
        assert isinstance(problem, PracticeProblem)
        assert validate_practice_answer(problem, problem.expected_answer).correct
        assert not validate_practice_answer(problem, problem.wrong_answer).correct
        assert problem.worked_solution.rule
        assert problem.worked_solution.setup
        assert problem.worked_solution.calculation
        assert problem.worked_solution.final_answer == problem.expected_answer
        assert problem.worked_solution.check
        assert problem.source_type == "source_markdown_controlled_template"
        assert problem.source_refs
        assert problem.difficulty_layer.value in {f"L{index}" for index in range(8)}
        assert problem.representation
        assert problem.variant_reason
        assert problem.reasoning_checkpoints


@pytest.mark.parametrize("name", PRESET_SESSIONS)
def test_ready_made_session_has_exact_requested_count(name: str) -> None:
    count, family_ids = PRESET_SESSIONS[name]
    session = build_session(family_ids, count, seed=900)
    assert len(session) == count
    assert all(problem.family_id in family_ids for problem in session)


def test_session_selection_returns_requested_family() -> None:
    family_id = "CH34-TABLES"
    assert {p.family_id for p in build_session([family_id], 12)} == {family_id}


def test_interval_validator_enforces_endpoint_types() -> None:
    problem = generate_practice_problem("CH12-INEQUALITIES", 153, 0)
    assert validate_practice_answer(problem, problem.expected_answer).correct
    wrong_brackets = problem.expected_answer.translate(str.maketrans("()[]", "][)("))
    assert not validate_practice_answer(problem, wrong_brackets).correct


def test_rational_function_domain_excludes_hole_and_asymptote() -> None:
    problem = generate_practice_problem("CH34-RATIONAL-FUNCTIONS", 153, 0)
    assert validate_practice_answer(problem, problem.expected_answer).correct
    one_value_only = problem.expected_answer.split(",")[1]
    assert not validate_practice_answer(problem, one_value_only).correct


def test_requested_factored_and_radical_forms_are_enforced() -> None:
    factoring = generate_practice_problem("CH12-FACTORING", 153, 0)
    expanded = str(sympy.expand(sympy.sympify(factoring.expected_answer)))
    assert not validate_practice_answer(factoring, expanded).correct

    radical = generate_practice_problem("CH12-RADICALS", 153, 0)
    coefficient, radicand = radical.expected_answer.split("*sqrt(")
    unsimplified = f"sqrt({int(coefficient) ** 2 * int(radicand.rstrip(')'))})"
    assert not validate_practice_answer(radical, unsimplified).correct
