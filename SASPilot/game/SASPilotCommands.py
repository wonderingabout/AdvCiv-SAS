# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The commands SASPilot answers. SASPilot.py loads this file from disk and reloads it when it changes, so commands can be added or fixed while Civ4 runs; nothing imports it normally, and it lives outside Assets because the EXE reinitializes Python when a .py file there changes.
# Each command is a function cmd_<name>(args) taking the request's args dict and returning plain data (dict, list, str, number, bool, None), which poll() writes back as JSON.
# Commands see everything, without fog of war: SASPilot is a research and debugging tool for the active player, not a fair opponent as in civai.
# 'fog on=1' switches to what the active player's team knows, to play as a person would; see cmd_fog. (Claude code Fable 5.2)
# Python 2.4 has no json module, so the encoder and decoder below are our own. (Claude code Fable 5.2) -->

# <!-- custom: This API keeps growing, with plain fact commands (what a screen shows) and strategic ones that combine them (targets, settings' leader personalities); the user's rule (2026-11-15). Add commands freely, and keep them reusable:
# make a 'py' snippet a command once a later game would ask it again; build a new command on existing ones and shared helpers (targets calls relations and borders, settings and its possibleLeaders share _leaderFacts) rather than copying their code;
# reuse a screen's own code where a player-visible screen already decides what is known (timeline calls CvInfoScreen.getTimelineRecords), so SASPilot and the screen cannot disagree; keep to what the player may know unless the command is meant to be omniscient.
# Reuse data SAS already prepared for its screens too: settings ranks each leader's AI personality from the Sevopedia leader panel's predumped cache (SevoPediaLeaderCachePredumped, one of SAS's oldest additions, which CI keeps in step with the leader XML) rather than ranking the leaders again.
# A suggestion, not a rule: what a player needs to see, SASPilot likely needs too, and the reverse. When SASPilot needed a unit's fortified state (islands replay, 2026-11-15), the player saw it only as an icon, so both may gain from showing it as text; an agent looking for a SASPilot field can ask whether a player screen deserves it as well, and a new screen feature whether SASPilot should read it.
# The AI's own ratings, such as found values or the city governor's picks, are a reference to weigh, not the answer: they follow the AI's general rules, which may not fit the game at hand. At turn 57 of the islands replay (2026-11-15) AI_foundValue rated only one site on our island and gave 0 to every coastal corner near our cities, while the user's plan for an isolated island, claiming the coast by settling its corners with overlap accepted, favours exactly those; 'plansites legal=1' shows them beside the AI's value so the agent can choose.
# Measure before moving a command to C++: on 2026-11-15, with 48 players, most took 1 to 25 ms in game, and world dropped from 52 to 4 ms by finding its wonder buildings once rather than per city. (Claude code Opus 5.5) -->

# <!-- custom: os handles mailbox files, sys and traceback capture output and errors of a request; CvScreensInterface opens advisors and Sevopedia pages. (Claude code Fable 5.2) -->
from CvPythonExtensions import *
import os
# <!-- custom: re finds strings that need escaping for the JSON fast path. (Claude code Opus 5.5) -->
import re
import sys
# <!-- custom: time times each request for gameMs. (Claude code Opus 5.5) -->
import time
import traceback
import CvScreensInterface
# <!-- custom: CvScreenEnums for MAIN_INTERFACE, the screen 'resolution' reads its real size from, and for PEDIA_ITEM_KINDS, the Sevopedia's item kinds (2026-11-28). (Claude code Opus 5.5) -->
import CvScreenEnums
# <!-- custom: SASCurrentDefines reads the inherited defines the geography, deal and builds commands show, as main's python_define_reads_cached.py requires once it covered SASPilot/game (Codex's review of the 2026-11-27 merge); a leaf module, so no cycle. See KI#128.9. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
import SASCurrentDefines
# <!-- custom: SASBattleHistory holds the Military Advisor's Battles tab rows, saved in the game through BugData; 'battles' reads them.
# It is already loaded by the advisor's module, so importing it here runs no new code. (Claude code Opus 5.5) -->
import SASBattleHistory
# <!-- custom: Required types from game data use the shared strict lookup; optional tags and command input retain their own missing-tag handling. (GPT-6.2-Sol) -->
from SASUtils import getInfoTypeOrFail

gc = CyGlobalContext()

# <!-- custom: Bump when a command's name, arguments or reply changes, so a client can tell which bridge it talks to. (Claude code Fable 5.2) -->
PILOT_REVISION = 1

_state = None


# <!-- custom: JSON (Claude code Opus 5.5) -->

# <!-- custom: Writing 441 plots took 28 ms of the 31 ms the request spent in the game, against 3 ms to read them, as the loop below handled every character in Python (2026-11-13).
# Most strings are plain ASCII XML types and names, so they are copied whole when this finds nothing to escape; that brought the encoding of the same plots to a few ms. (Claude code Opus 5.5) -->
_reNeedsEscape = re.compile(r'[^\x20\x21\x23-\x5b\x5d-\x7e]')
_keyCache = {}


def _jsonString(value):
	if isinstance(value, str) and _reNeedsEscape.search(value) is None:
		return '"' + value + '"'
	if not isinstance(value, unicode):
		# <!-- custom: Game strings are Windows-1252 bytes when not unicode. (Claude code Fable 5.2) -->
		value = value.decode("cp1252", "replace")
	out = ['"']
	for ch in value:
		code = ord(ch)
		if ch == u'"':
			out.append('\\"')
		elif ch == u"\\":
			out.append("\\\\")
		elif ch == u"\n":
			out.append("\\n")
		elif ch == u"\r":
			out.append("\\r")
		elif ch == u"\t":
			out.append("\\t")
		elif code < 32 or code > 126:
			out.append("\\u%04x" % code)
		else:
			out.append(str(ch))
	out.append('"')
	return "".join(out)


class RawJson:
	# <!-- custom: JSON already written by the DLL, such as the plots from CyGame.getSASPilotPlotsJson, passed into the reply as it is. (Claude code Opus 5.5) -->
	def __init__(self, text):
		self.text = text


def toJson(value):
	if value is None:
		return "null"
	if isinstance(value, RawJson):
		return value.text
	if value is True:
		return "true"
	if value is False:
		return "false"
	if type(value) in (int, long):
		return str(value)
	if isinstance(value, (int, long)):
		# <!-- custom: A Boost.Python enum is an int subclass whose str() is its name: 'info' wrote "getCommandType":COMMAND_UPGRADE, which no JSON reader accepts, so enums go out as quoted names. (Claude code Fable 5.2) -->
		return _jsonString(str(value))
	if isinstance(value, float):
		text = repr(value)
		if "n" in text:
			# <!-- custom: inf and nan are not JSON. (Claude code Fable 5.2) -->
			return _jsonString(text)
		return text
	if isinstance(value, (str, unicode)):
		return _jsonString(value)
	if isinstance(value, (list, tuple)):
		return "[" + ",".join([toJson(item) for item in value]) + "]"
	if isinstance(value, dict):
		keys = value.keys()
		keys.sort()
		parts = []
		for key in keys:
			# <!-- custom: Only plain str keys are cached: equal keys of other types, such as 1, True and 1.0, would share one entry and print as the first one seen (found by Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if type(key) is str:
				szKey = _keyCache.get(key)
				if szKey is None:
					szKey = _jsonString(key) + ":"
					_keyCache[key] = szKey
			else:
				szKey = _jsonString(str(key)) + ":"
			parts.append(szKey + toJson(value[key]))
		return "{" + ",".join(parts) + "}"
	# <!-- custom: A Cy object or enum left in a result is shown by its repr rather than failing the whole reply. (Claude code Fable 5.2) -->
	return _jsonString(repr(value))


def _unescapeStrings(value):
	if isinstance(value, str):
		if "\\u" in value:
			return value.decode("unicode_escape")
		return value
	if isinstance(value, list):
		return [_unescapeStrings(item) for item in value]
	if isinstance(value, dict):
		result = {}
		for key in value.keys():
			result[str(key)] = _unescapeStrings(value[key])
		return result
	return value


def fromJson(text):
	# <!-- custom: JSON written by the client (ASCII, from json.dumps) is also a Python literal once true, false and null are names, so eval with no builtins reads it; a \uXXXX escape stays literal in a Python 2 str and is decoded afterwards. (Claude code Fable 5.2) -->
	return _unescapeStrings(eval(text, {"__builtins__": {}, "true": True, "false": False, "null": None}))


# <!-- custom: Mailbox (Claude code Opus 5.5) -->

def _writeAtomic(path, text):
	temp = path + ".tmp"
	handle = open(temp, "wb")
	handle.write(text)
	handle.close()
	if os.path.exists(path):
		os.remove(path)
	os.rename(temp, path)


class _ErrorTee:
	# <!-- custom: Keeps this client's Python error output for 'pyerrors', and passes every write on to the stream it wraps, so PythonErr.log gets it as before.
	# Needed on 2026-11-20: PythonErr.log is one file for every client (KI#1081), and a Civ4 stuck while exiting kept it locked, so no later client's traceback reached it and SASPilotUISweep.py could not see one.
	# The methods use only their instance, no module global or builtin, as a reload of this file frees the old module's globals while sys.stderr may still hold this object. (Claude code Opus 5.5) -->
	def __init__(self, stream, lines, count):
		self.stream = stream
		self.lines = lines
		self.count = count

	# <!-- custom: Kept before it is passed on, so a sink that raises cannot lose the write this was added to catch (Codex's review); the wrapped stream's own error still reaches the caller. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def write(self, text):
		try:
			self.lines.append(text)
			self.count[0] = self.count[0] + 1
			if self.lines.__len__() > 400:
				del self.lines[0]
		except:
			pass
		self.stream.write(text)

	def flush(self):
		try:
			self.stream.flush()
		except:
			pass


def _installErrorTee(state):
	# <!-- custom: Checked every tick, as the EXE can replace sys.stderr after CvUtil set it (CvUtil's note); a tee from an earlier version of this file is kept, its state being the same lists. (Claude code Opus 5.5) -->
	if sys.stderr.__class__.__name__ == "_ErrorTee":
		return
	sys.stderr = _ErrorTee(sys.stderr, state.setdefault("pyErrors", []), state.setdefault("pyErrorWrites", [0]))


def poll(state, szReloadError):
	# <!-- custom: Called on every tick; one directory listing when no request waits. (Claude code Fable 5.2) -->
	global _state
	_state = state
	state["reloadError"] = szReloadError
	_installErrorTee(state)
	_loadUI()
	if state.get("uiInstalled") and sys.modules.has_key(_UI_NAME):
		sys.modules[_UI_NAME]._tick()
	mailbox = state["mailbox"]
	if not state.get("helloWritten"):
		_writeAtomic(os.path.join(mailbox, "hello.json"), toJson({"pid": os.getpid(), "pilotRevision": PILOT_REVISION, "session": state.get("session")}))
		state["helloWritten"] = True
		# <!-- custom: Hold popups back from the first request on; a DLL without the binding leaves them in the window. (Claude code Fable 5.2) -->
		if hasattr(gc.getGame(), "setSASPilotPopupsHeld"):
			gc.getGame().setSASPilotPopupsHeld(True)
	names = [name for name in os.listdir(mailbox) if name.startswith("req_") and name.endswith(".json")]
	if not names:
		return
	names.sort()
	for name in names:
		path = os.path.join(mailbox, name)
		# <!-- custom: gameMs is the game-side time from reading the request through encoding the reply, so the client can tell it apart from the wait for the next tick; time.clock is the high-resolution timer on Windows in Python 2.4. (Claude code Opus 5.5) -->
		fStart = time.clock()
		# <!-- custom: Claimed by renaming req_ to run_ before it runs, and run_ removed only once the reply is written.
		# The first version read and deleted the request first, so a client that timed out could not tell a command never started, which is safe to retry, from one already running, which a retry would repeat (ChatGPT's review, 2026-11-14).
		# SASPilotClient.py's timeout now withdraws only a request still named req_. (Claude code Opus 5.5 + ChatGPT-5.6-Sol) -->
		# <!-- custom: Read the atomically published request before claiming it.
		# The first claim renamed, then read: a transient read error after the claim stranded the request under run_, where the poll never retries it, so the client waited out its timeout (the late-game Sevopedia sweep on the Hammurabi T403 save, 2026-11-27).
		# If the client withdraws it before the rename, the rename fails and nothing runs. (GPT-6.2-Sol + Claude code Opus 5.5) -->
		running = os.path.join(mailbox, "run_" + name[4:])
		try:
			handle = open(path, "rb")
			try:
				text = handle.read()
			finally:
				handle.close()
			os.rename(path, running)
		except (IOError, OSError):
			continue  # <!-- custom: still being written, withdrawn or already taken; the next tick retries (Claude code Fable 5.2) -->
		reply = _serve(text)
		state["served"] = state["served"] + 1
		iPyErrorWritesThrough = reply.pop("_pyErrorWritesThrough", None)
		newsSnapshot = reply.pop("_newsSnapshot", None)
		szReply = toJson(reply)
		szReply = szReply[:-1] + ',"gameMs":' + repr((time.clock() - fStart) * 1000.0) + ',"tick":"' + state.get("lastTick", "") + '"}'
		_writeAtomic(os.path.join(mailbox, "rep_" + name[4:]), szReply)
		# <!-- custom: Marked as reported only once the reply is written: marked while building it, a failed write lost the errors from the next reply too (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if iPyErrorWritesThrough is not None:
			state["pyErrorWritesReported"] = iPyErrorWritesThrough
		# <!-- custom: The news's baseline likewise moves only once the reply carrying it is written. (Claude code Opus 5.5) -->
		if newsSnapshot is not None:
			state["newsSnapshot"] = newsSnapshot
		try:
			os.remove(running)
		except OSError:
			pass  # <!-- custom: the reply is out; a run_ file left behind only means the claim was not cleaned up (Claude code Opus 5.5) -->


# <!-- custom: SASPilotUI.py beside this file holds the ui* commands, loaded as SASPilot.py loads this one: compiled from the file, again whenever it changes, and once more after this module reloads (_siblingStamps starts over). (Claude code Opus 5.5) -->
_UI_NAME = "SASPilotUI"
# <!-- custom: SASPilotNews.py beside it builds the news every reply carries, split from this file as a concept of its own that grows (the user's suggestion, 2026-11-28); loaded the same way, but only when a reply is built, so idle ticks do not check a second file. (Claude code Opus 5.5) -->
_NEWS_NAME = "SASPilotNews"
# <!-- custom: Each sibling file's (size, modification time) when it was last read; this was _uiStamp, the UI's alone, before SASPilotNews.py shared the loader. (Claude code Opus 5.5) -->
_siblingStamps = {}


def _readSibling(szName, szErrorKey):
	# <!-- custom: The source of the sibling file szName when it changed since it was last read, else None; a read error goes to _state[szErrorKey].
	# Codex's review found two flaws in the first version: os.stat ran outside the error handler before any request was served, so a missing or briefly locked SASPilotUI.py would have stopped every command, and the stamp was taken before the read, so a failed read waited for the next edit.
	# A read error now leaves the stamp alone and is retried on the next tick; only a file that was read is marked, whether it then loaded or failed to compile. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	path = os.path.join(os.path.dirname(__file__), szName + ".py")
	try:
		stat = os.stat(path)
		stamp = (stat.st_size, stat.st_mtime)
		if stamp == _siblingStamps.get(szName):
			return None
		handle = open(path, "rb")
		source = handle.read().replace("\r\n", "\n")
		handle.close()
	except (IOError, OSError):
		# <!-- custom: A read error forgets the stamp, so the file is compiled again once it reads, and the read error then gives way to that load's own result.
		# The UI loader first cleared the read error when the same file read again, as it otherwise blocked the ui commands until the next edit (Codex's review); but after a compile error, that cleared the compile error too without compiling, so a broken file went unreported (Codex reproduced it, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		_state[szErrorKey] = "%s cannot be read: %s" % (path, sys.exc_info()[1])
		if _siblingStamps.has_key(szName):
			del _siblingStamps[szName]
		return None
	_siblingStamps[szName] = stamp
	return (path, source)


def _compileSibling(szName, path, source):
	# <!-- custom: imp builds the module from its file.
	# Imported here, as the game's Python 2.4 has it but the modern Python the CI tests load this file with does not (removed in 3.12): a top-level import broke all 9 tests of test_saspilot_graphs.py. (Claude code Opus 5.5) -->
	import imp
	module = imp.new_module(szName)
	module.__file__ = path
	eval(compile(source + "\n", path, "exec"), module.__dict__)
	module.saspilot = sys.modules[__name__]
	return module


# <!-- custom: The command names each sibling module registered, so a reload takes away the commands its new version no longer has. (Claude code Opus 5.5) -->
_siblingCommands = {}


def _siblingExports(module):
	# <!-- custom: A sibling's commands and help, checked before the module replaces the loaded one, so a file that compiles but lacks _HELP fails its own load rather than every later request (Codex reproduced it, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	helpTexts = getattr(module, "_HELP", None)
	if not isinstance(helpTexts, dict):
		raise ValueError("%s has no _HELP dict" % module.__name__)
	commands = [szName for szName in dir(module) if szName.startswith("cmd_")]
	# <!-- custom: A command another file already has is refused: a sibling exporting cmd_endturn replaced the core's, and deleted it once the sibling dropped the export (Codex reproduced it in Python 2.4, 2026-11-28); no files clash today. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for szCommand in commands:
		if not globals().has_key(szCommand) or szCommand in _siblingCommands.get(module.__name__, []):
			continue
		owners = [szOwner for szOwner in _siblingCommands.keys() if szCommand in _siblingCommands[szOwner]]
		raise ValueError("%s defines %s, which %s already has" % (module.__name__, szCommand, (owners or [__name__])[0]))
	return (commands, helpTexts)


def _registerSibling(szName, module, exports):
	# <!-- custom: Replaces the sibling's commands and help as one: a reload first only added, so a command removed from the file stayed callable, pointing at the previous module, whose globals Python had cleared (Codex reproduced it in Python 2.4, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	(commands, helpTexts) = exports
	for szCommand in _siblingCommands.get(szName, []):
		if globals().has_key(szCommand):
			del globals()[szCommand]
		if _HELP.has_key(szCommand[len("cmd_"):]):
			del _HELP[szCommand[len("cmd_"):]]
	for szCommand in commands:
		globals()[szCommand] = getattr(module, szCommand)
	_HELP.update(helpTexts)
	_siblingCommands[szName] = commands
	sys.modules[szName] = module


def _loadNews():
	# <!-- custom: A failed load keeps the previous news module, and the error goes in each reply's newsError, as for the ui commands. (Claude code Opus 5.5) -->
	read = _readSibling(_NEWS_NAME, "newsLoadError")
	if read is not None:
		try:
			module = _compileSibling(_NEWS_NAME, read[0], read[1])
		except Exception:
			_state["newsLoadError"] = "".join(traceback.format_exception(*sys.exc_info()))
		else:
			_state["newsLoadError"] = None
			sys.modules[_NEWS_NAME] = module
	return sys.modules.get(_NEWS_NAME)


# <!-- custom: The files beside this one that hold commands by topic, the parts of this file moved out since 2026-11-28: SASPilotCatalog.py the commands reading the game's definitions ('info', 'types', 'pedia'), SASPilotDiplomacy.py those talking and trading with the other players, SASPilotCities.py those running a city, SASPilotUnits.py those commanding units, SASPilotMap.py the map as the player knows it, SASPilotExpansion.py where to explore and settle, SASPilotOptions.py Civ4's and BUG's settings.
# They are grouped by concept, not by the game's screens or by how a player or Firaxis divides them (the user, 2026-11-28): diplomacy and trade share a module although the game splits them between the diplomacy screen and the Foreign Advisor, and a city's production and citizens share one.
# Each is loaded before a request is served, as its commands and help must be there when the request is checked; SASPilotUI.py, loaded every tick for its hooks, is apart. (Claude code Opus 5.5) -->
_CATALOG_NAME = "SASPilotCatalog"
_COMMAND_SIBLINGS = (_CATALOG_NAME, "SASPilotDiplomacy", "SASPilotCities", "SASPilotUnits", "SASPilotMap", "SASPilotExpansion", "SASPilotOptions")


def _loadCommandSibling(szName):
	# <!-- custom: Loads or reloads a command sibling if its file changed, replacing its commands and help in this module; a failed load keeps the previous version, and its commands then report the error, as the ui commands do, in _state[szName + "LoadError"].
	# It never raises, so a broken sibling stops only its own commands, not every request. (Claude code Opus 5.5) -->
	szErrorKey = szName + "LoadError"
	read = _readSibling(szName, szErrorKey)
	if read is not None:
		try:
			module = _compileSibling(szName, read[0], read[1])
			exports = _siblingExports(module)
		except Exception:
			_state[szErrorKey] = "".join(traceback.format_exception(*sys.exc_info()))
		else:
			_state[szErrorKey] = None
			_registerSibling(szName, module, exports)
	return sys.modules.get(szName)


def _loadCommandSiblings():
	for szName in _COMMAND_SIBLINGS:
		_loadCommandSibling(szName)


def _catalog():
	# <!-- custom: The catalog module for code that needs its helpers, such as SASPilotUI's Sevopedia kinds and the 'py' namespace's describe; raises if it never loaded. (Claude code Opus 5.5) -->
	module = _loadCommandSibling(_CATALOG_NAME)
	if module is None:
		raise ValueError("SASPilotCatalog.py failed to load:\n%s" % _state.get(_CATALOG_NAME + "LoadError"))
	return module


def _command(szName):
	# <!-- custom: A command that lives in a sibling file, such as 'relations' in SASPilotDiplomacy.py, for code here that calls it: the loader adds the siblings' commands to this module at run time, which static checks cannot see, so 'cmd_relations(args)' here read as an undefined name to star_import_names.py (2026-11-28); this says the command is looked up, and names a sibling that failed to load. (Claude code Opus 5.5) -->
	handler = globals().get("cmd_" + szName)
	if handler is None:
		_loadCommandSiblings()
		handler = globals().get("cmd_" + szName)
	if handler is None:
		errors = ["%s: %s" % (szSibling, _state.get(szSibling + "LoadError")) for szSibling in _COMMAND_SIBLINGS if _state.get(szSibling + "LoadError")]
		raise ValueError("no command %s is loaded%s" % (szName, errors and "; " + "; ".join(errors) or ""))
	# <!-- custom: Refused like a direct request when its sibling's last reload failed: Codex simulated a syntax error in SASPilotExpansion.py, and a direct 'plansites' was refused while 'reminders' still ran the old handler through here (2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for szSibling in _COMMAND_SIBLINGS:
		if hasattr(sys.modules.get(szSibling), "cmd_" + szName) and _state.get(szSibling + "LoadError"):
			raise ValueError("%s.py failed to load:\n%s" % (szSibling, _state[szSibling + "LoadError"]))
	return handler


def _describe(target):
	# <!-- custom: The catalog's describe for the 'py' namespace, resolved at each call. (Claude code Opus 5.5) -->
	return _catalog().describe(target)


def _loadUI():
	read = _readSibling(_UI_NAME, "uiLoadError")
	if read is None:
		return
	# <!-- custom: A failed load keeps the previous ui commands and is reported by each ui command, so a syntax error in an edit does not stop the other commands. (Claude code Opus 5.5) -->
	try:
		module = _compileSibling(_UI_NAME, read[0], read[1])
		exports = _siblingExports(module)
		# <!-- custom: Kept alive before its wrappers go on the screen class, and for good: the first test kept no reference to the module, and Python 2 set the freed module's globals to None, so every recorded call failed with "'NoneType' object is not callable", 479 popups from the main interface's own drawing.
		# Every loaded version stays in this list, as a wrapper left by a failed or partial install could still point to it (Codex's review); a few modules per session. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		_state.setdefault("uiModules", []).append(module)
		module._reloaded()
	except Exception:
		_state["uiLoadError"] = "".join(traceback.format_exception(*sys.exc_info()))
		return
	_state["uiLoadError"] = None
	_registerSibling(_UI_NAME, module, exports)


def aroundMainInterfaceBuild(state, bBefore):
	# <!-- custom: Called by SASPilot.py around the main interface's build at game start, possibly before the first poll, so the state is taken here; SASPilotUI records the build. (Claude code Opus 5.5) -->
	global _state
	_state = state
	# <!-- custom: Loaded before the build only, so the cleanup after it runs in the module that started recording (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if bBefore:
		_loadUI()
	ui = sys.modules.get(_UI_NAME)
	if ui is not None:
		ui._aroundMainBuild(bBefore)


def _checkedHandler(name, args):
	if str(name).startswith("ui") and _state.get("uiLoadError"):
		raise ValueError("SASPilotUI.py failed to load:\n%s" % _state["uiLoadError"])
	for szSibling in _COMMAND_SIBLINGS:
		if hasattr(sys.modules.get(szSibling), "cmd_" + str(name)) and _state.get(szSibling + "LoadError"):
			raise ValueError("%s.py failed to load:\n%s" % (szSibling, _state[szSibling + "LoadError"]))
	# <!-- custom: The command's function, once its name and argument keys are checked: 'civics adopt=CIVIC_THEOCRACY' returned the civics list as if it had worked, as the command takes set= and the unknown key was ignored (fog-on playthrough, turn 131, 2026-11-13). A key the command's help does not list is refused; player and fog are read by shared helpers for any command.
	# Used by 'batch' and 'profile' too, which first called handlers directly and so skipped the check (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	handler = globals().get("cmd_" + str(name))
	if handler is None:
		raise ValueError("unknown command %r; 'help' lists the commands" % name)
	allowed = _allowedArgs(name)
	unknown = [key for key in args.keys() if key not in allowed]
	if unknown:
		# <!-- custom: A hint for the keys agents guess first: 'uiopen screen=victory' and 'uipress name=members' were each refused with the whole key list, the right keys being name= and widget= or text= (2026-11-21). (Claude code Opus 5.5) -->
		hints = []
		for key in unknown:
			for guess in _ARG_GUESSES.get(key, ()):
				if guess in allowed:
					hints.append("%s= for %s=" % (guess, key))
		szHint = ""
		if hints:
			szHint = "; did you mean " + ", ".join(hints) + "?"
		raise ValueError("%s takes no %s; it takes: %s%s" % (name, ", ".join(unknown), ", ".join(allowed) or "nothing", szHint))
	# <!-- custom: A required argument left out is named before the command runs: 'emphasize city=Babylon' and 'specialist city=Babylon' answered with a bare KeyError: 'type' (2026-11-28).
	# Listed per command rather than caught as KeyError after the call, which would hide a KeyError raised by a bug inside a handler (Codex's review); commands with alternative arguments check their own. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	missing = [key for key in _REQUIRED_ARGS.get(str(name), ()) if not args.has_key(key)]
	if missing:
		raise ValueError("%s needs %s; it takes: %s" % (name, ", ".join(missing), ", ".join(allowed)))
	return handler


# <!-- custom: Arguments a command cannot run without, as its help lists them. (Claude code Opus 5.5) -->
_REQUIRED_ARGS = {"specialist": ("type",), "emphasize": ("type",), "shore": ("x", "y")}


# <!-- custom: The keys agents tried in place of a command's own, with what that command may take instead; used only to word the refusal above. (Claude code Opus 5.5) -->
# <!-- custom: "name" also maps to "path": 'save name=...' was refused with no hint (save/reload test, 2026-11-22). (Claude code Opus 5.5) -->
_ARG_GUESSES = {"screen": ("name",), "name": ("widget", "text", "path"), "tab": ("widget", "text"), "button": ("widget", "text"), "file": ("out", "save"), "path": ("out", "save")}


def _allowedArgs(name):
	# <!-- custom: The argument names from the end of the command's help, "args: unit, x, y (default ...), player."; a help without "args:" takes none but the shared ones.
	# The first version left such commands unchecked (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	szHelp = _HELP.get(name, "")
	iStart = szHelp.rfind("args:")
	szArgs = ""
	if iStart >= 0:
		szArgs = szHelp[iStart + len("args:"):]
	while re.search(r"\([^()]*\)", szArgs):
		szArgs = re.sub(r"\([^()]*\)", "", szArgs)
	szArgs = szArgs.split(".")[0]
	names = []
	for szPart in szArgs.split(","):
		match = re.match(r"\s*([A-Za-z_0-9]+)", szPart)
		# <!-- custom: sas-ci-string-compare-exemption: The launch settings use a literal none marker. (GPT-6.2-Sol) -->
		if match is not None and match.group(1) != "none":
			names.append(match.group(1))
	for szShared in ("player", "fog"):
		if szShared not in names:
			names.append(szShared)
	return names


def _applyLaunchRole():
	# <!-- custom: The role 'SASPilotClient.py start --role' wrote in the per-run INI ([SASPilot] Role), applied and locked once, before the first request is served, so no command can run under another role first (Codex's review, round 33).
	# Read here rather than in the SASPilot.py loader, which cannot be changed while Civ4 runs; the loader's own INI reader is reused.
	# A role the bridge does not know is refused loudly on every request rather than ignored. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _state.get("launchRoleRead"):
		return
	import SASPilot
	szRole = SASPilot._pilotSection().get("role")
	if szRole:
		if szRole not in _ROLE_ALLOWED:
			raise ValueError("the per-run INI's [SASPilot] Role is %s, which is not play, assist or all" % szRole)
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox uses stable role keys. (GPT-6.2-Sol) -->
		if szRole != "all":
			_state["role"] = szRole
			_state["fog"] = True
		_state["roleLocked"] = True
	_state["launchRoleRead"] = True


def _serve(text):
	reply = {"ok": False}
	bAccepted = False
	requestArgs = {}
	try:
		request = fromJson(text)
		reply["id"] = request.get("id")
		# <!-- custom: Codex's review simulated a stale req_ that SASPilot._start could not delete from a recycled PID's folder, and the new game ran it.
		# A launched session refuses any request not carrying its own session ID, which SASPilotClient.py reads from hello.json; without a session (SAS_PILOT_ON with no per-run INI) every request is served, as before. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if _state.get("session") and request.get("session") != _state.get("session"):
			raise ValueError("request %s is for session %s, not this game's %s; it was not run" % (request.get("id"), request.get("session"), _state.get("session")))
		name = request["cmd"]
		args = request.get("args") or {}
		_applyLaunchRole()
		bAccepted = True
		_loadCommandSiblings()
		handler = _checkedHandler(name, args)
		_checkRole(name, args)
		# <!-- custom: The request's fog counts for the news only once the role allows the request: taken before _checkRole, a play session's refused fog=0 gave a full-view rank in the refusal's news (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		requestArgs = args
		# <!-- custom: On unless 'look follow=0' turns it off: the user watching the Orleans attack (turn 129 of the turn-0 game, 2026-11-14) asked for the camera to follow without anyone having to switch it on each session. (Claude code Opus 5.5) -->
		if _state.get("follow", True):
			_followOrder(name, args)
		reply["result"] = handler(args)
		reply["ok"] = True
	except Exception:
		kind, error, trace = sys.exc_info()
		reply["error"] = "%s: %s" % (getattr(kind, "__name__", str(kind)), error)
		reply["traceback"] = "".join(traceback.format_exception(kind, error, trace))
	game = gc.getGame()
	reply["gameTurn"] = game.getGameTurn()
	_reportNewErrors(reply)
	# <!-- custom: Only for a request of this session, once its launch role is applied: a stale request from another session got news too, and could set a baseline without the role's fog, as the role is applied after the session check (Codex reproduced it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if bAccepted:
		_reportNews(reply, requestArgs)
	return reply


def _reportNews(reply, requestArgs):
	# <!-- custom: The news since the previous reply, built by SASPilotNews.py beside this file, which says what it holds and why. (Claude code Opus 5.5) -->
	# <!-- custom: No game to compare while one loads: as 'ping' does, nothing is reported before an active player and the final initialization; the first version raised newsError on every ping of a load (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	game = gc.getGame()
	if game.getActivePlayer() < 0 or not game.isFinalInitialized():
		return
	# <!-- custom: A failure here is reported beside the command's own result rather than replacing it, as the command itself ran. (Claude code Opus 5.5) -->
	try:
		news = _loadNews()
		if _state.get("newsLoadError"):
			reply["newsError"] = "SASPilotNews.py failed to load: %s" % _state["newsLoadError"]
		if news is not None:
			news.report(reply, requestArgs)
	except Exception:
		reply["newsError"] = "%s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1])


def _reportNewErrors(reply):
	# <!-- custom: Any reply carries the Python errors this client wrote since the previous reply, so an agent learns of one without thinking to read the log (the user's idea, 2026-11-28).
	# Found by the user that day: the options screen's refresh raised after 'resolution' (KI#123.7), code the EXE ran between requests, so no reply showed it while the agent went on testing. (Claude code Opus 5.5) -->
	count = _state.setdefault("pyErrorWrites", [0])
	iSeen = _state.get("pyErrorWritesReported", 0)
	# <!-- custom: 'pyerrors clear=1' sets the count back to 0. (Claude code Opus 5.5) -->
	if count[0] < iSeen:
		iSeen = 0
	if count[0] > iSeen:
		rows = [row for row in _errorText(_state.setdefault("pyErrors", [])[-(count[0] - iSeen):]).split(u"\n") if row.strip()]
		reply["pythonErrors"] = {"writes": count[0] - iSeen, "lines": rows[-12:]}
	reply["_pyErrorWritesThrough"] = count[0]


def _errorText(writes):
	# <!-- custom: The writes as one Unicode text, which toJson escapes: encoded to UTF-8 bytes first, as both this and 'pyerrors' did, the JSON writer read them as Windows-1252 and turned an e acute into two characters (Codex's review, 2026-11-28).
	# A byte write is decoded as UTF-8 when it is valid, else with Windows' ANSI code page (mbcs), in which the game's French error messages come. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	parts = []
	for part in writes:
		if not isinstance(part, unicode):
			try:
				part = part.decode("utf-8")
			except UnicodeError:
				part = part.decode("mbcs", "replace")
		parts.append(part)
	return u"".join(parts)


# <!-- custom: Lookups (Claude code Opus 5.5) -->

def _typeName(info):
	if info is None:
		return None
	return info.getType()


def _typeOrNone(getter, iType):
	if iType is None or iType < 0:
		return None
	return getter(iType).getType()


# <!-- custom: Keep -1 for optional XML types and command arguments that need their own error or fallback. (GPT-6.2-Sol) -->
def _findOptionalInfoType(szType):
	return gc.getInfoTypeForString(szType)


def _infoIndex(szType):
	iType = _findOptionalInfoType(szType)
	if iType < 0:
		raise ValueError("unknown XML type %s" % szType)
	return iType


def _typedIndex(szType, szPrefix, iNum, getter):
	# <!-- custom: _infoIndex resolves any XML type, so 'specialist type=UNIT_WARRIOR' would have passed a unit's index to the DLL as a specialist (Codex's review); check that the type belongs to the kind the command takes, by its entry's own type. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	iType = _infoIndex(szType)
	if iType >= iNum or getter(iType).getType() != szType:
		raise ValueError("%s is not a %s type" % (szType, szPrefix))
	return iType


def _enum(enumClass, szName):
	# <!-- custom: Enum arguments are passed by their name, e.g. MISSION_FORTIFY, and resolved on the Boost.Python enum class. (Claude code Fable 5.2) -->
	if isinstance(szName, (int, long)):
		return szName
	value = getattr(enumClass, szName, None)
	if value is None:
		raise ValueError("unknown %s %s" % (enumClass.__name__, szName))
	return value


def _enumName(enumClass, value):
	# <!-- custom: The reverse of _enum, for enums without XML info; a NO_ value gives null, as _typeOrNone does for XML types. (Claude code Opus 5.5) -->
	iValue = int(value)
	if iValue < 0:
		return None
	for name in dir(enumClass):
		if name.isupper() and not name.startswith("NUM_") and not name.startswith("NO_") and int(getattr(enumClass, name)) == iValue:
			return name
	return iValue


def _activePlayerId():
	iPlayer = gc.getGame().getActivePlayer()
	if iPlayer < 0:
		raise ValueError("no game is running (no active player)")
	return iPlayer


def _checkedPlayerId(value):
	# <!-- custom: gc.getPlayer indexes the native player array without a check, so -2 read before it in a Release DLL; 'contact' already checked its ID, while 'trade', 'propose' and every player= argument did not (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iPlayer = int(value)
	if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS() or not gc.getPlayer(iPlayer).isAlive():
		raise ValueError("no living player %d" % iPlayer)
	return iPlayer


def _playerId(args):
	iPlayer = args.get("player")
	if iPlayer is None:
		return _activePlayerId()
	return _checkedPlayerId(iPlayer)


def _player(args):
	return gc.getPlayer(_playerId(args))


def _units(player):
	result = []
	(unit, iterator) = player.firstUnit(False)
	while unit:
		if not unit.isNone():
			result.append(unit)
		(unit, iterator) = player.nextUnit(iterator, False)
	return result


def _cities(player):
	result = []
	(city, iterator) = player.firstCity(False)
	while city:
		if not city.isNone():
			result.append(city)
		(city, iterator) = player.nextCity(iterator, False)
	return result


def _unit(args):
	player = _player(args)
	# <!-- custom: 'sites' without unit= first failed as a bare KeyError: 'unit' (islands replay, 2026-11-15); name the missing argument instead. (Claude code Opus 5.5) -->
	if not args.has_key("unit"):
		raise ValueError("this command needs unit=<id>; 'units' lists ours")
	unit = player.getUnit(int(args["unit"]))
	if unit is None or unit.isNone():
		raise ValueError("player %d has no unit %s" % (player.getID(), args["unit"]))
	return unit


def _city(args):
	player = _player(args)
	key = args["city"]
	# <!-- custom: str(key) raised UnicodeEncodeError on a Portuguese city name with a non-ASCII letter, which broke 'turn' through its homeUnknown reminder (JOAO turn-112 save, 2026-11-22); unicode() takes both kinds of string. (Claude code Opus 5.5) -->
	if isinstance(key, (int, long)) or unicode(key).isdigit():
		city = player.getCity(int(key))
		if city is not None and not city.isNone():
			return city
	for city in _cities(player):
		if city.getName().lower() == unicode(key).lower():
			return city
	raise ValueError("player %d has no city %s" % (player.getID(), key))


def _plot(args):
	plot = CyMap().plot(int(args["x"]), int(args["y"]))
	if plot is None or plot.isNone():
		raise ValueError("no plot at %s,%s" % (args["x"], args["y"]))
	return plot


def _yields(getter):
	# <!-- custom: Boost.Python rejects a plain int where the C++ signature has an enum (CyPlot.getYield raised ArgumentError), so convert with the enum class. (Claude code Fable 5.2) -->
	return [getter(YieldTypes(i)) for i in range(YieldTypes.NUM_YIELD_TYPES)]


# <!-- custom: Views (Claude code Opus 5.5) -->

def _unitBrief(unit, iFogTeam=None):
	# <!-- custom: The 'units' list and the units inside plots come from appendSASPilotUnitJson in CvGameInterface.cpp instead; keep the two writers' fields the same. (Claude code Opus 5.5) -->
	# <!-- custom: experience, level and the unit's own name added as in the C++ writer (2026-11-14). (Claude code Opus 5.5) -->
	result = {"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "owner": unit.getOwner(), "movesLeft": unit.movesLeft(), "damage": unit.getDamage(), "group": unit.getGroupID(), "experience": unit.getExperience(), "level": unit.getLevel()}
	if unit.getNameNoDesc():
		result["name"] = unit.getNameNoDesc()
	# <!-- custom: The unit's state as in the C++ writer (2026-11-15): for every unit in the full view, and for our own units under fog, as the game shows rivals' states nowhere.
	# iFogTeam is the request's (_fogTeam(args)); the first version read the session switch alone, so 'fog=1' on one request still gave a rival's orders, which the C++ writer omits (Codex's review).
	# Callers without a request leave it None for the session switch. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if iFogTeam is None:
		iFogTeam = _fogTeam({})
	group = unit.getGroup()
	if iFogTeam < 0 or unit.getTeam() == iFogTeam:
		result["activity"] = _enumName(ActivityTypes, group.getActivityType())
		result["automate"] = _enumName(AutomateTypes, group.getAutomateType())
		result["fortifyTurns"] = unit.getFortifyTurns()
		result["promotionReady"] = bool(unit.isPromotionReady())
		# <!-- custom: Promoting heals half the damage (CvUnit::promotionHeal, leader promotions excepted), and the pick can wait for the opponent: at turn 17 of the 2026-11-19 validation run the Warrior took Combat I at 17 damage, healing 8, which the user pointed out was the cheap use of both. (Claude code Opus 5.5) -->
		if result["promotionReady"]:
			result["promotionHealsNow"] = unit.getDamage() * 50 / 100
			result["promotionAdvice"] = "promoting heals half the damage and the pick can wait: hold it while healthy and nothing is to fight, use it after a hard fight or just before a known matchup, as plans change (a planned city assault can turn into a field battle, or the reverse)"
		result["mission"] = None
		if group.getLengthMissionQueue() > 0:
			result["mission"] = gc.getMissionInfo(group.getMissionType(0)).getType()
			dest = _headMissionPlot(group, iFogTeam)
			if dest is not None:
				result["missionPlot"] = [dest.getX(), dest.getY()]
	return result


def _headMissionPlot(group, iViewTeam):
	# <!-- custom: As getSASHeadMissionPlot in CvGameCoreUtils.cpp: the head mission target, Move To and Route To by their plot, Move To Unit by the target unit plot only while iViewTeam (-1: always) sees it; lastMissionPlot gave the end of the queue and the live position of a rival out of sight (Codex's review, 2026-11-15). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	eMission = group.getMissionType(0)
	if eMission in (MissionTypes.MISSION_MOVE_TO, MissionTypes.MISSION_ROUTE_TO):
		plot = CyMap().plot(group.getMissionData1(0), group.getMissionData2(0))
		if plot is None or plot.isNone():
			return None
		return plot
	if eMission == MissionTypes.MISSION_MOVE_TO_UNIT:
		iOwner = group.getMissionData1(0)
		if iOwner < 0 or iOwner >= gc.getMAX_PLAYERS():
			return None
		target = gc.getPlayer(iOwner).getUnit(group.getMissionData2(0))
		if target is None or target.isNone():
			return None
		if iViewTeam >= 0 and target.getTeam() != iViewTeam and (not target.plot().isVisible(iViewTeam, False) or target.isInvisible(iViewTeam, False)):
			return None
		return target.plot()
	return None


def _missionQueue(group):
	queue = []
	for i in range(group.getLengthMissionQueue()):
		iData1 = group.getMissionData1(i)
		# <!-- custom: A build mission's data1 is a BuildTypes index, which came back as 17 in the fog-on playthrough (2026-11-13); name it as every other type.
		# Move targets keep their x and y. (Claude code Opus 5.5) -->
		if group.getMissionType(i) == MissionTypes.MISSION_BUILD and iData1 >= 0:
			iData1 = gc.getBuildInfo(iData1).getType()
		queue.append({"mission": gc.getMissionInfo(group.getMissionType(i)).getType(), "data1": iData1, "data2": group.getMissionData2(i)})
	return queue


def _unitFull(unit, iFogTeam=None):
	# <!-- custom: iFogTeam passed on to the briefs, as with _unitBrief: 'unit unit=<ours> fog=1' with the session switch off still gave the live missionPlot of a followed rival (Codex's review, 2026-11-15). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	result = _unitBrief(unit, iFogTeam)
	group = unit.getGroup()
	result["name"] = unit.getName()
	result["strength"] = unit.baseCombatStr()
	result["baseMoves"] = unit.baseMoves()
	# <!-- custom: Whether the unit may enter peaks, as SAS's Scout may; SASPilotScout.py then keeps peaks as look-outs (2026-11-19). (Claude code Opus 5.5) -->
	result["canMoveImpassable"] = unit.canMoveImpassable()
	result["level"] = unit.getLevel()
	result["experience"] = unit.getExperience()
	result["fortifyTurns"] = unit.getFortifyTurns()
	result["canMove"] = unit.canMove()
	result["domain"] = _typeOrNone(gc.getDomainInfo, unit.getDomainType())
	result["unitAI"] = _typeOrNone(gc.getUnitAIInfo, unit.getUnitAIType())
	result["promotions"] = [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if unit.isHasPromotion(i)]
	result["cargo"] = unit.getCargo()
	# <!-- custom: After COMMAND_LOAD at turn 114 of the fog-on playthrough (2026-11-13), the Galley showed cargo 1 but not which unit, and the Archer did not show its ship; the window shows both. (Claude code Opus 5.5) -->
	result["cargoSpace"] = unit.cargoSpace()
	result["transport"] = None
	if unit.isCargo():
		result["transport"] = unit.getTransportUnit().getID()
	if unit.hasCargo():
		plot = unit.plot()
		result["cargoUnits"] = [_unitBrief(plot.getUnit(i), iFogTeam) for i in range(plot.getNumUnits()) if plot.getUnit(i).isCargo() and plot.getUnit(i).getTransportUnit().getID() == unit.getID() and plot.getUnit(i).getOwner() == unit.getOwner()]
	result["groupSize"] = group.getNumUnits()
	# <!-- custom: These first came as numbers ("activity": 6, "automate": 3) while every other type is a name; the fog-on playthrough (2026-11-13) needed the enum read up to know a scout was exploring. (Claude code Opus 5.5) -->
	result["activity"] = _enumName(ActivityTypes, group.getActivityType())
	result["automate"] = _enumName(AutomateTypes, group.getAutomateType())
	result["readyToMove"] = group.readyToMove(False)
	result["missions"] = _missionQueue(group)
	return result


def _orderData(order):
	eOrder = order.eOrderType
	if eOrder == OrderTypes.ORDER_TRAIN:
		return gc.getUnitInfo(order.iData1).getType()
	if eOrder == OrderTypes.ORDER_CONSTRUCT:
		return gc.getBuildingInfo(order.iData1).getType()
	if eOrder == OrderTypes.ORDER_CREATE:
		return gc.getProjectInfo(order.iData1).getType()
	if eOrder == OrderTypes.ORDER_MAINTAIN:
		return gc.getProcessInfo(order.iData1).getType()
	return "ORDER_%d" % int(eOrder)


def _cityBrief(city):
	queue = [_orderData(city.getOrderFromQueue(i)) for i in range(city.getOrderQueueLength())]
	return {"id": city.getID(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "owner": city.getOwner(), "population": city.getPopulation(), "queue": queue, "productionTurnsLeft": city.getProductionTurnsLeft(), "foodTurnsLeft": city.getFoodTurnsLeft()}


def _plotFull(plot):
	# <!-- custom: Written in C++ by CyGame.getSASPilotPlotsJson, which took 0.32 ms for 441 plots against 8 ms for the Python writer it replaced (2026-11-13); the user preferred the long-term speed.
	# There is one writer only, so a new plot field goes in appendSASPilotPlotJson in CvGameInterface.cpp and needs a DLL build; see "Would the DLL be faster?"
	# in README_SASPilot.md. (Claude code Opus 5.5) -->
	return RawJson(_plotsJson(plot.getX(), plot.getY(), 0)[1:-1])


def _plotsJson(iX, iY, iRadius, iFogTeam=-1):
	text = _pilotGame("getSASPilotPathJson").getSASPilotPlotsJson(iX, iY, iRadius, iFogTeam)
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("radius %d is out of range: 0 to the larger map side" % iRadius)
	# <!-- custom: The area ID comes from the true map, so with fog it leaked hidden geography: in the scouting trial (2026-11-14) the bay by the capital and a sea seen far south-west shared one ID, telling that they connect through plots nobody had seen.
	# appendSASPilotPlotJson now writes null with fog; this blanks it for a DLL built before that change and can go once one is installed. (Claude code Opus 5.5) -->
	if iFogTeam >= 0:
		text = re.sub(r'"area":-?\d+', '"area":null', text)
	return text


def _pilotGame(szNewestBinding):
	# <!-- custom: SASPilot's C++ bindings grew over several builds, and a DLL without the newest one a command needs, such as the shipped Release DLL until it is refreshed, would raise a bare AttributeError or TypeError; name the cause instead. (Claude code Fable 5.2) -->
	game = gc.getGame()
	if not hasattr(game, szNewestBinding):
		raise ValueError("this DLL predates CyGame.%s; build or install a current one" % szNewestBinding)
	return game


def _fogTeam(args):
	# <!-- custom: The team whose knowledge limits a reply, or -1 for the full view: a request's own fog argument first, then the session's 'fog' switch. (Claude code Fable 5.2) -->
	bFog = args.get("fog")
	if bFog is None:
		bFog = _state.get("fog", False)
	if not bFog:
		return -1
	return gc.getPlayer(_activePlayerId()).getTeam()


def _requireOwnTeamUnderFog(args, player, szWhat):
	# <!-- custom: For commands that read a player's own records (its land, spies, Great People), which the window shows only for the viewing team: under fog, player= naming another team is refused. Shared by 'routes', 'spy' and 'greatpeople' after Codex's reviews found each could be pointed at a rival (2026-11-14). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iTeam = _fogTeam(args)
	if iTeam >= 0 and player.getTeam() != iTeam:
		raise ValueError("%s of player %d, another team, is hidden; fog is on" % (szWhat, player.getID()))


def _requireSeen(args, iOwner, plot, szWhat):
	# <!-- custom: With fog on, another team's unit or city is only given when the active team sees its plot now, as on the map.
	# Returns whether it is another team's. (Claude code Fable 5.2) -->
	iTeam = _fogTeam(args)
	if iTeam < 0 or gc.getPlayer(iOwner).getTeam() == iTeam:
		return False
	if not plot.isVisible(iTeam, False):
		raise ValueError("%s is not in sight; fog is on" % szWhat)
	return True


def _playerFull(player):
	iPlayer = player.getID()
	team = gc.getTeam(player.getTeam())
	result = {"id": iPlayer, "team": player.getTeam(), "name": player.getName(), "civ": _typeOrNone(gc.getCivilizationInfo, player.getCivilizationType()), "leader": _typeOrNone(gc.getLeaderHeadInfo, player.getLeaderType())}
	result["alive"] = player.isAlive()
	result["human"] = player.isHuman()
	result["turnActive"] = player.isTurnActive()
	result["score"] = gc.getGame().getPlayerScore(iPlayer)
	result["gold"] = player.getGold()
	result["goldRate"] = player.calculateGoldRate()
	result["commercePercent"] = [player.getCommercePercent(CommerceTypes(i)) for i in range(CommerceTypes.NUM_COMMERCE_TYPES)]
	result["research"] = _typeOrNone(gc.getTechInfo, player.getCurrentResearch())
	if player.getCurrentResearch() >= 0:
		result["researchTurnsLeft"] = player.getResearchTurnsLeft(player.getCurrentResearch(), True)
	result["civics"] = [gc.getCivicInfo(player.getCivics(i)).getType() for i in range(gc.getNumCivicOptionInfos())]
	result["stateReligion"] = _typeOrNone(gc.getReligionInfo, player.getStateReligion())
	result["numCities"] = player.getNumCities()
	result["numUnits"] = player.getNumUnits()
	result["population"] = player.getTotalPopulation()
	result["capital"] = None
	capital = player.getCapitalCity()
	if capital is not None and not capital.isNone():
		result["capital"] = capital.getName()
	result["atWarWith"] = [i for i in range(gc.getMAX_CIV_TEAMS()) if i != player.getTeam() and gc.getTeam(i).isAlive() and team.isAtWar(i)]
	result["anarchyTurns"] = player.getAnarchyTurns()
	return result


# <!-- custom: Read commands (Claude code Opus 5.5) -->

# <!-- custom: One line per command for 'help', kept beside each function instead of a docstring. (Claude code Fable 5.2) -->
# <!-- custom: Help texts are returned as written, never %-formatted, so a percent sign is a plain %: the first 'advise' help had "70%%", from habit with format strings, which 'help' would have shown doubled (2026-11-14).
# It now says per mille, as the odds are given. (Claude code Opus 5.5) -->
_HELP = {}

_HELP["help"] = "List the commands with their one-line descriptions."


def cmd_help(args):
	return _HELP


_HELP["ping"] = "Bridge and game state: revision, PID, whether a game runs, turn, active player and whether it is that player's turn."


def cmd_ping(args):
	game = gc.getGame()
	iActive = game.getActivePlayer()
	result = {"pilotRevision": PILOT_REVISION, "pid": os.getpid(), "served": _state["served"], "loads": _state.get("loads"), "ticks": _state["ticks"], "reloadError": _state.get("reloadError"), "tickError": _state.get("tickError"), "tickErrorCount": _state.get("tickErrorCount", 0), "lastTickError": _state.get("lastTickError")}
	result["inGame"] = (iActive >= 0 and game.isFinalInitialized())
	result["activePlayer"] = iActive
	if result["inGame"]:
		player = gc.getPlayer(iActive)
		result["gameTurn"] = game.getGameTurn()
		result["gameYear"] = game.getGameTurnYear()
		result["turnActive"] = player.isTurnActive()
		result["autoPlayTurns"] = game.getAIAutoPlay()
		result["paused"] = game.isPaused()
		result["gameState"] = int(game.getGameState())
		result["debugMode"] = game.isDebugMode()
		result["mapScript"] = CyMap().getMapScriptName()
		result["gridWidth"] = CyMap().getGridWidth()
		result["gridHeight"] = CyMap().getGridHeight()
		# <!-- custom: The enabled game options, so a run can confirm its setup, such as GAMEOPTION_NO_EVENTS: the user tests with random events off, as they add variation between runs, and new games take it from the user's CivilizationIV.ini. (Claude code Fable 5.2) -->
		result["gameOptions"] = [gc.getGameOptionInfo(i).getType() for i in range(gc.getNumGameOptionInfos()) if game.isOption(GameOptionTypes(i))]
		# <!-- custom: The difficulty, which the Victory screen shows a player: the user asked whether SASPilot played Monarch or Noble (2026-11-14), and no command said.
		# The game's level and the active player's, which can differ. (Claude code Opus 5.5) -->
		result["handicap"] = _typeOrNone(gc.getHandicapInfo, game.getHandicapType())
		if game.getActivePlayer() >= 0:
			result["playerHandicap"] = _typeOrNone(gc.getHandicapInfo, gc.getPlayer(game.getActivePlayer()).getHandicapType())
	return result


_HELP["player"] = "One player's empire summary. args: player (default: the active player)."


def cmd_player(args):
	return _playerFull(_player(args))


_HELP["players"] = "Every player ever alive, as in 'player'. With fog on, the active team's players so, and other teams' players only once met, with their ID, name, civilization, team, whether alive and state religion, as the scoreboard shows them, plus civics for living major civilizations as in Foreign Diplomacy."


def cmd_players(args):
	# <!-- custom: Under play, 'players' gave every civilization's full summary, unmet ones included (Codex's review, round 32).
	# With fog on, a player we have not met is not listed, and one we have is given as the scoreboard shows it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iTeam = _fogTeam(args)
	result = []
	for i in range(gc.getMAX_PLAYERS()):
		player = gc.getPlayer(i)
		if not player.isEverAlive():
			continue
		if iTeam < 0 or player.getTeam() == iTeam:
			result.append(_playerFull(player))
		elif gc.getTeam(iTeam).isHasMet(player.getTeam()):
			entry = _who(i)
			entry["team"] = player.getTeam()
			entry["alive"] = bool(player.isAlive())
			# <!-- custom: The scoreboard shows a met rival's state religion, which a conversion popup at turn 52 of the 2026-11-19 validation run needed: converting pleases rivals of the same faith. (Claude code Opus 5.5) -->
			entry["stateReligion"] = _typeOrNone(gc.getReligionInfo, player.getStateReligion())
			# <!-- custom: Match the Foreign Diplomacy Advisor Info tab, which shows civics for living, met major civilizations.
			# The 2026-11-22 tab audit found no command giving them under fog. See KI#1110. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			if player.isAlive() and not player.isBarbarian() and not player.isMinorCiv():
				entry["civics"] = [_typeOrNone(gc.getCivicInfo, player.getCivics(iOption)) for iOption in range(gc.getNumCivicOptionInfos())]
			result.append(entry)
	return result


_HELP["hover"] = "The hover text a player reads for units, as plain text: without unit, each of the player's units in one line, as the plot hover lists them; with unit, that unit's full hover, as the plot list shows it. Under fog, another player's unit only while the active team sees it. args: unit, player."


def cmd_hover(args):
	# <!-- custom: Checking the unit-state hover text (2026-11-15) took a 'py' call to CyGameTextMgr().getSpecificUnitHelp; any later change to that text, or a question about what a player sees, asks it again. (Claude code Opus 5.5) -->
	iTeam = _fogTeam(args)
	if args.get("unit") is None:
		player = _player(args)
		# <!-- custom: The list too keeps to what the team sees under fog: the first version filtered only one unit, so 'hover player=<rival>' listed the rival's every unit (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		result = []
		for unit in _units(player):
			if iTeam >= 0 and unit.getTeam() != iTeam and (not unit.plot().isVisible(iTeam, False) or unit.isInvisible(iTeam, False)):
				continue
			result.append({"id": unit.getID(), "text": _plainText(CyGameTextMgr().getSpecificUnitHelp(unit, True, False))})
		return result
	unit = _unit(args)
	if iTeam >= 0 and unit.getTeam() != iTeam and (not unit.plot().isVisible(iTeam, False) or unit.isInvisible(iTeam, False)):
		raise ValueError("unit %d is not in sight; fog is on" % unit.getID())
	return {"id": unit.getID(), "text": _plainText(CyGameTextMgr().getSpecificUnitHelp(unit, False, False))}


def _dotMapCities(iPlayer):
	# <!-- custom: The dot map's cities for a player, as BUG's Strategy Overlay holds them (CvStrategyOverlay.DotMapLayer); an empty list outside the game or before the overlay starts. (Claude code Opus 5.5) -->
	try:
		import CvStrategyOverlay
		dotMap = CvStrategyOverlay.g_DotMap
	except Exception:
		return []
	if dotMap is None:
		return []
	return [{"x": city.point[0], "y": city.point[1], "color": gc.getColorInfo(city.color).getType(), "layer": city.layer} for city in dotMap.iterCities(iPlayer)]


# <!-- custom: Colours a contrast mark is chosen from, the plain ones BtS's colour table has. (Claude code Opus 5.5) -->
MARK_CONTRAST_COLORS = ("COLOR_BLACK", "COLOR_WHITE", "COLOR_RED", "COLOR_YELLOW", "COLOR_BLUE", "COLOR_GREEN", "COLOR_CYAN", "COLOR_MAGENTA")


def _contrastColor(player):
	# <!-- custom: The candidate farthest in RGB from both of the player's colours (primary and secondary, from its PlayerColorInfo). (Claude code Opus 5.5) -->
	colorInfo = gc.getPlayerColorInfo(player.getPlayerColor())
	ours = []
	for iColor in (colorInfo.getColorTypePrimary(), colorInfo.getColorTypeSecondary()):
		rgb = gc.getColorInfo(iColor).getColor()
		ours.append((rgb.r, rgb.g, rgb.b))
	best = None
	for szColor in MARK_CONTRAST_COLORS:
		iColor = _findOptionalInfoType(szColor)
		if iColor < 0:
			continue
		rgb = gc.getColorInfo(iColor).getColor()
		fDistance = min([(rgb.r - r) ** 2 + (rgb.g - g) ** 2 + (rgb.b - b) ** 2 for (r, g, b) in ours])
		if best is None or fDistance > best[0]:
			best = (fDistance, szColor)
	if best is None:
		raise ValueError("none of %s is in the colour table" % ", ".join(MARK_CONTRAST_COLORS))
	return best[1]


_HELP["fog"] = "Without args: whether fog is on. With on=1 or 0: switch it. With fog on, 'plots', 'plot', 'units', 'unit', 'cities' and 'city' give only what the active player's team knows or sees, as a person at the window would; off (the default) gives everything, for debugging. 'players' lists other teams' players once met; most read commands follow the same rules, but 'py' is not limited. args: on."


# <!-- custom: Each command's role, the user's idea (2026-11-14): play is what a player sees and does in a normal game; omniscient sees past the fog, for debugging; create changes the game beyond play, as the WorldBuilder or 'py' can; meta runs the session. A session set to 'role set=play' refuses the rest, so a playthrough stays fair by construction, "same rules as the game".
# Commands not listed are play; some depend on their arguments, see _commandRole. (Claude code Opus 5.5) -->
# <!-- custom: The user's next idea the same day: tell facts from judgments. play commands state what the game shows a player, the same for every player who can see it, and rarely change; advice weighs facts into a recommendation by a heuristic of ours, which may be wrong and gets tuned as we learn, such as 'advise about=threats'.
# So advice is a role of its own: the session role 'play' gets facts only, which shows what an agent works out by itself, and 'assist' adds advice, so the log shows which advice an agent asked for. 'sites' stays play, as the window circles those sites for any player with a Settler selected; the city AI's builds in 'workers' are advice, as no screen shows them. (Claude code Opus 5.5) -->
# <!-- custom: settings, for 'option', changes the player's own Civ4 and BUG settings, which outlive the game and may be shared with other clients, so only the all role allows it; reading them ('options') is play (Codex's advice, 2026-11-28).
# 'uioption' too, as it calls BUG's setter through the screen: left play, it let the play role change what 'option' refused (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_COMMAND_ROLES = {"py": "create", "autoplay": "meta", "save": "meta", "menu": "meta", "profile": "meta", "batch": "meta", "ping": "meta", "help": "meta", "role": "meta", "advise": "advice", "uiprobe": "omniscient", "meet": "create", "uisplash": "create", "option": "settings", "uioption": "settings"}
_ROLE_ALLOWED = {"play": ("play", "meta"), "assist": ("play", "meta", "advice"), "all": ("play", "meta", "advice", "omniscient", "create", "settings")}
# <!-- custom: Controls that leave play, checked by value: the play role compared the control's name as typed, so its number passed (Codex's review, round 32). Loading a save is meta, as 'menu path=' is. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_CONTROL_ROLES = (("CONTROL_WORLD_BUILDER", "create"), ("CONTROL_ADMIN_DETAILS", "omniscient"), ("CONTROL_LOAD_GAME", "meta"), ("CONTROL_QUICK_LOAD", "meta"))


def _adviceAllowed():
	# <!-- custom: For commands that are mostly facts with a judgment among them, such as 'workers' with the city AI's builds: the judgment is left out when the session's role does not allow advice. (Claude code Opus 5.5) -->
	szRole = _state.get("role")
	return not szRole or "advice" in _ROLE_ALLOWED[szRole]


# <!-- custom: The screens a player opens from the window, by a short name after SAS's titles (BtS's single Foreign Advisor is SAS's Foreign Trade and Foreign Diplomacy Advisors, as the user pointed out), with the CvScreensInterface function their button calls (pediaShow for the Sevopedia, which reopens the last page); under the play role, 'uiopen' passes the same check as 'screen'. (Claude code Opus 5.5) -->
# <!-- custom: The third column is the control each short name's key sends (CvGame::doControl in CvGameInterface.cpp), which 'uiopen' prefers to the show function; None where there is none or where it is not used: CONTROL_CIVICS_SCREEN first kills every waiting change-civic popup (advc.004x), so opening the Policy Advisor by it could remove a popup before a check saw it (Codex's review); its show function draws it fully. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
# <!-- custom: Moved here from SASPilotUI.py with its controls, which were a second table, on 2026-11-28, so _PLAY_SCREENS below is derived from it rather than a third list of the same show functions. See KI#1110.2. (Claude code Opus 5.5) -->
_OPENERS = (
	("tech", "showTechChooser", "CONTROL_TECH_CHOOSER"),
	("policy", "showPolicyAdvisorScreen", None),
	("religion", "showReligionScreen", None),
	("corporation", "showCorporationScreen", None),
	("foreigntrade", "showForeignAdvisorScreen", "CONTROL_FOREIGN_SCREEN"),
	("foreigndiplomacy", "showForeignDiplomacyAdvisor", "CONTROL_FOREIGN_DIPLOMACY_SCREEN"),
	("domestic", "showDomesticAdvisor", "CONTROL_DOMESTIC_SCREEN"),
	("military", "showMilitaryAdvisor", "CONTROL_MILITARY_SCREEN"),
	("espionage", "showEspionageAdvisor", "CONTROL_ESPIONAGE_SCREEN"),
	("info", "showInfoScreen", "CONTROL_INFO"),
	("world", "showWorldAdvisorScreen", "CONTROL_WORLD_ADVISOR_SCREEN"),
	("victory", "showVictoryScreen", "CONTROL_VICTORY_SCREEN"),
	("halloffame", "showHallOfFame", "CONTROL_HALL_OF_FAME"),
	("pedia", "pediaShow", "CONTROL_CIVILOPEDIA"),
)


# <!-- custom: showTopCivs left the list on 2026-11-19: a player has no button for the Greatest Civilizations screen, which comes only on its schedule, so calling it under play gave a fresh ranking of unmet civs at will, and each call uses a draw of the synchronized random number; under all it stays, for tests. (Claude code Opus 5.5) -->
# <!-- custom: The screens a player opens from the window's buttons, the play role's 'screen' calls, without arguments. Round 32 had any show*/pedia* name pass, but showReplay forwards its args[0] to CyGame.saveReplay, so args=[9999,0,0,0,0] reached GET_PLAYER(9999) in CvGame::saveReplay (Codex's review, round 33). A list, and no args: the advisors take none from a player, and 'pedia' gives Sevopedia text without the pedia jumps' indices. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_PLAY_SCREENS = tuple([playOpener[1] for playOpener in _OPENERS]) + ("pediaMain", "pediaBack", "pediaForward")


def _screenRole(szName, args):
	# <!-- custom: 'screen' calls any CvScreensInterface function, and under play it could open the WorldBuilder or call WorldBuilderRevealAllCB (Codex's review, round 32). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if szName.find("Debug") >= 0:
		return "omniscient"
	if szName in _PLAY_SCREENS and args.get("args") is None:
		return "play"
	# <!-- custom: The Foreign Advisor's tab number is a click a player makes, as WIDGET_FOREIGN_ADVISOR does; the user asked at turn 127 of the turn-0 game (2026-11-14) to open the Glance tab, which play refused. (Claude code Opus 5.5) -->
	tabArgs = args.get("args")
	if szName == "showForeignAdvisorScreen" and isinstance(tabArgs, list) and len(tabArgs) == 1 and isinstance(tabArgs[0], int):
		return "play"
	return "create"


def _commandRole(name, args):
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if name == "fog" and args.get("on") is not None and not args.get("on"):
		return "omniscient"
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if name == "control" and args.get("control") is not None:
		iControl = int(_enum(ControlTypes, args["control"]))
		for (szControl, szRole) in _CONTROL_ROLES:
			if iControl == int(getattr(ControlTypes, szControl)):
				return szRole
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if name == "screen" and args.get("name") is not None:
		return _screenRole(str(args["name"]), args)
	# <!-- custom: Reading the font sizes is available in play; their session preview is a layout test. (GPT-6.2-Sol) -->
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if name == "uifont" and set(args).difference(("player", "fog")):
		return "create"
	# <!-- custom: A recorded widget is what the window shows a player, but widgettype, data1, data2 or option can send any widget action with any data, which no click can. (Claude code Opus 5.5) -->
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if name == "uipress" and [szKey for szKey in ("widgettype", "data1", "data2", "option") if args.get(szKey) is not None]:
		return "create"
	if args.get("fog") is not None and not args.get("fog"):
		return "omniscient"
	return _COMMAND_ROLES.get(name, "play")


def _checkRole(name, args):
	# <!-- custom: Under a play role, also refuse player= naming another team, which would give orders or reads for a rival, and fog=0 on a single request. Batch and profile check each command they run. (Claude code Opus 5.5) -->
	szRole = _state.get("role")
	if not szRole:
		return
	szNeeds = _commandRole(name, args)
	if szNeeds not in _ROLE_ALLOWED[szRole]:
		# <!-- custom: Name the session roles that allow it: the message said "'role set=all' lifts it" for 'advise' too, where assist is the role meant, and a locked role cannot be lifted at all. (Claude code Opus 5.5) -->
		allowing = [szName for szName in ("play", "assist", "all") if szNeeds in _ROLE_ALLOWED[szName]]
		szHow = "'role set=%s' allows it" % " or ".join(allowing)
		if _state.get("roleLocked"):
			szHow = "the role is locked for this client; a client started with --role %s allows it" % " or ".join(allowing)
		raise ValueError("'%s' has the %s role, which the session's %s role does not allow; %s" % (name, szNeeds, szRole, szHow))
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox uses stable role keys. (GPT-6.2-Sol) -->
	if szRole != "all" and args.get("player") is not None:
		# <!-- custom: Through _checkedPlayerId, as player=-2 reached gc.getPlayer unchecked here, an out-of-bounds read in a Release DLL (Codex's review, P1). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		iPlayer = _checkedPlayerId(args["player"])
		if gc.getPlayer(iPlayer).getTeam() != gc.getPlayer(_activePlayerId()).getTeam():
			raise ValueError("player %d is another team, which the play role does not allow" % iPlayer)


_HELP["role"] = "The session's role: play allows what a player sees and does, facts only (fog stays on; 'py', the WorldBuilder, fog=0, other teams' player= and 'advise' are refused); assist is play plus advice ('advise', and the city AI's builds in 'workers'); all allows everything, the default. With lock=1 the role holds until Civ4 closes, as 'SASPilotClient.py start --role' sets it. Without set, the role and each command's role: play (facts), advice, omniscient, create or meta. args: set, lock."


def cmd_role(args):
	if args.get("set") is not None:
		if args["set"] not in _ROLE_ALLOWED:
			raise ValueError("role is play, assist or all, not %s" % args["set"])
		# <!-- custom: 'role set=all' from the same mailbox lifted a 'start --role play' (Codex's review, round 32), so a launch role is locked: a fair playthrough should not be one command away from the WorldBuilder. The lock lives in the bridge's state, which lasts until Civ4 closes. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if _state.get("roleLocked") and args["set"] != (_state.get("role") or "all"):
			raise ValueError("the role %s is locked for this client, as 'start --role' set it; start a new client for another role" % (_state.get("role") or "all"))
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if args["set"] == "all":
			_state["role"] = None
		else:
			_state["role"] = args["set"]
			_state["fog"] = True
		if args.get("lock"):
			_state["roleLocked"] = True
	roles = {}
	for name in _HELP.keys():
		roles[name] = _COMMAND_ROLES.get(name, "play")
	return {"role": _state.get("role") or "all", "locked": bool(_state.get("roleLocked")), "commands": roles, "byArguments": "fog on=0 and fog=0 are omniscient; control CONTROL_WORLD_BUILDER is create, CONTROL_ADMIN_DETAILS omniscient, CONTROL_LOAD_GAME and CONTROL_QUICK_LOAD meta; screen is play for the advisors and Sevopedia navigation (_PLAY_SCREENS) without args, omniscient for Debug ones, else create; workers leaves out the city AI's builds unless advice is allowed; players under fog gives other teams' players only once met, briefly; uipress with widgettype, data1, data2 or option is create"}


def cmd_fog(args):
	# <!-- custom: SASPilot began with full information only, as a debugging tool; the user then asked for play as a person would, "manage the fog" included (2026-11-13).
	# A switch rather than a second set of commands, so the same orders and reads serve both uses. (Claude code Fable 5.2) -->
	if args.get("on") is not None:
		_state["fog"] = bool(args["on"])
	return {"fog": bool(_state.get("fog", False))}


_HELP["messages"] = "The messages the game showed the player at the top of the screen and still lists, such as combat results, oldest first: turn, text, x, y, from (player or -1), messageType. args: since (game turn, default the previous turn), player."


def cmd_messages(args):
	iSince = args.get("since")
	if iSince is None:
		iSince = gc.getGame().getGameTurn() - 1
	text = _pilotGame("getSASPilotMessagesJson").getSASPilotMessagesJson(_playerId(args), int(iSince))
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("no player %s" % args.get("player"))
	# <!-- custom: The texts carry font and color tags and icon characters, as the first test showed ("<font=3>You have captured Beshbalik!!!</font>"); the list is short, so it is read back and cleaned here rather than in the DLL. (Claude code Fable 5.2) -->
	messages = fromJson(text)
	# <!-- custom: AdvCiv separates each turn's messages with an "----- Older messages:" line of MESSAGE_TYPE_EOT (advc.106b, CvPlayer.cpp), which came back as a message every turn of the fog-on playthrough (2026-11-13); leave it out, and give the type by name. (Claude code Opus 5.5) -->
	result = []
	for message in messages:
		szType = _MESSAGE_TYPE_NAMES[message["messageType"]]
		if szType == "MESSAGE_TYPE_EOT":
			continue
		message["messageType"] = szType
		message["text"] = _plainText(message["text"])
		result.append(message)
	return result


# <!-- custom: InterfaceMessageTypes in CvEnums.h order; Python's enum lacks AdvCiv's last two (advc.106b), so the names are listed here. (Claude code Opus 5.5) -->
_MESSAGE_TYPE_NAMES = ("MESSAGE_TYPE_INFO", "MESSAGE_TYPE_DISPLAY_ONLY", "MESSAGE_TYPE_MAJOR_EVENT", "MESSAGE_TYPE_MINOR_EVENT", "MESSAGE_TYPE_CHAT", "MESSAGE_TYPE_COMBAT_MESSAGE", "MESSAGE_TYPE_QUEST", "MESSAGE_TYPE_MAJOR_EVENT_LOG_ONLY", "MESSAGE_TYPE_EOT")


_HELP["todo"] = "What waits for the player's orders: cities with an empty build queue, missing research, and units ready to move with no mission. args: player."


def cmd_todo(args):
	# <!-- custom: The game's choose-production and choose-tech popups only show in the window and do not stop 'endturn': 22 turns ended with an empty queue and no research (2026-11-13), so SASPilot has to ask what is idle. (Claude code Fable 5.2) -->
	player = _player(args)
	# <!-- custom: The game turn too: a turn loop of the islands replay (2026-11-15) asked it with a 'py' call after each endturn; the year with it, as autosaves are named by year (AutoSave_BC-2120 was turn 68). (Claude code Opus 5.5) -->
	result = {"turn": gc.getGame().getGameTurn(), "year": gc.getGame().getGameTurnYear(), "turnActive": player.isTurnActive()}
	result["idleCities"] = [_cityBrief(city) for city in _cities(player) if city.getOrderQueueLength() == 0]
	result["needsResearch"] = (player.getCurrentResearch() < 0)
	# <!-- custom: An automated group, such as a scout on Explore, was listed as idle every turn of the fog-on playthrough (2026-11-13), while the window does not ask for its orders; leave such groups out. (Claude code Opus 5.5) -->
	result["idleUnits"] = [_unitBrief(unit) for unit in _units(player) if unit.getGroup().readyToMove(False) and unit.getGroup().getLengthMissionQueue() == 0 and not unit.getGroup().isAutomated()]
	# <!-- custom: Choices the game asked for and SASPilot holds, such as keeping or razing a captured city; production and tech popups are left out, as the two entries above cover them. (Claude code Fable 5.2) -->
	if player.getID() == gc.getGame().getActivePlayer() and hasattr(gc.getGame(), "getSASPilotPathJson"):
		result["heldPopups"] = [{"id": popup["id"], "type": popup["type"], "data1": popup["data1"], "buttons": [item["name"] for item in popup["buttons"]], "about": popup.get("about")} for popup in _popups() if popup["state"] == "HELD" and not (popup["type"] == "BUTTONPOPUP_CHOOSEPRODUCTION" or (popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] <= 0)) and not _isNotice(popup)]
	# <!-- custom: An open diplomacy screen waits for a reply as a popup does; see 'diplo'. (Claude code Opus 5.5) -->
	if player.getID() == gc.getGame().getActivePlayer():
		state = _diploState()
		if state["open"]:
			result["diplomacy"] = {"screen": _diploToken(state), "who": state["who"], "whoName": gc.getPlayer(state["who"]).getName(), "aiComment": _typeOrNone(gc.getDiplomacyInfo, state["aiComment"]), "replies": [gc.getDiplomacyInfo(response["comment"]).getType() for response in state["responses"]]}
		# <!-- custom: A tech bought from Pacal at turn 148 (2026-11-13) put its splash on display at once, and 'todo' reported nothing while the window waited on Continue; only 'turn' closes such screens, as notices.
		# Listed here unclosed, so a check of 'todo' alone sees the window is blocked. (Claude code Opus 5.5) -->
		screens = _closeInfoScreens(False)
		if screens:
			result["infoScreens"] = screens
		# <!-- custom: A spy's Investigate City at Oporto (turn 284, 2026-11-14) opened that city's screen, which stayed over the map beside a diplomacy screen until the user pointed it out; nothing in 'todo' said so.
		# It blocks nothing, so it is reported, not waited on; CyInterface().clearSelectedCities() or Esc closes it. (Claude code Opus 5.5) -->
		if CyInterface().isCityScreenUp():
			city = CyInterface().getHeadSelectedCity()
			result["cityScreen"] = (city and [city.getName()] or [True])[0]
		# <!-- custom: Advisors and other Python screens left open, such as the Foreign Advisor a numeric control test opened (2026-11-14); reported like the city screen, as they block nothing but cover the map. (Claude code Opus 5.5) -->
		others = [szName for szName in _openScreens() if szName != "cityScreen"]
		if others:
			result["openScreens"] = others
	# <!-- custom: A free-tech chooser already on display, as after loading a save before SASPilot held popups again, is not in heldPopups, so 'endturn --turns' did not stop for it (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Only while the game still counts a free tech as owed: after 'freetech' took one through a displayed chooser, the chooser stayed on screen, and listing it kept 'todo' waiting for good (2026-11-13). (Claude code Opus 5.5) -->
	if player.getID() == gc.getGame().getActivePlayer() and hasattr(gc.getGame(), "getSASPilotPathJson"):
		displayed = [popup for popup in _popups() if popup["state"] == "DISPLAYED" and popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0]
		if displayed and _pilotGame("isSASPilotChoosingFreeTech").isSASPilotChoosingFreeTech():
			result["freeTechOwed"] = displayed[0]["data1"]
	# <!-- custom: One flag for a turn loop: at turn 65 of the islands replay (2026-11-15) Pericles opened first contact, and a loop that stopped only for idle cities, units, popups and research ended the turn against the open diplomacy screen six times.
	# True while anything here waits on the player. (Claude code Opus 5.5) -->
	result["blocking"] = bool(result["idleCities"] or result["idleUnits"] or result["needsResearch"] or result.get("heldPopups") or result.get("diplomacy") or result.get("freeTechOwed"))
	return result


# <!-- custom: F6 and Sevopedia draw these relationships from loaded infos.
# Index the rules lazily in this module so polling and ordinary gameplay pay nothing, and a SASPilot hot reload rebuilds the index on demand.
# Research progress and diplomacy come from the current game on each request. (GPT-6.1-Sol) -->
_GRAPH_CACHE = {}


def _infoTypes(getter, indices):
	return sorted(set([getter(i).getType() for i in indices if i >= 0]))


def _prerequisites(info, allCount, anyCount):
	return {
		"all": _infoTypes(gc.getTechInfo, [info.getPrereqAndTechs(i) for i in range(allCount)]),
		"any": _infoTypes(gc.getTechInfo, [info.getPrereqOrTechs(i) for i in range(anyCount)]),
	}


def _techNodes():
	if "tech" not in _GRAPH_CACHE:
		rows = []
		for i in range(gc.getNumTechInfos()):
			info = gc.getTechInfo(i)
			rows.append({"type": info.getType(), "name": info.getDescription(), "baseCost": info.getResearchCost(),
				"era": _typeOrNone(gc.getEraInfo, info.getEra()), "grid": [info.getGridX(), info.getGridY()],
				"requires": _prerequisites(info, gc.getNUM_AND_TECH_PREREQS(), gc.getNUM_OR_TECH_PREREQS()),
				"disabled": bool(info.isDisable()), "repeatable": bool(info.isRepeat()), "tradeable": bool(info.isTrade())})
		_GRAPH_CACHE["tech"] = rows
	return _GRAPH_CACHE["tech"]


def _promotionNodes():
	if "promotions" not in _GRAPH_CACHE:
		rows = []
		for i in range(gc.getNumPromotionInfos()):
			info = gc.getPromotionInfo(i)
			rows.append({"type": info.getType(), "name": info.getDescription(),
				"requires": {"all": _infoTypes(gc.getPromotionInfo, [info.getPrereqPromotion()]),
					"any": _infoTypes(gc.getPromotionInfo, [info.getPrereqOrPromotion1(), info.getPrereqOrPromotion2(), info.getPrereqOrPromotion3()])},
				"tech": _typeOrNone(gc.getTechInfo, info.getTechPrereq()),
				"stateReligion": _typeOrNone(gc.getReligionInfo, info.getStateReligionPrereq()),
				"requiresLeader": bool(info.isLeader()),
				"unitCombats": _infoTypes(gc.getUnitCombatInfo, [j for j in range(gc.getNumUnitCombatInfos()) if info.getUnitCombat(j)])})
		_GRAPH_CACHE["promotions"] = rows
	return _GRAPH_CACHE["promotions"]


def _assetRequirements(info, kind):
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if kind == "unit":
		allCount = gc.getNUM_UNIT_AND_TECH_PREREQS()
		bonusCount = gc.getNUM_UNIT_PREREQ_OR_BONUSES()
	else:
		allCount = gc.getNUM_BUILDING_AND_TECH_PREREQS()
		bonusCount = gc.getNUM_BUILDING_PREREQ_OR_BONUSES()
	return {"techAll": _infoTypes(gc.getTechInfo, [info.getPrereqAndTech()] + [info.getPrereqAndTechs(i) for i in range(allCount)]),
		"bonusAll": _infoTypes(gc.getBonusInfo, [info.getPrereqAndBonus()]),
		"bonusAny": _infoTypes(gc.getBonusInfo, [info.getPrereqOrBonuses(i) for i in range(bonusCount)]),
		"cityReligion": _typeOrNone(gc.getReligionInfo, info.getPrereqReligion()),
		"stateReligion": _typeOrNone(gc.getReligionInfo, info.getStateReligion())}


def _upgradeNodes(iCiv):
	key = ("upgrades", iCiv)
	if key not in _GRAPH_CACHE:
		civ = gc.getCivilizationInfo(iCiv)
		units = [civ.getCivilizationUnits(i) for i in range(gc.getNumUnitClassInfos())]
		rows = []
		for i in units:
			if i < 0:
				continue
			info = gc.getUnitInfo(i)
			requires = _assetRequirements(info, "unit")
			requires["building"] = _typeOrNone(gc.getBuildingInfo, info.getPrereqBuilding())
			requires["corporation"] = _typeOrNone(gc.getCorporationInfo, info.getPrereqCorporation())
			rows.append({"type": info.getType(), "name": info.getDescription(),
				"class": gc.getUnitClassInfo(info.getUnitClassType()).getType(), "requires": requires,
				"upgradesTo": _infoTypes(gc.getUnitInfo, [units[j] for j in range(len(units)) if info.getUpgradeUnitClass(j)])})
		_GRAPH_CACHE[key] = rows
	return _GRAPH_CACHE[key]


def _recordTechEffect(effects, iTech, effect, target, details=None):
	if iTech < 0:
		return
	row = {"effect": effect, "target": target}
	if details:
		row.update(details)
	effects[gc.getTechInfo(iTech).getType()].append(row)


def _techEffects(iCiv):
	key = ("effects", iCiv)
	if key in _GRAPH_CACHE:
		return _GRAPH_CACHE[key]
	effects = dict([(node["type"], []) for node in _techNodes()])
	# <!-- custom: Was "prerequisite" like the units and buildings a tech unlocks, so reading what a tech brings meant sorting TECH_ targets from the rest by hand (Continents game, 2026-11-14); techs it leads to now say leadsTo. (Claude code Opus 5.5) -->
	for node in _techNodes():
		for relation in ("all", "any"):
			for tech in node["requires"][relation]:
				effects[tech].append({"effect": "leadsTo", "target": node["type"], "group": relation})
	for kind in ("Build", "Civic", "Project", "Process", "Religion", "Corporation", "Promotion", "SpecialBuilding", "EspionageMission"):
		for i in range(getattr(gc, "getNum" + kind + "Infos")()):
			info = getattr(gc, "get" + kind + "Info")(i)
			_recordTechEffect(effects, info.getTechPrereq(), "prerequisite", info.getType())
	for node in _upgradeNodes(iCiv):
		for tech in node["requires"]["techAll"]:
			effects[tech].append({"effect": "prerequisite", "target": node["type"], "requires": node["requires"]})
	civ = gc.getCivilizationInfo(iCiv)
	for i in range(gc.getNumBuildingClassInfos()):
		iBuilding = civ.getCivilizationBuildings(i)
		if iBuilding >= 0:
			info = gc.getBuildingInfo(iBuilding)
			requires = _assetRequirements(info, "building")
			requires["corporation"] = _typeOrNone(gc.getCorporationInfo, info.getPrereqCorporation())
			for tech in requires["techAll"]:
				effects[tech].append({"effect": "prerequisite", "target": info.getType(), "requires": requires})
			_recordTechEffect(effects, info.getObsoleteTech(), "obsoletes", info.getType())
	for i in range(gc.getNumSpecialBuildingInfos()):
		info = gc.getSpecialBuildingInfo(i)
		_recordTechEffect(effects, info.getObsoleteTech(), "obsoletes", info.getType())
	for i in range(gc.getNumBonusInfos()):
		info = gc.getBonusInfo(i)
		for effect, tech in (("reveals", info.getTechReveal()), ("allowsResourceConnection", info.getTechCityTrade()), ("obsoletes", info.getTechObsolete())):
			_recordTechEffect(effects, tech, effect, info.getType())
	for i in range(gc.getNumBuildInfos()):
		info = gc.getBuildInfo(i)
		iTech = info.getTechPrereq()
		for effect, getter, target in (("allowsImprovementBuild", gc.getImprovementInfo, info.getImprovement()), ("allowsRouteBuild", gc.getRouteInfo, info.getRoute())):
			if target >= 0:
				result = getter(target)
				details = {"build": info.getType()}
				if effect == "allowsImprovementBuild":
					details["connectsBonuses"] = _infoTypes(gc.getBonusInfo, [j for j in range(gc.getNumBonusInfos()) if result.isImprovementBonusTrade(j)])
				else:
					details["bonusAll"] = _infoTypes(gc.getBonusInfo, [result.getPrereqBonus()])
					details["bonusAny"] = _infoTypes(gc.getBonusInfo, [result.getPrereqOrBonus(j) for j in range(gc.getNUM_ROUTE_PREREQ_OR_BONUSES())])
				_recordTechEffect(effects, iTech, effect, result.getType(), details)
		for j in range(gc.getNumFeatureInfos()):
			if info.isFeatureRemove(j):
				_recordTechEffect(effects, info.getFeatureTech(j), "allowsFeatureRemoval", gc.getFeatureInfo(j).getType(), {"build": info.getType(), "buildTech": _typeOrNone(gc.getTechInfo, iTech), "production": info.getFeatureProduction(j)})
	for i in range(gc.getNumTechInfos()):
		info = gc.getTechInfo(i)
		rows = effects[info.getType()]
		for flag in ("MapCentering", "MapVisible", "MapTrading", "TechTrading", "GoldTrading", "OpenBordersTrading", "DefensivePactTrading", "PermanentAllianceTrading", "VassalStateTrading", "BridgeBuilding", "Irrigation", "IgnoreIrrigation", "WaterWork", "RiverTrade", "ExtraWaterSeeFrom"):
			if getattr(info, "is" + flag)():
				rows.append({"effect": "enables", "target": flag})
		for field in ("TradeRoutes", "FeatureProductionModifier", "WorkerSpeedModifier", "Health", "Happiness", "FirstFreeTechs"):
			amount = getattr(info, "get" + field)()
			if amount:
				rows.append({"effect": "changes", "target": field, "amount": amount})
		iClass = info.getFirstFreeUnitClass()
		if iClass >= 0:
			iUnit = civ.getCivilizationUnits(iClass)
			if iUnit >= 0:
				rows.append({"effect": "firstDiscoveryUnit", "target": gc.getUnitInfo(iUnit).getType()})
		for j in range(gc.getNumTerrainInfos()):
			if info.isTerrainTrade(j):
				rows.append({"effect": "allowsTerrainTrade", "target": gc.getTerrainInfo(j).getType()})
		for j in range(gc.getNumRouteInfos()):
			route = gc.getRouteInfo(j)
			amount = route.getTechMovementChange(i)
			if amount:
				rows.append({"effect": "changesRouteMovementCost", "target": route.getType(), "amount": amount})
		for j in range(int(DomainTypes.NUM_DOMAIN_TYPES)):
			amount = info.getDomainExtraMoves(j)
			if amount:
				rows.append({"effect": "changesDomainMoves", "target": _enumName(DomainTypes, j), "amount": amount})
		for j in range(int(CommerceTypes.NUM_COMMERCE_TYPES)):
			commerce = gc.getCommerceInfo(j).getType()
			if info.isCommerceFlexible(j):
				rows.append({"effect": "allowsCommerceSlider", "target": commerce})
			for effect, amount in (("changesCommerceModifier", info.getCommerceModifier(j)), ("changesSpecialistCommerce", info.getSpecialistExtraCommerce(j))):
				if amount:
					rows.append({"effect": effect, "target": commerce, "amount": amount})
		for j in range(gc.getNumImprovementInfos()):
			improvement = gc.getImprovementInfo(j)
			for iYield in range(YieldTypes.NUM_YIELD_TYPES):
				amount = improvement.getTechYieldChanges(i, iYield)
				if amount:
					rows.append({"effect": "changesImprovementYield", "target": improvement.getType(), "yield": gc.getYieldInfo(iYield).getType(), "amount": amount})
	_GRAPH_CACHE[key] = effects
	return effects


# <!-- custom: Read the Info screen's completed-turn series without opening it.
# CvInfoScreen's partial score rule allows the public score once enough turns have passed since contact, while the other series require visible demographics. (GPT-6.1-Sol) -->
_HISTORY_GETTERS = {
	"score": "getScoreHistory", "economy": "getEconomyHistory", "industry": "getIndustryHistory",
	"agriculture": "getAgricultureHistory", "power": "getPowerHistory",
	"culture": "getCultureHistory", "espionage": "getEspionageHistory",
}


def _historyStart(player, other, metric, first, current, fog, partial):
	if not fog or other.getTeam() == player.getTeam():
		return first
	team = gc.getTeam(player.getTeam())
	if not team.isHasMet(other.getTeam()):
		return None
	if player.canSeeDemographics(other.getID()):
		return first
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if metric != "score":
		return None
	if player.hasEverSeenDemographics(other.getID()):
		return first
	met = team.getHasMetTurn(other.getTeam())
	if partial and current - met >= 5:
		return max(first, met)
	return None


def _historyGraph(args, result):
	# <!-- custom: BUG's advisor options say whether the score graph shows partial scores, as the Info Screen's graph does; imported here as only this command needs them. (Claude code Opus 5.5) -->
	from BugCore import game as bug
	metric = args.get("metric", "score")
	if metric not in _HISTORY_GETTERS:
		raise ValueError("history metric must be " + ", ".join(sorted(_HISTORY_GETTERS)))
	game = gc.getGame()
	first = game.getStartTurn()
	current = game.getGameTurn()
	start = max(first, int(args.get("start", first)))
	end = min(current - 1, int(args.get("end", current - 1)))
	viewer = _player(args)
	_requireOwnTeamUnderFog(args, viewer, "history")
	fog = _fogTeam(args) >= 0 and game.getGameState() != GameStateTypes.GAMESTATE_OVER
	partial = bug.Advisors.isPartialScoreGraphs()
	series = []
	for i in range(gc.getMAX_CIV_PLAYERS()):
		player = gc.getPlayer(i)
		if not player.isEverAlive() or player.isBarbarian():
			continue
		visible = _historyStart(viewer, player, metric, first, current, fog, partial)
		if visible is None:
			continue
		getValue = getattr(player, _HISTORY_GETTERS[metric])
		points = []
		for turn in range(max(start, visible), end + 1):
			value = 0
			if player.getScoreHistory(turn):
				value = getValue(turn)
			points.append([turn, value])
		series.append({"player": i, "name": player.getName(), "points": points})
	result.update({"metric": metric, "start": start, "end": end, "series": series})
	return result


_HELP["graph"] = "Read a graph as structured JSON. tech: prerequisite groups, F6 grid and effects for the selected civilization. promotions: prerequisite groups, tech and eligible unit combat classes. upgrades: direct unit upgrade links for the selected civilization. relations: current F3 relationships by player ID. history: completed-turn series from the Info graphs, metric defaults to score. Use type to look up a single rules node. args: kind (tech, promotions, upgrades, relations or history), type, metric, start, end, player."


def cmd_graph(args):
	kind = args.get("kind")
	szType = args.get("type")
	result = {"kind": kind}
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if kind == "history":
		if szType is not None:
			raise ValueError("the history graph takes metric instead of type")
		return _historyGraph(args, result)
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if kind == "relations":
		if szType is not None:
			raise ValueError("the relations graph takes no type filter")
		query = dict(args)
		del query["kind"]
		query["graph"] = True
		result = _command("relations")(query)
		result["kind"] = kind
		return result
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if kind == "promotions":
		nodes = _promotionNodes()
	elif kind in ("tech", "upgrades"):
		iCiv = _player(args).getCivilizationType()
		result["civilization"] = gc.getCivilizationInfo(iCiv).getType()
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if kind == "upgrades":
			nodes = _upgradeNodes(iCiv)
		else:
			effects = _techEffects(iCiv)
			nodes = [dict(node, effects=effects[node["type"]]) for node in _techNodes()]
	else:
		raise ValueError("graph kind must be tech, promotions, upgrades, relations or history")
	if szType is not None:
		nodes = [node for node in nodes if node["type"] == szType]
		if not nodes:
			raise ValueError("%s is not in the %s graph" % (szType, kind))
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if kind == "upgrades":
			result["upgradesFrom"] = [node["type"] for node in _upgradeNodes(iCiv) if szType in node["upgradesTo"]]
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if kind == "promotions":
			result["requiredBy"] = [{"type": node["type"], "group": group} for node in _promotionNodes()
				for group in ("all", "any") if szType in node["requires"][group]]
	result["nodes"] = nodes
	return result


_HELP["tech"] = "Show one technology: rule effects and prerequisites, plus live research cost, progress, availability and which immediate prerequisites are missing. path lists every tech still to research for it, prerequisites first, in the order 'research tech=...' queues them, each with its remaining beakers and turns at the current rate; pathRemaining and pathTurns add them up. Effects say leadsTo for techs it is a prerequisite of, and prerequisite for the units, buildings and other things it unlocks. args: type (TECH_ type), player."


def cmd_tech(args):
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "research progress")
	iTech = _typedIndex(args["type"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	node = dict(_techNodes()[iTech])
	team = gc.getTeam(player.getTeam())
	effects = _techEffects(player.getCivilizationType())[node["type"]]
	node["effects"] = []
	for effect in effects:
		row = dict(effect)
		if "requires" in row:
			row["otherMissingTechs"] = [tech for tech in row["requires"]["techAll"] if tech != node["type"]
				and not team.isHasTech(getInfoTypeOrFail(tech))]
		node["effects"].append(row)
	requires = node["requires"]
	node["missingAll"] = [tech for tech in requires["all"] if not team.isHasTech(getInfoTypeOrFail(tech))]
	node["missingAny"] = []
	if requires["any"] and not [tech for tech in requires["any"] if team.isHasTech(getInfoTypeOrFail(tech))]:
		node["missingAny"] = requires["any"]
	node["known"] = bool(team.isHasTech(iTech))
	node["canResearch"] = bool(player.canResearch(iTech, False))
	node["cost"] = team.getResearchCost(iTech)
	node["progress"] = team.getResearchProgress(iTech)
	# <!-- custom: missingAll and missingAny named only the immediate prerequisites, so at turn 19 of the Continents game (2026-11-14) a tech plan toward a goal meant one 'tech' call per step and adding the costs by hand.
	# The path lists every tech still to research, prerequisites first, with what each costs and takes at the current rate. (Claude code Opus 5.5) -->
	path = []
	if not node["known"]:
		_techPathVisit(player, team, iTech, path, {}, {})
	node["path"] = [{"tech": gc.getTechInfo(i).getType(), "remaining": team.getResearchCost(i) - team.getResearchProgress(i), "turns": player.getResearchTurnsLeft(i, True)} for i in path]
	node["pathRemaining"] = sum([entry["remaining"] for entry in node["path"]])
	node["pathTurns"] = sum([entry["turns"] for entry in node["path"]])
	return node


def _techPathLength(team, iTech, memo):
	# <!-- custom: CvPlayer::findPathLength in Python, its total research cost to a tech, used only to pick among OR prerequisites as pushResearch does.
	# It counts a prerequisite shared by two branches twice (its k146 note), as the engine does, so the choice matches; unlike the engine it does not count queued techs as known, since 'research' clears the queue before pushing. (Claude code Opus 5.5) -->
	if team.isHasTech(iTech):
		return 0
	if iTech not in memo:
		info = gc.getTechInfo(iTech)
		iLength = team.getResearchCost(iTech)
		for i in range(gc.getNUM_AND_TECH_PREREQS()):
			if info.getPrereqAndTechs(i) >= 0:
				iLength += _techPathLength(team, info.getPrereqAndTechs(i), memo)
		lengths = [_techPathLength(team, info.getPrereqOrTechs(i), memo) for i in range(gc.getNUM_OR_TECH_PREREQS()) if info.getPrereqOrTechs(i) >= 0]
		if lengths:
			iLength += min(lengths)
		memo[iTech] = iLength
	return memo[iTech]


def _techPathVisit(player, team, iTech, path, seen, memo):
	# <!-- custom: The order 'research tech=...' would queue, mirroring CvPlayer::pushResearch: every AND prerequisite first, then the cheapest path among the OR prerequisites unless one is known (the first wins a tie), then the tech itself. A tech reached by two branches is listed once. (Claude code Opus 5.5) -->
	if team.isHasTech(iTech) or iTech in seen:
		return
	info = gc.getTechInfo(iTech)
	for i in range(gc.getNUM_AND_TECH_PREREQS()):
		if info.getPrereqAndTechs(i) >= 0:
			_techPathVisit(player, team, info.getPrereqAndTechs(i), path, seen, memo)
	options = [info.getPrereqOrTechs(i) for i in range(gc.getNUM_OR_TECH_PREREQS()) if info.getPrereqOrTechs(i) >= 0]
	if options and not [i for i in options if team.isHasTech(i)]:
		iBest = -1
		for i in options:
			if player.canEverResearch(i) and (iBest < 0 or _techPathLength(team, i, memo) < _techPathLength(team, iBest, memo)):
				iBest = i
		if iBest < 0:
			raise ValueError("player %d can never research any OR prerequisite of %s" % (player.getID(), info.getType()))
		_techPathVisit(player, team, iBest, path, seen, memo)
	seen[iTech] = True
	path.append(iTech)


_HELP["research"] = "Without args: the techs the player knows (known), the techs it can research now, each with its turns and its case (resources of ours it improves, met civs that would sell it to us now in buyFrom, how many met civs lack it in sellTo when the XML lets it be traded, the techs it leads to, what it unlocks, and meetsNeeds: a happiness or health building where a city has a margin of 1 or less, marking the limit that binds first, or a land unit stronger than any we train, with the resources it needs and our status for each), and limits (each city's happy and health margins, and which binds first), and the research queue. With tech: research it; a tech not available yet is queued after its missing prerequisites, as a shift-click in the tech tree does. append=1 adds to the queue instead of replacing it. With effects=1, include the effects of each available tech. With ahead=N, every tech at most N techs away, in F6 column then row order, with era, steps, beakers and turns to reach it, the techs on the way, its OR alternatives (orChoice), what it unlocks or reveals, the met players seen to hold it and whether the XML lets it be traded; rivals lists each met player's current research with its percent, or unknown when espionage does not show it. args: tech (TECH_ type), append, effects, ahead, player."


# <!-- custom: Needs a tech's case lists before counting the rest. (Claude code Opus 5.5) -->
MEETS_NEEDS_SHOWN = 3


def _seenBonuses(player):
	# <!-- custom: Each bonus type our team has seen on the map, "ours" when one lies in our borders, else "elsewhere". (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	kMap = gc.getMap()
	seen = {}
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if not plot.isRevealed(iTeam, False):
			continue
		iBonus = plot.getBonusType(iTeam)
		if iBonus < 0:
			continue
		if plot.getOwner() == player.getID():
			seen[iBonus] = "ours"
		elif not seen.has_key(iBonus):
			seen[iBonus] = "elsewhere"
	return seen


def _unitResourceStatus(player, unitInfo, seenBonuses, techInfo=None):
	# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: a military game needs metals or mounts, and none was seen but the Camel; 'research' had called the Chariot and Axeman "stronger" without saying they need a Horse or Copper.
	# The unit's resource requirements from its XML (one AND bonus, any of the OR bonuses), each with our status: have (connected), seen in our borders, seen elsewhere, or unseen. (Claude code Opus 5.5) -->
	parts = []
	iAnd = unitInfo.getPrereqAndBonus()
	if iAnd >= 0:
		parts.append("needs %s (%s)" % (gc.getBonusInfo(iAnd).getType(), _bonusStatus(player, iAnd, seenBonuses, techInfo)))
	ors = [unitInfo.getPrereqOrBonuses(i) for i in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()) if unitInfo.getPrereqOrBonuses(i) >= 0]
	if ors:
		parts.append("needs one of %s" % ", ".join(["%s (%s)" % (gc.getBonusInfo(i).getType(), _bonusStatus(player, i, seenBonuses, techInfo)) for i in ors]))
	return "; ".join(parts)


def _bonusStatus(player, iBonus, seenBonuses, techInfo=None):
	if player.getNumAvailableBonuses(iBonus) > 0:
		return "have"
	# <!-- custom: A bonus this very tech reveals is unseen until it is known (Bronze Working reveals Copper), so it says so rather than plain unseen. (Claude code Opus 5.5) -->
	iReveal = gc.getBonusInfo(iBonus).getTechReveal()
	if not seenBonuses.has_key(iBonus) and techInfo is not None and iReveal >= 0 and gc.getTechInfo(iReveal).getType() == techInfo.getType():
		return "this tech reveals it"
	if not seenBonuses.has_key(iBonus) and iReveal >= 0 and not gc.getTeam(player.getTeam()).isHasTech(iReveal):
		return "hidden until %s" % gc.getTechInfo(iReveal).getType()
	return seenBonuses.get(iBonus, "unseen")


def _addTechCases(player, args, entries):
	# <!-- custom: The market from 'techs' (the Foreign Advisor's tech tab) and the paths from the tech tree, added to each entry by its "tech" type. (Claude code Opus 5.5) -->
	market = _command("techs")({"player": player.getID(), "fog": args.get("fog")})
	iMet = len(market["weCouldGive"])
	sellers = {}
	holders = {}
	for row in market["wanted"]:
		holders[row["tech"]] = len(row["holders"])
		sellers[row["tech"]] = [holder["name"] for holder in row["holders"] if holder["canTrade"] and holder.get("denial") is None and holder.get("willTalk", True)]
	effects = _techEffects(player.getCivilizationType())
	# <!-- custom: The user, same turn: what units and buildings a tech gives and whether the empire needs them (happiness, health, defense).
	# Needs from our cities now: the smallest happy and health margin, and the strongest land unit any city can train, so a tech's buildings and units are weighed against them. (Claude code Opus 5.5) -->
	cities = _cities(player)
	iHappyMargin = min([city.happyLevel() - city.unhappyLevel(0) for city in cities] or [0])
	iHealthMargin = min([city.goodHealth() - city.badHealth(False) for city in cities] or [0])
	# <!-- custom: The user: weigh happiness against health.
	# The limit with the smaller margin stops growth first, so its need is marked "binds first"; each city's margins are returned as 'limits'. (Claude code Opus 5.5) -->
	szBinding = (iHappyMargin <= iHealthMargin and "happiness") or "health"
	limits = {"bindsFirst": szBinding, "cities": [{"city": city.getName(), "happyMargin": city.happyLevel() - city.unhappyLevel(0), "healthMargin": city.goodHealth() - city.badHealth(False), "growsIn": city.getFoodTurnsLeft()} for city in cities]}
	iBestStrength = 0
	for i in range(gc.getNumUnitInfos()):
		unitInfo = gc.getUnitInfo(i)
		if unitInfo.getDomainType() == DomainTypes.DOMAIN_LAND and [1 for city in cities if city.canTrain(i, False, False)]:
			iBestStrength = max(iBestStrength, unitInfo.getCombat())
	seenBonuses = _seenBonuses(player)
	civ = gc.getCivilizationInfo(player.getCivilizationType())
	for entry in entries:
		szTech = entry["tech"]
		info = gc.getTechInfo(_typedIndex(szTech, "TECH_", gc.getNumTechInfos(), gc.getTechInfo))
		entry["buyFrom"] = sellers.get(szTech, [])
		entry["metHolding"] = holders.get(szTech, 0)
		entry["sellTo"] = (info.isTrade() and iMet - holders.get(szTech, 0)) or 0
		entry["xmlTradeable"] = bool(info.isTrade())
		entry["leadsTo"] = [effect["target"] for effect in effects[szTech] if effect["effect"] == "leadsTo"]
		# <!-- custom: sas-ci-string-compare-exemption: The technology report uses a stable prerequisite kind. (GPT-6.2-Sol) -->
		unlocks = [effect["target"] for effect in effects[szTech] if effect["effect"] == "prerequisite"]
		entry["unlocks"] = unlocks
		needs = []
		for szTarget in unlocks:
			iType = _findOptionalInfoType(szTarget)
			if iType < 0:
				continue
			# <!-- custom: At turn 77 of the 2026-11-19 validation run Code of Laws read as meeting happiness through the Palace, which we already had (one per civ), while Polytheism read as nothing though it unlocks Temples, a special-building class whose buildings give happiness under a state religion.
			# So a maxed-out building class is skipped, and a special building stands for our civ's buildings of that class. (Claude code Opus 5.5) -->
			targets = []
			if szTarget.startswith("BUILDING_"):
				targets = [iType]
			elif szTarget.startswith("SPECIALBUILDING_"):
				targets = [i for i in range(gc.getNumBuildingInfos()) if gc.getBuildingInfo(i).getSpecialBuildingType() == iType and civ.getCivilizationBuildings(gc.getBuildingInfo(i).getBuildingClassType()) == i]
			for iBuilding in targets:
				building = gc.getBuildingInfo(iBuilding)
				szTarget = building.getType()
				if player.isBuildingClassMaxedOut(building.getBuildingClassType(), 0) or building.isCapital():
					continue
				# <!-- custom: A building that needs a religion counts only for our state religion or one already in our cities; the first version listed every faith's Temple. (Claude code Opus 5.5) -->
				iNeedReligion = building.getPrereqReligion()
				if iNeedReligion >= 0 and iNeedReligion != player.getStateReligion() and not [1 for city in cities if city.isHasReligion(iNeedReligion)]:
					continue
				iHappy = building.getHappiness() + (building.getStateReligionHappiness() > 0 and player.getStateReligion() >= 0 and building.getStateReligionHappiness() or 0)
				if building.getPrereqReligion() >= 0 and building.getPrereqReligion() != player.getStateReligion():
					iHappy = building.getHappiness()
				if iHappy > 0 and iHappyMargin <= 1:
					# <!-- custom: sas-ci-string-compare-exemption: The city audit uses stable happiness and health result keys. (GPT-6.2-Sol) -->
					needs.append("happiness (%s +%d; smallest happy margin %d%s)" % (szTarget, iHappy, iHappyMargin, (szBinding == "happiness" and ", binds first") or ""))
				if building.getHealth() > 0 and iHealthMargin <= 1:
					# <!-- custom: sas-ci-string-compare-exemption: The city audit uses stable happiness and health result keys. (GPT-6.2-Sol) -->
					needs.append("health (%s +%d; smallest health margin %d%s)" % (szTarget, building.getHealth(), iHealthMargin, (szBinding == "health" and ", binds first") or ""))
			if szTarget.startswith("UNIT_"):
				unitInfo = gc.getUnitInfo(iType)
				if unitInfo.getDomainType() == DomainTypes.DOMAIN_LAND and unitInfo.getCombat() > iBestStrength:
					szNeed = "stronger land unit (%s strength %d; best we train %d)" % (szTarget, unitInfo.getCombat(), iBestStrength)
					szResources = _unitResourceStatus(player, unitInfo, seenBonuses, info)
					if szResources:
						szNeed = "%s, %s" % (szNeed[:-1], szResources + ")")
					needs.append(szNeed)
		# <!-- custom: Mounted Combat listed eight stronger units, one line each; the first MEETS_NEEDS_SHOWN keep a case readable, with the count of the rest. (Claude code Opus 5.5) -->
		if len(needs) > MEETS_NEEDS_SHOWN:
			needs = needs[:MEETS_NEEDS_SHOWN] + ["and %d more" % (len(needs) - MEETS_NEEDS_SHOWN)]
		entry["meetsNeeds"] = needs
	return limits


def cmd_research(args):
	player = _player(args)
	# <!-- custom: The user's idea (2026-11-15): go by proximity and read techs in the tree's own layout rather than from memory. ahead=N lists every tech whose path holds at most N techs, sorted by F6 column then row, with its era. (Claude code Opus 5.5) -->
	if args.get("ahead") is not None:
		_requireOwnTeamUnderFog(args, player, "research progress")
		iFogTeam = _fogTeam(args)
		return _techsAhead(player, int(args["ahead"]), iFogTeam >= 0)
	if args.get("tech") is None:
		# <!-- custom: The list first held only the names, so choosing a tech meant a 'py' call per tech for what the window's tech chooser shows at a glance, its turns (fog-on playthrough, 2026-11-13).
		# Each entry now has its turns at the current rate, its cost and the progress already made. (Claude code Opus 5.5) -->
		team = gc.getTeam(player.getTeam())
		available = [{"tech": gc.getTechInfo(i).getType(), "turns": player.getResearchTurnsLeft(i, True), "cost": team.getResearchCost(i), "progress": team.getResearchProgress(i)} for i in range(gc.getNumTechInfos()) if player.canResearch(i, False)]
		if args.get("effects"):
			effects = _techEffects(player.getCivilizationType())
			for entry in available:
				entry["effects"] = effects[entry["tech"]]
		# <!-- custom: For each tech, the resources in sight whose improvement it would unlock, so "what would this tech do for the land we know" is read beside it: at turn 16 of the Continents replay (2026-11-19) the user looked through the resources to find that Agriculture had nothing to improve yet, and asked for it in the API. (Claude code Opus 5.5) -->
		uses = {}
		for resource in _command("resources")(args)["resources"]:
			for build in resource["builds"]:
				if not build["haveTech"] and build["tech"]:
					uses.setdefault(build["tech"], []).append("%s@%d,%d" % (resource["bonus"][6:], resource["x"], resource["y"]))
		for entry in available:
			entry["forOurResources"] = uses.get(entry["tech"], [])
		# <!-- custom: At turn 54 of the 2026-11-19 validation run the agent researched Calendar with no case for it, then nearly dropped it for The Wheel; the user asked whether it had read the market and a need.
		# So each tech comes with its case: who would sell it to us now (buy, don't research), how many met civs lack it while the XML lets it be traded (sell it on), and the techs it leads to.
		# A tech with none of these and no resource of ours to improve is named in 'reminders' (research). (Claude code Opus 5.5) -->
		limits = _addTechCases(player, args, available)
		# <!-- custom: The techs already known, as the tech screen shows them; at turn 0 of the Continents game (2026-11-19) they took a 'py' snippet, which the play role refuses. (Claude code Opus 5.5) -->
		known = [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if team.isHasTech(i)]
		return {"known": known, "available": available, "queue": _researchQueue(player), "limits": limits}
	iTech = _typedIndex(args["tech"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	# <!-- custom: Only techs available now were taken, so 'tech=TECH_BRONZE_WORKING' was refused while Mining was its one missing prerequisite (fog-on playthrough, 2026-11-13).
	# CvPlayer::pushResearch queues the missing prerequisites first, as the tech tree's shift-click does, so take any tech the player could ever research and does not have. (Claude code Opus 5.5) -->
	if gc.getTeam(player.getTeam()).isHasTech(iTech):
		raise ValueError("player %d already has %s" % (player.getID(), args["tech"]))
	if not player.canEverResearch(iTech):
		raise ValueError("player %d can never research %s" % (player.getID(), args["tech"]))
	# <!-- custom: pushResearch returns false when it could not queue the tech, and a clearing push may then leave the queue empty or partly filled (Codex's review); report it with the queue as it is. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Cleared here rather than by pushResearch's own flag: CvPlayer::pushResearch returns before clearing when the tech is already queued, so in the scouting trial (2026-11-14) 'research tech=TECH_AGRICULTURE', meant to restart the queue at the current tech, left Mining before Animal Husbandry. Progress is kept per tech, so clearing loses none. (Claude code Opus 5.5) -->
	if not args.get("append", False):
		player.clearResearchQueue()
	if not player.pushResearch(iTech, False):
		raise ValueError("could not queue %s; research queue now: %s" % (args["tech"], ", ".join([entry["tech"] for entry in _researchQueue(player)]) or "empty"))
	return {"research": _typeOrNone(gc.getTechInfo, player.getCurrentResearch()), "queue": _researchQueue(player)}


def _techsAhead(player, iMaxSteps, bFog):
	team = gc.getTeam(player.getTeam())
	memo = {}
	rows = []
	effects = _techEffects(player.getCivilizationType())
	# <!-- custom: The user's follow-up (2026-11-15): alternatives and rivals' techs help strategize.
	# Holders are the met players whose techs we can see, under fog only those canSeeTech allows, as in 'techs'. (Claude code Opus 5.5) -->
	others = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and not gc.getPlayer(i).isMinorCiv() and team.isHasMet(gc.getPlayer(i).getTeam())]
	if bFog:
		others = [other for other in others if player.canSeeTech(other.getID())]
	for iTech in range(gc.getNumTechInfos()):
		if team.isHasTech(iTech) or not player.canEverResearch(iTech):
			continue
		path = []
		_techPathVisit(player, team, iTech, path, {}, memo)
		if len(path) > iMaxSteps:
			continue
		info = gc.getTechInfo(iTech)
		rows.append({"tech": info.getType(), "era": _typeOrNone(gc.getEraInfo, info.getEra()), "grid": [info.getGridX(), info.getGridY()], "steps": len(path),
			"pathRemaining": sum([team.getResearchCost(i) - team.getResearchProgress(i) for i in path]), "pathTurns": sum([player.getResearchTurnsLeft(i, True) for i in path]),
			"path": [gc.getTechInfo(i).getType() for i in path[:-1]],
			"unlocks": [effect["target"] for effect in effects[info.getType()] if effect["effect"] in ("prerequisite", "reveals")],
			"holders": [other.getName() for other in others if gc.getTeam(other.getTeam()).isHasTech(iTech)], "xmlTradeable": bool(info.isTrade())})
		options = [info.getPrereqOrTechs(i) for i in range(gc.getNUM_OR_TECH_PREREQS()) if info.getPrereqOrTechs(i) >= 0]
		if len(options) > 1:
			rows[-1]["orChoice"] = [gc.getTechInfo(i).getType() for i in options]
	rows.sort(lambda a, b: cmp(a["grid"], b["grid"]))
	# <!-- custom: The user asked whether a rival is researching a tech, with its percent, or whether that is unknown (2026-11-15).
	# The game shows a rival's research only through espionage (K-Mod's canSeeResearch, as the Espionage Advisor does), so under fog the rest say unknown. (Claude code Opus 5.5) -->
	rivals = []
	for other in [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and not gc.getPlayer(i).isMinorCiv() and team.isHasMet(gc.getPlayer(i).getTeam())]:
		entry = {"player": other.getID(), "name": other.getName(), "research": "unknown"}
		iResearch = other.getCurrentResearch()
		if not bFog or player.canSeeResearch(other.getID()):
			entry["research"] = _typeOrNone(gc.getTechInfo, iResearch)
			if iResearch >= 0:
				otherTeam = gc.getTeam(other.getTeam())
				entry["percent"] = otherTeam.getResearchProgress(iResearch) * 100 / max(1, otherTeam.getResearchCost(iResearch))
				for row in rows:
					if row["tech"] == entry["research"]:
						row.setdefault("researchedBy", []).append(other.getName())
		rivals.append(entry)
	return {"ahead": rows, "rivals": rivals}


def _researchQueue(player):
	# <!-- custom: CyPlayer exposes no queue list, only each tech's position in it (1 is the current one), so rebuild the order from getQueuePosition. (Claude code Opus 5.5) -->
	queued = [(player.getQueuePosition(i), i) for i in range(gc.getNumTechInfos()) if player.isResearchingTech(i)]
	queued.sort()
	return [{"tech": gc.getTechInfo(i).getType(), "turns": player.getResearchTurnsLeft(i, False)} for (iPosition, i) in queued]


# <!-- custom: Order commands (Claude code Opus 5.5) -->


# <!-- custom: Missions that take no data, which can be queued behind others with data -1. (Claude code Opus 5.5) -->


_HELP["settle"] = "Give every idle group the first of MISSION_FORTIFY, MISSION_SLEEP or MISSION_SKIP it can start, as a player would before ending the turn: 'todo's idleUnits, once per group. MISSION_SKIP lasts one turn, so those units come back. args: player."


def cmd_settle(args):
	# <!-- custom: Written as a shell loop over 'todo' twice at turns 271-276 of the modern baseline (2026-11-14), the second time for 20 Musketmen upgraded to Riflemen, which come out awake as in the window.
	# The first loop gave each unit Fortify, else Sleep, else Skip, and Skip overrode a group-mate's Fortify, which already covered the unit but made its own Fortify fail; so order once per group, and only groups still awake. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	seen = {}
	result = []
	for unit in _units(player):
		group = unit.getGroup()
		if seen.has_key(group.getID()) or not group.readyToMove(False) or group.getLengthMissionQueue() != 0 or group.isAutomated():
			continue
		seen[group.getID()] = True
		szGiven = None
		for szMission in ("MISSION_FORTIFY", "MISSION_SLEEP", "MISSION_SKIP"):
			eMission = getattr(MissionTypes, szMission)
			if group.canStartMission(eMission, -1, -1, unit.plot(), False):
				group.pushMission(eMission, -1, -1, 0, False, True, MissionAITypes.NO_MISSIONAI, None, None)
				szGiven = szMission
				break
		result.append({"unit": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "groupSize": group.getNumUnits(), "mission": szGiven})
	return {"groups": result}


_HELP["wartargets"] = "War targets and threats side by side, facts rather than one score. Per player met: power against ours (per mille, where the scoreboard shows it), our frontier and the distance from their nearest seen city to ours (from 'borders'), cities seen, war, their attitude toward us and whether we are their worst enemy; then the diplomatic cost of a war on them: who is Pleased or Friendly with them (angered), who has them as worst enemy or fights them (pleased), who would join a war on them if asked, and the players a war on them also brings in, their defensive pacts, masters and vassals. 'threat' flags a rival at least as strong as us that is Annoyed or Furious with us, has us as worst enemy or fights us, however far away: an attack from far is rarer but happens. Sorted by frontier. args: player."


def cmd_wartargets(args):
	# <!-- custom: Named wartargets, as it first reused the name of the unit command 'targets' and its later definition silently replaced that one until Ruff's F811 caught it. (Claude code Opus 5.5) -->
	# <!-- custom: The user's points at turn 200 of a Large autoplay (2026-11-15): pick a target on more than weakness and nearness, as a war costs attitude with the target's friends (and expansion annoys some anyway), attacking someone's friend angers them, and a strong rival far away rarely attacks but is not harmless.
	# 'relations' and 'borders' each held part of this; this puts it in one row per player. (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	fronts = dict([(row["player"], row) for row in _command("borders")(args)["players"]])
	relations = _command("relations")(args)["players"]
	rows = []
	for entry in relations:
		iOther = entry["player"]
		other = gc.getPlayer(iOther)
		otherTeam = gc.getTeam(other.getTeam())
		front = fronts.get(iOther, {})
		row = {"player": iOther, "name": entry["name"], "powerRatioPerMille": entry.get("powerRatioPerMille"), "frontier": front.get("frontier", 0), "closestCityDistance": entry.get("closestCityDistance"),
			"citiesSeen": entry["citiesSeen"], "atWar": entry["atWar"], "attitudeToUs": entry["attitude"][9:], "attitudeValue": entry.get("attitudeValue"),
			"weAreWorstEnemy": bool(not otherTeam.isHuman() and other.getWorstEnemyName() and other.getWorstEnemyName() == team.getName())}
		angered = []
		pleased = []
		joiners = []
		for third in relations:
			if third["player"] == iOther:
				continue
			view = third["viewsOf"].get(entry["name"])
			if view is None:
				continue
			if view["attitude"] in ("PLEASED", "FRIENDLY"):
				angered.append(third["name"])
			if view["worstEnemy"] or view["atWar"]:
				pleased.append(third["name"])
			if view.get("wouldJoinWarIfAsked"):
				joiners.append(third["name"])
		row["angered"] = angered
		row["pleased"] = pleased
		row["wouldJoinIfAsked"] = joiners
		# <!-- custom: A war on a vassal is a war on its master, and a defensive pact brings the partner in; both are known to a player from the Foreign Advisor. (Claude code Opus 5.5) -->
		row["alsoAtWarWith"] = [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() != other.getTeam() and gc.getPlayer(i).getTeam() != player.getTeam()
			and team.isHasMet(gc.getPlayer(i).getTeam()) and (otherTeam.isDefensivePact(gc.getPlayer(i).getTeam()) or otherTeam.isVassal(gc.getPlayer(i).getTeam()) or gc.getTeam(gc.getPlayer(i).getTeam()).isVassal(other.getTeam()))]
		if otherTeam.isVassal(player.getTeam()):
			row["ourVassal"] = True
		iRatio = row["powerRatioPerMille"]
		row["threat"] = bool(iRatio is not None and iRatio >= 1000 and (row["attitudeToUs"] in ("ANNOYED", "FURIOUS") or row["weAreWorstEnemy"] or row["atWar"]))
		rows.append(row)
	rows.sort(lambda a, b: cmp(b["frontier"], a["frontier"]))
	return {"players": rows}


_HELP["rivalcities"] = "Rival cities near ours, as a player can judge them: per seen city within 'range' plots of our nearest city (default 12; player=<id> of the owner to keep one rival), its owner, population, capital, coast, the defense bonus its city bar shows, the defenders on it when we see the plot now, the bonuses in its radius we do not have, and an estimate of its food surplus and production from the tiles we have seen, assuming it works its best tiles for its population. Beside them our cities' population (average and largest) and the game's progress. args: range, owner, player."


def cmd_rivalcities(args):
	# <!-- custom: The user's next step in choosing a target at turn 200 of a Large autoplay (2026-11-15): look at the nearby cities, how well guarded, which bonuses they have that we lack, their population against ours and the game's stage, their growth and production; estimated from the yields we can see when we cannot look inside. (Claude code Opus 5.5) -->
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "rival cities")
	iTeam = _fogTeam(args)
	iSeeTeam = player.getTeam()
	team = gc.getTeam(iSeeTeam)
	iRange = int(args.get("range", 12))
	ours = _cities(player)
	if not ours:
		raise ValueError("player %d has no city to measure from" % player.getID())
	game = gc.getGame()
	pops = [city.getPopulation() for city in ours]
	result = {"turn": game.getGameTurn(), "estimatedEndTurn": game.getEstimateEndTurn(), "ourCities": len(ours), "ourAveragePopulation": sum(pops) / len(pops), "ourLargestPopulation": max(pops)}
	iFoodPerPop = gc.getFOOD_CONSUMPTION_PER_POPULATION()
	cities = []
	for iOwner in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOwner)
		if iOwner == player.getID() or not other.isAlive() or not team.isHasMet(other.getTeam()):
			continue
		if args.get("owner") is not None and int(args["owner"]) != iOwner:
			continue
		for city in _cities(other):
			if iTeam >= 0 and not city.isRevealed(iTeam, False):
				continue
			iDistance = min([plotDistance(city.getX(), city.getY(), mine.getX(), mine.getY()) for mine in ours])
			if iDistance > iRange:
				continue
			row = {"owner": iOwner, "ownerName": other.getName(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "distance": iDistance, "population": city.getPopulation(),
				"capital": bool(city.isCapital()), "coastal": bool(city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN())), "defensePercent": city.getDefenseModifier(False)}
			center = city.plot()
			# <!-- custom: Defenders only while we see the plot now, as the window shows a city's units; otherwise null, not an empty list, which would read as undefended. (Claude code Opus 5.5) -->
			row["defenders"] = None
			if iTeam < 0 or center.isVisible(iSeeTeam, False):
				units = [center.getUnit(i) for i in range(center.getNumUnits())]
				# <!-- custom: CyUnit.canDefend takes the plot, unlike CvUnit::canDefend's default argument: canDefend() failed with a Boost ArgumentError on the first run. (Claude code Opus 5.5) -->
				row["defenders"] = [{"unit": gc.getUnitInfo(unit.getUnitType()).getType(), "strength": unit.baseCombatStr(), "damage": unit.getDamage()} for unit in units if unit.canDefend(center) and not unit.isInvisible(iSeeTeam, False)]
			lacking = {}
			tiles = []
			for i in range(gc.getNUM_CITY_PLOTS()):
				plot = city.getCityIndexPlot(i)
				if plot is None or plot.isNone() or (iTeam >= 0 and not plot.isRevealed(iTeam, False)):
					continue
				iBonus = plot.getBonusType(iSeeTeam)
				iPlotOwner = plot.getOwner()
				if iTeam >= 0:
					iPlotOwner = plot.getRevealedOwner(iTeam, False)
				if iBonus >= 0 and iPlotOwner == iOwner and player.getNumAvailableBonuses(iBonus) == 0:
					lacking[gc.getBonusInfo(iBonus).getType()] = True
				# <!-- custom: Yields from what we have seen: the plot's nature for our team plus the improvement we last saw there, for the owner, not the live yield, which would tell of improvements built out of sight. (Claude code Opus 5.5) -->
				iImprovement = plot.getImprovementType()
				if iTeam >= 0:
					iImprovement = plot.getRevealedImprovementType(iTeam, False)
				yields = []
				# <!-- custom: Both yield calls are bound with some enum types themselves, so plain ints failed with Boost ArgumentErrors on the first runs: calculateNatureYield wants YieldTypes and TeamTypes, calculateImprovementYieldChange YieldTypes but ints for the improvement and player. (Claude code Opus 5.5) -->
				for iYield in range(3):
					iAmount = plot.calculateNatureYield(YieldTypes(iYield), TeamTypes(iSeeTeam), False)
					if iImprovement >= 0:
						iAmount += plot.calculateImprovementYieldChange(iImprovement, YieldTypes(iYield), iOwner, False)
					yields.append(max(0, iAmount))
				if i == 0:
					center_yields = yields
				elif iPlotOwner == iOwner:
					tiles.append(yields)
			row["bonusesWeLack"] = sorted(lacking.keys())
			# <!-- custom: Best tiles by food twice plus production plus commerce, as a city governor favours food; the estimate ignores specialists, buildings, health and happiness, so it is a rough guide. (Claude code Opus 5.5) -->
			tiles.sort(lambda a, b: cmp(2 * b[0] + b[1] + b[2], 2 * a[0] + a[1] + a[2]))
			worked = tiles[:city.getPopulation()]
			row["estimate"] = {"foodSurplus": center_yields[0] + sum([t[0] for t in worked]) - iFoodPerPop * city.getPopulation(), "production": center_yields[1] + sum([t[1] for t in worked]),
				"commerce": center_yields[2] + sum([t[2] for t in worked]), "tilesSeen": len(tiles), "tilesWorked": len(worked)}
			cities.append(row)
	cities.sort(lambda a, b: cmp(a["distance"], b["distance"]))
	result["cities"] = cities
	return result


_HELP["world"] = "What every player can know about the world, met or not, as the Info screen's Top 5 Cities / Wonders tab shows it: each world wonder built with its year (negative BC, as the tab dates it), and its owner and city only where the tab names them (our team, a player met, or a city seen; otherwise null); national and team wonders of our team and of met players in cities seen; every project built, its team named once met; the five top cities by the tab's own ranking with size, founding turn and world wonders, named with their owner only once seen, and from their wonders what a player can work out: the owner the Wonders list gives one of them (ownerFromWonders), the religions whose holy city it is (a shrine), and foundedAtStart (a capital, so each is another civilization); how many rivals are alive against how many we have met (the Victory screen's Rivals left); each founded religion's turn and world influence with its holy city and leader once seen, each corporation's headquarters once seen; and each vote source, whether its building stands, its builder once met, its religion and total votes. The rival averages in 'demographics' count unmet rivals too. args: player."


def cmd_world(args):
	# <!-- custom: The user's point at turn 120 of a SAS48 island autoplay (2026-11-15): with only 2 of the rivals met, the Wonders tab still dated 20 wonders built by "Unknown" owners and the Top 5 Cities showed four unknown cities' sizes, founding dates and wonders.
	# Public intelligence a player has, which no command read.
	# Follows CvInfoScreen's tests. (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	iTeam = player.getTeam()
	wonders = []
	nationalWonders = []
	ranked = []
	# <!-- custom: The wonder buildings are found once, not per city: the first version tested every building's XML for every city, and at turn 120 of the SAS48 islands save (48 players) world took 52 ms in game, and 4 ms after this change, with the same reply. (Claude code Opus 5.5) -->
	worldWonderIds = []
	nationalWonderIds = []
	for iBuilding in range(gc.getNumBuildingInfos()):
		info = gc.getBuildingInfo(iBuilding)
		buildingClass = gc.getBuildingClassInfo(info.getBuildingClassType())
		if buildingClass.getMaxGlobalInstances() > -1:
			worldWonderIds.append((iBuilding, info.getType()))
		# <!-- custom: The tab's National Wonders mode (the user's follow-up): national and team wonders of our team, and of a met player only in a city we have seen, so these are not public like world wonders. (Claude code Opus 5.5) -->
		elif (buildingClass.getMaxPlayerInstances() > -1 or buildingClass.getMaxTeamInstances() > -1) and not info.isCapital():
			nationalWonderIds.append((iBuilding, info.getType()))
	for iOwner in range(gc.getMAX_PLAYERS()):
		owner = gc.getPlayer(iOwner)
		if not owner.isAlive():
			continue
		bKnown = owner.getTeam() == iTeam or team.isHasMet(owner.getTeam())
		for city in _cities(owner):
			bSeen = city.isRevealed(iTeam, False)
			cityWonders = []
			if owner.getTeam() == iTeam or (bKnown and bSeen):
				for iBuilding, szType in nationalWonderIds:
					if city.getNumBuilding(iBuilding) > 0:
						nationalWonders.append({"wonder": szType, "year": city.getBuildingOriginalTime(iBuilding), "owner": owner.getName(), "city": city.getName()})
			for iBuilding, szType in worldWonderIds:
				if city.getNumBuilding(iBuilding) > 0:
					cityWonders.append(szType)
					entry = {"wonder": szType, "year": city.getBuildingOriginalTime(iBuilding), "owner": None, "city": None}
					# <!-- custom: As the tab's list does (advc.001d): the owner is named for our team, a player met or a city seen, as its borders' colour tells whose it is; the city only once seen. (Claude code Opus 5.5) -->
					if bKnown or bSeen:
						entry["owner"] = owner.getName()
						entry["ownerId"] = iOwner
					if bSeen:
						entry["city"] = city.getName()
					wonders.append(entry)
			if not owner.isBarbarian():
				# <!-- custom: The tab's ranking, CvInfoScreen.calculateTopCities: (culture / 5 + food + production + gold rates) times population.
				# Its getFoodRate and the others are PyHelpers' PyCity wrappers over getYieldRate, which CyCity lacks: the first run failed on getFoodRate. (Claude code Opus 5.5) -->
				iValue = (city.getCulture(iOwner) / 5 + city.getYieldRate(YieldTypes.YIELD_FOOD) + city.getYieldRate(YieldTypes.YIELD_PRODUCTION) + city.getYieldRate(YieldTypes.YIELD_COMMERCE)) * city.getPopulation()
				row = {"population": city.getPopulation(), "founded": city.getGameTurnFounded(), "wonders": cityWonders, "name": None, "owner": None}
				if bSeen:
					row["name"] = city.getName()
					row["owner"] = owner.getName()
				ranked.append((iValue, row))
	wonders.sort(lambda a, b: cmp(a["year"], b["year"]))
	ranked.sort(lambda a, b: cmp(b[0], a[0]))
	# <!-- custom: The user hoped a top city's name would tell an unmet rival's civilization; it does not: unseen cities show "UNKNOWN", and AdvCiv (advc.001d) even dropped BtS's naming of a met player's unseen city.
	# Its wonder icons still tell what a player can work out from the two public lists: a wonder the Wonders tab gives an owner names the top city's owner (at turn 120 of the SAS48 islands save, the Natya Shastra made the third an unseen Maya city); a shrine marks a religion's holy city; a city founded on the start turn is a capital, so each is another civilization. (Claude code Opus 5.5) -->
	# <!-- custom: By player ID, not name: in the same save the Settings tab listed a second, unmet Pacal II of Maya beside the met one, as random setups can repeat a leader or civilization. (Claude code Opus 5.5) -->
	wonderOwners = {}
	for entry in wonders:
		if entry["owner"] is not None:
			wonderOwners[entry["wonder"]] = entry["ownerId"]
	iStartTurn = gc.getGame().getStartTurn()
	for (iValue, row) in ranked[:5]:
		row["foundedAtStart"] = row["founded"] == iStartTurn
		row["holyCityOf"] = []
		inferred = []
		for szWonder in row["wonders"]:
			info = gc.getBuildingInfo(getInfoTypeOrFail(szWonder))
			iReligion = info.getHolyCity()
			if iReligion == -1:
				iReligion = info.getGlobalReligionCommerce()
			if iReligion != -1:
				row["holyCityOf"].append(gc.getReligionInfo(iReligion).getType())
			if row["owner"] is None and wonderOwners.has_key(szWonder) and wonderOwners[szWonder] not in inferred:
				inferred.append(wonderOwners[szWonder])
		row["ownerFromWonders"] = None
		if len(inferred) == 1:
			row["ownerFromWonders"] = {"id": inferred[0], "name": gc.getPlayer(inferred[0]).getName()}
	rivals =[gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isMinorCiv() and gc.getPlayer(i).getTeam() != iTeam]
	game = gc.getGame()
	# <!-- custom: The tab's Projects mode: every project any team has built is listed, its team named only for ours or a met one, and without a date, as the tab shows them; so a mod-mod's early project shows up even from players not met. (Claude code Opus 5.5) -->
	projects = []
	for iLoopTeam in range(gc.getMAX_TEAMS()):
		loopTeam = gc.getTeam(iLoopTeam)
		if not loopTeam.isAlive() or loopTeam.isBarbarian():
			continue
		for iProject in range(gc.getNumProjectInfos()):
			for i in range(loopTeam.getProjectCount(iProject)):
				builder = None
				if iLoopTeam == iTeam or team.isHasMet(iLoopTeam):
					builder = loopTeam.getName()
				projects.append({"project": gc.getProjectInfo(iProject).getType(), "builder": builder})
	# <!-- custom: The Policy Advisor's Religions and Corporations tabs, the user's next pointer at the same turn: every founded religion's date and world influence, which count unmet civs, but its holy city and leader only once the city is seen, as CvPolicyAdvisorScreen tests (advc.001d); likewise a corporation's headquarters. (Claude code Opus 5.5) -->
	religions = []
	for iReligion in range(gc.getNumReligionInfos()):
		iFounded = game.getReligionGameTurnFounded(iReligion)
		if iFounded < 0:
			continue
		row = {"religion": gc.getReligionInfo(iReligion).getType(), "foundedTurn": iFounded, "influencePercent": game.calculateReligionPercent(iReligion), "holyCity": None, "leader": None}
		holy = game.getHolyCity(iReligion)
		if not holy.isNone() and holy.isRevealed(iTeam, False):
			row["holyCity"] = holy.getName()
			row["leader"] = gc.getPlayer(holy.getOwner()).getName()
		religions.append(row)
	corporations = []
	for iCorporation in range(gc.getNumCorporationInfos()):
		iFounded = game.getCorporationGameTurnFounded(iCorporation)
		if iFounded < 0:
			continue
		row = {"corporation": gc.getCorporationInfo(iCorporation).getType(), "foundedTurn": iFounded, "headquarters": None, "owner": None}
		hq = game.getHeadquarters(iCorporation)
		if not hq.isNone() and hq.isRevealed(iTeam, False):
			row["headquarters"] = hq.getName()
			row["owner"] = gc.getPlayer(hq.getOwner()).getName()
		corporations.append(row)
	# <!-- custom: The Victory screen's diplomatic rows and Resolutions tab: whether each vote building stands, its builder only when met ("Built by An Unknown Civilization" otherwise, which raised KI#118.2 before its fix), the vote source's religion, and its total votes, which grow with that religion's or the world's population, met or not. (Claude code Opus 5.5) -->
	voteSources = []
	for iSource in range(gc.getNumVoteSourceInfos()):
		row = {"voteSource": gc.getVoteSourceInfo(iSource).getType(), "built": False, "builder": None, "religion": _typeOrNone(gc.getReligionInfo, game.getVoteSourceReligion(iSource))}
		for iBuilding in range(gc.getNumBuildingInfos()):
			if gc.getBuildingInfo(iBuilding).getVoteSourceType() != iSource:
				continue
			iClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
			for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
				loopTeam = gc.getTeam(iLoopTeam)
				if loopTeam.isAlive() and not loopTeam.isBarbarian() and loopTeam.getBuildingClassCount(iClass) > 0:
					row["built"] = True
					if iLoopTeam == iTeam or team.isHasMet(iLoopTeam):
						row["builder"] = loopTeam.getName()
		bActive = game.isDiploVote(iSource)
		if bActive:
			# <!-- custom: Match Victory Members' election weight.
			# Some resolutions vote by cities or civilizations instead of population, so taking the maximum mixes different ballots.
			# Keep the public total and list only known members under fog. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			aiVotes = [i for i in range(gc.getNumVoteInfos()) if gc.getVoteInfo(i).isVoteSourceType(iSource)]
			iElection = -1
			for iVote in aiVotes:
				if gc.getVoteInfo(iVote).isSecretaryGeneral():
					iElection = iVote
					break
			iSecretary = -1
			if iElection >= 0:
				iSecretary = game.getSecretaryGeneral(iSource)
				row["totalVotes"] = game.countPossibleVote(iElection, iSource)
			else:
				row["totalVotes"] = max([0] + [game.countPossibleVote(iVote, iSource) for iVote in aiVotes])
			bFog = _fogTeam(args) >= 0
			members = []
			for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
				member = gc.getPlayer(iPlayer)
				if not member.isAlive() or not member.isVotingMember(iSource):
					continue
				if bFog and member.getTeam() != iTeam and not team.isHasMet(member.getTeam()):
					continue
				iVotes = None
				if iElection >= 0:
					iVotes = member.getVotes(iElection, iSource)
				entry = {"player": iPlayer, "name": member.getName(), "votes": iVotes, "status": member.isFullMember(iSource) and "full" or "voting"}
				if member.getTeam() == iSecretary:
					entry["status"] = "secretaryGeneral"
				members.append(entry)
			members.sort(lambda a, b: cmp(b["votes"], a["votes"]))
			row["members"] = members
		# <!-- custom: The Victory screen's Resolutions tab rows (CvVictoryScreen.drawResolutionTable): each resolution the source can choose, a diplomatic victory only while that victory is valid (advc.178), with the votes required and possible while the source is active, and whether it passed; an inactive source keeps its resolutions and outcomes, as the tab does.
		# The 2026-11-22 tab audit found no command for them: 'world' gave the members only. See KI#1110. (Claude code Opus 5.5) -->
		if bActive or row["built"]:
			resolutions = []
			for iVote in range(gc.getNumVoteInfos()):
				info = gc.getVoteInfo(iVote)
				if not info.isVoteSourceType(iSource) or not game.isChooseElection(iVote) or (info.isVictory() and not game.isDiploVictoryValid()):
					continue
				entry = {"resolution": info.getType(), "passed": bool(game.isVotePassed(iVote))}
				if bActive:
					iPossible = game.countPossibleVote(iVote, iSource)
					if iPossible <= 0:
						continue
					entry["required"] = game.getVoteRequired(iVote, iSource)
					entry["total"] = iPossible
				resolutions.append(entry)
			row["resolutions"] = resolutions
		voteSources.append(row)
	return {"wonders": wonders, "topCities": [row for (iValue, row) in ranked[:5]], "rivalsAlive": len(rivals), "rivalsMet": len([p for p in rivals if team.isHasMet(p.getTeam())]), "religions": religions, "corporations": corporations, "voteSources": voteSources, "nationalWonders": nationalWonders, "projects": projects}


_HELP["timeline"] = "The Info screen's Timeline tab as entries, newest first: the same filter, so only what the player may know: events of met players in plots revealed to us (era changes, first discoveries, Great People born, cities founded where we saw the owner, wars, wonders), plus the public announcements every player gets, religion and corporation foundings and world wonders, in their faraway-land form where the tab words them so. Each entry has its turn, date, text, kind (MAJOR_EVENT or CITY_FOUNDED), its player once met (else null) and public (a public announcement). since=<turn> keeps later turns, find=<text> entries whose text holds it (any case), public=1 only public announcements; limit (default 40) caps the list, 'total' counts every match. args: since, find, public, limit, player."


def cmd_timeline(args):
	# <!-- custom: The user's follow-up after the public-information survey (2026-11-15): the Timeline shows met rivals' era changes, first discoveries and Great People, which no command read.
	# Uses CvInfoScreen.getTimelineRecords on a copy of the screen object set to our perspective, never reveal-all, so SASPilot and the tab share one filter and the open screen's own state and cache stay untouched.
	# A 2026-11-20 merge slip in that method broke this command and the tab alike. See KI#1101. (Claude code Opus 5.5) -->
	# <!-- custom: The screen's session settings, which getTimelineRecords reads, are set when the screen object is made since 2026-11-28: read only when it opened, this command failed in a session where the Info screen had not been opened. See KI#1101.2. (Claude code Opus 5.5) -->
	import copy
	player = _player(args)
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	view = copy.copy(CvScreensInterface.infoScreen)
	view.iActivePlayer = player.getID()
	view.pActivePlayer = player
	view.iActiveTeam = iTeam
	view.pActiveTeam = team
	view.bRevealAll = False
	# <!-- custom: The screen sets TEXT_TIMELINE_UNKNOWN_CITY in initText when it opens, not in __init__: the first run, with the Info screen never opened, failed on that attribute.
	# Calling initText then failed on X_EXIT, as it also sizes the layout, so only the one text the records need is set here, from the screen's own key. (Claude code Opus 5.5) -->
	view.TEXT_TIMELINE_UNKNOWN_CITY = CyTranslator().getText("TXT_KEY_SAS_INFO_TIMELINE_UNKNOWN_CITY", ())
	replayInfo = CyReplayInfo()
	replayInfo.createInfo(player.getID())
	kinds = {}
	for szName in ("REPLAY_MESSAGE_MAJOR_EVENT", "REPLAY_MESSAGE_CITY_FOUNDED", "REPLAY_MESSAGE_PLOT_OWNER_CHANGE"):
		eKind = getattr(ReplayMessageTypes, szName, None)
		if eKind is not None:
			kinds[int(eKind)] = szName[len("REPLAY_MESSAGE_"):]
	iSince = int(args.get("since", -1))
	szFind = args.get("find", "").lower()
	bPublicOnly = str(args.get("public", "0")) == "1"
	iLimit = int(args.get("limit", 40))
	entries = []
	iTotal = 0
	for iTurn, szDate, szText, eColor, iPlayer, eKind, bMet, bPublic in view.getTimelineRecords(replayInfo):
		if iTurn < iSince or (bPublicOnly and not bPublic) or (szFind and szText.lower().find(szFind) == -1):
			continue
		iTotal += 1
		if len(entries) >= iLimit:
			continue
		szPlayer = None
		# <!-- custom: The record carries the replay's own player even for an unmet one, whose name a player does not know, so it is named only once met. (Claude code Opus 5.5) -->
		if iPlayer > -1 and (bMet or gc.getPlayer(iPlayer).getTeam() == iTeam):
			szPlayer = gc.getPlayer(iPlayer).getName()
		entries.append({"turn": iTurn, "date": szDate, "text": szText, "kind": kinds.get(int(eKind), int(eKind)), "player": szPlayer, "public": bool(bPublic)})
	return {"entries": entries, "total": iTotal, "turn": gc.getGame().getGameTurn()}


# <!-- custom: The AI personality fields the Sevopedia's leader panel shows that most change a game (the user's point: Gandhi, Willem and Pacal do not make the same game as Montezuma, Boudica and Caesar). (Claude code Opus 5.5) -->
_PERSONALITY_FIELDS = (("totalWar", "getMaxWarRand"), ("limitedWar", "getLimitedWarRand"), ("dogpileWar", "getDogpileWarRand"), ("makePeace", "getMakePeaceRand"), ("nearbyWarPowerRatio", "getMaxWarNearbyPowerRatio"), ("baseAttitude", "getBaseAttitude"), ("peaceWeight", "getBasePeaceWeight"), ("warmongerRespect", "getWarmongerRespect"), ("wonders", "getWonderConstructRand"), ("buildUnits", "getBuildUnitProb"), ("razeCity", "getRazeCityProb"), ("riskyAttacks", "getBaseAttackOddsChange"), ("cultureVictory", "getCultureVictoryWeight"), ("spaceVictory", "getSpaceVictoryWeight"), ("conquestVictory", "getConquestVictoryWeight"), ("dominationVictory", "getDominationVictoryWeight"), ("diplomacyVictory", "getDiplomacyVictoryWeight"))


def _personality(eLeader):
	# <!-- custom: raw is the live XML value; rank is the panel's own 0-100 standing among all leaders from its predumped cache (SevoPediaLeaderCachePredumped), already inverted where a lower raw value means more of it, e.g. a lower iMaxWarRand means total war more often, so a higher rank always means more of what the field names.
	# The cache is keyed by leader index; CI's aip_predump_values.py checks it against the leader XML, and on 2026-11-15 all 4290 values matched the live game. (Claude code Opus 5.5) -->
	import SevoPediaLeaderCachePredumped
	leaderInfo = gc.getLeaderHeadInfo(eLeader)
	cached = SevoPediaLeaderCachePredumped.LEADERS_INFO_CACHED.get(eLeader, {})
	row = {}
	for szName, szGetter in _PERSONALITY_FIELDS:
		iRank = None
		if cached.has_key(szGetter):
			iRank = cached[szGetter][1]
		row[szName] = {"raw": getattr(leaderInfo, szGetter)(), "rank": iRank}
	row["favoriteCivic"] = None
	if leaderInfo.getFavoriteCivic() != -1:
		row["favoriteCivic"] = gc.getCivicInfo(leaderInfo.getFavoriteCivic()).getType()
	return row


def _leaderFacts(eLeader):
	# <!-- custom: A leader's type, traits and AI personality, shared by settings' named leaders and its possibleLeaders, which first rebuilt the traits inline. (Claude code Opus 5.5) -->
	leaderInfo = gc.getLeaderHeadInfo(eLeader)
	return {"leader": leaderInfo.getType(), "traits": [gc.getTraitInfo(i).getType() for i in range(gc.getNumTraitInfos()) if leaderInfo.hasTrait(i)], "personality": _personality(eLeader)}


def _settingsCiv(eLeader, eCiv):
	# <!-- custom: A leader's traits and a civilization's unique units and buildings, as XML facts the Sevopedia shows anyone; None where the Settings tab does not tell which leader or civilization it is. (Claude code Opus 5.5) -->
	row = {"leader": None, "traits": None, "personality": None, "civilization": None, "uniqueUnits": None, "uniqueBuildings": None}
	if eLeader != -1:
		row.update(_leaderFacts(eLeader))
	if eCiv != -1:
		civ = gc.getCivilizationInfo(eCiv)
		row["civilization"] = civ.getType()
		row["uniqueUnits"] = []
		for iClass in range(gc.getNumUnitClassInfos()):
			eUnit = civ.getCivilizationUnits(iClass)
			if eUnit != -1 and eUnit != gc.getUnitClassInfo(iClass).getDefaultUnitIndex():
				row["uniqueUnits"].append(gc.getUnitInfo(eUnit).getType())
		row["uniqueBuildings"] = []
		for iClass in range(gc.getNumBuildingClassInfos()):
			eBuilding = civ.getCivilizationBuildings(iClass)
			if eBuilding != -1 and eBuilding != gc.getBuildingClassInfo(iClass).getDefaultBuildingIndex():
				row["uniqueBuildings"].append(gc.getBuildingInfo(eBuilding).getType())
	return row


_HELP["settings"] = "The Victory screen's Settings tab: the game being played. Our leader and civilization with traits, unique units and buildings, and whether we were chosen at random; difficulty (ours, the game's, and the AI's under Rise and Fall); map script, world size with the real grid, climate, sea level, non-default map options and the AI's land-heavy / naval-heavy reading of the map; players ever alive and whether all or none were random; starting era and turn, game speed; game options, disabled victories, Aggressive AI, Advanced Start points, and in multiplayer its options, turn limit and city elimination; the mod build running and the builds the save was made with. Then the rivals as the tab lists them: those met with ID, name, leader, civilization, traits and uniques, and, when the civilizations and leaders chosen at setup are known (advc.190c), those not met that were not random, with only the leader or the civilization when the other was random (then possibleLeaders with their traits, or possibleCivilizations, the picks the known half allows unless Lead Any Civ is on), and a count of fully random ones (unknownRivals). Every leader named comes with its AI personality as the Sevopedia's leader panel ranks it: war odds (total, limited, dogpile), making peace, attitude, peace weight, respect for warmongers, wonders, units, razing, risky attacks, each victory's weight and the favorite civic, each with its raw XML value and its 0-100 rank among all leaders (higher means more of it). args: player."


def cmd_settings(args):
	# <!-- custom: The user's point (2026-11-15): you need to know what game you are playing before making decisions.
	# Follows CvVictoryScreen.showGameSettingsScreen line by line; the tab shows a rival not met only when the setup is known and that pick was not random, the same here. (Claude code Opus 5.5) -->
	player = _player(args)
	g = gc.getGame()
	m = gc.getMap()
	bSetupKnown = g.isCivLeaderSetupKnown()
	bAllRandom = bSetupKnown
	bNoneRandom = bSetupKnown
	if bSetupKnown:
		for i in range(gc.getMAX_CIV_PLAYERS()):
			p = gc.getPlayer(i)
			if not p.isEverAlive() or p.isMinorCiv():
				continue
			if p.wasCivRandomlyChosen() or p.wasLeaderRandomlyChosen():
				bNoneRandom = False
			if not p.wasCivRandomlyChosen() or not p.wasLeaderRandomlyChosen():
				bAllRandom = False
	us = _settingsCiv(player.getLeaderType(), player.getCivilizationType())
	us["name"] = player.getName()
	us["civRandom"] = None
	us["leaderRandom"] = None
	if bSetupKnown and not bAllRandom and not bNoneRandom:
		us["civRandom"] = bool(player.wasCivRandomlyChosen())
		us["leaderRandom"] = bool(player.wasLeaderRandomlyChosen())
	handicap = {"player": gc.getHandicapInfo(player.getHandicapType()).getType(), "game": gc.getHandicapInfo(g.getHandicapType()).getType(), "ai": None}
	if g.isOption(GameOptionTypes.GAMEOPTION_RISE_FALL):
		handicap["ai"] = gc.getHandicapInfo(g.getAIHandicap()).getType()
	mapOptions = []
	for i in range(m.getNumCustomMapOptions()):
		szDesc = m.getNonDefaultCustomMapOptionDesc(i)
		if len(szDesc) > 0:
			mapOptions.append(szDesc)
	result = {"us": us, "handicap": handicap, "mapScript": m.getMapScriptName(), "worldSize": gc.getWorldInfo(m.getWorldSize()).getType(), "grid": [m.getGridWidth(), m.getGridHeight()], "climate": gc.getClimateInfo(m.getClimate()).getType(), "seaLevel": gc.getSeaLevelInfo(m.getSeaLevel()).getType(), "mapOptions": mapOptions, "mapOptionsAll": _mapOptionsAll(m.getMapScriptName()), "landHeavy": bool(g.isLandHeavyMapnameCached()), "navalHeavy": bool(g.isNavalHeavyMapnameCached())}
	result["playersEverAlive"] = g.countCivPlayersEverAlive()
	result["allRandom"] = bAllRandom
	result["noneRandom"] = bNoneRandom and not g.isScenario()
	result["startEra"] = gc.getEraInfo(g.getStartEra()).getType()
	result["startTurn"] = g.getStartTurn()
	result["gameSpeed"] = gc.getGameSpeedInfo(g.getGameSpeedType()).getType()
	result["options"] = [gc.getGameOptionInfo(i).getType() for i in range(GameOptionTypes.NUM_GAMEOPTION_TYPES) if g.isOption(i)]
	result["victoriesDisabled"] = [gc.getVictoryInfo(i).getType() for i in range(gc.getNumVictoryInfos()) if not g.isVictoryValid(i)]
	result["legacyAI"] = bool(g.useKModAI())
	result["advancedStartPoints"] = None
	if g.isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START):
		result["advancedStartPoints"] = g.getNumAdvancedStartPoints()
	if g.isGameMultiPlayer():
		result["mpOptions"] = [gc.getMPOptionInfo(i).getType() for i in range(gc.getNumMPOptionInfos()) if g.isMPOption(i)]
		result["maxTurns"] = g.getMaxTurns()
		result["maxCityElimination"] = g.getMaxCityElimination()
	met = []
	notMet = []
	iUnknown = 0
	for i in range(gc.getMAX_CIV_PLAYERS()):
		p = gc.getPlayer(i)
		if not p.isEverAlive() or i == player.getID() or p.isMinorCiv():
			continue
		if gc.getTeam(p.getTeam()).isHasMet(player.getTeam()):
			row = _settingsCiv(p.getLeaderType(), p.getCivilizationType())
			row["id"] = i
			row["name"] = p.getName()
			row["alive"] = bool(p.isAlive())
			met.append(row)
		elif bSetupKnown:
			if p.wasCivRandomlyChosen() and p.wasLeaderRandomlyChosen():
				iUnknown += 1
				continue
			eLeader = -1
			eCiv = -1
			if not p.wasLeaderRandomlyChosen():
				eLeader = p.getLeaderType()
			if not p.wasCivRandomlyChosen():
				eCiv = p.getCivilizationType()
			row = _settingsCiv(eLeader, eCiv)
			# <!-- custom: A random pick is drawn from what the known half allows (CvInitCore: a random leader among the civilization's isLeaders, a random civilization among the playable ones that list the leader), unless Lead Any Civ is on, so a player narrows it with the Sevopedia: at turn 120 of the SAS48 islands save, five rivals were listed by civilization only. (Claude code Opus 5.5) -->
			row["possibleLeaders"] = None
			row["possibleCivilizations"] = None
			if not g.isOption(GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV):
				if eLeader == -1 and eCiv != -1:
					civ = gc.getCivilizationInfo(eCiv)
					row["possibleLeaders"] = [_leaderFacts(l) for l in range(gc.getNumLeaderHeadInfos()) if civ.isLeaders(l)]
				if eCiv == -1 and eLeader != -1:
					row["possibleCivilizations"] = [gc.getCivilizationInfo(c).getType() for c in range(gc.getNumCivilizationInfos()) if gc.getCivilizationInfo(c).isPlayable() and gc.getCivilizationInfo(c).isLeaders(eLeader)]
			notMet.append(row)
	# <!-- custom: The tab's last Settings rows: the mod build running and the builds this save was made and continued with. (Claude code Opus 5.5) -->
	import CvModName
	result["runtimeSource"] = CvModName.getDisplayNameAndVersion()
	result["saveHistory"] = [{"version": CvModName.formatVersionDetails(g.getSASVersionHistoryVersion(i), g.getSASVersionHistoryCommitHash(i), g.getSASVersionHistoryDirtyState(i)), "turn": g.getSASVersionHistoryTurn(i)} for i in range(g.getNumSASVersionHistoryEntries())]
	result["setupKnown"] = bool(bSetupKnown)
	result["met"] = met
	result["notMet"] = notMet
	result["unknownRivals"] = iUnknown
	return result


_HELP["victory"] = "The Victory screen's Victories tab, per victory still valid: Time (turns left, our score and the best met team's), Conquest (rivals left, met, our vassals), Domination (the population and land shares needed, ours, the best met team's), Cultural (Legendary cities needed and their culture, our best cities' culture and turns to it, and the best met team's seen cities), Space Race (each part needed, ours and the best met team's). The tab's percentages divide by the whole world, unmet players included, so 'world' gives what they imply: the world's population and land plots, and the population held by everyone but us. Vote sources are in 'world'. args: player."


def _victoryValue(loopTeam, szKind, iArg):
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szKind == "score":
		return gc.getGame().getTeamScore(loopTeam.getID())
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szKind == "population":
		return loopTeam.getTotalPopulation()
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szKind == "land":
		return loopTeam.getTotalLand()
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szKind == "project":
		return loopTeam.getProjectCount(iArg)
	return loopTeam.getBuildingClassCount(iArg)


def _victoryBestMet(iTeam, szKind, iArg=-1):
	# <!-- custom: The tab's 'best' column: the met team, not ours, with the highest value; None when no met team has any.
	# A value kind rather than a lambda, as AGENTS.md avoids closures in Civ4 Python. (Claude code Opus 5.5) -->
	team = gc.getTeam(iTeam)
	iBest = -1
	best = 0
	for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
		loopTeam = gc.getTeam(iLoopTeam)
		if iLoopTeam != iTeam and loopTeam.isAlive() and not loopTeam.isMinorCiv() and not loopTeam.isBarbarian() and team.isHasMet(iLoopTeam):
			value = _victoryValue(loopTeam, szKind, iArg)
			if value > best:
				best = value
				iBest = iLoopTeam
	if iBest == -1:
		return None
	return {"team": gc.getTeam(iBest).getName(), "teamId": iBest, "value": best}


def _victoryCultureCities(screenObject, iTeam, victory):
	return [{"city": c[1].getName(), "culture": c[0], "turnsLeft": c[2]} for c in screenObject.getListCultureCities(iTeam, victory)]


def cmd_victory(args):
	# <!-- custom: The user's follow-up after the Settings tab (2026-11-15).
	# Follows CvVictoryScreen.showVictoryConditionScreen; the culture rows reuse its getListCultureCities, which lists only cities the active team has seen (advc.001d). (Claude code Opus 5.5) -->
	player = _player(args)
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	g = gc.getGame()
	import GameUtil
	screenObject = CvScreensInterface.victoryScreen
	iTotalPop = g.getTotalPopulation()
	iLandPlots = gc.getMap().getLandPlots()
	iRivals = 0
	iMet = 0
	iVassals = 0
	for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
		loopTeam = gc.getTeam(iLoopTeam)
		if iLoopTeam != iTeam and loopTeam.isAlive() and not loopTeam.isMinorCiv() and not loopTeam.isBarbarian():
			iRivals += 1
			if team.isHasMet(iLoopTeam):
				iMet += 1
			if loopTeam.isVassal(iTeam):
				iVassals += 1
	# <!-- custom: Our share of world population and land is our total over the world's, which counts unmet players: so the world totals, and the population everyone but us holds, are public even before contact. (Claude code Opus 5.5) -->
	world = {"population": iTotalPop, "landPlots": iLandPlots, "ourPopulation": team.getTotalPopulation(), "populationNotOurs": iTotalPop - team.getTotalPopulation(), "ourLand": team.getTotalLand()}
	victories = []
	for iVictory in range(gc.getNumVictoryInfos()):
		if not g.isVictoryValid(iVictory):
			continue
		victory = gc.getVictoryInfo(iVictory)
		row = {"victory": victory.getType()}
		if victory.isEndScore() or victory.isTargetScore():
			row["score"] = g.getTeamScore(iTeam)
			row["bestMetScore"] = _victoryBestMet(iTeam, "score")
			if victory.isEndScore() and g.getMaxTurns() > g.getElapsedGameTurns():
				row["turnsLeft"] = g.getMaxTurns() - g.getElapsedGameTurns()
			if victory.isTargetScore() and g.getTargetScore() != 0:
				row["targetScore"] = g.getTargetScore()
		if victory.isConquest():
			row["rivalsLeft"] = iRivals
			row["rivalsMet"] = iMet
			row["ourVassals"] = iVassals
		if g.getAdjustedPopulationPercent(iVictory) > 0:
			bestPop = _victoryBestMet(iTeam, "population")
			if bestPop is not None:
				bestPop["percent"] = bestPop["value"] * 100.0 / max(1, iTotalPop)
			row["populationPercentNeeded"] = g.getAdjustedPopulationPercent(iVictory)
			row["ourPopulationPercent"] = team.getTotalPopulation() * 100.0 / max(1, iTotalPop)
			row["bestMetPopulation"] = bestPop
		if g.getAdjustedLandPercent(iVictory) > 0:
			bestLand = _victoryBestMet(iTeam, "land")
			if bestLand is not None:
				bestLand["percent"] = bestLand["value"] * 100.0 / max(1, iLandPlots)
			row["landPercentNeeded"] = g.getAdjustedLandPercent(iVictory)
			row["ourLandPercent"] = team.getTotalLand() * 100.0 / max(1, iLandPlots)
			row["bestMetLand"] = bestLand
		if victory.getReligionPercent() > 0:
			row["religionPercentNeeded"] = victory.getReligionPercent()
			row["religions"] = [{"religion": gc.getReligionInfo(i).getType(), "percent": g.calculateReligionPercent(i), "ourHolyCity": bool(team.hasHolyCity(i))} for i in range(gc.getNumReligionInfos()) if g.getReligionGameTurnFounded(i) >= 0]
		if victory.getCityCulture() != CultureLevelTypes.NO_CULTURELEVEL and victory.getNumCultureCities() > 0:
			iThreshold = GameUtil.getCultureThreshold(victory.getCityCulture())
			row["cultureCitiesNeeded"] = victory.getNumCultureCities()
			row["cultureLevel"] = gc.getCultureLevelInfo(victory.getCityCulture()).getType()
			row["cultureThreshold"] = iThreshold
			row["ourCultureCities"] = _victoryCultureCities(screenObject, iTeam, victory)
			# <!-- custom: As the tab picks it (K-Mod): the met team whose best seen cities, each capped at the threshold, hold the most culture. (Claude code Opus 5.5) -->
			iBestTeam = -1
			iBestTotal = 0
			for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
				loopTeam = gc.getTeam(iLoopTeam)
				if iLoopTeam != iTeam and loopTeam.isAlive() and not loopTeam.isMinorCiv() and not loopTeam.isBarbarian() and team.isHasMet(iLoopTeam):
					iTotal = 0
					for c in screenObject.getListCultureCities(iLoopTeam, victory):
						iTotal += min(c[0], iThreshold)
					if iTotal >= iBestTotal:
						iBestTotal = iTotal
						iBestTeam = iLoopTeam
			row["bestMetCultureCities"] = None
			if iBestTeam != -1:
				row["bestMetCultureCities"] = {"team": gc.getTeam(iBestTeam).getName(), "teamId": iBestTeam, "cities": _victoryCultureCities(screenObject, iBestTeam, victory)}
		parts = []
		for iProject in range(gc.getNumProjectInfos()):
			info = gc.getProjectInfo(iProject)
			if info.getVictoryThreshold(iVictory) > 0:
				parts.append({"project": info.getType(), "needed": info.getVictoryThreshold(iVictory), "minimum": info.getVictoryMinThreshold(iVictory), "ours": team.getProjectCount(iProject), "bestMet": _victoryBestMet(iTeam, "project", iProject)})
		if parts:
			row["spaceParts"] = parts
		buildings = []
		for iClass in range(gc.getNumBuildingClassInfos()):
			if gc.getBuildingClassInfo(iClass).getVictoryThreshold(iVictory) > 0:
				buildings.append({"buildingClass": gc.getBuildingClassInfo(iClass).getType(), "needed": gc.getBuildingClassInfo(iClass).getVictoryThreshold(iVictory), "ours": team.getBuildingClassCount(iClass), "bestMet": _victoryBestMet(iTeam, "buildingClass", iClass)})
		if buildings:
			row["buildings"] = buildings
		victories.append(row)
	return {"victories": victories, "world": world, "turn": g.getGameTurn()}


_HELP["reminders"] = "What a player would want pointed out, beyond what 'todo' says must be decided before the turn ends: no ship exploring while teams are unmet and seen water borders the unknown (waterScouting), unowned land of our landmass out of sight where Barbarians can spawn, with a plot to watch it from (fogBusting), no research, an empty build queue, a starving or angry city, a city growing within 5 turns past its happy or healthy limit, a wounded unit outside our borders, gold that runs out within ten turns at the current rate, and techs we could trade to a met player now; our research when a met civ would sell it, or when it has no case (no resource of ours, no buyer, no need met; research). A Settler queued or out while Workers number fewer than 2 per city less 1 or a city has no defender (expansionSupport); land still unknown within 6 plots of a city, by direction (homeUnknown); a city with 1 or less to spare in happiness or health: the limit binding first, trait effects, our resources of the other kind to trade away, met civs exporting what we lack and linked trade networks (happyHealth); a city making fewer than 3 hammers a turn, with its best unworked hammer tiles and the improvements on its tiles that would add hammers (lowProduction); a city's strong plots (a bonus or 4+ yield) that a rival owns or whose rival culture reaches 70% of ours, with the city's culture rate and the culture buildings it can build (borderPressure); a change since the last call in the 12 best city sites' priority, food, unknown plots or strong plots shared, or a site new or gone, as fog, resources, borders, wars and cities founded or destroyed all move them (sitesChanged; the first call records); a build a 1-citizen whip could finish in a city with no happy or health margin left (stalled, so growing wastes food) or whose citizen regrows within 6 turns, unless whip anger runs with at most one happy face to spare (whip). Each entry has its check, a text and the thing it is about. Only what the player's own screens show. A food bonus two or more of our cities reach, worked by none or by a city with more food than another that reaches it, comes with the 'work' click that moves it (sharedBonuses). A met rival whose attitude, the techs and resources it would trade, or the resources we could offer it (last copies marked) changed since the last call (rivalMoods; the first call states each). mute=CHECK silences a check for the session, mute=CHECK@x,y one entry by its plot; unmute=CHECK, CHECK@x,y or all lifts it; the muted list comes with each reply. args: player, mute, unmute."


def _remindResearch(player, args):
	if player.getCurrentResearch() < 0:
		return [{"text": "no research chosen"}]
	# <!-- custom: The user's rule at turn 74 of the islands replay (2026-11-15): being ahead lets a player sell each new tech to several rivals, while researching what everyone sells wastes the turns.
	# So current research that a met rival would trade us now is pointed out, with what no met rival has, to research and sell instead (from 'techs'). (Claude code Opus 5.5) -->
	market = _command("techs")({"player": player.getID(), "fog": args.get("fog")})
	iTech = player.getCurrentResearch()
	szTech = gc.getTechInfo(iTech).getType()
	sellers = []
	for entry in market["wanted"]:
		if entry["tech"] == szTech:
			sellers = [holder["name"] for holder in entry["holders"] if holder["canTrade"] and holder["denial"] is None]
	nobody = [entry["tech"] for entry in market["nobodyHas"] if entry["xmlTradeable"]]
	if sellers:
		return [{"text": "%s, our research, is for sale from %s: buy it, and research what no met rival has instead (%s)" % (szTech, ", ".join(sellers), ", ".join(nobody) or "none tradeable"), "tech": szTech, "sellers": sellers, "nobodyHas": nobody}]
	# <!-- custom: Research with no case at all: no resource of ours to improve, no met civ to sell it to, no need it meets (happiness, health, a stronger unit); the 2026-11-19 validation run researched Calendar that way.
	# Its leadsTo is given, as a tech can still be a step toward one with a case. (Claude code Opus 5.5) -->
	case = {"tech": szTech}
	_addTechCases(player, args, [case])
	uses = []
	for resource in _command("resources")(args)["resources"]:
		for build in resource["builds"]:
			if build["tech"] == szTech and not build["haveTech"]:
				uses.append(resource["bonus"])
	if uses or case["sellTo"] > 0 or case["meetsNeeds"]:
		return []
	return [{"text": "%s, our research, improves no resource we see, no met civ would buy it and it meets no current need; it leads to %s: check it fits the plan, or research a tech with a case ('research' lists each one's)" % (szTech, ", ".join(case["leadsTo"]) or "nothing"), "tech": szTech, "leadsTo": case["leadsTo"], "unlocks": case["unlocks"]}]


# <!-- custom: Turns of growth a food-as-production build may cost before the foodProductionTiming reminder speaks; beyond that, growing first delays the build more than it gains. (Claude code Opus 5.5) -->
FOOD_PRODUCTION_GROW_TURNS = 2


def _remindCities(player, args):
	result = []
	# <!-- custom: Units the current research makes obsolete: in SAS, Animal Husbandry obsoletes the Warrior, and at turn 18 of the 2026-11-19 validation run Dublin's queued Warrior and its 12 hammers vanished without a message when it landed. (Claude code Opus 5.5) -->
	eResearch = player.getCurrentResearch()
	obsoleted = []
	if eResearch >= 0:
		obsoleted = [i for i in range(gc.getNumUnitInfos()) if gc.getUnitInfo(i).getObsoleteTech() == eResearch]
	(city, iterator) = player.firstCity(False)
	while city:
		name = city.getName()
		if city.getOrderQueueLength() == 0:
			result.append({"text": "%s builds nothing" % name, "city": city.getID()})
		for eUnit in obsoleted:
			bQueued = city.getOrderQueueLength() > 0 and eUnit in [city.getOrderFromQueue(i).iData1 for i in range(city.getOrderQueueLength()) if city.getOrderFromQueue(i).eOrderType == OrderTypes.ORDER_TRAIN]
			iStored = city.getUnitProduction(eUnit)
			if bQueued or iStored > 0:
				result.append({"text": "%s: researching %s makes %s obsolete; it then leaves the queue and its %d stored hammers are lost: finish it first or build something else" % (name, gc.getTechInfo(eResearch).getType(), gc.getUnitInfo(eUnit).getType(), iStored), "city": city.getID(), "unit": gc.getUnitInfo(eUnit).getType(), "storedHammers": iStored})
		if city.foodDifference(True) < 0:
			result.append({"text": "%s starves: food %d a turn" % (name, city.foodDifference(True)), "city": city.getID()})
		if city.angryPopulation(0) > 0:
			result.append({"text": "%s has %d angry citizens" % (name, city.angryPopulation(0)), "city": city.getID()})
		# <!-- custom: A Settler or Worker turns the food surplus into production and stops growth, so a nearly full food bar waits; at turn 34 of the Continents replay (2026-11-19) Dublin started its Settler at 23 of 24 food, and the user noticed it could have grown first.
		# Named when the bar would fill within FOOD_PRODUCTION_GROW_TURNS turns with the surplus it has: building something else that long lets the city grow first. (Claude code Opus 5.5) -->
		if city.isFoodProduction():
			iSurplus = city.getYieldRate(YieldTypes.YIELD_FOOD) - city.foodConsumption(False, 0)
			iMissing = city.growthThreshold() - city.getFood()
			if iSurplus > 0 and iMissing > 0:
				iTurns = (iMissing + iSurplus - 1) / iSurplus
				if iTurns <= FOOD_PRODUCTION_GROW_TURNS:
					szItem = city.getOrderQueueLength() > 0 and str(_orderData(city.getOrderFromQueue(0))) or "its build"
					result.append({"text": "%s is %d food from size %d, but %s takes the food as production and stops growth: build something else %d turn(s) first to grow" % (name, iMissing, city.getPopulation() + 1, szItem, iTurns), "city": city.getID(), "growsInIfNotFoodProduction": iTurns})
		# <!-- custom: The user's idea while reading the domestic overview at turn 71 of the islands replay (2026-11-15): what the overview implies but does not say, a city about to grow past its happy or healthy limit.
		# Utrecht had one happy face to spare and grew in 7 turns.
		# Within 5 turns of growing, with no face to spare: the new citizen would be unhappy (works nothing) or unhealthy (costs a food each turn).
		# The city screen then shows why, and a happiness resource, a whip or a specialist are the usual answers. (Claude code Opus 5.5) -->
		iGrow = city.getFoodTurnsLeft()
		if city.foodDifference(True) > 0 and iGrow <= 5:
			iHappy = city.happyLevel() - city.unhappyLevel(0)
			iHealth = city.goodHealth() - city.badHealth(False)
			if iHappy <= 0:
				result.append({"text": "%s grows in %d turn(s) with no happy face to spare: the new citizen would be unhappy" % (name, iGrow), "city": city.getID(), "growsIn": iGrow, "happyMargin": iHappy, "limit": "happiness"})
			if iHealth <= 0:
				result.append({"text": "%s grows in %d turn(s) with no health to spare: the new citizen would cost a food each turn" % (name, iGrow), "city": city.getID(), "growsIn": iGrow, "healthMargin": iHealth, "limit": "health"})
		(city, iterator) = player.nextCity(iterator, False)
	return result


def _remindWounded(player, args):
	# <!-- custom: The scout that fought on at 15 HP outside our borders and died at turn 35 of the turn-0 game (2026-11-14): a wounded unit away from home should heal first. (Claude code Opus 5.5) -->
	result = []
	for unit in _units(player):
		if unit.getDamage() >= 30 and unit.plot().getOwner() != player.getID() and unit.canFight():
			result.append({"text": "%s %d is at %d%% health outside our borders" % (gc.getUnitInfo(unit.getUnitType()).getType(), unit.getID(), 100 - unit.getDamage(), ), "unit": unit.getID(), "x": unit.getX(), "y": unit.getY()})
	return result


def _remindUnfinished(player, args):
	# <!-- custom: Builds a city has hammers in but is not making now, which the city keeps (CvCity's per-unit and per-building production): the user advised at turn 119 of the turn-0 game (2026-11-14) not to leave a nearly done build, as a Worker one turn from done, after switching the queue; Hastings had switched from an Axeman to a Worker.
	# Each with its stored hammers, its cost and the turns it would take now; not every one is worth finishing, which stays the agent's choice. (Claude code Opus 5.5) -->
	# <!-- custom: The text said only "has 10 of 60 hammers in UNIT_WORKER, 6 turns from done now", which read as the current build right after a Monument was put first in Lisbon (JOAO turn-114 save, 2026-11-22); it now says the build is set aside. (Claude code Opus 5.5) -->
	result = []
	for city in _cities(player):
		iCurrentUnit = -1
		iCurrentBuilding = -1
		if city.isProductionUnit():
			iCurrentUnit = city.getProductionUnit()
		elif city.isProductionBuilding():
			iCurrentBuilding = city.getProductionBuilding()
		for i in range(gc.getNumUnitInfos()):
			iStored = city.getUnitProduction(i)
			if iStored > 0 and i != iCurrentUnit and city.canTrain(i, False, False):
				# <!-- custom: A Worker or Settler is built from food as well as hammers (isFoodProduction), so "hammers" misnamed its stored amount; say "production" for those (the user, 2026-11-22). (Claude code Opus 5.5) -->
				szStored = gc.getUnitInfo(i).isFoodProduction() and "production (food and hammers)" or "hammers"
				result.append({"text": "%s has %d of %d %s in %s, set aside behind its current build, %d turns from done if made now" % (city.getName(), iStored, player.getUnitProductionNeeded(i), szStored, gc.getUnitInfo(i).getType(), city.getUnitProductionTurnsLeft(i, 0)), "city": city.getID(), "item": gc.getUnitInfo(i).getType()})
		for i in range(gc.getNumBuildingInfos()):
			iStored = city.getBuildingProduction(i)
			if iStored > 0 and i != iCurrentBuilding and city.canConstruct(i, False, False, False):
				result.append({"text": "%s has %d of %d hammers in %s, set aside behind its current build, %d turns from done if made now" % (city.getName(), iStored, player.getBuildingProductionNeeded(i), gc.getBuildingInfo(i).getType(), city.getBuildingProductionTurnsLeft(i, 0)), "city": city.getID(), "item": gc.getBuildingInfo(i).getType()})
	return result


def _remindLosses(player, args):
	# <!-- custom: Units lost since the previous turn, from the messages the player was shown: at turns 84-89 of the turn-0 game (2026-11-14) a barbarian Archer killed the two Workers chopping near Nottingham, and the agent, reading each turn's digest cut to its last lines, missed "your Worker was destroyed" until the units were found gone at turn 90.
	# Matched on the English texts of CvUnit's combat and capture messages, so another language would not match. (Claude code Opus 5.5) -->
	result = []
	if not hasattr(gc.getGame(), "getSASPilotMessagesJson"):
		return result
	for message in cmd_messages({"player": player.getID()}):
		szText = message["text"]
		if szText.find("your ") >= 0 and (szText.find(" was destroyed") >= 0 or szText.find(" was captured") >= 0 or szText.find("has been captured") >= 0):
			result.append({"text": "turn %d: %s" % (message["turn"], szText)})
	return result


def _openScreens():
	# <!-- custom: Screens left open in the window: the user saw the Foreign Advisor that a 'control control=42' test had opened (42 is CONTROL_FOREIGN_SCREEN), with nothing in the replies saying so (2026-11-14). An open screen covers the map for a person watching and can keep the diplomacy screen from opening, as a tech splash did at turn 97 of the fog-on playthrough.
	# Each Python screen object in CvScreensInterface with a getScreen method is asked whether its screen is up; the main interface is always up, so it is left out. Only the screens' state, which the window shows anyone. (Claude code Opus 5.5) -->
	import CvScreensInterface
	result = []
	for szName in dir(CvScreensInterface):
		if szName == "mainInterface":
			continue
		screenObject = getattr(CvScreensInterface, szName, None)
		getScreen = getattr(screenObject, "getScreen", None)
		if not callable(getScreen):
			continue
		try:
			if getScreen().isActive():
				result.append(szName)
		except Exception:
			continue
	# <!-- custom: The Greatest Civilizations screen (CvTopCivs) has no getScreen method, so the loop above missed it: at turn 82 of the islands replay (2026-11-15) the user saw it up while 'todo' reported nothing.
	# Its screen object exists once shown. (Claude code Opus 5.5) -->
	# <!-- custom: Asked of the screen by its ID: CvEventManager shows it through its own throwaway instance, so CvScreensInterface.topCivs never had it up, and 'todo' missed the screen again at turn 82 of the 2026-11-19 validation run. (Claude code Opus 5.5) -->
	import CvScreenEnums
	if CyGInterfaceScreen("CvTopCivs", CvScreenEnums.TOP_CIVS).isActive():
		result.append("topCivs")
	if CyInterface().isCityScreenUp():
		result.append("cityScreen")
	return result


_HELP["topcivs"] = "Every Greatest Civilizations screen this player's team saw (it comes now and then, while the player has met half the teams or fewer), from the replay rows the save keeps, as the Timeline lists them: history, each with its turn, title row (category and historian) and one row per rank, met players by leader, civilization, player and team, the others unknown; latest, the newest of them; ourRank in it; and screenUp. The values behind the ranks are not shown, as on screen. args: player."


def cmd_topcivs(args):
	# <!-- custom: The user saw this screen at turn 82 of the islands replay (2026-11-15) and asked that SASPilot map it: a ranking of the most powerful civilizations, public in that a player reads it, all eight unknown to us then.
	# CvEventManager showed it through a throwaway CvTopCivs instance, so its ranking could not be read; since the 2026-11-19 validation run (turn 82, us 2nd in culture, unseen by SASPilot) CvTopCivs records each screen as replay rows, read here. (Claude code Opus 5.5) -->
	player = _player(args)
	# <!-- custom: Read through CyReplayInfo.createInfo, as the Timeline does, so each row's stored audience (KI#337) decides what this player sees; the first version checked the writer's current team, which a later team change would get wrong.
	# A CvTopCivs.g_lastShown global went too, as it outlived loading an earlier save and a hot-seat change (Codex's review, 2026-11-19).
	# Title rows are matched in the current language, so rows saved in another language are missed, as on the Timeline; a known limit kept for simplicity. (Claude code Opus 5.5) -->
	replay = CyReplayInfo()
	replay.createInfo(player.getID())
	szTitle = CyTranslator().getText("TXT_KEY_TOPCIVS_TITLE", ())
	# <!-- custom: CvTopCivs writes the rank rows from the last to the first, then the title, so the Timeline (newest first) reads them in order; a title row collects the rank rows just before it from the same turn and player, back in rank order. (Claude code Opus 5.5) -->
	history = []
	for i in range(replay.getNumReplayMessages()):
		if not replay.getReplayMessageText(i).startswith(szTitle):
			continue
		iTurn = replay.getReplayMessageTurn(i)
		iWho = replay.getReplayMessagePlayer(i)
		ranks = []
		j = i - 1
		while j >= 0 and replay.getReplayMessageTurn(j) == iTurn and replay.getReplayMessagePlayer(j) == iWho and re.match(r"^\d+\) ", replay.getReplayMessageText(j)):
			ranks.append(replay.getReplayMessageText(j))
			j -= 1
		history.append({"turn": iTurn, "title": replay.getReplayMessageText(i), "ranks": ranks})
	if not history:
		raise ValueError("no Greatest Civilizations screen has been shown to this player's team yet")
	# <!-- custom: Our rank from the latest screen's rows, whose met ranks end "player <ID>, team <ID>" (TXT_KEY_SAS_TOPCIVS_TIMELINE_RANK, English only like all SAS text). (Claude code Opus 5.5) -->
	iOurRank = None
	for szRank in history[-1]["ranks"]:
		match = re.match(r"^(\d+)\) .*, player (\d+), team \d+$", szRank)
		if match and int(match.group(2)) == player.getID():
			iOurRank = int(match.group(1))
	# <!-- custom: Whether the screen is up, asked of the screen itself: CvScreensInterface.topCivs is another instance than the one shown, and read false while the screen was up. (Claude code Opus 5.5) -->
	import CvScreenEnums
	bUp = bool(CyGInterfaceScreen("CvTopCivs", CvScreenEnums.TOP_CIVS).isActive())
	return {"latest": history[-1], "ourRank": iOurRank, "screenUp": bUp, "history": history}


_HELP["closescreens"] = "Close the screens left open in the window, as Esc or their Exit button does: every advisor or other Python screen 'todo' lists in openScreens, and the city screen; or only one with name (as openScreens names it, or cityScreen). Returns what was closed. args: name."


def cmd_closescreens(args):
	# <!-- custom: SASPilot could open an advisor ('control', 'screen') but not close it: the Foreign Advisor from a test (2026-11-14) took an Esc sent to the window.
	# hideScreen is what an advisor's Exit button calls; the city screen closes by clearing the selected cities, as noted in 'todo'. (Claude code Opus 5.5) -->
	import CvScreensInterface
	szOnly = args.get("name")
	closed = []
	for szName in _openScreens():
		if szOnly is not None and szName != szOnly:
			continue
		if szName == "cityScreen":
			CyInterface().clearSelectedCities()
		# <!-- custom: The Greatest Civilizations screen has no getScreen; its screen object is closed directly, as its Exit button does (islands replay, 2026-11-15). (Claude code Opus 5.5) -->
		elif szName == "topCivs":
			# <!-- custom: CvScreenEnums for the screen's ID, TOP_CIVS: closed by its ID, as CvEventManager shows it through its own instance that CvScreensInterface.topCivs is not (2026-11-19 validation run). (Claude code Opus 5.5) -->
			import CvScreenEnums
			CyGInterfaceScreen("CvTopCivs", CvScreenEnums.TOP_CIVS).hideScreen()
		else:
			getattr(CvScreensInterface, szName).getScreen().hideScreen()
		closed.append(szName)
	if szOnly is not None and not closed:
		raise ValueError("no open screen named %s; 'todo' lists the open ones" % szOnly)
	return {"closed": closed}


def _remindScreens(player, args):
	result = []
	for szName in _openScreens():
		result.append({"text": "the %s screen is open in the window; 'closescreens' closes it" % szName, "screen": szName})
	# <!-- custom: Popups on display in the window, as against those SASPilot holds, which 'todo' lists.
	# Read through the DLL, so only with one that has it. (Claude code Opus 5.5) -->
	if not hasattr(gc.getGame(), "getSASPilotPathJson"):
		return result
	for popup in _popups():
		if popup["state"] == "DISPLAYED":
			result.append({"text": "a %s popup is on display in the window ('popups' lists it)" % popup["type"], "popup": popup["type"]})
	return result


def _remindGold(player, args):
	iRate = player.calculateGoldRate()
	if iRate < 0 and player.getGold() + 10 * iRate < 0:
		return [{"text": "gold runs out in about %d turns (%d, %d a turn)" % (player.getGold() / -iRate, player.getGold(), iRate)}]
	return []


def _remindTrades(player, args):
	# <!-- custom: Seafaring, 2 turns of research that no neighbour had, bought Construction and Metal Casting at turn 59 of the turn-0 game (2026-11-14); a tech we could give is worth a look each turn.
	# Taken from 'techs', which applies the fog rules. (Claude code Opus 5.5) -->
	result = []
	market = _command("techs")({"player": player.getID(), "fog": args.get("fog")})
	# <!-- custom: Which of those another met civ also knows, the user's point at turn 41 of the 2026-11-19 validation run: that civ can sell it to the buyer first, so holding it gains nothing and a sale now is the chance; a unique one keeps its value. (Claude code Opus 5.5) -->
	team = gc.getTeam(player.getTeam())
	for entry in market["weCouldGive"]:
		if entry["techs"]:
			buyer = gc.getPlayer(entry["player"]).getTeam()
			contested = []
			for szTech in entry["techs"]:
				iTech = getInfoTypeOrFail(szTech)
				# <!-- custom: The holder must be able to trade techs with the buyer, which needs the tech-trading tech on either side (CvPlayer::canTradeItem): at turn 57 of the 2026-11-19 validation run Sitting Bull knew Calendar, but neither he nor Cyrus had Writing, so he could not sell it to Cyrus, while the reminder said he could and suggested giving our one trade good away. (Claude code Opus 5.5) -->
				for iTeam in range(gc.getMAX_CIV_TEAMS()):
					if iTeam not in (player.getTeam(), buyer) and gc.getTeam(iTeam).isAlive() and team.isHasMet(iTeam) and gc.getTeam(iTeam).isHasTech(iTech) and (gc.getTeam(iTeam).isTechTrading() or gc.getTeam(buyer).isTechTrading()) and gc.getTechInfo(iTech).isTrade():
						contested.append(szTech)
						break
			szText = "%s could be offered %s" % (entry["name"], ", ".join(entry["techs"]))
			# <!-- custom: "Sell it now" misled at turn 44 of the same run: Cyrus had no tech we lacked and gold trading needs Currency, so he could pay nothing; then a gift only buys goodwill, which costs nothing when another civ would hand it over anyway. (Claude code Opus 5.5) -->
			bCanPay = len([1 for wanted in market["wanted"] for holder in wanted["holders"] if holder["player"] == entry["player"] and holder["canTrade"] and holder["denial"] is None]) > 0
			if contested and bCanPay:
				szText += "; another met civ also knows %s and can sell it to them first: sell it now" % ", ".join(contested)
			elif contested:
				szText += "; they have nothing we lack to pay with now, and another met civ also knows %s: a gift costs nothing and earns goodwill, unless helping them hurts us" % ", ".join(contested)
			result.append({"text": szText, "player": entry["player"], "othersCanSell": contested})
	# <!-- custom: Resource trades decide more than open borders, the user's point at turn 51 of the 2026-11-19 validation run: sell spare copies for gold per turn, buy rarely (when short of a key one such as Iron).
	# Gold in deals needs a tech in SAS, so name it while it is missing. (Claude code Opus 5.5) -->
	spares = [gc.getBonusInfo(i).getType() for i in range(gc.getNumBonusInfos()) if player.getNumAvailableBonuses(i) >= 2]
	if spares:
		# <!-- custom: Either side's tech allows gold in a deal, as CvPlayer::canTradeItem checks isGoldTrading on either team; the user's question. (Claude code Opus 5.5) -->
		payers = [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() != player.getTeam() and team.isHasMet(gc.getPlayer(i).getTeam()) and (team.isGoldTrading() or gc.getTeam(gc.getPlayer(i).getTeam()).isGoldTrading())]
		szText = "spare resource copies to sell for gold per turn: %s" % ", ".join(spares)
		if payers:
			szText += "; gold deals possible with %s" % ", ".join(payers)
		else:
			szText += "; no met civ can put gold in a deal yet: either side needs %s" % " or ".join([gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if gc.getTechInfo(i).isGoldTrading()])
		result.append({"text": szText, "spares": spares, "goldDealsWith": payers})
	return result


def _remindRivalMoods(player, args):
	# <!-- custom: The user's point at turn 71 of the islands replay (2026-11-15): check Pericles every turn, as a Cautious leader who refused a tech may warm up, and offers come and go as a human checking the trade screen each turn sees.
	# Each met rival's attitude (and its Glance-tab value), the techs and resources it would trade us, and the resources we could offer it are kept in the session and compared with the previous call; a change comes back as a reminder, and the first call states each one.
	# Our offers include last copies, marked lastCopy with what they give: the user's point that a last spare copy is worth selling for gold or a tech when no city would drop below its limit.
	# Kept with string keys and lists, as the session state goes through JSON: the first version keyed by the player number and stored tuples, which came back as "8" and lists, so a change at turn 74 (Pericles now trading Polytheism) was never seen. (Claude code Opus 5.5) -->
	seen = _state.setdefault("rivalMoods", {})
	market = _command("techs")({"player": player.getID(), "fog": args.get("fog")})
	gives = {}
	# <!-- custom: How many met civs know each tech we lack, the user's point at turn 39 of the 2026-11-19 validation run: a tech everyone knows is cheap and soon offered by all, so paying a unique tech or gold for it is bad, while the one who has met the most civs can broker unique techs between them. (Claude code Opus 5.5) -->
	spread = {}
	for entry in market["wanted"]:
		spread[entry["tech"]] = len(entry["holders"])
		for holder in entry["holders"]:
			if holder["canTrade"] and holder["denial"] is None:
				gives.setdefault(holder["player"], []).append(entry["tech"])
	team = gc.getTeam(player.getTeam())
	result = []
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.getTeam() == player.getTeam() or not team.isHasMet(other.getTeam()) or other.isHuman():
			continue
		szAttitude = _enumName(AttitudeTypes, other.AI_getAttitude(player.getID()))
		iValue = _attitudeCount(iOther, player.getID())
		techs = gives.get(iOther, [])
		techs.sort()
		theirItems = fromJson(_tradeItemsJson(other, player.getID()))
		theirs = [item["what"] for item in theirItems if item["item"] == "TRADE_RESOURCES" and item.get("denial") is None]
		# <!-- custom: Open borders too, the user's point at the second contact (Pacal, turn 68 of the islands replay, 2026-11-15): check right away whether a newly met rival would sign, as it was the first thing traded with Pericles.
		# "signed", null when he would sign, or his DENIAL_ reason. (Claude code Opus 5.5) -->
		szBorders = "signed"
		if not team.isOpenBorders(other.getTeam()):
			szBorders = "not on the table"
			for item in theirItems:
				if item["item"] == "TRADE_OPEN_BORDERS":
					szBorders = item.get("denial") or "would sign"
		theirs.sort()
		ours = []
		for item in fromJson(_tradeItemsJson(player, iOther)):
			if item["item"] != "TRADE_RESOURCES":
				continue
			ours.append(item["what"])
		ours.sort()
		now = [szAttitude, iValue, techs, theirs, ours, szBorders]
		szKey = str(iOther)
		before = seen.get(szKey)
		seen[szKey] = now
		if before == now:
			continue
		offers = []
		for szBonus in ours:
			iBonus = getInfoTypeOrFail(szBonus)
			info = gc.getBonusInfo(iBonus)
			offers.append({"bonus": szBonus, "lastCopy": player.getNumAvailableBonuses(iBonus) <= 1, "happiness": info.getHappiness(), "health": info.getHealth()})
		if before is None:
			szText = "%s is %s (%+d); open borders: %s; would trade techs %s and resources %s; we could offer %s" % (other.getName(), szAttitude[9:].lower(), iValue, szBorders, ", ".join(techs) or "none", ", ".join(theirs) or "none", ", ".join(ours) or "nothing")
		else:
			parts = []
			if before[0] != szAttitude or before[1] != iValue:
				parts.append("%s %+d is now %s %+d" % (before[0][9:].lower(), before[1], szAttitude[9:].lower(), iValue))
			for (szWhat, oldList, newList) in (("techs", before[2], techs), ("resources", before[3], theirs), ("our offers", before[4], ours)):
				added = [x for x in newList if x not in oldList]
				gone = [x for x in oldList if x not in newList]
				if added:
					parts.append("%s now: %s" % (szWhat, ", ".join(added)))
				if gone:
					parts.append("%s gone: %s" % (szWhat, ", ".join(gone)))
			if len(before) < 6 or before[5] != szBorders:
				parts.append("open borders: %s" % szBorders)
			szText = "%s: %s" % (other.getName(), "; ".join(parts))
		if techs:
			szText += " (met civs knowing each: %s; a widely known tech is cheap, so pay little for it; a tech we give stays ours and can be traded again to each civ, while gold and resources are spent once)" % ", ".join(["%s %d" % (t, spread.get(t, 0)) for t in techs])
		result.append({"text": szText, "player": iOther, "attitude": szAttitude, "attitudeValue": iValue, "openBorders": szBorders, "wouldTradeTechs": techs, "techKnownByMetCivs": dict([(t, spread.get(t, 0)) for t in techs]), "wouldTradeResources": theirs, "weCouldOffer": offers})
	return result


def _remindSleepingWorkers(player, args):
	# <!-- custom: The activity is the group's (CySelectionGroup.getActivityType), as CyUnit has no getter for it.
	# A sleeping unit is not idle, so 'todo' and the turn's waits never list it: three Workers the agent had put to sleep near York at turns 155 to 157 of the turn-0 game (2026-11-14) slept unnoticed while York kept a bare grass hill, a marsh and two forests, until the user pointed out that York was under-improved. (Claude code Opus 5.5) -->
	result = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.workRate(True) > 0 and unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP:
			result.append({"text": "%s %d sleeps at %d,%d; 'workers' lists what its cities still need" % (unit.getUnitType() >= 0 and gc.getUnitInfo(unit.getUnitType()).getType() or "unit", unit.getID(), unit.getX(), unit.getY()), "unit": unit.getID()})
		(unit, it) = player.nextUnit(it, False)
	return result


# <!-- custom: Faces of happiness or health to spare at or under which a city counts as needing more of it. (Claude code Opus 5.5) -->
ROAD_NEED_MARGIN = 1


def _bonusNeed(player, iBonus):
	# <!-- custom: What connecting this bonus would answer now, or None: its happiness or health where a city is within ROAD_NEED_MARGIN of the cap, or a unit or building that requires it (as AND or OR prerequisite) and we lack it. (Claude code Opus 5.5) -->
	if iBonus < 0 or player.getNumAvailableBonuses(iBonus) > 0:
		return None
	info = gc.getBonusInfo(iBonus)
	cities = _cities(player)
	needs = []
	if info.getHappiness() > 0 and [1 for city in cities if city.happyLevel() - city.unhappyLevel(0) <= ROAD_NEED_MARGIN]:
		needs.append("+%d happiness" % info.getHappiness())
	if info.getHealth() > 0 and [1 for city in cities if city.goodHealth() - city.badHealth(False) <= ROAD_NEED_MARGIN]:
		needs.append("+%d health" % info.getHealth())
	for i in range(gc.getNumUnitInfos()):
		unitInfo = gc.getUnitInfo(i)
		if unitInfo.getPrereqAndBonus() == iBonus or iBonus in [unitInfo.getPrereqOrBonuses(k) for k in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES())]:
			if player.canResearch(unitInfo.getPrereqAndTech(), False) or gc.getTeam(player.getTeam()).isHasTech(unitInfo.getPrereqAndTech()):
				needs.append("%s needs it" % unitInfo.getType())
				break
	for i in range(gc.getNumBuildingInfos()):
		buildingInfo = gc.getBuildingInfo(i)
		if buildingInfo.getPrereqAndBonus() == iBonus and gc.getTeam(player.getTeam()).isHasTech(buildingInfo.getPrereqAndTech()):
			needs.append("%s needs it" % buildingInfo.getType())
			break
	return ", ".join(needs) or None


def _remindUnimproved(player, args):
	# <!-- custom: Resources inside our borders that supply nothing yet though we have the tech for a build that would connect them: at turn 156 of the turn-0 game (2026-11-14) the Clam at 22,31 sat in Coventry's borders, outside every city's radius, until the user pointed out that a Work Boat connects it for health all the same.
	# The same check catches an improvement pillaged by barbarians or rivals, as the plot then reads unconnected.
	# Taken from 'resources', which applies the fog rules. (Claude code Opus 5.5) -->
	# <!-- custom: Which of our workers already head for each plot (where its group's mission queue ends, lastMissionPlot): at turn 160 of the turn-0 game the agent queued a second Work Boat in Hastings for the Clam while the first was one plot away with that very order, and the user asked where the boat had come from. (Claude code Opus 5.5) -->
	onTheWay = {}
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.workRate(True) > 0 and unit.getGroup().getLengthMissionQueue() > 0:
			target = unit.getGroup().lastMissionPlot()
			if target and not target.isNone():
				onTheWay[(target.getX(), target.getY())] = unit.getID()
		(unit, it) = player.nextUnit(it, False)
	# <!-- custom: Units that can make each build and stand in a city's queue: in the scouting trial (2026-11-14) the Clam reminder came every turn from turn 4 while Constantinople's first build was the Work Boat for it, so an agent stopping on reminders stopped each turn for nothing it could act on. (Claude code Opus 5.5) -->
	queued = {}
	(city, it) = player.firstCity(False)
	while city:
		for i in range(city.getOrderQueueLength()):
			order = city.getOrderFromQueue(i)
			if order.eOrderType == OrderTypes.ORDER_TRAIN:
				queued.setdefault(order.iData1, city.getName())
		(city, it) = player.nextCity(it, False)
	result = []
	for entry in _command("resources")({"player": player.getID(), "fog": args.get("fog")})["resources"]:
		if entry["owner"] != player.getID() or entry.get("connected"):
			continue
		builds = [build["build"] for build in entry["builds"] if build["haveTech"]]
		# <!-- custom: At turn 66 of the 2026-11-19 validation run Dublin's Stone already had its quarry and the Pig its pasture, yet both read "BUILD_QUARRY would connect it": an improved resource still supplies nothing until a route links it to a city's trade network, and with no roads (The Wheel had just arrived) none was linked.
		# So an improved plot that is not connected now names the route instead, from the route builds the team can make. (Claude code Opus 5.5) -->
		plot = gc.getMap().plot(entry["x"], entry["y"])
		if plot.getImprovementType() >= 0:
			routes = [gc.getBuildInfo(i).getType() for i in range(gc.getNumBuildInfos()) if gc.getBuildInfo(i).getRoute() >= 0 and plot.canBuild(i, player.getID(), False)]
			builds = []
			# <!-- custom: The user, next turn: roading every resource is very inefficient; a worked tile gives its yields without a road, which adds only the resource's own effect, and our health had room to spare.
			# So the road is named only when that effect answers a need: happiness or health within ROAD_NEED_MARGIN of a city's cap, or a unit or building that requires the resource (read from the XML). (Claude code Opus 5.5) -->
			szNeed = _bonusNeed(player, plot.getBonusType(player.getTeam()))
			if routes and szNeed:
				szText = "%s at %d,%d has its %s but is not on a city's trade network, so its %s does not count: %s linking it to a city (or a river or coast the city shares) connects it" % (entry["bonus"], entry["x"], entry["y"], gc.getImprovementInfo(plot.getImprovementType()).getType(), szNeed, " or ".join(routes))
				result.append({"bonus": entry["bonus"], "x": entry["x"], "y": entry["y"], "improvement": gc.getImprovementInfo(plot.getImprovementType()).getType(), "needsRoute": routes, "text": szText})
		if builds:
			szText = "%s at %d,%d is in our borders but supplies nothing; %s would connect it" % (entry["bonus"], entry["x"], entry["y"], " or ".join(builds))
			row = {"bonus": entry["bonus"], "x": entry["x"], "y": entry["y"]}
			if onTheWay.has_key((entry["x"], entry["y"])):
				row["unitOnTheWay"] = onTheWay[(entry["x"], entry["y"])]
				szText = szText + " (unit %d is on its way)" % row["unitOnTheWay"]
			for iUnit, szCity in queued.items():
				for szBuild in builds:
					if gc.getUnitInfo(iUnit).getBuilds(getInfoTypeOrFail(szBuild)):
						row["inProduction"] = {"unit": gc.getUnitInfo(iUnit).getType(), "city": szCity}
				if row.has_key("inProduction"):
					szText = szText + " (%s is in %s's queue)" % (row["inProduction"]["unit"], row["inProduction"]["city"])
					break
			row["text"] = szText
			result.append(row)
	return result


def _remindExports(player, args):
	# <!-- custom: At turn 118 of the turn-0 game (2026-11-14) a Pig sale to Gilgamesh was signed with our only Iron in it too, and nothing said so: the Iron read unconnected for seven turns and no city could train a Swordsman.
	# Each resource we give away while none is left for us. (Claude code Opus 5.5) -->
	result = []
	for deal in _command("deals")({"player": player.getID()})["deals"]:
		for item in deal["weGive"]:
			if item["item"] == "TRADE_RESOURCES" and player.getNumAvailableBonuses(item["data"]) == 0:
				result.append({"text": "we export our only %s to %s (since turn %d, deal %d); it can be cancelled from 'deals' once the game allows" % (item.get("what"), deal["name"], deal["sinceTurn"], deal["id"]), "bonus": item.get("what"), "player": deal["with"]})
	return result


# <!-- custom: The user asked for reminders the game does not give, so no turn is lost to an unnoticed gap (2026-11-14), made of small checks so each new reminder is one function in this list.
# Each sees only what the player's own screens show. (Claude code Opus 5.5) -->
IDLE_GARRISON_THREAT_PLOTS = 4


# <!-- custom: Plots within which a seen rival city makes a city's only defender stay home. (Claude code Opus 5.5) -->
GARRISON_RIVAL_RANGE = 8


def _soleDefenderNearRival(player, unit):
	# <!-- custom: At turn 59 of the 2026-11-19 validation run the reminder told Cork's only Archer to go exploring, while Pasargadae, Cyrus's city at 3 times our power with aggressive AI on, was 7 plots away and the user had just called us militarily very weak.
	# The rule to explore stays for a city with other defenders or no rival city near, as in the 2026-11-14 game where nothing threatened. (Claude code Opus 5.5) -->
	plot = unit.plot()
	iDefenders = len([1 for k in range(plot.getNumUnits()) if plot.getUnit(k).getOwner() == player.getID() and plot.getUnit(k).canDefend(plot) and plot.getUnit(k).canFight()])
	if iDefenders > 1:
		return False
	iTeam = player.getTeam()
	for i in range(gc.getMAX_CIV_PLAYERS()):
		rival = gc.getPlayer(i)
		if not rival.isAlive() or rival.getTeam() == iTeam:
			continue
		for city in _cities(rival):
			if city.plot().isRevealed(iTeam, False) and plotDistance(plot.getX(), plot.getY(), city.getX(), city.getY()) <= GARRISON_RIVAL_RANGE:
				return True
	return False


def _remindIdleGarrison(player, args):
	# <!-- custom: Fortified is read as getFortifyTurns() > 0: ActivityTypes has no ACTIVITY_FORTIFY in Python, and the first version broke every 'endturn' with an AttributeError. (Claude code Opus 5.5) -->
	# <!-- custom: Military units fortified or asleep in a city, with the nearest foreign unit the team sees and how much of the map it has revealed, so an agent can weigh sending one out: early in the Continents game of 2026-11-14 the Archer was sent home to garrison while nothing threatened and the map was mostly unknown, and the user pointed out that it should explore.
	# Usually, not always (the user), so the reminder states the facts and leaves the call. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	kMap = gc.getMap()
	idle = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and unit.canAttack() and unit.plot().isCity() and (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP or unit.getFortifyTurns() > 0) and not _soleDefenderNearRival(player, unit):
			idle.append(unit)
		(unit, it) = player.nextUnit(it, False)
	if not idle:
		return []
	iRevealed = 0
	foreign = []
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if plot.isRevealed(iTeam, False):
			iRevealed += 1
		if plot.isVisible(iTeam, False):
			for j in range(plot.getNumUnits()):
				other = plot.getUnit(j)
				if other.getTeam() != iTeam and not other.isInvisible(iTeam, False) and other.canAttack():
					foreign.append((plot.getX(), plot.getY()))
	iPerMille = 1000 * iRevealed / max(1, kMap.numPlots())
	# <!-- custom: One entry per city, not per unit: at turn 302 of the ASOKA Huge save (2026-11-22) the check gave 71 of 132 reminders, one per fortified unit in 17 cities, and drowned the rest of the digest.
	# Each entry keeps the unit IDs, types and the nearest foreign unit (the same for every unit on the plot), so the call stays the agent's as before, and the city's plot, so mute=idleGarrison@x,y silences one city. (Claude code Opus 5.5) -->
	byCity = {}
	order = []
	for unit in idle:
		key = (unit.getX(), unit.getY())
		if not byCity.has_key(key):
			byCity[key] = []
			order.append(key)
		byCity[key].append(unit)
	result = []
	for key in order:
		units = byCity[key]
		near = None
		for (x, y) in foreign:
			iDist = max(abs(key[0] - x), abs(key[1] - y))
			if near is None or iDist < near:
				near = iDist
		szNear = near is None and "no foreign military unit in sight" or "nearest foreign military unit %d plots away" % near
		# <!-- custom: Says what to do instead: at turn 32 of the 2026-11-19 validation run the Warrior slept in Dublin with nothing in sight, and the user called it wasteful next to exploring. (Claude code Opus 5.5) -->
		if near is None or near > IDLE_GARRISON_THREAT_PLOTS:
			szNear += "; with no threat in reach it pays more exploring, fog-busting (the fogBusting posts) or escorting a Settler, and can come back when a threat shows"
		counts = {}
		for unit in units:
			szType = gc.getUnitInfo(unit.getUnitType()).getType()
			counts[szType] = counts.get(szType, 0) + 1
		szTypes = ", ".join(["%s x%d" % (szType, counts[szType]) for szType in sorted(counts.keys())])
		szCity = units[0].plot().getPlotCity().getName()
		result.append({"text": "%s holds %d fortified or sleeping military unit(s): %s (%s; %d per mille of the map revealed)" % (szCity, len(units), szTypes, szNear, iPerMille), "city": units[0].plot().getPlotCity().getID(), "x": key[0], "y": key[1], "units": [unit.getID() for unit in units], "nearestForeign": near, "revealedPerMille": iPerMille})
	return result


def _remindHuts(player, args):
	# <!-- custom: Goody huts the team has seen, with the nearest of our land units and its distance in plots: huts give techs, maps and gold early, and rivals' scouts take them too, so an agent scouting should see them all at once (the user, Continents game of 2026-11-14, after three huts in the first runs gave Mining, a map and research).
	# Only huts as the team last saw them. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	iHut = _findOptionalInfoType("IMPROVEMENT_GOODY_HUT")
	if iHut < 0:
		return []
	units = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and unit.canMove():
			units.append(unit)
		(unit, it) = player.nextUnit(it, False)
	result = []
	szRisk = _hutBarbarianRisk(player)
	kMap = gc.getMap()
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if plot.isRevealed(iTeam, False) and plot.getRevealedImprovementType(iTeam, False) == iHut:
			nearest = None
			for unit in units:
				iDist = max(abs(unit.getX() - plot.getX()), abs(unit.getY() - plot.getY()))
				if nearest is None or iDist < nearest[1]:
					nearest = (unit, iDist)
			row = {"x": plot.getX(), "y": plot.getY()}
			szNear = "no unit of ours can move"
			if nearest:
				row["nearestUnit"] = nearest[0].getID()
				row["distance"] = nearest[1]
				szNear = "nearest %s %d, %d plots" % (gc.getUnitInfo(nearest[0].getUnitType()).getType(), nearest[0].getID(), nearest[1])
			row["text"] = "goody hut at %d,%d (%s)%s" % (plot.getX(), plot.getY(), szNear, szRisk)
			result.append(row)
	return result


def _hutBarbarianRisk(player):
	# <!-- custom: Whether a hut can release Barbarians now, from the handicap's own goody list and AdvCiv's early rule (advc.314 in CvPlayer::canReceiveGoody: no result of more than one Barbarian before turn 16 at Normal speed, scaled by game speed).
	# The user asked at turn 20 of the Continents replay (2026-11-19) whether huts were safe so early; on Noble one Barbarian can come from turn 0, which the user had guessed could not happen. (Claude code Opus 5.5) -->
	handicap = gc.getHandicapInfo(player.getHandicapType())
	iMaxBarbarians = 0
	for i in range(handicap.getNumGoodies()):
		goody = gc.getGoodyInfo(handicap.getGoodies(i))
		if goody.isBad():
			iMaxBarbarians = max(iMaxBarbarians, goody.getMinBarbarians())
	if iMaxBarbarians <= 0:
		return ""
	iTrainHalved = (gc.getGameSpeedInfo(CyGame().getGameSpeedType()).getTrainPercent() + 100) / 2
	iStrongTurn = (iTrainHalved * 16 + 99) / 100
	if CyGame().getGameTurn() < iStrongTurn:
		szRisk = "; it can release 1 Barbarian now, more from turn %d: enter with a healthy unit that can defend" % iStrongTurn
	else:
		szRisk = "; it can release %d Barbarians or more: enter with a healthy unit that can defend" % iMaxBarbarians
	return szRisk + _hutSafeUnit(player)


def _hutSafeUnit(player):
	# <!-- custom: A unit safe at huts, as the player knows the Scout to be: ours if we have one, else the cheapest one a city of ours can train.
	# The user's point in the Continents replay (2026-11-19): a Scout, not an Archer, as the opening's filler while the capital grows. (Claude code Opus 5.5) -->
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.isNoBadGoodies():
			return ", or %s %d, which huts give no bad result" % (gc.getUnitInfo(unit.getUnitType()).getType(), unit.getID())
		(unit, it) = player.nextUnit(it, False)
	best = None
	(city, it) = player.firstCity(False)
	while city:
		for i in range(gc.getNumUnitInfos()):
			info = gc.getUnitInfo(i)
			if info.isNoBadGoodies() and city.canTrain(i, False, False):
				iCost = player.getUnitProductionNeeded(i)
				if best is None or iCost < best[0]:
					best = (iCost, info, city)
		(city, it) = player.nextCity(it, False)
	if best is None:
		return ""
	return "; huts give no bad result to %s (%d hammers, %d moves), which %s can train" % (best[1].getType(), best[0], best[1].getMoves(), best[2].getName())


def _remindExposed(player, args):
	# <!-- custom: Our units outside cities within two plots of a barbarian or animal unit the team sees, with their moves left: in the scouting trial (run 3, turn 33) the Scout ended its turn beside a visible Bear and was killed, and nothing pointed at it (the user caught it).
	# Animals mostly move one plot, so two keeps a turn's margin. (Claude code Opus 5.5) -->
	result = []
	iTeam = player.getTeam()
	kMap = gc.getMap()
	(unit, it) = player.firstUnit(False)
	while unit:
		plot = unit.plot()
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and not plot.isCity():
			near = []
			for dx in range(-2, 3):
				for dy in range(-2, 3):
					other = kMap.plot(unit.getX() + dx, unit.getY() + dy)
					if other is None or other.isNone() or not other.isVisible(iTeam, False):
						continue
					for j in range(other.getNumUnits()):
						foe = other.getUnit(j)
						if foe.isBarbarian() and not foe.isInvisible(iTeam, False):
							near.append("%s at %d,%d" % (gc.getUnitInfo(foe.getUnitType()).getType(), other.getX(), other.getY()))
			if near:
				result.append({"text": "%s %d at %d,%d (%d%% health, %d moves left) is within two plots of %s" % (gc.getUnitInfo(unit.getUnitType()).getType(), unit.getID(), unit.getX(), unit.getY(), 100 - unit.getDamage(), unit.movesLeft() / gc.getMOVE_DENOMINATOR(), ", ".join(near)), "unit": unit.getID(), "x": unit.getX(), "y": unit.getY()})
		(unit, it) = player.nextUnit(it, False)
	return result


def _remindScoutBeforeFounding(player, args):
	# <!-- custom: With no city yet, a Settler waits while other units still have moves: moving them first can reveal a better site before the Settler commits.
	# The user's lesson from the scouting trial (2026-11-14): runs 1 and 2 founded on turn 0 before the Warrior moved; run 3 sent it to the 19,18 hill first, which confirmed the site. (Claude code Opus 5.5) -->
	if player.getNumCities() > 0:
		return []
	settlers, movers = [], []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.isFound():
			settlers.append(unit.getID())
		elif unit.movesLeft() > 0 and unit.getDomainType() == DomainTypes.DOMAIN_LAND:
			movers.append(unit.getID())
		(unit, it) = player.nextUnit(it, False)
	if settlers and movers:
		return [{"text": "no city yet: units %s still have moves; moving them first may show a better site before Settler %s founds" % (", ".join([str(i) for i in movers]), settlers[0]), "units": movers, "settler": settlers[0]}]
	return []


def _yieldText(plot):
	# <!-- custom: A plot's yields as food/hammers/commerce, as the city screen shows them. (Claude code Opus 5.5) -->
	return "/".join([str(plot.getYield(YieldTypes(k))) for k in range(YieldTypes.NUM_YIELD_TYPES)])


def _remindIdleImprovements(player, args):
	# <!-- custom: An improved plot of a city's that no city works while that city works a plot with no improvement, as its city screen shows.
	# With the governor off, nothing moves a citizen onto a new improvement: in the scouting trial (2026-11-14) the Clam's fishing boats sat unworked for six turns, then the new Banana plantation for two, until the user or the agent noticed.
	# A plain fact; which plot is better stays the agent's call. (Claude code Opus 5.5) -->
	result = []
	(city, it) = player.firstCity(False)
	while city:
		idle, bare = [], []
		for i in range(1, gc.getNUM_CITY_PLOTS()):
			plot = city.getCityIndexPlot(i)
			if plot is None or plot.isNone() or plot.getOwner() != player.getID():
				continue
			if plot.getImprovementType() >= 0 and not plot.isBeingWorked() and city.canWork(plot):
				idle.append((plot.getX(), plot.getY(), gc.getImprovementInfo(plot.getImprovementType()).getType()))
			elif plot.getImprovementType() < 0 and city.isWorkingPlot(plot):
				bare.append((plot.getX(), plot.getY()))
		# <!-- custom: At turn 61 of the 2026-11-19 validation run this flagged Dublin working a 3-hammer hill forest instead of its Crab and Deer camp, a deliberate swap of food Dublin could not use (one citizen from its happy cap) for hammers it lacked, as the user had asked.
		# An unimproved plot giving more hammers than every unworked improved one is now taken as such a choice and left out; the yields are given so the rest can be judged. (Claude code Opus 5.5) -->
		if idle:
			iBestIdleHammers = max([gc.getMap().plot(x, y).getYield(YieldTypes.YIELD_PRODUCTION) for (x, y, szType) in idle])
			bare = [(x, y) for (x, y) in bare if gc.getMap().plot(x, y).getYield(YieldTypes.YIELD_PRODUCTION) <= iBestIdleHammers]
		if idle and bare:
			result.append({"text": "%s does not work %s while it works %s, which have no improvement" % (city.getName(), ", ".join(["%s at %d,%d (%s)" % (szType, x, y, _yieldText(gc.getMap().plot(x, y))) for (x, y, szType) in idle]), ", ".join(["%d,%d (%s)" % (x, y, _yieldText(gc.getMap().plot(x, y))) for (x, y) in bare])), "city": city.getID(), "idle": [[x, y] for (x, y, szType) in idle], "unimprovedWorked": [[x, y] for (x, y) in bare]})
		(city, it) = player.nextCity(it, False)
	return result


def _coastLaneRows(player):
	# <!-- custom: The rows of the coast lanes to the east and west neighbours on SAS_Large_Facing_Islands with "E-W Coast Bands": _apply_horizontal_coast_lanes lays them along each island row's centre row, plus or minus one, widest near the islands.
	# Our island's centre row is taken from the revealed land of our landmass.
	# At turn 71 of the islands replay (2026-11-15) the boats drifted north along the map's edge, where nothing lies, while the lanes to every rival of our row ran along y 24 to 26; the user pointed it out.
	# Other maps give null. (Claude code Opus 5.5) -->
	szScript = CyMap().getMapScriptName()
	if szScript != "SAS_Large_Facing_Islands":
		return None
	options = _mapOptionsAll(szScript) or []
	if not [o for o in options if o["value"].startswith("E-W Coast Bands")]:
		return None
	land = _revealedLandmass(player)
	if not land:
		return None
	ys = [y for (x, y) in land.keys()]
	iCenter = (min(ys) + max(ys)) / 2
	return [iCenter - 1, iCenter, iCenter + 1]


def _mapOptionsAll(szScript):
	# <!-- custom: Every custom option of the map script with the value this game uses, defaults included: getNonDefaultCustomMapOptionDesc, as the Settings tab, lists only changed ones, so a SAS_Large_Facing_Islands game on its recommended "E-W Coast Bands" and "N-S Ocean Bands" listed none, and the agent took the east-west coast lanes for ocean (islands replay, 2026-11-15; the user's correction).
	# Map scripts take their arguments as one list. (Claude code Opus 5.5) -->
	try:
		module = __import__(szScript)
		result = []
		for i in range(module.getNumCustomMapOptions()):
			iValue = int(CyMap().getCustomMapOption(i))
			result.append({"option": module.getCustomMapOptionName([i]), "value": module.getCustomMapOptionDescAt([i, iValue])})
		return result
	except Exception:
		return None


def _remindWaterScouting(player, args):
	# <!-- custom: The user's idea after the SAS48 islands autoplay (2026-11-15), where the AI had met 2 of 47 rivals by turn 120 though Galleys were known and its seen coast ran on into unrevealed water: contact brings trades and faster research, so point out when no ship of ours explores while rivals are unmet and seen water, coast for any ship or ocean once we have an ocean-going one, borders unrevealed plots.
	# Only what the team has seen, its own units and what its cities can build. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	iUnmet = len([1 for i in range(gc.getMAX_CIV_TEAMS()) if i != iTeam and gc.getTeam(i).isAlive() and not gc.getTeam(i).isMinorCiv() and not gc.getTeam(i).isBarbarian() and not team.isHasMet(i)])
	if iUnmet == 0:
		return []
	iOcean = getInfoTypeOrFail("TERRAIN_OCEAN")
	bOceanShip = False
	idle = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_SEA:
			if unit.getGroup().getAutomateType() == AutomateTypes.AUTOMATE_EXPLORE:
				# <!-- custom: An exploring ship inside a met rival's borders is pointed out, as at turn 75 of the islands replay both Work Boats roamed the waters of Greece, already met, while other directions stayed unknown; see 'seareach'.
				# Otherwise an explorer means nothing to remind. (Claude code Opus 5.5) -->
				iOwner = unit.plot().getRevealedOwner(iTeam, False)
				if iOwner >= 0 and gc.getPlayer(iOwner).getTeam() != iTeam:
					return [{"text": "%s %d explores inside the borders of %s, already met, where coast is partly known; if open borders end or culture takes its plot, the game moves it to the nearest plot it may enter, or deletes it when there is none (CvPlot::verifyUnitValidPlot); 'seareach unit=%d' lists the unknown coast it can reach elsewhere" % (gc.getUnitInfo(unit.getUnitType()).getType(), unit.getID(), gc.getPlayer(iOwner).getName(), unit.getID()), "unit": unit.getID(), "x": unit.getX(), "y": unit.getY()}]
				return []
			# <!-- custom: A ship sailing on orders explores too: at turn 69 of the islands replay (2026-11-15) both Work Boats were on their way to unknown coast that 'seareach' chose, yet this said no ship explored, as it counted only automated exploring. (Claude code Opus 5.5) -->
			if unit.getGroup().getLengthMissionQueue() > 0 and unit.getGroup().getMissionType(0) == MissionTypes.MISSION_MOVE_TO:
				return []
			if not gc.getUnitInfo(unit.getUnitType()).getTerrainImpassable(iOcean):
				bOceanShip = True
			if unit.canMove() and unit.getGroup().getLengthMissionQueue() == 0 and unit.getCargo() == 0:
				idle.append(unit)
		(unit, it) = player.nextUnit(it, False)
	# <!-- custom: Per city, as a ship needs a coastal city: the first version tested the player alone and told an inland capital at turn 0 of the islands replay to build a Work Boat it could not.
	# With the tech but no coastal city, it says to found one. (Claude code Opus 5.5) -->
	trainable = []
	known = []
	civ = gc.getCivilizationInfo(player.getCivilizationType())
	cities = _cities(player)
	for iClass in range(gc.getNumUnitClassInfos()):
		iUnit = civ.getCivilizationUnits(iClass)
		if iUnit == -1 or gc.getUnitInfo(iUnit).getDomainType() != DomainTypes.DOMAIN_SEA or not player.canTrain(iUnit, False, False):
			continue
		known.append(iUnit)
		for city in cities:
			# <!-- custom: Only a city on a sea, not a lake, launches explorers (the user's point): a lake city can train boats that never leave its lake. (Claude code Opus 5.5) -->
			if city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()) and city.canTrain(iUnit, False, False):
				trainable.append((iUnit, city))
				if not gc.getUnitInfo(iUnit).getTerrainImpassable(iOcean):
					bOceanShip = True
				break
	if not idle and not known:
		return []
	kMap = gc.getMap()
	iFrontier = 0
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if not plot.isWater() or not plot.isRevealed(iTeam, False) or (plot.getTerrainType() == iOcean and not bOceanShip):
			continue
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
			if adjacent is not None and not adjacent.isNone() and not adjacent.isRevealed(iTeam, False):
				iFrontier += 1
				break
	if iFrontier == 0:
		return []
	# <!-- custom: Ranked by hammers per move, the user's suggestion at turn 60 of the islands replay (2026-11-15): a Work Boat (30 hammers, 2 moves) and a Galley (45, 3) both cost 15 per move there, the boat later becoming a fishing improvement.
	# Strength is shown and breaks ties, as an explorer that is sunk scouts no more; a Work Boat has none. (Claude code Opus 5.5) -->
	ranked = []
	for (iUnit, city) in trainable:
		info = gc.getUnitInfo(iUnit)
		iCost = player.getUnitProductionNeeded(iUnit)
		ranked.append({"unit": info.getType(), "city": city.getName(), "cost": iCost, "moves": info.getMoves(), "hammersPerMove": iCost / float(max(1, info.getMoves())), "strength": info.getCombat(), "turns": city.getUnitProductionTurnsLeft(iUnit, 0)})
	ranked.sort(lambda a, b: cmp((a["hammersPerMove"], -a["strength"]), (b["hammersPerMove"], -b["strength"])))
	row = {"unmetTeams": iUnmet, "frontierWaterPlots": iFrontier, "idleShips": [u.getID() for u in idle], "trainable": ranked}
	if idle:
		szHow = "send idle %s %d exploring (command COMMAND_AUTOMATE data1=AUTOMATE_EXPLORE)" % (gc.getUnitInfo(idle[0].getUnitType()).getType(), idle[0].getID())
	elif ranked:
		best = ranked[0]
		szHow = "build %s in %s to explore (%d hammers per move, strength %d, %d turns)" % (best["unit"], best["city"], best["hammersPerMove"], best["strength"], best["turns"])
	else:
		szHow = "found a city on the sea coast (not a lake; it need not be the capital) to build %s" % gc.getUnitInfo(known[0]).getType()
	row["text"] = "no ship explores while %d teams are unmet and %d seen water plots border the unknown: %s" % (iUnmet, iFrontier, szHow)
	return [row]


def _fogPostSight(plot):
	# <!-- custom: A plain sight radius: 1, or 2 from hills or a peak, which raise a unit's see-from level; forests and hills between can still block a view, which this does not model. (Claude code Opus 5.5) -->
	if plot.isHills() or plot.isPeak():
		return 2
	return 1


def _revealedLandmass(player):
	# <!-- custom: Our landmass as the team knows it: revealed land connected to our cities (diagonals connect, as units move), or to our land units before the first city.
	# The game's area IDs come from the true map, so grouping revealed plots by them told whether two explored patches connect through fog (Codex's review, 2026-11-15). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iTeam = player.getTeam()
	starts = [(city.getX(), city.getY()) for city in _cities(player)]
	if not starts:
		starts = [(unit.getX(), unit.getY()) for unit in _units(player) if unit.getDomainType() == DomainTypes.DOMAIN_LAND and not unit.plot().isWater()]
	seen = {}
	todo = list(starts)
	for xy in starts:
		seen[xy] = True
	while todo:
		(x, y) = todo.pop()
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(x, y, DirectionTypes(iDirection))
			if adjacent is None or adjacent.isNone() or adjacent.isWater() or not adjacent.isRevealed(iTeam, False):
				continue
			xy = (adjacent.getX(), adjacent.getY())
			if not seen.has_key(xy):
				seen[xy] = True
				todo.append(xy)
	return seen


def _remindFogBusting(player, args):
	# <!-- custom: The user's point at turn 8 of the islands replay (2026-11-15), alone on our island: a good time to learn fog busting.
	# CvGame::randomBarbarianPlot spawns a Barbarian unit only on land that is unowned, passable, habitable, not visible to any civ and at least MIN_BARBARIAN_STARTING_DISTANCE from civ units, so land in our borders is safe and unowned land kept in sight is too.
	# The user then asked for the posts that watch it all most efficiently, hills seeing further: a greedy cover of all unowned land of our landmasses, as seen, picking each time the plot whose sight covers the most of what is left, hills first on a tie, so the posts do not move as units walk; posts already held by a unit of ours are marked. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	kMap = gc.getMap()
	if not _cities(player):
		return []
	ourLand = _revealedLandmass(player)
	target = {}
	iExposed = 0
	candidates = []
	for (x, y) in ourLand.keys():
		plot = kMap.plot(x, y)
		if plot.isImpassable():
			continue
		candidates.append(plot)
		if plot.getRevealedOwner(iTeam, False) == -1:
			target[(plot.getX(), plot.getY())] = True
			if not plot.isVisible(iTeam, False):
				iExposed += 1
	# <!-- custom: Posts that no longer watch anything: at turn 61 of the islands replay a Warrior still sat fortified at (96,25) after Utrecht, next to it, had taken in and lit that land; the user asked for a wake-up.
	# A fortified or sleeping land unit of ours outside a city whose sight covers no unowned land is listed as free; the activity is the group's, as CyUnit has no getActivityType (the first run failed on it), and a fortified unit shows as ACTIVITY_SLEEP, the binding having no ACTIVITY_FORTIFY. (Claude code Opus 5.5) -->
	free = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and not unit.plot().isCity() and unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP:
			plot = unit.plot()
			iRange = _fogPostSight(plot)
			# <!-- custom: Free when every unowned plot in its sight is also seen by something else (visibility count of 2 or more), not only when none is in sight: the first version kept the (96,25) Warrior, whose hill sight still touched unowned plots that Utrecht and Amsterdam saw anyway. (Claude code Opus 5.5) -->
			bNeeded = False
			for dx in range(-iRange, iRange + 1):
				for dy in range(-iRange, iRange + 1):
					xy = (plot.getX() + dx, plot.getY() + dy)
					if target.has_key(xy) and kMap.plot(xy[0], xy[1]).getVisibilityCount(iTeam) < 2:
						bNeeded = True
			if not bNeeded:
				free.append(unit)
		(unit, it) = player.nextUnit(it, False)
	result = []
	# <!-- custom: Whether Barbarian land units can spawn on our landmass at all: AdvCiv spawns them in a settled land area only while its unowned land plus half its unowned shelf (passable, habitable shallow coast next to it, not lake or ice) is at least half the handicap's iUnownedTilesPerBarbarianUnit (advc.300, CvGame::createBarbarianUnits and CvMap::computeShelves).
	# At turn 57 of the islands replay (2026-11-15) the user called the north post a mistake: on Noble (55 tiles per unit, so 27) the island had 24 unowned land plots, and scouting the rest of it came first.
	# Counted from what the team has revealed, so it is an estimate. (Claude code Opus 5.5) -->
	iCoast = getInfoTypeOrFail("TERRAIN_COAST")
	iThreshold = gc.getHandicapInfo(gc.getGame().getHandicapType()).getUnownedTilesPerBarbarianUnit() / 2
	# <!-- custom: Counted over what the team knows, so a known count under the cutoff is not proof: the engine counts all the area's unowned land, and unrevealed land of the landmass may lift it over.
	# The first wording said "cannot spawn" outright (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iLand = len(target)
	iUnknownEdge = 0
	shelf = {}
	for (x, y) in ourLand.keys():
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(x, y, DirectionTypes(iDirection))
			if adjacent is None or adjacent.isNone():
				continue
			if not adjacent.isRevealed(iTeam, False):
				iUnknownEdge += 1
				continue
			if adjacent.getTerrainType() != iCoast or adjacent.isImpassable() or adjacent.isLake() or adjacent.getRevealedOwner(iTeam, False) != -1 or adjacent.getYield(YieldTypes.YIELD_FOOD) <= 0:
				continue
			shelf[(adjacent.getX(), adjacent.getY())] = True
	iShelf = len(shelf)
	iEstimate = iLand + iShelf / 2
	row = {"unownedLand": iLand, "unownedShelf": iShelf, "estimate": iEstimate, "threshold": iThreshold, "unrevealedNextToOurLand": iUnknownEdge}
	if iEstimate >= iThreshold:
		row["landBarbariansCanSpawn"] = True
		row["text"] = "Barbarian land units can still spawn on our landmass: its known unowned land (%d) plus half its known unowned shelf (%d) is %d, at least %d (advc.300); they stop once borders take it under that" % (iLand, iShelf, iEstimate, iThreshold)
	elif iUnknownEdge:
		row["landBarbariansCanSpawn"] = None
		row["text"] = "Uncertain whether Barbarian land units can spawn on our landmass: what we know of its unowned land (%d) plus half its unowned shelf (%d) is %d, under %d (advc.300), but %d unrevealed plot(s) border it and may add to the count; scouting them settles it" % (iLand, iShelf, iEstimate, iThreshold, iUnknownEdge)
	else:
		row["landBarbariansCanSpawn"] = False
		row["text"] = "Barbarian land units cannot spawn on our landmass now: all of it is revealed, and its unowned land (%d) plus half its unowned shelf (%d) is %d, under %d (advc.300); scout or work instead of fog busting here, unless a Barbarian city or ship comes" % (iLand, iShelf, iEstimate, iThreshold)
	result.append(row)
	if free:
		# <!-- custom: The user asked (2026-11-15) that the reminder also say where freed posts could go, as fog busting ends once the land is lit: an unheld post if any remains, a city with no land defender, or fog elsewhere. (Claude code Opus 5.5) -->
		undefended = []
		for city in _cities(player):
			plot = city.plot()
			bDefended = False
			for i in range(plot.getNumUnits()):
				other = plot.getUnit(i)
				if other.getOwner() == player.getID() and other.getDomainType() == DomainTypes.DOMAIN_LAND and other.canDefend(plot):
					bDefended = True
					break
			if not bDefended:
				undefended.append(city.getName())
		szWhere = "fog elsewhere"
		if iExposed > 0:
			szWhere = "an unheld post below, or fog elsewhere"
		if undefended:
			szWhere = "a city with no land defender (%s), %s" % (", ".join(undefended), szWhere)
		result.append({"freePosts": [{"unit": u.getID(), "type": gc.getUnitInfo(u.getUnitType()).getType(), "x": u.getX(), "y": u.getY()} for u in free], "undefendedCities": undefended, "text": "%s watch no unowned land that nothing else sees: wake them for %s" % (", ".join(["%s %d at %d,%d" % (gc.getUnitInfo(u.getUnitType()).getType(), u.getID(), u.getX(), u.getY()) for u in free]), szWhere)})
	if iExposed == 0:
		# <!-- custom: Said plainly, so posts are not kept for land that no longer needs them. (Claude code Opus 5.5) -->
		if target:
			result.append({"done": True, "text": "every unowned plot of our landmass is in sight now: fog busting needs no more posts here"})
		return result
	held = {}
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND:
			held[(unit.getX(), unit.getY())] = unit.getID()
		(unit, it) = player.nextUnit(it, False)
	# <!-- custom: Ties go to hills, then to the plot furthest from our cities: at turn 14 of the islands replay (98,29) and (99,28) both covered 14, and the user pointed out (98,29) lies further out, where land stays unowned longer as the capital's borders grow. (Claude code Opus 5.5) -->
	cityPlots = [(c.getX(), c.getY()) for c in _cities(player)]
	posts = []
	left = target.copy()
	while left and len(posts) < 8:
		best = None
		for plot in candidates:
			iRange = _fogPostSight(plot)
			covered = [(plot.getX() + dx, plot.getY() + dy) for dx in range(-iRange, iRange + 1) for dy in range(-iRange, iRange + 1) if left.has_key((plot.getX() + dx, plot.getY() + dy))]
			key = (len(covered), iRange, min([max(abs(plot.getX() - cx), abs(plot.getY() - cy)) for (cx, cy) in cityPlots]))
			if best is None or key > best[2]:
				best = (plot, covered, key)
		if best is None or not best[1]:
			break
		for xy in best[1]:
			del left[xy]
		post = {"x": best[0].getX(), "y": best[0].getY(), "hills": _fogPostSight(best[0]) == 2, "covers": len(best[1]), "heldBy": held.get((best[0].getX(), best[0].getY()))}
		posts.append(post)
	szPosts = ", ".join(["%d,%d%s" % (p["x"], p["y"], (p["hills"] and " (hills)") or "") for p in posts])
	row = {"exposedNow": iExposed, "unownedLand": len(target), "posts": posts, "uncoveredByPosts": len(left)}
	row["text"] = "%d unowned plots of our landmass are out of sight now, where Barbarians can spawn; %d post(s) would watch all %d unowned plots: %s" % (iExposed, len(posts), len(target) - len(left), szPosts)
	return [row] + result


def _remindSharedBonuses(player, args):
	# <!-- custom: The user's idea at turn 65 of the islands replay (2026-11-15), after The Hague lived on a Sheep moved from Amsterdam: a food bonus two or more of our cities reach can be worked by whichever needs it most.
	# Listed with the city working it and each city's food surplus; when a city with less food than the one working it could take it, the 'work' click that moves it is given.
	# The choice stays the agent's: a city building a Settler turns food into production, so its surplus reads low. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	cities = _cities(player)
	if len(cities) < 2:
		return []
	byPlot = {}
	for city in cities:
		for i in range(gc.getNUM_CITY_PLOTS()):
			plot = city.getCityIndexPlot(i)
			if plot is None or plot.isNone() or plot.getOwner() != player.getID():
				continue
			iBonus = plot.getBonusType(iTeam)
			if iBonus < 0 or gc.getBonusInfo(iBonus).getYieldChange(YieldTypes.YIELD_FOOD) <= 0:
				continue
			byPlot.setdefault((plot.getX(), plot.getY()), []).append(city)
	result = []
	for ((x, y), reach) in byPlot.items():
		if len(reach) < 2:
			continue
		plot = gc.getMap().plot(x, y)
		worker = None
		for city in reach:
			if city.isWorkingPlot(plot):
				worker = city
		surplus = [{"city": city.getName(), "id": city.getID(), "foodDifference": city.foodDifference(True)} for city in reach]
		row = {"x": x, "y": y, "bonus": gc.getBonusInfo(plot.getBonusType(iTeam)).getType(), "workedBy": worker and worker.getName() or None, "cities": surplus}
		szBonus = row["bonus"][6:].capitalize()
		# <!-- custom: A city building a Settler or Worker turns its food into production, so its surplus reads 0: at turn 74 of the islands replay this told the agent to move the Rice from The Hague (+5) to Amsterdam, which was building a Worker.
		# Such a city is not offered as the hungrier one (CyCity.isFoodProduction). (Claude code Opus 5.5) -->
		hungrier = [city for city in reach if not city.isFoodProduction() and (worker is None or city.getID() != worker.getID()) and (worker is None or city.foodDifference(True) < worker.foodDifference(True))]
		hungrier.sort(lambda a, b: cmp(a.foodDifference(True), b.foodDifference(True)))
		szCities = ", ".join(["%s %+d food" % (c["city"], c["foodDifference"]) for c in surplus])
		if worker is None:
			row["text"] = "%s at %d,%d is worked by none of %s; 'work city=%d x=%d y=%d' gives it to %s" % (szBonus, x, y, szCities, hungrier[0].getID(), x, y, hungrier[0].getName())
		elif hungrier:
			row["text"] = "%s at %d,%d, worked by %s, is shared with %s: 'work city=%d x=%d y=%d' moves it to %s" % (szBonus, x, y, worker.getName(), szCities, hungrier[0].getID(), x, y, hungrier[0].getName())
		else:
			continue
		result.append(row)
	return result


# <!-- custom: Workers per city, less WORKERS_LESS, that expansionSupport aims for: 2N - 1, the user's rule of thumb. (Claude code Opus 5.5) -->
WORKERS_PER_CITY = 2
WORKERS_LESS = 1


def _remindExpansionSupport(player, args):
	# <!-- custom: At turn 52 of the 2026-11-19 validation run a second Settler was 2 turns out while our 2 cities had 1 Worker, no defender and 5 resources unimproved; the user caught it.
	# Spoken while a Settler (a unit that founds, read from the XML) is queued or out: the Workers (units with a work rate) per city and the cities with no unit able to defend them, so expansion does not outrun what holds and improves the land. (Claude code Opus 5.5) -->
	cities = _cities(player)
	iSettlers = len([1 for unit in _units(player) if unit.isFound()])
	iWorkers = len([1 for unit in _units(player) if gc.getUnitInfo(unit.getUnitType()).getWorkRate() > 0 and unit.getDomainType() == DomainTypes.DOMAIN_LAND])
	iSettlersQueued = 0
	iWorkersQueued = 0
	undefended = []
	for city in cities:
		for i in range(city.getOrderQueueLength()):
			order = city.getOrderFromQueue(i)
			if order.eOrderType == OrderTypes.ORDER_TRAIN:
				info = gc.getUnitInfo(order.iData1)
				if info.isFound():
					iSettlersQueued += 1
				elif info.getWorkRate() > 0 and info.getDomainType() == DomainTypes.DOMAIN_LAND:
					iWorkersQueued += 1
		plot = city.plot()
		if not [1 for k in range(plot.getNumUnits()) if plot.getUnit(k).getOwner() == player.getID() and plot.getUnit(k).canDefend(plot) and plot.getUnit(k).canFight()]:
			undefended.append(city.getName())
	# <!-- custom: The user's rule of thumb, turn 81: about 2 Workers per city minus 1 (5 for 3 cities), as the user also gives the AI; the first version asked for 1 per city. (Claude code Opus 5.5) -->
	iTarget = WORKERS_PER_CITY * len(cities) - WORKERS_LESS
	if iSettlers + iSettlersQueued == 0 or (iWorkers >= iTarget and not undefended):
		return []
	szText = "a Settler is %s while %d cities have %d Worker(s) out (%d queued; about %d is the target)" % ((iSettlers and "out") or "queued", len(cities), iWorkers, iWorkersQueued, iTarget)
	if undefended:
		szText += " and no defender in %s" % ", ".join(undefended)
	szText += ": a new city adds land to improve and hold; Workers and a defender where threats can reach usually come first, unless the site is contested"
	return [{"text": szText, "cities": len(cities), "workers": iWorkers, "workersQueued": iWorkersQueued, "settlers": iSettlers, "settlersQueued": iSettlersQueued, "undefended": undefended}]


# <!-- custom: Plots from a city within which unknown land still matters for the empire's shape: the next city sites and the threats that could reach us lie there. (Claude code Opus 5.5) -->
HOME_UNKNOWN_RADIUS = 6


def _remindHomeUnknown(player, args):
	# <!-- custom: At turn 54 of the 2026-11-19 validation run the land east and west of Dublin was still unknown while a unit had been fortified in the capital with no danger near; the user: the empire's shape and the next sites were then chosen blind.
	# Per city, the directions whose known land borders the unknown within HOME_UNKNOWN_RADIUS plots, from 'directions'. (Claude code Opus 5.5) -->
	result = []
	for city in _cities(player):
		# <!-- custom: Pass the city's ID, not its name: two cities can share a name, and the name lookup failed on a non-ASCII one (2026-11-22). (Claude code Opus 5.5) -->
		sectors = _command("directions")({"player": player.getID(), "city": city.getID(), "radius": HOME_UNKNOWN_RADIUS, "fog": args.get("fog")})["sectors"]
		edges = [(row["direction"], row["unknownEdge"]) for row in sectors if row["unknownEdge"] > 0]
		if not edges:
			continue
		result.append({"text": "unknown land within %d plots of %s, by direction: %s; the next sites and threats lie there, so scout it before units sit idle or a site is chosen" % (HOME_UNKNOWN_RADIUS, city.getName(), ", ".join(["%s %d" % pair for pair in edges])), "city": city.getID(), "unknownEdge": dict(edges)})
	return result


_HELP["limits"] = "Happiness and health, the two limits on a city's growth, and where more of each could come from: per city its happy and health margins (faces to spare) and turns to grow, which limit binds first, what our traits give; the resources giving either, with our status (have, seen in our borders, seen elsewhere) and the tech that lets a city use one; the buildings giving either that a city can build now, or that one tech we can research now unlocks (with the religion one needs); and state religion: the religions in our cities and the happiness our civics give a state religion's cities. Read from the XML, so other rules and mod-mods are followed. args: player."


def cmd_limits(args):
	# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: in this game the focus is happiness, usually scarce early, while health was plentiful; the answers were spread over 'research', 'bonustrade', 'religion' and the city screens. (Claude code Opus 5.5) -->
	player = _player(args)
	iTeam = player.getTeam()
	cities = _cities(player)
	rows = [{"city": city.getName(), "happyMargin": city.happyLevel() - city.unhappyLevel(0), "healthMargin": city.goodHealth() - city.badHealth(False), "growsIn": city.getFoodTurnsLeft()} for city in cities]
	iHappy = min([row["happyMargin"] for row in rows] or [0])
	iHealth = min([row["healthMargin"] for row in rows] or [0])
	traits = [gc.getTraitInfo(i) for i in range(gc.getNumTraitInfos()) if player.hasTrait(i)]
	seen = _seenBonuses(player)
	resources = []
	for i in range(gc.getNumBonusInfos()):
		info = gc.getBonusInfo(i)
		if info.getHappiness() <= 0 and info.getHealth() <= 0:
			continue
		szStatus = _bonusStatus(player, i, seen)
		# <!-- custom: sas-ci-string-compare-exemption: The map report uses a stable visibility state key. (GPT-6.2-Sol) -->
		if szStatus == "unseen":
			continue
		resources.append({"bonus": info.getType(), "happiness": info.getHappiness(), "health": info.getHealth(), "status": szStatus, "usableWith": _typeOrNone(gc.getTechInfo, info.getTechCityTrade()), "haveUsableTech": bool(info.getTechCityTrade() < 0 or gc.getTeam(iTeam).isHasTech(info.getTechCityTrade()))})
	civ = gc.getCivilizationInfo(player.getCivilizationType())
	buildings = []
	for i in range(gc.getNumBuildingInfos()):
		info = gc.getBuildingInfo(i)
		if info.getHappiness() <= 0 and info.getHealth() <= 0:
			continue
		if civ.getCivilizationBuildings(info.getBuildingClassType()) != i:
			continue
		buildable = [city.getName() for city in cities if city.canConstruct(i, False, False, False)]
		iTech = info.getPrereqAndTech()
		if buildable:
			szWhen = "now"
		elif iTech >= 0 and player.canResearch(iTech, False):
			szWhen = "after %s" % gc.getTechInfo(iTech).getType()
		else:
			continue
		buildings.append({"building": info.getType(), "happiness": info.getHappiness(), "health": info.getHealth(), "when": szWhen, "buildableIn": buildable, "needsReligion": _typeOrNone(gc.getReligionInfo, info.getPrereqReligion())})
	religions = []
	for i in range(gc.getNumReligionInfos()):
		inCities = [city.getName() for city in cities if city.isHasReligion(i)]
		if inCities:
			religions.append({"religion": gc.getReligionInfo(i).getType(), "inCities": inCities, "isState": bool(player.getStateReligion() == i)})
	return {"cities": rows, "bindsFirst": (iHappy <= iHealth and "happiness") or "health", "traitHappiness": sum([trait.getHappiness() for trait in traits]), "traitHealth": sum([trait.getHealth() for trait in traits]), "resources": resources, "buildings": buildings, "stateReligion": {"current": _typeOrNone(gc.getReligionInfo, player.getStateReligion()), "happinessFromCivics": player.getStateReligionHappiness(), "religionsInOurCities": religions}}


def _remindHappyHealth(player, args):
	# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: our cities had strong health sources and health to spare while happiness, usually scarce early, would cap Dublin next; with no happiness trait, focus on happiness sources and trade health ones.
	# Spoken when a city has 1 or less to spare in either limit: both margins per city, the limit that binds first, what our traits give (read from the trait XML, so other leaders and mod-mods are followed), the resources we have for each and the copies we could trade away while every city keeps a margin, the happiness or health resources met civs would export, and whether our trade networks are linked to theirs. (Claude code Opus 5.5) -->
	cities = _cities(player)
	if not cities:
		return []
	rows = [(city.getName(), city.happyLevel() - city.unhappyLevel(0), city.goodHealth() - city.badHealth(False)) for city in cities]
	iHappy = min([row[1] for row in rows])
	iHealth = min([row[2] for row in rows])
	if iHappy > 1 and iHealth > 1:
		return []
	szBinding = (iHappy <= iHealth and "happiness") or "health"
	traits = [gc.getTraitInfo(i) for i in range(gc.getNumTraitInfos()) if player.hasTrait(i)]
	traitHappy = sum([trait.getHappiness() for trait in traits])
	traitHealth = sum([trait.getHealth() for trait in traits])
	ours = []
	for i in range(gc.getNumBonusInfos()):
		iHave = player.getNumAvailableBonuses(i)
		info = gc.getBonusInfo(i)
		if iHave <= 0 or (info.getHappiness() <= 0 and info.getHealth() <= 0):
			continue
		# <!-- custom: A copy can go when we hold more than one, or when the one copy's effect leaves every city a margin. (Claude code Opus 5.5) -->
		bSpare = iHave > 1 or (info.getHealth() > 0 and iHealth > info.getHealth()) or (info.getHappiness() > 0 and iHappy > info.getHappiness())
		ours.append({"bonus": info.getType(), "have": iHave, "happiness": info.getHappiness(), "health": info.getHealth(), "canTradeAway": bool(bSpare)})
	market = _command("bonustrade")({"player": player.getID(), "fog": args.get("fog")})
	offers = []
	linked = []
	for leader in market["leaders"]:
		if leader.get("connected"):
			linked.append(leader["name"])
		for szBonus in leader.get("willExport", []):
			info = gc.getBonusInfo(getInfoTypeOrFail(szBonus))
			# <!-- custom: sas-ci-string-compare-exemption: The city audit uses stable happiness and health result keys. (GPT-6.2-Sol) -->
			if (szBinding == "happiness" and info.getHappiness() > 0) or (szBinding == "health" and info.getHealth() > 0):
				offers.append("%s from %s" % (szBonus, leader["name"]))
	# <!-- custom: sas-ci-string-compare-exemption: The city audit uses stable happiness and health result keys. (GPT-6.2-Sol) -->
	szText = "%s binds first (smallest margins: happy %d, health %d); traits give %+d happy, %+d health; our %s resources to trade away: %s; %s resources met civs would export: %s; trade networks linked with: %s" % (szBinding, iHappy, iHealth, traitHappy, traitHealth, (szBinding == "happiness" and "health") or "happiness", ", ".join([row["bonus"] for row in ours if row["canTradeAway"] and ((szBinding == "happiness" and row["health"] > 0) or (szBinding == "health" and row["happiness"] > 0))]) or "none", szBinding, ", ".join(offers) or "none", ", ".join(linked) or "nobody (a resource trade needs our networks linked, by road or coast)")
	return [{"text": szText, "bindsFirst": szBinding, "cities": [{"city": name, "happyMargin": h, "healthMargin": g} for (name, h, g) in rows], "traitHappiness": traitHappy, "traitHealth": traitHealth, "ourResources": ours, "offers": offers, "linkedWith": linked}]


# <!-- custom: Each player's last seen city-site verdicts, by plot, for the sitesChanged check; kept for the session, like rivalMoods' state. (Claude code Opus 5.5) -->
_lastSites = {}
# <!-- custom: Sites the sitesChanged check follows, best by found value. (Claude code Opus 5.5) -->
SITES_FOLLOWED = 12


def _siteWorthSettling(szPriority):
	return bool(szPriority) and not szPriority.startswith("skip") and not szPriority.startswith("dart") and not szPriority.endswith("(poor food)")


def _remindSitesChanged(player, args):
	# <!-- custom: The user at turn 79 of the 2026-11-19 validation run: candidate sites must be reconsidered whenever new information arrives, fog cleared, a resource revealed, a war, a city founded or destroyed; the plan had kept 29,14 though Cork's grown borders made it take 2 of Cork's strong plots, while 30,15 shared none.
	# All of those reach a site's priority, food, unknown plots or overlap, so a change in any of them since the last call is named; the first call only records. (Claude code Opus 5.5) -->
	sites = _command("plansites")({"player": player.getID(), "legal": True, "spread": 0, "limit": SITES_FOLLOWED, "fog": args.get("fog")})["sites"]
	now = {}
	for site in sites:
		now[(site["x"], site["y"])] = (site.get("priority"), site.get("foodAtSize%d" % SITE_FOOD_SIZE), site["unknownPlots"], site["sharedStrong"])
	before = _lastSites.get(player.getID())
	_lastSites[player.getID()] = now
	if before is None:
		return []
	# <!-- custom: The first version named every site entering or leaving the 12 by ranking shifts, mostly "dart only" or "skip" sites (turn 80); now a site new or gone is named only when worth settling, and a change only when its verdict changed. (Claude code Opus 5.5) -->
	changes = []
	for (xy, verdict) in now.items():
		if not before.has_key(xy):
			if _siteWorthSettling(verdict[0]):
				changes.append("%d,%d new (%s, food %s)" % (xy[0], xy[1], verdict[0], verdict[1]))
		elif before[xy] != verdict and (_siteWorthSettling(verdict[0]) or _siteWorthSettling(before[xy][0])):
			changes.append("%d,%d %s -> %s (food %s -> %s, unknown %d -> %d, strong shared %d -> %d)" % (xy[0], xy[1], before[xy][0], verdict[0], before[xy][1], verdict[1], before[xy][2], verdict[2], before[xy][3], verdict[3]))
	for xy in before.keys():
		if not now.has_key(xy) and _siteWorthSettling(before[xy][0]):
			changes.append("%d,%d gone (founded, taken, no longer legal or out of the best %d)" % (xy[0], xy[1], SITES_FOLLOWED))
	if not changes:
		return []
	return [{"text": "city sites changed since the last check: %s; review the dot-map marks" % "; ".join(changes), "changes": changes}]


# <!-- custom: A rival's culture on a plot at this percent of ours or more counts as pressure. (Claude code Opus 5.5) -->
CULTURE_PRESSURE_PCT = 70


def _remindBorderPressure(player, args):
	# <!-- custom: The user at turn 72 of the 2026-11-19 validation run: Emain Macha, founded 6 plots from Pasargadae, a holy city, would find it hard to hold the Gold 2 plots away without culture of its own.
	# Per city, the strong plots of its radius (a bonus, or SHARED_STRONG_YIELD+ total yield) that a rival owns or whose rival culture reaches CULTURE_PRESSURE_PCT of ours, as a plot's hover shows each civ's culture, with the city's culture rate and the culture buildings it can build (read from the XML). (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	rivals = [i for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() != iTeam]
	result = []
	for city in _cities(player):
		pressed = []
		for j in range(1, gc.getNUM_CITY_PLOTS()):
			plot = city.getCityIndexPlot(j)
			if plot is None or plot.isNone() or not plot.isRevealed(iTeam, False):
				continue
			iBonus = plot.getBonusType(iTeam)
			if iBonus < 0 and sum([plot.getYield(YieldTypes(k)) for k in range(YieldTypes.NUM_YIELD_TYPES)]) < SHARED_STRONG_YIELD:
				continue
			iOurs = plot.getCulture(player.getID())
			(iRival, iWho) = max([(plot.getCulture(i), i) for i in rivals] or [(0, -1)])
			if iRival <= 0:
				continue
			if plot.getOwner() != player.getID() or iRival * 100 >= iOurs * CULTURE_PRESSURE_PCT:
				pressed.append("%d,%d%s (%s %d against our %d)" % (plot.getX(), plot.getY(), (iBonus >= 0 and " " + gc.getBonusInfo(iBonus).getType()) or "", gc.getPlayer(iWho).getName(), iRival, iOurs))
		if not pressed:
			continue
		buildings = [gc.getBuildingInfo(i).getType() for i in range(gc.getNumBuildingInfos()) if (gc.getBuildingInfo(i).getCommerceChange(CommerceTypes.COMMERCE_CULTURE) > 0 or gc.getBuildingInfo(i).getObsoleteSafeCommerceChange(CommerceTypes.COMMERCE_CULTURE) > 0) and city.canConstruct(i, False, False, False)]
		result.append({"text": "%s's strong plots under a rival's culture: %s; its culture is %d a turn; culture buildings it can build: %s" % (city.getName(), ", ".join(pressed), city.getCommerceRate(CommerceTypes.COMMERCE_CULTURE), ", ".join(buildings) or "none"), "city": city.getID()})
	return result


# <!-- custom: Hammers a turn below which a city's production is named as a concern. (Claude code Opus 5.5) -->
LOW_PRODUCTION_HAMMERS = 3


def _remindLowProduction(player, args):
	# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: Dublin made 2 hammers a turn, so each Archer took 13 turns while the empire had no defender; look at hammer sources such as the Stone or a plains hill.
	# For a city under LOW_PRODUCTION_HAMMERS: the unworked tiles of its radius giving 2 hammers or more now, and the improvements we can build on its own tiles that add hammers (the game's own canBuild and yield change, so other rules are followed), best first. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	result = []
	for city in _cities(player):
		iHammers = city.getYieldRate(YieldTypes.YIELD_PRODUCTION)
		if iHammers >= LOW_PRODUCTION_HAMMERS:
			continue
		tiles = []
		builds = []
		for j in range(gc.getNUM_CITY_PLOTS()):
			plot = city.getCityIndexPlot(j)
			if plot is None or plot.isNone() or j == 0 or plot.getOwner() != player.getID() or not plot.isRevealed(iTeam, False):
				continue
			iNow = plot.getYield(YieldTypes.YIELD_PRODUCTION)
			if iNow >= 2 and not city.isWorkingPlot(plot):
				tiles.append((iNow, "%d,%d (%s)" % (plot.getX(), plot.getY(), "/".join([str(plot.getYield(YieldTypes(k))) for k in range(YieldTypes.NUM_YIELD_TYPES)]))))
			for i in range(gc.getNumBuildInfos()):
				iImprovement = gc.getBuildInfo(i).getImprovement()
				if iImprovement < 0 or not plot.canBuild(i, player.getID(), False):
					continue
				iGain = plot.calculateImprovementYieldChange(iImprovement, YieldTypes.YIELD_PRODUCTION, player.getID(), False)
				# <!-- custom: The user, turn 81: improve river plots first, for the extra commerce rivers give in our balance; they sort first and are marked. (Claude code Opus 5.5) -->
				if iGain > 0:
					bRiver = bool(plot.isRiver())
					builds.append((bRiver, iNow + iGain, "%s at %d,%d (%d hammers%s)" % (gc.getBuildInfo(i).getType(), plot.getX(), plot.getY(), iNow + iGain, (bRiver and ", river") or "")))
		tiles.sort()
		tiles.reverse()
		builds.sort()
		builds.reverse()
		if not tiles and not builds:
			continue
		result.append({"text": "%s makes %d hammer(s) a turn; unworked hammer tiles: %s; improvements adding hammers: %s" % (city.getName(), iHammers, ", ".join([text for (n, text) in tiles[:3]]) or "none", ", ".join([text for (r, n, text) in builds[:3]]) or "none"), "city": city.getID(), "hammers": iHammers})
	return result


# <!-- custom: Turns within which a whipped citizen regrows for the whip check to call the city food-rich. (Claude code Opus 5.5) -->
WHIP_REGROW_TURNS = 6


def _remindWhip(player, args):
	# <!-- custom: The user asked for a slaving plan at turn 54 of the 2026-11-19 validation run: a whip trades a citizen for hammers, which pays most when that citizen could not work well anyway.
	# Named when a hurry that costs population (read from the hurry XML, so other rules are followed) could finish the build with 1 citizen while the city has no happy or health margin left; builds made with food (isFoodProduction) are left out, as they already use the surplus food. (Claude code Opus 5.5) -->
	# <!-- custom: The user, same turn: a whip also pays when the city has lots of food, as food then becomes production without the city stalling, provided happiness allows it.
	# So it is also named when the citizen regrows within WHIP_REGROW_TURNS at the current surplus (the food bar of the current size over the surplus, a slight overestimate as the bar is smaller one size down), unless whip anger is already running in a city with at most one happy face to spare. (Claude code Opus 5.5) -->
	whips = [i for i in range(gc.getNumHurryInfos()) if gc.getHurryInfo(i).getProductionPerPopulation() > 0]
	result = []
	for city in _cities(player):
		if city.getOrderQueueLength() == 0 or city.isFoodProduction():
			continue
		for iHurry in whips:
			if not city.canHurry(iHurry, False) or city.hurryPopulation(iHurry) != 1:
				continue
			iHappy = city.happyLevel() - city.unhappyLevel(0)
			iHealth = city.goodHealth() - city.badHealth(False)
			iSurplus = city.foodDifference(True)
			iRegrow = -1
			if iSurplus > 0:
				iRegrow = (city.growthThreshold() + iSurplus - 1) / iSurplus
			bCapped = iHappy <= 0 or iHealth <= 0
			bFoodRich = iRegrow >= 0 and iRegrow <= WHIP_REGROW_TURNS
			if not bCapped and not bFoodRich:
				continue
			# <!-- custom: Whip anger stacks: at turn 65 of the 2026-11-19 validation run this suggested whipping Dublin's Archer at no happy face to spare while the Granary whip's anger still ran 8 turns, which would add a second angry citizen.
			# While anger runs, a city must have more than one happy face to spare. (Claude code Opus 5.5) -->
			if city.getHurryAngerTimer() > 0 and iHappy <= 1:
				continue
			if bCapped:
				szWhy = "no %s to spare, so the city is stalled and growing wastes its +%d food on a citizen who cannot work well: better whip than waste" % ((iHappy <= 0 and "happy face") or "health", iSurplus)
			else:
				szWhy = "the citizen regrows in about %d turn(s) at +%d food, so food becomes production without stalling the city" % (iRegrow, iSurplus)
			# <!-- custom: The user, turn 57 of the 2026-11-19 validation run: a Granary goes well with whipping, as it keeps food after growth so the whipped citizen regrows sooner; "or whatever a mod-mod has", so any building with food kept (getFoodKept) counts. (Claude code Opus 5.5) -->
			if city.getFoodKept() <= 0:
				keepers = [gc.getBuildingInfo(i).getType() for i in range(gc.getNumBuildingInfos()) if gc.getBuildingInfo(i).getFoodKept() > 0 and city.canConstruct(i, False, False, False)]
				if keepers:
					szWhy += "; %s would keep food after growth, so each whip regrows sooner" % " or ".join(keepers)
			result.append({"text": "%s can finish %s by %s for 1 citizen: %s; whip anger now %d turn(s), happy margin %d" % (city.getName(), str(_orderData(city.getOrderFromQueue(0))), gc.getHurryInfo(iHurry).getType(), szWhy, city.getHurryAngerTimer(), iHappy), "city": city.getID(), "hurry": gc.getHurryInfo(iHurry).getType(), "happyMargin": iHappy, "healthMargin": iHealth, "foodSurplus": iSurplus, "regrowTurns": iRegrow, "hurryAngerTurns": city.getHurryAngerTimer()})
	return result


def _remindStaleMarks(player, args):
	# <!-- custom: The user's idea at turn 71 of the islands replay (2026-11-15), after Rotterdam was founded on its own dot-map site: a city-site mark that has done its job should go, so the map shows only the plan still open. A dot or sign on a plot where one of our cities stands, or within 2 plots of one (the site taken or crowded out); 'mark x= y= clear=1' removes both. What a mark is for cannot be read from it, so other marks, such as a road path, are left to the agent. (Claude code Opus 5.5) -->
	cityPlots = [(city.getX(), city.getY(), city.getName()) for city in _cities(player)]
	marks = {}
	dotColors = {}
	for dot in _dotMapCities(player.getID()):
		marks[(dot["x"], dot["y"])] = "dot"
		dotColors[(dot["x"], dot["y"])] = dot["color"]
	engine = CyEngine()
	for i in range(engine.getNumSigns()):
		sign = engine.getSignByIndex(i)
		if int(sign.getPlayerType()) in (-1, player.getID()):
			xy = (sign.getPlot().getX(), sign.getPlot().getY())
			marks[xy] = (marks.has_key(xy) and "dot and sign") or "sign"
	result = []
	for ((x, y), szKind) in marks.items():
		near = [(plotDistance(x, y, cx, cy), name) for (cx, cy, name) in cityPlots if plotDistance(x, y, cx, cy) <= 2]
		if not near:
			continue
		near.sort()
		(iDistance, szCity) = near[0]
		# <!-- custom: A mark on the city itself is kept: the user marks our cities on the dot map to see a planned site's overlap with them (2026-11-19 validation run).
		# A candidate's mark left on the city just founded there is named once, to re-mark it as a city (the contrast colour and its name), as the user asked when Emain Macha was founded at turn 71. (Claude code Opus 5.5) -->
		if iDistance == 0:
			if dotColors.get((x, y)) not in (None, _contrastColor(player)):
				result.append({"x": x, "y": y, "mark": szKind, "city": szCity, "distance": 0, "text": "%s stands on a site mark: 'mark x=%d y=%d text=%s' re-marks it as our city" % (szCity, x, y, szCity)})
			continue
		szWhy = (iDistance == 0 and "%s stands on it" % szCity) or ("%s is %d plot(s) away" % (szCity, iDistance))
		result.append({"x": x, "y": y, "mark": szKind, "city": szCity, "distance": iDistance, "text": "the %s at %d,%d is done with: %s; 'mark x=%d y=%d clear=1' removes it" % (szKind, x, y, szWhy, x, y)})
	return result


_REMINDER_CHECKS = (("huts", _remindHuts), ("waterScouting", _remindWaterScouting), ("fogBusting", _remindFogBusting), ("idleGarrison", _remindIdleGarrison), ("exposed", _remindExposed), ("scoutBeforeFounding", _remindScoutBeforeFounding), ("research", _remindResearch), ("cities", _remindCities), ("wounded", _remindWounded), ("gold", _remindGold), ("trades", _remindTrades), ("screens", _remindScreens), ("losses", _remindLosses), ("unfinished", _remindUnfinished), ("exports", _remindExports), ("unimproved", _remindUnimproved), ("sleepingWorkers", _remindSleepingWorkers), ("idleImprovements", _remindIdleImprovements), ("sharedBonuses", _remindSharedBonuses), ("expansionSupport", _remindExpansionSupport), ("homeUnknown", _remindHomeUnknown), ("happyHealth", _remindHappyHealth), ("lowProduction", _remindLowProduction), ("borderPressure", _remindBorderPressure), ("sitesChanged", _remindSitesChanged), ("whip", _remindWhip), ("staleMarks", _remindStaleMarks), ("rivalMoods", _remindRivalMoods))


def cmd_reminders(args):
	player = gc.getPlayer(_playerId(args))
	_requireOwnTeamUnderFog(args, player, "reminders")
	# <!-- custom: mute and unmute, the user's idea (2026-11-15): an agent that has weighed a reminder can silence it, a whole check (mute=fogBusting) or one entry (mute=sharedBonuses@100,27, by the entry's plot), for the rest of the session; unmute=all lifts every one. The muted list comes back with each reply, so nothing is hidden unawares. (Claude code Opus 5.5) -->
	muted = _state.setdefault("mutedReminders", {})
	if args.get("mute"):
		muted[str(args["mute"])] = True
	if args.get("unmute"):
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if str(args["unmute"]) == "all":
			muted.clear()
		elif muted.has_key(str(args["unmute"])):
			del muted[str(args["unmute"])]
	result = []
	iMuted = 0
	for (szCheck, check) in _REMINDER_CHECKS:
		if muted.has_key(szCheck):
			continue
		for entry in check(player, args):
			entry["check"] = szCheck
			if entry.has_key("x") and entry.has_key("y") and muted.has_key("%s@%d,%d" % (szCheck, entry["x"], entry["y"])):
				iMuted += 1
				continue
			result.append(entry)
	return {"reminders": result, "muted": muted.keys(), "mutedEntriesLeftOut": iMuted}


_HELP["scores"] = "The Info screen's Score tab, per player met and ourselves: score and its change since last turn, techs known, land share, power and power per city where the demographics are visible (as the scoreboard's ratio), cities seen, state religion and holy city, vassal status, will to talk, and current research and progress where espionage lets it be seen (research null: seen, researching nothing). Also its other columns: traits, land in hundredths of a percent, masters and vassals by player ID, and per rival the power ratio (per mille, theirs against ours), attitude and its value, worst enemy, war, peace treaty, trade network, open borders, defensive pact, golden age, anarchy and our espionage weight. sort=<field> puts the highest first, sort=-<field> the lowest, as clicking a column header does; default score. args: sort, player."


def cmd_scores(args):
	# <!-- custom: The user pointed to the Info screen's Score tab at turn 150 of the turn-0 game (2026-11-14): it showed at a glance that we knew 27 techs against 29 to 37 for every rival, that Pericles gained +42 score a turn, and power totals per city, which no SASPilot command gave together.
	# Follows CvInfoScreen.drawScoreTab: the same tests decide what is visible. (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	iTurn = gc.getGame().getGameTurn()
	map = CyMap()
	iLand = map.getLandPlots()
	rows = []
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if not other.isAlive() or other.isBarbarian() or other.isMinorCiv():
			continue
		bUs = iOther == player.getID()
		if not bUs and not team.isHasMet(other.getTeam()):
			continue
		otherTeam = gc.getTeam(other.getTeam())
		iTechs = len([i for i in range(gc.getNumTechInfos()) if otherTeam.isHasTech(i)])
		row = {"player": iOther, "name": other.getName(), "score": gc.getGame().getPlayerScore(iOther), "techs": iTechs}
		if iTurn >= 1:
			row["scoreChange"] = other.getScoreHistory(iTurn - 1) - other.getScoreHistory(max(0, iTurn - 2))
		if iLand > 0:
			row["landPerMille"] = 1000 * other.getTotalLand() / iLand
		cities = [city for city in _cities(other) if bUs or city.isRevealed(player.getTeam(), False)]
		row["citiesSeen"] = len(cities)
		if bUs or player.canSeeDemographics(iOther):
			row["power"] = other.getPower()
			if cities:
				row["powerPerCity"] = other.getPower() / len(cities)
		iReligion = other.getStateReligion()
		if iReligion >= 0:
			row["religion"] = gc.getReligionInfo(iReligion).getType()
			row["holyCity"] = bool(other.hasHolyCity(iReligion))
		row["vassal"] = bool(otherTeam.isAVassal())
		# <!-- custom: The rest of the Score tab's columns, the user's ask at turn 200 of a Large autoplay (2026-11-15), where the tab and this reply were compared column by column: traits, land to the hundredth of a percent, V/M, and for rivals the power ratio, attitude and its number, war or forced peace, trade network, open borders, defensive pact, worst enemy, golden age or anarchy and our espionage weight, each under the test drawScoreTab applies. (Claude code Opus 5.5) -->
		leader = gc.getLeaderHeadInfo(other.getLeaderType())
		row["traits"] = [gc.getTraitInfo(i).getType() for i in range(gc.getNumTraitInfos()) if leader.hasTrait(i)][:2]
		if iLand > 0:
			row["landPerTenThousand"] = 10000 * other.getTotalLand() / iLand
		met = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and (i == player.getID() or team.isHasMet(gc.getPlayer(i).getTeam()))]
		row["masters"] = [p.getID() for p in met if p.getTeam() != other.getTeam() and otherTeam.isVassal(p.getTeam())]
		row["vassals"] = [p.getID() for p in met if p.getTeam() != other.getTeam() and gc.getTeam(p.getTeam()).isVassal(other.getTeam())]
		if not bUs:
			row["willTalk"] = bool(other.AI_isWillingToTalk(player.getID()) and player.AI_isWillingToTalk(iOther))
			if "power" in row and row["power"] > 0:
				# <!-- custom: Their power against ours, as the tab shows it with BUG's default 'them versus you' (0.752 for Gandhi); per mille to stay an integer. (Claude code Opus 5.5) -->
				row["powerRatioPerMille"] = 1000 * row["power"] / max(1, player.getPower())
			if not other.isHuman():
				row["attitude"] = _enumName(AttitudeTypes, other.AI_getAttitude(player.getID()))
				row["attitudeValue"] = _attitudeCount(iOther, player.getID())
				row["worstEnemy"] = bool(not otherTeam.isHuman() and other.getWorstEnemyName() and other.getWorstEnemyName() == team.getName())
			row["atWar"] = bool(otherTeam.isAtWar(player.getTeam()))
			row["peaceTreaty"] = bool(team.isForcePeace(other.getTeam()))
			row["tradeNetwork"] = bool(other.canTradeNetworkWith(player.getID()))
			row["openBorders"] = bool(otherTeam.isOpenBorders(player.getTeam()))
			row["defensivePact"] = bool(otherTeam.isDefensivePact(player.getTeam()))
			row["goldenAge"] = bool(other.isGoldenAge())
			row["anarchy"] = bool(other.isAnarchy())
			row["espionageWeight"] = player.getEspionageSpendingWeightAgainstTeam(other.getTeam())
		if player.canSeeResearch(iOther) or bUs:
			iTech = other.getCurrentResearch()
			# <!-- custom: A visible rival researching nothing was left out, so at turn 200 of a Large autoplay (2026-11-15) Kublai looked hidden while the scoreboard showed him at 0% (advc.085) and the Score tab a blank percent.
			# Now research is null with no percent, as the tab shows it. (Claude code Opus 5.5) -->
			row["research"] = _typeOrNone(gc.getTechInfo, iTech)
			if iTech >= 0:
				row["researchPercent"] = 100 * otherTeam.getResearchProgress(iTech) / max(1, otherTeam.getResearchCost(iTech))
		rows.append(row)
	# <!-- custom: Sorting as the tab's column headers do, the user's follow-up: sort=<field> puts the highest first, sort=-<field> the lowest; players without that field (hidden power, say) come last either way. (Claude code Opus 5.5) -->
	szSort = args.get("sort", "score")
	bAscending = szSort.startswith("-")
	szField = szSort.lstrip("-")
	shown = [row for row in rows if row.get(szField) is not None]
	if rows and not shown:
		raise ValueError("no player has a %s field to sort by" % szField)
	shown.sort(lambda a, b: cmp(a[szField], b[szField]))
	if not bAscending:
		shown.reverse()
	return {"players": shown + [row for row in rows if row.get(szField) is None], "sortedBy": szSort}


_HELP["demographics"] = "The Info screen's Demographics tab: for soldiers (military power), land, population, economy (commerce), industry (production) and agriculture (food), our value, our rank among us and our rivals (1 is best), and the rivals' best, average and worst. Rivals are every living non-Barbarian player of another team, met or not, as the tab counts them; their economy, industry and agriculture are last turn's, as the tab shows them (advc.077). args: player."


def cmd_demographics(args):
	# <!-- custom: The user pointed out at turn 90 of the turn-0 game (2026-11-14) that we were falling behind militarily, and that a player sees it on the Info screen's Demographics tab; SASPilot had no command for it, and 'relations' hides power under fog.
	# This follows CvInfoScreen.drawDemographicsTab (advc.077): the same rivals, current power, land and population for all, history for the rivals' economy, industry and agriculture. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	_requireOwnTeamUnderFog(args, player, "the demographics")
	team = gc.getTeam(player.getTeam())
	iTurn = gc.getGame().getGameTurn() - 1
	rows = {"soldiers": [], "land": [], "population": [], "economy": [], "industry": [], "agriculture": []}
	ours = {}
	for i in range(gc.getMAX_PLAYERS()):
		other = gc.getPlayer(i)
		if not (other.isAlive() or i == player.getID()) or other.isBarbarian() or other.isMinorCiv():
			continue
		bUs = i == player.getID()
		if not bUs:
			otherTeam = gc.getTeam(other.getTeam())
			# <!-- custom: The tab leaves out our own team, and a master and its other vassals unless we are a vassal ourselves. (Claude code Opus 5.5) -->
			if otherTeam.getID() == team.getID() or (not team.isAVassal() and otherTeam.getMasterTeam() == team.getMasterTeam()):
				continue
		values = {"soldiers": other.getPower() * 1000, "land": other.getTotalLand() * 1000, "population": other.getRealPopulation()}
		if bUs:
			values["economy"] = other.calculateTotalCommerce()
			values["industry"] = other.calculateTotalYield(YieldTypes.YIELD_PRODUCTION)
			values["agriculture"] = other.calculateTotalYield(YieldTypes.YIELD_FOOD)
			ours = values
		elif iTurn >= 0:
			values["economy"] = other.getEconomyHistory(iTurn)
			values["industry"] = other.getIndustryHistory(iTurn)
			values["agriculture"] = other.getAgricultureHistory(iTurn)
		else:
			values["economy"] = values["industry"] = values["agriculture"] = 0
		# <!-- custom: Under fog, the tab's own display rules with its default settings (bRanksAmongKnown, bShowBestKnown): the first version gave exact rival best, worst and average before meeting anyone (Codex's review, round 35).
		# The rank counts only players we have met; best and worst only met rivals whose demographics we can see, best with one such rival and worst with two; the average all rivals, met or not, shown above 3 rivals and rounded to a multiple of 5 (of 5,000 for the values scaled by 1,000).
		# Without fog, exact values for every rival, for debugging. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		bMet = bUs or team.isHasMet(other.getTeam())
		bSeen = bUs or player.canSeeDemographics(i)
		for szKey in rows.keys():
			rows[szKey].append((values[szKey], bUs, bMet, bSeen))
	bFog = _fogTeam(args) >= 0
	multiples = {"soldiers": 5000, "land": 5000, "population": 5000, "economy": 5, "industry": 5, "agriculture": 5}
	result = {}
	for szKey in rows.keys():
		allRivals = [row[0] for row in rows[szKey] if not row[1]]
		if bFog:
			ranked = [row[0] for row in rows[szKey] if not row[1] and row[2]]
			shown = [row[0] for row in rows[szKey] if not row[1] and row[2] and row[3]]
		else:
			ranked = allRivals
			shown = allRivals
		entry = {"value": ours[szKey], "rank": 1 + len([value for value in ranked if value > ours[szKey]])}
		if len(shown) >= 1:
			entry["rivalBest"] = max(shown)
		if len(shown) >= 2 or (not bFog and shown):
			entry["rivalWorst"] = min(shown)
		if allRivals and (not bFog or len(allRivals) > 3):
			iAverage = sum(allRivals) / len(allRivals)
			if bFog:
				iMultiple = multiples[szKey]
				# <!-- custom: CvInfoScreen.roundToMultiple in integers: Civ4's single-precision FPU (KI#1093) would round 5,000-scaled values in floats. (Claude code Opus 5.5) -->
				iAverage = iAverage + iMultiple / 2
				iAverage -= iAverage % iMultiple
			entry["rivalAverage"] = iAverage
		result[szKey] = entry
	result["rivals"] = len([1 for row in rows["soldiers"] if not row[1]])
	return result


_HELP["advise"] = "Advice: a heuristic of ours weighing facts into a recommendation, which may be wrong; each reply names its rule and shows the facts it weighed. about=scout: 'scout's steps ranked, most revealed first, then fewest enemies near, then the best defense. about=threats: each animal and barbarian we see within 4 plots of the unit, with its moves, strength against ours, distance, whether it could reach the unit this turn, and the odds if it attacked; 'avoid' where it could reach and would win more often than not, or where our odds of attacking it are under 700 per mille. The advice role: refused on the session role play, allowed on assist and all. args: about, unit, player."


def cmd_advise(args):
	# <!-- custom: The user's facts-versus-advice idea (2026-11-14), with their own example as its first rule: avoid an animal that is faster than you while you are weaker; animals are strong in SAS and give little.
	# A command of its own, so tuning a rule never touches the fact commands that replays compare against. (Claude code Opus 5.5) -->
	szAbout = args.get("about")
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szAbout == "scout":
		result = _command("scout")(args)
		result["rule"] = "most plots revealed first, then fewest animals and barbarians within two plots, then the best defense"
		result["steps"].sort(lambda a, b: cmp((-a["reveals"], len(a["enemiesNear"]), -a["defense"]), (-b["reveals"], len(b["enemiesNear"]), -b["defense"])))
		return result
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if szAbout == "threats":
		return _adviseThreats(args)
	raise ValueError("advise takes about=scout or about=threats, not %s" % szAbout)


def _adviseThreats(args):
	unit = _unit(args)
	_requireOwnTeamUnderFog(args, gc.getPlayer(unit.getOwner()), "threat advice")
	iTeam = unit.getTeam()
	kMap = gc.getMap()
	threats = []
	for dx in range(-4, 5):
		for dy in range(-4, 5):
			plot = kMap.plot(unit.getX() + dx, unit.getY() + dy)
			if plot.isNone() or not plot.isVisible(iTeam, False):
				continue
			for i in range(plot.getNumUnits()):
				other = plot.getUnit(i)
				# <!-- custom: Units the window would draw, as in 'scout'. (Claude code Opus 5.5) -->
				if not other.isBarbarian() or other.isInvisible(iTeam, False) or other.isCargo() or not other.canFight():
					continue
				iDistance = max(abs(dx), abs(dy))
				iTheirMoves = other.baseMoves()
				# <!-- custom: Odds only for an attack that can happen: the first version gave a Settler beside an animal weWinPerMille, and a Galley reach advice about a land animal from distance and moves alone (Codex's review, round 33).
				# An attack needs an attacker that can attack and both units in one domain. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				bSameDomain = other.getDomainType() == unit.getDomainType()
				# <!-- custom: And an animal cannot enter owned land (CvUnit::canMoveInto, CvUnit.cpp:2687), so it cannot attack a unit there: a Lion beside a Settler on our land showed couldReach and certain death (Codex's review, round 34). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				bTheyCanAttack = bSameDomain and other.canAttack() and not (other.isAnimal() and unit.plot().isOwned())
				bWeCanAttack = bSameDomain and unit.canAttack()
				# <!-- custom: Reach by plots, one per move point: terrain costs and roads are left out, so this is the reach on open ground, which is how the rule may be wrong. (Claude code Opus 5.5) -->
				bReach = bTheyCanAttack and iDistance <= iTheirMoves
				# <!-- custom: getCombatOdds(attacker, defender) is the window's hover odds; both ways, as an animal attacks on its own turn.
				# A unit that cannot fight, such as a Settler or Worker, is captured or killed if attacked, so they win for certain. (Claude code Opus 5.5) -->
				iTheyWin = None
				if bTheyCanAttack:
					if unit.canFight():
						iTheyWin = getCombatOdds(other, unit)
					else:
						iTheyWin = 1000
				iWeWin = None
				if bWeCanAttack:
					iWeWin = getCombatOdds(unit, other)
				bAvoid = (bReach and iTheyWin > 500) or (bWeCanAttack and iWeWin < 700)
				threats.append({"x": plot.getX(), "y": plot.getY(), "type": gc.getUnitInfo(other.getUnitType()).getType(), "animal": bool(other.isAnimal()), "distance": iDistance, "theirMoves": iTheirMoves, "ourMoves": unit.baseMoves(), "theirStrength": other.baseCombatStr(), "ourStrength": unit.baseCombatStr(), "theirDamage": other.getDamage(), "couldReach": bReach, "theyWinPerMille": iTheyWin, "weWinPerMille": iWeWin, "avoid": bAvoid})
	threats.sort(lambda a, b: cmp((not a["avoid"], a["distance"]), (not b["avoid"], b["distance"])))
	return {"unit": unit.getID(), "x": unit.getX(), "y": unit.getY(), "damage": unit.getDamage(), "rule": "avoid where it could attack us this turn on open ground (same domain, distance <= its moves) and would win more often than not (always, against a unit that cannot fight), or where we could attack it and would win under 70% of the time; odds are null for an attack that cannot happen", "threats": threats}


_HELP["meet"] = "Make our team meet other teams, as the WorldBuilder's diplomacy screen can: every living team, or the ones in team (a number or a list). For setting up tests, such as an SAS48 scoreboard that must overflow; changes the game, so the create role. Returns the teams met now. args: team."


def cmd_meet(args):
	# <!-- custom: Was a 'py' loop on 2026-11-20 to fill an SAS48 scoreboard so its scroll buttons appear; the user's rule: what the game can do (here the WorldBuilder) and is likely needed again becomes a command. (Claude code Opus 5.5) -->
	# <!-- custom: Codex's review: CyTeam.meet changes only this machine's game in a network game, and a bad team number late in the list raised after the earlier ones were met; so network games are refused and the list is checked first. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if gc.getGame().isNetworkMultiPlayer():
		raise ValueError("'meet' is for single-player tests; in a network game it would change only this machine's game")
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	targets = args.get("team")
	if targets is None:
		targets = range(gc.getMAX_CIV_TEAMS())
	elif not isinstance(targets, list):
		targets = [targets]
	targets = [int(iTeam) for iTeam in targets]
	for iTeam in targets:
		if iTeam < 0 or iTeam >= gc.getMAX_CIV_TEAMS():
			raise ValueError("no team %d; nothing was met" % iTeam)
	met = []
	for iTeam in targets:
		if iTeam != player.getTeam() and gc.getTeam(iTeam).isAlive() and not team.isHasMet(iTeam):
			team.meet(iTeam, False)
			met.append(iTeam)
	return {"met": met, "hasMet": team.getHasMetCivCount(True)}


_HELP["freetech"] = "Choose a free tech, such as the Oracle's, as the tech chooser does: 'todo' lists the held BUTTONPOPUP_CHOOSETECH with data1 above 0 while one is owed. Without tech: the techs it may be. args: tech (TECH_ type)."


def cmd_freetech(args):
	# <!-- custom: The Oracle's free tech at turn 105 of the fog-on playthrough (2026-11-13) waited in a held choose-tech popup that 'todo' hid, as it left out every choose-tech popup while research was set; 'answer' only drops it.
	# The count of techs owed is the popup's data1. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_activePlayerId())
	if not _pilotGame("isSASPilotChoosingFreeTech").isSASPilotChoosingFreeTech():
		raise ValueError("no free tech is owed now")
	# <!-- custom: Held choosers only: the DLL cannot close one on display, and Codex's review found that a spent displayed chooser becomes usable again with a later award.
	# Holding starts at the load, so one on display is rare; it is then the window's to answer. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	held = [popup for popup in _popups() if popup["state"] == "HELD" and popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0]
	if not held:
		raise ValueError("the free-tech chooser is on display, not held; choose in the window")
	if args.get("tech") is None:
		return {"owed": held[0]["data1"], "techs": [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if player.canResearch(i, False)]}
	iTech = _typedIndex(args["tech"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	# <!-- custom: The DLL now takes the chooser's ID (-1 for the one on display), reads the count from it and removes only that one: closing choosers by type and count could discard a second award (Codex's review).
	# Needs a DLL built after 2026-11-13's round 7. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if not _pilotGame("chooseSASPilotFreeTech").chooseSASPilotFreeTech(iTech, held[0]["id"]):
		raise ValueError("%s cannot be the free tech" % args["tech"])
	return {"chosen": args["tech"]}


def _diploState():
	# <!-- custom: CvDiplomacy.py records what the screen shows in SASPilotScreen, as CyDiplomacy has no getter for the AI's line or the replies; the EXE imports that module itself, so this reads the same state. (Claude code Opus 5.5) -->
	import CvDiplomacy
	state = CvDiplomacy.SASPilotScreen
	# <!-- custom: Declaring war through the screen closed it without passing the branch that clears "open", and the next 'diplo' raised "unidentifiable C++ exception" from CyDiplomacy.atWar on the closed screen (2026-11-13).
	# getWhoTradingWith gives -1 once the screen is closed and the partner while it is open, so it decides. (Claude code Opus 5.5) -->
	if state["open"] and CyDiplomacy().getWhoTradingWith() < 0:
		state["open"] = False
	# <!-- custom: A table opened with a deal on it (contact give=/take=) showed empty "has" columns, unlike Ctrl+clicking the leader, and the AI's counter-offer draws on those columns (pTheirInventory in AI_counterProposeExternal): with nothing of ours to ask for, Pacal gave Navigation for nothing, then asked 65 gold once the columns were filled (2026-11-13, turn 148, same save).
	# So the first read of the open screen fills them as the screen's own trade-proposal reply does, with showAllTrade(True), before any reply can ask for a counter-offer. (Claude code Opus 5.5) -->
	# <!-- custom: Tied to the leader the contact asked for, as Codex's review noted that another leader's screen opening first, an AI's own contact, could have taken a process-wide flag. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	pending = _pendingContact()
	# <!-- custom: Columns are filled only on that leader's trade table, not on another screen of theirs that happened to open first (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if state["open"] and pending is not None and pending[0] == state["who"] and (not pending[1] or _typeOrNone(gc.getDiplomacyInfo, state["aiComment"]) == "AI_DIPLOCOMMENT_TRADING"):
		del _state["contactPending"]
		if pending[1]:
			CyDiplomacy().showAllTrade(True)
	return state


# <!-- custom: A contact SASPilot queued is (leader, fill columns, time) until its screen opens; the EXE opens it on later frames, so 'menu' could load in between (Codex's review).
# Forgotten after CONTACT_PENDING_SECONDS, in case the screen never opens. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
# <!-- custom: Timed with time.clock(), not time.time(): Direct3D sets the process's FPU to single precision, so inside Civ4 time.time() (about 1.79e9) moves in 128-second steps, and 1794652928.0 + 1.5 printed 1794652928.0 (turn 291, 2026-11-14).
# A contact queued by a failed 'price' then never expired and blocked every later contact.
# time.clock() counts from the process start, small enough to stay precise. See KI#1093. (Claude code Opus 5.5) -->
CONTACT_PENDING_SECONDS = 10


def _pendingContact():
	pending = _state.get("contactPending")
	if pending is not None and time.clock() - pending[2] > CONTACT_PENDING_SECONDS:
		del _state["contactPending"]
		return None
	return pending


def _diploToken(state):
	# <!-- custom: Each read of the screen ('diplo', 'todo') gets its own number with a snapshot of what it showed, and 'reply' compares the live screen with the snapshot of the number it names.
	# The first version kept one snapshot per screen count and checked it only when the count had moved on, so a table changed without a new count let a reply chosen for the old deal act on the new one, and a later read could overwrite the snapshot (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iToken = _state.get("diploReads", 0) + 1
	_state["diploReads"] = iToken
	seen = _state.setdefault("diploSeen", {})
	seen[iToken] = _screenContent(state)
	for iOld in [i for i in seen.keys() if i <= iToken - 16]:
		del seen[iOld]
	return iToken


def _screenContent(state):
	# <!-- custom: Codex's round-15 review: the conversation was counted only when a SASPilot read found the screen newly open, so a close and reopen between reads was missed; CvDiplomacy.py now counts each conversation as it begins.
	# The screen's data is compared too, as the join-war and embargo replies take their target from CyDiplomacy.getData() (CvDiplomacy.handleUserResponse), not from the reply. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	diplo = CyDiplomacy()
	return (state.get("conversation", 0), state["who"], state["aiComment"], diplo.getData(), tuple([(r["comment"], r["data1"], r["data2"]) for r in state["responses"]]), tuple([tuple(sorted(item.items())) for item in _diploOffer(diplo.getTheirTradeOffer)]), tuple([tuple(sorted(item.items())) for item in _diploOffer(diplo.getPlayerTradeOffer)]))


# <!-- custom: More items than this are listed up to the limit with a "truncated" entry last, and 'reply' refuses such a screen, since a change past the limit would not show in its comparison (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
DIPLO_OFFER_MAX_ITEMS = 64


def _diploOffer(getter):
	# <!-- custom: CyDiplomacy gives the offer item by item and has no length; an index past the end returns None. (Claude code Opus 5.5) -->
	items = []
	for i in range(DIPLO_OFFER_MAX_ITEMS + 1):
		item = getter(i)
		if item is None:
			break
		if i == DIPLO_OFFER_MAX_ITEMS:
			items.append({"truncated": True})
			break
		entry = {"item": _enumName(TradeableItems, item.ItemType), "data": item.iData}
		szWhat = _tradeDataName(item.ItemType, item.iData)
		if szWhat is not None:
			entry["what"] = szWhat
		items.append(entry)
	return items


# <!-- custom: Trade kinds whose data is an XML entry: (type prefix, count getter, info getter).
# 'trade', 'diplo' and 'propose' each had their own chain of name comparisons for these kinds, and 'propose' resolved the data with the untyped _infoIndex, so TRADE_TECHNOLOGIES:BONUS_IRON would have sent Iron's index as a tech.
# Keyed by the TradeableItems value, as Codex suggested, so the names stay only in replies and arguments. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_TRADE_INFO_TABLES = {
	int(TradeableItems.TRADE_TECHNOLOGIES): ("TECH_", "getNumTechInfos", "getTechInfo"),
	int(TradeableItems.TRADE_RESOURCES): ("BONUS_", "getNumBonusInfos", "getBonusInfo"),
	int(TradeableItems.TRADE_CIVIC): ("CIVIC_", "getNumCivicInfos", "getCivicInfo"),
	int(TradeableItems.TRADE_RELIGION): ("RELIGION_", "getNumReligionInfos", "getReligionInfo"),
}


def _tradeDataName(eKind, iData):
	# <!-- custom: Pacal's first offer through 'diplo' read TRADE_TECHNOLOGIES 2 for 5 (2026-11-13); name the data as 'trade' does.
	# A city keeps its ID, as the giver is not known here. (Claude code Opus 5.5) -->
	table = _TRADE_INFO_TABLES.get(int(eKind))
	if table is None:
		return None
	return _typeOrNone(getattr(gc, table[2]), iData)


def _tradeItemsJson(giver, iReceiver, iKind=-1):
	# <!-- custom: Written in C++ by CyGame.getSASPilotTradeItemsJson since 2026-11-13: the Python loop here, every tradeable item with canTradeItem and getTradeDenial, took 3.5 ms of game time per 'trade' at turn 176 against 0.23 ms for a bare request, the slowest list command measured, and the user prefers the faster version even for a small measured gain.
	# Same entries, in the enum's order. (Claude code Opus 5.5) -->
	return _pilotGame("getSASPilotTradeItemsJson").getSASPilotTradeItemsJson(giver.getID(), iReceiver, iKind)


def _who(iPlayer):
	# <!-- custom: A player as ID, leader name and civilization XML type, as the BBAI and SASGameRecord rows give an ID beside a name: replies such as {"contacted": 2} needed a lookup to tell it was Kublai (the user, 2026-11-14).
	# The ID stays what commands take; the name and type say who it is.
	# Only the ID is unique: with duplicate leaders or civilizations allowed (game options, scenarios, mod-mods), two players can share both name and civilization (the user, 2026-11-14). (Claude code Opus 5.5) -->
	player = gc.getPlayer(iPlayer)
	return {"player": iPlayer, "name": player.getName(), "civ": _typeOrNone(gc.getCivilizationInfo, player.getCivilizationType())}


# <!-- custom: A shared plot counts as strong with a bonus or at least this total yield: Dublin's Fish (5/0/1) is strong, plain coast (1/0/2) and grassland (2/0/0) are not. (Claude code Opus 5.5) -->
SHARED_STRONG_YIELD = 4
# <!-- custom: The city size a site's natural food is checked against. (Claude code Opus 5.5) -->
SITE_FOOD_SIZE = 6


_HELP["look"] = "Turn the window's camera to a plot, a unit or a city, as clicking the minimap does, so a person watching sees what SASPilot acts on. Following is on by default: each 'move' (attacks included) looks at its destination first, and an order on one of our units or cities (mission, command, group, hurry with hurry=, produce, dequeue, citizens with automated=, work, specialist, emphasize); reads never move it looks at it; follow=0 stops that and follow=1 restores it. zoom sets the camera's distance (the EXE's scale; the window starts near 1). args: x, y, unit, city, follow, zoom, player."


def _lookAt(plot):
	CyCamera().JustLookAtPlot(plot)


# <!-- custom: Orders on one of our units or cities that follow=1 looks at first. Following only 'move' left the camera on a far fog-covered city while production, missions and a spy's work went on elsewhere (the user, turn 285, 2026-11-14). (Claude code Opus 5.5) -->
# <!-- custom: Orders only, never reads: 'spy' and 'targets' only list choices, as the action goes through 'mission', so they left the lists after a read-only 'citizens' kept pulling the user's camera back to Dublin while SASPilotWatch.py polled it (2026-11-19); 'hurry' and 'citizens' follow only in their acting forms (_followOrder). (Claude code Opus 5.5) -->
FOLLOW_UNIT_ORDERS = ("mission", "command", "group", "hurry")
FOLLOW_CITY_ORDERS = ("produce", "dequeue", "hurry", "citizens", "work", "specialist", "emphasize")


def _followOrder(name, args):
	# <!-- custom: Only the active player's own units and cities, so the camera never shows a place fog hides; a bad argument is left to the command's own error. (Claude code Opus 5.5) -->
	try:
		plot = None
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if name == "hurry" and args.get("hurry") is None:
			return
		if name in FOLLOW_UNIT_ORDERS and args.get("unit") is not None:
			unit = _unit(args)
			if unit.getOwner() == gc.getGame().getActivePlayer():
				plot = unit.plot()
		# <!-- custom: 'citizens' without automated= only reads the city screen, so it moves no camera: SASPilotWatch.py read each city's citizens every 2 seconds while the user played in the window, and the camera kept jumping back to Dublin (Continents replay, 2026-11-19). (Claude code Opus 5.5) -->
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		elif name in FOLLOW_CITY_ORDERS and args.get("city") is not None and not (name == "citizens" and args.get("automated") is None):
			city = _city(args)
			if city.getOwner() == gc.getGame().getActivePlayer():
				plot = city.plot()
		if plot is not None:
			_lookAt(plot)
	except Exception:
		pass


def cmd_look(args):
	# <!-- custom: The user watches the playthrough in the window, and SASPilot never moved the camera: when Paper was discovered the view was too far from the action to follow it (2026-11-13).
	# The camera changes only what is drawn, not the game. (Claude code Opus 5.5) -->
	if args.get("follow") is not None:
		_state["follow"] = bool(args["follow"])
	if args.get("zoom") is not None:
		CyCamera().SetZoom(float(args["zoom"]))
	plot = None
	# <!-- custom: Under fog, a unit or city of another team would have its place shown and returned, which the window does not tell (Codex's review); a plot by x and y is still allowed, as clicking the minimap is. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iFogTeam = _fogTeam(args)
	if iFogTeam >= 0 and (args.get("unit") is not None or args.get("city") is not None) and gc.getPlayer(_playerId(args)).getTeam() != iFogTeam:
		raise ValueError("with fog on, look at another team's unit or city by its plot instead")
	if args.get("unit") is not None:
		plot = _unit(args).plot()
	elif args.get("city") is not None:
		plot = _city(args).plot()
	elif args.get("x") is not None:
		plot = _plot(args)
	if plot is not None:
		_lookAt(plot)
	result = {"follow": bool(_state.get("follow", True))}
	if plot is not None:
		result["x"] = plot.getX()
		result["y"] = plot.getY()
	return result


_HELP["command"] = "Give a unit a command, e.g. COMMAND_PROMOTION data1=PROMOTION_ type, COMMAND_DELETE confirm=1 (deleting needs confirm, as it cannot be undone), COMMAND_AUTOMATE data1=AUTOMATE_EXPLORE ('unit' lists the automations it can take). args: unit, command, data1, data2, confirm, player."


def cmd_command(args):
	unit = _unit(args)
	eCommand = _enum(CommandTypes, args["command"])
	iData1 = args.get("data1", -1)
	# <!-- custom: 'command command=COMMAND_AUTOMATE data1=AUTOMATE_EXPLORE' first failed with "unknown XML type", as automation types are an enum without XML; the help asked for a number instead. Resolve AUTOMATE_ names on the enum. (Claude code Opus 5.5) -->
	if isinstance(iData1, (str, unicode)) and iData1.startswith("AUTOMATE_"):
		iData1 = int(_enum(AutomateTypes, iData1))
	elif isinstance(iData1, (str, unicode)):
		iData1 = _infoIndex(iData1)
	iData2 = int(args.get("data2", -1))
	# <!-- custom: Deleting a unit cannot be undone, so it needs confirm=1, as the window asks "Are you sure?": at turn 90 of the turn-0 game (2026-11-14) the agent sent COMMAND_DELETE to two new Workers, meaning to clear their mission queues, and one Worker was lost; the other was saved only because it was moving. A queue is cleared with a new order without append. (Claude code Opus 5.5) -->
	# <!-- custom: confirm must be 1 or true: the client passes confirm=no and confirm=False as non-empty strings, which a plain truth test took as yes (Codex's review, round 35). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if eCommand == CommandTypes.COMMAND_DELETE and str(args.get("confirm")).lower() not in ("1", "true"):
		raise ValueError("COMMAND_DELETE removes unit %d for good; send confirm=1 if that is meant. To clear its orders instead, give a new mission without append=1" % unit.getID())
	if not unit.canDoCommand(eCommand, iData1, iData2, False):
		raise ValueError("unit %d cannot do %s (%s, %s) now" % (unit.getID(), args["command"], iData1, iData2))
	# <!-- custom: Looked up again by ID afterwards: upgrading a Spearman to a Bazooka at turn 265 of the modern baseline (2026-11-14) worked, but reading the old object then raised an unidentifiable C++ exception, as an upgrade replaces the unit with a new one, like the used-up Work Boat in cmd_mission.
	# The new unit is the one of the target type with the highest ID on that plot. (Claude code Opus 5.5) -->
	iUnit = unit.getID()
	iOwner = unit.getOwner()
	(iX, iY) = (unit.getX(), unit.getY())
	unit.doCommand(eCommand, iData1, iData2)
	unit = gc.getPlayer(iOwner).getUnit(iUnit)
	if unit is None or unit.isNone() or unit.isDead():
		result = {"unitGone": True}
		if eCommand == CommandTypes.COMMAND_UPGRADE:
			plot = CyMap().plot(iX, iY)
			upgraded = [plot.getUnit(i) for i in range(plot.getNumUnits()) if plot.getUnit(i).getOwner() == iOwner and plot.getUnit(i).getUnitType() == iData1]
			if upgraded:
				upgraded.sort(lambda a, b: cmp(b.getID(), a.getID()))
				result["upgradedTo"] = _unitFull(upgraded[0])
		return result
	return _unitFull(unit)


_HELP["finance"] = "The Domestic Advisor's Finance tab: treasury and net gold per turn, the sliders, gross gold, trade routes split into domestic and foreign, gold from deals with other players, and the expenses with inflation as the tab adds them (unit cost, unit supply, city maintenance, civic upkeep). args: player."


def cmd_finance(args):
	# <!-- custom: The Finance tab breaks gold down into income and expenses, which SASPilot had only as two totals in 'player' (turn 265 of the modern baseline, 2026-11-14, visual pass over the advisors).
	# The expense arithmetic is the tab's own (CvDomesticAdvisor.py), inflation applied per line and once overall. (Claude code Opus 5.5) -->
	import TradeUtil
	player = _player(args)
	iInflation = 100 + player.calculateInflationRate()
	(iDomesticTrade, _iDomesticCount, iForeignTrade, _iForeignCount) = TradeUtil.calculateTradeRoutes(player)
	result = {"treasury": player.getGold(), "goldPerTurn": player.calculateGoldRate(), "commercePercent": dict([(gc.getCommerceInfo(i).getType(), player.getCommercePercent(i)) for i in range(int(CommerceTypes.NUM_COMMERCE_TYPES))]), "grossCommerce": dict([(gc.getCommerceInfo(i).getType(), player.getCommerceRate(CommerceTypes(i))) for i in range(int(CommerceTypes.NUM_COMMERCE_TYPES))]), "domesticTrade": iDomesticTrade, "foreignTrade": iForeignTrade, "goldFromDeals": player.getGoldPerTurn(), "inflationPercent": iInflation - 100}
	result["expenses"] = {"unitCost": (player.calculateUnitCost() * iInflation + 50) / 100, "unitSupply": (player.calculateUnitSupply() * iInflation + 50) / 100, "cityMaintenance": (player.getTotalMaintenance() * iInflation + 50) / 100, "civicUpkeep": (player.getCivicUpkeep([], False) * iInflation + 50) / 100, "total": player.calculateInflatedCosts()}
	return result


_HELP["domestic"] = "The Domestic Advisor's overview: one row per city with population, happiness and health margins (negative is a problem), food surplus, production, commerce by type, culture and its next level, Great People progress and rate, maintenance, trade route commerce, what it builds and in how many turns. args: player."


def cmd_domestic(args):
	# <!-- custom: The Domestic Advisor shows every city's state at a glance, while 'cities' gave only population and queue and 'city' one city at a time, so judging fifteen cities took fifteen requests (visual pass, 2026-11-14). (Claude code Opus 5.5) -->
	player = _player(args)
	rows = []
	for city in _cities(player):
		queue = _cityBrief(city)["queue"]
		row = {"id": city.getID(), "name": city.getName(), "population": city.getPopulation(), "happyMargin": city.happyLevel() - city.unhappyLevel(0), "healthMargin": city.goodHealth() - city.badHealth(False), "food": city.foodDifference(True), "production": city.getYieldRate(YieldTypes.YIELD_PRODUCTION), "commerce": dict([(gc.getCommerceInfo(i).getType()[9:], city.getCommerceRate(CommerceTypes(i))) for i in range(int(CommerceTypes.NUM_COMMERCE_TYPES))]), "culture": city.getCulture(city.getOwner()), "cultureNextLevel": city.getCultureThreshold(), "greatPeopleProgress": city.getGreatPeopleProgress(), "greatPeopleRate": city.getGreatPeopleRate(), "maintenance": city.getMaintenanceTimes100() / 100, "tradeCommerce": city.getTradeYield(YieldTypes.YIELD_COMMERCE), "building": (queue and [queue[0]] or [None])[0], "turns": city.getProductionTurnsLeft()}
		# <!-- custom: Coastal, as the Domestic Advisor's columns mark it (isCoastal with the game's MIN_WATER_SIZE_FOR_OCEAN), with an empire summary below: the user asked at turn 156 of the turn-0 game (2026-11-14) how many coastal cities we have, since a Harbor or Lighthouse pays per coastal city, and which cities need health or happiness, as the advisor's overview shows at a glance. (Claude code Opus 5.5) -->
		row["coastal"] = bool(city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()))
		# <!-- custom: More of the advisor's overview pages, as the user asked at turn 157 of the turn-0 game (2026-11-14): defense and garrison and the revolt chance from page 1 (advc.ctr's column; Orleans showed 9.2% to Pericles's culture at turn 139, which SASPilot learned only from a turn message), food stored against the growth threshold from page 2, war weariness from page 3, and the turn founded from page 4.
		# Revolt in per mille, an integer, as floats lose precision inside Civ4 (KI#1093). (Claude code Opus 5.5) -->
		row["defensePercent"] = city.getDefenseModifier(False)
		row["garrison"] = city.plot().getNumDefenders(city.getOwner())
		row["revoltPerMille"] = int(1000 * city.revoltProbability())
		row["foodStored"] = city.getFood()
		row["growthThreshold"] = city.growthThreshold()
		row["warWearinessPercent"] = city.getWarWearinessModifier()
		row["foundedTurn"] = city.getGameTurnFounded()
		# <!-- custom: The religions column of the Domestic Advisor, the one column this overview lacked (checked against CvDomesticAdvisor.py, 2026-11-15); the holy cities with them. (Claude code Opus 5.5) -->
		row["religions"] = [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if city.isHasReligion(i)]
		row["holyCityOf"] = [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if city.isHolyCityByType(i)]
		rows.append(row)
	summary = {"cities": len(rows), "coastal": len([r for r in rows if r["coastal"]]), "unhealthy": [r["name"] for r in rows if r["healthMargin"] < 0], "atHealthCap": [r["name"] for r in rows if r["healthMargin"] == 0], "unhappy": [r["name"] for r in rows if r["happyMargin"] < 0], "atHappyCap": [r["name"] for r in rows if r["happyMargin"] == 0], "starving": [r["name"] for r in rows if r["food"] < 0]}
	return {"greatPeopleThreshold": player.greatPeopleThreshold(False), "summary": summary, "cities": rows}


_HELP["greatpeople"] = "Great People planning: the threshold for the next one; per city with points, its progress, points per turn, rate modifier, turns left at that rate, and the mix of Great Person types its points came from, with each type's chance (as the city screen's Great People bar shows); and the techs whose first discoverer gets a free Great Person that no team has yet, with whether we can research each now and in how many turns. args: player."


def cmd_greatpeople(args):
	# <!-- custom: The user wanted to plan Great People while watching the bar (2026-11-14): 'domestic' gave each city's progress and rate but not which type it would bring, how soon, or which first-discovery techs are still open.
	# The chance per type is its share of the city's points, which is how CvCity::createGreatPeople picks one. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	_requireOwnTeamUnderFog(args, player, "Great People progress")
	iThreshold = player.greatPeopleThreshold(False)
	cities = []
	(city, iterator) = player.firstCity(False)
	while city:
		iProgress = city.getGreatPeopleProgress()
		iRate = city.getGreatPeopleRate()
		if iProgress > 0 or iRate > 0:
			mix = []
			for iUnit in range(gc.getNumUnitInfos()):
				iPoints = city.getGreatPeopleUnitProgress(iUnit)
				iUnitRate = city.getGreatPeopleUnitRate(iUnit)
				if iPoints > 0 or iUnitRate > 0:
					mix.append({"unit": gc.getUnitInfo(iUnit).getType(), "points": iPoints, "baseRate": iUnitRate})
			iTotal = sum([m["points"] for m in mix])
			for m in mix:
				# <!-- custom: In hundredths of a percent: Python 2.4's round() still printed 37.99 as 37.990001678 in the JSON. (Claude code Opus 5.5) -->
				m["chancePctX100"] = (iTotal > 0 and [m["points"] * 10000 / iTotal] or [0])[0]
			mix.sort(lambda a, b: cmp(b["points"], a["points"]))
			iTurns = None
			if iRate > 0:
				iTurns = max(0, (iThreshold - iProgress + iRate - 1) / iRate)
			cities.append({"id": city.getID(), "name": city.getName(), "progress": iProgress, "rate": iRate, "rateModifierPct": city.getTotalGreatPeopleRateModifier(), "turnsLeft": iTurns, "mix": mix})
		(city, iterator) = player.nextCity(iterator, False)
	cities.sort(lambda a, b: cmp(a["turnsLeft"] is None, b["turnsLeft"] is None) or cmp(a["turnsLeft"], b["turnsLeft"]))
	# <!-- custom: A free Great Person already claimed is announced to every player in game, so listing only unclaimed techs gives no more than a person at the window learns. (Claude code Opus 5.5) -->
	team = gc.getTeam(player.getTeam())
	firstFree = []
	for iTech in range(gc.getNumTechInfos()):
		info = gc.getTechInfo(iTech)
		iClass = info.getFirstFreeUnitClass()
		if iClass < 0 or team.isHasTech(iTech) or gc.getGame().countKnownTechNumTeams(iTech) > 0:
			continue
		# <!-- custom: As CvPlayer::getTechFreeUnit, which the tech hover uses (Codex's review): no reward where this civilization has no unit of the class, or for a spy unit with espionage off. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		iUnit = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(iClass)
		if iUnit < 0 or (gc.getUnitInfo(iUnit).getEspionagePoints() > 0 and gc.getGame().isOption(GameOptionTypes.GAMEOPTION_NO_ESPIONAGE)):
			continue
		bCan = player.canResearch(iTech, False)
		row = {"tech": info.getType(), "freeUnit": gc.getUnitInfo(iUnit).getType(), "canResearchNow": bool(bCan)}
		if bCan:
			row["turns"] = player.getResearchTurnsLeft(iTech, True)
		firstFree.append(row)
	return {"threshold": iThreshold, "created": player.getGreatPeopleCreated(), "cities": cities, "firstDiscoveryFree": firstFree}


_HELP["battles"] = "The Military Advisor's Battles tab: our battles as the save records them, newest first, each with its turn, our side's outcome (won, lost, retreated, or theirRetreat), the winner and loser (attacker and defender for a retreat) with their unit types, the plot with its terrain, feature, hill or peak and whether it was a city defended or captured, the attacker's and defender's strength at the start, their maximum and their strength at the end, times 100 (strengthX100), a unit captured after it, and each side's experience and whether it had a Great General. since= a turn, limit= rows (default 50). args: player, since, limit."


# <!-- custom: The rows' slots as SASBattleHistory writes them (recordCombatResult, recordCombatRetreat, _getEntryWithCapture, _getEntryWithPlotContext, _getEntryWithUnitContext); older rows are shorter, so a missing slot gives no field. (Claude code Opus 5.5) -->
_BATTLE_CITY_CONTEXT = {0: None, 1: "defended", 2: "captured"}


def _battleSlot(entry, i):
	if len(entry) > i:
		return entry[i]
	return None


def _battleRow(entry, iPlayer):
	# <!-- custom: Slots through _battleSlot rather than a nested function, as Civ4's Python code avoids closures (AGENTS.md). (Claude code Opus 5.5) -->
	bRetreat = SASBattleHistory.isRetreatEntry(entry)
	if bRetreat:
		szOutcome = _battleSlot(entry, 1) == iPlayer and "retreated" or "theirRetreat"
	else:
		szOutcome = _battleSlot(entry, 1) == iPlayer and "won" or "lost"
	row = {"turn": _battleSlot(entry, 0), "outcome": szOutcome, "x": _battleSlot(entry, 5), "y": _battleSlot(entry, 6)}
	if bRetreat:
		row.update({"attacker": _battleSlot(entry, 1), "defender": _battleSlot(entry, 2), "attackerUnit": _typeOrNone(gc.getUnitInfo, _battleSlot(entry, 3)), "defenderUnit": _typeOrNone(gc.getUnitInfo, _battleSlot(entry, 4))})
	else:
		row.update({"winner": _battleSlot(entry, 1), "loser": _battleSlot(entry, 2), "winnerUnit": _typeOrNone(gc.getUnitInfo, _battleSlot(entry, 3)), "loserUnit": _typeOrNone(gc.getUnitInfo, _battleSlot(entry, 4))})
	# <!-- custom: A retreat always records end strength, even when there was no matching combat callback for start/max strength.
	# The writer zero-pads that missing block.
	# Older lethal rows can have start/max without end strength.
	# Report each block only when recorded, in the game's units (1430 is 14.3). See KI#1110. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	strength = {}
	if _battleSlot(entry, 12):
		if not bRetreat:
			row.update({"attacker": entry[7], "defender": entry[8]})
		strength.update({"attackerStart": entry[9], "attackerMax": entry[10], "defenderStart": entry[11], "defenderMax": entry[12]})
	if bRetreat or (strength and len(entry) >= 18):
		strength.update({"attackerEnd": entry[16], "defenderEnd": entry[17]})
	if strength:
		row["strengthX100"] = strength
	if _battleSlot(entry, 15):
		row["captured"] = {"by": _battleSlot(entry, 13), "unit": _typeOrNone(gc.getUnitInfo, _battleSlot(entry, 14)), "count": _battleSlot(entry, 15)}
	(iTerrain, iFeature, iHillPeak, iCity) = SASBattleHistory.getPlotContext(entry)
	if iTerrain is not None and iTerrain >= 0:
		row["terrain"] = _typeOrNone(gc.getTerrainInfo, iTerrain)
		row["feature"] = _typeOrNone(gc.getFeatureInfo, iFeature)
		row["hillOrPeak"] = _typeOrNone(gc.getTerrainInfo, iHillPeak)
		row["city"] = _BATTLE_CITY_CONTEXT.get(iCity)
	(iAttackerXP, bAttackerGG, iDefenderXP, bDefenderGG) = SASBattleHistory.getUnitContext(entry)
	if iAttackerXP >= 0 or iDefenderXP >= 0:
		experience = {}
		if iAttackerXP >= 0:
			experience.update({"attacker": iAttackerXP, "attackerGreatGeneral": bool(bAttackerGG)})
		if iDefenderXP >= 0:
			experience.update({"defender": iDefenderXP, "defenderGreatGeneral": bool(bDefenderGG)})
		row["experience"] = experience
	return row


def cmd_battles(args):
	# <!-- custom: The 2026-11-22 tab audit found no command for the Battles tab, which an agent at war needs (which units won where, against what), and reading its 143-row table through the UI cost a screen per look.
	# Under fog, refuse another team's history even in a role that can select that team. See KI#1110. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "battle history")
	iPlayer = player.getID()
	iSince = int(args.get("since", -1))
	iLimit = int(args.get("limit", 50))
	if iLimit < 0:
		raise ValueError("limit must be nonnegative")
	entries = [entry for entry in SASBattleHistory.getEntriesForPlayer(iPlayer) if len(entry) >= 7 and entry[0] >= iSince]
	entries.reverse()
	return {"player": iPlayer, "total": len(entries), "battles": [_battleRow(entry, iPlayer) for entry in entries[:iLimit]]}


_HELP["environment"] = "The World Advisor's Environment tab: global warming's severity (low, medium or high, as the tab's title), the player's pollution by source (population, buildings, resources, power) and in total, its offsets, impact and sustainability threshold, the world's pollution, offsets, threshold and change rate, the player's share of the responsibility, the warming index, the expected events per turn (as the tab's one-decimal text, exact with the Debug Mode values), the events so far and the player's anger from warming (from 2%, as the tab). As the tab, the severity rating, the warming chances and, before the first event, the responsibility are given in Debug Mode only. args: player."


def cmd_environment(args):
	# <!-- custom: The 2026-11-22 tab audit left world/ENVIRONMENT with no command.
	# Read through CvWorldAdvisorScreen.collectEnvironmentData, split from the tab's drawing for this on 2026-11-28, on a copy of the screen set to the player, so the change rate, responsibility and expected events come from the tab's own formulas. (Claude code Opus 5.5) -->
	import copy
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "pollution")
	view = copy.copy(CvScreensInterface.worldAdvisorScreen)
	view.iActivePlayer = player.getID()
	data = view.collectEnvironmentData()
	# <!-- custom: The tab's Debug Mode-only values only when the request's fog is off too, as for 'bfc' (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	bDebug = gc.getGame().isDebugMode() and _fogTeam(args) < 0
	# <!-- custom: The tab's own thresholds for its LOW, MEDIUM and HIGH title (advc.137). (Claude code Opus 5.5) -->
	szSeverity = "high"
	if data["severityRating"] < 30:
		szSeverity = "low"
	elif data["severityRating"] < 75:
		szSeverity = "medium"
	result = {"player": player.getID(), "severity": szSeverity, "pollution": {"population": data["population"], "buildings": data["buildings"], "resources": data["resources"], "power": data["power"], "total": data["localPollution"]}, "offsets": data["localDefence"], "impact": data["localPollution"] - data["localDefence"], "threshold": data["localThreshold"], "world": {"pollution": data["globalPollution"], "offsets": data["globalDefence"], "threshold": data["threshold"], "changeRate": max(0, data["changeRate"])}, "warmingIndex": data["globalWarmingIndex"], "expectedEventsPerTurn": u"%0.1f" % data["expectedEvents"]}
	# <!-- custom: The tab shows one decimal, and the exact value is the hidden warming chance times a known factor (72 gave 1.44 at Normal speed), so the exact one only with the Debug Mode values (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: The tab shows the anger row from 2% only; the command first gave 1, which the tab hides (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if data["gwPercentAnger"] >= 2:
		result["angerPercent"] = data["gwPercentAnger"]
	if data["gwEventTally"] >= 0:
		result["events"] = data["gwEventTally"]
	if data["gwEventTally"] >= 0 or bDebug:
		result["responsibilityPercent"] = data["responsibility"]
	if bDebug:
		result["severityRating"] = data["severityRating"]
		result["warmingChances"] = data["globalWarmingChances"]
		result["expectedEventsPerTurn"] = data["expectedEvents"]
	return result


_HELP["statistics"] = "The Info Screen's Statistics tab: minutes played, the player's cities built and razed, religions founded, and per unit type built, killed, lost and current, per building type built; zeros left out. args: player."


def cmd_statistics(args):
	# <!-- custom: The 2026-11-22 tab audit left info/STATISTICS with no command.
	# Read through CvInfoScreen.collectStatsData, split from the tab's drawing for this on 2026-11-28, on a copy of the screen set to the player, as 'timeline' does. (Claude code Opus 5.5) -->
	import copy
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "statistics")
	view = copy.copy(CvScreensInterface.infoScreen)
	view.iActivePlayer = player.getID()
	(iCitiesBuilt, iCitiesRazed, iReligionsFounded, unitsBuilt, unitsKilled, unitsLost, buildingsBuilt, unitsCurrent) = view.collectStatsData()
	units = []
	for i in range(len(unitsBuilt)):
		if unitsBuilt[i] or unitsKilled[i] or unitsLost[i] or unitsCurrent[i]:
			units.append({"type": gc.getUnitInfo(i).getType(), "built": unitsBuilt[i], "killed": unitsKilled[i], "lost": unitsLost[i], "current": unitsCurrent[i]})
	buildings = [{"type": gc.getBuildingInfo(i).getType(), "built": buildingsBuilt[i]} for i in range(len(buildingsBuilt)) if buildingsBuilt[i]]
	return {"player": player.getID(), "minutesPlayed": gc.getGame().getMinutesPlayed(), "citiesBuilt": iCitiesBuilt, "citiesRazed": iCitiesRazed, "religionsFounded": iReligionsFounded, "units": units, "buildings": buildings}


_HELP["military"] ="The Military Advisor's summary as decisions need it: unit counts by domain, military and civilian; where they stand (own cities, own land, neutral land, enemy land, other land); the wounded by ID; every unit that can upgrade now with its targets and cheapest cost, and the total; Great General progress and generals created; cities with walls and castles. args: player."


def cmd_military(args):
	# <!-- custom: From a visual pass over SAS's Military Advisor Summary at turn 265 of the modern baseline (2026-11-14): SASPilot had the unit list but not what it adds up to, and the Summary's "Upgradeable: 24, total cost 2574" gave no unit IDs to act on.
	# This lists them, cheapest target first; canUpgrade is the game's own check, so an SAS tech gate such as the Rifleman's Military Tradition is respected. (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	domains = {}
	where = {"ownCity": 0, "ownLand": 0, "neutral": 0, "enemyLand": 0, "otherLand": 0}
	wounded = []
	upgradeable = []
	iMilitary = 0
	(unit, it) = player.firstUnit(False)
	while unit:
		szDomain = _enumName(DomainTypes, unit.getDomainType())
		domains[szDomain] = domains.get(szDomain, 0) + 1
		if unit.canFight():
			iMilitary = iMilitary + 1
		plot = unit.plot()
		iOwner = plot.getOwner()
		if iOwner == player.getID() and plot.isCity():
			where["ownCity"] = where["ownCity"] + 1
		elif iOwner == player.getID():
			where["ownLand"] = where["ownLand"] + 1
		elif iOwner < 0:
			where["neutral"] = where["neutral"] + 1
		elif team.isAtWar(gc.getPlayer(iOwner).getTeam()):
			where["enemyLand"] = where["enemyLand"] + 1
		else:
			where["otherLand"] = where["otherLand"] + 1
		if unit.getDamage() > 0:
			wounded.append({"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "damage": unit.getDamage(), "x": unit.getX(), "y": unit.getY()})
		targets = [(unit.upgradePrice(i), gc.getUnitInfo(i).getType()) for i in range(gc.getNumUnitInfos()) if unit.canUpgrade(i, False)]
		if targets:
			targets.sort()
			upgradeable.append({"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "to": [t[1] for t in targets], "cheapest": targets[0][0]})
		(unit, it) = player.nextUnit(it, False)
	defenses = {}
	for szClass in ("BUILDINGCLASS_WALLS", "BUILDINGCLASS_CASTLE"):
		iClass = _findOptionalInfoType(szClass)
		if iClass >= 0:
			iBuilding = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationBuildings(iClass)
			defenses[szClass[14:]] = len([city for city in _cities(player) if iBuilding >= 0 and city.getNumBuilding(iBuilding) > 0])
	# <!-- custom: Generals created too: checking why a turn-301 autoplay save showed "0 / 29" took a 'py' snippet three times (2026-11-21). (Claude code Opus 5.5) -->
	return {"units": player.getNumUnits(), "military": iMilitary, "byDomain": domains, "where": where, "wounded": wounded, "upgradeable": upgradeable, "upgradeTotalCost": sum([u["cheapest"] for u in upgradeable]), "greatGeneralProgress": player.getCombatExperience(), "greatGeneralThreshold": player.greatPeopleThreshold(True), "greatGeneralsCreated": player.getGreatGeneralsCreated(), "cities": player.getNumCities(), "citiesWith": defenses}


def _attitudeCount(iFrom, iTo):
	# <!-- custom: The number the Glance tab shows: the sum of the hover's modifiers, as AttitudeUtil.getAttitudeCount reads them, since AI_getAttitudeVal is not exposed to Python. (Claude code Opus 5.5) -->
	iTotal = 0
	for szLine in _plainText(CyGameTextMgr().getAttitudeString(iFrom, iTo)).split(u"\n"):
		match = re.match(u"^\\s*([-+][0-9]+)\\s?:", szLine)
		if match:
			iTotal += int(match.group(1))
	return iTotal


_HELP["espionage"] ="The espionage screen: per team met, the points gathered against it, the spending weight given to it and its counterespionage against us. With team and weight, set that weight, as the screen's +/- buttons do. args: team, weight, player."


def cmd_espionage(args):
	# <!-- custom: SASPilot had nothing for espionage (2026-11-14): no points per rival, no spending weights, which the Espionage Advisor sets with its +/- buttons. (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	if args.get("team") is not None:
		iTeam = int(args["team"])
		if iTeam < 0 or iTeam >= gc.getMAX_CIV_TEAMS() or iTeam == player.getTeam() or not team.isHasMet(iTeam):
			raise ValueError("team %d is not a team the player has met" % iTeam)
		if args.get("weight") is None:
			raise ValueError("team needs weight, the new spending weight")
		player.changeEspionageSpendingWeightAgainstTeam(iTeam, int(args["weight"]) - player.getEspionageSpendingWeightAgainstTeam(iTeam))
	teams = []
	for iTeam in range(gc.getMAX_CIV_TEAMS()):
		if iTeam == player.getTeam() or not gc.getTeam(iTeam).isAlive() or not team.isHasMet(iTeam):
			continue
		teams.append({"team": iTeam, "leaders": [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() == iTeam], "points": team.getEspionagePointsAgainstTeam(iTeam), "weight": player.getEspionageSpendingWeightAgainstTeam(iTeam), "theirCounterespionageTurns": gc.getTeam(iTeam).getCounterespionageTurnsLeftAgainstTeam(player.getTeam())})
	return {"teams": teams}


_HELP["spy"] = "What a spy could do where it stands, as the window's espionage popups offer it: the plot's owner (target), our espionage points against that team, and missions: each mission with its cost, and for a mission with a target (a building, unit, project, tech, civic or religion), each target with its cost. Run one with 'mission' as the window's click does: mission=MISSION_ESPIONAGE data1=<mission> data2=<data>. args: unit, player."


def cmd_spy(args):
	# <!-- custom: In C++, as the costs depend on the spy, which the Python bindings do not pass; see getSASPilotEspionageJson (2026-11-14). (Claude code Opus 5.5) -->
	unit = _unit(args)
	_requireOwnTeamUnderFog(args, gc.getPlayer(unit.getOwner()), "a spy's missions")
	missions = RawJson(_pilotGame("getSASPilotEspionageJson").getSASPilotEspionageJson(unit.getOwner(), unit.getID()))
	# <!-- custom: A spy sent to Madrid at turn 274 of the modern baseline (2026-11-14) arrived after Kublai had captured it, and 'spy' gave a bare [] there: the 40 points held against Kublai paid for no mission, as the window's popup lists only those it could.
	# Name the plot's owner and the points against that team, so an empty list says why. (Claude code Opus 5.5) -->
	iOwner = unit.plot().getOwner()
	if iOwner < 0:
		return {"target": None, "points": None, "missions": missions}
	iTargetTeam = gc.getPlayer(iOwner).getTeam()
	reply = {"target": iOwner, "targetName": gc.getPlayer(iOwner).getName(), "points": gc.getTeam(unit.getTeam()).getEspionagePointsAgainstTeam(iTargetTeam), "missions": missions}
	# <!-- custom: At Oporto on turn 283 (2026-11-14), with 901 points against Roosevelt, 'spy' still gave no missions: the spy had moved that turn, and CvUnit::canEspionage refuses a spy that moved or attacked this turn, or one the target team can see.
	# 'blocked' names the first such reason, so the agent waits a turn instead of guessing. (Claude code Opus 5.5) -->
	if unit.hasMoved():
		reply["blocked"] = "moved this turn; a spy can act only on a turn it has not moved"
	elif unit.isMadeAttack():
		reply["blocked"] = "attacked this turn"
	elif not unit.isInvisible(iTargetTeam, False):
		# <!-- custom: Under fog, naming the detection would tell more than the window, which only greys the button (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if _fogTeam(args) >= 0:
			reply["blocked"] = "no mission can start here this turn"
		else:
			reply["blocked"] = "the target team can see this spy"
	return reply


_HELP["endturn"] = "End the active player's turn, as the End Turn button does once nothing waits for orders."


def cmd_endturn(args):
	player = gc.getPlayer(_activePlayerId())
	if not player.isTurnActive():
		raise ValueError("it is not the active player's turn")
	# <!-- custom: In the fog-on playthrough (2026-11-13) three turns ended with no research set, as 'endturn' said nothing about what still waited.
	# It still ends the turn, as Ctrl+Enter does in the window, but reports in 'skipped' what 'todo' listed, so a caller sees what it left. (Claude code Opus 5.5) -->
	# <!-- custom: Moctezuma's war declaration at turn 148 stayed open on the diplomacy screen while three 'endturn' calls went through, each reporting it under 'skipped' (2026-11-13); in the window that screen covers the End Turn button until it is answered, so 'endturn' refuses as well. (Claude code Opus 5.5) -->
	if _diploState()["open"]:
		# <!-- custom: The refusal carries the screen's leader, comment and replies with a screen token, so its options are seen once and answered at once: at Sitting Bull's first contact (Continents game, turn 32, 2026-11-19) it said only "see 'diplo'", and the user suggested checking the options at every meeting. (Claude code Opus 5.5) -->
		screen = _command("diplo")({})
		szReplies = "; ".join(["%d %s" % (reply["n"], reply["comment"]) for reply in screen["replies"]])
		raise ValueError(("a diplomacy screen waits for an answer: %s (player %d), %s; replies: %s; answer with 'reply n=N screen=%d'" % (screen["whoName"], screen["who"], screen["aiComment"], szReplies, screen["screen"])).encode("ascii", "replace"))
	# <!-- custom: A contact SASPilot queued opens on later frames, so an 'endturn' right after it could slip past the check above (Codex's review); refused as 'menu' does. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _pendingContact() is not None:
		raise ValueError("a contact is queued and its screen has not opened yet; read 'diplo' once it does")
	skipped = cmd_todo({})
	del skipped["turnActive"]
	for key in skipped.keys():
		if not skipped[key]:
			del skipped[key]
	CyMessageControl().sendTurnComplete()
	return {"gameTurn": gc.getGame().getGameTurn(), "skipped": skipped}


_HELP["turn"] = "What a person sees at the start of a turn: turn and year, what waits for orders (as 'todo') and the messages since the previous turn (as 'messages'). 'SASPilotClient.py endturn' prints it for the new turn. args: player."


def cmd_turn(args):
	# <!-- custom: Playing turn by turn took 'endturn', 'todo' and 'messages' each time (fog-on playthrough, 2026-11-13); one request gives the three, as the window shows them together when a turn starts. (Claude code Opus 5.5) -->
	game = gc.getGame()
	# <!-- custom: Messages are stamped with the turn they were made in, and those made as a turn starts carry that turn, so "Pacal II will trade Agriculture, Mysticism" showed in the digests of turns 41 and 42 (fog-on playthrough, 2026-11-13).
	# The digest now leaves out messages it already showed; 'messages' itself still lists everything since the turn asked for. (Claude code Opus 5.5) -->
	# <!-- custom: Kept per load: the memory survived loading a save, so replaying the turn-115 sequence a second time in the same client gave a turn-116 digest without its four messages, already shown in the first run's game (2026-11-13). (Claude code Opus 5.5) -->
	if _state.get("turnMessagesLoad") != _state.get("loads"):
		_state["turnMessagesShown"] = {}
		_state["turnMessagesLoad"] = _state.get("loads")
	shown = _state.setdefault("turnMessagesShown", {})
	iPlayer = _playerId(args)
	seen = shown.get(iPlayer, [])
	messages = []
	for message in cmd_messages(args):
		key = (message["turn"], message["text"], message["x"], message["y"])
		if key not in seen:
			messages.append(message)
	shown[iPlayer] = [(message["turn"], message["text"], message["x"], message["y"]) for message in cmd_messages({"player": iPlayer, "since": game.getGameTurn() - 2})]
	result = {"gameTurn": game.getGameTurn(), "gameYear": game.getGameTurnYear(), "messages": messages}
	if iPlayer == game.getActivePlayer() and hasattr(game, "getSASPilotPathJson"):
		result["notices"] = _takeNotices()
	result["todo"] = cmd_todo(args)
	# <!-- custom: The reminders come with every turn's digest, so an agent ending turns sees them without asking (the user, 2026-11-14). (Claude code Opus 5.5) -->
	result["reminders"] = cmd_reminders(args)["reminders"]
	# <!-- custom: The scoreboard's power ratios in every turn's digest: the user advised watching military power every turn, as it decides much of the game and our rivals' ratios fell from 1.2-2.2 to 0.9-1.5 times ours over turns 90 to 106 of the turn-0 game (2026-11-14).
	# Per met player whose ratio the scoreboard shows (canSeeDemographics), their power against ours in per mille, as in 'relations'. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	iFogTeam = _fogTeam(args)
	power = []
	if player.getPower() > 0:
		for iOther in range(gc.getMAX_CIV_PLAYERS()):
			other = gc.getPlayer(iOther)
			if iOther == player.getID() or not other.isAlive() or not gc.getTeam(player.getTeam()).isHasMet(other.getTeam()):
				continue
			if iFogTeam < 0 or player.canSeeDemographics(iOther):
				power.append({"player": iOther, "name": other.getName(), "ratioPerMille": other.getPower() * 1000 / player.getPower()})
	result["power"] = power
	return result


def _isNotice(popup):
	# <!-- custom: A held popup that only informs: the "feat" popups of CvAdvisorUtils.py, such as "you have trained your first Archery unit", whose callback only opens an advisor or does nothing.
	# One came at turn 60 of the fog-on playthrough (2026-11-13), listed in 'todo' as waiting while 'answer' could not take it, as it is a Python popup. (Claude code Opus 5.5) -->
	if popup["state"] == "HELD" and popup["onClicked"] == "featAccomplishedOnClickedCallback":
		return True
	# <!-- custom: A plain text popup, such as the Apostolic Palace's election result at turn 138 of the fog-on playthrough (2026-11-13): its only button is OK, and CvDLLButtonPopup::OnOkClicked does nothing for it, so it waited in 'todo' with no button 'answer' could take. (Claude code Opus 5.5) -->
	if popup["state"] == "HELD" and popup["type"] == "BUTTONPOPUP_TEXT":
		return True
	# <!-- custom: The tech splash, era and wonder movie screens only show what happened.
	# The hold lets screens through, and AdvCiv's Minimize Pop-Ups kept them queued until every unit had moved, so twelve had piled up by turn 97 of the fog-on playthrough (2026-11-13); closing one diplomacy screen brought up the Animal Husbandry splash of turn 14.
	# Queued ones are notices; one already on display stays until clicked in the window. (Claude code Opus 5.5) -->
	return popup["state"] == "QUEUED" and popup["type"] == "BUTTONPOPUP_PYTHON_SCREEN" and popup["text"] in _INFO_SCREENS


_INFO_SCREENS = ("showTechSplash", "showEraMovie", "showWonderMovie")


def _closeInfoScreens(bClose=True):
	# <!-- custom: A tech splash on display kept the diplomacy screen from opening at turn 97 of the fog-on playthrough (2026-11-13): 'contact' opened nothing until it was closed, and a tech traded right after showed its splash at once.
	# These screens only inform, so close one on display as its Continue or OK button does, by hiding it under the name it was shown with (CvTechSplashScreen.py, CvWonderMovieScreen.py, CvEraMovieScreen.py), and report it as a notice. (Claude code Opus 5.5) -->
	import CvScreensInterface
	import CvScreenEnums
	closed = []
	splash = CvScreensInterface.techSplashScreen
	if getattr(splash, "iTech", None) is not None and splash.getScreen().isActive():
		closed.append(u"Tech screen: %s" % _typeOrNone(gc.getTechInfo, splash.iTech))
		if bClose:
			splash.getScreen().hideScreen()
	wonder = CvScreensInterface.wonderMovie
	if getattr(wonder, "iWonderId", None) is not None:
		screen = CyGInterfaceScreen("WonderMovieScreen" + str(wonder.iWonderId), CvScreenEnums.WONDER_MOVIE_SCREEN)
		if screen.isActive():
			closed.append(u"Wonder or religion movie: %d" % wonder.iWonderId)
			if bClose:
				screen.hideScreen()
	for iEra in range(gc.getNumEraInfos()):
		screen = CyGInterfaceScreen("EraMovieScreen" + str(iEra), CvScreenEnums.ERA_MOVIE_SCREEN)
		if screen.isActive():
			closed.append(u"Era movie: %s" % gc.getEraInfo(iEra).getType())
			if bClose:
				screen.hideScreen()
	return closed


def _noticeText(popup):
	# <!-- custom: A feat's own text; for an info screen, what it was about, from the data the DLL (CvTeam.cpp, CvPlayer.cpp) and CvEventManager.py give it. (Claude code Opus 5.5) -->
	szText = popup["text"]
	if szText == "showTechSplash":
		return u"Tech screen: %s" % _typeOrNone(gc.getTechInfo, popup["data1"])
	if szText == "showEraMovie":
		return u"Era movie: %s" % _typeOrNone(gc.getEraInfo, popup["data1"])
	if szText == "showWonderMovie":
		# <!-- custom: data3 is 0 for a wonder, 1 for a religion founded and 2 for a project (CvEventManager.py).
		# The first version read every one as a building, and the Hinduism movie came out as "Wonder movie: BUILDING_CITY_CENTER". (Claude code Opus 5.5) -->
		if popup["data3"] == 1:
			return u"Religion movie: %s" % _typeOrNone(gc.getReligionInfo, popup["data1"])
		if popup["data3"] == 2:
			return u"Project movie: %s" % _typeOrNone(gc.getProjectInfo, popup["data1"])
		return u"Wonder movie: %s" % _typeOrNone(gc.getBuildingInfo, popup["data1"])
	return _plainText(szText)


def _takeNotices():
	# <!-- custom: Gives each notice's text once and drops it, as a person reads it and clicks OK. (Claude code Opus 5.5) -->
	# <!-- custom: Dropped one by one with dropSASPilotPopup: a held notice by its ID, a queued one by type, data1, data3 and text.
	# The first version went through closeSASPilotPopups, which matches only type and data1 and runs killAll, and killAll recalls and relaunches the popups on display (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	notices = _closeInfoScreens()
	for popup in _popups():
		if not _isNotice(popup):
			continue
		if _popupGame().dropSASPilotPopup(popup["id"], int(_enum(ButtonPopupTypes, popup["type"])), popup["data1"], popup["data3"], popup["text"]):
			notices.append(_noticeText(popup))
	return notices


_HELP["control"] = "Run a game control, as its hotkey or menu entry would, e.g. CONTROL_QUICK_SAVE, CONTROL_DOMESTIC_SCREEN, CONTROL_WORLD_BUILDER. args: control."


def cmd_control(args):
	eControl = _enum(ControlTypes, args["control"])
	gc.getGame().doControl(eControl)
	return None


_HELP["autoplay"] = "Start AI Auto Play for a number of turns; 0 stops it. args: turns."


def cmd_autoplay(args):
	gc.getGame().setAIAutoPlay(int(args["turns"]))
	return {"autoPlayTurns": gc.getGame().getAIAutoPlay()}


def _unusedSibling(path, szTag):
	# <!-- custom: Keeps the save extension last, so the EXE writes the name it was given. (Claude code Opus 5.5) -->
	root, ext = os.path.splitext(path)
	i = 0
	while True:
		candidate = "%s.%s%d_%d%s" % (root, szTag, os.getpid(), i, ext)
		if not os.path.exists(candidate):
			return candidate
		i = i + 1


_HELP["save"] ="Save the game; through SASPilotClient.py a bare name goes to Saves/single with the .CivBeyondSwordSave extension, else a full path. An existing file is refused unless overwrite=true. args: path, overwrite."


def cmd_save(args):
	# <!-- custom: Saving over an existing file made the EXE ask "already exists. Press OK to proceed, overwriting the file" in the window, which SASPilot cannot answer, and the reply still said exists for the old file (2026-11-13). So an existing file is refused unless overwrite=true, and then removed first, which is what that OK does. (Claude code Opus 5.5) -->
	# <!-- custom: With overwrite, the new save is written beside the old one and replaces it only once it exists: the first version removed the old file first, so a failed write would have lost both (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if os.path.isfile(args["path"]):
		if args.get("overwrite") is not True:
			raise ValueError("%s exists; pass overwrite=true to replace it" % args["path"])
		# <!-- custom: The second version still used one fixed ".new" name, so a file left by an earlier failed attempt could pass the size check and be installed stale, and it removed the old save before the rename, so a failed rename left only the temporary file (Codex's review).
		# Both side files now get names unused at that moment, and the old save is only renamed aside until the new one is in place; Python 2.4 on Windows has no atomic replace, since os.rename refuses an existing target. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		szNew = _unusedSibling(args["path"], "new")
		gc.getGame().saveGame(str(szNew))
		if not os.path.isfile(szNew) or os.path.getsize(szNew) == 0:
			raise ValueError("the new save was not written; %s is unchanged" % args["path"])
		# <!-- custom: Codex's round-16 review, with mocked failures: when putting the old save back failed too, the error did not say it was kept as the .old file, and a failed removal of that file after the new save was in place reported the whole save as failed.
		# Each outcome now names where the files are. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		szOld = _unusedSibling(args["path"], "old")
		os.rename(args["path"], szOld)
		try:
			os.rename(szNew, args["path"])
		except OSError:
			try:
				os.rename(szOld, args["path"])
			except OSError:
				raise ValueError("could not install the new save; the old one is kept as %s and the new one is %s" % (szOld, szNew))
			raise ValueError("could not install the new save; %s is unchanged and the new one is %s" % (args["path"], szNew))
		result = {"path": args["path"], "exists": True, "replaced": True}
		try:
			os.remove(szOld)
		except OSError:
			result["oldKeptAs"] = szOld
		return result
	gc.getGame().saveGame(str(args["path"]))
	return {"path": args["path"], "exists": os.path.isfile(args["path"])}


_HELP["menu"] = "Leave the game for the main menu; with path, load that save instead. The reply is written first; SASPilot answers again once a game runs. args: path."


def cmd_menu(args):
	# <!-- custom: Leaving a Huge turn-305 game this way crashed Civ4 in the EXE every time (2026-11-13), whatever was loaded next; in big games close the client and start it with the save instead. See KI#1084. (Claude code Opus 5.5) -->
	# <!-- custom: The EXE's binding takes (path, bool) although its help string shows the path alone; False loaded the save in the same process.
	# What the bool changes is not known. (Claude code Fable 5.2) -->
	# <!-- custom: Refused while a diplomacy screen is open, as the window does, its screen being modal: loaded from under an open screen, the screen stayed open over the new game with the old partner and offers, and 1 of 4 such loads crashed Civ4 with the diplomacy screen on the stack, while 8 of 8 loads with it closed worked (2026-11-13). See KI#1088. (Claude code Opus 5.5) -->
	if _diploState()["open"]:
		raise ValueError("a diplomacy screen is open; close it first ('diplo', then 'reply' with its Farewell), as the window allows no load while it is open")
	# <!-- custom: Also while a contact is queued but its screen not yet open, which would then open over the loaded game (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _pendingContact() is not None:
		raise ValueError("a diplomacy screen is about to open; read 'diplo' and close it first")
	CyInterface().exitingToMainMenu(str(args.get("path", "")), False)
	return None


_HELP["screen"] = "Call a CvScreensInterface function, e.g. name=showDomesticAdvisor, name=pediaJumpToUnit args=[UNIT_ index], name=pediaShow. args: name, args (list, optional)."


# <!-- custom: Fixed arguments for the play screens that index an argument list, as the play role allows them only without args and the None retry below failed for them (Codex's review, round 34): the Info Screen's first tab outside the end of a game, the Hall of Fame without replays, the Sevopedia's first category (see cmd_screen). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
# <!-- custom: showForeignAdvisorScreen too: called with None it passed None as the tab to SASGameRecordActions.logScreenAction, whose DLL binding takes an int, and failed (turn 114 of the turn-0 game, 2026-11-14); -1 is its own default tab. (Claude code Opus 5.5) -->
_SCREEN_DEFAULT_ARGS = {"showInfoScreen": [0, 0], "showHallOfFame": [0], "showForeignAdvisorScreen": [-1]}


def cmd_screen(args):
	function = getattr(CvScreensInterface, args["name"])
	# <!-- custom: pediaMain [0] failed in SevoPediaMain.showContents with "'NoneType' object is not callable": SAS's Sevopedia has no list for category 0 (2026-11-20).
	# Its own first category, which pediaShow falls back to, is used instead. (Claude code Opus 5.5) -->
	if "args" not in args and args["name"] == "pediaMain":
		CvScreensInterface.createCivilopedia()
		function([CvScreensInterface.pediaMainScreen.SAS_defaultCategory])
	elif "args" not in args and _SCREEN_DEFAULT_ARGS.has_key(args["name"]):
		function(_SCREEN_DEFAULT_ARGS[args["name"]])
	elif "args" in args:
		function(args["args"])
	else:
		try:
			function()
		except TypeError:
			function(None)
	# <!-- custom: Replied null, the screen functions' own return, which read as a failure in SASPilotConsole (the user, 2026-11-19); the call made is said instead. (Claude code Opus 5.5) -->
	return {"called": args["name"], "args": args.get("args")}


_POPUP_FIELDS = ("state", "id", "type", "typeId", "data1", "data2", "data3", "flags", "option1", "option2", "pythonButtons", "pythonModule", "onClicked", "buttons", "text")


def _popupGame():
	return _pilotGame("getSASPilotPathJson")


def _popups():
	result = []
	for line in _popupGame().getSASPilotPopups().split(u"\n"):
		if not line:
			continue
		# <!-- custom: The text is the last field and may hold anything but tabs, so split only the fixed fields before it. (Claude code Fable 5.2) -->
		parts = line.split(u"\t", len(_POPUP_FIELDS) - 1)
		popup = {}
		for i in range(len(_POPUP_FIELDS)):
			value = parts[i]
			if _POPUP_FIELDS[i] in ("id", "typeId", "data1", "data2", "data3", "flags", "option1", "option2", "pythonButtons"):
				value = int(value)
			# <!-- custom: sas-ci-string-compare-exemption: The DLL popup dictionary uses a stable field name. (GPT-6.2-Sol) -->
			elif _POPUP_FIELDS[i] == "buttons":
				# <!-- custom: "0=KEEP,1=RAZE" from getSASPilotPopupButtons: the buttons the game would offer now, by number and name. (Claude code Fable 5.2) -->
				buttons = []
				for item in value.split(u","):
					if item:
						(szId, szName) = item.split(u"=", 1)
						buttons.append({"button": int(szId), "name": str(szName)})
				value = buttons
			popup[_POPUP_FIELDS[i]] = value
		_popupAbout(popup)
		result.append(popup)
	return result


def _popupAbout(popup):
	# <!-- custom: The window says "Adopt Caste System?", while the held CHANGECIVIC popup at turn 70 of the fog-on playthrough (2026-11-13) gave data1 2 and data2 12 with no text.
	# Name what the data stand for in the popups SASPilot answers, from each launcher's use of them in CvDLLButtonPopup.cpp. (Claude code Opus 5.5) -->
	szType = popup["type"]
	if szType == "BUTTONPOPUP_CHANGECIVIC":
		popup["about"] = {"civicOption": _typeOrNone(gc.getCivicOptionInfo, popup["data1"]), "civic": _typeOrNone(gc.getCivicInfo, popup["data2"])}
		# <!-- custom: Adopting Slavery from this popup at turn 8 of the islands replay (2026-11-15) cost two turns of anarchy, which the popup does not say; an earlier game had shown none, so the anarchy it would cost is read from the game, as for a state religion below. (Claude code Opus 5.5) -->
		player = gc.getActivePlayer()
		if player is not None and not player.isNone() and popup["data1"] >= 0 and popup["data2"] >= 0:
			civics = [player.getCivics(i) for i in range(gc.getNumCivicOptionInfos())]
			civics[popup["data1"]] = popup["data2"]
			popup["about"]["anarchyTurns"] = player.getCivicAnarchyLength(civics)
	elif szType == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0:
		popup["about"] = {"freeTechs": popup["data1"], "use": "freetech"}
	elif szType == "BUTTONPOPUP_DECLAREWARMOVE":
		# <!-- custom: Declaring war in the diplomacy screen raised this confirmation, held by SASPilot, with the target team in data1 (2026-11-13). (Claude code Opus 5.5) -->
		popup["about"] = {"team": popup["data1"], "leaders": [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() == popup["data1"]]}
	elif szType == "BUTTONPOPUP_CHANGERELIGION":
		popup["about"] = {"religion": _typeOrNone(gc.getReligionInfo, popup["data1"])}
		# <!-- custom: A state religion costs anarchy too (none for a Spiritual leader), as the user pointed out; corporations do not. (Claude code Opus 5.5) -->
		player = gc.getActivePlayer()
		if player is not None and not player.isNone():
			popup["about"]["anarchyTurns"] = player.getReligionAnarchyLength()
	elif szType == "BUTTONPOPUP_DIPLOVOTE":
		# <!-- custom: The resolution the window shows, which the DLL puts in the text (getSASPilotPopups); 'todo' lists 'about', not the text.
		# A TEAM_<id> button elects that team. (Claude code Opus 5.5) -->
		popup["about"] = {"resolution": _plainText(popup["text"])}
		# <!-- custom: Each TEAM_<id> button also names that team's leaders, as the window's vote buttons do: the turn-305 U.N. election of the ASOKA Huge save (2026-11-22) offered TEAM_1 and TEAM_4, and telling Cyrus from the rest took a 'players' lookup. (Claude code Opus 5.5) -->
		for button in popup.get("buttons", []):
			szName = str(button.get("name", ""))
			if szName.startswith("TEAM_") and szName[5:].isdigit():
				iTeam = int(szName[5:])
				button["leaders"] = [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() == iTeam]
	elif szType in ("BUTTONPOPUP_RAZECITY", "BUTTONPOPUP_CHOOSEPRODUCTION"):
		city = gc.getPlayer(_activePlayerId()).getCity(popup["data1"])
		if city is not None and not city.isNone():
			popup["about"] = {"city": city.getName()}
	elif szType == "BUTTONPOPUP_PYTHON" and popup.get("onClicked") == CITY_TIP_CALLBACK:
		# <!-- custom: The advisor's tip to build something, such as Hippo's Colosseum or Utica's Punic Agora (turns 155 and 174, 2026-11-13): data1 is the city, data2 the order type and data3 the item.
		# Its buttons come from the DLL (getSASPilotPopupButtons), which 'answer' then uses as for any other popup. (Claude code Opus 5.5) -->
		city = gc.getPlayer(_activePlayerId()).getCity(popup["data1"])
		item = None
		if popup["data2"] == int(OrderTypes.ORDER_CONSTRUCT):
			item = _typeOrNone(gc.getBuildingInfo, popup["data3"])
		elif popup["data2"] == int(OrderTypes.ORDER_TRAIN):
			item = _typeOrNone(gc.getUnitInfo, popup["data3"])
		elif popup["data2"] == int(OrderTypes.ORDER_CREATE):
			item = _typeOrNone(gc.getProjectInfo, popup["data3"])
		popup["about"] = {"city": (city is not None and not city.isNone()) and city.getName() or None, "build": item}


# <!-- custom: The advisor tip's click handler, named on the popup by CvAdvisorUtils.py. (Claude code Opus 5.5) -->
CITY_TIP_CALLBACK = "cityWarningOnClickedCallback"


_HELP["popups"] = "The active player's popups. HELD ones were kept from the window while SASPilot drives and can be answered by their id; DISPLAYED and QUEUED ones are in the window. Each has state, id (-1 unless held), type (BUTTONPOPUP_ name), data1-3, flags, options, buttons (the ones 'answer' takes now, by number and name) and text. args: held (optional, 1 or 0, to switch holding on or off first; switching it off hands the held popups back to the window)."


def cmd_popups(args):
	if args.get("held") is not None:
		_popupGame().setSASPilotPopupsHeld(bool(args["held"]))
	return {"held": _popupGame().isSASPilotPopupsHeld(), "popups": _popups()}


_HELP["closepopups"] = "Drop held and queued popups without answering them: all of them, or only one type. A dropped choice is not made: set production, research and the like by command. A popup already on display stays until clicked. args: type (BUTTONPOPUP_ name, optional), data1 (optional, e.g. the city ID)."


def cmd_closepopups(args):
	game = _popupGame()
	iType = -1
	if args.get("type") is not None:
		iType = int(_enum(ButtonPopupTypes, args["type"]))
	game.closeSASPilotPopups(iType, int(args.get("data1", -1)))
	return _popups()


_HELP["answer"] = "Answer a held popup as if one of its buttons were clicked. 'popups' lists each held popup's buttons by number and name, such as 0 KEEP and 1 RAZE; only the buttons the game would offer now are accepted. Production and tech are chosen with 'produce' and 'research' instead. args: id (from 'popups'), button (number or name, default 0), text (edit box)."


def cmd_answer(args):
	# <!-- custom: By id rather than list position: Codex's review found a position could name another popup after the list shifted.
	# The DLL prunes and looks the id up again before answering. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iId = int(args["id"])
	popup = None
	for item in _popups():
		if item["state"] == "HELD" and item["id"] == iId:
			popup = item
	if popup is None:
		raise ValueError("no held popup with id %d; 'popups' lists them" % iId)
	# <!-- custom: A table of each type's highest button stood here; it accepted raze button 1 when the city could not be razed and button 2 when liberation was not on offer (Codex's review).
	# The DLL now lists the buttons the game would offer, with names, and checks the button again itself, so this only turns a name into its number and explains a refusal. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if not popup["buttons"]:
		raise ValueError("'answer' does not take %s yet" % popup["type"])
	button = args.get("button", 0)
	iButton = None
	for item in popup["buttons"]:
		if str(button) == item["name"] or str(button) == str(item["button"]):
			iButton = item["button"]
	if iButton is None:
		raise ValueError("%s is not offered by this %s; its buttons: %s" % (button, popup["type"], ", ".join(["%d %s" % (item["button"], item["name"]) for item in popup["buttons"]])))
	if not _popupGame().answerSASPilotPopup(iId, iButton, unicode(args.get("text", u""))):
		raise ValueError("the game refused to answer popup %d" % iId)
	return popup


# <!-- custom: City screen (Claude code Opus 5.5) -->


# <!-- custom: Empire choices (Claude code Opus 5.5) -->

_HELP["civics"] = "Without set: each civic option with the current civic and the ones the player can adopt, and whether a revolution is possible now. Timing: each civic or religion change costs its own anarchy, and no second change can start while anarchy runs (CvPlayer::canRevolution and canConvert refuse it), so changes cannot share one anarchy; a golden age makes both free. Switch when a candidate pays soon (couldWhipNow, upkeep saved, a needed effect, the binding happiness or health limit rather than a spare one); weigh the anarchy turns' cost (anarchyCostPerTurn) against what the civic returns soon, rather than adopting it because it is available: the 2026-11-19 validation run took Slavery for 2 turns of anarchy at turn 37, and its two whips in the next 20 turns (a Settler 3 turns sooner, an Archer about 12 turns sooner in a 2-hammer city with no defender) likely repaid it. With set: adopt those civics, one per option at most, as the civics screen's Revolution button does; a change with anarchy needs confirm=1. args: set (list of CIVIC_ types), confirm, player."


def cmd_civics(args):
	player = _player(args)
	civics = [player.getCivics(i) for i in range(gc.getNumCivicOptionInfos())]
	if args.get("set") is None:
		options = {}
		for iOption in range(gc.getNumCivicOptionInfos()):
			available = [gc.getCivicInfo(i).getType() for i in range(gc.getNumCivicInfos()) if gc.getCivicInfo(i).getCivicOptionType() == iOption and player.canDoCivics(i)]
			options[gc.getCivicOptionInfo(iOption).getType()] = {"current": gc.getCivicInfo(civics[iOption]).getType(), "available": available}
		# <!-- custom: When a switch pays, not only that it is possible: the user's request after Slavery cost 2 turns of anarchy at turn 26 of the 2026-11-19 validation run with nothing to whip.
		# Per candidate civic: anarchy turns alone, upkeep change, and for a whip civic the cities that could whip now; anarchyCostPerTurn is what the empire makes in a turn, all lost in anarchy. (Claude code Opus 5.5) -->
		iUpkeepNow = player.getCivicUpkeep(civics, False)
		candidates = []
		for iOption in range(gc.getNumCivicOptionInfos()):
			for iCivic in range(gc.getNumCivicInfos()):
				kCivic = gc.getCivicInfo(iCivic)
				if kCivic.getCivicOptionType() != iOption or iCivic == civics[iOption] or not player.canDoCivics(iCivic):
					continue
				changed = list(civics)
				changed[iOption] = iCivic
				entry = {"civic": kCivic.getType(), "anarchyTurns": player.getCivicAnarchyLength(changed), "upkeepChange": player.getCivicUpkeep(changed, False) - iUpkeepNow}
				whips = [i for i in range(gc.getNumHurryInfos()) if kCivic.isHurry(i) and gc.getHurryInfo(i).getProductionPerPopulation() > 0]
				if whips:
					ready = []
					(city, it) = player.firstCity(False)
					while city:
						iNeeded = city.getProductionNeeded() - city.getProduction()
						iPerPop = gc.getHurryInfo(whips[0]).getProductionPerPopulation() * gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getHurryPercent() / 100
						if city.getOrderQueueLength() > 0 and city.maxHurryPopulation() > 0 and iPerPop > 0:
							iPop = (iNeeded + iPerPop - 1) / iPerPop
							if iPop <= city.maxHurryPopulation():
								ready.append({"city": city.getName(), "build": str(_orderData(city.getOrderFromQueue(0))), "population": iPop})
						(city, it) = player.nextCity(it, False)
					entry["couldWhipNow"] = ready
				candidates.append(entry)
		iHammers = 0
		(city, it) = player.firstCity(False)
		while city:
			iHammers += city.getYieldRate(YieldTypes.YIELD_PRODUCTION)
			(city, it) = player.nextCity(it, False)
		return {"options": options, "canRevolution": player.canRevolution(0), "revolutionTimer": player.getRevolutionTimer(), "anarchyTurns": player.getAnarchyTurns(), "candidates": candidates, "anarchyCostPerTurn": {"hammers": iHammers, "commerce": player.calculateTotalYield(YieldTypes.YIELD_COMMERCE)}}
	wanted = args["set"]
	if isinstance(wanted, (str, unicode)):
		wanted = [wanted]
	for szCivic in wanted:
		iCivic = _typedIndex(szCivic, "CIVIC_", gc.getNumCivicInfos(), gc.getCivicInfo)
		# <!-- custom: canAdopt (CvPlayer::canRevolution) only checks that a revolution is possible and changes something, not that each civic is available: the first test adopted Slavery on turn 0, without its tech (2026-11-13).
		# The civics screen never offers such a civic, so check it here. (Claude code Fable 5.2) -->
		if not player.canDoCivics(iCivic):
			raise ValueError("player %d cannot adopt %s; 'civics' lists the available ones" % (player.getID(), szCivic))
		civics[gc.getCivicInfo(iCivic).getCivicOptionType()] = iCivic
	if not player.canAdopt(civics):
		# <!-- custom: After enemy spies imposed Despotism at turn 113 of the fog-on playthrough (2026-11-13), restoring Hereditary Rule was refused with no reason; the revolution timer was at 4.
		# Say so. (Claude code Opus 5.5) -->
		raise ValueError("player %d cannot start a revolution to %s now (revolution timer %d, anarchy turns %d)" % (player.getID(), ", ".join(wanted), player.getRevolutionTimer(), player.getAnarchyTurns()))
	iAnarchy = player.getCivicAnarchyLength(civics)
	# <!-- custom: At turn 26 of the 2026-11-19 validation run Slavery was adopted at once for 2 turns of anarchy, which stopped production as well as research (the Worker sat at 56 of 60), while size-2 Dublin had nothing to whip yet; the user asked why so soon. (Claude code Opus 5.5) -->
	if iAnarchy > 0 and not args.get("confirm"):
		raise ValueError("this revolution costs %d turn(s) of anarchy, in which cities produce nothing and research stops: switch when the civic pays at once (a whip ready, a big upkeep saving) and bundle changes into one anarchy; confirm=1 adopts" % iAnarchy)
	# <!-- custom: Applied directly rather than with CyMessageControl().sendUpdateCivics, which the civics screen uses: the net message is handled after the reply is written, so the first test's reply still showed the old civics.
	# Both end in CvPlayer::revolution; a network game would need the message. (Claude code Fable 5.2) -->
	player.revolution(civics, False)
	return {"civics": [gc.getCivicInfo(player.getCivics(i)).getType() for i in range(gc.getNumCivicOptionInfos())], "anarchyLength": iAnarchy}


_HELP["sliders"] = "Without args: the commerce percentages (gold is what the others leave). With commerce and percent: set one, as the +/- buttons do. args: commerce (COMMERCE_ type), percent, player."


def cmd_sliders(args):
	player = _player(args)
	if args.get("commerce") is not None:
		iCommerce = _typedIndex(args["commerce"], "COMMERCE_", CommerceTypes.NUM_COMMERCE_TYPES, gc.getCommerceInfo)
		player.setCommercePercent(CommerceTypes(iCommerce), int(args["percent"]))
	result = {}
	for i in range(CommerceTypes.NUM_COMMERCE_TYPES):
		result[gc.getCommerceInfo(i).getType()] = {"percent": player.getCommercePercent(CommerceTypes(i)), "rate": player.getCommerceRate(CommerceTypes(i))}
	result["goldRate"] = player.calculateGoldRate()
	result["gold"] = player.getGold()
	return result


_HELP["resolution"] = "Without args: the game's screen resolution and the modes the Options screen's Graphics tab offers. size=WIDTHxHEIGHT, such as 1920x1080 or 2560x1440, switches to that mode during play, as choosing it there does; SAS's screens follow such a change (KI#123.2 to KI#123.5). args: size."


def cmd_resolution(args):
	# <!-- custom: Through CyUserProfile, as the Options screen's handleResolutionDropdownInput does, so a test at another size keeps the running game.
	# Before (2026-11-28) an agent restarted Civ4 to go from 2560 x 1440 to 1920 x 1080, losing the client's state, as nothing told it the screens follow a change made during play; switching in the Options by clicks works but needs coordinates per window size. (Claude code Opus 5.5) -->
	# <!-- custom: current is the screen's real size, profile the mode the profile names: they can differ, as an unanswered "keep this resolution" dialog puts the old size back but leaves the profile on the new mode (2026-11-28).
	# The switch applies after this reply, which so still shows the old size; SASPilotClient.py waits for the window and confirms the dialog. (Claude code Opus 5.5) -->
	profile = CyUserProfile()
	modes = [profile.getResolutionString(i) for i in range(profile.getResolutionMaxModes())]
	iProfile = profile.getResolution()
	screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
	szCurrent = "%d x %d" % (screen.getXResolution(), screen.getYResolution())
	result = {"current": szCurrent, "profile": modes[iProfile]}
	if args.get("size") is None:
		result["modes"] = modes
		return result
	szWanted = str(args["size"]).replace(" ", "").lower()
	matches = [i for i in range(len(modes)) if modes[i].replace(" ", "").lower() == szWanted]
	if not matches:
		raise ValueError("no resolution mode %s; modes: %s" % (args["size"], ", ".join(modes)))
	bScreenFits = szCurrent.replace(" ", "").lower() == szWanted
	# <!-- custom: Nothing to do when the screen and the profile both have the size: no switch, so no keep dialog, and the client presses no key.
	# The first version switched anyway and the client pressed Enter, which is also the End Turn key, with no dialog up (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if bScreenFits and matches[0] == iProfile:
		result["unchanged"] = True
		return result
	# <!-- custom: Setting the mode the profile already names does nothing, so when an earlier revert left the profile on the wanted mode and the screen elsewhere, say so rather than reply as if it switched.
	# Switching to the screen's own size realigns the profile (it shows the keep dialog too), after which the wanted size switches. (Claude code Opus 5.5) -->
	if matches[0] == iProfile:
		raise ValueError("the profile already names %s while the screen is %s, after an unanswered keep dialog; switch to %s first" % (modes[iProfile], szCurrent, szCurrent))
	profile.setResolution(matches[0])
	# <!-- custom: "initiated", not "switched": the EXE then asks whether to keep the mode and puts the old one back unless answered, so the switch is not done when this replies; SASPilotClient.py logs the verified outcome in a row of its own (the user, 2026-11-28).
	# The name came from the user's review: "requested", the first one, read as asking permission, and of "attempted" and "initiated" the user chose "initiated", as the switch has begun but awaits its answer. (Claude code Opus 5.5) -->
	result["initiated"] = modes[matches[0]]
	return result


_HELP["corporations"] = "The Policy Advisor's Corporations tab: per corporation, when it was founded (turn, or null), the unit that founds it, the resources it consumes and produces, and what each resource it consumes yields in a city, scaled to the map size as the tab shows it (yieldsPerResource and commercesPerResource, in hundredths as the tab's rows store them: 50 is +0.5); then per city of the player, whether it is the capital, the headquarters it holds, the corporations in it with whether each is active and the yields and commerces each gives that city now, and the gold the city pays for them per turn in hundredths (maintenanceX100, an estimate of the sum of the tab's per-corporation figures: the tab rounds each corporation's share down, so its sum can be lower, by up to one gold per corporation; Python cannot read them one by one). args: player."


def cmd_corporations(args):
	# <!-- custom: The 2026-11-22 tab audit left policy/CORPORATIONS with no command ('world' lists corporations, not this tab's per-city detail); Codex suggested it next on 2026-11-28, for spread decisions.
	# The inputs and per-resource outputs come from the tab's own helpers on a copy of the screen, so their world-size scaling (KI#231) is the tab's; the per-city numbers are the city's own per-corporation getters, as the tab's text comes from CyGameTextMgr. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	import copy
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "corporations in cities")
	view = copy.copy(CvScreensInterface.policyAdvisorScreen)
	# <!-- custom: The screen reads this define when it first draws the tab, so it was None in a session where the tab had not been opened, and the first run raised "range() integer end argument expected, got NoneType"; read here through SASCurrentDefines, the shared cache CI asks for, on the copy only. (Claude code Opus 5.5) -->
	if view.NUM_CORPORATION_PREREQ_BONUSES is None:
		view.NUM_CORPORATION_PREREQ_BONUSES = SASCurrentDefines.getInt("NUM_CORPORATION_PREREQ_BONUSES")
	iWorldPercent = gc.getWorldInfo(gc.getMap().getWorldSize()).getCorporationMaintenancePercent()
	game = gc.getGame()
	corporations = []
	for iCorp in range(gc.getNumCorporationInfos()):
		info = gc.getCorporationInfo(iCorp)
		iTurn = game.getCorporationGameTurnFounded(iCorp)
		szBuiltBy = None
		for iBuilding in range(gc.getNumBuildingInfos()):
			if gc.getBuildingInfo(iBuilding).getFoundsCorporation() == iCorp:
				for iUnit in range(gc.getNumUnitInfos()):
					if gc.getUnitInfo(iUnit).getBuildings(iBuilding) or gc.getUnitInfo(iUnit).getForceBuildings(iBuilding):
						szBuiltBy = gc.getUnitInfo(iUnit).getType()
						break
				break
		yields = {}
		for iYield in range(YieldTypes.NUM_YIELD_TYPES):
			iValue = view.getScaledCorporationGeneratedValue(info.getYieldProduced(iYield), iWorldPercent)
			if iValue:
				yields[_enumName(YieldTypes, iYield)] = iValue
		commerces = {}
		for iCommerce in range(CommerceTypes.NUM_COMMERCE_TYPES):
			iValue = view.getScaledCorporationGeneratedValue(info.getCommerceProduced(iCommerce), iWorldPercent)
			if iValue:
				commerces[_enumName(CommerceTypes, iCommerce)] = iValue
		# <!-- custom: Turn 0 is founded too: 'iTurn >= 0 and iTurn or None' gave None for it, as 0 is false (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iFoundedTurn = None
		if iTurn >= 0:
			iFoundedTurn = iTurn
		corporations.append({"type": info.getType(), "foundedTurn": iFoundedTurn, "builtBy": szBuiltBy, "consumes": [gc.getBonusInfo(eBonus).getType() for eBonus in view.getCorporationConsumedBonuses(info)], "produces": _typeOrNone(gc.getBonusInfo, info.getBonusProduced()), "yieldsPerResource": yields, "commercesPerResource": commerces})
	cities = []
	for city in _cities(player):
		inCity = []
		for iCorp in range(gc.getNumCorporationInfos()):
			if not city.isHasCorporation(iCorp):
				continue
			yields = {}
			for iYield in range(YieldTypes.NUM_YIELD_TYPES):
				iValue = city.getCorporationYieldByCorporation(iYield, iCorp)
				if iValue:
					yields[_enumName(YieldTypes, iYield)] = iValue
			commerces = {}
			for iCommerce in range(CommerceTypes.NUM_COMMERCE_TYPES):
				iValue = city.getCorporationCommerceByCorporation(iCommerce, iCorp)
				if iValue:
					commerces[_enumName(CommerceTypes, iCommerce)] = iValue
			inCity.append({"type": gc.getCorporationInfo(iCorp).getType(), "active": bool(city.isActiveCorporation(iCorp)), "yields": yields, "commerces": commerces})
		headquarters = [gc.getCorporationInfo(iCorp).getType() for iCorp in range(gc.getNumCorporationInfos()) if city.isHeadquartersByType(iCorp)]
		# <!-- custom: The tab shows each corporation's gold maintenance in the city (Aachen -21); Python has only the city's total, while the per-corporation figure is CvCity's alone, so the total is given.
		# calculateCorporationMaintenanceTimes100 is before inflation (it divides by it), which gave Aachen 11; the tab's text (CvGameTextMgr::setCorporationHelpCity) applies the city's maintenance modifier and the K-Mod inflation rate, as here.
		# It is an estimate of the tab's sum: the tab applies both factors to each corporation and truncates each, so with two base costs of 101 hundredths and a -50% modifier it gives 50 + 50 where this gives 101 (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iMaintenance = city.calculateCorporationMaintenanceTimes100() * (100 + city.getMaintenanceModifier()) / 100
		iMaintenance = iMaintenance * (100 + player.calculateInflationRate()) / 100
		cities.append({"city": city.getName(), "cityId": city.getID(), "capital": bool(city.isCapital()), "headquarters": headquarters, "corporations": inCity, "maintenanceX100": iMaintenance})
	return {"player": player.getID(), "corporations": corporations, "cities": cities}


_HELP["religion"] ="Without args: the state religion and the religions the player can convert to now, each candidate with our cities that have it (where the state religion's happiness, happinessFromCivics, applies), our holy city of it, and the met civs whose state religion it is (sharedWith, who like us for it) or who follow another (otherFaithOf, who dislike a different one), each with its power against ours and its closest city's distance: happiness against diplomacy, where a near or strong neighbour weighs most. With convert: convert to it (NO_RELIGION: none). args: convert (RELIGION_ type), player."


def cmd_religion(args):
	player = _player(args)
	if args.get("convert") is not None:
		iReligion = -1
		if args["convert"] != "NO_RELIGION":
			iReligion = _typedIndex(args["convert"], "RELIGION_", gc.getNumReligionInfos(), gc.getReligionInfo)
		if not player.canConvert(iReligion):
			raise ValueError("player %d cannot convert to %s now" % (player.getID(), args["convert"]))
		# <!-- custom: Applied directly, as in 'civics', so the reply shows the result. (Claude code Fable 5.2) -->
		player.convert(iReligion)
	# <!-- custom: At turn 56 of the 2026-11-19 validation run Hinduism was founded in Cork while Paganism had spread there too; Paganism was chosen for Cyrus, its follower and the neighbour with 3 times our power, who went to Pleased (+4, "brothers and sisters of the faith"), while Hinduism would have given the same +1 happiness in Cork alone.
	# That trade-off was worked out by hand, so each candidate now gives: our cities that have it (where a state religion's happiness applies), our holy city of it, and the met civs whose state religion it is or is not, as a player reads them on the scoreboard. (Claude code Opus 5.5) -->
	cities = _cities(player)
	met = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and gc.getTeam(player.getTeam()).isHasMet(gc.getPlayer(i).getTeam())]
	# <!-- custom: The user, same game: align with a neighbour's faith, a strong one especially, though even a weaker one may attack; so each civ comes with its power against ours and its closest city's distance, from 'relations', which applies the scoreboard's visibility. (Claude code Opus 5.5) -->
	known = {}
	for row in _command("relations")({"player": player.getID(), "fog": args.get("fog")})["players"]:
		known[row["name"]] = {"name": row["name"], "powerRatioPerMille": row.get("powerRatioPerMille"), "closestCityDistance": row.get("closestCityDistance")}
	candidates = []
	for i in range(gc.getNumReligionInfos()):
		if not player.canConvert(i) and player.getStateReligion() != i:
			continue
		candidates.append({"religion": gc.getReligionInfo(i).getType(), "inOurCities": [city.getName() for city in cities if city.isHasReligion(i)], "ourHolyCity": [city.getName() for city in cities if city.isHolyCityByType(i)], "sharedWith": [known.get(other.getName(), other.getName()) for other in met if other.getStateReligion() == i], "otherFaithOf": [known.get(other.getName(), other.getName()) for other in met if other.getStateReligion() >= 0 and other.getStateReligion() != i]})
	return {"stateReligion": _typeOrNone(gc.getReligionInfo, player.getStateReligion()), "canConvertTo": [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if player.canConvert(i)], "anarchyLength": player.getReligionAnarchyLength(), "happinessFromCivics": player.getStateReligionHappiness(), "candidates": candidates}


# <!-- custom: Game text, which several commands read; the Sevopedia's data commands moved to SASPilotCatalog.py on 2026-11-28. (Claude code Opus 5.5) -->

_reMarkup = re.compile(r"<[^>]*>")


_symbolNames = None


def _plainText(text):
	# <!-- custom: Game text draws its icons as GameFont characters, which reached the first 'pedia' reply as meaningless letters such as U+01C6 for the bullet; name them instead, e.g. [YIELD_FOOD], and write the bullet as a dash. (Claude code Fable 5.2) -->
	global _symbolNames
	if _symbolNames is None:
		names = {}
		game = gc.getGame()
		for szName in dir(FontSymbols):
			if szName.endswith("_CHAR"):
				names[game.getSymbolID(getattr(FontSymbols, szName))] = "[" + szName[:-5] + "]"
		names[game.getSymbolID(FontSymbols.BULLET_CHAR)] = "- "
		for (iNum, getter) in ((YieldTypes.NUM_YIELD_TYPES, gc.getYieldInfo), (CommerceTypes.NUM_COMMERCE_TYPES, gc.getCommerceInfo), (gc.getNumBonusInfos(), gc.getBonusInfo), (gc.getNumReligionInfos(), gc.getReligionInfo), (gc.getNumCorporationInfos(), gc.getCorporationInfo)):
			for i in range(iNum):
				names[getter(i).getChar()] = "[" + getter(i).getType() + "]"
		_symbolNames = names
	text = _reMarkup.sub("", text)
	parts = []
	for ch in text:
		parts.append(_symbolNames.get(ord(ch), ch))
	return u"".join(parts).strip()


_HELP["batch"] = "Run several commands in one request, in order, stopping at the first failure. args: commands (list of {cmd, args}). From the CLI: SASPilotClient.py batch 'commands=[{\"cmd\":\"units\"},{\"cmd\":\"cities\"}]'."


def cmd_batch(args):
	# <!-- custom: A request waited for the next game update, about 250 ms each when measured (2026-11-13), so a turn's worth of orders was far quicker as one request; served every frame it is now about 2 ms, which still makes one request cheaper. (Claude code Fable 5.2 + Claude code Opus 5.5) -->
	results = []
	for item in args["commands"]:
		try:
			handler = _checkedHandler(item["cmd"], item.get("args") or {})
			_checkRole(item["cmd"], item.get("args") or {})
		except ValueError:
			raise ValueError("%s, after %d done" % (sys.exc_info()[1], len(results)))
		results.append(handler(item.get("args") or {}))
	return results


_HELP["profile"] = "Run a command and time its parts: reading the game (gatherMs) and writing the JSON (encodeMs), each the best of 'repeat' runs. args: cmd, args (dict, optional), repeat (default 3)."


def cmd_profile(args):
	# <!-- custom: Found 441 plots spending 3 ms reading the game and 28 ms writing JSON (2026-11-13), which pointed at the writer rather than the game or Python as a whole; kept as a command so the next slow command is split the same way. (Claude code Opus 5.5) -->
	commandArgs = args.get("args") or {}
	handler = _checkedHandler(args["cmd"], commandArgs)
	_checkRole(args["cmd"], commandArgs)
	gather = []
	encode = []
	for i in range(int(args.get("repeat", 3))):
		fStart = time.clock()
		value = handler(commandArgs)
		fMiddle = time.clock()
		text = toJson(value)
		gather.append((fMiddle - fStart) * 1000.0)
		encode.append((time.clock() - fMiddle) * 1000.0)
	return {"cmd": args["cmd"], "gatherMs": min(gather), "encodeMs": min(encode), "bytes": len(text)}


class _Capture:
	def __init__(self):
		self.parts = []

	def write(self, text):
		if isinstance(text, unicode):
			text = text.encode("cp1252", "replace")
		self.parts.append(text)


_HELP["pyerrors"] = "This client's Python error output since SASPilot started, which the game also writes to PythonErr.log: the last lines, up to 400 writes kept, and how many writes there were. Every client shares PythonErr.log, and a Civ4 stuck while exiting can keep it locked, so this is the one read that is surely this client's. Any reply also carries pythonErrors, the last 12 lines written since the previous reply, when there are any. clear=1 empties it after this read, so the next shows only what came after. args: clear, lines (default 40)."


def cmd_pyerrors(args):
	lines = _state.setdefault("pyErrors", [])
	count = _state.setdefault("pyErrorWrites", [0])
	rows = [row for row in _errorText(lines).split(u"\n") if row.strip()]
	result = {"writes": count[0], "lines": rows[-int(args.get("lines", 40)):]}
	# <!-- custom: Emptied after the reply is built: the first version emptied it first, so SASPilotUISweep.py, which reads with clear=1, never saw an error, while a raised test error stood open in the window (2026-11-20). (Claude code Opus 5.5) -->
	if args.get("clear"):
		del lines[:]
		count[0] = 0
		# <!-- custom: The replies' count starts over with it: left as it was, two writes reported, cleared, then two new ones, were not reported (Codex's review, 2026-11-28). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		_state["pyErrorWritesReported"] = 0
	return result


_HELP["py"] = "Run Python inside the game and return what it printed, plus the value of 'result' if the code sets it, or of the code itself when it is one expression. The namespace persists between calls and has gc, game, map, interface, player (active), describe() and everything from CvPythonExtensions. args: code."


def cmd_py(args):
	namespace = _state["py"]
	if "gc" not in namespace:
		# <!-- custom: Was the statement form exec "..." in namespace, which Python 2.4 runs but Ruff's modern parser cannot read, so CI's Ruff stopped on this file (Codex found it).
		# eval of a code object compiled in "exec" mode runs the statements in both, checked with C:\Python24. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		eval(compile("from CvPythonExtensions import *\n", "<saspilot>", "exec"), namespace)
	namespace["gc"] = gc
	namespace["game"] = gc.getGame()
	namespace["map"] = CyMap()
	namespace["interface"] = CyInterface()
	# <!-- custom: describe lives in SASPilotCatalog.py since 2026-11-28, and is looked up when called: looked up here, a catalog that failed to load stopped every 'py' snippet, the tool to diagnose it with (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	namespace["describe"] = _describe
	namespace["saspilot"] = sys.modules.get(__name__) or globals()
	iActive = gc.getGame().getActivePlayer()
	if iActive >= 0:
		namespace["player"] = gc.getPlayer(iActive)
	namespace.pop("result", None)
	code = args["code"].replace("\r\n", "\n")
	capture = _Capture()
	stdout = sys.stdout
	sys.stdout = capture
	try:
		try:
			compiled = compile(code, "<saspilot>", "eval")
		except SyntaxError:
			compiled = None
		if compiled is not None:
			namespace["result"] = eval(compiled, namespace)
		else:
			# <!-- custom: The game's Python is 2.4, without "a if c else b": three agent sessions in a row wrote one into 'py' code on 2026-11-13 and read the bare "invalid syntax" each time.
			# Name the likely cause when the failing line has that shape. (Claude code Opus 5.5) -->
			# <!-- custom: eval of an "exec" code object and sys.exc_info() replace exec ... in and "except SyntaxError, error", which Ruff cannot parse; see the namespace setup above. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			try:
				eval(compile(code + "\n", "<saspilot>", "exec"), namespace)
			except SyntaxError:
				error = sys.exc_info()[1]
				szLine = error.text or ""
				if " if " in szLine and " else " in szLine:
					raise SyntaxError("%s; Python 2.4 has no 'a if c else b': use an if statement or (c and [a] or [b])[0]" % error)
				raise
	finally:
		sys.stdout = stdout
	return {"output": "".join(capture.parts), "result": namespace.get("result")}
