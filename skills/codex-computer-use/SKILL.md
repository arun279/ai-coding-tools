---
name: codex-computer-use
description: Ask Codex CLI (gpt-5.6-sol) to run local app verification that needs computer use, browser automation, simulators, screenshots, app launching, or independent runtime inspection. This is how gpt-5.6-sol is invoked for computer-use work. Use when the user asks Claude to test a flow, verify UI behavior, inspect a running app, capture screenshots, or report confirmation and feedback about implemented behavior that benefits from computer use functionality.
---

# Codex Computer Use

Use Codex as a separate local verification agent when the task needs real UI interaction, screenshots, simulator/browser/device state, or an independent runtime check outside Claude's current context.

Do not use this for ordinary code reading, typechecking, linting, or tests Claude can run directly. Launching apps, simulators, or browsers to verify the requested work is fine without asking; ask first only if the run could disrupt the user's environment beyond that (closing their apps, changing system settings, acting on real accounts or data).

## Execution context

This codex-computer-use skill is a runbook for whichever agent executes it, and the executor determines the mechanics:

- **Main/orchestrator context:** do not run `codex` here. Spawn a thin wrapper agent (a cheap model such as Sonnet at low effort) whose prompt carries this skill's workflow and the task specifics, and have the wrapper run `codex`. Inside a Workflow, label the wrapper `gpt-5.6-sol:<task>` so the true worker is visible in the progress UI.
- **Wrapper or subagent context:** run `codex` directly via Bash exactly as described below. Do not spawn further wrappers. This rule never nests: one wrapper, then codex.

This keeps long codex runs observable (they appear as agents/workflow lanes, not invisible background shells) and prevents recursive wrapping.

## Workflow

1. Create a temporary artifact directory.
2. Give Codex a self-contained prompt with the repo path, exact flow, constraints, artifact directory, and report format.
3. Run `codex exec` non-interactively.
4. Read Codex's report, inspect or reference screenshot paths, and summarize the result for the user.

Use this command shape:

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-computer-use.XXXXXX")"
REPORT="$ARTIFACT_DIR/report.md"
PROMPT="$ARTIFACT_DIR/prompt.md"

# Write a self-contained prompt to $PROMPT, then run:
codex exec \
  -C "$PWD" \
  --add-dir "$ARTIFACT_DIR" \
  -s danger-full-access \
  -o "$REPORT" \
  "$(cat "$PROMPT")" </dev/null
```

Always redirect stdin from `/dev/null`. `codex exec` appends piped stdin to the prompt as a `<stdin>` block, so in any non-interactive context (this harness, a background job, an overnight workflow) stdin is a pipe that never sends EOF and Codex blocks forever waiting on it. Codex runs also routinely exceed the harness's ~10-minute Bash timeout: launch this in the background and poll `$REPORT` instead of waiting in the foreground. (macOS has no `timeout` binary, so do not wrap the call in one.)

Use `-s danger-full-access` for GUI automation, iOS simulators, desktop app launching, screenshots, or access outside the repo. For non-GUI checks that only need the repo and artifact directory, prefer `-s workspace-write`. Add `--skip-git-repo-check` when the working directory is not a git repository.

## macOS permissions and unattended runs

Computer-use fails *silently* when a required macOS permission is missing, because an unattended run cannot answer the consent dialog that would grant it. macOS attributes these TCC permissions to the **terminal app that launched codex** (Ghostty, iTerm, Terminal, ...), not to `codex` itself — so grant them to that app once, in System Settings > Privacy & Security, before relying on an overnight run. Do not confuse this with OpenAI's standalone ChatGPT / "Codex Computer Use" desktop app, which appears as its own entry in the permission lists: it is a different product, and granting *it* does nothing for the `codex exec` CLI this skill drives. If unsure which terminal is the responsible app, trace the process ancestry up to the `.app` (e.g. `ps -o ppid=,comm= -p $$` walked to the top). The three permissions are independent; holding one does not imply the others:

- **Screen Recording** — required for `screencapture` and any pixel/vision check. It also needs an awake, unlocked display with an active framebuffer: on a sleeping or locked screen `screencapture` fails with `could not create image from display` and writes no file. For unattended runs keep the display awake, e.g. wrap the call with `caffeinate -d` (`caffeinate -d codex exec ... </dev/null`).
- **Accessibility** — required to click, type, drag, or read UI elements (System Events keystroke/click, `cliclick`, AX queries). Without it these fail with `not allowed assistive access` (`-1719` / `-25211`). Screen Recording being granted does **not** imply this; a terminal can screenshot yet be unable to drive any UI.
- **Automation (Apple Events)** — scripting another app (`tell application "X"`) prompts for per-app consent the first time. Pre-consent by running that automation once interactively; otherwise the first hit on a new target app blocks or is denied unattended.

Also for unattended runs: keep the machine logged in and unlocked (the lock screen and login window block both capture and UI control), and pre-install any heavier tooling the task needs (Xcode + `xcrun simctl` for the iOS Simulator, Playwright/WebDriver for browser automation) so the run does not stall on a first-use install or download.

Before trusting an overnight computer-use workflow, verify the grants are actually in place rather than assuming: `osascript -e 'tell application "System Events" to return UI elements enabled'` should print `true` (Accessibility), and a probe `screencapture -x /tmp/probe.png` should yield a non-empty file (Screen Recording + live display). If either check fails, fix the grant before scheduling the run.

## Prompt Requirements

Tell Codex:
- The exact behavior to verify.
- The platform and app type, such as iOS, web, Electron, CLI, or desktop.
- Known launch commands, test credentials, seed data, deep links, or fixtures.
- Whether source edits are allowed. Default to no edits.
- Where screenshots, logs, and the final report should be saved.
- To return pass, fail, or blocked, plus steps performed, observed behavior, screenshot paths, and actionable feedback.
- If a GUI action is refused, to report the exact error verbatim (e.g. `not allowed assistive access`, `could not create image from display`, Apple Events consent), so the missing macOS permission is identifiable rather than reported as a generic failure.

Keep the prompt specific enough that Codex does not need the surrounding Claude conversation.