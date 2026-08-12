from math153_tutor.course_content import (
    COURSE_SECTIONS, PROBLEM_FAMILY_INDEX, source_coverage, validate_course_content
)


def test_canonical_course_depth():
    validate_course_content()
    assert len(COURSE_SECTIONS) >= 20
    assert len(PROBLEM_FAMILY_INDEX) >= 35
    assert source_coverage()["placeholder_source_refs"] == 0


def test_family_ids_unique():
    ids=list(PROBLEM_FAMILY_INDEX)
    assert len(ids)==len(set(ids))


def test_review_supported_sections_35_and_36_are_present():
    from math153_tutor.course_content import SECTION_INDEX
    assert "3.5" in SECTION_INDEX
    assert "3.6" in SECTION_INDEX
