## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

# <!-- custom: The BUG Mod notice below is retained for the definitions moved from SevoScreenEnums.py into this file's SevoScreenEnums class. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->

## Copyright 2007 BUG Mod

# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# Enum for screens...

from CvPythonExtensions import CivilopediaPageTypes

DOMESTIC_ADVISOR = 0
REWARD_SCREEN = 1
DAWN_OF_MAN = 2
TECH_CHOOSER = 3
FOREIGN_ADVISOR = 4
# <!-- custom: legacy screen id 5 now maps to Foreign Diplomacy naming. (GPT-5.3-Codex) -->
FOREIGN_DIPLOMACY_SCREEN = 5
WONDER_MOVIE_SCREEN = 6
# <!-- custom: Now opens the Policy Advisor's Religion tab; HandleInputMap routes it to policyAdvisorScreen. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
RELIGION_SCREEN = 7
INTRO_MOVIE_SCREEN = 8
# <!-- custom: canonical policy advisor screen id; removed civics/policy alias layer for strict naming consistency. (GPT-5.3-Codex) -->
POLICY_ADVISOR_SCREEN = 9
DIPLOMACY_SCREEN = 10
OPTIONS_SCREEN = 11
TECH_SPLASH = 12
REPLAY_SCREEN = 13
MILITARY_ADVISOR = 14
VICTORY_SCREEN = 15
TOP_CIVS = 16
TUTORIAL_SCREEN = 17
INFO_SCREEN = 18
ERA_MOVIE_SCREEN = 19
ADVISOR_SCREEN = 20
HALL_OF_FAME = 21
DAN_QUAYLE_SCREEN = 22
WORLDBUILDER_SCREEN = 23
WORLDBUILDER_DIPLOMACY_SCREEN = 24
VICTORY_MOVIE_SCREEN = 25
UN_SCREEN = 26
# <!-- custom: Now opens the Foreign Diplomacy Advisor's Espionage tab; HandleInputMap routes it to foreignDiplomacyAdvisor. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
ESPIONAGE_ADVISOR = 27
SPACE_SHIP_SCREEN = 28
# <!-- custom: Now opens the Policy Advisor's Corporation tab; HandleInputMap routes it to policyAdvisorScreen. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
CORPORATION_SCREEN = 29
# <!-- custom: split Foreign advisor shell id for diplomacy/intel cluster (F3 slot). (GPT-5.3-Codex) -->
FOREIGN_DIPLOMACY_ADVISOR = 30
# <!-- custom: World Advisor owns the Environment tab (moved out of its former location). (GPT-5.5) -->
WORLD_ADVISOR = 31

GAMEFONT_DISPLAY_SCREEN = 75 # advc.gfd

MAIN_INTERFACE = 99
DEBUG_INFO_SCREEN = 100

# <!-- custom: Retain these original vanilla Civilopedia IDs for the legacy option selected by CvScreensInterface.createCivilopedia; they are not aliases for the overlapping SevoScreenEnums IDs below.
# SAS supports Sevopedia; retaining the inherited alternative does not establish coverage of SAS-specific pages/categories. (GPT-6.1-Sol) -->
# Civilopedia Pages start at 200
PEDIA_START = 200
PEDIA_MAIN = 199#CivilopediaPageTypes.CIVILOPEDIA_PAGE_MAIN + PEDIA_START
PEDIA_TECH = CivilopediaPageTypes.CIVILOPEDIA_PAGE_TECH + PEDIA_START
PEDIA_UNIT = CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT + PEDIA_START
PEDIA_BUILDING = CivilopediaPageTypes.CIVILOPEDIA_PAGE_BUILDING + PEDIA_START
PEDIA_TERRAIN = CivilopediaPageTypes.CIVILOPEDIA_PAGE_TERRAIN + PEDIA_START
PEDIA_FEATURE = CivilopediaPageTypes.CIVILOPEDIA_PAGE_FEATURE + PEDIA_START
PEDIA_BONUS = CivilopediaPageTypes.CIVILOPEDIA_PAGE_BONUS + PEDIA_START
PEDIA_IMPROVEMENT = CivilopediaPageTypes.CIVILOPEDIA_PAGE_IMPROVEMENT + PEDIA_START
PEDIA_SPECIALIST = CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPECIALIST + PEDIA_START
PEDIA_PROMOTION = CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROMOTION + PEDIA_START
PEDIA_UNIT_CHART = CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT_GROUP + PEDIA_START
PEDIA_CIVILIZATION = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIV + PEDIA_START
PEDIA_LEADER = CivilopediaPageTypes.CIVILOPEDIA_PAGE_LEADER + PEDIA_START
PEDIA_RELIGION = CivilopediaPageTypes.CIVILOPEDIA_PAGE_RELIGION + PEDIA_START
PEDIA_CORPORATION = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CORPORATION + PEDIA_START
PEDIA_CIVIC = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIVIC + PEDIA_START
PEDIA_PROJECT = CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROJECT + PEDIA_START
PEDIA_CONCEPT = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT + PEDIA_START
PEDIA_CONCEPT_NEW = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW + PEDIA_START
PEDIA_HINTS = CivilopediaPageTypes.CIVILOPEDIA_PAGE_HINTS + PEDIA_START
PEDIA_HISTORY = PEDIA_HINTS+1#CivilopediaPageTypes.CIVILOPEDIA_PAGE_HISTORY + PEDIA_START

