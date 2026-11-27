# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: These values apply for the lifetime of the Civ4 process.
# Restart Civ4 to apply edits.
# Loading another save keeps the current values.
# Settings that only Python reads live here, out of GlobalDefines_advciv_sas.xml, which the DLL loads and which stays the home of what the DLL or the EXE reads: one central place to tune the interface, with a shorter XML (the user's idea).
# Named for that session, as SASLiveDefineOverrides.txt is named for changes during play: the defines meant to change while Civ4 runs, such as the font sizes, stay in the XML, where that file reaches them; editing Python while Civ4 runs has caused errors before.
# The name was chosen with Codex (GPT-6.2-Sol): Session, a state like live, over Static, a C++ cache in this repository, Fixed, which also reads as repaired, Startup, which hints at code run only early, and Restart, an action; and Tunables, as these are plain values edited by hand, no longer GlobalDefines the engine loads, over Defines, kept for those, Settings, which may suggest BUG's options menu, and Python, as live Python-read defines stay in the XML.
# ci_pure_module: player settings only, read by importing this module; it holds plain values and imports nothing, so any screen, map script or helper can import it at any time, as SASMagicNumbers.py does for constants.
# Each value keeps the name and comment it had as a define, so a search for SAS_MAIN_UI_UNITS_WAITING_ON finds it here and in its readers.
# A typo here stops the module loading, where a bad XML value gives an error message instead; CI compiles this file as Python 2.4 and checks it stays pure. (Claude code Opus 5.5 + GPT-6.2-Sol) -->


# <!-- custom: Main interface, moved from GlobalDefines_advciv_sas.xml: the 23 SAS_MAIN_UI_ defines that only Python reads, in their XML order; the DLL reads the others of the family, which stay there. (Claude code Opus 5.5) -->
# <!-- custom: optionally set how many extra rows of things to build (units, buildings, processes (research, wealth, culture)) you want to show in the city screen's production chooser bar.
# 0 disables this feature entirely.
# 1 Adds an extra row, 2 adds 2 extra rows, etc. Code added with the help of chatgpt 5.2 thanks.
# (Note: as of now does not affect the production chooser outside of the city screen (i.e. by clicking without entering the city screen)) -->
SAS_MAIN_UI_CITY_BAR_EXTRA_ROWS = 2

# <!-- custom: extra vertical adjustment for the city-screen things-to-build bar (inactive if SAS_MAIN_UI_CITY_BAR_EXTRA_ROWS <= 0).
# Value is resolution-scaled and sign-preserving: < 0 moves the bar up, > 0 moves it down, 0 keeps base placement.
# Adjust as you see fit. (GPT-5.3-Codex (summarized)) -->
SAS_MAIN_UI_CITY_BAR_EXTRA_ROWS_ADJ = 5

# <!-- custom: extra city-screen build-bar height tweak (pixels, VSPACE-scaled). Positive = taller (helps clipped bottom-row icons), negative = shorter. 0 keeps base behavior. (GPT-5.3-Codex) -->
SAS_MAIN_UI_CITY_BAR_HEIGHT_ADJ = 30

# <!-- custom: extra city-screen center blue-ribbon lift only (on top of base city-screen lift).
# Positive lifts more, negative lowers.
# 0 keeps base behavior. (GPT-5.3-Codex) -->
SAS_MAIN_UI_CITY_BLUE_RIBBON_EXTRA_LIFT = 27

# <!-- custom: Show the unit bar ("PlotListPanel") while a city is selected when 1.
# Default 0 keeps it hidden because the production chooser's extra rows partially cover it; this preserves the earlier HIDE=1 layout with positive SHOW naming.
# The main-interface define cache requires a Civ4 restart after changing it. (ChatGPT-5.2 Thinking + GPT-6.1-Sol) -->
SAS_MAIN_UI_CITY_SHOW_PLOT_LIST = 0

# <!-- custom: city-screen bonus rendering mode: 0 = old AdvCiv-SAS text glyphs, 1 = base AdvCiv-style framed image buttons, 2 = new AdvCiv-SAS frameless DDS icons (addDDS removes distracting button-frame edges).
# Text glyphs are kept for legacy/debug mode and forced overflow fallback, but testing showed they stay much smaller than image buttons even when font is increased, so use mode 1 or 2 for large bonus icons. (GPT-5.5) -->
SAS_MAIN_UI_CITY_BONUS_ICON_MODE = 2

# <!-- custom: add buttons city screen in the production queue and other places, with the help of claude opus 4.5 -->
SAS_MAIN_UI_PROD_QUEUE_BUTTONS = 1

# <!-- custom: show unit info button in the map view unit panel (GPT-5.2-Codex) -->
SAS_MAIN_UI_UNIT_INFO_BUTTON = 1

# <!-- custom: 1 shows beside the selected unit's name how many of our units still wait for orders, out of all of them, such as "(52 / 151 waiting)"; cycling units, nothing said how many were left (2026-11-27). (Claude code Opus 5.5) -->
SAS_MAIN_UI_UNITS_WAITING_ON = 1

# <!-- custom: 1 shows in the city screen's title the city's place in our city list, the order its arrows cycle through, such as "[4/17]" (2026-11-27). (Claude code Opus 5.5) -->
SAS_MAIN_UI_CITY_POSITION_ON = 1

# <!-- custom: enable compact top-left civ flag (hover/click) and matching left-text spacing shift (e.g. treasury); set to 0 to hide the flag and keep left text at base position. (GPT-5.3-Codex (summarized)) -->
SAS_MAIN_UI_TOP_LEFT_FLAG_TEXT_SHIFT = 0

# <!-- custom: width adjustment (resolution-scaled (HLEN/VLEN) pixels) for the left-side default help text area used in the map view (unit hover info, plot/unit-list selection details).
# Positive (e.g., 100) widens the box rightward into the map; negative (e.g., -50) narrows it. (Claude code Opus 4.7).
# Note: Extreme values (e.g., -1000, 2000) can produce the opposite effect so use moderate values to produce the intended effect.
# (Base AdvCiv value: 0) -->
SAS_MAIN_UI_HELP_AREA_WIDTH_ADJ = 25

# <!-- custom: shift the map-view unit bar horizontally (resolution-scaled pixels). Positive = right, negative = left. (Claude code Opus 4.7). (Base AdvCiv value: 0) -->
SAS_MAIN_UI_PLOT_LIST_X_OFFSET = 0

