# Configuration

`wtf.setup` records four choices in `.wtf/config.json`. Commit the file to give each teammate the same settings.

| Key | Values | Meaning |
| --- | --- | --- |
| `classification` | `types` / `labels` | How WTF marks the kind of an issue. `types` uses native GitHub issue types (organizations only). `labels` uses labels. |
| `planning` | `guided` / `flow` | `guided` asks step by step. `flow` derives what it can and shows one consolidated review before it creates anything. Both modes run the same quality gates. |
| `feature_scope` | `single-story` / `grouped` | One user story per Feature, or more than one |
| `delivery` | `staged` / `trunk` | `staged`: Trace PRs merge into the feature branch. Then the feature branch merges into `main`. `trunk`: Trace PRs merge into `main` directly. |

To change the planning mode for one run, add the mode as an argument. For example: `/wtf.epic-to-features 42 flow`.

A Feature can override the `delivery` mode for itself. [Delivery and stacks](Delivery-and-Stacks.md) shows the two modes as git graphs.
