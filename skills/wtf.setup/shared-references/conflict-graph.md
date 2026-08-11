# File-Conflict Graph Coloring

Partition a set of parallelizable work units into sub-phases. No two units in the same sub-phase touch overlapping files. Use this before spawning parallel sub-agents with worktree isolation.

## What the graph arbitrates

Traces within one Feature never enter the graph. They are sequential by design — spine-first. Each Trace branches only after the previous Trace's PR merged. Traces of one Feature share files by construction, so the graph would serialize them anyway.

**Features are the parallel unit.** The graph arbitrates file conflicts **across** Features. A Feature node carries its whole Trace sequence. Two Features run in parallel only when no Trace of one can touch a file of the other.

The graph still applies to legacy Task children (see `./issue-classification.md`). Legacy Tasks keep conflict-graph scheduling among themselves and against every other unit in the run.

## When to use

Use this any time multiple sub-agents will each modify files:

- `wtf.loop` — parallel Feature execution (plus legacy Task children within a phase)
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

Sub-phases execute sequentially. Units within a single sub-phase spawn in parallel. Inside a Feature unit, its Traces still run one at a time — the sub-phase parallelism never overrides spine-first sequencing.

## Advancement gate

Before advancing to the next sub-phase, all PRs from the current sub-phase must be merged. For a Feature unit in `staged` delivery, that is the feature PR. In `trunk` delivery, it is the Feature's final Trace PR. The next worktree then branches off a tree that already contains the prior work. Poll each PR until its state is `MERGED`:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Skills that do not produce PRs (for example `wtf.refine`) adapt this gate. Wait for all sub-agents in the current sub-phase to complete. Include any `NEEDS_INPUT` resolution. Then start the next sub-phase.