# <!-- custom: shift the map-view unit bar vertically (resolution-scaled pixels). Positive = down, negative = up. (Claude code Opus 4.7). (Base AdvCiv value: 0) -->
SAS_MAIN_UI_PLOT_LIST_Y_OFFSET = 0

# <!-- custom: hard-pixel width tweak for the unit bar (not resolution-scaled). Negative shrinks rows = fewer buttons per row, useful when an expanded scoreboard or an X/Y offset pushes the bar into other UI / off-screen. Granularity is one button width: e.g. -100 vs -110 may behave the same, then -120 drops one column. (Claude code Opus 4.7). (Base AdvCiv value: 0) -->
SAS_MAIN_UI_PLOT_LIST_WIDTH_ADJ = -120

# <!-- custom: What the Great General bar's text shows: 0 = no text; 1 = stored / threshold experience, such as "9 / 29"; 2 = base AdvCiv's experience still needed, such as "20"; 3 = both, such as "9 / 29 (20)".
# The bar's width follows the text, base AdvCiv's for 0 and 2. (Claude code Opus 5.5) -->
SAS_MAIN_UI_GG_BAR_TEXT = 1

# <!-- custom: The Military Advisor tab a click on the Great General bar opens: 0 = Summary, 1 = Map, 2 = Battles, 3 = Composition.
# Battles by default, the fights that earn the experience, as the advisor's own button and F5 already open it on its last tab, which starts as Map (the user, 2026-11-21). (Claude code Opus 5.5) -->
SAS_MAIN_UI_GG_BAR_CLICK_TAB = 2

# <!-- custom: map-view commerce block anchor side: 1 = anchor to InterfaceTopRight, 0 = anchor to InterfaceTopLeft. (GPT-5.3-Codex)
# In map view, 1 now anchors to where advisors leave the scoreboard its space, the Technology Advisor's own while it is open, so the sliders line up with the scoreboard. (Claude code Opus 5.5) -->
SAS_MAIN_UI_MAP_COMMERCE_ANCHOR_RIGHT = 1

# <!-- custom: horizontal offset for the map-view commerce block anchor. (GPT-5.3-Codex)
# Was 178 from InterfaceTopRight, which kept the sliders clear of the Technology Advisor at 1920 px but far right of the scoreboard; now from the anchor above, a few px right of the advisors' edge, as the scoreboard's war dots start about 6 px right of it. (Claude code Opus 5.5) -->
SAS_MAIN_UI_MAP_COMMERCE_RIGHT_X_OFFSET = 6

# <!-- custom: vertical offset for the same map-view commerce block anchor; negative moves up, positive moves down. (GPT-5.3-Codex) -->
SAS_MAIN_UI_MAP_COMMERCE_RIGHT_Y_OFFSET = 12

SAS_MAIN_UI_CITY_COMMERCE_ANCHOR_RIGHT = 0

# <!-- custom: horizontal offset for the same commerce block while city screen is open; lets map view and city screen use separate positions. (GPT-5.3-Codex) -->
SAS_MAIN_UI_CITY_COMMERCE_RIGHT_X_OFFSET = 14

# <!-- custom: vertical offset for the same commerce block while city screen is open; negative moves up, positive moves down. (GPT-5.3-Codex) -->
SAS_MAIN_UI_CITY_COMMERCE_RIGHT_Y_OFFSET = 12


# <!-- custom: The other settings only Python reads, moved from GlobalDefines_advciv_sas.xml in their XML order: the Sevopedia, the advisors, the scoreboard and map generation among others.
# Those SASLiveDefineOverrides.txt may change during play, such as the font sizes, and those our tooling or CI reads from the XML, such as the movie switches in define_values.py, stay there. (Claude code Opus 5.5) -->
# <!-- custom: city billboard scale multiplier percent per SAS_UI_FONT_BODY level (1..4).
# 100 = no change from base AdvCiv values.
# Applied on game load by SASBillboardScale.py to CIV4DetailManager.xml.
# Note: as of now increased from 100 to 120 at font 2 so it is more readable. (Claude code Opus 4.6) -->
SAS_BILLBOARD_SCALE_PCT_FONT_1 = 100

SAS_BILLBOARD_SCALE_PCT_FONT_2 = 120

SAS_BILLBOARD_SCALE_PCT_FONT_3 = 140

SAS_BILLBOARD_SCALE_PCT_FONT_4 = 160


# <!-- custom: disable the Sevopedia Leader custom item-list width when screen width is at or above this threshold (>=).
# Set to <=0 to keep custom width always enabled. (GPT-5.3-Codex + ChatGPT-5.6-Sol + GPT-5.6-Sol).
# This is because at higher resolutions we have enough width to accommodate an enlarged AI Personality Panel, so we don't need to reduce width of the item bar anymore.
# Note: AI Personality panel is still expanded when text is upscaled (so it is not cramped) regardless of this item bar setting -->
SAS_SEVO_LEADER_ITEMS_FULL_MIN_WIDTH = 2560

# <!-- custom: Sevopedia Leader item-list width by SAS_UI_FONT_LABEL (1..4).
# For upscaled fonts we reclaim width from the leader item list and use it to enlarge/rebalance Leader AI panel columns.
# <=0 falls back to default item width. (GPT-5.3-Codex) -->
SAS_SEVO_LEADER_ITEMS_WIDTH_FONT_1 = 230

SAS_SEVO_LEADER_ITEMS_WIDTH_FONT_2 = 230

SAS_SEVO_LEADER_ITEMS_WIDTH_FONT_3 = 200

SAS_SEVO_LEADER_ITEMS_WIDTH_FONT_4 = 40


# <!-- custom: Sevopedia Game Speed chart first-column width by SAS_UI_FONT_LABEL (1..4).
# Lower values free more room for the speed-value columns when text is upscaled. (GPT-5.4) -->
SAS_SEVO_SPEED_FIELD_COL_WIDTH_FONT_1 = 180

SAS_SEVO_SPEED_FIELD_COL_WIDTH_FONT_2 = 180

SAS_SEVO_SPEED_FIELD_COL_WIDTH_FONT_3 = 150

SAS_SEVO_SPEED_FIELD_COL_WIDTH_FONT_4 = 80

# <!-- custom: disable first-column width reduction for Sevopedia Game Speed chart when screen width is >= this threshold; <=0 keeps reduced width always enabled. (GPT-5.4) -->
SAS_SEVO_SPEED_FIELD_FULL_MIN_WIDTH = 2560

