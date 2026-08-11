---
name: wtf.health
description: This skill should be used when a developer or lead wants a project status overview — for example "what's the state of the project", "show me what's blocked", "project health check", "what traces are stuck", "standup summary", "how many issues are unverified", "what's left in this epic", "show me what needs attention", "what's been implemented but not verified", or "what's blocking the release". Scans all open WTF issues — Traces plus legacy Tasks — and produces a triage-ready health report with actionable next steps.
---

# Health

Project health dashboard.

This skill gives a full-stack view of open WTF issues in under a minute.
It reports what is blocked, what is stale, and the clear next action for each problem found.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`.
Stop if `gh` is not installed or not authenticated.

### 1. Choose the scope

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What scope do you want to check?"
- header: "Scope"
- options:
  - **Full project** → all open Epics, Features, and Traces
  - **One Epic** → all work under a specific Epic
  - **One Feature** → all Traces under a specific Feature

For Epic or Feature scope, prompt for the issue number with options pre-filled from recent open issues.

### 2. Fetch all open issues

Run in parallel:

```bash
# Resolve $WTF_CLASS once — see ../references/issue-classification.md.
# labels mode → query by kind label; types mode → query by native issue type.
# The Trace query also matches legacy Task issues (Legacy Task reads in
# issue-classification.md) so migrated repos stay visible.
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search 'type:"Epic" state:open'    --json number,title,labels,updatedAt --limit 50
  gh issue list --search 'type:"Feature" state:open' --json number,title,body,labels,updatedAt --limit 100
  gh issue list --search 'state:open (type:"Trace" OR type:"Task")' --json number,title,labels,updatedAt --limit 200
  gh issue list --search 'type:"Bug" state:open'     --json number,title,labels,updatedAt --limit 50
else
  gh issue list --label "epic"       --state open --json number,title,labels,updatedAt --limit 50
  gh issue list --label "feature"    --state open --json number,title,body,labels,updatedAt --limit 100
  gh issue list --label "trace,task" --state open --json number,title,labels,updatedAt --limit 200
  gh issue list --label "bug"        --state open --json number,title,labels,updatedAt --limit 50
fi
```

The Feature query requests `body` because step 3 reads each Feature's User Stories and Trace Plan.

Also fetch open PRs to detect traces with an open PR but no `verified` label:

```bash
gh pr list --state open --json number,title,headRefName,body --limit 50
```

### 3. Classify issues into health categories

For each issue, check its labels against the expected lifecycle:

**Epics:**
| Signal | Category |
|--------|----------|
| No child Features linked | ⚠️ Epic has no Features |
| All child Features closed | ✅ Epic complete — needs `wtf.retro` |

**Features:**
| Signal | Category |
|--------|----------|
| No `designed` label, no child Traces | ⚠️ Feature not designed, no traces |
| No Skeleton entry — Trace Plan absent, or item 1 is not the Skeleton | ⚠️ No Skeleton — the Spine is unproven |
| Partition gap — a story scenario in the Feature body that no Trace Plan entry claims | ⚠️ Unclaimed scenarios — re-aim the Trace Plan |
| Has child Traces, none `implemented` | 🔵 In progress |
| All child Traces `verified`, Feature still open | ✅ Feature complete — needs Feature PR |

Read each Feature body's User Stories and Trace Plan for the Skeleton and partition checks. Compare the scenario names per story against the Scenario Claims in the Trace Plan entries. Do not check the synced scenario copies in Trace bodies — `wtf.verify-trace` owns drift detection.

**Traces (legacy Task issues share this table — mark each such finding "legacy Task"):**
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
| Open, no Trace linked in body | ⚠️ Bug not linked to a Trace |
| Open > 14 days | 🕐 Stale bug |

Staleness threshold for traces is 7 days since last update.
For bugs, it is 14 days.
These are heuristics — flag but do not auto-close anything.

### 4. Render the health report

```
Project Health — <scope> — <YYYY-MM-DD>
────────────────────────────────────────────────────────

Epics:    [n open]
Features: [n open]
Traces:   [n open]  ([n] implemented, [n] verified, [n] stale, [n] legacy Tasks)
Bugs:     [n open]  ([n] stale)

────────────────────────────────────────────────────────

⚠️  Needs attention ([n])

  [#n] Trace: <title>
       Label gap: designed — not yet implemented (stale [n days])
       Next: run implement-trace

  [#n] Trace: <title>
       implemented — not verified
       Next: run verify-trace

  [#n] Feature: <title>
       Partition gap: scenario "<name>" claimed by no Trace Plan entry
       Next: run refine to re-aim the Trace Plan

  [#n] Feature: <title>
       All traces verified — Feature PR not opened
       Next: run create-pr targeting main

  [#n] Bug: <title>
       Open [n days], no linked Trace
       Next: run write-trace to create a fix Trace

🕐  Stale ([n])

  [#n] Trace: <title>
       Last updated [n days ago] — no activity since designed

────────────────────────────────────────────────────────

✅  Clean
  [n] traces verified and merged
  [n] features closed
```

If everything is clean, print: "All open issues are in a healthy state. Nothing needs attention."

### 5. Offer to act on findings

If findings exist, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Would you like to act on any of these findings now?"
- header: "Next action"
- options:
  - One option per ⚠️ finding (e.g. **Verify Trace #42** → run `verify-trace`)
  - **Done — just the report** → exit

Route each selection to the appropriate skill with the issue number pre-loaded as context.
