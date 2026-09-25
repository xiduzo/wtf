# Release and closure

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.changelog` | "write the changelog", "generate release notes" | Derive user-facing release notes from closed Traces and Features |
| `wtf.retro` | "run a retro on this epic", "close out the epic" | Close an Epic with a comparison of the plan and the result, and add the learnings to the steering docs |
| `wtf.health` | "project health check", "what's blocked" | Scan the status of all issues and list the problems to fix |

## Changelog

`wtf.changelog` reads the Gherkin `Then` steps and the names of the Feature capabilities. It writes plain-language release notes, not commit messages, to `CHANGELOG.md` or a GitHub Release.

## Retro

`wtf.retro` compares the Epic spec with what shipped. It gathers the learnings and sends them to the [steering docs](Steering-Docs.md) through `wtf.reflect`. Then it closes the Epic and offers to run `wtf.changelog`.

## Health check

Run `wtf.health` at any time, on any scope. It compares all open Epics, Features, Traces, and Bugs with the expected lifecycle labels. It reports these problems:

- Traces that are implemented but not verified
- Features with all Traces done but no PR
- Stale issues
- Bugs without a linked Trace

It ends with a triage list. For each finding, it offers to start the correct skill.