# <!-- custom: non-reduced first-column width used at/above the threshold above; this restores a roomier label column on high resolutions. (GPT-5.4) -->
SAS_SEVO_SPEED_FIELD_FULL_COL_WIDTH = 260


# <!-- custom: scoreboard fast-scroll step.
# The normal + / - buttons move one row; the fast + / - buttons move this many rows per click, with offset clamped to the first/last valid slice.
# Base AdvCiv's scoreboard had no row limit or scrolling, so with 48 civilizations it ran up over the turn counter. See KI#134.2. (Claude code Opus 4.7 + ChatGPT-5.5 + GPT-5.5 + Claude code Opus 5.5) -->
SAS_SCOREBOARD_SCROLL_FAST_INCR = 5

# <!-- custom: scoreboard background default style; this sets the default background at each save load / new game: 0 = HUD_HELP (vanilla scoreboard panel, the shipped default), 1 = SOLID (most opaque, darkest), 2 = MAIN (plain panel), 3 = MAIN_BLACK50 (dark translucent), 4 = MAIN_BLACK25 (light translucent), 5 = EMPTY (no visible background, text drawn over the map).
# These indices mirror the aScoreBgStyleLevels list in CvMainInterface.py; keep both in sync if styles are added or reordered.
# Keep at 0 to preserve the vanilla look. (Claude code Opus 4.7) -->
SAS_SCOREBOARD_BG_DEFAULT_STYLE = 0

# <!-- custom: scoreboard lock-hover default state.
# 0 = expanded columns appear only while hovering the scoreboard; 1 = start each new game / loaded save with lock-hover enabled so expanded columns stay visible until manually toggled off.
# This only sets the initial state; the in-game lock button still toggles it normally. (ChatGPT-5.5) -->
SAS_SCOREBOARD_LOCK_HOVER_DEFAULT_ON = 1


# <!-- custom: 1 = on the map too, fit the scoreboard to the space advisors leave it, shortening leader names as beside an open advisor, so it keeps the same width whether a standard advisor is open or not and lines up with the commerce sliders; 0 = keep its full width on the map, with whole names.
# The Technology Advisor still gives its own space, narrower below 2560 px, and only names are cut, not columns. See KI#1103.2. (Claude code Opus 5.5) -->
SAS_SCOREBOARD_MAP_FIT_ADVISOR_SPACE_ON = 1

# <!-- custom: commerce sliders second (Min/Max) + + and - - pair step size (e.g., setting it to 50 makes it require 2 clicks to go from 0% to 100% (0->50->100) and vice versa for - -).
# Keep in [1,100].
# Base AdvCiv value: 100. (Claude code Opus 4.7) -->
SAS_COMMERCE_SLIDERS_FAST_INCR_PCT = 50

# <!-- custom: Where the map view shows each commerce's per-turn rate: 1 = in green beside its slider, as base AdvCiv does; 2 = in one compact row below the sliders, as SAS did when Min/Max buttons were on; 3 = both.
# Where the rates do not fit beside the sliders, as with the Technology Advisor open at 1920 px, they show below instead. (Claude code Opus 5.5) -->
SAS_COMMERCE_SLIDERS_RATE_SHOW = 1

# <!-- custom: The commerce sliders' background style at each save load / new game, cycled in game by its button (placed by SAS_COMMERCE_SLIDERS_BG_BUTTON_POS); the levels are SAS_SCOREBOARD_BG_DEFAULT_STYLE's, from 0 = HUD_HELP to 5 = EMPTY (no background, as before it existed).
# The scoreboard already had a background, while the slider text over the map had none and was hard to read, so the sliders got one too.
# The blue PANEL_STYLE_MAIN (2) chosen first (the user, 2026-11-20) hid the map under it; the default is now the scoreboard's own, HUD_HELP (0), so both read alike, and it stays a setting apart from SAS_SCOREBOARD_BG_DEFAULT_STYLE so each can be tuned (the user, 2026-11-21, Civ4ScreenShot0263). (Claude code Opus 5.5) -->
SAS_COMMERCE_SLIDERS_BG_DEFAULT_STYLE = 0

# <!-- custom: Where the commerce sliders' background style button sits: 0 = the panel's bottom-right, 1 = left of the scoreboard's buttons, 2 = left of the advisor buttons, just above the sliders; -1 = no button, the background then staying at SAS_COMMERCE_SLIDERS_BG_DEFAULT_STYLE's style (the user, 2026-11-21).
# At the panel's bottom-right it stood out over the map (the user, 2026-11-21). (Claude code Opus 5.5) -->
SAS_COMMERCE_SLIDERS_BG_BUTTON_POS = 2


# <!-- custom: Tech Chooser (i.e. Technology Advisor) low-res scoreboard swap threshold (in pixels).
# <= 0: hard disable; > 0: if current screen width is below this threshold, Tech Chooser uses the alternate low-res scoreboard margin below to gain tree width (more columns).
# A very high value like 9999 effectively always applies on current displays.
# Example: a value of 2560 means the right space alternate value applies for widths below 2560*1440 (i.e. 1440p) (e.g., for 1920*1080 (i.e. 1080p)). (GPT-5.3-Codex) -->
SAS_TECH_UI_SCOREBOARD_SWAP_MAX_WIDTH = 2560

# <!-- custom: Tech Chooser alternate right-side reserved space for scoreboard when low-res swap is active. Lower value => wider tech tree and more chance to fit one extra column at low resolution. Higher value => preserves more scoreboard/map area. This is mainly useful on lower resolutions where reclaiming some scoreboard space can make one more tech-tree column visible. Use 0 for maximum squeeze during low-res mode. (GPT-5.3-Codex); for example at 1080p a value of 206 allows to show exactly one more technology advisor column.
# With right-anchored map sliders, the strip still keeps enough room for their percentage and ordinary plus and minus buttons. (GPT-6.2-Sol) -->
SAS_TECH_UI_LOW_RES_SCOREBOARD_RIGHT_SPACE = 206

# <!-- custom: optional low-res top-space replacement paired with the low-res width swap; useful to keep map-view advisor buttons accessible when Tech Chooser is widened. (GPT-5.3-Codex) -->
SAS_TECH_UI_LOW_RES_TECH_BAR_TOP_SPACE = 52

