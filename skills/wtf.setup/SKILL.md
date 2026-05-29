---
name: wtf.setup
description: This skill should be used when a user wants to set up WTF in a new repository, verify their environment is ready, check that GitHub CLI is installed and authenticated, install required gh extensions, or ensure the .github/ISSUE_TEMPLATE/ templates are in place — for example "set up wtf", "run setup", "check my environment", "install wtf templates", "verify everything is configured", "initialize wtf", "onboard to wtf", "first time setup", "configure gh for wtf", "prepare this repo for wtf", "is wtf ready", "get wtf running", or "a new dev joined, set them up". Run once per repo when onboarding, or when a contributor joins the project.
---

# Setup

Pre-flight check and installer for the WTF workflow. Validates the GitHub CLI, installs required extensions, ensures `.github/ISSUE_TEMPLATE/` contains all required templates, sets up issue classification (native GitHub issue types or labels) and the lifecycle labels, and installs the PR template so both agents and humans can create structured issues and pull requests.

## Process

### 1. Verify `gh` is installed

```bash
gh --version
```

If not found: tell the user that the GitHub CLI is required, link them to https://cli.github.com, and stop. Do not proceed until `gh` is confirmed installed.

### 2. Verify `gh` is authenticated

```bash
gh auth status
```

If not authenticated: tell the user to run `gh auth login` and stop. Do not proceed until authentication is confirmed.

### 3. Check and install required extensions

```bash
gh extension list
```

Check the output for both of the following extensions. For each that is missing, install it:

```bash
# Sub-issue hierarchy (epic → feature → task)
gh extension install yahsan2/gh-sub-issue

# Issue dependency tracking (X blocks Y)
gh extension install xiduzo/gh-issue-dependency
```

If installation fails (e.g. network error, permissions), warn the user that relationship tracking will be unavailable until the extension is installed. Note the failure — it will be included in the final status report.

After attempting installation, verify the command syntax for any newly installed extension:

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

If this fails (not inside a git repo, or no GitHub remote), warn the user and note that issue creation will not work until the repo is connected to GitHub. Continue to the template check regardless.

### 4b. Verify GitHub permissions

The workflow requires the authenticated user to manage labels and create issue relationships (sub-issues, dependencies). Both need **write access** to the repo and a token with the `repo` scope (or `public_repo` for public repos).

**Check token scopes:**

```bash
gh auth status 2>&1 | grep -i "token scopes"
```

Required scopes (any of):
- `repo` — full control (private + public repos)
- `public_repo` — sufficient for public repos only

If neither scope is present, instruct the user to refresh auth with the right scopes:

```bash
gh auth refresh -h github.com -s repo
```

…and stop until re-run.

**Check repo write permission:**

```bash
gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
  --jq '.permissions | {admin, maintain, push, triage, pull}'
```

The user must have `admin: true`, `maintain: true`, or `push: true`. If only `triage` or `pull`, warn:

> ⚠️ You have read-only access to this repo. Label creation and issue linking will fail. Ask a maintainer for write access or fork the repo.

Record two booleans for the final report:
- `token-scopes-ok`: true if `repo` or `public_repo` scope present
- `repo-write-ok`: true if `admin`, `maintain`, or `push` is true

If either is false, skip label creation in step 7 and warn that sub-issue / dependency creation will fail at runtime.

### 5. Check issue templates

Check whether `.github/ISSUE_TEMPLATE/` exists and contains all four required templates:

```bash
ls .github/ISSUE_TEMPLATE/
```

Required files:
- `BUG.md`
- `EPIC.md`
- `FEATURE.md`
- `TASK.md`

For each missing file, copy it from this skill's bundled references:

```bash
mkdir -p .github/ISSUE_TEMPLATE

# Copy each missing template from the skill's references folder.
# The references folder is at: skills/wtf.setup/references/
cp skills/wtf.setup/references/BUG.md .github/ISSUE_TEMPLATE/BUG.md
cp skills/wtf.setup/references/EPIC.md .github/ISSUE_TEMPLATE/EPIC.md
cp skills/wtf.setup/references/FEATURE.md .github/ISSUE_TEMPLATE/FEATURE.md
cp skills/wtf.setup/references/TASK.md .github/ISSUE_TEMPLATE/TASK.md
```

Only copy files that are missing — do not overwrite existing templates. After copying, list the final contents of `.github/ISSUE_TEMPLATE/` to confirm.

### 6. Check PR template

Check whether `.github/pull_request_template.md` exists:

```bash
ls .github/pull_request_template.md 2>/dev/null
```

If missing, copy it from the skill's bundled references:

```bash
cp skills/wtf.setup/references/pull_request_template.md .github/pull_request_template.md
```

Do not overwrite if it already exists.

### 7. Choose the issue-classification mode and provision it

