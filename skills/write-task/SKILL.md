---
name: wtf:write-task
description: This skill should be used when a user wants to create a task, write a ticket, decompose a feature into implementable work, break down a story, define a vertical slice for development, or write Gherkin scenarios — for example "create a task", "write a task for this feature", "break this feature into tasks", "define implementation work", or "add a sub-issue to this feature". Guides creation of a GitHub Task issue linked to a parent Feature and Epic, derives Gherkin acceptance scenarios from the Feature's ACs, enforces DDD ubiquitous language in scenarios, and checks for vertical-slice integrity and task dependencies.
---

# Write Task

Create a GitHub Task issue — the implementable unit of work. Core value: derives Gherkin scenarios directly from the parent Feature's Acceptance Criteria, so nothing gets lost in translation.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native sub-issue and dependency links are created in step 10.

Skip this step if invoked from `wtf:feature-to-tasks` or `wtf:write-feature` (the orchestrator already ran it), or on re-invocations within the same session (e.g. "Write next Task" loop in step 11).

### 1. Identify the parent Feature

Search for recent open issues with label `feature` to populate options. Call `AskUserQuestion` with `question: "Which Feature does this Task belong to?"`, `header: "Feature"`, and `options` pre-filled with 1–2 likely open Feature issue references inferred from GitHub search (e.g. recent open issues labeled `feature`).

Fetch the Feature, then find its parent Epic via the sub-issue hierarchy:

```bash
gh issue view <feature_number>                                         # ACs, edge cases, user stories
gh sub-issue list <feature_number> --relation parent                   # find parent Epic number
gh issue view <epic_number>                                            # Goal, Context
```

If the Epic number was passed in as context (e.g. from an orchestrator), skip the `gh sub-issue list` call and use it directly.

### 2. Name the task

**If a task description was passed in from the orchestrator** (e.g. from `wtf:feature-to-tasks` step 3 or `wtf:write-feature` step 11), present it directly as the proposal without offering source options:

> "Here's the task I'll write: _[task description]_. Does this look right, or would you like to adjust it?"

**If invoked from `write-feature` or `feature-to-tasks` context but no description was pre-filled**, call `AskUserQuestion` with:

- `question`: "How would you like to define this task?"
- `header`: "Task source"
- `options`: `[{label: "Propose from ACs", description: "Let me propose a task based on the Feature ACs (default)"}, {label: "Describe myself", description: "I'll describe the task myself"}]`

- **Propose from ACs** → based on the Feature's Acceptance Criteria, existing tasks, and the Proposed Tasks checklist from the Feature body, propose the next concrete unimplemented task. State it clearly and ask: "Does this task look right, or would you like to adjust it?"
- **Describe myself** → ask: "What is this task implementing?" (one sentence)

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

**Questioning style:**

- Ask questions **one at a time**. Wait for the answer before asking the next.
- **Always use the `AskUserQuestion` tool for every question** — including open-ended ones like "What are the entry/exit points?" or "What invariants must hold?". For each question, infer 1–2 likely answers from codebase research (e.g. Aggregate names found in the code, event names from existing domain events) and pass them as `options`. The UI automatically appends an "Other (type your answer)" escape hatch — do NOT add one manually.
- Stop when you have enough to write a complete draft. Do not invent answers or assume away ambiguity.

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

**Cross-feature dependency scan:** Fetch the sibling Features from the Epic's Feature Breakdown checklist (already fetched above), then fetch the Proposed Tasks checklist from each sibling Feature's issue body:

```bash
# For each sibling Feature number extracted from the Epic's Feature Breakdown:
gh issue view <sibling_feature_number> --json number,title,body
```

Extract the task names and issue numbers (where linked) from each Feature's Proposed Tasks section. Then fetch the full body of any already-created sibling tasks to understand their scope:

```bash
gh issue list --label task --state open --json number,title,body
```

Filter this list client-side to tasks whose body references a sibling Feature number. Note any whose scope overlaps with or must precede this task. Keep these candidate dependencies in mind for step 5.

### 5. Vertical slice assessment

A task must be a **vertical slice**: it touches all layers needed to deliver one observable, user-facing behavior end-to-end (e.g. DB schema → service logic → API → UI). It must be independently shippable without requiring another unmerged task to be complete first.

This assessment runs on the **codebase findings from step 4** — before a draft is written. It catches structural problems early. A second, draft-level scope check runs at step 9 after the written artefact is complete.

Evaluate whether this task meets that bar:

- **Passes** → proceed.
- **Too broad** → propose splitting into smaller slices; present the breakdown and ask the user to confirm before continuing.
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

Call `AskUserQuestion` with `question: "Are there specific API contracts, events, or data schemas I should know about?"`, `header: "Contracts"`, and `options` pre-filled with 1–2 contract names or event names inferred from the codebase (e.g. existing API routes or domain events found in step 4). Include `{label: "None — proceed without", description: "Skip this section"}` as an option if nothing was found.

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