# <!-- custom: Foreign Advisor Glance tab: number of rival columns shown per page.
# Page size 16 fits worldsize Huge and displays fine at 1080p, and suits worldsize SAS48 with 3 pages at 1080p. See KI#134. (Claude code Opus 4.7) -->
SAS_FOREIGN_UI_GLANCE_MAX_PLAYERS_PER_PAGE = 16

# <!-- custom: Foreign Advisor Espionage tab: switch the target-player list to compact single-line rows when met rivals are above this value.
# A value of 17 keeps the normal two-line layout for standard 18-player games, but compacts 18+ known rivals for SAS24/SAS48-style games.
# Set to 0 to always use compact rows.
# Base AdvCiv's two-line rows crowded into each other with 48 civilizations. See KI#134.5. (GPT-5.5-Thinking + GPT-5.5? + Claude code Opus 5.5) -->
SAS_FOREIGN_UI_ESP_COMPACT_ROWS_THRESH = 17


# <!-- custom: Zero-based position of the Military Advisor tab shown on its first opening in a Civ4 session: 0 is the first tab (as of now Summary), then add 1 for each following tab (as of now Map is one tab after Summary, so Map = 1). Map is the most useful initial view for locating and reviewing current units; subsequent close/reopen retains the last selected tab. See KI#129 (Update). (GPT-5.5 + GPT-5.6-Sol) -->
SAS_MILIT_UI_DEFAULT_TAB = 1

# <!-- custom: enable icons (images) for unit-combat and unit rows in Military Advisor). (GPT-5.3-Codex) -->
SAS_MILIT_UI_UNIT_COMBATS_UNITS_ICONS = 1

# <!-- custom: base inline icon size (px) for Military Advisor (F5) unit list rows. (GPT-5.3-Codex) -->
SAS_MILIT_UI_BASE_ICON_SIZE = 24

# <!-- custom: if current game resolution height is >= this value, Military Advisor uses the high-res inline icon size below. <=0 disables the high-res switch. (GPT-5.3-Codex) -->
SAS_MILIT_UI_HI_RES_ICON_MIN_HEIGHT = 1440

# <!-- custom: high-res inline icon size (px) used by Military Advisor when resolution height reaches the threshold above. (GPT-5.3-Codex) -->
SAS_MILIT_UI_HI_RES_ICON_SIZE = 32

# <!-- custom: max saved battle-history rows per player for Military Advisor Battles tab.
# 0 disables recording; -1 keeps all future entries. (GPT-5.5) -->
SAS_MILIT_UI_BATTLE_HISTORY_MAX_ENTRIES = -1

# <!-- custom: show compact hill-or-peak/terrain/feature context columns in the Military Advisor Battles tab.
# Battle history always stores this snapshot so changing the define after a Civ4 restart can display already-recorded rows. (GPT-5.5) -->
SAS_MILIT_UI_BATTLE_PLOT_CONTEXT_ON = 1


# <!-- custom: show/hide score-related legend links (Info Screen Score Tab and Sevopedia Leader AI legend). (GPT-5.3-Codex) -->
SAS_SHOW_LEGEND_LINK = 1

# <!-- custom: enable selected advisors to inspect the current active player's alive vassals outside debug mode; see SASUtils.py for behavior details. (GPT-5.5) -->
SAS_ADVISOR_ALLOW_VASSAL_PERSPECTIVE = 1


# <!-- custom: enable/disable to show trait icons (chars) before trait names in the Sevopedia leader Traits section.
# 0 is disabled (no icons), any other value e.g. 1 is enabled (shows icons like in the Traits category). -->
SAS_SEVO_LEADER_TRAITS_SHOW_ICONS = 1

# <!-- custom: Sevopedia Leader attitude button style; 1 = show emojis on all attitude buttons (selected/unselected sizes differ in Python), 0 = text labels with uppercase selected fallback (FU/AN/CA/PL/FR). (GPT-5.3-Codex) -->
SAS_SEVO_LEADER_ATTITUDE_EMOJI_ON = 1


# <!-- custom: Sevopedia trait combinations: 0 = show only existing pairs, 1 = include zero-count pairs. (GPT-5.2-Codex) -->
SAS_SEVO_TRAIT_SHOW_ZERO_PAIRS = 1

# <!-- custom: Sevopedia trait left table: 0 = only existing pairs, 1 = include zero-count pairs. (GPT-5.2-Codex) -->
SAS_SEVO_TRAIT_SHOW_ZERO_PAIRS_LEFT = 1


# <!-- custom: change its value if you don't want to see AI information in the special abilities panel -->
SAS_SEVO_UNIT_SHOW_AI_INFORMATION = 1

SAS_SEVO_BONUS_SHOW_AI_INFORMATION = 1


# <!-- custom: show red X overlay on obsolete items in the Obsoletes panel (set to 0 to disable).
# Note new thinner RedX button generated by ChatGPT 5.2 thanks a lot! -->
SAS_SEVO_TECH_SHOW_OBSOLETES_RED_X = 1


# <!-- custom: enable the optional Sevopedia search clickable special-character ()_/*+-=[]'#&~;,:!?.@\|<> keyboard and a KEYS header link.
# Does not disable direct keyboard typing support.
# Disabled by default because punctuation is rarely useful in Civ4 item-name searches and the header link adds visual noise. (GPT-5.5) -->
SAS_SEVO_SEARCH_SPECIAL_CHAR_LINKS_ON = 0


# <!-- custom: in Sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.) instead of one long alphabetical list.
# The earlier implementation was derived from RFC Dawn of Civilization and adapted with ChatGPT 5.2. (ChatGPT-5.6-Sol) -->
SAS_SEVO_CIVICS_GROUP_BY_CIVIC_TYPES = 1

SAS_SEVO_TECHS_GROUP_BY_ERA = 1

SAS_SEVO_BLDGS_GROUP_BY_ERA = 1

SAS_SEVO_UNITS_GROUP_BY_ERA = 1

SAS_SEVO_CORPORATIONS_GROUP_BY_ERA = 1

SAS_SEVO_RELIGIONS_GROUP_BY_ERA = 1

SAS_SEVO_PROJECTS_GROUP_BY_ERA = 1

# <!-- custom: Routes take the earliest era of the Builds that create them. (Claude code Opus 5.5) -->
SAS_SEVO_ROUTES_GROUP_BY_ERA = 1

SAS_SEVO_SPECIALISTS_GROUP_BY_TYPE = 1

SAS_SEVO_BONUSES_GROUP_BY_IMPROVE = 1