# <!-- custom: Moved the constants from the removed SevoScreenEnums.py into class SevoScreenEnums in CvScreenEnums.py, so general/vanilla and Sevopedia IDs share one catalog without renumbering.
# The inherited Sevopedia definitions overlap vanilla page IDs and PEDIA_MAIN names; the class keeps those meanings distinct. (GPT-6.1-Sol) -->
class SevoScreenEnums:
	PEDIA_MAIN = 200
	PEDIA_TECHS = 201
	PEDIA_UNITS = 202
	PEDIA_UNIT_UPGRADES = 203
	PEDIA_UNIT_CATEGORIES = 204
	PEDIA_PROMOTIONS = 205
	PEDIA_PROMOTION_TREE = 206
	PEDIA_BUILDINGS = 207
	PEDIA_NATIONAL_WONDERS = 208
	PEDIA_WORLD_WONDERS = 209
	PEDIA_PROJECTS = 210
	PEDIA_SPECIALISTS = 211
	PEDIA_TERRAINS = 212
	PEDIA_FEATURES = 213
	PEDIA_BONUSES = 214
	PEDIA_IMPROVEMENTS = 215
	PEDIA_BUILDS = 232
	PEDIA_CIVS = 216
	PEDIA_LEADERS = 217
	PEDIA_TRAITS = 218 # <!-- custom: advc.004y: Restored; retain the trait category in the consolidated catalog. (GPT-6.1-Sol) -->
	PEDIA_CIVICS = 219
	PEDIA_RELIGIONS = 220
	PEDIA_CORPORATIONS = 221
	PEDIA_CONCEPTS = 222
	PEDIA_BTS_CONCEPTS = 223
	PEDIA_HINTS = 224
	PEDIA_SHORTCUTS = 225
	PEDIA_HANDICAP_CHART = 226
	PEDIA_INDEX = 227
	PEDIA_STRATEGY = 228
	PEDIA_GAME_SPEED_CHART = 229
	PEDIA_WORLD_SIZE_CHART = 230
	PEDIA_ERA_CHART = 231
	PEDIA_MOVIES = 233
	PEDIA_MUSIC = 234
	PEDIA_VOTES = 235
	PEDIA_EVENT_TRIGGERS = 236
	PEDIA_ROUTES = 237


