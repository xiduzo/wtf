---
name: ste-writing
description: Rewrite prose into ASD-STE100 Simplified Technical English to remove AI slop. Use when asked to make docs plain, make writing not sound like AI, or enforce a controlled writing style.
sources:
  - https://raw.githubusercontent.com/woosal1337/blog/main/videos/ep01-the-cure-for-ai-slop/ste-writing-skill.md
generated_by: url-to-skill
---

# STE Writing

## Overview

Write prose in ASD-STE100 Simplified Technical English. STE is a controlled
language: one word per meaning, active voice, short sentences. It removes the
form of "AI slop" — the padding, hedging, and marketing adjectives that mark
generated text.

STE strips voice on purpose. That is the point for technical text and the
reason to keep it away from anything that needs a voice.

## When to use

Use it for: documentation, READMEs, pull-request text, error messages, release
notes, comments.

Do NOT use it for:

- Code, identifiers, or command syntax.
- Marketing copy, essays, or anything that needs a voice.

## Key patterns

### Modes

- **strict** — procedures, runbooks, safety text, error messages. Apply every
  rule and both length caps.
- **STE-flavored** — general prose (READMEs, PR descriptions, docs). Apply the
  sentence, paragraph, active-voice, and no-phrasal-verb discipline. Relax the
  875-word dictionary lockdown so the text keeps enough range to read
  naturally.

Both modes keep the structural rules. Only the dictionary lockdown relaxes.

In strict mode, check words against
[`references/dictionary.md`](references/dictionary.md) instead of guessing.
Grep the not-approved table first, then the approved list.

### Words

- Use one name for one thing. Do not call the same item by two different names.
  (Rule 1.11)
- Use the short common word: start (not begin/commence/initiate), use (not
  utilize/leverage), help (not facilitate), make sure (not ensure), before (not
  prior to), after (not subsequent to), about (not regarding/concerning), get
  (not obtain/acquire), show (not demonstrate), also (not
  additionally/furthermore/moreover).
- Give each word one meaning. "fall" means to move down, not to decrease.
  (Rule 1.3)
- Use each approved word only as its listed part of speech. Do not verb a noun
  or nominalize a verb. (Rules 1.2, 1.7, 1.13)
- No marketing adjectives: seamless, robust, powerful, cutting-edge,
  effortless, world-class, next-generation, revolutionary.
- American spelling. (Rule 1.14)
- Domain terminology enters through the technical noun and technical verb
  categories, not by relaxing the dictionary. Pick a short term, keep it
  consistent, and no slang or jargon. (Rules 1.5–1.12)

### Multi-word nouns

- Maximum three words in a multi-word noun. (Rule 2.1)
- The head noun is the last word. Every modifier in front of it is another
  connection the reader must guess. "runway light connection resistance
  calibration" makes the reader hold four modifiers before the head noun.
- When a technical name is longer than three words, write it in full rather
  than clipping it. (Rule 2.2)

### Verbs

- Active voice. "the parser reads the file", not "the file is read by the
  parser". In descriptive text, the passive voice is allowed only when the
  agent is unknown. In procedures it is never allowed. (Rule 3.6)
- Use only these forms and tenses: infinitive, imperative, simple present,
  simple past, simple future, and past participle as an adjective. (Rule 3.2)
- Not approved: present perfect ("has parsed"), past perfect ("had parsed"),
  progressive ("is parsing"), and every other complex construction. (Rule 3.4)
- Use a verb for an action. "analyze the log", not "perform an analysis of the
  log". (Rule 3.7)
- No stacked auxiliaries. Not "it is important to note that this may help to
  improve". Write "this improves X".
- Use "-ing" only as a technical noun or as a modifier inside a technical name.
  (Rule 3.5)
- No phrasal verbs. Both halves can be approved words while the pair is not:
  "spin up" → "start", "give off" → "release", "put out" → "extinguish".
  (Rule 9.3)

### Sentences and punctuation

- One instruction per sentence, unless two actions happen at the same time.
  (Rule 5.2)
- Max 20 words for an instruction, max 25 for a descriptive sentence.
  (Rules 5.1, 6.3)
- No contractions, and do not drop words to hit the word cap. Split the
  sentence instead. (Rule 4.2)
- Keep articles and demonstratives: "Turn the shaft assembly", not "Turn shaft
  assembly". (Rule 4.5)
- No semicolons. Write two sentences instead. The semicolon is the only banned
  mark. The em dash is not banned by STE. Add "no em dash" yourself if you want
  it gone. (Rule 8.1)
- Connect related sentences with approved connectors: and, but, then, thus, as
  a result, at the same time. (Rule 4.4)
- Word count: text in parentheses counts as one word. So do numbers,
  numbers with units, abbreviations, alphanumeric identifiers, quoted text,
  headings and labels, and proper nouns. Hyphenated words count as one.
  (Rules 8.5–8.7)

### Structure

- One topic per paragraph, max six sentences. (Rules 6.5, 6.6)
- Give information gradually and lead with key words. (Rules 6.1, 6.2)
- For steps, use a numbered vertical list, one action per item, imperative
  form. (Rules 4.3, 5.3)
