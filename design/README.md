# Math 153 Design Studio

This directory is the approval boundary between the product specification and production implementation.

```text
source analysis → user journey → wireframe → backend connection map
→ owner approval → prototype → owner approval → production implementation
```

Nothing in `design/wireframes/` is a production Streamlit page. The files use static sample data, make no backend calls, and exist only for visual review.

The course PDF/image binaries are not present in this repository. Source-analysis files therefore distinguish verified filename evidence from blocked visual analysis. Fixture mathematics in wireframes and prototypes is not presented as a professor transcription.

## Areas

- `source_analysis/`: evidence status, visual-review protocol, and construction catalog.
- `design_system/`: proposed Math 153 principles, typography, and component contracts.
- `journeys/`: six separate learner journeys with states, events, storage, and exits.
- `screens/`: one specification for every required screen.
- `wireframes/`: clickable static screen gallery.
- `prototypes/`: isolated fake-data interaction; never imports production code.
- `connections/`: state machines and visible-component/backend map.
- `decisions/`: Codex-controlled, proposed, and owner-controlled choices.
- `approvals/`: explicit screen status; nothing is implicitly approved.

## Approval gates

1. **Workflow:** approve actions, visible information, and hidden information.
2. **Wireframe:** approve one screen's layout and hierarchy.
3. **Visual mockup:** approve spacing, typography, navigation, and feedback states.
4. **Connection map:** approve each component-to-service relationship.
5. **Functional prototype:** implement one approved journey with one family.
6. **Expansion:** add families or modes only after the first workflow is approved.

## Review order

1. `../docs/current_repository_audit.md`
2. `source_analysis/course_source_visual_language.md`
3. `journeys/02_handwritten_practice.md`
4. `screens/screen-registry.md`
5. Open `wireframes/index.html`, then `prototypes/handwritten-practice.html`.
6. `connections/ui_backend_map.md` and `connections/state_machines.md`
7. `decisions/open_decisions.md`
8. Record explicit approval in `approvals/screen_status.md`.
