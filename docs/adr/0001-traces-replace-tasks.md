# Traces replace Tasks as the implementation unit

**Status:** accepted (2026-08-11)

The Task layer claimed to hold vertical slices but invited horizontal layering: decomposition pressure produced layer tasks (model → API → UI → email) that defer integration feedback, and an agent does not need layer decomposition — it drives one story end-to-end in one pass. Following the tracer-bullet sources ([aihero.dev/tracer-bullets](https://www.aihero.dev/tracer-bullets), *The Pragmatic Programmer*), we replace Tasks with **Traces**: a Trace is one pass over the Feature's Spine that claims exactly one story plus a Scenario Claim, Traces run spine-first within a Feature, the Trace Plan is re-aimed grow-only through `wtf.refine`, scenarios stay canonical in the Feature issue, and delivery is `staged` or `trunk` per config. The full model is specified in [`docs/future-work/trace-model.md`](../future-work/trace-model.md).

## Considered Options

- **Keep Tasks, tighten the vertical-slice rules.** Rejected. The task spec is a lossy translation between the story and the implementation, with no consumer. Rules do not remove the decomposition pressure that produces layer tasks.
- **Dual model behind a config switch (Tasks and Traces).** Rejected. Two write paths across ~22 skills, permanent query and skill-triggering ambiguity, and no user who benefits. Legacy read support gives old repos what they need without a second model.
- **One issue per scenario.** Rejected. Too fine a grain — issue overhead per scenario with no delivery benefit. The Scenario Claim partition gives the same mechanical verification at a coarser, schedulable grain.
- **File-canonical Gherkin (committed `.feature` files).** Rejected. It splits the product surface from the issue that PMs and designers actually edit, and it requires permalink and sync machinery. Ephemeral projection at verify time keeps the Feature body canonical and still executes real Gherkin when a runner exists.

## Consequences

- Fewer, bigger PRs: one per Trace instead of one per layer task. Every Trace must leave the system releasable.
- A phased 4-stage migration touches ~22 skills and 13+ references (foundations → authoring → execution → periphery).
- Read paths treat legacy Task issues as legacy-Traces indefinitely. Write paths never create Tasks again.
- Five skills rename without deprecation aliases: write-task → write-trace, feature-to-tasks → feature-to-traces, implement-task → implement-trace, verify-task → verify-trace, design-task → design-trace. A changelog rename table covers the migration.
- `.wtf/config.json` gains `feature_scope` and `delivery`. The Trace kind (☄️) is provisioned like Epic. 🛠 retires and is never reused.
