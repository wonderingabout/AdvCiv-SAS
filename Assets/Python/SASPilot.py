# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: SASPilot lets an external agent read and drive the running game from the command line instead of through the UI: requests arrive as JSON files in a per-process mailbox folder, run inside the game's Python, and are answered as JSON files.
# This module is only the stable loader: it decides once whether the pilot is on, then on game updates and screen updates hands the mailbox to LLM_Helpers/game_runs/SASPilotCommands.py, loaded from disk and reloaded when that file changes.
# Off unless SAS_PILOT_ON is 1 or the ini= launch file has an [SASPilot] section with On = 1, so ordinary players pay one comparison per game update and per frame.
# See LLM_Helpers/game_runs/pilot.py and _1_AdvCiv-SAS/Docs/Modding_Resources/README_Pilot.md. (Claude code Fable 5.2) -->

# <!-- custom: imp loads the command module from its file, os handles the mailbox folder and PID, sys and traceback report a failed reload; BugPath finds the mod and user folders; SASAutoplayRequest shares its ini= reader. (Claude code Fable 5.2) -->
from CvPythonExtensions import *
import imp
import os
import sys
import traceback
import BugPath
import CvUtil
import SASAutoplayRequest

gc = CyGlobalContext()

_SECTION = "SASPilot"
_COMMANDS_NAME = "SASPilotCommands"

# <!-- custom: None until the first tick resolves it; XML defines and the command line are not safe to read at import. (Claude code Fable 5.2) -->
_bEnabled = None
_commands = None
_commandsPath = None
_commandsStamp = None
_szReloadError = None
# <!-- custom: Survives hot reloads of the command module: mailbox folder, tick counters and the "py" command's namespace. (Claude code Fable 5.2) -->
state = {"mailbox": None, "ticks": {"gameUpdate": 0, "Update": 0, "screenUpdate": 0}, "py": {}, "served": 0, "loads": 0}

# <!-- custom: Ticks between checks of the command file's size and mtime.
# The embedded Python clock moves in coarse steps (SASPythonLogging records a 15-second trial where it stayed fixed), so intervals count ticks, not seconds. (Claude code Fable 5.2) -->
_RELOAD_CHECK_TICKS = 20


def _resolveEnabled():
	if gc.getDefineINT("SAS_PILOT_ON") > 0:
		return True
	path = SASAutoplayRequest._findRequestIni()
	if path is None:
		return False
	from configobj import ConfigObj
	config = ConfigObj(path, list_values=False, interpolation=False)
	for name in config.keys():
		if name.lower() == _SECTION.lower():
			for key in config[name].keys():
				if key.lower() == "on":
					return int(str(config[name][key]).strip()) > 0
	return False


def _fileStamp(path):
	# <!-- custom: Size and integer mtime, as civai's bridge does; float mtimes suffer the same coarse clock. (Claude code Fable 5.2) -->
	st = os.stat(path)
	return (st[6], st[8])


def _loadCommands():
	global _commands, _commandsStamp, _szReloadError
	stamp = _fileStamp(_commandsPath)
	if stamp == _commandsStamp:
		return
	_commandsStamp = stamp
	try:
		# <!-- custom: Civ4 caches the mod's Python at startup, so an ordinary import or reload() would return the code from launch (civai found the same); loading from the file picks up edits without restarting Civ4.
		# imp.load_source did that but left a SASPilotCommands.pyc beside the source, so compile the text ourselves into a fresh module. (Claude code Fable 5.2) -->
		handle = open(_commandsPath, "rb")
		source = handle.read().replace("\r\n", "\n")
		handle.close()
		module = imp.new_module(_COMMANDS_NAME)
		module.__file__ = _commandsPath
		# <!-- custom: Was the statement form exec ... in module.__dict__, which Ruff's modern parser cannot read; eval of an "exec" code object runs it the same way in Python 2.4 (Codex found it). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		eval(compile(source + "\n", _commandsPath, "exec"), module.__dict__)
		sys.modules[_COMMANDS_NAME] = module
		_commands = module
		_szReloadError = None
		CvUtil.pyPrintRecord("SAS_PILOT", "outcome=COMMANDS_LOADED revision=%d size=%d" % (_commands.PILOT_REVISION, stamp[0]))
	except:
		# <!-- custom: Keep the previous module serving and report the failure through status, so a syntax error in an edit does not cut the agent off. (Claude code Fable 5.2) -->
		_szReloadError = "".join(traceback.format_exception(*sys.exc_info()))
		CvUtil.pyPrintRecord("SAS_PILOT", "outcome=COMMANDS_LOAD_FAILED")
		sys.stderr.write(_szReloadError)


