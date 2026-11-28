#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Shipped GlobalDefines values that workflow checks require and toggle_dev_diagnostics.py restores with "off", and the development values its "on" sets.
#
# This module runs outside Civ4, through GitHub Actions or a local Python 3 command.
# It does not need Civ4 Python 2.4 compatibility.

# <!-- custom: These lists lived in sas_game_record_log.py, runtime_status.py and hands_free_defaults.py, and the toggle kept a second copy of the values it switches.
# Holding them in one data module lets the checks and the toggle share one source without the toggle loading check scripts.
# It sits beside the toggle rather than in .github/workflows/lib: these values serve local development and its future helpers more than CI, which checks only the shipped half.
# Change a value here only: .github/workflows/build/source/shared_define_values.py fails when another script writes one of these names with a number. (Claude code Opus 5.5) -->


EXPECTED_GAME_RECORD_DEFAULTS = {
	# <!-- custom: Since SASGameRecord revision 214 (SGR214) the master and the level both ship at 0, as BBAI's master and categories do; until then SAS_SGR_LOG was both. (Claude code Opus 5.5) -->
	"SAS_SGR_LOG_ON": 0,
	"SAS_SGR_LOG": 0,
	# <!-- custom: Ship action tracing ready for deliberately enabled records while the recorder master stays off; catch accidental staging of an actions-off test override. (GPT-6.1-Sol) -->
	"SAS_SGR_ACTION_TRACE_ON": 1,
	# <!-- custom: Preserve the independent caption-text opt-in when shipping the annotation observer; local test values remain unstaged. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	"SAS_SGR_MAP_ANNOTATION_TEXT_ON": 0,
	# <!-- custom: Player-authored multiplayer chat bodies are private/free-form text; metadata remains available, but exact bodies must ship opt-in. (ChatGPT-5.6-Sol) -->
	"SAS_SGR_CHAT_ALL_TEXT_ON": 0,
	"SAS_SGR_CHAT_TEAM_TEXT_ON": 0,
	"SAS_SGR_CHAT_DIRECT_TEXT_ON": 0,
	# <!-- custom: Saved Changes history is independent of the recorder master; ship applied WorldBuilder script-text capture enabled as documented, while allowing local opt-out tests. (GPT-6.1-Sol) -->
	"SAS_WORLD_CHANGES_SCRIPT_TEXT_ON": 1,
	# <!-- custom: Keep richer support context opt-in; catch hardware/path/process and private/network INI test settings accidentally staged for shipping. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
	"SAS_SGR_SYSTEM_CONTEXT_LVL": 2,
	"SAS_SGR_HARDWARE_IDENTITY_ON": 0,
	"SAS_SGR_EXACT_PATHS_ON": 0,
	"SAS_SGR_PROCESS_CONTEXT_ON": 0,
	"SAS_SGR_BUG_STRING_VALS_ON": 0,
	"SAS_SGR_INI_PRIVATE_VALS_ON": 0,
	"SAS_SGR_INI_NETWORK_VALS_ON": 0,
}

EXPECTED_RUNTIME_DEFAULTS = {
	"SAS_RUNTIME_STATUS_ON": 0,
	"SAS_RUNTIME_PLAYER_TURN_LIVE_THRESHOLD_MS": 3000,
	"SAS_RUNTIME_PLAYER_TURN_LIVE_REFRESH_MS": 3000,
	"SAS_RUNTIME_SOURCE_WATCH_ON": 0,
	"SAS_RUNTIME_SCREENSHOT_WATCH_ON": 0,
}

EXPECTED_HANDS_FREE_VALUES = {
	"SAS_UI_DAWN_OF_MAN_ON": 1,
	"SAS_UI_TECH_SPLASH_ON": 1,
	"SAS_UI_ERA_MOVIE_ON": 1,
	"SAS_UI_WONDER_MOVIE_ON": 1,
	"SAS_UI_RELIGION_MOVIE_ON": 1,
	"SAS_UI_PROJECT_MOVIE_ON": 1,
	"SAS_UI_TOP_CIVS_ON": 1,
	"SAS_AIAUTOPLAY_DISMISS_INFO_POPUPS_ON": 1,
	"SAS_AIAUTOPLAY_DEFAULT_SCALE_BY_SPEED_ON": 1,
	"SAS_FAST_SAVE_GAME_START_ON": 1,
	"SAS_FAST_SAVE_GAME_END_ON": 1,
	"SAS_FAST_SAVE_AUTOPLAY_STOP_ON": 1,
	"SAS_SCOREBOARD_AUTOCENTER_DEFAULT_ON": 1,
	"SAS_ASSERT_SILENT_ACTION": 1,
	# <!-- custom: Not hands-free but checked the same way: SASPilotClient.py opens SASPilotConsole for every client unless a local edit sets 0 (2026-11-27). (Claude code Opus 5.5) -->
	"SAS_PILOT_CONSOLE_ON": 1,
}

