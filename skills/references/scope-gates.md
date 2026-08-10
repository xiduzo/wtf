# Vertical-Slice Assessment and Scope Gates

Shared two-stage scope check used by every wtf write-* skill (`wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`). Also used by `wtf.refine` when scope changes.

The two stages fire at different points. They catch different problems. Both can fire in the same run. Treat them as independent.

## Stage 1 — Vertical-slice assessment (pre-draft)

Runs on **gathered context** (seed idea, research findings, user answers) before any draft exists. Catches structural incoherence when it is cheapest to fix.

The unit must be:

- **Epic** — a coherent, independently deliverable strategic initiative. It produces real user or business value on its own. It is not only a dependency for another epic.
- **Feature** — an end-to-end slice. It delivers one coherent, independently releasable user-facing capability. Concrete test: if this feature shipped tomorrow with no other unshipped features, could a domain actor use it and gain business value?
- **Task** — a vertical slice. It touches every layer needed for one observable, user-facing behavior (for example DB schema → service logic → API → UI). Independently shippable without another unmerged task.

Evaluate:

- **Passes** → proceed to draft.
- **Too broad** → propose smaller slices. Present the breakdown. Ask the user to confirm before continuing.
- **Has dependencies** → identify explicitly (what this depends on, what depends on this). Record issue numbers for later native-link creation. Do NOT write dependency references into the body yet. The create step handles native links and body writes together.

## Stage 2 — Scope gate (post-draft)

Runs on the **written draft**. Drafting sometimes reveals bundled objectives that were not visible in the abstract. Frame this to the user as a structural check. Do not frame it as a challenge to their earlier answers.

If one or more split signals fire:

1. State which signals you found.
2. Explain the risk in concrete terms — review friction, merge conflict surface, rollback complexity.
3. Propose a concrete split. Give two or three focused candidate titles. Write one sentence each. Use the right shape for the level (for example `[Actor] can [verb] [object]` for Features).
4. Ask "How do you want to handle this?" — header `Scope`:
   - **Keep the original draft** → proceed with the current draft without splitting
   - **Split it** → start over with one of the proposed smaller units
   - **Stop here** → exit without creating

On **Split it**, return to the earliest step where the seed was chosen. Carry forward already-gathered research. Only ask again for narrowed-scope clarification.

## Where the per-level signals live

Split signals are level-specific. They belong in the individual skills, not here:

| Level | Signal list |
|---|---|
| Epic | `wtf.write-epic` step 7 — multiple objectives, >8 features, spans contexts without seam, etc. |
| Feature | `wtf.write-feature` step 9 — >6 ACs, multiple actors, "and" in capability name, etc. |
| Task | `wtf.write-task` step 9 — >4 Gherkin scenarios, >4 unrelated modules, migration + behavior bundled, etc. |

Signals are heuristics, not rigid thresholds. The skills explicitly note this. Use judgment.

## Using this in refinement

`wtf.refine` reuses both stages when an insight changes scope. Re-run the vertical-slice assessment on the refined intent. Re-run the scope gate on the rewritten sections. Present findings as refinement concerns (not blockers). The user may knowingly accept a broader scope.