SAS_SEVO_IMPROVES_GROUP_BY_TERRAIN = 1

SAS_SEVO_BUILDS_GROUP_BY_TYPE = 1

SAS_SEVO_TERRAINS_GROUP_BY_LAND_WATER = 1

SAS_SEVO_FEATURES_GROUP_BY_LAND_WATER = 1

SAS_SEVO_CIVS_GROUP_BY_ARTSTYLE = 1

SAS_SEVO_LEADERS_GROUP_BY_CIV = 1


SAS_SEVO_MUSIC_LEADER_INTRO_PEACE_1ST_ONLY = 1

SAS_SEVO_MUSIC_LEADER_PEACE_1ST_ONLY = 1

SAS_SEVO_MUSIC_LEADER_INTRO_WAR_1ST_ONLY = 1

SAS_SEVO_MUSIC_LEADER_WAR_1ST_ONLY = 1

# <!-- custom: set the Sevopedia music item list width in the contents view. (GPT-5.2-Codex).
# Update: increase to support upscaled text in a simple way (not much to display so we can be aggressive; the longest AMB_FINAL_FRONTIER row now barely fits so this is in fact conservative) (was 800) -->
SAS_SEVO_MUSIC_ITEMS_WIDTH = 1000


# <!-- custom: For modders: set where GOODY and AIFreeTechs/FreeTechs rows resume in the Sevopedia handicap chart; default appends them at the end (excluding those rows).
# Based on Middle-earth Platypedia CvHandicapInfo approach. (GPT-5.2-Codex) -->
SAS_SEVO_HANDICAP_CHART_ANCHOR_FIELD = 'iUnownedWaterTilesPerBarbarianUnit'

# <!-- custom: set the handicap chart table fill percent for the columns area; 100 uses full width, lower leaves empty space on the right for tighter reading (GPT-5.2-Codex).
# Update: make larger to accommodate font size 4 (was 65).
# Update 2: larger to accomodate the 2 new Handicaps at font size 4 (as of now Rookie and Deity+ (was 80)) -->
SAS_SEVO_HANDICAP_CHART_FILL_PCT = 90

# <!-- custom: enable (1) / disable (0) to add an icon column for the left-side field labels in the handicap chart table. (GPT-5.2-Codex) -->
SAS_SEVO_HANDICAP_CHART_HEADER_ICONS = 1

# <!-- custom: set the game speed chart table fill percent for the columns area; 100 uses full width, lower leaves empty space on the right for tighter reading. (GPT-5.2-Codex). -->
SAS_SEVO_SPEED_CHART_FILL_PCT = 100

SAS_SEVO_SPEED_CHART_HEADER_ICONS = 1

# <!-- custom: set the world size chart table fill percent for the columns area; 100 uses full width, lower leaves empty space on the right for tighter reading. (GPT-5.2-Codex) -->
SAS_SEVO_WORLD_CHART_FILL_PCT = 85

SAS_SEVO_WORLD_CHART_HEADER_ICONS = 1

SAS_SEVO_ERA_CHART_FILL_PCT = 100

SAS_SEVO_ERA_CHART_HEADER_ICONS = 1

SAS_SEVO_ERA_CHART_SHOW_ERA_BUTTONS = 1


# <!-- custom: show the Timeline panel "Log" button; click to write the visible (spoiler-filtered) timeline lines to PythonDbg.log. -->
SAS_INFO_UI_TIMELINE_LOG_BUTTON_ON = 1

# <!-- custom: show the Military Advisor Battles tab "Log" button; click to write the current battle history rows to PythonDbg.log. (Claude code Opus 4.7) -->
SAS_MILIT_UI_BATTLES_LOG_BUTTON_ON = 1

# <!-- custom: dev playground: show "STYLE: <name> (i/n)" + PREV/NEXT buttons in the Sevopedia expanded text overlay header to live-cycle through every PanelStyles enum value.
# Lets us pick a style for other tabs/screens (e.g. battles tab, score tab) and visualize it ingame instead of editing-recompiling-screenshotting one style at a time.
# The selection persists for the whole Civ4 session and applies across all pedia categories that show an expanded text panel (history/background, unit strategy, leader bio, etc.).
# 0 = off (default; restores PANEL_STYLE_MAIN and hides the cycle UI). -->
SAS_PEDIA_PANEL_STYLE_PLAYGROUND_ON = 1

# <!-- custom: Timeline tab cache: 0 = disable caching entirely (no cache state stored), 1 (recommended: faster performance) = reuse cached entries when valid. (GPT-5.2-Codex) -->
SAS_INFO_UI_TIMELINE_CACHE_ON = 1

# <!-- custom: Gridlines on the Info screen's graphs, about this many on each axis, at round turn numbers (x) and round values (y), or powers of 10 with the log scale; 0 turns that axis's off.
# Without them a line's height read the same whatever the top value, and a turn between the date labels had to be guessed (the user, 2026-11-21). (Claude code Opus 5.5) -->
SAS_INFO_UI_GRAPH_X_GRID_LINES = 10

SAS_INFO_UI_GRAPH_Y_GRID_LINES = 5

# <!-- custom: 1 lists each Greatest Civilizations ranking on the Timeline tab (a title row and one row per rank); 0 hides them there, for players who find them noise.
# They stay in the save and the replay either way, so turning it back on shows past rankings again (the user's idea, 2026-11-19).
# On by default: a ranking comes a few times a game, mostly early, while "X is the first to discover Y" rows come far more often. (Claude code Opus 5.5) -->
SAS_INFO_UI_TIMELINE_TOP_CIVS_ON = 1

# <!-- custom: widen the Info Screen Score Tab laterally only when visible players reach this threshold. (GPT-5.3-Codex) -->
SAS_INFO_UI_SCORE_MAX_RENDER_THRESH = 36


# <!-- custom: show the DLL's cached landHeavy/navalHeavy AI map-heaviness flags in Victory Screen > Settings near the other map information.
# This matches BBAI_GAME_SETTINGS and avoids requiring logs to verify the active classification. (GPT-5.5) -->
SAS_VICT_UI_SHOW_AI_MAP_HEAVINESS = 1

