---
name: codex-review
description: Ask Codex CLI (gpt-5.6-sol) for an independent code review of uncommitted changes or a branch diff, a commit, or a specific implementation. This is how gpt-5.6-sol is invoked for all review work. Use when the user asks Claude to have Codex or gpt-5.6-sol review work, when the model-selection ruberic calls for a gpt-5.6-sol review perspective, or when Codex should audit a diff, find bugs or regressions, or compare Claude's implementation against requirements. For a review by Claude itself, use the normal review process instead.
---

# Codex Review

Use Codex as an independent reviewer when the user wants a second-pass review or when a change is broad enough that another agent's perspective is useful.

Prefer Claude's normal review process for small local checks. Do not delegate review just to avoid reading the code yourself. Treat Codex's output as not authority.

## Execution context

This codex-review skill is a runbook for whichever agent executes it, and the executor determines the mechanics:

- **Main/orchestrator context:** do not run `codex` here. Spawn a thin wrapper agent (a cheap model such as Sonnet at low effort) whose prompt carries this skill's workflow and the task specifics, and have the wrapper run `codex`. Inside a Workflow, label the wrapper `gpt-5.6-sol:<task>` so the true worker is visible in the progress UI.
- **Wrapper or subagent context:** run `codex` directly via Bash exactly as described below. Do not spawn further wrappers. This rule never nests: one wrapper, then codex.

This keeps long codex runs observable (they appear as agents/workflow lanes, not invisible background shells) and prevents recursive wrapping.

## Workflow

1. Identify the review target: uncommitted changes, base branch, commit SHA, PR checkout, or specific files.
2. Create a temporary artifact directory for the Codex report.
3. Run `codex review`, choosing exactly one target (see below).
4. Read Codex's report and verify important claims against the code before presenting them.

A review target and a custom prompt are mutually exclusive in `codex review`: pick exactly one of `--uncommitted`, `--base`, `--commit`, or a `PROMPT`. This is intended Codex behavior, not a bug to work around. The final review is written to stdout; progress and the diff go to stderr, so redirect stdout to capture the report.

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")"
REPORT="$ARTIFACT_DIR/report.md"
PROMPT="$ARTIFACT_DIR/prompt.md"

# Uncommitted working tree WITH focused instructions. Prompt-only review defaults
# to the uncommitted diff, so this is how you pass a custom review stance. Write
# the instructions to $PROMPT first, then:
codex -C "$PWD" review - < "$PROMPT" > "$REPORT"

# Base branch or single commit. The native target flags do NOT accept a custom
# prompt in this CLI, so these run Codex's built-in reviewer with no extra
# instructions. Fold focus into the target instead (e.g. review one commit).
codex -C "$PWD" review --base main > "$REPORT"
codex -C "$PWD" review --commit <sha> > "$REPORT"
```

A large diff can still exceed the Bash timeout: run codex review in the FOREGROUND. Inside a Workflow lane, never `run_in_background` and never end your turn to wait — that returns your last message as the lane's result and abandons the run. Crucially, **distinguish "codex found nothing" from "codex failed/timed out"** — an empty or truncated report is NOT a clean review; retry once with a narrower target (a single commit) and, if it still produces no analysis, report "review unavailable" rather than "no findings." `codex review` accepts `-m <model>` / `-c model_reasoning_effort=...`; review is judgment-heavy, so keep the frontier tier (gpt-5.6-sol) unless the diff is trivial.

## Review Prompt

Ask Codex to use a code-review stance:

```text
Review these changes for bugs, regressions, missing tests, security issues, and requirement mismatches.

Prioritze findings over summary. For each finding include:
- severity
- file and line reference
- concrete failure mode
- suggested fix direction

Do not edit files. If there are no substantive findings, say so and name any residual test gaps.
```

Add task-specific context when useful: requirements, risky areas, expected behavior, relevant tests, or files Claude is unsure about. This custom prompt only applies to the uncommitted (prompt-only) path above; `--base` and `--commit` reviews cannot take a prompt, so narrow the target itself when you need focus.

## Reporting back

Before relaying a Codex finding, inspect the cited code or diff enough to decide whether the finding is real. In the user-facing response, separate confirmed issues from Codex suggestions you did not verify.

If Codex finds nothing, say that clearly and mention what review target it inspected.

If `codex` is not installed or the command fails, reprot the error and offer to review the changes directly instead.