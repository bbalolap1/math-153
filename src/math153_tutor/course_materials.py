from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class AddedCourseMaterial:
    path: Path
    title: str
    section: str
    source_type: str
    created_at: str
    body: str


FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _safe_fragment(value: str) -> str:
    fragment = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return fragment[:48] or "material"


def save_course_material(
    root: str | Path, *, title: str, section: str, source_type: str, body: str,
) -> Path:
    """Persist user-added course material as canonical Markdown."""
    if not body.strip():
        raise ValueError("Course material cannot be empty.")
    directory = Path(root)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{stamp}-{_safe_fragment(title)}.md"
    document = (
        "---\n"
        f'title: "{title.replace(chr(34), chr(39))}"\n'
        f'section: "{section.replace(chr(34), chr(39))}"\n'
        f'source_type: "{source_type.replace(chr(34), chr(39))}"\n'
        f'created_at: "{stamp}"\n'
        "---\n\n"
        f"{body.strip()}\n"
    )
    path.write_text(document, encoding="utf-8")
    return path


def list_course_materials(root: str | Path) -> list[AddedCourseMaterial]:
    """Read user-added Markdown without treating it as verified professor source material."""
    materials: list[AddedCourseMaterial] = []
    for path in sorted(Path(root).glob("*.md"), reverse=True):
        text = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        if not match:
            continue
        metadata = {}
        for line in match.group(1).splitlines():
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = value.strip().strip('"')
        materials.append(AddedCourseMaterial(
            path=path,
            title=metadata.get("title", path.stem),
            section=metadata.get("section", "Unassigned"),
            source_type=metadata.get("source_type", "Other"),
            created_at=metadata.get("created_at", ""),
            body=text[match.end():].strip(),
        ))
    return materials
