# Trace Execution

Detailed per-trace execution sequence for `wtf.loop` step 4. Apply `../../references/subagent-protocol.md` for every Agent call. Key rules:

- Read each target skill's `SKILL.md` at spawn time and paste the relevant steps into the sub-agent prompt — sub-agents cannot load skills by name.
- Sub-agents must not call `AskUserQuestion`; unresolved questions come back as `NEEDS_INPUT` blocks that the orchestrator batches for the user.
- Mandatory labels (`implemented`, `verified`) are owned by the sub-agent and must execute even if other steps fail.

## Skills to inline per trace sub-agent

Inline the execution steps of each skill below, minus its interactive gates (skipped per the sub-agent protocol — approach review, "what's next?" prompts):

| Skill | Inline | Expected return |
|---|---|---|
| `skills/wtf.implement-trace/SKILL.md` | branch setup through the `implemented` label | the **"Revealed:"** learnings block — capture it for re-aim |
| `skills/wtf.verify-trace/SKILL.md` | verification of the Scenario Claim through the `verified` label | pass/fail per claimed scenario |
| `skills/wtf.create-pr/SKILL.md` | steps 4–8 (spec fetch, diff, draft, create PR) | the PR URL |

## Parallelism — Features advance concurrently, Traces serialize

The conflict-free sub-phases from step 2d are the unit of cross-feature parallelism. Within a sub-phase, every Feature unit advances its Trace sequence concurrently. Within one Feature, exactly **one** Trace runs at a time, in Trace Plan order. Legacy Task units in the sub-phase spawn in parallel as before, one sub-agent per Task.

Execution order: iterate phases in order → within each phase, iterate sub-phases in order → within each sub-phase, run all Feature units (and legacy Tasks) in parallel, each Feature stepping through its own Trace sequence.

**Worktrees isolate Features, not Traces** (see `../../references/branch-setup.md` "Worktree decision"). One Feature's Traces share one branch line. Spawn each trace sub-agent with `isolation: "worktree"`; the worktree branches from the Trace's base branch at spawn time — the feature branch in `staged` delivery, `main` in `trunk` delivery. Because each Trace starts only after the previous Trace's PR merged, that base already contains all prior Traces' work. The sub-agent must run `git pull --rebase origin <base_branch>` before starting work.

**Before advancing to the next sub-phase, every unit in the current sub-phase must be complete** per the advancement gate in `../../references/conflict-graph.md`: in `staged` delivery the feature PR is merged, in `trunk` delivery the Feature's final Trace PR is merged, and every legacy Task PR is merged. Poll each PR until merged:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Pass the full sub-phase conflict map to each sub-agent in its prompt context so it knows which files are exclusively owned by its worktree during execution.

## Per-trace sequence

For each Trace, in Trace Plan order within its Feature unit:

### a. Merge + dependency gate (lightweight re-check)

The previous plan entry's PR must be merged — this holds by construction, but verify it on resume. Then re-check the Trace's and its Feature's **internal** blockers from the graph built in step 1. The full dependency validation already ran in step 2d — this check only guards against the case where an earlier unit in this run was skipped or its PR was not merged.

If an internal blocker is a parent node (Feature/Epic — it carries `rolls_up` children), expand it to its descendant Traces (and legacy Tasks) and check those PRs instead: a parent issue can stay open until its feature PR merges, so testing the parent's state mid-run would falsely block.

For each internal blocker, verify the PR is merged (not just the issue closed):

```bash
gh pr list --state merged --search "Closes #<blocker_number>" --json number,mergedAt \
  --jq '.[0] | "#\(.number) merged \(.mergedAt)"'
```

If no merged PR is found for the blocker, also check issue state as fallback:

```bash
gh issue view <blocker_number> --json state,stateReason \
  --jq '"#\(.number) \(.state) (\(.stateReason))"'
```

A blocker is resolved only when its PR is merged (preferred signal) or the issue is `CLOSED` / `COMPLETED`. If a blocker is unresolved, pause and ask "#<blocker> (an internal blocker) hasn't been merged yet. How do you want to proceed?" — header `Blocked`:

- **Wait — I'll merge it now** → pause here; re-run the loop from this Trace after merging
- **Skip this trace** → skip Trace #<current_trace> and continue with units that aren't blocked. Skipping a Trace also pauses its Feature's sequence — later Traces build on it.

If all internal blockers are resolved, continue silently.

### b. Implement

The sub-agent runs the inlined implement-trace steps. It must:

