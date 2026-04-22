---
name: wtf.feature-to-tasks
description: This skill should be used when a user wants to plan and create the complete set of Tasks for a Feature all at once, systematically walk through every implementable slice of work for a Feature, or create tasks in batch with step-by-step confirmation. Triggers on phrases like "plan all tasks for this feature", "create all tasks for feature #42", "what tasks do I need for this feature", "walk me through all the tasks", or when chained automatically from the epic-to-features skill. Use this skill for bulk Task creation; use `wtf.write-task` to write a single Task in isolation.
---

# Feature to Tasks

Break a Feature down into its full set of Tasks and create them one by one. Core value: proposes the complete task list upfront derived from the Feature's Acceptance Criteria, then walks through writing each Task with full user control.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available — this determines whether native sub-issue and dependency links are created downstream (via `wtf.write-task`).

Skip this step if gh-setup was already confirmed this session (e.g. when chained from `wtf.write-feature` or `wtf.epic-to-features`).

### 1. Identify the Feature

If a Feature number was passed in as context, use it directly. Otherwise search for recent open issues with label `feature` to populate options and call `AskUserQuestion` with `question: "Which Feature are you breaking into Tasks?"`, `header: "Feature"`, and `options` pre-filled with 1–2 likely open Feature issue references inferred from GitHub search (e.g. recent open issues labeled `feature`).

Fetch the Feature, then find its parent Epic via the sub-issue hierarchy:

```bash
gh issue view <feature_number>                                         # ACs, edge cases, user stories
gh sub-issue list <feature_number> --relation parent                   # find parent Epic number
gh issue view <epic_number>                                            # Goal, Context
```

Extract any existing Proposed Tasks checklist items (named, unnumbered items) from the Feature body. In Step 2, use these as the starting point for the proposal rather than generating from scratch.

List Features already created under the Epic — used in step 4 to identify the next Feature:

```bash
gh sub-issue list <epic_number>
```

### 2. Propose the full Task list

Based on the Feature's Acceptance Criteria, User Stories, and Edge Cases, derive a proposed list of Tasks. Each task should be a vertical slice — touching all layers needed for one observable, user-facing behavior.

Present the list as plain numbered text, for example:

> Here are the Tasks I'd propose to implement this Feature:
>
> 1. Add settlement status field to Payment Aggregate
> 2. Expose settlement status on the payments API endpoint
> 3. Display settlement status in the merchant dashboard UI
> 4. Send settlement notification email when status changes

Then call `AskUserQuestion` with:

- `question`: "Does this list look complete? You can add, remove, or rename any Task before we start."
- `header`: "Task list"
- `options`: `[{label: "Looks good", description: "Proceed with this list"}, {label: "Make changes", description: "I want to add, remove, or rename a Task"}]`

Wait for the user to confirm or adjust the list. Apply any changes.

### 3. Walk through Tasks one by one

For each Task in the confirmed list, in order:

1. Announce: "Creating Task [N/total]: _[task description]_"
2. Follow the `wtf.write-task` process, passing:
   - The Feature number (skip step 1 of write-task — Feature already fetched)
   - The task description as the pre-filled proposal in step 2 of write-task (user can confirm or adjust)
   - Skip write-task clarification questions already answered by the loaded Feature context (ACs, user stories, edge cases). Only ask about scope or contract details that cannot be derived from the Feature.
3. Before moving to the next Task, call `AskUserQuestion` with:
   - `question`: "Task [N] created. Ready to continue to Task [N+1]: _[next task description]_?" _(replace [N] and [N+1] with actual numbers and description)_
   - `header`: "Continue?"
   - `options`: `[{label: "Yes, continue", description: "Proceed to the next Task (default)"}, {label: "Pause here", description: "Exit — I'll continue later"}, {label: "Skip this task", description: "Mark as skipped and move on"}, {label: "Add a new task", description: "Insert a new task into the list before continuing"}]`

   - **Yes, continue** → continue.
   - **Pause here** → exit. Print a summary of which Tasks were created and which remain. Suggest `/clear` before resuming.
   - **Skip this task** → mark as skipped in the list and move to the next.
   - **Add a new task** → call `AskUserQuestion` with `question: "What is the new task?"`, `header: "New task"`, and `options` pre-filled with 1–2 plausible tasks inferred from the remaining Feature ACs not yet covered. Add the confirmed task to the list, then continue.

### 4. Completion

When all Tasks have been created (or skipped), print a summary:

> "Feature #<feature_number> Task breakdown complete.
> Created: [list with issue numbers]
> Skipped: [list if any]"

Then call `AskUserQuestion` with:

- `question`: "What's next?"
- `header`: "Next step"
- `options`: `[{label: "Implement first Task", description: "Start implementing the first created Task (default)"}, {label: "Tasks for next Feature", description: "Plan Tasks for the next Feature in the Epic"}, {label: "Stop here", description: "Exit — no further action"}]`

- **Implement first Task** → follow the `wtf.implement-task` process with the first created Task number.
- **Tasks for next Feature** → follow the `wtf.feature-to-tasks` process with the next Feature from the `gh sub-issue list` result fetched in step 1 that does not yet have child tasks.
- **Stop here** → exit.

> Suggest `/clear` before continuing if the conversation has grown long.
