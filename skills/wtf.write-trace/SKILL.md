---
name: wtf.write-trace
description: This skill should be used when a user wants to create a single Trace issue under a Feature — for example "create a trace", "write a trace for this feature", "add a trace to feature #42", "claim these scenarios", "start the Skeleton", or "add a Deepening Trace". A Trace claims one story and a declared subset of that story's Gherkin scenarios from the Feature body. Scenarios are canonical in the Feature and are never re-derived here. Use `wtf.feature-to-traces` to plan and create the full Trace set for a Feature. Not applicable to Epics, Features, or bug reports.
---

# Write Trace

Create a GitHub Trace issue — one pass over the Feature's Spine. The story and its scenarios already live in the Feature body. This skill selects a claim. It does not invent a spec.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available. That result controls whether native sub-issue and dependency links are created in step 10.

If invoked from `wtf.feature-to-traces` or `wtf.write-feature`, skip this step. The orchestrator already ran it. Also skip on re-invocations in the same session (e.g. "Next Trace in plan" loop in step 12).

### 1. Identify the parent Feature and read its Trace state

If the orchestrator passed a Feature number, use it. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Feature does this Trace belong to?"
- header: "Feature"
- options: from recent open Feature issues (list per `../references/issue-classification.md`)

Walk Feature → Epic per `../references/spec-hierarchy.md`. From the Feature body, extract:

- The **User Stories**, each with its ACs and its canonical Gherkin scenarios.
- The **Trace Plan** — the ordered checklist, when present.
- The **delivery override**, when present.

Then list existing child Traces with `gh sub-issue list <feature_number>` per the cookbook in `../references/gh-setup.md`. Read each child's Scenario Claim. Also recognize legacy Task children per the legacy reads in `../references/issue-classification.md`. Treat a legacy Task's Gherkin scenario names as claims already taken.

You now hold the **claim state**: which scenarios of each story are claimed, and by which Trace. This state drives step 2.

### 2. Select the story and the Scenario Claim

The story is given, not asked. Do not run independent intent questioning. Show the user:

1. The Feature's stories with their scenario names.
2. The Trace Plan entries, with issue numbers where created.
3. Which scenarios are already claimed, and by which Trace.

If the orchestrator passed a plan entry, present its story and claim as the proposal. Otherwise, if the Trace Plan has a next unclaimed entry, propose that entry as the default. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which scenarios does this Trace claim?"
- header: "Claim"
- options:
  - **Next plan entry** — the proposed entry's story and scenario names (default, when a plan entry exists)
  - **Select a different subset** → the user names a story and its scenarios

Validate the confirmed claim:

- The claim covers exactly **one** story. A claim that spans two stories fails step 4.
- The claim must not overlap any existing Trace's claim, including legacy Task claims. If it overlaps, show the conflict and re-ask.
- Compare the union of all claims — existing Traces, remaining plan entries, and this claim — against the story's full scenario list. If scenarios stay unclaimed and no remaining plan entry names them, warn the user. The story's partition is then incomplete. Suggest a later Deepening Trace or a plan update via `wtf.refine`. Do not block creation.

### 3. Set the Spine Position

Decide the position from the claim state:

- **Skeleton** — only when the Feature has no child Trace and no legacy Task child. The Skeleton is the first Trace. It claims the primary story's happy-path scenario, minimally, through every layer. Lean but complete — never a prototype.
- **Extension** — the first Trace of a further story on an existing Spine.
- **Deepening** — further scenarios of a story already started. Always cite the story it deepens. A Deepening Trace is never storyless.

Record **Builds on**: the issue numbers of the previous Trace in the plan order. The Skeleton builds on nothing. This replaces free-form dependency questioning — Traces within a Feature are sequential by design. The previous Trace becomes the blocked-by link in step 10.

### 4. Claim assessment

Run Stage 1 of `../references/scope-gates.md` on the selected claim. Trace bar: one story, one Scenario Claim, end-to-end through every layer, releasable on merge.

Trace-level split signals (heuristics — use judgment, not rigid thresholds):

- The claim spans more than one story.
- The claim is too large for one agent pass — many scenarios with distinct setup, or scenarios that touch unrelated failure domains.

If a signal fires, split by **depth**: re-partition the claim into a smaller first claim plus Deepening Traces. Never split by layer (model → API → UI). Present the re-partition and confirm with the user.

### 5. Explore the codebase and glossary

Use the Agent tool to search the codebase for:

- Current interfaces at the integration points the claim touches (for Contracts & Interfaces).
- Existing domain Event definitions to reuse rather than invent.
- Observability patterns (logs, metrics, alerts) near the touched code paths.

Also fetch `docs/glossary.md`, wiki pages for the Bounded Context, or ADR files when they exist. Use these to verify Ubiquitous Language terms. If none exist, proceed without comment.

Do not design the implementation here. The Technical Approach is filled by `wtf.implement-trace` at implementation time.

### 6. Ask about contracts

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Are there specific API contracts, events, or data schemas I should know about?"
- header: "Contracts"
- options:
  - Candidates from contract or event names found in step 5, plus the Feature's Domain Events
  - **None — proceed without** — skip this section (include only if nothing was found)

