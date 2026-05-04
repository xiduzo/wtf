# Task: Add evals to deterministic skills

**Status:** Complete for all viable candidates (2026-05-04). All skills rated Excellent or Good in the table below have evals. Fair and Poor candidates have been assessed and documented. See CLAUDE.md for the full eval inventory.

## What

Add `evals/evals.json` + `evals/fixtures/` to skills whose output is objectively verifiable. Use the skill-creator plugin's harness (`aggregate_benchmark.py`, `generate_review.py`) to run with-skill vs. without-skill comparisons, grade assertions, and produce pass-rate / time / token benchmarks.

## Why

1. **Regression detection.** Skills in `skills/` get edited frequently. Right now the only way to confirm a change didn't break something is manual walkthrough. Evals turn that into an automated pass/fail signal.
2. **Proof of value.** Skill-creator runs each prompt twice — with the skill and without — so it surfaces cases where Claude would have done equally well freehand. Dead-weight skills become visible.
3. **Description tuning.** Skill-creator has a loop that optimizes the `description:` frontmatter against trigger-eval queries. wtf descriptions are long and deliberately "pushy" (per skill-creator guidance) — currently guesswork; eval-driven tuning would measure which phrasings actually fire.
4. **Skill-as-spec.** Eval files double as concrete examples of the skill's contract — often easier to read than `SKILL.md`.

## Candidate ranking

Best → worst for simple (single-turn) evals:

| Skill | Suitability | Reason |
|---|---|---|
| `wtf.health` | Excellent ✅ | Pure classifier: GitHub issue state → triage report. Mock `gh issue list` JSON as fixture, assert report text. |
| `wtf.loop` step 2d (conflict graph) | Excellent ✅ | Pure function: task set + impacted areas → sub-phase partition. Easy to assert partition correctness. |
| `wtf.create-pr` (no-Task path) | Good ✅ | Diff + branch → PR title + body. Title assertable via Conventional Commits regex; body sections by substring. |
| `wtf.refine` classify step | Good ✅ | Issue body + insight text → change map. Assert which sections got marked dirty. |
| `wtf.changelog` | Good ✅ | Closed issues (fixtures) → Keep-a-Changelog markdown. Assert structure and absence of implementation vocabulary. |
| `wtf.write-task` | Good ✅ | Checkpoint evals: step 7 (Gherkin generation), step 9 (scope gate), step 3 (ambiguity clarification). Each is a deterministic sub-function isolated from the interactive steps. |
| `wtf.pr-review` | Good ✅ | Step 5 (review checklist) checkpoint: diff + task spec → PASS/FAIL/WARN per dimension. Missing test coverage, schema drift, and scope creep are all assertable. |
| `wtf.report-bug` | Good ✅ | Step 6 (bug report draft) checkpoint: failing scenario + task context → structured bug report. Assert all template sections present, Gherkin evidence included, domain language enforced. |
| `wtf.epic-to-features` | Good ✅ | Step 2 (feature list proposal) checkpoint: epic fixture → feature list. Assert Actor-verb-object pattern, domain language only, no re-proposal of already-created features. |
| `wtf.feature-to-tasks` | Good ✅ | Step 2 (task list proposal) checkpoint: feature fixture → task list. Assert vertical slices, migration tasks separated from behavior tasks, each task maps to at least one AC. |
| `wtf.write-epic`, `wtf.write-feature` | Poor (simple) | Heavy `AskUserQuestion` flow with no sub-step as deterministic as write-task's Gherkin generator or scope gate. Needs trajectory evals for meaningful coverage. |
| `wtf.reflect` | Fair ✅ | Step 4 routing (learning → TECH/QA/DESIGN/VISION) is deterministic. 5 evals cover all four targets plus the ambiguous-defaults-to-TECH case. |
| `wtf.hotfix` | Fair ✅ | Step 4 (branch naming), step 6 (scope gate), and step 8 (PR body structure) are all deterministic checkpoints. Implementation step is codebase-dependent and untested. |
| `wtf.retro` | Poor | Needs live GitHub issue/PR history to compare planned vs shipped. Cannot be fixture-mocked without enormous complexity. |
| `wtf.implement-task` | Poor | Codebase-dependent; every output is unique to the actual files changed. |
| `wtf.verify-task` | Poor | Needs running software and real test execution. |
| `wtf.setup` | Poor | Environment-dependent; output varies by installed tools and repo state. |
| `wtf.design-*` | Poor | Figma MCP coupling; non-deterministic outputs. |
| `wtf.steer-*` | Poor | Research-heavy; output depends on live codebase state. |

