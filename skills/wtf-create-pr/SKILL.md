---
name: wtf:create-pr
description: This skill should be used when a developer wants to open a pull request for a completed task branch — for example "create a PR", "open a pull request", "submit this for review", "make a PR for task #42", "push this up for review", or "create PR from current branch". Reads the Task + Feature + Epic hierarchy to write a meaningful PR description. Handles branches with or without a linked WTF task issue.
---

# Create PR

Open a pull request for a completed task branch. Core value: reads the full spec hierarchy (Task + Feature + Epic) and the branch diff to write a PR description that explains _why_ the change exists — not just what it does.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf:verify-task` or another skill that already ran gh-setup this session.

### 1. Confirm the branch

Check the current branch and verify it is not `main`:

```bash
git branch --show-current
```

If on `main`, ask: "Which branch should I open a PR from?"

Check whether a PR already exists for this branch:

```bash
gh pr list --head <branch_name> --state open
```

If an open PR already exists, print its URL and call `AskUserQuestion` with:

- `question`: "A PR already exists for this branch. Would you like me to update its description instead?"
- `header`: "Existing PR"
- `options`: `[{label: "Update description", description: "Edit the existing PR's description"}, {label: "Open a new one", description: "Create a new PR anyway"}]`

- **Update description** → skip to step 5, targeting the existing PR for update via `gh pr edit <pr_number>`.
- **Open a new one** → continue.

### 2. Identify the Task (if any)

Try to extract a task number from the branch name (e.g. `task/42-date-range-filter` → `#42`).

If found, call `AskUserQuestion` with `question: "I found Task #<n> linked to this branch. Is that the right task?"`, `header: "Linked task"`, and `options: [{label: "Yes, that's correct", description: "Use Task #<n>"}, {label: "No, use a different task", description: "I'll provide the correct issue number"}]`.

If not found or the user says no, call `AskUserQuestion` with `question: "Is there a Task issue linked to this work?"`, `header: "Linked task"`, and `options: [{label: "No linked task", description: "Proceed without a task link"}, {label: "Yes — I'll provide the number", description: "Enter the task issue number"}]`.

### 3. Lifecycle check (if Task linked)

If a Task issue is known, check its labels:

```bash
gh issue view <task_number> --json labels --jq '.labels[].name'
```

If the `verified` label is **absent**, warn the user that the task hasn't been verified yet and that the recommended flow is: **write-task → design-task → implement-task → verify-task → create-pr**. Then call `AskUserQuestion` with:

- `question`: "This task hasn't been verified yet. How would you like to proceed?"
- `header`: "Verify first?"
- `options`: `[{label: "Verify first", description: "Run wtf:verify-task before opening the PR (default)"}, {label: "Open PR anyway", description: "Skip verification and open the PR now"}]`

- **Verify first** → follow the `wtf:verify-task` process, passing the Task number in as context.
- **Open PR anyway** → proceed.

If no Task is linked, skip this step.

### 4. Fetch the spec hierarchy

**If a Task issue is known**, fetch the full hierarchy:

```bash
gh issue view <task_number>    # Gherkin, Contracts, DoD, Test Mapping — also yields feature and epic numbers
# Extract feature and epic numbers, then in parallel:
gh issue view <feature_number> # ACs, user stories
gh issue view <epic_number>    # Goal, context, constraints
```

**If no Task issue**, skip hierarchy fetch. The PR will be written from diff context alone (step 5).

### 5. Inspect the diff

Collect the branch diff against `main`:

```bash
git log main..HEAD --oneline
git diff main...HEAD --stat
```

Use this to understand the scope of the change: which files changed, how many commits, what the commit messages say. Do not read full file diffs; use `--stat` output only unless a specific commit message is ambiguous and cannot be resolved without the diff.

### 6. Draft the PR

**Title generation:** Spawn a subagent using the `claude-haiku-4-5` model to generate a PR title following **Conventional Commits 1.0.0**. Pass in the task title (if available), the commit log, and whether this is a breaking change. If the subagent returns nothing usable, generate the title directly using the same rules below. Rules:

- Format: `<type>[optional scope]: <description>`
- Types: `feat` (new feature), `fix` (bug fix), `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`
- Scope: optional noun in parentheses describing the codebase section, e.g. `feat(auth): …`
- Breaking change: append `!` after type/scope, e.g. `feat!: …`
- Description: lowercase, imperative mood, no period at end
- Under 72 characters total
- Examples: `feat(search): add date range filter`, `fix(payments): prevent double settlement`, `refactor(orders): extract fulfilment service`

**Body:** Use the structure from @.github/pull_request_template.md. Fill in all sections:

- **Summary**: derived from the Task's Intent + Functional Description (or commit messages if no Task). Explain the _why_.
- **Changes**: grouped logical summary of `git diff --stat` output — not a file list.
- **Test plan**: if a Task exists, derive checklist items from the Gherkin scenario names. If no Task, derive from changed files and commit messages. At minimum one item per observable behavior changed.
- **Related**: `Closes #<task_number>` if a Task exists; omit section if no linked issue.

### 7. Review with user

Show the draft title and body. Then call `AskUserQuestion` with `question: "Does this look right?"`, `header: "Review"`, and `options: [{label: "Looks good — create the PR", description: "Proceed with PR creation"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed.

### 8. Create the PR

Write the body to a temp file, then create the PR targeting `main`:

```bash
gh pr create \
  --title "<title>" \
  --body-file /tmp/pr-body.md \
  --base main
```

Print the PR URL.

### 9. Update the Task issue (if linked)

If a Task issue is linked, post a comment linking the PR:

```bash
gh issue comment <task_number> --body "PR opened: <pr_url>"
```

### 10. Offer next steps

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Request a review", description: "Add reviewers to this PR now (default)"}, {label: "Done", description: "Exit — no further action"}]`

- **Request a review** → call `AskUserQuestion` with `question: "Who should review this?"`, `header: "Reviewer"`, and `options` pre-filled with team member usernames inferred from recent git log authors or the repository's CODEOWNERS file. Then:
  ```bash
  gh pr edit <pr_number> --add-reviewer <username>
  ```
  For multiple reviewers, pass a comma-separated list: `--add-reviewer user1,user2`.
  Print the PR URL.
- **Done** → exit.
