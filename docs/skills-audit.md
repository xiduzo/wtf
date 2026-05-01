# WTF Skill Suite Audit

01/05/2026

Scope: 25 skills under `skills/wtf.*/SKILL.md`. Source of truth confirmed at `skills/`. References at `skills/references/` (8 files). Audit conducted by reading each `SKILL.md` plus targeted greps. No skill files modified.

---

## 1. Skill -> References map

Imports detected via `grep '../references/'` and `grep 'docs/steering/'` against each SKILL.md. `*` denotes additional skill-local `references/` files (e.g. `wtf.design-task/references/component-spec-template.md`).

| Skill | references/ imports | Steering / other |
|---|---|---|
| wtf.changelog | commit-conventions, gh-setup, questioning-style | — |
| wtf.create-pr | commit-conventions, gh-setup, questioning-style | `.github/pull_request_template.md` |
| wtf.design-feature | gh-setup, questioning-style + local `component-spec-template.md` | `docs/steering/DESIGN.md` |
| wtf.design-task | gh-setup, questioning-style + local `component-spec-template.md` | `docs/steering/DESIGN.md` |
| wtf.epic-to-features | gh-setup, questioning-style | — |
| wtf.feature-to-tasks | gh-setup, questioning-style | — |
| wtf.health | gh-setup, questioning-style | — |
| wtf.hotfix | gh-setup, questioning-style, commit-conventions | `docs/steering/TECH.md` |
| wtf.implement-task | gh-setup, questioning-style, scope-gates, ddd-writing-rules, commit-conventions | `docs/steering/TECH.md`, `docs/steering/QA.md`, `@.github/ISSUE_TEMPLATE/TASK.md` |
| wtf.loop | gh-setup, questioning-style, conflict-graph, subagent-protocol, commit-conventions | `docs/steering/TECH.md` |
| wtf.pr-review | gh-setup, questioning-style, scope-gates, ddd-writing-rules, commit-conventions | `docs/steering/TECH.md` |
| wtf.refine | gh-setup, questioning-style, scope-gates, ddd-writing-rules, conflict-graph, subagent-protocol | — |
| wtf.reflect | questioning-style | `docs/steering/LEARNINGS.md` (mentioned), TECH/QA/DESIGN/VISION |
| wtf.report-bug | gh-setup, questioning-style | `@.github/ISSUE_TEMPLATE/BUG.md` |
| wtf.retro | gh-setup, questioning-style | — |
| wtf.setup | questioning-style + local `references/{BUG,EPIC,FEATURE,TASK,pull_request_template}.md` | — |
| wtf.spike | gh-setup, questioning-style | `docs/steering/TECH.md` |
| wtf.steer-design | questioning-style, steering-doc-process | `docs/steering/{DESIGN,VISION}.md` |
| wtf.steer-qa | questioning-style, steering-doc-process | `docs/steering/{QA,TECH}.md` |
| wtf.steer-tech | questioning-style, steering-doc-process | `docs/steering/TECH.md` |
| wtf.steer-vision | questioning-style, steering-doc-process | `docs/steering/VISION.md` |
| wtf.verify-task | gh-setup, questioning-style, conflict-graph, subagent-protocol | `docs/steering/QA.md` |
| wtf.write-epic | gh-setup, questioning-style, scope-gates, ddd-writing-rules | `@.github/ISSUE_TEMPLATE/EPIC.md` |
| wtf.write-feature | gh-setup, questioning-style, scope-gates, ddd-writing-rules | `@.github/ISSUE_TEMPLATE/FEATURE.md` |
| wtf.write-task | gh-setup, questioning-style, scope-gates, ddd-writing-rules | `@.github/ISSUE_TEMPLATE/TASK.md` |

**Skills referencing zero shared refs:** none. Floor is 1 (every skill at least imports `questioning-style.md`).

**Reference reuse counts:**
- `questioning-style.md` — 25/25 (universal)
- `gh-setup.md` — 21/25 (skipped only by reflect, setup, steer-*)
- `commit-conventions.md` — 5 (changelog, create-pr, hotfix, implement-task, loop, pr-review)
- `scope-gates.md` — 5 (write-epic, write-feature, write-task, refine, implement-task, pr-review)
- `ddd-writing-rules.md` — 5 (write-epic, write-feature, write-task, refine, pr-review, implement-task)
- `subagent-protocol.md` — 3 (loop, refine, verify-task)
- `conflict-graph.md` — 3 (loop, refine, verify-task)
- `steering-doc-process.md` — 4 (steer-* only)

---

