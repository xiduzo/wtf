# QA Verdict Guide

## Status Symbols

| Symbol | Meaning                                                               |
| ------ | --------------------------------------------------------------------- |
| ✅     | Passed — scenario behaved as specified                                |
| ❌     | Failed — scenario did not behave as specified; bug report required    |
| ⚠️     | Conditional pass — scenario passed with a caveat or deviation noted   |
| 🚫     | Blocked — could not be tested (missing dependency, environment issue) |

## Method Values

Every claimed scenario is verified by one of two methods. The verdict names the method per scenario.

| Method        | Meaning                                                                          |
| ------------- | -------------------------------------------------------------------------------- |
| `executed`    | A Gherkin runner ran the scenario from the ephemeral projection (primary)        |
| `interpreted` | QA walked the scenario manually against the running software (fallback)          |

The fallback applies when no runner exists, or when a scenario has unbound steps.

## Final Verdict Options

| Verdict             | Meaning                                                                     |
| ------------------- | --------------------------------------------------------------------------- |
| ✅ Ready for merge  | All claimed scenarios passed, DoD items checked, and the system is releasable |
| ❌ Needs fixes      | A claimed scenario failed, or the releasability check failed; bug reports filed |
| ⚠️ Conditional pass | Passed with noted caveats; PO or Tech Lead sign-off required                |

## Sample Completed Test Mapping Table

The running table format used during verification (columns: Claimed scenario, Method, Result, Bug Filed):

| Claimed scenario                             | Method      | Result | Bug Filed |
| -------------------------------------------- | ----------- | ------ | --------- |
| Status shown for a settled payment           | executed    | ✅     | —         |
| Status for a failed settlement               | executed    | ❌     | yes       |
| Status while settlement is pending           | interpreted | ⚠️     | —         |

## Sample QA Verdict Comment

```
## QA Verdict — Trace #42

**Scenario Claim:** 3 scenarios of story "Merchant sees settlement status"
**Executed:** 2 via cucumber-js (ephemeral projection from Feature #17) — 1 ✅ / 1 ❌
**Interpreted:** 1 — 1 ⚠️ (no step definition for "the settlement is pending")

### Findings

**❌ Scenario: Status for a failed settlement** (executed)
- Expected: The status "Failed" shows with the failure reason
- Actual: Runner reports a timeout — the status stays "Processing"
- Repro: Run the projected scenario, or fail a settlement and load /settlements
- Bug filed: #87

**⚠️ Scenario: Status while settlement is pending** (interpreted)
- The status shows, but only after a manual page refresh
- Not a merge blocker — filed as improvement in #88

### Releasability
Releasable: yes. Build and type check pass on `trace/42-settlement-status`. The Skeleton happy path still works.

### Roll-up
Story "Merchant sees settlement status" — 2 of 3 scenarios verified. Trace #43 claims the remainder.

### Verdict: ❌ Needs fixes
Bug #87 blocks the merge.
```
