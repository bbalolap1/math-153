# Handwritten Practice Screen-to-Backend Specification

“Proposed” identifies a service that does not yet exist. Owner approval here authorizes a relationship, not implementation.

| Screen / component | Learner sees | Why it exists | Data required | Backend service | Event | Transition | Failure state | Owner approval? |
|---|---|---|---|---|---|---|---|---|
| Setup / course mark | Math 153 + Handwritten Practice | Orientation | static product identity | none | none | none | none | yes: visual identity |
| Setup / review group | chapter/refresher choice | Scope session | curriculum index | proposed SessionService | SET_SCOPE | SESSION_SETUP | unavailable scope message | yes |
| Setup / family focus | mixed or selected families | Control transfer target | family index/status | proposed SessionService | SET_FAMILIES | SESSION_SETUP | unresolved sources disabled | yes |
| Setup / difficulty | L0–L7 distribution | Match readiness | family ladder | proposed SessionService | SET_DIFFICULTY | SESSION_SETUP | no valid templates | yes |
| Setup / session count | problem count | Bound workload | integer target | proposed SessionService | SET_COUNT | SESSION_SETUP | invalid count | yes |
| Setup / Start | primary button | Begin session | setup model | proposed SessionService.create | START_SESSION | PROBLEM_PRESENTATION | setup validation message | yes |
| All problem states / session rail | chapter, family scope, layer, position | Maintain context | Session, current index | proposed SessionService | none | none | fallback labels | yes |
| All problem states / progress dots | completed/current/remaining | Show bounded progress | Session progress | proposed SessionService | none | none | textual position | yes |
| Presentation / problem card | professor-style prompt | Central work object | `GeneratedProblem.prompt` | proposed ProblemService; current generator | BEGIN_PROBLEM | RECOGNITION | content unavailable | yes |
| Presentation / source-pattern badge | reviewed source pattern, not answer source | Establish provenance | construction/source status | proposed source index | none | none | pending-review label | yes |
| Presentation / Continue | primary action | Confirm prompt read | problem id | workflow controller | BEGIN_PROBLEM | RECOGNITION | remain in state | yes |
| Recognition / family choices | bounded classifications | Practice recognition | recognition options | current GeneratedProblem | SUBMIT_RECOGNITION | FIRST_DECISION | inline required message | yes: required/optional |
| Recognition / clue choices | visible construction clues | Connect surface to structure | authored clue set | proposed ProblemService | TOGGLE_CLUE | RECOGNITION | none | yes |
| Recognition / confidence | confidence scale | Calibrate recognition | 1–5 value | session attempt draft | SET_CONFIDENCE | RECOGNITION | default/required policy | yes |
| First Decision / action choices | candidate opening actions | Commit before solving | first-decision options | current GeneratedProblem | SUBMIT_FIRST_DECISION | PAPER_WORK | inline required message | yes |
| Paper / instruction card | solve by hand; answer hidden | Enforce product principle | workflow state | local workflow controller | none | none | none | yes |
| Paper / timer | optional elapsed time | Support time readiness | paper-start timestamp | workflow controller | none | none | unavailable timer | yes: visibility |
| Paper / Work completed | primary action | Open answer entry only after paper work | current state | workflow controller | CONFIRM_WORK_COMPLETE | ANSWER_ENTRY | remain in state | yes |
| Answer / form badge | exact/set/interval/etc. | Clarify requested presentation | validator declaration | validator registry | none | none | unsupported-form message | yes |
| Answer / math input | answer-appropriate control | Capture final result | answer schema | no call until submit | EDIT_ANSWER | ANSWER_ENTRY | parse guidance | yes |
| Answer / Submit | check answer | Begin evaluation | submission | ValidationService | SUBMIT_ANSWER | VALIDATING | retryable service error | yes |
| Validating / status | “Checking answer and required conditions” | Prevent duplicate action | pending submission | ValidationService | validation result | correct/incorrect feedback | safe error message | yes |
| Correct / result card | correct + satisfied checks | Confirm work | ValidationResult | ValidationService | none | none | generic confirmed state | yes |
| Correct / Continue | next problem | Advance session | Session progress | proposed SessionService | CONTINUE | PROBLEM_COMPLETE | retry navigation | yes |
| Incorrect / diagnosis card | probable error, no full solution | Locate failure | result + error patterns | proposed ErrorDiagnosisService | BEGIN_REMEDIATION | REMEDIATION | generic bounded cue | yes |
| Incorrect / reflection | learner uncertainty | Combine inferred/self report | error taxonomy | attempt draft/update policy | REPORT_UNCERTAINTY | INCORRECT_FEEDBACK | optional omission | yes: timing |
| Remediation / correction card | one clue/rule/partial line | Repair only failed stage | hint ladder + error | proposed RemediationService | REQUEST_LEVEL / RETRY | ANSWER_ENTRY or remain | escalation policy | yes |
| Summary / evidence rows | recognition, decision, procedure, checks, representation, independence, time | Show what transfers/breaks | Session attempts | mastery service (currently partial `progress`) | none | none | insufficient-evidence labels | yes |
| Summary / review plan | recommended families and modes | Direct next study action | error history/mastery | proposed recommendation service | SAVE_REVIEW_PLAN | SESSION_COMPLETE | manual suggestions | yes |
