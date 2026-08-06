from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_handwritten_workflow_advances_without_session_key_collisions(
    tmp_path: Path, monkeypatch,
) -> None:
    """Exercise every form transition that previously failed on Streamlit Cloud."""
    monkeypatch.chdir(tmp_path)
    app_path = Path(__file__).parents[1] / "src/math153_tutor/app.py"
    app = AppTest.from_file(str(app_path), default_timeout=10).run()

    assert not app.exception
    app.button(key="FormSubmitter:recognition_form-Lock recognition").click().run()
    assert not app.exception
    assert "What should you do first?" in [radio.label for radio in app.radio]

    app.button(key="FormSubmitter:decision_form-Lock first decision").click().run()
    assert not app.exception
    app.button[0].click().run()
    assert not app.exception
    assert "Final answer" in [field.label for field in app.text_input]

    app.text_input[0].set_value(app.session_state["problem"].expected_answer)
    app.button(key="FormSubmitter:answer_form-Submit answer").click().run()
    assert not app.exception
    assert app.success[0].value == "Final answer validated."


def test_sidebar_exposes_course_scope_and_source_inventory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    app_path = Path(__file__).parents[1] / "src/math153_tutor/app.py"
    app = AppTest.from_file(str(app_path), default_timeout=10).run()

    app.radio(key="navigation_page").set_value("Course Map").run()
    assert not app.exception
    assert app.title[0].value == "Course Map"
    assert any("Polynomial and rational graphs" in item.value for item in app.markdown)

    app.radio(key="navigation_page").set_value("Source Library").run()
    assert not app.exception
    assert app.title[0].value == "Source Library"
    assert "filename inventories" in app.warning[0].value
