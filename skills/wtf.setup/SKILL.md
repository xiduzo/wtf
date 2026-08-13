---
name: wtf.setup
description: This skill should be used when a user wants to set up WTF in a new repository, verify their environment is ready, check that GitHub CLI is installed and authenticated, install required gh extensions, or ensure the .github/ISSUE_TEMPLATE/ templates are in place — for example "set up wtf", "run setup", "check my environment", "install wtf templates", "verify everything is configured", "initialize wtf", "onboard to wtf", "first time setup", "configure gh for wtf", "prepare this repo for wtf", "is wtf ready", "get wtf running", or "a new dev joined, set them up". Run once per repo when onboarding, or when a contributor joins the project.
---

# Setup

Pre-flight check and installer for the WTF workflow.

Validate the GitHub CLI. Install required extensions. Make sure `.github/ISSUE_TEMPLATE/` holds all required templates.

Set up issue classification (native GitHub issue types or labels) and the lifecycle labels.

Install the PR template. Agents and humans can then create structured issues and pull requests.

## Process

### 1. Verify `gh` is installed

```bash
gh --version
```

If `gh` is not found, tell the user that the GitHub CLI is required. Link them to https://cli.github.com. Stop. Do not continue until `gh` is installed.

### 2. Verify `gh` is authenticated

```bash
gh auth status
```

If `gh` is not authenticated, tell the user to run `gh auth login`. Stop. Do not continue until authentication is confirmed.

### 3. Check and install required extensions

```bash
gh extension list
```

Check the output for both extensions below. If an extension is missing, install it:

```bash
# Sub-issue hierarchy (epic → feature → trace)
gh extension install yahsan2/gh-sub-issue

# Issue dependency tracking (X blocks Y)
gh extension install xiduzo/gh-issue-dependency
```

If installation fails (for example network error or permissions), warn the user. Relationship tracking stays unavailable until the extension is installed. Note the failure for the final status report.

After you try installation, verify the command syntax for each newly installed extension:

```bash
gh sub-issue --help
gh issue-dependency --help
```

Record two booleans for the final report:

- `gh-sub-issue-available`: true if `yahsan2/gh-sub-issue` is installed and working
- `gh-issue-dependency-available`: true if `xiduzo/gh-issue-dependency` is installed and working

### 4. Detect repo context

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

If this fails (not inside a git repo, or no GitHub remote), warn the user. Note that issue creation will not work until the repo is connected to GitHub. Continue to the template check anyway.

### 4b. Verify GitHub permissions

The workflow needs the authenticated user to manage labels and create issue relationships (sub-issues, dependencies).

Both need **write access** to the repo. The token needs the `repo` scope (or `public_repo` for public repos).

**Check token scopes:**

```bash
gh auth status 2>&1 | grep -i "token scopes"
```

Required scopes (any of):

- `repo` — full control (private + public repos)
- `public_repo` — sufficient for public repos only

If neither scope is present, tell the user to refresh auth with the right scopes:

```bash
gh auth refresh -h github.com -s repo
```

Stop until the user re-runs setup.

**Check repo write permission:**

```bash
gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  --jq '.permissions | {admin, maintain, push, triage, pull}'
```

The user must have `admin: true`, `maintain: true`, or `push: true`. If the user has only `triage` or `pull`, warn:

> ⚠️ You have read-only access to this repo. Label creation and issue linking will fail. Ask a maintainer for write access or fork the repo.

Record two booleans for the final report:

- `token-scopes-ok`: true if `repo` or `public_repo` scope is present
- `repo-write-ok`: true if `admin`, `maintain`, or `push` is true

If either is false, skip label creation in step 7. Warn that sub-issue and dependency creation will fail at runtime.

### 5. Check issue templates

Check whether `.github/ISSUE_TEMPLATE/` exists and holds all four required templates:

```bash
ls .github/ISSUE_TEMPLATE/
```

Required files:

- `BUG.md`
- `EPIC.md`
- `FEATURE.md`
- `TRACE.md`

First resolve where this skill's payload is installed. `npx skills add` drops `wtf.setup` under the skills root (`~/.claude/skills/wtf.setup`, `.claude/skills/wtf.setup`, or the `.agents/skills` equivalent). The bundled files (`references/`, `shared-references/`, `hooks/`) are included inside it.

Probe in order. Keep the first that exists. Reuse `$SETUP_DIR` for every copy below:

```bash
for cand in \
  "$HOME/.claude/skills/wtf.setup" \
  "$HOME/.agents/skills/wtf.setup" \
  "$PWD/.claude/skills/wtf.setup" \
  "$PWD/.agents/skills/wtf.setup" \
  "$PWD/skills/wtf.setup"; do
  [ -d "$cand/references" ] && SETUP_DIR="$cand" && break
done
```

For each missing file, copy it from this skill's bundled references at `$SETUP_DIR/references/`:

```bash
mkdir -p .github/ISSUE_TEMPLATE
cp "$SETUP_DIR/references/BUG.md"     .github/ISSUE_TEMPLATE/BUG.md
cp "$SETUP_DIR/references/EPIC.md"    .github/ISSUE_TEMPLATE/EPIC.md
cp "$SETUP_DIR/references/FEATURE.md" .github/ISSUE_TEMPLATE/FEATURE.md
cp "$SETUP_DIR/references/TRACE.md"   .github/ISSUE_TEMPLATE/TRACE.md
```

Copy only files that are missing. Do not overwrite existing templates. After copying, list the final contents of `.github/ISSUE_TEMPLATE/` to confirm.

### 6. Check PR template

Check whether `.github/pull_request_template.md` exists:

```bash
ls .github/pull_request_template.md 2>/dev/null
```

If it is missing, copy it from the skill's bundled references (use `$SETUP_DIR` from step 5):

```bash
cp "$SETUP_DIR/references/pull_request_template.md" .github/pull_request_template.md
```

Do not overwrite the file if it already exists.

### 7. Choose the issue-classification mode and provision it

WTF classifies every issue as an **Epic**, **Feature**, **Trace**, or **Bug**.

There are two mechanisms. One is native **GitHub issue types** (an organization-only feature). That leaves labels free for your own segmentation. The other is the `epic`/`feature`/`trace`/`bug` **labels** (portable to any repo).

See `../references/issue-classification.md`. Pick the mode once here. Record it in `.wtf/config.json` so every skill resolves it the same way. Lifecycle labels (`implemented`, `designed`, `verified`) are always created in both modes.

**Step A — detect the owner type:**

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
OWNER_TYPE=$(gh api "users/$OWNER" --jq '.type' 2>/dev/null)   # "User" or "Organization"
```

**Step B — pick the mode.**

- If `OWNER_TYPE` is **not** `Organization` (a personal account, or detection failed): native issue types are unavailable. GitHub gates them to organizations. Set `CLASS_MODE=labels` and tell the user plainly: *"This is a personal-account repo, so GitHub issue types are not available (they are org-only). WTF will classify with the `epic`/`feature`/`trace`/`bug` labels."* Skip to Step D.

- If `OWNER_TYPE` is `Organization` **and** `repo-write-ok` and `token-scopes-ok` (from step 4b) are both true, call `AskUserQuestion` (per `../references/questioning-style.md`):
  - question: "This repo is in an org, so WTF can classify issues with native GitHub issue types (Epic/Feature/Trace/Bug) instead of labels — leaving labels free for your own segmentation like `phase-2`. Use native issue types?"
  - header: "Classification"
  - options:
    - **Native issue types (recommended)** → `CLASS_MODE=types`
    - **Labels** → `CLASS_MODE=labels`

  If write or token permissions are missing, do **not** offer types. Provisioning needs org-owner rights. Set `CLASS_MODE=labels` and note it.

**Step C — provision native types** (only when `CLASS_MODE=types`).

Run the **Provision native types** block from `../references/issue-classification.md`. It creates `Epic` and `Trace` (`Task`/`Bug`/`Feature` ship as org defaults — the `Task` default stays unused).

Then verify all four resolved. If any is missing (for example you are not an org owner), fall back to labels:

```bash
HAVE=$(gh api "orgs/$OWNER/issue-types" --jq '[.[].name]' 2>/dev/null)
for t in Epic Feature Trace Bug; do
  printf '%s' "$HAVE" | grep -qi "\"$t\"" || { echo "⚠️ could not provision issue type: $t — falling back to labels"; CLASS_MODE=labels; }
done
```

When this falls back, warn that native types need org-owner rights. WTF will use labels instead.

**Step D — create labels.** Always create the lifecycle labels.

Create the kind labels (`epic`/`feature`/`trace`/`bug`) **only in `labels` mode**. In `types` mode omit them on purpose so the label space stays free for your own segmentation.

`--force` is idempotent. It updates color/description if the label already exists. Otherwise it creates the label:

```bash
# Lifecycle labels — always, both modes:
gh label create implemented --color 0e8a16 --description "Implementation complete — ready for QA" --force
gh label create designed    --color f9d0c4 --description "Design coverage added to the Trace"     --force
gh label create verified    --color 006b75 --description "QA verified — ready for merge"          --force

