#!/usr/bin/env bash
# Regenerate the vendored copy of the cross-skill references that rides along
# in the wtf.setup payload.
#
# WHY: `npx skills add` installs each skills/wtf.*/ directory individually.
# skills/references/ has no SKILL.md, so it never ships — a consumer's installed
# skills would resolve `../references/foo.md` against an empty <skills-root>/references/.
# To fix that, wtf.setup carries a copy and writes it into <skills-root>/references/
# at setup time (see SKILL.md "Install shared skill references").
#
# SOURCE OF TRUTH is skills/references/. This directory is GENERATED — never edit
# skills/wtf.setup/shared-references/ by hand. Re-run this after changing any
# reference doc:
#
#   bash skills/wtf.setup/sync-shared-references.sh
#
# eval-fixture-convention.md is intentionally excluded — it is a dev-only doc
# (eval authoring) and is never loaded by a skill at runtime.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$here/../references"
dst="$here/shared-references"

mkdir -p "$dst"
# Drop stale files so deletions in source propagate.
rm -f "$dst"/*.md
for f in "$src"/*.md; do
  name="$(basename "$f")"
  [ "$name" = "eval-fixture-convention.md" ] && continue
  cp "$f" "$dst/$name"
done

echo "Synced shared references → $dst:"
ls -1 "$dst"
