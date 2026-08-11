---
name: wtf.feature-to-tasks
description: This skill should be used when a user wants to plan and create the complete set of Tasks for a Feature all at once, systematically walk through every implementable slice of work for a Feature, or create tasks in batch with step-by-step confirmation. Triggers on phrases like "plan all tasks for this feature", "create all tasks for feature #42", "what tasks do I need for this feature", "walk me through all the tasks", or when chained automatically from the epic-to-features skill. Use this skill for bulk Task creation. Use `wtf.write-task` to write a single Task in isolation.
---

# Feature to Tasks

Break a Feature down into its full set of Tasks. Create them one by one. Propose the complete task list first from the Feature's Acceptance Criteria. Then write each Task with full user control.

## Process

### 0. GitHub CLI setup

Run the setup check from `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated. Note whether the extensions are available. This determines whether native sub-issue and dependency links are created downstream (via `wtf.write-task`).

Skip this step if gh-setup was already confirmed this session (e.g. when chained from `wtf.write-feature` or `wtf.epic-to-features`).

### 1. Identify the Feature

If a Feature number was passed in as context, use it. Otherwise call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Which Feature are you breaking into Tasks?"
- header: "Feature"
- options: from recent open issues labeled `feature`

Walk Feature → Epic per `../references/spec-hierarchy.md`. Extract ACs, edge cases, and user stories from the Feature. Extract Goal and Context from the Epic.

Extract any existing Proposed Tasks checklist items (named, unnumbered items) from the Feature body. In Step 2, use these as the starting point for the proposal. Do not generate from scratch when they exist.

List Features already created under the Epic via `gh sub-issue list <epic_number>` per the cookbook in `../references/gh-setup.md`. Use this list in step 4 to identify the next Feature.

### 2. Propose the full Task list

From the Feature's Acceptance Criteria, User Stories, and Edge Cases, derive a proposed list of Tasks. Each task should be a vertical slice. It should touch all layers needed for one observable, user-facing behavior.

Present the list as plain numbered text, for example:

> Here are the Tasks I'd propose to implement this Feature:
>
> 1. Add settlement status field to Payment Aggregate
> 2. Expose settlement status on the payments API endpoint
> 3. Display settlement status in the merchant dashboard UI
> 4. Send settlement notification email when status changes

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Does this list look complete? You can add, remove, or rename any Task before we start."
- header: "Task list"
- options:
  - **Looks good** → proceed with this list
  - **Make changes** → add, remove, or rename a Task

Wait for the user to confirm or adjust the list. Apply any changes.

### 3. Process Tasks one by one

For each Task in the confirmed list, in order:

1. Announce: "Creating Task [N/total]: _[task description]_"
2. Follow the `wtf.write-task` process, passing:
   - The Feature number (skip step 1 of write-task — Feature already fetched)
   - The task description as the pre-filled proposal in step 2 of write-task (user can confirm or adjust)
   - Skip write-task clarification questions already answered by the loaded Feature context (ACs, user stories, edge cases). Only ask about scope or contract details that you cannot derive from the Feature.
3. Before you move to the next Task, call `AskUserQuestion` (per `../references/questioning-style.md`):
   - question: "Task [N] created. Ready to continue to Task [N+1]: _[next task description]_?" (replace [N]/[N+1] with actual numbers and description)
   - header: "Continue?"
   - options:
     - **Yes, continue** → proceed to the next Task (default)
     - **Pause here** → exit. Print a summary of which Tasks were created and which remain. Suggest `/clear` before resuming
     - **Skip this task** → mark as skipped in the list and move to the next
     - **Add a new task** → call `AskUserQuestion` with question "What is the new task?", header "New task". Offer options from plausible tasks inferred from the remaining Feature ACs. Add the confirmed task. Then continue

### 4. Completion

When all Tasks have been created (or skipped), print a summary:

> "Feature #<feature_number> Task breakdown complete.
> Created: [list with issue numbers]
> Skipped: [list if any]"

Then call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "What's next?"
- header: "Next step"
- options:
  - **Implement first Task** → follow `wtf.implement-task` with the first created Task number (default)
  - **Tasks for next Feature** → follow `wtf.feature-to-tasks` with the next Feature from `gh sub-issue list` that has no child tasks yet
  - **Stop here** → exit. No further action

> Suggest `/clear` before continuing if the conversation has grown long.
