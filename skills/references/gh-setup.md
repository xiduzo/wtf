# GitHub CLI Setup

Run this check at the start of any wtf skill that creates or links GitHub issues. Every calling skill has an identical step 0:

```
### 0. GitHub CLI setup

Run `../references/gh-setup.md`. Stop if `gh` is not installed or not authenticated.
```

## When to skip

Skip this entire step if **any** of the following is true:

- The calling orchestrator already ran gh-setup this session (e.g. `wtf.epic-to-features` → `wtf.write-feature`, `wtf.implement-task` → `wtf.verify-task`). The orchestrator passes along the confirmation implicitly by not re-asking.
- A prior wtf skill in the same session ran gh-setup and succeeded.
- The skill is re-invoking itself in a loop (e.g. "Write next Task" → restart from step 2).

## Which sections apply to which skills

- **Sections 1–2 (install + auth):** all skills — hard stop if either fails.
- **Sections 3–4 (extensions):** only skills that create or traverse native sub-issue/dependency links (`wtf.write-epic`, `wtf.write-feature`, `wtf.write-task`, `wtf.loop`, `wtf.refine`, `wtf.epic-to-features`, `wtf.feature-to-tasks`). Other skills (`wtf.verify-task`, `wtf.create-pr`, `wtf.report-bug`, `wtf.design-task`, `wtf.design-feature`, `wtf.pr-review`, `wtf.changelog`, `wtf.spike`, `wtf.retro`, `wtf.health`, `wtf.hotfix`) may skip these — they do not rely on the extensions.
- **Section 5 (repo detect):** run if the skill needs the `<owner>/<repo>` pair (wiki sync, repo-scoped queries).

## 1. Verify `gh` is installed

```bash
gh --version
```

If not found: tell the user `gh` CLI is required and link them to https://cli.github.com. Stop — do not proceed.

## 2. Verify `gh` is authenticated

```bash
gh auth status
```

If not authenticated: tell the user to run `gh auth login` and stop. Do not proceed until authentication is confirmed.

## 3. Check and install required extensions

```bash
gh extension list
```

Check the output for both of the following extensions. For each that is missing, install it:

```bash
# Sub-issue hierarchy (epic → feature → task)
gh extension install yahsan2/gh-sub-issue

# Issue dependency tracking (X blocks Y)
gh extension install xiduzo/gh-issue-dependency
```

If installation fails (e.g. network error, permissions), warn the user that relationship tracking is unavailable until the extension is installed. **Do not fall back to writing `Depends on #X` or `Blocks #Y` into issue bodies** — body-text relationship references are not used in this workflow.

After this step, record two booleans for use in the rest of the session:
- `gh-sub-issue-available`: true if `yahsan2/gh-sub-issue` is installed and working
- `gh-issue-dependency-available`: true if `xiduzo/gh-issue-dependency` is installed and working

All callers reference these flags when deciding whether to create native links.

## 4. Confirm command syntax (first install only)

After installing an extension for the first time, verify the available commands:

```bash
gh sub-issue --help
gh issue-dependency --help
```

Skip this step on subsequent sessions if the extensions were already confirmed working. Use the output to confirm the exact flag names. The reference signatures below are expected but may vary by extension version:

```md
List issues related to the specified issue based on relationship type.

Supports multiple output formats:
- Colored output for terminal (TTY)
- Plain text for scripts (non-TTY)
- JSON for programmatic use (--json)

Examples:
  # List child sub-issues for issue #123 (default)
  gh sub-issues list 123
  
  # List parent issue for sub-issue #456
  gh sub-issues list 456 --relation parent
  
  # List sibling issues for sub-issue #789
  gh sub-issues list 789 --relation siblings
  
  # List with URL
  gh sub-issues list https://github.com/owner/repo/issues/123
  
  # Filter by state
  gh sub-issues list 123 --state closed
  
  # JSON output with selected fields
  gh sub-issues list 123 --json number,title,state
  
  # JSON output with parent and meta info
  gh sub-issues list 123 --json parent.number,parent.title,total,openCount
  
  # Limit results
  gh sub-issues list 123 --limit 10

Usage:
  gh-sub-issue list <issue> [flags]

Flags:
  -h, --help              help for list
      --json string       Output JSON with the specified fields
  -L, --limit int         Maximum number of issues to display (default 30)
      --relation string   Relation type: {children|parent|siblings} (default "children")
  -R, --repo string       Repository in OWNER/REPO format
  -s, --state string      Filter by state: {open|closed|all} (default "open")
  -w, --web               Open in web browser
```

```md
Add a dependency relationship between two issues using GitHub's native dependency API.

RELATIONSHIP TYPES
You must specify exactly one of the following relationship types:

  --blocked-by   The specified issue is blocked by other issues
                 (those issues must be completed first)

  --blocks       The specified issue blocks other issues
                 (this issue must be completed before those issues)

ISSUE REFERENCES
Issues can be referenced in multiple ways:
  • Simple number: 123 (same repository)
  • Full reference: owner/repo#123 (cross-repository)
  • Multiple issues: 123,456,789 (comma-separated, no spaces)

VALIDATION
The command validates that:
  • All referenced issues exist and are accessible
  • You have permission to modify the specified issues
  • The dependency relationship doesn't create cycles

FLAGS
  --blocked-by string   Issue number(s) that block this issue (comma-separated)
  --blocks string       Issue number(s) that this issue blocks (comma-separated)

Usage:
  gh-issue-dependency add <issue-number> [flags]

Examples:
  # Make issue #123 depend on issue #456
  gh issue-dependency add 123 --blocked-by 456

  # Make issue #123 block issue #789
  gh issue-dependency add 123 --blocks 789

  # Add cross-repository dependency
  gh issue-dependency add 123 --blocked-by owner/other-repo#456

  # Add multiple dependencies at once
  gh issue-dependency add 123 --blocked-by 456,789,101

  # Work with issues in a different repository
  gh issue-dependency add 123 --blocks 456 --repo owner/other-repo

Flags:
      --blocked-by string   Issue number(s) that block this issue (comma-separated)
      --blocks string       Issue number(s) that this issue blocks (comma-separated)
  -h, --help                help for add

Global Flags:
  -R, --repo string   Select another repository using the [HOST/]OWNER/REPO format
```

If the `--help` output shows different flags, use those instead.

## 5. Detect repo context

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

Store the result as `<owner>/<repo>` for use in all subsequent extension calls in this session.
