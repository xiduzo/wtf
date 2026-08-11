# The Trace Model — replace Tasks with Traces

**Status:** Decided, not yet implemented. Four core decisions were made on 2026-08-11. This document pins the model down so implementation can proceed in phases.

**Source inspiration:** [Tracer Bullets for AI-Assisted Development](https://www.aihero.dev/tracer-bullets), itself borrowed from *The Pragmatic Programmer*. A tracer bullet is a small end-to-end slice that touches all layers of the system at once. The alternative — build layers separately, integrate late — is how AI agents "outrun their headlights" and produce slop.

## Why change

The current Task layer *claims* to hold vertical slices. In practice it invites horizontal layering. The canonical Proposed Tasks example in `wtf.write-feature` decomposes **one** user story into four layer tasks: model field → API exposure → UI display → notification email. The layer demands 4–8 nodes per Feature. A story rarely contains 4–8 genuinely vertical slices. So decomposition pressure produces layer tasks, and layer tasks defer integration feedback — the exact failure mode the tracer-bullet approach exists to prevent.

Agents do not need layer decomposition. An agent drives one story end-to-end in one pass and verifies it against the story's Gherkin. The intermediate task spec is a lossy translation step with no consumer.

## The model

| Layer | Meaning | Cardinality |
|---|---|---|
| **Epic** | The dot on the horizon. A strategic outcome. | 1 → n Features |
| **Feature** | One step toward the Epic. Carries 1..n **co-related** user stories that share one end-to-end spine. | 1 → n Traces |
| **Trace** | The implementation unit. One user story, driven end-to-end through every layer in one pass, verified directly against that story's Gherkin. | 1 story → 1 Trace |

A Trace replaces the Task. There is no config to keep both models. Old Task issues in existing repos stay untouched and readable. New planning produces Traces.

**The spec collapse:** a Trace's spec is the story + its Acceptance Criteria + its Gherkin scenarios. `feature-to-tasks`'s derivation problem becomes a 1:1 mapping plus ordering. Nothing is invented between the story and the implementation.

### Spine-first sequencing (decided)

Traces within a Feature are **sequential by design**:

1. **Trace 1 — the walking skeleton.** The Feature's primary story, implemented minimally, but touching every layer end-to-end. It proves the spine: the data path, the seam, the integration points.
2. **Each subsequent Trace extends the spine.** The next story, or a deepening of an earlier one (edge cases, hardening). It builds on code the skeleton laid down.

Consequences:

- The conflict graph simplifies. Traces of one Feature share files by construction, so they serialize. **Features become the parallel unit** in `wtf.loop`. Cross-feature file conflicts still use `conflict-graph.md`.
- `wtf.loop`'s fresh-context-per-unit already matches the tracer-bullet workflow ("move forward in fresh context windows"). No change to that principle — the unit changes.
- A story too big for one agent pass is not split into layer tasks. It is split into a skeleton Trace plus deepening Traces. The escape valve is depth, not layers.

### Feature scope (decided)

`.wtf/config.json` gains `"feature_scope": "single-story" | "grouped"`, asked once in `wtf.setup`:

- **`single-story`** — every Feature carries exactly one user story. Feature ≈ story ≈ one Trace (plus deepening Traces when needed). This is the traditional mode. Teams that want one-feature-one-story set it once and never see grouping.
- **`grouped`** — a Feature carries multiple co-related stories sharing one spine. This is the agentic mode. Fewer Features, richer Trace sequences.

`wtf.write-feature`'s scope gate may override the default per Feature with a stated reason (for example: two stories are so entangled that splitting them breaks the spine). Overrides are the exception. The config is the rule.

This knob is **orthogonal to the planning mode** (`"planning": "guided" | "flow"` — see `skills/references/planning-mode.md`). One controls artifact granularity. The other controls interaction density. The agentic sweet spot is `flow` + `grouped`. The traditional corner is `guided` + `single-story`.

## Classification (decided: new Trace kind)

The WTF kinds become **Epic / Feature / Trace / Bug**. In `skills/references/issue-classification.md`:

| Kind | Type name | Label | Label color | Type color | Title prefix |
|---|---|---|---|---|---|
| Trace | `Trace` | `trace` | `e4e669` | `yellow` | 🧵 |

- `types` mode: `Trace` is **not** a GitHub org default type. Provision it exactly like `Epic` (the machinery exists in `wtf.setup` step 7 / issue-classification's provisioning block).
- `labels` mode: create the `trace` label alongside the others.
- **Legacy reads:** detection and list queries keep recognizing `Task`/`task` as a legacy kind so `wtf.health`, `wtf.refine`, and `wtf.retro` do not go blind in migrated repos. Write paths never create Tasks again.
- Lifecycle labels (`designed` / `implemented` / `verified`) are unchanged and apply to Traces.

All child-issue machinery survives because a Trace **is** an issue: sub-issue links to the Feature, dependency links, lifecycle labels, PR closure via `Closes #<n>`, loop dispatch, verification, health scanning.

## Artifact shapes

### Feature body (template change)

- **User stories: 1..n**, each with its ACs and Gherkin scenarios (the Gherkin moves UP from the task layer into the Feature — it belongs to the story, and the story lives here).
- **Trace Plan** replaces **Proposed Tasks**: an *ordered* checklist. Item 1 is marked as the walking skeleton. Each item names its story and what it adds to the spine.

```markdown
## Trace Plan

1. [ ] 🧵 Skeleton — Merchant sees settlement status for one completed payment (minimal: field → API → UI)
2. [ ] 🧵 Merchant filters settlements by date range
3. [ ] 🧵 Settlement-delayed notification (extends the status spine with the delay event)
```

### Trace body (new template, replaces TASK)

- The story (verbatim from the Feature — no re-derivation).
- The Gherkin scenarios for this Trace (from the Feature; a deepening Trace carries the edge-case scenarios it hardens).
- **Spine position:** skeleton | extension, and what spine it builds on (previous Trace numbers).
- Technical Approach — filled by `implement-trace` at implementation time, as today.
- Definition of Done — as today.

## Skill impact

Grep confirms 22 of 26 skills and 13 of 16 references mention tasks. The migration is phased (below). Renames keep the `wtf.` namespace and change the noun:

| Current | Becomes | Change size |
|---|---|---|
| `wtf.write-task` | `wtf.write-trace` | Rewrite: story is given, not asked; Gherkin copied from Feature; spine position added |
| `wtf.feature-to-tasks` | `wtf.feature-to-traces` | Shrinks: stories → Traces 1:1 + skeleton choice + spine ordering. Derivation logic mostly deleted |
| `wtf.implement-task` | `wtf.implement-trace` | Modest: same TDD loop; skeleton Traces get an explicit "minimal, every layer, no gold-plating" directive (the article's anti-slop prompt) |
| `wtf.verify-task` | `wtf.verify-trace` | Small: verifies story Gherkin directly; no task-level derivation to cross-check |
| `wtf.design-task` | `wtf.design-trace` | Small: rename + body-section updates |
| `wtf.write-feature` | (keeps name) | Template change: stories + Gherkin + Trace Plan; `feature_scope` resolve; scope-gate override rule |
| `wtf.epic-to-features` | (keeps name) | `feature_scope` shapes the proposed list (single-story → more, smaller Features); flow-mode subagents draft Trace Plans |
| `wtf.loop` | (keeps name) | Dispatch unit = Trace; Traces within a Feature run sequentially; Features parallelize; roll-up dep logic unchanged |
| `wtf.health`, `wtf.retro`, `wtf.changelog`, `wtf.refine`, `wtf.report-bug`, `wtf.hotfix`, `wtf.create-pr`, `wtf.pr-review`, `wtf.spike` | (keep names) | Vocabulary + query updates; legacy-Task reads kept |
| `wtf.setup` | (keeps name) | Provision `Trace` kind; ask `feature_scope`; write config; TRACE template install |

References needing real changes (not just vocabulary): `issue-classification.md` (kind table + legacy reads), `spec-hierarchy.md` (Trace → Feature → Epic traversal), `conflict-graph.md` (features-parallel / traces-sequential rule), `scope-gates.md` (trace bar: end-to-end story, skeleton-vs-deepening split instead of layer split), `branch-setup.md` + `commit-conventions.md` (branch/commit naming for traces), `issue-template-loading.md` (TRACE.md), `lifecycle-labels.md` (wording only).

## Migration & compatibility

- Existing repos: old Task issues remain valid children of their Features. Read paths treat `Task` as legacy-Trace. No relabeling migration is required or offered.
- `wtf.loop` on a mixed Feature (some Tasks, some Traces) treats both as child work items; only sequencing differs (legacy Tasks keep conflict-graph scheduling).
- Slash-command aliases: keep `wtf.write-task` etc. as thin deprecation pointers for one release, or drop immediately — open question 3.

## Phases

1. **Foundations:** `issue-classification.md` (Trace kind + legacy reads), `wtf.setup` (provision + `feature_scope` + TRACE template), new `TRACE.md` template, `spec-hierarchy.md`, `lifecycle-labels.md` wording.
2. **Authoring:** `wtf.write-feature` template + scope changes, `wtf.epic-to-features`, new `wtf.feature-to-traces`, new `wtf.write-trace`.
3. **Execution:** `wtf.implement-trace`, `wtf.verify-trace`, `wtf.design-trace`, `wtf.loop`, `conflict-graph.md`, `branch-setup.md`, `commit-conventions.md`.
4. **Periphery:** health, retro, changelog, refine, report-bug, hotfix, create-pr, pr-review, spike vocabulary; CLAUDE.md tables; eval fixtures rewritten for traces; `sync-shared-references.sh` regeneration.

Each phase is committable on its own. Until phase 2 lands, nothing user-visible changes.

## Open questions

1. **Gherkin placement in `grouped` features with many stories** — the Feature body grows large. Alternative: Gherkin lives only on the Trace, Feature keeps AC summaries. Decide during phase 2 drafting.
2. **Deepening Traces and story mapping** — a hardening Trace has no *new* story. Its body cites the story it deepens plus the edge-case scenarios it covers. Confirm this reads well in the TRACE template draft.
3. **Deprecation aliases** for renamed skills: keep one release or drop immediately?
4. **Prefix emoji** 🧵 for Trace — placeholder; confirm before phase 1.
