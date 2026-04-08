#!/bin/bash
# WTF Intervention Tracker
#
# UserPromptSubmit: silently increments a counter when the user corrects Claude.
# Stop:            notifies when the correction count reaches the threshold (default: 3).
#
# Writes counter to /tmp/wtf-interventions-<user> so it resets between reboots
# but persists across context compactions within a working session.

COUNTER_FILE="/tmp/wtf-interventions-$(whoami)"
THRESHOLD=3

# Only act if docs/steering/ exists in cwd — this is a WTF-enabled project
if [ ! -d "docs/steering" ]; then
  exit 0
fi

INPUT=$(cat)
HOOK_EVENT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('hook_event_name',''))" 2>/dev/null)

case "$HOOK_EVENT" in
  UserPromptSubmit)
    PROMPT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt','').lower())" 2>/dev/null)

    # Detect correction / frustration language
    # Matches: "no,", "no.", "no!", "don't", "wrong", "actually", "stop that",
    #          "that's not", "not what i", "undo that", "wait no", "hold on",
    #          "revert that", "incorrect", "that is wrong", "you missed"
    if echo "$PROMPT" | grep -qiE "(^no[,\.! ]|don't do|wrong|actually[, ]|stop that|that's not|not what i|undo that|wait[,]? no|hold on[,]|revert that|incorrect|that is wrong|you missed|you forgot)"; then
      COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo "0")
      echo $((COUNT + 1)) > "$COUNTER_FILE"
    fi
    # No stdout output — don't inject noise into Claude's context
    ;;

  Stop)
    COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo "0")
    if [ "$COUNT" -ge "$THRESHOLD" ]; then
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "  WTF Reflect  ·  You've intervened $COUNT times this session."
      echo "  Run /wtf:reflect to capture learnings before they fade."
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
    fi
    ;;
esac
