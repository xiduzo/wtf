---
name: wtf.health
description: This skill should be used when a developer or lead wants a project status overview — for example "what's the state of the project", "show me what's blocked", "project health check", "what tasks are stuck", "standup summary", "how many issues are unverified", "what's left in this epic", "show me what needs attention", "what's been implemented but not verified", or "what's blocking the release". Scans all open WTF issues and produces a triage-ready health report with actionable next steps.
---

# Health

Project health dashboard. Core value: gives a full-stack view of open WTF issues in under a minute — surfaces what is blocked, what is stale, and what the clear next action is for each problem found.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

### 1. Choose the scope

Call `AskUserQuestion` with:

- `question`: "What scope do you want to check?"
- `header`: "Scope"
- `options`: `[{label: "Full project", description: "All open Epics, Features, and Tasks"}, {label: "One Epic", description: "All work under a specific Epic"}, {label: "One Feature", description: "All Tasks under a specific Feature"}]`

For Epic or Feature scope, prompt for the issue number with options pre-filled from recent open issues.

### 2. Fetch all open issues

Run in parallel:

```bash
gh issue list --label "epic"    --state open --json number,title,labels,updatedAt --limit 50
gh issue list --label "feature" --state open --json number,title,labels,updatedAt --limit 100
gh issue list --label "task"    --state open --json number,title,labels,updatedAt --limit 200
gh issue list --label "bug"     --state open --json number,title,labels,updatedAt --limit 50
```

Also fetch open PRs to detect tasks with an open PR but no `verified` label:

```bash
gh pr list --state open --json number,title,headRefName,body --limit 50
```

### 3. Classify issues into health categories

For each issue, check its labels against the expected lifecycle:

**Epics:**
| Signal | Category |
|--------|----------|
| No child Features linked | ⚠️ Epic has no Features |
| All child Features closed | ✅ Epic complete — needs `retro` |

**Features:**
| Signal | Category |
|--------|----------|
| No `designed` label, no child Tasks | ⚠️ Feature not designed, no tasks |
| Has child Tasks, none `implemented` | 🔵 In progress |
| All child Tasks `verified`, Feature still open | ✅ Feature complete — needs Feature PR |

**Tasks:**
| Signal | Category |
|--------|----------|
| No `designed` label | ⚠️ Not designed — blocked before implement |
| `designed` but not `implemented` for > 7 days | 🕐 Stale — may be forgotten |
| `implemented` but not `verified` | ⏳ Waiting for QA |
| `verified` but no open or merged PR | ⏳ Waiting for PR |
| Has open PR but not `verified` | ⚠️ PR open without QA sign-off |
| `implemented` + `verified` + PR merged | ✅ Done |

**Bugs:**
| Signal | Category |
|--------|----------|
| Open, no task linked in body | ⚠️ Bug not linked to a task |
| Open > 14 days | 🕐 Stale bug |

Staleness threshold for tasks is 7 days since last update; for bugs, 14 days. These are heuristics — flag but do not auto-close anything.

### 4. Render the health report

```
Project Health — <scope> — <YYYY-MM-DD>
────────────────────────────────────────────────────────

Epics:    [n open]
Features: [n open]
Tasks:    [n open]  ([n] implemented, [n] verified, [n] stale)
Bugs:     [n open]  ([n] stale)

────────────────────────────────────────────────────────

⚠️  Needs attention ([n])

  [#n] Task: <title>
       Label gap: designed — not yet implemented (stale [n days])
       Next: run implement-task

  [#n] Task: <title>
       implemented — not verified
       Next: run verify-task

  [#n] Feature: <title>
       All tasks verified — Feature PR not opened
       Next: run create-pr targeting main

  [#n] Bug: <title>
       Open [n days], no linked task
       Next: run write-task to create a fix task

🕐  Stale ([n])

  [#n] Task: <title>
       Last updated [n days ago] — no activity since designed

────────────────────────────────────────────────────────

✅  Clean
  [n] tasks verified and merged
  [n] features closed
```

If everything is clean, print: "All open issues are in a healthy state. Nothing needs attention."

### 5. Offer to act on findings

If findings exist, call `AskUserQuestion` with:

- `question`: "Would you like to act on any of these findings now?"
- `header`: "Next action"
- `options`: one option per ⚠️ finding (e.g. `{label: "Verify Task #42", description: "Run verify-task"}`), plus `{label: "Done — just the report", description: "Exit"}`.

Route each selection to the appropriate skill with the issue number pre-loaded as context.
