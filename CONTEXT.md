# WTF Work Model

The domain language of the WTF workflow system: how work is described, decomposed, and delivered. Skills and references use these terms; issue bodies are written in them.

## Language

**Epic**:
The dot on the horizon. A strategic outcome that takes multiple Features to reach.
_Avoid_: initiative, project

**Feature**:
One step toward an Epic. A user-facing capability carrying 1..n co-related user stories that share one spine.
_Avoid_: epic (for large features), module

**User Story**:
One actor's need within a Feature — actor, domain verb, business outcome — with its Acceptance Criteria and Gherkin scenarios.
_Avoid_: requirement, use case (a scenario is the use-case grain, not the story)

**Trace**:
One pass over a Feature's spine. It claims exactly one story and a declared subset of that story's Gherkin scenarios, implemented end-to-end through every layer. A story is delivered by 1..n Traces whose scenario claims cover all its scenarios without overlap. A Trace always leaves the system releasable: production quality, verified against its Scenario Claim, whichever branch it lands on.
_Avoid_: task (legacy kind), slice, ticket, subtask

**Skeleton**:
The first Trace of a Feature. It claims the primary story's happy-path scenario, minimally, through every layer, at production quality. Lean but complete — never a prototype.
_Avoid_: walking skeleton, prototype, spike (a spike is disposable; a Skeleton is not)

**Deepening Trace**:
A Trace after the Skeleton that claims further scenarios — edge cases, failure modes — of a story already started. It cites the story it deepens; it is never storyless.
_Avoid_: hardening task, polish, cleanup

**Spine**:
The end-to-end path through all system layers that a Feature's Traces lay down and extend. The Skeleton proves it; every later Trace builds on it.
_Avoid_: architecture, scaffolding

**Trace Plan**:
The ordered checklist of Traces in a Feature body. Each entry names its story, its Scenario Claim, and what it adds to the Spine. It is a living plan — the current aim, not a contract.
_Avoid_: task list, breakdown, backlog

**Re-aim**:
The update of a Feature's Trace Plan after a Trace lands, in response to what the Trace revealed. Always performed through refine. Autonomous re-aim is grow-only: it may reorder, re-batch, and add scenarios, and may only suggest a removal — a human approves every shrinkage.
_Avoid_: replan, groom

**Scenario Claim**:
The declared subset of one story's Gherkin scenarios that a single Trace implements and is verified against.
_Avoid_: test scope, coverage
