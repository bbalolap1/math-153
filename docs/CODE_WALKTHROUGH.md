# Math 153 Python Code Walkthrough

This document explains the current code as an information system, not merely as a list of filenames.
Each section states purpose, connections, top-to-bottom behavior, an example, problems found during the
V0 audit, and changes made. Paths are relative to the repository root.

## 1. `src/math153_tutor/app.py`

### A. Purpose

This is the Streamlit presentation/controller. It renders the approved Dashboard-first navigation and
coordinates domain services. It should decide what the learner sees and which service to call; it should
not invent mathematics or define persistence formats.

### B. Connections

Streamlit executes this file through `streamlit run` or the `math153-tutor` console script. It imports:

- assessment assembly/grading from `assessment.py`;
- textbook-like lessons from `course_content.py`;
- learner material parsing/search from `course_materials.py`;
- graph models/validation from `graph_questions.py`;
- canonical family parsing from `markdown_loader.py`;
- evidence labels from `mastery.py`;
- Pydantic records from `models.py`;
- controlled questions/catalog metadata from `practice_catalog.py`;
- stable paths from `paths.py`;
- SQLite repositories from `storage.py`;
- step validation from `step_engine.py`;
- final-answer validation from `validation.py`.

Inputs are widget events and session state. Outputs are rendered screens, Markdown files, SQLite records,
and updated transient state.

### C. Top-to-bottom walkthrough

1. **Imports and paths.** Standard-library `re` and `time` support graph parsing and timers. `DATA_ROOT`,
   `ADDED_MATERIALS`, `LEARNING_DB`, and `PRACTICE_DB` come from a repository-stable path rather than the
   current shell directory.
2. **Navigation/course constants.** `NAVIGATION` and `COURSES` are the exact Figma contract. `COURSE_SCOPE`
   supplies searchable topic names. `SCOPE_GROUP` translates UI section labels to catalog groups.
   `FAMILY_GROUP` maps the four canonical Markdown families into Course Review.
3. **Style.** `_style()` injects restrained worksheet-like CSS. It changes presentation only.
4. **Safe navigation.** `_go(page)` validates a destination, stores `pending_navigation`, and reruns.
   `_sidebar()` consumes that value *before* instantiating the radio. `_navigation_changed()` handles user
   radio changes. This ordering exists because Streamlit forbids changing a widget-owned key after the
   widget is created in a run.
5. **Dashboard.** `_dashboard()` renders welcome/search/section controls and four journey cards. Search
   covers both the static topic index and parsed learner notes. A result stores its destination context and
   queues Course Review navigation.
6. **Course Review.** `_family_pages()` parses canonical Markdown. `_course_review()` renders LaTeX lessons,
   worked examples, source maps, prerequisites, first decisions, answer forms, traps, learner materials,
   and a generated catalog-capability table. It never labels learner material verified.
7. **Add Material.** `_add_course_material()` captures title, original Markdown body, section, topic, and
   type. It calls `save_course_material`; empty content becomes a visible validation error.
8. **Problem rendering.** `_active_practice_problem()` supplies a deterministic initial tool problem.
   `_practice_solution()` renders authored checkpoints. `_render_practice_problem()` displays the prompt
   and creates an accurate Vega-Lite parabola for quadratic graph families.
9. **Learning Tools hub.** `_learning_tools()` selects one of five real tool functions.
10. **Paper Answer Mode.** `_paper_answer_mode()` uses meaningful choices, validates the selected paper
    result, persists a `PracticeAttempt`, displays feedback, and produces a related controlled problem.
11. **Professor Mode.** `_professor_mode()` teaches the active tool/assessment problem through four distinct
    depths. It uses the problem's rule, prerequisites, worked solution, parallel template, and relevant
    learner notes. The source-honesty caption remains visible. Returning to an assessment does not submit
    or overwrite its answer widget.
12. **Next-Line Coach.** `_next_line_coach()` sends exactly one entered line and the current checkpoint index
    to `step_engine.check_step`. A valid line advances one checkpoint; an invalid/parse/domain result shows
    its specific explanation and stops.
13. **Review and repair.** `_quiz_review()` selects one persisted assessment, not a global attempt pile. It
    displays each original problem, learner/correct answers, likely error, solution, and repair route.
    `_mistake_repair()` reteaches the actual missed family's rule, checks the setup decision, generates a
    transfer variant, validates it, and persists `RepairRecord`.