# <!-- custom: The footer tabs of every tabbed advisor, in one place, as this file already holds every screen's ID (the user's idea, 2026-11-22, akin to SevoScreenEnums).
# Each screen kept its own list in its own shape (ID lists, text keys built at draw time, two key sets in the Foreign Advisor, a Rise and Fall tab added in the Victory screen), so code that needed every tab, such as SASPilot's tab listing, had to open each screen and read what it drew.
# Advisors are in hotkey order, each with its key from CIV4ControlInfos.xml in a comment (the Tech Chooser, F6, has no footer tabs); each is (short name as SASPilot's uiopen takes it, screen ID, control that opens it, tabs), and each tab is (key, text key of its label, game option it needs or None).
# The screens draw their labels and tab order from here and keep their own widget names and page IDs, so input handling is unchanged. A tab's position is its page number where a screen numbers pages by position, so reordering here reorders the screen.
# Plain tuples and string keys are enough: the keys are read when a screen sets up or draws its tab bar, not per frame, while the active page is already an integer; a separate numeric enum would be another list to keep in step.
# Keep each tab tuple beside its advisor and hotkey so the whole entry is in one place. Naming the tuples separately also builds them once at import; the lookup dictionaries below are the same either way. (GPT-6.2-Sol)
# Domestic's Overview labels were hard-coded English; they now have text keys. See KI#1110. (Claude code Opus 5.5) -->
ADVISOR_TABS = (
	("domestic", DOMESTIC_ADVISOR, "CONTROL_DOMESTIC_SCREEN", ( # <!-- custom: F1 (Claude code Opus 5.5) -->
		("OVERVIEW1", "TXT_KEY_SAS_DOMESTIC_ADVISOR_OVERVIEW1_TAB", None),
		("OVERVIEW2", "TXT_KEY_SAS_DOMESTIC_ADVISOR_OVERVIEW2_TAB", None),
		("OVERVIEW3", "TXT_KEY_SAS_DOMESTIC_ADVISOR_OVERVIEW3_TAB", None),
		("OVERVIEW4", "TXT_KEY_SAS_DOMESTIC_ADVISOR_OVERVIEW4_TAB", None),
		("FINANCE", "TXT_KEY_ECONOMICS_ADVISOR_FINANCE_TAB", None),
	)),
	("policy", POLICY_ADVISOR_SCREEN, "CONTROL_CIVICS_SCREEN", ( # <!-- custom: F2 (Claude code Opus 5.5) -->
		("CIVICS", "TXT_KEY_CONCEPT_CIVICS", None),
		("RELIGIONS", "TXT_KEY_POLICY_TAB_RELIGIONS", None),
		("CORPORATIONS", "TXT_KEY_POLICY_TAB_CORPORATIONS", None),
	)),
	# <!-- custom: The Foreign Diplomacy and Foreign Trade advisors share CvForeignAdvisor; their keys are its SCREEN_DICT keys. (Claude code Opus 5.5) -->
	("foreigndiplomacy", FOREIGN_DIPLOMACY_ADVISOR, "CONTROL_FOREIGN_DIPLOMACY_SCREEN", ( # <!-- custom: F3 (Claude code Opus 5.5) -->
		("RELATIONS", "TXT_KEY_FOREIGN_ADVISOR_RELATIONS", None),
		("GLANCE", "TXT_KEY_FOREIGN_ADVISOR_GLANCE", None),
		("INFO", "TXT_KEY_FOREIGN_ADVISOR_INFO", None),
		("ESPIONAGE", "TXT_KEY_SAS_ESPIONAGE_SHORT", None),
	)),
	("foreigntrade", FOREIGN_ADVISOR, "CONTROL_FOREIGN_SCREEN", ( # <!-- custom: F4 (Claude code Opus 5.5) -->
		# <!-- custom: renamed Active tab label to Treaties to match the reduced scope (no bonus clutter). (GPT-5.3-Codex) -->
		("ACTIVE_TRADE", "TXT_KEY_FOREIGN_ADVISOR_TREATIES", None),
		("BONUS", "TXT_KEY_FOREIGN_ADVISOR_RESOURCES", None),
		("TECH", "TXT_KEY_FOREIGN_ADVISOR_TECHS", None),
		# <!-- custom: The Cities tab comes from AdvCiv advc.ctr. (Claude code Opus 5.5) -->
		("CITIES", "TXT_KEY_CONCEPT_CITIES", None),
	)),
	("military", MILITARY_ADVISOR, "CONTROL_MILITARY_SCREEN", ( # <!-- custom: F5 (Claude code Opus 5.5) -->
		("SUMMARY", "TXT_KEY_SAS_MILITARY_ADVISOR_SUMMARY_TAB", None),
		("MAP", "TXT_KEY_SAS_MILITARY_ADVISOR_MAP_TAB", None),
		("BATTLES", "TXT_KEY_SAS_MILITARY_ADVISOR_BATTLES_TAB", None),
		("COMPOSITION", "TXT_KEY_SAS_MILITARY_ADVISOR_COMPOSITION_TAB", None),
	)),
	("world", WORLD_ADVISOR, "CONTROL_WORLD_ADVISOR_SCREEN", ( # <!-- custom: F7 (Claude code Opus 5.5) -->
		# <!-- custom: Keep Environment after the territory pages and put Changes last as the more specialized persisted setup/editor provenance view. (Claude code Opus 4.7 + ChatGPT-5.6-Sol) -->
		("BFC1", "TXT_KEY_WORLD_ADVISOR_BFC1_TAB", None),
		("BFC2", "TXT_KEY_WORLD_ADVISOR_BFC2_TAB", None),
		("TERRITORY", "TXT_KEY_WORLD_ADVISOR_TERRITORY_TAB", None),
		("ENVIRONMENT", "TXT_KEY_ECONOMICS_ADVISOR_ENVIRONMENT_TAB", None),
		("CHANGES", "TXT_KEY_WORLD_ADVISOR_CHANGES_TAB", None),
	)),
	("info", INFO_SCREEN, "CONTROL_INFO", ( # <!-- custom: F8 (Claude code Opus 5.5) -->
		# <!-- custom: Score Tab registration in the Info screen tab bar/order. (GPT-5.3-Codex) -->
		# <!-- custom: Score must stay second: CvDLLWidgetData.cpp opens Info on Score with py.showInfoScreen(1), a number the DLL keeps, which advisor_tab_registry.py checks. See KI#1110. (Claude code Opus 5.5) -->
		("GRAPH", "TXT_KEY_INFO_GRAPH", None),
		("SCORE", "TXT_KEY_GAME_SCORE", None),
		("TIMELINE", "TXT_KEY_SAS_INFO_TIMELINE", None),
		("DEMOGRAPHICS", "TXT_KEY_DEMO_SCREEN_TITLE", None),
		("TOP_CITIES", "TXT_KEY_WONDERS_SCREEN_TOP_CITIES_TEXT", None),
		("STATISTICS", "TXT_KEY_INFO_SCREEN_STATISTICS_TITLE", None),
	)),
	("victory", VICTORY_SCREEN, "CONTROL_VICTORY_SCREEN", ( # <!-- custom: F9 (Claude code Opus 5.5) -->
		("VICTORIES", "TXT_KEY_MAIN_MENU_VICTORIES", None),
		("SETTINGS", "TXT_KEY_MAIN_MENU_SETTINGS", None),
		("RESOLUTIONS", "TXT_KEY_VOTING_TITLE", None),
		("MEMBERS", "TXT_KEY_MEMBERS_TITLE", None),
		# <!-- custom: advc.703's Rise and Fall score tab, which the Victory screen adds only in a Rise and Fall game. (Claude code Opus 5.5) -->
		("RISE_FALL_SCORE", "TXT_KEY_GAME_SCORE", "GAMEOPTION_RISE_FALL"),
	)),
)


