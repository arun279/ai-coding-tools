#!/usr/bin/env python3
"""PreToolUse gate: in an unattended run, the main loop may not hand-edit product code.

The session that worked never touched product code from the main loop; it built and fixed the workflow SCRIPTS and let workflows do the product edits (28 script edits, 0 product edits). The runs that failed did the inverse, hand-editing product source in main context and skipping the codex->independent-review->commit pipeline the prompt told them to use. The instruction to route product changes through the pipeline was present and ignored, so this enforces it rather than asking.

Scope: only unattended runs (owner away), and only the MAIN loop. Subagent/workflow tool calls carry agent_id and pass untouched, because they ARE the pipeline doing the work. Only Edit/Write/MultiEdit on product-source paths are denied; scripts, plans, docs, config, and the hooks themselves are never blocked. In an attended session it does nothing. Deny is a per-call block with a reason fed back to the model, so it re-routes rather than gets trapped.
"""
import json
import os
import re
import sys

# Paths the main loop must route through a workflow rather than hand-edit. Default: the usual source
# trees. Override with MAINLOOP_PRODUCT_PATHS (a regex matched against the file path).
PRODUCT_PATHS = os.environ.get("MAINLOOP_PRODUCT_PATHS", r"/(src|entrypoints|app|lib|components|pages|packages)/")

REASON = "Unattended run: implement product-source changes through a workflow rather than by hand, because a hand-edit in the main loop skips the independent review step and drifts uncaught when no one is watching. Use the working model prescribed in @~/.claude/CLAUDE.md. Edit workflow scripts, plans, docs, and config directly as much as you want; product source goes through that pipeline."


def is_unattended():
    return os.environ.get("CLAUDE_CODE_REMOTE") == "true" or bool(os.environ.get("CLAUDE_CODE_BRIDGE_SESSION_ID"))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("agent_id"):
        return 0
    if payload.get("tool_name") not in ("Edit", "Write", "MultiEdit"):
        return 0
    if not is_unattended():
        return 0
    path = (payload.get("tool_input") or {}).get("file_path", "")
    if not re.search(PRODUCT_PATHS, path):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": REASON}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
