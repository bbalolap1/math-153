# Implementation Plan

## Phase 0 — Repository and source registry

- Create source manifest and hashes.
- Extract both archives without altering originals.
- Pair quizzes/tests with solutions.
- Register transcript summaries.
- Add conflict log.

Acceptance: every source has a stable ID and provenance record.

## Phase 1 — Content models and Markdown parser

- Parse YAML front matter and required headings.
- Validate family IDs, source references, layers, and answer forms.
- Convert authored content to runtime Pydantic models.
- Reject incomplete templates with useful errors.

Acceptance: sample templates load and validation tests pass.

## Phase 2 — Chapter 5 vertical slice

Families:
1. exponential graph recognition;
2. exponential one-to-one equations;
3. compound interest;
4. exponential/log form conversion;
5. logarithm evaluation;
6. logarithmic one-to-one equations;
7. log properties;
8. exponential/log equations.

Acceptance: each family has source map, progression, three professor-style templates, validators, feedback, and quiz coverage.

## Phase 3 — Learner interface

Streamlit pages:
- Dashboard
- Source Map
- Learn
- Recognize
- Practice
- Quiz/Test
- Error Review
- Template Inspector

Acceptance: a learner can complete one Chapter 5 session end-to-end.

## Phase 4 — Attempt and mastery engine

- Store attempts in SQLite.
- Track recognition, first decision, final correctness, critical errors, hints, and duration.
- Recommend the next layer/family based on error taxonomy.

Acceptance: recommendations change after distinct error patterns.

## Phase 5 — Chapters 1–2 refresher

Prioritize prerequisite families that feed Chapter 5:
- exponent laws;
- rational exponents;
- equation solving;
- factoring;
- domain restrictions;
- inverses/composition.

## Phase 6 — Chapters 3–4 refresher

Prioritize:
- functions/domain/range;
- graph interpretation;
- transformations;
- inverse graph reflection;
- polynomial/rational sign analysis.

## Phase 7 — Assessment assembly

Implement blueprints mirroring:
- activity;
- quiz;
- test;
- final versions 1–3.

Do not copy source questions verbatim into generated public content. Use them as private structural templates and vary values/contexts within reviewed bounds.