14. **Assessment.** `_assessment_launcher()` chooses type, multiple scopes, topics, and length.
    `_active_assessment()` displays one question, preserves answer state, records a typed result, advances,
    and saves one `AssessmentRecord` at completion. `_assessment_results()` reloads the saved record and
    routes to Review.
15. **Graphs.** `_interactive_graph_demo()` plots `y=x^2-4`, captures explicit coordinate selections,
    validates the exact point set, and persists the graph attempt.
16. **Progress.** `_progress_page()` reads assessment, paper, graph, and repair records. It reports actual
    counts/accuracy, per-family weak areas, representation/transfer evidence, and assessment history. It
    does not invent recognition evidence.
17. **Entry point.** `main()` configures Streamlit, renders style/sidebar, and dispatches exactly one primary
    page. The module guard allows both direct Streamlit execution and console entry.

Session-state ownership is listed in `docs/V0_AUDIT.md`; widget keys and program-owned keys are deliberately
separate.

### D. Example

The learner chooses a Quiz, Chapters 1–2, Linear Equations, and five questions. The launcher calls
`build_assessment`; the answer radio retains a choice; Submit calls `grade_question`; completion writes an
assessment; Open Review reloads that ID; Repair carries the exact missed `PracticeProblem`; the transfer
answer is validated and saved; Progress reads both records.

### E. Problems found

The file had grown into a large controller, contained path policy, step validation, graph validation, and
content constants. The old deployed revision also mutated `navigation_page` after widget creation.

### F. Changes made

Path, step, graph, source, distractor, and material-index responsibilities were extracted. Navigation is
queued safely. Topic filtering, active-problem Professor Mode, error-aware Review, persistent graph work,
and evidence-aware Progress were connected end-to-end.

## 2. `src/math153_tutor/models.py`

### A. Purpose

Defines the Pydantic contracts shared across parsing, generation, validation, persistence, review, and UI.

### B. Connections

Every domain/service module imports one or more models. Inputs are Python/YAML/JSON values; outputs are
validated objects with serializable `model_dump()` data.

### C. Top-to-bottom walkthrough

- `DifficultyLayer` names L0–L7; `ErrorCategory` provides the product taxonomy.
- `SourceRef` models a stable source role/page/question.
- `QuestionFamily` is parsed from canonical Markdown and requires structure, prerequisites, decision path,
  traps, three template descriptions, progression, checks, answer presentation, and mastery rule.
- `Attempt` stores multidimensional evidence. Recognition/first-decision fields are optional because an
  assessment that never asks those questions must store `None`, not a fabricated success.
- `GeneratedProblem` is the older four-family runtime contract used by `generation.py` and `sessions.py`.
- `WorkedSolution` is the authored explanation/checkpoint object.
- `PracticeProblem` is the full-scope catalog contract: identity, source, layer, representation, variant
  reason, validation form, solution, and reasoning checkpoints.
- `PracticeAttempt` records Paper/graph results.
- `AssessmentQuestionResult` embeds the exact problem snapshot, selected answer, correctness, validator code,
  and likely error category.
- `AssessmentRecord` groups results under one assessment identity with start/end/duration and computed score.
- `RepairRecord` records rule and transfer evidence.

### D. Example

SQLite does not reconstruct a current template to review an old quiz. It loads the serialized
`AssessmentRecord`, whose embedded `PracticeProblem` preserves the exact prompt and answer from that session.

### E. Problems found

The project has both legacy `GeneratedProblem`/`Attempt` and newer full-scope `PracticeProblem`/assessment
records. This duplication is explicit rather than hidden but remains a migration concern.

### F. Changes made

Added complete assessment timing/error fields, repair records, and required family/trap/template and runtime
provenance/representation metadata.

## 3. `src/math153_tutor/practice_catalog.py`

### A. Purpose

This is the controlled V0 curriculum generator. It answers “what can the app teach/test?” for 35 families
and constructs problems without allowing SymPy to invent curriculum.

### B. Connections

Imported by assessment, tools, coverage reporting, and tests. It imports models, SymPy for deterministic
calculation, and final-answer validation only to guarantee its known-wrong answer is actually wrong.

### C. Top-to-bottom walkthrough

- Group constants define Foundation, Chapters 1–2, Chapters 3–4, Chapter 5, and review scopes.
- Immutable `FamilySpec` rows define family ID, title, group, chapter, section, skills, all L0–L7 layers,
  explicit model-inference grounding, and the V0 mastery rule.
- `_difficulty`, `_difficulty_layer`, and `_representation` convert a variant index/prompt into honest runtime
  metadata.
