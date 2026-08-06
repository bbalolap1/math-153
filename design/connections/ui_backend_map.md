# UI / Backend Connection Map

Existing names are exact current functions/classes. **Proposed** means no backend support exists yet. Wireframe gray annotations are design-review aids, not approved learner-facing metadata.

| Screen | Component | Learner purpose | Data required | Backend service | Event | State transition | Stored result | Failure state |
|---|---|---|---|---|---|---|---|---|
| Session Setup | CourseHeader | Identify workflow | product/mode | renderer only | none | remains | none | static fallback |
| Session Setup | ReviewGroup | scope session | curriculum index | SessionService **proposed** | SET_SCOPE | SESSION_SETUP | draft setup | unavailable group disabled |
| Session Setup | FamilyFocus | choose target | reviewed family index | SessionService **proposed** | SET_FAMILIES | SESSION_SETUP | draft setup | unresolved family disabled |
| Session Setup | Difficulty | choose L0–L7 range | family ladders | SessionService **proposed** | SET_DIFFICULTY | SESSION_SETUP | draft setup | no eligible template |
| Session Setup | ProblemCount | bound workload | integer target | SessionService **proposed** | SET_COUNT | SESSION_SETUP | draft setup | inline validation |
| Session Setup | StartSession | begin | setup model | SessionService.create **proposed** | START_SESSION | PROBLEM_PRESENTATION | Session | safe setup error |
| Course Review | ChapterGroups | choose refresher | curriculum index | CurriculumService **proposed** | SELECT_CHAPTER | SECTION_OVERVIEW | optional preference | missing index message |
| Course Review | SectionList | choose section/concept | families/source links | content-index adapter **proposed** | SELECT_SECTION | CONCEPT_VIEW | view event | pending source status |
| Source Comparison | LectureCard | see simple source form | linked lecture segment | SourceService **proposed** | none | remains | none | source unavailable |
| Source Comparison | ChangeColumn | identify added representation/prerequisite/decision | authored comparison | ConstructionService **proposed** | none | remains | viewed comparison | unreviewed label |
| Source Comparison | AssessmentCard | see activity/quiz/test form | assessment segment | SourceService **proposed** | none | remains | none | source unavailable |
| Source Comparison | TryBridge | move from comparison to action | family/construction | SessionService **proposed** | TRY_BRIDGE | GUIDED_EXAMPLE | bridge session | no reviewed template |
| Problem states | SessionContext | remain oriented | Session/current index | SessionService **proposed** | none | remains | none | textual fallback |
| Problem states | ProgressRail | see bounded progress | completed/current/remaining | SessionService **proposed** | none | remains | none | `n of total` fallback |
| Problem Presentation | ProblemSheet | read exact problem | current `GeneratedProblem` | current `generate_problem()`; ProblemService proposed | BEGIN_PROBLEM | RECOGNITION | exposure time proposed | content unavailable |
| Problem Presentation | SourceBadge | understand provenance | source/construction status | SourceService **proposed** | none | remains | none | pending-review text |
| Recognition | RecognitionPanel | classify structure/clues | current recognition options; authored clues proposed | current comparison inside `submit_attempt()`; RecognitionService proposed | SUBMIT_RECOGNITION | FIRST_DECISION | recognition/confidence draft | required message |
| First Decision | FirstDecisionPanel | commit opening action | current first-decision options | current comparison inside `submit_attempt()` | SUBMIT_FIRST_DECISION | PAPER_WORK | decision draft | required message |
| Paper Work | PaperGate | solve independently | active workflow/problem | controller **proposed** | WORK_COMPLETE | ANSWER_ENTRY | paper duration proposed | remain in state |
| Answer Entry | AnswerWorkspace | enter required form | validator declaration/schema | validator adapter **proposed** | EDIT_ANSWER | remains | submission draft | format guidance |
| Answer Entry | MathAnswerField | submit result | answer string | current `validate_answer()` through `submit_attempt()` | SUBMIT_ANSWER | VALIDATING | current `Attempt` | parse/safe service error |
| Correct Feedback | ValidationResult | confirm answer/checks | current `ValidationResult` | current `validate_answer()` | CONTINUE | PROBLEM_COMPLETE | current `Attempt` | generic confirmation |
| Incorrect Feedback | ErrorDiagnosis | locate likely failure | result/error patterns | current coarse tags in `submit_attempt()`; DiagnosisService proposed | REPAIR | REMEDIATION | error category | bounded generic cue |
| Remediation | RemediationCard | repair one point | hint ladder/error | RemediationService **proposed** | RETRY/REQUEST_LEVEL | REMEDIATION or ANSWER_ENTRY | hint/retry evidence | escalation limit |
| Related Problem | VariationCard | transfer changed surface | reviewed construction/seed | current `generate_problem()` is insufficient; generator service proposed | SUBMIT_VARIATION | PROBLEM_COMPLETE | transfer Attempt | no reviewed variation |
| Professor Mode | AssessmentNavigator | manage strict questions | assessment session | AssessmentService **proposed** | FLAG/NEXT | QUESTION_ACTIVE/NEXT_QUESTION | flag/position | autosave message |
| Professor Mode | CapturedAnswer | store without feedback | response schema | AssessmentRepository **proposed** | LOCK_ANSWER | QUESTION_LOCKED | response | capture error |
| Session Summary | EvidenceGrid | see multidimensional evidence | session attempts | current `progress()` partial; MasteryService proposed | none | remains | none | insufficient-evidence label |
| Session Summary | ReviewPlan | plan remediation/delay | errors/mastery/source coverage | RecommendationService **proposed** | SAVE_REVIEW_PLAN | SESSION_COMPLETE | ReviewQueue items | manual fallback |
