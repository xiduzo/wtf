# File-Conflict Graph Coloring

Partition a set of parallelizable tasks into sub-phases where no two tasks in the same sub-phase touch overlapping files. Use this before spawning parallel sub-agents with worktree isolation.

## When to use

Any time multiple sub-agents will each modify files:

- `wtf.loop` — parallel task execution within a phase
- `wtf.verify-task` Full Feature mode — parallel QA across tasks
- `wtf.refine` cascade — parallel refinement across affected children

Without this step, parallel worktrees can race on the same file and produce dirty merges.

## Algorithm

### 1. Fetch Impacted Areas

For each task in the input set:

```bash
gh issue view <task_number> --json body --jq '.body'
```

Parse the `## Impacted Areas` section — collect all file paths, modules, and components listed.

### 2. Build the conflict graph

Undirected graph:

- Node = task
- Edge between A and B if they share at least one impacted file, module, or component
- Use case-insensitive path prefix match — `src/payments/` conflicts with `src/payments/service.ts`

### 3. Greedy coloring

Assign tasks to sub-phases in issue-number order (stable):

- Assign the first task to sub-phase 1.
- For each subsequent task: assign the lowest-numbered sub-phase whose already-assigned tasks share no conflict edge with this task.

### 4. Handle missing Impacted Areas

If a task has no `## Impacted Areas` section (or it is empty), treat it as conflicting with all others — assign it to its own sub-phase to be safe. Note this in the execution plan so the user understands why the task is serialized.

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