WTF classifies every issue as an **Epic**, **Feature**, **Task**, or **Bug**. There are two mechanisms — native **GitHub issue types** (an organization-only feature, with labels left free for your own segmentation) or the `epic`/`feature`/`task`/`bug` **labels** (portable to any repo). See `../references/issue-classification.md`. Pick the mode once here and record it in `.wtf/config.json` so every skill resolves it identically. Lifecycle labels (`implemented`, `designed`, `verified`) are always created regardless of mode.

**Step A — detect the owner type:**

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
OWNER_TYPE=$(gh api "users/$OWNER" --jq '.type' 2>/dev/null)   # "User" or "Organization"
```

**Step B — pick the mode.**

- If `OWNER_TYPE` is **not** `Organization` (a personal account, or detection failed): native issue types are unavailable — GitHub gates them to organizations. Set `CLASS_MODE=labels` and tell the user plainly: *"This is a personal-account repo, so GitHub issue types aren't available (they're org-only). WTF will classify with the `epic`/`feature`/`task`/`bug` labels."* Skip to Step D.

- If `OWNER_TYPE` is `Organization` **and** `repo-write-ok` and `token-scopes-ok` (from step 4b) are both true, call `AskUserQuestion` (per `../references/questioning-style.md`):
  - question: "This repo is in an org, so WTF can classify issues with native GitHub issue types (Epic/Feature/Task/Bug) instead of labels — leaving labels free for your own segmentation like `phase-2`. Use native issue types?"
  - header: "Classification"
  - options:
    - **Native issue types (recommended)** → `CLASS_MODE=types`
    - **Labels** → `CLASS_MODE=labels`

  If write/token perms are missing, do **not** offer types — provisioning needs org-owner rights. Set `CLASS_MODE=labels` and note it.

**Step C — provision native types** (only when `CLASS_MODE=types`). Run the **Provision native types** block from `../references/issue-classification.md` — it creates `Epic` (`Task`/`Bug`/`Feature` ship as org defaults). Then verify all four resolved; if any is missing (e.g. you are not an org owner), fall back to labels:

```bash
HAVE=$(gh api "orgs/$OWNER/issue-types" --jq '[.[].name]' 2>/dev/null)
for t in Epic Feature Task Bug; do
  printf '%s' "$HAVE" | grep -qi "\"$t\"" || { echo "⚠️ could not provision issue type: $t — falling back to labels"; CLASS_MODE=labels; }
done
```

When this falls back, warn that native types need org-owner rights and WTF will use labels instead.

**Step D — create labels.** Always create the lifecycle labels. Create the kind labels (`epic`/`feature`/`task`/`bug`) **only in `labels` mode** — in `types` mode they are intentionally omitted so the label space stays free for your own segmentation. `--force` is idempotent (updates color/description if the label already exists, creates it otherwise):

```bash
# Lifecycle labels — always, both modes:
gh label create implemented --color 0e8a16 --description "Implementation complete — ready for QA" --force
gh label create designed    --color f9d0c4 --description "Design coverage added to the Task"      --force
gh label create verified    --color 006b75 --description "QA verified — ready for merge"          --force

# Kind labels — labels mode only:
if [ "$CLASS_MODE" = labels ]; then
  gh label create epic    --color 5319e7 --description "Strategic initiative spanning multiple features"      --force
  gh label create feature --color 0075ca --description "User-facing capability delivered as a vertical slice" --force
  gh label create task    --color e4e669 --description "Implementable vertical slice of a Feature"            --force
  gh label create bug     --color d73a4a --description "Something is broken"                                  --force
