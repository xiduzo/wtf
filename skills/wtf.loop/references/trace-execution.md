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

## Parallelism — Skeleton first, then Traces schedule like Features

The conflict-free sub-phases from step 2d are the unit of cross-feature parallelism. Within a sub-phase, every Feature unit advances concurrently. Legacy Task units in the sub-phase spawn in parallel as before, one sub-agent per Task.

Within one Feature, run two stages:

1. **Skeleton, alone.** It lays the Spine, so every later Trace depends on it. Nothing else in the Feature starts until its code is pushed and green.
2. **Everything else, colored.** Apply `../../references/conflict-graph.md` to the Feature's remaining Traces, using each Trace's `## Impacted Areas`. Traces with no shared files run at the same time, each in its own worktree. Traces that share files fall into later sub-phases and stack in Trace Plan order.

Expect much of a Feature's set to serialize — Traces of one Feature share files by construction. The win is the disjoint case, which shows up as soon as a Feature carries more than one story.

Execution order: phases in order → sub-phases in order → within each sub-phase, all Feature units and legacy Tasks in parallel → within each Feature, Skeleton then its own colored sub-phases.

**A Trace never waits for a merge.** It branches off the branch of the Trace it builds on, as soon as that code exists, and opens its PR against that branch — see `../../references/branch-setup.md` "Trace branch" and "Stack mechanics". Human review latency no longer idles the run. GitHub retargets each stacked PR when its parent merges with its head branch deleted, so the stack unwinds on its own.

**Worktrees isolate anything running at the same time**: separate Features, and sibling Traces of one Feature. Spawn each concurrent trace sub-agent with `isolation: "worktree"`. The worktree branches from that Trace's **stack base**, resolved per `branch-setup.md`. The sub-agent must run `git pull --rebase origin <stack_base>` before starting work. A Trace stacked behind another needs no worktree of its own — it runs after, on the same line.

**Advancement gates** follow `../../references/conflict-graph.md`:

- Between Trace sub-phases *inside* a Feature: the previous sub-phase's branches are pushed and green. No merge required.
- Between cross-Feature sub-phases: PRs merged — the feature PR in `staged` delivery, the Feature's final Trace PR in `trunk`, plus every legacy Task PR. Poll until merged:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Pass the full sub-phase conflict map to each sub-agent in its prompt context so it knows which files are exclusively owned by its worktree during execution.

**If review changes an already-stacked Trace**, restack its descendants per `branch-setup.md` "Restack" before they continue, and report which Traces moved.

## Per-trace sequence

For each Trace, in Trace Plan order within its Feature unit:

### a. Stack + dependency gate (lightweight re-check)

The Trace's stack base must exist and carry the code of the Trace it builds on — pushed and green. It does **not** need to be merged. Verify this on resume. Then re-check the Trace's and its Feature's **internal** blockers from the graph built in step 1.

An internal blocker inside the same Feature is satisfied by a pushed, green branch. An internal blocker in another Feature still needs a merged PR — a different Feature's unmerged stack is not visible from this branch line. The full dependency validation already ran in step 2d — this check only guards against the case where an earlier unit in this run was skipped or its PR was not merged.

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

The sub-agent runs the inlined create-pr steps. The PR base is this Trace's **stack base** per `../../references/branch-setup.md` "Base-branch policy" — the branch of the Trace it builds on when that Trace is still open, otherwise the feature branch (`staged`) or `main` (`trunk`). Closure happens via `Closes #<trace_number>` in the PR body per `../../references/commit-conventions.md` — do not call `gh issue close` directly.

**Opening this PR does not block the Feature's other Traces.** Traces in the next sub-phase branch off this Trace's branch as soon as it is pushed and green. Everything below runs alongside them, not in front of them. In `trunk` delivery, when this Trace exhausts the Trace Plan, the body also carries `Closes #<feature_number>` on its own line. Run non-interactively — no confirmation, title review, or body approval.

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

`--delete-branch` is mandatory, not stylistic: deleting the head branch is what makes GitHub retarget every PR stacked on this one. Without it the stack strands. Merge bottom-up — a stacked PR cannot merge before its base.

If the merge is refused because the base branch requires an approving review, leave the PR open and continue. The Traces stacked on it already have the code they need. Collect the pending approval as a loop gate rather than idling on it.

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

**Scenario-set gate.** The headless re-aim may reorder or re-batch the remaining Trace Plan entries and move scenarios between them — sequencing is its own. It may never change the plan's scenario set on its own, in either direction: it never adds a newly-discovered scenario and never drops one. It **proposes** both. Collect every proposal as a loop gate (`NEEDS_INPUT`-style), batched with other pending gates at the next gate round. A human approves every addition and every drop. On approval, re-run headless refine with the approved change as the pre-loaded insight, marked human-approved, so refine applies it and posts the audit trail. On rejection, the plan keeps its current set.

This is what bounds the run. Growth is the direction that never terminates on its own, so it is gated for the same reason shrinkage is: the delivery contract is human-owned.

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
   Re-aim: [no change | reordered | re-batched | set change proposed (gated): +<n> / -<n>]
   [n traces remaining in Feature #<f>]
```
