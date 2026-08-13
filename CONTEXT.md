# WTF Work Model

The domain language of the WTF workflow system: how work is described, decomposed, and delivered. Skills and references use these terms; issue bodies are written in them.

## Language

**Epic**:
The dot on the horizon. A strategic outcome that takes multiple Features to reach.
_Avoid_: initiative, project

**Feature**:
One step toward an Epic. A user-facing capability carrying 1..n co-related user stories that share one Spine.
_Avoid_: epic (for large features), module

**User Story**:
One actor's need within a Feature — actor, domain verb, business outcome — with its Acceptance Criteria and Gherkin scenarios.
_Avoid_: requirement, use case (a scenario is the use-case grain, not the story)

**Trace**:
One pass over a Feature's Spine. It claims exactly one story and a declared subset of that story's Gherkin scenarios, implemented end-to-end through every layer. A story is delivered by 1..n Traces whose scenario claims cover all its scenarios without overlap. The first Trace of a story is a Skeleton or an Extension Trace. A Trace always leaves the system releasable: production quality, verified against its Scenario Claim, whichever branch it lands on.
_Avoid_: task (legacy kind), slice, ticket, subtask

**Skeleton**:
The first Trace of a Feature. A Feature has exactly one. It claims the primary story's happy-path scenario, minimally, through every layer, at production quality. It lays the Spine. Lean but complete — never a prototype.
_Avoid_: walking skeleton, prototype, spike (a spike is disposable; a Skeleton is not)

**Extension Trace**:
The first Trace of a further story on the Spine that the Skeleton laid. It adds the story to the Spine. It does not prove the Spine again. Only a Feature with more than one story has one.
_Avoid_: second skeleton, follow-up trace, next slice (a `gh` CLI extension is a different thing)

**Deepening Trace**:
A Trace that claims further scenarios — edge cases, failure modes — of a story already started by a Skeleton or an Extension Trace. It cites the story it deepens. It is never storyless.
_Avoid_: hardening task, polish, cleanup

**Spine**:
The end-to-end path through all system layers that a Feature's Traces lay down and extend. The Skeleton proves it. Every later Trace builds on it.
_Avoid_: architecture, scaffolding

**Spine Position**:
The role of a Trace on its Feature's Spine — Skeleton, Extension, or Deepening. Every Trace records exactly one.
_Avoid_: trace type, phase, stage

**Trace Plan**:
The ordered checklist of Traces in a Feature body. Each entry names its story, its Scenario Claim, and what it adds to the Spine. It is a living plan — the current aim, not a contract.
_Avoid_: task list, breakdown, backlog

**Re-aim**:
The update of a Feature's Trace Plan after a Trace lands, in response to what the Trace revealed. Always performed through refine. Autonomous re-aim owns the order only. It can reorder entries, re-batch them, and move scenarios between them. It cannot change which scenarios the plan delivers. It proposes each addition and each removal. A human approves every change to the set, in both directions.
_Avoid_: replan, groom, grow-only (the set is gated in both directions)

**Scenario Claim**:
The declared subset of one story's Gherkin scenarios that a single Trace implements and is verified against.
_Avoid_: test scope, coverage