# Kind labels — labels mode only:
if [ "$CLASS_MODE" = labels ]; then
  gh label create epic    --color 5319e7 --description "Strategic initiative spanning multiple features"      --force
  gh label create feature --color 0075ca --description "User-facing capability delivered as a vertical slice" --force
  gh label create trace   --color e4e669 --description "One pass over a Feature's spine — one story, one Scenario Claim, end-to-end" --force
  gh label create bug     --color d73a4a --description "Something is broken"                                  --force
fi
```

If any label creation fails (for example insufficient permissions), warn the user. The affected skills fall back to creating labels on first use.

**Step D (cont.) — align the issue templates with the mode.**

In `types` mode, rewrite each copied `.github/ISSUE_TEMPLATE/*.md`. Make its kind come from the native type rather than a label.

Flip the `labels: <kind>` frontmatter line to `type: <Kind>`. (`type` is a supported template frontmatter key alongside `title`/`labels`/`assignees`.)

This keeps issues opened manually from the GitHub UI typed, not labelled. The label space stays free.

In `labels` mode leave the templates as they are. The rewrite is conservative. It only touches an exact single `labels: <kind>` line. Customized multi-label templates are left alone:

```bash
if [ "$CLASS_MODE" = types ]; then
  python3 - <<'PY'
import re, pathlib
kinds = {"BUG": ("bug", "Bug"), "EPIC": ("epic", "Epic"), "FEATURE": ("feature", "Feature"), "TRACE": ("trace", "Trace")}
d = pathlib.Path(".github/ISSUE_TEMPLATE")
for fname, (lbl, typ) in kinds.items():
    p = d / f"{fname}.md"
    if not p.exists():
        continue
    text = p.read_text()
    new = re.sub(rf'(?m)^labels:\s*{lbl}\s*$', f'type: {typ}', text)
    if new != text:
        p.write_text(new)
        print(f"  {fname}.md: labels: {lbl} -> type: {typ}")
PY
fi
```

**Step E — record the mode** so every skill resolves it the same way:

```bash
mkdir -p .wtf
python3 - ".wtf/config.json" "$CLASS_MODE" <<'PY'
import json, sys, pathlib
path, mode = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
data = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else {}
data["classification"] = mode
p.write_text(json.dumps(data, indent=2) + "\n")
PY
```

Commit `.wtf/config.json` so every teammate classifies issues the same way. Record `classification: types|labels` for the status report.

> **Closing convention:** GitHub has no native setting to require PR-based closure. Skill behavior enforces this. Issues are only "closed as completed" when a merged PR contains `Closes #<n>`. Direct `gh issue close` calls are reserved for `--reason "not planned"` (will not implement) and `--reason "duplicate"` only. Surface this convention in the status report.

### 7a-bis. Enable automatic head-branch deletion

Trace PRs stack: a Trace branches off the branch of the Trace it builds on rather than waiting for a merge (`../references/branch-setup.md`). GitHub retargets a stacked PR to its parent's base **only when the parent's head branch is deleted on merge**. Without this setting, a human merging through the web UI strands every PR above them.

Check it, and turn it on when the token allows:

```bash
gh repo view --json deleteBranchOnMerge --jq '.deleteBranchOnMerge'
```

If `false`, ask the user (per `../references/questioning-style.md`):

- question: "WTF stacks Trace pull requests. GitHub only re-points a stacked PR when the branch below it is deleted on merge. Turn on automatic head-branch deletion?"
- header: "Branch cleanup"
- options:
  - **Enable it (recommended)** → run the API call below
  - **Leave it off** → warn that stacked PRs will need their base re-pointed by hand, and record this in the status report

```bash
gh api -X PATCH "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  -F delete_branch_on_merge=true
```

If the call fails on permissions, say so plainly and tell the user to set **Settings → General → Automatically delete head branches** themselves. Record `delete_branch_on_merge: true|false` for the status report.

### 7b. Choose the planning mode

WTF planning skills work in one of two modes. See `../references/planning-mode.md`. `guided` asks at each step. `flow` derives everything it can and presents one consolidated review. Both modes run the same quality gates.

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "How should WTF planning skills work by default? You can override per invocation with a `guided` or `flow` argument."
- header: "Planning"
- options:
  - **Guided (recommended to start)** → `PLAN_MODE=guided` — the skill asks step by step; best while the team still shapes its specs
  - **Flow** → `PLAN_MODE=flow` — the skill drafts the full batch and asks once; best when Epics and steering docs already answer most questions

Record the mode next to the classification key. The write preserves other keys:

```bash
python3 - ".wtf/config.json" "$PLAN_MODE" <<'PY'
import json, sys, pathlib
path, mode = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
data = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else {}
data["planning"] = mode
p.write_text(json.dumps(data, indent=2) + "\n")
PY
```

Record `planning: guided|flow` for the status report.

### 7c. Choose the feature scope

WTF Features carry 1..n user stories. This knob sets how many. It controls artifact granularity. It is orthogonal to the planning mode, which controls interaction density. `wtf.write-feature`'s scope gate may override it per Feature with a stated reason.

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "How many user stories should a Feature carry by default? Single-story keeps the traditional one-feature-one-story shape. Grouped lets a Feature carry multiple co-related stories that share one Spine — fewer Features, richer Trace sequences."
- header: "Feature scope"
- options:
  - **Single-story** → `SCOPE_MODE=single-story` — every Feature carries exactly one user story; Feature ≈ story ≈ one Trace (plus Deepening Traces when needed)
  - **Grouped** → `SCOPE_MODE=grouped` — a Feature carries multiple co-related stories sharing one Spine; the agentic mode

Record the mode next to the other keys. The write preserves other keys:

```bash
python3 - ".wtf/config.json" "$SCOPE_MODE" <<'PY'
import json, sys, pathlib
path, mode = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
data = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else {}
data["feature_scope"] = mode
p.write_text(json.dumps(data, indent=2) + "\n")
PY
```

Record `feature_scope: single-story|grouped` for the status report.

### 7d. Choose the delivery mode

The delivery mode sets where Trace PRs merge. See `../references/branch-setup.md`. A human may override it per Feature with a stated reason. The override is recorded in the Feature body.

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Where should Trace PRs merge by default? Staged merges each Trace into its feature branch, then the feature PR merges into main when the Trace Plan is exhausted. Trunk merges each Trace PR into main directly."
- header: "Delivery"
- options:
  - **Staged (recommended)** → `DELIVERY_MODE=staged` — safe everywhere; each `trace/<n>-<slug>` branch starts from the feature branch
  - **Trunk** → `DELIVERY_MODE=trunk` — Trace PRs merge into `main`; the Feature issue closes when its Trace Plan is exhausted

If the user picks **Trunk**, show this caution before you write the config: *"Trunk delivery merges every Trace PR into `main` directly. Unfinished Features are live on `main`. This mode presumes feature-flag or dark-launch discipline. Without it, partial features reach production."*

Record the mode next to the other keys. The write preserves other keys:

```bash
python3 - ".wtf/config.json" "$DELIVERY_MODE" <<'PY'
import json, sys, pathlib
path, mode = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
data = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else {}
data["delivery"] = mode
p.write_text(json.dumps(data, indent=2) + "\n")
PY
```

Record `delivery: staged|trunk` for the status report.

### 8. Install intervention-tracker hook

The tracker hook counts user corrections and nudges toward `/wtf.reflect`. skills.sh copies the hook script into the skill dir. You must register the hook in Claude Code's `settings.json` manually.

**Step A — locate the installed hook script.** The hook is a Python script (`track-interventions.py`). It runs the same way on macOS, Linux, and Windows. Probe in order. Keep the first that exists:

```bash
for cand in \
  "$HOME/.claude/skills/wtf.setup/hooks/track-interventions.py" \
  "$PWD/.claude/skills/wtf.setup/hooks/track-interventions.py" \
  "$PWD/skills/wtf.setup/hooks/track-interventions.py"; do
  [ -f "$cand" ] && HOOK_PATH="$cand" && break
done
```

If none exist, warn the user that the hook script could not be found. Skip hook registration.

**Step B — ask scope** (apply `../references/questioning-style.md`):

Call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Install the WTF intervention-tracker hook globally or only for this repo?"
- header: "Hook scope"
- options:
  - **Global (~/.claude/settings.json)** → runs in every repo that has `docs/steering/`
  - **This repo only (.claude/settings.json)** → scoped to this project
  - **Skip** → do not install the hook

Set `SETTINGS_FILE` as follows:

- Global → `$HOME/.claude/settings.json`
- Per-repo → `.claude/settings.json`
- Skip → jump to step 9.

**Step C — patch settings.json idempotently.**

If the file is missing, create it (`echo '{}' > "$SETTINGS_FILE"`). Then merge the two hook entries with `python3`.

`python3` is available on macOS/Linux. git-bash on Windows ships it via the installer or can use `py`.

The registered command invokes the hook via `python3`. It works without a POSIX shell on Windows:

```bash
PY_BIN=$(command -v python3 || command -v py || echo python)
HOOK_CMD="$PY_BIN $HOOK_PATH"
python3 - "$SETTINGS_FILE" "$HOOK_CMD" <<'PY'
import json, sys, pathlib
path, cmd = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
data = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else {}
hooks = data.setdefault("hooks", {})
for event in ("UserPromptSubmit", "Stop"):
    arr = hooks.setdefault(event, [])
    # Strip legacy sh-based entries so we don't double-fire after the .sh→.py migration.
    for entry in arr:
        entry["hooks"] = [
            h for h in entry.get("hooks", [])
            if "track-interventions.sh" not in (h.get("command") or "")
        ]
    arr[:] = [e for e in arr if e.get("hooks")]
    exists = any(
        any(h.get("command") == cmd for h in entry.get("hooks", []))
        for entry in arr
    )
    if not exists:
        arr.append({"matcher": "", "hooks": [{"type": "command", "command": cmd}]})
p.write_text(json.dumps(data, indent=2))
PY
```

Re-running is safe. Existing entries are detected by exact `command` string and are not duplicated.

**Windows note:** If the user is on Windows without `python3`, skip the patch. Print the JSON snippet for manual paste. Detect via `command -v python3 >/dev/null || echo 'manual'`.

Record `hook-installed: true|false|skipped` for the status report.

### 8b. Install the gh body helper

`gh-body.py` is a cross-platform utility that makes every GitHub issue/PR body read and write UTF-8-safe. It prevents the CP850 mojibake, newline collapse, and inline-`--body` corruption that `gh` suffers under PowerShell on Windows.

Skills invoke it at `.wtf/gh-body.py`. Install it here so the guard is committed to the repo and shared with every teammate. See `../references/gh-body-helper.md`.

**Step A — locate the bundled helper** (same install-location probe as the tracker):

```bash
for cand in \
  "$HOME/.claude/skills/wtf.setup/hooks/gh-body.py" \
  "$PWD/.claude/skills/wtf.setup/hooks/gh-body.py" \
  "$PWD/skills/wtf.setup/hooks/gh-body.py"; do
  [ -f "$cand" ] && GHBODY_SRC="$cand" && break
done
```

**Step B — copy it into the repo:**

```bash
if [ -n "$GHBODY_SRC" ]; then
  mkdir -p .wtf
  cp "$GHBODY_SRC" .wtf/gh-body.py
fi
```

Commit `.wtf/gh-body.py` so the guard travels with the repo for every contributor.

If `GHBODY_SRC` is empty (helper not found) or `cp` is unavailable (Windows without git-bash), tell the user to copy `gh-body.py` into `.wtf/` manually. Note it. Skills fall back to raw `gh` until then. That path is unguarded on Windows.

**Step C — verify it actually runs.** Skills invoke the helper as `python3 .wtf/gh-body.py`. Test that *exact* form. It validates the interpreter name, that Python is present, and that the copy is valid, all in one shot:

```bash
if python3 .wtf/gh-body.py --help >/dev/null 2>&1; then
  GUARD=verified
elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || command -v py >/dev/null 2>&1; then
  GUARD=wrong-name     # Python is installed, but not reachable as `python3`
else
  GUARD=no-python
fi
```

Interpret the result for the user:

- `verified` → the guard is live.
- `wrong-name` → Python exists but not as `python3`. On Windows the python.org installer often provides `python`/`py`, not `python3`. The skill commands call `python3`. The guard will fail until the user adds a `python3` alias/shim. Show the working interpreter you found (for example `py -3`). Tell them to alias it.
- `no-python` → no Python 3 on PATH. The guard is inert. Every body/comment op falls back to raw `gh`. That corrupts UTF-8 on Windows. Point the user to https://www.python.org/downloads/. Have them re-run setup.

Record `gh-body-helper: verified|wrong-name|no-python|not-installed` for the status report (`not-installed` if Step B could not copy the file).

### 8c. Install the shared skill references

Every execution skill loads cross-skill docs via `../references/<name>.md`. That is a `references/` folder **next to the installed skills**, at the skills root.

`npx skills add` installs each `wtf.*` skill directory one by one. The repo's `skills/references/` folder has no `SKILL.md`, so it is never shipped. `<skills-root>/references/` would be empty.

To fix that, `wtf.setup` carries a vendored copy at `$SETUP_DIR/shared-references/` and writes it to the skills root here. Without this step, every other skill fails to resolve its references.

**Step A — derive the skills root** (the parent of `$SETUP_DIR`, resolved in step 5):

```bash
SKILLS_ROOT="$(dirname "$SETUP_DIR")"   # e.g. ~/.claude/skills
```

**Step B — copy the bundled references into `<skills-root>/references/`:**

```bash
if [ -d "$SETUP_DIR/shared-references" ]; then
  mkdir -p "$SKILLS_ROOT/references"
  cp "$SETUP_DIR/shared-references/"*.md "$SKILLS_ROOT/references/"
fi
```

This overwrites prior copies so updates propagate on every `npx skills update` + re-run.

When setup runs from the wtf repo itself (`$PWD/skills/wtf.setup`), `$SKILLS_ROOT` is `skills/`. The copy is a harmless no-op refresh.

If `$SETUP_DIR/shared-references` is absent (older payload, or `cp` unavailable on Windows without git-bash), tell the user to copy the repo's `skills/references/*.md` into `<skills-root>/references/` manually. Note it. Other skills cannot resolve `../references/...` until then.

**Step C — verify** that at least one known reference landed:

```bash
[ -f "$SKILLS_ROOT/references/questioning-style.md" ] && echo "shared-references: installed" || echo "shared-references: MISSING"
```

Record `shared-references: installed|missing` for the status report.

### 9. Report status

Print a clear status summary that covers every check:

```
WTF Setup — Status Report
─────────────────────────
gh CLI installed          ✅
gh authenticated          ✅
gh-sub-issue extension    ✅  (or ⚠️ not installed — relationship links unavailable)
gh-issue-dependency ext   ✅  (or ⚠️ not installed — dependency links unavailable)
Repo context              ✅  owner/repo  (or ⚠️ not detected)
Token scopes              ✅  repo  (or ⚠️ missing — run `gh auth refresh -s repo`)
Repo write permission     ✅  push/maintain/admin  (or ⚠️ read-only — labels & links will fail)
Issue templates
  BUG.md                  ✅  (or ✅ installed from references)
  EPIC.md                 ✅  (or ✅ installed from references)
  FEATURE.md              ✅  (or ✅ installed from references)
  TRACE.md                ✅  (or ✅ installed from references)
PR template               ✅  (or ✅ installed from references)
Issue classification      ✅  native types (Epic/Feature/Trace/Bug)  (or  ✅ labels: epic, feature, trace, bug)
Planning mode             ✅  guided  (or  ✅ flow)
Feature scope             ✅  single-story  (or  ✅ grouped)
Delivery mode             ✅  staged  (or  ⚠️ trunk — presumes feature-flag / dark-launch discipline)
Lifecycle labels          ✅  implemented, designed, verified
Intervention hook         ✅  installed (global)  (or  ✅ installed (repo)  /  ⚪ skipped  /  ⚠️ manual paste required)
Body encoding guard       ✅  verified (python3)  (or  ⚠️ Python is 'py'/'python', not 'python3' — alias it or body ops fail  /  ⚠️ Python 3 not found — guard inert, raw-gh fallback  /  ⚠️ helper not copied)
Shared skill references   ✅  installed (<skills-root>/references)  (or  ⚠️ missing — copy skills/references/*.md manually; other skills can't resolve ../references)
─────────────────────────
Ready to use WTF. Start with `wtf.write-epic` to plan your first initiative.
```

If any item failed (`gh` not installed, not authenticated), replace the closing line with a clear "Fix the issues above before proceeding." Do not suggest next steps.

### 10. Offer to set up steering docs

If setup completed without fatal errors, call `AskUserQuestion` (per `../references/questioning-style.md`):

- question: "Setup complete. The steering docs (VISION.md, TECH.md, DESIGN.md, QA.md) capture your project's principles and standards — every skill reads them automatically. Would you like to create them now?"
- header: "Steering docs"
- options:
  - **Yes — set them up now** → run `wtf.steer-vision` (it will offer to chain to TECH, DESIGN, and QA at the end)
  - **Not now** → skip. Skills will prompt you to create them on first use
