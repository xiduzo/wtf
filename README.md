# WTF — Workflow Task Framework

Skills for managing GitHub issues using an **Epic → Feature → Task** hierarchy, with guided discipline-specific workflows, steering documents, and a full lifecycle from planning through verification.

## Skills

### Setup

| Skill          | Trigger          | Purpose                                                        |
| -------------- | ---------------- | -------------------------------------------------------------- |
| `wtf.setup`   | "set up wtf"     | Pre-flight check and installer — run once per repo on onboard  |

Validates `gh` CLI is installed and authenticated, installs the `gh-sub-issue` and `gh-issue-dependency` extensions, scaffolds `.github/ISSUE_TEMPLATE/` with all four templates (Epic, Feature, Task, Bug), drops in the PR template, creates all lifecycle labels (`epic`, `feature`, `task`, `bug`, `implemented`, `designed`, `verified`), and prints a status report. Offers to kick off steering doc creation at the end.

### Planning spine

| Skill                | Trigger            | Purpose                                     |
| -------------------- | ------------------ | ------------------------------------------- |
| `wtf.write-epic`    | "create an epic"   | Define a strategic initiative               |
| `wtf.write-feature` | "create a feature" | Break an epic into user-facing capabilities |
| `wtf.write-task`    | "create a task"    | Define implementable work under a feature   |

Each skill fetches parent issue context automatically and guides you through a structured workflow, ending with a created and linked GitHub issue. **Tasks auto-generate Gherkin scenarios** from the parent Feature's Acceptance Criteria.

### Batch decomposition

Break down an entire level of the hierarchy at once, walking through each item with full user control:

| Skill                    | Trigger                          | Purpose                                              |
| ------------------------ | -------------------------------- | ---------------------------------------------------- |
| `wtf.epic-to-features`  | "break down this epic"           | Propose and create all Features for an Epic           |
| `wtf.feature-to-tasks`  | "plan all tasks for feature #12" | Propose and create all Tasks for a Feature            |

Both skills propose the full list upfront, then walk through creating each item one by one with pause/skip/add controls.

### Autonomous execution

| Skill         | Trigger                         | Purpose                                                  |
| ------------- | ------------------------------- | -------------------------------------------------------- |
| `wtf.loop`   | "go", "start building", "build it all" | Chain implement → verify → PR for every Task in dependency order |

Requires a fully-specified Epic/Feature/Task tree. Builds a dependency graph, topologically sorts tasks into execution phases, runs pre-flight checks (spec completeness, contradictions, codebase mismatches, circular deps), and chains `wtf.implement-task → wtf.verify-task → wtf.create-pr` for each task — pausing only when a human decision is actually needed. Supports resuming a previous run (skips tasks already labeled `implemented` or `verified`). Ends by opening a feature → main PR once all task PRs are merged.

### Feature design

Before breaking a Feature into Tasks, a designer can produce a holistic design covering the full user journey:

| Skill                   | Trigger                    | Purpose                                                          |
| ----------------------- | -------------------------- | ---------------------------------------------------------------- |
| `wtf.design-feature`   | "design feature #12"       | Map the full UX flow for a Feature and write the Design Handoff  |

`wtf.design-feature` reads the Feature's user stories and Acceptance Criteria, derives every screen and state across the journey, collects or scaffolds Figma frames, and writes the result back into the **Design Handoff** section of the Feature issue — fulfilling the Definition of Ready gate ("Design handoff complete") before tasks are cut.

This is distinct from the Epic's **Design Artifacts** field, which holds upstream strategic inputs (vision prototypes, UX research) that informed the Epic's scope. Feature Design Handoff is the execution-level output — the concrete Figma flow a developer and task-level designer will actually build against.

The shared component map produced here flows into `wtf.design-task` so per-task designers don't re-derive cross-feature decisions.

### Discipline pickup

Once a task exists, any discipline can pick it up independently:

| Skill                 | Trigger              | Purpose                                                     |
| --------------------- | -------------------- | ----------------------------------------------------------- |
| `wtf.design-task`    | "design task #42"    | Designer maps Gherkin scenarios to Figma frames and component specs |
| `wtf.implement-task` | "implement task #42" | Developer drafts technical approach and drives TDD cycle    |
| `wtf.verify-task`    | "verify task #42"    | QA walks Gherkin scenarios and records pass/fail verdict    |

All three write their output back into the Task issue — it stays the single source of truth.

`wtf.design-task` inherits the shared component map from `wtf.design-feature` when available — it covers Gherkin-level UI states for one task, not the full feature journey.

`wtf.implement-task` runs the TDD cycle scenario-by-scenario. Lint and type-checking run once after all scenarios are green (not per-commit), which keeps things fast on large codebases.

