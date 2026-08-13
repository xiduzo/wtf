# WTF — Claude Code Instructions

## Repo layout

- `skills/` — **source of truth** for all skill definitions. Always edit here.
- `skills/references/` — **source of truth** for cross-skill reference docs (see below). Skills load these at runtime via `../references/<name>.md`.
- `skills/wtf.setup/shared-references/` — **generated** vendored copy of `skills/references/` (minus dev-only `eval-fixture-convention.md`) that rides along in the `wtf.setup` payload. `npx skills add` installs each `wtf.*` skill dir individually, so `skills/references/` (no `SKILL.md`) never ships; `wtf.setup` carries this copy and writes it to `<skills-root>/references/` at setup time so installed skills can resolve `../references/...`. **Never edit by hand** — regenerate with `bash skills/wtf.setup/sync-shared-references.sh` after changing any reference doc.
- `skills/wtf.setup/hooks/` — scripts that ride along in the `wtf.setup` payload: `track-interventions.py` (registered into `settings.json`) and `gh-body.py` (a UTF-8-safe gh body utility copied into the repo at `.wtf/gh-body.py`, not a settings hook).
- `docs/` — project docs, including `docs/steering/` (VISION, TECH, QA, DESIGN), `docs/spikes/`, and `docs/adr/` (decision records).
- `CONTEXT.md` — the domain glossary: the DDD ubiquitous language for the WTF work model (Trace, Skeleton, Extension Trace, Deepening Trace, Spine, Spine Position, Scenario Claim, Re-aim). Use its terms exactly.
- `.claude/skills/` and `.agents/` — git-ignored. If a runtime installs or links WTF into this repo, that copy is disposable and always stale. **Never edit it, never commit it, never read it to answer a question about a skill** — read `skills/` instead. Delete it when it drifts.
- `.wtf/` — per-repo artifacts `wtf.setup` writes into the consuming repo: `gh-body.py` (the body helper) and `config.json` with four keys: `"classification": "types"|"labels"` (issue-kind mechanism, resolved via `skills/references/issue-classification.md`), `"planning": "guided"|"flow"` (interaction density, resolved via `skills/references/planning-mode.md`), `"feature_scope": "single-story"|"grouped"` (stories per Feature, resolved by `wtf.setup` / `wtf.write-feature` / `wtf.epic-to-features`), and `"delivery": "staged"|"trunk"` (where Trace PRs merge, resolved via `skills/references/branch-setup.md`).

## Canonical skill location

Edit skill files in `skills/<skill-name>/SKILL.md`. Any other path is a runtime artifact.

## Skill inventory

| Skill | File |
|---|---|
| ste-writing | `skills/ste-writing/SKILL.md` (ships the STE dictionary) |
| wtf.changelog | `skills/wtf.changelog/SKILL.md` |
| wtf.create-pr | `skills/wtf.create-pr/SKILL.md` |
| wtf.design-feature | `skills/wtf.design-feature/SKILL.md` |
| wtf.design-trace | `skills/wtf.design-trace/SKILL.md` |
| wtf.epic-to-features | `skills/wtf.epic-to-features/SKILL.md` |
| wtf.feature-to-traces | `skills/wtf.feature-to-traces/SKILL.md` |
| wtf.health | `skills/wtf.health/SKILL.md` |
| wtf.hotfix | `skills/wtf.hotfix/SKILL.md` |
| wtf.implement-trace | `skills/wtf.implement-trace/SKILL.md` |
| wtf.loop | `skills/wtf.loop/SKILL.md` |
| wtf.pr-review | `skills/wtf.pr-review/SKILL.md` |
| wtf.refine | `skills/wtf.refine/SKILL.md` |
| wtf.reflect | `skills/wtf.reflect/SKILL.md` |
| wtf.report-bug | `skills/wtf.report-bug/SKILL.md` |
| wtf.retro | `skills/wtf.retro/SKILL.md` |
| wtf.setup | `skills/wtf.setup/SKILL.md` |
| wtf.spike | `skills/wtf.spike/SKILL.md` |
| wtf.steer-design | `skills/wtf.steer-design/SKILL.md` |
| wtf.steer-qa | `skills/wtf.steer-qa/SKILL.md` |
| wtf.steer-tech | `skills/wtf.steer-tech/SKILL.md` |
| wtf.steer-vision | `skills/wtf.steer-vision/SKILL.md` |
| wtf.verify-trace | `skills/wtf.verify-trace/SKILL.md` |
| wtf.write-epic | `skills/wtf.write-epic/SKILL.md` |
| wtf.write-feature | `skills/wtf.write-feature/SKILL.md` |
| wtf.write-trace | `skills/wtf.write-trace/SKILL.md` |

Keep this table in sync with `skills/` when adding/removing skills.

## Skill invocation policy

**Never invoke wtf skills automatically.** Only activate on explicit `/` slash command (e.g. `/wtf.loop`, `/wtf.write-trace`). Do not auto-trigger from inferred intent, conversation context, or keywords — even when the user's phrasing matches a skill's description.

## Shared references

Cross-skill references live in `skills/references/`:

