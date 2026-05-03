---
name: wtf.steer-design
description: This skill should be used when a team wants to create or refine the design guidelines document — for example "create the design steering doc", "document our design system", "write the design principles", "document our component patterns", "set up the design guidelines", or "update the design doc". Generates docs/steering/DESIGN.md as a living document capturing design principles, the design system, tokens, component patterns, and accessibility standards. Generated once and refined — not regenerated from scratch.
---

# Steer Design

Generate or refine `docs/steering/DESIGN.md` — the design guidelines document. This document is the canonical reference for design decisions, the system in use, tokens, patterns, and accessibility requirements that every designer and implementer must follow.

The shared steering-doc flow (exists-check → research → interview → draft → review → write → wiki sync → continue) lives in `../references/steering-doc-process.md`. Follow that process with the skill-specific inputs below.

- **Doc path:** `docs/steering/DESIGN.md`
- **Template:** `references/design-template.md`
- **Display name / wiki page:** `WTF-Design.md`
- **Commit message:** `docs: add design guidelines steering document`

## Step 2 — Research checklist

Use the Agent tool to extract design facts directly. Do not ask the user for things that can be read:

- **Design system:** Storybook config, component library imports, design-system packages in `package.json`
- **Tokens:** CSS custom properties (`--color-*`, `--spacing-*`), Tailwind config, theme files, token definition files
- **Components:** existing UI components (look for `components/`, `ui/`, `src/components/`)
- **Figma links:** any Figma URLs in README, existing issues, or `docs/`
- **Accessibility:** existing WCAG references, axe configs, jest-axe usage
- **Responsive breakpoints:** Tailwind config, CSS media queries, layout files
- `docs/steering/VISION.md` if it exists — extract any design principles already stated there

Produce a draft of Stack, Tokens, and Component Patterns from research alone where possible.

## Step 3 — Gap-topic list

Apply `../references/questioning-style.md` for questions in this step. Ask only about items research could not determine:

1. **Design principles** — "What 3–5 principles guide every design decision for this product?" Pre-fill from `VISION.md` or any existing design docs.
2. **Design system** — "What design system are you using? Do you have a Figma library?" Pre-fill with anything found in the codebase or imports.
3. **Token gaps** — "Are there tokens not yet defined in code that designers rely on?" Pre-fill with gaps inferred from design-system research.
4. **Responsive strategy** — "How does the layout adapt across breakpoints?" Pre-fill with breakpoints found in the codebase.
5. **Accessibility target** — "Are there accessibility requirements beyond WCAG 2.1 AA?" Pre-fill with any existing a11y config found.

## Step 4 — Writing rules

- Tokens must reflect what is actually defined in the codebase — not aspirational values.
- Component patterns reference real component paths where they exist.
- Accessibility section always includes the baseline rules from the project's `CLAUDE.md` (if present) plus any additions.
- Principles are written as design directives, not engineering constraints.

## Step 8 — Continue options

- `{label: "Create QA.md", description: "Run wtf.steer-qa to document the QA standards"}`
- `{label: "Create TECH.md", description: "Run wtf.steer-tech to document the technical guidelines"}`
- `{label: "Create VISION.md", description: "Run wtf.steer-vision to document the product vision"}`
- `{label: "Stop here", description: "Exit — no further action"}`
