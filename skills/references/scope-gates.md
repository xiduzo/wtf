# Vertical-Slice Assessment and Scope Gates

Shared two-stage scope check used by every wtf write-* skill (`wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`) and by `wtf.refine` when scope changes.

The two stages fire at different points and catch different problems. Both can fire in the same run; treat them as independent.

## Stage 1 — Vertical-slice assessment (pre-draft)

Runs on **gathered context** (seed idea, research findings, user answers) before any draft exists. Catches structural incoherence when it is cheapest to fix.

The unit must be:

- **Epic** — a coherent, independently deliverable strategic initiative that produces real user or business value on its own, not only as a dependency for another epic.
- **Feature** — an end-to-end slice delivering one coherent, independently releasable user-facing capability. Concrete test: if this feature shipped tomorrow with no other unshipped features, could a domain actor use it and gain business value?
- **Task** — a vertical slice touching every layer needed for one observable, user-facing behavior (e.g. DB schema → service logic → API → UI). Independently shippable without another unmerged task.

Evaluate:

- **Passes** → proceed to draft.
- **Too broad** → propose smaller slices. Present the breakdown and ask the user to confirm before continuing.
- **Has dependencies** → identify explicitly (what this depends on, what depends on this). Record issue numbers for later native-link creation; do NOT write dependency references into the body yet — the create step handles native links and body writes together.

## Stage 2 — Scope gate (post-draft)

Runs on the **written draft**. Drafting sometimes reveals bundled objectives that were not visible in the abstract. Frame this to the user as a structural check, not a challenge to their earlier answers.

If one or more split signals fire:

1. State which signals you found.
2. Explain the risk in concrete terms — review friction, merge conflict surface, rollback complexity.
3. Propose a concrete split (two or three focused candidate titles, one sentence each, in the right shape for the level — e.g. `[Actor] can [verb] [object]` for Features).
4. Ask "How do you want to handle this?" — header `Scope`:
   - **Keep the original draft** → proceed with the current draft without splitting
   - **Split it** → start over with one of the proposed smaller units
   - **Stop here** → exit without creating

On **Split it**, return to the earliest step where the seed was chosen, carrying forward already-gathered research so only narrowed-scope clarification needs re-asking.

## Where the per-level signals live

Split signals are level-specific and belong in the individual skills, not here:

| Level | Signal list |
|---|---|
| Epic | `wtf.write-epic` step 7 — multiple objectives, >8 features, spans contexts without seam, etc. |
| Feature | `wtf.write-feature` step 9 — >6 ACs, multiple actors, "and" in capability name, etc. |
| Task | `wtf.write-task` step 9 — >4 Gherkin scenarios, >4 unrelated modules, migration + behavior bundled, etc. |

Signals are heuristics, not rigid thresholds — the skills explicitly note this. Use judgement.

## Using this in refinement

`wtf.refine` reuses both stages when an insight changes scope. Re-run the vertical-slice assessment on the refined intent, and re-run the scope gate on the rewritten sections. Present findings as refinement concerns (not blockers) — the user may knowingly accept a broader scope.
