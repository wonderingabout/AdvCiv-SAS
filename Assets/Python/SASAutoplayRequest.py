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
	_iPendingTurns = iTurns
	_bPendingDebugMode = bDebugMode
	CvUtil.pyPrintRecord("SAS_AUTOPLAY_REQUEST", "outcome=ARMED trigger=%s turns=%d debugMode=%d ini=%s" % (szTrigger, iTurns, int(_bPendingDebugMode), path))


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
