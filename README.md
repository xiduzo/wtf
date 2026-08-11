# WTF — Workflow Trace Framework

Drop-in support for the full product development lifecycle — from user insights to validated production code — run agentically alongside humans, with humans always in the loop.

## What is this?

WTF is a structured, agentic workflow that covers every step of product development: research, vision, planning, design, implementation, verification, release, and retrospective. It lives in the repo and GitHub Issues you already use, and it is built to be operated by AI agents and humans together — agents do the structural heavy lifting, humans stay in control of every meaningful decision.

Not tied to a role. Not tied to a phase. Same framework whether you're capturing a user insight, writing an epic, designing a flow, implementing a trace, reviewing a PR, or closing a milestone.

## What it covers

A single framework spanning the full lifecycle:

- **Discover** — spikes and user-insight capture feed into planning
- **Steer** — living VISION / TECH / DESIGN / QA docs inform every write
- **Plan** — Epic → Feature → Trace hierarchy; user stories with their canonical Gherkin live on the Feature, and each Trace claims a subset of those scenarios
- **Design** — full-feature UX journeys and per-trace UI states, written back into the issue
- **Build** — TDD-driven implementation against claimed scenarios, with spine-first autonomous execution
- **Verify** — QA executes each Trace's Scenario Claim; tech lead reviews code against spec
- **Ship** — PRs derived from full spec hierarchy; user-facing changelogs from Gherkin
- **Learn** — retros and reflections route learnings back into the steering docs

## How it works with you

- **Agentic, not autopilot** — skills propose, structure, and execute; humans approve, redirect, and decide
- **Human-in-the-loop by default** — every skill pauses for judgment calls rather than guessing
- **Two planning modes** — `guided` asks step by step; `flow` derives everything it can and presents one consolidated review before anything is created. Set the default once in `.wtf/config.json`, override per invocation (e.g. `/wtf.epic-to-features 42 flow`). Both modes run the same quality gates.
- **Single source of truth** — the GitHub issue holds design, implementation, and verification side-by-side
- **Drop-in** — works in the Issues and repo you already have; no parallel system to maintain

## Domain-Driven Design runs through everything

DDD is not an optional add-on — it is the spine of WTF. Every issue, scenario, and PR is written in the project's ubiquitous language, enforced at write time by `ddd-writing-rules.md`. Actors are named domain roles (never generic "user" or "admin"). Gherkin scenarios describe behavior in the same vocabulary your VISION doc defines, so product, design, engineering, and QA all converge on one shared model of the system.

The payoff: specs stay legible as the project grows, AI agents generate code against a stable contract instead of drifting synonyms, and onboarding a new contributor means reading the domain — not decoding tribal nicknames.

## 30-second example

