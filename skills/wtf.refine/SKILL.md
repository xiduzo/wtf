---
name: wtf.refine
description: Use when new insights change the scope, acceptance criteria, scenarios, domain language, or technical constraints of an existing Epic, Feature, or Trace — for example "refine epic #10", "re-aim feature #24", "the trace revealed the seam is wrong", "update this trace with the new requirements", "we got new feedback on feature #24", "incorporate these comments into the spec", or to re-aim a Feature's Trace Plan after a Trace landed. Also triggered when new Figma designs, documents, or GitHub comments reveal that the current spec is out of date. Accepts insights from CLI text, GitHub comments, referenced files or URLs, and conversation context. Detects the issue kind automatically (legacy Task issues read as legacy Traces), smart re-validates only what changed, shows a section-by-section before/after diff, posts an audit trail comment, warns about stale lifecycle labels, and cascades scenario edits to the Traces that claim them. Runs headless as wtf.loop's Re-aim step after each verified Trace.
---

# Refine

Update an existing Epic, Feature, or Trace issue from new insights.

This skill merges insights from any source. It finds which sections change. It re-runs only the validations those changes need. It shows a precise diff before it writes. It cascades scenario edits to claiming Traces so nothing goes stale.

This skill is also the single **Re-aim** mechanism. After a Trace lands, the Feature's Trace Plan absorbs what the Trace revealed. It has two entry points. A human runs it interactively. `wtf.loop` runs it headlessly after each verified Trace — see **Headless mode** at the end of this file.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check).
Stop if `gh` is not installed or not authenticated.
Note whether the extensions are available.
They are used in step 1 (hierarchy fetch) and step 9 (cascade).

Skip this step if gh-setup was already confirmed this session.

### 1. Identify the issue and its hierarchy

If an issue number was passed in as context or a CLI argument, use it directly.
Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which issue are you refining?"
- header: "Issue"
- options: from recently-updated open issues across all WTF kinds (epic, feature, trace — plus legacy task), inferred from:

```bash
# Resolve $WTF_CLASS once — see ../references/issue-classification.md.
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search 'state:open (type:"Epic" OR type:"Feature" OR type:"Trace" OR type:"Task")' --json number,title --limit 10
else
  gh issue list --label "epic,feature,trace,task" --state open --json number,title,labels --limit 10
fi
```

Fetch the issue:

```bash
gh issue view <issue_number> --json number,title,body,labels,comments,updatedAt
```

**Detect the issue kind** — follow the **Detect the kind of an existing issue** block in `../references/issue-classification.md`.
It reads the native issue type in `types` mode and the kind label in `labels` mode.
Compare case-insensitively:
- `Epic` → kind = **Epic**
- `Feature` → kind = **Feature**
- `Trace` → kind = **Trace**
- `Task` → kind = **legacy Trace**. Tell the user that this is a legacy Task issue and that you treat it as a legacy Trace. Route it through the Trace validation path. A legacy Trace carries its own canonical Gherkin in its body. The scenario canonicality guard (step 3) does not apply to it.
- Indeterminate (no type set and no kind label) → call `AskUserQuestion` (per `../references/questioning-style.md`):
  - question: "I couldn't detect the kind of this issue. What kind is it?"
  - header: "Issue kind"
  - options: **Epic** / **Feature** / **Trace**

**Fetch the hierarchy** for context and cascade planning:

```bash
# Parent (always fetch — needed for context)
gh sub-issue list <issue_number> --relation parent

# Children (needed for cascade planning in step 9)
gh sub-issue list <issue_number>
```

For the parent issue, fetch its body.
Extract goal, bounded context, and success metrics.
These show whether a child change conflicts with the parent intent.

If the issue is a Trace, the parent Feature body also holds the canonical scenarios and the Trace Plan.
Keep it at hand for steps 3–4.

### 2. Gather insights from all sources

Merge insights from every available source into one list.
Process all sources in parallel:

