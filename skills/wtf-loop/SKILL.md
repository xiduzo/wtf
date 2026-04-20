---
name: wtf.loop
description: This skill should be used when a developer wants to autonomously execute all tasks under a fully-specified Epic or Feature — for example "go", "start building", "implement everything", "run the loop", "execute the feature", "build it all", "kick it off". Requires that the Epic/Feature/Task tree is fully written before starting. Chains implement → verify → PR for every task in dependency order, with targeted human-in-the-loop gates for contradictions and ambiguities.
---

# Loop

Autonomously execute a fully-specified Epic or Feature. Core value: once the spec tree is complete (Epic → Features → Tasks), the developer says "go" and the system chains `wtf:implement-task → wtf:verify-task → wtf:create-pr` for every Task in dependency order — surfacing only the decisions a human must actually make.

## Pre-conditions

Before starting, the following must be true:
- All Tasks under the target Feature(s) have been written (`wtf:write-task` complete)
- All Tasks have been designed (`wtf:design-task` complete, `designed` label present) — or the user explicitly waives this
- No Task is missing Gherkin scenarios or Contracts

If any pre-condition fails, surface it as a gate (step 2) rather than stopping silently.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated.

Verify that the following extensions are available — they are required for dependency ordering and hierarchy traversal:

```bash
gh extension list
```

Required:
- `yahsan2/gh-sub-issue` — hierarchy traversal
- `xiduzo/gh-issue-dependency` — dependency ordering

If any are missing, install them before proceeding.

### 1. Identify the target and build the dependency graph

Call `AskUserQuestion` with:

- `question`: "What do you want to execute?"
- `header`: "Target"
- `options` pre-filled from open issues labeled `epic` or `feature`:
  - `[{label: "Feature #<n> — <title>", description: "Execute all Tasks under this Feature"}, ...]`
  - Include an "Epic — all features" option if an Epic is available.
  - Include `{label: "Resume a previous run", description: "Pick up where the loop left off for an in-progress Feature"}` — when selected, fetch open tasks under the chosen Feature that are **not** labeled `implemented` or `verified`, and skip straight to step 4 starting from the first unfinished task. Print which tasks will be skipped (already done) and which will run.

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

Build the full node list with parent context: `(issue_number, type, feature_number, epic_number)`. Include both Tasks and Features in the node list — features can also have cross-feature dependencies.

**Build the dependency graph:**

For every node (Task and Feature) in the list, fetch its dependency edges in parallel:

```bash
gh issue-dependency list <issue_number>
```

This returns two sets per issue: what it **blocks** and what **blocks it**. Record both directions for every node. Build a directed graph:

```
nodes:  { issue_number → { title, type, feature, labels } }
edges:  { issue_number → blocks: [issue_numbers], blocked_by: [issue_numbers] }
```

**Classify each dependency as internal or external:**

- **Internal** — the blocking issue is within the current run's node list. Execution order must respect this edge.
- **External** — the blocking issue is outside the current run (different feature, already-merged task, upstream work). This issue must already be merged before the loop can start.

Record this classification in the graph — it drives both the execution order (step 3) and the external blocker gate (step 2d).

### 2. Pre-flight validation

Run all checks in parallel. Surface failures as human-in-the-loop gates — do not silently skip.

**a. Spec completeness check**

For each Task, verify:
- `designed` label is present
- Gherkin section is non-empty
- Contracts section is non-empty

For each Feature, verify:
- Acceptance Criteria section is non-empty

For each Epic, verify:
- Goal and Bounded Context sections are non-empty

**b. Contradiction scan**

Read each level of the hierarchy and check for contradictions:

- Task Gherkin conflicts with parent Feature ACs (e.g. Task passes a scenario the Feature says should fail)
- Task scope leaks outside the Feature's Bounded Context
- Duplicate Gherkin scenario names across Tasks in the same Feature
- Technical Approach (if present) uses a stack not in `docs/steering/TECH.md`

