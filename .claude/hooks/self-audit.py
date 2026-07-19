#!/usr/bin/env python3
"""Periodic re-grounding checkpoint for a long autonomous Claude Code session.

A PostToolUse hook that, at most once per INTERVAL_SECONDS, injects a block of
`additionalContext` into the MAIN conversation so a long unattended run gets
re-grounded before drift or stale assumptions compound. The block reproduces the
working model (~/.claude/CLAUDE.md), points at the session's memories and durable
notes to re-read, reports the REAL context-window usage measured from the
transcript, and ends by making the agent WRITE a short status (a forcing function:
a passively re-read reminder falls into a low-attention region and gets skimmed,
whereas self-authored, ground-truth-tied text lands in the model's own attention).

Why PostToolUse and not Stop: the target case is a run that is NOT yielding to the
user, which is exactly when a Stop hook would not fire. PostToolUse fires through a
heads-down burst, and its per-call cost is a cheap stat that bails until the timer
is due.

Scoping: subagent tool calls fire PostToolUse with the same session_id and
transcript_path as the main loop, but only they carry agent_id/agent_type. Their
absence identifies a main-loop call, so the checkpoint lands in the driving context
and subagents never burn the interval.

Cadence: a per-session clock file under the temp dir. The first tool call only
starts the clock (CLAUDE.md is still fresh at session start); thereafter the block
is injected once the clock is older than INTERVAL_SECONDS. The interval is claimed
under an flock so a parallel tool batch crossing the threshold injects once, not
once per tool.
"""
import fcntl
import json
import os
import pathlib
import sys
import tempfile
import time

INTERVAL_SECONDS = int(os.environ.get("SELF_AUDIT_INTERVAL_SECONDS", 1800))


def measure_context_tokens(transcript_path):
    """Real context-window occupancy from the last main-loop usage block.

    Streams the transcript (holding one line at a time, so memory is bounded even
    for a large file) and parses only lines that carry a usage object, skipping the
    many tool-result and user lines cheaply. Sums the input side of the most recent
    assistant turn (input + cache_read + cache_creation), which is exactly Claude
    Code's own `used_percentage` formula (output tokens are excluded). Returns None
    if the transcript cannot be read or has no usage block, so an unmeasurable run
    injects no number rather than a guessed one.
    """
    latest_usage = None
    try:
        with open(transcript_path, "r", errors="replace") as handle:
            for line in handle:
                if '"usage"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if entry.get("agent_id") or entry.get("isSidechain"):
                    continue
                message = entry.get("message")
                usage = message.get("usage") if isinstance(message, dict) else None
                if isinstance(usage, dict) and ("cache_read_input_tokens" in usage or "input_tokens" in usage):
                    latest_usage = usage
    except OSError:
        return None
    if latest_usage is None:
        return None
    return (
        latest_usage.get("input_tokens", 0)
        + latest_usage.get("cache_read_input_tokens", 0)
        + latest_usage.get("cache_creation_input_tokens", 0)
    )


def context_usage_line(transcript_path):
    tokens = measure_context_tokens(transcript_path) if transcript_path else None
    if tokens is None:
        return None
    return (
        f"Your context usage, read from your own transcript rather than estimated: about {tokens:,} "
        f"tokens are in your context window as of your last turn (roughly {tokens / 1_000_000 * 100:.0f}% "
        f"of a 1M-token window, {tokens / 200_000 * 100:.0f}% of a 200K-token window). Use the size of "
        "your own window to turn that into a real utilization, and judge your context-limit rule against "
        "that number instead of a feeling."
    )


def memory_pointers(transcript_path):
    """Concrete paths to the memory stores Claude Code creates by convention.

    Only the user-level and project-level memory directories, since those are part
    of the standard layout and can be located reliably. Task-specific artifacts
    (plans, handoffs, worklogs) are NOT enumerated here because they are not created
    by default and may not exist; the injected text asks Claude to find its own.
    """
    pointers = []
    user_memory = pathlib.Path.home() / ".claude" / "memory"
    if user_memory.is_dir():
        pointers.append(f"- your user-level memories: {user_memory}")
    if transcript_path:
        project_memory = pathlib.Path(transcript_path).parent / "memory"
        if project_memory.is_dir():
            pointers.append(
                f"- your project memories: {project_memory} (start with MEMORY.md, then the files it indexes)"
            )
    return "\n".join(pointers)


def claim_interval(clock):
    """True if this call may inject now. Reset the interval under an flock so that
    concurrent hooks from a parallel tool batch let exactly one through."""
    try:
        with open(clock, "r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if time.time() - clock.stat().st_mtime < INTERVAL_SECONDS:
                return False
            os.utime(clock, None)
            return True
    except OSError:
        return False


def build_injection(transcript_path, claude_md):
    pointers = memory_pointers(transcript_path)
    if pointers:
        memory_section = (
            "Re-read your standing memories rather than trust your recollection of them, since another "
            "session may have changed them since you last looked:\n" + pointers
        )
    else:
        memory_section = (
            "Re-read your standing user-level and project-level memories rather than trust your "
            "recollection of them."
        )
    memory_section += (
        "\nThen find and skim any durable artifacts you have created for this task (plans, handoffs, "
        "decision logs, worklogs, scratchpad notes) and pull in what is relevant. Do not assume any "
        "particular file exists; look for what is actually there."
    )

    sections = [
        f"Automated re-grounding checkpoint: a periodic timer (about every {INTERVAL_SECONDS // 60} minutes) "
        "placed this between your tool calls, so it is not a message from the user. Long autonomous runs "
        "are where standing instructions quietly go stale and process drift creeps in unnoticed, which is "
        "why the material below is reproduced as current ground truth.",
        "Your working model, reproduced so it is fresh rather than recalled from a load many turns ago:\n"
        f"----- ~/.claude/CLAUDE.md -----\n{claude_md}",
        memory_section,
    ]
    usage = context_usage_line(transcript_path)
    if usage:
        sections.append(usage)
    sections.append(
        "Before your next tool call, write a short status to the chat, so this checkpoint lands in your "
        "own output instead of being skimmed. Make it specific to right now, not a generic reassurance, "
        "four lines:\n"
        "- the one task you are actively working on;\n"
        "- your last non-trivial decision and the specific principle above it followed or bent;\n"
        "- your measured context figure above, and whether it means keep going or start a handoff;\n"
        "- your next concrete step.\n"
        "If writing that surfaces a drift from the working model or your memories, correct it before "
        "continuing and say what you changed."
    )
    return "\n\n".join(sections)


def main() -> int:
    payload = json.load(sys.stdin)
    if payload.get("agent_id"):
        return 0

    session_id = payload.get("session_id", "unknown")
    clock = pathlib.Path(tempfile.gettempdir()) / f"claude-self-audit-{session_id}"

    # First tool call of the session only starts the clock: CLAUDE.md is still fresh
    # in context at that point, so injecting it again would be noise.
    if not clock.exists():
        clock.touch()
        return 0
    # Hot path, taken on almost every tool call: a single stat, then bail until due.
    try:
        if time.time() - clock.stat().st_mtime < INTERVAL_SECONDS:
            return 0
    except OSError:
        return 0

    claude_md = pathlib.Path.home() / ".claude" / "CLAUDE.md"
    if not claude_md.exists():
        return 0
    # Slow path (~once per interval): everything below runs only when a checkpoint
    # is actually due, so the flock and transcript read never touch the hot path.
    if not claim_interval(clock):
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": build_injection(payload.get("transcript_path"), claude_md.read_text()),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
