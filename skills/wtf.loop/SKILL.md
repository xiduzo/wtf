---
name: wtf.loop
description: This skill should be used when a developer wants to autonomously execute all tasks under a fully-specified Epic or Feature — for example "go", "start building", "implement everything", "run the loop", "execute the feature", "build it all", "kick it off". Requires that the Epic/Feature/Task tree is fully written before starting. Chains implement → verify → PR for every task in dependency order, with targeted human-in-the-loop gates for contradictions and ambiguities.
---

# Loop

Autonomously execute a fully-specified Epic or Feature.

Once the spec tree is complete (Epic → Features → Tasks), the developer says "go".

The system then chains `wtf.implement-task → wtf.verify-task → wtf.create-pr` for every Task in dependency order. Surface only the decisions a human must make.

Shared behavior used throughout this skill:

- Sub-agent spawning rules → `../references/subagent-protocol.md`
- File-conflict graph coloring → `../references/conflict-graph.md`
- Commit and PR conventions → `../references/commit-conventions.md`
- Branch and worktree setup → `../references/branch-setup.md`
- Pre-flight checks (step 2) → `references/pre-flight-validation.md`
- Per-task execution (step 4) → `references/task-execution.md`

## Pre-conditions

Before you start, all of the following must be true:

- All Tasks under the target Feature(s) have been written (`wtf.write-task` complete)
- All Tasks have been designed (`wtf.design-task` complete, `designed` label present) — or the user explicitly waives this
- No Task is missing Gherkin scenarios or Contracts

