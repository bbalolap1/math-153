# Repository Audit — 2026-08-06

## Current assets

Two text inventories name section PDFs, activities, quizzes/solutions, tests/reviews, three final versions, and screenshots. The binaries and named transcripts are absent. One Chapter 5 seed family, a Markdown loader, source scripts, and design documents were present.

## Current architecture and reusable components

Version 0.0 established Python/Pydantic/Streamlit/SymPy/SQLite, Markdown-first content, eight layers, safe archive extraction, and a conflict register. These conventions are retained.

## Missing components at audit time

There was no runnable UI, practice-session state machine, generated-problem model, validation registry, persistence, mastery aggregation, or complete vertical-loop integration test.

## Data risks and source conflicts

Inventory entries are not reviewable evidence without files. `TRANSCRIPT-CH5-LOGS` did not resolve. See `data/derived/source_conflicts.md`. Milestone prompts are marked model inference and cannot be called professor-verified.

## Implementation blockers

Professor wording, layout, traps, and exact answer conventions remain blocked pending source delivery and visual review. Broad course mapping is intentionally deferred.

## Recommended first milestone

A four-family, paper-gated loop that independently captures recognition, first decision, answer, error reflection, remediation, related retry, and skill evidence.
