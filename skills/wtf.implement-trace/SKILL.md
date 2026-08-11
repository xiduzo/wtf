---
name: wtf.implement-trace
description: This skill should be used when a developer is ready to implement a GitHub Trace issue and needs to read the full spec hierarchy (Trace + Feature + Epic), explore the codebase, produce a concrete Technical Approach with real file paths, and drive TDD implementation against the Trace's claimed Gherkin scenarios. Triggers on phrases like "implement trace #42", "pick up the trace", "start working on this trace", "build the trace", "develop trace #X", "code up the trace", "write the tests for trace #X", "start the Skeleton", "resume trace #X", "continue trace #X", or "I want to implement this trace".
---

# Implement Trace

Start an existing Trace as a developer.

Read the full spec (Trace + Feature + Epic). The Trace's contract is its Scenario Claim. Map the claim to the actual codebase. Propose a concrete technical approach. Drive implementation test-first against each claimed Gherkin scenario. Leave the system releasable on merge.

The expected Trace issue body structure is defined in @.github/ISSUE_TEMPLATE/TRACE.md.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). If `gh` is not installed or not authenticated, stop. Extensions are not required for this skill.

If this skill was invoked from `wtf.write-trace`, `wtf.loop`, or another skill that already ran gh-setup this session, skip this step.

### 1. Identify the Trace

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Which Trace are you implementing?"
- header: "Trace"
- options: from recent open Trace issues (list per `../references/issue-classification.md`)

Walk Trace → Feature → Epic per `../references/spec-hierarchy.md`. Extract:

- **Trace**: Story, Scenario Claim, synced scenario copy, Spine Position (with Builds-on Traces), Contracts & Interfaces, DoD.
- **Feature**: ACs, User Stories with canonical Gherkin scenarios, Trace Plan, delivery override (when present).
- **Epic**: Goal and constraints.

### 2. Resolve the claimed scenarios

The Feature body is canonical for scenario text. The Trace body carries a synced courtesy copy. Take each scenario name from the Scenario Claim. Find its canonical text in the Feature body.

If the Trace's synced copy differs from the Feature's canonical text, the Feature wins. Tell the user about the drift. Recommend `wtf.refine` on the Feature to re-sync the copy. Continue with the canonical text.

If a claimed scenario name does not exist in the Feature body, stop and ask the user. Do not invent scenario text.

The resolved canonical scenarios drive the TDD cycle in step 8. Only the claimed scenarios are in scope — never the story's full scenario list.

### 3. Lifecycle check

Apply the **absent-label gate** from `../references/lifecycle-labels.md` for the `designed` label on the Trace.

Recommended skill: `wtf.design-trace`. Header: `Design check`.

On **Design it first** → follow `wtf.design-trace` and pass the Trace number as context. On **Skip design** → continue. If the label is present, continue silently.

### 4. Load the technical steering document

Load `docs/steering/TECH.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-tech`). Apply its stack, architecture patterns, key constraints, commands, and ADRs silently throughout this session.

### 5. Sequencing gate and branch setup

Traces within a Feature are sequential by design. Before you branch, check the previous Trace:

1. Read the Builds-on Trace numbers from the Spine Position section. When they are absent, use the Trace Plan order in the Feature body.
2. If this Trace builds on a previous Trace, find that Trace's PR and check its state (`gh pr view <pr_number> --json state`).
3. If the previous Trace's PR is not merged, warn the user and stop. The base branch does not yet contain the Spine this Trace extends. Continue only when the user explicitly overrides.
4. A Skeleton builds on nothing. It passes this gate without a check.

Then set up branches per `../references/branch-setup.md`: resolve the delivery mode (config plus per-feature override), generate the slug, and create or resume `trace/<trace-number>-<trace-slug>`. In `staged` delivery, first create or check out the feature branch — the trace branch bases on it. In `trunk` delivery, base on `main` and do not create a feature branch. Resolve any conflicts before you continue.

### 6. Explore the codebase

Before you explore, identify the test framework setup. Read a sample of existing test files. Record the following in a working scratchpad before you continue. These govern every test written in step 8:

| Field             | Value                                          |
| ----------------- | ---------------------------------------------- |
| Test framework    | (e.g. Jest, Vitest, pytest, RSpec)             |
| Test file pattern | (e.g. `**/*.test.ts`, `tests/test_*.py`)       |
| Import convention | (e.g. `import { describe, it } from 'vitest'`) |
| Run command       | (e.g. `npm test`, `pytest`)                    |
| Coverage command  | (e.g. `npm run coverage`, `pytest --cov`)      |

Use the Agent tool with these concrete searches (run in parallel):

- `Grep` for the domain nouns and verbs from the story and the claimed scenarios across `*.{ts,tsx,js,jsx,py,go,rb}` files — finds files and modules this Trace will touch
- `Grep` for interface or type names from the Trace's Contracts section — finds current interface definitions to implement against
- `Glob` matching the test file pattern from the scratchpad (e.g. `**/*.test.ts`) near the integration points found above — surfaces existing tests covering adjacent behavior
- `Grep` for any import of the domain objects or services this Trace depends on — identifies dependencies that must exist first

**Extension or Deepening Traces:** also read the PRs and commits of the Traces this one builds on (`gh pr view`, `git log --oneline <base-branch>`). The earlier Traces laid the Spine. Find the seams they created — the modules, interfaces, and test files this Trace extends. Build on those seams. Do not create parallel structures.

Also fetch any relevant wiki pages or in-repo glossary docs for this Trace's Bounded Context. Use these so the implementation and test naming align with the team's Ubiquitous Language.

