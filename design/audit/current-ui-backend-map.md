# Current-State UI and Backend Audit

This is an audit of commit `8e0cb7b`, not a future design. No production code was changed during this audit.

## Navigation and pages

| Screen | UI component | User purpose | Backend service | Data object | Event | Resulting state | Problem |
|---|---|---|---|---|---|---|---|
| Global | Sidebar page radio | Choose Practice, Course Map, Source Library, or Progress | none; direct Streamlit branching | `navigation_page` | radio change | selected page rerenders | Navigation model was selected without owner approval. |
| Global | Review-group select | Choose Chapters 1–2, Chapters 3–4, or Chapter 5 | module constants | `COURSE_SCOPE`, `navigation_chapter` | select change | Practice options change | Visible globally even where the choice has no effect. |
| Global | Mode status list | See proposed modes | none | hard-coded Markdown | none | none | Looks interactive but has no backend purpose. |
| Practice | Family select | Pick one of four runtime families | generation module registry | `FAMILIES`, `FAMILY_CHAPTER` | select change | calls `_reset_problem` | Only four generic templates; source families are not loaded from Markdown. |
| Practice | Problem card | Read current prompt | `generate_problem()` | `GeneratedProblem.prompt` | family/reset | stage becomes recognition | Provenance caption exposes authoring status in the learner view. |
| Recognition | Family radio | Classify structure | no service; equality later in `submit_attempt()` | `recognition_options` | form submit | `decision` | Recognition is mandatory; this is owner-controlled and unapproved. |
| Recognition | Confidence slider | Self-report confidence | persisted by `submit_attempt()` | integer 1–5 | form submit | `decision` | Placement and scale are unapproved. |
| First decision | Decision radio | Choose first operation | no service; equality later in `submit_attempt()` | `first_decision_options` | form submit | `paper` | Number and format of choices are unapproved. |
| Paper | Instruction banner | Require work away from screen | local state only | `stage`, `started` | Work-complete click | `answer` | Timer is calculated only on rerun and does not visibly tick. |
| Answer | Text input | Enter final answer | `submit_attempt()` → `validate_answer()` | answer string, `GeneratedProblem.validator` | submit | `complete` | One generic text field cannot represent all required answer forms. |
| Answer | Uncertainty select | Self-classify error | `submit_attempt()` | `ErrorCategory` | submit | `complete` | Asks for error classification before correctness is known. |
| Feedback | Success/error banner | See correctness | `validate_answer()` result | `ValidationResult` | submission result | `complete` | Correct and incorrect feedback share one broad state. |
| Feedback | Targeted message | Receive bounded correction | dictionary lookup | `targeted_feedback` | incorrect result | `complete` | There is no explicit remediation state or retry escalation. |
| Feedback | Three metrics | See evidence | `progress()` + repository query | stored `Attempt` list | render | none | Per-problem feedback and cumulative metrics are mixed on one screen. |
| Feedback | Related-problem button | Retry family | `generate_problem()` | next seed | click | `recognition` | No session length, completion rule, or delayed-transfer event. |
| Course Map | Expanders/topic rows | View intended coverage | none | hard-coded `COURSE_SCOPE` | expand | same page | Availability detection uses title matching, not content index status. |
| Source Library | Warning and inventory expanders | View listed source filenames | filesystem reads | inventory text files | expand | same page | No source binaries, stable manifest, segments, or question links. |
| Progress | Family headings and metrics | View accumulated evidence | `AttemptRepository.list()`, `progress()` | SQLite attempts | navigate | same page | Mastery dimensions and visualization were not owner-approved. |

## Streamlit state variables

| Key | Writer | Reader | Lifecycle issue |
|---|---|---|---|
| `navigation_page` | sidebar radio | `main()` | Global UI decision, not domain state. |
| `navigation_chapter` | sidebar select | `_practice()` | Can change while a problem is active. |
| `seed` | `_reset_problem()` | `_reset_problem()` | Increments locally; not a formal session seed. |
| `problem` | `_reset_problem()` | `_practice()` | Runtime `GeneratedProblem`; no session aggregate owns it. |
| `stage` | reset and form/button handlers | `_practice()` | Free-form strings instead of an explicit state-machine type. |
| `started` | `_reset_problem()` | paper/submission | Measures from problem creation, not strictly paper time. |
| `result` | answer submit | feedback branch | Tuple stored directly in UI state. |
| `recognition_widget` | Streamlit radio | Streamlit | Widget state. |
| `confidence_widget` | Streamlit slider | Streamlit | Widget state. |
| `recognition_answer` | recognition submit | answer submit | Duplicates widget value for persistence. |
| `confidence_answer` | recognition submit | answer submit | Duplicates widget value for persistence. |
| `decision_widget` | Streamlit radio | Streamlit | Widget state. |
| `decision_answer` | decision submit | answer submit | Duplicates widget value for persistence. |
| `final_answer_widget` | Streamlit text input | Streamlit | Widget state. |
| `uncertain_stage_widget` | Streamlit select | Streamlit | Widget state. |

## Current navigation paths

```text
Sidebar → Practice Session → Recognition → First Decision → Paper → Answer → Feedback → Related Problem
Sidebar → Course Map
Sidebar → Source Library
Sidebar → Progress
```

There is no current entry path for Professor Mode or Next-Line Coach.

## Backend with no adequate visible UI

- Canonical Markdown family loader: no family library or source-linked family detail.
- `QuestionFamily` decision paths, difficulty ladder, restrictions, common errors, and mastery rule: parsed but not rendered.
- Exact-form validation modes: modeled but no answer-form-specific UI.
- Attempt fields for hints, critical checks, and self-reported errors: incomplete or misleading presentation.
- Source models and extraction/manifest scripts: no reviewed source object UI.

## UI with no clear backend purpose

- Sidebar mode list is static text.
- Course Map completion markers are inferred by title comparison.
- Provenance caption is useful to authors but not clearly useful during solving.

## Multiple stages or excess information

The practice code renders one main interaction stage at a time, but the feedback state combines correctness, diagnosis, cumulative skill metrics, mastery policy, and next action. Global navigation and the static mode list remain visible throughout solving. This weakens focus even without one long form.
