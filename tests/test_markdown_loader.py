from pathlib import Path

import pytest

from math153_tutor.markdown_loader import load_question_family


def test_seed_family_loads() -> None:
    root = Path(__file__).parents[1]
    family = load_question_family(root / "content/chapter_05/logarithmic_equations.md")
    assert family.family_id == "CH5-LOG-EQUATIONS"
    assert len(family.difficulty_ladder) == 8


def test_missing_heading_names_file(tmp_path: Path) -> None:
    path = tmp_path / "broken.md"
    path.write_text("---\nfamily_id: BAD\n---\n# Purpose\nPresent\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"broken.md.*Professor Surface Construction"):
        load_question_family(path)