# <!-- custom: Built once at import, so a lookup is a dict access rather than a loop of string compares (the user's question about cost), and each tab's position is its integer page number, the enum the screens compare against per frame.
# Five screens kept those numbers as their own constants (Domestic PAGE_OVERVIEW1 = 0, World iTerritoryID = 2...), a second copy of the order; they now take them from getAdvisorTabIndex at init. See KI#1110. (Claude code Opus 5.5) -->
_ADVISOR_TABS_BY_NAME = {}
_ADVISOR_TAB_INDEX = {}
for (_sasAdvisor, _sasScreen, _sasControl, _sasTabs) in ADVISOR_TABS:
	_ADVISOR_TABS_BY_NAME[_sasAdvisor] = _sasTabs
	for _sasIndex in range(len(_sasTabs)):
		_ADVISOR_TAB_INDEX[(_sasAdvisor, _sasTabs[_sasIndex][0])] = _sasIndex


def getAdvisorTabs(szAdvisor):
	# <!-- custom: An advisor's tabs by its short name; an unknown name fails loudly rather than drawing no tabs. (Claude code Opus 5.5) -->
	if not _ADVISOR_TABS_BY_NAME.has_key(szAdvisor):
		raise KeyError("no advisor %s in CvScreenEnums.ADVISOR_TABS" % szAdvisor)
	return _ADVISOR_TABS_BY_NAME[szAdvisor]


def getAdvisorTabIndex(szAdvisor, szTabKey):
	# <!-- custom: A tab's page number, its position in the registry; unknown keys fail loudly. (Claude code Opus 5.5) -->
	if not _ADVISOR_TAB_INDEX.has_key((szAdvisor, szTabKey)):
		raise KeyError("no tab %s in advisor %s of CvScreenEnums.ADVISOR_TABS" % (szTabKey, szAdvisor))
	return _ADVISOR_TAB_INDEX[(szAdvisor, szTabKey)]


def getAdvisorTabKeys(szAdvisor):
	return [tab[0] for tab in getAdvisorTabs(szAdvisor)]


def getAdvisorTabTextKeys(szAdvisor):
	return [tab[1] for tab in getAdvisorTabs(szAdvisor)]


