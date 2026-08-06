from __future__ import annotations

import sys
import zipfile
from pathlib import Path


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError(f"Unsafe archive member: {member.filename}")
        archive.extractall(destination)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python extract_sources.py ARCHIVE.zip DESTINATION")
    safe_extract(Path(sys.argv[1]), Path(sys.argv[2]))
