# WTF — Claude Code Instructions

## Repo layout

- `skills/` — **source of truth** for all skill definitions. Always edit here.
- `skills/references/` — cross-skill reference docs (see below).
- `skills/wtf.setup/hooks/` — shipped hook scripts (installed into `settings.json` by `wtf.setup`).
- `docs/` — project docs, including `docs/steering/` (VISION, TECH, QA, DESIGN) and `docs/spikes/`.
- `.claude/skills/` — symlinked mirror used by the Claude Code plugin runtime. **Never edit.** Regenerate from `skills/` if stale.

## Canonical skill location

Edit skill files in `skills/<skill-name>/SKILL.md`. Any other path is a runtime artifact.

## Skill inventory

| Skill | File |
|---|---|
| wtf.changelog | `skills/wtf.changelog/SKILL.md` |
| wtf.create-pr | `skills/wtf.create-pr/SKILL.md` |
| wtf.design-feature | `skills/wtf.design-feature/SKILL.md` |
| wtf.design-task | `skills/wtf.design-task/SKILL.md` |
| wtf.epic-to-features | `skills/wtf.epic-to-features/SKILL.md` |
| wtf.feature-to-tasks | `skills/wtf.feature-to-tasks/SKILL.md` |
| wtf.health | `skills/wtf.health/SKILL.md` |
| wtf.hotfix | `skills/wtf.hotfix/SKILL.md` |
| wtf.implement-task | `skills/wtf.implement-task/SKILL.md` |
| wtf.loop | `skills/wtf.loop/SKILL.md` |
| wtf.pr-review | `skills/wtf.pr-review/SKILL.md` |
| wtf.refine | `skills/wtf.refine/SKILL.md` |
| wtf.reflect | `skills/wtf.reflect/SKILL.md` |
| wtf.report-bug | `skills/wtf.report-bug/SKILL.md` |
| wtf.retro | `skills/wtf.retro/SKILL.md` |
| wtf.setup | `skills/wtf.setup/SKILL.md` |
| wtf.spike | `skills/wtf.spike/SKILL.md` |
| wtf.steer-design | `skills/wtf.steer-design/SKILL.md` |
| wtf.steer-qa | `skills/wtf.steer-qa/SKILL.md` |
| wtf.steer-tech | `skills/wtf.steer-tech/SKILL.md` |
| wtf.steer-vision | `skills/wtf.steer-vision/SKILL.md` |
| wtf.verify-task | `skills/wtf.verify-task/SKILL.md` |
| wtf.write-epic | `skills/wtf.write-epic/SKILL.md` |
| wtf.write-feature | `skills/wtf.write-feature/SKILL.md` |
| wtf.write-task | `skills/wtf.write-task/SKILL.md` |

Keep this table in sync with `skills/` when adding/removing skills.

## Skill invocation policy

**Never invoke wtf skills automatically.** Only activate on explicit `/` slash command (e.g. `/wtf.loop`, `/wtf.write-task`). Do not auto-trigger from inferred intent, conversation context, or keywords — even when the user's phrasing matches a skill's description.

## Shared references

Cross-skill references live in `skills/references/`:

| File | Purpose |
|---|---|
| `branch-setup.md` | Trunk-based branch hierarchy, slug rules, worktree policy |
| `commit-conventions.md` | Commit message format used across skills |
| `conflict-graph.md` | Dependency / file-conflict model for parallel task execution |
| `ddd-writing-rules.md` | Ubiquitous-language rules for issue/Gherkin authoring |
| `gh-setup.md` | `gh` CLI + extension install + sub-issue/dependency cookbook |
| `issue-template-loading.md` | Template verify + halt-or-setup + body-file create pattern |
| `lifecycle-labels.md` | Label semantics + absent/overwrite gate templates |
| `questioning-style.md` | How skills should prompt the user |
| `scope-gates.md` | Definition-of-Ready / Definition-of-Done gates |
| `spec-hierarchy.md` | Task → Feature → Epic traversal (extension + body-scrape) |
| `steering-doc-process.md` | How steering docs are created, refined, and consumed |
| `subagent-protocol.md` | Contract for subagent delegation |

Reference these from skills rather than duplicating content.

## Hooks

`skills/wtf.setup/hooks/track-interventions.sh` rides along inside the `wtf.setup` skill payload. The `wtf.setup` skill registers it into the user's `~/.claude/settings.json` or the repo's `.claude/settings.json` for `UserPromptSubmit` + `Stop` events. Counts user corrections and nudges toward `/wtf.reflect` when they accumulate. Do not bypass.