**a. CLI argument / conversation context**

If the user passed insight text in the invocation (e.g. `refine #42 "scope changed — exclude mobile"`), treat that as the primary insight.
If the insight is a landed Trace (e.g. `re-aim feature #24 after trace #57`), read the landed Trace issue.
Its Revealed learnings, verify results, and PR link are the insight sources.
If nothing was passed, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What changed or what new insight should I incorporate?"
- header: "Insight"
- options: from plausible changes inferred from recent issue comments (e.g. the last comment's key point)

**b. GitHub comments since last body edit**

Extract comments posted after the issue body was last edited:

```bash
gh issue view <issue_number> --json comments,updatedAt \
  --jq '.updatedAt as $bodyUpdatedAt | .comments[] | select(.createdAt > $bodyUpdatedAt) | "[\(.author.login)] \(.body)"'
```

Read each comment.
Extract actionable insights.
Discard discussion noise ("+1", "agreed", "thanks").
Synthesise into concrete change signals (e.g. "Stakeholder comment: settlement must support multi-currency").

**c. Referenced files**

If the user referenced any file paths or URLs in the CLI argument or conversation, read them now:

- File paths → use the Read tool
- URLs → use the WebFetch tool (if available) or ask the user to paste the relevant content

Extract the relevant change signals from each document.

**d. Consolidate**

Merge all signals into a numbered list of insights.
Present them briefly to the user:

> "I found [n] insight(s) to incorporate:
> 1. [insight summary]
> 2. [insight summary]
> ..."

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this capture everything you want to incorporate?"
- header: "Insights"
- options:
  - **Yes — proceed** → continue with these insights
  - **Add more** → I have additional context to provide
  - **Remove one** → some of these are not relevant

Apply any adjustments before you continue.

### 3. Classify the changes

For each insight, determine which sections of the issue it affects.
Also determine what type of change it is.
This classification drives which validations run in step 4.
It also drives which sections are rewritten in step 5.

**Change types and their affected sections:**

| Change type | Affected (Epic) | Affected (Feature) | Affected (Trace) |
|---|---|---|---|
| Scope narrowed / expanded | Goal, Success Metrics, Feature Breakdown | User Stories, ACs, Scenarios, Edge Cases, Trace Plan | Scenario Claim, Spine Position |
| New constraint | Risks, Bounded Context | ACs, Scenarios, Edge Cases | Contracts, Observability |
| Domain language correction | Context, Goal, Bounded Context | Capability name, User Stories, ACs, Scenarios | Contracts, Technical Approach |
| New stakeholder / actor | Context, Goal | Capability name, User Stories | — |
| New domain event | — | Domain Events, Scenarios (When steps) | Contracts |
| Technical constraint | — | Edge Cases | Contracts, Technical Approach |
| Deadline / priority | Risks | — | — |
| Trace landed — re-aim | — | Trace Plan (and Scenarios, when the Trace discovered new ones) | — |

Notes on the Trace column:
- A Trace has **no canonical Gherkin of its own**. Scenario-text changes happen on the Feature. A Trace-level refinement touches its Scenario Claim (which scenarios it names), Spine Position, Contracts, and Technical Approach.
- **Scenarios** and **Trace Plan** are Feature sections. A scenario edit on a Feature cascades to every Trace whose Scenario Claim names it (step 9): the synced courtesy copy is refreshed and stale lifecycle labels are stripped.
- **Legacy Trace**: map the Trace column onto its legacy sections — Gherkin, Functional Description, Contracts, Technical Approach. Its body is canonical for its own Gherkin. Edit the Gherkin in place.

**Trace landed — re-aim.** The landed Trace's learnings re-aim the remaining plan.
Affected section: the Feature's Trace Plan.
Allowed moves: reorder the remaining entries, re-batch them, move scenarios between remaining entries, and add newly discovered scenarios to the right story and to plan entries.
Landed (checked) entries stay untouched.
Validation: the partition re-check in step 4.

**Scenario canonicality guard.** If an insight would edit scenario text on a **Trace** — the synced `<details>` copy — stop.
That copy is a courtesy projection.
The canonical scenarios live on the parent Feature.
Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "This change edits scenario text, which is canonical on Feature #<n>. How should I proceed?"
- header: "Canonical scenarios"
- options:
  - **Refine the Feature** → re-target this refinement at the parent Feature. The cascade (step 9) then refreshes this Trace's synced copy. (default)
  - **Edit the claim only** → the change is which scenarios this Trace claims (names), not their text
  - **Cancel** → exit without changes

Exception: legacy Traces hold their own Gherkin — the guard does not fire for them.

Produce a **change map** — a structured internal summary:

```
Change map:
  scope changed:        yes
  DDD language changed: no
  ACs changed:          yes
  Scenarios affected:   yes  (canonical on the Feature — because ACs changed)
  Trace Plan affected:  yes  (claims may need re-partition)
  Contracts affected:   no
  Sections to rewrite:  [Goal, Success Metrics] / [User Stories, ACs, Scenarios, Edge Cases, Trace Plan] / [Scenario Claim, Contracts]
```

### 4. Re-run relevant validations only

Using the change map from step 3, run only the validations that apply.
Skip the rest.
Do not re-validate unchanged sections.

**Scope changed → Vertical slice + Scope gate**

Re-run both stages defined in `../references/scope-gates.md` on the refined intent, then on the rewritten sections.
The per-level split signals live in the matching write-* skill:

- Epic → `wtf.write-epic` step 7
- Feature → `wtf.write-feature` step 9
- Trace → `wtf.write-trace`

A Trace split is by depth — a Skeleton plus Deepening Traces — never by layer.
If a split signal fires on the **refined** issue, present it as a refinement concern (not a blocker).
Use the same keep / split / stop ask the write-* skill uses (see `../references/scope-gates.md`).

**Domain language changed → DDD Language Guard**

Re-run the checks from `../references/ddd-writing-rules.md` on any section whose text is being rewritten.
Flag and correct violations silently.
Note corrections in the diff (step 5).

Apply strict STE per `../references/ste-writing.md` before writing any durable body (rewritten sections and the audit trail comment).

**ACs changed (Feature) → Scenario re-derivation**

The scenarios are canonical on the Feature, so re-derive them here.
Re-derive only the scenarios that map to the changed AC(s).
Keep unchanged scenarios exactly as they are.
Mark the Trace Plan as potentially stale.
Traces whose Scenario Claims name a changed scenario become cascade items (step 9).
For a legacy Trace, re-derive its in-body Gherkin the same way.

**Scenario Claim changed (Trace) → Claim re-check**

Verify that every claimed name exists on the parent Feature's story.
Verify that the story's claims across all its Traces still cover its scenarios exactly once — full cover, no overlap.

**Trace landed — re-aim → Partition re-check**

After the Trace Plan rewrite, verify:

1. The remaining claims plus the landed Traces' claims cover each story's scenarios exactly once — full cover, no overlap.
2. The plan has exactly one Skeleton.
3. The spine order is sound — every entry builds on landed Traces or on earlier entries.

### 5. Draft the section updates and show a diff

Produce the updated content for each section in the change map.
Do not touch sections that are not in the change map.

Present a **section-by-section before/after diff** for every changed section.
Format each section's diff as:

```
## [Section name]

BEFORE:
  [original text]

AFTER:
  [updated text]
```

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this diff look right?"
- header: "Diff review"
- options:
  - **Looks good — apply it** → write the changes to the issue
  - **I have corrections** → adjust one or more sections
  - **Start over** → the insights were wrong. Re-describe what changed.

Apply any corrections, then proceed.

### 6. Lifecycle label check

Check the current labels on the issue:

```bash
gh issue view <issue_number> --json labels --jq '.labels[].name'
```

**Stale label rules by change type:**

| What changed | Stale labels (Trace) | Stale labels (Feature) |
|---|---|---|
| Scenario Claim changed (on the Trace) | `implemented`, `verified` | — |
| Scenarios changed (on the Feature) | `implemented`, `verified` on every Trace that claims a changed scenario | — |
| ACs changed | `verified` | DoR: "Acceptance criteria written and reviewed" unchecked |
| Contracts changed | `implemented`, `verified` | — |
| Trace Plan reordered / re-batched only | — | — |

Legacy Traces carry the same labels.
Apply the same rules, reading "Gherkin changed (in-body)" for the two scenario rows.

If any stale labels are present, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "The following labels may no longer be accurate after this refinement: [list]. How should I handle them?"
- header: "Stale labels"
- options:
  - **Strip stale labels** → remove the labels that no longer reflect reality (recommended)
  - **Keep labels as-is** → leave labels unchanged. The user will manage them manually.

The "Scenarios changed (on the Feature)" row targets labels on the **claiming Traces**, not on the Feature.
Those labels are stripped during the cascade sync (step 9), with the same decision applied.
Record the decision for the audit comment in step 8.

### 7. Apply the changes

Read the current issue body.
Merge only the changed sections.
Preserve all unchanged content.
Write the updated body through the gh body helper (`../references/gh-body-helper.md`):

```bash
python3 .wtf/gh-body.py read <issue_number>       # prints a temp path
```

Use the Edit tool to replace each changed section in the printed temp file with its updated content.
Preserve all other sections verbatim.

```bash
python3 .wtf/gh-body.py edit <issue_number> --body-file "<path-from-read>"
```

If stale labels should be stripped (from step 6):

```bash
gh issue edit <issue_number> --remove-label "implemented,verified"
# Only remove labels that were confirmed stale — use the actual list
```

Print the updated issue URL.

### 8. Post the audit trail comment

Post a structured comment that summarises the refinement:

```bash
# Write the audit comment to a temp file with the Write tool; $COMMENT is that path.
python3 .wtf/gh-body.py comment <issue_number> --body-file "$COMMENT"
```

The audit comment must include:

```markdown
## Refinement — <YYYY-MM-DD>

**Entry point:** [interactive | headless re-aim after Trace #<n>]

**Insights incorporated:**
- [insight 1]
- [insight 2]

**Sections updated:** [comma-separated list]

**Trace Plan delta:** [reordered: …, re-batched: …, scenarios moved: …, added: … — or "no Trace Plan change"]

**Validations re-run:** [scope gate / DDD guard / scenario re-derivation / claim re-check / partition re-check — or "none required"]

**Labels affected:** [stripped: implemented, verified — or "none"]

**Suggested shrinkage:** [the scenario or story the evidence says to drop, plus that evidence — omit this block when there is none]

**Children that may need refinement:** [list with issue numbers and reason — or "none identified"]
```

In headless mode, use the heading `## Re-aim (headless) — after Trace #<n> — <YYYY-MM-DD>` instead.
Posting this comment is mandatory in both modes.

### 9. Cascade to affected children

Using the hierarchy fetched in step 1, cascade in two parts.

**a. Mechanical sync (Feature refined — scenarios or claims changed)**

This part is deterministic.
Run it directly after step 7 — no sub-agents, no extra question.
For every Trace whose Scenario Claim names a changed, renamed, moved, or newly added scenario:

1. If the Trace Plan moved scenarios between entries, update the Trace's Scenario Claim names to match.
2. Refresh the synced `<details>` copy from the Feature body. Keep its marker line: "Synced from Feature #N — edit there, not here".
3. Strip stale lifecycle labels per the step 6 decision (`implemented`, `verified`).

Use the gh body helper (`../references/gh-body-helper.md`) for each body edit.
List the synced Traces in the summary and in the audit comment.

**b. Judgment cascade (children that need their own refinement)**

Determine which children need more than a sync:

**Epic refined:**
- Features whose scope overlaps the changed Goal or Success Metrics
- Features listed in the Feature Breakdown that reference changed bounded context terms

**Feature refined:**
- Traces whose Scenario Claim, Spine Position, Contracts, or Technical Approach no longer match the rewritten stories or plan — beyond what the mechanical sync fixed
- Legacy Tasks (legacy Traces) whose in-body Gherkin tests the changed ACs

Present the affected children as a numbered list.
Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "These child issues may be out of sync with the updated spec: [list]. How would you like to handle them?"
- header: "Cascade"
- options:
  - **Refine each one now** → walk through `wtf.refine` for each affected child in order (default)
  - **I'll handle them manually** → exit. The user will open each child and update it.
  - **Skip** → leave children as-is

- **Refine each one now** → partition the affected children into conflict-free sub-groups using `../references/conflict-graph.md` (sub-groups here play the role of sub-phases). For each sub-group, spawn one sub-agent per child in parallel using the Agent tool, following `../references/subagent-protocol.md`. Read `skills/wtf.refine/SKILL.md` at spawn time. Paste steps 2 onward into each sub-agent prompt. Pass in the child issue number and the parent insight as pre-loaded context so the user is not re-asked. Wait for all sub-agents in a sub-group to complete (resolving any `NEEDS_INPUT` responses). Then start the next sub-group. After all sub-groups complete, summarise results.
- **I'll handle them manually** / **Skip** → exit.

If no children are affected, skip this step entirely.

## Headless mode

`wtf.loop` invokes this skill after each verified Trace, via a sub-agent per `../references/subagent-protocol.md`.
The loop pastes this file's body into the sub-agent prompt (sub-agents cannot load skills).
The insight is pre-loaded: the Feature number, the landed Trace's number, its Revealed learnings, and its verify results.
The sub-agent never calls `AskUserQuestion` (protocol rule 2).
A genuine blocker returns a `NEEDS_INPUT` block instead (protocol rule 3).

**Step overrides:**

| Interactive step | Headless behavior |
|---|---|
| Step 1 — issue ask | Skip the ask. The Feature number is pre-loaded. Detection and hierarchy fetch still run. |
| Step 2 — insight interview + 2d confirmation | Skip both. The pre-loaded learnings and verify results are the insight list. |
| Step 3 — classify | Runs. The default change type is **Trace landed — re-aim**. Other change types may also fire from the learnings. |
| Step 4 — validations | Runs. If a split signal fires, or the partition re-check fails and grow-only moves cannot fix it, return `NEEDS_INPUT`. |
| Step 5 — diff review question | Skip the question. Apply the diff directly. |
| Step 6 — stale label question | Resolve by rule: auto-strip per the stale-label table. Record the strips in the audit comment. |
| Step 8 — audit comment | ALWAYS post it. Heading: `## Re-aim (headless) — after Trace #<n> — <YYYY-MM-DD>`. |
| Step 9 — cascade | Runs without asking, but only part (a), the mechanical sync. Never refine judgment children autonomously — list them in the audit comment. |

**Grow-only rule (hard boundary).**
In headless mode the skill may reorder the remaining plan entries.
It may re-batch them.
It may move scenarios between remaining entries.
It may add newly discovered scenarios and plan entries.
It MUST NOT drop or weaken any scenario or story.
"Weaken" includes: delete a scenario, loosen a Then step, delete a story, or remove a plan entry without moving its claimed scenarios.

When the evidence suggests a drop:

1. Do not apply the drop.
2. Record a **Suggested shrinkage** block in the audit comment: what to drop, and the evidence.
3. Return a `NEEDS_INPUT`-style result (per `../references/subagent-protocol.md` rule 3) so the loop gates on a human.

Interactive mode has no such restriction.
The human is present and approves the diff.
Scenarios are the delivery contract.
Traces are the delivery schedule.
