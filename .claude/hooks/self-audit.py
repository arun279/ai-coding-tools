#!/usr/bin/env python3
"""Periodic re-grounding checkpoint for a long autonomous Claude Code session.

A PostToolUse hook that, at most once per INTERVAL_SECONDS, injects a short block of `additionalContext` into the MAIN conversation so a long unattended run gets re-grounded before drift or stale assumptions compound.

Why it POINTS at the instructions instead of inlining them: Claude Code caps hook output (additionalContext / systemMessage / stdout) at 10,000 characters and replaces anything larger with a 2KB preview plus a file path. ~/.claude/CLAUDE.md alone now exceeds that cap, so an inlined copy is delivered only as a truncated preview and the actual instructions never reach the model. An earlier version of this hook inlined the full file and hit exactly that: the model received a header and the first ~15 lines of CLAUDE.md, and none of the ask. So this block stays well under the cap and DIRECTS the model to re-read the live files, which also gives it the current instructions rather than a stale copy.

The block carries three things, all delivered whole: a directive to re-read the working model + memories + this task's durable artifacts, the REAL context-window usage measured from the transcript, and a forcing function (write a short status) so the checkpoint lands in the model's own output instead of being skimmed.

Why PostToolUse and not Stop: the target case is a run that is NOT yielding to the user, which is exactly when a Stop hook would not fire. PostToolUse fires through a heads-down burst, and its per-call cost is a cheap stat that bails until due.

Scoping: subagent tool calls fire PostToolUse with the same session_id and transcript_path as the main loop, but only they carry agent_id/agent_type. Their absence identifies a main-loop call, so the checkpoint lands in the driving context and subagents never burn the interval.

Cadence: a per-session clock file under the temp dir. The first tool call only starts the clock; thereafter the block is injected once the clock is older than INTERVAL_SECONDS. The interval is claimed under an flock so a parallel tool batch crossing the threshold injects once, not once per tool.
"""
import fcntl
import json
import os
import pathlib
import sys
import tempfile
import time

INTERVAL_SECONDS = int(os.environ.get("SELF_AUDIT_INTERVAL_SECONDS", 1800))
START_DELAY_SECONDS = int(os.environ.get("SELF_AUDIT_START_DELAY_SECONDS", 0))

# The injected checkpoint. Plain WYSIWYG template: each paragraph is one line, real newlines are real
# newlines in the output, and {minutes}/{targets}/{context} are filled in by build_injection. Edit freely.
INJECTION = """Automated re-grounding checkpoint: a periodic timer (about every {minutes} minutes) fired this between your tool calls, so it is not a message from the user. On a long run your standing instructions scroll out of attention and drift sets in unnoticed. Do not skim this.

First, before your next tool call, re-read these in full now. Don't ignore it to save context, this is vital to the health of the session. They are your operating instructions and the current source of truth; do not trust your memory of them, and this checkpoint's questions assume you have just re-read them:
{targets}{context}

Then write a short status to the chat, so this checkpoint lands in your own output instead of being skimmed. Make it specific to right now, not a generic reassurance, four lines:
- the task(s) you are actively working on;
- your last non-trivial decision and the ~/.claude/CLAUDE.md principle it followed or bent (name the principle, which requires having just re-read the file);
- what your measured context above means: keep going, or start a handoff;
- your next concrete step(s).
If re-reading surfaces a drift from your instructions or memories, correct it before continuing and say what you changed."""


def measure_context_tokens(transcript_path):
    """Real context-window occupancy from the last main-loop usage block.

    Streams the transcript (one line at a time, so memory is bounded even for a large file) and parses only lines carrying a usage object. Sums the input side of the most recent assistant turn (input + cache_read + cache_creation), which is exactly Claude Code's own used_percentage formula (output tokens excluded). Returns None if unreadable or no usage block, so an unmeasurable run injects no number rather than a guessed one.
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
    return latest_usage.get("input_tokens", 0) + latest_usage.get("cache_read_input_tokens", 0) + latest_usage.get("cache_creation_input_tokens", 0)


def context_usage_line(transcript_path):
    tokens = measure_context_tokens(transcript_path) if transcript_path else None
    if tokens is None:
        return None
    return f"Your context usage, read from your own transcript rather than estimated: about {tokens:,} tokens are in your context window as of your last turn (roughly {tokens / 1_000_000 * 100:.0f}% of a 1M-token window, {tokens / 200_000 * 100:.0f}% of a 200K-token window). Use the size of your own window to turn that into a real utilization, and judge your context-limit rule against that number instead of a feeling."


def reread_targets(transcript_path):
    """The paths to re-read: the working model, then the memory stores Claude Code creates by convention. Task-specific artifacts are not enumerated (they are not created by default); the injected text asks the model to find its own."""
    targets = ["- ~/.claude/CLAUDE.md (your working model)"]
    user_memory = pathlib.Path.home() / ".claude" / "memory"
    if user_memory.is_dir():
        targets.append(f"- your user-level memories: {user_memory}")
    if transcript_path:
        project_memory = pathlib.Path(transcript_path).parent / "memory"
        if project_memory.is_dir():
            targets.append(f"- your project memories: {project_memory} (start with MEMORY.md, then the files it indexes)")
    targets.append("- any durable artifacts you have made for this task (plan, handoff, worklog, decision log, scratchpad notes); find them yourself, do not assume a path")
    return "\n".join(targets)


def claim_interval(clock):
    """True if this call may inject now. Reset the interval under an flock so that concurrent hooks from a parallel tool batch let exactly one through."""
    try:
        with open(clock, "r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if time.time() - clock.stat().st_mtime < INTERVAL_SECONDS:
                return False
            os.utime(clock, None)
            return True
    except OSError:
        return False


def build_injection(transcript_path):
    ctx = context_usage_line(transcript_path)
    return INJECTION.format(
        minutes=INTERVAL_SECONDS // 60,
        targets=reread_targets(transcript_path),
        context=f"\n\n{ctx}" if ctx else "",
    )


def main() -> int:
    payload = json.load(sys.stdin)
    if payload.get("agent_id"):
        return 0

    session_id = payload.get("session_id", "unknown")
    clock = pathlib.Path(tempfile.gettempdir()) / f"claude-self-audit-{session_id}"

    # First tool call of the session: fire an initial checkpoint at the start rather than a full interval
    # in, since the worst drift happens in the opening minutes. Backdate the clock so the first fire lands
    # SELF_AUDIT_START_DELAY_SECONDS after start (default 0 = this call), then the normal interval after.
    # Do not return, so a 0 start delay injects on this same call.
    if not clock.exists():
        clock.touch()
        first = time.time() - max(0, INTERVAL_SECONDS - START_DELAY_SECONDS)
        os.utime(clock, (first, first))
    # Hot path, taken on almost every tool call: a single stat, then bail until due.
    try:
        if time.time() - clock.stat().st_mtime < INTERVAL_SECONDS:
            return 0
    except OSError:
        return 0
    # Slow path (~once per interval): claim atomically so a parallel tool batch injects once, not per tool.
    if not claim_interval(clock):
        return 0

    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": build_injection(payload.get("transcript_path"))}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
