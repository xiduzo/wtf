---
name: wtf.design-trace
description: This skill should be used when a designer is picking up a Trace issue to add design coverage — mapping the Trace's claimed Gherkin scenarios to Figma frames or component specs. Triggers on phrases like "I want to design trace #X", "help me add Figma references to this trace", "create a component spec for this trace", "what UI states need design coverage", "scaffold the design reference section", "what components do I need for this trace", "which Figma frames cover this trace", "add design coverage to trace #X", "does trace #X have design coverage", or "link designs to this trace". Handles exploring the design system, deriving UI states from the claimed scenarios, and writing back a structured Design Reference into the issue.
---

# Design Trace

Take an existing Trace as a designer. Read the Trace's claimed Gherkin scenarios. Find every UI state the claim needs design coverage for. Document the design references in the issue so developers have one source of truth.

The scope is the Scenario Claim — only the claimed scenarios, never the story's full list. The scenario text is canonical in the Feature body. Shared, feature-level design decisions come from the Feature's Design Handoff (written by `wtf.design-feature`).

See `references/component-spec-template.md` for the structure when you scaffold a component spec without Figma frames.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.write-trace` or another skill that already ran gh-setup this session.

### 1. Identify the Trace

If the user gave an issue number, use it. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Trace are you designing?"
- header: "Trace"
- options: from recent open Trace issues (list per `../references/issue-classification.md`)

Walk Trace → Feature per `../references/spec-hierarchy.md`. Extract the Story, the Scenario Claim, the Spine Position, and any existing Design Reference from the Trace. Extract the user stories with their canonical Gherkin, the ACs, and the Design Handoff (shared components, tokens, visual context) from the Feature.

Resolve each claimed scenario name to its canonical text in the Feature body. If the Trace's synced copy differs, the Feature wins — note the drift to the user and continue with the canonical text.

### 2. Lifecycle check

Apply the **present-label overwrite gate** from `../references/lifecycle-labels.md` for the `designed` label on the Trace. Output is "Design Reference". Re-run verb is "Redesign". If the label is absent, continue.

### 3. Load the design steering document

Load `docs/steering/DESIGN.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-design`). Apply its design principles, tokens, component patterns, and accessibility standards for this session.

### 4. Explore the design system

Use the Agent tool with these searches (run in parallel):

- `Glob('src/components/**/*', 'src/**/components/**/*', 'components/**/*')` — existing UI components. Note file names that match domain objects or UI states in the claimed scenarios
- `Glob('**/{tokens,theme,variables,design-tokens}.{css,scss,ts,js,json}')` + `Grep` for CSS custom property declarations (`--`) or Tailwind config keys — design tokens in use (colors, spacing, typography)
- `Glob('src/**/*.{stories,story}.{ts,tsx,js,jsx,mdx}')` — Storybook stories as pattern references for similar screens or flows
- `Grep` for `figma.com` URLs across `.md`, `.mdx`, and issue body files — existing Figma references in related issues or docs

### 5. Identify UI states from the claimed scenarios

For each claimed Gherkin scenario (canonical text from step 1):

- Identify the UI state it represents (e.g. empty, loading, error, success, disabled, edge case)
- Note any interaction or transition implied by the When/Then steps

List these states. This list is the design coverage checklist. Do not add states for scenarios outside the claim — those belong to other Traces of the story.

### 6. Ask about design assets

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "How would you like to handle design assets for this trace?"
- header: "Design assets"
- options:
  - **I have Figma frames** → provide frame URLs. Validate coverage against the claimed scenarios (Path A)
  - **Generate designs for me** → use Figma MCP to generate frames from the claimed scenarios and design system (Path B)
  - **Scaffold a spec only** → no Figma. Produce a text component spec from the claimed scenarios (Path C)
  - **Partial — some states designed** → provide available frames. Send remaining states to generate or scaffold

**Path A — Human provides frames:**
Collect frame URLs. For each claimed scenario from step 5, check whether a frame covers it. Flag any scenario with no matching frame as a gap. Present the coverage matrix: scenario → frame URL (or ⚠ gap). If gaps exist, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "How should I handle the uncovered scenarios?"
- header: "Gaps"
- options:
  - **Generate missing frames** → run Path B for the gaps
  - **Leave as pending** → record gaps in the Design Reference and continue

**Path B — AI generates via Figma MCP:**
Check whether the Figma MCP tool `generate_figma_design` is available. If it is unavailable, warn the user and use Path C (scaffold).

If available: for each uncovered UI state, call `generate_figma_design` with:
- The claimed Gherkin scenario as the design brief
- Component patterns and tokens from `docs/steering/DESIGN.md` (loaded in step 3)
- Any shared components from the parent Feature's Design Handoff (if available)

Collect the generated frame URLs. Treat them as Path A frames from this point.

**Path C — Scaffold spec only:**
Draft a component spec with the structure in `references/component-spec-template.md`. List each state with its required UI elements and interactions. No Figma frames. This is a text-only design brief for the developer.

**Partial:**
Collect available frame URLs. Run Path A validation on covered states. For uncovered states, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "How should I handle the remaining states?"
- header: "Remainder"
- options:
  - **Generate** → run Path B
  - **Scaffold** → run Path C

### 7. Draft the Design Reference

Apply strict STE per `../references/ste-writing.md` before you write any durable body.

Produce the content for the Design Reference section of the Trace:

- Frame URLs mapped to claimed scenarios (Path A/B), or scaffolded component spec (Path C)
- Coverage matrix: claimed scenario → frame URL or ⚠ pending
- Component breakdown: which exist in the codebase or the Feature's Design Handoff, which are new
- Interaction notes: hover, focus, error states, transitions
- Responsive behavior if applicable
- Design tokens to apply

Reference scenarios by name only — the canonical text lives in the Feature body. Do not copy Gherkin into the Design Reference.

### 8. Review with user

Show the draft. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this cover all the states in the claimed scenarios?"
- header: "Review"
- options:
  - **Yes — looks complete** → proceed to update the trace
  - **Missing states** → add more coverage
  - **Other changes** → adjust something else

Apply edits. Then proceed.

### 9. Update the Trace issue

> Note: read the current body with the gh body helper. Replace only the Design Reference section with the new content (Read + Edit tools). Preserve all other sections. If the body has no `## Design Reference` section yet, insert one before `## Definition of Done`. See `../references/gh-body-helper.md`.

```bash
python3 .wtf/gh-body.py read <trace_number>        # prints a temp path; Read it, edit the Design Reference section
python3 .wtf/gh-body.py edit <trace_number> --body-file "<path-from-read>"
```

Add the `designed` lifecycle label to mark this step complete:

```bash
gh issue edit <trace_number> --add-label "designed"
```

Print the updated Trace issue URL.

### 10. Offer to continue

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Implement this Trace** → run `wtf.implement-trace` for this Trace now (default)
  - **Design another Trace** → design another Trace for the same Feature
  - **Stop here** → exit. No further action

- **Implement this Trace** → follow the `wtf.implement-trace` process. Pass the Trace number as context so the user is not asked for it again.
- **Design another Trace** → restart this skill from step 1. Reuse the same Feature context.
- **Stop here** → exit.
