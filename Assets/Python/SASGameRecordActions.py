# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Keep revision-151 Python UI tracing tiny and factual: fixed screen/action labels plus scalar state only.
# Free-text search, names, paths, mouse movement, redraws, and other high-volume/private input deliberately stay outside SASGameRecord. (ChatGPT-5.6-Sol) -->

from CvPythonExtensions import CyGame, FeatTypes, OrderTypes # <!-- custom: CyGame supplies the existing SGR bridge; FeatTypes exposes actual DLL enum names and OrderTypes disambiguates reviewed advisor production targets without repeating gameplay eligibility checks. (GPT-6.1-Sol) -->
import SASGameRecordConfig
import SASPopupChoices # <!-- custom: Resolve reviewed Python response names from the same UI catalog that creates buttons and assigns gameplay-handler IDs, rather than a recorder-owned duplicate table. (GPT-6.1-Sol) -->

# <!-- custom: Python 2.4 has no standard Enum class; shared named constants keep action labels consistent and make misspelled attribute references fail visibly.
# These are existing log tokens, not new numeric IDs or a separate runtime registry. (GPT-6.1-Sol) -->
SHOW_REQUEST = "SHOW_REQUEST"
SHOW = "SHOW"
HIDE = "HIDE"
NAVIGATE = "NAVIGATE"
BACK = "BACK"
FORWARD = "FORWARD"
CLOSE_CALLBACK = "CLOSE_CALLBACK"
SCROLL_UP = "SCROLL_UP"
SCROLL_DOWN = "SCROLL_DOWN"
SCROLL_UP_FAST = "SCROLL_UP_FAST"
SCROLL_DOWN_FAST = "SCROLL_DOWN_FAST"
CENTER_ACTIVE_PLAYER = "CENTER_ACTIVE_PLAYER"
AUTOCENTER_TOGGLE = "AUTOCENTER_TOGGLE"
BACKGROUND_STYLE_CYCLE = "BACKGROUND_STYLE_CYCLE"
EXPAND_LOCK_TOGGLE = "EXPAND_LOCK_TOGGLE"
VISIBILITY_TOGGLE = "VISIBILITY_TOGGLE"

# <!-- custom: Screen/component tokens are diagnostic labels, not new Civ4 screen IDs; retain engine screen IDs separately in the numeric destination fields. (GPT-6.1-Sol) -->
SCREEN_BUG_OPTIONS = "BUG_OPTIONS"
SCREEN_DIPLOMACY = "DIPLOMACY"
SCREEN_DOMESTIC_ADVISOR = "DOMESTIC_ADVISOR"
SCREEN_FOREIGN_ADVISOR = "FOREIGN_ADVISOR"
SCREEN_FOREIGN_DIPLOMACY_ADVISOR = "FOREIGN_DIPLOMACY_ADVISOR"
SCREEN_INFO_SCREEN = "INFO_SCREEN"
SCREEN_MAP_ANNOTATIONS = "MAP_ANNOTATIONS"
SCREEN_MILITARY_ADVISOR = "MILITARY_ADVISOR"
SCREEN_OPTIONS = "OPTIONS"
SCREEN_POLICY_ADVISOR = "POLICY_ADVISOR"
SCREEN_PYTHON_SCREEN = "PYTHON_SCREEN"
SCREEN_SCOREBOARD = "SCOREBOARD"
SCREEN_SEVOPEDIA = "SEVOPEDIA"
SCREEN_TECH_CHOOSER = "TECH_CHOOSER"
SCREEN_VICTORY_SCREEN = "VICTORY_SCREEN"
SCREEN_WORLD_ADVISOR = "WORLD_ADVISOR"
SCREEN_WORLD_BUILDER = "WORLD_BUILDER"
SCREEN_WORLD_BUILDER_DIPLOMACY = "WORLD_BUILDER_DIPLOMACY"

# <!-- custom: Advance only at explicit new/load/reload boundaries; persistent screen objects must not suppress a later session's baseline.
# Zero also keeps disabled redraws on their cheap integer-comparison path. (GPT-6.1-Sol) -->
g_sessionSerial = 0


def resetSession():
	global g_sessionSerial
	if SASGameRecordConfig.getLogLevel() >= 2 and SASGameRecordConfig.getActionTraceEnabled():
		g_sessionSerial += 1


def isEnabled():
	return SASGameRecordConfig.getLogLevel() >= 2 and SASGameRecordConfig.getActionTraceEnabled() and CyGame().isFinalInitialized()


# <!-- custom: Check the cached detail level and action-trace subject switch before constructing the native wrapper; enabled emitters reuse that one wrapper for the initialization check and output instead of constructing it twice. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
def _getEnabledGame():
	if SASGameRecordConfig.getLogLevel() < 2 or not SASGameRecordConfig.getActionTraceEnabled():
		return None
	game = CyGame()
	if not game.isFinalInitialized():
		return None
	return game


