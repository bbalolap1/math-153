# HP-02 — Problem Presentation

## Screen ID

`HP-02`

## Journey

Handwritten Practice

## Purpose

Read a professor-style problem without method leakage.

## Source influence

Must later preserve reviewed source construction. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/problem-presentation.html`

## Visible components

session context; progress; problem; source badge; begin. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

topic; method; answer; hints; solution.

## Backend dependencies

current GeneratedProblem; ProblemService proposed.

## Events

`BEGIN_PROBLEM`

## State transitions

`RECOGNITION`

## Error states

content/media unavailable. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

layout; badge; recognition requirement.

## Approval status

`needs_owner_decision`

## Implementation status

`implemented_with_difference`
