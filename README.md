# WTF — Workflow Task Framework

Claude Code skills for managing GitHub issues using an **Epic → Feature → Task** hierarchy, with guided discipline-specific workflows, steering documents, and a full lifecycle from planning through verification.

## Skills

### Planning spine

| Skill                | Trigger            | Purpose                                     |
| -------------------- | ------------------ | ------------------------------------------- |
| `/wtf:write-epic`    | "create an epic"   | Define a strategic initiative               |
| `/wtf:write-feature` | "create a feature" | Break an epic into user-facing capabilities |
| `/wtf:write-task`    | "create a task"    | Define implementable work under a feature   |

Each skill fetches parent issue context automatically and guides you through a structured workflow, ending with a created and linked GitHub issue. **Tasks auto-generate Gherkin scenarios** from the parent Feature's Acceptance Criteria.

### Batch decomposition

Break down an entire level of the hierarchy at once, walking through each item with full user control:

| Skill                    | Trigger                          | Purpose                                              |
| ------------------------ | -------------------------------- | ---------------------------------------------------- |
| `/wtf:epic-to-features`  | "break down this epic"           | Propose and create all Features for an Epic           |
| `/wtf:feature-to-tasks`  | "plan all tasks for feature #12" | Propose and create all Tasks for a Feature            |

Both skills propose the full list upfront, then walk through creating each item one by one with pause/skip/add controls.

### Discipline pickup

Once a task exists, any discipline can pick it up independently:

| Skill                 | Trigger              | Purpose                                                     |
| --------------------- | -------------------- | ----------------------------------------------------------- |
| `/wtf:design-task`    | "design task #42"    | Designer adds Figma references and component specs          |
| `/wtf:implement-task` | "implement task #42" | Developer drafts technical approach and drives TDD cycle    |
| `/wtf:verify-task`    | "verify task #42"    | QA walks Gherkin scenarios and records pass/fail verdict    |

All three write their output back into the Task issue — it stays the single source of truth.

### Shipping

| Skill            | Trigger          | Purpose                                                        |
| ---------------- | ---------------- | -------------------------------------------------------------- |
| `/wtf:create-pr` | "create a PR"    | Open a PR with description derived from the Task/Feature/Epic hierarchy |

Reads the full spec hierarchy and branch diff to write a PR description that explains _why_ the change exists. Checks for verification status and offers to run `verify-task` first.

### Bug reporting

| Skill              | Trigger          | Purpose                                                      |
| ------------------ | ---------------- | ------------------------------------------------------------ |
| `/wtf:report-bug`  | "report a bug"   | File a structured Bug issue linked to the originating Task   |

Maps failing Gherkin scenarios as reproducible test evidence and links the originating Task and Feature automatically.

### Steering documents

Generate and maintain living project guideline documents in `docs/steering/`:

| Skill                | Trigger                    | Purpose                                          |
| -------------------- | -------------------------- | ------------------------------------------------ |
| `/wtf:steer-vision`  | "create the vision doc"    | Product constitution — purpose, users, principles |
| `/wtf:steer-tech`    | "create the tech doc"      | Stack, architecture, constraints, ADRs            |
| `/wtf:steer-design`  | "create the design doc"    | Design principles, tokens, component patterns     |
| `/wtf:steer-qa`      | "create the QA doc"        | Test strategy, coverage thresholds, DoD           |

Each skill researches the codebase first, only asks about gaps, and offers wiki sync. They chain to each other so you can set up all four in one session.

### Reflection

| Skill           | Trigger            | Purpose                                                       |
| --------------- | ------------------ | ------------------------------------------------------------- |
| `/wtf:reflect`  | "let's reflect"    | Capture session learnings and route them into steering docs   |

Routes each learning into the right steering doc (TECH, QA, DESIGN, or VISION) under a "Hard-Won Lessons" section.

### Refinement

| Skill           | Trigger                    | Purpose                                                                 |
| --------------- | -------------------------- | ----------------------------------------------------------------------- |
| `/wtf:refine`   | "refine task #42"          | Update an existing Epic/Feature/Task from new insights with audit trail |

Merges insights from conversation, GitHub comments, and referenced docs; re-validates only affected sections; shows a section-by-section diff before applying updates; and offers cascade refinement for impacted child issues.

