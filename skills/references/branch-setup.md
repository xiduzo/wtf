# Branch Setup

Shared trunk-based branch strategy and worktree policy for `wtf.implement-trace`, `wtf.hotfix`, `wtf.create-pr`, and `wtf.loop`.

## Resolve the delivery mode

Read `delivery` from `.wtf/config.json` (written by `wtf.setup`). Default to `staged`:

```bash
WTF_DELIVERY=$(python3 - <<'PY' 2>/dev/null || true
import json
try:
    print((json.load(open(".wtf/config.json")).get("delivery") or "").strip())
except Exception:
    pass
PY
)
case "$WTF_DELIVERY" in staged|trunk) : ;; *) WTF_DELIVERY=staged ;; esac
```

Then check the Feature body for a per-feature delivery override with its stated reason. When the Feature declares one, that mode wins for the Feature and its Traces.

## Branch hierarchy

`staged` delivery (default):

```
main
└── feature/<feature-number>-<feature-slug>    (merges → main)
    └── trace/<trace-number>-<trace-slug>       (merges → feature branch)
```

`trunk` delivery:

```
main
└── trace/<trace-number>-<trace-slug>           (merges → main)
```

In `trunk` delivery, do not create a feature branch. The Feature closes when its Trace Plan is exhausted, not via a feature-PR merge.

Hotfixes are identical in both modes:

```
main
└── hotfix/<bug-number>-<slug>                  (merges → main)
```

## Slug generation

A slug is a 2–4 word kebab-case summary. Restrict it to `[a-z0-9-]`.

Spawn a subagent with model `claude-haiku-4-5-20251001`. Pass the title as input. Apply `./subagent-protocol.md` for the spawn. Do not use `AskUserQuestion` inside that subagent.

Examples: `date-range-filter`, `null-check-payment-id`.

## Feature branch — create or check out (`staged` only)

```bash
git fetch origin
git checkout feature/<feature-number>-<feature-slug> 2>/dev/null || {
  git checkout main
  git pull --rebase origin main
  git checkout -b feature/<feature-number>-<feature-slug>
  git push -u origin feature/<feature-number>-<feature-slug>
}
git pull --rebase origin feature/<feature-number>-<feature-slug>
```

## Trace branch — create or resume

Trace branches **stack**. A Trace branches off the branch of the Trace it builds on, as soon as that Trace's code exists. It never waits for that Trace's PR to merge. A human reviewing is not a reason for the next Trace to idle.

The Skeleton is always first and always alone — it lays the Spine, so every later Trace of the Feature depends on it.

Resolve the **stack base**:

| The Trace | Stack base |
|---|---|
| Skeleton | the feature branch (`staged`) or `main` (`trunk`) |
| A later Trace whose **Builds on** Trace is still open | that Trace's branch |
| A later Trace whose **Builds on** Trace already merged | the feature branch (`staged`) or `main` (`trunk`) |

Two Traces that build on the same Trace and share no files are **siblings**. Both branch off the same stack base and run at the same time, each in its own worktree. Two Traces that share files stack one on the other, in Trace Plan order.

```bash
# Fresh work — branch off the resolved stack base:
git fetch origin
git checkout <stack-base>
git pull --rebase origin <stack-base>
git checkout -b trace/<trace-number>-<trace-slug>

# Resumed work (branch already exists):
git checkout trace/<trace-number>-<trace-slug>
git rebase origin/<stack-base>
```

Resolve all conflicts before you continue.

## Stack mechanics

Open every Trace PR against its **stack base**, not against the feature branch:

```bash
gh pr create --base <stack-base> --head trace/<trace-number>-<trace-slug> ...
```

**Every merge must delete the head branch.** GitHub retargets an open PR to its parent's base when the parent merges *and the parent's head branch is deleted*. That is what unwinds the stack with no manual work: when `trace/10` merges into `feature/5` and its branch is deleted, every PR based on `trace/10` retargets to `feature/5` on its own, and each diff collapses to that Trace's own commits, because `trace/10`'s commits are now ancestors of `feature/5`.

```bash
gh pr merge <pr_number> --squash --delete-branch
```

Turn on **Settings → General → Automatically delete head branches** so a human who merges through the web UI does not strand the stack. `wtf.setup` checks this setting.

A stacked PR can never merge before the PR it is based on. Merge bottom-up, in stack order.

## Restack — when a base Trace changes

Review feedback on a Trace that others stack on invalidates their base. Rebase the whole chain from its root. `--update-refs` moves every intermediate `trace/*` branch with it (needs git 2.38 or later):

```bash
git fetch origin
git checkout trace/<deepest-trace-in-the-stack>
git rebase --update-refs origin/<stack-root>
git push --force-with-lease origin trace/<n1>-<slug1> trace/<n2>-<slug2> ...
```

Set `git config rebase.updateRefs true` once, and plain `git rebase` behaves this way.

Resolve conflicts before you continue. Tell the user which Traces were restacked and why.

This is the price of stacking. You pay it only when review changes an earlier Trace, and only for the Traces above it.

## Hotfix branch — direct from main

```bash
git fetch origin
git checkout main
git pull --rebase origin main
git checkout -b hotfix/<bug-number>-<slug>
git push -u origin hotfix/<bug-number>-<slug>
```

Hotfix branches never depend on a feature branch. They target `main` directly.

## Base-branch policy (PR target)

| Current branch | Delivery mode | PR base |
|---|---|---|
| `trace/*` — Skeleton | `staged` | parent `feature/*` |
| `trace/*` — Skeleton | `trunk` | `main` |
| `trace/*` — stacked on an open Trace | any | that Trace's `trace/*` branch |
| `trace/*` — its base Trace already merged | `staged` | parent `feature/*` |
| `trace/*` — its base Trace already merged | `trunk` | `main` |
| `feature/*` | `staged` | `main` |
| `hotfix/*` | any | `main` |
| `task/*` (legacy) | any | parent `feature/*` |
| anything else | — | ask the user |

The PR base always equals the stack base the branch was cut from. Never open a Trace PR against a branch the Trace did not branch from — the diff would carry the intervening Trace's commits.

## Worktree decision (cross-feature parallelism)

When a skill spawns multiple sub-agents that edit code (`wtf.loop`, `wtf.verify-trace` Full Feature mode), set Agent `isolation: "worktree"`. Each sub-agent then has its own copy of the repo.

Worktrees isolate anything that runs **at the same time**: separate Features, and sibling Traces of one Feature that share no files. A Trace stacked on another Trace does not need its own worktree — it runs after, on the same branch line. Schedule siblings with `./conflict-graph.md` before spawning them.

The worktree branches from the Trace's base branch at spawn time — the feature branch in `staged` delivery, `main` in `trunk` delivery. Spawn only after all prior PRs in the same conflict-graph sub-phase have merged.

Before work starts, each sub-agent must run `git pull --rebase origin <base_branch>`.

See `./conflict-graph.md` for how to schedule worktrees so two parallel agents never touch the same files.

## Print the branch name

After setup, always print the active branch name. The user then knows where work happens.
