from pathlib import Path

from math153_tutor.source_manifest import (
    build_inventory_manifest,
    classify,
    read_manifest,
    write_manifest,
)


def test_inventory_manifest_records_absent_binaries_and_pairs_sources(tmp_path: Path) -> None:
    inventory = tmp_path / "math_inventory.txt"
    inventory.write_text(
        "math153/1.1.pdf\nmath153/Quiz_1.pdf\nmath153/Quiz_1 Solution.pdf\n",
        encoding="utf-8",
    )

    entries = build_inventory_manifest([inventory])

    assert entries[0].source_kind == "lecture_section"
    assert entries[0].section == "1.1"
    assert all(not entry.binary_present for entry in entries)
    quiz = next(entry for entry in entries if entry.source_kind == "quiz")
    solution = next(entry for entry in entries if entry.source_kind == "quiz_solution")
    assert quiz.paired_source_id == solution.source_id
    assert solution.paired_source_id == quiz.source_id

    output = tmp_path / "manifest.csv"
    write_manifest(entries, output)
    assert "inventory_only" in output.read_text(encoding="utf-8")
    assert read_manifest(output) == entries


def test_manifest_classification_is_filename_evidence_only() -> None:
    assert classify("Version 2 (With Solutions).pdf")[0] == "exam_solution"
    assert classify("Screenshot 2026.png")[0] == "image"
