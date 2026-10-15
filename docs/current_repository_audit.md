# Current Repository Audit

**Verified:** 2026-08-06  
**Branch:** `codex/conduct-initial-repository-audit-fsk87prepo`  
**Production-code baseline audited:** `src/math153_tutor/` at commit `8d29684` parent state.  
**Method:** complete tracked-file inventory; Python, Markdown, templates, scripts, tests, inventories, and existing design artifacts read directly. No PDF or image binary exists in the working tree or Git object history, so visual course-source claims are explicitly blocked.

## 2.1 Current application structure

### Entry points

- `src/math153_tutor/app.py`: single Streamlit entry point; `main()` selects one of four rendered branches.
- `pyproject.toml`: console entry `math153-tutor = math153_tutor.app:main`.
- No `pages/` directory, multipage Streamlit entry, or separate production UI component package exists.

### Pages

The app simulates four pages inside one script: Practice Session, Course Map, Source Library, and Progress. Handwritten Practice contains recognition, first decision, paper, answer, and combined feedback states.

### Components

There are no reusable UI component modules. Forms, cards, messages, metrics, navigation, and state transitions are authored directly with `st.*` calls in `app.py`.

### Backend services

- `generation.generate_problem()`: deterministic selection of one of four hard-coded templates.
- `sessions.submit_attempt()`: orchestrates validation, error tags, attempt construction, and persistence.
- `validation.validate_answer()`: SymPy-backed expression/solution-set validation.
- `storage.AttemptRepository`: SQLite schema, insert, and list.
- `mastery.progress()`: three ratios; full mastery always false.
- `markdown_loader.load_question_family()`: Markdown/YAML parsing into Pydantic content model.

These are functions/modules rather than a formal service layer. Proposed services in design documents do not yet exist.

### Models

`DifficultyLayer`, `ErrorCategory`, `SourceRef`, `QuestionFamily`, `Attempt`, and `GeneratedProblem` are Pydantic models/enums. There is no Session, AnswerSubmission, Source, SourceSegment, Construction, StepGraph, Assessment, ReviewQueue, or view-model type.

### Storage

`AttemptRepository` writes JSON payloads plus selected index columns to ignored local SQLite at `learner_data/attempts.sqlite3`. Content remains Markdown/Python; no content database exists.

### Content loaders

The Markdown loader parses front matter, required `#` headings, and `## L0`–`L7` subsections. The production generator does not call it, so authored family content is disconnected from runtime questions.

### Validators

The registry named in the product specification is not implemented. One dispatch function handles `solution_set` and otherwise treats numeric, exact numeric, and expression declarations through a shared expression path. Interval, domain, range, equations, ordered pairs, lines, tables, units, and graph features are absent.

### State handling

Streamlit session state uses free-form string stages and widget keys. Domain state, workflow state, result tuples, and widget state are mixed in the same store. The page directly resets problems, calls repositories, and calls session/validation orchestration.

### Tests

- `test_app.py`: Streamlit transitions and navigation.
- `test_content.py`: all family files parse and meet minimal fields.
- `test_generation.py`: deterministic runtime generation and provenance fields.
- `test_markdown_loader.py`: seed load and readable missing-heading error.
- `test_sessions.py`: validation/persistence/progress integration.
- `test_validation.py`: solution-set equivalence and basic incorrect answers.

No screenshot regression, source-resolution, manifest, accessibility, state-machine, domain/extraneous candidate, or assessment-flow tests exist.

## 2.2 Current UI inventory

