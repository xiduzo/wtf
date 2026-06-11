# Spec Hierarchy Traversal

Shared procedure for fetching the Task → Feature → Epic chain when a skill needs upstream context.

Used by `wtf.write-task`, `wtf.write-feature`, `wtf.feature-to-tasks`, `wtf.implement-task`, `wtf.pr-review`, `wtf.design-task`, `wtf.design-feature`, `wtf.create-pr`, `wtf.changelog`, `wtf.verify-task`.

## Pick the entry point

| Have | Walk to |
|---|---|
| Task number | Feature, then Epic |
| Feature number | Epic (down to children only when planning) |
| Epic number | Children only |
| PR | Extract Task number from `Closes #<n>` in body |
| Branch | Extract Task number from `task/<n>-<slug>` |

## Extension-first traversal (preferred)

Requires `gh-sub-issue-available` from `./gh-setup.md`. Fetch in parallel where possible:

```bash
# From a Task — find Feature, then Epic:
gh issue view <task_number>
gh sub-issue list <task_number> --relation parent --json number --jq '.[0].number'   # → feature_number
gh sub-issue list <feature_number> --relation parent --json number --jq '.[0].number' # → epic_number
gh issue view <feature_number>
gh issue view <epic_number>
```

```bash
# From a Feature — find Epic, optionally fetch sibling Features and child Tasks:
gh sub-issue list <feature_number> --relation parent --jq '.[0].number'  # → epic_number
gh sub-issue list <epic_number>      # sibling Features (when needed)
gh sub-issue list <feature_number>   # child Tasks (when planning)
```

```bash
# From an Epic — fetch child Features:
gh sub-issue list <epic_number>      # child Features
```

## Body-scrape fallback (extension absent)

If `gh-sub-issue-available` is false, parse the issue body's `## Context` section:

```
## Context
- Feature: #<feature_number>
- Epic: #<epic_number>
```

Use `gh issue view <n> --json body --jq .body` and a regex extracting `#(\d+)` after `Feature:` / `Epic:`. If the body lacks a Context section, ask the user — do not invent the parent.

## Extracting from a PR or branch

```bash
# PR body — closure keyword:
gh pr view <pr_number> --json body --jq '.body' | grep -oE 'Closes #[0-9]+' | head -1

# Branch name — task/<n>-<slug>:
git rev-parse --abbrev-ref HEAD | grep -oE '^task/[0-9]+' | grep -oE '[0-9]+'
```

## Caching across a session

Once fetched, each issue body is stable for the session. Skills that re-invoke each other (e.g. `wtf.feature-to-tasks` → `wtf.write-task`, `wtf.implement-task` → `wtf.verify-task`) should pass parent issue numbers via context rather than re-traversing — every walk costs API calls. Re-fetch only when the body may have changed (after a `gh issue edit`).

## What to extract per level

| Level | Extract |
|---|---|
| Task | Functional Description, Gherkin scenarios, Contracts & Interfaces, Impacted Areas, Test Mapping, DoD |
| Feature | Acceptance Criteria, User Stories, Edge Cases, Domain Events, Bounded Context, Proposed Tasks |
| Epic | Goal, Context, Success Metrics, Bounded Context, Design Artifacts |
