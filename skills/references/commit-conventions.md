# Commit and PR Conventions

Unified rules for commit messages, PR titles, and issue-closing syntax across all wtf skills.

## Commit messages

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

**Subject:** `<type>(<scope>): <description>`

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`
- Scope: optional noun in parentheses describing the codebase section (e.g. `feat(auth):`)
- Description: lowercase, imperative mood, no trailing period
- Breaking change: append `!` after type/scope (e.g. `feat!:` or `feat(auth)!:`)
- Total subject under 72 characters

**Body** (optional — include when the "why" is not obvious from the subject):

- Wrap at 72 columns
- Explain motivation and trade-offs, not what the diff already shows

**Trailers:**

| Trailer | Used in |
|---|---|
| `Task: #<task_number>` | Regular implementation commits (`wtf.implement-task`) |
| `Bug: #<bug_number>` | Hotfix commits (`wtf.hotfix`) |
| `Scenario: <scenario name>` | Atomic commits that complete a specific Gherkin scenario during the TDD cycle |

Do NOT put `Closes #<n>` in commit messages. Issue closure happens via the PR body — see below. This keeps the audit trail consistent: every closed issue has a merged PR that references it explicitly.

## PR titles

Same Conventional Commits format as commit subjects. One PR corresponds to one logical change; the PR title is the authoritative summary.

## PR bodies — issue closure

Closure keywords live in the PR body, one per line — never comma-separated, because GitHub only parses the first reference in a comma-separated line.

```
Closes #42
Closes #15
```

Rules:

- Task PRs always include `Closes #<task_number>`.
- Feature PRs always include `Closes #<feature_number>` plus one `Closes #<task_number>` line per closed task.
- Epic closure chains automatically from Feature PRs that include `Closes #<epic_number>`.
- Hotfix PRs always include `Closes #<bug_number>`.

## When to close directly

Direct `gh issue close` is reserved for:

- `--reason "not planned"` — explicitly won't implement
- `--reason "duplicate"` — duplicate of another issue

Never call `gh issue close` to mark completed work — that breaks the merged-PR audit trail.
