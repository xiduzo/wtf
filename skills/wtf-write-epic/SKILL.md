---
name: wtf.write-epic
description: This skill should be used when a user wants to create, draft, or plan a GitHub Epic issue — for example "write an epic", "I want to define a new initiative", "scope out this strategic project", "turn this idea into an epic", "plan work that spans multiple features", or "start from a bounded context". Also use when the user asks to define domain outcomes, capture a large initiative before breaking it into features, or describe work in terms of business goals rather than technical tasks.
---

# Write Epic

Create a GitHub Epic issue capturing a strategic initiative with stakeholders, goals, success metrics, and a feature breakdown scaffold.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native dependency links are created in step 8.

Skip this step if gh-setup was already confirmed this session (e.g. when this skill is re-invoked via `write-feature` step 11 "Write another Epic").

### 1. Capture the seed idea

Ask ONE question: "What initiative are you working on?"

Do not ask follow-up questions yet. Acknowledge the idea briefly and move straight to research.

### 2. Deep research

Run in parallel using the Agent tool and GitHub issue search:

**Codebase exploration:**

- Existing systems or features this initiative builds on or replaces
- Current architecture constraints and integration points
- Patterns, conventions, or prior attempts relevant to the initiative
- Any existing domain glossary, ubiquitous language docs, or domain expert documentation (README, ADRs, wiki files)

**Wiki / glossary fetch:**
Fetch relevant GitHub wiki pages or in-repo glossary docs. Search for pages matching the initiative's domain area. Use these to:

- Identify existing Ubiquitous Language terms the team already uses
- Avoid introducing synonyms for already-named concepts
- Surface any existing Bounded Context definitions

**Related issues (optional — if GitHub is unavailable, skip this sub-step without comment):**

- Open and closed issues/epics that overlap or inform this initiative
- Prior discussions, decisions, or rejected approaches

Synthesise findings internally. Do not dump raw research at the user.

### 3. Grill the user

Using what research revealed, ask targeted follow-up questions to close the remaining gaps. The topics below are a **completeness checklist** — only ask about items that research did not already answer:

