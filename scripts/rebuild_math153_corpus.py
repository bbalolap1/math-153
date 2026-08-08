from __future__ import annotations

import json

from math153_tutor.corpus import ingest_source_corpus
from math153_tutor.paths import REPOSITORY_ROOT
from math153_tutor.source_manifest import write_manifest


if __name__ == "__main__":
    source_root = REPOSITORY_ROOT / "source"
    extracted = ingest_source_corpus(source_root)
    if not source_root.is_dir():
        raise SystemExit("Build failed: authoritative source/ directory is absent.")
    write_manifest(
        [source.manifest for source in extracted],
        REPOSITORY_ROOT / "data" / "derived" / "source_manifest.csv",
    )
    report = {
        "source_files": len(extracted),
        "markdown_files": sum(item.manifest.filename.casefold().endswith(".md") for item in extracted),
        "complete": sum(item.manifest.extraction_status == "complete" for item in extracted),
        "partial": sum(item.manifest.extraction_status == "partial" for item in extracted),
        "extracted_questions": sum(len(item.questions) for item in extracted),
        "extracted_formulas": sum(len(item.formulas) for item in extracted),
    }
    print(json.dumps(report, indent=2))
    if not extracted or any(item.manifest.extraction_status != "complete" for item in extracted):
        raise SystemExit(1)
