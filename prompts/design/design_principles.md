# Dieter Rams' 10 Principles of Good Design

Rams' principles were written for physical products, but they map powerfully to software. Use the notes and checklists below to guide decisions from strategy to pixels to code.

---

## 1) Good design is **innovative**
**Meaning:** Create new value, not novelty for its own sake.
**In software:** Innovate where it materially improves user outcomes; reuse conventions elsewhere.

**Practices**
- Identify top user jobs-to-be-done and target the moments of highest friction for innovation.
- Timebox experiments behind feature flags; measure impact with clear success metrics (e.g., task success rate, time-to-complete).
- Prefer composable architecture (APIs, plugins) so new ideas don't require rewrites.

**Watch-outs**
- Reinventing well-known patterns (e.g., auth flows) without benefit.
- Shipping "wow" demos that underperform in real tasks.

---

## 2) Good design **makes a product useful**
**Meaning:** Utility over vanity.
**In software:** Prioritize real user outcomes; avoid feature bloat.

**Practices**
- Tie each feature to a measurable user outcome; remove or deprecate unused features.
- Optimize for speed-to-value in the first session (clear "aha" path).
- Instrument core flows; fix the top blockers before adding new surface area.

**Watch-outs**
- "Checkbox" features added for parity or sales decks that few users need.

---

## 3) Good design is **aesthetic**
**Meaning:** Beauty supports use, clarity, and trust.
**In software:** Visual design should reduce cognitive load and foster confidence.

**Practices**
- Establish a design system (type scale, spacing, elevation, color roles) and enforce it in code.
- Use hierarchy (size, weight, contrast, spacing) to guide the eye to primary actions.
- Ensure motion and micro-interactions are purposeful, brief, and consistent.

**Watch-outs**
- Over-decoration (shadows, colors, animations) that obscures content or slows the UI.

---

## 4) Good design **makes a product understandable**
**Meaning:** The product explains itself.
**In software:** Clarity in copy, structure, and feedback minimizes the need for help docs.

**Practices**
- Use user-language, not internal jargon; test with plain-language reviews.
- Make affordances obvious (buttons look clickable; inline validation explains what and why).
- Progressive disclosure: advanced options exist, but don't overwhelm newcomers.

**Watch-outs**
- Clever labels, ambiguous icons, or hidden states that require guesswork.

---

## 5) Good design is **unobtrusive**
**Meaning:** It supports the task, not itself.
**In software:** The interface gets out of the way so users can focus on their work.

**Practices**
- Default to sensible presets; avoid configuration walls before value.
- Keep notifications, tooltips, and modals sparse and context-aware.
- Respect platform conventions so users' muscle memory works.

**Watch-outs**
- Interstitials, popovers, or upsells that interrupt critical flows.

---

## 6) Good design is **honest**
**Meaning:** No overpromises or tricks.
**In software:** Be transparent about capabilities, limitations, and data use.

**Practices**
- Set accurate expectations in UI copy; show loading and partial states truthfully.
- Make pricing, limits, and error conditions clear and upfront.
- Provide explainability for algorithmic results and meaningful controls.

**Watch-outs**
- Dark patterns (preselected opt-ins, disguised ads, misleading CTA copy).

---

## 7) Good design is **long-lasting**
**Meaning:** Avoid trend-chasing; aim for durability.
**In software:** Build stable mental models and architectures that age well.

**Practices**
- Favor timeless patterns (lists, detail views, wizards) over fads.
- Maintain API and URL stability; provide deprecation paths and migration guides.
- Invest in accessibility and performance—both compound over time.

**Watch-outs**
- Frequent redesigns that break habits and erode trust.

---

## 8) Good design is **thorough down to the last detail**
**Meaning:** Details are where quality shows.
**In software:** Edge cases, empty states, errors, and microcopy matter.

**Practices**
- Design every state: loading, empty, error, partial, success, offline.
- Align "system" and "brand" voices in microcopy; include examples in inputs.
- QA with real-world data variability (long names, different locales, slow networks).

**Watch-outs**
- Pixel-perfect happy paths with broken edge-case handling.

---

## 9) Good design is **environmentally friendly**
**Meaning:** Minimize resource waste and harm.
**In software:** Consider energy, compute, and ethical data practices.

**Practices**
- Optimize for efficiency: reduce payloads, cache intelligently, prefer incremental updates.
- Right-size ML/AI: choose models and inference strategies that balance accuracy and energy.
- Offer data export, retention controls, and privacy-by-default settings.

