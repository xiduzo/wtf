---
name: wtf.write-epic
description: This skill should be used when a user wants to create, draft, or plan a GitHub Epic issue — for example "write an epic", "I want to define a new initiative", "scope out this strategic project", "turn this idea into an epic", "plan work that spans multiple features", or "start from a bounded context". Also use when the user asks to define domain outcomes, capture a large initiative before breaking it into features, or describe work in terms of business goals rather than technical tasks.
---

# Write Epic

Create a GitHub Epic issue capturing a strategic initiative with stakeholders, goals, success metrics, and a feature breakdown scaffold.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native dependency links are created in step 8.

Skip this step if gh-setup was already confirmed this session (e.g. when this skill is re-invoked via `wtf.write-feature` step 11 "Write another Epic").

### 1. Capture the seed idea

Ask ONE question: "What initiative are you working on?"

Do not ask follow-up questions yet. Acknowledge the idea briefly and move straight to research.

### 2. Deep research

Run in parallel using the Agent tool and GitHub issue search:

**Codebase exploration:**

Use the Agent tool with these concrete searches (run in parallel):

- `Glob('**/{README,readme}.md')` + `Glob('docs/**/*.md')` + `Glob('**/*.{adr,ADR}.md')` — for existing product descriptions, ADRs, and architectural notes
- `Glob('src/**', 'lib/**', 'packages/**')` — to understand the module structure and which systems exist
- `Grep` for the initiative's key domain nouns across `*.{ts,tsx,js,jsx,py,go,rb,java,cs}` files — to find existing implementations, prior attempts, or integration points
- `Glob('**/{GLOSSARY,glossary,ubiquitous-language,domain}.md')` + `Glob('.github/**/*.md')` — for any existing domain glossary, ubiquitous language docs, or prior DDD artefacts

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

Using what research revealed, ask targeted follow-up questions to close the remaining gaps. Apply `../references/questioning-style.md` for every question.

Completeness checklist (ask only about unanswered items):

- Scope boundaries (what is explicitly out of scope?)
- Success criteria (how will we know we're done?)
- Stakeholders (Product Owner, Lead Designer, Tech Lead — skip any that don't apply)
- Constraints or deadlines that must shape the approach
- Any known risks or dependencies the research surfaced that need confirmation
- **Bounded Context:** Which domain context(s) does this initiative live in? (Ask last — use an option list if multiple contexts were found in research.)
- **Ubiquitous Language:** What domain actors (named roles, not "users") and domain verbs (business actions) define this space? Are there existing terms the team already uses that must be preserved?

### 4. DDD Language Check

Before drafting, review the seed idea and all gathered context against the rules in `../references/ddd-writing-rules.md`:

- Does the Epic title describe a **business outcome**, not a technology action?
- Does the Goal use domain vocabulary — not engineering jargon?
- Reframe any tech terms as business outcomes — the implementation detail belongs in Tasks.
- Flag any ambiguous or undefined term and propose the domain-correct alternative.

### 5. Vertical slice assessment

Run Stage 1 of `../references/scope-gates.md` on the gathered context. The Epic-specific bar: a coherent, independently deliverable strategic initiative that produces real user or business value on its own, not only as a dependency for another epic.

Evaluate:

- **Passes** → proceed to draft.
- **Too broad** → propose focused epics and confirm with the user before continuing.
- **Has dependencies** → identify Epics this epic depends on and Epics that depend on this one. Record each dependency issue number for step 8; do not write them into the body yet.

### 6. Draft the Epic

Produce a complete draft. Success Metrics must be specific and measurable. Feature Breakdown stays as empty placeholders.

Before drafting, verify `.github/ISSUE_TEMPLATE/EPIC.md` exists. If missing, ask the user (per `../references/questioning-style.md`) whether to run `/wtf.setup` or cancel — then halt either way.

Use the issue body structure from @.github/ISSUE_TEMPLATE/EPIC.md (ignore the YAML frontmatter — use only the markdown body below the second `---` delimiter). Fill in all sections with the gathered context.

**DDD writing rules for this draft:**

- **Bounded Context:** Fill in the Bounded Context field. If the epic spans multiple contexts, name each and describe where the seam is.
- **Context and Goal sections:** Every sentence must use Ubiquitous Language. No tech jargon.
- **Success Metrics:** Phrase as business-observable outcomes ("Merchants can view settlement status within 2 minutes of payment"), not system metrics ("API latency < 200ms").
- **Risks:** Frame risks in domain terms ("Dispute resolution rules differ by jurisdiction") before listing technical risks.

### 7. Scope gate

Run Stage 2 of `../references/scope-gates.md` on the written draft. Even if step 5 passed, run this — drafting sometimes reveals bundled objectives that were invisible in the abstract.

**Epic-level split signals** (heuristics — use judgement, not rigid thresholds):

- The Goal statement contains multiple distinct business objectives joined by "and" — each could stand alone as a separate initiative.
- The Feature Breakdown has more than 8 proposed features — treat this as a signal worth scrutiny, not an automatic trigger (8 tightly related features in one domain can be fine).
- The Epic spans more than one Bounded Context without a clear seam or handoff point.
- Success Metrics describe outcomes that belong to completely different user journeys.
- The epic's beneficiary cannot be stated in a single sentence without using "and" to cover unrelated groups.

If no signals fire, proceed to creation. If one or more fire, follow the Stage 2 procedure: state the signals, explain the risk, propose a concrete split (two or three focused epic titles with a one-line goal each), and use the keep/split/stop ask from `../references/scope-gates.md`.

On **Split it** → return to step 3 with the chosen focused Epic as the seed. Carry forward all research and codebase findings already gathered — only re-ask stakeholder questions that the narrowed scope makes ambiguous. Note the remaining proposed sub-epics to the user as follow-on work.

### 8. Review with user

Show the draft. Then ask "Does this look right?" — header `Review`:

- **Looks good — create the issue** → proceed with issue creation
- **I have changes** → adjust first

Apply edits, then proceed immediately.

### 9. Create the issue

> Note: Write the issue body to a temp file with the Write tool, then use `--body-file` to avoid shell quoting issues with multi-line content.

> **Title generation:** Spawn a subagent using the `claude-haiku-4-5-20251001` model to generate a concise, domain-language title from the Epic's Goal. Pass in the Goal text and ask for a title (no prefix emoji/label needed — that is added below).

```bash
# Ensure the label exists before creating the issue
gh label create epic --color 5319e7 --description "Strategic initiative spanning multiple features" 2>/dev/null || true

gh issue create --title "🎯 Epic: <title>" --body-file /tmp/wtf.epic-$(date +%s)-body.md --label "epic"
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

Ask "What's next?" — header `Next step`:

- **Plan all Features** → invoke `wtf.epic-to-features`, passing the Epic number in as context (default)
- **Write one Feature** → proceed with `wtf.write-feature`, passing the Epic number in as context so the user is not asked for it again
- **Write another Epic** → restart this skill from step 1
- **Stop here** → exit, no further action

> Suggest clearing context before continuing to features if the conversation has grown long: "The context is getting long — you may want to `/clear` before continuing."
