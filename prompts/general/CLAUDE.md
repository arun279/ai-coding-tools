# Personal Preferences

## Mental models and general guidelines

- Employ this 5-step process as a general philosopy of working:
  1. Question your constraints and assumptions. Make the requirements less dumb.
  2. Delete any part or process you can. If you're not adding back at least some percentage of things you're deleting, you're not deleting enough.
  3. Simplify and optimize (once it survives 1. and 2., a commong mistake is to prematurely optimize something that shuold not exist).
  4. Accelerate cycle time. The faster you can iterate, the faster you can make progress towards goals.
  5. Automate as much as you can. A common mistake people make is to automate something too early or automate something that should not exist. That's why this is the last step.
- Avoid AI slop patterns, like (but not limited to):
  - Extra comments that a competent senior engineer wouldn't add or is inconsistent with the rest of the codebase.
  - Extra defensive checks, try/catch blocks, or other simlar patterns that are abnormal for that area of the codebase (especially if called by trusted/validated codepaths).
  - Casting to get around type issues, variables that are only used a single time right after declaration or returned immediately (prefer inlining), inconsistent style/formatting, or other similar anti-patterns.
- Always follow best practices, modern standards, avoid any known anti-patterns. Use good code organization, code hygiene, and use the right abstractions/patterns. Do not overbloat the codebase. Always remember that the instinct to delete code is slighyly more important than the instinct to add code. Any code you produce should hold up to rigorous code review. Use functional, declarative, async, reactive programming patterns correctly and effectively wherever applicable.
- Generally try to strive for concise, simply solutions. If a problem can be solved in a simpler way, propose it.
- Follow DRY, SOLID, KISS, YAGNI, Five Whys and other similar practices, techniques, principles, etc., wherever applicable. You don't have to follow all of them all the time, but use them as useful mental models and patterns to lean on while dealing with problems and use them wherever applicable.
- Never give timeline estimates, team size estimates, etc. Don't make any decisions based on your perceptions of the technical expertise of the team. You are the team. You only pick what makes the most sense for the problem.
- Keep a work log of every notable you do in `~/.claude/projects/{your-project-folder}` so you can keep track of everything being done, stays durable across compactions, and another session can pick up where you left off.

## General workflow principles

- Prefer using ultracode dynamic workflows wherever appropriate.
- Use exa mcp to look for things online.
- While using dynamic workflows, once you implement something, run a loop where you review it, and address the issues brought up by the review, until it converges or you run it for a reasonable number of iterations (around 3).
- Make sure you keep a log of issues brought up so you won't run into a loop of fixing, unfixing, refixing, the same things. Once an issue is flagged up and considered as valid, unless new information is brough to light (or underlying implementation changes), the issue should be considered closed.
- If you use codex for implementation, use claude for review, and vice versa.
- Unless an issue is blocked by external dependencies or future work or something else, you should strive to address valid issues regardless the level of severity.
- When dealing with anything related to design, fetch and use this document along with the frontend-design skill: `https://github.com/arun279/ai-coding-tools/blob/master/prompts/design/design_principles.md`

## Picking the right models for the workflows and subagents

Rankings, higher = better. Cost reflects what I actually pay, not list price. Intelligence is how hard a problem you can hand the model unsupervised. Taste covers UI/UX, code quality, API design, and copy.

| model       | cost | intelligence | taste |
|-------------|------|--------------|-------|
| gpt-5.6-sol | 8    | 8            | 5     |
| sonnet-5    | 5    | 5            | 7     |
| opus-4.8    | 4    | 7            | 8     |
| fable-5     | 2    | 9            | 9     |

How to apply:
- These are defaults, not limits. You have standing permission to override them: if a cheaper model's output doesn't meet the bar, rerun or redo the work with a smarter model without asking. Judge the output, not the price tag. Escalating costs less than shipping mediocre work.
- Don't let cost prevent you from using the right model for the job. Instead, take advantage of cheaper options to get more information and try things before moving the work to a more expensive option.
- Bulk/mechanical work (clear-spec implementation, data anlaysis, migrations): gpt-5.6-sol
- Anything user-facing (UI, copy, API design) needs taste >= 7.
- Reviews of plans/implementations: fable-5 or opus-4.8, optionally gpt-5.6-sol as an extra independent perspective.
- Never use Haiku.
- Mechanics: gpt-5.6-sol is only reachable through Codex CLI - `codex exec` / `codex review` (my config might default to gpt-5.6-sol so you might need to `-m gpt-5.6-sol`). Use the codex-review, codex-implementation, and codex-computer-use skills; for work they don't cover (investigation, data analysis), run `codex exec -s read-only` directly with a self-contained prompt (with the right model of course).
- Claude models (sonnet-5, opus-4.8, fable-5) run via the Agent/Workflow model parameter.

Using gpt-5.6-sol inside workflows and subagents (the model parameter only takes Claude models, so use a wrapper):
- Spawn a thin Claude wrapper agent with `model: 'sonnet', effort: 'low'` whose prompt instructs it to write a self-contained codex prompt, run `codex exec` via Bash, and return the report (use `schema` on the wrapper to get structured output back).
- Always label the agents with a `gpt-5.6-sol:` prefix, eg. `{label: 'gpt-5.6-sol:review-auth'}` - the workflow UI shows the wrapper's Claude model, so the label is the only indication the real worker is gpt-5.6-sol.
- Codex runs can exceed Bash's 10-minute timeout: pass an explicit timeout, or run in the background and poll for the report file.
- Parallel gpt-5.6-sol implementation agents must use `isolation: 'worktree'` so codex edits don't collide in the shared checkout.
- Workflow token budgets only count Claude tokens; codex work has generous limits and invisible to `budget.spent()`.