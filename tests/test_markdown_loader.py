from pathlib import Path

from math153_tutor.markdown_loader import load_question_family


def test_seed_family_loads() -> None:
    root = Path(__file__).parents[1]
    family = load_question_family(root / "content/chapter_05/logarithmic_equations.md")
    assert family.family_id == "CH5-LOG-EQUATIONS"
    assert family.chapter == 5
    assert "positive" in family.underlying_mathematical_structure.lower()