Use the answer to fill Contracts & Interfaces. Apply domain event naming rules from `../references/ddd-writing-rules.md`. If "none", stub events with the Feature's Domain Event names rather than leaving them blank.

### 7. Draft the Trace

Apply strict STE per `../references/ste-writing.md` before writing any durable body.

Load the TRACE template per `../references/issue-template-loading.md` (verify existence, halt-or-setup if missing, read body below the second `---` delimiter). Fill the sections:

- **Story** — copy it verbatim from the Feature. Do not re-derive it. Do not reword it.
- **Scenario Claim** — list the claimed scenario names. Below them, fill the collapsed `<details>` block with the claimed scenarios copied verbatim from the Feature body. Set the summary line to "Claimed scenarios — synced from Feature #<feature_number> — edit there, not here".
- **Spine Position** — the position from step 3 and the Builds-on Trace numbers. A Deepening Trace names the story it deepens.
- **Contracts & Interfaces** — from step 6.
- **Technical Approach** — leave the placeholders. `wtf.implement-trace` fills this section.
- **Observability** — fill from the patterns found in step 5. If the Trace has no production observability need, state "None required for this trace".
- **Definition of Done** — keep the template checklist unchanged.
- **Test Mapping** — one row per claimed scenario, with the scenario name filled and the test file blank.

Run the DDD Language Guard from `../references/ddd-writing-rules.md` on any new prose you wrote. Copied scenarios and the copied story are canonical — leave them untouched even when they would fail the guard. Flag such a failure to the user as a Feature-body concern for `wtf.refine`.

### 8. Scope gate

Run Stage 2 of `../references/scope-gates.md` on the written draft. Drafting sometimes reveals a claim that is larger than it looked.

If a split signal fires, follow the Stage 2 procedure. State the signals. Propose a **depth** split: a re-partitioned Scenario Claim — a smaller claim now, Deepening Traces for the rest. Never propose layer slices. Use the keep/split/stop ask from `../references/scope-gates.md`.

On **Split it** → return to step 2 with the narrowed claim as the proposal. Carry forward the codebase findings from step 5.

### 9. Review with user

Show the draft. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does the claim and the draft look right?"
- header: "Review"
- options:
  - **Looks good — create the issue** → proceed with issue creation
  - **Change the claim** → return to step 2
  - **Other changes** → adjust something else

Apply edits. Then proceed.

### 10. Create the issue and link it

> Note: Write the body to a temp file (`$BODY`) with the Write tool. Then create it through the gh body helper so multi-line UTF-8 content survives on Windows. See `../references/gh-body-helper.md`.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise, domain-language title from the story and the claim. Pass in the story and the claimed scenario names. Ask for a short title (no prefix emoji/label needed — that is added below). If the subagent returns nothing usable, derive the title from the story and position (e.g. "Skeleton — <story summary>").

Create the Trace issue:

```bash
# $BODY is the temp file you wrote the filled body to with the Write tool.
# Create the issue WITHOUT a kind label — the classify step below sets the kind.
python3 .wtf/gh-body.py create --title "☄️ Trace: <title>" --body-file "$BODY"
```

Print the Trace issue URL and number.

**Classify the issue as `Trace`.** Set `TYPE="Trace"` and `ISSUE_NUMBER=<number from the URL>`. Then run the **Classify a new issue** block from `../references/issue-classification.md` (resolve `$WTF_CLASS` once first). In `types` mode it sets the native GitHub issue type and leaves labels free for your own segmentation. In `labels` mode it applies the `trace` label. Either way the Trace is classified.

**Native relationships:** If `gh-sub-issue-available` (from step 0), link this Trace as a child of its Feature:

```bash
gh sub-issue add <feature_number> <trace_number>
```

If `gh-issue-dependency-available` and this Trace builds on a previous Trace (step 3), create the sequential blocking link:

```bash
gh issue-dependency add <trace_number> --blocked-by <previous_trace_number>
```

If either extension is unavailable, warn the user. Do not write relationship references into the issue body.

### 11. Update the Trace Plan in the Feature

Record the created issue number in the Feature's Trace Plan. Use the read → modify → write flow from `../references/gh-body-helper.md`:

1. `python3 .wtf/gh-body.py read <feature_number>` — fetch the current body to a temp file.
2. With the Edit tool, append ` #<trace_number>` to the matching Trace Plan entry. Change nothing else.
3. `python3 .wtf/gh-body.py edit <feature_number> --body-file "<path>"` — push it back.

If the Feature has no Trace Plan, or no entry matches this claim, add an entry in plan order instead. Name the story, the Scenario Claim, and what it adds to the Spine. Tell the user the plan was extended.

### 12. Offer to continue

Count the Trace Plan entries that have no issue number yet. Mention how many remain.

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Next Trace in plan** → write the next unclaimed plan entry (N remaining — replace N with the actual count) (default when entries remain)
  - **Implement now** → follow `wtf.implement-trace` with this Trace number
  - **Stop here** → exit, no further action

- **Next Trace in plan** → restart from step 2, reusing the same Feature. Propose the next unclaimed plan entry as the default.
- **Implement now** → proceed with the `wtf.implement-trace` skill, passing the Trace number in as context.
- **Stop here** → exit.

> Suggest clearing context before continuing if the conversation has grown long.
