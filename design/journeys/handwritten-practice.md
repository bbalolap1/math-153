# Journey: Handwritten Practice

**Status:** draft; requires owner workflow approval.

## Learner goal

Recognize a professor-style construction, make the first mathematical decision, solve independently on paper, enter the required answer form, diagnose the exact failure point, and complete a controlled related problem.

## Proposed sequence

```text
Entry: choose Handwritten Practice
→ SESSION_SETUP: select review group, family scope, difficulty, and session length
→ start_session (SessionService; proposed—not implemented)
→ PROBLEM_PRESENTATION: see problem only; topic/method/hints hidden
→ acknowledge_problem
→ RECOGNITION: classify family/clue/answer form (whether required is unresolved)
→ record_recognition
→ FIRST_DECISION: enter/select first action
→ record_first_decision
→ PAPER_WORK: problem + paper instruction; answer and hints hidden
→ confirm_work_complete
→ ANSWER_ENTRY: answer control matches declared validator
→ submit_answer
→ VALIDATING: ValidationService validates; AttemptRepository stores
→ CORRECT_FEEDBACK or INCORRECT_FEEDBACK
→ if incorrect: REMEDIATION with one bounded correction → retry or prerequisite
→ PROBLEM_COMPLETE: related-problem or next-problem action
→ repeat until session target
→ SESSION_COMPLETE: summary and review queue
```

## Initially visible

Session position, source-pattern badge, prompt, representation, and the primary action for the active state.

## Initially hidden

Family name, method, first decision, formula, hint, expected answer, worked solution, validation result, and mastery calculation.

## Completion point

A session summary after its configured problem count. Full mastery is not awarded solely by completing this journey.
