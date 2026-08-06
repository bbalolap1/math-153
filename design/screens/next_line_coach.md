# NL-01 — Next Line Coach

## Screen ID

`NL-01`

## Journey

Next-Line Coach

## Purpose

Validate one handwritten transformation at a time.

## Source influence

Requires reviewed branch-aware solution paths. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

Not produced in the current bounded wireframe set.

## Visible components

problem; current state; step field; line feedback. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

future steps/terminal answer.

## Backend dependencies

StepEngine/StepGraph proposed.

## Events

`SUBMIT_STEP`

## State transitions

`STEP_VALIDATING then branch`

## Error states

unparsed/valid alternative missing. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

syntax; branches; escalation.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
