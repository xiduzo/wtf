---
name: wtf.implement-task
description: This skill should be used when a developer is ready to implement a GitHub Task issue and needs to read the full spec hierarchy (Task + Feature + Epic), explore the codebase, produce a concrete Technical Approach with real file paths, and drive TDD implementation against Gherkin scenarios. Triggers on phrases like "implement task #42", "pick up task", "start working on this task", "build the task", "develop task #X", "code up the task", "write the tests for task #X", "start coding this ticket", "resume task #X", "continue task #X", or "I want to implement this ticket".
---

# Implement Task

Pick up an existing Task as a developer. Core value: reads the full spec (Task + Feature + Epic), maps it to the actual codebase, proposes a concrete technical approach, then drives implementation test-first against each Gherkin scenario.

The expected Task issue body structure is defined in @.github/ISSUE_TEMPLATE/TASK.md.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if invoked from `wtf.verify-task` or another skill that already ran gh-setup this session.

### 1. Identify the Task

Ask: "Which Task are you implementing? (issue number)"

Walk Task → Feature → Epic per `../references/spec-hierarchy.md` to extract Gherkin, Contracts, Impacted Areas (Task) and ACs / Goal / constraints (Feature, Epic).

### 2. Lifecycle check

Apply the **absent-label gate** from `../references/lifecycle-labels.md` for the `designed` label on the Task — recommended skill `wtf.design-task`, header `Design check`. On **Design it first** → follow `wtf.design-task` passing the Task number as context. On **Skip design** → proceed. If present, continue silently.

### 3. Load the technical steering document

Load `docs/steering/TECH.md` per the **strict consumer-side load** in `../references/steering-doc-process.md` (recommended skill: `wtf.steer-tech`). Apply its stack, architecture patterns, key constraints, commands, and ADRs silently throughout this session.

### 4. Set up the branch

Set up the feature branch and task branch per `../references/branch-setup.md` (slug generation, feature-branch create-or-checkout, task-branch create-or-resume). Resolve any conflicts before proceeding.

### 5. Explore the codebase

Before exploring, identify the test framework setup by reading a sample of existing test files. Record the following in a working scratchpad before proceeding — these govern every test written in step 8:

| Field             | Value                                          |
| ----------------- | ---------------------------------------------- |
| Test framework    | (e.g. Jest, Vitest, pytest, RSpec)             |
| Test file pattern | (e.g. `**/*.test.ts`, `tests/test_*.py`)       |
| Import convention | (e.g. `import { describe, it } from 'vitest'`) |
| Run command       | (e.g. `npm test`, `pytest`)                    |
| Coverage command  | (e.g. `npm run coverage`, `pytest --cov`)      |

Use the Agent tool with these concrete searches (run in parallel):

- `Grep` for the domain nouns and verbs from the Task's Functional Description across `*.{ts,tsx,js,jsx,py,go,rb}` files — finds files and modules this task will touch
- `Glob` matching the file patterns for each **Impacted Area** listed in the Task (e.g. `src/api/**/*`, `src/features/<feature-slug>/**/*`) — surfaces integration points and existing patterns
- `Grep` for interface or type names from the Task's Contracts section — finds current interface definitions to implement against
- `Glob` matching the test file pattern from the scratchpad (e.g. `**/*.test.ts`) near the integration points found above — surfaces existing tests covering adjacent behavior
- `Grep` for any import of the domain objects or services this task depends on — identifies dependencies that must exist first

Also fetch any relevant wiki pages or in-repo glossary docs for this task's Bounded Context. Use these to ensure the implementation and test naming aligns with the team's Ubiquitous Language.

### 6. Draft the Technical Approach

Produce a concrete Technical Approach with actual file paths (not generic layer names):

- Architecture decisions: which layer owns what, which patterns to follow
- Data flow: how data moves from input to output
- Trade-offs: what alternatives were considered and why this approach was chosen
- Impacted Areas: concrete file paths for Backend, Frontend, Database, APIs

### 7. Review approach with user

Show the Technical Approach. Then ask "Does this align with how you'd approach it?" — header `Approach review`:

- **Yes — looks good, proceed** → continue with implementation
- **I have constraints to share** → adjust the approach first
- **Suggest an alternative** → describe a different approach

Apply changes. Then update the Task issue with the Technical Approach and Impacted Areas.

> See `references/issue-body-update-pattern.md` for the read-merge-write pattern. Use `/tmp/wtf.implement-task-<task_number>-approach.md` as the temp file.

```bash
gh issue edit <task_number> --body-file /tmp/wtf.implement-task-<task_number>-approach.md
```

### 8. Drive the TDD cycle

For each Gherkin scenario in the Task, work through them in order. Match the project's established test patterns discovered in step 5. Reference the Contracts & Interfaces section for exact request/response shapes.

1. **Write the failing test** for the scenario.
2. **Implement the minimum code** to make it pass.
3. **Refactor** if needed — keep functions under 40 lines, no deep nesting.
4. **Commit** — atomic semantic commit per `../references/commit-conventions.md`. Use the `Scenario:` and `Task:` trailers:

   ```bash
   git add <changed files>
   git commit -m "<type>(<scope>): <short description>

   Scenario: <scenario name>
   Task: #<task_number>"
   ```

5. Do not skip ahead — each scenario is a checkpoint.

Once all scenarios are green, run the full lint and type-check gate once across all changes. Check `package.json` for `lint`, `typecheck`, `type-check`, or `check` script keys and run whichever exist:

```bash
# e.g. npm run lint && npm run typecheck
```

Fix any issues before proceeding to coverage.

### 9. Verify coverage

Once all scenarios pass, confirm unit test coverage meets the minimum threshold for all new and modified code. Use the threshold specified in `docs/steering/QA.md` if it exists; default to 80% if the document is absent or does not define a threshold:

```bash
# Run the project's coverage command (check package.json scripts)
```

If coverage is below 80% on any new or modified file, add targeted tests before proceeding. Every public function must have at least one happy-path and one error-path test.

### 10. Update Test Mapping

Fill the Test Mapping table in the Task issue with concrete file paths:

| Gherkin Scenario  | Test file               | Status  |
| ----------------- | ----------------------- | ------- |
| `<scenario name>` | `<test file path:line>` | passing |

> See `references/issue-body-update-pattern.md` for the read-merge-write pattern. Re-fetch the body (do not reuse the temp file from step 6). Use `/tmp/wtf.implement-task-<task_number>-test-mapping.md` as the temp file.

```bash
gh issue edit <task_number> --body-file /tmp/wtf.implement-task-<task_number>-test-mapping.md
```

Print the updated Task issue URL.

### 11. Mark implemented and offer to continue

Add the `implemented` lifecycle label — this is mandatory regardless of invocation mode:

```bash
gh issue edit <task_number> --add-label "implemented"
```

If invoked from the loop (non-interactive mode), skip the ask below and return control to the loop.

Ask "What's next?" — header `Next step`:

- **Verify this Task** → run QA against the Gherkin scenarios (recommended next step, default)
- **Open a pull request** → create a PR for this branch
- **Implement another Task** → implement another Task for the same Feature

- **Verify this Task** → follow the `wtf.verify-task` process, passing the Task number in as context so the user is not asked for it again.
- **Open a pull request** → follow the `wtf.create-pr` process, passing the Task number and branch in as context.
- **Implement another Task** → restart this skill from step 1.
