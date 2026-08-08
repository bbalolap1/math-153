from __future__ import annotations

import os
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def learner_data_root() -> Path:
    """Return a stable data directory, with an environment override for tests/deployments."""
    configured = os.environ.get("MATH153_DATA_DIR")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT / "learner_data"


def content_root() -> Path:
    return REPOSITORY_ROOT / "content"


def source_manifest_path() -> Path:
    return REPOSITORY_ROOT / "data" / "derived" / "source_manifest.csv"


def source_root() -> Path:
    return REPOSITORY_ROOT / "source"
