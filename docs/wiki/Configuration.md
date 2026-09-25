# Configuration

`wtf.setup` records four choices in `.wtf/config.json`. Commit the file so every teammate uses the same settings.

| Key | Values | Meaning |
| --- | --- | --- |
| `classification` | `types` / `labels` | How an issue gets its kind: native GitHub issue types in orgs, labels everywhere else |
| `planning` | `guided` / `flow` | `guided` asks step by step. `flow` derives what it can and shows one consolidated review before it creates anything. Both modes run the same quality gates. |
| `feature_scope` | `single-story` / `grouped` | One user story per Feature, or several |
| `delivery` | `staged` / `trunk` | `staged`: Trace PRs merge into the feature branch, then the feature branch merges into `main`. `trunk`: Trace PRs merge into `main` directly. |

Override the planning mode per invocation, for example `/wtf.epic-to-features 42 flow`.

A Feature can override the `delivery` mode for itself. [Delivery and stacks](Delivery-and-Stacks.md) shows both modes as git graphs.