## 2. Commonality candidates

### 2.1 `gh issue create` body-from-template + pre-flight template-exists check (NEW REF)

Pattern repeats in `wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`, `wtf.report-bug`. Each:
1. Verifies `.github/ISSUE_TEMPLATE/<X>.md` exists (`wtf.report-bug:101`, `wtf.write-epic:88`, `wtf.write-task` similar).
2. If missing, applies `questioning-style.md` to ask whether to run `/wtf.setup` and halts.
3. Reads template via Read tool.
4. Substitutes section content.
5. Calls `gh issue create --title ... --body-file -`.

Sample (`wtf.write-epic` SKILL.md:88-91):

> Before drafting, verify `.github/ISSUE_TEMPLATE/EPIC.md` exists. If missing, ask the user (per `../references/questioning-style.md`) whether to run `/wtf.setup` or cancel — then halt either way.

`wtf.create-pr` does the equivalent for `pull_request_template.md` (line 102). Same idiom, four-five copies.

**Recommendation:** create `references/issue-template-loading.md` (a) verify template, (b) halt-or-setup ask, (c) Read pattern, (d) `gh issue create --body-file` invocation. Saves ~10 lines per write-* skill. (c) **create new reference**.

### 2.2 Lifecycle label gates (NEW REF)

`wtf.create-pr:64`, `wtf.design-feature:40-46`, `wtf.design-task` (similar), `wtf.implement-task:35-49` all encode the same shape:

> If `<label>` is **absent**, warn the user that the task hasn't been <X> yet and that the recommended flow is: **write-task -> design-task -> implement-task -> verify-task -> create-pr**. Then ask ... — header `<header>`: ... [Continue / Run skill X / Cancel]

Same four labels (`designed`, `implemented`, `verified`, `merged`), same recommended flow string, same three-option ask, repeated 4x. ~15 lines duplicated per skill.

**Recommendation:** create `references/lifecycle-labels.md` describing label semantics + the canonical "absent / present / overwrite" gate template. Each skill cites with the specific `<label>` to check. **(b) create new reference.**

### 2.3 "Load the X steering document" boilerplate (NEW REF or extend steering-doc-process)

Identical step appears in `wtf.design-feature:53`, `wtf.design-task:47`, `wtf.hotfix:54`, `wtf.implement-task:51`, `wtf.pr-review:52`, `wtf.verify-task:71`, `wtf.spike` (TECH).

Verbatim text in `wtf.hotfix` and `wtf.pr-review` (and very near-identical in `wtf.implement-task`):

> Use the Read tool to attempt reading `docs/steering/TECH.md`. If it exists, apply its stack constraints, coding patterns, and test commands silently throughout this session.

Six skills repeat the same sentence with only the doc name swapped. ~3 lines each, but cross-skill normalization matters more than line count.

**Recommendation:** add a "How consumer skills load steering docs" section to existing `steering-doc-process.md` with a one-line template per doc (TECH/QA/DESIGN/VISION). Skills then say: "Load `docs/steering/TECH.md` per `../references/steering-doc-process.md#consumer-load`." **(a) extend existing reference.**

### 2.4 Native sub-issue / dependency CLI patterns (EXTEND gh-setup)

`gh sub-issue list/add` and `gh issue-dependency add` show up in 7 skills:
- `wtf.epic-to-features:33,42`
- `wtf.feature-to-tasks:26,35,88`
- `wtf.loop:61`
- `wtf.write-task:30,205,212,222`
- `wtf.write-feature` (similar)
- `wtf.changelog:27`
- `wtf.verify-task` (sub-issue list to gather siblings)

Each describes the same call shape. The fact that the extension is optional is documented in `gh-setup.md`, but the actual *call patterns* (e.g. `gh sub-issue list <feature_number> --relation parent`) are repeated. ~3-5 lines per skill.

**Recommendation:** add a "Sub-issue and dependency call cookbook" appendix to `gh-setup.md` with the four canonical commands. Skills cite by name. **(a) extend existing reference.**

### 2.5 "Find parent Epic / Feature" traversal (EXTEND gh-setup or NEW REF)

`wtf.write-task:30`, `wtf.write-feature` (~9 mentions), `wtf.feature-to-tasks:26` (find parent Epic), `wtf.implement-task` (fetch spec hierarchy), `wtf.pr-review:34-52` (Fetch the spec hierarchy), `wtf.design-feature:22-27` (Fetch the Feature and parent Epic), `wtf.design-task:24-30`, `wtf.create-pr:74` ("Fetch the spec hierarchy"), `wtf.changelog:27`.

