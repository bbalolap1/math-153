from __future__ import annotations

import sys
from pathlib import Path

from math153_tutor.source_manifest import build_inventory_manifest, write_manifest


def main(registry_root: str, output: str, source_root: str | None = None) -> None:
    registries = sorted(Path(registry_root).glob("*_inventory.txt"))
    if not registries:
        raise ValueError(f"No inventory files found under {registry_root}")
    entries = build_inventory_manifest(
        registries, Path(source_root) if source_root is not None else None
    )
    write_manifest(entries, Path(output))


if __name__ == "__main__":
    if len(sys.argv) not in {3, 4}:
        raise SystemExit(
            "Usage: python scripts/build_source_manifest.py REGISTRY_DIR OUTPUT.csv [SOURCE_ROOT]"
        )
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
