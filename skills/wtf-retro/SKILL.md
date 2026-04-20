---
name: wtf.retro
description: This skill should be used when a team wants to close out a completed Epic or sprint, capture what was planned vs. what shipped, learn from deviations, and formally mark the Epic done — for example "run a retro on this epic", "close out the epic", "what deviated from the plan", "retrospective for epic #X", "what did we learn from this epic", "mark this epic as complete", or "write up the post-mortem". Routes learnings into steering docs and generates a final Epic summary. Pairs naturally with the changelog skill for the user-facing output.
---

# Retro

Close out a completed Epic with a structured retrospective. Core value: compares what was planned (original Epic spec) against what shipped (closed Tasks + PRs), surfaces deviations, routes learnings into steering docs, and formally closes the Epic so the team starts the next initiative with a clean slate.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

### 1. Identify the Epic

If an Epic number was passed in, use it directly. Otherwise call `AskUserQuestion` with `question: "Which Epic are you closing out?"`, `header: "Epic"`, and `options` pre-filled from open Epics via `gh issue list --label epic --state open --limit 10`.

Fetch the Epic and its full hierarchy:

```bash
gh issue view <epic_number>
gh sub-issue list <epic_number>              # feature numbers
# For each feature (in parallel):
gh issue view <feature_number>
gh sub-issue list <feature_number>           # task numbers
# For each task (in parallel):
gh issue view <task_number>
```

Also fetch:
- All PRs that closed issues under this Epic (search by `Closes #<n>` in merged PRs):
  ```bash
  gh pr list --state merged --json number,title,body,mergedAt --limit 100
  ```
- The original Epic creation date and the date of the last merged PR (actual duration)

### 2. Check completion status

Verify all work is actually done before running a retro:

- All child Features are closed
- All child Tasks are closed (or explicitly marked `won't implement`)
- No open PRs targeting feature branches under this Epic

If anything is still open, call `AskUserQuestion` with:

- `question`: "Not all work is closed yet — [list open items]. Run the retro anyway?"
- `header`: "Incomplete work"
- `options`: `[{label: "Run retro anyway", description: "Some items are open — I'll note them as incomplete"}, {label: "Wait until complete", description: "Exit — finish the remaining work first"}]`

### 3. Compare planned vs. shipped

Build a side-by-side comparison:

**Planned** (from original Epic spec):
- Goal statement
- Success Metrics
- Feature Breakdown (original list from Epic body)
- Bounded Context

**Shipped** (from closed issues and PRs):
- Features actually created and merged
- Tasks actually created and merged
- Actual calendar duration (Epic opened → last PR merged)

Identify deviations:
- Features planned but not built (descoped or deferred)
- Features added that were not in the original breakdown (scope growth)
- Tasks that took significantly more iterations than expected (PR re-open, multiple verify cycles)
- Success Metrics: were they actually achieved? (state what you can verify from the spec; flag ones that require manual measurement)

### 4. Gather learnings

Use `AskUserQuestion` for each question. Only ask what isn't already evident from the issue history.

**Q1 — What was harder than expected?**

- `question`: "What was harder or took longer than planned in this Epic?"
- `header`: "Friction points"
- `options`: pre-filled with 2–3 inferences from the deviation analysis (e.g. "Feature #X needed 3 verify cycles", "Task #Y was unscoped after implementation started")

**Q2 — What should we do differently next time?**

- `question`: "If you ran this Epic again, what would you change about how it was planned or executed?"
- `header`: "Process improvements"
- `options`: `[{label: "Better scoping upfront", description: "Scope drift was the main issue"}, {label: "Earlier design", description: "Design gaps caused implementation rework"}, {label: "Clearer contracts", description: "Interface ambiguity caused re-work"}, {label: "Nothing significant", description: "Execution was smooth"}, {label: "I'll describe it", description: "Free text"}]`

**Q3 — Any domain model insights?**

- `question`: "Did this Epic reveal anything new about the domain model — new concepts, corrected names, missing bounded contexts?"
- `header`: "Domain insights"
- `options`: `[{label: "Yes — describe them", description: "New terms or corrections to capture"}, {label: "No domain changes", description: "Model held up well"}]`

### 5. Route learnings to steering docs

For each learning gathered, determine where it belongs using the same routing table as `reflect`:

| Learning type | Target doc |
|---|---|
| Architecture pattern, implementation gotcha | `TECH.md` |
| Test failure pattern, QA gap | `QA.md` |
| Design inconsistency, component misuse | `DESIGN.md` |
| Scope confusion, domain language drift | `VISION.md` |
| Doesn't clearly fit | `TECH.md` (default) |

For each target doc, append under `## Hard-Won Lessons` using the format:

```
- **[Short label]** — [Concrete rule or observation]. *Learned <YYYY-MM-DD> during Epic #<n>.*
```

Commit the steering doc updates:

```bash
git add docs/steering/
git commit -m "docs(steering): lessons from Epic #<epic_number>"
```

If any domain model insights were gathered (Q3), also update the glossary via the same pattern as `write-epic` step 10.

### 6. Write the retro summary

Post a structured retro comment on the Epic issue:

```bash
gh issue comment <epic_number> --body "<retro_summary>"
```

The retro summary must include:

```markdown
## Retrospective — <YYYY-MM-DD>

**Duration:** <Epic opened> → <last PR merged> ([n] days)

### Planned vs. shipped

| Item | Planned | Shipped | Delta |
|------|---------|---------|-------|
| Features | [n] | [n] | [+n added / -n descoped] |
| Tasks | [n] | [n] | ... |

**Descoped:** [list features/tasks that were planned but not built — with reason]  
**Added:** [list features/tasks added beyond original scope — with reason]

### Success Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| <from Epic spec> | <value> | ✅ / ❌ / ⚠️ needs manual check |

### Lessons learned

[Bullet list of the learnings gathered in step 4 — in plain language, not the steering doc format]

### Steering docs updated

[List which docs were updated with new lessons]
```

### 7. Offer to generate a changelog

Call `AskUserQuestion` with:

- `question`: "Would you like to generate a changelog entry or GitHub Release for this Epic?"
- `header`: "Changelog"
- `options`: `[{label: "Yes — run changelog", description: "Run wtf.changelog for this Epic (recommended)"}, {label: "Not now", description: "Skip — I'll handle the release notes separately"}]`

If yes → follow the `changelog` process with the Epic number pre-loaded as context.

### 8. Close the Epic

The Epic closes automatically when all child Feature PRs contain `Closes #<feature_number>`, which in turn contains `Closes #<epic_number>` — via GitHub's auto-close chain. Confirm this has happened:

```bash
gh issue view <epic_number> --json state -q .state
```

If the Epic is already `CLOSED` → print: "Epic #<n> is already closed via merged PRs. Retro complete."

If still open (e.g. auto-close chain didn't fire): ask the user whether to close it via a merged PR reference or directly:

Call `AskUserQuestion` with:

- `question`: "Epic #<n> is still open. How would you like to close it?"
- `header`: "Close Epic"
- `options`: `[{label: "Close as completed", description: "Mark as closed — all work is done"}, {label: "Leave open", description: "I'll close it separately"}]`

If "Close as completed":
```bash
gh issue close <epic_number> --comment "Closed after retro — all Features and Tasks merged."
```

### 9. Print the final summary

```
Retro complete — Epic #<n>: <title>
──────────────────────────────────────
Duration:      [n] days
Features:      [n] shipped / [n] descoped
Tasks:         [n] merged
Learnings:     [n] captured → TECH.md, QA.md, ...
Epic status:   closed ✅
```
