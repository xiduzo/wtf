---
name: wtf.write-feature
description: This skill should be used when a user wants to create a GitHub Feature issue, break down an Epic into user-facing capabilities, write user stories in domain language, or capture what a domain actor can do — for example "create a feature", "write a feature for this epic", "add a feature to an epic", "break this epic into features", "write user stories for this feature", or "describe what this actor can do". Use this skill to write a single Feature. Use `wtf.epic-to-features` to generate the full set of Features for an Epic at once. Supports two planning modes — `guided` (step-by-step questions) and `flow` (derive, one consolidated review) — passed as an argument or read from `.wtf/config.json`. Not applicable to Traces, Epics, or bug reports.
argument-hint: "[capability] [guided|flow]"
---

# Write Feature

Create a GitHub Feature issue that defines a user-facing capability. Fetch the parent Epic for context so the user does not repeat it.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available. That result controls whether native sub-issue and dependency links are created in step 10.

If invoked from `wtf.epic-to-features` or `wtf.write-epic`, skip this step. The orchestrator already ran it. Also skip on re-invocations in the same session (e.g. "Write next Feature" loop in step 11).

### 0b. Resolve the planning mode and the feature scope

Run the **Resolve the mode** block from `../references/planning-mode.md`. An explicit `guided` or `flow` argument in the invocation wins over config. `$WTF_PLAN` shapes steps 3 and 8 below. Every quality gate runs in both modes.

Then resolve the feature scope from `.wtf/config.json` with the same read pattern:

```bash
WTF_SCOPE=$(python3 - <<'PY' 2>/dev/null || true
import json
try:
    print((json.load(open(".wtf/config.json")).get("feature_scope") or "").strip())
except Exception:
    pass
PY
)
```

If `$WTF_SCOPE` is not `single-story` or `grouped`, ask once. Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "How many user stories should this Feature carry?"
- header: "Feature scope"
- options:
  - **Single-story** → `single-story` — the Feature carries exactly one user story
  - **Grouped** → `grouped` — the Feature carries co-related stories that share one Spine

`$WTF_SCOPE` shapes steps 4 and 9 below. The scope gate (step 9) may override it for this Feature with a stated reason recorded in the body.

If invoked from `wtf.epic-to-features`, use the planning mode and the feature scope the orchestrator passed in. Do not re-resolve either.

### 1. Identify the parent Epic

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Epic does this Feature belong to?"
- header: "Epic"
- options:
  - Candidates from recent open issues labeled `epic`
  - **None** — no parent Epic exists yet

- If an Epic number is given: fetch it per `../references/spec-hierarchy.md` and extract Goal, Context, and Success Metrics.
- If "none": note there is no parent Epic. Proceed, but flag the gap at the end. A Feature without an Epic is a planning debt.

**Wiki / glossary fetch:** After fetching the Epic (or immediately if no Epic), search for any wiki pages or in-repo glossary docs relevant to this Feature's domain area. Use these to identify existing Ubiquitous Language terms before naming anything new.

### 2. Name the capability

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What user-facing capability is this?" (one sentence)
- header: "Capability"
- options: infer 1–2 candidates from the Epic's Goal or Success Metrics if available

The capability name must follow the pattern: **[Domain Actor] can [domain verb] [domain object]** — where:

- **Domain Actor** is the named role from the business (e.g. "Fulfilment Manager", "Payment Auditor", "Merchant") — never just "user" or "admin"
- **Domain verb** is a business action (e.g. allocate, settle, reconcile, dispute, approve) — not a generic CRUD verb like "store", "query", or "render"
- **Domain object** uses the Ubiquitous Language term for the concept (e.g. "Purchase Order", not "record" or "entry")

If the user gives a vague or tech-flavored name, help them reframe it in domain terms before proceeding.

### 3. Clarify ambiguity before proceeding

Assess whether you have enough information to write a clear Feature. Cross-check the user's input against the Epic's Goal, Context, and Success Metrics.

If anything is unclear or underspecified — scope boundaries, target users, key behaviors, constraints, success conditions — stop and ask. Do not proceed until you have answers.

