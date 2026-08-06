# Question Construction Catalog

## Status

No professor construction can be cataloged from filenames alone. The records below separate what is currently available from the fields required after source review. Existing runtime problems are model-inferred scaffolds and are not professor templates.

## Construction record schema

| Field | Requirement |
|---|---|
| Construction ID | Stable ID independent of display title |
| Source references | Question page/number plus solution and lecture references |
| Visible wording | Faithful transcription with uncertainty notes |
| Information order | Sequence in which givens/instructions/parts appear |
| Representation | equation, table, graph, ordered pairs, context, multipart, etc. |
| Number of parts | Explicit and dependent subparts |
| Required inference | What the prompt does not state directly |
| Required prerequisites | Earlier skills necessary to proceed |
| First decision | Opening mathematical action |
| Reasoning stages | Expected checkpoints, including alternatives |
| Answer form | exact, decimal, set, interval, formula, table, graph feature, explanation |
| Trap structure | Source-supported likely failure |
| Difficulty | L0–L7 rationale, not number size alone |
| Allowed variation | Reviewed structural/parameter bounds |
| Disallowed variation | Changes that destroy fidelity or answer requirements |

## Source review queue

| Catalog group | Candidate filenames | Required comparison | Current status |
|---|---|---|---|
| Section-to-activity bridge | `1.1.pdf`–`1.4.pdf`, `Activity_1-1.pdf`–`Activity_4.pdf` | lecture form → activity form | blocked: binaries absent |
| Completing the square | `2.x` section candidates, `Completing_the_Square.pdf`, assessment items | direct method → mixed prerequisite/assessment | blocked |
| Quiz progression | Quiz 1–6 plus named solutions | question wording, parts, traps, expected form | blocked |
| Test transfer | Test 1, solution, reviews, Test 2 review | quiz family → test construction | blocked |
| Final transfer | Versions 1–3 with/without solutions | cross-version invariants and controlled variation | blocked |
| Screenshot exercises | chronological screenshot inventory | representation/diversity clusters | blocked |

## Table and fill-in analysis checklist

When the visual sources are available, each table item must record what the learner must infer before calculation: independent/dependent variable, rule direction, missing-cell dependency, constant rate or ratio, function/composition order, domain restrictions, graph scale, units, and requested answer form. Table structure itself is part of the construction and must not be flattened into generic text.

## Exercise-diversity matrix

For every verified family, compare at least three constructions across these dimensions: representation, numeric structure, prerequisite, wording/information order, subparts, answer form, validity/extraneous behavior, context, guidance density, and time demand. A generated variation must change at least two meaningful reviewed dimensions while preserving hidden method and answer-validation behavior.

## Existing model-inferred scaffolds (not source constructions)

| Runtime family | Current representation | Known limitation |
|---|---|---|
| Linear equations | direct equation | generic; no assessment evidence |
| Function composition | direct formulas/value | not a word problem, table, or source construction |
| Exponential equations | equal-base equation | number-swapped direct template |
| Logarithmic equations | equal logs/domain instruction | not verified against course assessment |