### 7. Draft the Technical Approach

Apply strict STE per `../references/ste-writing.md` before you write any durable body (Technical Approach prose and later issue updates). Commit subject/body prose follows STE via `../references/commit-conventions.md`.

**Skeleton directive.** When the Trace's Spine Position is Skeleton, hold this line through the approach and the whole implementation:

> Build the MINIMAL end-to-end path through every layer for the claimed happy-path scenario. Touch each layer once — data, logic, interface — with the least code that makes the scenario pass at production quality. Do not gold-plate. Do not add speculative endpoints, configuration, options, or abstractions for scenarios not in the claim. Do not generalize for imagined future needs. Production quality is required — error handling and tests for the claimed path — but feature-complete is not. The Deepening Traces add the rest.

When the Position is Extension or Deepening: build on the Spine the earlier Traces laid (seams found in step 6). Extend their modules and interfaces. Keep the approach scoped to the claimed scenarios.

Produce a concrete Technical Approach with actual file paths (not generic layer names):

- Architecture decisions: which layer owns what, which patterns to follow, which existing seams this Trace extends
- Data flow: how data moves from input to output, with the concrete file paths touched
- Trade-offs: what alternatives were considered and why this approach was chosen
- Aggregates & Invariants: which Aggregates this Trace modifies, and which business rules must hold after the change

### 8. Review approach with user

Show the Technical Approach. Then call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Does this align with how you'd approach it?"
- header: "Approach review"
- options:
  - **Yes — looks good, proceed** → continue with implementation
  - **I have constraints to share** → adjust the approach first
  - **Suggest an alternative** → describe a different approach

Apply changes. Then update the Trace issue's Technical Approach section (including Aggregates & Invariants).

> See `references/issue-body-update-pattern.md` for the read-merge-write pattern (it goes through the gh body helper).

```bash
python3 .wtf/gh-body.py read <trace_number>        # prints a temp path; Read it, merge in the Technical Approach
python3 .wtf/gh-body.py edit <trace_number> --body-file "<path-from-read>"
```

### 9. Drive the TDD cycle

Process the claimed scenarios (resolved in step 2) in order — only those, never the story's unclaimed scenarios. Match the project's established test patterns discovered in step 6. Reference the Contracts & Interfaces section for exact request/response shapes.

1. **Write the failing test** for the scenario.
2. **Implement the minimum code** to make it pass.
3. **Refactor** if needed. Keep functions under 40 lines. Avoid deep nesting.
4. **Commit** — atomic semantic commit per `../references/commit-conventions.md`. Use the `Scenario:` and `Trace:` trailers:

   ```bash
   git add <changed files>
   git commit -m "<type>(<scope>): <short description>

   Scenario: <scenario name>
   Trace: #<trace_number>"
   ```

5. Do not skip ahead. Each scenario is a checkpoint.

Once all claimed scenarios are green, run the full lint and type-check gate once across all changes. Check `package.json` for `lint`, `typecheck`, `type-check`, or `check` script keys. Run whichever exist:

```bash
# e.g. npm run lint && npm run typecheck
```

Fix any issues before you continue to coverage.

### 10. Verify coverage and releasability

Once all claimed scenarios pass, confirm unit test coverage meets the minimum threshold for all new and modified code.

Use the threshold specified in `docs/steering/QA.md` if it exists. Default to 80% if the document is absent or does not define a threshold:

```bash
# Run the project's coverage command (check package.json scripts)
```

If coverage is below 80% on any new or modified file, add targeted tests before you continue. Every public function must have at least one happy-path and one error-path test.

**Releasability check.** Every Trace leaves the system releasable after merge — the DoD says so, and a Skeleton is never a prototype. Run the full existing test suite, not only the new tests. If any previously green test broke, fix it before you continue. Unfinished paths outside the claim must fail safely, not half-work.

### 11. Update Test Mapping

Fill the Test Mapping table in the Trace issue with concrete file paths:

| Claimed scenario  | Test file               | Status  |
| ----------------- | ----------------------- | ------- |
| `<scenario name>` | `<test file path:line>` | passing |

> See `references/issue-body-update-pattern.md` for the read-merge-write pattern. Re-`read` the body (do not reuse the temp file from step 8).

```bash
python3 .wtf/gh-body.py read <trace_number>        # re-fetch; prints a fresh temp path; Read it, update the Test Mapping table
python3 .wtf/gh-body.py edit <trace_number> --body-file "<path-from-read>"
```

Print the updated Trace issue URL.

### 12. Mark implemented, report learnings, offer to continue

Add the `implemented` lifecycle label. This is mandatory regardless of invocation mode:

```bash
gh issue edit <trace_number> --add-label "implemented"
```

**Learnings capture.** End the completion output with one short structured block that states what this Trace revealed — surprises in the codebase, drift between spec and reality, discovered edge cases, scenarios that look wrong or missing. `wtf.loop` feeds this block to headless `wtf.refine` as the re-aim insight:

```
Revealed:
- <surprise, drift, or discovered edge case>
- <...>
```

If the Trace revealed nothing, state `Revealed: nothing — plan held.` Do not omit the block.

If invoked from the loop (non-interactive mode), skip the ask below and return control to the loop.

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "What's next?"
- header: "Next step"
- options:
  - **Verify this Trace** → follow `wtf.verify-trace`, passing the Trace number in as context (recommended)
  - **Open a pull request** → follow `wtf.create-pr`, passing the Trace number and branch in as context
  - **Implement another Trace** → restart this skill from step 1
