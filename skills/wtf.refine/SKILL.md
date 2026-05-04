---
name: wtf.refine
description: Use when new insights change the scope, acceptance criteria, domain language, or technical constraints of an existing Epic, Feature, or Task — for example "refine epic #10", "update this task with the new requirements", "we got new feedback on feature #24", "incorporate these comments into the spec", or when new Figma designs, documents, or GitHub comments reveal that the current spec is out of date. Accepts insights from CLI text, GitHub comments, referenced files or URLs, and conversation context. Detects the issue type automatically, smart re-validates only what changed, shows a section-by-section before/after diff, posts an audit trail comment, warns about stale lifecycle labels, and cascades refinement offers to affected children.
---

# Refine

Update an existing Epic, Feature, or Task issue based on new insights. Core value: merges insights from any source, determines exactly which sections change, re-runs only the validations those changes require, shows you a precise diff before touching anything, and cascades to children so nothing goes stale.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — they are used in step 1 (hierarchy fetch) and step 9 (cascade).

Skip this step if gh-setup was already confirmed this session.

### 1. Identify the issue and its hierarchy

If an issue number was passed in as context or a CLI argument, use it directly. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which issue are you refining?"
- header: "Issue"
- options: from recently-updated open issues across all WTF labels (epic, feature, task), inferred from:

```bash
gh issue list --label "epic,feature,task" --state open --json number,title,labels --limit 10
```

Fetch the issue:

```bash
gh issue view <issue_number> --json number,title,body,labels,comments,updatedAt
```

**Detect the issue type** from its labels:
- Has label `epic` → type = **Epic**
- Has label `feature` → type = **Feature**
- Has label `task` → type = **Task**
- None of the above → call `AskUserQuestion` (per `../references/questioning-style.md`):
  - question: "I couldn't detect the type from the labels. What kind of issue is this?"
  - header: "Issue type"
  - options: **Epic** / **Feature** / **Task**

**Fetch the hierarchy** for context and cascade planning:

```bash
# Parent (always fetch — needed for context)
gh sub-issue list <issue_number> --relation parent

# Children (needed for cascade planning in step 9)
gh sub-issue list <issue_number>
```

For the parent issue, fetch its body to extract goal, bounded context, and success metrics — these inform whether a change in the child conflicts with the parent's intent.

### 2. Gather insights from all sources

Merge insights from every available source into a single consolidated list. Process all sources in parallel:

**a. CLI argument / conversation context**

