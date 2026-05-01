# Questioning Style

How any wtf skill should use `AskUserQuestion` when gathering context from the user.

## Core rules

1. **One question at a time.** Wait for the answer before asking the next. Do not batch questions into a single message — it makes the UI confusing and the answers hard to route.

2. **Always use `AskUserQuestion`** — including for open-ended questions like "What are the success criteria?" or "Who is the stakeholder?". Free-text-only prompts make research-backed suggestions invisible to the user and skip a chance to narrow the answer space.

3. **Pre-fill options from research.** For each question, infer 1–2 likely answers from the codebase, issue history, or prior conversation and pass them as `options`. The user can still type a free-text answer — the UI automatically appends an "Other (type your answer)" escape hatch, so do NOT add one manually.

4. **Prioritize by urgency.** Ask the questions that most constrain the draft first. Stop when you have enough to write a complete draft — do not run through every possible question.

5. **Skip what research answered.** Topics already addressed by research, prior answers, or loaded context (Epic/Feature/steering docs) must be skipped silently. Re-asking them costs trust.

6. **Acknowledge briefly between answers.** One sentence max. Do not re-explain the prior answer — move on.

## Compact notation in skill files

Skill files describe asks in a compact form. **You (Claude) must translate each compact ask into an actual `AskUserQuestion` tool call** — the notation is shorthand for the author, not a directive to another system. The tool name and field names (`question:`, `header:`, `options:`) do not need to repeat in the skill file, but you must emit the tool call when executing.

**Form 1 — inline** (inferred options, source-driven):

> Ask "Which Feature does this belong to?" — header `Feature`, options from recent open issues labeled `feature`.

**Form 2 — sub-list** (explicit options or branching):

> Ask "Does this look right?" — header `Review`:
> - **Looks good** → proceed with creation
> - **I have changes** → revise first

**Form 3 — mixed** (inferred candidates plus a static fallback):

> Ask "Which Epic does this Feature belong to?" — header `Epic`:
> - Candidates from recent open issues labeled `epic`
> - **None** — no parent Epic exists yet

### Operators

- `→` — branch action ("what the skill does next on this answer"). Use for routing decisions.
- `—` — description ("what this option means"). Use when the option needs clarification but does not branch the flow.

### Conventions

- Wrap the question in straight double quotes — it is the literal user-facing text.
- Wrap the header in backticks — it is the UI tag the user sees.
- Drop the "1–2 likely options" boilerplate; rule 3 enforces it.
- For conditional asks ("if X is present, ask…"), put the condition before the `Ask` clause.

## Reference shapes

You must expand compact notation into this tool call. Canonical form:

```
AskUserQuestion(
  question: "What triggers this capability?",
  header: "Trigger",
  options: [
    {label: "User initiates", description: "Explicit button or form action"},
    {label: "System triggers", description: "Automatic event or schedule"},
    {label: "Both", description: "User-initiated and automatic"},
  ]
)
```

## When to ask in a single message instead

Rare. Only when three conditions all hold: the questions are tightly coupled, the answers are short, and no answer changes which other questions are needed. Even then, prefer `AskUserQuestion` with options when at least one question has a constrained answer space.