All do the same dance: extract issue number, walk up via `gh sub-issue list --relation parent` or scrape the issue body's "Context" section for the parent ref, then `gh issue view` each ancestor.

**Recommendation:** add `references/spec-hierarchy.md` (or section in gh-setup) defining the canonical traversal: Task -> Feature -> Epic, with the exact `gh` calls and the body-scraping fallback when extension is absent. **(b) create new reference** — it's distinct enough from gh-setup.

### 2.6 "Update the issue" lifecycle-label section (small, candidate for inline)

`wtf.design-feature:192,200-205`, `wtf.design-task:131`, `wtf.implement-task:203-208`, `wtf.verify-task` analog, `wtf.create-pr:149-156` ("Update the Task issue (if linked)").

Each appends a comment + adds a label. Similar to 2.2 but the *write* side rather than the gate side.

**Recommendation:** if 2.2 ships, fold this in there as a "Mark transition" subsection. Otherwise leave inline — the body comments differ enough. **(c) leave inline if 2.2 not done.**

### 2.7 Branch setup / worktree pattern (NEW REF)

`wtf.implement-task:65-103` and `wtf.hotfix:58-69` both describe how to start work: branch naming, worktree consideration, `git checkout`. Loop also references this pattern at `wtf.loop:240+` for parallel tasks. Three skills, ~30+ lines of repeated guidance.

**Recommendation:** create `references/branch-setup.md` covering naming convention (already alluded to in commit-conventions but not codified for branches), worktree decision tree, base-branch policy (main vs hotfix). **(b) create new reference.**

### 2.8 Trigger-phrase frontmatter (skill-specific — leave inline)

Frontmatter `description:` ranges 71-115 words across the 25 skills, each with 4-12 quoted trigger phrases. There is no shared "phrase library" but cross-skill *wording* is consistent (e.g., "for example ..."). This is fine — descriptions are intentionally skill-specific for trigger discrimination. **(c) leave inline.**

### 2.9 DDD ubiquitous-language enforcement (already covered)

`ddd-writing-rules.md` is referenced by write-epic, write-feature, write-task, refine, implement-task, pr-review. No detected duplication of the rules in skills themselves — they cite. `wtf.refine:142` is exemplary. **No action.**

### 2.10 Subagent delegation (already covered, mostly)

`subagent-protocol.md` is referenced by loop, refine, verify-task. `wtf.create-pr:100` spawns a subagent for PR title generation but does *not* cite the protocol. Inconsistent. ~1 line drift.

**Recommendation:** add a one-line citation in `wtf.create-pr` to bring it under protocol — small fix, not a new reference. **(c) inline fix.**

### 2.11 Conflict-graph for parallel work (already covered)

`conflict-graph.md` is referenced by loop, refine, verify-task. The algorithm description is not duplicated in skills. **No action.**

### 2.12 Scope-gates DoR/DoD (already covered, asymmetric usage)

`scope-gates.md` is referenced by write-epic, write-feature, write-task, refine, implement-task, pr-review. But health, retro, and verify-task each touch DoD-shaped concerns (`Definition of Done`, "ready to merge" gates) — `wtf.verify-task:3,58-60` mentions "sign off" without citing scope-gates. Possible reuse opportunity but the verify-task gate is task-level not the DoR/DoD scope gate; likely **(c) leave inline.**

### 2.13 Questioning-style usage (universal — confirm consistency)

All 25 skills cite `questioning-style.md`. Inline phrasing of the actual ask varies: some pre-format "header / question / options" structure (`wtf.design-feature:20`, `wtf.write-task:30`), others paraphrase. The reference itself defines the structure, so citation alone is sufficient. **No action.**

---

## 3. Strength audit per skill

Scores 1-5 (5 best). Order matches the skill table.

### wtf.changelog (800w / 112L)
T:4 P:5 R:4. Strong: lean, references commit-conventions for tag/release syntax. Lacking: no native `gh release create` cookbook citation.

### wtf.create-pr (1164w / 170L)
T:4 P:4 R:4. Strong: explicit lifecycle gate, subagent for title gen. Lacking: subagent call (line 100) does not cite `subagent-protocol.md`.

### wtf.design-feature (1715w / 224L)
T:4 P:3 R:4. Strong: clear Path A/B/C structure, design handoff template inline. Lacking: long (~1.7k words) — Design Handoff section could move to local `references/design-handoff-template.md`.

### wtf.design-task (1286w / 157L)
T:4 P:4 R:4. Strong: tight Gherkin-state mapping at line 67-76. Lacking: lifecycle gate near-duplicates wtf.implement-task — candidate for ref 2.2.