### Shipping

| Skill            | Trigger          | Purpose                                                        |
| ---------------- | ---------------- | -------------------------------------------------------------- |
| `wtf.create-pr` | "create a PR"    | Open a PR with description derived from the Task/Feature/Epic hierarchy |

Reads the full spec hierarchy and branch diff to write a PR description that explains _why_ the change exists. Checks for verification status and offers to run `verify-task` first.

### Bug reporting

| Skill              | Trigger          | Purpose                                                      |
| ------------------ | ---------------- | ------------------------------------------------------------ |
| `wtf.report-bug`  | "report a bug"   | File a structured Bug issue linked to the originating Task   |

Maps failing Gherkin scenarios as reproducible test evidence and links the originating Task and Feature automatically.

### Steering documents

Generate and maintain living project guideline documents in `docs/steering/`:

| Skill                | Trigger                    | Purpose                                          |
| -------------------- | -------------------------- | ------------------------------------------------ |
| `wtf.steer-vision`  | "create the vision doc"    | Product constitution — purpose, users, principles |
| `wtf.steer-tech`    | "create the tech doc"      | Stack, architecture, constraints, ADRs            |
| `wtf.steer-design`  | "create the design doc"    | Design principles, tokens, component patterns     |
| `wtf.steer-qa`      | "create the QA doc"        | Test strategy, coverage thresholds, DoD           |

Each skill researches the codebase first, only asks about gaps, and offers wiki sync. They chain to each other so you can set up all four in one session.

### Reflection

| Skill           | Trigger            | Purpose                                                       |
| --------------- | ------------------ | ------------------------------------------------------------- |
| `wtf.reflect`  | "let's reflect"    | Capture session learnings and route them into steering docs   |

Routes each learning into the right steering doc (TECH, QA, DESIGN, or VISION) under a "Hard-Won Lessons" section.

### Refinement

| Skill           | Trigger                    | Purpose                                                                 |
| --------------- | -------------------------- | ----------------------------------------------------------------------- |
| `wtf.refine`   | "refine task #42"          | Update an existing Epic/Feature/Task from new insights with audit trail |

Merges insights from conversation, GitHub comments, and referenced docs; re-validates only affected sections; shows a section-by-section diff before applying updates; and offers cascade refinement for impacted child issues.

## How it all fits together

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        STEERING  (Project Constitution)                      │
│                                                                              │
│  wtf.steer-vision ─→ wtf.steer-tech ─→ wtf.steer-design ─→ wtf.steer-qa      │
│         ↓                 ↓                ↓                 ↓               │
│     VISION.md          TECH.md          DESIGN.md          QA.md             │
│   (product/DDD)      (arch/ADRs)      (tokens/a11y)     (test strat)         │
│                                                                              │
│                          wtf.reflect                                         │
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
│    wtf.write-epic  ◄────────────────────────────────────────────────────────────┐ │            │                    │
│         │                                                                    │  │ │            ▼                    │
│         │    creates GitHub Epic issue                                       │  │ │                                 │
│         │                                                                    │  │ │       wtf.refine                │
│         ├────→  wtf.epic-to-features   (bulk)                                │  │ │                                 │
│         │                                                                    │  │ │       updates changed           │
│         ▼                                                                    │  │ │       sections only,            │
│                                                                              │  │ │       posts audit trail,        │
│    wtf.write-feature  ◄─────────────────────────────────────────────────────────┤ │       cascades to               │
│         │                                                                    │  │ │       affected children         │
│         │    creates GitHub Feature issue                                    │  │ │                                 │
│         │    → derives user stories + Acceptance Criteria                    │  │ │            │                    │
│         │                                                                    │  │ └────────────┤────────────────────┘
│         ├────→  wtf.feature-to-tasks   (bulk)                                │  │              │
│         │                                                                    │  └──────────────┤  updates
│         │    wtf.design-feature  (optional, before tasks are cut)            │                 │
│         │    ├─ reads user stories + ACs → maps full screen journey          │                 │
│         │    ├─ Epic "Design Artifacts" = upstream strategic input           │                 │
│         │    └─ Feature "Design Handoff" = execution output for devs ↓       │                 │
│         ▼                                                                    │                 │
│                                                                              │                 │
│    wtf.write-task  ◄───────────────────────────────────────────────────────────────────────────┘
│         │                                                                    │
│         │    creates GitHub Task issue                                       │
│         │    → generates Gherkin from Feature ACs                            │
│         │    → declares dependency links                                     │
│         │                                                                    │
└─────────┼────────────────────────────────────────────────────────────────────┘
          │
          │
          │  executed by
          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                  AUTONOMOUS EXECUTION  (wtf.loop)                            │