# <!-- custom: Enrich Python screen diagnostics by deriving names once from this catalog, instead of repeating ID-to-name tables at log callers.
# Like the derive-once category wiring in SevoPediaMain.py (SAS_CATEGORY_DEFS), reuse canonical definitions; here the inputs are integer constants, not page builders or navigation rules.
# Both contain general screens; each contains only its own encyclopedia pages, so one selection handles the overlapping IDs.
# PEDIA_START is an offset, not a screen. (GPT-6.1-Sol) -->
_SAS_SCREEN_NAMES = {}
_SAS_SEVO_SCREEN_NAMES = {}
for _sasName, _sasValue in globals().items():
	if _sasName.isupper() and _sasName != "PEDIA_START" and isinstance(_sasValue, int):
		_SAS_SCREEN_NAMES[_sasValue] = "CvScreenEnums." + _sasName
		if not _sasName.startswith("PEDIA_"):
			_SAS_SEVO_SCREEN_NAMES[_sasValue] = "CvScreenEnums." + _sasName
for _sasName, _sasValue in vars(SevoScreenEnums).items():
	if _sasName.startswith("PEDIA_") and isinstance(_sasValue, int):
		_SAS_SEVO_SCREEN_NAMES[_sasValue] = "CvScreenEnums.SevoScreenEnums." + _sasName


def getSASScreenName(iScreen, bUsingSevopedia=False):
	# <!-- custom: Select the active encyclopedia catalog here so diagnostic callers need no per-page conditions.
	# Retain the numeric ID at callers too: EXE/custom screens absent from the selected catalog are explicitly unregistered rather than guessed. (GPT-6.1-Sol) -->
	if iScreen == -1:
		return "NO_SCREEN"
	if bUsingSevopedia:
		names = _SAS_SEVO_SCREEN_NAMES
	else:
		names = _SAS_SCREEN_NAMES
	return names.get(iScreen, "UNREGISTERED_SCREEN")


