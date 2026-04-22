# WTF — Workflow Task Framework

Drop-in support for the full product development lifecycle — from user insights to validated production code — run agentically alongside humans, with humans always in the loop.

## What is this?

WTF is a structured, agentic workflow that covers every step of product development: research, vision, planning, design, implementation, verification, release, and retrospective. It lives in the repo and GitHub Issues you already use, and it is built to be operated by AI agents and humans together — agents do the structural heavy lifting, humans stay in control of every meaningful decision.

Not tied to a role. Not tied to a phase. Same framework whether you're capturing a user insight, writing an epic, designing a flow, implementing a task, reviewing a PR, or closing a milestone.

## What it covers

A single framework spanning the full lifecycle:

- **Discover** — spikes and user-insight capture feed into planning
- **Steer** — living VISION / TECH / DESIGN / QA docs inform every write
- **Plan** — Epic → Feature → Task hierarchy with Gherkin acceptance tests
- **Design** — full-feature UX journeys and per-task UI states, written back into the issue
- **Build** — TDD-driven implementation against Gherkin, with dependency-aware autonomous execution
- **Verify** — QA walks scenarios; tech lead reviews code against spec
- **Ship** — PRs derived from full spec hierarchy; user-facing changelogs from Gherkin
- **Learn** — retros and reflections route learnings back into the steering docs

## How it works with you

- **Agentic, not autopilot** — skills propose, structure, and execute; humans approve, redirect, and decide
- **Human-in-the-loop by default** — every skill pauses for judgment calls rather than guessing
- **Single source of truth** — the GitHub issue holds design, implementation, and verification side-by-side
- **Drop-in** — works in the Issues and repo you already have; no parallel system to maintain

## Domain-Driven Design runs through everything

DDD is not an optional add-on — it is the spine of WTF. Every issue, scenario, and PR is written in the project's ubiquitous language, enforced at write time by `ddd-writing-rules.md`. Actors are named domain roles (never generic "user" or "admin"). Gherkin scenarios describe behavior in the same vocabulary your VISION doc defines, so product, design, engineering, and QA all converge on one shared model of the system.

The payoff: specs stay legible as the project grows, AI agents generate code against a stable contract instead of drifting synonyms, and onboarding a new contributor means reading the domain — not decoding tribal nicknames.

## 30-second example

```
wtf.write-epic              → draft strategic initiative
wtf.epic-to-features        → break into user-facing capabilities
wtf.feature-to-tasks        → slice into implementable work
wtf.loop                    → autonomously implement → verify → PR
```

Every step writes back to the GitHub issue. The issue stays the source of truth.

## When NOT to use WTF

- One-off scripts or throwaway projects where structure costs more than it saves
- You want fully autonomous execution with no human gates — WTF keeps humans in the loop on purpose

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
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                          PRE-PLANNING                                        │
│                                                                              │
│  wtf.spike  ──  define question → research → 2–3 approaches → recommend      │
│             └──→ docs/spikes/<date>-<slug>.md                                │
│                                                                              │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   │  feeds into
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
│  inherits from            (per task)                 (per task, by QA)       │
│  design-feature ↑                                                            │
│                                   │                         │                │
│                                   ▼                         ▼                │
│                                                                              │
│                              wtf.create-pr          wtf.report-bug           │
│                             PR from full            links failing            │
│                             hierarchy context       scenario → Task          │
│                                                                              │
│                              wtf.pr-review                                   │
│                             code vs spec            ← tech lead reviews      │
│                             (distinct from          PR before merge          │
│                              verify-task)                                    │
│                                                                              │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   │  after merge
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                         RELEASE & CLOSURE                                    │
│                                                                              │
│     wtf.changelog  ──→  CHANGELOG.md / GitHub Release                        │
│                         (user-facing language from Gherkin, not commits)     │
│                                                                              │
│     wtf.retro  ──→  planned vs. shipped comparison                           │
│                     routes learnings → steering docs  ↺                      │
│                     closes Epic                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

EMERGENCY PATH  (bypasses planning spine entirely):

    main ──→  wtf.hotfix  ──→  hotfix/<bug>-<slug>  ──→  fix + test  ──→  PR → main

CROSS-CUTTING  (run any time, any scope):

    wtf.health  ──→  scans all open issues  ──→  surfaces label gaps, stale work, and blockers
