# Math 153 Learning System Specification

This document is the permanent architecture and additive requirements contract for the Math 153
learning system. Change requests must name the affected layer. A change in one layer must not
silently weaken or replace requirements in another layer.

## 1. Source Layer

- `sources/**/*.md` is the canonical course corpus.
- Preserve source bodies exactly. Generated and derived data must remain outside `sources/`.
- Evidence priority is original assessment, official solution, lecture, review, then clearly
  marked inference.
- Retain source paths, hashes, extraction status, and conflicts. Missing legacy binaries do not
  invalidate canonical Markdown.

## 2. Knowledge Layer

Read every source body and extract topics, formulas, questions, solutions, professor wording,
required answer forms, prerequisites, application contexts, methods, restrictions, and recurring
errors. Knowledge claims must retain `source_refs`. Source type is complexity evidence: lectures
primarily support L0–L2, activities L2–L4, quizzes L4–L5, tests L4–L6, and practice finals L5–L7.

## 3. Question-Family Layer

Families represent distinct mathematical decision paths, not broad vocabulary matches. Each
family defines recognition clues, structure, prerequisites, first decision, decision path,
professor traps, answer presentation, error categories, variation boundaries, at least five
progression levels, source examples, generation rules, validators, feedback, mastery, tests, and a
UI path.

Application is an independent dimension, not a synonym for difficulty. Detect only
source-supported applications, including geometry, distance/rate/time, work/rate,
mixture/concentration, finance, growth/decay, population, radioactive decay, projectile or
quadratic models, and other contexts actually present in the corpus.

## 4. Generator Layer

A generated question combines:

`family + complexity + representation + application_context + structural_variant + seed`.

Every question exposes `family_id`, `source_refs`, `difficulty_layer`, `variant_reason`, seed,
structural signature, decision count, prerequisite count, estimated solution steps,
representation, and required checks. Templates control construction; SymPy validates only.

### 4.1 Structural complexity ladder

- **L0 Foundation:** one prerequisite skill.
- **L1 Direct:** one concept with an explicitly signaled method.
- **L2 Guided:** main concept plus one supporting operation.
- **L3 Representation:** same structure through a table, graph, alternate notation, or context.
- **L4 Mixed prerequisite:** at least two skills or decisions before the main method.
- **L5 Professor style:** source-observed assessment wording, parts, answer form, and checks.
- **L6 Timed/exam:** professor construction with reduced signaling; recognize family, method,
  checks, and answer format.
- **L7 Cumulative transfer:** multiple concepts, method selection, and interpretation without
  announcing the family.

Larger or uglier numbers alone never justify a higher level.

### 4.2 Complexity profiles

Profiles distribute questions across levels; they do not change question count:

- Foundation: L0 20%, L1 35%, L2 30%, L3 15%.
- Direct Practice: L0–L2, emphasizing L1.
- Mixed Practice: L1–L5, emphasizing L2–L4.
- Professor Style: L3–L6, emphasizing L5.
- Test Review: L2 10%, L3 15%, L4 25%, L5 30%, L6 15%, L7 5%.
- Final Exam Challenge: L2 5%, L3 10%, L4 20%, L5 30%, L6 20%, L7 15%.

### 4.3 Session constraints

- Question count is independently selectable from 1 through 50.
- Mixed sessions rotate eligible families, source surfaces, structural signatures, and levels.
- No exact duplicates. No exact structural template exceeds 10% of a 50-question mixed set.
- Avoid consecutive identical `family + structure + level` combinations.
- Report insufficient source-supported variation rather than inventing unrelated questions.

## 5. Solver and Validator Layer

- Validate mathematical construction, expected answer, required form, restrictions, and all
  generated variants.
- Teaching solutions use Recognize, Decide, Execute, Verify, Present.
- Each execution step records title, before expression, operation, why it is allowed, and after
  expression. L4–L7 solutions scale their step count with reasoning depth.
- Never hide expansions, distribution, sign changes, common denominators, factoring,
  cancellation, domain restrictions, or extraneous-root checks.

## 6. Streamlit UI Layer

- Render student mathematics visually, not primarily as raw LaTeX or programming syntax.
- Multiple-choice presentation is vertically ordered A, B, C, D with stable label association.
- Provide a visible **Difficulty / Complexity** control independent of question count.
- Optionally display level, required skills, estimated steps, application context, and why the
  problem is harder.
- Preserve session state and show `Question n of total`.
- Do not render all solutions at once. Quiz/Test Review defaults to teaching solutions, with a
  learner-selected shorter view available.
- Source Inspector shows original Markdown, extracted records, family use, and generated variants.

## 7. Validation and Change Control

- Parser, generator, validator, scoring, complexity, signature, session-distribution, solution,
  and rendering rules require automated tests.
- Derived reports are reproducible; Markdown remains canonical authoring.
- New requirements are additive unless an approved change explicitly supersedes a named clause.
- Future changes should state affected and unaffected layers before implementation.
