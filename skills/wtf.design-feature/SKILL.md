---
name: wtf.design-feature
description: This skill should be used when a designer wants to produce a holistic design for a full feature before it is broken into tasks — for example "design feature #X", "create the Figma flow for this feature", "map the UX for this feature", "design the full user journey for feature #X", "create a feature design handoff", or "add design coverage to feature #X". Covers the full feature journey (all user stories, all screens, cross-screen states) and writes the Design Handoff section back into the Feature issue, fulfilling the Definition of Ready gate. Not applicable to individual Tasks — use `wtf.design-task` for per-task Gherkin-level coverage.
---

# Design Feature

Pick up a Feature as a designer and produce a holistic design covering the full user journey before tasks are cut. Core value: maps every user story to screens and states, identifies shared components across the feature, and writes a complete Design Handoff back into the Feature issue — so `wtf.feature-to-tasks` can derive better tasks and `wtf.design-task` inherits feature-level decisions rather than reinventing them.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from another skill that already ran gh-setup this session.

### 1. Identify the Feature

If the user provided an issue number in their request, use it directly. Otherwise apply `../references/questioning-style.md` and ask "Which Feature are you designing?" — header `Feature`, options from recent open issues labeled `feature`.

Walk Feature → Epic per `../references/spec-hierarchy.md` to extract user stories, ACs, Edge Cases, Domain Events (Feature) and Goal, Context, Design Artifacts (Epic — strategic input).

Extract and hold in context:
- Feature capability name (Actor + verb + object)
- All user stories
- All Acceptance Criteria
- Edge Cases
- Domain Events (emitted/consumed)
- Epic's Design Artifacts (any Figma links or research docs — these are upstream constraints)

### 2. Lifecycle check

Apply the **present-label overwrite gate** from `../references/lifecycle-labels.md` for the `designed` label on the Feature — output is "Design Handoff", re-run verb is "Redesign". If absent, continue silently.

### 3. Load the design steering document

Load `docs/steering/DESIGN.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-design`). Apply its design principles, tokens, component patterns, and accessibility standards silently throughout this session.

### 4. Explore the design system and codebase

Use the Agent tool with these searches (run in parallel):

- `Glob('src/components/**/*', 'src/**/components/**/*', 'components/**/*')` — existing UI components; flag any that map to domain objects in this Feature's user stories
- `Glob('**/{tokens,theme,variables,design-tokens}.{css,scss,ts,js,json}')` — design tokens
- `Glob('src/**/*.{stories,story}.{ts,tsx,js,jsx,mdx}')` — Storybook stories as pattern references for similar flows
- `Grep` for `figma.com` URLs across `.md`, `.mdx` files — existing Figma references in related issues or docs

Note which existing components can be reused vs which are new. This feeds step 7.

### 5. Map the full user journey

For each user story ("As a [Actor], I want [action] so that [outcome]"), derive:

1. **Entry point** — what triggers this story? (screen, action, event)
2. **Happy path screens** — ordered list of screens/states the actor moves through
3. **Branch states** — loading, error, empty, partial data, permission denied
4. **Exit point** — what confirms the story is complete for the actor?

Also map:
- **Cross-story transitions** — screens shared between multiple user stories
- **Edge case screens** — one screen per Edge Case from the Feature issue
- **Domain Event surfaces** — where in the UI does each emitted Domain Event become visible to the actor?

Produce a journey map as a structured list — do not ask the user, derive from user stories and ACs.

### 6. Ask about design assets

Ask "How would you like to handle designs for this feature?" — header `Design assets`:

- **I have Figma frames** → provide frame URLs; I'll validate coverage against the full journey map (Path A)
- **Generate designs for me** → use Figma MCP to generate frames from the user stories and design system (Path B)
- **Scaffold a brief only** → no Figma; produce a text screen inventory and component map (Path C)
- **Partial — some screens designed** → provide available frames; remaining screens go to generate or scaffold

**Path A — Human provides frames:**
Collect the top-level Figma file URL plus individual frame URLs. For each screen in the journey map (step 5), check whether a frame covers it. Present a coverage matrix: screen → frame URL (or ⚠ gap). If gaps exist, ask "How should I handle the uncovered screens?" — header `Gaps`:

- **Generate missing frames** → run Path B for the gaps
- **Leave as pending** → record gaps in the Design Handoff and continue

Also validate provided frames against spec:
- Every user story has at least one matching frame
- Every edge case from the Feature issue has a matching error/boundary state frame
- Every Domain Event surface identified in step 5 is represented

Flag any validation failures as gaps in the coverage matrix.

**Path B — AI generates via Figma MCP:**
Check whether the Figma MCP tool `generate_figma_design` is available. If unavailable, warn the user and fall back to Path C (scaffold).

If available: for each screen in the journey map without a frame, call `generate_figma_design` with:
- The screen's user story and entry/exit points as the design brief
- Component patterns and tokens from `docs/steering/DESIGN.md` (loaded in step 3)
- Shared components identified in step 7 as reuse constraints
- Any Figma URLs from the Epic's Design Artifacts as style reference

Collect the generated frame URLs and treat them as Path A frames for the coverage matrix and Design Handoff.

**Path C — Scaffold brief only:**
For each screen in the journey map, produce a text brief listing required UI elements, interactions, and relevant design tokens. This is a Figma-free design brief a designer or developer can execute against. Use `references/component-spec-template.md` as the structure if available.

**Partial:**
Collect available frame URLs, run Path A validation on covered screens. For uncovered screens, ask "How should I handle the remaining screens?" — header `Remainder`:

- **Generate** → run Path B
- **Scaffold** → run Path C

### 7. Identify shared components

Across all screens in the journey map, identify:

- **Reused existing components** — already in the codebase (found in step 4); list component path + which screens use it
- **New shared components** — appear on 2+ screens but do not exist yet; name them using domain language
- **Screen-specific components** — appear on only one screen; note them but do not detail here (that is `wtf.design-task`'s job)

This component map reduces duplication when `wtf.design-task` runs per-task.

### 8. Draft the Design Handoff

Produce content for the **Design Handoff** section of the Feature issue. Use the structure in `references/design-handoff-template.md`.

### 9. Review with user

Show the draft. Then ask "Does this cover the full feature journey?" — header `Review`:

- **Looks complete — update the issue** → proceed
- **Missing screens or states** → add coverage
- **Other changes** → adjust something else

Apply edits, then proceed.

### 10. Update the Feature issue

Read the current issue body, replace only the **Design Handoff** section with the new content, preserve all other sections. Write to temp file and use `--body-file`:

```bash
gh issue edit <feature_number> --body-file /tmp/wtf.design-feature-<feature_number>-body.md
```

Add the `designed` label when either:
- Path A/B: all screens in the journey map have Figma frames (no open gaps in coverage matrix), or
- Path C: the full scaffold brief is complete (no Figma expected)

```bash
gh issue edit <feature_number> --add-label "designed"
```

If Path A/B has open gaps, do not add `designed` — note it will be added once gaps are closed.

This fulfills the Feature DoR gate: "Design handoff complete".

Print the updated Feature issue URL.

### 11. Offer to continue

Ask "What's next?" — header `Next step`:

- **Break into Tasks** → run `feature-to-tasks`; design context will inform task breakdown (default)
- **Design another Feature** → design another Feature for the same Epic
- **Stop here** → exit, no further action

- **Break into Tasks** → follow the `wtf.feature-to-tasks` skill, passing the Feature number in as context. Note to the user that `wtf.design-task` will inherit the shared component map from this Design Handoff.
- **Design another Feature** → restart from step 1, reusing the same Epic context.
- **Stop here** → exit.
