from math153_tutor.practice_catalog import generate_practice_problem
from math153_tutor.validation import validate_practice_answer


FAMILY_ID = "CH34-DOMAIN-RADICAL-RATIONAL"


def test_five_domain_variants_preserve_invariants_and_validate() -> None:
    problems = [generate_practice_problem(FAMILY_ID, 500 + index, 4 + index) for index in range(5)]
    assert len({problem.prompt for problem in problems}) == 5
    for problem in problems:
        assert r"\frac{\sqrt{" in problem.prompt
        assert problem.answer_type == "domain"
        assert problem.source_refs == ["USER-PROMPT-2026-08-08-DOMAIN-EXAMPLE"]
        assert len(problem.reasoning_checkpoints) >= 5
        assert validate_practice_answer(problem, problem.expected_answer).correct
        assert not validate_practice_answer(problem, problem.wrong_answer).correct


def test_same_seed_family_and_variant_are_reproducible() -> None:
    first = generate_practice_problem(FAMILY_ID, 808, 8)
    assert first == generate_practice_problem(FAMILY_ID, 808, 8)
