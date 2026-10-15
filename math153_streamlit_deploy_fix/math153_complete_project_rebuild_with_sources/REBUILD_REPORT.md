# Math 153 Source-Fidelity SRC Rebuild

## Authority rule

This rebuild uses the following direction of authority:

`source lectures / activities / quizzes / tests / reviews / practice finals`
→ `course_content.py canonical course model`
→ `practice_catalog.py canonical family registry + generators`
→ `complexity.py + fidelity.py`
→ `assessment.py`
→ `sessions / mastery / storage`
→ `app.py`

No downstream file is intended to invent an independent curriculum taxonomy.

## Canonical course status

- 27 section-level entries: Foundation; 1.1–1.4; 2.1–2.7; 3.1–3.7 where supported (including review/final-supported 3.5 and 3.6); 4.1–4.2; 5.1–5.6.
- 60 canonical problem families.
- 236 source references in canonical course content.
- 0 placeholder/PENDING source references.
- Sections 3.5 and 3.6 are identified as review/final-supported because the supplied Markdown corpus contains no standalone 3.5/3.6 lecture files. Their references are not falsely labeled as lecture evidence.

## Source extraction status

From the supplied Markdown source corpus:

- 53 documents indexed.
- 187 question exemplars extracted.
- 47 solution records extracted.
- 1,486 formula-like records extracted.
- Representation evidence includes symbolic, graph, table, and contextual questions.
- Instructional verbs preserved include: approximate, compute, convert, determine, express, factor, find, find all, graph, rationalize, show, simplify, sketch, solve, use, and write.
- Source question fidelity audit: 187/187 classified into a canonical family.
- Canonical family fidelity matrix: 60/60 passed the current source/implementation validation gate.

## Structural-diversity status

Every canonical problem family realizes more than numerical-only variation across its first eight variants.

Current realized normalized-structure distribution:

- 18 families: 2 structures
- 19 families: 3 structures
- 11 families: 4 structures
- 4 families: 5 structures
- 5 families: 6 structures
- 1 family: 7 structures
- 2 families: 8 structures
- 0 families: number-only/single normalized structure

The generator now varies source-supported task form, representation, given/unknown arrangement, restrictions, context, method selection, and verification burden where applicable. Difficulty is derived from cognitive/structural evidence rather than simply larger numbers.

## Assessment verification

- Quiz 1–6 source-pattern presets build at their default size without exact or normalized near duplicates.
- Test 1, Unit 2, and Test 3 review patterns build without exact or normalized near duplicates.
- Practice Final V1/V2/V3 and cumulative final patterns build without exact or normalized near duplicates.
- 50-question cumulative exam check:
  - 50 visible prompts / 50 unique
  - 50 normalized structures / 50 unique
  - 50 structural signatures / 50 unique
  - complexity distribution in verification run: L3=6, L4=8, L5=18, L6=12, L7=6
  - 44 questions at L4+
  - 18 questions at L6/L7
  - maximum 2 questions from one family

## UI behavior changed

The Streamlit application now exposes:

- Dashboard
- Course Review
- Professor Mode
- Quiz
- Test
- Exam
- Mistake Repair
- Progress

Removed from the rebuilt navigation/workflow:

- dashboard search
- Paper Answer Mode
- Next-Line Coach

Course navigation uses Foundation, Unit 1 (Chapters 1–2), Unit 2 (Chapter 3), and Unit 3 (Chapters 4–5), while Course Review exposes individual sections underneath each unit.

Quiz, Test, and Exam are separate learner modules. Source-pattern assessment presets are distinct rather than three labels over one generic assessment. Every question has a separate "Show your work" input and final-answer control. Multiple-choice choices are rendered as labeled radio options.

## File-by-file rebuild

### `__init__.py`
Documents the authority flow and marks this package as the source-fidelity rebuild.

### `app.py`
Rewritten learner-facing Streamlit workflow. Uses canonical course sections/families, full section review, Professor Mode, separate Quiz/Test/Exam modules, work capture, mistake repair, and structural-progress reporting.

