# Math 153 Version 0 — Evidence-Based Repository Audit

## Audit scope and method

This audit reads the project instructions, product/content/source documentation, Figma handoff,
design journeys and state maps, every canonical family Markdown file, both source inventories, every
Python module under `src/math153_tutor/`, both scripts, and the complete test suite. The current source
tree contains the inventory text files but no referenced PDF, image, transcript, or archive binary.

## Information-flow traces

### Inventoried course sources

`data/source_registry/*_inventory.txt` → `source_manifest.build_inventory_manifest()` →
`data/derived/source_manifest.csv` → inventory-only source records. Because the binaries are absent,
the flow correctly stops before visual/text extraction and source-backed family authoring. Canonical
family Markdown therefore retains `MODEL-INFERENCE-PENDING-SOURCE-REVIEW`.

### Canonical family and problem flow

`content/chapter_*/*.md` → `markdown_loader.load_question_family()` → `QuestionFamily` → Course
Review and Professor metadata. Separately, controlled Python templates in `practice_catalog.py` →
`PracticeProblem` → `assessment.build_assessment()` or a learning tool → `validation.py` → typed
question/attempt records → SQLite repositories → Review, Repair, evidence status, and Progress.

The canonical Markdown and 35-family runtime catalog are not yet one authoring source: only four
families have canonical Markdown. The UI does not claim the other catalog entries are complete
source-reviewed `QuestionFamily` records.

### Learner-added material flow

Add Material form → `course_materials.save_course_material()` → original Markdown body plus source ID,
course, section, topic, source type, timestamp, and `learner_added_unverified` status → parser/index →
Dashboard search → Course Review → Professor Mode retrieval by section/skill. Learner content is never
promoted to professor-verified evidence and is not automatically used to generate questions.

## Root-cause and remediation report

| User experience | Exact owner | Root cause and triggering state | Category | Fix | Regression test |
|---|---|---|---|---|---|
| Dashboard card raised “`navigation_page` cannot be modified…” | `app.py::_go`, `_sidebar` | Older deployed code assigned a widget-owned key after the sidebar radio was instantiated in the same run. | UI/state bug plus deployment/version mismatch | Queue `pending_navigation`, synchronize `navigation_selector` before widget creation, then rerun. Current tree contains this fix. The supplied traceback line numbers match an older, shorter revision; no repository remote/deployment API is available to prove which commit Streamlit Cloud currently serves. | `test_dashboard_cards_queue_navigation_without_mutating_sidebar_widget` and section-shortcut test click the real buttons. |
| Data files depended on launch directory | `app.py` path constants | Relative `learner_data/...` resolved against the process working directory. | persistence/deployment bug | `paths.py` resolves repository-root storage, with `MATH153_DATA_DIR` for deployments/tests. | App tests run from temporary working directories with explicit data roots. |
| Source registry could not describe absent files | old `scripts/build_source_manifest.py` | It scanned only extracted binaries, so an absent archive produced an empty manifest and lost inventory evidence. | source/architectural gap | Typed manifest builder now parses real inventories, classifies filename evidence, pairs obvious question/solution names, records presence/hash, and labels absent files `inventory_only`. | `test_source_manifest.py`. |
| Added notes stopped after save/display | `course_materials.py`, Dashboard, Course Review, Professor Mode | Metadata had no source ID/topic/verification status and there was no search/retrieval function. | content/pipeline gap | Preserve typed provenance, tokenize/index search, deep-link results, and retrieve section-relevant learner notes in Professor Mode. | course-material round-trip/search and AppTest persistence tests. |
| Assessment distractors included `999999` or arithmetic offsets | `practice_catalog.generate_practice_problem`, old `assessment_choices` | A sentinel was used to satisfy negative tests; generic choices were appended without family semantics. | generation bug | Preserve authored wrong answers, reject accidentally equivalent wrong answers, and build family/answer-form-aware distractors with named error patterns. | distractor and full-catalog validator tests. |
| Review could not explain why an option was wrong | `AssessmentQuestionResult`, `assessment.grade_question` | Only validator error code was retained. | data-model/review gap | Persist the selected distractor’s likely error pattern and display it in the single-assessment review. | assessment tests retain problem, explanation, and category. |
| Next-Line Coach only compared UI strings in `app.py` | old `_line_matches` | Parsing, family checks, and feedback were buried in UI code. | validation/architecture gap | Typed `step_engine.py` checks one checkpoint, recognizes equivalent equations/expressions, enforces supported log-domain opening checks, and returns bounded parse/transformation feedback. | `test_step_engine_accepts_equivalent_equation_and_rejects_invalid_line`. |
| Graph preview gave no persisted learning evidence | `_interactive_graph_demo` | Coordinate checking was inline and did not create an attempt. | UI/persistence gap | Typed graph question and point validator capture selected coordinates, validate the exact set, and persist a graph attempt. | graph validator test and Streamlit graph journey test. |
| `mastered` was permanently false | `mastery.progress` | The first implementation calculated ratios but had no evidence rule. | mastery gap | Full mastery can now be earned only with three recognized problems, professor/timed first-decision evidence, two correct variants, no critical failure, and delayed timed success. Assessment-only status remains explicitly non-mastery. | delayed complete-evidence mastery test. |
| Professor Mode taught a detached default problem | `_active_assessment`, `_professor_mode` | Active assessment problem was not transferred into teaching context. | state/connection bug | “Ask Professor Mode” carries the active `PracticeProblem`, preserves the widget-owned unsent selection, and returns to the same assessment index. | unsent-assessment-answer preservation test. |
| Assessment scope could not be narrowed to topics | `_assessment_launcher`, `assessment.build_assessment` | Only broad group selection was passed to the catalog. | UI/generation gap | Topic multiselect filters eligible family IDs inside selected scopes. | assessment build and complete AppTests. |
| Canonical families lacked explicit trap/template sections | family Markdown, `QuestionFamily`, loader | Required architecture fields were only implicit in common errors/construction prose. | content-model gap | Added required professor-trap and three controlled-template sections, explicitly marked model-inferred pending review. | all-family parse tests and missing-heading tests. |
| Questions and choices exposed validator syntax such as `4*x+(-9)` | `app.py` prompt/choice/solution rendering | Stored SymPy-compatible strings were reused directly as learner-facing labels; Streamlit radio labels do not reliably typeset LaTeX. | mathematical-presentation bug | `math_display.py` separates raw validator answers from LaTeX presentations; choices render as labeled math cards while radios store the unchanged raw value. | `test_math_display.py` plus Streamlit assessment/tool journeys. |
| Short assessments started with the easiest variant slots | `assessment.build_assessment`, launcher | `index % 10` meant a five-question assessment always selected variants 0–4. | generation/progression bug | Launcher now defaults to the L5–L7 professor/timed/transfer pool and offers explicit bridge, full, and foundation progressions. | professor/transfer layer assessment test. |

