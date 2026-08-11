from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


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
    tags: list[str] = Field(default_factory=list)


FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "material"


def save_course_material(
    root: Path,
    title: str,
    section: str,
    topic: str,
    source_type: str,
    body: str,
) -> AddedCourseMaterial:
    """Save learner-added material without silently promoting it to canonical professor evidence."""
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).isoformat()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12].upper()
    source_id = f"LEARNER-{digest}"
    path = root / f"{_slug(section)}-{_slug(title)}-{digest.lower()}.md"
    metadata = {
        "source_id": source_id,
        "title": title,
        "course": "Math 153",
        "section": section,
        "topic": topic,
        "source_type": source_type,
        "verification_status": "learner_added_unverified",
        "created_at": stamp,
    }
    path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n\n" + body.strip() + "\n", encoding="utf-8")
    return AddedCourseMaterial(path=path, body=body, tags=[topic], **metadata)


def _load(path: Path) -> AddedCourseMaterial | None:
    try:
        text=path.read_text(encoding="utf-8")
        match=FRONT_MATTER.match(text)
        if not match: return None
        data=yaml.safe_load(match.group(1)) or {}
        body=text[match.end():].strip()
        return AddedCourseMaterial(path=path, body=body, tags=[data.get("topic","")], **data)
    except Exception:
        return None


def list_course_materials(root: Path) -> list[AddedCourseMaterial]:
    if not root.exists(): return []
    return [m for p in sorted(root.rglob("*.md")) if (m:=_load(p)) is not None]


def search_course_materials(root: Path, query: str) -> list[AddedCourseMaterial]:
    q=query.casefold().strip()
    if not q: return list_course_materials(root)
    return [
        m for m in list_course_materials(root)
        if q in "\n".join([m.title,m.section,m.topic,m.source_type,m.body]).casefold()
    ]
