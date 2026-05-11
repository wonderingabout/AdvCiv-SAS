# AGENTS

## Credit

AI, UI, or other modifications
Created as part of AdvCiv-SAS improvements
(c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

## General information

This is the general guidelines to follow for this repo of our mod AdvCiv-SAS that is based on AdvCiv 1.12, for AI helpers. You don't need to look at files mentioned in this sub-section for now, just get aware of their existence if you need them later in our tasks.

You can expand this [AGENTS.md](/AGENTS.md) freely as you see fit.

## git, GitHub, and git diff info

Our mod is also on github, see [AdvCiv-SAS's github repo](https://github.com/wonderingabout/AdvCiv-SAS).

Locally our project is a git repo too, generally with a fresh commit for each new main task, so feel free to git diff while doing your tasks to see your progress and analyze or such.

Important git-diff caution: moving/reordering plus modifying large similar-looking XML blocks (e.g. `<BuildingInfo>` blocks) can make `git diff` look like a large rewrite/modification of these was made, when in fact none or only one was changed. Example: moving `BUILDING_IRELAND_SCRIPTORIUM` in `CIV4BuildingInfos.xml` from around the Library area to under the last civ-specific University block makes it seem like generic university, university madrassa, university salon were modified, but they were not and are still the same as before. In this case, let the user handle a separate commit for the move/reorder first, then continue with gameplay/stat edits afterward (then user will ammend commit later after second-step modifications are reviewed).

## Information Fetching from other known helpful mods

If you don't know how to do something, generally mostly for UI stuff as we like to have and invent our own AI logic, generally (not a strict requirement but generally so), if you find yourself stuck or in doubt to double-check how other mods implement things, consider looking at what these mods do, as they usually have high-tech stuff that has oftentimes proven handy for the AdvCiv-SAS mod, in particular and mostly for UI:

- The Middle-earth mod (in particular but not only their Platypedia) at "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Middle-earth"
- The C2C (Cavemen2Cosmos) mod (in particular but not only for UI/EXE stuff) at "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Caveman2Cosmos"

While doing so and comparing with our approach and what our mod does, in the end we'd adjust for our AdvCiv-based mod and not strictly copy paste it, unless it is fine for our needs. We should properly credit them as such in code comments or docs when we do so.

Example of UI tip discovered: if a new Sevopedia category needs clickable entries and the EXE doesn't fire a custom widget, use `WidgetTypes.WIDGET_PYTHON` with a custom data1 code (e.g. 6798) and route it in `SevoPediaMain.handleInput` to `pediaJump`. Middle-earth's PlatyPedia routes/traits use this pattern. C2C mod also uses `WidgetTypes.WIDGET_PYTHON`.

## Information Fetching locally (Dbg.log, Err.log, etc.)

You can find Civ4 local user folder here "C:\Users\PC\Documents\My Games\beyond the sword".

In particular but not only, these are usually helpful:

- "C:\Users\PC\Documents\My Games\beyond the sword\Logs\PythonDbg.log"
- "C:\Users\PC\Documents\My Games\beyond the sword\Logs\PythonErr.log"
- "C:\Users\PC\Documents\My Games\beyond the sword\CivilizationIV.ini"

The root Program Files Civ4 folder is here:

- "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\"

Also, legacy documentation (K-Mod, AdvCiv, etc.) may prove helpful, but it is lengthy, grep if needed from there:

- "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_0_Common_Docs\AdvCiv_Base_Doc\manual.txt"

Our AdvCiv-SAS documentation is mostly located here:

- root README.md: "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\README.md"
- Docs folder: "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_1_AdvCiv-SAS\Docs"
- Screenshots for a lot of AdvCiv-SAS elements ingame including but not only Sevopedia, Advisors, etc. They are fairly updated too if it helps: "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_1_AdvCiv-SAS\Images"

May help to find key documentation, additionally to doing a grep or such, indexes like `# advc.004y: Restored (comment out to remove traits)` refer to and provide key information about a change (grep the tag e.g. `004y` in the manual).

Compile errors (e.g., for a "Release" build) at:

- "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\CvGameCoreDLL\Project\Release\AdvCiv.log"

## File reading from a non-global link

- If you cannot read one of the files or links the user sends (not including web pages or such), specify it to the user instead of blindly proceeding, as the info like a screenshot may help you see and solve the issue.

## Sevopedia debug dumps (Python API introspection)

When a Python getter seems missing or unclear (e.g., the culture breakdown error where `CvCivicInfo` has no `getCommerceChange`), use Sevopedia debug dumps to verify what Python can actually access without having to guess if a getter is exposed in Python or requires DLL changes; these debug logs are usually our first and preferred source of truth since they are real inspect logs, although they might be slightly outdated if DLL changes were made since then.

- "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\Assets\Python\Contrib\Sevopedia\Debug" (example file: [__SevoPediaCivic-gc-inner.txt](/Assets/Python/Contrib/Sevopedia/Debug/__SevoPediaCivic-gc-inner.txt)).

Alternatively, the Civ4 BUG documentation is also provided as .txt, may be helpful, consider reading it for double check or grep needs if in doubt or such. It helped us find the `Destroy2DSound` python function for example, doc is helpful as reference (but lengthy):

- "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\AdvCiv-SAS\_0_Common_Docs\CIV4BUG_Sourceforge_net_All_Classes_Doc\civ4bug_pythonAPI_AllClasses_html.txt"

## Information Fetching online

If you find yourself stuck like for audio stopping issues, feel free to ask the user to perform one or many web searches, maybe some solutions exist or insights on how solvable issues are.

## Comment Editing Rules

- Always preserve the `<!-- custom` prefix - never remove it when summarizing comments. At the end of your comment, append a `-->` if not already done.
- Simplify verbose comments without changing meaning or technical details.
- Focus on rewording/rephrasing - the goal is to remove prose and conversational filler while preserving all technical information. Don't over-summarize to the point of losing important technical context.
- Do not requalify subjective wording (e.g., keep "nicer display" instead of rephrasing as "tighter look") to avoid misinterpreting meaning.
- Keep credits (e.g., "with help of Gemini 3 Pro/Claude/ChatGPT") and preserve them when rewriting.
- Preserve important technical specifics verbatim (e.g., "0 / 0 / 0 / 0 / 100", "2 placeholders vs 3 substitutions", "remove the extra X starting position").
- Preserve all technical qualifiers - e.g., "debug DLL" not just "DLL", "tech advisor screen height" not just "screen height", etc. These distinctions matter.
- Preserve specific scope qualifiers in technical details; avoid vague rewrites that drop precise context (e.g., keep "tech advisor screen height" rather than just "screen height").
- Keep exact technical phrasing; avoid substituting terms like "starting position" -> "start" or dropping modifiers like "vertically".
- Preserve exact spacing/formatting in technical details (e.g., "- 30" vs "-30").
- Preserve exact counts/quantities when they are mentioned (e.g., "3 strings").
- Preserve rationales (e.g., "it is distracting") when they explain why a change was made.
- Preserve rationale clauses about why something is unnecessary (e.g., "we don't need to show beyond BFC").
- Be more verbose when explaining rationales - it's important to capture the intent behind the change while summarizing. The "why" is critical, so preserve problem descriptions, observed behavior, and intended fixes more fully than other commentary.
- Preserve contrast/difference phrasing when it carries technical meaning (e.g., "unlike in the foreign advisor").
- Keep exact marker strings like "AdvCiv Mod" or "AdvCiv-SAS Mod" for later searches.
- When adding new comments, use the format `<!-- custom: ... (GPT-5.3-Codex) -->` (with `//` or `#` prefix as appropriate) instead of other tags like advc.sas.
- Do not use `/*` or `"""` or `'''` or such docstrings or variants. Prefer `//` or `#` or similar so they are easier to manage/uncomment and less costly computationally. Keep existing ones as they are, as some `"""` docstrings seem functionally used in tests (do not modify these, only the new ones we create).
- Add a suffix with your model name to your code comments; e.g., `(GPT-5.3-Codex (summarized)) -->`, `(Claude code Sonnet 4.5 (summarized)) -->`.
- When writing new code, do not use other credentials than our custom ones, e.g. no `// advc.`, as they do not belong to us. Use `<!-- custom:` instead.
- Do NOT commit changes without explicit user approval - wait for review at the end.
- Preserve problem descriptions, observed behaviors, empirical results (e.g., "city C fully improved at turn 105"), and intended fixes while removing verbosity
- Pattern: Keep technical details and "why" verbose, remove conversational filler

## Comment Style Example

```cpp
// <!-- custom: For AI stack attacks, spend expendable units first to preserve elite finishers.
// This is economically efficient: older/weaker units cost upkeep but scale poorly, while elite units are costly to lose
// and can secure the fight if early attacks go badly; keeping them as finishers preserves flexibility and escape odds.
// Once bombard is done and we have decided to attack, siege/collateral units go first because they are less useful on defense
// and have already contributed their main value; this also front-loads collateral damage to soften the defenders.
// Order by lowest effective power, then lowest XP; among healthy units (>= SAS_*_MIN_HEALTH_PERCENT), lower health first. (GPT-5.3-Codex) -->
```

## Examples of Good Summarization

**Before:**

```python
# <!-- custom: use "is" not "==" when checking none as per ruff rule and chatgpt's answer and my idea too -->
```

**After:**

```python
# <!-- custom: use "is" not "==" when checking None (ruff). Credit: ChatGPT. (GPT-5.3-Codex (summarized)) -->
```

**Before:**

```python
# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for Sevopedia, so that we don't have to scroll or less so. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks ;check if accurate -->
```

**After:**

```python
# <!-- custom: expand the screen like Foreign Advisor/Sevopedia so crowded player lists require less scrolling. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.3-Codex (summarized)) -->
```

## Coding Preferences

These are general guidelines, not irrevocable requirements; adjust based on task needs.

### General

- No approximations like `"%.1f"` or `%02d`; we want precision, no fluff. Use `%f` or `%d` instead. Example of exception: `%02d` as zero-padding for nicer ordering/alignment `(Calendar_01, Calendar_02, ...)`.
- Prefer `const` for locals whenever possible to make intent clear and prevent accidental mutation.
- Favor effectiveness and simplicity over complex heuristics; avoid overengineering.
- Prefer derived variables or an explicit `if/else` over assigning a value and then mutating it. Example problem: avoid setting `iPlotCol = iBaseCol` and later doing `iPlotCol += 3`, or setting a default like `iPlotCol = 19` and then overriding it later with `iPlotCol = 22`. Example solution: use `iContextColCount = 3` and `iPlotCol = iBaseCol + iContextColCount`, or set `iPlotCol` once in each branch when a SAS define changes the number of desired columns/parameters. An `if/else` is also good when the branches explain distinct layout or logic cases.
- For AI or gameplay logic changes, include a slightly more verbose rationale (why it helps efficiency or outcomes), not just what changed.
- When adding rationale, focus on the economic/strategic reasoning (efficiency, versatility, risk, maintenance) and capture the thought process behind the change.
- Do not commit changes unless the user explicitly approves; prefer review/discussion before commits.
- Try to make one liner code whenever possible, for example a line like `draw_expandable_text_panel(screen, self.top, szTitle, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, szText, self.bHistoryExpanded, self.top.SAS_PEDIA_PYTHON_HISTORY_EXPAND)` is much easier to scan or grep through/compare throughout our codebase than a multi-line mostly needlessly stylized version of it. As such a refactor would be extensive, do it as we go rather than all in one-go. See also a LLM-helper to perform that refactor for py files in [collapse_multiline_brackets.py](/LLM_Helpers/collapse_multiline_brackets.py).
- Note that an exception to the former is for very long or uniform listings such as as of now in `self.SAS_CATEGORY_DEFS` or `getMusicList` (in SevoPediaMain.py): a multiline statement seems preferable and more readable for these. Adjust as you see fit.
- When doing performance optimizations, checking quotes (i.e. `"`) only on one side is handy to spot all string lookups we could potentially cache. E.g. `gc.getInfoTypeForString("` has this result `iHill = gc.getInfoTypeForString("TERRAIN_HILL")`. Or appending `.` or `)` or ` ` or `,`, or ` `, etc., to what we want to simplify. E.g., `GET_TEAM(getTeam()).` or `GET_TEAM(getTeam()))`, or `GET_TEAM(getTeam()) `, or `GET_TEAM(getTeam()),`, etc. Basically any charcter other than `;`, for example `GET_TEAM(getTeam());`, most likely indicates this is not a cached variable and so most likely an optimize candidate.
- When doing performance optimizations, using local variables only is enough and best if we don't use this variable elsewhere. E.g. `eYellow = gc.getInfoTypeForString("COLOR_YELLOW")` at init in SevoPediaMain.py.
- In some rare cases, it is better not to cache rather than cache, because we will not read the define again, so caching is costlier and needless. For example, `start_year = gc.getDefineINT("START_YEAR")` when `start_year` is only used once to build a (sevopedia game speed) chart that we cache and then the variable is discarded. Mark these with a comment like `not cached: read once only`.
- Use specific asset names whenever possibly to avoid likely reuse of an unknown BTS one that may not be listed in our mod's files. Example: `TXT_KEY_PEDIA_STATISTICS` to `TXT_KEY_PEDIA_SAS_STATISTICS`.
- Avoid fluff like `================`, keep it nice and simple and clean.
- Avoid silent fallbacks or placeholder defaults when data is missing: we want it to loudly fail so code is more robust rather.
- Avoid complicated and formatting-error prone characters (e.g., `“` or `”`), use simple characters (e.g., `"`) instead.
- Note: codex's shell/tool output likely sometimes displays mojibake for characters that look correct in VS Code or git diff (e.g., smart quotes shown as `â€œ` / `â€`) hence the user/LLM mismatch. Do not "fix" encoding based only on the terminal/tool rendering; rely on VS Code (user feedback) or git diff if they show the file cleanly.
- Note: sometimes our files have a mix of CRLF/LF in them causing next commit to have a massive git diff (e.g., 240 insertions(+), 240 deletions(-) when there is in fact no change) when VS Code or maybe the LLM tries to next modify it, and this is a problem because it pollutes diff and makes it hard to read. Empirically, it happened to [CvInfoScreen.py](/Assets/Python/Screens/CvInfoScreen.py) or [CvMilitaryAdvisor.py](/Assets/Python/Screens/CvMilitaryAdvisor.py), and we could resolve it by adding a newline at end of file, saving, then deleting it (not undoing, so we preserve the change) or some other minor modifications (this is likely why VS Code shows no diff lines changed but the file is still not removed from changed files), then git staging this file only, committing it so the massive noisy diff normalizes (or we may commit the noisy diff with our actual change in one commit anyway if not critical for no tedium), and then reapplying our proper file (note that you need to reapply it in same expected format, usually CRLF not LF, else you'd have every line to be a diff (git would assume we changed it all from CRLF to LF)). This is likely caused by codex's apply patching tool (git bash shows `warning: in the working copy of 'AGENTS.md', LF will be replaced by CRLF the next time Git touches it` after codex's one line modification). On your end, don't mind it and let the user handle it, as it is cheaper in tokens and more reliable, but inform the user if you notice it. Use `git diff --ignore-space-at-eol --stat` and `git diff --ignore-space-at-eol -- <file>` to continue your work and review the semantic changes, then let the user handle EOL cleanup afterwards unless explicitly asked.

### Python (Civ4)

- Assume Python 2.4 constraints: avoid closures and ternary operators, define variables before use, and prefer tabs for indentation.
- For UI text, do not hardcode font tags like `<font=2/3/4>`; use `SASFontUtils` (`sasFontTag*`/ `sasFontTag*.bold` / `SAS_FONT_TAG_CLOSE` / `getSASUIFont*`) so XML defines control scaling globally. Example good: `sasFontTagLabel + szText + SAS_FONT_TAG_CLOSE` or `sasFontTagTitle.bold + szText + SAS_FONT_TAG_CLOSE`; avoid: `u"<font=3>%s</font>" % szText` or `u"<font=4b>%s</font>" % szText`.
- Some rare exceptions exist where hard coded font size is necessary (e.g., as of now Foreign Advisor's Glance tab's diplomacy icons (else the cell's text clips horizontally)), some places where font size was not necessary to increase empirically to achieve the wanted result, or some places where upscaling was not implemented yet due to it being not possible (EXE-controlled or such) or not supported in AdvCiv-SAS (e.g., as of now Chat log, etc.).
- Treat linting output as hints only; Civ4 runs Python 2.4 and engine imports can look unused to Python 3 linters.
- Use the Python 2.4/3 print compatibility trick for debugging: `print("msg %s" % value)` is valid in both (single string only).
- Prefer robust UI identifiers: widget names can strip numeric suffixes, so use descriptive text suffixes and map widget IDs to data for event handling.
- For Civ4 Python UI labels that pass through font-tagged/markup renderers (`screen.setText`, `screen.setLabel`, `SASTextScale.labelText`, etc.), keep raw text in state and escape only the display string: `szDisplay = szRaw.replace(u"&", u"&amp;").replace(u"<", u"&lt;").replace(u">", u"&gt;")`. This preserves clicked or keyboard-typed raw characters for logic/search while rendering them safely. Raw `&`, `<`, and `>` are XML/markup-sensitive and would normally break XML, so they are rarely useful for ordinary XML text-key search; this rule is mainly for Python UI rendering of dynamic/user-entered text. In the Sevopedia search bar, raw `<`/`>` corrupted the label with `/font`-like fragments, and raw `&` could be invisible and make following characters unclear.
- In fragile Civ4 Python, wrap risky calls in try/except and trust UI state when engine state can drift.
- When adding guidance, include at least one simple code example so other agents can copy the pattern.
- When caching defines or XML variables, we need to init to `None` and cache explictly later when the variable is used or somewhere at call time. This is because empirically aggressive initialization at init is fragile and can cause crashes. For helper files, we use the `global` and if `None` pattern. Since this new pattern is a recent addition, we are not changing them all right now but rather as we go or implement new stuff. See [KI#128](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#128---seemingly-fixed--worked-around-runtime-ui-definestyle-changes-could-produce-crashy-python-like-behavior).
- It seems definebool does not exist in python, so use boolean comparison on int rather; e.g., `IS_SAS_CV_INFO_SCREEN_HISTORY_LOG_BUTTON_ENABLE = (gc.getDefineINT("SAS_CV_INFO_SCREEN_HISTORY_LOG_BUTTON_ENABLE") > 0)`. Does not apply to C++ though that has defineBOOL.
- Avoid silent fallbacks or placeholder defaults when data is missing; prefer fatal errors with clear messages so issues surface early, and validate list structures (e.g., assert expected prefixes/types in debug checks).
- Prefer `getInfoTypeOrFail("TAG")` (from `SASUtils`) over raw `gc.getInfoTypeForString("TAG")` whenever possible so bad XML tags fail loudly and early; this helped catch incorrect direction-string usage in Planet Generator map (e.g., incorrect `getInfoTypeOrFail("DIRECTION_NORTH")` failing instead of `DirectionTypes.DIRECTION_NORTH*` enum constants; or incorrect `getInfoTypeOrFail("PLOT_PEAK")` instead of correct `PlotTypes.PLOT_PEAK` (in Peirce map)).
- When parsing large structured data, validate against expected samples or assertions early, and log diagnostics to surface schema/list mistakes (e.g., missing commas or malformed enum lists).
- Use `from module import *` for helper modules to reduce import tedium and make future additions seamless.
- Keep import burden on callers for Civ4-specific dependencies: helper functions should receive Civ4 objects (e.g. `gc`, `screen`, `CyGame()`) as parameters rather than importing them internally. This avoids circular dependencies. Standard Python modules (`re`, `math`, etc.) are fine to import directly in helpers since they're cached and always available.
- When extracting shared code to helpers, group all patterns together if similar enough otherwise (e.g. all enum prefixes in one tuple) for simplicity, even if some prefixes are only used by one caller.

## XML

- Any new XML text should go to our AdvCiv-SAS files such as [AdvCiv-SAS_main.xml](/Assets/XML/Text/AdvCiv-SAS_main.xml) (e.g., `TXT_KEY_BUILDING_KOREAN_GYEONGDANG`), and only in `<English>`.
- Example of exception: long Civilopedia blurbs (e.g., `TXT_KEY_BUILDING_KOREAN_GYEONGDANG_PEDIA`) in [AdvCiv-SAS_Sevopedia_Lengthy.xml](/Assets/XML/Text/AdvCiv-SAS_Sevopedia_Lengthy.xml), even when it uses a stub (becuase it will be filled later with lengthy content).
- Move XML texts we modify from other files to our AdvCiv-SAS files too and remove other languages while doing so.
- Avoid to comment in deep-nested XML just in case. For example, comment before `<ObsoleteSafeCommerceChanges>`, not before its child `<iCommerce>`.
- Avoid complicated and formatting-error prone characters (e.g., `“` or `”`), use simple characters (e.g., `"`) instead.
- Prefer UTF-8 as it's simple and seemingly works well enough; avoid UTF-8 with BOM as it can cause actual mojibake artifacts like `â€”it` or `â€™` the user sees on VS Code or other issues.
- Exception: preserve each XML file's existing encoding if it's not UTF-8; do not convert encodings unless explicitly requested for no tedium and as we have no reason to (e.g., keep legacy Windows-1252 files such as BUG XML files as-is), plus this would have a high chance of causing formatting errors otherwise.
- Note and additional observation: the codex formatter seems unreliable and inconsistent with what users see (e.g., showing the LLM model a BOM text when user sees a non BOM one, causing mismatches and weird git diff: refer to git diff or what base AdvCiv mod uses as format if in doubt).

## C++

- Prefer SAS defines for new AI toggles; use `SAS_<func_name>_<effect>` naming and a boolean-style enable/disable flag (int in XML, bool in C++). Rationale: toggles allow quick testing without recompiles; avoid overusing defines when the feature is tiny or unlikely to need tuning.
- Prefer minimalistic, simple AI changes that are easy to reason about and compile.
- Discuss candidate locations and a minimal draft before coding larger AI behavior changes.
- When changing attack logic, account for special unit roles (bombard/collateral) and UWAI expectations.
- Prefer low-level entry points (e.g., `canScrap`, `canUpgrade`, `AI_chooseUnit` or equivalent) to avoid edge cases from higher-level callers; keep logic close to core decisions. Example: for attack order changes, hook `groupAttack`/`AI_getBestGroupAttacker` rather than odds-estimation helpers, so other functions or pieces of logic don't overlap with or override our code.
- When doing performance optimizations, such as caching to `CvTeamAI const& kTeam = GET_TEAM(getTeam());` redundant definitions in a function, reuse existing variable names unless not relevant for our needs. It is fine if some functions have `kTeam` while others have `kOurTeam` in the same file, what matters is same function is consistent when using the same variable. This avoids errors too. Same reasoning with `kPlayer` and `kOwner`, etc.
- Use `static const` for our defines whenever possible and relevant for computational efficiency (value is always the same, quick check it rather). Example `static const bool bSAS_CAN_SCRAP_OBSOLETE_TECH = GC.getDefineBOOL("SAS_CAN_SCRAP_OBSOLETE_TECH");`.

### Docs

- For markdownlint, try to resolve warnings; if a fix is unclear or risky, ask the user.
- When adding doc entries in the [README_Main_Changes_Guide.md](/_1_AdvCiv-SAS/Docs/README_Main_Changes_Guide.md), prefix bullet titles with `- (Requires AdvCiv-SAS X+)` where `X` is current latest commit + 1, since docs describe post-commit state for readers. Current rule of thumb: latest stable is 5500, so the first commit after it would be 5501+, 10 commits later would be 5510+, etc.
- When a new stable release is made, then all these previous markers can be stripped (e.g. if next stable is AdvCiv-SAS 5560, then any requires <= 5559+ is stripped because players would have the changes in latest stable, so they don't need anymore the marker about a change they might not have yet (in tech-rework i.e. as of now our dev branch)). We don't need to mark other files since they are generally not player facing in that way and more general information on the mod (plus it's less tedious as such).
