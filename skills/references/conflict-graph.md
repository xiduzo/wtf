# File-Conflict Graph Coloring

Partition a set of parallelizable work units into sub-phases. No two units in the same sub-phase touch overlapping files. Use this before spawning parallel sub-agents with worktree isolation.

## What the graph arbitrates

The graph arbitrates file conflicts at two levels.

**Across Features.** A Feature node carries its whole Trace set. Two Features run in parallel only when no Trace of one can touch a file of the other.

**Within one Feature, after the Skeleton lands.** The Skeleton is never in the graph: it lays the Spine, every later Trace of the Feature depends on it, so it runs first and alone. Once its code exists, the Feature's remaining Traces enter a graph of their own. Siblings with no shared files run at the same time, each in its own worktree. Traces that share files land in later sub-phases and stack on each other in Trace Plan order.

Two Traces of one Feature often *do* share files — that is what a Spine is. Expect the intra-Feature graph to serialize much of the set. It buys the disjoint cases, which are common once a Feature carries more than one story: an Extension Trace for story 2 rarely touches the files a Deepening Trace for story 1 touches.

Branching and PR bases for both cases follow `./branch-setup.md`. A Trace never waits for a merge — only for the code it builds on.

The graph still applies to legacy Task children (see `./issue-classification.md`). Legacy Tasks keep conflict-graph scheduling among themselves and against every other unit in the run.

## When to use

Use this any time multiple sub-agents will each modify files:

- `wtf.loop` — parallel Feature execution, and parallel Traces within one Feature after its Skeleton lands (plus legacy Task children within a phase)
- `wtf.verify-trace` Full Feature mode — sequential QA in spine order within a Feature; the graph schedules only its legacy Task children
- `wtf.refine` cascade — parallel refinement across affected children

Without this step, parallel worktrees can race on the same file. That produces dirty merges.

## Algorithm

### 1. Fetch Impacted Areas (with parent inheritance)

For **every** unit in the input set — Feature, legacy Task, Epic, Bug, or any loose/untyped issue:

```bash
gh issue view <issue_number> --json body --jq '.body'
```

Parse the `## Impacted Areas` section. Collect all file paths, modules, and components listed. Bugs and loose issues often skip this section. Treat them like any other node below.

**Inherit from parents (when a parent exists).** A node's *effective* impacted set is the union of:

- its own `## Impacted Areas`
- every ancestor's `## Impacted Areas` (walk `gh sub-issue list` / parent links up to the root)
- any `## Bounded Context` paths declared at any ancestor level

For a Feature node, also union any areas its child Traces declare. The Feature carries the conflict surface of its whole Trace sequence.

Parent-declared scope counts as conflict surface even when the child omits the specific file. This prevents two issues under different parents from racing on a shared module that only an ancestor names. Loose issues with no parent use only their own declared set.

### 2. Build the conflict graph

Undirected graph:

- Node = any unit in the run (Feature, legacy Task, Epic, Bug, loose item — type-agnostic)
- Edge between A and B if their *effective* impacted sets share at least one path, module, or component
- Edge also exists if A and B sit under different ancestors whose impacted sets overlap — cross-parent conflicts are real conflicts
- Use case-insensitive path prefix match — `src/payments/` conflicts with `src/payments/service.ts`

### 3. Greedy coloring

Assign units to sub-phases in issue-number order (stable):

- Assign the first unit to sub-phase 1.
- For each subsequent unit: assign the lowest-numbered sub-phase whose already-assigned units share no conflict edge with this unit.

### 4. Handle missing Impacted Areas

If an issue has no `## Impacted Areas` *and* inherits nothing from any ancestor, treat it as conflicting with all others. This is common for bugs and loose issues. Assign it to its own sub-phase. Note this in the execution plan so the user understands why it is serialized.

If the issue is empty but an ancestor declares impacted areas, use the inherited set (step 1). Do not serialize unnecessarily.

## Output shape

```
sub_phases: [
  { sub: 1, units: [#10, #11] },  # no file overlap — run in parallel
  { sub: 2, units: [#14] }         # overlaps with #10 or #11 — run after
]
```

Sub-phases execute sequentially. Units within a single sub-phase spawn in parallel. Inside a Feature unit, the Skeleton runs first and alone; its remaining Traces are then colored by this same algorithm into their own sub-phases.

## Advancement gate

Before advancing to the next sub-phase, every unit in the current sub-phase must have its **code landed on the branch the next sub-phase will branch from** — not necessarily merged to `main`.

- **Intra-Feature (Traces).** The gate is the previous Trace's branch, pushed and green. Do not wait for its PR to merge. The next Trace stacks on that branch per `./branch-setup.md`, so the code it needs is already there. Waiting for a human to review would idle the run for no gain.
- **Cross-Feature.** The gate is a merged PR, because the next Feature branches off `main` (or the feature branch) and cannot see another Feature's unmerged stack. For a Feature unit in `staged` delivery that is the feature PR; in `trunk` delivery it is the Feature's final Trace PR. Poll until `MERGED`:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Skills that do not produce PRs (for example `wtf.refine`) adapt this gate. Wait for all sub-agents in the current sub-phase to complete. Include any `NEEDS_INPUT` resolution. Then start the next sub-phase.
