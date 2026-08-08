# Math 153 Handwritten Training System

A source-grounded learning system built around **Student solves; computer coaches and evaluates.** It bridges visible professor-style construction to hidden mathematical structure while requiring paper work before answer entry.

## Current milestone

The runnable vertical slice supports family recognition, an independently recorded first decision, a paper gate with voluntary timer, mathematically aware final-answer validation, error reflection, bounded remediation, a deterministic related problem, local attempt storage, and multidimensional skill evidence. Four representative families are included, but their prompts are explicitly model-inferred until the absent course binaries can be reviewed.

## Install and run

Requires Python 3.12.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
streamlit run src/math153_tutor/app.py
```

Learner history is stored locally in ignored `learner_data/attempts.sqlite3`.

## Repository structure

- `content/`: canonical family Markdown
- `src/math153_tutor/`: generation, validation, session, persistence, mastery, and UI logic
- `data/source_registry/`: available file inventories
- `data/derived/source_conflicts.md`: discrepancies and provenance gaps
- `templates/`: human authoring templates
- `docs/`: architecture, policy, audit, and roadmap
- `tests/`: content, mathematics, and workflow checks

## Content authoring

Read `AGENTS.md`, the relevant registry entry, `templates/question_family_template.md`, and `docs/content-authoring.md`. Never author canonical content in JSON or silently repair a source.

## Testing

```bash
pytest
ruff check .
```

## Known limitations

Actual PDFs, screenshots, and transcripts are not present, so professor fidelity is not yet verifiable. Professor Mode, assessment builders, delayed scheduling, interval/domain parsing, and Next-Line graphs are later phases. The system does not claim full family or course coverage.
