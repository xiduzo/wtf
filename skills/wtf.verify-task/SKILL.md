---
name: wtf.verify-task
description: This skill should be used when a QA engineer wants to test or verify a completed task, run through acceptance criteria, check Gherkin scenarios against the implementation, record pass/fail results, or sign off on a ticket before merge. Triggers on phrases like "verify task #42", "run QA on this issue", "test the acceptance criteria", "sign off on task", "check if this task is ready to merge", "does this task meet its acceptance criteria", "run acceptance tests for task #X", "walk through the Gherkin for task #X", or "I want to test this task".
---

# Verify Task

Pick up an existing Task as a QA engineer. Core value: uses the Gherkin scenarios as the executable test script — each scenario is a concrete test case with Given/When/Then steps to run against the implementation.

Read `references/qa-verdict-guide.md` before starting — it defines the status symbols, verdict options, and the expected Test Mapping table format used throughout this skill.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.implement-task` or another skill that already ran gh-setup this session.

### 1. Identify the verification scope

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Are you verifying a single Task or a full Feature?"
- header: "Scope"
- options:
  - **Single Task** → verify one Task's Gherkin scenarios
  - **Full Feature** → verify all Tasks under a Feature using its sub-issues

**If Single Task:**

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Task are you testing?"
- header: "Task"
- options: from recent open issues labeled `task` or `implemented`

Walk Task → Feature per `../references/spec-hierarchy.md` to extract Gherkin, Contracts, Edge Cases, Test Mapping, DoD (Task) and ACs / edge cases for additional probe scenarios (Feature).

Apply the **absent-label gate** from `../references/lifecycle-labels.md` for the `implemented` label on the Task — recommended skill `wtf.implement-task`, header `Implement first?`. On **Implement first** → follow `wtf.implement-task` passing the Task number as context. On **Verify anyway** → proceed.

**If Full Feature:**

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Feature are you verifying?"
- header: "Feature"
- options: from open feature issues

Fetch all sub-issues of the Feature using `gh sub-issue list <feature_number>` per the cookbook in `../references/gh-setup.md`. This returns the authoritative list of Tasks — do not search by label or title matching.

**Sub-phase the task list.** Apply the file-conflict coloring algorithm in `../references/conflict-graph.md` to partition the tasks into conflict-free sub-phases — tasks within a sub-phase can run in parallel worktrees; sub-phases run sequentially.

**Spawn one sub-agent per task, per sub-phase.** Apply the rules in `../references/subagent-protocol.md` for every Agent call. Specifically for Full Feature mode:

- Read `skills/wtf.verify-task/SKILL.md` at spawn time and paste steps 3–9 into each sub-agent prompt (inline instructions — sub-agents cannot load this skill by name).
- Override interactive prompts as follows:
  - "Test surface" confirmation (step 3) → skip, proceed with all found scenarios
  - Per-scenario pass/fail (step 4) → return as `NEEDS_INPUT` to the orchestrator
  - Bug-filing prompts → defer to the aggregated step 9
- Mandatory label (non-skippable): `gh issue edit <task_number> --add-label "verified"` after verification completes.

Wait for all sub-agents in a sub-phase to complete (and any `NEEDS_INPUT` responses to be resolved) before starting the next sub-phase. After all sub-phases finish, aggregate into a feature-level summary (total tasks, pass/fail/blocked counts) and present it.

### 2. Load the QA steering document

Load `docs/steering/QA.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-qa`). Apply its test strategy, coverage thresholds, definition of done, and known flaky areas silently throughout this session.

### 3. Establish the test surface

From the Task, extract and present:

- All Gherkin scenarios (these are the test cases)
- The contracts (request/response schemas to verify against)
- Edge Cases & Risks (additional scenarios to probe)
- Observability requirements (logs, metrics, alerts to verify)

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "I found [n] Gherkin scenarios and [m] edge cases to cover. Does this match what you expect?" (replace [n] and [m] with actual counts)
- header: "Test surface"
- options:
  - **Yes — that's everything** → proceed to testing
  - **There are more scenarios** → add them first

### 4. Walk through each Gherkin scenario

For each scenario, one at a time, call `AskUserQuestion` (per `../references/questioning-style.md`):

1. Present it as a concrete test case — restate the Given/When/Then in plain language.
2. Ask "Did this scenario pass?" — header `Result`:
   - **Yes ✅** → mark ✅ in the running Test Mapping table; set `bug filed` to `—`
   - **No ❌** → record failure (see below)
   - **Blocked 🚫** → record blocker (see below)
   - **N/A or Conditional ⚠️** → record condition (see below)

   On **No ❌**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "What actually happened?"
   - header: "Failure details"
   - options: from plausible failure modes inferred from the scenario (e.g. "No error shown", "Wrong data returned")
   Record findings with repro steps. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Would you like to file a bug report now?"
   - header: "File bug?"
   - options:
     - **File now** → run `wtf.report-bug` immediately with the task number and scenario details (default); mark `bug filed` as `yes`
     - **Continue and file later** → defer; mark `bug filed` as `no`

   On **Blocked 🚫**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "What dependency or environment issue prevented testing?"
   - header: "Blocker"
   - options: from common blockers inferred from the task context (e.g. "Missing test environment", "Depends on unmerged task")
   Set `bug filed` to `—`.

   On **N/A or Conditional ⚠️**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Is this N/A, or does it pass only under a condition?"
   - header: "Condition"
   - options:
     - **N/A — not applicable** → this scenario does not apply
     - **Conditional — specify the condition** → passes only under a specific circumstance

   Record appropriately. Set `bug filed` to `—` (track the condition separately).
3. After recording the result, **immediately update the Task issue** with the current state of the Test Mapping table (do not wait until all scenarios are done). The table must include a `Bug Filed` column:

   The running Test Mapping table format (update after every scenario):

   | Scenario          | Result          | Bug Filed    |
   | ----------------- | --------------- | ------------ |
   | `<scenario name>` | ✅/❌/🚫/N/A/⚠️ | yes / no / — |

   ```bash
   gh issue view <task_number> --json body -q .body > /tmp/wtf.verify-<task_number>-body.md
   ```

   Programmatically replace the Test Mapping table section in `/tmp/wtf.verify-<task_number>-body.md` using the Write or Edit tool, preserving all other sections unchanged. Then push:

   ```bash
   gh issue edit <task_number> --body-file /tmp/wtf.verify-<task_number>-body.md
   ```

4. Keep a running tally. After updating, confirm: "Updated. Moving to next scenario..."

### 5. Probe the edge cases

For each Edge Case listed in the Task (and the parent Feature), one at a time:

1. Derive a concrete test action from the edge case description.
2. Call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Did this edge case pass?"
   - header: "Result"
   - options: **Yes ✅** / **No ❌** / **Blocked 🚫** / **N/A**

   On **No ❌**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "What actually happened?"
   - header: "Failure details"
   - options: from plausible failure modes inferred from the edge case
   Record findings with repro steps, then ask to file a bug report as in step 4.
3. After each result, update the Task issue — append an Edge Cases section (or update it if present) with the same table format used in step 4.

### 6. Verify observability

For each item in the Observability section (logs, metrics, alerts), one at a time, call `AskUserQuestion` (per `../references/questioning-style.md`):

1. Ask "Was this observability item present and correct?" — header `Result`:
   - **Yes ✅** → present and correct
   - **No ❌** → missing or incorrect
   - **N/A** → not applicable to this task
2. Record the result. On ❌, ask for details and offer to file a bug report as in step 4.
3. After each result, update the Task issue with an Observability Results section.

### 7. Finalize results and post QA summary

The Test Mapping table has been updated after each scenario (step 4). Now do a final update: check off DoD items that passed; leave failing ones unchecked.

```bash
gh issue view <task_number> --json body -q .body > /tmp/wtf.verify-<task_number>-final.md
```

Programmatically update the DoD checklist in `/tmp/wtf.verify-<task_number>-final.md` using the Write or Edit tool. Then push:

```bash
gh issue edit <task_number> --body-file /tmp/wtf.verify-<task_number>-final.md
```

Post a QA summary comment:

```bash
gh issue comment <task_number> --body "<qa_summary>"
```

The QA summary must include:

- Total scenarios tested and pass/fail/conditional count
- Any findings with repro steps
- Conditional passes: list each ⚠️ scenario with its required condition
- Clear verdict: ✅ Ready for merge / ❌ Needs fixes / ⚠️ Conditional pass (list conditions)

If the verdict is ✅ or ⚠️, add the `verified` lifecycle label:

```bash
gh issue edit <task_number> --add-label "verified"
```

Print the updated Task issue URL.

### 8. Offer to open a PR and close the issue

If the verdict is ✅ or ⚠️, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Task verified. What would you like to do next?"
- header: "Next step"
- options:
  - **Open PR now** → follow the `wtf.create-pr` process, passing the Task number in as context (recommended)
  - **Skip for now** → exit; I'll open the PR later

> **Closing policy:** Issues are only "closed as completed" via a merged PR that contains `Closes #<n>`. Never call `gh issue close <n>` for completed work. Direct closes are reserved for:
> - `gh issue close <n> --reason "not planned"` — won't implement
> - `gh issue close <n> --reason "duplicate"` — duplicate of another issue

### 9. Offer bug reports for remaining failures

Check all result tables (Gherkin scenarios from step 4, edge cases from step 5, observability from step 6): find all rows where Result is ❌ and `Bug Filed` is `no`. These are the unfiled failures.

If none exist, skip this step entirely.

If unfiled failures exist, present them as a numbered list, then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "[n] failing scenario(s) without a bug report. How would you like to handle them?" (replace [n] with the actual count)
- header: "File bugs?"
- options:
  - **File separately** → spawn one sub-agent per failing scenario in parallel using the Agent tool, each running the report-bug fast path. Apply `../references/subagent-protocol.md`. Wait for all sub-agents to complete before exiting (default).
  - **File combined** → follow the `wtf.report-bug` process once, passing in the task number and all failing scenarios together.
  - **Skip** → exit without filing reports.