- `_solution` constructs a typed worked solution.
- `_build` is the large controlled-template dispatcher. Each branch chooses coherent parameters, prompt,
  answer form, expected answer, authored common wrong answer, choices, and solution. Context branches such as
  service pricing, growth, models, and interest map variables/units to actual equations.
- `generate_practice_problem` adds identity/provenance/layer/reason/checkpoints. If random parameters make the
  authored wrong answer accidentally equivalent, it substitutes a validator-confirmed wrong form.
- `family_variants` creates the ten-slot audit ladder. `PRESET_SESSIONS` defines bounded review sets.
- `build_session` rejects empty/unknown scopes and deterministically interleaves selected families.

### D. Example

A contextual linear variant chooses setup fee, per-part rate, and whole-number quantity, computes a matching
bill, asks for the quantity, stores the equation checkpoint, and validates the contextual integer result.

### E. Problems found

This module is over 1,000 lines and has only four corresponding canonical family Markdown files. The breadth
is usable V0 coverage, not evidence that all 35 families meet the source-reviewed definition of done.
Previously, runtime wrong answers were overwritten with `999999`, and layer/representation metadata was absent.

### F. Changes made

Preserved authored errors, validator-checked negative examples, L0–L7 metadata, representations, source refs,
variant reasons, reasoning checkpoints, and a coherent contextual linear bridge.

## 4. `src/math153_tutor/assessment.py`

### A. Purpose

Assembles and grades one bounded Quiz/Test/Exam independently of Streamlit.

### B. Connections

The UI calls it; it calls the catalog, distractor service, and practice validator; it emits assessment models
for `LearningRecordRepository`.

### C. Top-to-bottom walkthrough

`assessment_choices` combines the correct answer, authored choices, and error-pattern distractors, removes
duplicates, guarantees the answer is present, and shuffles deterministically. `build_assessment` filters both
scope and optional topics. `grade_question` validates and attaches the matching error pattern.
`complete_assessment` creates a unique ID and derives start time from measured duration.

### D. Example

Selecting a coordinate-reversal distractor stores both the selected ordered pair and “reversed coordinates,”
which Review can explain later.

### E. Problems found / F. Changes made

Generic `correct±1` options lacked semantic meaning. The module now consumes validator-checked error patterns
and supports topic filtering and complete timing.

## 5. `src/math153_tutor/distractors.py`

### A. Purpose

Creates bounded, meaningful wrong choices and names the likely mathematical mistake.

### B. Connections

Imported by `assessment.py`; imports `PracticeProblem` and the final validator so no distractor can be accepted
as correct.

### C. Top-to-bottom walkthrough

Immutable `Distractor` holds answer and error pattern. `_numeric_candidates` branches for logarithm/exponent,
linear, and general numeric errors. `meaningful_distractors` handles multi-solution omission, coordinate
reversal/signs, endpoint errors, equation signs, expression identities, and complex signs. The final loop
deduplicates and validator-rejects every candidate.

### D. Example

For vertex `(2,-4)`, choices can include `(-4,2)` with “reversed coordinates” and `(2,4)` with “y-sign error.”

### E. Problems found / F. Changes made

This responsibility was formerly generic logic in `assessment.py`; extraction makes error construction typed,
testable, and family/answer-form aware.

## 6. `src/math153_tutor/step_engine.py`

### A. Purpose

Validates exactly one learner line against the controlled solution path and returns only bounded next guidance.

### B. Connections

Next-Line Coach calls it with a `PracticeProblem`, line, and index. It imports SymPy only for validation and
returns `StepCheck`.

### C. Top-to-bottom walkthrough

`StepCheck` holds validity, next index, normalized text, error code, explanation, and optional guidance.
`solution_steps` reads setup/calculation checkpoints. `_clean` normalizes common syntax. `_equivalent` compares
expressions or equations up to a nonzero constant multiple. `check_step` clamps the index; handles empty input;
enforces an authored log-domain opening when present; reports parse errors; rejects invalid transformations;
and advances only one checkpoint after success.

### D. Example

For `3^x=9`, `3^x=3^2` is accepted at checkpoint zero and only `x=2` is suggested next; `x=999` is rejected
with the applicable exponent rule.

### E. Problems found / F. Changes made

The previous string/SymPy comparison was private UI code with generic feedback. It is now a typed, family-aware,
unit-tested engine. It intentionally validates the authored branch rather than arbitrary proofs.

## 7. `src/math153_tutor/graph_questions.py`

