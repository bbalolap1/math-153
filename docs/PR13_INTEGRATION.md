# PR #13 integration reconciliation

The PR head at `466ec89` retained the root launch instructions but removed the active root
project. This change restores the last complete integrated revision, `66785dd`, at its original
paths, including the source-grounding audit and teaching-depth/complexity work.

## Active system

- Root `AGENTS.md`, canonical family Markdown, templates, source registry, design and architecture
  documentation, source corpus, manifest builders, fidelity artifacts, and tests are restored.
- Root `src/math153_tutor/app.py` preserves the dashboard, course binder, learner-added notes,
  paper work, next-line coaching, professor support, assessments, mistake repair and progress.
- Packaging explicitly selects `src`; pytest selects root `tests`. The nested rebuild is retained
  as a historical snapshot, excluded from active packaging, test collection and linting.
- Direct Streamlit execution bootstraps the root package path. Learner data retains the existing
  SQLite/Markdown layout and `MATH153_DATA_DIR` override. No migration or database rewrite occurs.
- README manifest rebuilding now uses the actual script interface. The source-conflicts record
  distinguishes available Markdown evidence from unavailable original PDF/image verification.

## Validation (2026-10-15)

- Editable installation from root succeeded.
- Root pytest collection: **145 passed**. Existing tests exercise paper submissions, next-line
  coaching, professor tools, assessment persistence/review, learner notes and transfer repair.
- New integration tests verify every manifest source hash and launch the app from an unrelated
  working directory with the project removed from import paths.
- Root Streamlit server entry point returned HTTP 200 on its health endpoint.
- `python -m ruff check .` passed. The staged whitespace check reports seven restored
  Markdown hard line breaks, including one in the hashed source corpus; these are preserved.
- No path present in the PR target revision `b37e596` is deleted by the reconciled tree.

## Scope and limits

The later nested replacement UI is not promoted: it omits original learning workflows. Its code,
rendering experiments, sources and report remain available for future selective integration.
Automated source mapping, mathematical validation and hash checks do not independently certify
every professor method against original course PDFs/images. This work does not deploy or merge
the PR and makes no claim about the health of an existing hosted application.
