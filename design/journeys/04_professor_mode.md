# 04 — Professor Mode

**Status:** not started / owner-controlled

- **Learner goal:** complete a source-backed assessment under minimal-guidance conditions and receive a report only after submission.
- **Entry point:** Professor Mode setup.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Select assessment/section/timing | ASSESSMENT_SETUP | builder/session service proposed | AssessmentSession |
| 2 | Solve active question on paper | QUESTION_ACTIVE | serve source-backed problem | timing/flags |
| 3 | Enter answer | ANSWER_CAPTURED | stage answer; no feedback | captured answer |
| 4 | Lock/continue | QUESTION_LOCKED/NEXT_QUESTION | persist captured response | response |
| 5 | Review flags and submit assessment | ASSESSMENT_SUBMITTED | batch validate/score proposed | scored attempts |
| 6 | Review report/remediation sequence | REPORT | aggregate family/skill/error breakdown | review queue |

- **Exit condition:** submitted report saved or abandoned according to approved policy.
- **Unresolved:** formulas, timer, answer locking, navigation, autosave, solution timing, report design.