│                                                                              │
│  builds dependency graph → topological sort → pre-flight checks              │
│  chains: implement-task → verify-task → create-pr  (per task, in order)      │
│  resumes from last completed task if interrupted                             │
│  ends with: feature → main PR                                                │
│                                                                              │
│          OR  run each step manually via DISCIPLINE PICKUP:                   │
│                                                                              │
│     wtf.design-task         wtf.implement-task        wtf.verify-task        │
│  Gherkin → UI states      Tech approach + TDD        Scenario verdict        │
│  inherits from            (per task)                 (per task)              │
│  design-feature ↑                                                            │
│                                   │                         │                │
│                                   ▼                         ▼                │
│                                                                              │
│                              wtf.create-pr          wtf.report-bug           │
│                             PR from full            links failing            │
│                             hierarchy context       scenario → Task          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

DDD runs through everything — all issues use domain language, `ddd-writing-rules.md` is enforced at every write step, and actors are always named domain roles (never "user" or "admin"). The Task issue is the single source of truth: Designer, Developer, and QA each append their own section to it in sequence.

Each skill offers to chain to the next step automatically. When requirements evolve after creation, use `wtf.refine` to keep hierarchy specs aligned without rewriting unchanged sections.

## Prerequisites

| Requirement | Required by | Notes |
| --- | --- | --- |
| An AI assistant supporting skills | All skills | See [skills documentation](https://skills.sh/docs/faq) for supported runtimes |
| [GitHub CLI (`gh`)](https://cli.github.com) | All skills except steering/reflect | Must be installed and authenticated (`gh auth login`) |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | write-task, epic-to-features, feature-to-tasks | Epic → Feature → Task sub-issue hierarchy; auto-installed by gh-setup |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | write-task, feature-to-tasks, loop | Native `Blocks`/`Blocked-by` links; auto-installed by gh-setup |
| [`MeroFuruya/gh-dep`](https://github.com/MeroFuruya/gh-dep) | loop | Dependency graph for topological sort; installed by loop on first run |
| GitHub repository | write-epic, write-feature, write-task, epic-to-features, feature-to-tasks, report-bug, create-pr, design-task, implement-task, verify-task, refine, loop | Project must be hosted on GitHub |
| [Figma](https://figma.com) account | `design-feature`, `design-task` (optional) | Only needed when linking Figma frames; both skills can scaffold without it |

The two `gh` extensions are checked and installed automatically the first time any issue-creating skill runs. You don't need to install them manually.

## Installation

### One-command setup

Run this from your project root:

```bash
npx skills add https://github.com/xiduzo/wtf
```

Get started by opening claude and run

```bash
wtf.setup
```

### Keeping up to date

```bash
npx skills update
```

## Usage

### Full lifecycle example

```
"write an epic for user authentication"
→ wtf.write-epic

"break down this epic"
→ wtf.epic-to-features  (proposes all Features, creates them one by one)

"plan all tasks for feature #12"
→ wtf.feature-to-tasks   (proposes all Tasks, creates them one by one)

"design feature #12"
→ wtf.design-feature      (map full UX journey before tasks are cut; writes Design Handoff into Feature issue)

"design task #42"
→ wtf.design-task         (Gherkin scenarios → per-task Figma frames + component spec; inherits shared components from design-feature)

# Option A: autonomous
"go" / "build it all" / "start the loop"
→ wtf.loop                (chains implement → verify → PR for every task in dependency order)

# Option B: manual, per discipline
"implement task #42"
→ wtf.implement-task      (developer plans + codes TDD against Gherkin)

"verify task #42"
→ wtf.verify-task         (QA walks scenarios + posts verdict)

"create a PR"
→ wtf.create-pr           (PR description from full spec hierarchy)

"refine task #42 with latest stakeholder comments"
→ wtf.refine              (updates changed sections only, posts refinement audit trail)

"report a bug"
→ wtf.report-bug          (structured bug from failing Gherkin scenario)

"let's reflect"
→ wtf.reflect             (capture learnings into steering docs)
```

### Steering setup

```
"create the vision doc"    → wtf.steer-vision
"create the tech doc"      → wtf.steer-tech
"create the design doc"    → wtf.steer-design
"create the QA doc"        → wtf.steer-qa
```

## Issue Templates

The `.github/ISSUE_TEMPLATE/` directory contains matching templates:

- `EPIC.md` — strategic initiative template
- `FEATURE.md` — user-facing capability template
- `TASK.md` — implementable unit of work template
- `BUG.md` — bug report template
