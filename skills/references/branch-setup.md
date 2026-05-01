# Branch Setup

Shared trunk-based branching strategy and worktree policy used by `wtf.implement-task`, `wtf.hotfix`, and `wtf.loop`.

## Branch hierarchy

```
main
└── feature/<feature-number>-<feature-slug>    (merges → main)
    └── task/<task-number>-<task-slug>          (merges → feature branch)

main
└── hotfix/<bug-number>-<slug>                  (merges → main)
```

## Slug generation

Slugs are 2–4 word kebab-case summaries restricted to `[a-z0-9-]`. Spawn a subagent using the `claude-haiku-4-5-20251001` model with the title as input — apply `./subagent-protocol.md` for the spawn (no `AskUserQuestion` inside). Examples: `date-range-filter`, `null-check-payment-id`.

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

Resolve any conflicts before proceeding.

## Hotfix branch — direct from main

```bash
git fetch origin
git checkout main
git pull --rebase origin main
git checkout -b hotfix/<bug-number>-<slug>
git push -u origin hotfix/<bug-number>-<slug>
```

Hotfix branches never depend on a feature branch — they target `main` directly.

## Base-branch policy (PR target)

| Current branch | PR base |
|---|---|
| `task/*` | parent `feature/*` |
| `feature/*` | `main` |
| `hotfix/*` | `main` |
| anything else | ask the user |

## Worktree decision (parallel runs)

When a skill spawns multiple sub-agents that touch code (`wtf.loop`, `wtf.verify-task` Full Feature mode), use Agent `isolation: "worktree"` so each sub-agent has its own copy of the repo. The worktree branches off the **feature branch** at spawn time — after all preceding PRs in the same DAG sub-phase have merged. Each sub-agent must `git pull --rebase origin <feature_branch>` before starting work.

See `./conflict-graph.md` for how to schedule worktrees so two parallel agents never touch the same files.

## Print the branch name

After setting up, always print the active branch name so the user knows where work is happening.
