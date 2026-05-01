# Pre-flight Validation

Detailed pre-flight checks for `wtf.loop` step 2. All checks run in parallel. Surface failures as human-in-the-loop gates — do not silently skip.

## a. Spec completeness check

For each Task, verify:

- `designed` label is present
- Gherkin section is non-empty
- Contracts section is non-empty

For each Feature, verify:

- Acceptance Criteria section is non-empty

For each Epic, verify:

- Goal and Bounded Context sections are non-empty

## b. Contradiction scan

Read each level of the hierarchy and check for contradictions:

- Task Gherkin conflicts with parent Feature ACs (e.g. Task passes a scenario the Feature says should fail)
- Task scope leaks outside the Feature's Bounded Context
- Duplicate Gherkin scenario names across Tasks in the same Feature
- Technical Approach (if present) uses a stack not in `docs/steering/TECH.md`

## c. Codebase reality check

For each Task's Impacted Areas and Contracts:

- Check that referenced modules, files, or interfaces exist in the codebase
- Check that API shapes in Contracts match current code signatures

Use the Agent tool to search the codebase for each referenced path/interface.

## d. Dependency validation

Using the dependency graph built in step 1:

1. **Circular dependency check** — run a topological sort over the internal edges. If a cycle is detected, list all issues involved and **hard stop** — do not proceed until the cycle is broken.

2. **External blocker check** — for each external blocker, verify it is merged:

   ```bash
   gh issue view <external_blocker_number> --json state,stateReason \
     --jq '"#\(.number) \(.state) (\(.stateReason))"'
   ```

   An external blocker is resolved only if its state is `CLOSED` with `stateReason: COMPLETED` (i.e., closed via a merged PR). If any external blocker is unresolved, list them as blockers — the loop cannot start until they are resolved.

3. **Topological sort** — sort **every** node (any type) into an execution order that respects every `blocked_by` edge at every level. A node inherits every ancestor's `blocked_by` edges: it cannot start until every dependency of every ancestor is also satisfied. Group nodes at the same effective depth into **execution phases** — nodes within a phase have no dependency between them, directly or through any ancestor.

4. **File-conflict sub-phasing** — apply the algorithm in `../../references/conflict-graph.md` to each phase, using the *effective* impacted set (node ∪ every ancestor's impacted set). This partitions each phase into numbered sub-phases where nodes within a sub-phase share no overlapping impacted files — including cross-parent overlaps inherited from ancestors, and overlaps against loose bugs/issues mixed into the run. Record the final execution structure as:

   ```
   phases: [
     { phase: 1, sub_phases: [
       { sub: 1, tasks: [#10, #11] },   # no file overlap — run in parallel
       { sub: 2, tasks: [#14] }          # overlaps with #10 or #11 — run after
     ]},
     { phase: 2, sub_phases: [...] }
   ]
   ```

## Gate — surface all findings at once

If any pre-flight check found issues, present them grouped by type:

```
Pre-flight findings:
  Contradictions:    [list with issue numbers and description]
  Missing sections:  [list]
  Codebase mismatches: [list]
  Unresolved deps:   [list]
  Circular deps:     [list — HARD STOP if any]
```

Apply `../../references/questioning-style.md` and ask "Pre-flight found [n] issue(s). How would you like to proceed?" — header `Pre-flight`:

- **Fix before running** → resolve the issues above, then re-run the loop
- **Proceed with warnings** → acknowledge the issues and run anyway (not recommended for contradictions; only available if no circular deps)
- **Stop** → exit; I'll address these manually

If **no findings**: continue silently.
