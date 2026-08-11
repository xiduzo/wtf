---
name: wtf.feature-to-traces
description: This skill should be used when a user wants to plan and create the complete set of Traces for a Feature — for example "plan all traces", "create the traces for feature #42", "break this feature into traces", "execute the trace plan", or when chained from wtf.write-feature or wtf.epic-to-features. It validates the Feature's Trace Plan (or derives one for older Features), then creates the Trace issues in spine order with sequential dependency links. Supports two planning modes — `guided` (per-item confirmation) and `flow` (one consolidated review) — passed as an argument or read from `.wtf/config.json`. Use `wtf.write-trace` to write a single Trace in isolation.
argument-hint: "[feature-number] [guided|flow]"
---

# Feature to Traces

Turn a Feature's Trace Plan into Trace issues. The plan and the scenarios are canonical in the Feature body. This skill validates the plan, fills gaps, and executes it. It does not re-derive work from Acceptance Criteria when a plan exists.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available. That result controls whether native sub-issue and dependency links are created downstream.

Skip this step if gh-setup was already confirmed this session (e.g. when chained from `wtf.write-feature` or `wtf.epic-to-features`).

### 0b. Resolve the planning mode

Run the **Resolve the mode** block from `../references/planning-mode.md`. An explicit `guided` or `flow` argument in the invocation wins over config. `$WTF_PLAN` shapes steps 2–5 below. Every quality gate runs in both modes.

If invoked from an orchestrator, use the mode it passed in. Do not re-resolve.

### 1. Identify the Feature and read its Trace state

If a Feature number was passed in as context, use it. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Feature are you planning Traces for?"
- header: "Feature"
- options: from recent open Feature issues (list per `../references/issue-classification.md`)

Walk Feature → Epic per `../references/spec-hierarchy.md`. From the Feature body, extract:

- The **User Stories**, each with its ACs and its canonical Gherkin scenarios.
- The **Trace Plan**, when present.
- The **delivery override**, when present.

Then list existing children with `gh sub-issue list <feature_number>` per the cookbook in `../references/gh-setup.md`:

- **Child Traces** — read each one's Scenario Claim.
- **Legacy Task children** — recognize them per the legacy reads in `../references/issue-classification.md`. Treat each legacy Task's Gherkin scenario names as claims already taken. Match them against the story scenarios by name where possible. Do NOT recreate that work as new Traces. When a match is fuzzy, ask the user which scenarios the Task covers.

You now hold the **claim state**: which scenarios of each story are claimed, and by which issue.

### 2. Validate the Trace Plan (when present)

If the Feature body has a Trace Plan, that plan **is** the list. Do not re-derive it. Validate it:

1. **Story named** — every entry names exactly one story.
2. **Partition** — for each story, the entries' claims plus existing issue claims cover all its scenarios, with no overlap.
3. **One Skeleton, first** — exactly one Skeleton entry exists, and it is item 1. If a child Trace or legacy Task already laid the Spine, no Skeleton entry may remain open.
4. **Numbers match** — checked entries carry issue numbers that exist as children. Unchecked entries with numbers point at open child Traces.

For each gap, propose a concrete fix — a re-partitioned claim, a reordered list, a named story, a corrected checkbox. In `guided` mode, confirm each fix with the user as you find it. In `flow` mode, collect all fixes and confirm them in the step 4 review. Write confirmed fixes into the Feature body in step 4.

If the plan is valid and complete, say so in one line and go to step 4.

### 3. Derive a Trace Plan (when absent)

An older Feature may predate the Trace model. When the body has no Trace Plan, derive one — 1:1 from the stories and scenarios, plus ordering:

1. **Backfill scenarios if needed.** If a story has no canonical Gherkin scenarios (legacy Feature shape), derive scenario names from its ACs and the Edge Cases first. Write full Gherkin per `../references/ddd-writing-rules.md`. These go into the Feature body with the plan — the Feature stays canonical.
2. **Pick the primary story.** The Skeleton claims the primary story's happy-path scenario. Propose the story that most directly delivers the Feature's Goal. In `guided` mode, confirm the choice with the user. In `flow` mode, derive it and surface it in the step 4 review.
3. **Order the entries.** Item 1 is the Skeleton — the primary story's happy path, minimally, through every layer. Then Extension entries for further stories. Then Deepening entries for remaining scenarios — edge cases, failure modes — each citing its story. A small story gets one entry that claims all its scenarios.
4. **Never slice by layer.** A legacy `Proposed Tasks` checklist in the body is not a Trace Plan. If it slices by layer (model → API → UI), do not adopt it. Say so, and derive depth-ordered entries instead. A story too big for one agent pass splits into a Skeleton plus Deepening entries — the escape valve is depth, not layers.

