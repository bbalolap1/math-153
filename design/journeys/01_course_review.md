# 01 — Course Review

**Status:** draft / needs owner decision

- **Learner goal:** see how one concept changes from lecture form to exercise, activity, and assessment construction before beginning paper practice.
- **Entry point:** Course Review → chapter group.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Choose Foundation, Chapters 1–2, Chapters 3–4, or Chapter 5 | CHAPTER_SELECTION | load curriculum index (proposed) | optional preference |
| 2 | Choose section | SECTION_OVERVIEW | load reviewed family/source links (proposed) | none |
| 3 | Select concept/family | CONCEPT_VIEW | load `QuestionFamily` via content index (proposed adapter) | none |
| 4 | Compare lecture/activity/quiz-test forms | SOURCE_COMPARISON | load linked SourceSegments (proposed) | viewed constructions |
| 5 | Inspect “what changed” | SOURCE_COMPARISON | compute/show authored comparison fields | viewed clues |
| 6 | Try a bridge example | GUIDED_EXAMPLE | build reviewed template problem (proposed) | draft attempt if submitted |
| 7 | Begin paper practice | PRACTICE_TRANSITION | create session (proposed) | Session |

- **Exit condition:** learner starts practice or returns to section list.
- **Unresolved:** comparison density; three columns vs sequential view; whether original source image is visible by default; bridge-problem count.
- **Blocker:** actual linked source binaries/segments are absent.
