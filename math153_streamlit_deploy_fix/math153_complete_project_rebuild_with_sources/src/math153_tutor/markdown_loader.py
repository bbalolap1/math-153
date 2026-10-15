from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import DifficultyLayer, QuestionFamily


FRONT_MATTER=re.compile(r"\A---\s*\n(.*?)\n---\s*\n",re.DOTALL)
HEADING=re.compile(r"^# (.+?)\s*$",re.MULTILINE)
REQUIRED_HEADINGS={
    "Purpose":"purpose",
    "Professor Surface Construction":"professor_surface_construction",
    "Underlying Mathematical Structure":"underlying_mathematical_structure",
    "Recognition Clues":"recognition_clues",
    "First Decision":"first_decision",
    "Decision Path":"decision_path",
    "Hidden Prerequisites":"hidden_prerequisites",
    "Difficulty Ladder":"difficulty_ladder_raw",
    "Expected Answer Presentation":"expected_answer_presentation",
    "Professor Traps":"professor_traps",
    "Professor-Style Templates":"professor_style_templates",
}


def _sections(text: str) -> dict[str,str]:
    matches=list(re.finditer(r"(?m)^# (.+?)\s*$",text))
    out={}
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        out[m.group(1).strip()]=text[m.end():end].strip()
    return out


def load_question_family(path: str | Path) -> QuestionFamily:
    path=Path(path); text=path.read_text(encoding="utf-8")
    fm=FRONT_MATTER.match(text)
    metadata=yaml.safe_load(fm.group(1)) if fm else {}
    body=text[fm.end():] if fm else text
    sections=_sections(body)
    missing=[h for h in REQUIRED_HEADINGS if h not in sections]
    if missing:
        raise ValueError(f"{path.name} is missing required family sections: {', '.join(missing)}")
    ladder={}
    for layer in DifficultyLayer:
        m=re.search(rf"(?mi)^\s*[-*]?\s*{layer.value}\s*[:—-]\s*(.+)$",sections["Difficulty Ladder"])
        if m: ladder[layer]=m.group(1).strip()
    if not ladder:
        ladder={layer:"Not authored." for layer in DifficultyLayer}
    return QuestionFamily(
        family_id=metadata.get("family_id",path.stem),
        title=metadata.get("title",path.stem.replace("_"," ")),
        chapter=int(metadata.get("chapter",0)),
        section=str(metadata.get("section","")),
        status=str(metadata.get("status","draft")),
        source_refs=list(metadata.get("source_refs",[])),
        purpose=sections["Purpose"],
        professor_surface_construction=sections["Professor Surface Construction"],
        underlying_mathematical_structure=sections["Underlying Mathematical Structure"],
        recognition_clues=sections["Recognition Clues"],
        first_decision=sections["First Decision"],
        decision_path=sections["Decision Path"],
        hidden_prerequisites=sections["Hidden Prerequisites"],
        difficulty_ladder=ladder,
        expected_answer_presentation=sections["Expected Answer Presentation"],
        restrictions_and_required_checks=sections.get("Restrictions and Required Checks",""),
        common_errors=sections.get("Common Errors",""),
        professor_traps=sections["Professor Traps"],
        professor_style_templates=sections["Professor-Style Templates"],
        mastery_rule=sections.get("Mastery Rule",""),
    )
