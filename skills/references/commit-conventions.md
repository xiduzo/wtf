# Commit and PR Conventions

Unified rules for commit messages, PR titles, and issue-closing syntax across all wtf skills.

## Commit messages

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

**Subject:** `<type>(<scope>): <description>`

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `chore`, `ci`
- Scope: optional noun in parentheses that names the codebase section (e.g. `feat(auth):`)
- Description: lowercase, imperative mood, no trailing period
- Breaking change: append `!` after type/scope (e.g. `feat!:` or `feat(auth)!:`)
- Keep the full subject under 72 characters
- Free-text description and body prose follow strict STE per `ste-writing.md` (keep the `type` / `(scope)` / `!` prefix as-is)

**Body** (optional — include when the subject does not make the "why" clear):

- Wrap at 72 columns
- Explain motivation and trade-offs. Do not restate what the diff already shows.
- Apply `ste-writing.md` to the body prose

**Trailers:**

| Trailer | Used in |
|---|---|
| `Trace: #<trace_number>` | Regular implementation commits (`wtf.implement-trace`) |
| `Bug: #<bug_number>` | Hotfix commits (`wtf.hotfix`) |
| `Scenario: <scenario name>` | Atomic commits that complete one scenario from the Trace's Scenario Claim during the TDD cycle |

Do NOT put `Closes #<n>` in commit messages. Close issues via the PR body — see below. This keeps the audit trail consistent. Every closed issue then has a merged PR that names it.

## PR titles

Use the same Conventional Commits format as commit subjects. One PR maps to one logical change. The PR title is the authoritative summary.

## PR bodies — issue closure

Put closure keywords in the PR body, one per line. Never use comma-separated lists. GitHub parses only the first reference on a comma-separated line.

```
Closes #42
Closes #15
```

Rules:

- Trace PRs always include `Closes #<trace_number>`.
- In `staged` delivery, feature PRs include `Closes #<feature_number>` plus one `Closes #<trace_number>` line per completed Trace.
- In `trunk` delivery, there is no feature PR. The final Trace PR — the one that exhausts the Trace Plan — also includes `Closes #<feature_number>`. The merged-PR audit trail stays intact.
- Epic closure chains automatically from the PR that closes the Epic's final Feature and includes `Closes #<epic_number>`.
- Hotfix PRs always include `Closes #<bug_number>`.

## When to close directly

Reserve direct `gh issue close` for:

- `--reason "not planned"` — work that will not be implemented
- `--reason "duplicate"` — duplicate of another issue

Never call `gh issue close` to mark completed work. That breaks the merged-PR audit trail.
