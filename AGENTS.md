# Codex Working Instructions

## Mission

Build a source-grounded Math 153 learning system that closes the gap between simple lecture examples and the professor's more complex activities, quizzes, tests, and final-exam questions.

## Before changing code

1. Read the relevant source registry entry.
2. Read the question-family Markdown template.
3. Identify the exact representation, hidden prerequisite, and expected answer form.
4. Preserve the user's original learning architecture. Do not add unrelated features.

## Source hierarchy

1. Original assessment or exercise image
2. Official solution to that assessment
3. Lecture section PDF/transcript
4. Review sheet
5. Model inference, clearly marked

Never silently “correct” a source. Record conflicts in `data/derived/source_conflicts.md`.

## Content rules

- Markdown is the canonical authoring format.
- YAML front matter is permitted for small metadata fields.
- Runtime JSON may be generated, but never treated as the main editable source.
- Every generated question must include `source_refs`, `family_id`, `difficulty_layer`, and `variant_reason`.
- Preserve mathematical notation with LaTeX.
- Store both the final answer and the expected reasoning checkpoints.

## Learning rules

Each question family must define:

- surface clues;
- underlying structure;
- hidden prerequisites;
- first decision;
- decision path;
- professor traps;
- answer presentation;
- error categories;
- variation boundaries;
- progression levels.

Do not jump from a definition directly to an exam problem. Use bridge problems that change one dimension at a time.

## Coding rules

- Keep modules small and typed.
- Use Pydantic models for parsed content.
- Use dataclasses only for internal immutable helpers.
- Add tests with each parser, validator, generator, or scoring rule.
- Do not let SymPy generate arbitrary questions. Templates control question construction; SymPy only validates.
- Never accept a mathematically equivalent answer if the prompt requires a specific form without checking that form requirement.

## Definition of done for a family

A family is complete only when it has:

1. a source map;
2. a family overview;
3. a lecture-to-exam bridge;
4. at least five progression layers;
5. three or more professor-style templates;
6. answer and reasoning validators;
7. common-error feedback;
8. a mastery rule;
9. automated tests;
10. a working UI path.
