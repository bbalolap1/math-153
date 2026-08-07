from pathlib import Path

from streamlit.testing.v1 import AppTest

from math153_tutor.assessment import build_assessment, complete_assessment, grade_question
from math153_tutor.practice_catalog import CHAPTERS_12, generate_practice_problem
from math153_tutor.storage import LearningRecordRepository


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


def test_dashboard_cards_queue_navigation_without_mutating_sidebar_widget(
    tmp_path: Path, monkeypatch
) -> None:
    destinations = {
        "Course Review": "Math 153 — Course Review",
        "Learning Tools": "Learning Tools",
        "Quiz / Test / Exam": "Quiz / Test / Exam",
        "Progress": "Progress",
    }
    for destination, expected_title in destinations.items():
        app = _app(tmp_path, monkeypatch)
        next(
            button for button in app.button if button.label == f"Open {destination}"
        ).click().run()

        assert not app.exception
        assert app.session_state["navigation_page"] == destination
        assert app.session_state["navigation_selector"] == destination
        assert app.title[0].value == expected_title


def test_dashboard_section_shortcut_uses_safe_navigation(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    next(button for button in app.button if button.label == "Open Foundation").click().run()

    assert not app.exception
    assert app.session_state["navigation_page"] == "Course Review"
    assert app.title[0].value == "Math 153 — Course Review"


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


def test_added_course_material_is_saved_and_reopened(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Course Review").run()
    next(button for button in app.button if button.label == "Add Course Material").click().run()
    next(field for field in app.text_input if field.label == "Title").set_value("My lecture").run()
    next(area for area in app.text_area if area.label == "Transcript or notes").set_value(
        "## Fractions\n\nUse a common denominator."
    ).run()
    next(button for button in app.button if button.label == "Add to Course Review").click().run()

    assert not app.exception
    assert list((tmp_path / "learner_data/course_materials").glob("*.md"))
    assert any("My lecture" in expander.label for expander in app.expander)


def test_paper_mode_validates_and_persists_selected_answer(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Learning Tools").run()
    next(button for button in app.button if button.label == "Open Paper Answer Mode").click().run()
    problem = app.session_state["practice_tool_problem"]
    next(radio for radio in app.radio if radio.label == "What answer did you get on paper?").set_value(
        problem.expected_answer
    ).run()
    next(button for button in app.button if button.label == "Submit selected answer").click().run()

    assert not app.exception
    assert any(message.value == "Final answer validated." for message in app.success)
    assert (tmp_path / "learner_data/practice_attempts.sqlite3").is_file()


def test_review_routes_real_mistake_through_transfer_repair(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    problem = build_assessment([CHAPTERS_12], count=1, seed=800)[0]
    record = complete_assessment(
        "Quiz", ["Chapters 1–2"], [grade_question(problem, problem.wrong_answer)], 10
    )
    repository = LearningRecordRepository("learner_data/learning_records.sqlite3")
    repository.add_assessment(record)

    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Learning Tools").run()
    next(button for button in app.button if button.label == "Open Quiz Review").click().run()
    assert any(problem.expected_answer in item.value for item in app.markdown)
    next(button for button in app.button if button.label == "Repair this mistake").click().run()

    assert any(header.value == "Mistake Repair" for header in app.header)
    next(button for button in app.button if button.label == "Check repair").click().run()
    transfer = next(radio for radio in app.radio if radio.label == "Select the transfer answer")
    actual_transfer = generate_practice_problem(
        problem.family_id, problem.parameter_seed + 503, (problem.parameter_seed + 1) % 10
    )
    transfer.set_value(actual_transfer.expected_answer).run()
    next(button for button in app.button if button.label == "Submit transfer").click().run()

    assert any("Transfer confirmed" in message.value for message in app.success)
    assert repository.list_repairs()[0].transfer_correct is True


def test_configured_assessment_completes_saves_and_opens_review(
    tmp_path: Path, monkeypatch
) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Quiz / Test / Exam").run()
    next(button for button in app.button if button.label == "Launch Assessment").click().run()

    for _ in range(5):
        index = app.session_state["assessment_index"]
        problem = app.session_state["assessment_problems"][index]
        next(radio for radio in app.radio if radio.label == "Select one answer").set_value(
            problem.expected_answer
        ).run()
        next(button for button in app.button if button.label == "Submit Answer").click().run()

    assert not app.exception
    assert any("Assessment complete and saved" in message.value for message in app.success)
    assert (tmp_path / "learner_data/learning_records.sqlite3").is_file()
    next(button for button in app.button if button.label == "Open Quiz Review").click().run()
    assert any(header.value == "Quiz / Test Review" for header in app.header)
    assert app.metric[0].value == "100%"


def test_professor_and_next_line_tools_use_real_problem_metadata(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    _navigation(app).set_value("Learning Tools").run()
    next(button for button in app.button if button.label == "Open Professor Mode").click().run()
    problem = app.session_state["practice_tool_problem"]
    assert any(problem.worked_solution.rule in item.value for item in app.markdown)

    next(button for button in app.button if button.label == "Open Next-Line Coach").click().run()
    first_line = problem.worked_solution.setup
    next(field for field in app.text_input if field.label == "Your current line").set_value(
        first_line
    ).run()
    next(button for button in app.button if button.label == "Check this line").click().run()
    assert app.session_state["coach_step"] == 1
    assert any("mathematically consistent" in message.value for message in app.success)
