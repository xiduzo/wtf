---
name: wtf.report-bug
description: This skill should be used when a developer or QA engineer wants to report a bug, create a bug ticket, document a test failure, log a defect, file an issue found during a QA session, or report something that is broken — for example "report a bug", "create a bug ticket", "I found a defect", "something is broken in trace #X", or "document this test failure". Files a structured GitHub Bug issue that links the originating Trace and Feature, maps failing Gherkin scenarios as reproducible test evidence, and fills every section of the BUG template.
---

# Report Bug

File a structured Bug issue from a QA finding. The failed Gherkin scenario becomes the reproducible test evidence. The bug cites the scenario name and the Trace that claimed it. The scenario text is canonical in the Feature body. The originating Trace and Feature are linked so context is kept.

## Fast path (for wtf.hotfix)

When invoked from `wtf.hotfix`, skip the Gherkin-derivation and Ubiquitous-Language mapping work. The goal is to file the issue fast so the fix can start. Run only:

- Step 0 — GitHub CLI setup (skip if already confirmed this session).
- Step 1 — Identify the source (one-sentence bug, impact, optional trace link).
- Step 3 — Gather bug details, but only `a. Observed behavior`, `b. Expected behavior`, and `c. Reproduction steps`. Skip contract violation / regression risk / suggested fix questions. The hotfix will uncover those.
- Step 6 — Draft the Bug report with only the sections the fast path produced (leave Contracts Violated, Regression Risk, Suggested Fix blank or marked "Fast path — to be captured during hotfix").
- Step 7 — Review briefly (or skip if the caller signaled non-interactive).
- Step 8 — Create the issue.

Return the bug issue number to the caller. Do not run the offer-next-steps prompt in step 9.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

If invoked from `wtf.verify-trace` or another skill that already ran gh-setup this session, skip this step.

### 1. Identify the source

**If called from `wtf.verify-trace`:** the trace number and failing scenario(s) are already in context — skip to step 2. Do not ask the questions below.

**If invoked directly:**

Ask in a single message:

- "What is the bug? (one sentence)"
- "Which Trace claimed the failing behavior? (issue number, or 'unknown')"

If a trace number is known, walk Trace → Feature per `../references/spec-hierarchy.md`. From the Trace, extract the Scenario Claim, the synced scenario copy, Contracts, and DoD. From the Feature, extract the canonical text of the claimed scenarios, plus ACs and user stories for expected-behavior context.

If the linked issue is a legacy Task, link it as a legacy Trace (see `../references/issue-classification.md`). Its Gherkin lives in the Task body — extract Gherkin, Contracts, ACs, and DoD per the legacy sections of `../references/spec-hierarchy.md`.

### 2. Identify the failing scenario(s)

If the Trace has a Scenario Claim, present the claimed scenario names. Their canonical text lives in the Feature body — quote from there, not from the synced copy. For a legacy Task, present the scenario list from the Task body instead. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which scenarios failed?"
- header: "Failing scenarios"
- options:
  - One option per claimed scenario name
  - **New — not covered by existing scenarios** — this bug is not covered by the current Gherkin

For each failing scenario, note:

- The scenario name
- The file path of the automated test (if it exists) or "manual"
- The failing step (the first Then / When that did not hold)

If no Gherkin exists for this bug, skip this step and rely on step 3.

### 3. Gather bug details

**If called from `wtf.verify-trace` and all six details below are already in context, skip this step entirely.**

Otherwise, for each unknown item below (omitting any already known), call `AskUserQuestion` (per `../references/questioning-style.md`):

- **a. Observed behavior** — question: "What was the exact behavior you observed?" / header: "Actual behavior" / options: from plausible failure descriptions inferred from the scenario context.
- **b. Expected behavior** — question: "What did you expect to happen instead?" / header: "Expected behavior" / options: from the relevant Gherkin `Then` step or AC text if available.
- **c. Reproduction steps** — question: "What are the reproduction steps?" / header: "Repro steps" / options: **I'll type them out** — enter numbered steps.
- **d. Contract violation** — question: "Is any contract violated?" / header: "Contract" / options: candidates from contract names in the Trace. **None identified**.
- **e. Regression risk** — question: "What else might break if we fix this?" / header: "Regression risk" / options: from adjacent areas found in the codebase or related Aggregates.
- **f. Suggested fix** — question: "Do you have a suggested fix in mind?" / header: "Suggested fix" / options: **No suggestion** — leave blank.

### 4. Map to Ubiquitous Language

Review the bug description and reproduction steps. If implementation vocabulary has crept in (e.g. "the database returned null", "the HTTP 500 response", "the JSON field"), restate in domain terms that match the Ubiquitous Language of the Trace's story and its Feature (e.g. "the Order could not be found", "the Payment Settlement failed", "the Shipment Reference was missing").

