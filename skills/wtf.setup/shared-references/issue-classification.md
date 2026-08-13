# Issue Classification — native types vs. labels

Every WTF skill uses this file to mark an issue as an **Epic**, **Feature**, **Trace**, or **Bug**. Skills also use it to find issues of a given kind later.

Read this from any skill that *sets* the kind of a new issue. Also read it when a skill *lists* issues of a kind. Also read it when a skill *detects* the kind of an existing issue.

GitHub offers two mechanisms. GitHub gates the better one.

- **`types`** — native [GitHub issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization). These work in **organizations only**. Org owners define them. Personal and user accounts cannot use them. When available, the issue *type* carries the classification. **Labels stay free for your own segmentation** (for example `phase-2`, `frontend`).
- **`labels`** — the `epic` / `feature` / `trace` / `bug` labels carry the classification. This fallback works on **any** repo, including personal accounts.

`wtf.setup` picks the mode once. It records the mode in `.wtf/config.json`. The two mechanisms are interchangeable for classification. They are **not** the same as lifecycle labels. `designed` / `implemented` / `verified` are always labels in **both** modes — see `./lifecycle-labels.md`. Issue types replace only the *kind* label. They never replace lifecycle labels.

## Contents

- [The four WTF kinds](#the-four-wtf-kinds)
- [Resolve the mode](#resolve-the-mode) — set `$WTF_CLASS` once per session
- [Classify a new issue](#classify-a-new-issue) — write side (`write-*`, `report-bug`)
- [List issues of a kind](#list-issues-of-a-kind) — read side (`health`, `retro`, …)
- [Detect the kind of an existing issue](#detect-the-kind-of-an-existing-issue) — `refine`
- [Legacy Task reads](#legacy-task-reads) — old repos, read side only
- [Provision native types](#provision-native-types) — used by `wtf.setup` only
- [`gh` limitations to know](#gh-limitations-to-know)

## The four WTF kinds

| Kind | Type name | Label | Label color | Type color | Title prefix |
|---|---|---|---|---|---|
| Epic | `Epic` | `epic` | `5319e7` | `purple` | 🎯 |
| Feature | `Feature` | `feature` | `0075ca` | `blue` | 🚀 |
| Trace | `Trace` | `trace` | `e4e669` | `yellow` | ☄️ |
| Bug | `Bug` | `bug` | `d73a4a` | `red` | 🐞 |

Type names are **capitalized** (`Epic`). Labels are **lowercase** (`epic`). In `types` mode, search and `select` match the capitalized type name. In `labels` mode, everything is lowercase. Every organization ships `Task`/`Bug`/`Feature` as defaults. The shipped `Task` default is simply unused — WTF write paths never create Tasks. `Epic` and `Trace` must be created (see [Provision native types](#provision-native-types)).

## Resolve the mode

Run this **once** near the start of a skill's GitHub work. Reuse `$WTF_CLASS` for the rest of the session. The source of truth is `.wtf/config.json` (written by `wtf.setup`). If it is missing, fall back to runtime detection. Then fall back to `labels` (the choice that works everywhere):

```bash
WTF_CLASS=$(python3 - <<'PY' 2>/dev/null || true
import json
try:
    print((json.load(open(".wtf/config.json")).get("classification") or "").strip())
except Exception:
    pass
PY
)
if [ -z "$WTF_CLASS" ]; then
  # No config — does this repo's owner expose native issue types?
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
  N=$(gh api graphql -f query="{ repository(owner:\"${REPO%%/*}\", name:\"${REPO##*/}\"){ issueTypes(first:1){ totalCount } } }" \
        --jq '.data.repository.issueTypes.totalCount' 2>/dev/null)
  case "$N" in ''|0|null) WTF_CLASS=labels ;; *) WTF_CLASS=types ;; esac
fi
```

`$WTF_CLASS` is now either `types` or `labels`.

## Classify a new issue

Used by `write-epic` / `write-feature` / `write-trace` / `report-bug` **after** the issue is created. Create the issue *without* a kind label. That keeps labels free in `types` mode. Capture its number. Then set `TYPE` and run this block. It sets the native type when the mode and the type allow. Otherwise it falls back to the kind label. So it is always safe:

```bash
TYPE="Trace"           # Epic | Feature | Trace | Bug
ISSUE_NUMBER=<number from the created issue URL>

case "$TYPE" in
  Epic)    LABEL=epic;    COLOR=5319e7; DESC="Strategic initiative spanning multiple features" ;;
  Feature) LABEL=feature; COLOR=0075ca; DESC="User-facing capability delivered as a vertical slice" ;;
  Trace)   LABEL=trace;   COLOR=e4e669; DESC="One pass over a Feature's spine — one story, one Scenario Claim, end-to-end" ;;
  Bug)     LABEL=bug;     COLOR=d73a4a; DESC="Something is broken" ;;
esac

if [ "$WTF_CLASS" = types ]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  ISSUE_ID=$(gh api graphql -f query="{ repository(owner:\"${REPO%%/*}\", name:\"${REPO##*/}\"){ issue(number:$ISSUE_NUMBER){ id } } }" \
               --jq '.data.repository.issue.id' 2>/dev/null)
  TYPE_ID=$(gh api graphql -f query="{ repository(owner:\"${REPO%%/*}\", name:\"${REPO##*/}\"){ issueTypes(first:25){ nodes{ id name } } } }" \
              --jq ".data.repository.issueTypes.nodes[] | select(.name==\"$TYPE\") | .id" 2>/dev/null)
  if [ -n "$ISSUE_ID" ] && [ -n "$TYPE_ID" ]; then
    gh api graphql -f query="mutation { updateIssue(input:{ id:\"$ISSUE_ID\", issueTypeId:\"$TYPE_ID\" }){ issue{ number } } }" >/dev/null 2>&1
  else
    # Type not provisioned — fall back to the label so the issue is still classified.
    gh label create "$LABEL" --color "$COLOR" --description "$DESC" 2>/dev/null || true
    gh issue edit "$ISSUE_NUMBER" --add-label "$LABEL"
  fi
else
  gh label create "$LABEL" --color "$COLOR" --description "$DESC" 2>/dev/null || true
  gh issue edit "$ISSUE_NUMBER" --add-label "$LABEL"
fi
```

The `gh label create … || true` keeps `labels` mode self-healing. It still works if `wtf.setup` was never run. It still works if a label was deleted.

## List issues of a kind

Used by `health`, `retro`, `epic-to-features`, `write-trace`, `spike`, `refine`, and similar skills. The fields you request stay the same across modes. Only the filter changes.

**Single kind** (`TYPE` capitalized, `LABEL` lowercase from the table):

```bash
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search "type:\"$TYPE\" state:open" --json number,title,labels,updatedAt --limit 200
else
  gh issue list --label "$LABEL" --state open --json number,title,labels,updatedAt --limit 200
fi
```

**Several kinds at once** (logical OR — for example the Epic/Feature/Trace candidate list `refine` and `spike` show):

```bash
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search 'state:open (type:"Epic" OR type:"Feature" OR type:"Trace")' --json number,title --limit 10
else
  gh issue list --label "epic,feature,trace" --state open --json number,title --limit 10
fi
```

(`--label "a,b,c"` is OR for labels. `type:"A" OR type:"B"` is OR for types.)

When the repo may hold legacy Task issues, extend the filter — see [Legacy Task reads](#legacy-task-reads).

## Detect the kind of an existing issue

Used by `refine` to route validation. Returns the capitalized type name in `types` mode. Returns the lowercase label in `labels` mode. **Compare case-insensitively**:

```bash
ISSUE_NUMBER=<number>
if [ "$WTF_CLASS" = types ]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  KIND=$(gh api graphql -f query="{ repository(owner:\"${REPO%%/*}\", name:\"${REPO##*/}\"){ issue(number:$ISSUE_NUMBER){ issueType{ name } } } }" \
           --jq '.data.repository.issue.issueType.name' 2>/dev/null)
else
  KIND=$(gh issue view "$ISSUE_NUMBER" --json labels --jq '.labels[].name' | grep -iE '^(epic|feature|trace|bug|task)$' | head -1)
fi
```

If `$KIND` is `Task` or `task`, treat the issue as a legacy Trace (see [Legacy Task reads](#legacy-task-reads)). If `$KIND` is empty (no type set and no kind label), ask the user. See `wtf.refine`.

## Legacy Task reads

Repos that predate the Trace model hold `Task` issues (type `Task`, label `task`, prefix 🛠). Read paths treat them as legacy Traces. `wtf.health`, `wtf.refine`, and `wtf.retro` then stay complete in migrated repos.

- **List** — when the repo may hold legacy Tasks, add the legacy filter. In `types` mode: `(type:"Trace" OR type:"Task")`. In `labels` mode: `--label "trace,task"`.
- **Detect** — the detect block above already matches `task`. Map `Task`/`task` to the Trace kind before you route.

Write paths never create Tasks. Do not set the `Task` type on a new issue. Do not add the `task` label. No relabel migration runs — legacy Task issues stay as they are.

## Provision native types

**`wtf.setup` only.** Native types live at the **organization** level. They need an **org owner**. Orgs ship `Task`/`Bug`/`Feature` by default. No org ships a `Trace` type. Create whatever is missing — in practice `Epic` **and** `Trace` — with the REST API. Never create a `Task` type. The shipped `Task` default stays unused. `color` must be one of `gray, blue, green, yellow, orange, red, pink, purple, null`:

```bash
# $OWNER is the org login. Create a type only if a same-named one doesn't already exist.
EXISTING=$(gh api "orgs/$OWNER/issue-types" --jq '.[].name' 2>/dev/null)
create_type() {  # $1=name $2=color $3=description
  printf '%s\n' "$EXISTING" | grep -qix "$1" && return 0
  gh api -X POST "orgs/$OWNER/issue-types" \
    -f name="$1" -f color="$2" -f description="$3" -F is_enabled=true >/dev/null 2>&1 \
    && echo "  + created issue type: $1"
}
create_type Epic    purple "Strategic initiative spanning multiple features"
create_type Feature blue   "User-facing capability delivered as a vertical slice"
create_type Trace   yellow "One pass over a Feature's spine — one story, one Scenario Claim, end-to-end"
create_type Bug     red    "Something is broken"
```

Creation needs the **"Issue Types" org write** permission (org owner). If the POST is forbidden, `wtf.setup` falls back to `labels` mode.

## `gh` limitations to know

- **`gh issue list --json issueType` does not exist** (verified on gh 2.92.0). You can *filter* by type server-side with `--search "type:\"X\""`. To *read* one issue's type you must use the GraphQL `issue.issueType.name` query above. That is why the read snippets above never request an `issueType` JSON field.
- `--search 'type:"Trace"'` returns nothing when no native types exist. That is why `labels` mode is the safe default. That is why the mode is resolved before any query.
- Type names in `--search` are quoted and case-insensitive (`type:"trace"` works). The GraphQL `select(.name=="Trace")` match is **exact**. Keep the capitalized names from the table.
