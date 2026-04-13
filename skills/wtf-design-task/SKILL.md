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

Skip this step if invoked from `write-task` or another skill that already ran gh-setup this session.

### 1. Identify the Task

If the user provided an issue number in their request, use it directly. Otherwise search for recent open issues with label `task` to populate options and call `AskUserQuestion` with `question: "Which Task are you designing?"`, `header: "Task"`, and `options` pre-filled with 1–2 likely open Task issue references inferred from GitHub search (e.g. recent open issues labeled `task`).

Fetch the Task first, extract the Feature number from its Context section, then fetch the Feature:

```bash
gh issue view <task_number>    # Functional Description, Gherkin, Design Reference — also yields feature number
# Extract feature number, then:
gh issue view <feature_number> # User stories, ACs, visual context
```

### 2. Lifecycle check

Check whether the task already has a `designed` label:

```bash
gh issue view <task_number> --json labels --jq '.labels[].name'
```

If the `designed` label is **present**, call `AskUserQuestion` with:

- `question`: "This task already has a `designed` label. Continuing will overwrite the existing Design Reference. How would you like to proceed?"
- `header`: "Already designed"
- `options`: `[{label: "Redesign it", description: "Overwrite the existing Design Reference with a new one"}, {label: "Exit", description: "Leave the existing design as-is"}]`

- **Redesign it** → continue.
- **Exit** → exit immediately.

If the `designed` label is **absent**, continue silently.

### 3. Load the design steering document

Use the Read tool to attempt reading `docs/steering/DESIGN.md`.

If the file **exists**: keep its content in context. Use its design principles, tokens, component patterns, and accessibility standards to inform every decision in this session. Do not surface it to the user — just apply it silently.

If the file **does not exist**, call `AskUserQuestion` with:

- `question`: "docs/steering/DESIGN.md doesn't exist yet. This document captures your design principles, tokens, and component patterns. Would you like to create it now?"
- `header`: "Design steering doc missing"
- `options`: `[{label: "Create it now", description: "Run `steer-design` before continuing (recommended)"}, {label: "Skip for this session", description: "Continue without it — design decisions won't reference project standards"}]`

- **Create it now** → follow the `steer-design` process, then return to this skill and continue from step 4.
- **Skip for this session** → continue without it.

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

Call `AskUserQuestion` with `question: "How would you like to handle design assets for this task?"`, `header: "Design assets"`, and `options`:

- `{label: "I have Figma frames", description: "Provide frame URLs — I'll validate coverage against Gherkin scenarios"}`
- `{label: "Generate designs for me", description: "I'll use Figma MCP to generate frames from the Gherkin scenarios and design system"}`
- `{label: "Scaffold a spec only", description: "No Figma — produce a text component spec from the scenarios"}`
- `{label: "Partial — some states designed", description: "Provide available frames; remaining states go to generate or scaffold"}`

**Path A — Human provides frames:**
Collect frame URLs. For each Gherkin scenario from step 5, check whether a frame covers it. Flag any scenario with no matching frame as a gap. Present the coverage matrix: scenario → frame URL (or ⚠ gap). If gaps exist, call `AskUserQuestion` asking whether to generate the missing frames (route to Path B) or leave them as pending.

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
Collect available frame URLs, run Path A validation on covered states. For uncovered states, call `AskUserQuestion` asking whether to generate (Path B) or scaffold (Path C) the remainder.

### 7. Draft the Design Reference

Produce the content for the Design Reference section of the Task:

- Frame URLs mapped to Gherkin scenarios (Path A/B), or scaffolded component spec (Path C)
- Coverage matrix: scenario → frame URL or ⚠ pending
- Component breakdown: which exist in codebase, which are new
- Interaction notes: hover, focus, error states, transitions
- Responsive behavior if applicable
- Design tokens to apply

### 8. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this cover all the states in the Gherkin?"`, `header: "Review"`, and `options: [{label: "Yes — looks complete", description: "Proceed to update the task"}, {label: "Missing states", description: "I want to add more coverage"}, {label: "Other changes", description: "I want to adjust something else"}]`.

Apply edits, then proceed.

### 9. Update the Task issue

> Note: read the current issue body first (`gh issue view <task_number>`), replace only the Design Reference section with the new content, and preserve all other sections unchanged. Write the full updated body to a temp file and use `--body-file`.

```bash
gh issue edit <task_number> --body-file /tmp/wtf-design-task-body.md
```

Add the `designed` lifecycle label to mark this step complete:

```bash
gh issue edit <task_number> --add-label "designed"
```

Print the updated Task issue URL.

### 10. Offer to continue

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Implement this Task", description: "Run `implement-task` for this Task now (default)"}, {label: "Design another Task", description: "Design another Task for the same Feature"}, {label: "Stop here", description: "Exit — no further action"}]`

- **Implement this Task** → follow the `implement-task` process, passing the Task number in as context so the user is not asked for it again.
- **Design another Task** → restart this skill from step 1, reusing the same Feature context.
- **Stop here** → exit.
