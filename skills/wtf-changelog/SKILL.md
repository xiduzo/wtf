---
name: wtf.changelog
description: This skill should be used when a developer wants to generate release notes or a changelog entry after merging a Feature or closing an Epic — for example "write the changelog", "generate release notes", "what shipped in this release", "create a GitHub Release for this feature", "document what we built", "update CHANGELOG.md", or "summarize what merged". Derives user-facing language from closed Task Gherkin scenarios and Feature Acceptance Criteria rather than from raw commit messages.
---

# Changelog

Generate a changelog entry or GitHub Release from merged work. Core value: derives user-facing language from the spec hierarchy (Epic → Feature → Task Gherkin) rather than raw commit messages — so the output reads as product changes, not implementation details.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.

Skip this step if gh-setup was already confirmed this session.

### 1. Identify the release scope

Call `AskUserQuestion` with:

- `question`: "What are you writing a changelog entry for?"
- `header`: "Release scope"
- `options`:
  - `{label: "A Feature", description: "Changelog for all Tasks merged under one Feature"}`
  - `{label: "An Epic", description: "Changelog for all Features merged under one Epic"}`
  - `{label: "A date range", description: "All merged PRs between two dates"}`

**Feature scope:** fetch the Feature and its closed child tasks:

```bash
gh issue view <feature_number>
gh sub-issue list <feature_number>        # get task numbers
# For each task (in parallel):
gh issue view <task_number>               # Gherkin, Functional Description
```

**Epic scope:** fetch the Epic and walk the full hierarchy:

```bash
gh issue view <epic_number>
gh sub-issue list <epic_number>           # feature numbers
# For each feature (in parallel):
gh issue view <feature_number>
gh sub-issue list <feature_number>        # task numbers
# For each task (in parallel):
gh issue view <task_number>
```

**Date range scope:** fetch merged PRs between two dates:

```bash
gh pr list --state merged --json number,title,mergedAt,body \
  --jq '[.[] | select(.mergedAt >= "<start>" and .mergedAt <= "<end>")]'
```

### 2. Classify changes by type

For each closed Feature or Task, classify it as:

| Type | Signal |
|------|--------|
| **New feature** | Task label is `task`, no prior issue for same capability |
| **Improvement** | Refactor, performance, or UX enhancement Gherkin |
| **Bug fix** | Linked bug issue, or Gherkin scenario describes a failure path now handled |
| **Breaking change** | Contract change in Task Contracts section, or `!` in PR title |
| **Deprecation** | Mentioned in Feature ACs or Task Functional Description |

### 3. Derive user-facing change descriptions

For each item in scope:

- Extract the domain actor and business outcome from the Feature capability name or Task Functional Description
- Use the Gherkin `Then` steps as the concrete observable change (translated to plain language)
- Do NOT use implementation language ("refactored X", "migrated Y", "updated the API") — use domain outcomes ("Merchants can now filter settlements by date range")
- Remove internal-only changes (test infrastructure, CI config, internal refactors with no user-facing effect) unless the release includes no other changes

### 4. Draft the changelog entry

Follow [Keep a Changelog](https://keepachangelog.com) conventions:

```markdown
## [<version or date>] — <YYYY-MM-DD>

### Added
- <Domain Actor> can now <business action> — [#<issue>](<url>)

### Changed
- <What changed from the user's perspective> — [#<issue>](<url>)

### Fixed
- <What was broken and is now resolved> — [#<issue>](<url>)

### Breaking Changes
- <What changed that requires action from integrators or users> — [#<issue>](<url>)
```

Omit any section that has no entries. For Epic-level changelogs, group entries under Feature headings if there are more than 5 entries.

### 5. Review with user

Show the draft. Then call `AskUserQuestion` with:

- `question`: "Does this accurately describe what shipped?"
- `header`: "Review"
- `options`: `[{label: "Looks good — write it", description: "Proceed"}, {label: "Missing items", description: "I want to add something"}, {label: "Wrong language", description: "I want to adjust the phrasing"}]`

Apply edits, then proceed.

### 6. Write the output

Call `AskUserQuestion` with:

- `question`: "Where should the changelog go?"
- `header`: "Output"
- `options`: `[{label: "Update CHANGELOG.md", description: "Prepend the entry to CHANGELOG.md"}, {label: "Create a GitHub Release", description: "Publish as a GitHub Release (tag required)"}, {label: "Both", description: "Write to CHANGELOG.md and create a GitHub Release"}]`

**Update CHANGELOG.md:**

Read the current file (or create it with a `# Changelog` header if missing). Prepend the new entry after the `# Changelog` heading, above any existing entries.

```bash
git add CHANGELOG.md
git commit -m "chore(changelog): add release notes for <scope>"
```

**Create a GitHub Release:**

Call `AskUserQuestion` with `question: "What tag should this release use?"`, `header: "Tag"`, and `options` pre-filled from `git tag --sort=-version:refname | head -5` (recent tags), plus `{label: "I'll type a new tag", description: "e.g. v1.2.0"}`.

```bash
gh release create <tag> \
  --title "<release title>" \
  --notes-file /tmp/wtf-release-notes-<tag>.md
```

Print the release URL or CHANGELOG.md path.
