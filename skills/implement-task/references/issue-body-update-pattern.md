# Issue Body Update Pattern

Use this pattern whenever you need to update a section of a GitHub issue body without overwriting the rest.

## Steps

1. Fetch the current body:

   ```bash
   gh issue view <issue_number> --json body -q .body > /tmp/updated-issue-body.md
   ```

2. Programmatically replace only the target section in the file (use the Write or Edit tool — do not manually construct the full body from scratch, as other sections may have changed since the issue was created).

3. Push the updated body:
   ```bash
   gh issue edit <issue_number> --body-file /tmp/updated-issue-body.md
   ```

## Notes

- Always read before writing — never assume the current body matches the original draft.
- The second write in a session (e.g. step 9 updating Test Mapping after step 6 updated Technical Approach) must re-fetch the body rather than reusing the temp file from the earlier step, since other sections may have been updated in between.
- Use a descriptive temp file name if multiple updates occur in one session (e.g. `/tmp/updated-task-body.md` for step 6, `/tmp/updated-task-body-test-mapping.md` for step 9).
