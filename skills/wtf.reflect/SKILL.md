---
name: wtf.reflect
description: This skill should be used when a developer wants to capture learnings from a difficult session, record what Claude got wrong, save implementation gotchas, or update the steering docs with hard-won knowledge — for example "let's reflect", "capture what we learned", "that was painful, save this", "update the steering docs with what went wrong", "I need to debrief", "what went wrong today", "log this lesson", "save this gotcha", "document this mistake", "I want to write this down before I forget", "add this to the steering docs", or when prompted by the intervention tracker after multiple corrections. Routes each learning into the right steering doc (TECH, QA, DESIGN, or VISION) under a "Hard-Won Lessons" section.
---

# WTF Reflect

Capture learnings from this session and route them into the right steering document. Every hard-won insight — especially about where the AI went wrong or where implementation was harder than expected — belongs in a steering doc so it guides future work automatically.

**Intervention tracker:** The `hooks/track-interventions.sh` hook runs automatically on every `UserPromptSubmit` event and increments `/tmp/wtf.interventions-$(whoami)-$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")` when it detects correction or frustration language (e.g. "no,", "wrong", "actually", "stop that"). When the counter reaches 3, the hook prints a reminder at the end of the session to run `wtf.reflect`. Step 6 of this skill resets the counter to zero. No manual tracking is needed — the hook handles it.

## Process

### 1. Check which steering docs exist

```bash
ls docs/steering/ 2>/dev/null
```

Build a map of which of the four docs are present: `TECH.md`, `QA.md`, `DESIGN.md`, `VISION.md`.

**If none exist**, ask "No steering docs found. Would you like to create them first?" — header `No steering docs`:

- **Create them now** → run the `steer-*` skills to set up the docs
- **Skip — just capture notes** → save all learnings to `docs/steering/LEARNINGS.md` instead

If **Create them now** → invoke `wtf.steer-tech`. Note that `wtf.steer-tech` will offer to chain to the other steer-\* skills at the end — let the user complete that flow, then return here. When control returns, re-run the `ls` check to see which docs now exist.
If **Skip** → set all four doc paths to the fallback: `docs/steering/LEARNINGS.md`.

**If some exist but not all** → continue. In step 4, route learnings for a missing doc to `docs/steering/LEARNINGS.md` as a per-doc fallback (create the file if needed).

### 2. Orient to the session

Briefly scan context to understand what was worked on:

- Recent git commits: `git log --oneline -10`
- Any failing/passing tests, PRs, or issues mentioned in conversation
- Do NOT dump this at the user — use it only to pre-fill questions.

### 3. Gather learnings

Apply `../references/questioning-style.md` for every question.

**Q1 — What was harder than expected?**

Ask "What was harder or more painful than it should have been in this session?" — header `Session friction`:

- 2–3 inferred options based on what was worked on (e.g. "Debugging X took too long", "Claude kept misunderstanding Y")
- **Nothing — skip** — session went smoothly

If **Nothing — skip** → skip to step 6 (reset counter) and exit with: "Great session — nothing to capture."

**Q2 — Did Claude make a recurring mistake?**

Ask "Did Claude keep making the same mistake you had to correct?" — header `AI mistakes`:

- **Yes — describe it** → tell me what it kept doing
- **No recurring mistakes** → one-off issues only

If **Yes** → ask "Describe the mistake briefly. What rule would prevent it next time?" — header `AI mistake — the rule`:

- **Skip** — hard to articulate right now

**Q3 — What is the one rule this session taught you?**

Ask "If you had to write one rule that would have prevented the most wasted time today, what would it be?" — header `The lesson`:

- 1–2 rules inferred from the session
- **Skip this one** — nothing to add

### 4. Route each learning to the right steering doc

For each learning gathered, determine where it belongs:

| Learning type                                                  | Target doc          |
| -------------------------------------------------------------- | ------------------- |
| Architecture pattern, implementation gotcha, AI coding mistake | `TECH.md`           |
| Test failure pattern, flaky test cause, QA gap                 | `QA.md`             |
| Design inconsistency, component misuse, style mistake          | `DESIGN.md`         |
| Scope confusion, priority conflict, domain language drift      | `VISION.md`         |
| Doesn't clearly fit one doc                                    | `TECH.md` (default) |

For each target doc:

1. If the target doc does not exist (from the map built in step 1) → use `docs/steering/LEARNINGS.md` instead. Create it with a `# Overflow Learnings` heading if it doesn't exist yet.
2. Read the current file.
3. Look for a `## Hard-Won Lessons` section.
4. If it exists → append the new bullet(s) under it.
5. If it does not exist → append the section at the end of the file, inserting it **before** the `<!-- MANUAL ADDITIONS START -->` marker if present.

**Bullet format:**

```
- **[Short label]** — [Concrete rule or observation]. *Learned [YYYY-MM-DD].*
```

Example:

```
- **Don't mock the auth middleware in tests** — Three tests passed with mocks but failed in CI against the real service. Always integrate against real dependencies. *Learned 2026-03-24.*
```

### 5. Write the updated steering docs

Write each modified doc. Then commit using today's date:

```bash
git add docs/steering/
git commit -m "docs(steering): add hard-won lessons from $(date +%Y-%m-%d) session"
```

### 6. Reset the intervention counter

```bash
echo "0" > /tmp/wtf.interventions-$(whoami)-$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")
```

### 7. Close the loop

Print a brief summary:

- Which docs were updated
- How many learnings were captured
- Remind the user: "These rules will guide every future session automatically."
