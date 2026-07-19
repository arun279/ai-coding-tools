#!/usr/bin/env python3
"""Periodically re-inject the working model into the MAIN conversation and force an
adherence check, so long autonomous runs get challenged without the user present.

Scoping: subagent tool calls fire PostToolUse with the same session_id and
transcript_path as the main loop, but only they carry agent_id/agent_type. Their
absence is what identifies a main-loop call.
"""
import json
import os
import pathlib
import sys
import tempfile
import time

INTERVAL_SECONDS = int(os.environ.get("SELF_AUDIT_INTERVAL_SECONDS", 1800))

PREAMBLE = """DETERMINISTIC PROCESS SELF-AUDIT (automated hook on a timer, not the user).

You have been running for a while without user intervention, which is exactly when
process drift goes unnoticed. Stop and audit yourself honestly against the working
model reproduced in full below. Do not summarize it back; check your actual recent
behavior against it and name where you drifted. Where you have violated it, fix the
process before continuing and redo the work that was done in violation. If you have
been following it, say so in one line and carry on.

----- ~/.claude/CLAUDE.md -----
"""


def main() -> int:
    payload = json.load(sys.stdin)
    if payload.get("agent_id"):
        return 0

    claude_md = pathlib.Path.home() / ".claude" / "CLAUDE.md"
    if not claude_md.exists():
        return 0

    session_id = payload.get("session_id", "unknown")
    clock = pathlib.Path(tempfile.gettempdir()) / f"claude-self-audit-{session_id}"

    # First call of a session only starts the clock: CLAUDE.md is still fresh in
    # context at that point, so injecting it again would be noise.
    if not clock.exists():
        clock.touch()
        return 0
    if time.time() - clock.stat().st_mtime < INTERVAL_SECONDS:
        return 0
    clock.touch()

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": PREAMBLE + claude_md.read_text(),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
