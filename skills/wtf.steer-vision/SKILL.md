---
name: wtf.steer-vision
description: This skill should be used when a team wants to create or refine the project vision document — for example "create the vision document", "write our product constitution", "define the product principles", "document our bounded contexts", "what is our product vision", "set up the steering docs", "update our vision", "revise the product strategy", "align on product goals", "what are we building and why", "who are our users", "capture our product purpose", or "the vision doc is outdated". Generates docs/steering/VISION.md as a living document capturing product purpose, target users, principles, strategic goals, and bounded contexts. Generated once and refined — not regenerated from scratch.
---

# Steer Vision

Generate or refine `docs/steering/VISION.md` — the product constitution. This document is the highest-level steering artifact: it captures why the product exists, who it serves, and what principles govern every decision.

The shared steering-doc flow (exists-check → research → interview → draft → review → write → wiki sync → continue) lives in `../references/steering-doc-process.md`. Follow that process with the skill-specific inputs below. Apply `../references/questioning-style.md` for every user question.

- **Doc path:** `docs/steering/VISION.md`
- **Template:** `references/vision-template.md`
- **Display name / wiki page:** `WTF-Vision.md`
- **Commit message:** `docs: add project vision steering document`

## Step 2 — Research checklist

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

## Step 3 — Gap-topic list

Ask only about items research could not determine, in priority order:

1. **Product purpose** — "What problem does this product solve, and for whom?" Pre-fill with purpose statements inferred from README or codebase.
2. **Target users** — "Who are the primary users? Use their domain role names." Pre-fill with named roles inferred from the codebase.
3. **Core principles** — "What 3–5 principles guide every product decision?" Pre-fill with principles inferred from `CLAUDE.md` or READMEs.
4. **Strategic goals** — "What does success look like in 12–18 months?" Pre-fill with goals inferred from open Epics or README.
5. **Bounded contexts** — "Which domain contexts does this product span?" Pre-fill with contexts inferred from module structure or Epic vocabulary.
6. **Out of scope** — "What is explicitly out of scope?" Pre-fill with exclusions found in existing docs or issue discussions.

## Step 4 — Writing rules

- Every sentence uses domain language — the words domain experts and stakeholders use.
- Target users are named domain actors, never "users" or "admins".
- Strategic goals are business outcomes, not features or technical tasks.
- Bounded context names are consistent with vocabulary found in the codebase.

## Step 8 — Continue options

- `{label: "Create TECH.md", description: "Run wtf.steer-tech to document the technical guidelines"}`
- `{label: "Create DESIGN.md", description: "Run wtf.steer-design to document the design guidelines"}`
- `{label: "Create QA.md", description: "Run wtf.steer-qa to document the QA standards"}`
- `{label: "Stop here", description: "Exit — no further action"}`
