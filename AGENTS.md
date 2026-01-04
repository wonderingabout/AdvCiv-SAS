# AGENTS

These rules apply to me GPT-Codex Guidelines or other agents now and later (future me too). Append the following instructions as we agree on them. You can expand this freely as you see fit.

## Comment Editing Rules (for me, now and later)

- **ALWAYS preserve the `<!-- custom` prefix** - never remove it when summarizing comments.
- Simplify verbose comments without changing meaning or technical details.
- **Focus on rewording/rephrasing** - the goal is to remove prose and conversational filler while preserving all technical information. Don't over-summarize to the point of losing important technical context.
- Do not requalify subjective wording (e.g., keep "nicer display" instead of rephrasing as "tighter look") to avoid misinterpreting meaning.
- Keep credits (e.g., "with help of Gemini 3 Pro/Claude/ChatGPT") and preserve them when rewriting.
- Preserve important technical specifics verbatim (e.g., "0 / 0 / 0 / 0 / 100", "2 placeholders vs 3 substitutions", "remove the extra X starting position").
- **Preserve ALL technical qualifiers** - e.g., "debug DLL" not just "DLL", "tech advisor screen height" not just "screen height", etc. These distinctions matter.
- Preserve specific scope qualifiers in technical details; avoid vague rewrites that drop precise context (e.g., keep "tech advisor screen height" rather than just "screen height").
- Keep exact technical phrasing; avoid substituting terms like "starting position" -> "start" or dropping modifiers like "vertically".
- Preserve exact spacing/formatting in technical details (e.g., "- 30" vs "-30").
- Preserve exact counts/quantities when they are mentioned (e.g., "3 strings").
- Preserve rationales (e.g., "it is distracting") when they explain why a change was made.
- Preserve rationale clauses about why something is unnecessary (e.g., "we don't need to show beyond BFC").
- **Be more verbose when explaining rationales** - it's important to capture the intent behind the change while summarizing. The "why" is critical, so preserve problem descriptions, observed behavior, and intended fixes more fully than other commentary.
- Preserve contrast/difference phrasing when it carries technical meaning (e.g., "unlike in the foreign advisor").
- Keep exact marker strings like "AdvCiv Mod" or "AdvCiv-SAS Mod" for later searches.
- Add this suffix to any comment I edit: `(GPT-5.2-Codex (summarized)) -->` or `(Claude code Sonnet 4.5 (summarized)) -->` depending on which model is doing the summarization.
- **Do NOT commit changes without explicit user approval** - wait for review at the end.
- When committing, add a `Co-authored-by:` trailer with the model identifier unless the user requests otherwise.
- When user feedback adds a new rule, update this file proactively.

## Current Scope (2026-01-02)

- **Focus on:** Python (.py) files with lengthy verbose comments
- **Ignore for now:** Markdown (.md) files and git commit messages
  - These may be handled later or manually, or left as-is

## Examples of Good Summarization

**Before:**

```python
# <!-- custom: use "is" not "==" when checking none as per ruff rule and chatgpt's answer and my idea too anyways etc -->
```

**After (GPT-5.2-Codex):**

```python
# <!-- custom: use "is" not "==" when checking None (ruff). Credit: ChatGPT. (GPT-5.2-Codex (summarized)) -->
```

**Before:**

```python
# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
```

**After (GPT-5.2-Codex):**

```python
# <!-- custom: expand the screen like Foreign Advisor/Sevopedia so crowded player lists require less scrolling. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.2-Codex (summarized)) -->
```

## Model Work Logs

### GPT-5.2-Codex

- 2026-01-02: Summarized Python comments across 36 files (commit 8d980497)
  - Files: BUG utilities, Screens (Military/Domestic/Tech advisors, etc.), Python scripts
  - Applied all comment editing rules consistently
  - Preserved all credits (ChatGPT, Gemini 3 Pro, Claude Sonnet 4.5)

### Claude Sonnet 4.5