**Watch-outs**
- Heavy clients, unnecessary background tasks, and limitless data hoarding.

---

## 10) Good design is **as little design as possible**
**Meaning:** Less, but better.
**In software:** Prioritize the essential; remove the non-essential.

**Practices**
- Ruthless pruning: every screen, control, and setting must earn its keep.
- Provide powerful defaults; allow expert shortcuts without cluttering the UI.
- Express complexity through progressive depth, not initial breadth.

**Watch-outs**
- "Kitchen sink" dashboards and over-configurable settings panels.

---

## Team Checklist (use in design reviews)

- **Outcome-first:** Can we name the user outcome and how we'll measure it? (P2, P1 metric)
- **Clarity:** Would a first-time user know what to do next without help?
- **Focus:** What did we remove or defer to keep the core simple?
- **States covered:** Do we handle loading/empty/error/offline gracefully?
- **Respect:** Are we honest about limits, pricing, and data use?
- **Performance & access:** Is it fast on average hardware and accessible (WCAG 2.2 AA)?
- **Maintainability:** Does the design align with our system and avoid custom one-offs?
- **Sustainability:** Are we minimizing compute, bandwidth, and storage?
- **Consistency:** Does it follow our patterns and naming?
- **Delight with purpose:** Any motion or flair serves comprehension, not decoration.

> **Principle in one line:** Make it useful, clear, respectful, and as simple as it can be—and no simpler.

---
---

# Ben Shneiderman's Eight Golden Rules of Interface Design

These rules were written for interactive systems and map directly to modern software. Use the explanations, practices, and "watch-outs" during planning, design reviews, and QA.

---

## 1) **Strive for consistency**
**Meaning:** Similar things should look, behave, and be named the same way—across screens, roles, and platforms.
**In software:** Consistent patterns reduce cognitive load and support transfer of learning.

**Practices**
- Establish a design system (tokens, components, interaction patterns) and lint for divergence in code.
- Standardize copy conventions (e.g., "Sign in" vs "Log in"), date/time formats, and error styles.
- Reuse layouts (list → detail → edit) and placement of key actions.

**Watch-outs**
- One-off components, one-off copy, and "just this once" exceptions that multiply maintenance cost.

---

## 2) **Enable frequent users to use shortcuts**
**Meaning:** Provide accelerators for expert flow without harming beginners.
**In software:** Speed equals satisfaction; let proficiency shine.

**Practices**
- Keyboard shortcuts, command palettes, autocomplete, macros, saved filters.
- Progressive disclosure: start simple; reveal power as expertise grows.
- Remember user choices (last used format, preferred sort) per context.

**Watch-outs**
- Hidden, undocumented shortcuts; accelerators that change behavior rather than speed it up.

---

## 3) **Offer informative feedback**
**Meaning:** Every user action should get a clear, timely, and appropriate response.
**In software:** Feedback communicates state, progress, and outcomes.

**Practices**
- Micro-feedback for small actions (button press states, toasts).
- Graduated feedback for longer tasks (spinners → progress bars → percent → ETA).
- Inline validation that says **what went wrong** and **how to fix it**.

**Watch-outs**
- Silent failures, vague messages ("Something went wrong"), and infinite spinners.

---

## 4) **Design dialogs to yield closure**
**Meaning:** Group actions into clear beginnings, middles, and ends; signal completion.
**In software:** Users should feel "I'm done" and know the system state.

**Practices**
- Wizards with steps → confirmation → success summary and next best actions.
- Receipts (order ID, timestamp), activity logs, and emails for consequential actions.
- After task completion, return users to a meaningful place (context restoration).

**Watch-outs**
- Ambiguous completion (was it saved?), dead-end success screens with no onward path.

---

## 5) **Offer simple error handling**
**Meaning:** Prevent errors first; when they occur, help users recover gracefully.
**In software:** Errors should be rare, clear, and fixable.

**Practices**
- Constrain inputs (masking, pickers), sensible defaults, and destructive-action guards.
- Write actionable messages: cause → impact → remedy. Provide "try again" when possible.
- Log errors with correlation IDs; let users share them in a click.

**Watch-outs**
- Blaming users, jargon ("HTTP 500"), or forcing re-entry of all fields after an error.

---

