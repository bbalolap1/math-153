# PM-02 — Assessment Report

## Screen ID

`PM-02`

## Journey

Professor Mode

## Purpose

Review score by family, skill, error, and remediation.

## Source influence

Scoring requirements depend on source assessment/solutions. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

Not produced in the current bounded wireframe set.

## Visible components

score; breakdowns; review list; sequence. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

active assessment controls.

## Backend dependencies

AssessmentScorer/RecommendationService proposed.

## Events

`OPEN_REVIEW/SAVE_PLAN`

## State transitions

`REPORT`

## Error states

incomplete scoring. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

report hierarchy; solution timing.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