- 2026-01-03: Summarized **ALL** C++ comments across entire CvGameCoreDLL directory (commit TBD)
  - **Session 1 (manual)**: 11 files with "with help" pattern (~55 comments)
    - CvCityAI.cpp (~15), CvUnitAI.cpp (~20), CvGameTextMgr.cpp (3), CvDLLWidgetData.cpp (4), CvCity.cpp (2), CitySiteEvaluator.cpp (3), CvPlayerAI.cpp (4), CvInfo_Unit.cpp (4), CvInitCore.cpp (2), CvSelectionGroupAI.cpp (1), CvTeamAI.cpp (1)
  - **Session 2 (batch + agent)**: All remaining files (~600+ comments)
    - Batch processed common patterns (static const, cache calls, hoist, etc.) across 26 files
    - Agent processed unique verbose comments in CvCityAI.cpp (235), CvUnitAI.cpp (122), CitySiteEvaluator.cpp (44), CvCity.cpp (38), CvPlayerAI.cpp (27), CvUnit.cpp (24), CvGameTextMgr.cpp (17), and 340+ other files
  - **Total**: 650+ comments summarized across 348 C++ source and header files
  - **Verification**: 0 "anyways etc" remaining in CvGameCoreDLL directory
  - Applied all comment editing rules consistently, with emphasis on preserving rationales and "why" behind changes
  - Preserved all credits (ChatGPT, ChatGPT 5, ChatGPT 5.1, ChatGPT 5.2, ChatGPT o3, Gemini AI, Gemini 2.5 Pro, Gemini 3 Pro, Claude Sonnet 4.5, Claude AI)
  - Uses suffix: `(Claude code Sonnet 4.5 (summarized)) -->`
  - Removed conversational filler: "anyways etc", "check if accurate", "if i may say", "xd", "hehe", redundant phrases
  - Key improvements: Preserved problem descriptions, observed behaviors, empirical results (e.g., "city C fully improved at turn 105"), and intended fixes while removing verbosity
  - Pattern: Keep technical details and "why" verbose, remove conversational filler
  - **Status**: Complete - all C++ files in CvGameCoreDLL now have concise, professional comments

## Coding Preferences

### Python (Civ4)

- Assume Python 2.4 constraints: avoid closures and ternary operators, define variables before use, and prefer tabs for indentation.
- Treat linting output as hints only; Civ4 runs Python 2.4 and engine imports can look unused to Python 3 linters.
- Use the Python 2.4/3 print compatibility trick for debugging: `print("msg %s" % value)` is valid in both (single string only).
- Prefer robust UI identifiers: widget names can strip numeric suffixes, so use descriptive text suffixes and map widget IDs to data for event handling.
- In fragile Civ4 Python, wrap risky calls in try/except and trust UI state when engine state can drift.
- When adding guidance, include at least one simple code example so other agents can copy the pattern.

### Docs

- For markdownlint, try to resolve warnings; if a fix is unclear or risky, ask the user.

## Comment Style Example

```cpp
// <!-- custom: For AI stack attacks, spend expendable units first to preserve elite finishers.
// This is economically efficient: older/weaker units cost upkeep but scale poorly, while elite units are costly to lose
// and can secure the fight if early attacks go badly; keeping them as finishers preserves flexibility and escape odds.
// Once bombard is done and we have decided to attack, siege/collateral units go first because they are less useful on defense
// and have already contributed their main value; this also front-loads collateral damage to soften the defenders.
// Order by lowest effective power, then lowest XP; among healthy units (>= SAS_*_MIN_HEALTH_PERCENT), lower health first. (GPT-5.2-Codex) -->
```

- Prefer SAS defines for new AI toggles; use `SAS_<func_name>_<effect>` naming and a boolean-style enable/disable flag (int in XML, bool in C++).
- Rationale: toggles allow quick testing without recompiles and give players more tuning options; avoid overusing defines when the feature is tiny or unlikely to need tuning.
- Do not commit changes unless the user explicitly approves; prefer review/discussion before commits.
- Prefer minimalistic, simple AI changes that are easy to reason about and compile.
- Prefer `const` for locals whenever possible to make intent clear and prevent accidental mutation.
- Discuss candidate locations and a minimal draft before coding larger AI behavior changes.
- Favor effectiveness and simplicity over complex heuristics; avoid overengineering.
- For AI or gameplay logic changes, include a slightly more verbose rationale (why it helps efficiency or outcomes), not just what changed.
- When adding rationale, focus on the economic/strategic reasoning (efficiency, versatility, risk, maintenance) and capture the thought process behind the change.
- When changing attack logic, account for special unit roles (bombard/collateral) and UWAI expectations.
- These are general guidelines, not strict requirements; adjust based on task needs.
- Prefer low-level entry points (e.g., `canScrap`, `canUpgrade`, `AI_chooseUnit` or equivalent) to avoid edge cases from higher-level callers; keep logic close to core decisions.
- When adding doc entries in dev mode (most of the time), prefix bullet titles with `- (Requires AdvCiv-SAS X+)` where `X` is current latest commit + 1, since docs describe post-commit state for readers. Current rule of thumb: last stable is 5282, so 5283+ is beta/dev and should carry the prefix until the next stable release.
- When adding new comments, use the format `<!-- custom: ... (GPT-5.2-Codex) -->` (with `//` or `#` prefix as appropriate) instead of other tags like advc.sas.
- Example: for attack order changes, hook `groupAttack`/`AI_getBestGroupAttacker` rather than odds-estimation helpers, so other functions or pieces of logic don't overlap with or override our code.
