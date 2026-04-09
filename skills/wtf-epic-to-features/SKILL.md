---
name: wtf:epic-to-features
description: This skill should be used when a user wants to decompose an Epic into its complete set of Features all at once, invoked automatically after write-epic completes, or triggered by phrases like "create all features for this epic", "walk me through all the features", "let's break down this epic", or "plan the features for epic #N". Use this skill for bulk Feature decomposition; use wtf:write-feature for creating a single Feature in isolation.
---

# Epic to Features

Break an Epic down into its full set of Features and create them one by one. Core value: proposes the complete feature list upfront, then walks through writing each Feature with full user control.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native sub-issue and dependency links are created downstream (via `wtf:write-feature` and `wtf:write-task`).

Skip this step if gh-setup was already confirmed this session (e.g. when chained from `wtf:write-epic`).

### 1. Identify the Epic

If an Epic number was passed in as context, use it directly. Otherwise call `AskUserQuestion` with `question: "Which Epic are you breaking into Features?"`, `header: "Epic"`, and `options` pre-filled with recent open Epic issue numbers and titles found via `gh issue list --label epic`.

Fetch the Epic:

```bash
gh issue view <epic_number>
```

Extract: Goal, Context, and Success Metrics.

List Features already created under this Epic using the sub-issue hierarchy:

```bash
gh sub-issue list <epic_number>
```

Note which Features already exist. Do not re-propose or re-create them.

### 2. Propose the full Feature list

Based on the Epic's Goal, Context, and Success Metrics, derive a proposed list of Features that together deliver the Epic's outcome. Each Feature must follow the pattern: **[Domain Actor] can [domain verb] [domain object]**.

If the Epic already has partially-created Features (found via `gh sub-issue list`), open the list with a note: "Epic #N already has [X] Features created: [list with issue numbers]. Here are the remaining Features I'd propose:"

Present the remaining (or full, if none exist yet) list as plain numbered text, for example:

> Here are the Features I'd propose for this Epic:
>
> 1. Merchant can view settlement status for a completed payment
> 2. Merchant can filter settlements by date range
> 3. Finance Manager can export settlement report as CSV
> 4. System notifies Merchant when settlement is delayed

Then call `AskUserQuestion` with:

- `question`: "Does this list look complete? You can add, remove, or rename any Feature before we start."
- `header`: "Feature list"
- `options`: `[{label: "Looks good", description: "Proceed with this list"}, {label: "Make changes", description: "I want to add, remove, or rename a Feature"}]`

Wait for the user to confirm or adjust the list. Apply any changes.

### 3. Walk through Features one by one

For each Feature in the confirmed list, in order:

1. Announce: "Creating Feature [N/total]: _[capability name]_"
2. Follow the `wtf:write-feature` process, passing:
   - The Epic number (skip step 1 of write-feature — Epic is already fetched)
   - The capability name as the pre-filled answer to step 2 of write-feature
   - **Abbreviated clarification**: because the capability name already follows the `[Actor] can [verb] [object]` pattern and the Epic context is already in hand, skip write-feature step 3 (clarification questions) unless something is genuinely ambiguous from the Epic. Write-feature step 4 (user story derivation) and step 5 (DDD Language Guard) should still run silently. Resume from write-feature step 6 (vertical slice assessment).
3. Before moving to the next Feature, call `AskUserQuestion` with:
   - `question`: "Feature [N] created. Ready to continue to Feature [N+1]: _[next capability name]_?"
   - `header`: "Continue?"
   - `options`: `[{label: "Yes, continue", description: "Proceed to the next Feature (default)"}, {label: "Pause here", description: "Exit — I'll continue later"}, {label: "Skip this feature", description: "Mark as skipped and move on"}, {label: "Add a new feature", description: "Insert a new feature into the list before continuing"}]`

   - **Yes, continue** → continue.
   - **Pause here** → exit. Print a summary of which Features were created and which remain. Suggest `/clear` before resuming.
   - **Skip this feature** → mark as skipped in the list and move to the next.
   - **Add a new feature** → call `AskUserQuestion` with `question: "What is the new feature capability?"`, `header: "New feature"`, and `options` pre-filled with 1–2 capability names inferred from the Epic's Goal or Success Metrics not yet represented in the list. Add the confirmed feature to the list, then continue.

### 4. Completion

When all Features have been created (or skipped), print a summary:

> "Epic #<epic_number> Feature breakdown complete.
> Created: [list with issue numbers]
> Skipped: [list if any]"

Then call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Break down first Feature", description: "Plan and create Tasks for the first Feature (default)"}, {label: "Break down next Feature", description: "Plan and create Tasks for a different Feature"}, {label: "Stop here", description: "Exit — no further action"}]`

- **Break down first Feature** → follow the `wtf:feature-to-tasks` process with the first created Feature number.
- **Break down next Feature** → follow the `wtf:feature-to-tasks` process with the second created Feature number (or whichever the user specifies).
- **Stop here** → exit.

> Suggest `/clear` before continuing if the conversation has grown long.
