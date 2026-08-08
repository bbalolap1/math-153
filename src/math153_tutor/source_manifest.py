from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


SourceKind = Literal[
    "lecture_section",
    "professor_activity",
    "quiz",
    "quiz_solution",
    "test",
    "test_solution",
    "review_sheet",
    "exam",
    "exam_solution",
    "transcript",
    "notes",
    "image",
    "unknown",
]


class SourceManifestEntry(BaseModel):
    source_id: str
    filename: str
    relative_path: str
    source_kind: SourceKind
    document_type: str
    title: str
    chapter: str = ""
    section: str = ""
    topic: str = ""
    subtopics: str = ""
    questions_present: bool = False
    solutions_present: bool = False
    worked_examples_present: bool = False
    graphs_present: bool = False
    formulas_present: bool = False
    tables_present: bool = False
    content_length: int = 0
    extraction_status: Literal["complete", "partial", "failed"]
    extracted_records: int = 0
    unresolved_items: str = ""
    paired_source_id: str = ""
    binary_present: bool
    sha256: str = ""
    verification_status: Literal["inventory_only", "present_unreviewed", "reviewed"]
    notes: str = ""


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def classify(filename: str) -> tuple[SourceKind, str, str]:
    lower = filename.casefold()
    section = re.fullmatch(r"(\d+)\.(\d+)(?:-\d+)?\.pdf", filename, re.IGNORECASE)
    if section:
        return "lecture_section", section.group(1), f"{section.group(1)}.{section.group(2)}"
    if lower.endswith((".png", ".jpg", ".jpeg")):
        return "image", "", ""
    if "activity" in lower or "completing_the_square" in lower:
        return "professor_activity", "", ""
    if "quiz" in lower and "solution" in lower:
        return "quiz_solution", "", ""
    if "quiz" in lower:
        return "quiz", "", ""
    if "test" in lower and "solution" in lower:
        return "test_solution", "", ""
    if "review" in lower:
        return "review_sheet", "", ""
    if "test" in lower:
        return "test", "", ""
    if "version" in lower and "with solutions" in lower:
        return "exam_solution", "", ""
    if "version" in lower:
        return "exam", "", ""
    if "transcript" in lower:
        return "transcript", "", ""
    if "note" in lower:
        return "notes", "", ""
    return "unknown", "", ""


def _pair_key(filename: str) -> str:
    stem = Path(filename).stem.casefold()
    stem = re.sub(r"\b(without|with) solutions?\b", "", stem)
    stem = re.sub(r"\bsolutions?\b", "", stem)
    stem = re.sub(r"-\d+$", "", stem)
    return re.sub(r"[^a-z0-9]+", "", stem)


def build_inventory_manifest(
    inventory_paths: list[Path], source_root: Path | None = None
) -> list[SourceManifestEntry]:
    declared = sorted(
        {
            line.strip()
            for inventory in inventory_paths
            for line in inventory.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().endswith("/")
        }
    )
    rows: list[SourceManifestEntry] = []
    for index, relative in enumerate(declared, 1):
        filename = Path(relative).name
        kind, chapter, section = classify(filename)
        actual = source_root / relative if source_root else None
        present = bool(actual and actual.is_file())
        body = ""
        if (
            present
            and actual
            and actual.suffix.casefold() in {".md", ".txt", ".json", ".yaml", ".yml"}
        ):
            body = actual.read_text(encoding="utf-8").strip()
        extracted = bool(body)
        rows.append(
            SourceManifestEntry(
                source_id=f"SRC-{index:04d}",
                filename=filename,
                relative_path=relative,
                source_kind=kind,
                document_type=kind,
                title=Path(filename).stem,
                chapter=chapter,
                section=section,
                questions_present=(
                    "?" in body or bool(re.search(r"\b(?:question|problem)\b", body, re.I))
                ),
                solutions_present=(
                    "solution" in kind or bool(re.search(r"\bsolution\b", body, re.I))
                ),
                worked_examples_present=bool(
                    re.search(r"\b(?:worked example|example)\b", body, re.I)
                ),
                graphs_present=bool(re.search(r"\bgraph\b|!\[", body, re.I)),
                formulas_present=bool(re.search(r"\$[^$]+\$|\\frac|\\sqrt", body)),
                tables_present=bool(re.search(r"(?m)^\s*\|.+\|\s*$", body)),
                content_length=len(body),
                extraction_status=("complete" if extracted else "partial" if present else "failed"),
                extracted_records=0,
                unresolved_items=("Source binary is absent." if not present else "Extraction required."),
                binary_present=present,
                sha256=digest(actual) if present and actual else "",
                verification_status="present_unreviewed" if present else "inventory_only",
                notes=(
                    "Filename is inventoried, but the binary is absent; content and professor "
                    "construction cannot be verified."
                    if not present
                    else (
                        "Body extracted but not yet source-reviewed."
                        if extracted
                        else "Binary present but body extraction/visual review is incomplete."
                    )
                ),
            )
        )
    by_key: dict[str, list[SourceManifestEntry]] = {}
    for row in rows:
        by_key.setdefault(_pair_key(row.filename), []).append(row)
    for matches in by_key.values():
        questions = [row for row in matches if row.source_kind in {"quiz", "test", "exam"}]
        solutions = [
            row
            for row in matches
            if row.source_kind in {"quiz_solution", "test_solution", "exam_solution"}
        ]
        if questions and solutions:
            questions[0].paired_source_id = solutions[0].source_id
            solutions[0].paired_source_id = questions[0].source_id
    return rows


def write_manifest(entries: list[SourceManifestEntry], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(SourceManifestEntry.model_fields)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.model_dump())


def read_manifest(path: Path) -> list[SourceManifestEntry]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [SourceManifestEntry.model_validate(row) for row in csv.DictReader(handle)]
