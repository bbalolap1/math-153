# Math 153 Design Language

**Status:** proposed; no owner-controlled visual choice is approved.  
**Source caveat:** course binaries are unavailable, so this language follows the product specification's worksheet-aware requirements, not an asserted copy of professor typography.

## 4.1 Visual principles

1. **Academic, not gamified:** restrained hierarchy; no coins, streak celebrations, or decorative dashboards.
2. **Paper-centered:** the prompt and blank mathematical space dominate; the interface supports work done elsewhere.
3. **One active stage:** controls unrelated to the current state are absent, not merely collapsed below.
4. **Representation fidelity:** tables, graphs, formulas, units, and part labels remain in their authored order.
5. **Bounded evidence:** progress is visible but secondary during solving.
6. **Source honesty:** verified, inferred, and unavailable provenance look distinct; author/debug metadata stays out of learner view.
7. **Accessible meaning:** never use color alone; labels and status text accompany visual states.

## 4.2 Layout principles

- Stable problem workspace with consistent prompt position across states.
- Clear regions for session context, problem, state-specific instruction, response, and action.
- Generous whitespace for mathematical reading and the psychological handoff to paper.
- Limited navigation during an active problem; exact model remains owner-controlled.
- Consistent answer workspace placement to reduce reorientation.
- Source comparison uses lecture / what changed / assessment columns on desktop and ordered stacked panels on narrow screens.
- Narrow screens preserve source order and primary action; no horizontal dependency for solving.

## 4.3 Typography tokens (proposed)

| Role | Proposed treatment | Purpose | Owner decision |
|---|---|---|---|
| Course title | sans, 20–24 px, semibold | stable product identity | exact typeface/weight |
| Screen heading | sans, 28–34 px, strong | active task | scale and density |
| Section/eyebrow | sans, 12–13 px, uppercase/letterspaced | state and source role | capitalization |
| Body/instructions | sans, 16–18 px, 1.5 line height | readable coaching | family/size |
| Math prompt | math rendering or serif fallback, 22–30 px | primary mathematical object | renderer/type scale |
| Question number/parts | tabular sans, bold | preserve construction | position/style |
| Hint/remediation | normal body with explicit “Clue/Rule” label | bounded support | visual emphasis |
| Feedback | text label + icon + restrained semantic color | correctness/diagnosis | placement and tone |
| Metadata/source | 12–13 px, muted but readable | provenance outside main prompt | learner visibility |

## 4.4 Component vocabulary

“Existing” names current functions/models. “Proposed” means backend work would require later approval.

| Component | Visual purpose | Learner purpose | Backend dependency | States | Owner-controlled decisions |
|---|---|---|---|---|---|
| CourseHeader | quiet identity/current mode | know course and workflow | static + Session view model (proposed) | all | branding, active navigation |
| SessionContext | chapter/family/layer/position | remain oriented | Session model/service (proposed) | active session | rail vs header, detail level |
| ProblemSheet | stable worksheet-like surface | read/source problem | `GeneratedProblem`; ProblemService proposed | problem states | dimensions, density, source styling |
| QuestionNumber | preserve assessment position | track multipart problem | construction/problem metadata proposed | problem states | display syntax |
| MathPrompt | render formulas/tables/graphs/context | understand exact givens | prompt/representation model proposed | problem states | size, media behavior |
| SourceBadge | mark reviewed pattern/source role | distinguish source-derived/generated | source index proposed | review/problem | learner visibility and wording |
| RecognitionPanel | classification/clue controls | practice structural recognition | current recognition fields; service proposed | RECOGNITION | mandatory layers, input type |
| FirstDecisionPanel | opening-action control | commit method before execution | current first-decision fields | FIRST_DECISION | select vs free response |
| PaperGate | instruction/timer/action | complete independent work | workflow controller proposed | PAPER_WORK | timer and bypass behavior |
| AnswerWorkspace | answer-form container | enter required presentation | validator schema proposed | ANSWER_ENTRY | layout, return-to-paper |
| MathAnswerField | math-aware entry | submit expression/value/set | current validator + adapter proposed | ANSWER_ENTRY | input technology |
| DomainField | restriction-specific entry | state/check domain | domain validator proposed | ANSWER_ENTRY/remediation | required placement |
| RangeField | range-specific entry | enter interval/set | range validator proposed | ANSWER_ENTRY | notation assistance |
| StepEntry | single-line transformation | show next handwritten line | StepEngine proposed | Next-Line | parsing and branches |
| ValidationResult | bounded result state | know correctness/checks | current `ValidationResult` | feedback | explanation depth |
| ErrorDiagnosis | classified likely failure | locate breakdown | DiagnosisService proposed | INCORRECT_FEEDBACK | learner override/timing |
| RemediationCard | one clue/rule/prerequisite | repair without full reveal | RemediationService proposed | REMEDIATION | escalation and solution access |
| ProgressRail | position without dashboard clutter | know session boundary | Session progress proposed | active session | dots/bar/text, navigation |
| SessionSummary | end-of-session evidence | plan next work | attempts + mastery/recommendation proposed | SESSION_COMPLETE | metrics and mastery language |
| SourceComparison | three-part lecture/change/assessment view | understand transfer | linked source segments proposed | SOURCE_COMPARISON | columns and annotation depth |
| AssessmentNavigator | question position/flag | manage strict assessment | assessment session proposed | Professor Mode | navigation/locking behavior |

## Component rule

Every production component must declare its data contract and event contract before implementation. Authoring/debug badges shown in wireframes are explanatory annotations; whether they appear to learners is an owner decision.
