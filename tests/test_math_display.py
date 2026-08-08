from math153_tutor.math_display import (
    answer_to_latex,
    display_choices,
    normalize_math_fragment,
    readable_prompt,
)


def test_validator_syntax_becomes_familiar_latex() -> None:
    assert answer_to_latex("5*sqrt(2)", "radical") == "5 \\sqrt{2}"
    assert answer_to_latex("(2,-4)", "ordered_pair") == r"\left(2,\,-4\right)"
    assert answer_to_latex("-3,1", "solution_set") == r"\left\{-3,\;1\right\}"
    assert answer_to_latex("(-oo,2] U (5,oo)", "interval") == (
        r"(-\infty,2] \cup (5,\infty)"
    )


def test_prompt_normalization_removes_python_style_multiplication_and_powers() -> None:
    prompt = readable_prompt("Factor: $x**2+5*x+6$.")
    assert "**" not in prompt
    assert "*" not in prompt
    assert prompt == r"Factor: $x^2+5\,x+6$."


def test_choices_keep_raw_validator_answer_behind_latex_display() -> None:
    choices = display_choices(["4*x+(-9)", "0"], "expression")
    assert choices[0].raw_answer == "4*x+(-9)"
    assert choices[0].letter == "A"
    assert "\\left" not in choices[0].latex
    assert "x" in choices[0].latex


def test_choice_letters_preserve_underlying_option_order() -> None:
    raw = ["11", "22", "33", "44"]
    choices = display_choices(raw, "integer")
    assert [choice.letter for choice in choices] == ["A", "B", "C", "D"]
    assert [choice.raw_answer for choice in choices] == raw


def test_inequalities_and_exclusions_use_standard_symbols() -> None:
    assert normalize_math_fragment("2x-6>=0") == r"2x-6\ge 0"
    assert normalize_math_fragment("5x+10!=0") == r"5x+10\ne 0"
