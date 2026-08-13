---
name: wtf.verify-trace
description: This skill should be used when a QA engineer wants to verify a completed Trace, walk the claimed Gherkin scenarios against the implementation, record a verdict, or sign off before merge. Triggers on phrases like "verify trace #42", "run QA on this trace", "walk the claimed scenarios", "check the Scenario Claim for trace #X", "sign off on trace #X", "is this trace ready to merge", "run acceptance tests for trace #X", "verify all traces of this feature", or "I want to test this trace".
---

# Verify Trace

Start an existing Trace as a QA engineer.

The verification contract is the Trace's **Scenario Claim**. Verify exactly the claimed scenarios — no more, no less. The scenario text is canonical in the parent Feature body. Fetch it from there. Edge cases outside the claim belong to other Traces in the Trace Plan. Do not probe them here.

Two verification methods exist. When the repo has a Gherkin runner, project the claimed scenarios into a temporary `.feature` file and execute them. When no runner exists, or steps are unbound, walk each scenario against the running software. The verdict states which method verified each scenario.

Read `references/qa-verdict-guide.md` before you start. It defines the status symbols, the method values, the verdict options, and the Test Mapping table format used throughout this skill.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). If `gh` is not installed or not authenticated, stop. Extensions are not required for this skill.

If this skill was invoked from `wtf.implement-trace` or another skill that already ran gh-setup this session, skip this step.

### 1. Identify the verification scope

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Are you verifying a single Trace or a full Feature?"
- header: "Scope"
- options:
  - **Single Trace** → verify one Trace's Scenario Claim
  - **Full Feature** → verify all child Traces of a Feature using its sub-issues

**If Single Trace:**

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Which Trace are you testing?"
- header: "Trace"
- options: from recent open Trace issues (list per `../references/issue-classification.md`). Prefer issues labeled `implemented`.

Walk Trace → Feature per `../references/spec-hierarchy.md`. From the Trace, extract the Scenario Claim, the synced scenario copy, the Spine position, Contracts, Observability, and DoD. From the Feature, extract the claimed story with its canonical scenarios, plus the Trace Plan.

Apply the **absent-label gate** from `../references/lifecycle-labels.md` for the `implemented` label on the Trace.

Recommended skill: `wtf.implement-trace`. Header: `Implement first?`.

On **Implement first** → follow `wtf.implement-trace` and pass the Trace number as context. On **Verify anyway** → continue.

**If Full Feature:**

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Which Feature are you verifying?"
- header: "Feature"
- options: from open feature issues

Fetch all sub-issues of the Feature using `gh sub-issue list <feature_number>` per the cookbook in `../references/gh-setup.md`. This returns the authoritative list of children. Do not search by label or title matching. Split the children by kind per `../references/issue-classification.md`: Trace children, and legacy Task children.

**Verify Traces sequentially.** Traces of one Feature build on each other's Spine, and sibling Traces may have landed in either order. Verify in Trace Plan order regardless — it is the order the Spine was designed in. If a Trace does not appear in the plan, fall back to issue-number order. Do not parallelize Traces of one Feature: they share a checkout, and a later Trace's scenarios can depend on an earlier Trace's code.

**Spawn one sub-agent per Trace, one at a time.** Apply the rules in `../references/subagent-protocol.md` for every Agent call. Specifically for Full Feature mode:

- Read `skills/wtf.verify-trace/SKILL.md` at spawn time and paste steps 2–8 into each sub-agent prompt (inline instructions — sub-agents cannot load this skill by name).
- Override interactive prompts as follows:
  - Claim confirmation (step 3) → skip, proceed with the full Scenario Claim
  - Drift gate (step 3) → do not resolve alone. Return as `NEEDS_INPUT` to the orchestrator
  - Per-scenario pass/fail in the interpretive walk (step 6) → return as `NEEDS_INPUT` to the orchestrator
  - Bug-filing prompts → defer to the aggregated step 10
- Mandatory label (non-skippable): `gh issue edit <trace_number> --add-label "verified"` after verification passes.

