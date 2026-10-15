# HP-06 — Answer Entry

## Screen ID

`HP-06`

## Journey

Handwritten Practice

## Purpose

Enter the requested mathematical form.

## Source influence

Answer form must follow source prompt/solution. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/answer-entry.html`

## Visible components

problem; answer-type badge; form-specific field; submit. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

expected answer; diagnosis; solution.

## Backend dependencies

validator schema adapter proposed; current validate_answer.

## Events

`SUBMIT_ANSWER`

## State transitions

`VALIDATING`

## Error states

parse/unsupported validator/service error. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

input technology; checks; return to paper.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
