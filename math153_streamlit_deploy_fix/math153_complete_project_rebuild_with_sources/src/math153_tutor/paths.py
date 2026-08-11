from __future__ import annotations

import os
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def learner_data_root() -> Path:
    configured = os.environ.get("MATH153_DATA_DIR")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT / "learner_data"


def content_root() -> Path:
    configured = os.environ.get("MATH153_CONTENT_DIR")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT / "content"


def sources_root() -> Path:
    """
    Canonical professor/course Markdown corpus. An environment override is preferred in
    deployments; repository-local `sources/` is the default.
    """
    configured = os.environ.get("MATH153_SOURCES_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    candidates = [
        REPOSITORY_ROOT / "sources",
        REPOSITORY_ROOT.parent / "sources",
        Path.cwd() / "sources",
    ]
    return next((p for p in candidates if p.exists()), candidates[0])


def source_manifest_path() -> Path:
    configured = os.environ.get("MATH153_SOURCE_MANIFEST")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT / "data" / "derived" / "source_manifest.json"


def ensure_runtime_dirs() -> None:
    learner_data_root().mkdir(parents=True, exist_ok=True)
