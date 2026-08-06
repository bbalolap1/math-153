from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main(source_root: str, output: str) -> None:
    source = Path(source_root)
    rows = []
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        rows.append(
            {
                "source_id": f"SRC-{len(rows)+1:04d}",
                "relative_path": str(path.relative_to(source)),
                "extension": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
                "source_kind": "unclassified",
                "chapter": "",
                "section": "",
                "paired_solution": "",
                "visual_review_status": "pending",
                "notes": "",
            }
        )

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python build_source_manifest.py SOURCE_DIR OUTPUT.csv")
    main(sys.argv[1], sys.argv[2])