If the user passed insight text in the invocation (e.g. `refine #42 "scope changed — exclude mobile"`), treat that as the primary insight. If nothing was passed, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What changed or what new insight should I incorporate?"
- header: "Insight"
- options: from plausible changes inferred from recent issue comments (e.g. the last comment's key point)

**b. GitHub comments since last body edit**

Extract comments posted after the issue body was last edited:

```bash
gh issue view <issue_number> --json comments,updatedAt \
  --jq '.updatedAt as $bodyUpdatedAt | .comments[] | select(.createdAt > $bodyUpdatedAt) | "[\(.author.login)] \(.body)"'
```

Read each comment and extract actionable insights — discard discussion noise ("+1", "agreed", "thanks"). Synthesise into concrete change signals (e.g. "Stakeholder comment: settlement must support multi-currency").

**c. Referenced files**

If the user referenced any file paths or URLs in the CLI argument or conversation, read them now:

- File paths → use the Read tool
- URLs → use the WebFetch tool (if available) or ask the user to paste the relevant content

Extract the relevant change signals from each document.

**d. Consolidate**

Merge all signals into a numbered list of insights. Present them briefly to the user:

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
  - **Remove one** → some of these aren't relevant

Apply any adjustments before continuing.

### 3. Classify the changes

For each insight, determine which sections of the issue it affects and what type of change it is. This classification drives which validations run in step 4 and which sections are rewritten in step 5.

**Change types and their affected sections:**

| Change type | Affected (Epic) | Affected (Feature) | Affected (Task) |
|---|---|---|---|
| Scope narrowed / expanded | Goal, Success Metrics, Feature Breakdown | ACs, Edge Cases, Proposed Tasks | Gherkin, Functional Description |
| New constraint | Risks, Bounded Context | ACs, Edge Cases, Rollout | Contracts, Observability, Rollout |
| Domain language correction | Context, Goal, Bounded Context | Capability name, User Stories, ACs | Gherkin steps, Contracts |
| New stakeholder / actor | Context, Goal | Capability name, User Stories | — |
| New domain event | — | Domain Events | Gherkin (When steps), Contracts |
| Technical constraint | — | Edge Cases | Contracts, Technical Approach |
| Deadline / priority | Risks | — | — |

Produce a **change map** — a structured internal summary:

```
Change map:
  scope changed:        yes
  DDD language changed: no
  ACs changed:          yes
  Gherkin affected:     yes  (because ACs changed)
  Contracts affected:   no
  Sections to rewrite:  [Goal, Success Metrics] / [ACs, Edge Cases] / [Gherkin, Functional Description]
```

### 4. Re-run relevant validations only

Using the change map from step 3, run only the validations that apply. Skip the rest — do not re-validate unchanged sections.

**Scope changed → Vertical slice + Scope gate**

Re-run both stages defined in `../references/scope-gates.md` on the refined intent, then on the rewritten sections. The per-level split signals live in the matching write-* skill:

- Epic → `wtf.write-epic` step 7
- Feature → `wtf.write-feature` step 9
- Task → `wtf.write-task` step 9

If a split signal fires on the **refined** issue, present it as a refinement concern (not a blocker). Use the same keep / split / stop ask the write-* skill uses (see `../references/scope-gates.md`).

**Domain language changed → DDD Language Guard**

Re-run the checks from `../references/ddd-writing-rules.md` on any section whose text is being rewritten. Flag and correct violations silently; note corrections in the diff (step 5).

**ACs changed (Feature or Task) → Gherkin re-derivation**

If Feature ACs changed, mark the Proposed Tasks section as potentially stale — note which tasks may need re-scoping. Do not automatically update child Tasks here; that is handled in step 9 (cascade).

If Task ACs changed, re-derive only the Gherkin scenarios that map to the changed AC(s). Keep unchanged scenarios exactly as they are.

### 5. Draft the section updates and show a diff

Produce the updated content for each section in the change map. Do not touch sections that are not in the change map.

Present a **section-by-section before/after diff** for every changed section. Format each section's diff as:

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
  - **Start over** → the insights were wrong; re-describe what changed

Apply any corrections, then proceed.

### 6. Lifecycle label check

Check the current labels on the issue:

```bash
gh issue view <issue_number> --json labels --jq '.labels[].name'
```

**Stale label rules by change type:**

| What changed | Stale labels (Task) | Stale labels (Feature) |
|---|---|---|
| Gherkin scenarios changed | `implemented`, `verified` | — |
| ACs changed | `verified` | DoR: "Acceptance criteria written and reviewed" unchecked |
| Contracts changed | `implemented`, `verified` | — |
| Functional Description changed | — | — |

If any stale labels are present, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "The following labels may no longer be accurate after this refinement: [list]. How should I handle them?"
- header: "Stale labels"
- options:
  - **Strip stale labels** → remove the labels that no longer reflect reality (recommended)
  - **Keep labels as-is** → leave labels unchanged; I'll manage them manually

Record the decision for the audit comment in step 8.

### 7. Apply the changes

Read the current issue body, merge only the changed sections (preserving all unchanged content), and write the updated body:

```bash
gh issue view <issue_number> --json body -q .body > /tmp/wtf.refine-<issue_number>-body.md
```

Use the Edit tool to replace each changed section in `/tmp/wtf.refine-<issue_number>-body.md` with its updated content. Preserve all other sections verbatim.

```bash
gh issue edit <issue_number> --body-file /tmp/wtf.refine-<issue_number>-body.md
```

If stale labels should be stripped (from step 6):

```bash
gh issue edit <issue_number> --remove-label "implemented,verified"
# Only remove labels that were confirmed stale — use the actual list
```

Print the updated issue URL.

### 8. Post the audit trail comment

Post a structured comment summarising the refinement:

```bash
gh issue comment <issue_number> --body "<audit_comment>"
```

The audit comment must include:

```markdown
## Refinement — <YYYY-MM-DD>

**Insights incorporated:**
- [insight 1]
- [insight 2]

**Sections updated:** [comma-separated list]

**Validations re-run:** [scope gate / DDD guard / Gherkin re-derivation — or "none required"]

**Labels affected:** [stripped: implemented, verified — or "none"]

**Children that may need refinement:** [list with issue numbers and reason — or "none identified"]
```

### 9. Cascade to affected children

Using the hierarchy fetched in step 1, determine which children are affected by this refinement:

**Epic refined:**
- Features whose scope overlaps the changed Goal or Success Metrics
- Features listed in the Feature Breakdown that reference changed bounded context terms

**Feature refined:**
- Tasks whose Gherkin scenarios directly test the changed ACs
- Tasks whose Proposed Tasks checklist entry was modified or removed

Present the affected children as a numbered list. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "These child issues may be out of sync with the updated spec: [list]. How would you like to handle them?"
- header: "Cascade"
- options:
  - **Refine each one now** → walk through `wtf.refine` for each affected child in order (default)
  - **I'll handle them manually** → exit; I'll open each child and update it myself
  - **Skip** → leave children as-is

- **Refine each one now** → partition the affected children into conflict-free sub-groups using `../references/conflict-graph.md` (sub-groups here play the role of sub-phases). For each sub-group, spawn one sub-agent per child in parallel using the Agent tool, following `../references/subagent-protocol.md` — read `skills/wtf.refine/SKILL.md` at spawn time and paste steps 2 onward into each sub-agent prompt. Pass in the child issue number and the parent insight as pre-loaded context so the user is not re-asked. Wait for all sub-agents in a sub-group to complete (resolving any `NEEDS_INPUT` responses) before starting the next sub-group. After all sub-groups complete, summarise results.
- **I'll handle them manually** / **Skip** → exit.

If no children are affected, skip this step entirely.
