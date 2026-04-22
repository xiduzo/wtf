# Task: Add evals to deterministic skills

**Status:** Not started. Surfaced during the 2026-04-22 refactor.

## What

Add `evals/evals.json` + `evals/fixtures/` to skills whose output is objectively verifiable. Use the skill-creator plugin's harness (`aggregate_benchmark.py`, `generate_review.py`) to run with-skill vs. without-skill comparisons, grade assertions, and produce pass-rate / time / token benchmarks.

## Why

1. **Regression detection.** Skills in `skills/` get edited frequently. Right now the only way to confirm a change didn't break something is manual walkthrough. Evals turn that into an automated pass/fail signal.
2. **Proof of value.** Skill-creator runs each prompt twice — with the skill and without — so it surfaces cases where Claude would have done equally well freehand. Dead-weight skills become visible.
3. **Description tuning.** Skill-creator has a loop that optimizes the `description:` frontmatter against trigger-eval queries. wtf descriptions are long and deliberately "pushy" (per skill-creator guidance) — currently guesswork; eval-driven tuning would measure which phrasings actually fire.
4. **Skill-as-spec.** Eval files double as concrete examples of the skill's contract — often easier to read than `SKILL.md`.

## Candidate ranking

Best → worst:

| Skill | Suitability | Reason |
|---|---|---|
| `wtf.health` | Excellent | Pure classifier: GitHub issue state → triage report. Mock `gh issue list` JSON as fixture, assert report text. |
| `wtf.loop` step 2d (conflict graph) | Excellent | Pure function: task set + impacted areas → sub-phase partition. Easy to assert partition correctness. |
| `wtf.create-pr` (no-Task path) | Good | Diff + branch → PR title + body. Title assertable via Conventional Commits regex; body sections by substring. |
| `wtf.refine` classify step | Good | Issue body + insight text → change map. Assert which sections got marked dirty. |
| `wtf.changelog` | Good | Closed issues (fixtures) → Keep-a-Changelog markdown. Assert structure and absence of implementation vocabulary. |
| `wtf.write-epic/feature/task` | Poor | Heavy `AskUserQuestion` flow — needs mocked user answers, adds complexity without proportional benefit. |
| `wtf.design-*` | Poor | Figma MCP coupling; non-deterministic outputs. |
| `wtf.steer-*` | Poor | Research-heavy; output depends on live codebase state. |

## Recommended starting point

`wtf.health` — lowest cost, highest signal. Build 3 evals:

1. Clean project (no findings) → assert "All open issues are in a healthy state".
2. Task `implemented` but not `verified` → assert the ⚠️ section contains it and the "Next" line suggests `wtf.verify-task`.
3. Task `designed` and stale >7 days → assert the 🕐 section contains it with the correct day count.

If that proves useful, extend to `wtf.loop` (highest regression risk — big recent refactor) and `wtf.create-pr`.

## How to run it

The skill-creator plugin is separate from this repo. To eval a wtf skill:

1. Install the skill-creator plugin in Claude Code.
2. Author `evals/evals.json` inside the target skill's folder (e.g. `skills/wtf.health/evals/evals.json`).
3. Add any fixture files the evals reference under `evals/fixtures/`.
4. Invoke skill-creator's test loop on the skill path. It handles with-skill vs. without-skill runs, grading, aggregation, and the eval viewer.

## Tradeoffs

- **Fixture maintenance.** One fixture set covers many evals, but when the `gh` CLI extension or issue template changes, fixtures need updating.
- **Interactivity.** Most wtf skills pause for `AskUserQuestion`. The skill-creator harness handles this via the sub-agent protocol (non-interactive overrides) already documented in `skills/references/subagent-protocol.md`.
- **Assertion brittleness.** Prefer invariant checks ("title matches `^(feat|fix|chore)(\([a-z-]+\))?: `") over exact-string checks — otherwise every prose tweak breaks the eval.

## Definition of done

- At least one skill (`wtf.health`) has a working `evals/evals.json` with ≥3 assertions.
- Fixture convention is documented in `skills/references/` so other skills can follow it.
- A short section added to `CLAUDE.md` or `README.md` explaining how to run evals locally.
