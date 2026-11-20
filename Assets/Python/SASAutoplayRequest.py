# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Lets an external runner start AI Auto Play without keyboard or mouse input: Civ4 is launched with ini=<file> and /FXSLOAD=<save>, and that INI carries an [SASAutoplay] section.
# Only an explicit ini= launch argument is read, so ordinary launches with the default CivilizationIV.ini never start autoplay; Civ4 ignores the unknown section.
# Keystrokes sent to the game window did not reach the Ctrl+Shift+X chooser while mouse clicks did, and anyone typing at the PC could interfere, so the request travels in the INI instead.
# The request is consumed once per process, by the first game loaded or started (QuickStart = 1 starts a new game from the INI's [GAME] keys); a later game in the same process does not autoplay again.
# See LLM_Helpers/autoplay/run_autoplay.py. (Claude Code Opus 5.5) -->

from CvPythonExtensions import *
import CvUtil
import BugPath
import os

gc = CyGlobalContext()

_SECTION = "SASAutoplay"

_bConsumed = False
_iPendingTurns = 0
_bPendingDebugMode = False


def _findRequestIni():
	# <!-- custom: Reuse the DLL's command-line ini= parser that SASGameRecord added for its settings snapshot; the argument itself is not SGR-specific. (Claude Code Opus 5.5) -->
	argument = CyGame().getSASGameRecordIniFileArgument()
	if not argument:
		return None
	if os.path.isabs(argument) or (len(argument) >= 2 and argument[1] == ":"):
		candidates = [argument]
	else:
		candidates = [os.path.join(BugPath.getAppDir(), argument), os.path.join(BugPath.getRootDir(), argument)]
	for path in candidates:
		if os.path.isfile(path):
			return path
	return None


def _readRequest(path):
	# <!-- custom: ConfigObj, bundled with BUG, reads the INI as SASGameRecordSettings already does; imported at use so ordinary launches without ini= never load it. (Claude Code Opus 5.5) -->
	from configobj import ConfigObj
	config = ConfigObj(path, list_values=False, interpolation=False)
	for name in config.keys():
		if name.lower() == _SECTION.lower():
			section = config[name]
			values = {}
			for key in section.keys():
				values[key.lower()] = str(section[key]).strip()
			return values
	return None


def onLoadGame(argsList):
	_armRequest("ON_LOAD")


def onGameStart(argsList):
	_armRequest("GAME_START")


def _armRequest(szTrigger):
	global _bConsumed, _iPendingTurns, _bPendingDebugMode
	if _bConsumed:
		return
	_bConsumed = True
	path = _findRequestIni()
	if path is None:
		return
	request = _readRequest(path)
	if request is None:
		return
	# <!-- custom: Fail loudly on a malformed request rather than silently playing a different interval. (Claude Code Opus 5.5) -->
	iTurns = int(request.get("turns", "0"))
	if iTurns <= 0:
		raise ValueError("[%s] Turns must be a positive integer in %s" % (_SECTION, path))
	# <!-- custom: The leader check ran after the turns were armed, so a request it rejected still started autoplay, as Codex's 2026-11-10 review found; a bad DebugMode value did the same.
	# Parse and check everything first, so a raise leaves nothing armed. (Claude Code Opus 5.5) -->
	bDebugMode = (int(request.get("debugmode", "0")) > 0)
	if szTrigger == "GAME_START" and request.get("leaders"):
		_checkLeaders(request["leaders"], request.get("runid", "-"))
	# <!-- custom: QuickStart gives Advanced Start 0 points, as only Custom Game sets them, so an agent testing Advanced Start (2026-11-19) asks for points here; each living civ player gets them before its first turn, when the AI spends them. (Claude code Opus 5.5) -->
	if request.get("advancedstartpoints"):
		iPoints = int(request["advancedstartpoints"])
		if szTrigger != "GAME_START" or not CyGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START) or iPoints < 0:
			raise ValueError("[%s] AdvancedStartPoints needs a new Advanced Start game and a non-negative value in %s" % (_SECTION, path))
		for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(iPlayer).isAlive():
				gc.getPlayer(iPlayer).setAdvancedStartPoints(iPoints)
	# <!-- custom: Without AdvancedStartPoints, a QuickStart Advanced Start run gave every civ 0 points, so the AI founded one small city each, and the run waited on the Begin button with our points unspent (2026-11-19, SAS24 Pangaea from the Industrial era).
	# So civs still at 0 get the points the Custom Game screen would give, and the active player's are spent by the same automation as the Advanced Start screen's button before the phase ends, as Begin would end it.
	# That automation writes the Changes tab's Automate row, placed where it began, before the buys it made. See KI#1100. (Claude code Opus 5.5) -->
	if szTrigger == "GAME_START" and CyGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START):
		if not request.get("advancedstartpoints"):
			_setCustomGameAdvancedStartPoints()
		iActive = CyGame().getActivePlayer()
		if iActive >= 0 and gc.getPlayer(iActive).getAdvancedStartPoints() >= 0:
			CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE, iActive, -1, -1, -1, True)
			CyMessageControl().sendAdvancedStartAction(AdvancedStartActionTypes.ADVANCEDSTARTACTION_EXIT, iActive, -1, -1, -1, True)
	_iPendingTurns = iTurns
	_bPendingDebugMode = bDebugMode
	CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=ARMED trigger=%s turns=%d debugMode=%d ini=%s" % (szTrigger, iTurns, int(_bPendingDebugMode), path))


