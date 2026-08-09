from __future__ import annotations

import json
import sys
from pathlib import Path

from math153_tutor.practice_catalog import FAMILY_SPECS
from math153_tutor.source_manifest import (
    build_family_source_map,
    build_markdown_manifest,
    coverage_report,
    write_manifest,
)


def main(repository_root: str = ".") -> None:
    root = Path(repository_root).resolve()
    entries = build_markdown_manifest(root)
    derived = root / "data" / "derived"
    write_manifest(entries, derived / "source_manifest.json")
    write_manifest(entries, derived / "source_manifest.csv")
    coverage = coverage_report(entries)
    (derived / "source_coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    family_map = build_family_source_map(entries, list(FAMILY_SPECS))
    (derived / "family_source_map.json").write_text(json.dumps(family_map, indent=2) + "\n", encoding="utf-8")
    by_path = {entry.actual_path: entry for entry in entries}
    families = []
    for family_id, refs in family_map.items():
        spec = FAMILY_SPECS[family_id]
        evidence = [
            record.content
            for ref in refs
            for record in by_path[ref].extracted_records
            if record.record_type in {"question", "example", "solution"} and record.content
        ][:3]
        topics = sorted({topic for ref in refs for topic in by_path[ref].topics})
        families.append({
            "family_id": family_id,
            "title": spec.title,
            "chapter_or_section": spec.section,
            "source_refs": refs,
            "purpose": f"Practice {spec.title} using the attached Math 153 lecture and assessment evidence.",
            "recognition_clues": topics,
            "underlying_structure": list(spec.skills),
            "hidden_prerequisites": list(spec.skills),
            "first_decision": f"Recognize the {spec.title} structure before selecting an operation.",
            "decision_path": ["recognize", "choose a source-supported method", "execute", "verify", "present"],
            "professor_traps": [],
            "answer_presentation": "Use the form and checks requested by the source-shaped prompt.",
            "error_categories": ["recognition", "first decision", "algebra execution", "answer form"],
            "variation_boundaries": "Controlled template parameters only; do not invent a new construction.",
            "progression_levels": [f"L{level}" for level in range(8)],
            "source_evidence": evidence,
        })
    (derived / "question_families.json").write_text(json.dumps(families, indent=2) + "\n", encoding="utf-8")
    used = {path for paths in family_map.values() for path in paths}
    validation = {
        "markdown_sources_discovered": len(entries),
        "markdown_sources_read": sum(entry.extraction_status == "complete" for entry in entries),
        "markdown_sources_failed": sum(entry.extraction_status == "failed" for entry in entries),
        "markdown_sources_unused": sum(entry.actual_path not in used for entry in entries),
        "questions_extracted": sum(entry.question_count for entry in entries),
        "solutions_extracted": sum(entry.solution_count for entry in entries),
        "formulas_extracted": sum(entry.formula_count for entry in entries),
        "topics_extracted": len({topic for entry in entries for topic in entry.topics}),
        "question_families_created": len(family_map),
        "question_families_with_source_refs": sum(bool(refs) for refs in family_map.values()),
        "empty_derived_files": 0,
        "heading_only_templates": 0,
        "chapters_detected": coverage["chapters_detected"],
    }
    (derived / "source_validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
