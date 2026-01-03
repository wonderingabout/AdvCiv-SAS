# GPT-Codex Guidelines

These rules apply to me now and later (future me too). Append the following instructions as we agree on them. You can expand this freely as you see fit.

## Comment Editing Rules (for me, now and later)

- Simplify verbose comments without changing meaning or technical details.
- Do not requalify subjective wording (e.g., keep "nicer display" instead of rephrasing as "tighter look") to avoid misinterpreting meaning.
- Keep credits (e.g., "with help of Gemini 3 Pro/Claude/ChatGPT") and preserve them when rewriting.
- Preserve important technical specifics verbatim (e.g., "0 / 0 / 0 / 0 / 100", "2 placeholders vs 3 substitutions", "remove the extra X starting position").
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

- 2026-01-02: Summarized C++ comments across multiple files (in progress, not yet committed)
  - Files completed: CvCityAI.cpp (~15 comments), CvGameTextMgr.cpp (3), CvDLLWidgetData.cpp (4), CvCity.cpp (2), CitySiteEvaluator.cpp (3), CvUnitAI.cpp (~20 comments)
  - Applied all comment editing rules consistently, with emphasis on preserving rationales and "why" behind changes
  - Preserved all credits (ChatGPT, ChatGPT 5, ChatGPT 5.1, ChatGPT 5.2, Gemini AI, Gemini 2.5 Pro, Gemini 3 Pro, Claude Sonnet 4.5, Claude AI)
  - Focused on lengthy verbose comments in CvGameCoreDLL directory
  - Uses suffix: `(Claude code Sonnet 4.5 (summarized)) -->`
  - Key improvements: Preserved problem descriptions, observed behaviors, empirical results, and intended fixes more fully than other commentary
  - Remaining work: CvPlayerAI.cpp (7 comments), CvInfo_Unit.cpp (4 comments), and a few other files

## AI Enhancement Preferences

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
