# QA Verdict Guide

## Status Symbols

| Symbol | Meaning                                                               |
| ------ | --------------------------------------------------------------------- |
| ✅     | Passed — scenario behaved as specified                                |
| ❌     | Failed — scenario did not behave as specified; bug report required    |
| ⚠️     | Conditional pass — scenario passed with a caveat or deviation noted   |
| 🚫     | Blocked — could not be tested (missing dependency, environment issue) |

## Final Verdict Options

| Verdict             | Meaning                                                      |
| ------------------- | ------------------------------------------------------------ |
| ✅ Ready for merge  | All scenarios passed, all DoD items checked                  |
| ❌ Needs fixes      | One or more scenarios failed; bug reports filed              |
| ⚠️ Conditional pass | Passed with noted caveats; PO or Tech Lead sign-off required |

## Sample Completed Test Mapping Table

The running table format used during verification (columns: Scenario, Result, Bug Filed):

| Scenario                                                      | Result | Bug Filed |
| ------------------------------------------------------------- | ------ | --------- |
| Fulfilment Manager views open Purchase Orders                 | ✅     | —         |
| Order list is empty when no open orders exist                 | ✅     | —         |
| Order list shows error when fulfilment service is unavailable | ❌     | yes       |
| Paginated order list loads next page on scroll                | ⚠️     | —         |

## Sample QA Summary Comment

```
## QA Summary — Task #42

**Scenarios tested:** 4
**Passed:** 2 ✅
**Failed:** 1 ❌
**Conditional:** 1 ⚠️

### Findings

**❌ Scenario: Order list shows error when fulfilment service is unavailable**
- Expected: An error message "Fulfilment service unavailable — try again shortly" appears
- Actual: Page shows blank white screen with no user feedback
- Repro: Stop the fulfilment service, load /orders
- Bug filed: #87

**⚠️ Scenario: Paginated order list loads next page on scroll**
- Passed functionally but scroll performance is sluggish on mobile (< 30fps)
- Not a blocker for merge; filed as improvement in #88

### Verdict: ❌ Needs fixes
Bug #87 must be resolved before merge.
```
