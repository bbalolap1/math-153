# Screen Registry

Statuses: `not_started`, `draft`, `needs_owner_decision`, `approved`, `implemented`, `implemented_with_difference`, `rejected`. No screen is approved.

| screen_id | screen_name | journey | purpose | status | backend_dependencies | states | unresolved_decisions | approval_status | implementation_status |
|---|---|---|---|---|---|---|---|---|---|
| DS-01 | Dashboard | Global | Choose a journey and see urgent context | draft | curriculum/attempt summaries proposed | entry | hierarchy, cards, urgency | needs_owner_decision | not_started |
| CR-01 | Chapter Group Selection | Course Review | Choose requested refresher group | draft | curriculum index proposed | CHAPTER_SELECTION | card/list/default | needs_owner_decision | implemented_with_difference |
| CR-02 | Section Overview | Course Review | Choose section/concept and see coverage | draft | content/source index proposed | SECTION_OVERVIEW, CONCEPT_VIEW | density/status | needs_owner_decision | not_started |
| CR-03 | Source Comparison | Course Review | Compare lecture/change/assessment | draft/source-blocked | Source/Construction services proposed | SOURCE_COMPARISON | layout/source visibility | needs_owner_decision | not_started |
| HP-01 | Session Setup | Handwritten Practice | Configure bounded session | draft | SessionService proposed | SESSION_SETUP | defaults/weights/density | needs_owner_decision | not_started |
| HP-02 | Problem Presentation | Handwritten Practice | Read without method leakage | draft | GeneratedProblem; ProblemService proposed | PROBLEM_PRESENTATION | layout/navigation/badge | needs_owner_decision | implemented_with_difference |
| HP-03 | Recognition | Handwritten Practice | Identify family/clues/form | draft | current recognition fields; service proposed | RECOGNITION | required layers/choices/confidence | needs_owner_decision | implemented_with_difference |
| HP-04 | First Decision | Handwritten Practice | Commit opening action | draft | current first-decision fields | FIRST_DECISION | choice vs entry/feedback | needs_owner_decision | implemented_with_difference |
| HP-05 | Paper Work | Handwritten Practice | Solve independently | draft | controller/timer proposed | PAPER_WORK | timer/bypass/navigation | needs_owner_decision | implemented_with_difference |
| HP-06 | Answer Entry | Handwritten Practice | Enter required answer form | draft | validator schema/adapter proposed | ANSWER_ENTRY, VALIDATING | input/checks | needs_owner_decision | implemented_with_difference |
| HP-07 | Correct Feedback | Handwritten Practice | Confirm answer/checks | draft | ValidationResult, Attempt | CORRECT_FEEDBACK | depth/next action | needs_owner_decision | implemented_with_difference |
| HP-08 | Incorrect Feedback | Handwritten Practice | Locate failure without reveal | draft | current tags; DiagnosisService proposed | INCORRECT_FEEDBACK | placement/reflection | needs_owner_decision | implemented_with_difference |
| HP-09 | Remediation | Handwritten Practice | Repair one failure | draft | RemediationService proposed | REMEDIATION | ladder/retries/solution | needs_owner_decision | not_started |
| HP-10 | Session Summary | Handwritten Practice | Review evidence/next work | draft | session/mastery/recommendation proposed | SESSION_COMPLETE | visualization/authority | needs_owner_decision | not_started |
| NL-01 | Next-Line Coach | Next-Line Coach | Validate one transformation | not_started | StepEngine/StepGraph proposed | step states | syntax/branches/hints | needs_owner_decision | not_started |
| PM-01 | Professor Mode | Professor Mode | Strict assessment | draft/source-blocked | assessment services proposed | assessment states | all behavior | needs_owner_decision | not_started |
| PM-02 | Assessment Report | Professor Mode | Report family/skill/error evidence | not_started | scorer/recommendation proposed | REPORT | hierarchy/solution timing | needs_owner_decision | not_started |
| MR-01 | Mistake Review | Mistake Repair | Select and repair error cluster | not_started | diagnosis/review queue proposed | repair states | clustering/override | needs_owner_decision | not_started |