SHIPPED_VALUES = {**EXPECTED_GAME_RECORD_DEFAULTS, **EXPECTED_RUNTIME_DEFAULTS, **EXPECTED_HANDS_FREE_VALUES}

# <!-- custom: The shipped values above that live in Assets/Python/SASSessionTunables.py rather than the XML, as only Python reads them (KI#128.11); the checks read these names from there and the rest from the XML.
# toggle_dev_diagnostics.py switches the ones in DEVELOPMENT_VALUES in whichever file holds them; it first edited the XML only, which had kept the seven informing screens' switches, such as SAS_UI_DAWN_OF_MAN_ON, there. (Claude code Opus 5.5) -->
SESSION_TUNABLE_NAMES = ("SAS_SGR_BUG_STRING_VALS_ON", "SAS_AIAUTOPLAY_DEFAULT_SCALE_BY_SPEED_ON", "SAS_FAST_SAVE_GAME_START_ON", "SAS_FAST_SAVE_AUTOPLAY_STOP_ON", "SAS_SCOREBOARD_AUTOCENTER_DEFAULT_ON")
# <!-- custom: The informing screens' switches, which the toggle sets to 0 for development, in the same file. (Claude code Opus 5.5) -->
SESSION_TUNABLE_NAMES += ("SAS_UI_DAWN_OF_MAN_ON", "SAS_UI_TECH_SPLASH_ON", "SAS_UI_ERA_MOVIE_ON", "SAS_UI_WONDER_MOVIE_ON", "SAS_UI_RELIGION_MOVIE_ON", "SAS_UI_PROJECT_MOVIE_ON", "SAS_UI_TOP_CIVS_ON")
# <!-- custom: SASPilot's console switch, read by SASPilotClient.py through the toggle's reader (2026-11-27). (Claude code Opus 5.5) -->
SESSION_TUNABLE_NAMES += ("SAS_PILOT_CONSOLE_ON",)

# <!-- custom: The values toggle_dev_diagnostics.py "on" sets locally; CI never reads them.
# They sit beside the shipped values so both settings of each switched define can be seen and changed in one place. (Claude code Opus 5.5) -->
DEVELOPMENT_VALUES = {
	"SAS_SGR_LOG_ON": 1,
	"SAS_SGR_LOG": 3,
	"SAS_SGR_MAP_ANNOTATION_TEXT_ON": 1,
	# <!-- custom: The local chat test profile captures all three channels; off restores each privacy default. (GPT-6.1-Sol) -->
	"SAS_SGR_CHAT_ALL_TEXT_ON": 1,
	"SAS_SGR_CHAT_TEAM_TEXT_ON": 1,
	"SAS_SGR_CHAT_DIRECT_TEXT_ON": 1,
	"SAS_RUNTIME_STATUS_ON": 1,
	"SAS_RUNTIME_SCREENSHOT_WATCH_ON": 1,
	"SAS_RUNTIME_SOURCE_WATCH_ON": 1,
	# <!-- custom: Not a diagnostic but the same kind of local switch: skip the Dawn of Man screen during development and agent runs; players keep it. (Claude Code Opus 5.5) -->
	"SAS_UI_DAWN_OF_MAN_ON": 0,
	# <!-- custom: The same for the screens that only inform, one switch each, added after a traded tech's splash held up a pilot game (2026-11-13). (Claude code Opus 5.5) -->
	"SAS_UI_TECH_SPLASH_ON": 0,
	"SAS_UI_ERA_MOVIE_ON": 0,
	"SAS_UI_WONDER_MOVIE_ON": 0,
	"SAS_UI_RELIGION_MOVIE_ON": 0,
	"SAS_UI_PROJECT_MOVIE_ON": 0,
	# <!-- custom: The Greatest Civilizations screen, recorded as a Timeline row either way (2026-11-19). (Claude code Opus 5.5) -->
	"SAS_UI_TOP_CIVS_ON": 0,
}

# <!-- custom: Settings that agent runs want besides the toggled ones, which SASPilotClient.py lists in its greeting: informational popups dismissed during autoplay.
# Moved here from SASPilotClient.py on 2026-11-19. (Claude code Opus 5.5) -->
AGENT_RUN_VALUES = {
	"SAS_AIAUTOPLAY_DISMISS_INFO_POPUPS_ON": 1,
}