# <!-- custom: 1 also shows a vote source whose building stands but no longer votes, such as an Apostolic Palace late in a game, in the Victory screen's Resolutions and Members tabs, tagged (INACTIVE); 0 shows only the sources voting now, as before.
# It ships off: the game keeps only whether each resolution is in force now, not what an inactive source decided, so its section is mostly empty (2026-11-21, Civ4ScreenShot0383).
# It stays a switch for players who want every source listed, and for modmods whose sources turn on and off during a game. (Claude code Opus 5.5) -->
SAS_VICT_UI_SHOW_INACTIVE_VOTE_SOURCES = 0


# <!-- custom: 1 uses AdvCiv's standard TerrainGenerator adjustments: no guaranteed equatorial Grassland belt, slightly more and differently clustered Plains, Deserts biased toward Plains, and a tiny hills increase.
# 0 uses the retained BTS paths for those adjustments.
# This does not override terrain generators supplied by individual map scripts. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_TERRAIN_ON = 1

# <!-- custom: Default source-fractal width exponent.
# AdvCiv uses -1 so the DLL chooses for the map dimensions; BTS hardcoded 7.
# A map script that supplies fracXExp keeps its value. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_X_EXP = -1

# <!-- custom: Default source-fractal height exponent.
# AdvCiv uses -1 so the DLL chooses for the map dimensions; BTS hardcoded 6.
# A map script that supplies fracYExp keeps its value. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_Y_EXP = -1

# <!-- custom: Default landmass grain.
# Higher values produce more and smaller landmasses.
# Both BTS and AdvCiv use 2; explicit map-script continent_grain remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_CONTINENT_GRAIN = 2

# <!-- custom: Default grain for forced rift-water strips; -1 disables rifts.
# Both BTS and AdvCiv use 2; explicit map-script rift_grain remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_RIFT_GRAIN = 2

# <!-- custom: Default shared hills grain; Peaks use this value + 1.
# Higher values produce smaller highland patches.
# Both BTS and AdvCiv use 3; explicit map-script grain_amount remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_HILLS_GRAIN = 3

# <!-- custom: Default water percentage for shared FractalWorld plot generation before the selected sea-level adjustment.
# AdvCiv changed 78 to 77; use 78 for BTS.
# A map script that supplies its own water_percent keeps that value. (GPT-5.6-Sol) -->
SAS_MAPGEN_FRACTAL_DEFAULT_WATER_PCT = 77

# <!-- custom: 1 uses AdvCiv's coastal-Peak reduction in the shared FractalWorld and MultilayeredFractal generators: half the otherwise eligible coastal Peaks become Hills, while the Peak threshold is raised by 8/7 to compensate.
# 0 restores BTS's original Peak threshold and allows every eligible coastal Peak.
# A map script can still alter Peaks afterward. (GPT-5.6-Sol) -->
SAS_MAPGEN_COASTAL_PEAK_REDUCTION_ON = 1

# <!-- custom: 1 uses AdvCiv's shared latitude algorithm: DLL plot latitudes, less terrain-latitude variation, and the True Starts sparse-equator and coastal-temperate adjustments.
# 0 restores BTS row-based latitude and the original variation.
# Snow and Tundra thresholds are independently tunable below; explicit thresholds and getLatitudeAtPlot overrides supplied by map scripts remain independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_LATITUDE_TERRAIN_ON = 1


# <!-- custom: The shared TerrainGenerator inputs below apply only when a map script omits them.
# Latitude percentages are divided by 100.0 in Python 2.4. (GPT-5.6-Sol) -->
# <!-- custom: Approximate base Desert share before Climate adjustments and AdvCiv's terrain compensation. Both BTS and AdvCiv start from 32; for the BTS algorithm use 32 with SAS_MAPGEN_STANDARD_TERRAIN_ON=0. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_DESERT_PCT = 32

# <!-- custom: Approximate base Plains share. Both BTS and AdvCiv start from 18; the AdvCiv terrain algorithm then adds 2 and uses differently grained Plains fractals. Use 18 with SAS_MAPGEN_STANDARD_TERRAIN_ON=0 for BTS, or keep 18 with it enabled for current AdvCiv-SAS behavior. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_PLAINS_PCT = 18

# <!-- custom: Base grain for Desert, Plains, and latitude variation.
# Higher values produce smaller patches.
# Both BTS and AdvCiv use 4; WorldInfo TerrainGrainChange is added afterward, and explicit map-script grain_amount remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_TERRAIN_GRAIN = 4

# <!-- custom: Latitude below this percentage is guaranteed Grassland before Climate adjustment. The base is 10 in both BTS and AdvCiv. Use 10 with SAS_MAPGEN_STANDARD_TERRAIN_ON=0 for BTS; with it enabled, AdvCiv subtracts 10, so 10 removes the belt and 20 restores an effective 10% belt while retaining the other AdvCiv terrain changes. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_GRASS_LAT_PCT = 10

# <!-- custom: Lowest latitude where Desert may appear before Climate adjustment, on a 0 equator to 100 poles scale.
# Both BTS and AdvCiv use 20; lowering it permits Desert closer to the equator. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_DESERT_BOTTOM_LAT_PCT = 20

# <!-- custom: Upper latitude limit for Desert before Climate adjustment, on the same scale.
# Both BTS and AdvCiv use 50; raising it permits Desert farther toward the poles. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_DESERT_TOP_LAT_PCT = 50

# <!-- custom: Default Snow boundary before Climate adjustment, on the same scale. AdvCiv uses 78; BTS uses 70. A higher value confines Snow closer to the poles. For the full BTS latitude profile, use 70 with SAS_MAPGEN_LATITUDE_TERRAIN_ON=0. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_SNOW_LAT_PCT = 78

# <!-- custom: Default Tundra boundary before Climate adjustment, on the same scale. AdvCiv uses 64; BTS uses 60. A higher value confines Tundra closer to the poles. For the full BTS latitude profile, use 60 with SAS_MAPGEN_LATITUDE_TERRAIN_ON=0. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_TUNDRA_LAT_PCT = 64

# <!-- custom: Width of the FeatureGenerator's Jungle fractal acceptance band; higher values make more eligible plots receive Jungle.
# Both BTS and AdvCiv use 80; latitude, Climate, terrain eligibility, and map-script overrides still apply. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_JUNGLE_PCT = 80

# <!-- custom: Base Jungle grain; higher values produce smaller Jungle patches.
# Both BTS and AdvCiv use 5; WorldInfo FeatureGrainChange is added afterward, and explicit map-script jungle_grain remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_JUNGLE_GRAIN = 5

