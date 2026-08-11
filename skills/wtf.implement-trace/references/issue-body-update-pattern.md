# Issue Body Update Pattern

Use this pattern whenever you need to update a section of a GitHub issue body without overwriting the rest. All body reads and writes go through the **gh body helper** so multi-line UTF-8 content survives on every platform — see `../../references/gh-body-helper.md`.

## Steps

1. Fetch the current body to a UTF-8 temp file. The helper prints the temp file's path on stdout:

   ```bash
   python3 .wtf/gh-body.py read <issue_number>
   ```

2. Read that path with the Read tool, then replace only the target section with the Write or Edit tool — do not manually construct the full body from scratch, as other sections may have changed since the issue was created.

3. Push the updated body back:

   ```bash
   python3 .wtf/gh-body.py edit <issue_number> --body-file "<path-from-step-1>"
   ```

## Notes

- Always read before writing — never assume the current body matches the original draft.
- **Never capture a body into a shell variable** (`BODY=$(gh issue view …)`) — PowerShell joins multi-line output with spaces and destroys the body. Always go through `read` → temp file → Read tool.
- The second write in a run (e.g. step 9 updating Test Mapping after step 6 updated Technical Approach) must re-`read` the body rather than reusing the temp file from the earlier step, since other sections may have been updated in between.
- `read` uses `mkstemp`, so every call yields a unique path — parallel runs never collide; no need to hand-roll names with the issue number or `$(date +%s)`.
- If `.wtf/gh-body.py` is absent, use the raw-`gh` fallback in `../../references/gh-body-helper.md` (unguarded on Windows).
