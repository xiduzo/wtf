# Pre-flight Validation

Detailed pre-flight checks for `wtf.loop` step 2. All checks run in parallel. Surface failures as human-in-the-loop gates — do not silently skip.

## a. Spec completeness check

For each Feature, verify:

- Acceptance Criteria section is non-empty
- Each user story carries its canonical Gherkin scenarios in the Feature body
- A **Trace Plan** exists: an ordered checklist where each entry names its story, its Scenario Claim, and what it adds to the Spine
- Entry 1 is the Skeleton, and no other entry is a Skeleton
- Every story other than the Skeleton's story has exactly one Extension entry, before that story's Deepening entries
- Each unchecked plan entry links an existing Trace issue

For each Trace, verify:

- `designed` label is present (unless the user waived design)
- The story and the Scenario Claim are present in the body

For each Epic, verify:

- Goal and Bounded Context sections are non-empty

For each legacy Task (see `../../references/issue-classification.md`), keep the old checks:

- `designed` label is present
- Gherkin section is non-empty
- Contracts section is non-empty

**Partition check.** Per story, take the union of all Scenario Claims across the story's Traces. The union must equal the story's canonical scenario set — full cover. No scenario may appear in two claims — no overlap. Report each uncovered scenario and each double-claimed scenario as a finding.

## b. Contradiction scan

Read each level of the hierarchy and check for contradictions:

- A Scenario Claim names a scenario that does not exist in the Feature's canonical set
- A Trace's synced scenario copy drifts from the Feature body (different actor, steps, or outcome)
- A Trace's claimed scenarios conflict with the parent Feature's ACs (e.g. a Trace passes a scenario the Feature says should fail)
- Trace scope leaks outside the Feature's Bounded Context
- Technical Approach (if present) uses a stack not in `docs/steering/TECH.md`
- Legacy Tasks: duplicate Gherkin scenario names across Tasks in the same Feature, Gherkin vs Feature AC conflicts

## c. Codebase reality check

For each Feature's Impacted Areas, each Trace's Technical Approach (when present), and each legacy Task's Impacted Areas and Contracts:

- Check that referenced modules, files, or interfaces exist in the codebase
- Check that API shapes in legacy Contracts match current code signatures

Use the Agent tool to search the codebase for each referenced path/interface.

## d. Dependency validation

Using the dependency graph and the Feature units built in step 1:

1. **Circular dependency check** — run a topological sort over the internal edges. If a cycle is detected, list all issues involved and **hard stop** — do not proceed until the cycle is broken.

2. **External blocker check** — for each external blocker, verify it is merged:

   ```bash
   gh issue view <external_blocker_number> --json state,stateReason \
     --jq '"#\(.number) \(.state) (\(.stateReason))"'
   ```

   An external blocker is resolved only if its state is `CLOSED` with `stateReason: COMPLETED` (i.e., closed via a merged PR). If any external blocker is unresolved, list them as blockers — the loop cannot start until they are resolved.

3. **Topological sort** — sort **every** unit into an execution order that respects both edge kinds from step 1: `blocked_by` (dependency) and `rolls_up` (parent→child join). A unit inherits every ancestor's `blocked_by` edges — but **not** their `rolls_up` edges (inheriting roll-up would make a child depend on itself, a false cycle): it cannot start until every dependency of every ancestor is also satisfied. Because each parent rolls up its whole subtree, a dependency on a parent (e.g. Feature B `blocked_by` Feature A) is automatically deferred until **every** Trace under Feature A has merged — not just the Feature A node. A Feature unit already carries its own Traces, so it satisfies its `rolls_up` edges through its Trace sequence. Epic nodes appear in the order purely as join barriers; step 4 dispatches only Feature units and legacy Tasks, so a phase holding only barrier nodes is a no-op. Group units at the same effective depth into **execution phases** — units within a phase have no dependency between them, directly or through any ancestor.

4. **Cross-feature conflict sub-phasing** — apply the algorithm in `../../references/conflict-graph.md` to each phase, using the *effective* impacted set (unit ∪ every ancestor's impacted set; a Feature unit also unions the areas its Traces declare). This partitions each phase into numbered sub-phases where units within a sub-phase share no overlapping impacted files — including cross-parent overlaps inherited from ancestors, and overlaps against loose bugs/issues mixed into the run. Then apply the same algorithm a second time, **inside** each Feature unit, over its own Traces: the Skeleton alone in trace-sub-phase 1, the remaining Traces colored by their `## Impacted Areas`. Record the final execution structure as:

   ```
   phases: [
     { phase: 1, sub_phases: [
       { sub: 1, units: [
           Feature #5 (traces: [#10] → [#11, #12] → [#13]),   # #11 and #12 share no files — parallel
           Feature #6 (traces: [#20])
         ] },                                                  # no file overlap between #5 and #6 — parallel
       { sub: 2, units: [Task #14 (legacy)] }                  # overlaps with #5 — run after
     ]},
     { phase: 2, sub_phases: [...] }
   ]
   ```

   A Trace's branch stacks on the Trace it builds on rather than waiting for a merge (`../../references/branch-setup.md`), so a later trace-sub-phase gates on a pushed, green branch — not on a merged PR.

## Gate — surface all findings at once

If any pre-flight check found issues, present them grouped by type:

```
Pre-flight findings:
  Contradictions:      [list with issue numbers and description]
  Partition violations: [uncovered / double-claimed scenarios per story]
  Missing sections:    [list — includes missing Trace Plan or Skeleton]
  Codebase mismatches: [list]
  Unresolved deps:     [list]
  Circular deps:       [list — HARD STOP if any]
```

Apply `../../references/questioning-style.md` and ask "Pre-flight found [n] issue(s). How would you like to proceed?" — header `Pre-flight`:

- **Fix before running** → resolve the issues above, then re-run the loop
- **Proceed with warnings** → acknowledge the issues and run anyway (not recommended for contradictions or partition violations; only available if no circular deps)
- **Stop** → exit; I'll address these manually

If **no findings**: continue silently.
