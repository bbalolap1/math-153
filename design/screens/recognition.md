# HP-03 — Recognition

## Screen ID

`HP-03`

## Journey

Handwritten Practice

## Purpose

Identify family, clues, and answer form.

## Source influence

Recognition clues must be source/family authored. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/recognition.html`

## Visible components

problem; classification/clues; confidence; submit. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

correct classification; method; answer.

## Backend dependencies

current recognition fields; service proposed.

## Events

`SUBMIT_RECOGNITION`

## State transitions

`FIRST_DECISION`

## Error states

required input/unsupported clue. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

mandatory layers; choice count; confidence.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
