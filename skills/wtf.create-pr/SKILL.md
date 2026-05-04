---
name: wtf.create-pr
description: This skill should be used when a developer wants to open a pull request for a completed task branch — for example "create a PR", "open a pull request", "submit this for review", "make a PR for task #42", "push this up for review", or "create PR from current branch". Reads the Task + Feature + Epic hierarchy to write a meaningful PR description. Handles branches with or without a linked WTF task issue.
---

# Create PR

Open a pull request for a completed task branch. Core value: reads the full spec hierarchy (Task + Feature + Epic) and the branch diff to write a PR description that explains _why_ the change exists — not just what it does.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.verify-task` or another skill that already ran gh-setup this session.

### 1. Confirm the branch

Check the current branch and verify it is not `main`:

```bash
git branch --show-current
```

If on `main`, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which branch should I open a PR from?"
- header: "Branch"
- options: from `git branch --list` (local branches)

Check whether a PR already exists for this branch:

```bash
gh pr list --head <branch_name> --state open
```

If an open PR already exists, print its URL and call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "A PR already exists for this branch. Would you like me to update its description instead?"
- header: "Existing PR"
- options:
  - **Update description** → skip to step 5, targeting the existing PR for update via `gh pr edit <pr_number>`
  - **Open a new one** → create a new PR anyway

### 2. Identify the Task (if any)

Try to extract a task number from the branch name (e.g. `task/42-date-range-filter` → `#42`).

If found, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "I found Task #<n> linked to this branch. Is that the right task?"
- header: "Linked task"
- options:
  - **Yes, that's correct** → use Task #<n>
  - **No, use a different task** → I'll provide the correct issue number

If not found or the user says no, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Is there a Task issue linked to this work?"
- header: "Linked task"
- options:
  - **No linked task** → proceed without a task link
  - **Yes — I'll provide the number** → enter the task issue number

### 3. Lifecycle check (if Task linked)

If no Task is linked, skip this step.

Apply the **absent-label gate** from `../references/lifecycle-labels.md` for the `verified` label on the Task — recommended skill `wtf.verify-task`, header `Verify first?`. On **Verify first** → follow `wtf.verify-task` passing the Task number as context. On **Open PR anyway** → proceed.

### 4. Fetch the spec hierarchy

**If a Task issue is known**, walk Task → Feature → Epic per `../references/spec-hierarchy.md` to extract Gherkin, Contracts, DoD, Test Mapping (Task) and ACs / Goal / constraints (Feature, Epic).

**If no Task issue**, skip hierarchy fetch. The PR will be written from diff context alone (step 5).

### 5. Inspect the diff

Determine the base branch using the same logic as step 8 (task/* → parent feature branch; feature/* → main), then collect the branch diff against that base:

```bash
git log <base_branch>..HEAD --oneline
git diff <base_branch>...HEAD --stat
```

This avoids including unrelated merged commits when the branch has a long history against main. Use `--stat` output only unless a specific commit message is ambiguous and cannot be resolved without the diff.

### 6. Draft the PR

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model — apply `../references/subagent-protocol.md` for the spawn — to generate a PR title per `../references/commit-conventions.md`. Pass in the task title (if available), the commit log, and whether this is a breaking change. If the subagent returns nothing usable, generate the title directly following the same rules. Examples: `feat(search): add date range filter`, `fix(payments): prevent double settlement`, `refactor(orders): extract fulfilment service`.

**Body:** Load the PR template per `../references/issue-template-loading.md` (verify `.github/pull_request_template.md` exists, halt-or-setup if missing). Fill in all sections:

- **Summary**: derived from the Task's Intent + Functional Description (or commit messages if no Task). Explain the _why_.
- **Changes**: grouped logical summary of `git diff --stat` output — not a file list.
- **Test plan**: if a Task exists, derive checklist items from the Gherkin scenario names. If no Task, derive from changed files and commit messages. At minimum one item per observable behavior changed.
- **Related**: closure keywords per `../references/commit-conventions.md`. If a Task exists, include `Closes #<task_number>`. If the PR also closes the parent Feature (all sibling tasks already merged), add `Closes #<feature_number>` on its own line.

### 7. Review with user

Show the draft title and body. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this look right?"
- header: "Review"
- options:
  - **Looks good — create the PR** → proceed with PR creation
  - **I have changes** → adjust first

Apply edits, then proceed.

### 8. Create the PR

Determine the base branch from the current branch name:

- `task/*` branch → target the parent feature branch (`feature/<feature-number>-<feature-slug>`)
- `feature/*` branch → target `main`
- Other → call `AskUserQuestion` (per `../references/questioning-style.md`):
  - question: "What branch should this PR target?"
  - header: "Base branch"
  - options: from `git branch -r`

Write the body to a temp file, then create the PR:

```bash
# Derive a unique suffix from the branch name (fallback to timestamp):
SUFFIX=$(git rev-parse --abbrev-ref HEAD | tr '/' '-' || date +%s)

# task branch:
gh pr create \
  --title "<title>" \
  --body-file /tmp/wtf.create-pr-${SUFFIX}-body.md \
  --base feature/<feature-number>-<feature-slug>

# feature branch:
gh pr create \
  --title "<title>" \
  --body-file /tmp/wtf.create-pr-${SUFFIX}-body.md \
  --base main
```

Print the PR URL.

### 9. Update the Task issue (if linked)

If a Task issue is linked, post a comment linking the PR:

```bash
gh issue comment <task_number> --body "PR opened: <pr_url>"
```

### 10. Offer next steps

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Request a review** → add reviewers to this PR now (default)
  - **Done** → exit, no further action

On **Request a review** → call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Who should review this?"
- header: "Reviewer"
- options: from team member usernames inferred from recent `git log` authors or the repository's CODEOWNERS file

Then:
  ```bash
  gh pr edit <pr_number> --add-reviewer <username>
  ```
  For multiple reviewers, pass a comma-separated list: `--add-reviewer user1,user2`.
  Print the PR URL.
- **Done** → exit.
