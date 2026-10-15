# CR-03 — Source Comparison

## Screen ID

`CR-03`

## Journey

Course Review

## Purpose

Compare lecture, what changed, and assessment construction.

## Source influence

Requires linked source segments; current examples are fixtures. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/source-comparison.html`

## Visible components

lecture card; change column; assessment card; bridge action. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

official answer and full solution.

## Backend dependencies

SourceService and ConstructionService proposed.

## Events

`TRY_BRIDGE`

## State transitions

`GUIDED_EXAMPLE`

## Error states

source unavailable. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

columns vs steps; source image visibility.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