Clarification questions are split into two tiers. Work through all Required questions first. Only then move to Context-dependent questions, and only those you cannot answer from the Epic or codebase.

**Required — always ask if not already clear:**

1. Who exactly is the domain actor? (named role, permissions, context — not "user")
2. What triggers this capability? What ends it?
3. What does success look like for the actor in domain terms?

**Context-dependent — ask only if not resolvable from the Epic, codebase, or prior answers:**

4. What are the limits or constraints? (quantity, format, access level)
5. What domain Aggregates does this Feature touch? (e.g. "Order", "Invoice", "Payment Transaction") — optional if the project does not use DDD modeling
6. What domain Events does this Feature emit or consume? (past-tense domain names, e.g. `OrderPlaced`, `PaymentSettled`)
7. What business invariants must hold?
8. Are there known edge cases or failure modes?

For each unanswered item above, call `AskUserQuestion` (per `../references/questioning-style.md`). Stop when you have enough for a complete draft.

**In `flow` mode:** answer these questions yourself first — from the Epic, the codebase, the glossary, and the steering docs. Only the genuinely unanswerable items survive. Batch those into **one** `AskUserQuestion` call instead of asking one by one. If every item resolves, ask nothing.

### 4. Derive user stories and scenarios

Based on the Epic's goal, the capability name, and clarified details, write the user stories in "As a **_, I want _** so that \_\_\_" format. Derive these. Do not ask the user. `$WTF_SCOPE` sets the count:

- **`single-story`** — exactly one user story.
- **`grouped`** — 2–4 co-related stories that share one Spine.

For each story, derive its Acceptance Criteria. Then derive canonical Gherkin scenarios from those ACs. Each AC maps to one or more scenarios. Step 7 writes them into the Feature body per story — story, ACs, scenarios — per the FEATURE template. The Feature body is the canonical, PM-editable home of all scenarios. Traces claim subsets of them by name. They never own them.

**DDD rules for user stories** (see `../references/ddd-writing-rules.md`):

- The "As a \_\_\_" role must be the domain actor name — never "user" or "admin"
- The "I want \_\_\_" must use domain verbs and objects from the Ubiquitous Language
- The "so that \_\_\_" must express a business outcome, not a system state

### 5. DDD Language Guard

Scan the capability name, user stories, and clarified context against the anti-patterns defined in `../references/ddd-writing-rules.md`. Flag and correct any violations found.

If issues are found, correct them silently. Note the changes when showing the draft.

### 6. Vertical slice assessment

Run Stage 1 of `../references/scope-gates.md` on the gathered context and user stories. Feature bar: one step toward the Epic, carrying 1..n co-related user stories that share one Spine. Concrete test — if this feature shipped tomorrow with no other unshipped features, could a domain actor use it and gain business value? If no, it fails.

Evaluate:

- **Passes** → proceed to draft.
- **Too broad** → propose smaller capability slices and confirm with the user.
- **Has dependencies** → identify them against sibling Features already under this Epic. Use `gh sub-issue list <epic_number>` per the cookbook in `../references/gh-setup.md`. Decide which Features this one depends on (must ship first) and which depend on it (will be blocked until this ships). Record each dependency issue number for step 10. Do not write them into the body yet.

### 7. Draft the Feature

Each story block carries its own Acceptance Criteria and its canonical scenarios (from step 4). Edge Cases must name at least 2 explicit failure or boundary cases, so Deepening Traces can claim scenarios that cover them.

Apply strict STE per `../references/ste-writing.md` before writing any durable body.

Load the FEATURE template per `../references/issue-template-loading.md` (verify existence, halt-or-setup if missing, read body below the second `---` delimiter). Fill all sections with the gathered context.

**DDD writing rules for this draft** (see `../references/ddd-writing-rules.md` for full rules):

