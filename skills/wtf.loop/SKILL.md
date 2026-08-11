---
name: wtf.loop
description: This skill should be used when a developer wants to autonomously execute all Traces under a fully-specified Epic or Feature — for example "go", "start building", "implement everything", "run the loop", "execute the feature", "build it all", "kick it off". Requires that the Epic/Feature/Trace tree is fully written before starting. Chains implement → verify → PR → re-aim for every Trace — spine-first within each Feature, parallel across Features — with targeted human-in-the-loop gates for contradictions, ambiguities, and plan shrinkage.
---

# Loop

Autonomously execute a fully-specified Epic or Feature.

Once the spec tree is complete (Epic → Features → Traces), the developer says "go".

The dispatch unit is the **Trace**. For every Trace the system chains `wtf.implement-trace → wtf.verify-trace → wtf.create-pr`, waits for the PR to merge, then re-aims the parent Feature's Trace Plan through headless `wtf.refine`. Traces within a Feature run strictly sequentially, in Trace Plan order. Features run in parallel where the cross-feature conflict graph allows. Surface only the decisions a human must make.

Shared behavior used throughout this skill:

- Sub-agent spawning rules → `../references/subagent-protocol.md`
- Conflict scheduling (Features parallel, Traces sequential) → `../references/conflict-graph.md`
- Commit and PR conventions → `../references/commit-conventions.md`
- Branch, worktree, and delivery-mode setup → `../references/branch-setup.md`
- Pre-flight checks (step 2) → `references/pre-flight-validation.md`
- Per-trace execution (step 4) → `references/trace-execution.md`

## Pre-conditions

Before you start, all of the following must be true:

- Each target Feature has a Trace Plan, and its Trace issues exist (`wtf.feature-to-traces` complete)
- Each Trace Plan starts with exactly one Skeleton
- Per story, the Scenario Claims partition the story's scenarios — full cover, no overlap
- All Traces are designed (`wtf.design-trace` complete, `designed` label present) — or the user explicitly waives this

If any pre-condition fails, surface it as a gate (step 2). Do not stop silently.

## Delivery mode

Resolve the delivery mode once, per `../references/branch-setup.md`. Honor a per-Feature override declared in the Feature body.

- **`staged`** — trace PRs merge into the feature branch. When the Trace Plan is exhausted, a feature PR merges into `main`.
- **`trunk`** — trace PRs merge into `main`. No feature branch exists. The final Trace PR closes the Feature with a `Closes #<feature_number>` line per `../references/commit-conventions.md`.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install + auth). If `gh` is not installed or not authenticated, stop.

Verify that the extensions below are available. They are required for dependency ordering and hierarchy traversal:

```bash
gh extension list
```

Required:

- `yahsan2/gh-sub-issue` — hierarchy traversal
- `xiduzo/gh-issue-dependency` — dependency ordering

If any are missing, install them before you continue.

