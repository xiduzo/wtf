---
name: wtf.changelog
description: This skill should be used when a developer wants to generate release notes or a changelog entry after merging a Feature or closing an Epic — for example "write the changelog", "generate release notes", "what shipped in this release", "create a GitHub Release for this feature", "document what we built", "update CHANGELOG.md", or "summarize what merged". Derives user-facing language from closed Task Gherkin scenarios and Feature Acceptance Criteria rather than from raw commit messages.
---

# Changelog

Generate a changelog entry or GitHub Release from merged work. Core value: derives user-facing language from the spec hierarchy (Epic → Feature → Task Gherkin) rather than raw commit messages — so the output reads as product changes, not implementation details.

Shared behavior:

- User-question style → `../references/questioning-style.md`
- Commit / tag / release syntax → `../references/commit-conventions.md`

## Process

### 0. GitHub CLI setup

Run `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

### 1. Identify the release scope

If an Epic or Feature number was already passed in as context (e.g. from `wtf.retro`), skip the question and use it directly.

Otherwise ask the user whether the changelog covers a Feature, an Epic, or a date range. Each scope has distinct follow-up queries:

- **Feature scope** — walk the Feature and its closed child tasks per `../references/spec-hierarchy.md` to extract Gherkin and Functional Description per task.
- **Epic scope** — walk Epic → Features → Tasks per the same reference, in parallel at each level.
- **Date range scope** — fetch merged PRs between two dates via `gh pr list --state merged --json number,title,mergedAt,body` and filter with `--jq`.

### 2. Classify and translate each change

For every closed Feature or Task in scope, do two things in one pass:

**a. Classify** into one of these buckets using the signal column:

| Type | Signal |
|---|---|
| **Added** | New capability — Feature or Task implements a previously-unavailable user action |
| **Changed** | Refactor, performance, or UX enhancement reflected in Gherkin `Then` steps |
| **Fixed** | Linked bug issue, or Gherkin scenario describes a failure path that now passes |
| **Deprecated** | Mentioned in Feature ACs or Task Functional Description as phasing out |
| **Removed** | Task or Feature explicitly tears down prior behavior |
| **Breaking** | Contract change in Task Contracts section, `!` in PR title, or `BREAKING CHANGE:` trailer per `../references/commit-conventions.md` |

**b. Translate into user-facing language:**

- Pull the domain actor and business outcome from the Feature capability name or Task Functional Description.
- Use the Gherkin `Then` steps as the concrete observable change, translated to plain language.
- Do NOT use implementation vocabulary ("refactored X", "migrated Y", "updated the API") — use domain outcomes ("Merchants can now filter settlements by date range").
- Drop internal-only work (test infra, CI config, internal refactors with no user-facing effect) unless the release contains nothing else.

### 3. Draft the changelog entry

Follow [Keep a Changelog](https://keepachangelog.com) conventions. Omit any section with no entries. For Epic-level changelogs, group entries under Feature headings if there are more than 5 entries.

```markdown
## [<version or date>] — <YYYY-MM-DD>

### Added
- <Domain Actor> can now <business action> — [#<issue>](<url>)

### Changed
- <What changed from the user's perspective> — [#<issue>](<url>)

### Fixed
- <What was broken and is now resolved> — [#<issue>](<url>)

### Deprecated
- <What is being phased out and the replacement> — [#<issue>](<url>)

### Removed
- <What was removed and the migration path> — [#<issue>](<url>)

### Breaking
- <What requires action from integrators or users> — [#<issue>](<url>)
```

### 4. Review with user

Show the draft and ask whether it accurately describes what shipped. Offer three paths: approve and write, add missing items, or adjust the phrasing. Apply edits, then proceed.

### 5. Choose the output target

Ask the user whether to update `CHANGELOG.md`, create a GitHub Release, or do both.

### 6. Write CHANGELOG.md (if selected)

Read the current file (or create it with a `# Changelog` header if missing). Prepend the new entry after the `# Changelog` heading, above any existing entries.

Commit per `../references/commit-conventions.md`:

```bash
git add CHANGELOG.md
git commit -m "chore(changelog): add release notes for <scope>"
```

### 7. Create the GitHub Release (if selected)

Ask which tag to use. Pre-fill the options with recent tags from `git tag --sort=-version:refname | head -5`, plus an escape hatch for a new tag (the user types it).

Write the entry to a temp file and create the release:

```bash
gh release create <tag> \
  --title "<release title>" \
  --notes-file /tmp/wtf.release-notes-<tag>.md
```

### 8. Report and offer to continue

Print the release URL and/or `CHANGELOG.md` path. Then offer two paths: continue with `wtf.retro` to close out the Epic (recommended when the changelog covered an Epic), or exit.