# <!-- custom: The XML tables the Sevopedia has a page per entry for, in one place, as ADVISOR_TABS is for the advisors' tabs (the user's idea, 2026-11-28).
# Two copies had grown apart: SevoPediaMain's SAS_linkMatchDefs (count and info getters on gc, category) for link(), and SASPilotCommands' _PEDIA_KINDS (XML type prefix, the same getters, a pediaJumpTo* name, the categories a page lands in) for 'types', 'pedia' and 'uiopen item='; each lacked kinds the other had, such as UNITCOMBAT_ in SASPilot and ERA_ in link().
# Each row is (XML type prefix, gc count method, gc info method, category pediaJump takes or None for no page, categories the page may land in, whether link() matches it); pediaJump moves a building into a Wonders category and a new concept into Shortcuts, hence the landing column.
# Row order is link()'s order, first match wins, so keep it when adding a row; the kinds link() does not match come last.
# CONCEPT_ starts both concept tables' types, so a prefix alone does not name the table: a reader checks the entry's own type, as SASPilot's _pediaKind does. See KI#1110.2. (Claude code Opus 5.5) -->
PEDIA_ITEM_KINDS = (
	("TECH_", "getNumTechInfos", "getTechInfo", SevoScreenEnums.PEDIA_TECHS, (SevoScreenEnums.PEDIA_TECHS,), True),
	("UNIT_", "getNumUnitInfos", "getUnitInfo", SevoScreenEnums.PEDIA_UNITS, (SevoScreenEnums.PEDIA_UNITS,), True),
	("UNITCOMBAT_", "getNumUnitCombatInfos", "getUnitCombatInfo", SevoScreenEnums.PEDIA_UNIT_CATEGORIES, (SevoScreenEnums.PEDIA_UNIT_CATEGORIES,), True),
	("PROMOTION_", "getNumPromotionInfos", "getPromotionInfo", SevoScreenEnums.PEDIA_PROMOTIONS, (SevoScreenEnums.PEDIA_PROMOTIONS,), True),
	("BUILDING_", "getNumBuildingInfos", "getBuildingInfo", SevoScreenEnums.PEDIA_BUILDINGS, (SevoScreenEnums.PEDIA_BUILDINGS, SevoScreenEnums.PEDIA_NATIONAL_WONDERS, SevoScreenEnums.PEDIA_WORLD_WONDERS), True),
	("PROJECT_", "getNumProjectInfos", "getProjectInfo", SevoScreenEnums.PEDIA_PROJECTS, (SevoScreenEnums.PEDIA_PROJECTS,), True),
	("SPECIALIST_", "getNumSpecialistInfos", "getSpecialistInfo", SevoScreenEnums.PEDIA_SPECIALISTS, (SevoScreenEnums.PEDIA_SPECIALISTS,), True),
	("TERRAIN_", "getNumTerrainInfos", "getTerrainInfo", SevoScreenEnums.PEDIA_TERRAINS, (SevoScreenEnums.PEDIA_TERRAINS,), True),
	("FEATURE_", "getNumFeatureInfos", "getFeatureInfo", SevoScreenEnums.PEDIA_FEATURES, (SevoScreenEnums.PEDIA_FEATURES,), True),
	("BONUS_", "getNumBonusInfos", "getBonusInfo", SevoScreenEnums.PEDIA_BONUSES, (SevoScreenEnums.PEDIA_BONUSES,), True),
	("IMPROVEMENT_", "getNumImprovementInfos", "getImprovementInfo", SevoScreenEnums.PEDIA_IMPROVEMENTS, (SevoScreenEnums.PEDIA_IMPROVEMENTS,), True),
	("ROUTE_", "getNumRouteInfos", "getRouteInfo", SevoScreenEnums.PEDIA_ROUTES, (SevoScreenEnums.PEDIA_ROUTES,), True),
	("BUILD_", "getNumBuildInfos", "getBuildInfo", SevoScreenEnums.PEDIA_BUILDS, (SevoScreenEnums.PEDIA_BUILDS,), True),
	("CIVILIZATION_", "getNumCivilizationInfos", "getCivilizationInfo", SevoScreenEnums.PEDIA_CIVS, (SevoScreenEnums.PEDIA_CIVS,), True),
	("LEADER_", "getNumLeaderHeadInfos", "getLeaderHeadInfo", SevoScreenEnums.PEDIA_LEADERS, (SevoScreenEnums.PEDIA_LEADERS,), True),
	# <!-- custom: Traits are matched so that clicking <link=literal>TraitName</link> in Sevopedia Leader (or anywhere else) navigates to the Sevopedia Traits page.
	# The DLL wraps trait names in <link=literal> tags (see CvGameTextMgr.cpp parseTraits); without this row, clicking trait links had no effect. (Claude Opus 4.5) -->
	("TRAIT_", "getNumTraitInfos", "getTraitInfo", SevoScreenEnums.PEDIA_TRAITS, (SevoScreenEnums.PEDIA_TRAITS,), True),
	("CIVIC_", "getNumCivicInfos", "getCivicInfo", SevoScreenEnums.PEDIA_CIVICS, (SevoScreenEnums.PEDIA_CIVICS,), True),
	("RELIGION_", "getNumReligionInfos", "getReligionInfo", SevoScreenEnums.PEDIA_RELIGIONS, (SevoScreenEnums.PEDIA_RELIGIONS,), True),
	("CORPORATION_", "getNumCorporationInfos", "getCorporationInfo", SevoScreenEnums.PEDIA_CORPORATIONS, (SevoScreenEnums.PEDIA_CORPORATIONS,), True),
	("CONCEPT_", "getNumConceptInfos", "getConceptInfo", SevoScreenEnums.PEDIA_CONCEPTS, (SevoScreenEnums.PEDIA_CONCEPTS,), True),
	("CONCEPT_", "getNumNewConceptInfos", "getNewConceptInfo", SevoScreenEnums.PEDIA_BTS_CONCEPTS, (SevoScreenEnums.PEDIA_BTS_CONCEPTS, SevoScreenEnums.PEDIA_SHORTCUTS), True),
	("VOTE_", "getNumVoteInfos", "getVoteInfo", SevoScreenEnums.PEDIA_VOTES, (SevoScreenEnums.PEDIA_VOTES,), False),
	("EVENTTRIGGER_", "getNumEventTriggerInfos", "getEventTriggerInfo", SevoScreenEnums.PEDIA_EVENT_TRIGGERS, (SevoScreenEnums.PEDIA_EVENT_TRIGGERS,), False),
	# <!-- custom: An era's page is its column of the Era chart, which records the era as its item. (Claude code Opus 5.5) -->
	("ERA_", "getNumEraInfos", "getEraInfo", SevoScreenEnums.PEDIA_ERA_CHART, (SevoScreenEnums.PEDIA_ERA_CHART,), False),
	# <!-- custom: Handicaps are shown only in the Handicap chart, with no page per handicap. (Claude code Opus 5.5) -->
	("HANDICAP_", "getNumHandicapInfos", "getHandicapInfo", None, (), False),
)
