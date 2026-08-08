from pathlib import Path

from math153_tutor.build_validation import validate_build


ROOT = Path(__file__).parents[1]


def test_repository_build_has_no_empty_content_or_unvalidated_questions() -> None:
    report = validate_build(ROOT)
    assert report.passed, report.errors
    assert report.source_files_with_zero_content == 0
    assert report.empty_output_files == 0
    assert report.generated_example_questions == report.generated_questions_validated
    assert report.question_families_created >= 5
