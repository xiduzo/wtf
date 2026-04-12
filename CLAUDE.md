# WTF — Claude Code Instructions

## Canonical skill location

**Always edit skill files in `skills/`** — this is the source of truth.

The `.agents/skills/` and `.claude/skills/` directories are copies or symlinks used by the plugin runtime. Changes made there will not persist correctly. When modifying or creating a skill, always target:

```
skills/<skill-name>/SKILL.md
```

## Skill inventory

| Skill | File |
|---|---|
| wtf-create-pr | `skills/wtf-create-pr/SKILL.md` |
| wtf-design-task | `skills/wtf-design-task/SKILL.md` |
| wtf-epic-to-features | `skills/wtf-epic-to-features/SKILL.md` |
| wtf-feature-to-tasks | `skills/wtf-feature-to-tasks/SKILL.md` |
| wtf-implement-task | `skills/wtf-implement-task/SKILL.md` |
| wtf-loop | `skills/wtf-loop/SKILL.md` |
| wtf-refine | `skills/wtf-refine/SKILL.md` |
| wtf-reflect | `skills/wtf-reflect/SKILL.md` |
| wtf-report-bug | `skills/wtf-report-bug/SKILL.md` |
| wtf-setup | `skills/wtf-setup/SKILL.md` |
| wtf-steer-design | `skills/wtf-steer-design/SKILL.md` |
| wtf-steer-qa | `skills/wtf-steer-qa/SKILL.md` |
| wtf-steer-tech | `skills/wtf-steer-tech/SKILL.md` |
| wtf-steer-vision | `skills/wtf-steer-vision/SKILL.md` |
| wtf-verify-task | `skills/wtf-verify-task/SKILL.md` |
| wtf-write-epic | `skills/wtf-write-epic/SKILL.md` |
| wtf-write-feature | `skills/wtf-write-feature/SKILL.md` |
| wtf-write-task | `skills/wtf-write-task/SKILL.md` |

## Skill invocation policy

**Never invoke wtf skills automatically.** Skills in this project are only activated when the user explicitly triggers them via a `/` slash command (e.g. `/wtf.loop`, `/wtf.write-task`). Do not auto-trigger any wtf skill based on inferred intent, conversation context, or keywords.

## Shared references

Cross-skill references (gh-setup, issue templates, DDD rules, etc.) live in `skills/references/`.
