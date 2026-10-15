# HP-09 — Remediation

## Screen ID

`HP-09`

## Journey

Handwritten Practice

## Purpose

Repair one specific prerequisite/decision.

## Source influence

Rule/checkpoint should link to reviewed lecture/family. No unverified PDF/image visual characteristic is treated as evidence.

## Wireframe

`../wireframes/remediation.html`

## Visible components

one clue/rule/input; retry/prerequisite action. Each requires the data/service contract in `../connections/ui_backend_map.md`.

## Hidden components

remaining steps and final answer.

## Backend dependencies

RemediationService proposed.

## Events

`RETRY/REQUEST_LEVEL`

## State transitions

`REMEDIATION or ANSWER_ENTRY`

## Error states

escalation exhausted. Raw backend exceptions must never be shown.

## Accessibility

Keyboard-operable controls; programmatic labels; logical focus after transition; text plus icon for status; responsive reading order; no color-only meaning; math/table/graph alternatives as applicable.

## Open decisions

hint ladder; retry limits; solution access.

## Approval status

`needs_owner_decision`

## Implementation status

`not_started`
