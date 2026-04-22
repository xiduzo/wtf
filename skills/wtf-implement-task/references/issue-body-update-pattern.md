# Issue Body Update Pattern

Use this pattern whenever you need to update a section of a GitHub issue body without overwriting the rest.

## Steps

1. Fetch the current body to a uniquely-named temp file (include the issue number, skill name, and a step label so parallel runs never collide):

   ```bash
   gh issue view <issue_number> --json body -q .body > /tmp/wtf-<skill>-<issue_number>-<step>.md
   ```

2. Programmatically replace only the target section in the file (use the Write or Edit tool — do not manually construct the full body from scratch, as other sections may have changed since the issue was created).

3. Push the updated body:
   ```bash
   gh issue edit <issue_number> --body-file /tmp/wtf-<skill>-<issue_number>-<step>.md
   ```

## Notes

- Always read before writing — never assume the current body matches the original draft.
- The second write in a session (e.g. step 9 updating Test Mapping after step 6 updated Technical Approach) must re-fetch the body rather than reusing the temp file from the earlier step, since other sections may have been updated in between.
- **Uniqueness rule:** every temp file name must include the issue number. When the issue number is not yet known (pre-create flows), use `$(date +%s)` instead. Add a step label (e.g. `-approach`, `-test-mapping`) when multiple writes happen in one run so they do not overwrite each other.