**c. Codebase reality check**

For each Task's Impacted Areas and Contracts:
- Check that referenced modules, files, or interfaces exist in the codebase
- Check that API shapes in Contracts match current code signatures

Use the Agent tool to search the codebase for each referenced path/interface.

**d. Dependency validation**

Using the dependency graph built in step 1:

1. **Circular dependency check** — run a topological sort over the internal edges. If a cycle is detected, list all issues involved and **hard stop** — do not proceed until the cycle is broken.

2. **External blocker check** — for each external blocker, verify it is merged:

   ```bash
   # Check if the blocking issue is closed (merged via PR):
   gh issue view <external_blocker_number> --json state,stateReason \
     --jq '"#\(.number) \(.state) (\(.stateReason))"'
   ```

   An external blocker is resolved only if its state is `CLOSED` with `stateReason: COMPLETED` (i.e., closed via a merged PR). If any external blocker is unresolved, list them as blockers — the loop cannot start until they are resolved.

3. **Topological sort** — sort all internal nodes into an execution order that respects every `blocked_by` edge. Group nodes at the same depth into **execution phases** — tasks within a phase have no dependency between them and could run in parallel.

**Gate — surface all findings at once:**

If any pre-flight check found issues, present them grouped by type:

```
Pre-flight findings:
  Contradictions:    [list with issue numbers and description]
  Missing sections:  [list]
  Codebase mismatches: [list]
  Unresolved deps:   [list]
  Circular deps:     [list — HARD STOP if any]
```

Call `AskUserQuestion` with:

- `question`: "Pre-flight found [n] issue(s). How would you like to proceed?"
- `header`: "Pre-flight"
- `options`:
  - `{label: "Fix before running", description: "Resolve the issues above, then re-run the loop"}`
  - `{label: "Proceed with warnings", description: "Acknowledge the issues and run anyway (not recommended for contradictions)"}` — only if no circular deps
  - `{label: "Stop", description: "Exit — I'll address these manually"}`

If **no findings**: continue silently.

### 3. Propose the execution plan and wait for approval

Present the dependency-ordered plan as a suggestion derived from the graph. Do not start any implementation until the human explicitly approves it.

Tasks within a phase have no internal dependencies between them; tasks in a later phase depend on at least one task from an earlier phase.

```
Proposed execution plan — Feature #<n>: <title>
─────────────────────────────────────────────
External blockers: ✅ #<x> merged  ✅ #<y> merged

Phase 1  (no blockers)
  Task #10 — Setup DB schema
  Task #11 — Define API contracts

Phase 2  (blocked by Phase 1)
  Task #12 — Settlement logic       blocked by #10, #11  ·  blocks #13

Phase 3  (blocked by Phase 2)
  Task #13 — Notifications          blocked by #12
─────────────────────────────────────────────
3 phases · 4 tasks
```

If executing an Epic, also show cross-feature blocking:

```
Feature #5 — Payment Settlement   (no feature-level blockers)
Feature #6 — Reporting            blocked by Feature #5
```

Call `AskUserQuestion` with:

- `question`: "Here's the suggested execution plan based on the dependency graph. Does this look right?"
- `header`: "Plan review"
- `options`:
  - `{label: "Approve — start the loop", description: "Execute tasks in this order"}`
  - `{label: "Remove a task", description: "Drop one or more tasks from this run — I'll specify which"}`
  - `{label: "Change the order", description: "Override the suggested phase ordering — I'll describe the change"}`
  - `{label: "Decline — stop", description: "Exit without executing anything"}`

**If "Remove a task":** ask which tasks to drop, remove them from the graph (and re-evaluate whether any remaining tasks lose all their blockers and can move to an earlier phase), then re-present the updated plan and ask again.

**If "Change the order":** ask the user to describe the desired change. Apply it, check that no `blocked_by` edges are violated by the new order (warn if they are but do not block), re-present the updated plan and ask again.

**If "Decline — stop":** exit immediately. Nothing has been implemented.

