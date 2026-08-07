from pathlib import Path

from streamlit.testing.v1 import AppTest


def _app(tmp_path: Path, monkeypatch) -> AppTest:
    monkeypatch.chdir(tmp_path)
    path = Path(__file__).parents[1] / "src/math153_tutor/app.py"
    return AppTest.from_file(str(path), default_timeout=10).run()


def _navigation(app: AppTest):
    return next(radio for radio in app.radio if radio.label == "Navigate")


def test_app_launches_on_dashboard_without_starting_assessment(
    tmp_path: Path, monkeypatch
) -> None:
    app = _app(tmp_path, monkeypatch)

    assert not app.exception
    assert app.title[0].value == "Math 153 — Welcome"
    assert app.session_state["navigation_page"] == "Dashboard"
    assert "assessment_active" not in app.session_state
    assert list(_navigation(app).options) == [
        "Dashboard",
        "Course Review",
        "Learning Tools",
        "Quiz / Test / Exam",
        "Progress",
    ]


def test_course_review_opens_readable_family_content(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Course Review").run()

    assert not app.exception
    assert app.title[0].value == "Math 153 — Course Review"
    assert any("course binder or textbook" in item.value for item in app.markdown)
    assert any("Real numbers" in item.value for item in app.markdown)


def test_assessment_page_stays_at_launcher_until_launch(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Quiz / Test / Exam").run()

    assert not app.exception
    assert app.title[0].value == "Quiz / Test / Exam"
    assert any(button.label == "Launch Assessment" for button in app.button)
    assert "assessment_active" not in app.session_state
