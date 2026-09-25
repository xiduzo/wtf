# Release and closure

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.changelog` | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Traces and Features |
| `wtf.retro` | "run a retro on this epic", "close out the epic" | Close an Epic with a planned-versus-shipped comparison and routed learnings |
| `wtf.health` | "project health check", "what's blocked" | Cross-issue status scan with actionable findings |

## Changelog

`wtf.changelog` reads the Gherkin `Then` steps and the Feature capability names. It writes plain-language release notes, not commit messages, to `CHANGELOG.md` or a GitHub Release.

## Retro

`wtf.retro` compares the original Epic spec against what shipped, gathers learnings, and routes them into the [steering docs](Steering-Docs.md) through `wtf.reflect`. It closes the Epic and chains to `wtf.changelog`.

## Health check

Run `wtf.health` at any time, on any scope. It scans all open Epics, Features, Traces (plus legacy Tasks), and Bugs against the expected lifecycle labels. It reports Traces implemented but not verified, Features with all Traces done but no PR, stale issues, and Bugs without a linked Trace. It ends with a triage list and offers to route each finding into the right skill.
