import pytest

from math153_tutor.generation import GENERATORS, generate_problem


@pytest.mark.parametrize("family_id", GENERATORS)
def test_generation_is_deterministic_and_complete(family_id: str) -> None:
    first = generate_problem(family_id, 153)
    assert first == generate_problem(family_id, 153)
    assert first.source_refs
    assert first.family_id == family_id
    assert first.difficulty_layer.value == "L2"
    assert first.variant_reason
    assert first.reasoning_checkpoints
    assert first.validator