- Set up the trace branch from the delivery-mode base (creating the feature branch first in `staged` delivery, if absent) per `../../references/branch-setup.md`
- Run the TDD cycle against the claimed scenarios per `../../references/commit-conventions.md`
- Explicitly run `gh issue edit <trace_number> --add-label "implemented"` — mandatory, per the sub-agent protocol
- Return the **"Revealed:"** learnings block — what the Trace exposed about the Spine, the plan, or the spec

Capture the "Revealed:" block. Step e feeds it into the re-aim.

### c. Verify

The sub-agent runs the inlined verify-trace steps (single-trace mode). Verification covers exactly the Scenario Claim — the claimed scenarios projected from the Feature body.

Before verifying, classify each claimed scenario:

- **Test-suite covered** — a test file exists that exercises this scenario (e.g. a `describe`/`it` block, a Cucumber step, a `test_*` function). Verification is the test run result. If the suite passes, the scenario is verified — continue automatically.
- **Not covered** — no automated test maps to this scenario. Requires a human-in-the-loop check (manual steps, UI walkthrough, or explicit sign-off).

If **all** claimed scenarios are test-suite covered and the suite passes → proceed to step d automatically.

If **any** claimed scenario is not covered by the test suite → pause and present only those uncovered scenarios for human verification. Do not re-verify covered scenarios.

If a covered scenario's tests **fail**, ask "Trace #<n> — [n] test(s) failed. How do you want to proceed?" — header `Tests failed`:

- **Fix and re-verify** → pause the loop; fix the implementation, then re-run from this Trace
- **Skip and continue** → skip this Trace for now; its Feature's sequence pauses with it
- **Stop loop** → exit the loop entirely

Capture the verify results (pass/fail per claimed scenario) for the re-aim in step e.

### d. Open PR, wait for pipeline, merge

The sub-agent runs the inlined create-pr steps. The PR base follows `../../references/branch-setup.md` "Base-branch policy": the parent feature branch in `staged` delivery, `main` in `trunk` delivery. Closure happens via `Closes #<trace_number>` in the PR body per `../../references/commit-conventions.md` — do not call `gh issue close` directly. In `trunk` delivery, when this Trace exhausts the Trace Plan, the body also carries `Closes #<feature_number>` on its own line. Run non-interactively — no confirmation, title review, or body approval.

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

**If any check fails** (`conclusion: FAILURE` or `conclusion: ACTION_REQUIRED`), ask "Trace #<n> PR pipeline failed — [list failing check names]. How do you want to proceed?" — header `Pipeline failed`:

- **Fix and re-run** → pause the loop; push a fix, then re-run the pipeline
- **Skip this trace** → leave the PR open; the Feature's sequence pauses with it
- **Stop loop** → exit the loop entirely

**If the pipeline times out or returns no checks** (repo has no CI configured) → merge automatically, as there is nothing to wait on.

### e. Re-aim via headless refine

After the Trace's PR merges, run `wtf.refine` headlessly per its Headless mode section, on the parent Feature, with the insight pre-loaded. The insight is the Trace's outcome:

- the "Revealed:" learnings block from step b
- the verify results from step c (pass/fail per claimed scenario, plus anything QA surfaced)

Spawn it as a sub-agent per `../../references/subagent-protocol.md`: read `skills/wtf.refine/SKILL.md` at spawn time and inline its Headless mode steps. The audit-trail comment on the Feature is refine's mandatory side effect — it is always posted.

**Grow-only rule.** The headless re-aim may reorder or re-batch the remaining Trace Plan entries, move scenarios between entries, and add newly-discovered scenarios. It may never drop a scenario or a story on its own. It may only **suggest** a drop. Collect every drop suggestion as a loop gate (`NEEDS_INPUT`-style), batched with other pending gates at the next gate round. A human approves every shrinkage. On approval, re-run headless refine with the approved drop as the pre-loaded insight, marked human-approved, so refine applies it and posts the audit trail. On rejection, the plan keeps the scenario.

If refine reports nothing to change, continue silently.

### f. Reconcile the Trace Plan

Re-read the Feature body's Trace Plan — the re-aim may have changed it:

- Update the remaining sequence to the new order and batching.
- If a new entry has no Trace issue yet, create it before dispatch: spawn a sub-agent with the inlined non-interactive steps of `skills/wtf.write-trace/SKILL.md`.
- If the plan is exhausted, run Feature completion (`wtf.loop` step 5) for this unit.

Then continue with the next entry.

### g. Progress update

After each Trace's PR is merged and the re-aim is done, print:

```
✅ Trace #<n> — <title> — merged: <url>
   Re-aim: [no change | reordered | +<n> scenarios | drop suggested (gated)]
   [n traces remaining in Feature #<f>]
```
