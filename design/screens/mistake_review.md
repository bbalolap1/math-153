# MR-01 — Mistake Review

## Screen ID

`MR-01`

## Journey

Mistake Repair

## Purpose

Choose error cluster and repair sequence.

## Source influence

Feedback should link to reviewed source/family checkpoints. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

Not produced in the current bounded wireframe set.

## Visible components

error clusters; affected families; repair action. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

unrelated dashboard data.

## Backend dependencies

attempt query; Diagnosis/ReviewQueue proposed.

## Events

`START_REPAIR`

## State transitions

`REPAIR_OVERVIEW`

## Error states

insufficient evidence. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

clustering; learner override; terminology.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
