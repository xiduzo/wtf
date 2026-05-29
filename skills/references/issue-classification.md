# Issue Classification — native types vs. labels

How every WTF skill labels an issue as an **Epic**, **Feature**, **Task**, or **Bug** — and how it finds issues of a given kind later. Read this from any skill that *sets* the kind of a new issue, *lists* issues of a kind, or *detects* the kind of an existing issue.

There are two mechanisms, because GitHub gates the nicer one:

- **`types`** — native [GitHub issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization). These are an **organization-only** feature (org owners define them; personal/user accounts cannot have them). When available, the issue *type* carries the classification and **labels are left free for your own segmentation** (e.g. `phase-2`, `frontend`).
- **`labels`** — the `epic` / `feature` / `task` / `bug` labels carry the classification. This is the portable fallback that works on **any** repo, including personal accounts.

`wtf.setup` picks the mode once and records it in `.wtf/config.json`. The two mechanisms are interchangeable for classification, but they are **not** the same as lifecycle labels: `designed` / `implemented` / `verified` are always labels in **both** modes — see `./lifecycle-labels.md`. Issue types replace only the *kind* label, never the lifecycle labels.

## Contents

- [The four WTF kinds](#the-four-wtf-kinds)
- [Resolve the mode](#resolve-the-mode) — set `$WTF_CLASS` once per session
- [Classify a new issue](#classify-a-new-issue) — write side (`write-*`, `report-bug`)
- [List issues of a kind](#list-issues-of-a-kind) — read side (`health`, `retro`, …)
- [Detect the kind of an existing issue](#detect-the-kind-of-an-existing-issue) — `refine`
- [Provision native types](#provision-native-types) — used by `wtf.setup` only
- [`gh` limitations to know](#gh-limitations-to-know)

## The four WTF kinds

| Kind | Type name | Label | Label color | Type color | Title prefix |
|---|---|---|---|---|---|
| Epic | `Epic` | `epic` | `5319e7` | `purple` | 🎯 |
| Feature | `Feature` | `feature` | `0075ca` | `blue` | 🚀 |
| Task | `Task` | `task` | `e4e669` | `yellow` | 🛠 |
| Bug | `Bug` | `bug` | `d73a4a` | `red` | 🐞 |

Type names are **capitalized** (`Epic`); labels are **lowercase** (`epic`). In `types` mode the search/`select` match on the capitalized type name; in `labels` mode everything is lowercase. Every organization ships `Task`/`Bug`/`Feature` as defaults — only `Epic` has to be created (see [Provision native types](#provision-native-types)).

## Resolve the mode

Run this **once** near the start of a skill's GitHub work and reuse `$WTF_CLASS` for the rest of the session. Source of truth is `.wtf/config.json` (written by `wtf.setup`); if it is missing, fall back to runtime detection, then to `labels` (the choice that works everywhere):

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

Used by `write-epic` / `write-feature` / `write-task` / `report-bug` **after** the issue is created. Create the issue *without* a kind label (so labels stay free in `types` mode), capture its number, then set `TYPE` and run this block. It sets the native type when the mode (and the type) allow, and falls back to the kind label otherwise — so it is always safe:

```bash
TYPE="Task"            # Epic | Feature | Task | Bug
ISSUE_NUMBER=<number from the created issue URL>

case "$TYPE" in
  Epic)    LABEL=epic;    COLOR=5319e7; DESC="Strategic initiative spanning multiple features" ;;
  Feature) LABEL=feature; COLOR=0075ca; DESC="User-facing capability delivered as a vertical slice" ;;
  Task)    LABEL=task;    COLOR=e4e669; DESC="Implementable vertical slice of a Feature" ;;
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

The `gh label create … || true` keeps `labels` mode self-healing if `wtf.setup` was never run or a label was deleted.

## List issues of a kind

Used by `health`, `retro`, `epic-to-features`, `write-task`, `spike`, `refine`, etc. The fields you request stay the same across modes — only the filter changes.

**Single kind** (`TYPE` capitalized, `LABEL` lowercase from the table):

```bash
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search "type:\"$TYPE\" state:open" --json number,title,labels,updatedAt --limit 200
else
  gh issue list --label "$LABEL" --state open --json number,title,labels,updatedAt --limit 200
fi
```

**Several kinds at once** (logical OR — e.g. the Epic/Feature/Task candidate list `refine` and `spike` show):

```bash
if [ "$WTF_CLASS" = types ]; then
  gh issue list --search 'state:open (type:"Epic" OR type:"Feature" OR type:"Task")' --json number,title --limit 10
else
  gh issue list --label "epic,feature,task" --state open --json number,title --limit 10
fi
```

(`--label "a,b,c"` is OR for labels; `type:"A" OR type:"B"` is OR for types.)

## Detect the kind of an existing issue

Used by `refine` to route validation. Returns the capitalized type name in `types` mode and the lowercase label in `labels` mode — **compare case-insensitively**:

```bash
ISSUE_NUMBER=<number>
if [ "$WTF_CLASS" = types ]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  KIND=$(gh api graphql -f query="{ repository(owner:\"${REPO%%/*}\", name:\"${REPO##*/}\"){ issue(number:$ISSUE_NUMBER){ issueType{ name } } } }" \
           --jq '.data.repository.issue.issueType.name' 2>/dev/null)
else
  KIND=$(gh issue view "$ISSUE_NUMBER" --json labels --jq '.labels[].name' | grep -iE '^(epic|feature|task|bug)$' | head -1)
fi
```

If `$KIND` is empty (no type set and no kind label), fall back to asking the user — see `wtf.refine`.

## Provision native types

**`wtf.setup` only.** Native types live at the **organization** level and require an **org owner**. Orgs ship `Task`/`Bug`/`Feature` by default; create whatever is missing (in practice just `Epic`) with the REST API. `color` must be one of `gray, blue, green, yellow, orange, red, pink, purple, null`:

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
create_type Task    yellow "Implementable vertical slice of a Feature"
create_type Bug     red    "Something is broken"
```

Creation needs the **"Issue Types" org write** permission (org owner). If the POST is forbidden, `wtf.setup` falls back to `labels` mode.

## `gh` limitations to know

- **`gh issue list --json issueType` does not exist** (verified on gh 2.92.0). You can *filter* by type server-side with `--search "type:\"X\""`, but to *read* one issue's type you must use the GraphQL `issue.issueType.name` query above. That is why the read snippets above never request an `issueType` JSON field.
- `--search 'type:"Task"'` returns nothing when no native types exist — which is exactly why `labels` mode is the safe default and why the mode is resolved before any query.
- Type names in `--search` are quoted and case-insensitive (`type:"task"` works); the GraphQL `select(.name=="Task")` match is **exact**, so keep the capitalized names from the table.
