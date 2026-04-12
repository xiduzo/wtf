---
name: wtf.steer-vision
description: This skill should be used when a team wants to create or refine the project vision document — for example "create the vision document", "write our product constitution", "define the product principles", "document our bounded contexts", "what is our product vision", or "set up the steering docs". Generates docs/steering/VISION.md as a living document capturing product purpose, target users, principles, strategic goals, and bounded contexts. Generated once and refined — not regenerated from scratch.
---

# Steer Vision

Generate or refine `docs/steering/VISION.md` — the product constitution. This document is the highest-level steering artifact: it captures why the product exists, who it serves, and what principles govern every decision.

See `references/vision-template.md` for the expected document shape.

## Process

### 1. Check if the document already exists

Use the Read tool to attempt reading `docs/steering/VISION.md`.

If the file **exists**, call `AskUserQuestion` with:

- `question`: "docs/steering/VISION.md already exists. What would you like to do?"
- `header`: "Vision doc found"
- `options`: `[{label: "Refine it", description: "Review and improve the existing document"}, {label: "Exit", description: "Leave it as-is"}]`

- **Refine it** → read the current document, then skip to step 4 (skip research and questioning — use the existing doc as context, only ask about gaps or outdated sections).
- **Exit** → exit immediately.

If the file **does not exist**, continue to step 2.

### 2. Research the codebase and existing docs

Run in parallel using the Agent tool:

**Codebase signals:**

- README for product description and stated goals
- Any existing `docs/` files, ADRs, or architectural notes
- Domain language in file names, module names, and type definitions
- Existing wiki pages or glossary files

**GitHub signals (optional — skip if unavailable):**

- Open and closed Epics (issues labeled `epic`) for strategic intent
- Any issues or discussions referencing product goals or principles

Synthesise internally. Do not dump raw research at the user.

### 3. Interview the user

Using what research revealed, ask questions to close gaps. Work through them **one at a time** using `AskUserQuestion`. Only ask what research did not already answer.

**Topics in priority order:**

1. **Product purpose** — "What problem does this product solve, and for whom?"
   - Pre-fill options with 1–2 purpose statements inferred from the README or codebase.
2. **Target users** — "Who are the primary users? Use their domain role names."
   - Pre-fill with named roles inferred from the codebase (e.g. actors found in issue labels, code, or docs).
3. **Core principles** — "What 3–5 principles guide every product decision?"
   - Pre-fill with principles inferred from existing guidelines (CLAUDE.md, READMEs).
4. **Strategic goals** — "What does success look like in 12–18 months?"
   - Pre-fill with goals inferred from open Epics or README.
5. **Bounded contexts** — "Which domain contexts does this product span?"
   - Pre-fill with contexts inferred from module structure or Epic vocabulary.
6. **Out of scope** — "What is explicitly out of scope?"
   - Pre-fill with exclusions found in existing docs or issue discussions.

Stop when you have enough to write a complete draft. Do not ask questions you can confidently answer from research.

### 4. Draft the document

Using `references/vision-template.md` as the shape reference, fill in all sections with gathered context. Replace every `[PLACEHOLDER]` with real content.

**Writing rules:**

- Every sentence uses domain language — the words domain experts and stakeholders use
- Target users are named domain actors, never "users" or "admins"
- Strategic goals are business outcomes, not features or technical tasks
- Bounded context names are consistent with vocabulary found in the codebase

### 5. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this capture the product vision accurately?"`, `header: "Review"`, and `options: [{label: "Looks good — save it", description: "Write to docs/steering/VISION.md"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed.

### 6. Write the document

```bash
mkdir -p docs/steering
```

Write the final content to `docs/steering/VISION.md`.

Commit the file:

```bash
git add docs/steering/VISION.md
git commit -m "docs: add project vision steering document"
```

Print the file path.

### 7. Offer wiki sync

Call `AskUserQuestion` with:

- `question`: "Would you like to sync this to the GitHub wiki?"
- `header`: "Wiki sync"
- `options`: `[{label: "Yes — push to wiki", description: "Publish VISION.md as a wiki page"}, {label: "Not now", description: "Skip wiki sync"}]`

If **yes**:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
git clone https://github.com/$REPO.wiki.git /tmp/wiki-sync
cp docs/steering/VISION.md /tmp/wiki-sync/WTF-Vision.md
cd /tmp/wiki-sync && git add WTF-Vision.md && git commit -m "Sync: project vision" && git push
rm -rf /tmp/wiki-sync
```

### 8. Offer to continue

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Create TECH.md", description: "Run `steer-tech` to document the technical guidelines"}, {label: "Create DESIGN.md", description: "Run `steer-design` to document the design guidelines"}, {label: "Create QA.md", description: "Run `steer-qa` to document the QA standards"}, {label: "Stop here", description: "Exit — no further action"}]`

Route to the appropriate skill based on the answer.
