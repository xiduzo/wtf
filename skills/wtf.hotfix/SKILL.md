---
name: wtf.hotfix
description: This skill should be used when something is broken in production and needs an immediate fix that bypasses the normal Epic→Feature→Task planning flow — for example "production is down", "hotfix needed", "critical bug in prod", "emergency fix for #X", "patch this now", "security patch", or "this can't wait for the normal flow". Cuts a hotfix branch directly from main, implements a narrow fix with TDD, and opens a PR back to main. Not for large or unclear changes — use write-epic + write-task for those.
---

# Hotfix

Emergency fix path that bypasses the normal Epic→Feature→Task hierarchy. Core value: gets a narrow, well-understood fix into production as fast as possible while still maintaining a test, a commit trail, and a PR review.

## When to use vs. when not to use

**Use when:** something is broken in production, the fix is narrow and well-understood, and waiting for the full workflow is not acceptable.

**Do not use when:** the fix is large, the scope is unclear, or the change needs design review — use `wtf.write-epic` + `wtf.write-task` instead.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

### 1. Identify the bug

If a bug issue number was passed in, fetch it:

```bash
gh issue view <bug_number>
```

If no issue exists yet, ask in a single message:

- "What is broken? (one sentence)"
- "What is the user impact? (e.g. data loss, revenue impact, all users blocked, subset of users)"
- "Is there an existing bug issue, or should I create one?"

If no issue exists, follow the **Fast path** section of `wtf.report-bug` (Gherkin derivation and Ubiquitous Language mapping are skipped — the goal is to file the issue fast).

### 2. Confirm hotfix scope

A hotfix must be:
- **Narrow**: touches the minimum files necessary to fix the specific breakage
- **Non-breaking**: no API contract changes, no schema migrations unless strictly required
- **Testable**: at least one automated test can verify the fix

Apply `../references/questioning-style.md` for every question in this skill.

Ask "Does this fix meet the hotfix criteria? (narrow, non-breaking, testable)" — header `Scope check`:

- **Yes — proceed** → create the hotfix branch and start the fix
- **Not sure — it may be larger than that** → use the normal workflow instead

If "Not sure" → exit. Suggest `wtf.write-task` as the next step.

### 3. Load the technical steering document

Load `docs/steering/TECH.md` per the **best-effort consumer-side load** in `../references/steering-doc-process.md`. If present, apply its stack constraints, coding patterns, and test commands silently throughout this session.

### 4. Set up the hotfix branch

Set up the hotfix branch per `../references/branch-setup.md` ("Hotfix branch — direct from main" section). Print the branch name.

### 5. Explore the codebase

Use the Agent tool to find:

- The specific file(s) responsible for the breakage
- Existing tests covering the broken behavior (or noting their absence)
- Contracts or interfaces the fix must preserve without changing

Do not expand scope based on what you find. If the fix turns out to be larger than expected, surface it as a gate in step 6.

### 6. Scope gate

If exploration reveals the fix touches more than 3–4 files, requires changing an API contract, or requires a schema migration, surface it before writing any code:

Ask "This fix is larger than a typical hotfix — [describe what was found]. How do you want to proceed?" — header `Scope gate`:

- **Proceed as hotfix** → accept the larger scope; I understand the risk
- **Switch to normal flow** → exit and use `write-epic` + `write-task` instead

### 7. Implement the fix

Write the failing test first (one test per broken behavior), then implement the minimum fix to make it pass. Follow the TDD cycle from `wtf.implement-task` step 8.

Run the full test suite after the fix:

```bash
# Run project test command (from TECH.md or package.json scripts)
```

If unrelated tests fail: do not block — record them in the PR body as pre-existing failures.

Commit per `../references/commit-conventions.md`. The commit message uses a `Bug:` trailer; the `Closes #<n>` keyword lives in the PR body, not the commit:

```bash
git add <changed files>
git commit -m "fix(<scope>): <description>

Bug: #<bug_number>"
```

### 8. Open the PR

Write the body to a temp file, then create the PR targeting `main`:

```bash
# Ensure the hotfix label exists
gh label create hotfix --color e11d48 --description "Emergency fix targeting main directly" 2>/dev/null || true

gh pr create \
  --title "fix(<scope>): <description>" \
  --body-file /tmp/wtf.hotfix-<bug_number>-body.md \
  --base main \
  --label "hotfix"
```

PR body must include:

- **Related**: closure keywords per `../references/commit-conventions.md` — one `Closes #<n>` per line, always include `Closes #<bug_number>`.
- **Impact**: what was broken and who was affected.
- **Root cause**: what caused it.
- **Fix**: what was changed and why it's safe.
- **Risk**: what could be affected by this change.
- **Pre-existing failures** (if any): unrelated tests that were already failing before this change.

Print the PR URL.

### 9. Offer backport

If the project uses release branches, offer to backport:

Ask "Should this fix be backported to a release branch?" — header `Backport`:

- Candidates from `git branch -r | grep -iE 'release|v[0-9]'` (limit 5)
- **No backport needed** — main only

If a backport branch is selected — wait until the hotfix PR merges, then:

```bash
git checkout <release-branch>
git pull --rebase origin <release-branch>
git cherry-pick <hotfix-commit-sha>
git push origin <release-branch>
```

### 10. Report status

Print:

```
Hotfix
──────────────────────────────────
Branch:   hotfix/<slug>
PR:       <url>
Closes:   #<bug_number>
Target:   main
Backport: <branch> or —
```