def _start():
	global _commandsPath
	# <!-- custom: The command file first sat in Assets/Python: saving an edit there made the running Civ4 reinitialize its Python, after which PythonErr.log filled with "Can't find module CvScreensInterface" and the mailbox went unanswered (2026-11-13).
	# Moving it to Assets/SASPilot did the same, so the EXE watches all of Assets; LLM_Helpers/game_runs, beside its client pilot.py, is outside it. (Claude code Fable 5.2) -->
	_commandsPath = os.path.join(BugPath.getModDir(), "LLM_Helpers", "game_runs", _COMMANDS_NAME + ".py")
	# <!-- custom: One folder per process, named by PID like our logs, so several clients can each be piloted. See KI#1081. (Claude code Fable 5.2) -->
	mailbox = os.path.join(BugPath.getRootDir(), "SASPilot", str(os.getpid()))
	if not os.path.isdir(mailbox):
		os.makedirs(mailbox)
	state["mailbox"] = mailbox
	_loadCommands()
	CvUtil.pyPrintRecord("SAS_PILOT", "outcome=STARTED mailbox=%s" % mailbox)


def _tick(szEvent):
	global _bEnabled
	if _bEnabled is None:
		_bEnabled = _resolveEnabled()
		if _bEnabled:
			_start()
	if not _bEnabled:
		return
	ticks = state["ticks"]
	ticks[szEvent] = ticks[szEvent] + 1
	# <!-- custom: Which event served the last request, so timings show whether game updates or per-frame updates set the pace. (Claude code Opus 5.5) -->
	state["lastTick"] = szEvent
	if (ticks["gameUpdate"] + ticks["Update"] + ticks["screenUpdate"]) % _RELOAD_CHECK_TICKS == 0:
		try:
			_loadCommands()
		except OSError:
			pass  # <!-- custom: the file is being rewritten; the next check reads it (Claude code Fable 5.2) -->
	if _commands is not None:
		_commands.poll(state, _szReloadError)


def isEnabled():
	# <!-- custom: False until the first game update has resolved the switch, which comes before any city can be founded. (Claude code Fable 5.2) -->
	return _bEnabled is True


def _safeTick(szEvent):
	# <!-- custom: Codex's review found that a pilot error in the screen update would skip the screen's own update; a forced error (2026-11-13) was contained there but reached PythonErr.log from the game update, where it could also stop handlers registered after it.
	# So every hook keeps its error here, logged once and shown by 'ping' as tickError; saving the command file reloads it and recovers. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		_tick(szEvent)
	except:
		if state.get("tickError") is None:
			state["tickError"] = szEvent + ": " + traceback.format_exc()
			CvUtil.pyPrintRecord("SAS_PILOT", "outcome=TICK_ERROR error=%s" % repr(state["tickError"]))


def onGameUpdate(argsList):
	_safeTick("gameUpdate")


def onLoad(argsList):
	# <!-- custom: Counts finished loads, which 'ping' reports, so the client can wait for the game it asked to load: after 'menu path=' the old game still answered ping as in game with its turn active, so waiting for an active turn returned before the load had begun, and commands ran on the old game (2026-11-13).
	# Counted whether or not the pilot is on, as the switch may not be resolved yet when a launch loads a save; one addition per load. (Claude code Opus 5.5) -->
	state["loads"] = state["loads"] + 1
	# <!-- custom: Holding popups began with the first request, after the load had already launched the save's popups: starting from the turn-105 save, the Oracle's free-tech chooser came up in the window instead of being held, and once the pilot chose through it, it stayed there, as the DLL cannot close a popup on display (2026-11-13). So hold from the load on.
	# The XML defines are loaded by now, so the switch can be read here. (Claude code Opus 5.5) -->
	# <!-- custom: Read here without setting _bEnabled or starting the mailbox, which stay with the first game update and _safeTick's guard: the first version started them here, where a bad pilot INI or a missing command file would have raised into the load handler with _bEnabled already set (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	try:
		bOn = _bEnabled
		if bOn is None:
			bOn = _resolveEnabled()
		if bOn and hasattr(gc.getGame(), "setSASPilotPopupsHeld"):
			gc.getGame().setSASPilotPopupsHeld(True)
	except:
		if state.get("tickError") is None:
			state["tickError"] = "OnLoad: " + traceback.format_exc()
			CvUtil.pyPrintRecord("SAS_PILOT", "outcome=TICK_ERROR error=%s" % repr(state["tickError"]))


def onUpdate(argsList):
	# <!-- custom: Fires per frame only when USE_ON_UPDATE_CALLBACK is 1 in PythonCallbackDefines.xml, which SAS leaves at 0; registered so that setting it is the only step needed to serve the mailbox between game updates. (Claude code Fable 5.2) -->
	_safeTick("Update")


def onScreenUpdate():
	# <!-- custom: Called from CvScreensInterface.update, which the EXE calls for the open Python screens, the main interface included, without the USE_ON_UPDATE_CALLBACK switch.
	# Serving only on game updates made every request wait about 250 ms; see "Speed" in README_Pilot.md.
	# The switch is left to game updates to resolve, so players pay one comparison here; errors are kept by _safeTick. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _bEnabled is not True:
		return
	_safeTick("screenUpdate")