## 6) **Permit easy reversal of actions (Undo)**
**Meaning:** Reversible actions encourage exploration and reduce anxiety.
**In software:** "Undo," version history, and soft-delete make the product forgiving.

**Practices**
- Universal "Undo/Redo" where feasible; snack-bar "Undo" for quick reversals.
- Drafts and autosave; versioning with diff + restore; recycle bin with retention policy.
- Dry-run previews for risky operations (e.g., "This will affect 12 records: preview").

**Watch-outs**
- Permanent, instant, non-reversible operations—especially on single mis-clicks.

---

## 7) **Support an internal locus of control**
**Meaning:** Users should feel in charge; the system should be predictable and responsive.
**In software:** No surprises; the UI follows the user's lead, not the other way around.

**Practices**
- Keep primary actions visible and deterministic; avoid unsolicited mode switches.
- Predictable navigation, keyboard focus order, and cancellation everywhere.
- Respect user intent: no hijacking scroll, auto-playing, or auto-submitting.

**Watch-outs**
- Dark patterns, nag modals, or timeouts that discard work without consent.

---

## 8) **Reduce short-term memory load**
**Meaning:** Minimize the need to remember information across views or moments.
**In software:** Favor recognition over recall.

**Practices**
- Keep context visible (sticky headers, selected filters, field labels not placeholders).
- Chunk complexity: step forms, progressive disclosure, sensible defaults.
- Provide examples, suggestions, and recent items; prefill from known data.

**Watch-outs**
- Forcing users to memorize IDs, switch back and forth between pages, or decipher cryptic icons.

---

## Applying the Rules in Practice

**Design Review Heuristics**
- **Consistency:** Does this diverge from our system? If yes, why is it worth the new pattern?
- **Shortcuts:** What's the expert path and its time-to-complete vs the novice path?
- **Feedback & Closure:** Can a first-time user tell what just happened and what's next?
- **Error Handling:** Show me the copy for the top 3 likely errors. Is recovery one step?
- **Undo:** What's the reversal model (undo, versioning, soft-delete)? What's the retention?
- **Control:** Could anything unexpected happen here? How do we cancel/escape?
- **Memory Load:** What can we keep on screen so users don't have to remember it?

**Instrumentation & Guardrails**
- Track task success rate, time-to-first-value, and undo usage (a proxy for safety).
- Alert on error clusters with user-visible correlation IDs.
- Include accessibility checks (focus order, ARIA, contrast) in CI; consistency linting in PRs.

**Definition of Done (DoD) Add-Ons**
- Designs cover all states: loading, empty, partial, error, success.
- Copy reviewed for clarity, actionability, and single-voice tone.
- Keyboard and screen-reader flows verified for the happy path and at least one error path.
- Undo/restore verified (or explicit rationale for irreversibility approved).

---

> **One-liner:** Make interactions predictable, forgiving, and efficient—so users stay in control, see what's happening, and never have to remember what the interface could remind them of.

---
---

# Nielsen's 10 Usability Heuristics

Classic, durable guidance for building interfaces that feel obvious, safe, and fast. Pair each heuristic with practices, anti-patterns, and checks you can use in design reviews and QA.

---

## 1) **Visibility of system status**
**Meaning:** Always show what's happening, quickly and clearly.
**In software:** Users should never wonder if the system received input or is still working.

**Practices**
- Immediate visual feedback on interaction (pressed states, skeletons).
- Progress indicators scaled to task length (spinner < progress bar < steps + %).
- Live system state (sync status, connection, autosave, role/permission hints).

**Watch-outs**
- Silent delays, infinite spinners, and ambiguous "Saved" states with no timestamp.

---

## 2) **Match between system and the real world**
**Meaning:** Speak the user's language and mental models.
**In software:** Domain terms, data formats, and workflows should reflect how users think.

**Practices**
- User-language in labels and messages; avoid internal jargon and codes.
- Real-world ordering (chronological, business priority) and familiar metaphors.
- Show domain units and examples (e.g., "mm/dd/yyyy • ex: 09/09/2025").

**Watch-outs**
- Engineering-centric labels, arbitrary field order, and cryptic abbreviations.

---

## 3) **User control and freedom**
**Meaning:** Users should feel in charge and be able to back out.
**In software:** Provide escape hatches, cancellability, and predictable actions.

**Practices**
- Clear primary/secondary actions; "Cancel" everywhere; ESC closes modals.
- Undo/redo, drafts, version history, soft-delete with retention.
- No mode traps; explicit entry/exit for bulk-edit, admin, or "danger" modes.

