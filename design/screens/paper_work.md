# HP-05 — Paper Work

## Screen ID

`HP-05`

## Journey

Handwritten Practice

## Purpose

Leave screen and solve independently.

## Source influence

Worksheet whitespace is a product hypothesis pending source visuals. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/paper-work.html`

## Visible components

problem; paper instruction; optional timer; work complete. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

answer; hints; validation; solution.

## Backend dependencies

workflow controller proposed.

## Events

`WORK_COMPLETE`

## State transitions

`ANSWER_ENTRY`

## Error states

timer/save failure. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

timer; bypass; navigation.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
