---
name: wtf.write-task
description: This skill should be used when a user wants to create a task, write a ticket, decompose a feature into implementable work, break down a story, define a vertical slice for development, or write Gherkin scenarios — for example "create a task", "write a task for this feature", "break this feature into tasks", "define implementation work", or "add a sub-issue to this feature". Guides creation of a GitHub Task issue linked to a parent Feature and Epic, derives Gherkin acceptance scenarios from the Feature's ACs, enforces DDD ubiquitous language in scenarios, and checks for vertical-slice integrity and task dependencies.
---

# Write Task

Create a GitHub Task issue — the implementable unit of work. Core value: derives Gherkin scenarios directly from the parent Feature's Acceptance Criteria, so nothing gets lost in translation.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native sub-issue and dependency links are created in step 10.

Skip this step if invoked from `wtf.feature-to-tasks` or `wtf.write-feature` (the orchestrator already ran it), or on re-invocations within the same session (e.g. "Write next Task" loop in step 11).

### 1. Identify the parent Feature

Apply `../references/questioning-style.md` and ask "Which Feature does this Task belong to?" — header `Feature`, options from recent open issues labeled `feature`.

Walk Task → Feature → Epic per `../references/spec-hierarchy.md` to extract ACs, edge cases, user stories, Goal, and Context. If the Epic number was passed in as context (e.g. from an orchestrator), skip the parent walk and use it directly.

### 2. Name the task

**If a task description was passed in from the orchestrator** (e.g. from `wtf.feature-to-tasks` step 3 or `wtf.write-feature` step 11), present it directly as the proposal without offering source options:

> "Here's the task I'll write: _[task description]_. Does this look right, or would you like to adjust it?"

**If invoked from `wtf.write-feature` or `wtf.feature-to-tasks` context but no description was pre-filled**, ask "How would you like to define this task?" — header `Task source`:

- **Propose from ACs** → based on the Feature's Acceptance Criteria, existing tasks, and the Proposed Tasks checklist from the Feature body, propose the next concrete unimplemented task; state it clearly and ask "Does this task look right, or would you like to adjust it?" (default)
- **Describe myself** → ask "What is this task implementing?" (one sentence)

**If invoked standalone** (no Feature context), ask directly: "What is this task implementing?" (one sentence — e.g. "Add date range filter to search API")

### 3. Clarify ambiguity before proceeding

**Critically assess** whether you have enough information to define a single, focused, implementable task. Cross-check the user's input against the Feature's Acceptance Criteria, Edge Cases, and the Epic's Goal.

Topics that may require clarification (in priority order):

- Exact scope, entry/exit points
- Data contracts and error handling
- User roles and permissions
- Performance requirements
- Which **Aggregate(s)** does this Task modify or query?
- What **invariants** must hold after the change?
- What **domain Events** does this Task emit?
- If this Task touches an integration boundary, which Bounded Contexts are involved?

Apply `../references/questioning-style.md` for questions in this step. Stop when you have enough to write a complete draft — do not invent answers or assume away ambiguity.

### 4. Explore the codebase and wiki

Use the Agent tool to search the codebase for:

- Files and modules this task will touch (Impacted Areas)
- Existing patterns that inform Technical Approach
- Current interfaces at the integration point
- Existing tests covering adjacent behavior
- Dependencies (other tasks or systems that must exist first)
- The Aggregate classes or modules relevant to this task — note their invariant-enforcement logic
- Any existing domain Event definitions to reuse rather than invent

Also fetch any relevant wiki pages or in-repo glossary docs for this task's Bounded Context — check `docs/glossary.md`, GitHub wiki pages matching the context name, or any ADR files. Use these to verify Ubiquitous Language terms before writing Gherkin scenarios. If no wiki or glossary exists, proceed without comment.

**Cross-feature dependency scan:** Fetch sibling Features from the Epic's Feature Breakdown (extracted above) and the Proposed Tasks checklist from each. For sibling Feature bodies, use the per-level fetch in `../references/spec-hierarchy.md`. Then list already-created sibling tasks:

```bash
gh issue list --label task --state open --json number,title,body
```

Filter client-side to tasks whose body references a sibling Feature number. Note any whose scope overlaps with or must precede this task. Keep these candidate dependencies in mind for step 5.

### 5. Vertical slice assessment

Run Stage 1 of `../references/scope-gates.md` on the codebase findings from step 4. The Task-specific bar: touches every layer needed for one observable, user-facing behavior end-to-end (e.g. DB schema → service logic → API → UI) and is independently shippable without another unmerged task.

Evaluate:

- **Passes** → proceed.
- **Too broad** → propose smaller slices and confirm with the user.
- **Has dependencies** → identify them explicitly, including tasks from **sibling Features** in the same Epic (surfaced in step 4):
  - Tasks this task **depends on** (must be merged first — check if the code path exists yet; these may belong to the same Feature or a different Feature in the Epic)
  - Tasks that **depend on this task** (will be blocked until this merges)

For each cross-feature dependency found, state explicitly: "Task #X (in Feature #Y) must be completed first because [reason]." This makes the inter-feature ordering visible before committing to it.

Document all dependencies in the draft with GitHub issue references. For cross-feature deps, annotate the reason inline:

```markdown
## Dependencies

- Depends on #42 (Feature #12 — payment aggregate must exist before settlement status can be read)
- Blocks #51 (Feature #15 — notification email requires this task's event to be emitted)
```

### 6. Ask about contracts

Ask "Are there specific API contracts, events, or data schemas I should know about?" — header `Contracts`:

- Candidates from contract names or event names inferred from the codebase (e.g. existing API routes or domain events found in step 4)
- **None — proceed without** — skip this section (include only if nothing was found)

Use the answer to fill Contracts & Interfaces. Apply domain event naming rules from `../references/ddd-writing-rules.md` — past-tense domain names, named from the domain's perspective. If "none", stub events with the domain Event names derived in step 3 rather than leaving them blank.

### 7. Generate Gherkin from Feature ACs

For each Acceptance Criterion in the parent Feature:

- Write at least one Scenario (happy path)
- Write a failure or edge case Scenario if the Feature listed one

Reference the contracts gathered in step 6 when writing scenarios — use the exact domain Event names, API operation names, and field names from those contracts in Given/When/Then steps so the scenarios align precisely with the implementation contracts.

Gherkin rules (vocabulary rules from `../references/ddd-writing-rules.md`):

- Scenarios describe observable outcomes — not internal state
- Given/When/Then must be concrete and specific, not abstract
- Each scenario must survive internal refactors — it tests behavior, not implementation
- **Use only Ubiquitous Language** in steps — never reference implementation details (no "database row", "REST call", "HTTP 200", "mock", "table", "JSON field")
- **Domain actors** appear in Given steps ("Given a Fulfilment Manager has an open Purchase Order")
- **Domain Events** appear in When steps where they trigger behavior ("When the `PaymentSettled` event is received")
- **Business outcomes** appear in Then steps ("Then the Order is marked as Fulfilled") — not system states ("Then the orders table has status = 'fulfilled'")

### 8. Draft the Task

Load the TASK template per `../references/issue-template-loading.md` (verify existence, halt-or-setup if missing, read body below the second `---` delimiter). Fill in all sections with the gathered context. Replace the placeholder Gherkin scenarios with the ones generated in step 7.

Section-specific guidance:

- **Design Reference**: Link the Figma frame if one exists; otherwise write "N/A — no design for this task."
- **Observability**: Fill Logs, Metrics, and Alerts from the codebase patterns found in step 4. If the task has no production observability requirements, state "None required for this task" rather than leaving blank.
- **Rollout**: Fill Feature flag, Backward compatibility, and Data migration only if applicable; otherwise write "N/A" for each.

### 9. Scope gate

