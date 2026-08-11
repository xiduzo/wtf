# The Trace Model — replace Tasks with Traces

**Status:** Decided 2026-08-11, refined the same day in a grilling session. All four earlier open questions are resolved (see the end of this document). Terminology is pinned in [CONTEXT.md](../../CONTEXT.md) — use its terms exactly. The replacement decision is recorded in [ADR 0001](../adr/0001-traces-replace-tasks.md). This document is the implementation plan.

**Source inspiration:** [Tracer Bullets for AI-Assisted Development](https://www.aihero.dev/tracer-bullets), itself borrowed from *The Pragmatic Programmer*. A tracer bullet is a small end-to-end slice that touches all layers of the system at once. Three readings anchor the model: every iteration is a tracer bullet, the increment grain is a use case (a scenario) rather than a story, and bullets exist so you can adjust aim.

## Why change

The current Task layer *claims* to hold vertical slices. In practice it invites horizontal layering. The canonical Proposed Tasks example in `wtf.write-feature` decomposes **one** user story into four layer tasks: model field → API exposure → UI display → notification email. The layer demands 4–8 nodes per Feature. A story rarely contains 4–8 genuinely vertical slices. So decomposition pressure produces layer tasks, and layer tasks defer integration feedback — the exact failure mode the tracer-bullet approach exists to prevent.

Agents do not need layer decomposition. An agent drives one story end-to-end in one pass and verifies it against the story's Gherkin. The intermediate task spec is a lossy translation step with no consumer.

## The model

| Layer | Meaning | Cardinality |
|---|---|---|
| **Epic** | The dot on the horizon. A strategic outcome. | 1 → n Features |
| **Feature** | One step toward the Epic. Carries 1..n **co-related** user stories that share one Spine. | 1 → n stories |
| **User story** | One actor's need — actor, domain verb, business outcome — with its Acceptance Criteria and Gherkin scenarios. | 1 → n Traces |
| **Trace** | The implementation unit. One pass over the Feature's Spine, driven through every layer. | exactly 1 story + one Scenario Claim |

A Trace replaces the Task. There is no config to keep both models. Old Task issues in existing repos stay untouched and readable. New planning produces Traces.

**The spec collapse:** a Trace's spec is its story plus its Scenario Claim. `feature-to-traces` maps stories to Traces and orders them. Nothing is invented between the story and the implementation.

### Scenario Claims and partitioning

A Trace claims exactly one story. It also declares a **Scenario Claim**: the subset of that story's Gherkin scenarios it implements. A story is delivered by 1..n Traces. Their Scenario Claims partition the story's scenarios — full cover, no overlap.

The **Skeleton** is simply the first Trace. It claims the primary story's happy-path scenario, minimally, through every layer. A **Deepening Trace** claims further scenarios — edge cases, failure modes — of a story already started. It always cites its story. It is never storyless.

A small story gets one Trace that claims all its scenarios. Then story = Trace = PR, and the traditional case falls out of the model naturally.

Verification is mechanical. `verify-trace` runs exactly the claimed scenarios. A story is done when its partition is exhausted. A Feature is done when all its stories are done.

### The releasability invariant

Every Trace leaves the system releasable. Each Trace lands at production quality: lean but complete, with error handling and tests. Each Trace is verified against its Scenario Claim before it merges. The invariant holds on whichever branch the Trace lands. A Skeleton is never a prototype.

### Spine-first sequencing

Traces within a Feature are **sequential by design**. The Skeleton is the first bullet, not a special kind of work. It proves the Spine: the data path, the seam, the integration points. Each later Trace extends the Spine — the next story, or a Deepening Trace on an earlier one.

Consequences:

- The conflict graph simplifies. Traces of one Feature share files by construction, so they serialize. **Features become the parallel unit** in `wtf.loop`. Cross-feature file conflicts still use `conflict-graph.md`.
- `wtf.loop`'s fresh-context-per-unit already matches the tracer-bullet workflow ("move forward in fresh context windows"). The principle stays. The unit changes.
- A story too big for one agent pass is not split into layer tasks. It is split into a Skeleton plus Deepening Traces. The escape valve is depth, not layers.

### Re-aim

The Trace Plan is a living aim, not a contract. "The power of tracer bullets is not that they hit the target on the first try, it is that they show you what you are hitting." After a Trace lands, the plan absorbs what the Trace revealed.

`wtf.refine` is the **single Re-aim mechanism**. It has two entry points:

1. **Interactive.** A human runs `/wtf.refine` on the Feature. The insight is what the last Trace revealed.
2. **Headless.** `wtf.loop` invokes refine via subagent after each verified Trace. Interactive gates are stripped per `subagent-protocol.md`. The audit-trail comment is always posted.

Refine therefore gains:

- A headless invocation mode.
- Trace vocabulary in its change-map and cascade tables: Trace Plan rows for Features, Scenario Claim rows for Traces.
- A new change type: **"Trace landed — re-aim"**.
- Stale-label auto-resolution by rule in headless mode.

**Grow-only autonomy.** Headless Re-aim may reorder the remaining Traces, re-batch them, and move scenarios between Traces. It may add newly discovered scenarios. It may never drop a scenario or a story on its own. It may only **suggest** a shrinkage, surfaced as a loop gate (`NEEDS_INPUT`). A human approves every drop. Scenarios are the delivery contract. Traces are the delivery schedule.

### Scenario ownership and ephemeral projection

The Feature issue body is **canonical** for all scenarios, grouped per story. It is the product surface: PMs and designers read it **and** edit it. Scenarios never move to committed spec files.

A Trace body carries the claimed scenario **names**, plus a synced courtesy copy of the claimed scenarios in a collapsed `<details>` block marked "Synced from Feature #N — edit there, not here". Refine's cascade keeps the copies fresh and strips stale lifecycle labels.

Executability comes from **ephemeral projection**. At run time, `verify-trace` scrapes the claimed scenarios from the Feature body and generates a temporary `.feature` file. When a Gherkin runner exists, it executes that file. When none exists, it falls back to interpretive verification. No committed `.feature` files. No permalink machinery.

### Feature scope

`.wtf/config.json` gains `"feature_scope": "single-story" | "grouped"`, asked once in `wtf.setup`:

- **`single-story`** — every Feature carries exactly one user story. Feature ≈ story ≈ one Trace (plus Deepening Traces when needed). This is the traditional mode. Teams that want one-feature-one-story set it once and never see grouping.
- **`grouped`** — a Feature carries multiple co-related stories sharing one Spine. This is the agentic mode. Fewer Features, richer Trace sequences.

`wtf.write-feature`'s scope gate may override the default per Feature with a stated reason (for example: two stories are so entangled that splitting them breaks the Spine). Overrides are the exception. The config is the rule.

This knob is **orthogonal to the planning mode** (`"planning": "guided" | "flow"` — see `skills/references/planning-mode.md`). One controls artifact granularity. The other controls interaction density. The agentic sweet spot is `flow` + `grouped`. The traditional corner is `guided` + `single-story`.

### Delivery config

`.wtf/config.json` gains `"delivery": "staged" | "trunk"`, asked in `wtf.setup`:

- **`staged`** (default — safe everywhere). Each `trace/<n>-<slug>` branch starts from the feature branch. Trace PRs merge into the feature branch sequentially: each Trace branches after the previous one merged. When the Trace Plan is exhausted, the feature PR merges into `main`.
- **`trunk`**. Trace PRs merge into `main` directly. Setup warns that this mode presumes feature-flag or dark-launch discipline. The Feature issue closes when its Trace Plan is exhausted, not via a feature-PR merge.

A human may override the mode per Feature with a stated reason. The override is recorded in the Feature body, so `wtf.loop` and `wtf.create-pr` read it from the spec. `branch-setup.md`'s base-branch table becomes mode-aware, and `task/*` renames to `trace/*`.

## Classification (decided: new Trace kind)

The WTF kinds become **Epic / Feature / Trace / Bug**. The title-prefix roster becomes 🎯 Epic, 🚀 Feature, ☄️ Trace, 🐞 Bug. 🛠 retires with Task and is never reused. In `skills/references/issue-classification.md`:

| Kind | Type name | Label | Label color | Type color | Title prefix |
|---|---|---|---|---|---|
| Trace | `Trace` | `trace` | `e4e669` | `yellow` | ☄️ |

- `types` mode: `Trace` is **not** a GitHub org default type. Provision it exactly like `Epic` (the machinery exists in `wtf.setup` step 7 / issue-classification's provisioning block).
- `labels` mode: create the `trace` label alongside the others.
- **Legacy reads:** detection and list queries keep recognizing `Task`/`task` as a legacy kind so `wtf.health`, `wtf.refine`, and `wtf.retro` do not go blind in migrated repos. Write paths never create Tasks again.
- Lifecycle labels (`designed` / `implemented` / `verified`) are unchanged and apply to Traces.

All child-issue machinery survives because a Trace **is** an issue: sub-issue links to the Feature, dependency links, lifecycle labels, PR closure via `Closes #<n>`, loop dispatch, verification, health scanning.

## Artifact shapes

### Feature body (template change)

- **User stories: 1..n**, each with its ACs and its **canonical** Gherkin scenarios (the Gherkin moves UP from the task layer into the Feature — it belongs to the story, and the story lives here).
- **Trace Plan** replaces **Proposed Tasks**: an *ordered* checklist. Item 1 is the Skeleton. Each item names its story, its Scenario Claim, and what it adds to the Spine.
- Optional **delivery override** (staged/trunk) with the stated reason, when a human set one.

```markdown
## Trace Plan

1. [ ] ☄️ Skeleton — Merchant sees settlement status for one completed payment (claims: "Status shown for a settled payment")
2. [ ] ☄️ Deepening — settlement status failure modes (claims: "Status for a failed settlement", "Status while settlement is pending")
3. [ ] ☄️ Merchant filters settlements by date range (claims: all scenarios)
```

### Trace body (new template, replaces TASK)

- The story (verbatim from the Feature — no re-derivation).
- The **Scenario Claim**: the claimed scenario names.
- A synced copy of the claimed scenarios in a collapsed `<details>` block, marked "Synced from Feature #N — edit there, not here".
- **Spine position:** Skeleton | extension | deepening, and which Traces it builds on.
- Technical Approach — filled by `implement-trace` at implementation time, as today.
- Definition of Done — as today.

## Skill impact

Grep confirms 22 of 26 skills and 13 of 16 references mention tasks. The migration is phased (below). Renames keep the `wtf.` namespace and change the noun:

| Current | Becomes | Change size |
|---|---|---|
| `wtf.write-task` | `wtf.write-trace` | Rewrite: story is given, not asked. Scenario Claim declared. Spine position added |
| `wtf.feature-to-tasks` | `wtf.feature-to-traces` | Shrinks: stories → Trace Plan with Scenario Claims, Skeleton choice, Spine ordering. Derivation logic mostly deleted |
| `wtf.implement-task` | `wtf.implement-trace` | Modest: same TDD loop. Skeleton Traces get an explicit "minimal, every layer, no gold-plating" directive (the article's anti-slop prompt) |
| `wtf.verify-task` | `wtf.verify-trace` | Medium: runs exactly the Scenario Claim. Ephemeral `.feature` projection from the Feature body, executed when a Gherkin runner exists, interpretive fallback otherwise |
| `wtf.design-task` | `wtf.design-trace` | Small: rename + body-section updates |
| `wtf.write-feature` | (keeps name) | Template change: stories with canonical Gherkin + Trace Plan. `feature_scope` resolve. Scope-gate and delivery override rules |
| `wtf.epic-to-features` | (keeps name) | `feature_scope` shapes the proposed list (single-story → more, smaller Features). Flow-mode subagents draft Trace Plans |
| `wtf.refine` | (keeps name) | Medium: headless invocation mode. Trace Plan rows (Features) and Scenario Claim rows (Traces) in change-map and cascade tables. New change type "Trace landed — re-aim". Stale-label auto-resolution by rule in headless mode |
| `wtf.loop` | (keeps name) | Dispatch unit = Trace. Traces within a Feature run sequentially, Features parallelize. Invokes headless refine after each verified Trace. Delivery-mode-aware merge targets. Roll-up dep logic unchanged |
| `wtf.create-pr` | (keeps name) | Delivery-mode-aware base selection: feature branch in `staged`, `main` in `trunk` |
| `wtf.setup` | (keeps name) | Provision `Trace` kind (☄️). Ask `feature_scope` + `delivery`. Write config. TRACE template install. Trunk-mode warning |
| `wtf.health`, `wtf.retro`, `wtf.changelog`, `wtf.report-bug`, `wtf.hotfix`, `wtf.pr-review`, `wtf.spike` | (keep names) | Vocabulary + query updates. Legacy-Task reads kept |

References needing real changes (not just vocabulary): `issue-classification.md` (kind table + ☄️ + legacy reads), `spec-hierarchy.md` (Trace → Feature → Epic traversal), `conflict-graph.md` (features-parallel / traces-sequential rule), `scope-gates.md` (the trace bar is its Scenario Claim, and the split rule is depth, not layers), `branch-setup.md` (mode-aware base-branch table, `task/*` → `trace/*`), `commit-conventions.md` (trace naming), `issue-template-loading.md` (TRACE.md), `lifecycle-labels.md` (wording only).

## Migration & compatibility

- Existing repos: old Task issues remain valid children of their Features. Read paths treat `Task` as legacy-Trace. No relabeling migration is required or offered.
- `wtf.loop` on a mixed Feature (some Tasks, some Traces) treats both as child work items. Only sequencing differs — legacy Tasks keep conflict-graph scheduling.
- **No deprecation aliases.** The five renamed skills drop the old names immediately. Non-updated installs keep working through the legacy Task path. Alias stubs would create skill-triggering ambiguity for the model. A changelog entry plus a migration rename table replaces them.

## Phases

1. **Foundations:** `issue-classification.md` (Trace kind + ☄️ + legacy reads), `wtf.setup` (provision + `feature_scope` + `delivery` config keys + TRACE template), new `TRACE.md` template, `spec-hierarchy.md`, `lifecycle-labels.md` wording.
2. **Authoring:** `wtf.write-feature` template + scope + delivery-override changes, `wtf.epic-to-features`, new `wtf.feature-to-traces`, new `wtf.write-trace`.
3. **Execution:** `wtf.implement-trace`, `wtf.verify-trace` (ephemeral projection + runner fallback), `wtf.design-trace`, `wtf.refine` headless mode, `wtf.loop` re-aim integration + delivery-mode merge targets, `wtf.create-pr` base selection, `conflict-graph.md`, `branch-setup.md`, `commit-conventions.md`.
4. **Periphery:** health, retro, changelog, report-bug, hotfix, pr-review, spike vocabulary; CLAUDE.md tables; eval fixtures rewritten for traces; `sync-shared-references.sh` regeneration; the migration rename table + changelog entry.

Each phase is committable on its own. Until phase 2 lands, nothing user-visible changes.

## Resolved questions

The four open questions from the first draft are closed:

1. **Gherkin placement in `grouped` features** — the Feature body is canonical for all scenarios. Trace bodies carry claim names plus a synced `<details>` copy. `verify-trace` projects an ephemeral `.feature` file at run time.
2. **Deepening Traces and story mapping** — a Deepening Trace always claims a story plus further scenarios of it. It is never storyless.
3. **Deprecation aliases** — drop the old names immediately. Legacy installs keep working, and alias stubs would blur skill triggering. A changelog rename table replaces them.
4. **Prefix emoji** — ☄️ for Trace. 🛠 retires with Task and is never reused.

## Open questions

1. **Gherkin runner detection** — how `verify-trace` detects a runner (playwright-bdd, cucumber-js, behave, …) and the exact shape of the interpretive fallback report. Decide during phase 3 drafting.
2. **Primary-story selection for the Skeleton** — in `grouped` mode, the rule by which `feature-to-traces` picks the primary story (proposal + confirmation, or a deterministic heuristic). Decide during phase 2 drafting.
3. **Headless stale-label rules** — the exact rule table for stale-label auto-resolution in headless refine. Decide during phase 3 drafting.
