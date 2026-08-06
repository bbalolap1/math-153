# Decision Log

## Level A — Codex implementation decisions

Codex may decide after a screen is approved:

- internal names, module boundaries, typed helper models, and test organization;
- safe exception mapping and database query details;
- HTML semantics and accessibility attributes that do not alter layout;
- deterministic test fixtures and fake prototype data.

| ID | Decision | Rationale | Status |
|---|---|---|---|
| A-001 | Keep wireframes static and backend-free. | Preserves the approval boundary. | decided |
| A-002 | Use explicit state names in design artifacts. | Makes transitions testable and reviewable. | decided |
| A-003 | Label proposed versus existing services. | Prevents design documents from claiming nonexistent backend capability. | decided |

## Level B — Codex proposes; owner chooses

Options and tradeoffs are in `unresolved-decisions.md`. They cover layout, navigation, timer, progress, feedback placement, and recognition-control count.

## Level C — owner-controlled

No decision below is approved by the presence of a wireframe:

- primary workflow and required recognition;
- what is visible before/after solving;
- hint and remediation escalation;
- Professor Mode behavior;
- dashboard and mastery presentation;
- navigation and visual feel;
- framework continuation or migration.
