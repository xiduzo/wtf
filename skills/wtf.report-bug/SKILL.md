---
name: wtf.report-bug
description: This skill should be used when a developer or QA engineer wants to report a bug, create a bug ticket, document a test failure, log a defect, file an issue found during a QA session, or report something that is broken — for example "report a bug", "create a bug ticket", "I found a defect", "something is broken in task #X", or "document this test failure". Files a structured GitHub Bug issue that links the originating Task and Feature, maps failing Gherkin scenarios as reproducible test evidence, and fills every section of the BUG template.
---

# Report Bug

File a structured Bug issue from a QA finding. Core value: the Gherkin scenario that failed becomes the reproducible test evidence, and the originating Task and Feature are linked automatically so nothing loses its context.

## Fast path (for wtf.hotfix)

When invoked from `wtf.hotfix`, skip the Gherkin-derivation and Ubiquitous-Language mapping work — the goal is to file the issue fast so the fix can start. Run only:

- Step 0 — GitHub CLI setup (skip if already confirmed this session).
- Step 1 — Identify the source (one-sentence bug, impact, optional task link).
- Step 3 — Gather bug details, but only `a. Observed behavior`, `b. Expected behavior`, and `c. Reproduction steps`. Skip contract violation / regression risk / suggested fix questions — the hotfix will uncover those.
- Step 6 — Draft the Bug report with only the sections the fast path produced (leave Contracts Violated, Regression Risk, Suggested Fix blank or marked "Fast path — to be captured during hotfix").
- Step 7 — Review briefly (or skip if the caller signalled non-interactive).
- Step 8 — Create the issue.