**Watch-outs**
- Forced flows, hijacked scroll, auto-advancing wizards, or irreversible one-clicks.

---

## 4) **Consistency and standards**
**Meaning:** Don't make users guess if two things mean the same thing.
**In software:** Reuse patterns, names, and placements across the product.

**Practices**
- Design system with tokens + components; lint for divergence in PRs.
- Standardize copy ("Sign in", not "Login" on one page and "Log in" on another).
- Align with platform conventions (keyboard shortcuts, OS dialogs).

**Watch-outs**
- One-off components, novel iconography, and "just this screen is different."

---

## 5) **Error prevention**
**Meaning:** The best error is the one that never occurs.
**In software:** Constrain inputs and flows to make the right thing easy.

**Practices**
- Input masks, pickers, validation as-you-type, sensible defaults.
- Confirmations for destructive actions; preview before bulk changes.
- Guardrails: required field hints, dependency checks, conflict detection.

**Watch-outs**
- Free-form inputs when structured ones exist; confirmations that users learn to ignore.

---

## 6) **Recognition rather than recall**
**Meaning:** Put needed info in view; don't make users remember it.
**In software:** Prefer visible choices and cues over memory.

**Practices**
- Persistent labels (not placeholder-only), helper text, examples.
- Recent items, suggestions, autofill, and meaningful empty states.
- Keep context in view (sticky filters/headers; selected items count).

**Watch-outs**
- Multi-step tasks that require memorizing IDs or flipping between tabs.

---

## 7) **Flexibility and efficiency of use**
**Meaning:** Novices succeed; experts fly.
**In software:** Layer accelerators that don't penalize beginners.

**Practices**
- Keyboard shortcuts, command palette, bulk actions, templates, saved views.
- Personalization that remembers last choices; API/webhooks for power users.
- Progressive disclosure: simple first, depth available.

**Watch-outs**
- Hidden or undocumented accelerators; power features that break the core model.

---

## 8) **Aesthetic and minimalist design**
**Meaning:** Less, but clearer—show only what helps the task.
**In software:** Reduce visual noise and cognitive load.

**Practices**
- Information hierarchy via type scale, spacing, contrast; single clear primary action.
- Remove low-value fields; collapse advanced options.
- Purposeful motion; consistent iconography; restrained color roles.

**Watch-outs**
- Dashboard "kitchen sinks," decorative chrome, and copy that says everything and nothing.

---

## 9) **Help users recognize, diagnose, and recover from errors**
**Meaning:** When errors happen, explain plainly and show the fix.
**In software:** Actionable, localized, human messages.

**Practices**
- Inline, field-level errors: cause → impact → remedy; link to docs if needed.
- Offer recovery actions (Retry, Restore draft, Contact support with log ID).
- Correlation IDs in logs and UI; preserve user input after errors.

**Watch-outs**
- Codes without meaning (e.g., "ERR_42"), blaming language, or wiping forms on submit.

---

## 10) **Help and documentation**
**Meaning:** Self-explanatory UIs still benefit from well-placed help.
**In software:** Make help discoverable, concise, and contextual.

**Practices**
- Contextual help icons, short how-tos, tooltips with examples.
- Searchable docs; checklists and troubleshooting trees for complex tasks.
- Onboarding tours that can be skipped, resumed, and referenced later.

**Watch-outs**
- External-only PDFs, long walls of text, or help that's out-of-date with the UI.

---

## Design Review Checklist (use verbatim in crits)

- **Status:** Is feedback immediate and scaled to task length? Where can waits hide?
- **Language fit:** Any internal jargon or unexplained codes?
- **Control:** Can I cancel, undo, and safely explore? What's irreversible and why?
- **Consistency:** Where does this diverge from our system—and is it justified?
- **Prevention:** What's the top likely user error, and how is it prevented?
- **Recognition:** What info do we force users to remember? Can we surface it?
- **Efficiency:** What's the expert path? Time-to-complete vs novice path?
- **Minimalism:** If we removed 20% of UI, would the task still succeed?
- **Error recovery:** Show the exact error copy and recovery path.
- **Help:** Is there just-in-time help where confusion is most likely?

## Instrumentation & Quality Gates

