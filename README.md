# Math 153 Adaptive Review System — Version 0.0

This repository is the Codex-ready foundation for a Math 153 study and assessment system built from the user's actual course materials.

## Central problem

The lecture usually presents a direct concept and a simple example, while activities, quizzes, tests, and final-exam versions hide the same concept behind different wording, representations, prerequisite skills, and multi-step decisions. The system must preserve the professor's question construction while teaching the learner to recognize the underlying mathematical structure.

## Non-negotiable requirements

1. Source-first: generated material must trace back to a lecture, activity, quiz, test, review, exam version, or uploaded exercise image.
2. Professor-style preservation: keep wording patterns, question order, answer form, common traps, and expected solution structure.
3. Layered progression: Version 0.0 foundation → guided recognition → direct skill → representation change → mixed prerequisite → professor-style → timed exam transfer.
4. Human-readable authoring: Markdown is the primary content format. Do not use large hand-authored JSON files.
5. Recognition before speed: every family teaches “what is this question really asking?” before requiring a full solution.
6. Exact mathematics: preserve domain restrictions, excluded values, extraneous-solution checks, endpoint rules, and requested answer format.
7. Computer practice with handwritten logic: math input, multiple choice, ordered steps, tables, graph interpretation, and free response must coexist.

## Course organization

- Chapter 0.0: real numbers, signs, fractions, algebra language, order of operations, exponent foundations.
- Chapters 1–2: radicals, rational exponents, factoring, rational expressions, equations, quadratics, complex numbers, absolute value, radical/rational equations, inequalities.
- Chapters 3–4: coordinate plane, distance/midpoint, lines, circles, functions, domain/range, transformations, polynomial and rational functions.
- Chapter 5: inverse/composition, exponential functions, compound interest, logarithms, log properties, exponential/log equations.

## Start here

1. Read `AGENTS.md`.
2. Read `docs/PRODUCT_SPEC.md` and `docs/CONTENT_ARCHITECTURE.md`.
3. Run `python scripts/build_source_manifest.py` after placing/extracting source archives.
4. Implement the vertical slice in `docs/IMPLEMENTATION_PLAN.md`.

## Initial vertical slice

Build one complete family: **Section 5.5 logarithm properties and equations**.

It must include:

- source-linked examples;
- concept-to-exam connection map;
- five difficulty layers;
- multiple-choice, ordered-step, and free-response modes;
- domain/extraneous-solution feedback;
- an eight-question quiz generated from readable Markdown templates;
- attempt storage and error classification.

## Technology direction

- Python 3.12
- Streamlit first for rapid visual iteration
- Pydantic for validated runtime models
- SQLite for attempts/mastery
- SymPy for controlled symbolic validation
- Markdown + YAML front matter for authored content
- pytest for logic tests

The system may later migrate to React/TypeScript, but Version 0.0 should prove the learning model and source fidelity first.
