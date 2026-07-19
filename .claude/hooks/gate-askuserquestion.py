#!/usr/bin/env python3
"""PreToolUse gate on AskUserQuestion.

Registered in settings.json with matcher "AskUserQuestion", so it runs only when the agent is about to ask the owner a question.

In an unattended run the owner is away, so a question blocks the entire session until they happen to return. That is the failure this exists to prevent: a run that stalled for hours on a decidable question. In that case this denies the call and tells the agent to decide it itself, or to defer a genuinely irreversible owner-only action and keep working. In an attended terminal session it does nothing and the question proceeds normally.

Unattended is detected from the environment (there is no input field for it): CLAUDE_CODE_REMOTE == "true" is a remote web run, and CLAUDE_CODE_BRIDGE_SESSION_ID being set means a local session with Remote Control attached. Deny is a per-call block with a reason fed back to the model; it does not trap the turn the way a Stop hook can, so the agent simply proceeds on its own judgment.
"""
import json
import os
import sys

REASON = "Unattended run (remote or Remote Control): the user may be away, and an AskUserQuestion blocks the whole session until they return. Decide this yourself wherever you can: read ~/.claude/CLAUDE.md now rather than relying on memory, weigh it against the project's stated goals, and proceed on your own best recommendation. Reserve the user for actions that are irreversible and owner-only: publishing or acting under their identity, spending money, deleting their data, making a public or legal commitment, and the like. For one of those, skip just that action, record it in a durable note for them to decide later, flag it in the chat, raise it again once you finish your other work, and keep going on everything else. Stop and wait for the user only when nothing else remains for you to do."


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
