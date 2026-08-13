# Planning Mode — guided vs. flow

Every WTF planning skill uses this file to decide how much it asks and how much it derives. The mode controls interaction density. It never controls quality.

Read this from any skill that authors Epics, Features, or Traces. The current consumers are `wtf.write-feature`, `wtf.epic-to-features`, and `wtf.feature-to-traces`. Other planning skills adopt it the same way.

There are two modes:

- **`guided`** — the skill asks at each step. The user shapes each artifact as it forms. Use this when the user still discovers what they want. This is the safe default.
- **`flow`** — the skill derives everything it can. It batches its questions. It presents **one consolidated review** before it creates anything. Use this when the spec source (the Epic, the codebase, the steering docs) already answers most questions.

## Contents

- [Resolve the mode](#resolve-the-mode) — set `$WTF_PLAN` once per session
- [What flow mode changes](#what-flow-mode-changes)
- [What no mode changes](#what-no-mode-changes)
- [Escalation in flow mode](#escalation-in-flow-mode)
- [Mid-run switches](#mid-run-switches)

## Resolve the mode

Run this **once** near the start of a planning skill. Reuse `$WTF_PLAN` for the rest of the session. The precedence is:

1. **Explicit argument** — the user typed a mode in the slash invocation (for example `/wtf.epic-to-features 42 flow`). Use it. Skip the config read.
2. **Config** — `.wtf/config.json` (written by `wtf.setup`).
3. **Default** — `guided`, the choice that is safe everywhere.

```bash
WTF_PLAN=$(python3 - <<'PY' 2>/dev/null || true
import json
try:
    print((json.load(open(".wtf/config.json")).get("planning") or "").strip())
except Exception:
    pass
PY
)
case "$WTF_PLAN" in guided|flow) : ;; *) WTF_PLAN=guided ;; esac
```

`$WTF_PLAN` is now either `guided` or `flow`. Tell the user which mode is active and where it came from (argument, config, or default) in one short line.

## What flow mode changes

Flow mode changes **when the user is consulted**, not **what gets built**. The concrete deltas:

| Concern | `guided` | `flow` |
|---|---|---|
| Clarification questions | Ask each unresolved question as it comes up | Answer from the Epic, codebase, glossary, and steering docs first. Collect only the genuinely unanswerable into **one** batched `AskUserQuestion` |
| Draft review | Review each artifact as it is drafted | One consolidated review of the full batch before anything is created |
| Continue gates ("ready for the next one?") | Ask between items | Skip. The confirmed plan controls sequencing |
| DoR items that name a human process (PO agreement, design handoff) | Ask blocker-or-waive per item | Auto-waive with the note `Waived (flow mode)`. The consolidated review is where the user objects |
| Drafting | Inline, sequential | May fan out to sub-agents per `./subagent-protocol.md`. Sub-agents draft; they never create issues |
| Next-step offers | Offer after each artifact | Offer once, at the end of the batch |

## What no mode changes

These run identically in both modes. Flow mode is not a quality waiver:

- The DDD Language Guard (`./ddd-writing-rules.md`).
- Scope gates, both stages (`./scope-gates.md`). A firing split signal is a genuine ambiguity — it escalates even in flow.
- Strict STE for durable bodies (`./ste-writing.md`).
- Template loading and body structure (`./issue-template-loading.md`).
- Issue classification, sub-issue links, and dependency links (`./issue-classification.md`, `./gh-setup.md`).
- The gh body helper for every body write (`./gh-body-helper.md`).
- Exactly one review before issues are created. Flow consolidates the review. It never removes it.

## Escalation in flow mode

Flow mode is not silent mode. Escalate when derivation hits a wall:

- A contradiction between the Epic and the codebase, or between two derived artifacts.
- A scope-gate split signal.
- A missing fact no source answers (an unnamed domain actor, an unknown constraint).

Collect escalations the way `wtf.loop` does. Batch them. Present them in a single `AskUserQuestion` per round. Sub-agents return `NEEDS_INPUT` blocks per `./subagent-protocol.md`; the orchestrator asks on their behalf. Never let a sub-agent ask the user directly.

## Mid-run switches

The user can flip the mode at any point. Honor both directions:

- In `guided`, phrases like "just do the rest", "stop asking", or "finish it" switch the remainder of the run to `flow`.
- In `flow`, phrases like "slow down", "walk me through it", or an answer that reopens the plan switch the remainder to `guided`.

A switch applies to the current run only. It does not rewrite `.wtf/config.json`. Tell the user the mode changed.