Skills marked ✅ have evals authored. See CLAUDE.md for the current table.

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

---

## Evaluating multi-step and interactive skills

The skills above ("Excellent/Good") are mostly single-turn: one input → one output. The interactive skills (`wtf.write-epic/feature/task`, `wtf.loop` end-to-end) involve multi-step reasoning, stateful decisions, and `AskUserQuestion` gates. These need a different approach.

### Trajectory evals (not single-turn)

Instead of checking one response, evaluate a **sequence of steps** — the path, not just the destination. Define the expected behavior at each step:

```json
{
  "task": "wtf.loop end-to-end — Feature #42",
  "steps": [
    { "input": "go", "expected_behavior": "asks which feature/epic to execute" },
    { "input": "Feature #42", "expected_behavior": "fetches hierarchy and builds dependency graph" },
    { "input": "approve plan", "expected_behavior": "starts task #10 in worktree, spawns implement sub-agent" }
  ]
}
```

Checkpoint evals are a useful lightweight form: pause mid-skill and ask "given current state, what should happen next?" — then compare expected vs actual next action. This isolates exactly where reasoning breaks rather than just observing final output quality.

### What to score

Define granular criteria for each skill — each becomes a scorable check:

| Criterion | Example check |
|---|---|
| Planning quality | Does `wtf.loop` partition tasks into correct phases? |
| Memory consistency | Does the skill remember a waived pre-condition 5 steps later? |
| Adaptation | Does `wtf.refine` correctly cascade when the user adds another insight? |
| Tool usage | Are `gh` commands called with correct flags? No hallucinated flags? |
| Completion | Does the skill reach a terminal state or stall in a loop? |

### Deterministic checks vs LLM-as-judge

Use both:

- **Deterministic:** JSON validity, correct label applied, step actually completed, no self-contradiction (check by regex / substring).
- **LLM-as-judge:** Coherence over the full trajectory, quality of decisions, whether constraints were respected. Use a rubric like "Score 1–5: did the skill maintain consistency across steps? Did it incorporate new constraints correctly? Did it avoid unnecessary steps?"

LLM judges are slower and cost more — reserve them for assertions that can't be expressed as substrings.

### Simulated environment

Multi-step evals need fake environments. For wtf skills this means:

- Pre-scripted `AskUserQuestion` responses (already handled by skill-creator's sub-agent protocol)
- Fixture-backed `gh` calls (same pattern as simple evals)
- Scripted `git` outputs for skills that inspect branches and diffs

The goal is a deterministic replay: same fixture → same trajectory every time.

### State drift and perturbation testing

Long skills degrade. Test these failure patterns explicitly:

| Failure pattern | What to inject |
|---|---|
| Forgets constraints after step 3 | Re-assert an early constraint mid-trajectory; check it's still respected |
| Overwrites previous decisions | Apply a conflicting instruction; verify the skill flags the conflict |
| Stops early and claims completion | Truncate expected output mid-flow; verify the skill does not self-declare done |
| Loops forever refining | Assert the skill reaches a terminal state within N steps |
| Hallucinated tool output | Inject a fixture where the expected `gh` result is empty; verify graceful handling |

Perturbation testing — changing requirements halfway, injecting ambiguous instructions — reveals whether the skill recovers gracefully or derails.

### Efficiency matters too

For multi-step skills, correctness alone is not enough. Also measure:

- **Step count** — did the skill take a direct path or circle?
- **Token usage** — does the with-skill run use fewer tokens than baseline (the skill should amortize setup cost)?
- **Redundant reasoning** — does the transcript show the skill re-deriving facts it already established?

Skill-creator's benchmark output already captures `total_tokens` and `duration_ms` per run; these are the right signals.

---

## Definition of done

- [x] `wtf.health` has a working `evals/evals.json` with ≥3 assertions.
- [x] Fixture convention is documented in `skills/references/eval-fixture-convention.md`.
- [x] `CLAUDE.md` has a section explaining how to run evals locally.
- [x] `wtf.loop`, `wtf.create-pr`, `wtf.refine`, `wtf.changelog` have simple evals authored.
- [x] At least one interactive skill (`wtf.write-task`) has checkpoint evals (Gherkin generation, scope gate, ambiguity clarification).
- [x] Common failure patterns covered: `wtf.loop` has contradiction-spec (spec contradiction) and external-blocker (external dep gate) perturbation evals; `wtf.refine` has conflicting-insights perturbation eval.
