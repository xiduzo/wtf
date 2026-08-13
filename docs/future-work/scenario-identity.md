# Scenario identity, duplication, and audit anchor (phase 5)

**Status:** planned, not started. Raised 2026-08-11 during review of [PR #2](https://github.com/xiduzo/wtf/pull/2) (the Trace model + planning modes).
**Delivery:** its own branch (`feat/scenario-identity`), with a new ADR 0002. Not part of PR #2.

That review found 7 issues; 6 were fixed inside PR #2. This is the seventh — the only one large enough to need its own phase.

---

## 1. Where things stand

The 6 fixes that shipped with PR #2 are written into the repo. Read them there rather than re-deriving:

| Fix | Where it landed |
|---|---|
| Stale `.claude/skills/` mirror removed; gitignore broadened | `.gitignore`, `CLAUDE.md` repo-layout section |
| `docs/skills-audit.md` marked historical + rename table | `docs/skills-audit.md` §6 |
| `Extension Trace` + `Spine Position` added to the glossary | `CONTEXT.md`, plus invariants in `feature-to-traces`, `loop/references/pre-flight-validation.md`, `refine`, `health` |
| Broken `## <!-- ... -->` heading in the Trace template | `.github/ISSUE_TEMPLATE/TRACE.md` + `skills/wtf.setup/references/TRACE.md` |
| Grow-only re-aim → **scenario-set gate** (growth *and* shrinkage human-gated) | `CONTEXT.md` Re-aim entry, `refine` "Scenario-set gate", `loop`, `docs/adr/0001` |
| Stacked Trace branches + post-Skeleton parallelism | `skills/references/branch-setup.md`, `skills/references/conflict-graph.md`, `implement-trace` step 5, `create-pr` step 8, `loop/references/trace-execution.md`, `wtf.setup` step 7a-bis, `docs/adr/0001` Consequences |

Two known-remaining cosmetic items, deliberately **not** fixed (pre-existing, out of PR scope) — mention them if the user asks, don't sweep them unprompted:
- The same `## <!-- ... -->` markdown artifact exists in `EPIC.md` (×3), `BUG.md`, `FEATURE.md`, and the retired `TASK.md`.
- Two ASD-STE100 semicolons in `CONTEXT.md` lines 3 and 25.

---

## 2. The work to do

Branch off `main` once PR #2 has merged — this builds on the Extension Trace vocabulary and the scenario-set gate that PR #2 introduced.

### The three problems being solved

- **(a) Orphaned claims.** A Scenario Claim is a list of scenario *names* resolved against the parent Feature's body. Renaming a scenario silently orphans every claim naming it.
- **(b) Duplicated text.** Each Trace body carries a synced `<details>` copy of the claimed Gherkin. Drift is detected but never repaired — two agent-synced copies of the same prose.
- **(c) No audit anchor.** The Feature body is canonical *and* mutable, so editing it retroactively rewrites what an already-merged, `verified`-labelled Trace was verified against.

### The agreed solution — ship A + B + H + D together

| | Mechanism | Fixes |
|---|---|---|
| **A** | Stable `@S-NNNN` Gherkin tags on every scenario in the Feature body. Claims reference the ID; the name is display text. Partition arithmetic runs on the ID set. | (a) |
| **B** | Delete the `<details>` courtesy copy from the TRACE template entirely. | (b) |
| **H** | Short `sha256` fingerprint on each claim line, e.g. `- @S-0007 — Settlement fails on expired mandate (sha:ab12cd)`. | keeps drift detection alive after B; also catches text changing *under* a stable ID |
| **D** | The QA verdict comment embeds the exact Gherkin text verified, with per-scenario hashes, in a collapsed block. | (c) |

**Rejected, with reasons** (record these in ADR 0002 as Considered Options):
- **Freeze the Trace copy at claim time** — dominated by D. Same cost, wrong moment: claim time precedes implementation, refinement, and verification.
- **Committed `.feature` files** — see the ADR correction below.
- **GitHub `userContentEdits` API history** — undocumented/unversioned, `diff` commonly returns null, yields diffs not addressable revisions, and still wouldn't record *which* revision a Trace was verified against.
- **`.wtf/` append-only JSONL ledger** — genuinely stronger than D (git as immutability substrate) but overlaps it. Note as the upgrade path if the verdict comment's editability ever becomes unacceptable.

### Tag rules — decided in conversation, not yet written anywhere

These are the invariants. State them explicitly in ADR 0002:

- **Allocation:** `max(existing) + 1` per Feature, after a fresh body read (`gh-body-helper.md` already mandates read-before-write).
- **Never updated.** The tag is identity, not position. Scenario name and text change freely; the tag never moves.
- **Never renumbered** — including after implementation. A merged Trace's claim points at `@S-0007` and its verdict snapshot pins that text.
- **Removed only when a human deletes the scenario** — already human-gated by the scenario-set gate landed in this PR.
- **Retired, not recycled.** No future scenario in that Feature ever gets `@S-0007` again.

### ADR 0002 must also correct ADR 0001

`docs/adr/0001-traces-replace-tasks.md` rejects file-canonical Gherkin because "it splits the product surface from the issue that PMs and designers actually edit." **That reason does not survive the generated-not-authored variant**, where the issue body stays the only editing surface and `.feature` files are build outputs.

The rejection still holds, for a stronger reason: regenerating a committed file on every scenario edit would require `wtf.refine` to acquire a git working tree, a branch policy, and a PR — for a skill that runs headless inside `wtf.loop` and whose entire design premise is that it touches issue bodies only. Secondary: repos using the interpretive verification fallback would inherit a directory of `.feature` files nobody executes.

### Sequencing, if it must be split

**D + H first** (~6 skills, no template change, no `sync-shared-references.sh` run) — closes (c) and mechanizes drift on its own. Then **B** (mostly deletions, safe once H replaced the copy's only job). Then **A** last as its own phase — it is the only piece touching the write path and the partition arithmetic across ten skills.

### Useful facts already established

- `wtf.verify-trace` **already builds D's artifact**: step 5 (~line 146) writes canonical claimed text to `$TMP/trace-<n>.feature`, then deletes it (~line 170). Stop deleting, embed instead.
- **No skill currently trusts the courtesy copy.** All six that read it immediately discard it for the Feature body: `implement-trace:38-40`, `verify-trace:96-103`, `design-trace:31`, `pr-review:53`, `report-bug:48`, `health:81`. B is safe.
- `.wtf/gh-body.py` forwards unknown flags verbatim and already has `comment --body-file`. **No helper change, no version bump, no `wtf.setup` re-run needed** in consuming repos.
- `@S-NNNN` tags are valid Gherkin, ignored by cucumber-js / behave / pytest-bdd unless filtered on, and pass through the ephemeral projection unchanged.

### Estimated blast radius

~11 skills, ~6 references (then re-run `sync-shared-references.sh`), 2 templates in 2 locations each. **Eval fixtures carrying claim strings need regeneration:** `wtf.write-trace`, `wtf.refine`, `wtf.health`, `wtf.pr-review`.

---

## 3. Repo gotchas that cost time last session

- **`skills/` is the only source of truth.** `.claude/skills/` was deleted (dead symlinks into a non-existent `.agents/skills/`) and both paths are now gitignored. Never read them.
- **Templates are duplicated by hand, ×2.** `.github/ISSUE_TEMPLATE/<X>.md` and `skills/wtf.setup/references/<X>.md` must stay byte-identical. **`sync-shared-references.sh` does NOT cover them** — it only syncs `skills/references/` → `skills/wtf.setup/shared-references/`. Verify with `diff -q` after every template edit.
- After editing anything in `skills/references/`, run `bash skills/wtf.setup/sync-shared-references.sh`.
- **`rtk` silently mangles piped `grep` output** — multi-match greps return `"N matches in 0 files"` instead of the lines. Use `rtk proxy grep ...` to bypass.
- `docs/skills-audit.md` is explicitly historical. Don't cite it as current state; `CLAUDE.md` is the maintained inventory.
- The user's global `CLAUDE.md` asks for responses under 500 words and artifacts written to files rather than returned inline. The `ctx_*` MCP tools it references were **not available** in the last session — `ToolSearch` found no match. `WebFetch` is nominally blocked by that config but `WebSearch` worked fine.

## 4. Verification checklist before opening the PR

```bash
bash skills/wtf.setup/sync-shared-references.sh
for f in skills/references/*.md; do b=$(basename $f); [ "$b" = "eval-fixture-convention.md" ] && continue; \
  diff -q "$f" "skills/wtf.setup/shared-references/$b" >/dev/null || echo "DRIFT: $b"; done
for t in BUG FEATURE TRACE EPIC; do diff -q .github/ISSUE_TEMPLATE/$t.md skills/wtf.setup/references/$t.md >/dev/null || echo "$t DRIFT"; done
```

Also grep for stale prose after the change: no surviving references to the synced courtesy copy, and every claim-resolution path reads IDs rather than names.

---

## 5. Suggested skills

| Skill | When |
|---|---|
| `architectural-decision-records` | Writing `docs/adr/0002-*.md`. Match the shape of `docs/adr/0001-traces-replace-tasks.md` — Status / prose decision / Considered Options with rejection reasons / Consequences. |
| `ste-writing` | Any edit to `CONTEXT.md` or a durable issue-template body — the repo enforces strict ASD-STE100 there. See `skills/references/ste-writing.md`. |
| `domain-modeling` | If the ID scheme forces new vocabulary into `CONTEXT.md` (e.g. naming the fingerprint or the snapshot). |
| `skill-creator` | Running evals after regenerating fixtures: `/skill-creator test skills/wtf.write-trace`. |
| `documentation-writer` | README / `CLAUDE.md` updates describing the new claim format. |

**Do not** auto-invoke any `wtf.*` skill. Per `CLAUDE.md`, they activate only on an explicit `/` slash command from the user — never from inferred intent, even when phrasing matches a description. You are *editing* those skills here, not running them.