Run Stage 2 of `../references/scope-gates.md` on the written draft. Step 5 catches tasks that cannot ship alone; this step catches tasks that are simply too large.

**Task-level split signals** (heuristics — use judgement, not rigid thresholds):

- More than 4 Gherkin scenarios covering distinct, independently shippable user journeys — not multiple failure modes for the same behavior (four ways a payment validation can fail is one behavior, not four tasks).
- The Impacted Areas list spans more than 3–4 unrelated modules (e.g. API layer, database schema, frontend component, and a background job all bundled together).
- The Technical Approach describes more than 5 distinct implementation steps that could each be merged separately without breaking anything.
- The task contains both a schema/data migration and user-facing behavior — migrations are typically safer as a separate prior task.

**Split strategy by signal:**

- Migration + behavior → propose the migration as task A and the behavior as task B; task B depends on task A.
- Broad modules → split along deployment boundaries (backend task + frontend task, or data-layer + service-layer).
- Too many Gherkin scenarios → split by user journey, keeping each task's scenarios tightly grouped around one observable outcome.

If no signals fire, proceed to user review. If one or more fire, follow the Stage 2 procedure: state the signals, explain the risk (large tasks increase review friction, merge conflict surface, and rollback complexity), propose a concrete split using the matching strategy, and use the keep/split/stop ask from `../references/scope-gates.md`.

On **Split it** → return to step 2 with the chosen focused task description as the seed, reusing the same parent Feature. Carry forward codebase findings from step 4.

### 10. Review with user

Show the draft. Pay specific attention to Gherkin. Then ask "Do the scenarios cover everything from the Feature ACs?" — header `Review`:

- **Yes — looks complete** → proceed with issue creation
- **Missing edge cases** → add more scenarios
- **Other changes** → adjust something else

Apply edits, then proceed.

### 11. Create the issue and link to Feature

> Note: Write each body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise title from the task description. Pass in the task description and ask for a short title (no prefix emoji/label needed — that is added below). If the subagent returns nothing usable, derive the title directly from the one-sentence task description provided in step 2.

Create the Task issue:

```bash
# Ensure the label exists before creating the issue
gh label create task --color e4e669 --description "Implementable vertical slice of a Feature" 2>/dev/null || true

gh issue create --title "🛠 Task: <title>" --body-file /tmp/wtf.task-$(date +%s)-body.md --label "task"
```

Print the Task issue URL and number.

**Native relationships:** If `gh-sub-issue-available` (from step 0), link this Task as a child of its Feature:

```bash
gh sub-issue add <feature_number> <task_number>
```

If `gh-issue-dependency-available`, create a blocking link for each dependency identified in step 5:

```bash
# For each issue this Task depends on (same Feature or sibling Feature):
gh issue-dependency add <task_number> --blocked-by <blocker_number>
```

If either extension is unavailable, warn the user — do not write relationship references into the issue body.

### 12. Offer to continue

Count remaining tasks by fetching the Feature's Proposed Tasks checklist (named items without issue numbers) and comparing against already-created child tasks. Use `gh sub-issue list <feature_number>` per the cookbook in `../references/gh-setup.md`. Subtract created task count from total named items in the Proposed Tasks list to get remaining. Mention how many remain.

Ask "What's next?" — header `Next step`:

- **Design this Task** → add design coverage for this Task now (default)
- **Write next Task** → write the next Task for this Feature (N remaining — replace N with actual count)
- **Write a Feature** → write a new Feature for the same Epic
- **Stop here** → exit, no further action

- **Design this Task** → follow the `wtf.design-task` process, opening with: "Continue with task #<task_number>".
- **Write next Task** → restart from step 2, reusing the same Feature. If the Feature's Proposed Tasks list has named-but-uncreated items, propose the next one as the default.
- **Write a Feature** → proceed with `wtf.write-feature`, passing the Epic number in as context.
- **Stop here** → exit.

> Suggest clearing context before continuing if the conversation has grown long.
