# HP-08 — Incorrect Feedback

## Screen ID

`HP-08`

## Journey

Handwritten Practice

## Purpose

Locate probable failure without answer reveal.

## Source influence

Error patterns require authored family/source evidence. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/incorrect-feedback.html`

## Visible components

bounded diagnosis; reflection; repair action. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

expected answer; full solution.

## Backend dependencies

current coarse tags; DiagnosisService proposed.

## Events

`REPAIR`

## State transitions

`REMEDIATION`

## Error states

generic cue. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

placement; reflection timing; override.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
