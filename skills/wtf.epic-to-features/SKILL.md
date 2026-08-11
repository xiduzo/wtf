---
name: wtf.epic-to-features
description: This skill should be used when a user wants to decompose an Epic into its complete set of Features all at once, invoked automatically after write-epic completes, or triggered by phrases like "create all features for this epic", "walk me through all the features", "let's break down this epic", or "plan the features for epic #N". Use this skill for bulk Feature decomposition. Supports two planning modes — `guided` (one Feature at a time, with questions) and `flow` (draft the whole set in parallel, one consolidated review) — passed as an argument or read from `.wtf/config.json`. Use `wtf.write-feature` for creating a single Feature in isolation.
argument-hint: "[epic#] [guided|flow]"
---

# Epic to Features

Break an Epic down into its full set of Features. Propose the complete feature list first. Then the planning mode decides the cadence. In `guided` mode, write each Feature one by one with full user control. In `flow` mode, draft the whole set in parallel and review it once.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available. This determines whether native sub-issue and dependency links are created downstream (via `wtf.write-feature` and `wtf.write-task`).

Skip this step if gh-setup was already confirmed this session (e.g. when chained from `wtf.write-epic`).

### 0b. Resolve the planning mode

Run the **Resolve the mode** block from `../references/planning-mode.md`. An explicit `guided` or `flow` argument in the invocation wins over config. `$WTF_PLAN` selects step 3 (guided) or step 3F (flow). Steps 0–2 and 4 run in both modes.

### 1. Identify the Epic

If an Epic number was passed in as context, use it. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Epic are you breaking into Features?"
- header: "Epic"
- options: from recent open Epics. List them per the **List issues of a kind** query (kind `Epic`) in `../references/issue-classification.md`. Use `--label epic` in labels mode. Use `--search 'type:"Epic"'` in types mode.

Fetch the Epic with `gh issue view <epic_number>`. Extract Goal, Context, and Success Metrics.

List Features already created under this Epic via `gh sub-issue list <epic_number>` per the cookbook in `../references/gh-setup.md`. Note which Features already exist. Do not re-propose or re-create them.

### 2. Propose the full Feature list

From the Epic's Goal, Context, and Success Metrics, derive a proposed list of Features that together deliver the Epic's outcome. Each Feature must follow the pattern: **[Domain Actor] can [domain verb] [domain object]**.

If the Epic already has partially-created Features (found via `gh sub-issue list`), open the list with a note. Use this form: "Epic #N already has [X] Features created: [list with issue numbers]. Here are the remaining Features I'd propose:"

Present the remaining (or full, if none exist yet) list as plain numbered text, for example:

> Here are the Features I'd propose for this Epic:
>
> 1. Merchant can view settlement status for a completed payment
> 2. Merchant can filter settlements by date range
> 3. Finance Manager can export settlement report as CSV
> 4. System notifies Merchant when settlement is delayed

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this list look complete? You can add, remove, or rename any Feature before we start."
- header: "Feature list"
- options:
  - **Looks good** → proceed with this list
  - **Make changes** → add, remove, or rename a Feature

Wait for the user to confirm or adjust the list. Apply any changes.

This confirmation gate runs in **both** modes. It is cheap and it anchors everything downstream. In `flow` mode it is the first of exactly two user gates (the second is the consolidated review in step 3F).

Then branch on `$WTF_PLAN`: `guided` → step 3. `flow` → step 3F.

### 3. Process Features one by one (`guided` mode)

For each Feature in the confirmed list, in order:

1. Announce: "Creating Feature [N/total]: _[capability name]_"
2. Follow the `wtf.write-feature` process, passing:
   - The Epic number (skip step 1 of write-feature — Epic is already fetched)
   - The capability name as the pre-filled answer to step 2 of write-feature
   - **Abbreviated clarification**: the capability name already follows the `[Actor] can [verb] [object]` pattern and the Epic context is already in hand. Skip write-feature step 3 (clarification questions) unless something is genuinely ambiguous from the Epic. Write-feature step 4 (user story derivation) and step 5 (DDD Language Guard) should still run. Resume from write-feature step 6 (vertical slice assessment).
