# Steering Document Process

Shared procedure for every `wtf.steer-*` skill (`steer-vision`, `steer-tech`, `steer-design`, `steer-qa`). Each skill inherits this structure; only the doc name, research checklist, gap-topic list, and template vary.

Every steering doc lives at `docs/steering/<NAME>.md`. The docs are treated as living — generated once from research + interview, then refined, never regenerated from scratch.

## Consumer-side load

Any non-steer skill that needs steering context follows this single procedure. Skills citing it: `wtf.design-feature`, `wtf.design-task`, `wtf.implement-task`, `wtf.hotfix`, `wtf.pr-review`, `wtf.spike`, `wtf.verify-task`, `wtf.retro`, `wtf.reflect`.

1. Use the Read tool to attempt reading `docs/steering/<DOC>.md` (one of `TECH.md`, `QA.md`, `DESIGN.md`, `VISION.md`).
2. If it **exists** → keep its content in context and apply it silently throughout the session. Do not surface it to the user.
3. If it **does not exist**, choose the appropriate behavior for the skill:
   - **Strict consumer** (skill cannot do its job without the doc — e.g. `wtf.design-task`, `wtf.design-feature`, `wtf.implement-task`, `wtf.verify-task`): apply `./questioning-style.md` and ask "`docs/steering/<DOC>.md` doesn't exist yet. <one-line description of what the doc captures>. Would you like to create it now?" — header `<Doc> steering doc missing`:
     - **Create it now** → invoke the matching `wtf.steer-<doc>` skill (recommended), then return and continue
     - **Skip for this session** → continue without it; decisions won't reference project standards
   - **Best-effort consumer** (skill can degrade gracefully — e.g. `wtf.hotfix`, `wtf.pr-review`, `wtf.spike`): silently continue without it. Note in any output if the doc would have changed the recommendation.

| Skill | Doc(s) consumed | Mode |
|---|---|---|
| `wtf.implement-task` | `TECH.md`, `QA.md` (coverage threshold) | strict for TECH, soft default for QA |
| `wtf.design-task` | `DESIGN.md` | strict |
| `wtf.design-feature` | `DESIGN.md` | strict |
| `wtf.verify-task` | `QA.md` | strict |
| `wtf.pr-review` | `TECH.md` | best-effort |
| `wtf.hotfix` | `TECH.md` | best-effort |
| `wtf.spike` | `TECH.md` | best-effort |
| `wtf.retro` | `TECH.md`, `QA.md`, `DESIGN.md`, `VISION.md` | best-effort, route deltas |
| `wtf.reflect` | all four (writes back) | producer — see "Hard-Won Lessons" below |

## Hard-Won Lessons (writer-side, for `wtf.reflect`)

`wtf.reflect` writes session learnings into the consuming docs under a `## Hard-Won Lessons` section. The bullet format and routing rules live in `wtf.reflect` itself — the steering docs accept the appended bullets without further structure changes.

## Step 1. Check if the document already exists

Use the Read tool to attempt reading `docs/steering/<DOC>.md`.

If the file **exists**, ask "docs/steering/<DOC>.md already exists. What would you like to do?" — header `<Doc> found`:

- **Refine it** → read the current doc, then skip to step 4 (use the existing doc as context; only ask about gaps or outdated sections).
- **Exit** → leave it as-is and exit immediately.

If the file does not exist, continue to step 2.

## Step 2. Research the codebase

Use the Agent tool to extract facts directly from the codebase. Do not ask the user for things that can be read. Each `steer-*` skill owns its own research checklist — see the skill's SKILL.md.

Synthesise findings internally. Produce a concrete draft of the factual sections from research alone where possible.

## Step 3. Interview the user for gaps only

Apply `./questioning-style.md` for every question. Each `steer-*` skill defines its own gap-topic list.

## Step 4. Draft the document

Using the skill's reference template as the shape, fill in all sections with gathered context. Replace every `[PLACEHOLDER]` with real content. Apply the skill's own writing rules.

## Step 5. Review with user

Show the draft. Ask "Does this accurately reflect <the focus>?" — header `Review`:

- **Looks good — save it** → write to `docs/steering/<DOC>.md`
- **I have changes** → adjust first

Apply edits, then proceed.

## Step 6. Write and commit

```bash
mkdir -p docs/steering
# Write the final content to docs/steering/<DOC>.md
git add docs/steering/<DOC>.md
git commit -m "docs: add <subject> steering document"
```

Print the file path.

## Step 7. Offer wiki sync

Ask "Would you like to sync this to the GitHub wiki?" — header `Wiki sync`:

- **Yes — push to wiki** → publish `<DOC>.md` as a wiki page
- **Not now** → skip wiki sync

If **yes**:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
WIKI_DIR=$(mktemp -d -t wtf.wiki-sync-<slug>-XXXXXX)
git clone "https://github.com/$REPO.wiki.git" "$WIKI_DIR"
cp "docs/steering/<DOC>.md" "$WIKI_DIR/WTF-<Subject>.md"
(cd "$WIKI_DIR" && git add "WTF-<Subject>.md" && git commit -m "Sync: <subject>" && git push)
rm -rf "$WIKI_DIR"
```

Substitute `<slug>` with a lowercase word matching the doc (e.g. `tech`, `design`, `qa`, `vision`) and `<Subject>` with the capitalized display name.

## Step 8. Offer to continue

Ask "Continue with another steering doc?" — header `Next steering doc`:

- One option per remaining `steer-*` skill not yet created (excluding this skill) → run that skill
- **Stop here** → exit, no further action
