# 03 — Next-Line Coach

**Status:** not started / needs owner decision

- **Learner goal:** validate one handwritten transformation at a time without revealing future steps.
- **Entry point:** family detail, remediation, or Next-Line setup.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Choose reviewed family/path | SETUP | load step graph (proposed) | StepSession |
| 2 | Read problem and solve next line on paper | PROBLEM_PRESENTATION/PAPER_WORK | expose current node | paper time |
| 3 | Enter only next line | STEP_ENTRY | create StepSubmission | line text |
| 4 | Submit transformation | STEP_VALIDATING | StepEngine.validate (proposed) | StepAttempt |
| 5a | Continue on valid branch | STEP_CORRECT | advance graph node | rule/branch |
| 5b | Retry bounded cue | STEP_INCORRECT/REMEDIATION | error-pattern lookup | hint level/retry |
| 6 | Finish branch and check | COMPLETE | summarize rules/errors | session result |

- **Exit condition:** valid terminal node or explicit defer.
- **Unresolved:** syntax, retry limits, branch display, optional domain lines, escalation/full-solution policy.
- **Missing backend:** all step-graph/step-validation capabilities.
