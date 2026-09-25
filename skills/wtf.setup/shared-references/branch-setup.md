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

## Resolve the stack base

Each Feature delivers through **one linear stack** of Trace PRs. A Trace never waits for a merge. It branches off the top of its Feature's stack as soon as the code below it exists. A human reviewing is not a reason for the next Trace to idle.

The **stack tip** is the head branch of the highest open Trace PR of the Feature. When no Trace PR of the Feature is open, the tip is the **root**: the feature branch (`staged`) or `main` (`trunk`). The Skeleton is always first and always alone. It lays the Spine, so every later Trace of the Feature depends on it.

The **stack base** of a Trace is the stack tip at the time the Trace branches or joins. It comes from the open PRs on GitHub, never from the git upstream of the current branch. `Builds on` does not select the base. The tip contains every Trace below it, so it carries the code of every Builds-on Trace that joined.

```bash
# Inputs: TRACE_NUMBER; FEATURE_NUMBER (per ./spec-hierarchy.md); WTF_DELIVERY (resolved above).
FEATURE_BODY=$(python3 .wtf/gh-body.py read "$FEATURE_NUMBER")
# The Traces of this Feature: the first #<n> on each Trace Plan item.
PLAN_RE=$(sed -n '/^## Trace Plan/,/^## /p' "$FEATURE_BODY" | grep -E '^[0-9]+\.' \
  | awk 'match($0,/#[0-9]+/){print substr($0,RSTART+1,RLENGTH-1)}' | paste -sd'|' -)

case "$WTF_DELIVERY" in staged) STACK_BASE="feature/<feature-number>-<feature-slug>" ;; *) STACK_BASE=main ;; esac
# Walk up the open Trace PRs of this Feature, from the root to the tip.
while :; do
  up=$(gh pr list --state open --base "$STACK_BASE" --json headRefName \
    --jq "[.[].headRefName | select(test(\"^trace/($PLAN_RE)-\"))] | join(\" \")")
  set -- $up
  [ $# -eq 0 ] && break
  [ $# -gt 1 ] && { echo "forked stack on $STACK_BASE: $up"; exit 1; }
  case "$1" in "trace/$TRACE_NUMBER-"*) break ;; esac   # this Trace already joined: keep the base below it
  STACK_BASE="$1"
done
echo "stack base: $STACK_BASE"
```

Rules:

- A Trace with an open PR has **joined** the stack. A Trace with a branch and no PR has not joined. Nothing stacks on it.
- A Trace can start only when every Builds-on Trace has joined or merged. A Builds-on Trace with only a branch has not joined. Open its PR first.
- A merged Trace has left the stack. GitHub retargets the PR above it to the root, so the walk no longer finds it.
- The Skeleton opens the stack. No Trace PR of the Feature is open yet, so the walk stops at the root.
- Two open Trace PRs on one base mean a forked stack from an older run. Stop and tell the user. Do not guess the order.
- An empty `PLAN_RE` means the Trace Plan links no Trace issues. Stop. Link the issues in the plan first.
- The PR base always equals the stack base.

### Join the stack

A Trace joins the stack when its PR opens. `wtf.loop` sets the join order: trace sub-phase first, then Trace Plan order inside a sub-phase.

The tip can move while a Trace builds: a sibling can join first. So resolve the stack base again just before the PR opens. If the branch does not contain that base, rebase onto it:

```bash
git fetch origin
git merge-base --is-ancestor "origin/$STACK_BASE" HEAD || git rebase "origin/$STACK_BASE"
# Run the project's test command. Then push:
git push --force-with-lease -u origin HEAD
```

Siblings share no files, so the rebase is clean. The test run proves that the combined code works. Then open the PR against the stack base and link it into the native stack. For a Trace that built alone, the base did not move and the rebase does nothing.

## Trace branch — create or resume

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

**Every merge must delete the head branch.** GitHub retargets an open PR to its parent's base when the parent merges *and the parent's head branch is deleted*. That is what unwinds the stack with no manual work: when `trace/10` merges into `feature/5` and its branch is deleted, every PR based on `trace/10` retargets to `feature/5` on its own. Each retargeted diff then shows only that Trace's own commits — but only because the merge commit keeps `trace/10`'s commits as ancestors of `feature/5`. A squash rewrites them into one new commit, and the PR above would show `trace/10`'s changes again until someone runs `git rebase --onto`.

