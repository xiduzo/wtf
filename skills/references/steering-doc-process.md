# Steering Document Process

Shared procedure for every `wtf.steer-*` skill (`steer-vision`, `steer-tech`, `steer-design`, `steer-qa`). Each skill inherits this structure; only the doc name, research checklist, gap-topic list, and template vary.

Every steering doc lives at `docs/steering/<NAME>.md`. The docs are treated as living — generated once from research + interview, then refined, never regenerated from scratch.

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
