# WTF — Workflow Trace Framework

Agentic support for the full product development lifecycle, from user insight to verified production code. Agents do the structural work. Humans make every decision that matters.

## What is WTF?

WTF is a set of skills for AI coding assistants. The skills cover research, vision, planning, design, implementation, verification, release, and retrospective. They live in the repo and the GitHub Issues you already use. There is no second system to maintain.

Each skill pauses at a judgment call instead of guessing. The GitHub issue holds the design, the implementation notes, and the verification verdict side by side. It stays the single source of truth.

The same framework serves every role and every phase. Use it to capture an insight, write an Epic, design a flow, implement a Trace, review a PR, or close a milestone.

### When not to use WTF

- One-off scripts or throwaway projects, where the structure costs more than it saves.
- Fully autonomous execution with no human gates. WTF keeps humans in the loop on purpose.

## Quick start

Install the skills from your project root:

```bash
npx skills add https://github.com/xiduzo/wtf
```

Open your AI assistant and run the setup skill:

```
/wtf.setup
```

Update the skills later with:

```bash
npx skills update
```

### Prerequisites

| Requirement | Notes |
| --- | --- |
| An AI assistant that supports skills | See the [skills documentation](https://skills.sh/docs/faq) for supported runtimes |
| [GitHub CLI (`gh`)](https://cli.github.com) | Installed and authenticated with `gh auth login`. The token needs the `repo` scope and write access to the repo. |
| A GitHub repository | Most execution skills need it |

### What `wtf.setup` installs

| Item | Purpose |
| --- | --- |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | Epic → Feature → Trace sub-issue hierarchy |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | Native `Blocks` / `Blocked-by` links |
| [`github/gh-stack`](https://github.com/github/gh-stack) | Native stacked PRs. `wtf.create-pr` links each stacked Trace PR into a GitHub stack, so every PR shows the stack map. |
| Issue and PR templates | Epic, Feature, Trace, and Bug templates in `.github/ISSUE_TEMPLATE/`, plus the PR template |
| Issue classification | Native issue types in orgs, with a ☄️ Trace type. Labels everywhere else. |
| Lifecycle labels | `designed`, `implemented`, `verified` |
| Head-branch auto-delete | Turns on **Automatically delete head branches** in the repo settings. Stacked Trace PRs need it to retarget after a merge. |
| `.wtf/config.json` | Your answers to the four setup questions. See [Configuration](#configuration). |
| `.wtf/gh-body.py` | UTF-8-safe helper for issue and PR bodies. Prevents body corruption on Windows. |
| Shared references | A copy of the cross-skill reference docs next to the installed skills |
| Intervention-tracker hook | `UserPromptSubmit` and `Stop` entries in `settings.json`. Nudges you toward `/wtf.reflect` after repeated corrections. Setup asks for global or per-repo scope. |

### Optional

| Requirement | Needed for |
| --- | --- |
| [Figma](https://figma.com) account | `wtf.design-feature` and `wtf.design-trace`, only to link Figma frames. Both skills scaffold without it. |
| `python3` in `PATH` | Hook registration, the body helper, and the config writes in `wtf.setup`. Without it, setup prints the JSON for manual paste and the body helper stays inactive. |

## Configuration

`wtf.setup` records four choices in `.wtf/config.json`. Commit the file so every teammate uses the same settings.

| Key | Values | Meaning |
| --- | --- | --- |
| `classification` | `types` / `labels` | How an issue gets its kind: native GitHub issue types in orgs, labels everywhere else |
| `planning` | `guided` / `flow` | `guided` asks step by step. `flow` derives what it can and shows one consolidated review before it creates anything. Both modes run the same quality gates. |
| `feature_scope` | `single-story` / `grouped` | One user story per Feature, or several |
| `delivery` | `staged` / `trunk` | `staged`: Trace PRs merge into the feature branch, then the feature branch merges into `main`. `trunk`: Trace PRs merge into `main` directly. |

Override the planning mode per invocation, for example `/wtf.epic-to-features 42 flow`.

## How it works

One framework across the lifecycle:

- **Discover** — spikes and user insights feed planning.
- **Steer** — living VISION, TECH, DESIGN, and QA docs inform every write.
- **Plan** — Epic → Feature → Trace. User stories and their Gherkin scenarios live on the Feature. Each Trace claims a subset of those scenarios.
- **Design** — full-feature UX journeys and per-Trace UI states, written into the issue.
- **Build** — TDD against the claimed scenarios, Skeleton first.
- **Verify** — QA runs each Trace's Scenario Claim. A tech lead reviews the code against the spec.
- **Ship** — PRs written from the full spec hierarchy. Changelogs written from the Gherkin.
- **Learn** — retros and reflections write learnings back into the steering docs.

The shortest path:

```
wtf.write-epic              → draft the strategic initiative
wtf.epic-to-features        → split it into user-facing capabilities
wtf.feature-to-traces       → plan and create the Trace sequence per Feature
wtf.loop                    → implement → verify → PR → re-aim, autonomously
```

Every step writes back to the GitHub issue.

### The Trace model

The unit of implementation is the **Trace**, a tracer-bullet work unit ([The Pragmatic Programmer](https://fullstackhub.substack.com/p/the-pragmatic-programmer-12-tracer), [AI Hero](https://www.aihero.dev/tracer-bullets)). A Trace claims one user story and a declared subset of its Gherkin scenarios: its **Scenario Claim**. It implements that claim through every layer in one pass. Every Trace leaves the system releasable.

The first Trace of a Feature is the **Skeleton**: the primary story's happy path, minimal, through every layer, at production quality. Each later Trace extends the **Spine**. An **Extension Trace** adds the next story. A **Deepening Trace** claims more scenarios of a story that already started. Scenario Claims partition a story's scenarios: full cover, no overlap.

The Feature body stays canonical for all stories and their Gherkin. Traces claim scenarios and never re-derive them. The Trace Plan is a living aim, not a contract. After each landed Trace, `wtf.refine` re-aims the plan. The autonomous re-aim owns the order only: it can reorder, re-batch, and move scenarios between entries. A human approves every change to the set of scenarios the plan delivers.

Each Feature delivers through one linear stack of Trace PRs. Each Trace branches off the top of the stack, so no Trace waits for a merge. Traces that share no files build at the same time, then join the stack one after the other. `wtf.create-pr` links each stacked Trace PR into a native GitHub stack with `gh-stack`. Without the extension, GitHub still retargets each stacked PR when the PR below it merges.

Legacy Task issues stay readable. Read paths treat them as legacy Traces. Write paths never create Tasks again.

The decision record is [`docs/adr/0001-traces-replace-tasks.md`](docs/adr/0001-traces-replace-tasks.md). [`CONTEXT.md`](CONTEXT.md) pins the vocabulary: Trace, Skeleton, Extension Trace, Deepening Trace, Spine, Spine Position, Scenario Claim, and Re-aim.

### Domain-Driven Design

DDD is the foundation of WTF, not an add-on. Every issue, scenario, and PR uses the project's ubiquitous language, and `ddd-writing-rules.md` enforces it at write time. Actors are domain roles, never a generic "user" or "admin". Gherkin scenarios use the vocabulary the VISION doc defines, so product, design, engineering, and QA share one model of the system.

The result: specs stay legible as the project grows. Agents generate code against a stable contract instead of drifting synonyms. A new contributor reads the domain instead of decoding nicknames.

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
│      (one linear PR stack per Feature; Features parallel)                    │
│      see "Inside wtf.loop" below                                             │
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

The Trace issue is the single source of truth. The designer, the developer, and QA each append their own section to it, in sequence. Each skill offers to chain to the next step. When requirements change after creation, `wtf.refine` keeps the hierarchy aligned without rewriting the unchanged sections.

### Inside `wtf.loop`

`wtf.loop` runs in five steps. Each Feature ends as one linear stack of Trace PRs, and that stack merges back into `main`.

```
/wtf.loop <Epic or Feature>
  │
  ▼
1 GRAPH         Epic → Features → Traces, plus their blocked-by links
  │
  ▼
2 PRE-FLIGHT    specs complete · no contradictions · paths exist · deps valid
  │             schedule: phases by dependency → sub-phases by shared files
  ▼
3 PLAN REVIEW   you approve the execution plan before any code is written
  │
  ▼
4 EXECUTE       Features that share no files run in parallel. Inside each one:
  │
  │  ┌─ Feature #5 ─────────────────────────────────────────────────────────┐
  │  │                                                                      │
  │  │  sub-phase 1   #10 Skeleton       alone: it lays the Spine           │
  │  │  sub-phase 2   #11 Extension  ─┐  no shared files, so they build     │
  │  │                #12 Deepening  ─┘  at the same time in two worktrees  │
  │  │  sub-phase 3   #13 Deepening      shares files with #11, so it waits │
  │  │                                                                      │
  │  │  every Trace   implement → verify → join the stack → open PR         │
  │  │                → CI green → merge → wtf.refine re-aims the plan ↺    │
  │  │                                                                      │
  │  └──────────────────────────────────────────────────────────────────────┘
  ▼
5 DELIVER       the stack of each Feature goes back to main


THE STACK       one linear stack per Feature, never a tree

    PR #63   trace/13 ──► trace/12       top of the stack
    PR #62   trace/12 ──► trace/11       built next to #11, then rebased onto it
    PR #61   trace/11 ──► trace/10
    PR #60   trace/10 ──► feature/5-…    bottom: the Skeleton

    gh-stack shows the stack map on every PR. Each PR shows only its own diff.
    A Trace never waits for a merge. The next one branches off the top as soon
    as the PR below it is open and green.


BACK TO MAIN

  staged (default)
    main ──┬─────────────────────────────────────────●──►    feature PR: Closes #5
           └── feature/5-… ──●──────●──────●──────●──┘
                            #10    #11    #12    #13         Trace PRs merge in, bottom-up

  trunk
    main ──●──────●──────●──────●──►                         each Trace PR merges into main
          #10    #11    #12    #13                           #13 also carries Closes #5

    PRs merge bottom-up. A merge deletes the branch, and GitHub retargets the
    PR above it. Without required reviews, the loop merges each PR when CI is
    green. With required reviews, the loop keeps going, and the open PRs wait
    for a reviewer as one stack.
```

## Skill reference

### Setup

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.setup` | "set up wtf" | Pre-flight check and installer. Run once per repo. |

Checks `gh`, its authentication, the token scopes, and repo write access. Installs everything listed in [What `wtf.setup` installs](#what-wtfsetup-installs). Asks the four [configuration](#configuration) questions, prints a status report, and offers to create the steering docs.

### Steering documents

Living guideline documents in `docs/steering/`:

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.steer-vision` | "create the vision doc" | Product constitution: purpose, users, principles |
| `wtf.steer-tech` | "create the tech doc" | Stack, architecture, constraints, ADRs |
| `wtf.steer-design` | "create the design doc" | Design principles, tokens, component patterns |
| `wtf.steer-qa` | "create the QA doc" | Test strategy, coverage thresholds, Definition of Done |

Each skill researches the codebase first and asks only about the gaps. The skills chain to each other, so one session can set up all four. They also offer a wiki sync.

### Pre-planning

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.spike` | "run a spike on X" | Time-boxed technical investigation before you commit to an approach |

`wtf.spike` defines the question, time-boxes the investigation, and researches the codebase and docs. It derives two or three approaches with trade-offs and writes a recommendation to `docs/spikes/`. The findings feed `wtf.write-epic` or `wtf.write-trace`.

### Planning (Epic → Feature → Trace)

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.write-epic` | "create an epic" | Define a strategic initiative |
| `wtf.write-feature` | "create a feature" | Describe one user-facing capability with its stories and Gherkin |
| `wtf.write-trace` | "create a trace" | Claim one story's scenarios as one implementation pass |

Each skill reads the parent issue, guides you through a structured workflow, and ends with a created and linked GitHub issue. Features carry the user stories with their canonical Gherkin scenarios. Traces claim a subset of those scenarios and never re-derive them.

### Batch decomposition

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.epic-to-features` | "break down this epic" | Propose and create all Features for an Epic |
| `wtf.feature-to-traces` | "plan all traces for feature #12" | Validate the Trace Plan and create all Traces for a Feature |

Both skills propose the full plan first. `wtf.feature-to-traces` validates the Feature's Trace Plan, or derives one for an older Feature. It then creates the Trace issues in spine order with sequential dependency links. In `guided` mode you create each item one by one, with pause, skip, and add controls. In `flow` mode the skill shows one consolidated review and then creates the batch. That is two user gates in total: confirm the plan, approve the tree.

### Feature design

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.design-feature` | "design feature #12" | Map the full UX flow for a Feature and write the Design Handoff |

`wtf.design-feature` reads the Feature's user stories and Acceptance Criteria and derives every screen and state in the journey. It collects or scaffolds Figma frames and writes the result into the **Design Handoff** section of the Feature issue. That satisfies the Definition of Ready gate "Design handoff complete" before you cut the Traces.

The Epic's **Design Artifacts** field is different. It holds upstream strategic inputs, such as vision prototypes and UX research. The Feature's Design Handoff is the execution-level output that developers build against. The shared component map from this skill flows into `wtf.design-trace`.

### Autonomous execution

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.loop` | "go", "start building", "build it all" | Chain implement → verify → PR → re-aim for every Trace, Skeleton first |

`wtf.loop` needs a fully specified Epic, Feature, and Trace tree. It reads each Feature's ordered Trace Plan and runs pre-flight checks: spec completeness, contradictions, codebase mismatches, and circular dependencies. Then it chains `wtf.implement-trace → wtf.verify-trace → wtf.create-pr` for each Trace.

A Feature's Skeleton runs first and alone. The file-conflict graph that schedules Features then schedules the Feature's remaining Traces. Features run in parallel. After each verified Trace, the loop re-aims the Feature's Trace Plan through headless `wtf.refine`. It pauses only for a human decision: a contradiction, an ambiguity, or a change to a Trace Plan's scenario set.

The loop resumes a previous run and skips Traces labeled `implemented` or `verified`. In `staged` delivery it ends with a feature → main PR after all Trace PRs merge. In `trunk` delivery the Trace PRs merge into `main` directly.

### Discipline pickup

Once a Trace exists, each discipline can work on it independently:

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.design-trace` | "design trace #42" | Designer maps the claimed scenarios to Figma frames and component specs |
| `wtf.implement-trace` | "implement trace #42" | Developer drafts the technical approach and drives TDD over the Scenario Claim |
| `wtf.verify-trace` | "verify trace #42" | QA runs the claimed scenarios and records a pass or fail verdict |

All three write their output into the Trace issue.

`wtf.design-trace` inherits the shared component map from `wtf.design-feature` when it exists. It covers the UI states for one Trace's claimed scenarios, not the full journey.

`wtf.implement-trace` runs the TDD cycle scenario by scenario over the Scenario Claim. A Skeleton Trace gets an explicit directive: minimal, through every layer, no gold-plating. Lint and type checks run once after all scenarios pass, which keeps large codebases fast.

`wtf.verify-trace` runs exactly the claimed scenarios through an **ephemeral projection**. It scrapes them from the Feature body into a temporary `.feature` file. When a Gherkin runner exists, it executes that file. Otherwise it verifies the scenarios interpretively. The skill commits no `.feature` file.

### Shipping and code review

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.create-pr` | "create a PR" | Open a PR with a description derived from the Trace, Feature, and Epic |
| `wtf.pr-review` | "review PR #42" | Review a PR's code against the linked Trace spec |

`wtf.create-pr` reads the full spec hierarchy and the branch diff. It writes a PR description that explains why the change exists. The base branch follows the delivery mode: the feature branch in `staged`, `main` in `trunk`. When another Trace PR of the Feature is open, a Trace targets the top of the Feature's stack instead. The skill links a stacked Trace PR into its native GitHub stack with `gh-stack`. It checks the verification status and offers to run `wtf.verify-trace` first.

`wtf.pr-review` reads the diff against the Trace's claimed scenarios, Contracts, and Impacted Areas. It checks spec adherence, contract compliance, test coverage, and code quality against `TECH.md`. It posts a GitHub PR review: approve, request changes, or comment.

The two verification skills differ. `wtf.verify-trace` is QA: it runs the software and checks the behavior. `wtf.pr-review` is a tech lead: it reads the code and checks it against the spec.

### Bugs and hotfixes

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.report-bug` | "report a bug" | File a structured Bug issue linked to the originating Trace |
| `wtf.hotfix` | "production is down", "emergency fix for #X" | Cut a hotfix branch from `main` and fix. Bypasses the planning hierarchy. |

`wtf.report-bug` records the failing Gherkin scenarios as reproducible evidence and links the originating Trace and Feature.

`wtf.hotfix` serves production incidents where the full flow is too slow. It cuts a `hotfix/<bug>-<slug>` branch from `main`, runs a targeted TDD fix, and opens a PR back to `main`. A scope gate redirects a large fix to the normal workflow. It offers a backport to release branches.

### Refinement, reflection, and health

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.refine` | "re-aim feature #12" | Update an existing Epic, Feature, or Trace from new insights. The single Re-aim mechanism. |
| `wtf.reflect` | "let's reflect" | Capture session learnings and route them into the steering docs |
| `wtf.health` | "project health check", "what's blocked" | Cross-issue status scan with actionable findings |

`wtf.refine` merges insights from the conversation, GitHub comments, and referenced docs. It re-validates only the affected sections and shows a section-by-section diff before it applies the update. It posts an audit-trail comment and cascades scenario edits to the Traces that claim them. `wtf.loop` runs it headless as the Re-aim step after each verified Trace.

`wtf.reflect` routes each learning into the right steering doc (TECH, QA, DESIGN, or VISION) under a "Hard-Won Lessons" section.

`wtf.health` scans all open Epics, Features, Traces (plus legacy Tasks), and Bugs against the expected lifecycle labels. It reports Traces implemented but not verified, Features with all Traces done but no PR, stale issues, and Bugs without a linked Trace. It ends with a triage list and offers to route each finding into the right skill.

### Release and closure

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.changelog` | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Traces and Features |
| `wtf.retro` | "run a retro on this epic", "close out the epic" | Close an Epic with a planned-versus-shipped comparison and routed learnings |

`wtf.changelog` reads the Gherkin `Then` steps and the Feature capability names. It writes plain-language release notes, not commit messages, to `CHANGELOG.md` or a GitHub Release.

`wtf.retro` compares the original Epic spec against what shipped, gathers learnings, and routes them into the steering docs through `wtf.reflect`. It closes the Epic and chains to `wtf.changelog`.