# <!-- custom: The Custom Game screen's points, as CvInitCore::resetAdvancedStartPoints and CvPlayer's game-start setup compute them: the start era's points times the world size's percent, then the player's handicap percent, and for an AI the game handicap's AI percent; advc.250c's minimum is left out, as it is not exposed to Python. (Claude code Opus 5.5) -->
def _setCustomGameAdvancedStartPoints():
	game = CyGame()
	iBase = gc.getEraInfo(game.getStartEra()).getAdvancedStartPoints() * gc.getWorldInfo(CyMap().getWorldSize()).getAdvancedStartPointsMod() / 100
	for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
		player = gc.getPlayer(iPlayer)
		if not player.isAlive() or player.getAdvancedStartPoints() != 0:
			continue
		iPoints = iBase * gc.getHandicapInfo(player.getHandicapType()).getAdvancedStartPointsMod() / 100
		if not player.isHuman():
			iPoints = iPoints * gc.getHandicapInfo(game.getHandicapType()).getAIAdvancedStartPercent() / 100
		player.setAdvancedStartPoints(iPoints)
	CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=ADVANCED_START_POINTS base=%d" % iBase)


# <!-- custom: CvInitCore::applySASRequestedLeaders sets the requested leaders before the game starts but can only assert on a bad name; compare the started game with the request here so a mismatch fails loudly in PythonErr.log, where run_autoplay.py reports it. (Claude Code Opus 5.5) -->
# <!-- custom: PythonErr.log is shared by every client, so the error names the request's RunId: a second client's runner wrongly reported this client's leader error as its own. See KI#1081. (Claude Code Opus 5.5) -->
def _checkLeaders(szLeaders, szRunId):
	slots = []
	for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
		player = gc.getPlayer(iPlayer)
		if player.isEverAlive() and not player.isMinorCiv():
			slots.append(player)
	mismatches = []
	tokens = szLeaders.split(",")
	for i in range(min(len(tokens), len(slots))):
		token = tokens[i].strip()
		if token == "" or token == "-":
			continue
		actual = gc.getLeaderHeadInfo(slots[i].getLeaderType()).getType()
		if actual != token:
			mismatches.append("player%d=%s(requested %s)" % (slots[i].getID(), actual, token))
	if len(tokens) > len(slots):
		mismatches.append("requested %d leaders for %d civilizations" % (len(tokens), len(slots)))
	if mismatches:
		CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=LEADERS_MISMATCH runId=%s %s" % (szRunId, " ".join(mismatches)))
		raise ValueError("[%s RunId=%s] Leaders not applied: %s" % (_SECTION, szRunId, ", ".join(mismatches)))
	CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=LEADERS_APPLIED leaders=%s" % ",".join([gc.getLeaderHeadInfo(player.getLeaderType()).getType() for player in slots]))


def onGameUpdate(argsList):
	global _iPendingTurns
	# <!-- custom: Start on the first game update after the load rather than inside OnLoad, so the load sequence and its handlers have finished before control passes to the AI. (Claude Code Opus 5.5) -->
	if _iPendingTurns <= 0:
		return
	game = CyGame()
	if game.getActivePlayer() == PlayerTypes.NO_PLAYER:
		return
	iTurns = _iPendingTurns
	_iPendingTurns = 0
	# <!-- custom: Debug Mode lets a watching user see the whole map, but it seems to change the AI's game, so compare only runs in the same mode. See KI#1080. (Claude Code Opus 5.5) -->
	if _bPendingDebugMode and not game.isDebugMode():
		game.toggleDebugMode()
	game.setAIAutoPlay(iTurns)
	CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=STARTED turns=%d gameTurn=%d debugMode=%d" % (iTurns, game.getGameTurn(), int(game.isDebugMode())))