```

The Task issue is the single source of truth: Designer, Developer, and QA each append their own section to it in sequence. Each skill offers to chain to the next step automatically. When requirements evolve after creation, use `wtf.refine` to keep hierarchy specs aligned without rewriting unchanged sections.

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

## Prerequisites

**Required:**

| Requirement | Notes |
| --- | --- |
| An AI assistant supporting skills | See [skills documentation](https://skills.sh/docs/faq) for supported runtimes |
| [GitHub CLI (`gh`)](https://cli.github.com) | Must be installed and authenticated (`gh auth login`) |
| GitHub repository | Project must be hosted on GitHub (needed by most execution skills) |

**Auto-installed by `wtf.setup`:**

| Extension | Purpose |
| --- | --- |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | Epic → Feature → Task sub-issue hierarchy |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | Native `Blocks` / `Blocked-by` links |

**Optional:**

| Requirement | Needed for |
| --- | --- |
| [Figma](https://figma.com) account | `wtf.design-feature`, `wtf.design-task` — only when linking Figma frames; both skills can scaffold without it |

## Skill reference

### Setup (run once)

| Skill          | Trigger          | Purpose                                                        |
| -------------- | ---------------- | -------------------------------------------------------------- |
| `wtf.setup`   | "set up wtf"     | Pre-flight check and installer — run once per repo on onboard  |

Validates `gh` CLI is installed and authenticated, installs the `gh-sub-issue` and `gh-issue-dependency` extensions, scaffolds `.github/ISSUE_TEMPLATE/` with all four templates (Epic, Feature, Task, Bug), drops in the PR template, creates all lifecycle labels (`epic`, `feature`, `task`, `bug`, `implemented`, `designed`, `verified`), and prints a status report. Offers to kick off steering doc creation at the end.

### Pre-planning

| Skill         | Trigger                               | Purpose                                                               |
| ------------- | ------------------------------------- | --------------------------------------------------------------------- |
| `wtf.spike`  | "run a spike on X", "investigate this before we commit" | Time-boxed technical investigation before committing to an approach |

When a technical unknown blocks planning, `wtf.spike` defines the question, time-boxes the investigation, researches the codebase and docs, derives 2–3 concrete approaches with trade-offs, and produces a recommendation + findings doc in `docs/spikes/`. Output feeds directly into `write-epic` or `write-task`.

### Planning (Epic → Feature → Task)

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

### Autonomous execution (the main event)

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

### Code review

| Skill              | Trigger           | Purpose                                                              |
| ------------------ | ----------------- | -------------------------------------------------------------------- |
| `wtf.pr-review`   | "review PR #42"   | Review a PR's code against the linked Task spec                      |

Reads the diff against the Task's Gherkin scenarios, Contracts, and Impacted Areas. Checks spec adherence, contract compliance, test coverage, and code quality against `TECH.md`. Posts a structured GitHub PR review (approve / request changes / comment).

**Distinct from `wtf.verify-task`** — `verify-task` is a QA engineer testing by *running the software* (does it behave correctly?). `wtf.pr-review` is a tech lead reviewing *the code itself* (is it written correctly against the spec?).

### Bug reporting

| Skill              | Trigger          | Purpose                                                      |
| ------------------ | ---------------- | ------------------------------------------------------------ |
| `wtf.report-bug`  | "report a bug"   | File a structured Bug issue linked to the originating Task   |

Maps failing Gherkin scenarios as reproducible test evidence and links the originating Task and Feature automatically.

### Emergency fix

| Skill            | Trigger                                    | Purpose                                                             |
| ---------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `wtf.hotfix`    | "production is down", "emergency fix for #X" | Cut a hotfix branch from main and fix — bypasses normal hierarchy   |

For production incidents where the full Epic→Feature→Task flow is too slow. Cuts a hotfix branch directly from `main`, runs a targeted TDD fix, and opens a PR back to `main`. Includes a scope gate — if the fix turns out to be large, it redirects to the normal workflow. Offers backport to release branches.

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

### Project health

| Skill           | Trigger                                       | Purpose                                              |
| --------------- | --------------------------------------------- | ---------------------------------------------------- |
| `wtf.health`   | "project health check", "what's blocked"      | Cross-issue status scan with actionable findings     |

Scans all open Epics, Features, Tasks, and Bugs against expected lifecycle labels. Surfaces tasks implemented but not verified, features with all tasks done but no PR opened, stale issues with no recent activity, and bugs without a linked task. Ends with a triage-ready action list and offers to route directly into the appropriate skill for each finding.

### Release & closure

| Skill              | Trigger                                      | Purpose                                                           |
| ------------------ | -------------------------------------------- | ----------------------------------------------------------------- |
| `wtf.changelog`   | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Tasks and Features |
| `wtf.retro`       | "run a retro on this epic", "close out the epic" | Close an Epic with planned-vs-shipped comparison and routed learnings |

`wtf.changelog` reads the Gherkin `Then` steps and Feature capability names to produce plain-language release notes — not raw commit messages. Outputs to `CHANGELOG.md` or a GitHub Release.

`wtf.retro` compares the original Epic spec against what actually shipped, gathers learnings, routes them into the appropriate steering docs via `reflect`, and formally closes the Epic. Chains to `changelog` at the end.

## Usage

### Full lifecycle example

```
# Before committing to an approach:
"run a spike on whether we should use Redis or in-memory for session storage"
→ wtf.spike     (findings doc + recommendation → feeds into write-epic)

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

"review PR #84"
→ wtf.pr-review           (tech lead reviews code vs spec — distinct from QA)

"create a PR"
→ wtf.create-pr           (PR description from full spec hierarchy)

# After merge:
"write the changelog for feature #12"
→ wtf.changelog           (user-facing release notes from Gherkin, not commits)

"run a retro on epic #3"
→ wtf.retro               (planned vs. shipped, routes learnings, closes Epic)

# Supporting, run any time:
"refine task #42 with latest stakeholder comments"
→ wtf.refine              (updates changed sections only, posts refinement audit trail)

"report a bug"
→ wtf.report-bug          (structured bug from failing Gherkin scenario)

"let's reflect"
→ wtf.reflect             (capture learnings into steering docs)

"project health check"
→ wtf.health              (surfaces blocked/stale issues + suggested next actions)

# Emergency:
"production is down — null pointer in payment settlement"
→ wtf.hotfix              (hotfix branch from main, fix, PR — bypasses normal flow)
```

### Steering setup

```
"create the vision doc"    → wtf.steer-vision
"create the tech doc"      → wtf.steer-tech
"create the design doc"    → wtf.steer-design
"create the QA doc"        → wtf.steer-qa
```
