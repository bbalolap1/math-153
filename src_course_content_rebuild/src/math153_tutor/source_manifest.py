from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


DocumentType = Literal[
    "lecture", "activity", "quiz", "quiz_solution", "test", "test_solution",
    "review", "practice_final", "practice_final_solution", "unknown",
]


class ExtractedRecord(BaseModel):
    record_type: Literal["question", "example", "formula", "solution", "topic"]
    label: str
    content: str


class SourceManifestEntry(BaseModel):
    source_id: str
    actual_path: str
    document_type: DocumentType
    chapter_or_section: str = ""
    title: str
    topics: list[str] = Field(default_factory=list)
    question_count: int = 0
    solution_count: int = 0
    formula_count: int = 0
    content_length: int
    content_hash: str
    extraction_status: Literal["complete", "failed"]
    extracted_records: list[ExtractedRecord] = Field(default_factory=list)


QUESTION = re.compile(
    r"(?im)^(?:#{1,4}\s*)?(?P<label>(?:q(?:uestion)?\.?\s*)?\d+(?:[.)]|\b)[^\n]*)$"
)
FORMULA = re.compile(
    r"\$\$(.+?)\$\$|\\\[(.+?)\\\]|(?<![\$\\])\$(?![\$\d])(.+?)(?<!\$)\$(?!\$)",
    re.DOTALL,
)
HEADING = re.compile(r"(?m)^#{1,6}\s+(.+?)\s*$")
SECTION = re.compile(r"(?<!\d)([1-5]\.\d)(?!\d)")

TOPIC_TERMS = {
    "absolute value": ("absolute value",),
    "applied problems": ("applied problem", "rate problem", "mixture problem"),
    "complex numbers": ("complex number", "imaginary",),
    "completing the square": ("completing the square", "complete the square"),
    "compound interest": ("compound interest", "compounded"),
    "coordinate plane": ("coordinate", "midpoint", "distance formula"),
    "difference quotient": ("difference quotient",),
    "equations": ("solve the equation", "equations"),
    "exponential equations": ("exponential equation",),
    "exponential functions": ("exponential function", "growth", "decay"),
    "factoring": ("factor", "factoring"),
    "function composition": ("composite function", "composition", "f \\circ g"),
    "functions": ("function", "domain", "range"),
    "inequalities": ("inequalit", "interval notation"),
    "inverse functions": ("inverse function", "one-to-one"),
    "lines": ("slope", "equation of the line", "linear function"),
    "logarithmic equations": ("logarithmic equation", "solve and check"),
    "logarithms": ("logarithm", "logarithmic"),
    "polynomials": ("polynomial", "synthetic division", "zeros"),
    "quadratic equations": ("quadratic equation", "quadratic formula"),
    "radicals": ("radical", "square root", "rational exponent"),
    "rational expressions": ("rational expression", "fractional expression"),
}


def source_root(repository_root: Path) -> Path:
    """Return the authoritative, human-authored Markdown corpus root."""
    return repository_root / "sources"