### A. Purpose

Defines graph-response data independently of Vega/Streamlit and validates captured mathematical coordinates.

### B. Connections

The app renders `INTERCEPT_QUESTION`, converts selected labels to `GraphPoint`, validates, then persists a
`PracticeAttempt`.

### C. Top-to-bottom walkthrough

Frozen `GraphPoint` is hashable for sets. `GraphQuestion` contains identity, family, prompt, exact expected set,
source refs, layer, and variant reason. The controlled V0 intercept question is model-inferred.
`validate_graph_points` requires exact set equality.

### D. Example

`{(-2,0),(2,0)}` passes; including the vertex `(0,-4)` fails.

### E. Problems found / F. Changes made

The old graph preview had inline validation and no record. Validation is now backend-owned and submissions
persist.

## 8. `src/math153_tutor/course_content.py`

### A. Purpose

Holds the system-authored V0 digital-textbook lessons outside UI code.

### B. Connections

Only Course Review imports it. It outputs immutable `CourseLesson` objects containing explanation, formulas,
example, and steps.

### C. Top-to-bottom walkthrough

`CourseLesson` is an immutable internal helper, appropriate for a fixed code-owned lesson. `COURSE_LESSONS`
groups Foundation, Chapters 1–2, Chapters 3–4, and Chapter 5. Raw LaTeX strings preserve fractions, radicals,
exponents, functions, logs, coordinates, and checks for `st.latex`.

### D. Example

The Chapter 5 interest lesson renders the compound-interest formula, substitutes all model quantities, and
shows the rounded result.

### E. Problems found / F. Changes made

These lessons are system-authored summaries, not extracted course sources. The UI labels that boundary. Content
was moved out of the former paragraph dictionary in `app.py`.

## 9. `src/math153_tutor/course_materials.py`

### A. Purpose

Persists, parses, indexes, and retrieves learner-added transcripts/notes without changing their provenance.

### B. Connections

Dashboard, Course Review, and Professor Mode call it. It imports YAML and Pydantic and reads/writes Markdown.

### C. Top-to-bottom walkthrough

`AddedCourseMaterial` validates path, source ID, title, course, section, topic, type, verification, timestamp,
and body. `_safe_fragment` creates safe filenames. `save_course_material` rejects empty bodies, generates a
stable learner source ID, YAML front matter, and writes the original trimmed body. `list_course_materials`
parses all valid Markdown and supplies conservative legacy defaults. `search_course_materials` tokenizes a
query and requires every token across metadata/body, optionally filtering a section.

### D. Example

A pasted “Week 5 compound interest” note is assigned Chapter 5/topic compound interest, saved with
`learner_added_unverified`, found by Dashboard search, and offered as unverified related material in Professor
Mode.

### E. Problems found / F. Changes made

The old immutable dataclass had no source ID/topic/course/verification or retrieval. It is now parsed Pydantic
content with a real V0 search/teaching pipeline.

## 10. `src/math153_tutor/source_manifest.py`

### A. Purpose

Turns the repository's real filename inventories into a typed, deterministic provenance manifest even when
the binaries are missing.

### B. Connections

The build script and tests import it. Inputs are inventory paths and optional extracted source root; output is
a list of `SourceManifestEntry` and CSV.

### C. Top-to-bottom walkthrough

`SourceKind` restricts classifications. `SourceManifestEntry` records ID/path/type/chapter/section/topic/pair,
presence/hash/review status/notes. `digest` hashes present binaries. `classify` uses filename evidence only.
`_pair_key` normalizes obvious solution markers. `build_inventory_manifest` deduplicates entries, checks actual
presence, avoids fake hashes, and pairs matching assessment/solution names. `write_manifest` emits stable CSV;
`read_manifest` validates CSV rows back into Pydantic records for Course Review.

### D. Example

`Quiz_1.pdf` and `Quiz_1 Solution-1.pdf` receive distinct IDs and reciprocal pair IDs; both remain
`inventory_only` when absent.

### E. Problems found / F. Changes made

The old script could only scan extracted files, making the known inventories invisible. The typed pipeline now
preserves exactly what is known and exactly what is not.

## 11. `src/math153_tutor/markdown_loader.py`

### A. Purpose

Parses canonical family Markdown/YAML into `QuestionFamily`.

### B. Connections

Course Review and tests call it; it imports YAML, regex, and the model.

### C. Top-to-bottom walkthrough