Each entry names its story, its Scenario Claim (scenario names), and what it adds to the Spine, in the Trace Plan shape from the FEATURE template.

### 4. Confirm the plan and write it to the Feature

Show the resulting plan — validated, fixed, or newly derived — with the claim state per story. This review runs in **both** planning modes. In `flow` mode it is the one consolidated review: plan fixes, backfilled scenarios, the primary-story choice, and the creation batch, all in one pass.

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this Trace Plan look right? Traces will be created in this order."
- header: "Trace Plan"
- options:
  - **Looks good** → write the plan and start creating
  - **Make changes** → adjust entries, claims, or order first

Apply changes. Then, if the plan or the scenarios changed against the Feature body, write them back with the read → modify → write flow from `../references/gh-body-helper.md`:

1. `python3 .wtf/gh-body.py read <feature_number>` — fetch the current body to a temp file.
2. With the Edit tool, replace only the Trace Plan section (and any backfilled Scenarios blocks). Change nothing else.
3. `python3 .wtf/gh-body.py edit <feature_number> --body-file "<path>"` — push it back.

Apply strict STE per `../references/ste-writing.md` to the written plan entries.

### 5. Create the Trace issues in plan order

Work through the plan top to bottom. Skip entries that already carry an issue number. For each remaining entry:

1. Announce: "Creating Trace [N/total]: _[entry summary]_".
2. Follow the `wtf.write-trace` process with everything pre-answered:
   - The Feature number and claim state (skip write-trace steps 0–1).
   - The plan entry as the confirmed story and Scenario Claim (write-trace step 2 needs no ask).
   - The Spine Position and Builds-on from the plan order (write-trace step 3 needs no ask).
   - The previous entry's issue number as the blocked-by link. The Skeleton has no blocker. If legacy Task children laid the Spine, the first new Trace also has no blocker — note the legacy base in its body.
   - Each created Trace is classified, linked as a sub-issue of the Feature, and recorded in the Trace Plan checklist per write-trace steps 10–11.
3. In `guided` mode, before the next entry, call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Trace [N] created. Continue to Trace [N+1]: _[next entry summary]_?" (replace with actual values)
   - header: "Continue?"
   - options:
     - **Yes, continue** → proceed to the next entry (default)
     - **Pause here** → exit. Print a summary of created and remaining entries. Suggest `/clear` before resuming
     - **Skip this trace** → leave the entry unchecked and move on. Warn that the story's partition stays incomplete until it is created
4. In `flow` mode, skip the continue gates — the step 4 review already confirmed the batch. Drafting may fan out to sub-agents per `../references/subagent-protocol.md`. Sub-agents draft bodies only. They never create issues, and they never call `AskUserQuestion`. The orchestrator creates the issues **sequentially in plan order**, so issue numbers, blocked-by links, and plan checkboxes stay consistent. Collect `NEEDS_INPUT` blocks and ask them in one batched round.

The scope gates inside the write-trace process still run in both modes. A firing split signal is a genuine ambiguity — it escalates even in flow.

### 6. Completion

When every plan entry is created (or skipped), print a summary:

> "Feature #<feature_number> Trace Plan executed.
> Created: [entries with issue numbers, in spine order]
> Skipped: [list if any]
> Claim state: [per story — fully partitioned, or naming the unclaimed scenarios]"

If any story's scenarios stay unclaimed, recommend a plan update via `wtf.refine`.

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Implement first Trace** → follow `wtf.implement-trace` with the Skeleton's issue number (default)
  - **Run the loop** → follow `wtf.loop` to execute the Trace sequence autonomously
  - **Stop here** → exit. No further action

> Suggest `/clear` before continuing if the conversation has grown long.