- **Bounded Context:** Fill the Bounded Context field and name the seam if the feature crosses contexts.
- **Domain Events:** List events this feature emits or consumes using past-tense domain names. These become integration contracts for child Traces.
- **Acceptance Criteria:** Every AC must be an observable, domain-relevant outcome — not an implementation detail. Write them per story.
- **Scenarios:** Write each story's canonical Gherkin under that story. Traces claim these scenarios by name. PMs and designers edit them here, not in Trace issues.
- **Edge Cases:** Name edge cases using domain language, not implementation state.
- **Delivery Override:** Fill this section only when the user asks for a non-default delivery mode for this Feature. Record the mode (`staged` | `trunk`) and the reason. Otherwise leave it blank — the `delivery` key in `.wtf/config.json` rules.

### 7b. Propose the Trace Plan

From the stories and their scenarios, derive the **Trace Plan**: an ordered checklist. Item 1 is the Skeleton. It claims the primary story's happy-path scenario, minimally, through every layer. Each later item names its story, its Scenario Claim (the claimed scenario names), and what it adds to the Spine. The Scenario Claims of one story's Traces must partition that story's scenarios — full cover, no overlap.

Add the checklist to the **Trace Plan** section of the draft:

```markdown
## Trace Plan

1. [ ] ☄️ Skeleton — Merchant sees settlement status for one completed payment (claims: "Status shown for a settled payment")
2. [ ] ☄️ Deepening — settlement status failure modes (claims: "Status for a failed settlement", "Status while settlement is pending")
3. [ ] ☄️ Merchant filters settlements by date range (claims: all scenarios)
```

Do not ask a separate question for this. It is shown as part of the draft in step 10. The user can adjust the plan during that review.

This plan is written into the Feature body and becomes the starting point for `wtf.feature-to-traces`. It reads the Trace Plan checklist directly rather than re-deriving it from the scenarios. The plan is a living aim, not a contract — `wtf.refine` re-aims it after each Trace lands. Still, write it carefully. It will drive Trace creation.

### 8. Run Definition of Ready checklist

The DoR items (from the Feature template) are:

- [ ] User stories agreed by PO
- [ ] Design handoff complete
- [ ] Acceptance criteria written and reviewed
- [ ] Edge cases identified

Evaluate each against the draft. For each unchecked item, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "The DoR item '[item name]' is not met. How should we handle it?"
- header: "DoR item"
- options:
  - **Flag as blocker** → add a ⛔ Blocker note to the issue body before creating
  - **Waive** → note the reason and proceed anyway

If "Design handoff complete" is flagged as a blocker, also call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Do you have a Figma link to include?"
- header: "Figma link"
- options:
  - **No link yet** → leave Design Reference empty for now

If the user provides a link via the free-text escape hatch, add it to the Design Reference section of the issue body.

**In `flow` mode:** do not interrogate DoR items one by one. Auto-waive the human-process items ("User stories agreed by PO", "Design handoff complete") with the note `Waived (flow mode)` in the issue body. Evaluate the derivable items ("Acceptance criteria written and reviewed", "Edge cases identified") against the draft yourself. The user objects at the step 10 review if a waiver is wrong.

### 9. Scope gate

Run Stage 2 of `../references/scope-gates.md` on the written draft. Even if step 6 passed, drafting sometimes exposes scope that was invisible in the abstract.

**Feature-level split signals** (heuristics — use judgement, not rigid thresholds):

- More than 6 Acceptance Criteria across the stories covering meaningfully different behaviors — not variations on one behavior (six ways a payment can fail is not six separate features).
- In `grouped` mode, a story that does not share the Spine with the others. The split question is always: do these stories share one Spine? A story that needs its own Spine belongs in its own Feature.
- The user stories reference more than one domain actor where each actor's need is independently satisfiable (e.g. a Manager story and a Customer story that could ship as separate features).
- The capability name contains "and" connecting two separable actions (e.g. "Merchant can view and export settlements"). This signal splits Features.
- In `single-story` mode, the draft carries more than one story.
- There is a natural early-release point: a subset of the stories could ship and deliver value on its own.

A story too big for one agent pass is **not** a split signal here. Depth handles that later: `wtf.feature-to-traces` plans a Skeleton plus Deepening Traces. Never split a story into layer slices.

