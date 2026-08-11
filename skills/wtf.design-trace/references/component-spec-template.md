# Component Spec Template

Use this structure when no Figma frames are available. Fill in each section from the Gherkin scenarios and Feature ACs identified in the design-task skill.

---

## Component: `<ComponentName>`

### Purpose

One sentence: what does this component do for the domain actor?

### States

| State    | Trigger                | Description                          |
| -------- | ---------------------- | ------------------------------------ |
| Default  | Initial render         | Normal, data-populated view          |
| Loading  | While fetching         | Show skeleton or spinner             |
| Empty    | No data returned       | Empty state with call-to-action      |
| Error    | Fetch or action failed | Inline error message with retry      |
| Success  | Action completed       | Confirmation feedback                |
| Disabled | Precondition not met   | Controls visible but non-interactive |

Add additional rows for domain-specific states derived from the Gherkin scenarios.

### Elements Required

For each state above, list the UI elements needed:

- Labels, headings, body text (with copy)
- Input controls (type, validation rules)
- Buttons and actions (label, primary/secondary/destructive)
- Data display (fields shown, format)
- Icons or illustrations

### Interactions

| Trigger                  | Action      | Result                                                                   |
| ------------------------ | ----------- | ------------------------------------------------------------------------ |
| Button click             | Submit form | Transition to loading state                                              |
| Focus (keyboard/pointer) | Tooltip     | Show help text (visible on focus, not hover-only — required for WCAG AA) |
| Focus                    | Keyboard    | Visible focus ring, aria-label                                           |

### Responsive Behavior

- Mobile (< 768px): describe layout changes
- Tablet (768–1024px): describe layout changes
- Desktop (> 1024px): default layout

### Accessibility

- Keyboard navigation order
- Screen reader announcements for state changes
- ARIA roles and labels for non-semantic elements
- Minimum contrast ratios met: 4.5:1 for body text, 3:1 for large text and UI components

### Design Tokens to Apply

List specific tokens from the project design system:

- Color: `--color-<name>`
- Spacing: `--spacing-<name>`
- Typography: `--text-<name>`
- Radius: `--radius-<name>`

### Components Needed

| Component         | Status                    | Notes                   |
| ----------------- | ------------------------- | ----------------------- |
| `<ComponentName>` | Existing / New / Modified | Location or description |
