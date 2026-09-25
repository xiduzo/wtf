# Steering docs

Steering docs are guideline documents in `docs/steering/`. You update them when the project changes. They guide each issue, design, and review that WTF writes.

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.steer-vision` | "create the vision doc" | Product constitution: purpose, users, principles |
| `wtf.steer-tech` | "create the tech doc" | Stack, architecture, constraints, architecture decisions |
| `wtf.steer-design` | "create the design doc" | Design principles, tokens, component patterns |
| `wtf.steer-qa` | "create the QA doc" | Test strategy, coverage thresholds, Definition of Done |

Each skill researches the codebase first. Then it asks only about the gaps. Each skill offers to start the next one, so one session can create all four docs. The skills also offer to sync each doc to the GitHub wiki of your project.

## Learnings

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.reflect` | "let's reflect" | Capture session learnings and add them to the steering docs |

`wtf.reflect` adds each learning to the correct steering doc (TECH, QA, DESIGN, or VISION). It puts the learning under a "Hard-Won Lessons" section.

The intervention-tracker hook counts your corrections during a session. When the count gets high, the hook suggests `/wtf.reflect`. `wtf.retro` also sends the learnings of a closed Epic through `wtf.reflect`. See [Release and closure](Release-and-Closure.md).
