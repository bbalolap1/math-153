from pathlib import Path

from math153_tutor.corpus import ingest_source_corpus


def test_ingestion_reads_markdown_body_and_extracts_evidence(tmp_path: Path) -> None:
    source = tmp_path / "source"
    quiz = source / "quizzes" / "Quiz_5.md"
    quiz.parent.mkdir(parents=True)
    quiz.write_text(
        "# Quiz 5\n\n## Domain\n\n1. Find the domain of $f(x)=\\frac{\\sqrt{x+1}}{2x}$?\n",
        encoding="utf-8",
    )

    extracted = ingest_source_corpus(source)

    assert len(extracted) == 1
    assert extracted[0].raw_text.startswith("# Quiz 5")
    assert extracted[0].questions
    assert extracted[0].formulas == [r"f(x)=\frac{\sqrt{x+1}}{2x}"]
    assert extracted[0].topics == ["Quiz 5", "Domain"]
    assert extracted[0].manifest.content_length > 0
    assert extracted[0].manifest.extracted_records == 2


def test_ingestion_never_creates_or_rewrites_missing_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    assert ingest_source_corpus(source) == []
    assert not source.exists()