| Screen | File | Visible elements | User purpose | Backend calls | State variables | Problems |
|---|---|---|---|---|---|---|
| Global shell | `app.py` | Sidebar page radio, review group, static mode list | Navigate and orient | none | `navigation_page`, `navigation_chapter` | Unapproved persistent sidebar; static modes look actionable but are not. |
| Practice selection | `app.py` | Title, family select | Choose among runtime families | `FAMILIES` registry | stage/problem | Only four generic Python templates; not source/content-index driven. |
| Recognition | `app.py` | prompt, family radio, confidence | Classify problem | none until final submit | widget/answer keys | Mandatory recognition is an unapproved product choice; no clue/answer-form recognition. |
| First decision | `app.py` | prompt, first-action radio | Commit initial action | none until final submit | decision keys, stage | No authored decision-path service or short-answer option. |
| Paper work | `app.py` | prompt, instruction, elapsed label, completion button | Solve away from screen | none | `started`, `stage` | Timer does not tick independently and begins before paper state. |
| Answer entry | `app.py` | generic text input, uncertainty select | Submit result | `submit_attempt()` → validator/repository | answer/error widget keys | Generic input; error self-report occurs before validation; direct DB orchestration from UI. |
| Combined feedback | `app.py` | result, diagnosis, three metrics, mastery caption, retry | Understand result and repeat | repository query, `progress()` | `result`, `problem` | Combines feedback, analytics, policy, and next action; no remediation state. |
| Course Map | `app.py` | expanders and topic status rows | See intended coverage | none | navigation | Hard-coded scope; availability inferred from title matching. |
| Source Library | `app.py` | missing-source warning, filename lists | See inventory | filesystem reads | navigation | Lists files rather than reviewed sources; binaries absent. |
| Progress | `app.py` | family headings and three metrics | See evidence | repository list, `progress()` | navigation | Partial mastery model shown with unapproved visual treatment. |

## 2.3 Backend inventory

| Backend component | Responsibility | Inputs | Outputs | Current UI connection | Missing connection |
|---|---|---|---|---|---|
| `generation.FAMILIES` | Four runtime labels | none | dict | selects family/navigation | Markdown content index and reviewed source construction records |
| `generate_problem()` | Deterministic direct problem | family ID, seed | `GeneratedProblem` | reset/current prompt | session assembly, representation templates, source-backed generator |
| `load_question_family()` | Parse canonical family Markdown | path | `QuestionFamily` | none | family library, generator, validation/build index |
| `validate_answer()` | Symbolic equivalence | problem, answer | `ValidationResult` | via submit | formal registry and answer-form UI adapter |
| `submit_attempt()` | Validate, infer coarse errors, persist | problem + responses | attempt/result | answer submit | controller/event boundary, diagnosis/remediation service |
| `AttemptRepository` | Local attempts | path/attempt/filter | stored/listed attempts | submit/progress | repository abstraction for sessions, review queue, migration/error handling |
| `progress()` | Three evidence rates | attempts | dict | feedback/progress | full mastery dimensions, delayed transfer, critical blocking |
| `QuestionFamily` | Authored content shape | parsed Markdown | validated model | parser tests only | runtime family browser/generation |
| `GeneratedProblem` | Runtime prompt/answers/provenance | template data | validated model | practice | construction entity, form-specific answer schema, media |
| source scripts | extract/hash inventory | archive/source path | files/CSV | none | reviewed manifest, pairing/classification UI, available archives |

## 2.4 Disconnect report

### Backend without visible learner purpose

- Family Markdown contains decision paths, prerequisites, ladder, restrictions, common errors, and mastery rules but runtime UI/generation does not consume it.
- Exact-form flags and several validator declarations have no distinct answer components.
- Source extraction and manifest scripts have no resolved manifest or review UI.

### UI without backend responsibility

- Static sidebar mode list.
- Course availability checks based on label matching.
- Author-facing model-inference provenance caption inside the solving workspace.

### Workflow/state problems

- `stage` is an untyped string instead of an explicit transition-checked state machine.
- UI owns workflow transitions, generator calls, repository construction, validation submission, and progress reads.
- The result tuple is stored directly in Streamlit session state.
- The feedback branch combines result, diagnosis, analytics, mastery policy, and retry.
- Chapter navigation can reset the current problem without a formal save/exit event.
- Timer semantics do not equal paper time.

### Duplicated or unclear logic

- Runtime family metadata is duplicated between Python registries and canonical Markdown.
- Widget values and copied answer values coexist in session state.
- Current page name and workflow state are separate, uncoordinated navigation systems.

### Technically present but not meaningfully exposed

- Four Markdown family definitions.
- Full error taxonomy enum.
- difficulty layers and reasoning checkpoints.
- source filename inventories.

### Product decisions made without approval

Persistent sidebar, two-level navigation, mandatory recognition, confidence scale, choice counts, timer visibility, generic answer field, feedback layout, progress metrics, mastery caption, and Streamlit-as-current-interface were selected before owner approval.

## Verified source availability

The tracked registry lists section PDFs 1.1–3.4, activities, quizzes/solutions, tests/reviews, and final versions. A second registry lists screenshots. The binaries themselves are absent. Section 1.5 is not named in the tracked PDF inventory. No discussion-problem or transcript binary is present. Therefore source visual analysis and representative professor constructions cannot be verified until source files are supplied or restored.
