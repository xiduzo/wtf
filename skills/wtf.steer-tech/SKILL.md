---
name: wtf.steer-tech
description: This skill should be used when a team wants to create or refine the technical guidelines document — for example "create the tech steering doc", "document our tech stack", "write the technical guidelines", "document our architecture decisions", "set up the tech steering", or "update the tech doc". Generates docs/steering/TECH.md as a living document capturing the stack, architecture patterns, constraints, commands, and ADRs. Generated once and refined — not regenerated from scratch.
---

# Steer Tech

Generate or refine `docs/steering/TECH.md` — the technical guidelines document. This document is the canonical reference for the stack, architectural patterns, and constraints every implementer must follow.

The shared steering-doc flow (exists-check → research → interview → draft → review → write → wiki sync → continue) lives in `../references/steering-doc-process.md`. Follow that process with the skill-specific inputs below.

- **Doc path:** `docs/steering/TECH.md`
- **Template:** `references/tech-template.md`
- **Display name / wiki page:** `WTF-Tech.md`
- **Commit message:** `docs: add technical guidelines steering document`

## Step 2 — Research checklist

Use the Agent tool to extract technical facts directly. Do not ask the user for things that can be read:

- **Stack:** `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `*.csproj`, or equivalent — languages, frameworks, versions
- **Architecture:** module structure, folder layout, layer separation patterns
- **Test framework:** existing test files, test scripts in `package.json`
- **Commands:** `package.json` scripts, `Makefile`, `justfile`, CI config
- **ADRs:** any `docs/adr/`, `docs/decisions/`, or inline decision records
- **Conventions:** naming patterns, import paths, test file locations
- `CLAUDE.md` and any existing architectural docs

Produce a concrete draft of Stack, Commands, and Code Conventions from research alone — these sections should require no user input.

## Step 3 — Gap-topic list

Ask only about items research could not determine. For each unanswered item, call `AskUserQuestion` (per `../references/questioning-style.md`):

1. **Key constraints** — question: "Are there non-negotiables every implementer must respect?" / header: "Key constraints" / options: pre-fill with constraints from `CLAUDE.md` or existing docs.
2. **Architecture decisions** — question: "Are there decisions that shaped the architecture but aren't documented yet?" / header: "Architecture decisions" / options: pre-fill with patterns inferred from the codebase structure.
3. **Known pain points** — question: "Are there areas of the codebase that need special care?" / header: "Known pain points" / options: pre-fill with anything flagged in README or comments.

## Step 4 — Writing rules

- Commands must be exact and tested — stale commands are worse than no commands.
- Architecture description reflects what the codebase actually does, not aspirations.
- Constraints are written as imperatives ("No synchronous I/O on the request path").
- ADRs link to source files where they exist; inline only the decision and rationale.

## Step 8 — Continue options

- `{label: "Create DESIGN.md", description: "Run wtf.steer-design to document the design guidelines"}`
- `{label: "Create QA.md", description: "Run wtf.steer-qa to document the QA standards"}`
- `{label: "Create VISION.md", description: "Run wtf.steer-vision to document the product vision"}`
- `{label: "Stop here", description: "Exit — no further action"}`
