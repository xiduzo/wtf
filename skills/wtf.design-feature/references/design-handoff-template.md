# Design Handoff Template

Section structure that `wtf.design-feature` writes back into the Feature issue. Each Feature gets exactly one Design Handoff section; running `wtf.design-feature` again replaces it (per the present-label overwrite gate in `../../references/lifecycle-labels.md`).

```markdown
## Design Handoff

- Figma: <top-level Figma file URL, generated file URL, or "pending (scaffold only)">
- Flow: <link to prototype/flow if available>
- Design path: <Path A: human-provided | Path B: AI-generated | Path C: scaffold brief>

### Screen inventory

| Screen | Story | Figma frame | States covered | Source |
|--------|-------|-------------|----------------|--------|
| <screen name> | As a... | <url or pending> | default / loading / error / empty | provided / generated / scaffolded |

### Validation (Path A/B only)

- [ ] Every user story has ≥1 frame
- [ ] Every edge case has a boundary/error state frame
- [ ] Every Domain Event surface is represented
- [ ] All frames consistent with DESIGN.md tokens and patterns

### Shared components

| Component | Exists? | Path or new | Used on |
|-----------|---------|-------------|---------|
| <name> | yes/no | <path or "new"> | <screens> |

### Accessibility notes

<any feature-level a11y constraints from steering doc or Epic>

### Open gaps

<list any screens or states not yet designed — pending Figma frames>
```

## Field rules

- **Design path** must match the path actually run in step 6 — do not over-claim Path B if frames were scaffolded.
- **Screen inventory** must list every screen identified in the journey map (step 5), even ones marked `pending`.
- **Validation** checkboxes are filled by the skill, not the user.
- **Shared components** is the inheritance contract for `wtf.design-task` — entries here are the per-feature reuse decisions that downstream Tasks must respect.
