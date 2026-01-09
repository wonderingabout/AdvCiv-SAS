# AGENTS

This is the general guidelines to follow for this repo of our mod AdvCiv-SAS that is based on AdvCiv 1.12.

These rules apply to me GPT-Codex Guidelines or other agents now and later (future me too). Append the following instructions as we agree on them. You can expand this freely as you see fit.

Note: our mod is also on github, see [AdvCiv-SAS's github repo](https://github.com/wonderingabout/AdvCiv-SAS) if needed.

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
- When adding new comments, use the format `<!-- custom: ... (GPT-5.2-Codex) -->` (with `//` or `#` prefix as appropriate) instead of other tags like advc.sas.
- Do not use `/*` or `"""` or `'''` or such docstrings or variants. Prefer `//` or `#` or similar so they are easierto manage/uncomment and less costly computationally. Keep existing ones as they are, as some `"""` docstrings seem functionally used in tests (do not modify these, only the new ones we create).
- Add this suffix to any comment I edit: `(GPT-5.2-Codex (summarized)) -->` or `(Claude code Sonnet 4.5 (summarized)) -->` or similar depending on which model is doing the summarization.
- When writing new code, do not use other credentials than our custom ones, e.g. no `// advc.`, as these help identify other maintainers than us. Keep old existing ones as much as possible for traceability unless clearly obsolete or not relevant anymore.
- **Do NOT commit changes without explicit user approval** - wait for review at the end.
- When committing, add a `Co-authored-by:` trailer with the model identifier unless the user requests otherwise.
- When user feedback adds a new rule, update this file proactively.
- Preserve all credits (ChatGPT, ChatGPT 5, ChatGPT 5.1, ChatGPT 5.2, ChatGPT o3, Gemini AI, Gemini 2.5 Pro, Gemini 3 Pro, Claude Sonnet 4.5, Claude AI)
- Use suffix with your model name/credential: `(Claude code Sonnet 4.5 (summarized)) -->`
- Preserv problem descriptions, observed behaviors, empirical results (e.g., "city C fully improved at turn 105"), and intended fixes while removing verbosity
- Pattern: Keep technical details and "why" verbose, remove conversational filler

## Comment Style Example

```cpp
// <!-- custom: For AI stack attacks, spend expendable units first to preserve elite finishers.
// This is economically efficient: older/weaker units cost upkeep but scale poorly, while elite units are costly to lose
// and can secure the fight if early attacks go badly; keeping them as finishers preserves flexibility and escape odds.
// Once bombard is done and we have decided to attack, siege/collateral units go first because they are less useful on defense
// and have already contributed their main value; this also front-loads collateral damage to soften the defenders.
// Order by lowest effective power, then lowest XP; among healthy units (>= SAS_*_MIN_HEALTH_PERCENT), lower health first. (GPT-5.2-Codex) -->
```

## Examples of Good Summarization

**Before:**

```python
# <!-- custom: use "is" not "==" when checking none as per ruff rule and chatgpt's answer and my idea too -->
```

**After (GPT-5.2-Codex):**

```python
# <!-- custom: use "is" not "==" when checking None (ruff). Credit: ChatGPT. (GPT-5.2-Codex (summarized)) -->
```

**Before:**

```python
# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia, so that we don't have to scroll or less so. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks ;check if accurate -->
```

**After (GPT-5.2-Codex):**

```python
# <!-- custom: expand the screen like Foreign Advisor/Sevopedia so crowded player lists require less scrolling. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.2-Codex (summarized)) -->
```

## Coding Preferences

These are general guidelines, not irrevocable requirements; adjust based on task needs.

### General

- No approximations like `"%.1f"` or `%02d`; we want precision, no fluff. Use `%f` or `%d` instead. Example of exception: `%02d` as zero-padding for nicer ordering/alignment `(Calendar_01, Calendar_02, ...)`.
- Prefer `const` for locals whenever possible to make intent clear and prevent accidental mutation.
- Favor effectiveness and simplicity over complex heuristics; avoid overengineering.
- For AI or gameplay logic changes, include a slightly more verbose rationale (why it helps efficiency or outcomes), not just what changed.
- When adding rationale, focus on the economic/strategic reasoning (efficiency, versatility, risk, maintenance) and capture the thought process behind the change.
- Do not commit changes unless the user explicitly approves; prefer review/discussion before commits.

### Python (Civ4)

- Assume Python 2.4 constraints: avoid closures and ternary operators, define variables before use, and prefer tabs for indentation.
- Treat linting output as hints only; Civ4 runs Python 2.4 and engine imports can look unused to Python 3 linters.
- Use the Python 2.4/3 print compatibility trick for debugging: `print("msg %s" % value)` is valid in both (single string only).
- Prefer robust UI identifiers: widget names can strip numeric suffixes, so use descriptive text suffixes and map widget IDs to data for event handling.
- In fragile Civ4 Python, wrap risky calls in try/except and trust UI state when engine state can drift.
- When adding guidance, include at least one simple code example so other agents can copy the pattern.
- Avoid silent fallbacks or placeholder defaults when data is missing; prefer fatal errors with clear messages so issues surface early, and validate list structures (e.g., assert expected prefixes/types in debug checks).
- When parsing large structured data, validate against expected samples or assertions early, and log diagnostics to surface schema/list mistakes (e.g., missing commas or malformed enum lists).

## XML

## C++

- Prefer SAS defines for new AI toggles; use `SAS_<func_name>_<effect>` naming and a boolean-style enable/disable flag (int in XML, bool in C++). Rationale: toggles allow quick testing without recompiles and give players more tuning options; avoid overusing defines when the feature is tiny or unlikely to need tuning.
- Prefer minimalistic, simple AI changes that are easy to reason about and compile.
- Discuss candidate locations and a minimal draft before coding larger AI behavior changes.
- When changing attack logic, account for special unit roles (bombard/collateral) and UWAI expectations.
- Prefer low-level entry points (e.g., `canScrap`, `canUpgrade`, `AI_chooseUnit` or equivalent) to avoid edge cases from higher-level callers; keep logic close to core decisions. Example: for attack order changes, hook `groupAttack`/`AI_getBestGroupAttacker` rather than odds-estimation helpers, so other functions or pieces of logic don't overlap with or override our code.
- When doing performance optimizations, such as caching to `CvTeamAI const& kTeam = GET_TEAM(getTeam());` redundant definitions in a function, reuse existing variable names unless not relevant for our needs. It is fine if some functions have `kTeam` while others have `kOurTeam` in the same file, what matters is same function is consistent when using the same variable. This avoids errors too. Same reasoning with `kPlayer` and `kOwner`, etc.
- When doing performance optimizations, a good trick that may help find many entries fairly cheaply is to append `.` or `)` or ` ` or `,`, etc., to what we want to simplify. For example `GET_TEAM(getTeam()).` or `GET_TEAM(getTeam()))`, or `GET_TEAM(getTeam()) `, or `GET_TEAM(getTeam()),`, etc. Basically any charcter other than `;`, for example `GET_TEAM(getTeam());`, most likely indicates this is not a cached variable and so most likely an optimize candidate.
- When doing performance optimizations, also optimize commented-out code for exhaustiveness.
- When doing performance optimizations, if there are returns and they don't use our cached variable, cache after them.

### Docs

- For markdownlint, try to resolve warnings; if a fix is unclear or risky, ask the user.
- When adding doc entries in dev mode (most of the time), prefix bullet titles with `- (Requires AdvCiv-SAS X+)` where `X` is current latest commit + 1, since docs describe post-commit state for readers. Current rule of thumb: last stable is 5282, so 5283+ is beta/dev and should carry the prefix until the next stable release.
