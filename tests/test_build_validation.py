from pathlib import Path

from math153_tutor.build_validation import validate_build


ROOT = Path(__file__).parents[1]


def test_repository_build_fails_closed_when_authoritative_corpus_is_absent() -> None:
    report = validate_build(ROOT)
    assert not report.passed
    assert "authoritative source/ directory is absent" in report.errors
    assert report.source_files_with_zero_content == 0
    assert report.empty_output_files == 0
    assert report.generated_example_questions == report.generated_questions_validated
    assert report.question_families_created >= 5
    assert report.template_with_only_headings == 0
