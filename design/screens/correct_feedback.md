# HP-07 — Correct Feedback

## Screen ID

`HP-07`

## Journey

Handwritten Practice

## Purpose

Confirm result and required checks.

## Source influence

Expected form/checks require reviewed solution. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/correct-feedback.html`

## Visible components

result; check status; next action. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

full solution unless approved.

## Backend dependencies

current ValidationResult and Attempt.

## Events

`CONTINUE`

## State transitions

`PROBLEM_COMPLETE`

## Error states

generic safe confirmation. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

reasoning depth; next action.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
