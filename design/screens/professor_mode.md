# PM-01 — Professor Mode

## Screen ID

`PM-01`

## Journey

Professor Mode

## Purpose

Complete strict assessment without premature feedback.

## Source influence

Must reproduce reviewed assessment construction/density. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/professor-mode.html`

## Visible components

assessment context; problem; capture; navigation/flag. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

topic; hints; correctness; score.

## Backend dependencies

AssessmentService/Repository proposed.

## Events

`LOCK_ANSWER/NEXT`

## State transitions

`QUESTION_LOCKED/NEXT_QUESTION`

## Error states

autosave/capture error. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

all strict-mode behavior.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