Resolve any `NEEDS_INPUT` responses for a Trace before you start the next Trace.

**Legacy Task children** are legacy Traces (see `../references/issue-classification.md`). Their Gherkin lives in the Task body — extract it per the legacy sections in `../references/spec-hierarchy.md`. Verify legacy Tasks interpretively (step 6 flow, no drift gate — the Task body is its own scenario source). Schedule them with the file-conflict coloring in `../references/conflict-graph.md`, after the Trace sequence completes.

After all children finish, aggregate into a feature-level summary. Include child counts, pass/fail/blocked totals, the partition status of each story, and whether the Feature is complete. Present it.

### 2. Load the QA steering document

Load `docs/steering/QA.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-qa`). Apply its test strategy, coverage thresholds, definition of done, and known flaky areas silently throughout this session.

Also record any Gherkin runner or BDD tooling the document declares. Step 4 uses that declaration first.

### 3. Establish the verification contract

From the Trace body, extract:

- The claimed scenario names (the **Scenario Claim**)
- The synced courtesy copy in the collapsed `<details>` block
- Contracts and Observability (step 7 uses these)

From the Feature body, extract the **canonical** text of each claimed scenario, under the Trace's story.

If a claimed scenario name does not exist in the Feature body, stop. The claim is broken. Report the missing name and recommend `/wtf.refine` on the Feature to repair the Trace Plan.

**Drift gate.** Compare the synced copy against the canonical Feature text, with whitespace normalized. If any claimed scenario differs, stop before you verify. The sync is stale. The Feature wins. Present the differences, then call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "The Trace's synced scenario copy differs from Feature #[N]. The Feature body is canonical. How do you want to proceed?"
- header: "Stale sync"
- options:
  - **Verify against the Feature text** → continue with the canonical text. Note the stale sync in the verdict and recommend `/wtf.refine` to resync the copy
  - **Halt** → exit. Run `/wtf.refine` on the Feature first, then verify again

**Confirm the claim.** Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "The Scenario Claim names [n] scenarios. I will verify exactly these — no more, no less. Correct?" (replace [n] with the actual count)
- header: "Claim"
- options:
  - **Yes — verify the claim** → proceed to testing
  - **The claim is wrong** → stop. Scenario ownership changes go through `/wtf.refine` on the Feature, not through an ad-hoc edit here

### 4. Detect a Gherkin runner

Decide the verification method before you test. Precedence:

1. A runner declared in `docs/steering/QA.md` (step 2) wins.
2. Otherwise probe the dependency manifests:

   ```bash
   grep -nE '"(playwright-bdd|@cucumber/cucumber|cucumber-js)"' package.json 2>/dev/null
   grep -nE '(behave|pytest-bdd)' pyproject.toml setup.cfg Pipfile requirements*.txt 2>/dev/null
   ```

3. Confirm that step definitions exist:

   ```bash
   ls features/step_definitions 2>/dev/null      # cucumber-js default
   ls features/steps 2>/dev/null                 # behave default
   git ls-files | grep -iE '(^|/)(steps?|step_definitions)(/|\.)' | head -20
   ```

Selection rules:

- If QA.md names a runner, use that runner.
- If exactly one manifest probe hits, use that runner.
- If several runners hit and QA.md is silent, ask the user which one to use (headless: `NEEDS_INPUT`).
- If no runner hits, or the runner has no step definitions at all, use the interpretive fallback for every claimed scenario. Skip step 5.

> **Note:** this probe covers the common runners. A repo can execute Gherkin in another way — `docs/steering/QA.md` is the place to declare that.

### 5. Project and execute (runner found)

Build the **ephemeral projection**:

1. Create a scratch directory outside the repo: `TMP=$(mktemp -d)`.
2. Write `$TMP/trace-<trace_number>.feature` with the Write tool. Content: a comment header, one `Feature:` line, then the canonical text of each claimed scenario, verbatim from the Feature body:

   ```gherkin
   # Ephemeral projection from Feature #<feature_number> for Trace #<trace_number>. Do not commit.
   Feature: <feature title> — Scenario Claim of Trace #<trace_number>

   Scenario: <claimed scenario, canonical text>
   ```

   Never write this file inside the repo. Never commit it. No `.feature` file becomes a repo artifact.