## Feature-to-code architecture map

| Feature | UI owner | Domain/model owner | Generation | Validation | Persistence | Source/content | Tests |
|---|---|---|---|---|---|---|---|
| Dashboard/navigation | `app.py` | session-state contract in `app.py` | — | destination guard | transient state | course scope + learner index | `test_app.py` |
| Course Review | `app.py` | `QuestionFamily`, `CourseLesson` | — | Markdown parser | learner Markdown | `course_content.py`, `content/`, `course_materials.py` | content/material/App tests |
| Added material/ingestion | `app.py` | `AddedCourseMaterial` | — | Pydantic + YAML parse | Markdown files | `course_materials.py` | `test_course_materials.py` |
| Source manifest | — | `SourceManifestEntry` | filename classifier | Pydantic | derived CSV | registries + `source_manifest.py` | `test_source_manifest.py` |
| Practice catalog | Course Review/assessment/tools | `FamilySpec`, `PracticeProblem` | `practice_catalog.py` controlled templates | `validation.py` | via attempts/assessments | model inference refs | `test_full_scope.py` |
| Canonical question families | Course Review/Professor | `QuestionFamily` | four legacy templates in `generation.py` | `validate_answer` | `AttemptRepository` | Markdown + loader | content/generation tests |
| Assessment creation/runtime | `app.py` | assessment models | `assessment.py` + catalog | `grade_question`/practice validator | `LearningRecordRepository` | catalog provenance | assessment/App tests |
| Multiple choice | `app.py` | `Distractor` | `distractors.py` | practice validator rechecks options | result record | family error patterns | learning-engine tests |
| Graph questions | `app.py` | `GraphQuestion`, `GraphPoint` | controlled graph constants/catalog parabola | `graph_questions.py` | practice attempts | model-inferred ref | graph tests |
| Paper Answer | `app.py` | `PracticeAttempt` | catalog | practice validator | `PracticeAttemptRepository` | catalog | AppTest |
| Professor Mode | `app.py` | active `PracticeProblem` | parallel catalog variant | — | preserves assessment state | lessons, family metadata, learner index | AppTest |
| Next-Line Coach | `app.py` | `StepCheck` | authored solution checkpoints | `step_engine.py` | transient state | worked solution/family | learning-engine/App tests |
| Review | `app.py` | assessment result/record | — | stored result | learning repository | worked solution/source refs | AppTest |
| Mistake Repair | `app.py` | `RepairRecord` | catalog transfer variant | practice validator | learning repository | family rule/skills | AppTest |
| Mastery/Progress | `app.py` | attempts/results/repairs | — | evidence rules in `mastery.py` | both repositories | family mastery rule | sessions/engine/App tests |
| Archive extraction | — | — | — | zip-slip path validation | extracted filesystem | `extract_sources.py` | script behavior is deterministic; binaries absent |