# <!-- custom: Base Forest grain; higher values produce smaller Forest patches.
# Both BTS and AdvCiv use 6; WorldInfo FeatureGrainChange is added afterward, and explicit map-script forest_grain remains independent. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_FOREST_GRAIN = 6

# <!-- custom: Default iForestPercent threshold for the shared FeatureGenerator; a lower value produces more Forest.
# AdvCiv uses 57 to compensate for reduced starting-position Forest normalization; use 60 for BTS.
# A map script that supplies its own threshold keeps that value. (GPT-5.6-Sol) -->
SAS_MAPGEN_STANDARD_FOREST_PCT = 57


# <!-- custom: Share of the FeatureGenerator's Marsh fractal that receives Marsh, as a percentage; unlike SAS_MAPGEN_STANDARD_FOREST_PCT, higher values mean more Marsh.
# Only flat Grassland without Jungle is eligible, so this is roughly the share of such plots that become Marsh. (Claude code Opus 5.5) -->
# <!-- custom: was 30; Marsh covered too much flat Grassland in test games, so about 17% less. (Claude code Opus 5.5) -->
SAS_MAPGEN_STANDARD_MARSH_PCT = 25

# <!-- custom: Base Marsh grain; higher values produce smaller Marsh patches.
# WorldInfo FeatureGrainChange is added afterward, as for Jungle and Forest. (Claude code Opus 5.5) -->
SAS_MAPGEN_STANDARD_MARSH_GRAIN = 6


# <!-- custom: 1 uses AdvCiv's randomized standard FeatureGenerator traversal, removing fixed coordinate-order bias for bNoAdjacent features such as Oasis.
# 0 restores BTS coordinate-order traversal.
# Custom map scripts that override feature generation retain their own behavior. (GPT-5.6-Sol) -->
SAS_MAPGEN_FEATURE_PLACEMENT_ORDER_ON = 1


# <!-- custom: Water.py mapscript has too many peak plots by default; this knob sets the kept peak percentage vs original (e.g., 25 = 25% of original peaks).
# The remainder stays under the script's normal non-peak logic (land/hills/water). (GPT-5.3-Codex) -->
SAS_WATER_MAP_PEAK_PCT_OF_BASE = 25

# <!-- custom: Earth2 staged starts by player count: below AFRICA_MIN_PLAYERS populate only Europe and Asia (base-like), from AFRICA_MIN_PLAYERS also populate Africa, and from FULL_WORLD_MIN_PLAYERS populate the whole world (notably America + Australia too). (GPT-5.3-Codex) -->
SAS_EARTH2_AFRICA_STARTS_MIN_PLAYERS = 16

SAS_EARTH2_WORLD_STARTS_MIN_PLAYERS = 32

# <!-- custom: Planet Generator map script world-size scaling percent.
# 40 means use 40% of selected WorldInfo grid size before script-specific spacing safety checks.
# Keep in [1,100]. (GPT-5.3-Codex) -->
SAS_PLANET_GENERATOR_GRID_PCT = 40

# <!-- custom: increase a bit as compared to planet generator, due to the abundance of water, snow/tundra, and desert, else players are a bit too crowded -->
SAS_PEIRCE_GRID_PCT = 50


# <!-- custom: Settings only Python reads that CI or our tooling had read from the XML, moved once those readers learned SASSessionTunables.py too: the scoreboard's autocenter default, the Military Advisor's and the World Changes history's defaults, the AI Personality Panel's switches and cache, FastSave's game-start and AI Auto Play stop saves, AI Auto Play's defaults and SASGameRecord's BUG string values. (Claude code Opus 5.5) -->
# <!-- custom: scoreboard scroll autocenter default state.
# 0 = keep the current scroll slice across redraws; 1 = start each new game / loaded save with autocenter enabled so overflowing scoreboards stay centered on the active player until manually toggled off.
# Manual scroll buttons also turn autocenter off.
# This only sets the initial state; the in-game autocenter button still toggles it normally. See KI#134.2. (ChatGPT-5.5 + Claude code Opus 5.5) -->
SAS_SCOREBOARD_AUTOCENTER_DEFAULT_ON = 1


# <!-- custom: Optional independently sortable X/Y columns in the Military Advisor Battles tab.
# Default 1 shows both independently sortable axes using already-recorded, observer-visible coordinates.
# Set 0 to preserve scarce horizontal space at 1080p, especially with enlarged text; coordinates remain available on the Plot icon hover.
# This changes presentation only and requires a Civ4 restart because advisor settings are cached. (GPT-6.1-Sol) -->
SAS_MILIT_UI_BATTLE_XY_ON = 1


# <!-- custom: master toggle for Sevopedia Leader AI personality feature; 0 disables both cache computation and panel/legend display, 1 enables them. (GPT-5.3-Codex) -->
SAS_SEVO_LEADER_AI_ON = 1


# <!-- custom: Long_Comments_XML.txt #132 -->
# <!-- custom: Set to 1 to load the committed pre-dumped module (SevoPediaLeaderCachePredumped.py).
# Set to 0 to compute the cache at runtime instead.
# The old manual runtime regeneration path is no longer normally needed: CI/local checks now verify that the committed predump still matches Leader XML and shared Python AIP display logic, and the Refresh AIP predump cache GitHub workflow can run aip_predump_values.py write mode and open a bot PR when the generated file actually changes.
# Local modders can still run the script's write mode directly outside Civ4.
# Manual fallback remains: set this to 0 and SAS_SEVO_LEADER_AI_CACHE_DUMP_TO_LOG to 1, open the Leaders / AI Personality panel once, copy the PythonDbg.log cache block, then restore defaults. (ChatGPT-5.5) -->
SAS_SEVO_LEADER_AI_CACHE_USE_PREDUMPED = 1

# <!-- custom: Runtime cache logging only: 0 = don't dump to log, 1 = dump a PythonDbg.log block for the old manual predump refresh path.
# Normally leave disabled; the GitHub refresh bot or local aip_predump_values.py write mode can refresh the predump outside Civ4 without this log dump. (ChatGPT-5.5); Long_Comments_XML.txt #192 -->
SAS_SEVO_LEADER_AI_CACHE_DUMP_TO_LOG = 0

# <!-- custom: use this to show instead of abbreviated or custom named labels the key or suffixes instead (shrinked if too long), for example "MaxWarRand", instead of "T.W. Likely"; Long_Comments_XML.txt #193 -->
SAS_SEVO_LEADER_AI_RAW_XML_NAMES_ON = 0