3. **Bind check (dry run), then run.** Bind the projection to the project's existing step definitions:

   | Runner | Bind check (dry run) | Run |
   |---|---|---|
   | cucumber-js / @cucumber/cucumber | `npx cucumber-js --dry-run "$TMP/trace-<n>.feature" --require <project step paths>` | Same command without `--dry-run` |
   | playwright-bdd | Scratch `defineBddConfig` that points `features` at the temp file and `steps` at the project's steps, then `npx bddgen -c <scratch config>` | `npx playwright test` on the generated specs |
   | behave | Copy the temp file into a scratch `features/` dir beside a copy of the project's `steps/`, then `behave --dry-run <dir>` | `behave <dir>` |
   | pytest-bdd | Scratch test module that calls `scenarios("$TMP/trace-<n>.feature")` and imports the project's step modules, then `pytest --collect-only <module>` | `pytest <module>` |

4. If the dry run reports undefined steps, record which scenarios contain them. Move those scenarios to step 6 (interpreted). Do not write new step definitions during verification. A missing binding is a finding for the verdict, not QA work.
5. Run the bound scenarios. Capture per-scenario pass/fail and the failure output.
6. Record each executed result per the recording rules in step 6, with method `executed`. On ❌, use the runner output as the failure details, then offer a bug report per the step 6 flow.
7. Remove the scratch directory after the run.

Executed results are the primary verdict evidence. Do not re-walk a scenario the runner already executed.

### 6. Walk the remaining scenarios (interpreted)

Scenario set: every claimed scenario when no runner was found, plus the scenarios with unbound steps from step 5.

For each scenario, one at a time, call `AskUserQuestion` (per `../references/questioning-style.md`):

1. Present it as a concrete test case. Restate the Given/When/Then in plain language. Walk it against the running software.
2. Ask "Did this scenario pass?" — header `Result`:
   - **Yes ✅** → mark ✅ in the running Test Mapping table. Set `bug filed` to `—`
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
     - **File now** → run `wtf.report-bug` immediately with the Trace number and the failing scenario name (default). It links the failing scenario to the Trace. Mark `bug filed` as `yes`
     - **Continue and file later** → defer. Mark `bug filed` as `no`

   On **Blocked 🚫**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "What dependency or environment issue prevented testing?"
   - header: "Blocker"
   - options: from common blockers inferred from the Trace context (e.g. "Missing test environment", "Depends on an unmerged Trace")
   Set `bug filed` to `—`.

   On **N/A or Conditional ⚠️**: call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Is this N/A, or does it pass only under a condition?"
   - header: "Condition"
   - options:
     - **N/A — not applicable** → this scenario does not apply
     - **Conditional — specify the condition** → passes only under a specific circumstance

   Record appropriately. Set `bug filed` to `—` (track the condition separately).
3. **Recording rules (both methods).** After you record a result — executed or interpreted — **immediately update the Trace issue** with the current state of the Test Mapping table. Do not wait until all scenarios are done.

   The table must include a `Method` column and a `Bug Filed` column:

   | Claimed scenario  | Method                 | Result          | Bug Filed    |
   | ----------------- | ---------------------- | --------------- | ------------ |
   | `<scenario name>` | executed / interpreted | ✅/❌/🚫/N/A/⚠️ | yes / no / — |

   ```bash
   python3 .wtf/gh-body.py read <trace_number>       # prints a temp path
   ```

   Programmatically replace the Test Mapping table section in the printed temp file using the Write or Edit tool. Preserve all other sections unchanged. Then push (see `../references/gh-body-helper.md`):

   ```bash
   python3 .wtf/gh-body.py edit <trace_number> --body-file "<path-from-read>"
   ```

4. Keep a running tally. After updating, confirm: "Updated. Moving to next scenario..."

### 7. Check releasability

Every Trace leaves the system releasable. Confirm the invariant with one short check — not a full regression:

1. Run the project's build and check gate on the Trace's branch (build, lint, type check — per `package.json` scripts or QA.md).
2. Smoke the Spine. Confirm the happy path of the Skeleton, and of the Traces this one builds on, still works. One quick pass, no detail.
3. Confirm the Observability items from the Trace body are present (logs, metrics, alerts). On a missing item, offer a bug report per the step 6 flow.

Record one releasability line: `Releasable: yes` or `Releasable: no — <reason>`. A `no` forces the ❌ verdict, even when all claimed scenarios passed.

### 8. Finalize results and post the QA verdict

Apply strict STE per `../references/ste-writing.md` before you write any durable body (QA verdict comment and free-text issue updates).

The Test Mapping table has been updated after each scenario (step 6). Now do a final update. Check off DoD items that passed. Leave failing ones unchecked.

```bash
python3 .wtf/gh-body.py read <trace_number>       # re-fetch; prints a fresh temp path
```

Programmatically update the DoD checklist in the printed temp file using the Write or Edit tool. Then push:

```bash
python3 .wtf/gh-body.py edit <trace_number> --body-file "<path-from-read>"
```

**Roll-up.** Determine what this verdict completes:

1. List the sibling Traces that claim the same story: the Feature's Trace Plan plus `gh sub-issue list <feature_number>`.
2. If every scenario of the story is now verified across its Traces, the story's partition is exhausted. State "Story complete: <story name>" in the verdict.
3. If every story of the Feature is complete, state "Feature complete" too. The Feature then closes per its delivery mode: the feature-PR merge in `staged`, Trace Plan exhaustion in `trunk`.

Post a QA verdict comment:

```bash
# Write the QA verdict to a temp file with the Write tool; $COMMENT is that path.
python3 .wtf/gh-body.py comment <trace_number> --body-file "$COMMENT"
```

The QA verdict must include:

- Claimed scenarios tested, with per-method counts (executed vs. interpreted) and pass/fail/conditional totals
- Which runner executed the projection, or why the interpretive fallback applied (no runner, or the unbound steps by name)
- Any findings with repro steps or runner output
- Conditional passes: list each ⚠️ scenario with its required condition
- The releasability line from step 7
- The roll-up note when a story or the Feature completes
- Clear verdict: ✅ Ready for merge / ❌ Needs fixes / ⚠️ Conditional pass (list conditions)

If the verdict is ✅ or ⚠️, add the `verified` lifecycle label:

```bash
gh issue edit <trace_number> --add-label "verified"
```

Print the updated Trace issue URL.

### 9. Offer to open a PR and close the issue

If the verdict is ✅ or ⚠️, call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Trace verified. What would you like to do next?"
- header: "Next step"
- options:
  - **Open PR now** → follow the `wtf.create-pr` process, passing the Trace number in as context (recommended)
  - **Skip for now** → exit. Open the PR later yourself

> **Closing policy:** Issues are only "closed as completed" via a merged PR that contains `Closes #<n>`. Never call `gh issue close <n>` for completed work. Direct closes are reserved for:
> - `gh issue close <n> --reason "not planned"` — will not implement
> - `gh issue close <n> --reason "duplicate"` — duplicate of another issue

### 10. Offer bug reports for remaining failures

Check the Test Mapping results (steps 5–6) and the releasability findings (step 7). Find all rows where Result is ❌ and `Bug Filed` is `no`. These are the unfiled failures.

If none exist, skip this step entirely.

If unfiled failures exist, present them as a numbered list. Then call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "[n] failing scenario(s) without a bug report. How would you like to handle them?" (replace [n] with the actual count)
- header: "File bugs?"
- options:
  - **File separately** → spawn one sub-agent per failing scenario in parallel using the Agent tool, each running the report-bug fast path. Apply `../references/subagent-protocol.md`. Wait for all sub-agents to complete before exiting (default).
  - **File combined** → follow the `wtf.report-bug` process once, passing in the Trace number and all failing scenarios together.
  - **Skip** → exit without filing reports.
