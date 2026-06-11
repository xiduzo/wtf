# Issue Template Loading

Shared procedure for any wtf skill that creates a GitHub issue from a template (`wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`, `wtf.report-bug`) or a PR from a template (`wtf.create-pr`).

## Templates by skill

| Skill | Template path |
|---|---|
| `wtf.write-epic` | `.github/ISSUE_TEMPLATE/EPIC.md` |
| `wtf.write-feature` | `.github/ISSUE_TEMPLATE/FEATURE.md` |
| `wtf.write-task` | `.github/ISSUE_TEMPLATE/TASK.md` |
| `wtf.report-bug` | `.github/ISSUE_TEMPLATE/BUG.md` |
| `wtf.create-pr` | `.github/pull_request_template.md` |

## 1. Verify the template exists

Before drafting, use the Read tool to verify the relevant template path exists.

## 2. Halt or run setup if missing

If the template is missing, apply `./questioning-style.md` and ask "`<TEMPLATE_PATH>` is missing. How would you like to proceed?" — header `Template missing`:

- **Run `/wtf.setup`** → invoke `wtf.setup` to scaffold all templates, then halt this skill so the user can re-invoke it
- **Cancel** → halt without scaffolding

Both branches halt the current skill. Do not fall back to drafting without the template — section names and structure are the contract that downstream skills consume.

## 3. Read the template body

Use only the markdown body **below the second `---` delimiter**. Ignore the YAML frontmatter at the top — it is GitHub issue-form metadata, not part of the body the user sees in the rendered issue.

## 4. Fill placeholders

Replace every `[PLACEHOLDER]` (or any section the template treats as fillable) with the gathered context. Preserve every section heading and structural element exactly — downstream skills parse these by name.

## 5. Write the body to a temp file, then create via the gh body helper

Multi-line bodies must go through a temp file (never an inline `--body`), and every create must go through the **gh body helper** so UTF-8 content survives on Windows. See `./gh-body-helper.md`.

1. Use the Write tool to write the filled body to a temp file `$BODY` (any path under the OS temp dir).
2. Create through the helper:

   ```bash
   # Issue:
   python3 .wtf/gh-body.py create --title "<emoji> <Type>: <title>" --body-file "$BODY" --label "<label>"

   # PR (add --pr and a base branch):
   python3 .wtf/gh-body.py create --pr --title "<title>" --body-file "$BODY" --base "<base_branch>"
   ```

If `.wtf/gh-body.py` is absent (repo hasn't run `wtf.setup` since the guard shipped), use the raw-`gh` fallback documented in `./gh-body-helper.md` — works on macOS/Linux, unguarded on Windows.

The exact title prefix (`🎯 Epic:`, `🚀 Feature:`, `🛠 Task:`, `🐞 Bug:`) and label name are skill-specific — see each skill's create step. The Read → Write-temp → helper pattern is universal.