# <!-- custom: enable/disable to show emojis (like ⚔️, 🏆, 💰) in the AI personality panel; Long_Comments_XML.txt #194 -->
SAS_SEVO_LEADER_AI_EMOJI_ON = 1


# <!-- custom: Reviewed BUG strings (currently Scores__DisplayOrder) use session-local REDACTED_0001-style IDs by default, preserving value equality/changes without logging the text.
# 1 records their exact configured values instead; editable strings may contain personal text, so enable deliberately before sharing logs.
# Other unreviewed BUG strings remain excluded; read failures remain UNREADABLE rather than receiving an ID.
# Inactive while the recorder is disabled; cached on first use, so restart Civ4 after changing this setting. (GPT-6.1-Sol) -->
SAS_SGR_BUG_STRING_VALS_ON = 0


# <!-- custom: Show every observer-permitted raw event as a separate row in the World Advisor Changes tab when 1.
# Default 0 keeps eligible repeated WorldBuilder scalar edits compact: while adjusting a spinner with its arrows, intermediate values usually add visual noise compared with the first Before and final After.
# These setters apply immediately; the compact view does not claim the edits were uncommitted drafts.
# Saved history, SASGameRecord and the LOG export always retain the applied steps regardless of this UI preference.
# Cached on the first Changes-tab draw; restart Civ4 after changing it. (GPT-6.1-Sol) -->
SAS_WORLD_CHANGES_SHOW_INTERMEDIATE_ON = 0

# <!-- custom: Show eligible cancelled Changes-table rows when 1; default 0 omits them from the summary.
# These are WB scalar runs whose first/final values match, and matching Advanced Start unit/population/building ADD-then-REMOVE pairs when identities, quoted costs and point/gold balances match exactly.
# Nested refund pairs can expose an earlier pair; hidden/omitted rows, other actions and WB edits are barriers.
# This summarizes recorded value/count and budget effects, not all gameplay side effects (e.g. revealed plots, food or city counters).
# City deletion, culture, technology, visibility and map replacements remain detailed; SHOW_INTERMEDIATE overrides this filter, and saved history/SGR/LOG always retain the raw events.
# Cached on first compact Changes-tab draw; restart Civ4 after changing it. (GPT-6.1-Sol) -->
SAS_WORLD_CHANGES_SHOW_CANCELLED_ON = 0


# <!-- custom: Optional fast-save convenience: create ordinary SAVEGAME_NORMAL files in My Games/Beyond the Sword/Saves/single.
# These are deliberately separate from Civ4's rotating Autosaves folder and BUG AutoSave UI/options.
# Each switch is independent.
# Game-start and game-end fast saves also apply to ordinary single-player games; the autoplay-stop fast save only matters when AI Auto Play is used.
# Set any switch to 0 when that fast save is not wanted. (ChatGPT-5.6-Sol) -->
SAS_FAST_SAVE_GAME_START_ON = 1


SAS_FAST_SAVE_AUTOPLAY_STOP_ON = 1

# <!-- custom: Scale the AI Auto Play popup default to the selected game speed's configured total number of turns, plus 1 for the existing SASGameRecord interval convention.
# E.g. Normal 500 -> 501, Marathon 1000 -> 1001.
# 1 enables this dynamic default; 0 uses SAS_AIAUTOPLAY_DEFAULT_T_UNSCALED_GS below. (ChatGPT-5.6-Sol) -->
SAS_AIAUTOPLAY_DEFAULT_SCALE_BY_SPEED_ON = 1

# <!-- custom: Manual unscaled number shown in the AI Auto Play popup when SAS_AIAUTOPLAY_DEFAULT_SCALE_BY_SPEED_ON is 0.
# It is intentionally literal rather than adjusted for game speed. (ChatGPT-5.6-Sol) -->
SAS_AIAUTOPLAY_DEFAULT_T_UNSCALED_GS = 501


# <!-- custom: The screens that only inform, moved from GlobalDefines_advciv_sas.xml once toggle_dev_diagnostics.py could switch them here: each is 1 for players and 0 during development and agent runs, which click through none of them. (Claude code Opus 5.5) -->
# <!-- custom: 1 shows the Dawn of Man screen at a game's start, as in base AdvCiv; 0 skips it, for hands-free runs and agents that start many games.
# Autoplay already passes it, but a game started or loaded for a quick look still waited on its Continue button.
# Ships as 1; LLM_Helpers/diagnostics/toggle_dev_diagnostics.py on sets 0 locally. (Claude Code Opus 5.5) -->
SAS_UI_DAWN_OF_MAN_ON = 1

# <!-- custom: 1 shows the tech splash when a tech is acquired, as in base AdvCiv; 0 skips it.
# The event log still says "You have discovered ...".
# At turn 148 of a pilot playthrough (2026-11-13), a tech bought from an AI put its splash on display at once and the window waited on its Continue button; agents and unattended runs only click through these screens.
# Ships as 1; LLM_Helpers/diagnostics/toggle_dev_diagnostics.py on sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_TECH_SPLASH_ON = 1

# <!-- custom: 1 plays the movie shown when a player enters a new era, as in base AdvCiv; 0 skips it.
# Ships as 1; the development toggle sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_ERA_MOVIE_ON = 1

# <!-- custom: 1 plays a wonder's movie when the player completes it, as in base AdvCiv; 0 skips it.
# Each kind of movie has its own switch, so a player can keep some.
# Ships as 1; the development toggle sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_WONDER_MOVIE_ON = 1

# <!-- custom: 1 plays the movie shown when the player founds a religion, as in base AdvCiv; 0 skips it.
# Ships as 1; the development toggle sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_RELIGION_MOVIE_ON = 1

# <!-- custom: 1 plays a project's movie when the player completes it, as in base AdvCiv; 0 skips it.
# Ships as 1; the development toggle sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_PROJECT_MOVIE_ON = 1

# <!-- custom: 1 shows the Greatest Civilizations screen when it comes, as in base AdvCiv; 0 skips it.
# Either way its ranking is recorded as a Timeline row in the save, so nothing is lost; at turn 82 of the 2026-11-19 validation run it waited on its Exit button in an agent game.
# Ships as 1; LLM_Helpers/diagnostics/toggle_dev_diagnostics.py on sets 0 locally. (Claude code Opus 5.5) -->
SAS_UI_TOP_CIVS_ON = 1
