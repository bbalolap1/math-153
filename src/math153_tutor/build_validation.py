from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from .markdown_loader import load_question_family
from .practice_catalog import FAMILY_SPECS, generate_practice_problem
from .source_manifest import read_manifest
from .corpus import ingest_source_corpus
from .validation import validate_practice_answer


class BuildValidationReport(BaseModel):
    sources_discovered: int
    sources_read_successfully: int
    source_files_with_zero_content: int
    question_families_created: int
    templates_populated: int
    generated_example_questions: int
    generated_questions_validated: int
    empty_output_files: int
    unresolved_sources: int
    unused_source_files: int
    template_with_only_headings: int
    errors: list[str]

    @property
    def passed(self) -> bool:
        return not self.errors


def validate_build(repository_root: Path) -> BuildValidationReport:
    """Fail closed on empty/readless authored content or unvalidated generated examples."""
    content_files = sorted((repository_root / "content").glob("chapter_*/*.md"))
    readable_sources = [
        path for path in content_files if path.read_text(encoding="utf-8").strip()
    ]
    zero_content = len(content_files) - len(readable_sources)
    errors: list[str] = []
    corpus_root = repository_root / "source"
    corpus = ingest_source_corpus(corpus_root)
    if not corpus_root.is_dir():
        errors.append("authoritative source/ directory is absent")
    elif not corpus:
        errors.append("authoritative source/ directory contains no files")
    families = []
    for path in readable_sources:
        try:
            family = load_question_family(path)
        except (ValueError, OSError) as error:
            errors.append(f"{path.relative_to(repository_root)}: {error}")
            continue
        if not family.source_refs:
            errors.append(f"{path.relative_to(repository_root)}: family has no source_refs")
        families.append(family)

    heading_only = 0
    for path in readable_sources:
        body_lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("---") and not line.startswith("#")
        ]
        if not body_lines:
            heading_only += 1
            errors.append(f"{path.relative_to(repository_root)}: template contains only headings")

    generated = []
    validated = 0
    for family_id in FAMILY_SPECS:
        for variant in range(5):
            problem = generate_practice_problem(family_id, 91000 + variant, variant)
            generated.append(problem)
            if validate_practice_answer(problem, problem.expected_answer).correct:
                validated += 1
            else:
                errors.append(f"{problem.problem_id}: generated answer did not validate")
            if not problem.source_refs or not problem.worked_solution.calculation:
                errors.append(f"{problem.problem_id}: missing source or worked solution")

    output_roots = [repository_root / "data" / "derived", repository_root / "docs"]
    outputs = [path for root in output_roots for path in root.glob("*") if path.is_file()]
    empty_outputs = sum(path.stat().st_size == 0 for path in outputs)
    if zero_content:
        errors.append(f"{zero_content} source files have zero content")
    if empty_outputs:
        errors.append(f"{empty_outputs} derived output files are empty")

    manifest = read_manifest(repository_root / "data" / "derived" / "source_manifest.csv")
    unresolved = sum(not entry.binary_present for entry in manifest)
    unused = (
        sum(item.manifest.extracted_records == 0 for item in corpus)
        if corpus_root.is_dir()
        else unresolved
    )
    for item in corpus:
        if item.manifest.content_length == 0:
            errors.append(f"{item.manifest.relative_path}: manifest record has no extracted content")
    if unused:
        errors.append(f"{unused} source files produced no extracted records")
    return BuildValidationReport(
        sources_discovered=len(content_files),
        sources_read_successfully=len(readable_sources),
        source_files_with_zero_content=zero_content,
        question_families_created=len(families),
        templates_populated=len(families),
        generated_example_questions=len(generated),
        generated_questions_validated=validated,
        empty_output_files=empty_outputs,
        unresolved_sources=unresolved,
        unused_source_files=unused,
        template_with_only_headings=heading_only,
        errors=errors,
    )
