# Questioning Style

How any wtf skill should use `AskUserQuestion` when gathering context from the user.

## Core rules

1. **One question at a time.** Wait for the answer before asking the next. Do not batch questions into a single message — it makes the UI confusing and the answers hard to route.

2. **Always use `AskUserQuestion`** — including for open-ended questions like "What are the success criteria?" or "Who is the stakeholder?". Free-text-only prompts make research-backed suggestions invisible to the user and skip a chance to narrow the answer space.

3. **Pre-fill options from research.** For each question, infer 1–2 likely answers from the codebase, issue history, or prior conversation and pass them as `options`. The user can still type a free-text answer — the UI automatically appends an "Other (type your answer)" escape hatch, so do NOT add one manually.

4. **Prioritize by urgency.** Ask the questions that most constrain the draft first. Stop when you have enough to write a complete draft — do not run through every possible question.

5. **Skip what research answered.** Topics already addressed by research, prior answers, or loaded context (Epic/Feature/steering docs) must be skipped silently. Re-asking them costs trust.

6. **Acknowledge briefly between answers.** One sentence max. Do not re-explain the prior answer — move on.

## Example shapes

Closed question with research-inferred options:

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

Open-ended question with plausible seeds:

```
AskUserQuestion(
  question: "Who is the primary domain actor?",
  header: "Actor",
  options: [
    {label: "Fulfilment Manager", description: "Found in src/fulfilment/*"},
    {label: "Payment Auditor", description: "Named role in the Epic context"},
  ]
)
```

## When to ask in a single message instead

Rare. Only when three conditions all hold: the questions are tightly coupled, the answers are short, and no answer changes which other questions are needed. Even then, prefer `AskUserQuestion` with options when at least one question has a constrained answer space.
