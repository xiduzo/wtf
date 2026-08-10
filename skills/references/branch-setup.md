# Branch Setup

Shared trunk-based branch strategy and worktree policy for `wtf.implement-task`, `wtf.hotfix`, and `wtf.loop`.

## Branch hierarchy

```
main
└── feature/<feature-number>-<feature-slug>    (merges → main)
    └── task/<task-number>-<task-slug>          (merges → feature branch)

main
└── hotfix/<bug-number>-<slug>                  (merges → main)
```

## Slug generation

A slug is a 2–4 word kebab-case summary. Restrict it to `[a-z0-9-]`.

Spawn a subagent with model `claude-haiku-4-5-20251001`. Pass the title as input. Apply `./subagent-protocol.md` for the spawn. Do not use `AskUserQuestion` inside that subagent.

Examples: `date-range-filter`, `null-check-payment-id`.

## Feature branch — create or check out

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

## Task branch — create or resume

```bash
# Fresh work:
git checkout -b task/<task-number>-<task-slug>

# Resumed work (branch already exists):
git checkout task/<task-number>-<task-slug>
git rebase origin/feature/<feature-number>-<feature-slug>
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

| Current branch | PR base |
|---|---|
| `task/*` | parent `feature/*` |
| `feature/*` | `main` |
| `hotfix/*` | `main` |
| anything else | ask the user |

## Worktree decision (parallel runs)

When a skill spawns multiple sub-agents that edit code (`wtf.loop`, `wtf.verify-task` Full Feature mode), set Agent `isolation: "worktree"`. Each sub-agent then has its own copy of the repo.

The worktree branches from the **feature branch** at spawn time. Spawn only after all prior PRs in the same DAG sub-phase have merged.

Before work starts, each sub-agent must run `git pull --rebase origin <feature_branch>`.

See `./conflict-graph.md` for how to schedule worktrees so two parallel agents never touch the same files.

## Print the branch name

After setup, always print the active branch name. The user then knows where work happens.