- Scope boundaries (what is explicitly out of scope?)
- Success criteria (how will we know we're done?)
- Stakeholders (Product Owner, Lead Designer, Tech Lead — skip any that don't apply)
- Constraints or deadlines that must shape the approach
- Any known risks or dependencies the research surfaced that need confirmation
- **Bounded Context:** Which domain context(s) does this initiative live in? (Ask last — use option list if multiple contexts were found in research)
- **Ubiquitous Language:** What domain actors (named roles, not "users") and domain verbs (business actions) define this space? Are there existing terms the team already uses that must be preserved?

**Questioning style:**

- Ask questions **one at a time** in order of priority. Wait for the answer before asking the next.
- **Always use the `AskUserQuestion` tool for every question** — including open-ended ones like "What are the success criteria?" or "Who is the stakeholder?". For each question, infer 1–2 likely answers from research (e.g. if research found a bounded context named "Payments", offer that as an option) and pass them as `options`. The UI automatically appends an "Other (type your answer)" escape hatch — do NOT add one manually.
  - Example: for "Who is the primary stakeholder?", call `AskUserQuestion` with `question: "Who is the primary stakeholder?"`, `header: "Stakeholder"`, and `options: [{label: "Product Owner"}, {label: "CTO / Eng lead"}, {label: "External client"}]`.
  - Example for open-ended: for "What are the success criteria?", call `AskUserQuestion` with `question: "What does success look like for this initiative?"`, `header: "Success criteria"`, and `options` pre-filled with 1–2 plausible outcomes inferred from research.

- After each answer, acknowledge briefly and ask the next question.
- Stop when you have enough to write a complete draft — do not ask questions you can fill in confidently from research. Skip any topic already answered by research.

### 4. DDD Language Check

Before drafting, review the seed idea and all gathered context against the rules in `../references/ddd-writing-rules.md`:

- Does the Epic title describe a **business outcome**, not a technology action?
- Does the Goal use domain vocabulary — not engineering jargon?
- Reframe any tech terms as business outcomes — the implementation detail belongs in Tasks.
- Flag any ambiguous or undefined term and propose the domain-correct alternative.

### 5. Vertical slice assessment

An epic must be a **coherent, independently deliverable strategic initiative** — it should produce real user or business value on its own, not only as a dependency for another epic.

This assessment runs on the **gathered context** (seed idea, research findings, and stakeholder answers) — before a draft exists. It catches structural incoherence early. A second, draft-level scope check runs at step 8 after the written artefact is complete.

Evaluate:

- **Passes** → proceed.
- **Too broad** → propose splitting into focused epics; present the breakdown and ask the user to confirm before continuing.
- **Has dependencies** → identify them explicitly:
  - Epics this epic **depends on** (must ship first)
  - Epics that **depend on this epic** (will be blocked until this ships)

Record each dependency issue number — these are applied in step 8. Do not write them to the body yet to avoid double-applying; step 8 handles all body writes and native links together.

### 6. Draft the Epic

Produce a complete draft. Success Metrics must be specific and measurable. Feature Breakdown stays as empty placeholders.

Use the issue body structure from @.github/ISSUE_TEMPLATE/EPIC.md (ignore the YAML frontmatter — use only the markdown body below the second `---` delimiter). Fill in all sections with the gathered context. If the file is missing or the reference cannot be resolved, use the following minimal structure: `## Context`, `## Goal`, `## Success Metrics`, `## Feature Breakdown`, `## Risks`, `## Bounded Context`.

**DDD writing rules for this draft:**

- **Bounded Context:** Fill in the Bounded Context field. If the epic spans multiple contexts, name each and describe where the seam is.
- **Context and Goal sections:** Every sentence must use Ubiquitous Language. No tech jargon.
- **Success Metrics:** Phrase as business-observable outcomes ("Merchants can view settlement status within 2 minutes of payment"), not system metrics ("API latency < 200ms").
- **Risks:** Frame risks in domain terms ("Dispute resolution rules differ by jurisdiction") before listing technical risks.

### 7. Scope gate

This is a final structural guardrail that operates on the **written draft** — distinct from step 5, which checked intent before drafting. It runs before user review so any structural issues are caught while they are cheapest to fix. Even if step 5 passed, run this check: drafting sometimes reveals bundled objectives that were not visible in the abstract.

Look for these **Epic-level split signals** (heuristics — use judgement, not rigid thresholds):

- The Goal statement contains multiple distinct business objectives joined by "and" — each could stand alone as a separate initiative
- The Feature Breakdown has more than 8 proposed features — treat this as a signal worth scrutiny, not an automatic trigger (8 tightly related features in one domain can be fine)
- The Epic spans more than one Bounded Context without a clear seam or handoff point
- Success Metrics describe outcomes that belong to completely different user journeys
- The epic's beneficiary cannot be stated in a single sentence without using "and" to cover unrelated groups

If **no signals are present**, proceed to creation.

If **one or more signals fire**, present your case: state which signals you found, explain why they suggest the epic should be split, and propose a concrete split (two or three focused epic titles with a one-line goal each). Then call `AskUserQuestion` with:

- `question`: "I think this Epic may be too broad — see my reasoning above. How do you want to proceed?"
- `header`: "Scope check"
- `options`:
  1. `{label: "Keep the original draft", description: "Proceed with the current draft without splitting"}`
  2. `{label: "Split it", description: "Start over with one of the proposed smaller Epics"}`
  3. `{label: "Stop here", description: "Exit without creating — I'll revisit the scope separately"}`

- **Keep the original draft** → proceed to user review (step 8) without further comment.
- **Split it** → return to step 3 with the chosen focused Epic as the seed. Carry forward all research and codebase findings already gathered — only re-ask stakeholder questions that the narrowed scope makes ambiguous. Note the remaining proposed sub-epics to the user as follow-on work.
- **Stop here** → exit.

### 8. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this look right?"`, `header: "Review"`, and `options: [{label: "Looks good — create the issue", description: "Proceed with issue creation"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed immediately.

### 9. Create the issue

> Note: Write the issue body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

> **Title generation:** Spawn a subagent using the `claude-haiku-4-5` model to generate a concise, domain-language title from the Epic's Goal. Pass in the Goal text and ask for a title (no prefix emoji/label needed — that is added below).

```bash
# Ensure the label exists before creating the issue
gh label create epic --color 5319e7 --description "Strategic initiative spanning multiple features" 2>/dev/null || true

gh issue create --title "🎯 Epic: <title>" --body-file /tmp/epic-body.md --label "epic"
```

Print the issue URL and number.

**Native dependency links:** Epics are top-level — no `gh sub-issue` call is needed here. If `gh-issue-dependency-available` (from step 0), create a blocking link for each dependency identified in step 5:

```bash
# For each issue this epic depends on (must ship first):
gh issue-dependency add <this_epic_number> --blocked-by <blocker_number>
```

If the extension is unavailable, warn the user — do not write dependency references into the issue body.

### 10. Update the wiki / glossary

If this Epic introduced or refined any **Bounded Context** definitions or **Ubiquitous Language** terms (domain actors, domain verbs, domain objects), update the project's glossary:

- Check whether a wiki page or in-repo glossary doc exists for this Bounded Context (e.g. `docs/glossary.md`, GitHub wiki page matching the context name).
- If a page exists: add or update the relevant term definitions, linking back to the Epic issue number.
- If no page exists: create one (prefer the GitHub wiki if available, otherwise `docs/glossary.md`), seeding it with the terms defined in this Epic.

Skip without comment if no terms were introduced. Report only the page name and terms added if an update was made.

### 11. Offer to continue

Use the `AskUserQuestion` tool with the following question and options:

- **question:** "What's next?"
- **header:** "Next step"
- **options:**
  1. label: "Plan all Features" · description: "Propose the full Feature list for this Epic and create them one by one (default)"
  2. label: "Write one Feature" · description: "Write a single Feature for this Epic now"
  3. label: "Write another Epic" · description: "Start a new Epic from scratch"
  4. label: "Stop here" · description: "Exit — no further action"

Route based on the answer:

- **Plan all Features** → invoke the `epic-to-features` skill, passing the Epic number in as context.
- **Write one Feature** → proceed with the `write-feature` skill, passing the Epic number in as context so the user is not asked for it again.
- **Write another Epic** → restart this skill from step 1.
- **Stop here** → exit.

> Suggest clearing context before continuing to features if the conversation has grown long: "The context is getting long — you may want to `/clear` before continuing."
