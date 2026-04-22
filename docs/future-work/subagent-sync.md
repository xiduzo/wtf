# Task: Prevent sub-agent inline-skill drift

**Status:** Convention documented in `skills/references/subagent-protocol.md` rule 1. Not enforced. Low priority — current approach works as long as the protocol is respected.

## Problem

`wtf.loop`, `wtf.verify-task` (Full Feature mode), and `wtf.refine` (cascade) spawn sub-agents that need the step-by-step content of other skills. Sub-agents do NOT inherit the parent session's loaded skills, so referencing a skill by name from inside a sub-agent prompt fails.

The current protocol (see `skills/references/subagent-protocol.md` rule 1) tells the orchestrator to:

1. `Read` the target skill's `SKILL.md` at runtime.
2. Paste the relevant step range into the sub-agent prompt.
3. Prepend overrides (no `AskUserQuestion`, `NEEDS_INPUT` return block, mandatory labels).

This relies entirely on the orchestrator following the rule every time. Two risks:

- **Drift.** An orchestrator skill could hard-code a stale copy of another skill's steps inline (forgetting the "read at runtime" part). The copy silently goes out of date when the referenced skill changes.
- **Inconsistency.** Each orchestrator reinvents the Read + paste logic. Subtle differences (which step range, which overrides included, how context is passed) compound over time.

## Possible approaches

### Option A — Helper script

Add a small script (Python or shell) at `skills/references/scripts/compose-subagent-prompt.sh` that:

- Takes a target skill name, a step-range spec, and a context object.
- Reads the skill's `SKILL.md`, extracts the requested steps.
- Emits a fully-formed sub-agent prompt with the standard override preamble.

Orchestrators call this script instead of implementing the logic inline.

**Pros:** Single source of truth for prompt composition. Evolves independently of individual skills.

**Cons:** Adds a runtime dependency (Python or shell). Sub-agent spawning becomes opaque to someone reading the orchestrator skill.

### Option B — CI check

Add a pre-commit or CI hook that:

- Scans each orchestrator skill for large inline quotations of other skills' content.
- Flags any block over N lines that matches substantial content from another skill's `SKILL.md`.

Prevents hard-coded copies from creeping in; the orchestrator must instead reference the skill's file path.

**Pros:** No runtime dependency. Catches drift at commit time.

**Cons:** False-positive noisy (legitimate short quotes of commit formats, section headings, etc.). Needs tuning.

### Option C — Status quo

Keep the current convention. Trust the protocol. Rely on code review to catch drift.

**Pros:** Zero added machinery.

**Cons:** Drift will eventually happen. No safety net.

## Recommendation

Start with Option C until drift actually shows up in a concrete incident. If drift is observed, jump to Option A (helper script). Option B is speculative and likely too noisy to be worth building.

## Definition of done

This task is "done" when one of:

- A real drift incident has been observed and Option A implemented to prevent recurrence.
- Six months have passed with zero drift incidents, at which point close as "not needed — convention is sufficient".
