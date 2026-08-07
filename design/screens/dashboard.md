# DS-01 — Dashboard

## Screen ID

`DS-01`

## Journey

Global

## Purpose

Orient and choose a journey.

## Source influence

No verified source influence; product navigation only. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

Not produced in the current bounded wireframe set.

## Visible components

CourseHeader; journey cards; urgent assessment context. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

active problem controls; mastery claims.

## Backend dependencies

attempt summaries; curriculum/source coverage adapters proposed.

## Events

`SELECT_JOURNEY`

## State transitions

`selected journey setup`

## Error states

unavailable journey; empty evidence. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

dashboard structure; urgency display.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
