# HP-04 — First Decision

## Screen ID

`HP-04`

## Journey

Handwritten Practice

## Purpose

Commit the first mathematical action.

## Source influence

Decision derived from family construction. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/first-decision.html`

## Visible components

problem; candidate actions; submit. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

correctness; answer; hints.

## Backend dependencies

current first-decision fields.

## Events

`SUBMIT_FIRST_DECISION`

## State transitions

`PAPER_WORK`

## Error states

required input. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

select vs short answer; feedback timing.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