def logScreenAction(szScreen, szAction, iPrimary=-1, iSecondary=-1):
	game = _getEnabledGame()
	if game is None:
		return
	game.logSASGameRecordScreenAction(szScreen, szAction, iPrimary, iSecondary)


def _scoreboardState(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter):
	# <!-- custom: Conditional expressions in the first draft require Python 2.5; Civ4 uses Python 2.4.
	# Explicit branches preserve unresolved None values as -1. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	if iBgStyle is None:
		iStyle = -1
	else:
		iStyle = int(iBgStyle)
	if bAlwaysExpand is None:
		iExpand = -1
	else:
		iExpand = int(bool(bAlwaysExpand))
	if bAutocenter is None:
		iCenter = -1
	else:
		iCenter = int(bool(bAutocenter))
	return (int(iScrollOffset), iStyle, iExpand, iCenter)


def logScoreboardSnapshot(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter):
	game = _getEnabledGame()
	if game is None:
		return False
	state = _scoreboardState(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter)
	szValues = "scrollOffset=%d;bgStyle=%d;alwaysExpand=%d;autocenter=%d" % state
	game.logSASGameRecordInterfaceState(SCREEN_SCOREBOARD, "SNAPSHOT", "FIRST_DRAW", 4, szValues)
	return True


def captureScoreboardState(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter):
	if not isEnabled():
		return None
	return _scoreboardState(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter)


def logScoreboardChange(szReason, before, iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter):
	if before is None:
		return
	game = _getEnabledGame()
	if game is None:
		return
	after = _scoreboardState(iScrollOffset, iBgStyle, bAlwaysExpand, bAutocenter)
	if before == after:
		return
	names = ("scrollOffset", "bgStyle", "alwaysExpand", "autocenter")
	changes = []
	for i in range(len(names)):
		if before[i] != after[i]:
			changes.append("%s=%d>%d" % (names[i], before[i], after[i]))
	game.logSASGameRecordInterfaceState(SCREEN_SCOREBOARD, "CHANGE", szReason, len(changes), ";".join(changes))


def logBooleanInterfaceChange(szComponent, szReason, szKey, bOldValue, bNewValue):
	game = _getEnabledGame()
	if game is None:
		return
	bOld = bool(bOldValue)
	bNew = bool(bNewValue)
	if bOld == bNew:
		return
	szValues = "%s=%d>%d" % (szKey, int(bOld), int(bNew))
	game.logSASGameRecordInterfaceState(szComponent, "CHANGE", szReason, 1, szValues)


# <!-- custom: Diplomacy conversations use a separate Python response callback rather than native ButtonPopup focus.
# Preserve the actual XML comment identity and counterpart before response dispatch, including navigation/refusal replies that need not produce a deal or war event; never copy the displayed conversation or edit-box text.
# The caller pre-gates context collection; the standard helper gate also keeps other callers from formatting values when tracing is disabled. (GPT-6.1-Sol) -->
def logDiplomacyResponse(gc, iComment, iOtherPlayer):
	game = _getEnabledGame()
	if game is None:
		return
	if iComment >= 0 and iComment < gc.getNumDiplomacyInfos():
		szComment = gc.getDiplomacyInfo(iComment).getType()
	else:
		szComment = "UNKNOWN_DIPLOMACY_COMMENT"
	# <!-- custom: Read the XML type itself instead of copying the handler's long string comparison chain into another enum/table; numeric callback payloads are omitted because arbitrary mod-defined replies can give them other meanings. (GPT-6.1-Sol) -->
	szValues = "commentId=%d;otherPlayer=%d;handling=NATIVE_RESPONSE" % (iComment, iOtherPlayer)
	game.logSASGameRecordInterfaceState(SCREEN_DIPLOMACY, "RESPONSE", szComment, 3, szValues)


_gFeatNames = None


# <!-- custom: Reuse the scalar interface-state bridge for companion Python response rows, retaining the native popup's numeric response separately.
# Callers below supply only fixed keys/labels, enum/XML identities and reviewed numbers, never argsList text/edit boxes.
# The supplied game has already passed the cached gate.
# A response is observed before callback dispatch, not proof that its command succeeded or that a human clicked. (GPT-6.1-Sol) -->
def _emitPythonPopupResponse(game, szCallback, iButton, choices, fields, szChoice="BUTTON_RESPONSE"):
	if choices is not None:
		szChoice = choices.getName(iButton)
	values = [("button", iButton), ("choice", szChoice), ("handling", "PYTHON_CALLBACK"), ("stage", "CALLBACK_DISPATCH")]
	values.extend(fields)
	game.logSASGameRecordInterfaceState("PYTHON_POPUP", "RESPONSE", szCallback, len(values), ";".join(["%s=%s" % item for item in values]))


