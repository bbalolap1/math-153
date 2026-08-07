# Handwritten Practice Screen Details

These descriptions accompany the static wireframes. All statuses are `draft`; all visual and behavioral choices require owner approval.

| Screen | Learner purpose | Displayed components | Backend connections | Possible state | Unresolved decisions | Implementation relationship |
|---|---|---|---|---|---|---|
| HP-01 Session Setup | Bound the work before beginning | identity, scope, family focus, difficulty, count, Start | curriculum/family indexes; proposed SessionService | SESSION_SETUP | setup density, defaults, weighting | No equivalent production setup screen. |
| HP-02 Problem Presentation | Read without method leakage | session rail, progress, source-pattern badge, problem card, Begin | Session; proposed ProblemService / current GeneratedProblem | PROBLEM_PRESENTATION | layout, active navigation, source badge | Current app immediately shows recognition controls. |
| HP-03 Recognition | Connect visible clues to family | persistent prompt, classification, clue selection, confidence, Lock | recognition fields in problem/attempt | RECOGNITION | required layers, choice count, confidence | Current app has family choices and confidence but no clue selection. |
| HP-04 First Decision | Commit the opening action | prompt, action choices, Lock | first-decision fields | FIRST_DECISION | select vs short entry, feedback timing | Current app is similar but layout is unapproved. |
| HP-05 Paper Gate | Complete independent work | prompt, paper instruction, timer, Work completed, Save | workflow state/timestamp | PAPER_WORK | timer, navigation, exit behavior | Current app has instruction and non-ticking elapsed display. |
| HP-06 Answer Entry | Submit required answer form | prompt, answer-type badge, typed input, critical-check confirmation, Submit | validator registry; AnswerSubmission | ANSWER_ENTRY / VALIDATING | math input, check boxes, return-to-paper | Current app uses one generic text input. |
| HP-07 Correct Feedback | Confirm correctness/checks | prompt, result, evidence, Continue | ValidationResult; Attempt | CORRECT_FEEDBACK | reasoning depth, full-solution access | Current app mixes feedback with cumulative metrics. |
| HP-08 Incorrect Feedback | Identify failure without answer reveal | prompt, diagnosis, uncertainty reflection, remediation action | proposed ErrorDiagnosisService; Attempt | INCORRECT_FEEDBACK | reflection timing, placement, learner override | Current app uses a generic inferred category. |
| HP-09 Targeted Remediation | Repair one point | prompt, one bounded clue, small input, retry/prerequisite action | proposed RemediationService | REMEDIATION | escalation ladder, retry limits | No separate production state exists. |
| HP-10 Session Summary | Understand evidence and next work | dimension metrics, repair sequence, Save/Exit | session attempts; mastery/recommendation services | SESSION_COMPLETE | mastery visualization, recommendation authority | No production session aggregate or summary exists. |
