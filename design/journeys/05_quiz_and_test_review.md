# 05 — Quiz and Test Review

**Status:** not started; blocked on assessment binaries

- **Learner goal:** compare an original assessment construction, official solution expectations, personal attempt, and targeted retry without turning review into passive watching.
- **Entry point:** completed assessment report or Source Review.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Choose quiz/test/final version | ASSESSMENT_SELECTION | load reviewed manifest (proposed) | selection |
| 2 | Choose missed/flagged question | QUESTION_REVIEW | link question/solution/family | review event |
| 3 | Compare expected checkpoints, not hidden chain-of-thought | CONSTRUCTION_REVIEW | retrieve authored checkpoints | viewed feedback |
| 4 | Classify failure | ERROR_REVIEW | diagnosis service proposed | confirmed error |
| 5 | Solve related source-faithful variation on paper | REVIEW_RETRY | generator/validator | Attempt |
| 6 | Add delayed transfer | REVIEW_COMPLETE | review queue proposed | ReviewQueueItem |

- **Exit condition:** review queue updated.
- **Unresolved:** source-image/solution reveal timing, teacher marks, exact-copy privacy, comparison layout.
