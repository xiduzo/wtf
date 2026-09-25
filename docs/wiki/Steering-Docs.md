# Steering docs

Steering docs are living guideline documents in `docs/steering/`. They inform every issue, design, and review that WTF writes.

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.steer-vision` | "create the vision doc" | Product constitution: purpose, users, principles |
| `wtf.steer-tech` | "create the tech doc" | Stack, architecture, constraints, ADRs |
| `wtf.steer-design` | "create the design doc" | Design principles, tokens, component patterns |
| `wtf.steer-qa` | "create the QA doc" | Test strategy, coverage thresholds, Definition of Done |

Each skill researches the codebase first and asks only about the gaps. The skills chain to each other, so one session can set up all four. They also offer to sync the doc to your project's GitHub wiki.

## Learnings flow back in

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `wtf.reflect` | "let's reflect" | Capture session learnings and route them into the steering docs |

`wtf.reflect` routes each learning into the right steering doc (TECH, QA, DESIGN, or VISION) under a "Hard-Won Lessons" section.

The intervention-tracker hook counts your corrections during a session. When they pile up, it suggests `/wtf.reflect`. `wtf.retro` also routes the learnings of a closed Epic through `wtf.reflect`. See [Release and closure](Release-and-Closure.md).