Regexes identify front matter, level-one headings, and L0–L7 subsections. `REQUIRED_HEADINGS` maps author names
to model fields, now including traps and templates. `_sections` slices text between headings. The loader checks
front matter, reports the exact missing headings/file, copies required sections, parses the ladder, requires at
least five levels, attaches optional checks/errors/mastery, and invokes Pydantic.

### D. Example

A family missing “Professor Traps” fails during authoring rather than silently reaching the UI incomplete.

### E. Problems found / F. Changes made

The architecture-required traps/templates were implicit. They are now required and present in all four files.

## 12. `src/math153_tutor/generation.py`

### A. Purpose

Legacy deterministic generators for four canonical Markdown-adjacent families.

### B. Connections

Generation/session tests use it; the main V0 assessment/tools use `practice_catalog.py` instead. It imports
models and Python `random`.

### C. Top-to-bottom walkthrough

`FAMILIES` labels four IDs. `_common` creates shared provenance, recognition/decision options, skills,
checkpoints, and feedback. `_linear`, `_composition`, `_exponential`, and `_logarithmic` construct controlled
parameters. `GENERATORS` dispatches IDs. `generate_problem` returns a reproducible problem or a readable error.

### D. Example

The log generator creates equal-log arguments, a positive-domain check, and domain-targeted feedback.

### E. Problems found / F. Changes made

This duplicates a small subset of the catalog and is not the main UI path. It remains for the multidimensional
recognition/first-decision `Attempt` pipeline and compatibility; the audit documents that split.

## 13. `src/math153_tutor/validation.py`

### A. Purpose

Owns mathematical parsing and form-aware answer validation. SymPy checks authored mathematics but never creates
curriculum.

### B. Connections

Assessment, sessions, tools, distractors, catalog audits, and tests call it.

### C. Top-to-bottom walkthrough

`ValidationResult` is an immutable internal result; `AnswerParseError` hides raw parser details. `_expression`
allows a bounded character set and converts `^`. `_solution_set`, `_equation`, `_pair`, and `_interval` parse
specific answer forms. `validate_answer` supports the legacy model and exact-form constraint.
`validate_practice_answer` dispatches multiple choice, multi-select, intervals/domain/range, pairs, equations,
sets, complex values, decimals, expressions, radicals, tables, and requested factoring/radical form checks.
Expected parse failures return `parse_error` rather than crashing Streamlit.

### D. Example

An expanded polynomial mathematically equal to a requested factored answer is rejected because the prompt's
form requirement is part of correctness.

### E. Problems found / F. Changes made

Graph points are intentionally validated in their typed graph module; the scalar validator remains focused.

## 14. `src/math153_tutor/sessions.py`

### A. Purpose

Orchestrates the legacy multidimensional learning attempt and plain assessment-only attempt.

### B. Connections

Tests/legacy flows call it; it imports validation, models, and `AttemptRepository`.

### C. Top-to-bottom walkthrough

`submit_attempt` independently evaluates recognition, first decision, and final answer; infers bounded errors;
constructs `Attempt`; persists; and returns both record/result. `submit_assessment_attempt` deliberately stores
recognition and first-decision as `None`, tags only observed answer/check evidence, and persists assessment mode.

### D. Example

A correct multiple-choice final answer collected without a recognition prompt contributes procedure evidence
only.

### E. Problems found / F. Changes made

The full assessment UI now uses grouped `AssessmentRecord`; this module remains the source-honest independent
dimension service for legacy/generated flows.

## 15. `src/math153_tutor/storage.py`

### A. Purpose

Implements local SQLite persistence without embedding UI decisions.

### B. Connections

Sessions and app import repositories; models provide JSON serialization.

### C. Top-to-bottom walkthrough

`AttemptRepository` creates/indexes a table, inserts attempt payloads, and filters by family.
`PracticeAttemptRepository` stores Paper/graph results. `LearningRecordRepository` creates assessment and repair
tables; upserts assessments by unique ID; lists newest first; retrieves one assessment; and appends/lists repair
records. Context managers commit and close each operation.

### D. Example

After a process restart, Review calls `get_assessment(id)` and receives the exact embedded questions.

### E. Problems found / F. Changes made

There is no schema migration/version table, which is acceptable for local V0 but must be added before incompatible
model changes. Stable root resolution now lives in `paths.py`.

## 16. `src/math153_tutor/mastery.py`

### A. Purpose

Calculates evidence without turning missing data into success.

### B. Connections

Legacy attempt tests call `progress`; the Progress UI uses `assessment_evidence_status` for assessment-only data.

