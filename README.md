# Math 153 Learning System — Version 0

A source-grounded learning system built around **Student solves; computer coaches and evaluates.** It bridges visible professor-style construction to hidden mathematical structure while requiring paper work before answer entry.

## Working Version 0

The app launches on a dashboard and provides a readable course binder, persistent learner-added
Markdown materials, paper-answer practice, professor-style teaching support, bounded next-line
coaching, configurable multiple-choice assessments, saved question-by-question review, mistake repair
with a transfer check, and progress calculated from stored attempts. The controlled practice catalog
covers 35 families across Foundation through Chapter 5. The source corpus and derived audit map controlled question families to the available course
Markdown. Automated mapping and algebra checks are evidence of those checks; they do not establish
independent visual verification against the original professor PDFs and screenshots.

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

Rebuild the Markdown source manifest and family mappings from the repository root with:

```bash
PYTHONPATH=src python scripts/build_source_manifest.py .
```

See `docs/V0_AUDIT.md`, `docs/PROBLEM_COVERAGE_MATRIX.md`, and
`docs/CODE_WALKTHROUGH.md` for the data-flow audit, architecture/state map, complete catalog matrix,
and teaching-oriented explanation of each Python module.

## Source boundary and V0 limits

The 53 course Markdown files in `sources/` support the source mappings. Original PDFs and
screenshots listed in the inventories remain unavailable for independent visual verification.
Professor Mode retains the explicit source boundary. Historical audit metrics describe the checks
performed by their scripts and are not a substitute for reviewing the original materials. Next-Line Coach validates equivalent symbolic lines along the authored worked-solution
path; it is intentionally not an unrestricted proof engine. Graph practice provides a rendered
coordinate plane plus a validated coordinate selection rather than free-form canvas clicking.

## Integration layout

The repository root is the active project. Launch `src/math153_tutor/app.py`; configure hosted
Streamlit deployments with that same entry point and the root `requirements.txt`.
The root package preserves Course Review, Paper Answer Mode, Next-Line Coach, Professor Mode,
assessment review, mistake repair, and local learner records.

`math153_streamlit_deploy_fix/` is retained as a historical rebuild snapshot, including later
rendering and assessment experiments. It is not the active package or a second install target.
Root packaging, pytest collection, and linting exclude that snapshot. Its UI replacement is not
used because it omits original coaching workflows. Source-audit content, scripts, and derived
artifacts from the last complete integrated revision (`66785dd`) are restored at their canonical
root paths. No learner database migration is required.
