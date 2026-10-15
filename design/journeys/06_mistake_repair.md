# 06 — Mistake Repair

**Status:** draft concept / backend incomplete

- **Learner goal:** repair the decision or prerequisite causing recent downstream failures.
- **Entry point:** incorrect feedback, summary, or Mistake Review.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Choose recent error cluster | ERROR_CLUSTER | query attempts/diagnoses proposed | repair selection |
| 2 | See failure point and source-linked rule | REPAIR_OVERVIEW | load feedback rule/source segment | view event |
| 3 | Solve smallest prerequisite on paper | PREREQUISITE_REPAIR | reviewed repair template proposed | Attempt |
| 4 | Return to original family variation | FAMILY_RETRY | controlled generator/validator | Attempt |
| 5 | Complete changed-representation transfer | TRANSFER_RETRY | session/review service proposed | transfer status |
| 6 | Schedule delayed check | REPAIR_COMPLETE | review queue proposed | ReviewQueueItem |

- **Exit condition:** prerequisite and family retry complete; mastery remains evidence-based.
- **Unresolved:** clustering authority, learner override, number of repairs, delayed interval, critical-error blocking display.
