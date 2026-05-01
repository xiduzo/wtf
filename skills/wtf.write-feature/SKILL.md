---
name: wtf.write-feature
description: This skill should be used when a user wants to create a GitHub Feature issue, break down an Epic into user-facing capabilities, write user stories in domain language, or capture what a domain actor can do — for example "create a feature", "write a feature for this epic", "add a feature to an epic", "break this epic into features", "write user stories for this feature", or "describe what this actor can do". Use this skill to write a single Feature; use `wtf.epic-to-features` to generate the full set of Features for an Epic at once. Not applicable to Tasks, Epics, or bug reports.
---

# Write Feature

Create a GitHub Feature issue defining a user-facing capability. Fetches the parent Epic for context so the user doesn't have to repeat it.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native sub-issue and dependency links are created in step 10.

Skip this step if invoked from `wtf.epic-to-features` or `wtf.write-epic` (the orchestrator already ran it), or on re-invocations within the same session (e.g. "Write next Feature" loop in step 11).

### 1. Identify the parent Epic

Apply `../references/questioning-style.md` and ask "Which Epic does this Feature belong to?" — header `Epic`:

- Candidates from recent open issues labeled `epic`
- **None** — no parent Epic exists yet

- If an Epic number is given: fetch it per `../references/spec-hierarchy.md` and extract Goal, Context, and Success Metrics.
- If "none": note there is no parent Epic. Proceed, but flag the gap at the end — a Feature without an Epic is a planning debt.

**Wiki / glossary fetch:** After fetching the Epic (or immediately if no Epic), search for any wiki pages or in-repo glossary docs relevant to this Feature's domain area. Use these to identify existing Ubiquitous Language terms before naming anything new.

### 2. Name the capability

Ask: "What user-facing capability is this?" (one sentence)

The capability name must follow the pattern: **[Domain Actor] can [domain verb] [domain object]** — where:

- **Domain Actor** is the named role from the business (e.g. "Fulfilment Manager", "Payment Auditor", "Merchant") — never just "user" or "admin"
- **Domain verb** is a business action (e.g. allocate, settle, reconcile, dispute, approve) — not a generic CRUD verb like "store", "query", or "render"
- **Domain object** uses the Ubiquitous Language term for the concept (e.g. "Purchase Order", not "record" or "entry")

If the user gives a vague or tech-flavoured name, help them reframe it in domain terms before proceeding.

### 3. Clarify ambiguity before proceeding

**Critically assess** whether you have enough information to write a meaningful, unambiguous Feature. Cross-check the user's input against the Epic's Goal, Context, and Success Metrics.

If _anything_ is unclear or underspecified — scope boundaries, target users, key behaviors, constraints, success conditions — **stop and ask**. Do not proceed until you have answers.

Clarification questions are split into two tiers. Work through all Required questions first. Only then move to Context-dependent questions, and only those you cannot answer from the Epic or codebase.

**Required — always ask if not already clear:**

1. Who exactly is the domain actor? (named role, permissions, context — not "user")
2. What triggers this capability? What ends it?
3. What does success look like for the actor in domain terms?

**Context-dependent — ask only if not resolvable from the Epic, codebase, or prior answers:**

4. What are the limits or constraints? (quantity, format, access level)
5. What domain Aggregates does this Feature touch? (e.g. "Order", "Invoice", "Payment Transaction") — optional if the project does not use DDD modelling
6. What domain Events does this Feature emit or consume? (past-tense domain names, e.g. `OrderPlaced`, `PaymentSettled`)
7. What business invariants must hold?
8. Are there known edge cases or failure modes?

Apply `../references/questioning-style.md` for every question. Stop when you have enough for a complete draft.

### 4. Derive user stories

Based on the Epic's goal, the capability name, and clarified details, write 2–4 user stories in "As a **_, I want _** so that \_\_\_" format. Derive these — do not ask the user.

**DDD rules for user stories** (see `../references/ddd-writing-rules.md`):

- The "As a \_\_\_" role must be the domain actor name — never "user" or "admin"
- The "I want \_\_\_" must use domain verbs and objects from the Ubiquitous Language
- The "so that \_\_\_" must express a business outcome, not a system state

### 5. DDD Language Guard

Scan the capability name, user stories, and clarified context against the anti-patterns defined in `../references/ddd-writing-rules.md`. Flag and correct any violations found.

If issues are found, correct them silently and note the changes when showing the draft.

### 6. Vertical slice assessment

Run Stage 1 of `../references/scope-gates.md` on the gathered context and user stories. The Feature-specific bar: an end-to-end slice delivering one coherent, independently releasable user-facing capability. Concrete test — if this feature shipped tomorrow with no other unshipped features, could a domain actor use it and gain business value? If no, it fails.

Evaluate:

- **Passes** → proceed to draft.
- **Too broad** → propose smaller capability slices and confirm with the user.
- **Has dependencies** → identify them against sibling Features already under this Epic. Use `gh sub-issue list <epic_number>` per the cookbook in `../references/gh-setup.md`. Decide which Features this one depends on (must ship first) and which depend on it (will be blocked until this ships). Record each dependency issue number for step 10; do not write them into the body yet.

### 7. Draft the Feature

Acceptance Criteria must map 1:1 to user stories. Edge Cases must name at least 2 explicit failure or boundary scenarios.

Load the FEATURE template per `../references/issue-template-loading.md` (verify existence, halt-or-setup if missing, read body below the second `---` delimiter). Fill in all sections with the gathered context.

**DDD writing rules for this draft** (see `../references/ddd-writing-rules.md` for full rules):