### 1. Identify the target and build the dependency graph

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "What do you want to execute?"
- header: "Target"
- options:
  - One option per open Feature (e.g. **Feature #<n> — <title>** → execute all Traces under this Feature)
  - One **Epic — all features** option if an Epic is available
  - **Resume a previous run** → fetch open Traces not yet labeled `implemented` or `verified`. Reconcile against each Feature's Trace Plan checklist: a checked entry with a merged PR is done. Resume each Feature from its first unfinished entry, in plan order. Skip to step 4.

**Fetch the hierarchy:**

If a Feature is selected:

```bash
gh issue view <feature_number>
gh sub-issue list <feature_number>
```

If an Epic is selected:

```bash
gh issue view <epic_number>
gh sub-issue list <epic_number>        # yields feature numbers
# For each feature in parallel:
gh sub-issue list <feature_number>     # yields trace numbers
```

From each Feature body, read the ordered Trace Plan, the stories with their canonical Gherkin, and any delivery override.

Build the full node list with parent context: `(issue_number, type, parent_chain)`.

**Include every issue in the run regardless of type.** Include Traces, legacy Tasks, Features, Epics, Bugs, and any loose or untyped issues linked via sub-issue or dependency edges. Type does not gate inclusion. Any issue that can block, be blocked by, or share files with another issue in the run belongs in the graph. Detect legacy Tasks per `../references/issue-classification.md` and treat them as legacy work items.

Walk the full transitive closure. Start from the selected target. Follow `gh sub-issue list` down. Follow `gh issue-dependency list` outward (both directions). Keep pulling until no new issues surface.

Do not stop at Feature or Epic boundaries. A Bug linked as a blocker of a Trace belongs in the DAG just like the Trace does.

**Build the dependency graph:**

For every node in the list — type-agnostic — fetch its dependency edges in parallel:

```bash
gh issue-dependency list <issue_number>
```

This returns two sets per issue: what it **blocks** and what **blocks it**. Record both directions for every node. Build a directed graph:

```
nodes:  { issue_number → { title, type, feature, labels } }
edges:  { issue_number → {
          blocks:     [issue_numbers],   # dependency — from gh issue-dependency
          blocked_by: [issue_numbers],   # dependency — from gh issue-dependency
          rolls_up:   [issue_numbers],   # children — added by the roll-up step below
        } }
```

**Roll up each parent over its children (so a parent is a join, not a shortcut):**

A sub-issue link is hierarchy, not a blocking edge.

Left as-is, a dependency on a *parent* (for example Feature B `blocked_by` Feature A) resolves against the parent node alone. That node sits shallower than its deepest child Trace. A sibling's Traces could then start before all of Feature A's Traces merge.

To prevent this, add a `rolls_up` edge from every parent to each of its children. Use the `gh sub-issue list` traversal already done above. A parent is then satisfied only when **every** descendant — recursively — is satisfied.

`rolls_up` edges are always internal. A parent's children are always pulled into the run. Keep them **separate** from `blocked_by`. They constrain ordering (step 2d.3). They are **not** inherited downward. Otherwise a child would inherit a dependency on itself and create a false cycle.

**Collapse Traces into Feature units:**

Fold each Feature and its Traces into one **Feature unit** that carries the ordered Trace sequence from the Trace Plan. Traces of one Feature never enter the conflict graph — they run spine-first, one after another, per `../references/conflict-graph.md`. Legacy Task children stay individual units and keep conflict-graph scheduling. In a mixed Feature, both are child work items. Only the sequencing differs: the Trace sequence serializes by plan order, and the legacy Tasks schedule by the graph.

**Classify each dependency edge (`blocks` / `blocked_by`) as internal or external** (`rolls_up` edges are internal by construction):

- **Internal** — the blocking issue is within the current run's node list. Execution order must respect this edge.
- **External** — the blocking issue is outside the current run (different feature, already-merged work, upstream work). This issue must already be merged before the loop can start.

Record this classification in the graph. It drives both the execution order (step 3) and the external blocker gate (step 2d).

### 2. Pre-flight validation

Run all four checks (a. spec completeness, b. contradiction scan, c. codebase reality, d. dependency validation) per `references/pre-flight-validation.md`. Run in parallel where possible. Surface findings via the Pre-flight gate from the same reference. Do not skip silently.

The dependency-validation step (d) produces the `phases → sub_phases → units` structure used in step 3 and step 4.

### 3. Propose the execution plan and wait for approval

Present the dependency-ordered plan as a suggestion derived from the graph. Do not start any implementation until the human explicitly approves it.

Units within a phase have no internal dependencies between them. Units in a later phase depend on at least one unit from an earlier phase. Inside a Feature unit, the Trace sequence is fixed by the Trace Plan.

```
Proposed execution plan — Epic #4: <title>   ·   delivery: staged
─────────────────────────────────────────────
External blockers: ✅ #<x> merged  ✅ #<y> merged

Phase 1  (no blockers)
  Sub-phase 1.1  [features in parallel]
    Feature #5 — Payment settlement       impacted: src/settlements/
      Trace sequence (spine-first):
        1. ☄️ #10 Skeleton — status for one settled payment
        2. ☄️ #11 Deepening — settlement failure modes
    Feature #6 — Reporting                impacted: src/reports/
      Trace sequence (spine-first):
        1. ☄️ #20 Skeleton — monthly report happy path
  Sub-phase 1.2  [after 1.1 — file conflict with #5]
    Task #14 — Seed migrations (legacy)   impacted: src/settlements/db/

Phase 2  (blocked by Phase 1)
  Sub-phase 2.1
    Feature #7 — Notifications            blocked by Feature #5
      Trace sequence (spine-first):
        1. ☄️ #30 Skeleton — settlement email happy path
─────────────────────────────────────────────
2 phases · 3 features · 4 traces · 1 legacy task
```

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Here's the suggested execution plan based on the dependency graph and the Trace Plans. Does this look right?"
- header: "Plan review"
- options:
  - **Approve — start the loop** → execute in this order
  - **Remove a unit** → drop one or more Features, Traces, or legacy Tasks from this run. Specify which
  - **Change the order** → override the suggested phase ordering. Describe the change
  - **Decline — stop** → exit without executing anything

**If "Remove a unit":** Ask which units to drop. Remove them from the graph. Re-evaluate whether any remaining units lose all their blockers and can move to an earlier phase. Removal from this run does not change the Feature's Trace Plan. To drop a Trace's scenarios permanently, run `wtf.refine` on the Feature — a human approves every drop. Then re-present the updated plan and ask again.

**If "Change the order":** Ask the user to describe the desired change. Apply it across units. Check that no `blocked_by` edges are violated by the new order (warn if they are, but do not block). Do not reorder Traces inside a Feature here — that order belongs to the Trace Plan and changes through `wtf.refine`. Re-present the updated plan and ask again.

**If "Decline — stop":** Exit immediately. Nothing has been implemented.

**Only continue to step 4 after an explicit "Approve" answer.**

### 4. Execute each Trace

Run the per-trace sequence per `references/trace-execution.md`. The sequence is: a. merge + dependency gate, b. implement, c. verify, d. open PR + pipeline + merge, e. re-aim via headless refine, f. plan reconcile, g. progress update.

The reference also covers the parallelism rules: Feature units in one sub-phase advance concurrently, one active Trace per Feature at a time. It lists the skill files to inline into each sub-agent prompt.

Apply `../references/subagent-protocol.md` for every Agent call. The conflict-free sub-phases from step 2d drive cross-feature parallelism.

Collect every `NEEDS_INPUT` block and every re-aim shrinkage suggestion into one pending-gates list. Present them batched at the next gate round (per `../references/subagent-protocol.md` rule 3), grouped by Feature.

### 5. Feature completion (delivery-mode aware)

Run this per Feature unit, as soon as its Trace Plan is exhausted. Exhausted means: every plan entry is checked, every Trace PR is merged, and every Trace carries the `verified` label.

**`staged` delivery** — open a PR from the feature branch to `main`. Confirm completion with both signals first:

```bash
gh pr list --state merged --base feature/<feature-number>-<feature-slug>
gh issue view <feature_number> --json body --jq .body   # Trace Plan — all entries checked
```

If both checks show all work is complete, open the feature PR automatically. No confirmation is needed. Open it by spawning a sub-agent that runs the inlined `wtf.create-pr` steps targeting `main`. The body must include `Closes #<feature_number>` and one `Closes #<trace_number>` per Trace, on separate lines, per `../references/commit-conventions.md`. After opening, poll and merge using the same pipeline pattern as step 4d.

If either check shows pending work, list the outstanding Traces and call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Not all trace PRs are merged yet. Open the feature PR anyway?"
- header: "Feature PR"
- options:
  - **Wait — I'll merge them first** → pause here
  - **Open it now** → open feature → main PR with unmerged Traces noted in the description

**`trunk` delivery** — no feature PR exists. The final Trace PR carries `Closes #<feature_number>` and closes the Feature on merge. Verify the Feature issue is closed. If it is still open, surface a gate — do not call `gh issue close` for completed work (see `../references/commit-conventions.md`).

**Re-aim after completion:** if a later re-aim adds entries to an exhausted Trace Plan, reopen the Feature issue and continue its Trace sequence from the new entries.

### 6. Summary

Print a final summary:

```
Loop complete — <target>: <title>
─────────────────────────────────────
Traces completed:  [n]
Traces skipped:    [n]
Re-aims applied:   [n]  (drops suggested: [n], approved: [n])
PRs merged:        [list of URLs]
Feature PRs:       [urls] (staged) / Features closed: [list] (trunk)
```

If any Traces were skipped, list them with reasons. Suggest follow-up actions.

### Human-in-the-loop gate reference

The loop pauses and asks for human input only when:

| Trigger | Why human input is needed |
|---|---|
| Spec contradiction (Trace claim vs Feature scenarios) | Model cannot resolve intent ambiguity |
| Spec contradiction (Feature vs Epic) | Scope boundary unclear |
| Scenario Claims do not partition a story (gap or overlap) | Delivery contract incomplete — human decides the split |
| Trace Plan missing, or Skeleton absent / not first | Cannot sequence without a plan |
| Codebase mismatch (module or path missing) | Implementation target may have changed |
| Circular dependency (internal) | Hard stop — cannot resolve automatically |
| External blocker not yet merged/closed | Loop cannot start until upstream work is done |
| Internal blocker skipped or unmerged mid-run | Ordering constraint within the current run |
| Re-aim suggests dropping a scenario or story | Grow-only rule — a human approves every shrinkage |
| Claimed scenario not covered by test suite | No automated signal — human must verify manually |
| Covered test(s) fail | Implementation may need rework |
| PR pipeline check(s) fail | CI signal is authoritative — human must decide whether to fix or skip |
| Pending trace PRs before feature PR (`staged`) | Some Traces not yet merged — human decides whether to wait or open early |
