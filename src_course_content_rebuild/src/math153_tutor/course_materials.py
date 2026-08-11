from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel


class AddedCourseMaterial(BaseModel):
    path: Path
    source_id: str
    title: str
    course: str = "Math 153"
    section: str
    topic: str
    source_type: str
    verification_status: str = "learner_added_unverified"
    created_at: str
    body: str


FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _safe_fragment(value: str) -> str:
    fragment = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return fragment[:48] or "material"


def save_course_material(
    root: str | Path,
    *,
    title: str,
    section: str,
    source_type: str,
    body: str,
    topic: str = "General",
    course: str = "Math 153",
) -> Path:
    """Persist the untouched learner body with explicit unverified provenance metadata."""
    if not body.strip():
        raise ValueError("Course material cannot be empty.")
    directory = Path(root)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    source_id = f"LEARNER-{stamp}"
    path = directory / f"{stamp}-{_safe_fragment(title)}.md"
    metadata = {
        "source_id": source_id,
        "title": title,
        "course": course,
        "section": section,
        "topic": topic,
        "source_type": source_type,
        "verification_status": "learner_added_unverified",
        "created_at": stamp,
    }
    front_matter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{front_matter}\n---\n\n{body.strip()}\n", encoding="utf-8")
    return path


def list_course_materials(root: str | Path) -> list[AddedCourseMaterial]:
    """Parse learner Markdown without promoting it to verified professor material."""
    materials: list[AddedCourseMaterial] = []
    for path in sorted(Path(root).glob("*.md"), reverse=True):
        text = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        if not match:
            continue
        metadata = yaml.safe_load(match.group(1)) or {}
        materials.append(
            AddedCourseMaterial(
                path=path,
                source_id=metadata.get("source_id", f"LEGACY-{path.stem}"),
                title=metadata.get("title", path.stem),
                course=metadata.get("course", "Math 153"),
                section=metadata.get("section", "Unassigned"),
                topic=metadata.get("topic", "General"),
                source_type=metadata.get("source_type", "Other"),
                verification_status=metadata.get(
                    "verification_status", "learner_added_unverified"
                ),
                created_at=metadata.get("created_at", ""),
                body=text[match.end() :].strip(),
            )
        )
    return materials


def search_course_materials(
    materials: list[AddedCourseMaterial], query: str, section: str | None = None
) -> list[AddedCourseMaterial]:
    """Return materials whose metadata or body contains every query token."""
    tokens = {token.casefold() for token in re.findall(r"[A-Za-z0-9]+", query)}
    matches = []
    for material in materials:
        if section is not None and material.section != section:
            continue
        haystack = " ".join(
            [material.title, material.section, material.topic, material.source_type, material.body]
        ).casefold()
        if not tokens or all(token in haystack for token in tokens):
            matches.append(material)
    return matches
