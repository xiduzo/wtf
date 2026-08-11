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

Traces within a Feature are sequential by design. Create a Trace branch only **after** the previous Trace's PR merged. The base then already contains the prior Trace's work. The Skeleton's branch is the first in the sequence.

```bash
# Fresh work — staged delivery (base = feature branch):
git checkout feature/<feature-number>-<feature-slug>
git pull --rebase origin feature/<feature-number>-<feature-slug>
git checkout -b trace/<trace-number>-<trace-slug>

# Fresh work — trunk delivery (base = main):
git checkout main
git pull --rebase origin main
git checkout -b trace/<trace-number>-<trace-slug>

# Resumed work (branch already exists):
git checkout trace/<trace-number>-<trace-slug>
git rebase origin/<base-branch>
```

Resolve all conflicts before you continue.

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
| `trace/*` | `staged` | parent `feature/*` |
| `trace/*` | `trunk` | `main` |
| `feature/*` | `staged` | `main` |
| `hotfix/*` | any | `main` |
| `task/*` (legacy) | any | parent `feature/*` |
| anything else | — | ask the user |

## Worktree decision (cross-feature parallelism)

When a skill spawns multiple sub-agents that edit code (`wtf.loop`, `wtf.verify-trace` Full Feature mode), set Agent `isolation: "worktree"`. Each sub-agent then has its own copy of the repo.

Worktrees isolate **Features**, not Traces of one Feature. Traces serialize on the same branch line, so a worktree per Trace buys nothing. One worktree runs one Feature's Trace sequence.

The worktree branches from the Trace's base branch at spawn time — the feature branch in `staged` delivery, `main` in `trunk` delivery. Spawn only after all prior PRs in the same conflict-graph sub-phase have merged.

Before work starts, each sub-agent must run `git pull --rebase origin <base_branch>`.

See `./conflict-graph.md` for how to schedule worktrees so two parallel agents never touch the same files.

## Print the branch name

After setup, always print the active branch name. The user then knows where work happens.
