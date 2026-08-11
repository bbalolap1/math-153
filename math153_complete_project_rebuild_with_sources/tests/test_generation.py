from math153_tutor.practice_catalog import FAMILY_SPECS, generate_practice_problem
from math153_tutor.validation import validate_practice_answer


def test_all_families_generate_valid_answers():
    for index,fid in enumerate(FAMILY_SPECS):
        for variant in range(8):
            problem=generate_practice_problem(fid,100000+index*100+variant,variant)
            assert problem.source_refs
            assert problem.structural_signature
            assert validate_practice_answer(problem,problem.expected_answer).correct


def test_every_family_realizes_more_than_number_only_variation():
    from math153_tutor.complexity import normalized_prompt_structure
    from math153_tutor.practice_catalog import FAMILY_SPECS, family_variants

    low = []
    for family_id in FAMILY_SPECS:
        variants = family_variants(family_id, count=8, seed=15300)
        structures = {normalized_prompt_structure(p.prompt) for p in variants}
        if len(structures) < 2:
            low.append(family_id)
    assert low == []
