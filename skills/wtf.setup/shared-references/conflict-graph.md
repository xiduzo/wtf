# File-Conflict Graph Coloring

Partition a set of parallelizable tasks into sub-phases where no two tasks in the same sub-phase touch overlapping files. Use this before spawning parallel sub-agents with worktree isolation.

## When to use

Any time multiple sub-agents will each modify files:

- `wtf.loop` — parallel task execution within a phase
- `wtf.verify-task` Full Feature mode — parallel QA across tasks
- `wtf.refine` cascade — parallel refinement across affected children

Without this step, parallel worktrees can race on the same file and produce dirty merges.

## Algorithm

### 1. Fetch Impacted Areas (with parent inheritance)

For **every** issue in the input set — Task, Feature, Epic, Bug, or any loose/untyped issue:

```bash
gh issue view <issue_number> --json body --jq '.body'
```

Parse the `## Impacted Areas` section — collect all file paths, modules, and components listed. Bugs and loose issues often skip this section; treat them like any other node below.

**Inherit from parents (when a parent exists).** A node's *effective* impacted set is the union of:

- its own `## Impacted Areas`
- every ancestor's `## Impacted Areas` (walk `gh sub-issue list` / parent links up to the root)
- any `## Bounded Context` paths declared at any ancestor level

Parent-declared scope counts as conflict surface even when the child omits the specific file. This prevents two issues under different parents from racing on a shared module that only an ancestor names. Loose issues with no parent use only their own declared set.

### 2. Build the conflict graph

Undirected graph:

- Node = any issue in the run (Task, Feature, Epic, Bug, loose item — type-agnostic)
- Edge between A and B if their *effective* impacted sets share at least one path, module, or component
- Edge also exists if A and B sit under different ancestors whose impacted sets overlap — cross-parent conflicts are real conflicts
- Use case-insensitive path prefix match — `src/payments/` conflicts with `src/payments/service.ts`

### 3. Greedy coloring

Assign tasks to sub-phases in issue-number order (stable):

- Assign the first task to sub-phase 1.
- For each subsequent task: assign the lowest-numbered sub-phase whose already-assigned tasks share no conflict edge with this task.

### 4. Handle missing Impacted Areas

If an issue has no `## Impacted Areas` *and* inherits nothing from any ancestor (common for bugs and loose issues), treat it as conflicting with all others — assign it to its own sub-phase. Note this in the execution plan so the user understands why it is serialized.

If the issue is empty but an ancestor declares impacted areas, use the inherited set (step 1) — do not serialize unnecessarily.

## Output shape

```
sub_phases: [
  { sub: 1, tasks: [#10, #11] },  # no file overlap — run in parallel
  { sub: 2, tasks: [#14] }         # overlaps with #10 or #11 — run after
]
```

Sub-phases execute sequentially. Tasks within a single sub-phase spawn in parallel.

## Advancement gate

Before advancing to the next sub-phase, all PRs from the current sub-phase must be merged so the next worktree branches off a tree that already contains the prior work. Poll each PR until its state is `MERGED`:

```bash
gh pr view <pr_number> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'
```

Skills that do not produce PRs (e.g. `wtf.refine`) adapt this gate: wait for all sub-agents in the current sub-phase to complete (including any `NEEDS_INPUT` resolution) before starting the next sub-phase.
