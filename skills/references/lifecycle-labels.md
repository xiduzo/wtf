# Lifecycle Labels

Shared label semantics and gate templates for any skill that reads or writes lifecycle labels on a Trace or Feature issue. Legacy Task issues carry the same labels with the same meanings.

## Label semantics

| Label | Meaning | Set by |
|---|---|---|
| `designed` | Design coverage produced (Design Reference / Handoff written) | `wtf.design-trace`, `wtf.design-feature` |
| `implemented` | Code complete. All claimed Gherkin scenarios pass. | `wtf.implement-trace` |
| `verified` | QA verified against the Scenario Claim + Edge Cases | `wtf.verify-trace` |
| `merged` | PR merged to main (closes the issue) | GitHub on PR merge |

## Canonical flow

The recommended end-to-end flow:

```
write-trace → design-trace → implement-trace → verify-trace → create-pr
```

Render this flow string verbatim inside gate prompts. The user is trained to recognize it.

## Read labels

```bash
gh issue view <issue_number> --json labels --jq '.labels[].name'
```

## Gate template — absent label (consumer skills)

Use when a skill that consumes a lifecycle stage finds the expected label **absent**:

> If `<label>` is **absent**, warn the user that the trace has not been `<verb>` yet and that the recommended flow is **write-trace → design-trace → implement-trace → verify-trace → create-pr**. Then apply `./questioning-style.md` and ask the question — header `<header>`:
>
> - **Run `<recommended-skill>`** → invoke that skill, passing the issue number in as context (default)
> - **Skip** → continue without it

| Consumer | Checked label | Recommended skill | Header |
|---|---|---|---|
| `wtf.implement-trace` | `designed` | `wtf.design-trace` | `Design check` |
| `wtf.verify-trace` | `implemented` | `wtf.implement-trace` | `Implement first?` |
| `wtf.create-pr` | `verified` | `wtf.verify-trace` | `Verify first?` |

If the label is present, continue silently. Do not announce.

## Gate template — present label (producer overwrite)

Use when a skill that **writes** a lifecycle output finds the label already present (re-run scenario):

> If `<label>` is **present**, ask "This `<issue type>` already has a `<label>` label. Continuing will overwrite the existing `<output>`. How would you like to proceed?" — header `Already <label>`:
>
> - **<Re-run verb> it** → overwrite the existing `<output>` and continue
> - **Exit** → leave the existing `<output>` as-is and exit immediately

| Producer | Checked label | Output | Re-run verb |
|---|---|---|---|
| `wtf.design-trace` | `designed` | Design Reference | Redesign |
| `wtf.design-feature` | `designed` | Design Handoff | Redesign |

## Mark transition (write side)

After you produce the output, set the lifecycle label:

```bash
gh issue edit <issue_number> --add-label "<label>"
```

This call is **mandatory**. The consuming skill's gate depends on it. In sub-agent contexts the label call is non-skippable per `./subagent-protocol.md` rule 4.