- **Metrics:** Task success rate, time-to-first-value, error rate by step, undo usage, rage-clicks.
- **Accessibility:** Contrast, focus order, labels/ARIA; target WCAG 2.2 AA in CI.
- **States:** Define and test loading/empty/error/offline/partial/success for each screen.
- **Docs:** Help content versioned with the UI; links validated in CI.

> **One-liner:** Keep users informed, in control, and unburdened—prevent errors, speak their language, and offer speed without sacrificing clarity.

---
---

# WCAG 2.0 — What It Is, What To Aim For, and How To Build It In

**WCAG 2.0** (Web Content Accessibility Guidelines, 2008) defines *testable* success criteria for accessible digital products.
It's organized under four principles—**P**erceivable, **O**perable, **U**nderstandable, **R**obust (a.k.a. **POUR**)—and three conformance levels: **A** (minimum), **AA** (industry norm), **AAA** (best-effort/optional).
For a formal "AA" claim, **every applicable AA (and A) success criterion must pass** on each page/screen.

> **Team target:** Ship **WCAG 2.0 AA** by default. (AAA items can be added where feasible.)

---

## The 4 Principles (POUR) with Key WCAG 2.0 AA (and A) items

### 1) **Perceivable** — information must be presented in ways users can perceive
- **1.1.1 Text Alternatives (A):** Provide meaningful `alt` for non-text content (images, icons).
  *Acceptance:* "Decorative images have empty `alt=""`; informative images describe function or content succinctly."
- **1.2 Time-based Media (A/AA):**
  - A: transcripts/captions for prerecorded audio-only/video-only basics.
  - **1.2.4 Captions (Live) (AA)**, **1.2.5 Audio Description (Prerecorded) (AA)** where applicable.
