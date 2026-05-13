#!/usr/bin/env python3
"""WTF Intervention Tracker (cross-platform).

UserPromptSubmit: silently increments a counter when the user corrects Claude.
Stop:             notifies when the correction count reaches the threshold (default: 3).

Platform-agnostic state dir: $WTF_STATE_DIR, else $XDG_STATE_HOME/wtf,
else $HOME/.local/state/wtf, else $TMPDIR/wtf.
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

THRESHOLD = int(os.environ.get("WTF_INTERVENTION_THRESHOLD", "3"))

PATTERN = re.compile(
    r"(^no[,\.! ]|don't do|wrong|actually[, ]|stop that|that's not|"
    r"not what i|undo that|wait,? no|hold on,|revert that|incorrect|"
    r"that is wrong|you missed|you forgot)"
)


def state_dir() -> Path:
    candidates = []
    if os.environ.get("WTF_STATE_DIR"):
        candidates.append(Path(os.environ["WTF_STATE_DIR"]))
    if os.environ.get("XDG_STATE_HOME"):
        candidates.append(Path(os.environ["XDG_STATE_HOME"]) / "wtf")
    home = Path.home()
    candidates.append(home / ".local" / "state" / "wtf")
    candidates.append(Path(tempfile.gettempdir()) / "wtf")
    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            return c
        except OSError:
            continue
    sys.exit(0)


def counter_file() -> Path:
    try:
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "user"
    except Exception:
        user = "user"
    return state_dir() / f"interventions-{user}"


def read_count(path: Path) -> int:
    try:
        return int(path.read_text().strip() or "0")
    except (OSError, ValueError):
        return 0


def main() -> None:
    if not Path("docs/steering").is_dir():
        return

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    event = payload.get("hook_event_name", "")
    path = counter_file()

    if event == "UserPromptSubmit":
        prompt = (payload.get("prompt") or "").lower()
        if PATTERN.search(prompt):
            count = read_count(path) + 1
            try:
                path.write_text(str(count))
            except OSError:
                pass
        return

    if event == "Stop":
        count = read_count(path)
        if count >= THRESHOLD:
            print()
            print("-" * 60)
            print(f"  WTF Reflect  .  You've intervened {count} times this session.")
            print("  Run /wtf.reflect to capture learnings before they fade.")
            print("-" * 60)
            print()
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