Use the issue body structure from @.github/ISSUE_TEMPLATE/TASK.md (ignore the YAML frontmatter — use only the markdown body below the second `---` delimiter). Fill in all sections with the gathered context. Replace the placeholder Gherkin scenarios with the ones generated in step 7.

Section-specific guidance:

- **Design Reference**: Link the Figma frame if one exists; otherwise write "N/A — no design for this task."
- **Observability**: Fill Logs, Metrics, and Alerts from the codebase patterns found in step 4. If the task has no production observability requirements, state "None required for this task" rather than leaving blank.
- **Rollout**: Fill Feature flag, Backward compatibility, and Data migration only if applicable; otherwise write "N/A" for each.

### 9. Scope gate

This is a final structural guardrail on the **written draft** — distinct from step 5's vertical-slice check on codebase findings. Both can fire independently: step 5 catches tasks that cannot ship alone; this step catches tasks that are simply too large. Frame this to the user as a structural check, not a challenge to their earlier answers.

Look for these **Task-level split signals** (heuristics — use judgement, not rigid thresholds):

- There are more than 4 Gherkin scenarios covering distinct, independently shippable user journeys — not multiple failure modes for the same behavior (four ways a payment validation can fail is one behavior, not four tasks)
- The Impacted Areas list spans more than 3–4 unrelated modules (e.g. API layer, database schema, frontend component, and a background job all bundled together)
- The Technical Approach describes more than 5 distinct implementation steps that could each be merged separately without breaking anything
- The task contains both a schema/data migration and user-facing behavior — migrations are typically safer as a separate prior task

**Split strategy by signal:**
- Migration + behavior signal → always propose the migration as task A and the behavior as task B; task B depends on task A.
- Broad modules signal → propose splits along deployment boundaries (e.g. backend task + frontend task, or data-layer task + service-layer task).
- Too many Gherkin scenarios → split by user journey, keeping each task's scenarios tightly grouped around one observable outcome.

If **no signals are present**, proceed to the user review.

If **one or more signals fire**, present your case: state which signals you found, explain the risk (large tasks increase review friction, merge conflict surface, and rollback complexity), and propose a concrete split using the matching strategy above (two focused task descriptions in one sentence each). Then call `AskUserQuestion` with:

- `question`: "I think this Task may be too broad — see my reasoning above. How do you want to proceed?"
- `header`: "Scope check"
- `options`:
  1. `{label: "Keep the original draft", description: "Proceed with the current draft without splitting"}`
  2. `{label: "Split it", description: "Start over with one of the proposed smaller Tasks"}`
  3. `{label: "Stop here", description: "Exit without creating — I'll handle the split manually"}`

- **Keep the original draft** → proceed to the user review without further comment.
- **Split it** → return to step 2 with the chosen focused task description as the seed, reusing the same parent Feature. Carry forward codebase findings from step 4.
- **Stop here** → exit.

### 10. Review with user

Show the draft. Pay specific attention to Gherkin. Then call `AskUserQuestion` with `question: "Do the scenarios cover everything from the Feature ACs?"`, `header: "Review"`, and `options: [{label: "Yes — looks complete", description: "Proceed with issue creation"}, {label: "Missing edge cases", description: "I want to add more scenarios"}, {label: "Other changes", description: "I want to adjust something else"}]`.

Apply edits, then proceed.

### 11. Create the issue and link to Feature

> Note: Write each body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5` model to generate a concise title from the task description. Pass in the task description and ask for a short title (no prefix emoji/label needed — that is added below). If the subagent returns nothing usable, derive the title directly from the one-sentence task description provided in step 2.

Create the Task issue:

```bash
# Ensure the label exists before creating the issue
gh label create task --color e4e669 --description "Implementable vertical slice of a Feature" 2>/dev/null || true

gh issue create --title "🛠 Task: <title>" --body-file /tmp/task-body.md --label "task"
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

Count remaining tasks by fetching the Feature's Proposed Tasks checklist (named items without issue numbers) and comparing against already-created child tasks via the sub-issue hierarchy:

```bash
gh sub-issue list <feature_number>
```

Subtract created task count from total named items in the Proposed Tasks list to get remaining. Mention how many remain.

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Design this Task", description: "Add design coverage for this Task now (default)"}, {label: "Write next Task", description: "Write the next Task for this Feature (N remaining)"}, {label: "Write a Feature", description: "Write a new Feature for the same Epic"}, {label: "Stop here", description: "Exit — no further action"}]`

_(Replace N with actual count.)_

- **Design this Task** → follow the `wtf:design-task` process, opening with: "Continue with task #<task_number>".
- **Write next Task** → restart from step 2, reusing the same Feature. If the Feature's Proposed Tasks list has named-but-uncreated items, propose the next one as the default.
- **Write a Feature** → proceed with `wtf:write-feature`, passing the Epic number in as context.
- **Stop here** → exit.

> Suggest clearing context before continuing if the conversation has grown long.
