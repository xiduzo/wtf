---
name: STE Writing
description: Strict ASD-STE100 Simplified Technical English for every durable WTF artifact. Extends the STE dictionary with the repo DDD glossary as TN/TV allowlist.
---

# STE Writing (strict)

Apply these rules before you write any **durable** artifact: issue bodies, PR bodies, review comments, release notes, changelog entries, steering docs, spike docs, and commit-message subject/body prose.

Do **not** apply STE to live chat replies or `AskUserQuestion` prompts (see `questioning-style.md`).

## Copyright

ASD-STE100 is free to read and copyrighted ([asd-ste100.org](https://asd-ste100.org)). Do not paste the standard in full. Do not copy or vendor the STE dictionary into this repo. Resolve the dictionary from the installed global `ste-writing` skill (see below).

## Mode

Always **strict**: structural rules **and** dictionary grep. Do not silently fall back to STE-flavored mode.

## Resolve the STE dictionary

Grep — do not read whole — this file (first path that exists):

1. `~/.claude/skills/ste-writing/references/dictionary.md`
2. `~/.cursor/skills/ste-writing/references/dictionary.md`
3. Any other installed `ste-writing` skill path the runtime exposes whose `references/dictionary.md` exists

If **no** dictionary file is found: **halt** durable writing. Tell the user to install the `ste-writing` skill (so its `references/dictionary.md` is available), then retry. Do not draft the durable body without the dictionary.

Header of that file says "Do not redistribute" — leave it in place; only grep it.

## Build the DDD allowlist (session set)

Domain terms enter STE as technical nouns (TN) and technical verbs (TV). Build the allowlist **before** drafting:

1. If `docs/glossary.md` exists, read it. Prefer the greppable term list (see **Glossary shape** below). Add every listed term.
2. If `docs/steering/VISION.md` exists, extract Target Users (actors) and Bounded Contexts (context names, key domain objects). Add them.
3. If the skill has a parent Epic / Feature / Task in hierarchy, extract named actors, domain verbs, and domain objects from those bodies. Add them.
4. If a Bounded Context wiki page or other in-repo glossary was already fetched for this skill, add its terms.
5. Merge into one session set. One name per thing (Rule 1.11) — if two aliases appear, pick the glossary form and use only that.

### Glossary shape (`docs/glossary.md`)

When creating or updating the glossary, keep a flat greppable list so allowlist extraction is reliable:

```markdown
## STE allowlist

| Term | Kind | Meaning | Source |
|------|------|---------|--------|
| Merchant | actor | ... | Epic #12 |
| settle | verb | ... | Epic #12 |
| Settlement | object | ... | Epic #12 |
```

Kinds: `actor` | `verb` | `object` | `context` | `event`. Add rows under that table; do not bury terms only in prose paragraphs.

## Word approval order

For each content word in durable prose:

1. **Out of scope** — leave as-is: code fences, identifiers, command syntax, Gherkin keywords (`Given`/`When`/`Then`/`And`/`But`/`Scenario`/`Feature`/`Background`), issue numbers, URLs, file paths, conventional-commit type/scope prefixes (`feat:`, `fix(auth):`).
2. **DDD allowlist** → allowed as TN/TV. Keep one name and one meaning.
3. Else grep **Not approved** in the STE dictionary → replace with a listed alternative.
4. Else grep **Approved** → use only the listed part of speech and meaning.
5. Else **reject or rephrase**. Do not invent marketing or slop words as TN/TV. Add a true new domain term to the glossary first, then use it.

## DDD vs STE

- **DDD** (`ddd-writing-rules.md`) chooses *which* domain term (actor, verb, object, event).
- **STE** (this file) governs sentence mechanics and every non-domain word.
- Domain terms from DDD feed the allowlist; they do not relax sentence caps, voice, or tense rules.

## Structural rules (always)

### Words

- One name for one thing. (Rule 1.11)
- Prefer short common words: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), make sure (not ensure), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- One meaning per word. (Rule 1.3)
- Use each approved word only as its listed part of speech. Do not verb a noun or nominalize a verb. (Rules 1.2, 1.7, 1.13)
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- American spelling. (Rule 1.14)

### Multi-word nouns

- Maximum three words in a multi-word noun. (Rule 2.1)
- If a technical name is longer than three words, write it in full rather than clipping it. (Rule 2.2)

### Verbs

- Active voice. Passive only in descriptive text when the agent is unknown. Never in procedures. (Rule 3.6)
- Approved forms only: infinitive, imperative, simple present, simple past, simple future, past participle as adjective. (Rule 3.2)
- Not approved: present perfect, past perfect, progressive, other complex constructions. (Rule 3.4)
- Use a verb for an action ("analyze the log", not "perform an analysis of the log"). (Rule 3.7)
- No stacked auxiliaries. No phrasal verbs ("spin up" → "start"). (Rule 9.3)
- Use "-ing" only as a technical noun or as a modifier inside a technical name. (Rule 3.5)

### Sentences and punctuation

- One instruction per sentence, unless two actions happen at the same time. (Rule 5.2)
- Max 20 words for an instruction, max 25 for a descriptive sentence. (Rules 5.1, 6.3)
- No contractions. Do not drop articles to hit the word cap — split the sentence. (Rules 4.2, 4.5)
- No semicolons. Write two sentences instead. (Rule 8.1)
- Connect related sentences with: and, but, then, thus, as a result, at the same time. (Rule 4.4)

### Structure

- One topic per paragraph, max six sentences. (Rules 6.5, 6.6)
- Lead with key words. Give information gradually. (Rules 6.1, 6.2)
- Numbered vertical lists for steps: one action per item, imperative. (Rules 4.3, 5.3)
- Condition before command. (Rule 5.4)
- Notes give information only — never an instruction. (Rule 5.5)

### Warnings and cautions

For error messages, destructive prompts, migration notes:

1. Injury/death → **warning**. Equipment/data damage → **caution**. Both → **warning**. (Rule 7.1)
2. Start with the command or the condition. (Rule 7.2)
3. Then state the risk or the result. (Rule 7.3)

## Commit messages and PR titles

Keep Conventional Commits structure (`commit-conventions.md`). Apply STE only to the free-text description and optional body — not to the `type`, optional `(scope)`, or `!`.

## Self-lint (before write)

1. Any sentence over 20 words (instruction) or 25 (descriptive)? Split it.
2. Any semicolon? Replace it with a period.
3. Any contraction? Expand it.
4. Any passive voice with a known actor? Make it active.
5. Any "-ing" main verb, nominalization, or phrasal verb? Replace it with a plain verb.
6. Same thing named two ways? Pick one name (prefer glossary form).
7. Any multi-word noun over three words? Break it up or write the full technical name.
8. Any compound tense? Use a simple tense.
9. Any dropped article? Put it back.
10. Any paragraph over six sentences, or covering two topics? Split it.
11. Any note that gives an instruction? Move it into a work step.
12. Any warning or caution that opens with the explanation? Reorder: command first, risk second.
13. Grep each content word against the STE dictionary (Not approved first, then Approved). Replace not-approved words with listed alternatives.
14. Every remaining content word is in Approved **or** the DDD allowlist (as TN/TV). If not, rephrase or add the domain term to the glossary first.

## Reference

| Item | Value |
|------|-------|
| Standard | ASD-STE100 Issue 9 (2025-01-15) |
| Global skill | `ste-writing` (dictionary + full rule index) |
| Max instruction sentence | 20 words |
| Max descriptive sentence | 25 words |
| Max words in a multi-word noun | 3 |
| Max sentences per paragraph | 6 |
| Banned punctuation | semicolon |
| Applies to | durable artifacts only |
| Does not apply to | chat, AskUserQuestion, code, identifiers, command syntax |
