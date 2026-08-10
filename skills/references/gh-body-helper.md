# gh Body Helper

Single source of truth for **reading and writing GitHub issue / PR bodies** from any wtf skill. Use it for every body round-trip. Multi-line UTF-8 content then survives on every platform. Windows needs this most.

Raw `gh` under PowerShell corrupts bodies three ways. First: CP850 console mojibake. Second: newline collapse on variable capture. Third: inline-`--body` re-encoding.

The helper is `gh-body.py`. It is a small stdlib-only Python utility. `wtf.setup` copies it into the repo at **`.wtf/gh-body.py`**. The guard is committed and travels with the repo for every teammate. See `../wtf.setup/hooks/gh-body.py` for the source and the full rationale.

## Invocation

```bash
python3 .wtf/gh-body.py <read|create|edit> ...
```

`wtf.setup` smoke-tests this exact `python3 .wtf/gh-body.py` invocation. It reports `verified` / `wrong-name` / `no-python`. On Windows the python.org installer provides `python`/`py` rather than `python3`. If setup reports `wrong-name`, add a `python3` alias or shim. Or substitute `python`/`py -3` in these commands. The script itself is identical on all platforms. Only the launcher name differs.

## When the helper is present (the normal path)

**Create** an issue or PR. Write the filled body to a temp file with the **Write tool** first. The helper re-encodes it to UTF-8 no-BOM. Then:

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

- **Never capture a body into a shell variable** (`BODY=$(gh issue view …)`). That is the newline-collapse bug. Always go through `read` → temp file → Read tool.
- **Always read before writing**. Never assume the current body matches the original draft.
- A second write in the same run must re-`read`. Do not reuse the earlier temp file. Other sections may have changed. Example: update Test Mapping after Technical Approach.
- `read` uses `mkstemp`. Each call yields a unique path. Parallel runs never collide. You do not need to hand-roll `$(date +%s)` names.

## Comments, PR reviews, and releases

Three more body-bearing `gh` commands go through the same guard. Never post these inline with `--body "..."`. That is the failure mode the helper exists to prevent. Write the comment, body, or notes to a temp file with the Write tool first. Then:

```bash
# Add a comment to an issue (or a PR with --pr):
python3 .wtf/gh-body.py comment <number> --body-file "$COMMENT"

# Post a PR review (the verdict flag is forwarded to gh pr review):
python3 .wtf/gh-body.py review <pr_number> --request-changes --body-file "$BODY"

# Create a release from a notes file:
python3 .wtf/gh-body.py release <tag> --title "<title>" --notes-file "$NOTES"
```

## Fallback when the helper is absent

If `.wtf/gh-body.py` does not exist, the repo has not run `wtf.setup` since this guard shipped. Fall back to raw `gh` with `--body-file`. Write the body with the Write tool. Never use inline `--body`. Never capture into a variable:

```bash
gh issue create --title "…" --body-file "$BODY" --label "…"
gh issue view <n> --json body -q .body > "$BODY" && gh issue edit <n> --body-file "$BODY"
```

This works on macOS/Linux. **On Windows it is unguarded**. Bodies with emoji or accented domain language may corrupt. In that case, tell the user to run `/wtf.setup` to install the helper. Then retry.