## Streamlit state table

| Key | Owner / initialization | Mutation | Lifetime | Widget-owned? |
|---|---|---|---|---|
| `navigation_selector` | sidebar radio | user callback; pre-widget pending sync | session | yes; never changed after instantiation |
| `navigation_page` | `_sidebar` | navigation callback/pre-widget sync | session | no |
| `pending_navigation` | `_go` | consumed before sidebar radio | one rerun | no |
| `course_choice` | sidebar radio | user | session | yes |
| `review_group` | Course Review radio | user; Dashboard before rerun | session | yes once Course Review renders |
| `review_topic`, `review_material_id` | Dashboard search | consumed by Course Review | one navigation | no |
| `show_add_material` | Course Review | add/save actions | transient | no |
| `tool_view` | tool buttons/review route | user/program action | session | no |
| `practice_tool_problem` | active tool helper/assessment professor route | related problem or active assessment | session | no |
| `paper_answer_choice_*` | Paper radio | user | session/problem | yes |
| `paper_result` | Paper submit | submit/new problem | session/problem | no |
| `coach_step` | Next-Line Coach | valid line/reset/new problem | session/problem | no |
| `repair_assessment_id`, `repair_problem_id` | Review | repair routing | session | no |
| `repair_check_*`, `transfer_*` | repair radios | user | session/problem | yes |
| `repair_passed_problem_id` | repair submit | rule result | session/problem | no |
| `assessment_problems`, `assessment_results` | launcher | question submit | active assessment | no |
| `assessment_draft_answers` | launcher/assessment Professor route | snapshots unsent widget values before leaving the page | active assessment | no |
| `assessment_index` | launcher | each accepted answer | active assessment | no |
| `assessment_started`, `assessment_type`, `assessment_scopes` | launcher | read until completion | active assessment | no |
| `assessment_active`, `assessment_complete`, `completed_assessment_id` | launcher/runtime | exit/completion/results | session | no |
| `assessment_answer_*` | answer radio | user; preserved across Professor Mode | session/question | yes |
| `professor_return_to_assessment` | assessment Professor action | return button | transient | no |
| `graph_points` | graph multiselect | user | session | yes |

## Source coverage

The derived manifest contains every unique filename from both inventories. Section numbers are inferred
only when encoded directly in filenames. Question/solution pairing is inferred only from normalized
matching names. Every row is `inventory_only`, `binary_present=false`, and has no hash because no binary
exists. Consequently, pages, exact questions, official answers, professor traps, typography, graphs,
and topic mapping for assessments cannot be reconstructed honestly. See
`data/derived/source_manifest.csv` and `data/derived/source_conflicts.md`.

## Remaining hard boundaries

1. Professor-source fidelity is blocked by absent binaries, not by application code.
2. Only four families have canonical authored Markdown; the 35-family Python catalog is broad V0
   practice coverage, not 35 completed source-reviewed families.
3. Arbitrary handwritten proof checking is outside bounded V0 technology; the step engine validates the
   controlled solution graph for supported generated templates.
4. Streamlit's Vega interaction API is not used as a free-click canvas; V0 captures explicit plotted
   coordinate selections and validates/persists them.
5. The environment exposes no Streamlit Cloud deployment API or configured Git remote, so deployed
   commit identity cannot be inspected locally. The supplied old traceback is a deployment-version
   mismatch relative to the tested current tree.
6. Direct access to Figma file `CiDJSaewXbedKrSY2WUBgs` returns HTTP 401 in this environment. Screen
   comparison therefore uses the repository-approved node registry and handoff contract rather than
   unauthenticated pixel inspection.
7. The professor worksheets/tests/screenshots requested for construction analysis are still not present
   anywhere in the working tree. Their inventory filenames are not enough to reconstruct wording. Those
   exact PDF/image binaries must be uploaded before their question formulations can be transcribed to
   Markdown and promoted from model inference to reviewed source templates.

## Prompt-grounded first procedural family

The user-provided domain example is now recorded as
`USER-PROMPT-2026-08-08-DOMAIN-EXAMPLE`, not as a verified professor binary. The canonical family
`CH34-DOMAIN-RADICAL-RATIONAL` preserves these invariants: even radical, variable denominator, two
restriction rules, intersection, and interval notation. Controlled variants change coefficients,
variables, function names, boundary locations, and whether the denominator zero lies inside the radical
interval. Five generated examples are required and mathematically validated by the build gate.

`scripts/validate_build.py` fails when authored source Markdown is empty, a family cannot parse or lacks
source references, a generated example lacks a worked solution or validated answer, or a derived output
file is empty. Inventory-only missing binaries remain counted as `unresolved_sources`, not falsely read.
