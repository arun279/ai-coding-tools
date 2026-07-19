#!/usr/bin/env python3
"""PreToolUse gate on AskUserQuestion.

Registered in settings.json with matcher "AskUserQuestion", so it runs only when the agent is about to ask the owner a question.

In an unattended run the owner is away, so a question blocks the entire session until they happen to return. That is the failure this exists to prevent: a run that stalled for hours on a decidable question. In that case this denies the call and tells the agent to decide it itself, or to defer a genuinely irreversible owner-only action and keep working. In an attended terminal session it does nothing and the question proceeds normally.

Unattended is detected from the environment (there is no input field for it): CLAUDE_CODE_REMOTE == "true" is a remote web run, and CLAUDE_CODE_BRIDGE_SESSION_ID being set means a local session with Remote Control attached. Deny is a per-call block with a reason fed back to the model; it does not trap the turn the way a Stop hook can, so the agent simply proceeds on its own judgment.
"""
import json
import os
import sys

REASON = "You are in an unattended run (remote or Remote Control), the user might be away and an AskUserQuestion blocks the whole session until they can pay attention to this. If it's possible for you to decide this yourself against ~/.claude/CLAUDE.md (READ IT, DON'T RELY ON YOUR RECOLLECTION) and the project's north star, do so using your own best recommendation. Do not wait on the user if you don't need to. The type of things genuinely require the user are are irreversible and owner-only: publishing or acting under their identity, spending money, deleting their data, a public or legal commitment, etc. If you hit one of those or one like it, skip just that action, record it in a durable record for them to decide later, mention it in the chat (and also bring it up once you're done with all your tasks), and keep working on everything else. If you're able proceed now with your own decision rather than asking or stop and wait for the user assuming you have no other tasks you can work on while you wait."


def is_unattended():
    return os.environ.get("CLAUDE_CODE_REMOTE") == "true" or bool(os.environ.get("CLAUDE_CODE_BRIDGE_SESSION_ID"))


def main() -> int:
    try:
        json.load(sys.stdin)
    except ValueError:
        pass
    if not is_unattended():
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": REASON}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
