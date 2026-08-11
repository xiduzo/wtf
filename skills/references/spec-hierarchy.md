# Spec Hierarchy Traversal

Shared procedure to fetch the Trace → Feature → Epic chain when a skill needs upstream context.

Used by `wtf.write-trace`, `wtf.write-feature`, `wtf.feature-to-traces`, `wtf.implement-trace`, `wtf.pr-review`, `wtf.design-trace`, `wtf.design-feature`, `wtf.create-pr`, `wtf.changelog`, `wtf.verify-trace`.

Legacy Task issues walk the same chain. A Task is a legacy Trace — see `./issue-classification.md`.

## Pick the entry point

| Have | Walk to |
|---|---|
| Trace number | Feature, then Epic |
| Feature number | Epic (down to children only when planning) |
| Epic number | Children only |
| PR | Extract Trace number from `Closes #<n>` in body |
| Branch | Extract Trace number from `trace/<n>-<slug>` |

## Extension-first traversal (preferred)

Requires `gh-sub-issue-available` from `./gh-setup.md`. Fetch in parallel where possible:

```bash
# From a Trace — find Feature, then Epic:
gh issue view <trace_number>
gh sub-issue list <trace_number> --relation parent --json number --jq '.[0].number'   # → feature_number
gh sub-issue list <feature_number> --relation parent --json number --jq '.[0].number' # → epic_number
gh issue view <feature_number>
gh issue view <epic_number>
```

```bash
# From a Feature — find Epic, optionally fetch sibling Features and child Traces:
gh sub-issue list <feature_number> --relation parent --jq '.[0].number'  # → epic_number
gh sub-issue list <epic_number>      # sibling Features (when needed)
gh sub-issue list <feature_number>   # child Traces (when planning)
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

Use `gh issue view <n> --json body --jq .body` and a regex that extracts `#(\d+)` after `Feature:` / `Epic:`. If the body has no Context section, ask the user. Do not invent the parent.

## Extracting from a PR or branch

```bash
# PR body — closure keyword:
gh pr view <pr_number> --json body --jq '.body' | grep -oE 'Closes #[0-9]+' | head -1

# Branch name — trace/<n>-<slug> (legacy task/<n>-<slug> also matches):
git rev-parse --abbrev-ref HEAD | grep -oE '^(trace|task)/[0-9]+' | grep -oE '[0-9]+'
```

## Caching across a session

Once fetched, each issue body is stable for the session. Skills that re-invoke each other (e.g. `wtf.feature-to-traces` → `wtf.write-trace`, `wtf.implement-trace` → `wtf.verify-trace`) should pass parent issue numbers via context rather than re-traverse. Every walk costs API calls. Re-fetch only when the body may have changed (after a `gh issue edit`).

## What to extract per level

| Level | Extract |
|---|---|
| Trace | Story, Scenario Claim, synced scenario copy, Spine position, Technical Approach, DoD |
| Feature | Acceptance Criteria, User Stories with canonical Gherkin scenarios, Edge Cases, Domain Events, Bounded Context, Trace Plan, delivery override (when present) |
| Epic | Goal, Context, Success Metrics, Bounded Context, Design Artifacts |

Legacy Task bodies keep the old sections. Extract Functional Description, Gherkin scenarios, Contracts & Interfaces, Impacted Areas, Test Mapping, and DoD from those.
