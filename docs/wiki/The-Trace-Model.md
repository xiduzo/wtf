# The Trace model

The unit of implementation is the **Trace**, a tracer-bullet work unit ([The Pragmatic Programmer](https://fullstackhub.substack.com/p/the-pragmatic-programmer-12-tracer), [AI Hero](https://www.aihero.dev/tracer-bullets)). A Trace claims one user story and a declared subset of its Gherkin scenarios: its **Scenario Claim**. It implements that claim through every layer in one pass. Every Trace leaves the system releasable.

## Skeleton, Spine, and later Traces

The first Trace of a Feature is the **Skeleton**: the primary story's happy path, minimal, through every layer, at production quality. Each later Trace extends the **Spine**.

- An **Extension Trace** adds the next story.
- A **Deepening Trace** claims more scenarios of a story that already started.

Scenario Claims partition a story's scenarios: full cover, no overlap.

## The Feature stays canonical

The Feature body stays canonical for all stories and their Gherkin. Traces claim scenarios and never re-derive them.

The Trace Plan is a living aim, not a contract. After each landed Trace, `wtf.refine` re-aims the plan. The autonomous re-aim owns the order only: it can reorder, re-batch, and move scenarios between entries. A human approves every change to the set of scenarios the plan delivers.

## One stack per Feature

Each Feature delivers through one linear stack of Trace PRs. Each Trace branches off the top of the stack, so no Trace waits for a merge. Traces that share no files build at the same time, then join the stack one after the other. See [Delivery and stacks](Delivery-and-Stacks.md).

## Legacy Tasks

Legacy Task issues stay readable. Read paths treat them as legacy Traces. Write paths never create Tasks again.

The decision record is [`docs/adr/0001-traces-replace-tasks.md`](https://github.com/xiduzo/wtf/blob/main/docs/adr/0001-traces-replace-tasks.md). [`CONTEXT.md`](https://github.com/xiduzo/wtf/blob/main/CONTEXT.md) pins the vocabulary: Trace, Skeleton, Extension Trace, Deepening Trace, Spine, Spine Position, Scenario Claim, and Re-aim.

## Domain-Driven Design

DDD is the foundation of WTF, not an add-on. Every issue, scenario, and PR uses the project's ubiquitous language, and `ddd-writing-rules.md` enforces it at write time. Actors are domain roles, never a generic "user" or "admin". Gherkin scenarios use the vocabulary the VISION doc defines, so product, design, engineering, and QA share one model of the system.

The result: specs stay legible as the project grows. Agents generate code against a stable contract instead of drifting synonyms. A new contributor reads the domain instead of decoding nicknames.
