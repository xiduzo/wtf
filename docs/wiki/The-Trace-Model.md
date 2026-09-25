# The Trace model

The unit of implementation is the **Trace**, a tracer-bullet work unit ([The Pragmatic Programmer](https://fullstackhub.substack.com/p/the-pragmatic-programmer-12-tracer), [AI Hero](https://www.aihero.dev/tracer-bullets)). A Trace claims one user story and a declared subset of its Gherkin scenarios: its **Scenario Claim**. It implements that claim through every layer in one pass. Each Trace leaves the system in a releasable state.

## Skeleton, Spine, and later Traces

The first Trace of a Feature is the **Skeleton**: the happy path of the primary story, minimal, through every layer, at production quality. Each later Trace extends the **Spine**.

- An **Extension Trace** adds the next story.
- A **Deepening Trace** claims more scenarios of a story that already started.

The Scenario Claims of a story cover all its scenarios, with no overlap.

## The Feature is canonical

The Feature body is the canonical source for all stories and their Gherkin. A Trace claims scenarios and never re-derives them.

The Trace Plan on the Feature is an aim, not a contract. After each Trace lands, `wtf.refine` re-aims the plan. An autonomous re-aim changes only the order. It can reorder entries, re-batch them, and move scenarios between them. A human approves each change to the set of scenarios that the plan delivers.

## One stack per Feature

Each Feature delivers through one linear stack of Trace PRs. Each Trace starts its branch from the top of the stack. Thus no Trace waits for a merge. Traces that share no files build at the same time. Then they join the stack one after the other. See [Delivery and stacks](Delivery-and-Stacks.md).

## Domain-Driven Design

DDD is the foundation of WTF, not an add-on. Each issue, scenario, and PR uses the ubiquitous language of the project. The skills apply `ddd-writing-rules.md` each time they write. Actors are domain roles, never a generic "user" or "admin". Gherkin scenarios use the vocabulary from the VISION doc. Thus product, design, engineering, and QA share one model of the system.

As a result, the specs stay clear when the project grows. Agents write code against stable terms, not against synonyms that drift. A new contributor learns the domain, not a set of nicknames.

WTF uses the same discipline for its own terms. [`CONTEXT.md`](https://github.com/xiduzo/wtf/blob/main/CONTEXT.md) defines them: Trace, Skeleton, Extension Trace, Deepening Trace, Spine, Spine Position, Scenario Claim, and Re-aim.
