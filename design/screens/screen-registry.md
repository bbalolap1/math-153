# Screen Registry

Allowed approval statuses: `not_started`, `draft`, `needs_owner_decision`, `approved`, `implemented`, `implemented_with_difference`, `rejected`.

| screen_id | screen_name | journey | purpose | status | backend_dependencies | states | unresolved_decisions | approval_status | implementation_status |
|---|---|---|---|---|---|---|---|---|---|
| HP-01 | Session Setup | Handwritten Practice | Configure a bounded session | draft | proposed SessionService, family index | SESSION_SETUP | layout, weights, defaults, session length | needs_owner_decision | not implemented |
| HP-02 | Problem Presentation | Handwritten Practice | Read without premature method disclosure | draft | GeneratedProblem / future ProblemService | PROBLEM_PRESENTATION | two columns, source badge, continue action | needs_owner_decision | current app differs |
| HP-03 | Recognition | Handwritten Practice | Identify structure and clues | draft | GeneratedProblem recognition data | RECOGNITION | required/optional, choice count, confidence | needs_owner_decision | current app differs |
| HP-04 | First Decision | Handwritten Practice | Commit opening mathematical action | draft | GeneratedProblem first-decision data | FIRST_DECISION | select vs short answer, feedback timing | needs_owner_decision | current app differs |
| HP-05 | Paper Gate | Handwritten Practice | Require independent handwritten work | draft | local workflow state, timer | PAPER_WORK | timer visibility, secondary action | needs_owner_decision | current app differs |
| HP-06 | Answer Entry | Handwritten Practice | Enter required mathematical form | draft | validator registry, answer schema | ANSWER_ENTRY, VALIDATING | math input design, check requirements | needs_owner_decision | current app differs |
| HP-07 | Correct Feedback | Handwritten Practice | Confirm result without unnecessary solution reveal | draft | ValidationResult, AttemptRepository | CORRECT_FEEDBACK | explanation depth, next action | needs_owner_decision | current app differs |
| HP-08 | Incorrect Feedback | Handwritten Practice | Identify probable failure without full reveal | draft | ErrorDiagnosisService (proposed) | INCORRECT_FEEDBACK | learner self-report timing, feedback placement | needs_owner_decision | current app differs |
| HP-09 | Targeted Remediation | Handwritten Practice | Repair one failure point | draft | remediation rules / future service | REMEDIATION | escalation, retry limits, prerequisite route | needs_owner_decision | not implemented |
| HP-10 | Session Summary | Handwritten Practice | Review evidence and next steps | draft | Session, attempts, mastery service | SESSION_COMPLETE | visualization and mastery language | needs_owner_decision | not implemented |
| PM-01 | Professor Setup/Assessment | Professor Mode | Strict source-backed simulation | not started | assessment builder/scorer (not implemented) | multiple | all Professor Mode behavior | not_started | not implemented |
| NL-01 | Next-Line Workspace | Next-Line Coach | Validate one transformation at a time | not started | step graph engine (not implemented) | multiple | all step-coach behavior | not_started | not implemented |