If no signals fire, proceed to user review. If one or more fire, follow the Stage 2 procedure. State the signals. Explain the risk. Propose a concrete split (two focused capability names following the **[Actor] can [verb] [object]** pattern). Use the keep/split/stop ask from `../references/scope-gates.md`.

**Scope override:** the gate may keep a draft that departs from `$WTF_SCOPE` — for example, two stories so entangled that a split breaks the Spine. State the reason to the user. Record it as a one-line note at the top of the User Stories section. Overrides are the exception. The config is the rule.

On **Split it** → return to step 3 with the chosen focused capability as the seed, carrying forward the already-fetched Epic context. Only re-ask clarification questions that the narrowed scope makes ambiguous.

### 10. Review with user

This review runs in **both** planning modes. In standalone `flow` mode it is the one consolidated review — everything before it asked nothing it could derive. When `wtf.epic-to-features` orchestrates in `flow` mode, its batch review replaces this step; skip it there.

Show the draft. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Any changes before I create the issue?"
- header: "Review"
- options:
  - **Looks good — create the issue** → proceed with issue creation
  - **I have changes** → adjust first

Apply edits. Then proceed.

### 11. Create the issue and link to Epic

> Note: Write the body to a temp file (`$BODY`) with the Write tool. Then create it through the gh body helper so multi-line UTF-8 content survives on Windows. See `../references/gh-body-helper.md`.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise, domain-language title from the capability name. Pass in the capability name and ask for a short title (no prefix emoji/label needed — that is added below).

Create the Feature issue:

```bash
# $BODY is the temp file you wrote the filled body to with the Write tool.
# Create the issue WITHOUT a kind label — the classify step below sets the kind.
python3 .wtf/gh-body.py create --title "🚀 Feature: <title>" --body-file "$BODY"
```

Print the Feature issue URL and number.

**Classify the issue as `Feature`.** Set `TYPE="Feature"` and `ISSUE_NUMBER=<number from the URL>`. Then run the **Classify a new issue** block from `../references/issue-classification.md` (resolve `$WTF_CLASS` once first). In `types` mode it sets the native GitHub issue type and leaves labels free for your own segmentation. In `labels` mode it applies the `feature` label. Either way the Feature is classified. Nothing downstream depends on which mechanism was used.

**Native relationships:** If `gh-sub-issue-available` (from step 0), link this Feature as a child of its Epic:

```bash
gh sub-issue add <epic_number> <feature_number>
```

If `gh-issue-dependency-available`, create a blocking link for each dependency identified in step 6:

```bash
# For each issue this Feature depends on (must ship first):
gh issue-dependency add <feature_number> --blocked-by <blocker_number>
```

If either extension is unavailable, warn the user. Do not write relationship references into the issue body.

Print the Feature issue URL and number.

**Wiki / glossary update:** If this Feature introduced or refined any Ubiquitous Language terms (new domain actors, domain verbs, domain events, or Bounded Context seams), update the project glossary — same rules as in `wtf.write-epic` step 10. Report only if a change was made.

### 12. Offer to continue

First, if there is a parent Epic, check its Feature Breakdown checklist. List any Feature placeholders that have not yet been created as issues (i.e. no `#issue` reference beside them). Mention how many remain.

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Plan all Traces** → walk this Feature's Trace Plan and create the Trace issues one by one (default)
  - **Write one Trace** → write a single Trace for this Feature now
  - **Write next Feature** → write the next Feature for the same Epic (N remaining — replace N with the actual count, or omit if none)
  - **Stop here** → exit, no further action

- **Plan all Traces** → invoke the `wtf.feature-to-traces` skill, passing the Feature number in as context.
- **Write one Trace** → proceed with the `wtf.write-trace` skill, passing the Feature number in as context.
- **Write next Feature** → restart this skill from step 2, reusing the same Epic (skip re-fetching it). If the Epic has a Feature Breakdown list, propose the next uncreated Feature as the default capability name.
- **Stop here** → exit.

If the conversation has grown long (more than ~20 exchanges), tell the user: "The context is getting long — you may want to `/clear` before continuing to avoid degraded quality."
