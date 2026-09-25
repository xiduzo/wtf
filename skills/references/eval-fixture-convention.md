# Eval Fixture Convention

How to add evals to a wtf skill so the skill-creator plugin can run with-skill vs. without-skill benchmarks.

## Directory layout

```
skills/<skill-name>/
  evals/
    evals.json          ← eval definitions (required)
    fixtures/           ← mock data consumed by evals (optional)
      <scenario>.json
```

## evals.json format

```json
{
  "skill_name": "wtf.<skill-name>",
  "evals": [
    {
      "id": 1,
      "prompt": "The user message that triggers the skill",
      "expected_output": "Human-readable description of the correct output",
      "files": ["evals/fixtures/<scenario>.json"],
      "expectations": [
        "Specific, invariant assertion about the output"
      ]
    }
  ]
}
```

Fields match the skill-creator schema. See the plugin's `references/schemas.md`.

## Writing good expectations

- **Invariant over time.** "The 🕐 section includes trace #17" beats "The report shows 480 days stale." Exact numbers change. Structure does not.
- **Substring / presence checks.** "The report includes the phrase 'All open issues are in a healthy state'" is testable by a grader. "The report is well-formatted" is not.
- **Prefer regex-expressible invariants.** "The PR title matches `^(feat|fix|chore)(\([a-z-]+\))?: `" is robust. Exact strings break on prose edits.
- **3–5 expectations per eval.** Too few miss regressions. Too many make grading slow and brittle.

## Fixture files for skills that call `gh`

Most wtf skills run `gh issue list`, `gh pr list`, or similar commands. To make evals deterministic without a live repo:

1. Create a JSON fixture file with the mock data the `gh` command would return.
2. Structure it as a top-level object whose keys match the data the skill needs:
   ```json
   {
     "_note": "What this fixture represents",
     "epics": [...],
     "features": [...],
     "traces": [...],
     "bugs": [...],
     "pull_requests": [...]
   }
   ```
   A fixture that exercises the legacy-Task read path may also carry a `tasks` array with `task`-labeled issues.
3. In the eval `prompt`, include an explicit test-mode instruction:
   > "Test mode: skip step 0 (gh setup already confirmed). Instead of running `gh issue list` commands, read `evals/fixtures/<scenario>.json` and use its arrays as the live data."
4. List the fixture in `files` so the skill executor has access to it.

### `gh issue list --json number,title,labels,updatedAt` fixture shape

```json
[
  {
    "number": 42,
    "title": "Human-readable title",
    "labels": [{"name": "trace"}, {"name": "implemented"}],
    "updatedAt": "2026-05-02T14:30:00Z"
  }
]
```

### `gh pr list --json number,title,headRefName,body` fixture shape

```json
[
  {
    "number": 7,
    "title": "feat(settlement): add status field",
    "headRefName": "feat/settlement-status",
    "body": "Closes #42"
  }
]
```

## Staleness in fixtures

Set `updatedAt` far in the past (e.g. `"2025-01-01T10:00:00Z"`) for issues that should always appear as stale, no matter when the eval runs. Avoid dates that sit only barely past the threshold. A fixture set 8 days in the past stops being stale after one week of clock drift or timezone differences.

## Skills suitable for evals

Best candidates have deterministic, assertable outputs:

| Suitability | Criterion |
|---|---|
| Excellent | Pure classifier — input state → structured report |
| Good | Template-driven output — sections and labels are assertable |
| Poor | Heavy interactive flow (`AskUserQuestion` at every step) |
| Poor | Research-heavy or Figma-dependent (non-deterministic) |

See `docs/future-work/add-evals.md` for the full candidate ranking.

## Running evals

Install the skill-creator plugin in Claude Code. Then use its test loop pointed at the skill path:

```
/skill-creator test skills/wtf.health
```

The harness runs each eval twice (with skill / without skill). It grades against expectations. It writes results to `benchmarks/<timestamp>/`.