| File | Purpose |
|---|---|
| `branch-setup.md` | Trunk-based branch hierarchy, slug rules, worktree policy, delivery-mode resolve (`staged`/`trunk`) |
| `commit-conventions.md` | Commit message format used across skills |
| `conflict-graph.md` | File-conflict graph for parallel scheduling — across Features, and across a Feature's Traces once its Skeleton lands |
| `ddd-writing-rules.md` | Ubiquitous-language rules for issue/Gherkin authoring |
| `gh-body-helper.md` | Cross-platform UTF-8-safe issue/PR body read & write (`.wtf/gh-body.py`) |
| `gh-setup.md` | `gh` CLI + extension install + sub-issue/dependency cookbook |
| `issue-classification.md` | Native issue types vs. labels — mode resolve, classify, query, detect |
| `issue-template-loading.md` | Template verify + halt-or-setup + body-file create pattern |
| `lifecycle-labels.md` | Label semantics + absent/overwrite gate templates |
| `planning-mode.md` | `guided` vs `flow` planning — mode resolve, flow deltas, escalation |
| `questioning-style.md` | How skills should prompt the user |
| `scope-gates.md` | Definition-of-Ready / Definition-of-Done gates |
| `spec-hierarchy.md` | Trace → Feature → Epic traversal (extension + body-scrape) |
| `ste-writing.md` | Strict ASD-STE100 for durable artifacts; DDD glossary as TN/TV allowlist |
| `steering-doc-process.md` | How steering docs are created, refined, and consumed |
| `subagent-protocol.md` | Contract for subagent delegation |

Reference these from skills rather than duplicating content.

## Evals

Selected skills have evals for regression detection and proof-of-value benchmarking.

**Location:** `skills/<skill-name>/evals/evals.json` + `evals/fixtures/`

**Convention:** See `skills/references/eval-fixture-convention.md` — covers `evals.json` format, fixture structure for `gh`-calling skills, and how to write invariant expectations.

**Running evals:** Install the skill-creator plugin, then:
```
/skill-creator test skills/wtf.health
```
The harness runs each eval with-skill and without-skill, grades expectations, and writes results to `benchmarks/<timestamp>/`.

**Skills with evals:**

| Skill | Evals | Status |
|---|---|---|
| `wtf.health` | 3 (clean, implemented-not-verified, stale-designed) | ✅ |
| `wtf.loop` | 5 (linear-chain, parallel-features, diamond-file-conflict, contradiction-spec, external-blocker) | ✅ |
| `wtf.create-pr` | 3 (feat-branch, fix-branch, refactor-branch — no-Trace path) | ✅ |
| `wtf.refine` | 4 (scope-narrowed, domain-language-correction, technical-constraint, conflicting-insights) | ✅ |
| `wtf.changelog` | 3 (all-added, mixed-added-fixed, drop-internal-refactor) | ✅ |
| `wtf.write-trace` | 3 checkpoint evals (claim-selection, depth-split-draft, ambiguous-claim) | ✅ |
| `wtf.pr-review` | 3 checkpoint evals (missing-test-coverage, schema-drift, scope-creep) | ✅ |
| `wtf.report-bug` | 3 checkpoint evals (failing-gherkin-scenario, domain-language-restatement, no-linked-trace) | ✅ |
| `wtf.epic-to-features` | 3 checkpoint evals (multi-actor-epic, existing-features-epic, ordered-capabilities-epic) | ✅ |
| `wtf.feature-to-traces` | 3 checkpoint evals (migration-implied, cross-layer-feature, complex-edge-case) | ✅ |
| `wtf.reflect` | 5 checkpoint evals (arch-gotcha→TECH, flaky-test→QA, domain-drift→VISION, component-misuse→DESIGN, ambiguous→TECH-default) | ✅ |
| `wtf.hotfix` | 3 checkpoint evals (branch-naming, scope-gate, pr-body-completeness) | ✅ |

Add new skills to this table when evals are authored. See `docs/future-work/add-evals.md` for the candidate ranking.

## Hooks

`skills/wtf.setup/hooks/track-interventions.py` rides along inside the `wtf.setup` skill payload. The `wtf.setup` skill registers it into the user's `~/.claude/settings.json` or the repo's `.claude/settings.json` for `UserPromptSubmit` + `Stop` events. Counts user corrections and nudges toward `/wtf.reflect` when they accumulate. Do not bypass.

`skills/wtf.setup/hooks/gh-body.py` also rides along in the `wtf.setup` payload, but it is a **CLI utility, not a settings hook**. `wtf.setup` copies it into the consuming repo at `.wtf/gh-body.py`. Every skill that reads or writes a GitHub issue/PR body or comment goes through it (`read`/`create`/`edit`/`comment`/`review`/`release`) so multi-line UTF-8 content survives on Windows, where raw `gh` under PowerShell corrupts bodies via CP850 mojibake, newline collapse on variable capture, and inline-`--body` re-encoding. See `skills/references/gh-body-helper.md`. Do not bypass it for body operations. A self-contained regression test sits beside it — `python3 skills/wtf.setup/hooks/test_gh_body.py` (stub `gh`, no network, exits non-zero on regression).

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
