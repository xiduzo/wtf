# Sub-Agent Protocol

Rules for any skill that spawns sub-agents via the Agent tool to execute wtf skill steps in parallel (e.g. `wtf.loop`, `wtf.verify-task` in Full Feature mode, `wtf.refine` during cascade).

## Why this matters

Sub-agents do NOT inherit the parent session's loaded skills. A sub-agent spawned from `wtf.loop` cannot see `wtf.implement-task`'s instructions unless those instructions are embedded in its prompt. Referencing a skill by name from inside a sub-agent prompt will fail — the sub-agent has no way to resolve it.

## Rules

### 1. Embed instructions inline

When a sub-agent needs to execute the steps of another wtf skill, the parent must Read that skill's `SKILL.md` at runtime and paste the relevant step-range into the sub-agent's prompt. Do not reference the skill by name — sub-agents cannot load skills.

The practical pattern is:

1. Read the target skill file (e.g. `skills/wtf.implement-task/SKILL.md`) at the moment the sub-agent is spawned.
2. Extract the body (skip YAML frontmatter).
3. Paste it into the sub-agent's prompt under a heading like "# Inline instructions — execute the steps below".
4. Prepend an override section that replaces interactive behavior (see rule 2) and passes any already-known context (task number, branch name, parent feature) so the sub-agent doesn't re-ask.

Reading at runtime (rather than hard-coding the steps in the orchestrator skill) keeps the sub-agent in sync with the underlying skill without manual mirroring.

### 2. No AskUserQuestion

Sub-agents MUST NOT call `AskUserQuestion`. All interactive prompts are replaced:

- Review/approval questions: skip, proceed automatically with the derived content.
- "What's next?" prompts: skip — the orchestrator controls sequencing.
- Any other interactive choice that would normally pause: record as a pending question (see rule 3).

### 3. NEEDS_INPUT return block

If a genuine blocker or ambiguity requires human input (test failures, missing contracts, codebase mismatches, approach conflicts), the sub-agent must return a structured result instead of asking:

```
NEEDS_INPUT
task: #<n>
question: <the question text>
options: <list of options>
context: <relevant details>
```

The orchestrator collects all `NEEDS_INPUT` results after each phase, groups them by task, presents them to the user via a single `AskUserQuestion` call, and re-dispatches the affected sub-agents with the answers embedded in their prompts before continuing.

### 4. Mandatory side effects still run

Lifecycle label updates must always execute in the sub-agent — they cannot be deferred to the orchestrator. If the `gh` command fails, record it in the sub-agent result so the orchestrator can retry.

The mandatory label transitions are:

| After step | Command |
|---|---|
| Implementation TDD cycle complete | `gh issue edit <task_number> --add-label "implemented"` |
| QA verification passes | `gh issue edit <task_number> --add-label "verified"` |
| Design handoff written | `gh issue edit <issue_number> --add-label "designed"` |

### 5. Isolation and worktree

When multiple sub-agents run in parallel, use `isolation: "worktree"` so each agent works on an independent copy of the repo. The worktree is branched from the current feature branch at spawn time. Instruct the sub-agent to run `git pull --rebase origin <feature_branch>` before starting work — it should not assume any particular local state.

See `./conflict-graph.md` for how to schedule sub-agents so overlapping files never run in parallel.

## Orchestrator checklist

Before spawning sub-agents, the orchestrator should verify:

1. The target skill file exists and can be read.
2. Each sub-agent prompt is fully self-contained: inline instructions, overrides, pre-known context, conflict-free sub-phase membership.
3. A collection point for `NEEDS_INPUT` results is prepared, with a plan for re-dispatch.
4. Label commands are listed in the sub-agent prompt with explicit "this must run even if other steps fail" framing.
