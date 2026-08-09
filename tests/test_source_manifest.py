import json
from pathlib import Path

from math153_tutor.source_manifest import (
    build_family_source_map,
    build_markdown_manifest,
    coverage_report,
    discover_markdown_sources,
    extract_markdown_source,
    read_manifest,
    write_manifest,
)
from math153_tutor.practice_catalog import FAMILY_SPECS


def test_markdown_extraction_reads_body_and_records_evidence(tmp_path: Path) -> None:
    root = tmp_path
    path = root / "sources" / "quizzes" / "Quiz_5.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Quiz 5\n\n## Q.1\nSolve $x+2=4$.\n", encoding="utf-8")

    entry = extract_markdown_source(path, root)

    assert entry.actual_path == "sources/quizzes/Quiz_5.md"
    assert entry.extraction_status == "complete"
    assert entry.question_count == 1
    assert entry.formula_count == 1
    assert entry.content_length == len(path.read_text(encoding="utf-8"))
    assert entry.content_hash
    assert any(record.content == "Solve $x+2=4$." for record in entry.extracted_records)


def test_repository_corpus_is_complete_and_covers_every_chapter() -> None:
    root = Path(__file__).parents[1]
    paths = discover_markdown_sources(root / "sources")
    entries = build_markdown_manifest(root)

    assert len(paths) == len(entries) == 53
    assert all(entry.extraction_status == "complete" for entry in entries)
    assert coverage_report(entries)["chapters_detected"] == ["1.x", "2.x", "3.x", "4.x", "5.x"]
    quiz = next(entry for entry in entries if entry.actual_path == "sources/quizzes/Quiz_5.md")
    assert quiz.question_count > 0
    assert quiz.formula_count > 0
    assert quiz.content_length > 100


def test_manifest_round_trip_and_every_source_is_used(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    entries = build_markdown_manifest(root)
    output = tmp_path / "manifest.json"
    write_manifest(entries, output)
    assert read_manifest(output) == entries

    mapping = build_family_source_map(entries, list(FAMILY_SPECS))
    assert all(mapping.values())
    used = {path for refs in mapping.values() for path in refs}
    assert used == {entry.actual_path for entry in entries}
    assert json.loads(output.read_text(encoding="utf-8"))[0]["extracted_records"]
