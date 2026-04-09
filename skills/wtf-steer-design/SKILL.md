---
name: wtf.steer-design
description: This skill should be used when a team wants to create or refine the design guidelines document — for example "create the design steering doc", "document our design system", "write the design principles", "document our component patterns", "set up the design guidelines", or "update the design doc". Generates docs/steering/DESIGN.md as a living document capturing design principles, the design system, tokens, component patterns, and accessibility standards. Generated once and refined — not regenerated from scratch.
---

# Steer Design

Generate or refine `docs/steering/DESIGN.md` — the design guidelines document. This document is the canonical reference for design decisions, the system in use, tokens, patterns, and accessibility requirements that every designer and implementer must follow.

See `references/design-template.md` for the expected document shape.

## Process

### 1. Check if the document already exists

```bash
cat docs/steering/DESIGN.md 2>/dev/null
```

If the file **exists**, call `AskUserQuestion` with:

- `question`: "docs/steering/DESIGN.md already exists. What would you like to do?"
- `header`: "Design doc found"
- `options`: `[{label: "Refine it", description: "Review and improve the existing document"}, {label: "Exit", description: "Leave it as-is"}]`

- **Refine it** → read the current document, then skip to step 4 (use existing doc as context, only ask about gaps or outdated sections).
- **Exit** → exit immediately.

If the file **does not exist**, continue to step 2.

### 2. Research the codebase and design artifacts

Use the Agent tool to extract design facts directly from the codebase. Do not ask the user for things that can be read:

- **Design system:** look for a Storybook config, component library imports, design-system packages in `package.json`
- **Tokens:** CSS custom properties (`--color-*`, `--spacing-*`), Tailwind config, theme files, token definition files
- **Components:** existing UI components and their structure (look for `components/`, `ui/`, `src/components/`)
- **Figma links:** any Figma URLs in README, existing issues, or `docs/`
- **Accessibility:** existing WCAG references, axe configs, jest-axe usage
- **Responsive breakpoints:** Tailwind config, CSS media queries, layout files
- **VISION.md** if it exists — extract any design principles already stated there

Also check `docs/steering/VISION.md` for any existing principles that should carry over.

Synthesise findings. Produce a draft of Stack, Tokens, and Component Patterns from this research alone where possible.

### 3. Interview the user for gaps only

Only ask about what research could not determine. Work through questions **one at a time** using `AskUserQuestion`.

**Topics that may need input:**

1. **Design principles** — "What 3–5 principles guide every design decision for this product?"
   - Pre-fill with principles inferred from VISION.md or any existing design docs.
2. **Design system** — "What design system are you using? Do you have a Figma library?"
   - Pre-fill with anything found in the codebase or imports.
3. **Token gaps** — "Are there tokens not yet defined in code that designers rely on?"
   - Pre-fill with gaps inferred from the design system research.
4. **Responsive strategy** — "How does the layout adapt across breakpoints?"
   - Pre-fill with breakpoints found in the codebase.
5. **Accessibility target** — "Are there any accessibility requirements beyond WCAG 2.1 AA?"
   - Pre-fill with any existing a11y config found.

Skip any topic already answered by research.

### 4. Draft the document

Using `references/design-template.md` as the shape reference, fill in all sections with gathered context. Replace every `[PLACEHOLDER]` with real content.

**Writing rules:**

- Tokens must reflect what is actually defined in the codebase — not aspirational values
- Component patterns reference real component paths where they exist
- Accessibility section always includes the baseline rules from the project's CLAUDE.md (if present) plus any additions
- Principles are written as design directives, not engineering constraints

### 5. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this reflect the design direction accurately?"`, `header: "Review"`, and `options: [{label: "Looks good — save it", description: "Write to docs/steering/DESIGN.md"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed.

### 6. Write the document

```bash
mkdir -p docs/steering
```

Write the final content to `docs/steering/DESIGN.md`.

Commit the file:

```bash
git add docs/steering/DESIGN.md
git commit -m "docs: add design guidelines steering document"
```

Print the file path.

### 7. Offer wiki sync

Call `AskUserQuestion` with:

- `question`: "Would you like to sync this to the GitHub wiki?"
- `header`: "Wiki sync"
- `options`: `[{label: "Yes — push to wiki", description: "Publish DESIGN.md as a wiki page"}, {label: "Not now", description: "Skip wiki sync"}]`

If **yes**:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
git clone https://github.com/$REPO.wiki.git /tmp/wiki-sync
cp docs/steering/DESIGN.md /tmp/wiki-sync/WTF-Design.md
cd /tmp/wiki-sync && git add WTF-Design.md && git commit -m "Sync: design guidelines" && git push
rm -rf /tmp/wiki-sync
```

### 8. Offer to continue

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Create QA.md", description: "Run `steer-qa` to document the QA standards"}, {label: "Create TECH.md", description: "Run `steer-tech` to document the technical guidelines"}, {label: "Create VISION.md", description: "Run `steer-vision` to document the product vision"}, {label: "Stop here", description: "Exit — no further action"}]`

Route to the appropriate skill based on the answer.