Return the bug issue number to the caller. Do not run the offer-next-steps prompt in step 9.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.verify-task` or another skill that already ran gh-setup this session.

### 1. Identify the source

**If called from `wtf.verify-task`:** the task number and failing scenario(s) are already in context — skip to step 2. Do not ask the questions below.

**If invoked directly:**

Ask in a single message:

- "What is the bug? (one sentence)"
- "Which Task does this trace back to? (issue number, or 'unknown')"

If a task number is known, fetch the Task first, extract the Feature number from its Context section, then fetch the Feature:

```bash
gh issue view <task_number>    # Gherkin, Contracts, ACs, DoD — also yields feature number
# Extract feature number, then:
gh issue view <feature_number> # ACs, user stories for expected behavior context
```

### 2. Identify the failing scenario(s)

If the Task has Gherkin, present the full scenario list and ask "Which scenarios failed?" — header `Failing scenarios`:

- One option per scenario name from the Task
- **New — not covered by existing scenarios** — this bug isn't covered by the current Gherkin

For each failing scenario, note:

- The scenario name
- The file path of the automated test (if it exists) or "manual"
- The failing step (the first Then / When that did not hold)

If no Gherkin exists for this bug, skip this step and rely on step 3.

### 3. Gather bug details

**If called from `wtf.verify-task` and all six details below are already in context, skip this step entirely.**

Otherwise, per `../references/questioning-style.md`, gather each unknown item below, omitting any already known:

- **a. Observed behavior** — ask "What was the exact behavior you observed?" — header `Actual behavior`, options from plausible failure descriptions inferred from the scenario context.
- **b. Expected behavior** — ask "What did you expect to happen instead?" — header `Expected behavior`, options from the relevant Gherkin `Then` step or AC text if available.
- **c. Reproduction steps** — ask "What are the reproduction steps?" — header `Repro steps`:
  - **I'll type them out** — enter numbered steps
- **d. Contract violation** — ask "Is any contract violated?" — header `Contract`:
  - Candidates from contract names in the Task (e.g. API schema name, event name)
  - **None identified**
- **e. Regression risk** — ask "What else might break if we fix this?" — header `Regression risk`, options from adjacent areas found in the codebase or related Aggregates.
- **f. Suggested fix** — ask "Do you have a suggested fix in mind?" — header `Suggested fix`:
  - **No suggestion** — leave blank

### 4. Map to Ubiquitous Language

Review the bug description and reproduction steps. If implementation vocabulary has crept in (e.g. "the database returned null", "the HTTP 500 response", "the JSON field"), restate in domain terms that match the Task's Ubiquitous Language (e.g. "the Order could not be found", "the Payment Settlement failed", "the Shipment Reference was missing").

Confirm the restatement with the user before proceeding.

> **When called from `wtf.verify-task` with multiple failures to file:** apply the restatement silently — do NOT ask for confirmation. Note the language changes made in the draft instead of asking the user to approve them. This prevents an interrogation when processing multiple bugs in sequence.

### 5. Find linked test files

Use the Grep tool to locate:

- Automated test files that cover the failing Gherkin scenario (search by scenario name or feature area)
- Any existing test for the contract section violated

List each file found with a one-line description of what it covers. These become the **Test Evidence** in the bug report.

### 6. Draft the Bug report

Before drafting, verify `.github/ISSUE_TEMPLATE/BUG.md` exists. If missing, ask the user (per `../references/questioning-style.md`) whether to run `/wtf.setup` or cancel — then halt either way.

Read the BUG template:

```bash
# Read .github/ISSUE_TEMPLATE/BUG.md
```

Use only the markdown body below the second `---` delimiter (ignore YAML frontmatter).

Fill in all sections:

**Related**

- Feature: #\<feature_number\> (if known)
- Task: #\<task_number\> (if known)
- Failing test(s): list each file path (or "manual" with reproduction steps)

**Expected Behavior**
Quote the relevant Gherkin `Then` step or Feature AC verbatim, then add a plain-language restatement.

**Actual Behavior**
Describe in domain terms what happened instead. Include any observable symptom (error message, wrong state, missing event).

**Steps to Reproduce**
Concrete numbered steps — exact inputs, routes, or actions. If from a Gherkin scenario, map Given → setup, When → action, Then → the failing assertion.

**Contracts Violated**
Paste the relevant contract section from the Task (API schema, event schema, invariant). If none, write "None identified."

**Suggested Fix**
Fill if the QA engineer or developer has a hypothesis. Otherwise leave blank.

**Regression Risk**
List other behaviors, Aggregates, or integration points that touch the same code path and could be affected by a fix.

### 7. Review with user

Show the draft. Then ask "Does this accurately capture the bug and its impact?" — header `Review`:

- **Yes — create the issue** → proceed with bug creation
- **I have changes** → adjust first

Apply edits, then proceed.

### 8. Create the issue

> Note: the commands below are pseudo-code. Write each body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise title from the bug's one-sentence description. Pass in the description and ask for a short title (no prefix emoji/label needed — that is added below). If the subagent returns nothing usable, derive the title directly from the one-sentence description.

```bash
BUG_TMP=/tmp/wtf.bug-$(date +%s)-body.md
gh issue create --title "🐞 Bug: <title>" --body-file "$BUG_TMP" --label "bug"
```

If the originating Task is known, add a comment to it linking the bug:

```bash
gh issue comment <task_number> --body "🐞 Bug reported: #<bug_number> — <one-line summary>"
```

Print the Bug issue URL and number.

```bash
rm "$BUG_TMP"
```

> Note: if the `bug` label does not exist on the repo, create it first with `gh label create bug --color d73a4a` before running `gh issue create`.

### 9. Offer next steps

Ask "What's next?" — header `Next step`:

- **Report another bug** → file another bug from this QA session (default if more failures remain)
- **Mark Task blocked** → reopen the Task and mark it blocked by this bug
- **Done** → exit, no further action (default if no more failures remain)

- **Report another bug** → restart from step 2 with the same Task context. Use as default only when the caller (e.g. `wtf.verify-task` step 8) has indicated more failures are pending.
- **Mark Task blocked** → reopen the Task and add a blocking comment:
  ```bash
  gh issue reopen <task_number>
  gh issue comment <task_number> --body "Blocked by #<bug_number>."
  ```
- **Done (default when no more failures remain)** → exit.