3. Before you move to the next Feature, call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Feature [N] created. Ready to continue to Feature [N+1]: _[next capability name]_?"
   - header: "Continue?"
   - options:
     - **Yes, continue** → proceed to the next Feature (default)
     - **Pause here** → exit. Print a summary of which Features were created and which remain. Suggest `/clear` before resuming
     - **Skip this feature** → mark as skipped in the list and move to the next
     - **Add a new feature** → call `AskUserQuestion` with question "What is the new feature capability?", header "New feature". Offer options from capability names inferred from the Epic's Goal or Success Metrics not yet in the list. Add the confirmed feature. Then continue

### 3F. Draft all Features, review once (`flow` mode)

Draft the full set in parallel. Create nothing until the user approves the batch. Follow `../references/subagent-protocol.md` throughout.

**3F.1 — Fan out drafting sub-agents.**

Read `skills/wtf.write-feature/SKILL.md` at runtime. Extract steps 3–9 (clarification through scope gate). Spawn one sub-agent per confirmed Feature, all in a single message so they run in parallel. Each prompt must contain:

- The inline write-feature step range under a heading "# Inline instructions — execute the steps below".
- An override section per the sub-agent protocol: no `AskUserQuestion`; unresolvable ambiguities and firing scope-gate signals return a `NEEDS_INPUT` block instead; skip step 8's per-item DoR interrogation and apply the `flow` waiver rule from write-feature step 8.
- The pre-known context: Epic number, Epic Goal / Context / Success Metrics, the capability name, the full confirmed feature list (for dependency detection in step 6), and any glossary terms found in step 1.
- The required return shape: the filled Feature body (template-complete, including the **Proposed Tasks** checklist from step 7b), the capability name, the dependency list (names of sibling Features this one depends on), and any `NEEDS_INPUT` block.

Sub-agents draft text only. They never create issues, never write files, and never touch `gh` beyond read-only queries.

**3F.2 — Resolve escalations.**

Collect all `NEEDS_INPUT` blocks. If any exist, group them and present them in a **single** `AskUserQuestion` round per `../references/planning-mode.md`. Re-dispatch only the affected sub-agents with the answers embedded. Scope-gate splits that the user accepts here update the feature list; dispatch drafting agents for the new slices.

**3F.3 — Consolidated review.**

Present the whole tree compactly — one block per Feature:

> **N. [capability name]**
> Stories: [one line per story, compressed] · ACs: [count] · Edge cases: [count]
> Proposed Tasks: [the checklist items, inline]
> Depends on: [sibling names, or —]

Note anything auto-waived or corrected (DoR waivers, DDD guard fixes). Offer any full body on request. Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "This is the full Feature set for Epic #N. Create all of them?"
- header: "Batch review"
- options:
  - **Create all** → proceed to 3F.4
  - **Edit first** → apply the user's changes to the affected drafts, re-show only those, then re-ask
  - **Drop some** → remove the named Features from the batch, then re-ask

**3F.4 — Batch create and link.**

For each approved Feature, in dependency order (blockers first), run write-feature steps 11 (create + classify + Epic sub-issue link) exactly as written. Reuse one Haiku sub-agent call to generate all titles at once. Record each capability name → issue number as you go. After all issues exist, create the dependency links from step 6's dependency lists using the recorded numbers. Skip write-feature steps 10 and 12 — the batch review replaced them.

If any creation or link fails, finish the rest, then report the failures with the exact commands to retry.

Then run the wiki / glossary update from write-feature step 11 once for the whole batch.

### 4. Completion

When all Features have been created (or skipped), print a summary:

> "Epic #<epic_number> Feature breakdown complete.
> Created: [list with issue numbers]
> Skipped: [list if any]"

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Break down first Feature** → follow `wtf.feature-to-tasks` with the first created Feature number (default)
  - **Break down next Feature** → follow `wtf.feature-to-tasks` with a different Feature number
  - **Stop here** → exit. No further action

> Suggest `/clear` before continuing if the conversation has grown long.
