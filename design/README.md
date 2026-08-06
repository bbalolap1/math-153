# Math 153 Design Studio

This directory is the approval boundary between the product specification and production implementation.

```text
learning requirement → journey → wireframe → backend connection map
→ owner approval → prototype → owner approval → production
```

Nothing in `design/wireframes/` is a production Streamlit page. The files use static sample data, make no backend calls, and exist only for visual review.

## Approval gates

1. **Workflow:** approve actions, visible information, and hidden information.
2. **Wireframe:** approve one screen's layout and hierarchy.
3. **Visual mockup:** approve spacing, typography, navigation, and feedback states.
4. **Connection map:** approve each component-to-service relationship.
5. **Functional prototype:** implement one approved journey with one family.
6. **Expansion:** add families or modes only after the first workflow is approved.

## Review order

1. `audit/current-ui-backend-map.md`
2. `journeys/handwritten-practice.md`
3. `screens/screen-registry.md`
4. Open `wireframes/index.html`
5. `connections/ui-backend-map.md` and `connections/event-flow.md`
6. `decisions/unresolved-decisions.md`
7. Record approval in `approvals/screen-status.md`
