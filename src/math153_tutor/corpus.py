from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .source_manifest import SourceManifestEntry, classify, digest


TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}


class ExtractedSource(BaseModel):
    manifest: SourceManifestEntry
    raw_text: str = ""
    headings: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


def _questions(body: str) -> list[str]:
    """Extract bounded question blocks without pretending to understand their mathematics."""
    blocks = re.split(r"(?im)(?=^\s*(?:#{1,6}\s*)?(?:q(?:uestion)?\.?\s*)?\d+[.):]\s+)", body)
    return [block.strip() for block in blocks if block.strip() and "?" in block][:200]


def _formulas(body: str) -> list[str]:
    formulas = re.findall(r"\$\$(.+?)\$\$|\$(.+?)\$", body, re.DOTALL)
    return list(dict.fromkeys((display or inline).strip() for display, inline in formulas))


def extract_source_file(path: Path, source_root: Path) -> ExtractedSource:
    relative = path.relative_to(source_root).as_posix()
    kind, chapter, section = classify(path.name)
    is_text = path.suffix.casefold() in TEXT_SUFFIXES
    body = path.read_text(encoding="utf-8").strip() if is_text else ""
    headings = re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", body)
    questions = _questions(body)
    formulas = _formulas(body)
    topics = list(dict.fromkeys(headings))
    status: Literal["complete", "partial", "failed"] = "complete" if body else "partial"
    entry = SourceManifestEntry(
        source_id=f"SRC-{digest(path)[:12].upper()}",
        filename=path.name,
        relative_path=f"source/{relative}",
        source_kind=kind,
        document_type=kind,
        title=headings[0] if headings else path.stem,
        chapter=chapter,
        section=section,
        topic="; ".join(topics[:5]),
        subtopics="; ".join(topics[5:15]),
        questions_present=bool(questions),
        solutions_present="solution" in kind or "solution" in body.casefold(),
        worked_examples_present=bool(re.search(r"\b(?:worked example|example)\b", body, re.I)),
        graphs_present=bool(re.search(r"\bgraph\b|!\[", body, re.I)),
        formulas_present=bool(formulas),
        tables_present=bool(re.search(r"(?m)^\s*\|.+\|\s*$", body)),
        content_length=len(body),
        extraction_status=status,
        extracted_records=len(questions) + len(formulas),
        unresolved_items="Visual/OCR extraction required." if not is_text else "",
        binary_present=True,
        sha256=digest(path),
        verification_status="present_unreviewed",
        notes=(
            "Body read and structurally extracted; mathematical/source review is still required."
            if body
            else "Binary preserved; no text body was extracted."
        ),
    )
    return ExtractedSource(
        manifest=entry,
        raw_text=body,
        headings=headings,
        questions=questions,
        formulas=formulas,
        topics=topics,
    )


def ingest_source_corpus(source_root: Path) -> list[ExtractedSource]:
    """Read every source file without modifying the immutable corpus."""
    if not source_root.is_dir():
        return []
    return [
        extract_source_file(path, source_root)
        for path in sorted(source_root.rglob("*"))
        if path.is_file()
    ]
