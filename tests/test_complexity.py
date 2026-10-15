from collections import Counter

from math153_tutor.assessment import build_assessment
from math153_tutor.complexity import PROFILES, normalized_prompt_structure, profile_layers
from math153_tutor.practice_catalog import FAMILY_SPECS, family_variants


def test_final_exam_profile_has_required_reasoning_distribution() -> None:
    layers = profile_layers("Final Exam Challenge", 50)
    counts = Counter(layer.value for layer in layers)
    assert len(layers) == 50
    assert sum(count for level, count in counts.items() if int(level[1]) >= 4) >= 25
    assert counts["L6"] + counts["L7"] >= 10


def test_every_profile_is_available_and_count_independent() -> None:
    assert set(PROFILES) == {
        "Foundation", "Direct Practice", "Mixed Practice", "Professor Style",
        "Test Review", "Final Exam Challenge",
    }
    assert len(profile_layers("Foundation", 5)) == 5
    assert len(profile_layers("Foundation", 50)) == 50


def test_50_question_final_has_metadata_distribution_and_no_duplicates() -> None:
    scopes = sorted({spec.group for spec in FAMILY_SPECS.values()})
    questions = build_assessment(
        scopes, 50, 91530, complexity_profile="Final Exam Challenge"
    )
    assert len({problem.prompt for problem in questions}) == 50
    assert len({problem.family_id for problem in questions}) == len(FAMILY_SPECS)
    assert max(Counter(problem.family_id for problem in questions).values()) == 2
    assert all(problem.structural_signature and problem.structural_variant_type for problem in questions)
    assert all(problem.complexity_level == problem.difficulty_layer for problem in questions)
    assert sum(problem.requires_multiple_methods for problem in questions) >= 25
    assert len({normalized_prompt_structure(problem.prompt) for problem in questions}) >= 35


def test_difference_quotient_has_source_supported_structural_variants() -> None:
    variants = family_variants("CH34-DIFFERENCE-QUOTIENT")
    structures = {normalized_prompt_structure(problem.prompt) for problem in variants}
    assert len(structures) >= 4
    assert any("x^3" in problem.prompt for problem in variants)
    assert any("find $f(x+h)$" in problem.prompt.casefold() for problem in variants)
