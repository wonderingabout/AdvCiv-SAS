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
