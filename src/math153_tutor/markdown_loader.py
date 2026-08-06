from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import QuestionFamily


FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING = re.compile(r"^# (.+?)\s*$", re.MULTILINE)


REQUIRED_HEADINGS = {
    "Purpose": "purpose",
    "Professor Surface Construction": "professor_surface_construction",
    "Underlying Mathematical Structure": "underlying_mathematical_structure",
    "Recognition Clues": "recognition_clues",
    "First Decision": "first_decision",
    "Decision Path": "decision_path",
}


def _sections(body: str) -> dict[str, str]:
    matches = list(HEADING.finditer(body))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group(1).strip()] = body[start:end].strip()
    return result


def load_question_family(path: str | Path) -> QuestionFamily:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    front = FRONT_MATTER.match(text)
    if not front:
        raise ValueError(f"Missing YAML front matter: {path}")

    metadata = yaml.safe_load(front.group(1)) or {}
    sections = _sections(text[front.end():])

    missing = [heading for heading in REQUIRED_HEADINGS if not sections.get(heading)]
    if missing:
        raise ValueError(f"Missing required headings in {path}: {', '.join(missing)}")

    payload = dict(metadata)
    for heading, field_name in REQUIRED_HEADINGS.items():
        payload[field_name] = sections[heading]
    payload["restrictions_and_required_checks"] = sections.get(
        "Restrictions and Required Checks", ""
    )
    payload["common_errors"] = sections.get("Common Errors", "")
    payload["mastery_rule"] = sections.get("Mastery Rule", "")
    return QuestionFamily.model_validate(payload)
