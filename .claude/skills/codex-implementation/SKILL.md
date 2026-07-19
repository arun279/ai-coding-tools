---
name: codex-implementation
description: Ask Codex CLI (gpt-5.6-sol) to implement scoped code changes in the current repository, then have Claude inspect the resulting diff and verification. This is how gpt-5.6-sol is invoked for implementation work. Use when the user asks Claude to delegate implementation to Codex or gpt-5.6-sol, when the model-selection rubric routes the work to gpt-5.6-sol, or when a bounded task would benefit from another coding agent producing a patch.
---

# Codex Implementation

Use Codex as a separate implementation agent for bounded code changes. Claude remains responsible for:
- Scoping the task.
- Reviewing the produced diff.
- Running or checking verification (tests, linting, type checking, etc.).
- Explaining the final result and any tradeoffs.

Use this workflow when:
- The user explicitly asks for Codex or implementation delegation.
- A bounded task would benfit from parallel implementation agent producing a patch

Do not use Codex commit, push, deploy, or edit global config unless the user explicitly asked for that.

## Execution context

This codex-implementation skill is a runbook for whichever agent executes it, and the executor determines the mechanics:

- **Main/orchestrator context:** do not run `codex` here. Spawn a thin wrapper agent (a cheap model such as Sonnet at low effort) whose prompt carries this skill's workflow and the task specifics, and have the wrapper run `codex`. Inside a Workflow, label the wrapper `gpt-5.6-sol:<task>` so the true worker is visible in the progress UI.
- **Wrapper or subagent context:** run `codex` directly via Bash exactly as described below. Do not spawn further wrappers. This rule never nests: one wrapper, then codex.

This keeps long codex runs observable (they appear as agents/workflow lanes, not invisible background shells) and prevents recursive wrapping.

## Workflow

1. Pin the current state with `git status --short` and note any user changes already present.
2. Define the implementation scope: files or behavior to change, files to avoid, constraints, and verification commands.
3. Create a temporary artifact directory for Codex's report.
4. Run `codex exec` with repo write access.
5. After Codex exits, inspect `git status` and `git diff`.
6. Run the cheapest reliable verification yourself when practical.
7. Report what Codex changed, what Claude verified, and any remaining risks.

Use this command shape:

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-implementation.XXXXXX")"
REPORT="$ARTIFACT_DIR/report.md"
PROMPT="$ARTIFACT_DIR/prompt.md"

# Write a self-contained prompt to $PROMPT, then run:
codex exec \
  -C "$PWD" \
  --add-dir "$ARTIFACT_DIR" \
  -s workspace-write \
  -o "$REPORT" \
  "$(cat "$PROMPT")" </dev/null
```

Always redirect stdin from `/dev/null`. `codex exec` appends piped stdin to the prompt as a `<stdin>` block, so in any non-interactive context (this harness, a background job, an overnight workflow) stdin is a pipe that never sends EOF and Codex blocks forever waiting on it. Codex runs routinely exceed the harness's ~10-minute Bash timeout, but **never end your turn while codex is still running** — how you wait depends on where you are:

- **A wrapper agent inside a Workflow lane:** run codex in the FOREGROUND with a long Bash timeout. Do NOT `run_in_background`, and do NOT end your turn to "wait for a notification" — inside a workflow, ending your turn returns your last message as the lane's result and abandons the codex process, losing its branch/report. If the foreground call times out, run another foreground continuation round against the same working directory (its progress persists on disk); repeat a bounded number of times, then report `VERDICT=BLOCKED` if still unfinished.
- **A standalone subagent wrapper:** if you `run_in_background`, you MUST poll for the report file in a loop within the SAME turn and finish only once it exists (or codex has exited). Launching a background codex and then ending your turn abandons the run — nobody reads the report.

(macOS has no `timeout` binary, so do not wrap the call in one.)

Judging whether a long run is alive: at 0% CPU codex is normally waiting on the model API, not wedged, so read a growing `git diff --stat` (or a live build/test child process), not CPU. Do not rely on ending your turn or `TaskStop` to reap what codex spawned: track the PIDs and kill them explicitly, and note that a still-running test process can keep relaunching browsers (a Playwright run on retry), so kill the runner, not just the browser.

`-o` writes only codex's FINAL message; if codex is killed or exhausts its budget before finishing, `-o` is empty. For long or risky runs, have codex write durable artifacts as it works (the report file, intermediate output) so a terminated run still leaves usable evidence — don't depend on `-o` alone.

Use `-s workspace-write` by default. Use `-s danger-full-access` only when the implementation truly needs access outside the repo, app launch automation, simulator work, package manager global state, or other machine-level operations.

Note: `-s workspace-write` blocks binding to `localhost`. If codex's verification runs a dev server or test runner that binds a port (Vitest under a Vite/WXT server, Playwright's webServer), it fails with `listen EPERM`. Grant `-s danger-full-access` for that run, or run that verification step yourself outside codex.

Model tier: `codex exec` accepts `-m <model>` and reasoning-effort config (`-c model_reasoning_effort="low|medium|high"`); `codex debug models` lists the catalog. Match the tier to the task — reserve the frontier model (gpt-5.6-sol) for hard implementation; a cheaper balanced model (e.g. gpt-5.6-terra) at low reasoning is enough for bulk/mechanical work.

## Prompt Requirements

Tell Codex:

- The exact implementation goal and acceptance criteria.
- The repo path and current branch context if relevant.
- Which existing patterns, files, or tests to inspect first.
- Files or behavior that must not be changed.
- That it must preserve unrelated user changes.
- That it must not commit, push, deploy, or edit global config.
- Which verification commands to run, or to explain why they were skipped. Have it run each on its own and capture the status immediately (`<cmd>; echo "EXIT=$?"`), then report that code verbatim beside the pass/fail summary lines: a pipeline like `<cmd> | tee log` reports only the last stage's status (the `tee`), and a `;` sequence reports only the trailing command, so either can mask a real failure as a false "passed".
- To write a concise final report with files changed, verification, and unresolved questions.

Keep the task bounded. If the requested work bundles several substantial changes, split it into separate Codex runs or ask the user to choose the first scope.

## Example Prompt

```text
You are implementing a scoped change for Claude.

Repository: /absolute/path/to/repo
Artifact directory: /tmp/codex-implementation.XXXXXX

Goal:
- Add keyboard navigation to the command palette.

Acceptance criteria:
- ArrowUp and ArrowDown move the highlighted item.
- Enter selects the highlighted item.
- Escape closes the palette.
- Existing mouse behavior keeps working.

Constraints:
- Preserve unrelated user changes.
- Do not commit, push, deploy, or edit global config.
- Follow existing component and test patterns.

Verification:
- Run the focused component tests if available.
- Otherwise run the nearest relevant typecheck or test command and explain the choice.

Report:
- Files changed
- Behavioral summary
- Verification run and result
- Anything blocked or uncertain
```

## Review After Codex

Always inspect Codex's diff before telling the user the work is done. Revert only Codex-created mistakes when you are sure they are not user changes. If Codex leaves the repo in a worse state or changes unrelated files, stop and report the issue with the diff summary.

If `codex` is not installed or the command fails, report the error and offer to implement the change directly instead.