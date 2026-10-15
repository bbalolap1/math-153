# CR-01 — Chapter Group Selection

## Screen ID

`CR-01`

## Journey

Course Review

## Purpose

Choose Foundation, Chapters 1–2, Chapters 3–4, or Chapter 5.

## Source influence

Course organization comes from repository architecture, not PDF visuals. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/course-review.html`

## Visible components

CourseHeader; review group cards; source availability. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

concept details and solutions.

## Backend dependencies

curriculum index proposed.

## Events

`SELECT_CHAPTER`

## State transitions

`SECTION_OVERVIEW`

## Error states

missing/empty group. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

card vs list; defaults.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
