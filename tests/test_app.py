from pathlib import Path

from streamlit.testing.v1 import AppTest


def _app(tmp_path: Path, monkeypatch) -> AppTest:
    monkeypatch.chdir(tmp_path)
    path = Path(__file__).parents[1] / "src/math153_tutor/app.py"
    return AppTest.from_file(str(path), default_timeout=10).run()


def test_direct_practice_runs_from_setup_through_worked_solution(
    tmp_path: Path, monkeypatch
) -> None:
    app = _app(tmp_path, monkeypatch)
    assert not app.exception
    next(box for box in app.selectbox if box.label == "Section").set_value("0.2").run()
    next(button for button in app.button if button.label == "Start practice").click().run()
    assert not app.exception
    assert any("Solve on paper" in heading.value for heading in app.markdown)

    next(
        button for button in app.button if button.label == "My paper work is complete"
    ).click().run()
    problem = app.session_state["practice_problems"][0]
    app.text_input[0].set_value(problem.expected_answer)
    next(button for button in app.button if button.label == "Submit answer").click().run()

    assert not app.exception
    assert app.success[0].value == "Correct."
    assert any("Worked solution" in heading.value for heading in app.subheader)
    assert any(button.label == "Try another from this family" for button in app.button)


def test_readiness_page_lists_every_working_family(tmp_path: Path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    app.radio[0].set_value("Practice readiness").run()
    assert not app.exception
    assert app.title[0].value == "Practice readiness"
    dataframe = app.dataframe[0].value
    assert len(dataframe) == 35
    assert set(dataframe["Practice-ready"]) == {"Ready"}
