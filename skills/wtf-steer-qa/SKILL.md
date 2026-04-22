---
name: wtf.steer-qa
description: This skill should be used when a team wants to create or refine the QA standards document — for example "create the QA steering doc", "document our test strategy", "write the QA standards", "document our definition of done", "set up the QA guidelines", or "update the QA doc". Generates docs/steering/QA.md as a living document capturing test strategy, coverage thresholds, test patterns, definition of done, and environments. Generated once and refined — not regenerated from scratch.
---

# Steer QA

Generate or refine `docs/steering/QA.md` — the QA standards document. This document is the canonical reference for test strategy, coverage requirements, test patterns, and the definition of done that every implementer and QA engineer must follow.

See `references/qa-template.md` for the expected document shape.

## Process

### 1. Check if the document already exists

Use the Read tool to attempt reading `docs/steering/QA.md`.

If the file **exists**, call `AskUserQuestion` with:

- `question`: "docs/steering/QA.md already exists. What would you like to do?"
- `header`: "QA doc found"
- `options`: `[{label: "Refine it", description: "Review and improve the existing document"}, {label: "Exit", description: "Leave it as-is"}]`

- **Refine it** → read the current document, then skip to step 4 (use existing doc as context, only ask about gaps or outdated sections).
- **Exit** → exit immediately.

If the file **does not exist**, continue to step 2.

### 2. Research the codebase

Use the Agent tool to extract QA facts directly from the codebase. Do not ask the user for things that can be read:

- **Test framework:** test runner config (`vitest.config.ts`, `jest.config.js`, `pytest.ini`, etc.)
- **Test scripts:** `package.json` scripts for `test`, `test:watch`, `test:coverage`
- **Coverage config:** coverage thresholds in test config files
- **Test file conventions:** where tests live, naming patterns (`.test.ts`, `.spec.ts`, `_test.go`, etc.)
- **Existing test types:** are there unit, integration, and e2e tests? What tools?
- **CI config:** `.github/workflows/` — what test gates run on PRs?
- **CLAUDE.md:** extract any testing rules already defined there
- **Known flaky areas:** any `skip`, `xit`, `@pytest.mark.skip` usage or TODO comments in tests

Also check `docs/steering/TECH.md` if it exists — extract testing-related constraints already documented there.

Synthesise findings. Produce a concrete draft of Test Strategy, Test Patterns, and Commands from research alone.

### 3. Interview the user for gaps only

Only ask about what research could not determine. Work through questions **one at a time** using `AskUserQuestion`.

**Topics that may need input:**

1. **Coverage thresholds** — "What is the minimum acceptable test coverage?"
   - Pre-fill with thresholds found in test config or CLAUDE.md.
2. **Definition of Done** — "What must be true before any task can be merged?"
   - Pre-fill with DoD items from CLAUDE.md or existing task templates.
3. **Test environments** — "What environments are available for testing? (local, staging, CI)"
   - Pre-fill with environments inferred from CI config or README.
4. **Known flaky areas** — "Are there known areas that produce non-deterministic test failures?"
   - Pre-fill with skipped tests or TODO comments found in step 2.
5. **Mock strategy** — "Are there any project-specific exceptions to the 'only mock at boundaries' rule?"
   - Pre-fill with mock patterns found in existing tests.

Skip any topic already answered by research.

### 4. Draft the document

Using `references/qa-template.md` as the shape reference, fill in all sections with gathered context. Replace every `[PLACEHOLDER]` with real content derived from the codebase.

**Writing rules:**

- Coverage thresholds are stated as enforced minimums, not targets
- Test commands must be exact and match what CI actually runs
- Definition of Done items are written as checkboxes — concrete and binary
- Known Flaky Areas is honest, not aspirational — flag real issues

### 5. Review with user

Show the draft. Then call `AskUserQuestion` with `question: "Does this reflect the QA standards accurately?"`, `header: "Review"`, and `options: [{label: "Looks good — save it", description: "Write to docs/steering/QA.md"}, {label: "I have changes", description: "I want to adjust something first"}]`.

Apply edits, then proceed.

### 6. Write the document

```bash
mkdir -p docs/steering
```

Write the final content to `docs/steering/QA.md`.

Commit the file:

```bash
git add docs/steering/QA.md
git commit -m "docs: add QA standards steering document"
```

Print the file path.

### 7. Offer wiki sync

Call `AskUserQuestion` with:

- `question`: "Would you like to sync this to the GitHub wiki?"
- `header`: "Wiki sync"
- `options`: `[{label: "Yes — push to wiki", description: "Publish QA.md as a wiki page"}, {label: "Not now", description: "Skip wiki sync"}]`

If **yes**:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
WIKI_DIR=$(mktemp -d -t wtf-wiki-sync-qa-XXXXXX)
git clone https://github.com/$REPO.wiki.git "$WIKI_DIR"
cp docs/steering/QA.md "$WIKI_DIR/WTF-QA.md"
(cd "$WIKI_DIR" && git add WTF-QA.md && git commit -m "Sync: QA standards" && git push)
rm -rf "$WIKI_DIR"
```

### 8. Offer to continue

Call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Create VISION.md", description: "Run `steer-vision` to document the product vision"}, {label: "Create TECH.md", description: "Run `steer-tech` to document the technical guidelines"}, {label: "Create DESIGN.md", description: "Run `steer-design` to document the design guidelines"}, {label: "Stop here", description: "Exit — no further action"}]`

Route to the appropriate skill based on the answer.