### wtf.epic-to-features (814w / 93L)
T:3 P:5 R:4. Strong: very lean, walks one-by-one. Lacking: trigger description has only 4 example phrases (lowest). Could surface "decompose epic" / "all features".

### wtf.feature-to-tasks (837w / 91L)
T:4 P:5 R:4. Strong: shortest of the breakdown skills, handles partial-state resumption. Lacking: parent-traversal block at lines 26-35 = candidate for ref 2.5.

### wtf.health (748w / 132L)
T:5 P:5 R:3. Strong: example output at lines 88-119 is concrete. Lacking: no scope-gates reuse despite reporting on stale-implemented (DoD-related).

### wtf.hotfix (956w / 166L)
T:4 P:4 R:4. Strong: explicit "When to use vs. when not" section. Lacking: branch setup (lines 58-69) duplicates wtf.implement-task — candidate for ref 2.7.

### wtf.implement-task (1570w / 221L)
T:5 P:3 R:5. Strong: rich reference reuse (5 refs), TDD cycle structure. Lacking: branch section + lifecycle gate are duplicated patterns; "fetch spec hierarchy" duplicates create-pr.

### wtf.loop (3104w / 416L) **largest**
T:3 P:2 R:5. Strong: most refs cited, explicit human-in-the-loop gate reference. Lacking: bloat — 3.1k words, 416 lines. Steps 2 (pre-flight) and 4 (execute) could split into local sub-references. Trigger description only 71 words and depends on hard-to-discover phrases ("go", "kick it off") — risky.

### wtf.pr-review (1063w / 168L)
T:4 P:4 R:5. Strong: 5 refs, scope-gates + DDD. Lacking: "Run the review checklist" at lines 68-114 is long and partially duplicates implement-task verification logic.

### wtf.refine (1822w / 268L)
T:4 P:3 R:5. Strong: most diverse reference reuse (6); detect-then-rewrite pattern is well-structured. Lacking: ~270 lines is heavy; cascade logic (line 265) is dense.

### wtf.reflect (950w / 124L)
T:5 P:4 R:2. Strong: rich trigger phrases (12), routing model is clear. Lacking: only 1 reference (questioning-style); steering-doc-process is *not* cited despite being the primary write surface (TECH/QA/DESIGN/VISION).

### wtf.report-bug (1467w / 185L)
T:4 P:3 R:3. Strong: fast-path mode for hotfix integration. Lacking: lifecycle-gate-shaped logic, BUG template loading duplicates write-* template loading — candidate for ref 2.1.

### wtf.retro (1230w / 207L)
T:4 P:4 R:3. Strong: planned-vs-shipped structure. Lacking: only 2 refs; could pull steering-doc-process for the "deltas to TECH/QA" routing.

### wtf.setup (1574w / 258L)
T:5 P:3 R:2. Strong: sole installer; bundles its own `references/{BUG,EPIC,FEATURE,TASK}.md` templates. Lacking: only references questioning-style; many sections are install-specific so refs are limited.

### wtf.spike (861w / 150L)
T:3 P:5 R:3. Strong: time-box concept, output-as-input handoff. Lacking: 14 questioning-style mentions (highest) but only 2 refs; produces `docs/spikes/` artifacts — no local reference template captured.

### wtf.steer-design (527w / 53L) **smallest**
T:4 P:5 R:5. Strong: ultra-lean, hands off to steering-doc-process. Lacking: heavily reliant on the shared process — risk if steering-doc-process drifts.

### wtf.steer-qa (549w / 56L)
T:4 P:5 R:5. Same shape as steer-design. Lacking: same shared-process dependency risk.

### wtf.steer-tech (468w / 51L)
T:4 P:5 R:5. Same shape. Lacking: same.

### wtf.steer-vision (538w / 58L)
T:4 P:5 R:5. Same shape. Lacking: same.

### wtf.verify-task (1915w / 222L)
T:5 P:3 R:5. Strong: orchestrator mode + sub-agent fan-out + report-bug fallback. Lacking: 1.9k words; gate handling for "all scenarios pass" duplicates lifecycle-gate pattern.

### wtf.write-epic (1523w / 167L)
T:4 P:4 R:5. Strong: scope-gates Stage 1+2 split, DDD enforcement. Lacking: write-epic / write-feature / write-task share ~30% boilerplate (template load + DoR + draft + DoD + create + post-create).