**Only proceed to step 4 after an explicit "Approve" answer.**

### 4. Execute each task

**Sub-agent protocol (mandatory for all phases)**

Sub-agents spawned by the loop do NOT inherit the parent session's loaded skills. Each sub-agent prompt must include:

1. **Inline instructions** — Embed the full step-by-step content of `wtf-implement-task`, `wtf-verify-task`, and `wtf-create-pr` directly in the prompt. Do not reference skill names — sub-agents cannot load them.

2. **Non-interactive overrides** — Sub-agents must NOT call `AskUserQuestion`. All interactive prompts are replaced:
   - Approach review (implement-task step 7): skip, proceed automatically with the derived approach
   - "What's next?" prompts (implement-task step 11, verify-task step 8): skip, the loop controls sequencing
   - Any other interactive choice that would normally pause: record as a pending question (see point 3)

3. **Question/blocker protocol** — If a genuine blocker or ambiguity requires human input (e.g. test failures, missing contracts, codebase mismatches, approach conflicts), the sub-agent must return a structured result instead of asking:
   ```
   NEEDS_INPUT
   task: #<n>
   question: <the question text>
   options: <list of options>
   context: <relevant details>
   ```
   The orchestrator collects all `NEEDS_INPUT` results after each phase, groups them by task, presents them to the user via a single `AskUserQuestion` call, and re-dispatches affected sub-agents with the answers embedded in the prompt before continuing to the next phase.

4. **Mandatory labels** — Sub-agents own label lifecycle for their assigned task. These must always execute, regardless of other outcomes:
   - After TDD cycle completes (implement-task step 11): `gh issue edit <task_number> --add-label "implemented"`
   - After verification passes (verify-task step 7): `gh issue edit <task_number> --add-label "verified"`
   
   Neither step may be deferred to the orchestrator or omitted. If the `gh` command fails, record it in the sub-agent result so the orchestrator can retry.

**Parallelism within phases:** Tasks within the same phase (from the plan in step 3) have no internal dependencies between them. For each phase, spawn one sub-agent per task in parallel using the Agent tool with `isolation: "worktree"`, passing the task number and full spec context to each sub-agent. Apply the sub-agent protocol above. Wait for all sub-agents in the phase to complete, then process any `NEEDS_INPUT` results before starting the next phase.

For each Task (within its phase):

**a. Dependency gate (lightweight re-check)**

Before starting each task, do a quick re-check against its **internal** blockers from the graph built in step 1. The full dependency validation already ran in step 2d — this check only guards against the case where an earlier task in this run was skipped or its PR wasn't merged before the dependent task starts.

For each internal blocker of the current task:

```bash
gh issue view <blocker_number> --json state,stateReason \
  --jq '"#\(.number) \(.state) (\(.stateReason))"'
```

If a blocker is not `CLOSED` / `COMPLETED`, pause:

- `question`: "Task #<blocker> (an internal blocker) hasn't been merged yet. How do you want to proceed?"
- `header`: "Blocked"
- `options`:
  - `{label: "Wait — I'll merge it now", description: "Pause here. Re-run the loop from this task after merging."}`
  - `{label: "Skip this task", description: "Skip Task #<current_task> and continue with tasks that aren't blocked"}`

If all internal blockers are resolved, continue silently.

**b. Implement**

Follow the `wtf:implement-task` process for the Task (embedded inline per the sub-agent protocol above), passing the Task number in as context. The sub-agent must:
- Set up the correct feature branch (creating it if absent)
- Run the TDD cycle
- Explicitly run `gh issue edit <task_number> --add-label "implemented"` — this is mandatory and must not be skipped or deferred

**c. Verify**

Follow the `wtf:verify-task` process (single-task mode), passing the Task number in as context.

Before verifying, classify each Gherkin scenario in the Task:

