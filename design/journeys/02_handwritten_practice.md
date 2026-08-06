# 02 — Handwritten Practice

**Status:** draft / needs owner workflow approval

- **Learner goal:** recognize construction, decide, solve on paper, submit the required form, repair the exact failure, and transfer to a controlled variation.
- **Entry point:** approved session setup or Course Review practice transition.

| Step | Learner action | UI state | Backend action | Stored data |
|---|---|---|---|---|
| 1 | Select scope/count/layer | SESSION_SETUP | SessionService.create (proposed) | Session |
| 2 | Read problem without method clues | PROBLEM_PRESENTATION | provide `GeneratedProblem` | exposure timestamp |
| 3 | Identify family/clues | RECOGNITION | compare/record later via controller | recognition/confidence draft |
| 4 | Choose first decision | FIRST_DECISION | record later via controller | first-decision draft |
| 5 | Solve on paper | PAPER_WORK | start paper timer | paper start/end |
| 6 | Enter form-specific answer | ANSWER_ENTRY | build AnswerSubmission (proposed) | submission draft |
| 7 | Submit | VALIDATING | current `validate_answer`; current repository via `submit_attempt` | Attempt |
| 8a | Continue after correct | CORRECT_FEEDBACK | update session evidence (proposed) | result/checks |
| 8b | Select repair after incorrect | INCORRECT_FEEDBACK | DiagnosisService proposed | inferred/self-reported error |
| 9 | Complete bounded repair/retry | REMEDIATION | RemediationService proposed | hint/retry attempt |
| 10 | Solve controlled variation | RELATED_PROBLEM | reviewed generator proposed | transfer attempt |
| 11 | Advance/end | PROBLEM_COMPLETE / SESSION_COMPLETE | session controller proposed | session summary/review queue |

- **Exit condition:** configured session target reached, or explicit Save & Exit.
- **Unresolved:** mandatory recognition layers; navigation; timer; answer input; feedback depth; remediation escalation; progress form.
