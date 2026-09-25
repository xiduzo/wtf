# Getting started

## Install

Install the skills from your project root:

```bash
npx skills add https://github.com/xiduzo/wtf
```

Open your AI assistant and run the setup skill:

```
/wtf.setup
```

Update the skills later with:

```bash
npx skills update
```

## Prerequisites

| Requirement | Notes |
| --- | --- |
| An AI assistant that supports skills | See the [skills documentation](https://skills.sh/docs/faq) for supported runtimes |
| [GitHub CLI (`gh`)](https://cli.github.com) | Installed and authenticated with `gh auth login`. The token needs the `repo` scope and write access to the repo. |
| A GitHub repository | Most execution skills need it |

## What `wtf.setup` does

`wtf.setup` is the pre-flight check and installer. Run it once per repo. It checks `gh`, its authentication, the token scopes, and repo write access. It installs the items below and asks the four [configuration](Configuration.md) questions. Then it prints a status report and offers to create the [steering docs](Steering-Docs.md).

| Item | Purpose |
| --- | --- |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | Epic → Feature → Trace sub-issue hierarchy |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | Native `Blocks` / `Blocked-by` links |
| [`github/gh-stack`](https://github.com/github/gh-stack) | Native stacked PRs. `wtf.create-pr` links each stacked Trace PR into a GitHub stack, so every PR shows the stack map. |
| Issue and PR templates | Epic, Feature, Trace, and Bug templates in `.github/ISSUE_TEMPLATE/`, plus the PR template |
| Issue classification | Native issue types in orgs, with a ☄️ Trace type. Labels everywhere else. |
| Lifecycle labels | `designed`, `implemented`, `verified` |
| Head-branch auto-delete | Turns on **Automatically delete head branches** in the repo settings. Stacked Trace PRs need it to retarget after a merge. |
| `.wtf/config.json` | Your answers to the four setup questions. See [Configuration](Configuration.md). |
| `.wtf/gh-body.py` | UTF-8-safe helper for issue and PR bodies. Prevents body corruption on Windows. |
| Shared references | A copy of the cross-skill reference docs next to the installed skills |
| Intervention-tracker hook | `UserPromptSubmit` and `Stop` entries in `settings.json`. Nudges you toward `/wtf.reflect` after repeated corrections. Setup asks for global or per-repo scope. |

## Optional

| Requirement | Needed for |
| --- | --- |
| [Figma](https://figma.com) account | `wtf.design-feature` and `wtf.design-trace`, only to link Figma frames. Both skills scaffold without it. |
| `python3` in `PATH` | Hook registration, the body helper, and the config writes in `wtf.setup`. Without it, setup prints the JSON for manual paste and the body helper stays inactive. |

## Next

Write the [steering docs](Steering-Docs.md), then start [planning](Planning.md).
