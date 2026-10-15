from pathlib import Path

import pytest

from math153_tutor.markdown_loader import load_question_family


@pytest.mark.parametrize("path", sorted(Path("content").glob("chapter_*/*.md")))
def test_all_family_content_is_complete(path: Path) -> None:
    family = load_question_family(path)
    assert len(family.difficulty_ladder) >= 5
    assert family.source_refs
    assert family.expected_answer_presentation
