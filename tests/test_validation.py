from math153_tutor.generation import generate_problem
from math153_tutor.validation import validate_answer


def test_equivalent_solution_set_passes() -> None:
    problem = generate_problem("CH1-LINEAR-EQUATIONS", 153)
    assert validate_answer(problem, f"{{{problem.expected_answer}}}").correct


def test_incorrect_sign_fails() -> None:
    problem = generate_problem("CH1-LINEAR-EQUATIONS", 153)
    wrong = str(-int(problem.expected_answer))
    if wrong == problem.expected_answer:
        wrong = "999"
    assert not validate_answer(problem, wrong).correct


def test_log_extraneous_value_is_rejected() -> None:
    problem = generate_problem("CH5-LOG-EQUATIONS", 153)
    assert not validate_answer(problem, "-999").correct
