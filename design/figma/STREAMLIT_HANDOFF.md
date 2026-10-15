# Figma → Streamlit Handoff

This file is the repo-readable contract for the approved Math 153 Figma workflow.

Figma file: `CiDJSaewXbedKrSY2WUBgs`  
Product stack: Python + Streamlit  
UI direction: dashboard-first; restrained worksheet/textbook surface; Inter UI; math rendered as math.

## Live workflow

| Order | Figma node | Screen | Streamlit owner |
|---|---|---|---|
| 01 | `57:158` | Dashboard — Welcome | `app._dashboard` |
| 02 | `57:159` | Course Review — Math 153 | `app._course_review` |
| 03 | `67:334` | Foundation — Textbook View | `app._course_review` + `COURSE_GUIDE` |
| 04 | `68:375` | Chapters 1–2 — Textbook View | `app._course_review` + repository family Markdown |
| 05 | `68:395` | Chapters 3–4 — Textbook View | `app._course_review` + repository family Markdown |
| 06 | `68:415` | Chapter 5 — Textbook View | `app._course_review` + repository family Markdown |
| 07 | `68:456` | Add Course Material | `app._add_course_material` + `course_materials.py` |
| 08 | `60:356` | Learning Tools — Hub | `app._learning_tools` |
| 09 | `57:160` | Quiz / Test / Exam Launcher | `app._assessment_launcher` |
| 10 | `57:161` | Active Assessment — Readable Math | `app._active_assessment` |
| 11 | `59:314` | Active Assessment — Interactive Graph | `app._interactive_graph_demo` |
| 12 | `35:125` | Paper Answer Mode | `app._paper_answer_mode` |
| 13 | `35:126` | Professor Mode | `app._professor_mode` |
| 14 | `35:127` | Next-Line Coach | `app._next_line_coach` |
| 15 | `35:128` | Quiz / Test Review | `app._quiz_review` |
| 16 | `35:129` | Mistake Repair | `app._mistake_repair` |
| 17 | `44:158` | Learning Note | repository family Markdown is surfaced in Course Review; a dedicated editable note service is not yet implemented |
| 18 | `26:38` | Progress + Source Library reference | `app._progress_page`; source binaries remain unavailable |

## Approved navigation

Course choices: `Math 153`, `07`.

Primary navigation:

1. Dashboard
2. Course Review
3. Learning Tools
4. Quiz / Test / Exam
5. Progress

The app must never open directly into an assessment. Dashboard is the default launch surface.

## Course Review contract

Course Review behaves like a digital course binder/textbook, not a course map. Selecting Foundation,
Chapters 1–2, Chapters 3–4, or Chapter 5 must reveal readable teaching content. Repository-authored
question-family Markdown remains canonical content. User-pasted transcripts/notes are persisted as
Markdown under `learner_data/course_materials/` and are clearly distinct from verified professor sources.

## Assessment contract

The launcher collects assessment type, scope, answer format, and length before starting. The current
runtime supports controlled generated families plus multiple-choice submission. The selected answer is
validated by the existing SymPy-aware validator.

Assessment attempts intentionally do **not** fabricate recognition or first-decision evidence. Those
dimensions are only scored when the learner actually completes those tasks.

## Math rendering contract

- Prefer LaTeX/Streamlit math rendering for fractions, radicals, exponents, roots, sets, and symbols.
- Never require the learner to read Python-style syntax as the primary mathematical presentation.
- Graph-family questions require an interactive coordinate plane with readable axes and coordinates.
- `app._interactive_graph_demo` is the first UI adapter. Scored graph-point validation is still a backend gap.

## Backend status by learning tool

| Tool | Current implementation | Remaining backend gap |
|---|---|---|
| Paper Answer Mode | Full-scope catalog problem + multiple-choice result + validator + persistent attempt | richer source-reviewed distractors |
| Professor Mode | Rule, prerequisites, bounded hint/deeper explanation, parallel example, and walkthrough | indexed professor-source citations after binaries are supplied |
| Next-Line Coach | Normalized symbolic/equation checking against the authored worked-solution path | unrestricted branch-aware symbolic step graph |
| Quiz Review | Persisted assessment sessions with prompt, learner/correct answer, explanation, and repair routing | source-linked explanation enrichment |
| Mistake Repair | Actual missed item, rule/setup repair, generated transfer check, and persistent repair result | delayed transfer scheduling |
| Progress | Assessment history, overall/topic accuracy, weak areas, paper attempts, and repair totals | delayed/varied mastery recommendation policy |

## Source-honesty boundary

The source registry contains filenames for professor/course screenshots, but the referenced binaries are
not present in this repository. The Streamlit build must not claim professor-source fidelity until those
materials are actually ingested and indexed.

## Codex continuation prompt

When continuing this implementation, start with this file plus `AGENTS.md`, `docs/PRODUCT_SPEC.md`,
`design/connections/ui-backend-map.md`, and the relevant question-family Markdown. Preserve the Figma
node mapping above. Compare the running Streamlit UI against the corresponding Figma node before calling
a screen complete.
