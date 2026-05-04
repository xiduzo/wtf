---
name: wtf.steer-qa
description: This skill should be used when a team wants to create or refine the QA standards document — for example "create the QA steering doc", "document our test strategy", "write the QA standards", "document our definition of done", "set up the QA guidelines", or "update the QA doc". Generates docs/steering/QA.md as a living document capturing test strategy, coverage thresholds, test patterns, definition of done, and environments. Generated once and refined — not regenerated from scratch.
---

# Steer QA

Generate or refine `docs/steering/QA.md` — the QA standards document. This document is the canonical reference for test strategy, coverage requirements, test patterns, and the definition of done that every implementer and QA engineer must follow.

The shared steering-doc flow (exists-check → research → interview → draft → review → write → wiki sync → continue) lives in `../references/steering-doc-process.md`. Follow that process with the skill-specific inputs below.

- **Doc path:** `docs/steering/QA.md`
- **Template:** `references/qa-template.md`
- **Display name / wiki page:** `WTF-QA.md`
- **Commit message:** `docs: add QA standards steering document`

## Step 2 — Research checklist

Use the Agent tool to extract QA facts directly. Do not ask the user for things that can be read:

- **Test framework:** test runner config (`vitest.config.ts`, `jest.config.js`, `pytest.ini`, etc.)
- **Test scripts:** `package.json` scripts for `test`, `test:watch`, `test:coverage`
- **Coverage config:** coverage thresholds in test config files
- **Test file conventions:** where tests live, naming patterns (`.test.ts`, `.spec.ts`, `_test.go`, etc.)
- **Existing test types:** are there unit, integration, and e2e tests? What tools?
- **CI config:** `.github/workflows/` — what test gates run on PRs?
- **CLAUDE.md:** extract any testing rules already defined there
- **Known flaky areas:** `skip`, `xit`, `@pytest.mark.skip` usage or TODO comments in tests

Also check `docs/steering/TECH.md` if it exists — extract testing-related constraints already documented there.

Produce a concrete draft of Test Strategy, Test Patterns, and Commands from research alone.

## Step 3 — Gap-topic list

Ask only about items research could not determine. For each unanswered item, call `AskUserQuestion` (per `../references/questioning-style.md`):

1. **Coverage thresholds** — question: "What is the minimum acceptable test coverage?" / header: "Coverage thresholds" / options: pre-fill with thresholds found in test config or `CLAUDE.md`.
2. **Definition of Done** — question: "What must be true before any task can be merged?" / header: "Definition of Done" / options: pre-fill with DoD items from `CLAUDE.md` or existing task templates.
3. **Test environments** — question: "What environments are available for testing? (local, staging, CI)" / header: "Test environments" / options: pre-fill from CI config or README.
4. **Known flaky areas** — question: "Are there known areas that produce non-deterministic test failures?" / header: "Known flaky areas" / options: pre-fill with skipped tests or TODO comments found in step 2.
5. **Mock strategy** — question: "Are there project-specific exceptions to the 'only mock at boundaries' rule?" / header: "Mock strategy" / options: pre-fill with mock patterns found in existing tests.

## Step 4 — Writing rules

- Coverage thresholds are stated as enforced minimums, not targets.
- Test commands must be exact and match what CI actually runs.
- Definition of Done items are written as checkboxes — concrete and binary.
- Known Flaky Areas is honest, not aspirational — flag real issues.

## Step 8 — Continue options

- `{label: "Create VISION.md", description: "Run wtf.steer-vision to document the product vision"}`
- `{label: "Create TECH.md", description: "Run wtf.steer-tech to document the technical guidelines"}`
- `{label: "Create DESIGN.md", description: "Run wtf.steer-design to document the design guidelines"}`
- `{label: "Stop here", description: "Exit — no further action"}`