def discover_markdown_sources(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def _document_type(path: Path) -> DocumentType:
    lower = path.as_posix().casefold()
    name = path.stem.casefold()
    if "/lectures/" in lower:
        return "lecture"
    if "/activities/" in lower:
        return "activity"
    if "/quizzes/" in lower:
        return "quiz_solution" if "solution" in name else "quiz"
    if "/tests/" in lower:
        if "solution" in name:
            return "test_solution"
        return "review" if "review" in name else "test"
    if "/final exam review/" in lower:
        return "practice_final_solution" if "with_solutions" in name else "practice_final"
    return "unknown"


def _title(text: str, path: Path) -> str:
    match = HEADING.search(text)
    return match.group(1).strip() if match else path.stem.replace("_", " ")


def _topics(text: str, title: str) -> list[str]:
    haystack = f"{title}\n{text}".casefold()
    found = [topic for topic, terms in TOPIC_TERMS.items() if any(term in haystack for term in terms)]
    return found or [title.casefold()]


def _records(text: str, document_type: DocumentType, topics: list[str]) -> list[ExtractedRecord]:
    records: list[ExtractedRecord] = []
    headings = list(HEADING.finditer(text))
    for index, match in enumerate(headings):
        heading = match.group(1).strip()
        if re.match(r"(?i)(?:q(?:uestion)?\.?\s*)?\d+", heading):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            records.append(ExtractedRecord(record_type="question", label=heading, content=text[match.end():end].strip()[:2000]))
        elif "example" in heading.casefold():
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            records.append(ExtractedRecord(record_type="example", label=heading, content=text[match.end():end].strip()[:2000]))
    if not any(record.record_type == "question" for record in records):
        for number, match in enumerate(QUESTION.finditer(text), 1):
            content = match.group("label")[:2000]
            administrative = (
                "do not open", "this is not the exam", "pages in this exam", "new exam from",
                "print your name", "mark your section", "hours to complete", "calculator is permitted",
                "scrap paper", "simplify all answers", "problems involving units",
            )
            if not any(phrase in content.casefold() for phrase in administrative):
                records.append(ExtractedRecord(record_type="question", label=f"question-{number}", content=content))
    for number, match in enumerate(FORMULA.finditer(text), 1):
        formula = next(group for group in match.groups() if group is not None).strip()
        if formula:
            records.append(ExtractedRecord(record_type="formula", label=f"formula-{number}", content=formula[:2000]))
    for topic in topics:
        records.append(ExtractedRecord(record_type="topic", label=topic, content=topic))
    if "solution" in document_type:
        questions = [record for record in records if record.record_type == "question"]
        if questions:
            records.extend(ExtractedRecord(record_type="solution", label=record.label, content=record.content) for record in questions)
        else:
            records.append(ExtractedRecord(record_type="solution", label="worked-solutions", content=text[:2000]))
    return records


def extract_markdown_source(path: Path, repository_root: Path) -> SourceManifestEntry:
    text = path.read_text(encoding="utf-8")
    title = _title(text, path)
    topics = _topics(text, title)
    records = _records(text, _document_type(path), topics)
    relative = path.relative_to(repository_root).as_posix()
    sections = SECTION.findall(f"{path.stem} {title}")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return SourceManifestEntry(
        source_id="SRC-MD-" + digest[:12].upper(),
        actual_path=relative,
        document_type=_document_type(path),
        chapter_or_section=sections[0] if sections else "cumulative",
        title=title,
        topics=topics,
        question_count=sum(record.record_type == "question" for record in records),
        solution_count=sum(record.record_type == "solution" for record in records),
        formula_count=sum(record.record_type == "formula" for record in records),
        content_length=len(text),
        content_hash=digest,
        extraction_status="complete",
        extracted_records=records,
    )


def build_markdown_manifest(repository_root: Path) -> list[SourceManifestEntry]:
    return [extract_markdown_source(path, repository_root) for path in discover_markdown_sources(source_root(repository_root))]


def write_manifest(entries: list[SourceManifestEntry], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix == ".json":
        output.write_text(json.dumps([entry.model_dump() for entry in entries], indent=2) + "\n", encoding="utf-8")
        return
    fields = list(SourceManifestEntry.model_fields)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for entry in entries:
            row = entry.model_dump()
            row["topics"] = json.dumps(row["topics"])
            row["extracted_records"] = json.dumps(row["extracted_records"])
            writer.writerow(row)


def read_manifest(path: Path) -> list[SourceManifestEntry]:
    if not path.is_file():
        return []
    if path.suffix == ".json":
        return [SourceManifestEntry.model_validate(row) for row in json.loads(path.read_text(encoding="utf-8"))]
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["topics"] = json.loads(row["topics"])
        row["extracted_records"] = json.loads(row["extracted_records"])
    return [SourceManifestEntry.model_validate(row) for row in rows]


def coverage_report(entries: list[SourceManifestEntry]) -> dict[str, object]:
    chapters = sorted({entry.chapter_or_section[0] + ".x" for entry in entries if SECTION.fullmatch(entry.chapter_or_section)})
    return {
        "chapters_detected": chapters,
        "sections_detected": sorted({entry.chapter_or_section for entry in entries if SECTION.fullmatch(entry.chapter_or_section)}),
        "document_types": dict(sorted(Counter(entry.document_type for entry in entries).items())),
        "topics": dict(sorted(Counter(topic for entry in entries for topic in entry.topics).items())),
    }


# Runtime family IDs remain controlled templates; this map replaces placeholder provenance.
FAMILY_TOPIC_MAP = {
    "F0-REAL-NUMBERS": ("complex numbers",), "F0-SIGNED-OPERATIONS": ("equations",),
    "F0-FRACTIONS": ("rational expressions",), "F0-ORDER-OPERATIONS": ("equations",),
    "F0-EXPONENT-RULES": ("exponential functions", "radicals"),
    "F0-ALGEBRA-VOCAB": ("equations", "functions"),
    "CH12-EXPRESSIONS": ("equations",),
    "CH12-LINEAR-EQUATIONS": ("equations", "applied problems"),
    "CH12-FACTORING": ("factoring",), "CH12-RATIONAL-EXPRESSIONS": ("rational expressions",),
    "CH12-RADICALS": ("radicals",), "CH12-RADICAL-EQUATIONS": ("radicals",),
    "CH12-QUADRATICS": ("quadratic equations", "completing the square"),
    "CH12-COMPLEX": ("complex numbers",), "CH12-ABSOLUTE": ("absolute value",),
    "CH12-INEQUALITIES": ("inequalities",), "CH34-COORDINATE": ("coordinate plane",),
    "CH34-LINES": ("lines",), "CH34-TABLES": ("functions", "lines"),
    "CH34-CIRCLES": ("completing the square",),
    "CH34-FUNCTIONS": ("functions",), "CH34-COMPOSITION": ("function composition",),
    "CH34-INVERSES": ("inverse functions",), "CH34-DIFFERENCE-QUOTIENT": ("difference quotient",),
    "CH34-QUADRATIC-FUNCTIONS": ("quadratic equations",), "CH34-POLYNOMIALS": ("polynomials",),
    "CH34-RATIONAL-FUNCTIONS": ("rational expressions", "functions"),
    "CH5-EXP-FUNCTIONS": ("exponential functions",), "CH5-EXP-MODELS": ("exponential functions",),
    "CH5-COMPOUND-INTEREST": ("compound interest",), "CH5-NATURAL-EXP": ("exponential functions",),
    "CH5-LOGARITHMS": ("logarithms",), "CH5-LOG-PROPERTIES": ("logarithms",),
    "CH5-LOG-EQUATIONS-FULL": ("logarithmic equations", "logarithms"),
    "CH5-EXP-EQUATIONS-FULL": ("exponential equations", "exponential functions"),
}


def build_family_source_map(entries: list[SourceManifestEntry], family_ids: list[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = defaultdict(list)
    for family_id in family_ids:
        wanted = FAMILY_TOPIC_MAP.get(family_id, ())
        mapping[family_id] = [entry.actual_path for entry in entries if set(wanted) & set(entry.topics)]
    return {key: sorted(set(value)) for key, value in mapping.items()}