- Put a condition before its command. (Rule 5.4)
- Notes give information only. Never put an instruction in a note. (Rule 5.5)
- Write only the requested text. No preamble, no summary, no closing remarks.

### Warnings and cautions

Applies to error messages, destructive-command prompts, and migration notes.

1. Label the level of risk. Injury or death → **warning**. Damage to equipment
   or data → **caution**. Both → **warning**. (Rule 7.1)
2. Start with the command or the condition, not with the explanation.
   (Rule 7.2)
3. Then state the risk or the result. (Rule 7.3)

"CAUTION: EXTREME CLEANLINESS OF OXYGEN TUBES IS IMPERATIVE" fails all three.
"WARNING: MAKE SURE THAT THE OXYGEN TUBES ARE FULLY CLEAN. OXYGEN AND GREASE
MAKE AN EXPLOSIVE MIXTURE. AN EXPLOSION CAN CAUSE INJURY OR DEATH." passes.

STE gives no formatting rules. Uppercase is a convention of the standard's
examples, not a requirement.

### Self-lint

Run this before you return text:

1. Any sentence over 20 words? Split it.
2. Any semicolon? Replace it with a period.
3. Any contraction? Expand it.
4. Any passive voice with a known actor? Make it active.
5. Any "-ing" main verb, nominalization ("perform an analysis"), or phrasal
   verb ("spin up")? Replace it with a plain verb.
6. Same thing named two ways? Pick one name.
7. Any multi-word noun over three words? Break it up or write the full
   technical name.
8. Any compound tense (has done, had done, is doing)? Use a simple tense.
9. Any dropped article ("Run command")? Put it back ("Run the command").
10. Any paragraph over six sentences, or covering two topics? Split it.
11. Any note that gives an instruction? Move it into a work step.
12. Any warning or caution that opens with the explanation instead of the
    command? Reorder it: command first, risk second.
13. Strict mode only: grep each content word against
    [`references/dictionary.md`](references/dictionary.md). Replace anything in
    the not-approved table with its listed alternative.

## Pitfalls

- **Applying STE to code.** The rules cover prose only. Leave identifiers,
  command syntax, and code samples alone.
- **Applying STE to copy that needs a voice.** Marketing text and essays lose
  their point when STE flattens them.
- **Expecting form to fix substance.** The mechanical rules are lintable and
  they remove the form of slop. Full STE also needs human judgment: the right
  technical noun, whether a sentence makes good sense. A checker cannot certify
  that. This skill cannot make a hollow paragraph true.
- **Pasting the standard.** The official standard is free to read but
  copyrighted. Do not paste it in full. The bundled rule index carries rule
  numbers and short statements only.
- **Treating STE-flavored as "the rules are optional".** Only the dictionary
  relaxes. Sentence caps, active voice, multi-word noun limits, and the
  paragraph rules still apply.
- **Chasing the word cap by deleting words.** Rule 4.2 forbids dropping
  articles or using contractions to fit the limit. Split the sentence.
- **Reading a word's absence as approval.** The dictionary is an aerospace
  vocabulary. Software words such as "leverage", "robust", and "seamless" are
  in neither list. They are still slop. The marketing-adjective rule and the
  short-common-word rule catch them, not the dictionary.
- **Loading the dictionary into context.** It is 69 KB and 2300 lines. Grep the
  words you need.
- **Skipping the self-lint.** The six checks are what catch the residue after a
  first pass.

## Reference

- Full rule index (all 63 rules, by section):
  [`references/asd-ste100-rules.md`](references/asd-ste100-rules.md).
- Word lists and substitutions:
  [`references/dictionary.md`](references/dictionary.md). Grep it for a word.
  Do not read it whole — it is 69 KB.

| Item | Value |
|------|-------|
| Standard | ASD-STE100 Simplified Technical English, Issue 9 (2025-01-15) |
| Official standard (free, copyrighted) | https://asd-ste100.org |
| Modes | `strict`, `STE-flavored` |
| Part 1 | 9 sections, 63 writing rules |
| Part 2 | dictionary: 875 approved words, 1274 not-approved with alternatives |
| Max instruction sentence | 20 words (Rule 5.1) |
| Max descriptive sentence | 25 words (Rule 6.3) |
| Max words in a multi-word noun | 3 (Rule 2.1) |
| Max sentences per paragraph | 6 (Rule 6.6) |
| Approved tenses | infinitive, imperative, simple present/past/future, past participle as adjective (Rule 3.2) |
| Banned punctuation | semicolon only (Rule 8.1) |
| Not banned | em dash |
| Passive voice | descriptive text only, and only when the agent is unknown (Rule 3.6) |
| Risk labels | warning (injury/death), caution (equipment damage) (Rule 7.1) |
| Spelling | American (Rule 1.14) |
| Applies to | docs, READMEs, PR text, error messages, release notes, comments |
| Does not apply to | code, identifiers, command syntax, marketing copy, essays |
| Self-lint checks | 12 |
