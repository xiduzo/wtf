# Getting started

## Install

Install the skills from your project root:

```bash
npx skills add https://github.com/xiduzo/wtf
```

Open your AI assistant. Then run the setup skill:

```
/wtf.setup
```

To update the skills, run:

```bash
npx skills update
```

## Prerequisites

| Requirement | Notes |
| --- | --- |
| An AI assistant that supports skills | The [skills documentation](https://skills.sh/docs/faq) lists the supported runtimes |
| [GitHub CLI (`gh`)](https://cli.github.com) | Installed and authenticated with `gh auth login`. The token needs the `repo` scope and write access to the repo. |
| A GitHub repository | Most execution skills need it |

## What `wtf.setup` does

`wtf.setup` is the pre-flight check and installer. Run it once per repo. It checks `gh`, its authentication, the token scopes, and the write access to the repo. It installs the items below and asks the four [configuration](Configuration.md) questions. Then it prints a status report and offers to create the [steering docs](Steering-Docs.md).

| Item | Purpose |
| --- | --- |
| [`yahsan2/gh-sub-issue`](https://github.com/yahsan2/gh-sub-issue) | Links the Epic → Feature → Trace hierarchy as sub-issues |
| [`xiduzo/gh-issue-dependency`](https://github.com/xiduzo/gh-issue-dependency) | Adds native `Blocks` and `Blocked-by` links |
| [`github/gh-stack`](https://github.com/github/gh-stack) | Native stacked PRs. `wtf.create-pr` links each stacked Trace PR into a GitHub stack. Each PR then shows the stack map. |
| Issue and PR templates | Epic, Feature, Trace, and Bug templates in `.github/ISSUE_TEMPLATE/`, and the PR template |
| Issue classification | Native issue types in an organization, with a ☄️ Trace type. Labels in all other repos. |
| Lifecycle labels | `designed`, `implemented`, `verified` |
| Head-branch auto-delete | Enables **Automatically delete head branches** in the repo settings. Stacked Trace PRs need it to retarget after a merge. |
| `.wtf/config.json` | Your answers to the four setup questions. See [Configuration](Configuration.md). |
| `.wtf/gh-body.py` | A UTF-8-safe helper for issue and PR bodies. It keeps the bodies intact on Windows. |
| Shared references | A copy of the cross-skill reference docs, next to the installed skills |
| Intervention-tracker hook | Adds `UserPromptSubmit` and `Stop` entries to `settings.json`. After many corrections, it suggests `/wtf.reflect`. Setup asks for a global or a per-repo scope. |

## Optional

| Requirement | Needed for |
| --- | --- |
| [Figma](https://figma.com) account | Links to Figma frames in `wtf.design-feature` and `wtf.design-trace`. Both skills work without it. |
| `python3` in `PATH` | The hook registration, the body helper, and the config file in `wtf.setup`. Without it, setup prints the JSON for you to paste, and the body helper does not run. |

## Next

Write the [steering docs](Steering-Docs.md). Then start [planning](Planning.md).
