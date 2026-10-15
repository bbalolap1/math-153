# Product Specification

## User need

The learner can often follow a lecture example but cannot recognize the same idea when the assessment changes the wording, combines prerequisite skills, introduces a table or graph, uses a real-world story, or asks for a different final form. The system must teach transfer without replacing the professor's question style.

## Core experience

For every topic, the learner moves through:

1. **Identify** — name the problem family and visible clues.
2. **Connect** — map the assessment form back to the lecture concept.
3. **Decide** — choose the first valid operation.
4. **Execute** — solve with structured checkpoints.
5. **Verify** — check domain, excluded values, signs, endpoints, or requested form.
6. **Compare** — see how a near-duplicate question changes one decision.
7. **Transfer** — solve professor-style and timed versions without scaffolding.

## Modes

### Learn mode
Shows the connection map, prerequisite chain, and guided checkpoints.

### Recognize mode
Shows a question and asks:
- What family is this?
- What clues identify it?
- What must be checked first?

### Practice mode
Adaptive mixed problems with optional hints.

### Professor mode
Preserves source-like wording and layout. Minimal scaffolding.

### Quiz/Test mode
Timed, fixed blueprint, no immediate feedback.

### Review mode
Groups errors by decision failure rather than only topic.

## Error taxonomy

- recognition_error
- representation_error
- first_step_error
- prerequisite_gap
- algebra_execution_error
- sign_error
- domain_error
- extraneous_solution_error
- endpoint_error
- formula_selection_error
- answer_format_error
- calculator_entry_error
- time_management_error

## Mastery

Mastery is tracked by family and layer. A learner does not master a family by repeating one surface form. Required evidence:

- correct recognition across at least three representations;
- correct first decision in professor mode;
- correct full solution on at least two variants;
- no critical restriction/check error;
- one timed success after a delay.

## Scope boundaries for Version 0.0

Included:
- source ingestion and registry;
- Markdown template parser;
- question-family browser;
- Chapter 5 vertical slice;
- attempts and error tagging;
- quiz assembly;
- basic adaptive recommendation.

Deferred:
- handwriting OCR;
- automatic extraction of every PDF/image;
- full React client;
- AI-generated explanations without a template;
- unrestricted symbolic question generation.