- **1.3 Adaptable (A):** Preserve structure in code: **1.3.1 Info & Relationships** (headings, lists, tables), **1.3.2 Meaningful Sequence**, **1.3.3 Sensory Characteristics** (don't rely on color/position alone).
- **1.4 Distinguishable:**
  - **1.4.1 Use of Color (A):** Never use color as the sole cue.
  - **1.4.3 Contrast (Minimum) (AA):** Text contrast ≥ **4.5:1** (normal) or **3:1** (large text: ≥18pt regular or ≥14pt bold).
  - **1.4.4 Resize Text (AA):** Content readable/functional at 200% zoom without assistive tech.
  - **1.4.5 Images of Text (AA):** Avoid text baked into images (except logos).

### 2) **Operable** — interface components and navigation must be operable
- **2.1 Keyboard Accessible (A):** All functionality by keyboard; **no traps** (2.1.1, 2.1.2).
  *Acceptance:* "Every interactive element reachable by Tab/Shift+Tab; ESC closes modals; focus never gets stuck."
- **2.2 Enough Time (A):** Provide ways to extend/disable time limits (2.2.1) and **Pause/Stop/Hide** moving content (2.2.2).
- **2.3 Seizures (A):** No content flashes more than *3 times per second* above thresholds (2.3.1).
- **2.4 Navigable:**
  - **2.4.1 Bypass Blocks (A):** "Skip to main content" or equivalent landmark structure.
  - **2.4.2 Page Titled (A).**
  - **2.4.3 Focus Order (A).**
  - **2.4.4 Link Purpose—In Context (A).**
  - **2.4.5 Multiple Ways (AA):** Provide more than one way to locate pages (search, sitemap, navigation).
  - **2.4.6 Headings and Labels (AA):** Describe topic/purpose.
  - **2.4.7 Focus Visible (AA):** A clear visible focus indicator is present.

### 3) **Understandable** — information and operation must be understandable
- **3.1 Readable:** **3.1.1 Language of Page (A)**; **3.1.2 Language of Parts (AA)** if mixed languages.
- **3.2 Predictable:**
  - **3.2.1 On Focus (A):** Focus doesn't unexpectedly change context.
  - **3.2.2 On Input (A):** Submitting or major context changes aren't triggered just by data entry.
  - **3.2.3 Consistent Navigation (AA)**; **3.2.4 Consistent Identification (AA)** for repeated components.
- **3.3 Input Assistance:**
  - **3.3.1 Error Identification (A)** and **3.3.2 Labels or Instructions (A)**.
  - **3.3.3 Error Suggestion (AA)**; **3.3.4 Error Prevention—Legal/Financial/Data (AA)** (confirm/review or undo).

### 4) **Robust** — content must work with AT (assistive tech) and user agents
- **4.1.1 Parsing (A):** Markup avoids major validity/structure errors.
- **4.1.2 Name, Role, Value (A):** UI components expose accessible **name**, **role**, **state/value** (use native HTML or correct ARIA).

---

## What "AA" Looks Like in Practice (engineering-friendly examples)

- **Semantics first:** Use `<button>`, `<a>`, `<label>`, `<fieldset>`, `<th scope="col">`, etc.; only add ARIA when native semantics don't exist.
- **Programmatic labels:** Inputs have visible labels connected by `for/id` or `aria-labelledby`; icons-only buttons have `aria-label`.
- **Focus management:** On opening a dialog, move focus to it; trap focus *inside* while open; return focus to the trigger on close.
- **Visible focus ring:** Never remove it; if customizing, ensure strong contrast and a hit area ≥ 44×44 CSS px where possible.
- **Error UX:** Inline, specific messages near the field; link errors to fields via `aria-describedby`; preserve user input on failure.
- **Color & contrast:** Validate text contrast ratios (normal 4.5:1, large 3:1). Don't rely on color alone to convey required/selected/invalid states.
- **Media:** Provide captions; supply audio descriptions for key visual information in prerecorded video (AA).
- **Zoom & reflow:** No horizontal scroll at 200% zoom; components don't overlap or become unreachable.
- **Keyboard every time:** All actions (menus, carousels, drag-drop alternatives) are operable by keyboard.

---

## "Definition of Done" add-ons (use in tickets/PRs)

- **States covered:** loading, empty, error, success, and validation states are designed and coded.
- **Keyboard path:** Every interactive element is reachable/operable by keyboard; Tab order matches visual order.
- **Focus:** Visible, non-obstructed focus indicator; focus managed on open/close of overlays.
- **Labels & names:** All controls expose an accessible name; icons-only controls labeled.
- **Errors:** Clear, human messages; programmatically associated; recovery suggested.
- **Contrast:** Text contrast checked (≥4.5:1 normal, ≥3:1 large).
- **Media:** Captions for video; transcripts where applicable.
- **Language:** `lang` set on root; parts tagged when language changes.
- **Consistency:** Headings/landmarks provide a logical outline (skip links or landmarks present).
- **Parsing/roles:** No critical HTML/ARIA violations; components expose name/role/value.

---

## How We Test (lightweight but effective)

1. **Automated linters** (CI): axe-core/HTML validation to catch low-hanging fruit (contrast, labels, roles).
2. **Keyboard sweep** (manual): Tab/Shift+Tab through a page; activate with Enter/Space; ESC closes overlays.
3. **Screen reader spot-checks:**
   - macOS: VoiceOver; Windows: NVDA.
   - Verify: page title, regions/landmarks, heading structure, control names, error announcements.
4. **Zoom pass:** 200% browser zoom; no loss of content/functionality.
5. **Color reliance:** Convert screen to grayscale; ensure meaning is preserved without color.
6. **Media check:** Captions present; moving content can be paused/stopped/hidden.

---

## Notes & Scope

- **WCAG 2.0 vs later versions:** 2.0 is widely referenced; many organizations now target WCAG **2.1 AA** or **2.2 AA** for stronger mobile and control-contrast coverage. If your contracts/laws say "2.0," ship 2.0 AA minimum and adopt relevant 2.1/2.2 items where easy wins exist.
- **Conformance units:** Claim at the *page/screen* level; all applicable content—including dynamic states and embedded widgets—must comply.
- **Legal note:** WCAG is technical guidance, not legal advice; regulatory obligations vary by region/industry.

---

## Quick AA Checklist (paste into design reviews)

- [ ] Text contrast ≥ 4.5:1 (normal) / 3:1 (large).
- [ ] All functionality by keyboard; no traps; visible focus ring.
- [ ] Correct semantics and landmarks; logical heading structure.
- [ ] Labels for every input; icons-only controls have accessible names.
- [ ] Clear, inline error messages linked to fields; input preserved.
- [ ] No color-only cues; provide a second cue (text/icon/pattern).
- [ ] "Skip to main" or landmark navigation provided.
- [ ] Meaningful page titles, link text, and headings.
- [ ] Video: captions; prerecorded visuals described where needed.
- [ ] Works at 200% zoom without horizontal scrolling.

> **One-liner for the team:** Build so everyone can *perceive* it, *operate* it, *understand* it, and so it stays *robust* across technologies—then prove it with testable criteria.
