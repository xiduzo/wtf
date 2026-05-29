# gh Body Helper

Single source of truth for **reading and writing GitHub issue / PR bodies** from any wtf skill. Use it for every body round-trip so multi-line UTF-8 content survives on every platform — especially Windows, where raw `gh` under PowerShell corrupts bodies three ways: CP850 console mojibake, newline collapse on variable capture, and inline-`--body` re-encoding.

The helper is `gh-body.py`, a small stdlib-only Python utility. `wtf.setup` copies it into the repo at **`.wtf/gh-body.py`** so the guard is committed and travels with the repo for every teammate. See `../wtf.setup/hooks/gh-body.py` for the source and the full rationale.

## Invocation

```bash
python3 .wtf/gh-body.py <read|create|edit> ...
```

`wtf.setup` smoke-tests this exact `python3 .wtf/gh-body.py` invocation and reports `verified` / `wrong-name` / `no-python`. On Windows the python.org installer provides `python`/`py` rather than `python3` — if setup reports `wrong-name`, add a `python3` alias/shim (or substitute `python`/`py -3` in these commands). The script itself is identical on all platforms; only the launcher name differs.

## When the helper is present (the normal path)

**Create** an issue or PR. Write the filled body to a temp file with the **Write tool** first (the helper re-encodes it to UTF-8 no-BOM), then:

```bash
# Issue:
python3 .wtf/gh-body.py create --title "<emoji> <Type>: <title>" --body-file "$BODY" --label "<label>"
# PR (add --pr and a base branch):
python3 .wtf/gh-body.py create --pr --title "<title>" --body-file "$BODY" --base "<base_branch>"
```

The helper prints `gh`'s own output (the created URL). Any extra flags — `--assignee`, `--milestone`, `--repo`, … — are forwarded verbatim to `gh`.

**Read → modify → write** (update one section of an existing body without clobbering the rest):

```bash
# 1. Fetch the current body to a UTF-8 temp file; the helper prints its path on stdout.
python3 .wtf/gh-body.py read <number>           # add --pr for a PR
# 2. Read that path with the Read tool, then replace ONLY the target section
#    with the Write or Edit tool. Never reconstruct the whole body from scratch.
# 3. Push it back:
python3 .wtf/gh-body.py edit <number> --body-file "<path-from-step-1>"   # add --pr for a PR
```

Rules:

- **Never capture a body into a shell variable** (`BODY=$(gh issue view …)`) — that is the newline-collapse bug. Always go through `read` → temp file → Read tool.
- **Always read before writing** — never assume the current body matches the original draft.
- A second write in the same run (e.g. updating Test Mapping after Technical Approach) must re-`read` rather than reuse the earlier temp file, since other sections may have changed in between.
- `read` uses `mkstemp`, so each call yields a unique path — parallel runs never collide and you do not need to hand-roll `$(date +%s)` names.

## Comments, PR reviews, and releases

Three more body-bearing `gh` commands go through the same guard — never post these inline with `--body "..."` (that is the failure mode the helper exists to prevent). Write the comment/body/notes to a temp file with the Write tool first, then:

```bash
# Add a comment to an issue (or a PR with --pr):
python3 .wtf/gh-body.py comment <number> --body-file "$COMMENT"

# Post a PR review (the verdict flag is forwarded to gh pr review):
python3 .wtf/gh-body.py review <pr_number> --request-changes --body-file "$BODY"

# Create a release from a notes file:
python3 .wtf/gh-body.py release <tag> --title "<title>" --notes-file "$NOTES"
```

## Fallback when the helper is absent

If `.wtf/gh-body.py` does not exist (the repo has not run `wtf.setup` since this guard shipped), fall back to raw `gh` with `--body-file` (write the body with the Write tool, never inline `--body`, never capture into a variable):

```bash
gh issue create --title "…" --body-file "$BODY" --label "…"
gh issue view <n> --json body -q .body > "$BODY" && gh issue edit <n> --body-file "$BODY"
```

This works on macOS/Linux. **On Windows it is unguarded** — bodies with emoji or accented domain language may corrupt. In that case, tell the user to run `/wtf.setup` to install the helper, then retry.