# <!-- custom: The city-warning callback carries an actual OrderTypes/XML item, unlike ambiguous native production buttons; record its recommendation even when refused or the city disappeared before response.
# Resolve only direct XML IDs behind the gate; do not call canTrain/canConstruct or repeat the advisor's scoring. (GPT-6.1-Sol) -->
def logCityRecommendationResponse(gc, iButton, iCity, iOrder, iTarget):
	game = _getEnabledGame()
	if game is None:
		return
	szKind = "UNKNOWN_ORDER"
	szTarget = "-"
	if iOrder == OrderTypes.ORDER_TRAIN and iTarget >= 0 and iTarget < gc.getNumUnitInfos():
		szKind = "UNIT"
		szTarget = gc.getUnitInfo(iTarget).getType()
	elif iOrder == OrderTypes.ORDER_CONSTRUCT and iTarget >= 0 and iTarget < gc.getNumBuildingInfos():
		szKind = "BUILDING"
		szTarget = gc.getBuildingInfo(iTarget).getType()
	_emitPythonPopupResponse(game, "cityWarningOnClickedCallback", iButton, SASPopupChoices.CITY_RECOMMENDATION,
		[("cityId", iCity), ("orderId", iOrder), ("targetKind", szKind), ("targetId", iTarget), ("target", szTarget)])


# <!-- custom: Liberation and colony recommendations share accept/refuse/examine buttons but trigger different existing operations; preserve that distinction without querying new liberation/area eligibility for diagnostics. (GPT-6.1-Sol) -->
def logCityDispositionResponse(iButton, iCity, bColony):
	game = _getEnabledGame()
	if game is None:
		return
	if bColony:
		szCallback = "colonyOnClickedCallback"
		choices = SASPopupChoices.COLONY
	else:
		szCallback = "liberateOnClickedCallback"
		choices = SASPopupChoices.LIBERATION
	_emitPythonPopupResponse(game, szCallback, iButton, choices, [("cityId", iCity)])


# <!-- custom: Feats are DLL enums rather than XML infos.
# Build a small name map once from the exposed enum itself, only for enabled tracing; a copied numeric/name table would drift when SAS adds unit-combat feats.
# data2 is a city ID for several feat producers but unspecified for others, so retain its reviewed numeric payload without claiming that it always identifies a city. (GPT-6.1-Sol) -->
def logFeatResponse(iButton, iFeat, iContextData2):
	game = _getEnabledGame()
	if game is None:
		return
	global _gFeatNames
	if _gFeatNames is None:
		_gFeatNames = {}
		for szName in sorted(dir(FeatTypes)):
			if szName.startswith("FEAT_"):
				_gFeatNames[int(getattr(FeatTypes, szName))] = szName
	_emitPythonPopupResponse(game, "featAccomplishedOnClickedCallback", iButton, SASPopupChoices.FEAT,
		[("featId", iFeat), ("feat", _gFeatNames.get(iFeat, "UNKNOWN_FEAT")), ("contextData2", iContextData2)])


# <!-- custom: The three reviewed random-event callbacks carry the responding and other player IDs, with Yes/No meaning war or peace according to the specific handler.
# Capture rejection as well as acceptance, separately from later war/peace effects and without copying localized event text. (GPT-6.1-Sol) -->
def logEventDiplomacyResponse(szCallback, iButton, iPlayer, iOtherPlayer, bWar):
	game = _getEnabledGame()
	if game is None:
		return
	if bWar:
		choices = SASPopupChoices.EVENT_WAR
	else:
		choices = SASPopupChoices.EVENT_PEACE
	_emitPythonPopupResponse(game, szCallback, iButton, choices, [("respondingPlayer", iPlayer), ("otherPlayer", iOtherPlayer)])


# <!-- custom: The BUG debug event selector indexes EventTriggerInfos directly and appends Cancel; preserve its exact XML identity rather than its prettified display name.
# This observes the debug request, not a successful event outcome. (GPT-6.1-Sol) -->
def logEventTriggerResponse(gc, iButton, iPlayer):
	game = _getEnabledGame()
	if game is None:
		return
	szChoice = "BUTTON_RESPONSE"
	szTarget = "-"
	if iButton >= 0 and iButton < gc.getNumEventTriggerInfos():
		szChoice = "TRIGGER_EVENT"
		szTarget = gc.getEventTriggerInfo(iButton).getType()
	elif iButton == gc.getNumEventTriggerInfos():
		szChoice = "CANCEL"
	_emitPythonPopupResponse(game, "triggerRandomEvent", iButton, None, [("targetPlayer", iPlayer), ("eventTriggerId", iButton), ("eventTrigger", szTarget)], szChoice)