- **Bounded Context:** Fill in the Bounded Context field and name the seam if the feature crosses contexts.
- **Domain Events:** List events this feature emits or consumes using past-tense domain names. These become integration contracts for child Tasks.
- **Acceptance Criteria:** Every AC must be an observable, domain-relevant outcome — not an implementation detail.
- **Edge Cases:** Name edge cases using domain language, not implementation state.

### 7b. Propose a Task list

Based on the Acceptance Criteria just drafted, derive a proposed list of Tasks that together implement this Feature. Each task should be a vertical slice — one observable, user-facing behaviour end-to-end.

Present the list as named-but-unnumbered checklist items and add them to the **Proposed Tasks** section of the draft:

```markdown
## Proposed Tasks

- [ ] Add settlement status field to Payment Aggregate
- [ ] Expose settlement status on the payments API endpoint
- [ ] Display settlement status in the merchant dashboard UI
- [ ] Send settlement notification email when status changes
```

Do not ask a separate question for this — it is shown as part of the draft in step 9. The user can adjust the task list during that review.

This list is written into the Feature body and becomes the starting point for `wtf.feature-to-tasks` — it reads the Proposed Tasks checklist directly rather than re-deriving from ACs. Write it carefully; it will drive task creation.

### 8. Run Definition of Ready checklist

The DoR items (from the Feature template) are:

- [ ] User stories agreed by PO
- [ ] Design handoff complete
- [ ] Acceptance criteria written and reviewed
- [ ] Edge cases identified

Evaluate each against the draft. For each unchecked item, ask "The DoR item '[item name]' is not met. How should we handle it?" — header `DoR item`:

- **Flag as blocker** → add a ⛔ Blocker note to the issue body before creating
- **Waive** → note the reason and proceed anyway

If "Design handoff complete" is flagged as a blocker, also ask "Do you have a Figma link to include?" — header `Figma link`:

- **No link yet** → leave Design Reference empty for now

If the user provides a link via the free-text escape hatch, add it to the Design Reference section of the issue body.

### 9. Scope gate

Run Stage 2 of `../references/scope-gates.md` on the written draft. Even if step 6 passed, drafting sometimes exposes scope that was invisible in the abstract.

**Feature-level split signals** (heuristics — use judgement, not rigid thresholds):

- More than 6 Acceptance Criteria covering meaningfully different behaviors — not variations on one behavior (six ways a payment can fail is not six separate features).
- The user stories reference more than one domain actor where each actor's need is independently satisfiable (e.g. a Manager story and a Customer story that could ship as separate features).
- The capability name contains "and" connecting two separable actions (e.g. "Merchant can view and export settlements").
- The Feature would require more than 6–8 Tasks to implement a single coherent behavior — likely two features bundled together.
- There is a natural early-release point: a subset of the ACs could ship and deliver value on its own.

If no signals fire, proceed to user review. If one or more fire, follow the Stage 2 procedure: state the signals, explain the risk, propose a concrete split (two focused capability names following the **[Actor] can [verb] [object]** pattern), and use the keep/split/stop ask from `../references/scope-gates.md`.

On **Split it** → return to step 3 with the chosen focused capability as the seed, carrying forward the already-fetched Epic context. Only re-ask clarification questions that the narrowed scope makes ambiguous.

### 10. Review with user

Show the draft. Then ask "Any changes before I create the issue?" — header `Review`:

- **Looks good — create the issue** → proceed with issue creation
- **I have changes** → adjust first

Apply edits, then proceed.

### 11. Create the issue and link to Epic

> Note: Write each body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

**Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise, domain-language title from the capability name. Pass in the capability name and ask for a short title (no prefix emoji/label needed — that is added below).

Create the Feature issue:

```bash
# Ensure the label exists before creating the issue
gh label create feature --color 0075ca --description "User-facing capability delivered as a vertical slice" 2>/dev/null || true

gh issue create --title "🚀 Feature: <title>" --body-file /tmp/wtf.feature-$(date +%s)-body.md --label "feature"
```

Print the Feature issue URL and number.

**Native relationships:** If `gh-sub-issue-available` (from step 0), link this Feature as a child of its Epic:

```bash
gh sub-issue add <epic_number> <feature_number>
```

If `gh-issue-dependency-available`, create a blocking link for each dependency identified in step 6:

```bash
# For each issue this Feature depends on (must ship first):
gh issue-dependency add <feature_number> --blocked-by <blocker_number>
```

If either extension is unavailable, warn the user — do not write relationship references into the issue body.

Print the Feature issue URL and number.

**Wiki / glossary update:** If this Feature introduced or refined any Ubiquitous Language terms (new domain actors, domain verbs, domain events, or Bounded Context seams), update the project glossary — same rules as in `wtf.write-epic` step 10. Report only if a change was made.

### 12. Offer to continue

First, if there is a parent Epic, check its Feature Breakdown checklist: list any Feature placeholders that have not yet been created as issues (i.e. no `#issue` reference beside them). Mention how many remain.

Then ask "What's next?" — header `Next step`:

- **Plan all Tasks** → propose the full Task list for this Feature and create them one by one (default)
- **Write one Task** → write a single Task for this Feature now
- **Write next Feature** → write the next Feature for the same Epic (N remaining — replace N with the actual count, or omit if none)
- **Stop here** → exit, no further action

- **Plan all Tasks** → invoke the `wtf.feature-to-tasks` skill, passing the Feature number in as context.
- **Write one Task** → proceed with the `wtf.write-task` skill, passing the Feature number in as context.
- **Write next Feature** → restart this skill from step 2, reusing the same Epic (skip re-fetching it). If the Epic has a Feature Breakdown list, propose the next uncreated Feature as the default capability name.
- **Stop here** → exit.

If the conversation has grown long (more than ~20 exchanges), tell the user: "The context is getting long — you may want to `/clear` before continuing to avoid degraded quality."