If any pre-condition fails, surface it as a gate (step 2). Do not stop silently.

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
  - One option per open Feature (e.g. **Feature #<n> — <title>** → execute all Tasks under this Feature)
  - One **Epic — all features** option if an Epic is available
  - **Resume a previous run** → fetch open tasks not yet labeled `implemented` or `verified`. Skip to step 4 from the first unfinished task

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
gh sub-issue list <feature_number>     # yields task numbers
```

Build the full node list with parent context: `(issue_number, type, parent_chain)`.

**Include every issue in the run regardless of type.** Include Tasks, Features, Epics, Bugs, and any loose or untyped issues linked via sub-issue or dependency edges. Type does not gate inclusion. Any issue that can block, be blocked by, or share files with another issue in the run belongs in the graph.

Walk the full transitive closure. Start from the selected target. Follow `gh sub-issue list` down. Follow `gh issue-dependency list` outward (both directions). Keep pulling until no new issues surface.

Do not stop at Feature or Epic boundaries. A Bug linked as a blocker of a Task belongs in the DAG just like the Task does.

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

Left as-is, a dependency on a *parent* (for example Feature B `blocked_by` Feature A) resolves against the parent node alone. That node sits shallower than its deepest child Task. A sibling's Tasks could then start before all of Feature A's Tasks merge.

To prevent this, add a `rolls_up` edge from every parent to each of its children. Use the `gh sub-issue list` traversal already done above. A parent is then satisfied only when **every** descendant — recursively — is satisfied.

`rolls_up` edges are always internal. A parent's children are always pulled into the run. Keep them **separate** from `blocked_by`. They constrain ordering (step 2d.3). They are **not** inherited downward. Otherwise a child would inherit a dependency on itself and create a false cycle.

**Classify each dependency edge (`blocks` / `blocked_by`) as internal or external** (`rolls_up` edges are internal by construction):

- **Internal** — the blocking issue is within the current run's node list. Execution order must respect this edge.
- **External** — the blocking issue is outside the current run (different feature, already-merged task, upstream work). This issue must already be merged before the loop can start.

Record this classification in the graph. It drives both the execution order (step 3) and the external blocker gate (step 2d).

### 2. Pre-flight validation

Run all four checks (a. spec completeness, b. contradiction scan, c. codebase reality, d. dependency validation) per `references/pre-flight-validation.md`. Run in parallel where possible. Surface findings via the Pre-flight gate from the same reference. Do not skip silently.

The dependency-validation step (d) produces the `phases → sub_phases → tasks` structure used in step 3 and step 4.

### 3. Propose the execution plan and wait for approval

Present the dependency-ordered plan as a suggestion derived from the graph. Do not start any implementation until the human explicitly approves it.

Tasks within a phase have no internal dependencies between them. Tasks in a later phase depend on at least one task from an earlier phase.

```
Proposed execution plan — Feature #<n>: <title>
─────────────────────────────────────────────
External blockers: ✅ #<x> merged  ✅ #<y> merged

Phase 1  (no blockers)
  Sub-phase 1.1  [parallel]
    Task #10 — Setup DB schema        impacted: src/db/
    Task #11 — Define API contracts   impacted: src/api/contracts/
  Sub-phase 1.2  [after 1.1 — file conflict with #10]
    Task #14 — Seed migrations        impacted: src/db/

Phase 2  (blocked by Phase 1)
  Sub-phase 2.1  [parallel]
    Task #12 — Settlement logic       blocked by #10, #11  ·  blocks #13

Phase 3  (blocked by Phase 2)
  Sub-phase 3.1  [parallel]
    Task #13 — Notifications          blocked by #12
─────────────────────────────────────────────
3 phases · 5 tasks · 4 sub-phases
```

If you execute an Epic, also show cross-feature blocking:

```
Feature #5 — Payment Settlement   (no feature-level blockers)
Feature #6 — Reporting            blocked by Feature #5
```

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Here's the suggested execution plan based on the dependency graph. Does this look right?"
- header: "Plan review"
- options:
  - **Approve — start the loop** → execute tasks in this order
  - **Remove a task** → drop one or more tasks from this run. Specify which
  - **Change the order** → override the suggested phase ordering. Describe the change
  - **Decline — stop** → exit without executing anything

**If "Remove a task":** Ask which tasks to drop. Remove them from the graph. Re-evaluate whether any remaining tasks lose all their blockers and can move to an earlier phase. Then re-present the updated plan and ask again.

**If "Change the order":** Ask the user to describe the desired change. Apply it. Check that no `blocked_by` edges are violated by the new order (warn if they are, but do not block). Re-present the updated plan and ask again.

**If "Decline — stop":** Exit immediately. Nothing has been implemented.

**Only continue to step 4 after an explicit "Approve" answer.**

### 4. Execute each task

Run the per-task sequence per `references/task-execution.md`. The sequence is: a. dependency gate, b. implement, c. verify, d. open PR + pipeline, e. progress update.

The reference also covers the parallelism-via-DAG-sub-phases rules. It lists the inline step ranges to paste into each sub-agent prompt (`wtf.implement-task` 4–11, `wtf.verify-task` 2–7, `wtf.create-pr` 4–8).

Apply `../references/subagent-protocol.md` for every Agent call. The conflict-free sub-phases from step 2d drive parallelism.

Within a sub-phase, tasks run in parallel via Agent `isolation: "worktree"`. Between sub-phases, all PRs must merge before you advance.

### 5. Feature PR (after all tasks)

Once all Tasks' PRs are merged into the feature branch, open a PR from the feature branch to `main`. Use both signals together. A task is complete only when its PR is merged AND the issue is closed:

```bash
gh pr list --state merged --base feature/<feature-number>-<feature-slug>
gh sub-issue list <feature_number>
# Should be empty (all task issues closed via merged PRs)
```

If both checks show all work is complete (no open sub-issues, all task PRs merged), open the feature PR automatically. No confirmation is needed.

If either check shows pending work, list the outstanding tasks and call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Not all task PRs are merged yet. Open the feature PR anyway?"
- header: "Feature PR"
- options:
  - **Wait — I'll merge them first** → pause here
  - **Open it now** → open feature → main PR with unmerged tasks noted in description

Open the feature PR by spawning a sub-agent that runs the inlined `wtf.create-pr` steps targeting `main`. The body must include `Closes #<feature_number>` and one `Closes #<task_number>` per task on separate lines per `../references/commit-conventions.md`.

After opening, poll and merge using the same pipeline pattern as step 4d. Wait for all checks. Auto-merge on green. Gate on red.

### 6. Summary

Print a final summary:

```
Loop complete — Feature #<n>: <title>
─────────────────────────────────────
Tasks completed:  [n]
Tasks skipped:    [n]
PRs merged:       [list of URLs]
Feature PR:       <url> (merged / open — pipeline pending)
```

If any Tasks were skipped, list them with reasons. Suggest follow-up actions.

### Human-in-the-loop gate reference

The loop pauses and asks for human input only when:

| Trigger | Why human input is needed |
|---|---|
| Spec contradiction (Task vs Feature) | Model cannot resolve intent ambiguity |
| Spec contradiction (Feature vs Epic) | Scope boundary unclear |
| Codebase mismatch (contract/module missing) | Implementation target may have changed |
| Missing Gherkin or Contracts | Cannot implement without a test target |
| Circular dependency (internal) | Hard stop — cannot resolve automatically |
| External blocker not yet merged/closed | Loop cannot start until upstream work is done |
| Internal blocker skipped or unmerged mid-run | Ordering constraint within the current run |
| Gherkin scenario not covered by test suite | No automated signal — human must verify manually |
| Covered test(s) fail | Implementation may need rework |
| PR pipeline check(s) fail | CI signal is authoritative — human must decide whether to fix or skip |
| Pending task PRs before feature PR | Some tasks not yet merged — human decides whether to wait or open early |
