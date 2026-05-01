---
name: wtf.design-task
description: This skill should be used when a designer is picking up a Task issue to add design coverage. Triggers on phrases like "I want to design task #X", "help me add Figma references to this task", "create a component spec for this feature", "what UI states need design coverage", "scaffold the design reference section", "what components do I need for this task", "which Figma frames cover this ticket", "add design coverage to task #X", "does task #X have design coverage", or "link designs to this task". Handles exploring the design system, deriving UI states from Gherkin scenarios, and writing back a structured Design Reference into the issue.
---

# Design Task

Pick up an existing Task as a designer. Core value: reads the Gherkin scenarios to identify every UI state that needs design coverage, then helps you document the design references back into the issue so developers have a single source of truth.

See `references/component-spec-template.md` for the expected structure when scaffolding a component spec without Figma frames.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.write-task` or another skill that already ran gh-setup this session.

### 1. Identify the Task

If the user provided an issue number in their request, use it directly. Otherwise apply `../references/questioning-style.md` and ask "Which Task are you designing?" — header `Task`, options from recent open issues labeled `task`.

Walk Task → Feature per `../references/spec-hierarchy.md` to extract Functional Description, Gherkin, Design Reference (Task) and user stories / ACs / visual context (Feature).

### 2. Lifecycle check

Apply the **present-label overwrite gate** from `../references/lifecycle-labels.md` for the `designed` label on the Task — output is "Design Reference", re-run verb is "Redesign". If absent, continue silently.

### 3. Load the design steering document

Load `docs/steering/DESIGN.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-design`). Apply its design principles, tokens, component patterns, and accessibility standards silently throughout this session.

### 4. Explore the design system

Use the Agent tool with these concrete searches (run in parallel):

- `Glob('src/components/**/*', 'src/**/components/**/*', 'components/**/*')` — existing UI components; note file names that match domain objects or UI states in the Task
- `Glob('**/{tokens,theme,variables,design-tokens}.{css,scss,ts,js,json}')` + `Grep` for CSS custom property declarations (`--`) or Tailwind config keys — design tokens in use (colors, spacing, typography)
- `Glob('src/**/*.{stories,story}.{ts,tsx,js,jsx,mdx}')` — Storybook stories as pattern references for similar screens or flows
- `Grep` for `figma.com` URLs across all `.md`, `.mdx`, and issue body files in the repo — existing Figma references linked in related issues or docs

### 5. Identify UI states from Gherkin

For each Gherkin scenario in the Task:

- Identify the UI state it represents (e.g. empty, loading, error, success, disabled, edge case)
- Note any interaction or transition implied by the When/Then steps

List these states explicitly — this becomes the design coverage checklist.

### 6. Ask about design assets

Ask "How would you like to handle design assets for this task?" — header `Design assets`:

- **I have Figma frames** → provide frame URLs; I'll validate coverage against Gherkin scenarios (Path A)
- **Generate designs for me** → use Figma MCP to generate frames from the Gherkin scenarios and design system (Path B)
- **Scaffold a spec only** → no Figma; produce a text component spec from the scenarios (Path C)
- **Partial — some states designed** → provide available frames; remaining states go to generate or scaffold

**Path A — Human provides frames:**
Collect frame URLs. For each Gherkin scenario from step 5, check whether a frame covers it. Flag any scenario with no matching frame as a gap. Present the coverage matrix: scenario → frame URL (or ⚠ gap). If gaps exist, ask "How should I handle the uncovered scenarios?" — header `Gaps`:

- **Generate missing frames** → run Path B for the gaps
- **Leave as pending** → record gaps in the Design Reference and continue

**Path B — AI generates via Figma MCP:**
Check whether the Figma MCP tool `generate_figma_design` is available. If unavailable, warn the user and fall back to Path C (scaffold).

If available: for each uncovered UI state, call `generate_figma_design` with:
- The Gherkin scenario as the design brief
- Component patterns and tokens from `docs/steering/DESIGN.md` (loaded in step 3)
- Any shared components identified in the parent Feature's Design Handoff (if available)

Collect the generated frame URLs and treat them as Path A frames from this point forward.

**Path C — Scaffold spec only:**
Draft a component spec using the structure in `references/component-spec-template.md`, listing each state with its required UI elements and interactions. No Figma frames — this is a text-only design brief for the developer.

**Partial:**
Collect available frame URLs, run Path A validation on covered states. For uncovered states, ask "How should I handle the remaining states?" — header `Remainder`:

- **Generate** → run Path B
- **Scaffold** → run Path C

### 7. Draft the Design Reference

Produce the content for the Design Reference section of the Task:

- Frame URLs mapped to Gherkin scenarios (Path A/B), or scaffolded component spec (Path C)
- Coverage matrix: scenario → frame URL or ⚠ pending
- Component breakdown: which exist in codebase, which are new
- Interaction notes: hover, focus, error states, transitions
- Responsive behavior if applicable
- Design tokens to apply

### 8. Review with user

Show the draft. Then ask "Does this cover all the states in the Gherkin?" — header `Review`:

- **Yes — looks complete** → proceed to update the task
- **Missing states** → add more coverage
- **Other changes** → adjust something else

Apply edits, then proceed.

### 9. Update the Task issue

> Note: read the current issue body first (`gh issue view <task_number>`), replace only the Design Reference section with the new content, and preserve all other sections unchanged. Write the full updated body to a temp file and use `--body-file`.

```bash
gh issue edit <task_number> --body-file /tmp/wtf.design-task-<task_number>-body.md
```

Add the `designed` lifecycle label to mark this step complete:

```bash
gh issue edit <task_number> --add-label "designed"
```

Print the updated Task issue URL.

### 10. Offer to continue

Ask "What's next?" — header `Next step`:

- **Implement this Task** → run `wtf.implement-task` for this Task now (default)
- **Design another Task** → design another Task for the same Feature
- **Stop here** → exit, no further action

- **Implement this Task** → follow the `wtf.implement-task` process, passing the Task number in as context so the user is not asked for it again.
- **Design another Task** → restart this skill from step 1, reusing the same Feature context.
- **Stop here** → exit.
