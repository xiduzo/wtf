# Task Execution

Detailed per-task execution sequence for `wtf.loop` step 4. Apply `../../references/subagent-protocol.md` for every Agent call. Key rules:

- Read each target skill's `SKILL.md` at spawn time and paste the relevant step range into the sub-agent prompt — sub-agents cannot load skills by name.
- Sub-agents must not call `AskUserQuestion`; unresolved questions come back as `NEEDS_INPUT` blocks that the orchestrator batches for the user.
- Mandatory labels (`implemented`, `verified`) are owned by the sub-agent and must execute even if other steps fail.

## Step ranges to inline per task sub-agent

| Skill | Step range | Purpose |
|---|---|---|
| `skills/wtf.implement-task/SKILL.md` | steps 4–11 | branch, explore, TDD, coverage, test mapping, mark implemented |
| `skills/wtf.verify-task/SKILL.md` | steps 2–7 | steering load, Gherkin walkthrough, edge cases, observability, QA summary, `verified` label |
| `skills/wtf.create-pr/SKILL.md` | steps 4–8 | spec fetch, diff, draft, create PR |

Skip the ask-user steps in each (approach review, next-step prompts) per the sub-agent protocol.

## Parallelism via DAG sub-phases

The conflict-free sub-phases from step 2d are the unit of parallel execution. For each sub-phase, spawn one sub-agent per task in parallel using the Agent tool with `isolation: "worktree"`. Tasks in different sub-phases within the same phase share overlapping files and must NOT run concurrently — execute sub-phases sequentially within a phase.

Execution order: iterate phases in order → within each phase, iterate sub-phases in order → within each sub-phase, spawn all tasks in parallel.

**Before spawning the next sub-phase or phase, all PRs from the current sub-phase must be merged into the feature branch.** Poll each PR until merged:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Only advance when every PR in the current sub-phase shows `MERGED`. This ensures each new worktree branches off a feature branch that already contains all prior work.

**Worktree base:** see `../../references/branch-setup.md` "Worktree decision" — each sub-agent worktree is created from the feature branch at the moment it is spawned, after all preceding PRs have merged. The sub-agent must always pull the latest feature branch before starting work.

Pass the full sub-phase conflict map to each sub-agent in its prompt context so it knows which files are exclusively owned by its worktree during execution.

## Per-task sequence

For each Task within its phase:

### a. Dependency gate (lightweight re-check)

Before starting each task, do a quick re-check against its **internal** blockers from the graph built in step 1. The full dependency validation already ran in step 2d — this check only guards against the case where an earlier task in this run was skipped or its PR wasn't merged before the dependent task starts.

For each internal blocker of the current task, verify the PR is merged (not just the issue closed):

```bash
gh pr list --state merged --search "Closes #<blocker_number>" --json number,mergedAt \
  --jq '.[0] | "#\(.number) merged \(.mergedAt)"'
```

If no merged PR is found for the blocker, also check issue state as fallback:

```bash
gh issue view <blocker_number> --json state,stateReason \
  --jq '"#\(.number) \(.state) (\(.stateReason))"'
```

A blocker is resolved only when its PR is merged (preferred signal) or the issue is `CLOSED` / `COMPLETED`. If a blocker is unresolved, pause and ask "Task #<blocker> (an internal blocker) hasn't been merged yet. How do you want to proceed?" — header `Blocked`:

- **Wait — I'll merge it now** → pause here; re-run the loop from this task after merging
- **Skip this task** → skip Task #<current_task> and continue with tasks that aren't blocked

If all internal blockers are resolved, continue silently.

### b. Implement

The sub-agent runs the inlined implement-task steps. It must:

- Set up the correct feature branch (creating it if absent) per `../../references/branch-setup.md`
- Run the TDD cycle per `../../references/commit-conventions.md`
- Explicitly run `gh issue edit <task_number> --add-label "implemented"` — mandatory, per the sub-agent protocol

### c. Verify

The sub-agent runs the inlined verify-task steps (single-task mode).

Before verifying, classify each Gherkin scenario in the Task:

- **Test-suite covered** — a test file exists that exercises this scenario (e.g. a `describe`/`it` block, a Cucumber step, a `test_*` function). Verification is the test run result. If the suite passes, the scenario is verified — continue automatically.
- **Not covered** — no automated test maps to this scenario. Requires a human-in-the-loop check (manual steps, UI walkthrough, or explicit sign-off).

If **all** scenarios are test-suite covered and the suite passes → proceed to step d automatically.

If **any** scenario is not covered by the test suite → pause and present only those uncovered scenarios for human verification. Do not re-verify covered scenarios.

If a covered scenario's tests **fail**, ask "Task #<n> — [n] test(s) failed. How do you want to proceed?" — header `Tests failed`:

- **Fix and re-verify** → pause the loop; fix the implementation, then re-run from this task
- **Skip and continue** → skip this task for now and proceed to the next
- **Stop loop** → exit the loop entirely

### d. Open PR and wait for pipeline

The sub-agent runs the inlined create-pr steps. The PR targets the parent feature branch per `../../references/branch-setup.md` "Base-branch policy". Closure happens via `Closes #<task_number>` in the PR body per `../../references/commit-conventions.md` — do not call `gh issue close` directly. Run non-interactively — no confirmation, title review, or body approval.

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

**If any check fails** (`conclusion: FAILURE` or `conclusion: ACTION_REQUIRED`), ask "Task #<n> PR pipeline failed — [list failing check names]. How do you want to proceed?" — header `Pipeline failed`:

- **Fix and re-run** → pause the loop; push a fix, then re-run the pipeline
- **Skip this task** → leave the PR open and continue with remaining tasks
- **Stop loop** → exit the loop entirely

**If the pipeline times out or returns no checks** (repo has no CI configured) → merge automatically, as there is nothing to wait on.

### e. Progress update

After each Task's PR is merged, print:

```
✅ Task #<n> — <title> — merged: <url>
   [n remaining]
```
