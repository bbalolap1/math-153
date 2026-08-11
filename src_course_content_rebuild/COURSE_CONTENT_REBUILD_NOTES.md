# Math 153 course-content rebuild

This patch replaces `src/math153_tutor/course_content.py` with a source-grounded canonical course model.

Coverage:
- 25 section-level entries including Foundation and Sections 1.1–5.6 present in the supplied Markdown sources
- 56 explicit problem families
- 214 source references
- no MODEL-INFERENCE-PENDING-SOURCE-REVIEW placeholders
- Foundation + Unit 1 (Chapters 1–2) + Unit 2 (Chapter 3) + Unit 3 (Chapters 4–5)
- backward-compatible `COURSE_LESSONS` aliases for the current Streamlit app

Important:
This patch intentionally does not pretend that the rest of the application is fixed.
`practice_catalog.py`, `assessment.py`, `complexity.py`, `generation.py`, `distractors.py`,
and `app.py` still require source-fidelity refactors so they consume the canonical problem
families and source exemplars instead of generating shallow numeric variants.