Confirm the restatement with the user before proceeding.

> **When called from `wtf.verify-trace` with multiple failures to file:** apply the restatement silently — do NOT ask for confirmation. Note the language changes made in the draft instead of asking the user to approve them. This prevents an interrogation when processing multiple bugs in sequence.

### 5. Find linked test files

Use the Grep tool to locate:

- Automated test files that cover the failing Gherkin scenario (search by scenario name or feature area)
- Any existing test for the contract section violated

List each file found with a one-line description of what it covers. These become the **Test Evidence** in the bug report.

### 6. Draft the Bug report

Apply strict STE per `../references/ste-writing.md` before writing any durable body.

Load the BUG template per `../references/issue-template-loading.md` (verify existence, halt-or-setup if missing, read body below the second `---` delimiter). Fill all sections:

**Related**

- Feature: #\<feature_number\> (if known)
- Trace: #\<trace_number\> (if known — the Trace that claimed the failing scenario. A legacy Task links here as a legacy Trace)
- Failing scenario: the scenario name (canonical text in the Feature body)
- Failing test(s): list each file path (or "manual" with reproduction steps)

**Expected Behavior**
Quote the relevant Gherkin `Then` step or Feature AC verbatim. Quote the scenario from the Feature body — it is canonical there. For a legacy Task, quote from the Task body. Then add a plain-language restatement.

**Actual Behavior**
Describe in domain terms what happened instead. Include any observable symptom (error message, wrong state, missing event).

**Steps to Reproduce**
Concrete numbered steps — exact inputs, routes, or actions. If from a Gherkin scenario, map Given → setup, When → action, Then → the failing assertion.

**Contracts Violated**
Paste the relevant contract section from the Trace (API schema, event schema, invariant). If none, write "None identified."

**Suggested Fix**
Fill if the QA engineer or developer has a hypothesis. Otherwise leave blank.

**Regression Risk**
List other behaviors, Aggregates, or integration points that touch the same code path and could be affected by a fix.

### 7. Review with user

Show the draft. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this accurately capture the bug and its impact?"
- header: "Review"
- options:
  - **Yes — create the issue** → proceed with bug creation
  - **I have changes** → adjust first

Apply edits. Then proceed.

### 8. Create the issue

> Note: the commands below are pseudo-code. Write each body to a temp file with the Write tool. Then create it through the gh body helper (`.wtf/gh-body.py`) so multi-line UTF-8 content survives on Windows. See `../references/gh-body-helper.md`.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise title from the bug's one-sentence description. Pass in the description and ask for a short title (no prefix emoji/label needed — that is added below). If the subagent returns nothing usable, derive the title directly from the one-sentence description.

```bash
# Write the filled bug body to a temp file with the Write tool; $BUG_TMP is that path.
# Create the issue WITHOUT a kind label — the classify step below sets the kind.
python3 .wtf/gh-body.py create --title "🐞 Bug: <title>" --body-file "$BUG_TMP"
```

**Classify the issue as `Bug`.** Set `TYPE="Bug"` and `ISSUE_NUMBER=<number from the URL>`. Then run the **Classify a new issue** block from `../references/issue-classification.md` (resolve `$WTF_CLASS` once first). In `types` mode it sets the native GitHub issue type and leaves labels free for your own segmentation. In `labels` mode it applies the `bug` label.

If the originating Trace is known, write this comment to a temp file with the Write tool, then post it linking the bug:

> 🐞 Bug reported: #<bug_number> — <one-line summary>

```bash
# $COMMENT is the temp file you wrote the comment above to.
python3 .wtf/gh-body.py comment <trace_number> --body-file "$COMMENT"
```

Print the Bug issue URL and number.

```bash
rm "$BUG_TMP"
```

### 9. Offer next steps

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Report another bug** → file another bug from this QA session (default if more failures remain)
  - **Mark Trace blocked** → reopen the Trace and mark it blocked by this bug
  - **Done** → exit, no further action (default if no more failures remain)

- **Report another bug** → restart from step 2 with the same Trace context. Use as default only when the caller (e.g. `wtf.verify-trace`) has indicated more failures are pending.
- **Mark Trace blocked** → reopen the Trace and add a blocking comment:
  ```bash
  gh issue reopen <trace_number>
  # Write "Blocked by #<bug_number>." to a temp file with the Write tool ($COMMENT), then:
  python3 .wtf/gh-body.py comment <trace_number> --body-file "$COMMENT"
  ```
- **Done (default when no more failures remain)** → exit.
