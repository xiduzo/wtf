---
name: wtf:setup
description: This skill should be used when a user wants to set up WTF in a new repository, verify their environment is ready, check that GitHub CLI is installed and authenticated, install required gh extensions, or ensure the .github/ISSUE_TEMPLATE/ templates are in place — for example "set up wtf", "run setup", "check my environment", "install wtf templates", or "verify everything is configured". Run once per repo when onboarding, or when a contributor joins the project.
---

# Setup

Pre-flight check and installer for the WTF workflow. Validates the GitHub CLI, installs required extensions, and ensures `.github/ISSUE_TEMPLATE/` contains all required templates so both agents and humans can create structured issues.

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
gh extension install torynet/gh-issue-dependency
```

If installation fails (e.g. network error, permissions), warn the user that relationship tracking will be unavailable until the extension is installed. Note the failure — it will be included in the final status report.

After attempting installation, verify the command syntax for any newly installed extension:

```bash
gh sub-issue --help
gh issue-dependency --help
```

Record two booleans for the final report:
- `gh-sub-issue-available`: true if `yahsan2/gh-sub-issue` is installed and working
- `gh-issue-dependency-available`: true if `torynet/gh-issue-dependency` is installed and working

### 4. Detect repo context

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

If this fails (not inside a git repo, or no GitHub remote), warn the user and note that issue creation will not work until the repo is connected to GitHub. Continue to the template check regardless.

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
# The references folder is at: skills/setup/references/
cp skills/setup/references/BUG.md .github/ISSUE_TEMPLATE/BUG.md
cp skills/setup/references/EPIC.md .github/ISSUE_TEMPLATE/EPIC.md
cp skills/setup/references/FEATURE.md .github/ISSUE_TEMPLATE/FEATURE.md
cp skills/setup/references/TASK.md .github/ISSUE_TEMPLATE/TASK.md
```

Only copy files that are missing — do not overwrite existing templates. After copying, list the final contents of `.github/ISSUE_TEMPLATE/` to confirm.

### 6. Report status

Print a clear status summary covering every check:

```
WTF Setup — Status Report
─────────────────────────
gh CLI installed          ✅
gh authenticated          ✅
gh-sub-issue extension    ✅  (or ⚠️ not installed — relationship links unavailable)
gh-issue-dependency ext   ✅  (or ⚠️ not installed — dependency links unavailable)
Repo context              ✅  owner/repo  (or ⚠️ not detected)
Issue templates
  BUG.md                  ✅  (or ✅ installed from references)
  EPIC.md                 ✅  (or ✅ installed from references)
  FEATURE.md              ✅  (or ✅ installed from references)
  TASK.md                 ✅  (or ✅ installed from references)
─────────────────────────
Ready to use WTF. Start with /wtf:write-epic to plan your first initiative.
```

If any item failed (gh not installed, not authenticated), replace the closing line with a clear "Fix the issues above before proceeding." and do not suggest next steps.
