# Skill reference

This table lists each skill, grouped by phase. The linked page gives the details.

| Skill | Trigger | Purpose | Page |
| --- | --- | --- | --- |
| `wtf.setup` | "set up wtf" | Pre-flight check and installer. Run it once per repo. | [Getting started](Getting-Started.md) |
| `wtf.steer-vision` | "create the vision doc" | Product constitution: purpose, users, principles | [Steering docs](Steering-Docs.md) |
| `wtf.steer-tech` | "create the tech doc" | Stack, architecture, constraints, architecture decisions | [Steering docs](Steering-Docs.md) |
| `wtf.steer-design` | "create the design doc" | Design principles, tokens, component patterns | [Steering docs](Steering-Docs.md) |
| `wtf.steer-qa` | "create the QA doc" | Test strategy, coverage thresholds, Definition of Done | [Steering docs](Steering-Docs.md) |
| `wtf.spike` | "run a spike on X" | A time-boxed technical investigation before you select an approach | [Planning](Planning.md) |
| `wtf.write-epic` | "create an epic" | Define a strategic initiative | [Planning](Planning.md) |
| `wtf.write-feature` | "create a feature" | Describe one user-facing capability with its stories and Gherkin | [Planning](Planning.md) |
| `wtf.write-trace` | "create a trace" | Claim the scenarios of one story as one implementation pass | [Planning](Planning.md) |
| `wtf.epic-to-features` | "break down this epic" | Propose and create all Features for an Epic | [Planning](Planning.md) |
| `wtf.feature-to-traces` | "plan all traces for feature #12" | Validate the Trace Plan and create all Traces for a Feature | [Planning](Planning.md) |
| `wtf.design-feature` | "design feature #12" | Map the full UX flow for a Feature and write the Design Handoff | [Planning](Planning.md) |
| `wtf.refine` | "re-aim feature #12" | Update an Epic, Feature, or Trace from new insights | [Planning](Planning.md) |
| `wtf.loop` | "go", "start building", "build it all" | Chain implement → verify → PR → re-aim for every Trace, Skeleton first | [Autonomous execution](Autonomous-Execution.md) |
| `wtf.design-trace` | "design trace #42" | Map the claimed scenarios to Figma frames and component specs | [Running Traces](Running-Traces.md) |
| `wtf.implement-trace` | "implement trace #42" | Draft the technical approach and drive TDD over the Scenario Claim | [Running Traces](Running-Traces.md) |
| `wtf.verify-trace` | "verify trace #42" | Run the claimed scenarios and record a pass or fail verdict | [Running Traces](Running-Traces.md) |
| `wtf.create-pr` | "create a PR" | Open a PR with a description derived from the Trace, Feature, and Epic | [Running Traces](Running-Traces.md) |
| `wtf.pr-review` | "review PR #42" | Review the code of a PR against the linked Trace spec | [Running Traces](Running-Traces.md) |
| `wtf.report-bug` | "report a bug" | File a structured Bug issue linked to the originating Trace | [Bugs and hotfixes](Bugs-and-Hotfixes.md) |
| `wtf.hotfix` | "production is down", "emergency fix for #X" | Create a hotfix branch from `main` and fix the problem. Skips the planning hierarchy. | [Bugs and hotfixes](Bugs-and-Hotfixes.md) |
| `wtf.reflect` | "let's reflect" | Capture session learnings and add them to the steering docs | [Steering docs](Steering-Docs.md) |
| `wtf.changelog` | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Traces and Features | [Release and closure](Release-and-Closure.md) |
| `wtf.retro` | "run a retro on this epic", "close out the epic" | Close an Epic with a comparison of the plan and the result, and add the learnings to the steering docs | [Release and closure](Release-and-Closure.md) |
| `wtf.health` | "project health check", "what's blocked" | Scan the status of all issues and list the problems to fix | [Release and closure](Release-and-Closure.md) |
| `ste-writing` | "make this plain" | Rewrite prose into ASD-STE100 Simplified Technical English. WTF skills apply the same rules to issue and PR bodies. | — |
