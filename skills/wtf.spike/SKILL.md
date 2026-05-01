---
name: wtf.spike
description: This skill should be used when a developer or tech lead needs to investigate a technical unknown before committing to an approach — for example "run a spike on X", "I need to research this before writing the epic", "we don't know how to approach this yet", "investigate if we can use X for Y", "time-box this exploration", "what's the right architecture for this?", or "should we use A or B?". Produces a findings document and a concrete recommendation that feeds directly into write-epic or write-task.
---

# Spike

Run a time-boxed technical investigation. Core value: turns an unknown into a decision — produces concrete findings and a recommendation so the team can write specs confidently rather than guessing.

## Process

### 0. GitHub CLI setup

Run steps 1–2 of `../references/gh-setup.md` (install check and auth check). Stop if `gh` is not installed or not authenticated. Extensions are not required for this skill.

Skip this step if gh-setup was already confirmed this session.

### 1. Define the question

Apply `../references/questioning-style.md` for every question in this skill.

If the user described the investigation in their request, extract the core question from it. Otherwise ask "What question should this spike answer?" — header `Spike question`, options from specific questions inferred from any context provided (e.g. linked Epic, conversation).

The question must be specific and answerable — not "how does caching work?" but "is Redis or in-memory caching the right choice for our session store given our deployment constraints?" — and scoped to a decision the team actually needs to make.

Then ask "How much time should this spike take?" — header `Time box`:

- **1 hour** → quick feasibility check
- **Half day** → moderate investigation
- **1 day** → deep dive with proof of concept

### 2. Identify the linked issue (optional)

Ask "Is this spike linked to an existing issue?" — header `Linked issue`:

- Candidates from `gh issue list --label "epic,feature" --state open --limit 5`
- **No linked issue** — standalone investigation

If linked: fetch the issue to extract domain context, constraints, and success metrics that inform the investigation scope.

### 3. Research

Run all research in parallel using the Agent tool:

**Codebase exploration:**
- Search for existing implementations, prior attempts, or ADRs addressing the same question (domain nouns, patterns, imports)
- Load `docs/steering/TECH.md` per the **best-effort consumer-side load** in `../references/steering-doc-process.md` for constraints that rule out certain approaches
- Identify integration points and dependencies the solution must respect

**External research (if available):**
- Use WebSearch/WebFetch for relevant documentation, benchmarks, or known trade-offs

Synthesise findings internally. Do not dump raw research at the user.

### 4. Derive 2–3 concrete approaches

For each approach:

- **Name**: short label (e.g. "Redis session store", "In-memory with TTL")
- **Summary**: one sentence describing what it involves
- **Pros**: 2–3 concrete advantages relevant to this codebase and constraints
- **Cons**: 2–3 concrete risks or costs
- **Effort estimate**: rough implementation cost (hours or days)
- **Fit with TECH.md**: does it align with the established stack and patterns?

### 5. Recommend

State a single recommendation:

> "Recommend [Approach N] because [1–2 key reasons]. Main risk: [X], mitigated by [Y]."

If evidence is genuinely ambiguous or the spike revealed the question is harder than expected, say so clearly — recommend a proof of concept or a follow-up spike with a narrower question.

### 6. Review with user

Show the full analysis (approaches + recommendation). Then ask "Does this answer the question well enough to proceed?" — header `Spike review`:

- **Yes — record the findings** → write the spike doc
- **Need more depth on one approach** → explore a specific area further
- **Question changed** → the investigation revealed a different question

Apply any adjustments, then proceed.

### 7. Write the findings doc

Write to `docs/spikes/<YYYY-MM-DD>-<slug>.md` where `<slug>` is a 2–4 word kebab-case summary of the question (e.g. `session-store-strategy`).

Structure:

```markdown
# Spike: <question>

**Date:** <YYYY-MM-DD>  
**Time box:** <duration>  
**Linked issue:** #<n> or —

## Question

<the specific question this spike answered>

## Approaches considered

### <Approach 1 name>
**Summary:** ...  
**Pros:** ...  
**Cons:** ...  
**Effort:** ...  

### <Approach 2 name>
...

## Recommendation

<recommendation text>

## Decision

<!-- Fill when the team decides -->
- [ ] Accepted — proceeding with [approach]
- [ ] Rejected — reason: ...
- [ ] Needs follow-up: ...
```

```bash
mkdir -p docs/spikes
git add docs/spikes/<filename>
git commit -m "docs(spike): <question summary>"
```

Print the file path.

### 8. Post to linked issue (if applicable)

If a linked issue exists, post a comment:

```bash
gh issue comment <issue_number> --body "🔬 Spike concluded: **<question>** → Recommendation: <one-line summary>. Full findings: docs/spikes/<filename>.md"
```

### 9. Offer next steps

Ask "What's next?" — header `Next step`:

- **Write an Epic from this** → turn the recommendation into an Epic issue (default)
- **Write a Task from this** → the spike uncovered a specific narrow change
- **Stop here** → exit; the team will decide separately

- **Write an Epic** → follow the `wtf.write-epic` process, seeding it with the spike's recommendation and findings as context.
- **Write a Task** → follow the `wtf.write-task` process with the spike recommendation as the task description.
- **Stop here** → exit.