### C. Top-to-bottom walkthrough

`progress` filters recognition and first-decision denominators to observed fields; calculates procedure accuracy;
then applies the full rule: three recognized problem IDs, professor/timed/cumulative first decision, two correct
variants, no critical failure, and a timed success at least one day after earliest evidence.
`assessment_evidence_status` labels transfer readiness but explicitly withholds full mastery because assessment
answers do not collect recognition/first-decision.

### D. Example

Four correct same-day answers do not master a family. Adding delayed L6 evidence still requires recognition and
first-decision evidence.

### E. Problems found / F. Changes made

`mastered` was permanently false; it is now achievable under the source-grounded rule.

## 17. `src/math153_tutor/paths.py`

### A. Purpose

Centralizes filesystem roots so persistence does not depend on `pwd`.

### B/C. Connections and walkthrough

`REPOSITORY_ROOT` derives from the installed module location. `learner_data_root` respects
`MATH153_DATA_DIR`—useful for Streamlit Cloud mounts and isolated tests—otherwise uses repository
`learner_data`. `content_root` and `source_manifest_path` point to repository assets.

### D–F. Example/problems/changes

Launching from `/tmp` still reads repository content and writes the configured data directory. This fixes the old
relative-path deployment bug.

## 18. `src/math153_tutor/assessment.py` supporting model flow

This file is covered in section 4; it is listed again here to emphasize that it actually exists in the current
tree and is not a proposed design artifact.

## 19. `src/math153_tutor/__init__.py`

### A–C. Purpose, connections, walkthrough

The empty package marker tells Python that `math153_tutor` is importable. It deliberately performs no eager
imports, database creation, or Streamlit calls, keeping imports predictable.

### D–F. Example/problems/changes

`import math153_tutor.validation` loads only requested package/module code. No audit change was needed.

## 20. `scripts/build_source_manifest.py`

### A. Purpose

Command-line adapter for the typed source manifest service.

### B/C. Connections and walkthrough

It imports `build_inventory_manifest`/`write_manifest`, finds `*_inventory.txt`, errors when none exist, accepts
an optional extracted source root, and writes CSV. The module guard validates two or three arguments and prints a
usage message through `SystemExit`.

### D. Example

`PYTHONPATH=src python scripts/build_source_manifest.py data/source_registry data/derived/source_manifest.csv`
records 222 inventoried files as absent rather than emitting an empty file.

### E/F. Problems and changes

The old script scanned binaries only and classified everything `unclassified`. Logic moved into a typed tested
module; the script is now a small CLI.

## 21. `scripts/extract_sources.py`

### A. Purpose

Safely extracts a supplied source archive without permitting zip-slip paths.

### B/C. Connections and walkthrough

`safe_extract(zip_path, destination)` resolves the destination, creates it, inspects every archive member, and
rejects any target outside the destination before extracting. The CLI requires archive and destination.

### D. Example

An entry `../../secret` raises `ValueError`; a normal `math153/Quiz_1.pdf` extracts.

### E/F. Problems and changes

No archives exist in this repository, so extraction cannot be run on actual course sources. The security logic
is sound and unchanged.

## 22. `scripts/__init__.py`

This one-line package marker makes maintenance scripts importable by tests without executing their command-line
blocks. It imports nothing and has no side effects.

## 23. Test modules

Tests are also Python files and are part of the application contract:

- `test_app.py` drives real Streamlit widgets through navigation, material persistence, Paper Mode,
  assessment completion, Review/Repair, Professor return, Next-Line Coach, graph persistence, and Progress.
- `test_assessment.py` covers deterministic assembly, grading, timing, snapshots, and repository round trips.
- `test_content.py` loads every canonical Markdown family.
- `test_course_materials.py` covers YAML/Markdown provenance and search.
- `test_design_artifacts.py` checks required design files/links/headings.
- `test_full_scope.py` audits ten variants for every catalog family and every validator.
- `test_generation.py` audits the legacy four-family generator.
- `test_learning_engines.py` covers distractors, steps, graph points, and achievable mastery.
- `test_markdown_loader.py` covers valid and malformed canonical authoring.
- `test_sessions.py` covers independent evidence and no fabricated assessment recognition.
- `test_source_manifest.py` covers classification, absence, pairing, and CSV.
- `test_validation.py` covers equivalence, signs, and log-domain rejection.

The tests import production modules, provide temporary storage roots, act on widgets rather than calling UI
functions directly where practical, and assert persisted artifacts/results.