## How it all fits together

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        STEERING  (Project Constitution)                      │
│                                                                              │
│     steer-vision ──→  steer-tech  ──→  steer-design  ──→  steer-qa           │
│         ↓                 ↓                ↓                 ↓               │
│     VISION.md          TECH.md          DESIGN.md          QA.md             │
│   (product/DDD)      (arch/ADRs)      (tokens/a11y)     (test strat)         │
│                                                                              │
│                          /wtf:reflect                                        │
│                    routes learnings back in ↺                                │
│                                                                              │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   │  informs
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐    ┌─────────────────────────────────┐
│                                                                              │    │                                 │
│                            PLANNING SPINE                                    │    │   New insights /                │
│                                                                              │    │   feedback / comments           │
│    /wtf:write-epic  ◄───────────────────────────────────────────────────────────┐ │            │                    │
│         │                                                                    │  │ │            ▼                    │
│         │    creates GitHub Epic issue                                       │  │ │                                 │
│         │                                                                    │  │ │       /wtf:refine               │
│         ├────→  /wtf:epic-to-features   (bulk)                               │  │ │                                 │
│         │                                                                    │  │ │       updates changed           │
│         ▼                                                                    │  │ │       sections only,            │
│                                                                              │  │ │       posts audit trail,        │
│    /wtf:write-feature  ◄────────────────────────────────────────────────────────┤ │       cascades to               │
│         │                                                                    │  │ │       affected children         │
│         │    creates GitHub Feature issue                                    │  │ │                                 │
│         │    → derives user stories + Acceptance Criteria                    │  │ │            │                    │
│         │                                                                    │  │ └────────────┤────────────────────┘
│         ├────→  /wtf:feature-to-tasks   (bulk)                               │  │              │
│         │                                                                    │  └──────────────┤
│         ▼                                                                    │                 │
│                                                                              │                 │  updates
│    /wtf:write-task  ◄──────────────────────────────────────────────────────────────────────────┘
│         │                                                                    │
│         │    creates GitHub Task issue                                       │
│         │    → generates Gherkin from Feature ACs                            │
│         │    → declares dependency links                                     │
│         │                                                                    │
└─────────┼────────────────────────────────────────────────────────────────────┘
          │
          │
          │  excecuted by
          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│               PARALLEL DISCIPLINE PICKUP  (single Task)                      │
│                                                                              │
│    /wtf:design-task        /wtf:implement-task        /wtf:verify-task       │
│    Design Reference        Tech approach + TDD        Scenario verdict       │
│                                   │                         │                │
│                                   ▼                         ▼                │
│                                                                              │
│                             /wtf:create-pr          /wtf:report-bug          │
│                             PR from full            links failing            │
│                             hierarchy context       scenario → Task          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

DDD runs through everything — all issues use domain language, `ddd-writing-rules.md` is enforced at every write step, and actors are always named domain roles (never "user" or "admin"). The Task issue is the single source of truth: Designer, Developer, and QA each append their own section to it in sequence.

Each skill offers to chain to the next step automatically. When requirements evolve after creation, use `/wtf:refine` to keep hierarchy specs aligned without rewriting unchanged sections.

## Prerequisites

| Requirement | Required by | Notes |
| --- | --- | --- |
| [Claude Code](https://claude.ai/code) | All skills | Skills run inside Claude Code |
| [GitHub CLI (`gh`)](https://cli.github.com) | All skills except steering/reflect | Must be installed and authenticated (`gh auth login`) |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | write-task, epic-to-features, feature-to-tasks | Epic → Feature → Task sub-issue hierarchy; auto-installed by gh-setup |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | write-task, feature-to-tasks | Native `Blocks`/`Blocked-by` links; auto-installed by gh-setup |
| GitHub repository | write-epic, write-feature, write-task, epic-to-features, feature-to-tasks, report-bug, create-pr, design-task, implement-task, verify-task, refine | Project must be hosted on GitHub |
| [Figma](https://figma.com) account | `design-task` (optional) | Only needed when linking Figma frames; skill can scaffold without it |

The two `gh` extensions are checked and installed automatically the first time any issue-creating skill runs. You don't need to install them manually.

## Installation

### One-command setup

Run this from your project root:

```bash
claude "Add .wtf as a local marketplace in .claude/settings.local.json with source path $(pwd)/.wtf, enable the plugin wtf@wtf, then confirm it's working by listing the available wtf skills"
```

### Manual setup

Add to `.claude/settings.local.json` (create if it doesn't exist):

```json
{
  "extraKnownMarketplaces": {
    "wtf": {
      "source": {
        "source": "directory",
        "path": "/absolute/path/to/.workflow"
      }
    }
  },
  "enabledPlugins": {
    "wtf@wtf": true
  }
}
```

Replace `/absolute/path/to/.workflow` with the actual absolute path.

## Usage

### Full lifecycle example

```
"write an epic for user authentication"
→ /wtf:write-epic

"break down this epic"
→ /wtf:epic-to-features  (proposes all Features, creates them one by one)

"plan all tasks for feature #12"
→ /wtf:feature-to-tasks   (proposes all Tasks, creates them one by one)

"design task #42"
→ /wtf:design-task         (designer adds Figma frames + component spec)

"implement task #42"
→ /wtf:implement-task      (developer plans + codes TDD against Gherkin)

"verify task #42"
→ /wtf:verify-task         (QA walks scenarios + posts verdict)

"refine task #42 with latest stakeholder comments"
→ /wtf:refine              (updates changed sections only, posts refinement audit trail)

"create a PR"
→ /wtf:create-pr           (PR description from full spec hierarchy)

"report a bug"
→ /wtf:report-bug          (structured bug from failing Gherkin scenario)

"let's reflect"
→ /wtf:reflect             (capture learnings into steering docs)
```

### Steering setup

```
"create the vision doc"    → /wtf:steer-vision
"create the tech doc"      → /wtf:steer-tech
"create the design doc"    → /wtf:steer-design
"create the QA doc"        → /wtf:steer-qa
```

## Issue Templates

The `.github/ISSUE_TEMPLATE/` directory contains matching templates:

- `EPIC.md` — strategic initiative template
- `FEATURE.md` — user-facing capability template
- `TASK.md` — implementable unit of work template
- `BUG.md` — bug report template
