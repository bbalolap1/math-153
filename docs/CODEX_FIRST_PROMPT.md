# First Codex Work Order

Read `AGENTS.md`, `README.md`, and all files in `docs/` before coding.

Implement Phase 0 and Phase 1 only.

## Task

1. Add a safe archive extraction script for `math153.zip` and `math153(1).zip`.
2. Generate a source manifest with SHA-256 hashes.
3. Classify files by filename into lecture section, activity, quiz, quiz solution, test, review, final version, final solution, screenshot, and transcript.
4. Pair assessment files with solution files where possible.
5. Extend the Markdown loader to parse all canonical headings and difficulty-ladder subsections.
6. Add validation errors that identify the exact missing section and file.
7. Add pytest coverage.
8. Add a small Streamlit “Template Inspector” page that lists loaded families and shows their source references and decision paths.

## Constraints

- Do not author content in JSON.
- Do not change source files.
- Do not use OCR in this phase.
- Do not generate new math questions yet.
- Keep all source-derived statements traceable.

## Acceptance checks

- `pytest` passes.
- both archives can be extracted idempotently;
- manifest is deterministic;
- quiz/solution pairs are visible;
- the seed Chapter 5 family loads in the UI;
- malformed Markdown templates fail with readable errors.
