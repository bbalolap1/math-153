# Math 153 Visual Architecture Report

## Current problem

The current application combines product decisions, workflow control, rendering, and backend orchestration inside one Streamlit script. It has useful primitives—typed problems/attempts, deterministic fixtures, symbolic checking, SQLite attempts, family Markdown, and tests—but the learner sees a generic four-family workflow rather than a source-shaped course system. Canonical family content is not connected to runtime generation; the UI directly calls submission, persistence, and progress code; and unapproved sidebar, recognition, timer, feedback, and mastery choices appear as if final.

The disconnect is not primarily cosmetic. There is no approved layer translating the handwritten learning journey into screen states, component data contracts, and backend events.

## Evidence from source materials

### Verified

The source registries name:

- section PDFs 1.1–1.4, 2.1–2.7, and 3.1–3.4;
- four activities and a Completing the Square document;
- quizzes 1–6 with several solution files;
- Test 1, its solution/review, a Test 2 review;
- final-exam Versions 1–3 with/without solutions;
- a chronological collection of screenshot filenames.

This naming evidence supports a design that distinguishes sections, activities, assessments, solutions, and final versions. Multiple source roles and solution pairing must be first-class metadata.

### Not verified

The actual PDFs, screenshot pixels, notes, and transcripts are absent from the repository and Git history. Section 1.5 is not listed. Therefore this report does not claim their typography, layout, tables, graphs, blank space, wording, or question construction. The static logarithm examples are labeled fixtures rather than transcriptions.

### Implication after source restoration

The review pipeline must visually inspect and segment each question/solution, then author explicit construction records: information order, representation, parts, inference, prerequisites, first decision, answer form, traps, difficulty rationale, and variation boundaries. Only then can the interface honestly compare lecture → activity → quiz/test → final construction or produce professor-style variants.

## Proposed visual system

### Screen hierarchy

```text
Course Review
├── Chapter Group Selection
├── Section Overview
├── Concept View
├── Source Comparison (lecture | what changed | assessment)
└── Practice Transition

Handwritten Practice
├── Session Setup
├── Problem Presentation
├── Recognition
├── First Decision
├── Paper Work
├── Answer Entry / Validating
├── Correct or Incorrect Feedback
├── Targeted Remediation
├── Related Problem
└── Session Summary

Next-Line Coach (separate state machine)
Professor Mode / Assessment Report (separate state machine)
Mistake Review / Repair (separate journey)
```

### Visual direction

The proposal is a restrained, worksheet-aware workspace: stable problem position, mathematical whitespace, explicit separation of prompt/instruction/response, only one active stage, low-emphasis progress, limited active-session navigation, and source context available without crowding the solver. This direction is a proposal—not an approved imitation of the unavailable PDFs.

### Review artifacts

- `design/wireframes/index.html`: clickable gallery of required static screens.
- `design/prototypes/handwritten-practice.html`: isolated fake-data interaction from recognition through related problem.
- `design/screens/`: one specification per required screen.
- `design/approvals/screen_status.md`: explicit unapproved statuses.

## Backend connection

Existing production capabilities map as follows:

- Current `GeneratedProblem`/`generate_problem()` can temporarily supply a problem fixture.
- Current `validate_answer()` supplies limited symbolic validation.
- Current `submit_attempt()` and `AttemptRepository` can persist a basic attempt.
- Current `progress()` supplies only three coarse evidence ratios.
- Current Markdown loader can parse family definitions but has no runtime index/adapter.

The proposed page architecture is:

```text
renderer/page
→ state-specific view model
→ session controller event
→ domain service
→ validator/repository/content adapter
```

The exact component/event/data mapping is in `design/connections/ui_backend_map.md`. Proposed services are labeled rather than represented as existing code.

## Gaps

1. Reviewed source binaries, manifest, segments, and question/solution links.
2. Content index connecting Markdown families to runtime services.
3. Source-backed ProfessorConstruction and representation/media models.
4. Session model/controller with typed states and validated transitions.
5. AnswerSubmission and validator-form adapter/registry.
6. Domain/range/interval/equation/table/graph/unit validators.
7. ErrorDiagnosis and bounded Remediation services.
8. Related/delayed-transfer scheduler and review queue.
9. Full mastery dimensions and critical-error blocking.
10. Assessment builder, response repository, scorer, and report.
11. Branch-aware Next-Line StepEngine.
12. State-specific view models and reusable renderer components.

## Framework recommendation

**Recommendation: retain Streamlit for the next isolated functional prototype, contingent on owner approval.**

The current failure is architectural, not proof that Streamlit is incapable. Streamlit can render one active state with columns/containers, math, tables, media, forms, and responsive CSS. It should not own transitions or call repositories directly. A typed controller/view-model boundary and reusable render functions can correct the immediate disconnect.

Known Streamlit constraints include rerun semantics, limited client-side interaction, coarse fine-grained responsive control, and difficulty creating advanced math editors or graph interactions. Those limitations become migration evidence only if an approved screen cannot be implemented faithfully.

A migration now would duplicate UI work and leave the missing source/content/session services unresolved. If later required, retain Pydantic models, content loaders, generators, validators, repositories, and domain/controller tests; expose them through a local API; migrate one approved journey at a time; compare each implementation against approved wireframes.

## Decisions Codex made

Only low-risk design-document choices were made: static backend-free artifacts, explicit state names, accessible semantic HTML/CSS, fake-data labels, and clear “existing vs proposed vs blocked” terminology. No production behavior changed.

## Owner decisions required

### 1. Workflow recognition

- Required on selected layers (recommended): measures transfer without burdening every direct problem.
- Required on every practice problem: strongest measurement, repetitive.
- Optional: flexible, incomplete evidence.

### 2. Active-problem layout/navigation

- Stable context rail plus work area and minimal Save/Exit (recommended): orientation with focus.
- Single centered card with compact header: strongest focus, less persistent context.
- Persistent full navigation: fastest switching, most clutter/risk.

### 3. Incorrect feedback/remediation

- Replace answer form, then clue → first-line cue → prerequisite → partial example (recommended): one active repair task.
- Inline feedback below answer, one clue then explanation: simpler, longer page and quicker reveal.
- Learner chooses help depth: control, but encourages premature solution access.

### 4. Course Review comparison

- Three columns desktop / ordered stack narrow (recommended): explicit simultaneous comparison.
- Step-through source forms: lower density, weaker comparison.
- Source image plus annotation drawer: strongest fidelity after binaries exist.

### 5. Professor Mode locking

- Editable navigation until final submit (recommended).
- Lock each response on Continue.
- Derive behavior per reviewed assessment source.

### 6. Visual direction

- Restrained worksheet workspace (recommended).
- Course-document facsimile influence after source review.
- Modern digital study workspace.

### 7. Framework

- Retain Streamlit for one approved isolated workflow (recommended).
- Continue only with static prototype before framework choice.
- Migrate now (not recommended without demonstrated approved-screen limitation).

## Production implementation after approval

Approve one journey and one screen at a time. First implement only the approved Handwritten Practice state/controller and one representative reviewed problem. Connect only approved components, produce an approved-vs-implemented difference report, and stop for owner review. Do not add content breadth, analytics, builders, or other modes until the workflow is accepted.
