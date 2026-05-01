---
name: wtf.pr-review
description: This skill should be used when a developer or tech lead wants to review a pull request for correctness, spec adherence, and code quality — for example "review PR #42", "check this PR against the spec", "does this PR match the task?", "code review PR #X", "review this before I approve", "check if the implementation matches the contracts", or "does this PR have the right tests?". Reviews the diff against the linked Task spec (Gherkin scenarios, Contracts, Impacted Areas) and posts a structured GitHub PR review. Distinct from verify-task, which is QA testing by running the software — this skill reads the code.
---

# PR Review

Review a pull request as a tech lead. Core value: reads the diff against the linked Task spec (Gherkin, Contracts, Impacted Areas) to catch spec drift, missing test coverage, and contract violations before merge — not by running the software, but by reading the code.

**Distinct from `wtf.verify-task`:** `wtf.verify-task` is a QA engineer running the implemented behavior against Gherkin scenarios (does the software do what it says?). This skill is a developer reviewing the code itself (is the code written correctly against the spec?).

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

### 1. Identify the PR

If a PR number was passed in, use it directly. Otherwise:

```bash
gh pr list --state open --json number,title,headRefName --limit 20
```

Apply `../references/questioning-style.md` and ask "Which PR are you reviewing?" — header `PR`, options from open PRs.

Fetch the PR:

```bash
gh pr view <pr_number> --json number,title,body,headRefName,baseRefName,additions,deletions,changedFiles
```

### 2. Fetch the spec hierarchy

Extract a Task number from the PR body (`Closes #<n>` or `Fixes #<n>`) per the PR-extraction recipe in `../references/spec-hierarchy.md`. If found, walk Task → Feature → Epic per the same reference to extract Gherkin, Contracts, Impacted Areas, DoD (Task) and ACs / Goal / constraints (Feature, Epic).

If no Task number is found, ask "Is there a Task issue linked to this PR?" — header `Linked task`:

- **No linked task** → review from diff only
- **Yes — I'll provide the number** → enter the task issue number

If there is no linked Task, the review proceeds from diff context alone (step 4 will note the absence of a spec as a finding).

### 3. Load the technical steering document

Load `docs/steering/TECH.md` per the **best-effort consumer-side load** in `../references/steering-doc-process.md`. Apply its patterns, constraints, and conventions as the baseline for code quality judgements throughout this review.

### 4. Inspect the diff

```bash
git diff <base_branch>...<pr_branch> --stat
git diff <base_branch>...<pr_branch>
```

Read the full diff. Note:
- Which files changed and which layers they touch
- What was added vs. removed vs. moved
- Whether the changes stay within the Impacted Areas listed in the Task

### 5. Run the review checklist

Evaluate each dimension. Record findings as PASS / FAIL / WARN per item.

**a. Spec adherence**

For each Gherkin scenario in the Task:
- Is there a test that covers this scenario? (search test files for scenario name or equivalent describe/it block)
- Does the implementation match the Given/When/Then behavior — not just passing the test, but structurally doing what the scenario describes?

Flag: missing test for a scenario, test present but testing the wrong behavior, implementation that bypasses the scenario entirely.

**b. Contract compliance**

For each entry in the Task's Contracts & Interfaces section:
- Does the code implement exactly the specified shape? (field names, types, optionality)
- Are there any added fields not in the spec (scope creep)?
- Are any specified fields missing from the implementation?

Flag: schema drift, extra fields, missing fields, wrong types.

**c. Impacted Areas**

Cross-reference the Task's Impacted Areas list against the actual changed files:
- Unexpected files changed outside the listed areas (scope creep signal)
- Listed areas with no changes (may indicate incomplete implementation)

**d. Code quality against TECH.md**

Review changed code against the patterns and constraints in `docs/steering/TECH.md`:
- Naming conventions (domain language vs. generic names)
- Layer separation (e.g. business logic in wrong layer)
- Error handling patterns
- Function length and nesting (flag >40 lines or deep nesting as a warning, not a blocker)

**e. Test coverage**

- Are there tests for the happy path AND at least one error/edge path per public function changed?
- Does the test file pattern match the project convention (from TECH.md)?
- Are there any `skip`, `todo`, or commented-out assertions in the new tests?

**f. Definition of Done**

Check the Task's DoD checklist against the diff:
- Are all DoD items evidenced in the diff or existing code?

### 6. Summarise findings

Produce a structured review summary:

```
PR Review — #<pr_number>: <title>
───────────────────────────────────────────────
Linked task: #<n> | Spec coverage: [n/n scenarios covered]

PASS  Spec adherence     — all [n] scenarios have matching tests
WARN  Contract compliance — `paymentId` field missing from response shape (Task spec: required)
PASS  Impacted Areas     — changes within declared scope
WARN  Code quality       — `processSettlement()` is 58 lines (threshold: 40)
PASS  Test coverage      — happy path + 2 error paths
FAIL  DoD                — "Observability: metrics emitted" not evidenced in diff

Verdict: REQUEST CHANGES
───────────────────────────────────────────────
Required (blocking merge):
  1. [Contract] Add `paymentId` to settlement response — Task spec requires it (Contracts §2)
  2. [DoD] Emit the `settlement_processed` metric — listed as required in Task DoD

Suggested (non-blocking):
  3. [Quality] Extract `processSettlement()` into smaller functions — currently 58 lines
```

Verdicts:
- **APPROVE** — no blocking findings
- **APPROVE WITH COMMENTS** — suggestions only, nothing blocking
- **REQUEST CHANGES** — one or more FAIL items that must be resolved before merge

### 7. Review with user

Show the summary. Then ask "Does this look right? Should I post this as a GitHub PR review?" — header `Post review`:

- **Post it** → submit as a GitHub PR review comment
- **I have edits** → adjust before posting
- **Don't post — just the summary** → keep it in the conversation

Apply any edits, then proceed.

### 8. Post the review

```bash
gh pr review <pr_number> \
  --<approve|request-changes|comment> \
  --body-file /tmp/wtf.pr-review-<pr_number>-body.md
```

Use:
- `--approve` for APPROVE or APPROVE WITH COMMENTS
- `--request-changes` for REQUEST CHANGES
- `--comment` if the user chose "Don't post — just the summary" but then changed their mind

Print the PR URL.