### `assessment.py`
Rewritten around source-pattern blueprints. Builds candidate pools from canonical families, balances structural complexity, enforces visible/normalized/signature novelty, provides Quiz/Test/Exam gates, presets, grading, and rejects requests that cannot be satisfied faithfully instead of padding with clones.

### `complexity.py`
Rewritten complexity model. Complexity evidence includes prerequisite depth, decision points, reasoning steps, representation shifts, concept/method combinations, verification/interpretation burden, time pressure, and source-style distance. Provides normalized prompt structure and structural signatures.

### `config.py`
Expanded quality/default settings for Quiz/Test/Exam sizing and strict fidelity behavior.

### `course_content.py`
Rebuilt as the canonical structured Math 153 educational model. Contains source refs, formulas, procedures, worked examples, problem families, recognition features, representations, professor verbs, answer forms, structural variants, mistakes, verification methods, applications, units, sections, indexes, and integrity validation.

### `course_materials.py`
Learner-added Markdown is stored explicitly as unverified learner material with hashes. It is not silently promoted to canonical course authority.

### `distractors.py`
Distractors are generated from family-specific misconception patterns and are checked so the distractor is not equivalent to the correct answer.

### `fidelity.py`
Rewritten source-to-family audit and fidelity matrix. Measures source question mapping, family validation, and source/generated similarity properties.

### `generation.py`
Reduced to a compatibility adapter over the canonical generator instead of maintaining a second independent generation truth.

### `graph_questions.py`
Expanded graph question structures with source-grounded graph points/requirements and validation.

### `markdown_loader.py`
Loads authored Markdown family material with required sections/metadata validation rather than treating arbitrary text as sufficient curriculum data.

### `mastery.py`
Mastery evidence now values successful transfer across distinct structures/families and professor-level tasks, not repeated success on one template.

### `math_display.py`
Human-facing math formatting helpers for expressions, answer forms, interval/infinity notation, and readable prompt/choice display.

### `models.py`
Expanded shared models for source refs, professor grammar, structural complexity evidence, practice/assessment records, shown work, blueprints, generated problems, and learning records.

### `paths.py`
Centralized path discovery with environment overrides for data/content/sources/manifest locations.

### `practice_catalog.py`
Rewritten to consume canonical problem-family IDs from `course_content.py`. Implements all 60 canonical families, source-grounded variants, validation of expected answers, complexity/signature metadata, and family/scope generation. It no longer owns a competing curriculum taxonomy.

### `sessions.py`
Simplified session state around recognition, method choice, answer/work tracking, and completion.

### `solution_detail.py`
Uses canonical `WorkedSolution` data for recognition, decisions, execution, and verification rather than family-specific regex explanations.

### `source_manifest.py`
Rewritten Markdown source extraction. Preserves question/exemplar content, document type, locator, verbs, expected answer form, representation, formulas, visual references, and hashes.

### `step_engine.py`
Accepts mathematically equivalent learner progress and provides source-grounded next-step guidance rather than requiring exact textual reproduction of a canned line.

### `storage.py`
SQLite persistence for attempts, practice work, learning records, assessment type, and structured JSON payloads; includes compatibility migration for older DBs.

### `validation.py`
Expanded symbolic/structured validation for multiple choice, multi-select, intervals, equations, solution sets, ordered pairs, complex values, exact/decimal expressions, radicals, logarithmic expressions, and text answers.

## Tests

Automated tests cover:

1. canonical course depth / no placeholders / unique family IDs;
2. presence of source-supported Sections 3.5 and 3.6;
3. all canonical generators and expected-answer self-validation;
4. every family realizing at least two normalized structures;
5. source-pattern Quiz/Test/Exam assessment novelty;
6. cumulative assessment structural uniqueness.

Final test run: **7 passed**.

## Important boundary

This rebuild is source-grounded to the material supplied. It does not claim that missing source material has been invented. The 3.5/3.6 content is modeled from assessment/review evidence, explicitly labeled that way. If additional professor transcripts, quizzes, tests, or section notes are added later, the intended path is source extraction → canonical course update → family variants/acceptance tests, not adding an unrelated generic generator.