- **Test-suite covered** — a test file exists that exercises this scenario (e.g. a `describe`/`it` block, a Cucumber step, a `test_*` function). Verification is the test run result. If the suite passes, the scenario is verified — continue automatically.
- **Not covered** — no automated test maps to this scenario. Requires a human-in-the-loop check (manual steps, UI walkthrough, or explicit sign-off).

If **all** scenarios are test-suite covered and the suite passes → proceed to step 4d automatically.

If **any** scenario is not covered by the test suite → pause and present only those uncovered scenarios for human verification. Do not re-verify covered scenarios.

If a covered scenario's tests **fail**:

Call `AskUserQuestion` with:

- `question`: "Task #<n> — [n] test(s) failed. How do you want to proceed?"
- `header`: "Tests failed"
- `options`:
  - `{label: "Fix and re-verify", description: "Pause the loop — fix the implementation, then re-run from this task"}`
  - `{label: "Skip and continue", description: "Skip this task for now and proceed to the next"}`
  - `{label: "Stop loop", description: "Exit the loop entirely"}`

**d. Open PR and wait for pipeline**

Follow the `wtf:create-pr` process, passing the Task number and branch in as context. The PR targets the parent feature branch. Closing happens via `Closes #<task_number>` in the PR body — do not call `gh issue close` directly. Run non-interactively — no confirmation, title review, or body approval.

After the PR is opened, poll its pipeline until all status checks complete:

```bash
gh pr checks <pr_number> --watch
```

This blocks until every check finishes. Once complete, inspect the result:

```bash
gh pr checks <pr_number> --json name,state,conclusion \
  --jq '.[] | "\(.state) \(.conclusion) \(.name)"'
```

**If all checks pass** (`conclusion: SUCCESS` or `conclusion: SKIPPED` for every check) → merge automatically:

```bash
gh pr merge <pr_number> --merge --delete-branch
```

Then continue to the next task.

**If any check fails** (`conclusion: FAILURE` or `conclusion: ACTION_REQUIRED`):

Call `AskUserQuestion` with:

- `question`: "Task #<n> PR pipeline failed — [list failing check names]. How do you want to proceed?"
- `header`: "Pipeline failed"
- `options`:
  - `{label: "Fix and re-run", description: "Pause the loop — push a fix, then re-run the pipeline"}`
  - `{label: "Skip this task", description: "Leave the PR open and continue with remaining tasks"}`
  - `{label: "Stop loop", description: "Exit the loop entirely"}`

**If the pipeline times out or returns no checks** (repo has no CI configured) → merge automatically, as there is nothing to wait on.

**e. Progress update**

After each Task's PR is merged, print:

```
✅ Task #<n> — <title> — merged: <url>
   [n remaining]
```

### 5. Feature PR (after all tasks)

Once all Tasks' PRs are merged into the feature branch, open a PR from the feature branch to `main`. Use both signals together — a task is complete only when its PR is merged AND the issue is closed:

```bash
# Check for merged task PRs
gh pr list --state merged --base feature/<feature-number>-<feature-slug>

# Check for open sub-issues (primary signal — reliable even if feature branch was just created)
gh sub-issue list <feature_number>
# Should be empty (all task issues closed via merged PRs)
```

If both checks show all work is complete (no open sub-issues, all task PRs merged), open the feature PR automatically — no confirmation needed.

If either check shows pending work, list the outstanding tasks and call `AskUserQuestion` with:

- `question`: "Not all task PRs are merged yet. Open the feature PR anyway?"
- `header`: "Feature PR"
- `options`:
  - `{label: "Wait — I'll merge them first", description: "Pause here"}`
  - `{label: "Open it now", description: "Open feature → main PR with unmerged tasks noted in description"}`

Open the feature PR using `wtf:create-pr` targeting `main`, running non-interactively. The body must include `Closes #<feature_number>` and one `Closes #<task_number>` per task on separate lines.

After opening, poll and merge using the same pipeline pattern as step 4d — wait for all checks, auto-merge on green, gate on red.

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

If any Tasks were skipped, list them with reasons and suggest follow-up actions.

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
