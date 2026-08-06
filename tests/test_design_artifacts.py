from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).parents[1]


class _HTMLValidator(HTMLParser):
    pass


def test_required_visual_architecture_artifacts_exist() -> None:
    required = [
        "docs/current_repository_audit.md",
        "docs/visual_architecture_report.md",
        "design/source_analysis/course_source_visual_language.md",
        "design/source_analysis/question_construction_catalog.md",
        "design/design_system/math153_design_language.md",
        "design/connections/state_machines.md",
        "design/connections/ui_backend_map.md",
        "design/approvals/screen_status.md",
        "design/decisions/decision_log.md",
        "design/decisions/open_decisions.md",
        "design/prototypes/handwritten-practice.html",
    ]
    required.extend(f"design/journeys/0{number}_{name}.md" for number, name in [
        (1, "course_review"), (2, "handwritten_practice"), (3, "next_line_coach"),
        (4, "professor_mode"), (5, "quiz_and_test_review"), (6, "mistake_repair"),
    ])
    assert not [path for path in required if not (ROOT / path).is_file()]


def test_wireframe_index_links_every_required_screen() -> None:
    required = {
        "session-setup.html", "course-review.html", "source-comparison.html",
        "problem-presentation.html", "recognition.html", "first-decision.html",
        "paper-work.html", "answer-entry.html", "correct-feedback.html",
        "incorrect-feedback.html", "remediation.html", "professor-mode.html",
        "session-summary.html",
    }
    index = (ROOT / "design/wireframes/index.html").read_text(encoding="utf-8")
    assert not [name for name in required if f'href="{name}"' not in index]
    for name in required:
        path = ROOT / "design/wireframes" / name
        parser = _HTMLValidator()
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()


def test_every_required_screen_has_approval_fields() -> None:
    screen_names = {
        "dashboard", "chapter_group_selection", "section_overview", "source_comparison",
        "session_setup", "problem_presentation", "recognition", "first_decision",
        "paper_work", "answer_entry", "correct_feedback", "incorrect_feedback",
        "remediation", "next_line_coach", "professor_mode", "assessment_report",
        "mistake_review", "session_summary",
    }
    headings = [
        "## Screen ID", "## Journey", "## Purpose", "## Source influence",
        "## Wireframe", "## Visible components", "## Hidden components",
        "## Backend dependencies", "## Events", "## State transitions",
        "## Error states", "## Accessibility", "## Open decisions",
        "## Approval status", "## Implementation status",
    ]
    for name in screen_names:
        text = (ROOT / "design/screens" / f"{name}.md").read_text(encoding="utf-8")
        assert all(heading in text for heading in headings), name