```
wtf.write-epic              → draft strategic initiative
wtf.epic-to-features        → break into user-facing capabilities
wtf.feature-to-traces       → plan and create the Trace sequence per feature
wtf.loop                    → autonomously implement → verify → PR → re-aim
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
│         ├────→  wtf.feature-to-traces  (bulk)                                │  │              │
│         │                                                                    │  └──────────────┤  updates
│         │    wtf.design-feature  (optional, before traces are cut)           │                 │
│         │    ├─ reads user stories + ACs → maps full screen journey          │                 │
│         │    ├─ Epic "Design Artifacts" = upstream strategic input           │                 │
│         │    └─ Feature "Design Handoff" = execution output for devs ↓       │                 │
│         ▼                                                                    │                 │
│                                                                              │                 │
│    wtf.write-trace ◄───────────────────────────────────────────────────────────────────────────┘
│         │                                                                    │
│         │    creates GitHub Trace issue                                      │
│         │    → claims scenarios from the Feature                             │
│         │      (canonical Gherkin lives there)                               │
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
│  chains: implement-trace → verify-trace → create-pr → re-aim                 │
│      (per trace, spine order; Features parallel)                             │
│  resumes from last completed trace if interrupted                            │
│  ends with: feature → main PR (staged) or trace PRs → main (trunk)           │
│                                                                              │
│          OR  run each step manually via DISCIPLINE PICKUP:                   │
│                                                                              │
│     wtf.design-trace        wtf.implement-trace       wtf.verify-trace       │
│  Gherkin → UI states      Tech approach + TDD        Scenario verdict        │
│  inherits from            (per trace)                (per trace, by QA)      │
│  design-feature ↑                                                            │
│                                   │                         │                │
│                                   ▼                         ▼                │
│                                                                              │
│                              wtf.create-pr          wtf.report-bug           │
│                             PR from full            links failing            │
│                             hierarchy context       scenario → Trace         │
│                                                                              │
│                              wtf.pr-review                                   │
│                             code vs spec            ← tech lead reviews      │
│                             (distinct from          PR before merge          │
│                              verify-trace)                                   │
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

The Trace issue is the single source of truth: Designer, Developer, and QA each append their own section to it in sequence. Each skill offers to chain to the next step automatically. When requirements evolve after creation, use `wtf.refine` to keep hierarchy specs aligned without rewriting unchanged sections.

## The Trace model

WTF's implementation unit is the **Trace** — a tracer-bullet work unit inspired by [The Pragmatic Programmer](https://fullstackhub.substack.com/p/the-pragmatic-programmer-12-tracer) and [AI Hero](https://www.aihero.dev/tracer-bullets). A Trace claims one user story and a declared subset of its Gherkin scenarios — its **Scenario Claim** — implemented end-to-end through every layer in one pass. The first Trace of a Feature is the **Skeleton**: the primary story's happy path, minimal, through every layer, at production quality. Each later Trace extends the spine — the next story, or a Deepening Trace that claims further scenarios of a story already started. Scenario Claims partition a story's scenarios: full cover, no overlap. Every Trace leaves the system releasable.

The Feature body stays canonical for all stories and their Gherkin — Traces claim scenarios, they never re-derive them. The Trace Plan is a living aim, not a contract: after each landed Trace, `wtf.refine` re-aims the plan. Autonomous re-aim is grow-only — it may reorder, re-batch, and add scenarios, but a human approves every drop. Delivery is `staged` (trace PRs merge into the feature branch, then feature → main) or `trunk` (trace PRs merge into `main` directly), set once in `.wtf/config.json`.

Legacy Task issues in existing repos stay readable — read paths treat them as legacy Traces. Write paths never create Tasks again.

The decision record is [`docs/adr/0001-traces-replace-tasks.md`](docs/adr/0001-traces-replace-tasks.md), and the vocabulary (Trace, Skeleton, Spine, Scenario Claim, Re-aim) is pinned in [`CONTEXT.md`](CONTEXT.md).

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
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | Epic → Feature → Trace sub-issue hierarchy |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | Native `Blocks` / `Blocked-by` links |
| Intervention-tracker hook | Registers `UserPromptSubmit` + `Stop` entries in `settings.json` to nudge you toward `/wtf.reflect` after repeated corrections. Asks scope (global `~/.claude/settings.json` or per-repo `.claude/settings.json`). |

**Optional:**

| Requirement | Needed for |
| --- | --- |
| [Figma](https://figma.com) account | `wtf.design-feature`, `wtf.design-trace` — only when linking Figma frames; both skills can scaffold without it |
| `python3` in `PATH` | Hook auto-registration in `settings.json`. If missing, `wtf.setup` prints the JSON snippet for manual paste. The hook itself only needs POSIX `sh`. |

## Skill reference

### Setup (run once)

| Skill          | Trigger          | Purpose                                                        |
| -------------- | ---------------- | -------------------------------------------------------------- |
| `wtf.setup`   | "set up wtf"     | Pre-flight check and installer — run once per repo on onboard  |

Validates `gh` CLI is installed and authenticated, installs the `gh-sub-issue` and `gh-issue-dependency` extensions, scaffolds `.github/ISSUE_TEMPLATE/` with all four templates (Epic, Feature, Trace, Bug), drops in the PR template, picks the issue-classification mode (native GitHub issue types in orgs, labels everywhere else) and provisions the Trace type (☄️), creates the lifecycle labels (`implemented`, `designed`, `verified`), asks the default planning mode (`guided` / `flow`), the feature scope (`single-story` / `grouped`), and the delivery mode (`staged` / `trunk` — with a trunk-mode warning), records all choices in `.wtf/config.json`, registers the intervention-tracker hook (asks global vs per-repo), and prints a status report. Offers to kick off steering doc creation at the end.

### Pre-planning

| Skill         | Trigger                               | Purpose                                                               |
| ------------- | ------------------------------------- | --------------------------------------------------------------------- |
| `wtf.spike`  | "run a spike on X", "investigate this before we commit" | Time-boxed technical investigation before committing to an approach |

When a technical unknown blocks planning, `wtf.spike` defines the question, time-boxes the investigation, researches the codebase and docs, derives 2–3 concrete approaches with trade-offs, and produces a recommendation + findings doc in `docs/spikes/`. Output feeds directly into `write-epic` or `write-trace`.

### Planning (Epic → Feature → Trace)

| Skill                | Trigger            | Purpose                                     |
| -------------------- | ------------------ | ------------------------------------------- |
| `wtf.write-epic`    | "create an epic"   | Define a strategic initiative               |
| `wtf.write-feature` | "create a feature" | Break an epic into user-facing capabilities |
| `wtf.write-trace`   | "create a trace"   | Claim one story's scenarios as one implementation pass |

Each skill fetches parent issue context automatically and guides you through a structured workflow, ending with a created and linked GitHub issue. **Features carry the user stories with their canonical Gherkin scenarios; Traces claim a subset of those scenarios** — they never re-derive them.

### Batch decomposition

Break down an entire level of the hierarchy at once, walking through each item with full user control:

| Skill                    | Trigger                           | Purpose                                              |
| ------------------------ | --------------------------------- | ---------------------------------------------------- |
| `wtf.epic-to-features`  | "break down this epic"            | Propose and create all Features for an Epic           |
| `wtf.feature-to-traces` | "plan all traces for feature #12" | Validate the Trace Plan and create all Traces for a Feature |

Both skills propose the full plan upfront. `wtf.feature-to-traces` validates the Feature's Trace Plan (or derives one for older Features) and creates the Trace issues in spine order with sequential dependency links. In `guided` mode both skills walk through creating each item one by one with pause/skip/add controls. In `flow` mode they present one consolidated review before batch-creating — two user gates total: confirm the plan, approve the tree.

### Autonomous execution (the main event)

| Skill         | Trigger                         | Purpose                                                  |
| ------------- | ------------------------------- | -------------------------------------------------------- |
| `wtf.loop`   | "go", "start building", "build it all" | Chain implement → verify → PR → re-aim for every Trace, spine-first |

Requires a fully-specified Epic/Feature/Trace tree. Reads each Feature's ordered Trace Plan, runs pre-flight checks (spec completeness, contradictions, codebase mismatches, circular deps), and chains `wtf.implement-trace → wtf.verify-trace → wtf.create-pr` for each Trace — Traces of one Feature run sequentially in spine order, Features run in parallel. After each verified Trace it re-aims the Feature's Trace Plan via headless `wtf.refine`, pausing only when a human decision is actually needed (contradictions, ambiguities, plan shrinkage). Supports resuming a previous run (skips traces already labeled `implemented` or `verified`). In `staged` delivery it ends by opening a feature → main PR once all trace PRs are merged; in `trunk` delivery trace PRs merge into `main` directly.

### Feature design

Before a Feature's Traces are cut, a designer can produce a holistic design covering the full user journey:

| Skill                   | Trigger                    | Purpose                                                          |
| ----------------------- | -------------------------- | ---------------------------------------------------------------- |
| `wtf.design-feature`   | "design feature #12"       | Map the full UX flow for a Feature and write the Design Handoff  |

`wtf.design-feature` reads the Feature's user stories and Acceptance Criteria, derives every screen and state across the journey, collects or scaffolds Figma frames, and writes the result back into the **Design Handoff** section of the Feature issue — fulfilling the Definition of Ready gate ("Design handoff complete") before traces are cut.

This is distinct from the Epic's **Design Artifacts** field, which holds upstream strategic inputs (vision prototypes, UX research) that informed the Epic's scope. Feature Design Handoff is the execution-level output — the concrete Figma flow a developer and trace-level designer will actually build against.

The shared component map produced here flows into `wtf.design-trace` so per-trace designers don't re-derive cross-feature decisions.

### Discipline pickup

Once a trace exists, any discipline can pick it up independently:

| Skill                  | Trigger               | Purpose                                                     |
| ---------------------- | --------------------- | ----------------------------------------------------------- |
| `wtf.design-trace`    | "design trace #42"    | Designer maps the claimed Gherkin scenarios to Figma frames and component specs |
| `wtf.implement-trace` | "implement trace #42" | Developer drafts technical approach and drives TDD over the Scenario Claim |
| `wtf.verify-trace`    | "verify trace #42"    | QA executes the claimed scenarios and records pass/fail verdict |

All three write their output back into the Trace issue — it stays the single source of truth.

`wtf.design-trace` inherits the shared component map from `wtf.design-feature` when available — it covers UI states for one Trace's claimed scenarios, not the full feature journey.

`wtf.implement-trace` runs the TDD cycle scenario-by-scenario over the Scenario Claim. A Skeleton Trace gets an explicit directive: minimal, through every layer, no gold-plating. Lint and type-checking run once after all scenarios are green (not per-commit), which keeps things fast on large codebases.

`wtf.verify-trace` runs exactly the claimed scenarios via **ephemeral projection**: it scrapes them from the Feature body into a temporary `.feature` file and executes it when a Gherkin runner exists, falling back to interpretive verification otherwise. No committed `.feature` files.

### Shipping

| Skill            | Trigger          | Purpose                                                        |
| ---------------- | ---------------- | -------------------------------------------------------------- |
| `wtf.create-pr` | "create a PR"    | Open a PR with description derived from the Trace/Feature/Epic hierarchy |

Reads the full spec hierarchy and branch diff to write a PR description that explains _why_ the change exists. Picks the base branch from the delivery mode: trace branches target the feature branch in `staged` delivery and `main` in `trunk`. Checks for verification status and offers to run `verify-trace` first.

### Code review

| Skill              | Trigger           | Purpose                                                              |
| ------------------ | ----------------- | -------------------------------------------------------------------- |
| `wtf.pr-review`   | "review PR #42"   | Review a PR's code against the linked Trace spec                     |

Reads the diff against the Trace's claimed Gherkin scenarios, Contracts, and Impacted Areas. Checks spec adherence, contract compliance, test coverage, and code quality against `TECH.md`. Posts a structured GitHub PR review (approve / request changes / comment).

**Distinct from `wtf.verify-trace`** — `verify-trace` is a QA engineer testing by *running the software* (does it behave correctly?). `wtf.pr-review` is a tech lead reviewing *the code itself* (is it written correctly against the spec?).

### Bug reporting

| Skill              | Trigger          | Purpose                                                      |
| ------------------ | ---------------- | ------------------------------------------------------------ |
| `wtf.report-bug`  | "report a bug"   | File a structured Bug issue linked to the originating Trace  |

Maps failing Gherkin scenarios as reproducible test evidence and links the originating Trace and Feature automatically.

### Emergency fix

| Skill            | Trigger                                    | Purpose                                                             |
| ---------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `wtf.hotfix`    | "production is down", "emergency fix for #X" | Cut a hotfix branch from main and fix — bypasses normal hierarchy   |

For production incidents where the full Epic→Feature→Trace flow is too slow. Cuts a hotfix branch directly from `main`, runs a targeted TDD fix, and opens a PR back to `main`. Includes a scope gate — if the fix turns out to be large, it redirects to the normal workflow. Offers backport to release branches.

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
| `wtf.refine`   | "re-aim feature #12"       | Update an existing Epic/Feature/Trace from new insights — the single Re-aim mechanism |

Merges insights from conversation, GitHub comments, and referenced docs; re-validates only affected sections; shows a section-by-section diff before applying updates; posts an audit-trail comment; and cascades scenario edits to the Traces that claim them. Runs headless as `wtf.loop`'s Re-aim step after each verified Trace — grow-only in that mode: it may reorder, re-batch, and add scenarios, but only suggests a drop for human approval.

### Project health

| Skill           | Trigger                                       | Purpose                                              |
| --------------- | --------------------------------------------- | ---------------------------------------------------- |
| `wtf.health`   | "project health check", "what's blocked"      | Cross-issue status scan with actionable findings     |

Scans all open Epics, Features, Traces (plus legacy Tasks), and Bugs against expected lifecycle labels. Surfaces traces implemented but not verified, features with all traces done but no PR opened, stale issues with no recent activity, and bugs without a linked trace. Ends with a triage-ready action list and offers to route directly into the appropriate skill for each finding.

### Release & closure

| Skill              | Trigger                                      | Purpose                                                           |
| ------------------ | -------------------------------------------- | ----------------------------------------------------------------- |
| `wtf.changelog`   | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Traces and Features |
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

"plan all traces for feature #12"
→ wtf.feature-to-traces   (validates the Trace Plan, creates all Traces in spine order)

"design feature #12"
→ wtf.design-feature      (map full UX journey before traces are cut; writes Design Handoff into Feature issue)

"design trace #42"
→ wtf.design-trace        (claimed scenarios → per-trace Figma frames + component spec; inherits shared components from design-feature)

# Option A: autonomous
"go" / "build it all" / "start the loop"
→ wtf.loop                (chains implement → verify → PR → re-aim per trace, spine-first; Features in parallel)

# Option B: manual, per discipline
"implement trace #42"
→ wtf.implement-trace     (developer plans + codes TDD against the Scenario Claim)

"verify trace #42"
→ wtf.verify-trace        (QA executes the claimed scenarios + posts verdict)

"review PR #84"
→ wtf.pr-review           (tech lead reviews code vs spec — distinct from QA)

"create a PR"
→ wtf.create-pr           (PR description from full spec hierarchy, base branch from delivery mode)

# After merge:
"write the changelog for feature #12"
→ wtf.changelog           (user-facing release notes from Gherkin, not commits)

"run a retro on epic #3"
→ wtf.retro               (planned vs. shipped, routes learnings, closes Epic)

# Supporting, run any time:
"re-aim feature #12 — the trace revealed the settlement seam is wrong"
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
