# Math 153 Learning System — Version 0

A source-grounded learning system built around **Student solves; computer coaches and evaluates.** It bridges visible professor-style construction to hidden mathematical structure while requiring paper work before answer entry.

## Working Version 0

The app launches on a dashboard and provides a readable course binder, persistent learner-added
Markdown materials, paper-answer practice, professor-style teaching support, bounded next-line
coaching, configurable multiple-choice assessments, saved question-by-question review, mistake repair
with a transfer check, and progress calculated from stored attempts. The controlled practice catalog
covers 35 families across Foundation through Chapter 5. Runtime questions remain explicitly
model-inferred until the absent professor/course binaries can be reviewed.

Question prompts, worked steps, and answer choices are rendered as learner-facing mathematics. Stored
validator syntax such as `4*x+(-9)` remains internal and is displayed as conventional notation such as
$4x-9$. Assessments default to the L5–L7 professor/timed/transfer pool; bridge and foundation pools are
available when the learner wants more scaffolding.

## Install and run

Requires Python 3.12.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
streamlit run src/math153_tutor/app.py
```

Learner data is stored locally under ignored `learner_data/`:

- `learning_records.sqlite3`: completed assessments and repair checks;
- `practice_attempts.sqlite3`: Paper Answer Mode submissions;
- `course_materials/*.md`: learner-added transcripts and notes.

Set `MATH153_DATA_DIR=/absolute/path` to place learner data outside the repository (recommended
for hosted deployments). Without the override, paths resolve from the installed package's repository
root, not the shell's current working directory.

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

Rebuild the filename-evidence source manifest with:

```bash
PYTHONPATH=src python scripts/build_source_manifest.py \
  data/source_registry data/derived/source_manifest.csv
```

See `docs/V0_AUDIT.md`, `docs/PROBLEM_COVERAGE_MATRIX.md`, and
`docs/CODE_WALKTHROUGH.md` for the data-flow audit, architecture/state map, complete catalog matrix,
and teaching-oriented explanation of each Python module.

## Source boundary and V0 limits

Actual professor PDFs, screenshots, and transcripts named in the source inventories are not present, so
professor fidelity is not verifiable. Professor Mode teaches from controlled runtime metadata and labels
that limitation. Next-Line Coach validates equivalent symbolic lines along the authored worked-solution
path; it is intentionally not an unrestricted proof engine. Graph practice provides a rendered
coordinate plane plus a validated coordinate selection rather than free-form canvas clicking.
