---
name: wtf:steer-tech
description: This skill should be used when a team wants to create or refine the technical guidelines document — for example "create the tech steering doc", "document our tech stack", "write the technical guidelines", "document our architecture decisions", "set up the tech steering", or "update the tech doc". Generates docs/steering/TECH.md as a living document capturing the stack, architecture patterns, constraints, commands, and ADRs. Generated once and refined — not regenerated from scratch.
---

# Steer Tech

Generate or refine `docs/steering/TECH.md` — the technical guidelines document. This document is the canonical reference for the stack, architectural patterns, and constraints every implementer must follow.

See `references/tech-template.md` for the expected document shape.

## Process

### 1. Check if the document already exists

```bash
cat docs/steering/TECH.md 2>/dev/null
```

If the file **exists**, call `AskUserQuestion` with:

- `question`: "docs/steering/TECH.md already exists. What would you like to do?"
- `header`: "Tech doc found"
- `options`: `[{label: "Refine it", description: "Review and improve the existing document"}, {label: "Exit", description: "Leave it as-is"}]`

- **Refine it** → read the current document, then skip to step 4 (use existing doc as context, only ask about gaps or outdated sections).
- **Exit** → exit immediately.

If the file **does not exist**, continue to step 2.

### 2. Research the codebase

Use the Agent tool to extract technical facts directly from the codebase. Do not ask the user for things that can be read:

- **Stack:** `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `*.csproj`, or equivalent — extract languages, frameworks, and versions
- **Architecture:** module structure, folder layout, layer separation patterns
- **Test framework:** existing test files, test scripts in `package.json`
- **Commands:** `package.json` scripts, `Makefile`, `justfile`, CI config
- **ADRs:** any `docs/adr/`, `docs/decisions/`, or inline decision records
- **Conventions:** naming patterns from existing files, import paths, test file locations
- **CLAUDE.md** and any existing architectural docs

Synthesise findings. Produce a concrete draft of Stack, Commands, and Code Conventions from this research alone — these sections should require no user input.

### 3. Interview the user for gaps only

Only ask about what research could not determine. Work through questions **one at a time** using `AskUserQuestion`.

**Topics that may need input:**

1. **Key constraints** — "Are there non-negotiables every implementer must respect?"
   - Pre-fill with constraints found in CLAUDE.md or existing docs.
2. **Architecture decisions** — "Are there key decisions that shaped the architecture that aren't documented yet?"
   - Pre-fill with patterns inferred from the codebase structure.
3. **Known pain points** — "Are there areas of the codebase that need special care?"
   - Pre-fill with anything flagged in README or comments.

Skip any topic already answered by research.

### 4. Draft the document

Using `references/tech-template.md` as the shape reference, fill in all sections with gathered context. Replace every `[PLACEHOLDER]` with real content derived from the codebase.

**Writing rules:**

- Commands must be exact and tested — stale commands are worse than no commands
- Architecture description reflects what the codebase actually does, not aspirations
- Constraints are written as imperatives ("No synchronous I/O on the request path")
- ADRs link to source files where they exist; inline only the decision and rationale

### 5. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this accurately reflect the technical setup?"`, `header: "Review"`, and `options: [{label: "Looks good — save it", description: "Write to docs/steering/TECH.md"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed.

### 6. Write the document

```bash
mkdir -p docs/steering
```

Write the final content to `docs/steering/TECH.md`.

Commit the file:

```bash
git add docs/steering/TECH.md
git commit -m "docs: add technical guidelines steering document"
```

Print the file path.

### 7. Offer wiki sync

Call `AskUserQuestion` with:

- `question`: "Would you like to sync this to the GitHub wiki?"
- `header`: "Wiki sync"
- `options`: `[{label: "Yes — push to wiki", description: "Publish TECH.md as a wiki page"}, {label: "Not now", description: "Skip wiki sync"}]`

If **yes**:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
git clone https://github.com/$REPO.wiki.git /tmp/wiki-sync
cp docs/steering/TECH.md /tmp/wiki-sync/WTF-Tech.md
cd /tmp/wiki-sync && git add WTF-Tech.md && git commit -m "Sync: technical guidelines" && git push
rm -rf /tmp/wiki-sync
```

### 8. Offer to continue

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Create DESIGN.md", description: "Run wtf:steer-design to document the design guidelines"}, {label: "Create QA.md", description: "Run wtf:steer-qa to document the QA standards"}, {label: "Create VISION.md", description: "Run wtf:steer-vision to document the product vision"}, {label: "Stop here", description: "Exit — no further action"}]`

Route to the appropriate skill based on the answer.
