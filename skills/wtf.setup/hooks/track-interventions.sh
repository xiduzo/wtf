#!/bin/sh
# WTF Intervention Tracker (POSIX)
#
# UserPromptSubmit: silently increments a counter when the user corrects Claude.
# Stop:            notifies when the correction count reaches the threshold (default: 3).
#
# Platform-agnostic state dir: $WTF_STATE_DIR, else $XDG_STATE_HOME/wtf,
# else $HOME/.local/state/wtf, else $TMPDIR/wtf.

THRESHOLD=${WTF_INTERVENTION_THRESHOLD:-3}

STATE_DIR="${WTF_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/wtf}"
if ! mkdir -p "$STATE_DIR" 2>/dev/null; then
  STATE_DIR="${TMPDIR:-/tmp}/wtf"
  mkdir -p "$STATE_DIR" 2>/dev/null || exit 0
fi
COUNTER_FILE="$STATE_DIR/interventions-$(id -un 2>/dev/null || echo user)"

# Only act inside WTF-enabled repo
[ -d "docs/steering" ] || exit 0

INPUT=$(cat)

parse_json() {
  # $1 = key. Requires python3; silently no-op otherwise.
  command -v python3 >/dev/null 2>&1 || return 1
  printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$1',''))" 2>/dev/null
}

HOOK_EVENT=$(parse_json hook_event_name)

case "$HOOK_EVENT" in
  UserPromptSubmit)
    PROMPT=$(parse_json prompt | tr '[:upper:]' '[:lower:]')
    if printf '%s' "$PROMPT" | grep -qE "(^no[,\.! ]|don't do|wrong|actually[, ]|stop that|that's not|not what i|undo that|wait,? no|hold on,|revert that|incorrect|that is wrong|you missed|you forgot)"; then
      COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
      echo $((COUNT + 1)) > "$COUNTER_FILE"
    fi
    ;;
  Stop)
    COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
    if [ "$COUNT" -ge "$THRESHOLD" ]; then
      echo ""
      echo "------------------------------------------------------------"
      echo "  WTF Reflect  .  You've intervened $COUNT times this session."
      echo "  Run /wtf.reflect to capture learnings before they fade."
      echo "------------------------------------------------------------"
      echo ""
    fi
    ;;
esac