fi
```

If any label creation fails (e.g. insufficient permissions), warn the user — the affected skills fall back to creating labels on first use.

**Step D (cont.) — align the issue templates with the mode.** In `types` mode, rewrite each copied `.github/ISSUE_TEMPLATE/*.md` so its kind comes from the native type rather than a label — flip the `labels: <kind>` frontmatter line to `type: <Kind>` (`type` is a supported template frontmatter key alongside `title`/`labels`/`assignees`). This keeps issues opened manually from the GitHub UI typed, not labelled, so the label space stays free. In `labels` mode leave the templates as-is. The rewrite is conservative — it only touches an exact single `labels: <kind>` line, so customized multi-label templates are left alone:

```bash
if [ "$CLASS_MODE" = types ]; then
  python3 - <<'PY'
import re, pathlib
kinds = {"BUG": ("bug", "Bug"), "EPIC": ("epic", "Epic"), "FEATURE": ("feature", "Feature"), "TASK": ("task", "Task")}
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

**Step E — record the mode** so every skill resolves it identically:

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

> **Closing convention:** GitHub has no native setting to require PR-based closure, so this is enforced by skill behavior. Issues are only "closed as completed" when a merged PR contains `Closes #<n>`. Direct `gh issue close` calls are reserved for `--reason "not planned"` (won't implement) and `--reason "duplicate"` only. Surface this convention in the status report.

### 8. Install intervention-tracker hook

The tracker hook counts user corrections and nudges toward `/wtf.reflect`. skills.sh copies the hook script into the skill dir, but the hook must be registered in Claude Code's `settings.json` manually.

**Step A — locate the installed hook script.** The hook is a Python script (`track-interventions.py`) so it runs identically on macOS, Linux, and Windows. Probe, in order, and keep the first that exists:

```bash
for cand in \
  "$HOME/.claude/skills/wtf.setup/hooks/track-interventions.py" \
  "$PWD/.claude/skills/wtf.setup/hooks/track-interventions.py" \
  "$PWD/skills/wtf.setup/hooks/track-interventions.py"; do
  [ -f "$cand" ] && HOOK_PATH="$cand" && break
done
```

If none exist: warn the user that the hook script could not be found and skip hook registration.

**Step B — ask scope** (apply `../references/questioning-style.md`):

Call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Install the WTF intervention-tracker hook globally or only for this repo?"
- header: "Hook scope"
- options:
  - **Global (~/.claude/settings.json)** → runs in every repo that has `docs/steering/`
  - **This repo only (.claude/settings.json)** → scoped to this project
  - **Skip** → don't install the hook

Set `SETTINGS_FILE` accordingly:
- Global → `$HOME/.claude/settings.json`
- Per-repo → `.claude/settings.json`
- Skip → jump to step 9.

**Step C — patch settings.json idempotently.** Create the file if missing (`echo '{}' > "$SETTINGS_FILE"`). Then merge the two hook entries using `python3` (available on macOS/Linux; git-bash on Windows ships it via the installer or can be swapped for `py`). The registered command invokes the hook via `python3` so it works without a POSIX shell on Windows:

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

Re-running is safe — existing entries are detected by exact `command` string and not duplicated.

**Windows note:** if the user is on Windows without `python3`, skip the patch and print the JSON snippet for manual paste. Detect via `command -v python3 >/dev/null || echo 'manual'`.

Record `hook-installed: true|false|skipped` for the status report.

### 8b. Install the gh body helper

`gh-body.py` is a cross-platform utility that makes every GitHub issue/PR body read and write UTF-8-safe — it prevents the CP850 mojibake, newline collapse, and inline-`--body` corruption that `gh` suffers under PowerShell on Windows. Skills invoke it at `.wtf/gh-body.py`; installing it here means the guard is committed to the repo and shared with every teammate. See `../references/gh-body-helper.md`.

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

Commit `.wtf/gh-body.py` so the guard travels with the repo for every contributor. If `GHBODY_SRC` is empty (helper not found) or `cp` is unavailable (Windows without git-bash), tell the user to copy `gh-body.py` into `.wtf/` manually and note it — skills fall back to raw `gh` until then, which is unguarded on Windows.

**Step C — verify it actually runs.** Skills invoke the helper as `python3 .wtf/gh-body.py`, so test that *exact* form — it validates the interpreter name, that Python is present, and that the copy is valid, all in one shot:

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
- `wrong-name` → Python exists but not as `python3` (common on Windows: the python.org installer provides `python`/`py`, not `python3`). The skill commands call `python3`, so the guard will fail until the user adds a `python3` alias/shim. Show the working interpreter you found (e.g. `py -3`) and tell them to alias it.
- `no-python` → no Python 3 on PATH. The guard is inert; every body/comment op falls back to raw `gh`, which corrupts UTF-8 on Windows. Point the user to https://www.python.org/downloads/ and have them re-run setup.

Record `gh-body-helper: verified|wrong-name|no-python|not-installed` for the status report (`not-installed` if Step B could not copy the file).

### 9. Report status

Print a clear status summary covering every check:

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
  TASK.md                 ✅  (or ✅ installed from references)
PR template               ✅  (or ✅ installed from references)
Issue classification      ✅  native types (Epic/Feature/Task/Bug)  (or  ✅ labels: epic, feature, task, bug)
Lifecycle labels          ✅  implemented, designed, verified
Intervention hook         ✅  installed (global)  (or  ✅ installed (repo)  /  ⚪ skipped  /  ⚠️ manual paste required)
Body encoding guard       ✅  verified (python3)  (or  ⚠️ Python is 'py'/'python', not 'python3' — alias it or body ops fail  /  ⚠️ Python 3 not found — guard inert, raw-gh fallback  /  ⚠️ helper not copied)
─────────────────────────
Ready to use WTF. Start with `wtf.write-epic` to plan your first initiative.
```

If any item failed (gh not installed, not authenticated), replace the closing line with a clear "Fix the issues above before proceeding." and do not suggest next steps.

### 10. Offer to set up steering docs

If setup completed without fatal errors, call `AskUserQuestion` (per `../references/questioning-style.md`):
- question: "Setup complete. The steering docs (VISION.md, TECH.md, DESIGN.md, QA.md) capture your project's principles and standards — every skill reads them automatically. Would you like to create them now?"
- header: "Steering docs"
- options:
  - **Yes — set them up now** → run `wtf.steer-vision` (it will offer to chain to TECH, DESIGN, and QA at the end)
  - **Not now** → skip; skills will prompt you to create them on first use