### wtf.write-feature (2144w / 229L)
T:4 P:3 R:5. Strong: clean parent-Epic context loading. Lacking: largest of the write-* trio; could share more with write-task. 7 questioning-style cites (joint highest with write-task).

### wtf.write-task (2230w / 239L)
T:4 P:3 R:5. Strong: most parent-traversal logic (13 mentions), explicit blocked-by handling. Lacking: same as write-feature — boilerplate triplication.

---

## 4. Cross-cutting findings

### Strengths (top 5)

1. **Universal `questioning-style` adoption (25/25).** Single source of truth for user prompts is enforced everywhere — recently standardized per recent commits (`f00441b Standardize questioning guidance`).
2. **Reference architecture is real.** 8 shared refs, average 2.6 imports per skill, no skill duplicates the content of an existing ref. The framework is being used.
3. **Lifecycle is explicit.** Labels (`designed`, `implemented`, `verified`) appear consistently as gates *and* as transitions, giving the suite a coherent state machine.
4. **Steer/* skills are exemplary lean.** 51-58 lines each — model for what a focused skill should look like.
5. **Trigger descriptions are concrete.** Median ~95 words, 4-12 example phrases each — discriminative enough that the policy "never auto-invoke" is enforceable.

### Gaps (top 5)

1. **Issue-template-loading duplication.** Same 6-line check repeats across 4-5 skills (write-epic, write-feature, write-task, report-bug, create-pr).
2. **Lifecycle gate template drift risk.** Each skill recodes the absent/present/overwrite ask; flow string ("write-task -> design-task -> ...") is hardcoded per-skill.
3. **Spec-hierarchy traversal is uncited.** 7+ skills walk Task -> Feature -> Epic with similar but slightly different `gh` invocations. Easy to drift.
4. **wtf.loop and wtf.refine are heavy.** 3104 / 1822 words. Consumer-load steps (steering doc, ref imports) are inline rather than cited.
5. **Subagent protocol coverage is incomplete.** wtf.create-pr spawns a subagent at line 100 without citing `subagent-protocol.md`.

---

## 5. Recommended actions (prioritized)

1. **Create `references/issue-template-loading.md`** capturing the verify-template / halt-or-setup / Read / `gh issue create --body-file` recipe. Cite from `wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`, `wtf.report-bug`, `wtf.create-pr` (PR template variant). High impact, low effort. (Candidate 2.1.)
2. **Create `references/lifecycle-labels.md`** with label semantics and the canonical absent/present/overwrite gate template. Cite from `wtf.create-pr:56-72`, `wtf.design-feature:38-52`, `wtf.design-task:32-46`, `wtf.implement-task:33-49`. (Candidate 2.2.)
3. **Extend `references/steering-doc-process.md`** with a "Consumer-side load" section. Replace the boilerplate "Use Read tool ... apply silently" sentence in 6 skills with a one-line cite. (Candidate 2.3.)
4. **Create `references/spec-hierarchy.md`** with Task -> Feature -> Epic traversal, both extension-present and body-scraping fallbacks. Cite from at least 7 skills (write-task, write-feature, feature-to-tasks, implement-task, pr-review, design-task, design-feature, create-pr, changelog). (Candidate 2.5.)
5. **Extend `references/gh-setup.md`** with a "Sub-issue and dependency cookbook" appendix. Targets `wtf.epic-to-features`, `wtf.feature-to-tasks`, `wtf.write-task`, `wtf.write-feature`, `wtf.loop`, `wtf.changelog`, `wtf.verify-task`. (Candidate 2.4.)
6. **Create `references/branch-setup.md`** covering naming, worktree decision, base-branch policy. Cite from `wtf.implement-task`, `wtf.hotfix`, `wtf.loop`. (Candidate 2.7.)
7. **Slim `wtf.loop`** by extracting Step 2 (pre-flight validation) and Step 4 (execute each task) into local `skills/wtf.loop/references/` files; keep SKILL.md as a contents map. Reduces 3104w skill to ~1500w shell.
8. **Add `subagent-protocol.md` cite to `wtf.create-pr:100`** where it spawns a haiku subagent for title generation. One-line fix; closes drift gap.
9. **Add `steering-doc-process.md` cite to `wtf.reflect`.** It is the primary writer of TECH/QA/DESIGN/VISION but does not invoke the shared process doc — 1-2 line fix.
10. **Move `wtf.design-feature` Design Handoff template (lines 148-180)** into a local `skills/wtf.design-feature/references/design-handoff-template.md`. Drops SKILL.md from 1715w to ~1100w. Mirrors how `wtf.design-task` already uses `component-spec-template.md`.