```bash
gh pr merge <pr_number> --merge --delete-branch
```

Never squash a Trace PR: squashing rewrites the commits the PRs above it were cut from. Feature-to-main PRs may squash — nothing stacks on them.

Turn on **Settings → General → Automatically delete head branches** so a human who merges through the web UI does not strand the stack. `wtf.setup` checks this setting.

A stacked PR can never merge before the PR it is based on. Merge bottom-up, in stack order.

### Native stacks

`wtf.setup` installs the `github/gh-stack` extension. After each stacked PR opens, link it into its native stack. Pass the PR numbers of the open Trace PRs of the Feature, bottom to top, up to this PR:

```bash
gh stack link <bottom-pr> <next-pr> ... <this-pr>   # bottom to top
```

`gh stack link` creates the stack when none exists and updates it when one does. PRs already in the stack stay in it. Pass PR numbers, not branch names: a branch name with no open PR makes the command open a PR on its own. A native stack renders the stack map on every PR, so the PR body must not say "stacked on #N".

The open Trace PRs of a Feature form one linear chain, so one native stack holds all of them. The walk in "Resolve the stack base" finds them in stack order.

Merge bottom-up with `gh pr merge --merge --delete-branch`. The head branch must be deleted. `gh stack merge` merges every layer up to a chosen PR in one atomic operation. It is for a human in an interactive terminal: pick the merge-commit method, never squash.

A stack locks the base branch of every PR in it. `gh pr edit --base` on a stacked PR fails with "part of a stack". Run `gh stack unstack <stack-number>` first, change the base, then link again. The stack number is shown in the GitHub stack UI on any PR of the stack. Unstack removes the grouping only. The PRs stay open. GitHub stacked PRs are a public preview feature.

**Fallback.** If `gh extension list` does not show `gh-stack` (the install failed or setup did not run), the retarget-on-delete mechanism above still applies. Skip the link and make the PR body say that the PR is stacked and name its base branch.

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
| `trace/*` — another Trace PR of the Feature is open | any | the stack tip: the head branch of the highest open Trace PR |
| `trace/*` — no other Trace PR of the Feature is open | `staged` | parent `feature/*` |
| `trace/*` — no other Trace PR of the Feature is open | `trunk` | `main` |
| `feature/*` | `staged` | `main` |
| `hotfix/*` | any | `main` |
| `task/*` (legacy) | any | parent `feature/*` |
| anything else | — | ask the user |

The PR base always equals the stack base the branch was cut from or rebased onto. Never open a Trace PR against a branch the Trace does not contain — the diff would carry the commits of another Trace.

## Worktree decision (cross-feature parallelism)

When a skill spawns multiple sub-agents that edit code at the same time, set Agent `isolation: "worktree"`. Each sub-agent then has its own copy of the repo. This applies to `wtf.loop` — Feature units, and sibling Traces of one Feature. `wtf.verify-trace` Full Feature mode verifies Traces one at a time in one checkout; it isolates only its legacy Task children.

Worktrees isolate anything that runs **at the same time**: separate Features, and sibling Traces of one Feature that share no files. Siblings build at the same time, but they join the one stack of the Feature one after the other. A Trace that shares files with an earlier Trace runs after it, on the same line, and needs no worktree of its own. Schedule siblings with `./conflict-graph.md` before spawning them.

The worktree branches from the stack tip at spawn time. Siblings that spawn together share that base. Spawn a Trace as soon as every Builds-on Trace has joined the stack or merged. Never wait for a merge. Only the conflict graph serializes siblings. Each sibling rebases onto the new tip when it joins — see "Join the stack".

Before work starts, each sub-agent must run `git pull --rebase origin <stack-base>`.

See `./conflict-graph.md` for how to schedule worktrees so two parallel agents never touch the same files.

## Print the branch name

After setup, always print the active branch name. The user then knows where work happens.
