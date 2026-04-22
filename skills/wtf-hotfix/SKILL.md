---
name: wtf.hotfix
description: This skill should be used when something is broken in production and needs an immediate fix that bypasses the normal Epic→Feature→Task planning flow — for example "production is down", "hotfix needed", "critical bug in prod", "emergency fix for #X", "patch this now", "security patch", or "this can't wait for the normal flow". Cuts a hotfix branch directly from main, implements a narrow fix with TDD, and opens a PR back to main. Not for large or unclear changes — use write-epic + write-task for those.
---

# Hotfix

Emergency fix path that bypasses the normal Epic→Feature→Task hierarchy. Core value: gets a narrow, well-understood fix into production as fast as possible while still maintaining a test, a commit trail, and a PR review.

## When to use vs. when not to use

**Use when:** something is broken in production, the fix is narrow and well-understood, and waiting for the full workflow is not acceptable.

**Do not use when:** the fix is large, the scope is unclear, or the change needs design review — use `write-epic` + `write-task` instead.

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

If no issue exists, create one now via a streamlined `report-bug` (steps 1–3 and 6–8 only — skip Gherkin derivation and DDD mapping, just file the issue fast).

### 2. Confirm hotfix scope

A hotfix must be:
- **Narrow**: touches the minimum files necessary to fix the specific breakage
- **Non-breaking**: no API contract changes, no schema migrations unless strictly required
- **Testable**: at least one automated test can verify the fix

Call `AskUserQuestion` with:

- `question`: "Does this fix meet the hotfix criteria? (narrow, non-breaking, testable)"
- `header`: "Scope check"
- `options`: `[{label: "Yes — proceed", description: "Create the hotfix branch and start the fix"}, {label: "Not sure — it may be larger than that", description: "Use the normal workflow instead"}]`

If "Not sure" → exit. Suggest `write-task` as the next step.

### 3. Load the technical steering document

Use the Read tool to attempt reading `docs/steering/TECH.md`. If it exists, apply its stack constraints, coding patterns, and test commands silently throughout this session.

### 4. Set up the hotfix branch

```bash
git fetch origin
git checkout main
git pull --rebase origin main
git checkout -b hotfix/<bug-number>-<slug>
git push -u origin hotfix/<bug-number>-<slug>
```

Where `<slug>` is a 2–4 word kebab-case description of the fix (e.g. `null-check-payment-id`). Print the branch name.

### 5. Explore the codebase

Use the Agent tool to find:

- The specific file(s) responsible for the breakage
- Existing tests covering the broken behavior (or noting their absence)
- Contracts or interfaces the fix must preserve without changing

Do not expand scope based on what you find. If the fix turns out to be larger than expected, surface it as a gate in step 6.

### 6. Scope gate

If exploration reveals the fix touches more than 3–4 files, requires changing an API contract, or requires a schema migration, surface it before writing any code:

Call `AskUserQuestion` with:

- `question`: "This fix is larger than a typical hotfix — [describe what was found]. How do you want to proceed?"
- `header`: "Scope gate"
- `options`: `[{label: "Proceed as hotfix", description: "Accept the larger scope — I understand the risk"}, {label: "Switch to normal flow", description: "Exit and use write-epic + write-task instead"}]`

### 7. Implement the fix

Write the failing test first (one test per broken behavior), then implement the minimum fix to make it pass. Follow the same TDD cycle as `implement-task` steps 1–4.

Run the full test suite after the fix:

```bash
# Run project test command (from TECH.md or package.json scripts)
```

If unrelated tests fail: do not block — record them in the PR body as pre-existing failures.

Commit:

```bash
git add <changed files>
git commit -m "fix(<scope>): <description>

Closes: #<bug_number>"
```

### 8. Open the PR

Write the body to a temp file, then create the PR targeting `main`:

```bash
# Ensure the hotfix label exists
gh label create hotfix --color e11d48 --description "Emergency fix targeting main directly" 2>/dev/null || true

gh pr create \
  --title "fix(<scope>): <description>" \
  --body-file /tmp/wtf-hotfix-<bug_number>-body.md \
  --base main \
  --label "hotfix"
```

PR body must include:

- **Related**: one `Closes #<n>` line per closed issue — never comma-separated. Always include `Closes #<bug_number>`. Add additional lines for any other issues this PR resolves. Example:
  ```
  Closes #42
  Closes #15
  ```
- **Impact**: what was broken and who was affected
- **Root cause**: what caused it
- **Fix**: what was changed and why it's safe
- **Risk**: what could be affected by this change
- **Pre-existing failures** (if any): unrelated tests that were already failing before this change

Print the PR URL.

### 9. Offer backport

If the project uses release branches, offer to backport:

Call `AskUserQuestion` with:

- `question`: "Should this fix be backported to a release branch?"
- `header`: "Backport"
- `options` pre-filled from `git branch -r | grep -iE 'release|v[0-9]'` (limit 5), plus `{label: "No backport needed", description: "main only"}`.

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
