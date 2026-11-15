# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: The commands SASPilot answers. SASPilot.py loads this file from disk and reloads it when it changes, so commands can be added or fixed while Civ4 runs; nothing imports it normally, and it lives outside Assets because the EXE reinitializes Python when a .py file there changes.
# Each command is a function cmd_<name>(args) taking the request's args dict and returning plain data (dict, list, str, number, bool, None), which poll() writes back as JSON.
# Commands see everything, without fog of war: the pilot is a research and debugging tool for the active player, not a fair opponent as in civai.
# 'fog on=1' switches to what the active player's team knows, to play as a person would; see cmd_fog. (Claude code Fable 5.2)
# Python 2.4 has no json module, so the encoder and decoder below are our own. (Claude code Fable 5.2) -->

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

gc = CyGlobalContext()

# <!-- custom: Bump when a command's name, arguments or reply changes, so a client can tell which bridge it talks to. (Claude code Fable 5.2) -->
PILOT_REVISION = 1

_state = None


# JSON

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


# Mailbox

def _writeAtomic(path, text):
	temp = path + ".tmp"
	handle = open(temp, "wb")
	handle.write(text)
	handle.close()
	if os.path.exists(path):
		os.remove(path)
	os.rename(temp, path)


def poll(state, szReloadError):
	# <!-- custom: Called on every tick; one directory listing when no request waits. (Claude code Fable 5.2) -->
	global _state
	_state = state
	state["reloadError"] = szReloadError
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
		# <!-- custom: Claimed by renaming req_ to run_ before it runs, and run_ removed only once the reply is written. The first version read and deleted the request first, so a client that timed out could not tell a command never started, which is safe to retry, from one already running, which a retry would repeat (ChatGPT's review, 2026-11-14). SASPilotClient.py's timeout now withdraws only a request still named req_. (Claude code Opus 5.5 + ChatGPT-5.6-Sol) -->
		running = os.path.join(mailbox, "run_" + name[4:])
		try:
			os.rename(path, running)
			handle = open(running, "rb")
			text = handle.read()
			handle.close()
		except (IOError, OSError):
			continue  # <!-- custom: still being written or already taken; the next tick retries (Claude code Fable 5.2) -->
		reply = _serve(text)
		state["served"] = state["served"] + 1
		szReply = toJson(reply)
		szReply = szReply[:-1] + ',"gameMs":' + repr((time.clock() - fStart) * 1000.0) + ',"tick":"' + state.get("lastTick", "") + '"}'
		_writeAtomic(os.path.join(mailbox, "rep_" + name[4:]), szReply)
		try:
			os.remove(running)
		except OSError:
			pass  # <!-- custom: the reply is out; a run_ file left behind only means the claim was not cleaned up (Claude code Opus 5.5) -->


def _checkedHandler(name, args):
	# <!-- custom: The command's function, once its name and argument keys are checked: 'civics adopt=CIVIC_THEOCRACY' returned the civics list as if it had worked, as the command takes set= and the unknown key was ignored (fog-on playthrough, turn 131, 2026-11-13). A key the command's help does not list is refused; player and fog are read by shared helpers for any command.
	# Used by 'batch' and 'profile' too, which first called handlers directly and so skipped the check (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	handler = globals().get("cmd_" + str(name))
	if handler is None:
		raise ValueError("unknown command %r; 'help' lists the commands" % name)
	allowed = _allowedArgs(name)
	unknown = [key for key in args.keys() if key not in allowed]
	if unknown:
		raise ValueError("%s takes no %s; it takes: %s" % (name, ", ".join(unknown), ", ".join(allowed) or "nothing"))
	return handler


def _allowedArgs(name):
	# <!-- custom: The argument names from the end of the command's help, "args: unit, x, y (default ...), player."; a help without "args:" takes none but the shared ones. The first version left such commands unchecked (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
		if match is not None and match.group(1) != "none":
			names.append(match.group(1))
	for szShared in ("player", "fog"):
		if szShared not in names:
			names.append(szShared)
	return names


def _applyLaunchRole():
	# <!-- custom: The role 'SASPilotClient.py start --role' wrote in the per-run INI ([SASPilot] Role), applied and locked once, before the first request is served, so no command can run under another role first (Codex's review, round 33). Read here rather than in the SASPilot.py loader, which cannot be changed while Civ4 runs; the loader's own INI reader is reused. A role the bridge does not know is refused loudly on every request rather than ignored. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _state.get("launchRoleRead"):
		return
	import SASPilot
	szRole = SASPilot._pilotSection().get("role")
	if szRole:
		if szRole not in _ROLE_ALLOWED:
			raise ValueError("the per-run INI's [SASPilot] Role is %s, which is not play, assist or all" % szRole)
		if szRole != "all":
			_state["role"] = szRole
			_state["fog"] = True
		_state["roleLocked"] = True
	_state["launchRoleRead"] = True


def _serve(text):
	reply = {"ok": False}
	try:
		request = fromJson(text)
		reply["id"] = request.get("id")
		# <!-- custom: Codex's review simulated a stale req_ that SASPilot._start could not delete from a recycled PID's folder, and the new game ran it. A launched session refuses any request not carrying its own session ID, which SASPilotClient.py reads from hello.json; without a session (SAS_PILOT_ON with no per-run INI) every request is served, as before. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if _state.get("session") and request.get("session") != _state.get("session"):
			raise ValueError("request %s is for session %s, not this game's %s; it was not run" % (request.get("id"), request.get("session"), _state.get("session")))
		name = request["cmd"]
		args = request.get("args") or {}
		_applyLaunchRole()
		handler = _checkedHandler(name, args)
		_checkRole(name, args)
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
	return reply


# Lookups

def _typeName(info):
	if info is None:
		return None
	return info.getType()


def _typeOrNone(getter, iType):
	if iType is None or iType < 0:
		return None
	return getter(iType).getType()


def _infoIndex(szType):
	iType = gc.getInfoTypeForString(szType)
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


def _otherAiId(player, value):
	# <!-- custom: The AI a diplomacy command talks to: another living civilization, not human, that the player can contact; shared by 'contact', 'trade' and 'propose'. (Claude code Opus 5.5) -->
	iOther = _checkedPlayerId(value)
	if iOther >= gc.getMAX_CIV_PLAYERS() or iOther == player.getID() or gc.getPlayer(iOther).isHuman():
		raise ValueError("player %d is not an AI player the active player could contact" % iOther)
	if not player.canContact(iOther):
		raise ValueError("player %d cannot contact player %d" % (player.getID(), iOther))
	return iOther


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
	unit = player.getUnit(int(args["unit"]))
	if unit is None or unit.isNone():
		raise ValueError("player %d has no unit %s" % (player.getID(), args["unit"]))
	return unit


def _city(args):
	player = _player(args)
	key = args["city"]
	if isinstance(key, (int, long)) or str(key).isdigit():
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


# Views

def _unitBrief(unit):
	# <!-- custom: The 'units' list and the units inside plots come from appendSASPilotUnitJson in CvGameInterface.cpp instead; keep the two writers' fields the same. (Claude code Opus 5.5) -->
	# <!-- custom: experience, level and the unit's own name added as in the C++ writer (2026-11-14). (Claude code Opus 5.5) -->
	result = {"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "owner": unit.getOwner(), "movesLeft": unit.movesLeft(), "damage": unit.getDamage(), "group": unit.getGroupID(), "experience": unit.getExperience(), "level": unit.getLevel()}
	if unit.getNameNoDesc():
		result["name"] = unit.getNameNoDesc()
	return result


def _missionQueue(group):
	queue = []
	for i in range(group.getLengthMissionQueue()):
		iData1 = group.getMissionData1(i)
		# <!-- custom: A build mission's data1 is a BuildTypes index, which came back as 17 in the fog-on playthrough (2026-11-13); name it as every other type. Move targets keep their x and y. (Claude code Opus 5.5) -->
		if group.getMissionType(i) == MissionTypes.MISSION_BUILD and iData1 >= 0:
			iData1 = gc.getBuildInfo(iData1).getType()
		queue.append({"mission": gc.getMissionInfo(group.getMissionType(i)).getType(), "data1": iData1, "data2": group.getMissionData2(i)})
	return queue


def _unitFull(unit):
	result = _unitBrief(unit)
	group = unit.getGroup()
	result["name"] = unit.getName()
	result["strength"] = unit.baseCombatStr()
	result["baseMoves"] = unit.baseMoves()
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
		result["cargoUnits"] = [_unitBrief(plot.getUnit(i)) for i in range(plot.getNumUnits()) if plot.getUnit(i).isCargo() and plot.getUnit(i).getTransportUnit().getID() == unit.getID() and plot.getUnit(i).getOwner() == unit.getOwner()]
	result["groupSize"] = group.getNumUnits()
	# <!-- custom: These first came as numbers ("activity": 6, "automate": 3) while every other type is a name; the fog-on playthrough (2026-11-13) needed the enum read up to know a scout was exploring. (Claude code Opus 5.5) -->
	result["activity"] = _enumName(ActivityTypes, group.getActivityType())
	result["automate"] = _enumName(AutomateTypes, group.getAutomateType())
	result["readyToMove"] = group.readyToMove(False)
	result["missions"] = _missionQueue(group)
	return result


def _unitActions(unit):
	# <!-- custom: What the unit's buttons would offer on its own plot: missions and commands with bTestVisible off, plus builds, promotions and upgrades. Target missions such as MISSION_MOVE_TO are listed when startable at all; the target is checked when the order is given. (Claude code Fable 5.2) -->
	group = unit.getGroup()
	plot = unit.plot()
	missions = []
	for i in range(gc.getNumMissionInfos()):
		if i == MissionTypes.MISSION_BUILD:
			continue
		if group.canStartMission(i, -1, -1, plot, False):
			missions.append(gc.getMissionInfo(i).getType())
	builds = [gc.getBuildInfo(i).getType() for i in range(gc.getNumBuildInfos()) if unit.canBuild(plot, i, False)]
	commands = []
	for i in range(gc.getNumCommandInfos()):
		if i in (CommandTypes.COMMAND_PROMOTION, CommandTypes.COMMAND_UPGRADE):
			continue
		if unit.canDoCommand(CommandTypes(i), -1, -1, False):
			commands.append(gc.getCommandInfo(i).getType())
	promotions = [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if unit.canPromote(i, -1)]
	upgrades = [gc.getUnitInfo(i).getType() for i in range(gc.getNumUnitInfos()) if unit.canUpgrade(i, False)]
	# <!-- custom: COMMAND_AUTOMATE was missing from 'commands', as it is tested with data1 -1 there, so the Explore button a person clicks for a scout had no listed equivalent (fog-on playthrough, 2026-11-13). List each automation the unit's buttons would offer. (Claude code Opus 5.5) -->
	# <!-- custom: Missions that take a type as data were tested with -1 only, so a Great Scientist born at turn 105 of the fog-on playthrough (2026-11-13) listed no "Join City" or "Build Academy". Test each specialist and building as the unit's buttons do and list them as MISSION:TYPE. (Claude code Opus 5.5) -->
	for i in range(gc.getNumSpecialistInfos()):
		if group.canStartMission(int(MissionTypes.MISSION_JOIN), i, -1, plot, False):
			missions.append("MISSION_JOIN:" + gc.getSpecialistInfo(i).getType())
	for i in range(gc.getNumBuildingInfos()):
		if group.canStartMission(int(MissionTypes.MISSION_CONSTRUCT), i, -1, plot, False):
			missions.append("MISSION_CONSTRUCT:" + gc.getBuildingInfo(i).getType())
	# <!-- custom: The same for religions and corporations: Hippo's free Islamic Missionary stood in Carthage at turn 129 of the second fog-on game (2026-11-13) with canSpread true, yet listed no spread, as MISSION_SPREAD takes the religion as data. (Claude code Opus 5.5) -->
	for i in range(gc.getNumReligionInfos()):
		if group.canStartMission(int(MissionTypes.MISSION_SPREAD), i, -1, plot, False):
			missions.append("MISSION_SPREAD:" + gc.getReligionInfo(i).getType())
	for i in range(gc.getNumCorporationInfos()):
		if group.canStartMission(int(MissionTypes.MISSION_SPREAD_CORPORATION), i, -1, plot, False):
			missions.append("MISSION_SPREAD_CORPORATION:" + gc.getCorporationInfo(i).getType())
	automations = [name for name in _AUTOMATE_NAMES if unit.canDoCommand(CommandTypes.COMMAND_AUTOMATE, int(getattr(AutomateTypes, name)), -1, False)]
	# <!-- custom: Recon, air bombing, air strikes, rebasing, paradrops, airlifts, ranged attacks and nukes start by picking a plot, as an interface mode, so canStartMission with no target never listed them.
	# List the modes the unit's buttons offer with the mission a plot click then gives; 'targets' lists the plots. (Claude code Opus 5.5) -->
	targetModes = []
	if hasattr(gc, "getInterfaceModeInfo"):
		for i in range(int(InterfaceModeTypes.NUM_INTERFACEMODE_TYPES)):
			info = gc.getInterfaceModeInfo(i)
			if info.getMissionType() >= 0 and group.canDoInterfaceMode(InterfaceModeTypes(i)):
				targetModes.append({"mode": info.getType(), "mission": gc.getMissionInfo(info.getMissionType()).getType()})
	return {"missions": missions, "builds": builds, "commands": commands, "promotions": promotions, "upgrades": upgrades, "automations": automations, "targetModes": targetModes}


# <!-- custom: AutomateTypes has no XML info, so its names come from the Boost enum class. (Claude code Opus 5.5) -->
_AUTOMATE_NAMES = [name for name in dir(AutomateTypes) if name.startswith("AUTOMATE_")]


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


def _cityFull(city):
	result = _cityBrief(city)
	iOwner = city.getOwner()
	result["food"] = city.getFood()
	result["growthThreshold"] = city.growthThreshold()
	result["foodDifference"] = city.foodDifference(True)
	result["production"] = city.getProduction()
	# <!-- custom: With an empty queue the game returns MAX_INT, which came back as 2147483647 (fog-on playthrough, 2026-11-13); give null instead, as nothing is being produced. (Claude code Opus 5.5) -->
	result["productionNeeded"] = None
	if city.getOrderQueueLength() > 0:
		result["productionNeeded"] = city.getProductionNeeded()
	result["yieldRate"] = _yields(city.getYieldRate)
	result["commerceRate"] = [city.getCommerceRate(CommerceTypes(i)) for i in range(CommerceTypes.NUM_COMMERCE_TYPES)]
	result["culture"] = city.getCulture(iOwner)
	result["cultureThreshold"] = city.getCultureThreshold()
	result["happy"] = city.happyLevel()
	result["unhappy"] = city.unhappyLevel(0)
	result["health"] = city.goodHealth()
	result["unhealth"] = city.badHealth(False)
	result["buildings"] = [gc.getBuildingInfo(i).getType() for i in range(gc.getNumBuildingInfos()) if city.getNumRealBuilding(i) > 0]
	result["specialists"] = dict([(gc.getSpecialistInfo(i).getType(), city.getSpecialistCount(i)) for i in range(gc.getNumSpecialistInfos()) if city.getSpecialistCount(i) > 0])
	# <!-- custom: A settled Great Scientist joined Utica as a free specialist at turn 105 (2026-11-13), which 'specialists' (getSpecialistCount) did not show, so the join looked to have failed. (Claude code Opus 5.5) -->
	result["freeSpecialists"] = dict([(gc.getSpecialistInfo(i).getType(), city.getFreeSpecialistCount(i)) for i in range(gc.getNumSpecialistInfos()) if city.getFreeSpecialistCount(i) > 0])
	result["isCapital"] = city.isCapital()
	# <!-- custom: The city screen's religion and corporation icons and its resistance count; after Gondar was taken at turn 146 of the fog-on playthrough (2026-11-13), 'city' said nothing of its Christianity, of its being that religion's holy city, or of the turns of unrest. (Claude code Opus 5.5) -->
	result["religions"] = [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if city.isHasReligion(i)]
	result["holyCityOf"] = [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if city.isHolyCityByType(i)]
	result["corporations"] = [gc.getCorporationInfo(i).getType() for i in range(gc.getNumCorporationInfos()) if city.isHasCorporation(i)]
	result["occupationTurns"] = city.getOccupationTimer()
	result["maintenance"] = city.getMaintenance()
	# <!-- custom: What else the city screen shows: its trade routes with each partner and the commerce it brings, the defense bonus and its bombard damage, and Great People progress. The user asked at turn 141 of the turn-0 game (2026-11-14) whether the pilot has the city screen's details; trade routes in particular need explored land and contact (a world map widens them), and 'city' had none of these. (Claude code Opus 5.5) -->
	routes = []
	for i in range(city.getTradeRoutes()):
		partner = city.getTradeCity(i)
		if partner is None or partner.isNone():
			continue
		routes.append({"city": partner.getName(), "owner": partner.getOwner(), "commerce": city.calculateTradeYield(YieldTypes.YIELD_COMMERCE, city.calculateTradeProfit(partner))})
	result["tradeRoutes"] = {"slots": city.getTradeRoutes(), "routes": routes}
	result["defense"] = {"percent": city.getDefenseModifier(False), "damagePercent": city.getDefenseDamage()}
	result["greatPeople"] = {"progress": city.getGreatPeopleProgress(), "rate": city.getGreatPeopleRate(), "threshold": gc.getPlayer(city.getOwner()).greatPeopleThreshold(False)}
	return result


def _cityOptions(city):
	# <!-- custom: Units, buildings and projects first came as bare lists of types; the city screen shows each with its turns, which decide most choices (fog-on playthrough, 2026-11-13). They are now type -> turns at the current production. (Claude code Opus 5.5) -->
	units = dict([(gc.getUnitInfo(i).getType(), city.getUnitProductionTurnsLeft(i, 0)) for i in range(gc.getNumUnitInfos()) if city.canTrain(i, False, False)])
	buildings = dict([(gc.getBuildingInfo(i).getType(), city.getBuildingProductionTurnsLeft(i, 0)) for i in range(gc.getNumBuildingInfos()) if city.canConstruct(i, False, False, False)])
	projects = dict([(gc.getProjectInfo(i).getType(), city.getProjectProductionTurnsLeft(i, 0)) for i in range(gc.getNumProjectInfos()) if city.canCreate(i, False, False)])
	processes = [gc.getProcessInfo(i).getType() for i in range(gc.getNumProcessInfos()) if city.canMaintain(i, False)]
	hurries = [gc.getHurryInfo(i).getType() for i in range(gc.getNumHurryInfos()) if city.canHurry(i, False)]
	return {"units": units, "buildings": buildings, "projects": projects, "processes": processes, "hurries": hurries}


def _plotFull(plot):
	# <!-- custom: Written in C++ by CyGame.getSASPilotPlotsJson, which took 0.32 ms for 441 plots against 8 ms for the Python writer it replaced (2026-11-13); the user preferred the long-term speed.
	# There is one writer only, so a new plot field goes in appendSASPilotPlotJson in CvGameInterface.cpp and needs a DLL build; see "Would the DLL be faster?" in README_Pilot.md. (Claude code Opus 5.5) -->
	return RawJson(_plotsJson(plot.getX(), plot.getY(), 0)[1:-1])


def _plotsJson(iX, iY, iRadius, iFogTeam=-1):
	text = _pilotGame("getSASPilotPathJson").getSASPilotPlotsJson(iX, iY, iRadius, iFogTeam)
	if text == "null":
		raise ValueError("radius %d is out of range: 0 to the larger map side" % iRadius)
	# <!-- custom: The area ID comes from the true map, so with fog it leaked hidden geography: in the scouting trial (2026-11-14) the bay by the capital and a sea seen far south-west shared one ID, telling that they connect through plots nobody had seen. appendSASPilotPlotJson now writes null with fog; this blanks it for a DLL built before that change and can go once one is installed. (Claude code Opus 5.5) -->
	if iFogTeam >= 0:
		text = re.sub(r'"area":-?\d+', '"area":null', text)
	return text


def _pilotGame(szNewestBinding):
	# <!-- custom: The pilot's C++ bindings grew over several builds, and a DLL without the newest one a command needs, such as the shipped Release DLL until it is refreshed, would raise a bare AttributeError or TypeError; name the cause instead. (Claude code Fable 5.2) -->
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
	# <!-- custom: With fog on, another team's unit or city is only given when the active team sees its plot now, as on the map. Returns whether it is another team's. (Claude code Fable 5.2) -->
	iTeam = _fogTeam(args)
	if iTeam < 0 or gc.getPlayer(iOwner).getTeam() == iTeam:
		return False
	if not plot.isVisible(iTeam, False):
		raise ValueError("%s is not in sight; fog is on" % szWhat)
	return True


def _cityAsSeen(city):
	# <!-- custom: What the map shows of a rival's city; its build queue, food and the like are on its city screen, which a player cannot open. (Claude code Fable 5.2) -->
	return {"id": city.getID(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "owner": city.getOwner(), "population": city.getPopulation()}


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


# Read commands

# <!-- custom: One line per command for 'help', kept beside each function instead of a docstring. (Claude code Fable 5.2) -->
# <!-- custom: Help texts are returned as written, never %-formatted, so a percent sign is a plain %: the first 'advise' help had "70%%", from habit with format strings, which 'help' would have shown doubled (2026-11-14). It now says per mille, as the odds are given. (Claude code Opus 5.5) -->
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
		# <!-- custom: The difficulty, which the Victory screen shows a player: the user asked whether the pilot played Monarch or Noble (2026-11-14), and no command said. The game's level and the active player's, which can differ. (Claude code Opus 5.5) -->
		result["handicap"] = _typeOrNone(gc.getHandicapInfo, game.getHandicapType())
		if game.getActivePlayer() >= 0:
			result["playerHandicap"] = _typeOrNone(gc.getHandicapInfo, gc.getPlayer(game.getActivePlayer()).getHandicapType())
	return result


_HELP["player"] = "One player's empire summary. args: player (default: the active player)."


def cmd_player(args):
	return _playerFull(_player(args))


_HELP["players"] = "Every player ever alive, as in 'player'. With fog on, the active team's players so, and other teams' players only once met, with their ID, name, civilization, team and whether alive, as the scoreboard shows them."


def cmd_players(args):
	# <!-- custom: Under play, 'players' gave every civilization's full summary, unmet ones included (Codex's review, round 32). With fog on, a player we have not met is not listed, and one we have is given as the scoreboard shows it. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
			result.append(entry)
	return result


_HELP["units"] = "A player's units, briefly, or every living player's with player=all. args: player."


def cmd_units(args):
	# <!-- custom: Written in C++ by CyGame.getSASPilotUnitsJson: on a Huge map at turn 300, Python took 8 ms for the 876 units of all players, 6 of them writing JSON (2026-11-13). (Claude code Opus 5.5) -->
	if args.get("player") == "all":
		iPlayer = -1
	else:
		iPlayer = _playerId(args)
	text = _pilotGame("getSASPilotPathJson").getSASPilotUnitsJson(iPlayer, _fogTeam(args))
	if text == "null":
		raise ValueError("no player %d" % iPlayer)
	return RawJson(text)


_HELP["unit"] = "One unit in full, with the orders it can take now. args: unit (ID), player."


def cmd_unit(args):
	unit = _unit(args)
	if _requireSeen(args, unit.getOwner(), unit.plot(), "unit %d" % unit.getID()):
		# <!-- custom: 'units' left out invisible units such as spies and submarines, but 'unit' by ID still gave them, and a rival unit's orders and mission queue with them (Codex's review). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		if unit.isInvisible(_fogTeam(args), False):
			raise ValueError("unit %d is not in sight; fog is on" % unit.getID())
		result = _unitBrief(unit)
		result["strength"] = unit.baseCombatStr()
		result["promotions"] = [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if unit.isHasPromotion(i)]
		return result
	result = _unitFull(unit)
	result["actions"] = _unitActions(unit)
	return result


_HELP["cities"] = "A player's cities, briefly. args: player."


def cmd_cities(args):
	player = _player(args)
	iTeam = _fogTeam(args)
	if iTeam >= 0 and player.getTeam() != iTeam:
		# <!-- custom: With fog on, a rival's cities are the ones the active team has revealed, with what the map shows of them. (Claude code Fable 5.2) -->
		return [{"id": city.getID(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "owner": city.getOwner()} for city in _cities(player) if city.isRevealed(iTeam, False)]
	return [_cityBrief(city) for city in _cities(player)]


_HELP["city"] = "One city in full, with what it can produce now. args: city (ID or name), player."


def cmd_city(args):
	city = _city(args)
	iTeam = _fogTeam(args)
	if iTeam >= 0 and gc.getPlayer(city.getOwner()).getTeam() != iTeam:
		# <!-- custom: A rival's city in sight first came back in full, queue and food included (Codex's review).
		# A city the team has revealed stays on its map out of sight, so it is given as 'cities' lists it, and with its population while in sight; the first fix refused it out of sight, which a test showed hid a city 'cities' still listed. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		if not city.isRevealed(iTeam, False):
			raise ValueError("player %d has no city %s" % (city.getOwner(), args["city"]))
		result = _cityAsSeen(city)
		if not city.plot().isVisible(iTeam, False):
			del result["population"]
		else:
			# <!-- custom: Its defence bonus while in sight, as the window's city bar shows it beside the size, so a siege can be planned without a 'py' call (Gondar at turn 118 of the fog-on playthrough, 2026-11-13). (Claude code Opus 5.5) -->
			result["defenseModifier"] = city.getDefenseModifier(False)
		return result
	result = _cityFull(city)
	result["options"] = _cityOptions(city)
	return result


_HELP["trainable"] = "The units a city can train now, for choosing value per hammer: each with its turns, cost, strength, moves, strength per 100 hammers (strengthPer100Hammers, integer), and what strength alone does not show: first strikes and their chance, collateral damage and how many units it reaches, withdrawal chance, bombard rate, city attack and defense bonuses, and bonuses against unit types (versus, in percent). Military units first, sorted by strength per 100 hammers, which misleads for siege: cityAttackPer100Hammers (with the city attack bonus), combatLimit (a siege unit cannot kill) and the effects weigh as much. args: city, player."


def cmd_trainable(args):
	# <!-- custom: The user advised at turn 100 of the turn-0 game (2026-11-14) weighing units by strength against cost, as an Axeman for 35 hammers is strong early, and by the effects strength leaves out, as a Trebuchet's strength is low but it bombards and harms several defenders. 'city' gave the trainable units with their turns only. These are the XML's facts, as the city screen's hover shows them; which to build stays the agent's choice. (Claude code Opus 5.5) -->
	city = _city(args)
	player = gc.getPlayer(city.getOwner())
	result = []
	for i in range(gc.getNumUnitInfos()):
		if not city.canTrain(i, False, False):
			continue
		info = gc.getUnitInfo(i)
		iCost = player.getUnitProductionNeeded(i)
		entry = {"unit": info.getType(), "turns": city.getUnitProductionTurnsLeft(i, 0), "cost": iCost, "strength": info.getCombat(), "moves": info.getMoves(), "combatType": _typeOrNone(gc.getUnitCombatInfo, info.getUnitCombatType())}
		if iCost > 0:
			entry["strengthPer100Hammers"] = info.getCombat() * 10000 / iCost
		for (szKey, iValue) in (("firstStrikes", info.getFirstStrikes()), ("chanceFirstStrikes", info.getChanceFirstStrikes()), ("collateralDamage", info.getCollateralDamage()), ("collateralMaxUnits", info.getCollateralDamageMaxUnits()), ("withdrawalPct", info.getWithdrawalProbability()), ("bombardRate", info.getBombardRate()), ("cityAttackPct", info.getCityAttackModifier()), ("cityDefensePct", info.getCityDefenseModifier())):
			if iValue:
				entry[szKey] = iValue
		# <!-- custom: The user's follow-up: strength per hammer misleads for siege, as a Trebuchet (4 strength, about 80 hammers) has +100% city attack, collateral damage and bombard, yet defends badly unlike a Catapult. So, beside the plain ratio, the strength against a city per 100 hammers for units with a city attack bonus, and the combat limit (a siege unit stops at that damage and cannot kill), with cityDefensePct shown when negative too. (Claude code Opus 5.5) -->
		if info.getCityAttackModifier() and iCost > 0:
			entry["cityAttackPer100Hammers"] = info.getCombat() * (100 + info.getCityAttackModifier()) * 100 / iCost
		if info.getCombatLimit() < 100:
			entry["combatLimit"] = info.getCombatLimit()
		# <!-- custom: The XML gives every unit a collateral reach of 3, so the first test listed it on Settlers and Scouts; it means something only beside collateral damage. (Claude code Opus 5.5) -->
		if not info.getCollateralDamage() and entry.has_key("collateralMaxUnits"):
			del entry["collateralMaxUnits"]
		versus = {}
		for k in range(gc.getNumUnitCombatInfos()):
			if info.getUnitCombatModifier(k):
				versus[gc.getUnitCombatInfo(k).getType()] = info.getUnitCombatModifier(k)
		if versus:
			entry["versus"] = versus
		result.append(entry)
	# <!-- custom: Aircraft fight with air strength, not strength, so they sorted with civilians at zero (Codex's review, round 36): airStrength and its per-100-hammers figure, and aircraft count as military. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	for entry in result:
		info = gc.getUnitInfo(gc.getInfoTypeForString(entry["unit"]))
		if info.getAirCombat() > 0:
			entry["airStrength"] = info.getAirCombat()
			if entry["cost"] > 0:
				entry["airStrengthPer100Hammers"] = info.getAirCombat() * 10000 / entry["cost"]
	result.sort(lambda a, b: cmp((a["strength"] <= 0 and not a.get("airStrength"), -a.get("strengthPer100Hammers", 0)), (b["strength"] <= 0 and not b.get("airStrength"), -b.get("strengthPer100Hammers", 0))))
	return {"city": city.getName(), "units": result}


_HELP["plot"] = "One plot in full, with its units. args: x, y."


def cmd_plot(args):
	plot = _plot(args)
	text = _plotsJson(plot.getX(), plot.getY(), 0, _fogTeam(args))
	if text == "[]":
		raise ValueError("plot %d,%d is not revealed; fog is on" % (plot.getX(), plot.getY()))
	return RawJson(text[1:-1])


_HELP["plots"] = "The plots within a radius, in full. With fog on, only the plots the active team has revealed, each as it last saw it and with units only where it sees now. Center it on coordinates, one of our units or a city. args: x, y, unit, city, radius (default 1; the larger map side covers the whole map), fog (optional, overrides the 'fog' switch for this request), player."


def cmd_plots(args):
	anchors = sum([args.get(key) is not None for key in ("x", "unit", "city")])
	if anchors != 1 or (args.get("x") is None) != (args.get("y") is None):
		raise ValueError("give x and y, a unit, or a city as the center")
	if args.get("unit") is not None or args.get("city") is not None:
		_requireOwnTeamUnderFog(args, _player(args), "the map center")
		if args.get("unit") is not None:
			plot = _unit(args).plot()
		else:
			plot = _city(args).plot()
	else:
		plot = _plot(args)
	return RawJson(_plotsJson(plot.getX(), plot.getY(), int(args.get("radius", 1)), _fogTeam(args)))


# <!-- custom: Export canonical coordinates for the desktop map renderer. Under fog, use the game's remembered ownership, improvements and routes, and withhold fields without a last-seen accessor until the tile is visible. (GPT-6.1-Sol) -->
_TRADE_NEIGHBORS = ((1, 0), (0, 1), (1, 1), (-1, 1))


def _gridBounds(kMap, args):
	width = kMap.getGridWidth()
	height = kMap.getGridHeight()
	if args.get("box") is not None:
		if [key for key in ("x", "y", "city", "unit", "radius") if key in args]:
			raise ValueError("give box or one center with radius")
		x0, y0, x1, y1 = [int(value) for value in args["box"]]
	elif [key for key in ("x", "y", "city", "unit", "radius") if key in args]:
		anchors = sum([args.get(key) is not None for key in ("x", "unit", "city")])
		if anchors != 1 or (args.get("x") is None) != (args.get("y") is None):
			raise ValueError("give x and y, a unit, or a city as the center")
		if "city" in args:
			plot = _city(args).plot()
		elif "unit" in args:
			plot = _unit(args).plot()
		else:
			plot = _plot(args)
		radius = int(args.get("radius", 5))
		if radius < 0 or radius > max(width, height):
			raise ValueError("radius must be between zero and the larger map side")
		x0, y0 = max(0, plot.getX() - radius), max(0, plot.getY() - radius)
		x1, y1 = min(width - 1, plot.getX() + radius), min(height - 1, plot.getY() + radius)
	else:
		x0, y0, x1, y1 = 0, 0, width - 1, height - 1
	if not (0 <= x0 <= x1 < width and 0 <= y0 <= y1 < height):
		raise ValueError("box must be [west,south,east,north] within the map")
	return (x0, y0, x1, y1)


def _gridTradeLinks(kMap, plots, iTeam):
	width, height = kMap.getGridWidth(), kMap.getGridHeight()
	wrapX, wrapY = kMap.isWrapX(), kMap.isWrapY()
	links = []
	seen = set()
	for x, y in sorted(plots):
		plot = plots[(x, y)]
		for dx, dy in _TRADE_NEIGHBORS:
			nx, ny = x + dx, y + dy
			if wrapX:
				nx %= width
			if wrapY:
				ny %= height
			other = plots.get((nx, ny))
			if other is None or (x, y) == (nx, ny):
				continue
			key = tuple(sorted(((x, y), (nx, ny))))
			if key in seen:
				continue
			seen.add(key)
			if plot.isTradeNetworkConnected(other, iTeam) or other.isTradeNetworkConnected(plot, iTeam):
				links.append({"from": [x, y], "to": [nx, ny], "step": [dx, dy]})
	return links


_HELP["grid"] = "Fetch structured map tiles, river boundaries and optional trade-network links. With no area, fetch the map. The box is inclusive; a center and radius clip to map bounds. With fog on, fogEdge lists the unrevealed plots next to a revealed one, each with only water true or false, which the coastline art shows a player at the fog's edge; edge=0 leaves it out. args: box ([west,south,east,north]), x, y, city, unit, radius, network, edge, player."


_HELP["mark"] = "Mark a candidate city site the way a player does with BUG's dot map (Alt+X): a city dot and cross at x, y in that overlay, which the player sees, edits and keeps with the save, plus a sign when text is given; 'grid' lists the dot map's cities, the player's own included. clear=1 removes the dot (and sign) at x, y. Cosmetic: nothing in the game changes. args: x, y, text, color (COLOR_ type, default COLOR_GREEN), layer (dot-map layer, default 0), clear."


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


def cmd_mark(args):
	# <!-- custom: The user's idea in the scouting trial (2026-11-14): the agent compared city sites only in JSON, so the user watching could not see which plots it meant. A first version drew its own dots on the overlay layer, until the user asked whether the agent had Alt+X: BUG's dot map is the player's tool for exactly this, so marks now go into it through addCityAt, the same game message an Alt+X click sends, and the player can see and edit them. (Claude code Opus 5.5) -->
	import CvStrategyOverlay
	dotMap = CvStrategyOverlay.getDotMap()
	player = gc.getPlayer(_activePlayerId())
	plot = gc.getMap().plot(int(args["x"]), int(args["y"]))
	if plot is None or plot.isNone():
		raise ValueError("no plot at %s,%s" % (args["x"], args["y"]))
	point = (plot.getX(), plot.getY())
	if args.get("clear"):
		dotMap.removeCityAt(point)
		CyEngine().removeSign(plot, player.getID())
	else:
		# <!-- custom: Only a COLOR_ type in the colour table: getInfoTypeForString accepts types of any table, so color=TECH_AGRICULTURE passed and stored an unrelated index in BUG's dot map (Codex's review, round 38). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		szColor = args.get("color") or "COLOR_GREEN"
		iColor = gc.getInfoTypeForString(szColor)
		if not szColor.startswith("COLOR_") or iColor < 0 or iColor >= gc.getNumColorInfos() or gc.getColorInfo(iColor).getType() != szColor:
			raise ValueError("unknown color %s; give a COLOR_ type" % szColor)
		dotMap.addCityAt(point, iColor, int(args.get("layer", 0)))
		if args.get("text"):
			CyEngine().removeSign(plot, player.getID())
			CyEngine().addSign(plot, player.getID(), args["text"])
		dotMap.show()
	return {"note": "the dot map applies the change through a game message, so it shows in the next reply", "dotMap": _dotMapCities(player.getID())}


def _fogEdgeRevealedNeighbor(kMap, x, y, iFogTeam):
	# <!-- custom: Whether one of the 8 plots around x, y is revealed to the team, with the map's wrap; plots off an unwrapped edge do not count. (Claude code Opus 5.5) -->
	iWidth, iHeight = kMap.getGridWidth(), kMap.getGridHeight()
	for dy in (-1, 0, 1):
		for dx in (-1, 0, 1):
			if dx == 0 and dy == 0:
				continue
			nx, ny = x + dx, y + dy
			if kMap.isWrapX():
				nx = nx % iWidth
			if kMap.isWrapY():
				ny = ny % iHeight
			if 0 <= nx < iWidth and 0 <= ny < iHeight and kMap.plot(nx, ny).isRevealed(iFogTeam, False):
				return True
	return False


def cmd_grid(args):
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "the map grid")
	iFogTeam = _fogTeam(args)
	iTeam = player.getTeam()
	kMap = gc.getMap()
	x0, y0, x1, y1 = _gridBounds(kMap, args)
	tiles, network, owners = [], {}, {}
	bNetwork = bool(args.get("network", True))
	# <!-- custom: The fog edge, the user's point at turn 2 of the scouting trial (2026-11-14): the plot two north of the Clam was unrevealed, yet the screen showed its shore, so the water beside it looked like a lake; strong players read the art at the fog's edge, and the pilot knew nothing there.
	# Civ4 draws each revealed plot's coastline from whether its neighbours are land or water, so that much of an unrevealed neighbour is on screen and stays fair under play. Only water is given: terrain and trees in the fade were not checked against the art. (Claude code Opus 5.5) -->
	bEdge = iFogTeam >= 0 and bool(args.get("edge", True))
	edge = []
	gb = gc.getBonusInfo
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			plot = kMap.plot(x, y)
			if iFogTeam >= 0 and not plot.isRevealed(iFogTeam, False):
				if bEdge and _fogEdgeRevealedNeighbor(kMap, x, y, iFogTeam):
					edge.append({"x": x, "y": y, "water": bool(plot.isWater())})
				continue
			visible = iFogTeam < 0 or plot.isVisible(iFogTeam, False)
			if visible:
				owner, improvement, route = plot.getOwner(), plot.getImprovementType(), plot.getRouteType()
			else:
				owner = plot.getRevealedOwner(iFogTeam, False)
				improvement = plot.getRevealedImprovementType(iFogTeam, False)
				route = plot.getRevealedRouteType(iFogTeam, False)
			# <!-- custom: Feature and resource for every revealed plot, not only those in sight: the window draws both on fogged plots, as Civ4 keeps no remembered copy of features and shows a resource once the team has its reveal tech (plot.getBonusType(team) applies that). In the scouting trial (2026-11-14) a goody hut's map revealed Rice at 11,18, which 'resources' listed, yet a city-site query over 'grid' missed it because the bonus was left out off sight. Rivers and yields stay for plots in sight. (Claude code Opus 5.5) -->
			row = {"x": x, "y": y, "visible": visible, "owner": owner,
				"feature": _typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "bonus": _typeOrNone(gb, plot.getBonusType(iFogTeam)),
				"terrain": _typeOrNone(gc.getTerrainInfo, plot.getTerrainType()),
				"hill": bool(plot.isHills()), "peak": bool(plot.isPeak()), "water": bool(plot.isWater()),
				"improvement": _typeOrNone(gc.getImprovementInfo, improvement), "route": _typeOrNone(gc.getRouteInfo, route)}
			if owner >= 0 and owner not in owners:
				owners[owner] = gc.getPlayer(owner).getName()
			if visible:
				row["southRiver"] = bool(plot.isNOfRiver())
				row["eastRiver"] = bool(plot.isWOfRiver())
				row["yields"] = _yields(plot.getYield)
				# <!-- custom: The defence a unit of ours would get here against anyone but the plot's owner, from the game's rule (CvPlot::defenseModifier, buildings left out), for scouts ending a turn on safe ground (the user, 2026-11-14). The XML alone misled: SAS forest is 0 and jungle -25, but both add iRivalDefense 25 outside the attacker's land, so forest gives +25%, jungle 0 and a hill +25 more, as the combat report at 11,15 showed. (Claude code Opus 5.5) -->
				row["defense"] = plot.defenseModifier(iTeam, True, False)
				if plot.isCity():
					row["city"] = plot.getPlotCity().getName()
				row["unitCount"] = 0
				for j in range(plot.getNumUnits()):
					if iFogTeam < 0 or not plot.getUnit(j).isInvisible(iFogTeam, False):
						row["unitCount"] += 1
				if bNetwork and plot.isTradeNetwork(iTeam):
					network[(x, y)] = plot
					row["capitalNetwork"] = bool(plot.isConnectedToCapital(player.getID()))
			tiles.append(row)
	links = _gridTradeLinks(kMap, network, iTeam)
	game = gc.getGame()
	return {"turn": game.getGameTurn(), "player": player.getID(), "fog": iFogTeam >= 0,
		"box": [x0, y0, x1, y1], "width": kMap.getGridWidth(), "height": kMap.getGridHeight(),
		"wrapX": bool(kMap.isWrapX()), "wrapY": bool(kMap.isWrapY()), "owners": owners, "tiles": tiles, "tradeLinks": links, "fogEdge": edge, "dotMap": _dotMapCities(player.getID())}


_HELP["fog"] = "Without args: whether fog is on. With on=1 or 0: switch it. With fog on, 'plots', 'plot', 'units', 'unit', 'cities' and 'city' give only what the active player's team knows or sees, as a person at the window would; off (the default) gives everything, for debugging. 'players' lists other teams' players once met; most read commands follow the same rules, but 'py' is not limited. args: on."


# <!-- custom: Each command's role, the user's idea (2026-11-14): play is what a player sees and does in a normal game; omniscient sees past the fog, for debugging; create changes the game beyond play, as the WorldBuilder or 'py' can; meta runs the session. A session set to 'role set=play' refuses the rest, so a playthrough stays fair by construction, "same rules as the game".
# Commands not listed are play; some depend on their arguments, see _commandRole. (Claude code Opus 5.5) -->
# <!-- custom: The user's next idea the same day: tell facts from judgments. play commands state what the game shows a player, the same for every player who can see it, and rarely change; advice weighs facts into a recommendation by a heuristic of ours, which may be wrong and gets tuned as we learn, such as 'advise about=threats'.
# So advice is a role of its own: the session role 'play' gets facts only, which shows what an agent works out by itself, and 'assist' adds advice, so the log shows which advice an agent asked for. 'sites' stays play, as the window circles those sites for any player with a Settler selected; the city AI's builds in 'workers' are advice, as no screen shows them. (Claude code Opus 5.5) -->
_COMMAND_ROLES = {"py": "create", "autoplay": "meta", "save": "meta", "menu": "meta", "profile": "meta", "batch": "meta", "ping": "meta", "help": "meta", "role": "meta", "advise": "advice"}
_ROLE_ALLOWED = {"play": ("play", "meta"), "assist": ("play", "meta", "advice"), "all": ("play", "meta", "advice", "omniscient", "create")}
# <!-- custom: Controls that leave play, checked by value: the play role compared the control's name as typed, so its number passed (Codex's review, round 32). Loading a save is meta, as 'menu path=' is. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_CONTROL_ROLES = (("CONTROL_WORLD_BUILDER", "create"), ("CONTROL_ADMIN_DETAILS", "omniscient"), ("CONTROL_LOAD_GAME", "meta"), ("CONTROL_QUICK_LOAD", "meta"))


def _adviceAllowed():
	# <!-- custom: For commands that are mostly facts with a judgment among them, such as 'workers' with the city AI's builds: the judgment is left out when the session's role does not allow advice. (Claude code Opus 5.5) -->
	szRole = _state.get("role")
	return not szRole or "advice" in _ROLE_ALLOWED[szRole]


# <!-- custom: The screens a player opens from the window's buttons, the play role's 'screen' calls, without arguments. Round 32 had any show*/pedia* name pass, but showReplay forwards its args[0] to CyGame.saveReplay, so args=[9999,0,0,0,0] reached GET_PLAYER(9999) in CvGame::saveReplay (Codex's review, round 33). A list, and no args: the advisors take none from a player, and 'pedia' gives Sevopedia text without the pedia jumps' indices. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_PLAY_SCREENS = ("showTechChooser", "showPolicyAdvisorScreen", "showReligionScreen", "showCorporationScreen", "showForeignAdvisorScreen", "showForeignDiplomacyAdvisor", "showDomesticAdvisor", "showMilitaryAdvisor", "showEspionageAdvisor", "showInfoScreen", "showWorldAdvisorScreen", "showVictoryScreen", "showTopCivs", "showHallOfFame", "pediaShow", "pediaMain", "pediaBack", "pediaForward")


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
	if name == "fog" and args.get("on") is not None and not args.get("on"):
		return "omniscient"
	if name == "control" and args.get("control") is not None:
		iControl = int(_enum(ControlTypes, args["control"]))
		for (szControl, szRole) in _CONTROL_ROLES:
			if iControl == int(getattr(ControlTypes, szControl)):
				return szRole
	if name == "screen" and args.get("name") is not None:
		return _screenRole(str(args["name"]), args)
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
	return {"role": _state.get("role") or "all", "locked": bool(_state.get("roleLocked")), "commands": roles, "byArguments": "fog on=0 and fog=0 are omniscient; control CONTROL_WORLD_BUILDER is create, CONTROL_ADMIN_DETAILS omniscient, CONTROL_LOAD_GAME and CONTROL_QUICK_LOAD meta; screen is play for the advisors and Sevopedia navigation (_PLAY_SCREENS) without args, omniscient for Debug ones, else create; workers leaves out the city AI's builds unless advice is allowed; players under fog gives other teams' players only once met, briefly"}


def cmd_fog(args):
	# <!-- custom: The pilot began with full information only, as a debugging tool; the user then asked for play as a person would, "manage the fog" included (2026-11-13). A switch rather than a second set of commands, so the same orders and reads serve both uses. (Claude code Fable 5.2) -->
	if args.get("on") is not None:
		_state["fog"] = bool(args["on"])
	return {"fog": bool(_state.get("fog", False))}


_HELP["path"] = "The route a unit would take to a plot, before ordering it: each step's plot, the turn it is reached on (1 is this turn) and the moves left there, and the total turns. args: unit, x, y, flags (MovementFlags number, default 0), player."


def cmd_path(args):
	unit = _unit(args)
	plot = _plot(args)
	iFlags = int(args.get("flags", 0))
	iTeam = _fogTeam(args)
	# <!-- custom: With fog on, only the team's own units and the default movement flags, as some flags change what the search treats as known (Codex's review); with fog off any unit and flags, for debugging. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if iTeam >= 0 and (gc.getPlayer(unit.getOwner()).getTeam() != iTeam or iFlags != 0):
		raise ValueError("with fog on, 'path' takes the team's own units and no flags")
	text = _pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), iFlags)
	if text == "null":
		raise ValueError("no path query for unit %d to %d,%d" % (unit.getID(), plot.getX(), plot.getY()))
	return RawJson(text)


_HELP["targets"] = "The plots a unit's group could pick for an interface mode from 'unit's targetModes, as the window highlights them, e.g. mode=INTERFACEMODE_RECON or INTERFACEMODE_AIRBOMB, with the mission to send: mission unit=<id> mission=<mission> data1=x data2=y. With fog on, only plots the team has revealed. args: unit, mode, player."


def cmd_targets(args):
	# <!-- custom: A scan of all 4368 plots of the turn-271 Large baseline took 2 to 4 ms in Python (2026-11-14), so this stays out of the DLL. (Claude code Opus 5.5) -->
	unit = _unit(args)
	if not hasattr(gc, "getInterfaceModeInfo"):
		raise ValueError("this DLL predates CyGlobalContext.getInterfaceModeInfo; build or install a current one")
	# <!-- custom: Without mode it raised a bare KeyError for the first Jet Fighter (turn 285, 2026-11-14); like 'hurry', list the choices instead, the unit's targetModes. (Claude code Opus 5.5) -->
	if args.get("mode") is None:
		group = unit.getGroup()
		return {"unit": unit.getID(), "targetModes": [{"mode": gc.getInterfaceModeInfo(i).getType(), "mission": gc.getMissionInfo(gc.getInterfaceModeInfo(i).getMissionType()).getType()} for i in range(int(InterfaceModeTypes.NUM_INTERFACEMODE_TYPES)) if gc.getInterfaceModeInfo(i).getMissionType() >= 0 and group.canDoInterfaceMode(InterfaceModeTypes(i))]}
	eMode =InterfaceModeTypes(int(_enum(InterfaceModeTypes, args["mode"])))
	info = gc.getInterfaceModeInfo(int(eMode))
	if info.getMissionType() < 0:
		raise ValueError("%s picks no plot for a mission" % args["mode"])
	group = unit.getGroup()
	# <!-- custom: canDoInterfaceModeAt does not recheck that the mode applies: for the SAS Airship, a land unit, INTERFACEMODE_REBASE accepted 4191 plots (2026-11-14). Check the mode first, as the window's button does. (Claude code Opus 5.5) -->
	if not group.canDoInterfaceMode(eMode):
		raise ValueError("unit %d cannot use %s now" % (unit.getID(), args["mode"]))
	iTeam = _fogTeam(args)
	if iTeam >= 0 and gc.getPlayer(unit.getOwner()).getTeam() != iTeam:
		raise ValueError("with fog on, 'targets' takes the team's own units")
	kMap = gc.getMap()
	plots = []
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if iTeam >= 0 and not plot.isRevealed(iTeam, False):
			continue
		if group.canDoInterfaceModeAt(eMode, plot):
			plots.append({"x": plot.getX(), "y": plot.getY()})
	return {"mode": info.getType(), "mission": gc.getMissionInfo(info.getMissionType()).getType(), "plots": plots}


_HELP["messages"] = "The messages the game showed the player at the top of the screen and still lists, such as combat results, oldest first: turn, text, x, y, from (player or -1), messageType. args: since (game turn, default the previous turn), player."


def cmd_messages(args):
	iSince = args.get("since")
	if iSince is None:
		iSince = gc.getGame().getGameTurn() - 1
	text = _pilotGame("getSASPilotMessagesJson").getSASPilotMessagesJson(_playerId(args), int(iSince))
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
	# <!-- custom: The game's choose-production and choose-tech popups only show in the window and do not stop 'endturn': 22 turns ended with an empty queue and no research (2026-11-13), so the pilot has to ask what is idle. (Claude code Fable 5.2) -->
	player = _player(args)
	result = {"turnActive": player.isTurnActive()}
	result["idleCities"] = [_cityBrief(city) for city in _cities(player) if city.getOrderQueueLength() == 0]
	result["needsResearch"] = (player.getCurrentResearch() < 0)
	# <!-- custom: An automated group, such as a scout on Explore, was listed as idle every turn of the fog-on playthrough (2026-11-13), while the window does not ask for its orders; leave such groups out. (Claude code Opus 5.5) -->
	result["idleUnits"] = [_unitBrief(unit) for unit in _units(player) if unit.getGroup().readyToMove(False) and unit.getGroup().getLengthMissionQueue() == 0 and not unit.getGroup().isAutomated()]
	# <!-- custom: Choices the game asked for and the pilot holds, such as keeping or razing a captured city; production and tech popups are left out, as the two entries above cover them. (Claude code Fable 5.2) -->
	if player.getID() == gc.getGame().getActivePlayer() and hasattr(gc.getGame(), "getSASPilotPathJson"):
		result["heldPopups"] = [{"id": popup["id"], "type": popup["type"], "data1": popup["data1"], "buttons": [item["name"] for item in popup["buttons"]], "about": popup.get("about")} for popup in _popups() if popup["state"] == "HELD" and not (popup["type"] == "BUTTONPOPUP_CHOOSEPRODUCTION" or (popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] <= 0)) and not _isNotice(popup)]
	# <!-- custom: An open diplomacy screen waits for a reply as a popup does; see 'diplo'. (Claude code Opus 5.5) -->
	if player.getID() == gc.getGame().getActivePlayer():
		state = _diploState()
		if state["open"]:
			result["diplomacy"] = {"screen": _diploToken(state), "who": state["who"], "whoName": gc.getPlayer(state["who"]).getName(), "aiComment": _typeOrNone(gc.getDiplomacyInfo, state["aiComment"]), "replies": [gc.getDiplomacyInfo(response["comment"]).getType() for response in state["responses"]]}
		# <!-- custom: A tech bought from Pacal at turn 148 (2026-11-13) put its splash on display at once, and 'todo' reported nothing while the window waited on Continue; only 'turn' closes such screens, as notices. Listed here unclosed, so a check of 'todo' alone sees the window is blocked. (Claude code Opus 5.5) -->
		screens = _closeInfoScreens(False)
		if screens:
			result["infoScreens"] = screens
		# <!-- custom: A spy's Investigate City at Oporto (turn 284, 2026-11-14) opened that city's screen, which stayed over the map beside a diplomacy screen until the user pointed it out; nothing in 'todo' said so. It blocks nothing, so it is reported, not waited on; CyInterface().clearSelectedCities() or Esc closes it. (Claude code Opus 5.5) -->
		if CyInterface().isCityScreenUp():
			city = CyInterface().getHeadSelectedCity()
			result["cityScreen"] = (city and [city.getName()] or [True])[0]
		# <!-- custom: Advisors and other Python screens left open, such as the Foreign Advisor a numeric control test opened (2026-11-14); reported like the city screen, as they block nothing but cover the map. (Claude code Opus 5.5) -->
		others = [szName for szName in _openScreens() if szName != "cityScreen"]
		if others:
			result["openScreens"] = others
	# <!-- custom: A free-tech chooser already on display, as after loading a save before the pilot held popups again, is not in heldPopups, so 'endturn --turns' did not stop for it (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Only while the game still counts a free tech as owed: after 'freetech' took one through a displayed chooser, the chooser stayed on screen, and listing it kept 'todo' waiting for good (2026-11-13). (Claude code Opus 5.5) -->
	if player.getID() == gc.getGame().getActivePlayer() and hasattr(gc.getGame(), "getSASPilotPathJson"):
		displayed = [popup for popup in _popups() if popup["state"] == "DISPLAYED" and popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0]
		if displayed and _pilotGame("isSASPilotChoosingFreeTech").isSASPilotChoosingFreeTech():
			result["freeTechOwed"] = displayed[0]["data1"]
	return result


# <!-- custom: F6 and Sevopedia draw these relationships from loaded infos. Index the rules lazily in this module so polling and ordinary gameplay pay nothing, and a Pilot hot reload rebuilds the index on demand. Research progress and diplomacy come from the current game on each request. (GPT-6.1-Sol) -->
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
	for node in _techNodes():
		for relation in ("all", "any"):
			for tech in node["requires"][relation]:
				effects[tech].append({"effect": "prerequisite", "target": node["type"], "group": relation})
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
				_recordTechEffect(effects, info.getFeatureTech(j), "allowsFeatureRemoval", gc.getFeatureInfo(j).getType(),
					{"build": info.getType(), "buildTech": _typeOrNone(gc.getTechInfo, iTech), "production": info.getFeatureProduction(j)})
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


# <!-- custom: Read the Info screen's completed-turn series without opening it. CvInfoScreen's partial score rule allows the public score once enough turns have passed since contact, while the other series require visible demographics. (GPT-6.1-Sol) -->
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
	if metric != "score":
		return None
	if player.hasEverSeenDemographics(other.getID()):
		return first
	met = team.getHasMetTurn(other.getTeam())
	if partial and current - met >= 5:
		return max(first, met)
	return None


def _historyGraph(args, result):
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
	if kind == "history":
		if szType is not None:
			raise ValueError("the history graph takes metric instead of type")
		return _historyGraph(args, result)
	if kind == "relations":
		if szType is not None:
			raise ValueError("the relations graph takes no type filter")
		query = dict(args)
		del query["kind"]
		query["graph"] = True
		result = cmd_relations(query)
		result["kind"] = kind
		return result
	if kind == "promotions":
		nodes = _promotionNodes()
	elif kind in ("tech", "upgrades"):
		iCiv = _player(args).getCivilizationType()
		result["civilization"] = gc.getCivilizationInfo(iCiv).getType()
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
		if kind == "upgrades":
			result["upgradesFrom"] = [node["type"] for node in _upgradeNodes(iCiv) if szType in node["upgradesTo"]]
		if kind == "promotions":
			result["requiredBy"] = [{"type": node["type"], "group": group} for node in _promotionNodes()
				for group in ("all", "any") if szType in node["requires"][group]]
	result["nodes"] = nodes
	return result


_HELP["tech"] = "Show one technology: rule effects and prerequisites, plus live research cost, progress, availability and which immediate prerequisites are missing. args: type (TECH_ type), player."


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
				and not team.isHasTech(gc.getInfoTypeForString(tech))]
		node["effects"].append(row)
	requires = node["requires"]
	node["missingAll"] = [tech for tech in requires["all"] if not team.isHasTech(gc.getInfoTypeForString(tech))]
	node["missingAny"] = []
	if requires["any"] and not [tech for tech in requires["any"] if team.isHasTech(gc.getInfoTypeForString(tech))]:
		node["missingAny"] = requires["any"]
	node["known"] = bool(team.isHasTech(iTech))
	node["canResearch"] = bool(player.canResearch(iTech, False))
	node["cost"] = team.getResearchCost(iTech)
	node["progress"] = team.getResearchProgress(iTech)
	return node


_HELP["research"] = "Without args: the techs the player can research now, each with its turns, and the research queue. With tech: research it; a tech not available yet is queued after its missing prerequisites, as a shift-click in the tech tree does. append=1 adds to the queue instead of replacing it. With effects=1, include the effects of each available tech. args: tech (TECH_ type), append, effects, player."


def cmd_research(args):
	player = _player(args)
	if args.get("tech") is None:
		# <!-- custom: The list first held only the names, so choosing a tech meant a 'py' call per tech for what the window's tech chooser shows at a glance, its turns (fog-on playthrough, 2026-11-13). Each entry now has its turns at the current rate, its cost and the progress already made. (Claude code Opus 5.5) -->
		team = gc.getTeam(player.getTeam())
		available = [{"tech": gc.getTechInfo(i).getType(), "turns": player.getResearchTurnsLeft(i, True), "cost": team.getResearchCost(i), "progress": team.getResearchProgress(i)} for i in range(gc.getNumTechInfos()) if player.canResearch(i, False)]
		if args.get("effects"):
			effects = _techEffects(player.getCivilizationType())
			for entry in available:
				entry["effects"] = effects[entry["tech"]]
		return {"available": available, "queue": _researchQueue(player)}
	iTech = _typedIndex(args["tech"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	# <!-- custom: Only techs available now were taken, so 'tech=TECH_BRONZE_WORKING' was refused while Mining was its one missing prerequisite (fog-on playthrough, 2026-11-13). CvPlayer::pushResearch queues the missing prerequisites first, as the tech tree's shift-click does, so take any tech the player could ever research and does not have. (Claude code Opus 5.5) -->
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


def _researchQueue(player):
	# <!-- custom: CyPlayer exposes no queue list, only each tech's position in it (1 is the current one), so rebuild the order from getQueuePosition. (Claude code Opus 5.5) -->
	queued = [(player.getQueuePosition(i), i) for i in range(gc.getNumTechInfos()) if player.isResearchingTech(i)]
	queued.sort()
	return [{"tech": gc.getTechInfo(i).getType(), "turns": player.getResearchTurnsLeft(i, False)} for (iPosition, i) in queued]


_HELP["info"] = "An XML info by type, e.g. UNIT_WARRIOR: every zero-argument get/is getter of its info object. args: type."


def cmd_info(args):
	szType = args["type"]
	iType = _infoIndex(szType)
	getter = None
	# <!-- custom: The type's prefix is not enough to pick the getter (BUILDINGCLASS_ vs BUILDING_, SPECIALBUILDING_...), so try each getXInfo and keep the one whose entry has this type. (Claude code Fable 5.2) -->
	for name in dir(gc):
		if name.startswith("get") and name.endswith("Info") and not name.startswith("getNum"):
			# <!-- custom: Only tables whose count getter exists and covers the index: an index past a table's end could reach native code unchecked (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			szCount = "getNum" + name[3:] + "s"
			if not hasattr(gc, szCount) or iType >= getattr(gc, szCount)():
				continue
			try:
				info = getattr(gc, name)(iType)
				if info is not None and info.getType() == szType:
					getter = name
					break
			except Exception:
				pass
	if getter is None:
		raise ValueError("no gc.get*Info yields %s" % szType)
	result = describe(info)
	_nameInfoIndices(result)
	result["_index"] = iType
	result["_getter"] = getter
	return result


# <!-- custom: Getters that return another info's index, with that info's getter and count. Codex's review found that the first version, which went by the getter's ending (...Tech, ...Bonus), would read a quantity as an index, getHealthBonus being an amount and getFreeSpecialist a count in buildings, and could ask a table for an entry out of range; so only these names, whose meaning is the same in every BtS info that has them, and within range. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_INDEX_GETTERS = {
	"getPrereqAndTech": ("getTechInfo", "getNumTechInfos"),
	"getObsoleteTech": ("getTechInfo", "getNumTechInfos"),
	"getTechReveal": ("getTechInfo", "getNumTechInfos"),
	"getTechCityTrade": ("getTechInfo", "getNumTechInfos"),
	"getTechObsolete": ("getTechInfo", "getNumTechInfos"),
	"getPrereqAndBonus": ("getBonusInfo", "getNumBonusInfos"),
	"getPrereqReligion": ("getReligionInfo", "getNumReligionInfos"),
	"getStateReligion": ("getReligionInfo", "getNumReligionInfos"),
}


def _nameInfoIndices(result):
	# <!-- custom: 'info type=UNIT_CATAPULT' gave getPrereqAndTech 32, and finding that 32 is TECH_MATHEMATICS took a 'py' call (fog-on playthrough, turn 115, 2026-11-13). These getters also get <getter>Type with the type's name; -1 and out-of-range values stay as they are. (Claude code Opus 5.5) -->
	for name in result.keys():
		if name not in _INDEX_GETTERS:
			continue
		value = result[name]
		(szGetter, szCount) = _INDEX_GETTERS[name]
		if isinstance(value, int) and not isinstance(value, bool) and value >= 0 and value < getattr(gc, szCount)():
			result[name + "Type"] = getattr(gc, szGetter)(value).getType()


def describe(target):
	# <!-- custom: Calls every zero-argument method named get*, is*, can*, has* or count*; a method that needs arguments raises and is skipped. Meant for info objects; also in the 'py' namespace for players, cities and units. (Claude code Fable 5.2) -->
	result = {}
	for name in dir(target):
		if name.startswith("get") or name.startswith("is") or name.startswith("can") or name.startswith("has") or name.startswith("count"):
			try:
				value = getattr(target, name)()
			except Exception:
				continue
			if value is None or isinstance(value, (int, long, float, str, unicode, bool)):
				result[name] = value
	return result


# Order commands

_HELP["mission"] = "Give a unit's group a mission, e.g. mission=MISSION_MOVE_TO data1=x data2=y, MISSION_FORTIFY, MISSION_BUILD data1=BUILD_ type. args: unit, mission, data1, data2, flags, append, player."


def cmd_mission(args):
	unit = _unit(args)
	group = unit.getGroup()
	eMission = _enum(MissionTypes, args["mission"])
	iData1 = args.get("data1", -1)
	if isinstance(iData1, (str, unicode)) and eMission == MissionTypes.MISSION_BUILD:
		iData1 = _typedIndex(iData1, "BUILD_", gc.getNumBuildInfos(), gc.getBuildInfo)
	elif isinstance(iData1, (str, unicode)):
		iData1 = _infoIndex(iData1)
	iData1 = int(iData1)
	iData2 = int(args.get("data2", -1))
	plot = unit.plot()
	# <!-- custom: An appended mission starts where the queue ends, as a shift-click in the window does; 'mission=MISSION_BUILD data1=BUILD_COTTAGE append=1' after a 'move' was first refused because it was checked on the Worker's current plot (fog-on playthrough, 2026-11-13). lastMissionPlot is the game's own end of the queue. (Claude code Opus 5.5) -->
	bQueued = bool(args.get("append", False)) and group.getLengthMissionQueue() > 0
	if bQueued:
		plot = group.lastMissionPlot()
	# <!-- custom: The check above then refused 'MISSION_FOUND append=1' right after a 'move': canStartMission returns false while the group is busy, as it was a few ms into its move, and the same call passed seconds later (2026-11-13). isBusy is not exposed to Python, and the window does not check a shift-clicked mission either; the game checks it when it starts and drops it if invalid, and the unit then shows in 'todo'. So a mission queued behind others is not checked here. (Claude code Opus 5.5) -->
	# <!-- custom: The data checks run for an immediate mission too: Codex's review found that a move given at once with coordinates off the map, or a build index out of range, reached native code that assumes them valid, as only queued missions were checked. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_checkMissionData(eMission, iData1, iData2, bQueued)
	# <!-- custom: Nor a new order for a unit with no moves left, which the window takes and starts next turn: at turn 118 of the turn-0 game (2026-11-14) a Worker busy clearing jungle was given a replacement queue, which this check refused as "moves left 0", so its old Mine order stayed. The game checks the order when it starts, as for a queued one. (Claude code Opus 5.5) -->
	if not bQueued and unit.movesLeft() > 0 and not group.canStartMission(eMission, iData1, iData2, plot, False):
		# <!-- custom: Two Field Guns refused a move to Ecbatana on turn 285 (2026-11-14) with no reason given: they were in a 9-unit group that a move of one of its units had already sent there. Say the moves left and the group, so such a refusal explains itself. (Claude code Opus 5.5) -->
		szWhy = "moves left %d, group %d of %d unit(s)" % (unit.movesLeft(), group.getID(), group.getNumUnits())
		if group.getLengthMissionQueue() > 0:
			szWhy += ", whose current mission is %s" % gc.getMissionInfo(group.getMissionType(0)).getType()
		raise ValueError("unit %d cannot start %s (%s, %s) now (%s)" % (unit.getID(), args["mission"], iData1, iData2, szWhy))
	# <!-- custom: No mission AI plot or unit, as the window's own orders give none (CvNetPushMission). The pilot first passed the plot above, which pushMission records as the group's mission AI plot while the group can move: a Work Boat sent by 'move' from (39,32) then had fishing boats appended after arriving with no moves left, and at the next turn the KI#176 stale-target guard in continueMission cancelled the build, as the boat was not at (39,32) (fog-on playthrough, turns 116-118, 2026-11-13). See KI#176.
	# CySelectionGroup.pushMission dereferenced None until that same day's DLL, hence the binding check. (Claude code Opus 5.5) -->
	_pilotGame("isSASPilotChoosingFreeTech")
	iUnit = unit.getID()
	iOwner = unit.getOwner()
	group.pushMission(eMission, iData1, iData2, int(args.get("flags", 0)), bool(args.get("append", False)), True, MissionAITypes.NO_MISSIONAI, None, None)
	# <!-- custom: Looked up again by ID: a Work Boat building fishing boats is used up at once, and reading the old object then raised an unidentifiable C++ exception instead of reporting it gone (turn 118, 2026-11-13). (Claude code Opus 5.5) -->
	unit = gc.getPlayer(iOwner).getUnit(iUnit)
	if unit is None or unit.isNone() or unit.isDead():
		return {"unitGone": True}
	return _unitFull(unit)


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


_HELP["map"] = "A text map of the known world, row by row from the north, as the window's map shows it: C our city, c another's city, ~ water, ^ peak, h hills, f forest or jungle, x another's land, . other land, space unknown; u marks a plot holding one of our units. Columns are x from 'x0', rows y from 'y1' down. With fog on, only what the team has revealed. args: x0, x1, y0, y1 (default the known area plus one plot), player."


def cmd_map(args):
	# <!-- custom: Planning scouting and city sites needed a picture of what is known: at turn 25 of the turn-0 game (2026-11-14) only 150 of 3168 plots were revealed, which the user's advice to scout first made the question; 'routes' draws only our own land. Written first as a 'py' snippet, then kept as a command. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	# <!-- custom: Codex's review: player= a rival would mark that rival's units under fog. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_requireOwnTeamUnderFog(args, player, "the map")
	iTeam = _fogTeam(args)
	kMap = gc.getMap()
	known = []
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if iTeam < 0 or plot.isRevealed(iTeam, False):
			known.append((plot.getX(), plot.getY()))
	if not known:
		raise ValueError("no plot is known")
	x0 = int(args.get("x0", max(0, min([x for (x, y) in known]) - 1)))
	x1 = int(args.get("x1", min(kMap.getGridWidth() - 1, max([x for (x, y) in known]) + 1)))
	y0 = int(args.get("y0", max(0, min([y for (x, y) in known]) - 1)))
	y1 = int(args.get("y1", min(kMap.getGridHeight() - 1, max([y for (x, y) in known]) + 1)))
	iForest = gc.getInfoTypeForString("FEATURE_FOREST")
	iJungle = gc.getInfoTypeForString("FEATURE_JUNGLE")
	ours = {}
	for unit in _units(player):
		ours[(unit.getX(), unit.getY())] = True
	rows = []
	for y in range(y1, y0 - 1, -1):
		line = []
		for x in range(x0, x1 + 1):
			plot = kMap.plot(x, y)
			if plot.isNone() or (iTeam >= 0 and not plot.isRevealed(iTeam, False)):
				line.append(" ")
				continue
			# <!-- custom: Under fog, the owner the team last saw, as the window's map shows it: the live owner would tell of borders that moved out of sight. (Claude code Opus 5.5) -->
			iOwner = plot.getOwner()
			if iTeam >= 0:
				iOwner = plot.getRevealedOwner(iTeam, False)
			# <!-- custom: Under fog, a city only once the team has seen it: a city founded since on an explored plot showed as c from the live plot (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			bCity = plot.isCity()
			if bCity and iTeam >= 0 and not plot.getPlotCity().isRevealed(iTeam, False):
				bCity = False
			if bCity:
				if iOwner == player.getID():
					line.append("C")
				else:
					line.append("c")
			elif ours.has_key((x, y)):
				line.append("u")
			elif plot.isWater():
				line.append("~")
			elif plot.isPeak():
				line.append("^")
			elif iOwner >= 0 and iOwner != player.getID():
				line.append("x")
			elif plot.isHills():
				line.append("h")
			elif plot.getFeatureType() == iForest or plot.getFeatureType() == iJungle:
				line.append("f")
			else:
				line.append(".")
		rows.append("%3d %s" % (y, "".join(line)))
	return {"x0": x0, "y1": y1, "known": len(known), "plots": kMap.numPlots(), "rows": rows}


_HELP["reminders"] = "What a player would want pointed out, beyond what 'todo' says must be decided before the turn ends: no research, an empty build queue, a starving or angry city, a wounded unit outside our borders, gold that runs out within ten turns at the current rate, and techs we could trade to a met player now. Each entry has its check, a text and the thing it is about. Only what the player's own screens show. args: player."


def _remindResearch(player, args):
	if player.getCurrentResearch() < 0:
		return [{"text": "no research chosen"}]
	return []


def _remindCities(player, args):
	result = []
	(city, iterator) = player.firstCity(False)
	while city:
		name = city.getName()
		if city.getOrderQueueLength() == 0:
			result.append({"text": "%s builds nothing" % name, "city": city.getID()})
		if city.foodDifference(True) < 0:
			result.append({"text": "%s starves: food %d a turn" % (name, city.foodDifference(True)), "city": city.getID()})
		if city.angryPopulation(0) > 0:
			result.append({"text": "%s has %d angry citizens" % (name, city.angryPopulation(0)), "city": city.getID()})
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
	# <!-- custom: Builds a city has hammers in but is not making now, which the city keeps (CvCity's per-unit and per-building production): the user advised at turn 119 of the turn-0 game (2026-11-14) not to leave a nearly done build, as a Worker one turn from done, after switching the queue; Hastings had switched from an Axeman to a Worker. Each with its stored hammers, its cost and the turns it would take now; not every one is worth finishing, which stays the agent's choice. (Claude code Opus 5.5) -->
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
				result.append({"text": "%s has %d of %d hammers in %s, %d turns from done now" % (city.getName(), iStored, player.getUnitProductionNeeded(i), gc.getUnitInfo(i).getType(), city.getUnitProductionTurnsLeft(i, 0)), "city": city.getID(), "item": gc.getUnitInfo(i).getType()})
		for i in range(gc.getNumBuildingInfos()):
			iStored = city.getBuildingProduction(i)
			if iStored > 0 and i != iCurrentBuilding and city.canConstruct(i, False, False, False):
				result.append({"text": "%s has %d of %d hammers in %s, %d turns from done now" % (city.getName(), iStored, player.getBuildingProductionNeeded(i), gc.getBuildingInfo(i).getType(), city.getBuildingProductionTurnsLeft(i, 0)), "city": city.getID(), "item": gc.getBuildingInfo(i).getType()})
	return result


def _remindLosses(player, args):
	# <!-- custom: Units lost since the previous turn, from the messages the player was shown: at turns 84-89 of the turn-0 game (2026-11-14) a barbarian Archer killed the two Workers chopping near Nottingham, and the agent, reading each turn's digest cut to its last lines, missed "your Worker was destroyed" until the units were found gone at turn 90. Matched on the English texts of CvUnit's combat and capture messages, so another language would not match. (Claude code Opus 5.5) -->
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
	if CyInterface().isCityScreenUp():
		result.append("cityScreen")
	return result


_HELP["closescreens"] = "Close the screens left open in the window, as Esc or their Exit button does: every advisor or other Python screen 'todo' lists in openScreens, and the city screen; or only one with name (as openScreens names it, or cityScreen). Returns what was closed. args: name."


def cmd_closescreens(args):
	# <!-- custom: The pilot could open an advisor ('control', 'screen') but not close it: the Foreign Advisor from a test (2026-11-14) took an Esc sent to the window. hideScreen is what an advisor's Exit button calls; the city screen closes by clearing the selected cities, as noted in 'todo'. (Claude code Opus 5.5) -->
	import CvScreensInterface
	szOnly = args.get("name")
	closed = []
	for szName in _openScreens():
		if szOnly is not None and szName != szOnly:
			continue
		if szName == "cityScreen":
			CyInterface().clearSelectedCities()
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
	# <!-- custom: Popups on display in the window, as against those the pilot holds, which 'todo' lists. Read through the DLL, so only with one that has it. (Claude code Opus 5.5) -->
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
	# <!-- custom: Seafaring, 2 turns of research that no neighbour had, bought Construction and Metal Casting at turn 59 of the turn-0 game (2026-11-14); a tech we could give is worth a look each turn. Taken from 'techs', which applies the fog rules. (Claude code Opus 5.5) -->
	result = []
	market = cmd_techs({"player": player.getID(), "fog": args.get("fog")})
	for entry in market["weCouldGive"]:
		if entry["techs"]:
			result.append({"text": "%s could be offered %s" % (entry["name"], ", ".join(entry["techs"])), "player": entry["player"]})
	return result


def _remindSleepingWorkers(player, args):
	# <!-- custom: The activity is the group's (CySelectionGroup.getActivityType), as CyUnit has no getter for it. A sleeping unit is not idle, so 'todo' and the turn's waits never list it: three Workers the agent had put to sleep near York at turns 155 to 157 of the turn-0 game (2026-11-14) slept unnoticed while York kept a bare grass hill, a marsh and two forests, until the user pointed out that York was under-improved. (Claude code Opus 5.5) -->
	result = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.workRate(True) > 0 and unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP:
			result.append({"text": "%s %d sleeps at %d,%d; 'workers' lists what its cities still need" % (unit.getUnitType() >= 0 and gc.getUnitInfo(unit.getUnitType()).getType() or "unit", unit.getID(), unit.getX(), unit.getY()), "unit": unit.getID()})
		(unit, it) = player.nextUnit(it, False)
	return result


def _remindUnimproved(player, args):
	# <!-- custom: Resources inside our borders that supply nothing yet though we have the tech for a build that would connect them: at turn 156 of the turn-0 game (2026-11-14) the Clam at 22,31 sat in Coventry's borders, outside every city's radius, until the user pointed out that a Work Boat connects it for health all the same. The same check catches an improvement pillaged by barbarians or rivals, as the plot then reads unconnected. Taken from 'resources', which applies the fog rules. (Claude code Opus 5.5) -->
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
	for entry in cmd_resources({"player": player.getID(), "fog": args.get("fog")})["resources"]:
		if entry["owner"] != player.getID() or entry.get("connected"):
			continue
		builds = [build["build"] for build in entry["builds"] if build["haveTech"]]
		if builds:
			szText = "%s at %d,%d is in our borders but supplies nothing; %s would connect it" % (entry["bonus"], entry["x"], entry["y"], " or ".join(builds))
			row = {"bonus": entry["bonus"], "x": entry["x"], "y": entry["y"]}
			if onTheWay.has_key((entry["x"], entry["y"])):
				row["unitOnTheWay"] = onTheWay[(entry["x"], entry["y"])]
				szText = szText + " (unit %d is on its way)" % row["unitOnTheWay"]
			for iUnit, szCity in queued.items():
				for szBuild in builds:
					if gc.getUnitInfo(iUnit).getBuilds(gc.getInfoTypeForString(szBuild)):
						row["inProduction"] = {"unit": gc.getUnitInfo(iUnit).getType(), "city": szCity}
				if row.has_key("inProduction"):
					szText = szText + " (%s is in %s's queue)" % (row["inProduction"]["unit"], row["inProduction"]["city"])
					break
			row["text"] = szText
			result.append(row)
	return result


def _remindExports(player, args):
	# <!-- custom: At turn 118 of the turn-0 game (2026-11-14) a Pig sale to Gilgamesh was signed with our only Iron in it too, and nothing said so: the Iron read unconnected for seven turns and no city could train a Swordsman. Each resource we give away while none is left for us. (Claude code Opus 5.5) -->
	result = []
	for deal in cmd_deals({"player": player.getID()})["deals"]:
		for item in deal["weGive"]:
			if item["item"] == "TRADE_RESOURCES" and player.getNumAvailableBonuses(item["data"]) == 0:
				result.append({"text": "we export our only %s to %s (since turn %d, deal %d); it can be cancelled from 'deals' once the game allows" % (item.get("what"), deal["name"], deal["sinceTurn"], deal["id"]), "bonus": item.get("what"), "player": deal["with"]})
	return result


# <!-- custom: The user asked for reminders the game does not give, so no turn is lost to an unnoticed gap (2026-11-14), made of small checks so each new reminder is one function in this list. Each sees only what the player's own screens show. (Claude code Opus 5.5) -->
def _remindIdleGarrison(player, args):
	# <!-- custom: Fortified is read as getFortifyTurns() > 0: ActivityTypes has no ACTIVITY_FORTIFY in Python, and the first version broke every 'endturn' with an AttributeError. (Claude code Opus 5.5) -->
	# <!-- custom: Military units fortified or asleep in a city, with the nearest foreign unit the team sees and how much of the map it has revealed, so an agent can weigh sending one out: early in the Continents game of 2026-11-14 the Archer was sent home to garrison while nothing threatened and the map was mostly unknown, and the user pointed out that it should explore. Usually, not always (the user), so the reminder states the facts and leaves the call. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	kMap = gc.getMap()
	idle = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and unit.canAttack() and unit.plot().isCity() and (unit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SLEEP or unit.getFortifyTurns() > 0):
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
	result = []
	for unit in idle:
		near = None
		for (x, y) in foreign:
			iDist = max(abs(unit.getX() - x), abs(unit.getY() - y))
			if near is None or iDist < near:
				near = iDist
		szNear = near is None and "no foreign military unit in sight" or "nearest foreign military unit %d plots away" % near
		result.append({"text": "%s %d waits in %s (%s; %d per mille of the map revealed)" % (gc.getUnitInfo(unit.getUnitType()).getType(), unit.getID(), unit.plot().getPlotCity().getName(), szNear, iPerMille), "unit": unit.getID(), "nearestForeign": near, "revealedPerMille": iPerMille})
	return result


def _remindHuts(player, args):
	# <!-- custom: Goody huts the team has seen, with the nearest of our land units and its distance in plots: huts give techs, maps and gold early, and rivals' scouts take them too, so an agent scouting should see them all at once (the user, Continents game of 2026-11-14, after three huts in the first runs gave Mining, a map and research). Only huts as the team last saw them. (Claude code Opus 5.5) -->
	iTeam = player.getTeam()
	iHut = gc.getInfoTypeForString("IMPROVEMENT_GOODY_HUT")
	if iHut < 0:
		return []
	units = []
	(unit, it) = player.firstUnit(False)
	while unit:
		if unit.getDomainType() == DomainTypes.DOMAIN_LAND and unit.canMove():
			units.append(unit)
		(unit, it) = player.nextUnit(it, False)
	result = []
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
			row["text"] = "goody hut at %d,%d (%s)" % (plot.getX(), plot.getY(), szNear)
			result.append(row)
	return result


def _remindExposed(player, args):
	# <!-- custom: Our units outside cities within two plots of a barbarian or animal unit the team sees, with their moves left: in the scouting trial (run 3, turn 33) the Scout ended its turn beside a visible Bear and was killed, and nothing pointed at it (the user caught it). Animals mostly move one plot, so two keeps a turn's margin. (Claude code Opus 5.5) -->
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
	# <!-- custom: With no city yet, a Settler waits while other units still have moves: moving them first can reveal a better site before the Settler commits. The user's lesson from the scouting trial (2026-11-14): runs 1 and 2 founded on turn 0 before the Warrior moved; run 3 sent it to the 19,18 hill first, which confirmed the site. (Claude code Opus 5.5) -->
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


def _remindIdleImprovements(player, args):
	# <!-- custom: An improved plot of a city's that no city works while that city works a plot with no improvement, as its city screen shows. With the governor off, nothing moves a citizen onto a new improvement: in the scouting trial (2026-11-14) the Clam's fishing boats sat unworked for six turns, then the new Banana plantation for two, until the user or the agent noticed. A plain fact; which plot is better stays the agent's call. (Claude code Opus 5.5) -->
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
		if idle and bare:
			result.append({"text": "%s does not work %s while it works %s, which have no improvement" % (city.getName(), ", ".join(["%s at %d,%d" % (szType, x, y) for (x, y, szType) in idle]), ", ".join(["%d,%d" % (x, y) for (x, y) in bare])), "city": city.getID(), "idle": [[x, y] for (x, y, szType) in idle], "unimprovedWorked": [[x, y] for (x, y) in bare]})
		(city, it) = player.nextCity(it, False)
	return result


_REMINDER_CHECKS = (("huts", _remindHuts), ("idleGarrison", _remindIdleGarrison), ("exposed", _remindExposed), ("scoutBeforeFounding", _remindScoutBeforeFounding), ("research", _remindResearch), ("cities", _remindCities), ("wounded", _remindWounded), ("gold", _remindGold), ("trades", _remindTrades), ("screens", _remindScreens), ("losses", _remindLosses), ("unfinished", _remindUnfinished), ("exports", _remindExports), ("unimproved", _remindUnimproved), ("sleepingWorkers", _remindSleepingWorkers), ("idleImprovements", _remindIdleImprovements))


def cmd_reminders(args):
	player = gc.getPlayer(_playerId(args))
	_requireOwnTeamUnderFog(args, player, "reminders")
	result = []
	for (szCheck, check) in _REMINDER_CHECKS:
		for entry in check(player, args):
			entry["check"] = szCheck
			result.append(entry)
	return {"reminders": result}


_HELP["resources"] ="Every resource the team knows of: plot, type, owner (-1 unclaimed), improvement, and each build that connects it with its tech and whether we have that tech; resources on our land first. Shows what a tech would open, e.g. Agriculture's Plantations. args: player."


def cmd_resources(args):
	# <!-- custom: The user's advice at turn 37 of the turn-0 game (2026-11-14), on seeing a Banana: check resources first. A 'py' listing showed the Banana needs a Plantation, which SAS gives with Agriculture, as do five more resources nearby, so Agriculture moved ahead of Masonry; kept as a command, as that check belongs to every opening.
	# Under fog, the resources and owners the team has seen, as the map shows them. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	# <!-- custom: Codex's review: player= a rival would read that rival's revealed plots and techs under fog. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_requireOwnTeamUnderFog(args, player, "the resource list")
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	bFog = _fogTeam(args) >= 0
	kMap = gc.getMap()
	# <!-- custom: Which builds connect each resource, worked out once per resource type: a build's improvement must trade that resource (isImprovementBonusTrade). (Claude code Opus 5.5) -->
	connectors = {}
	result = []
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if bFog and not plot.isRevealed(iTeam, False):
			continue
		iBonus = plot.getBonusType(iTeam)
		if iBonus < 0:
			continue
		if not connectors.has_key(iBonus):
			builds = []
			for k in range(gc.getNumBuildInfos()):
				info = gc.getBuildInfo(k)
				iImprovement = info.getImprovement()
				if iImprovement >= 0 and gc.getImprovementInfo(iImprovement).isImprovementBonusTrade(iBonus):
					iTech = info.getTechPrereq()
					szTech = None
					if iTech >= 0:
						szTech = gc.getTechInfo(iTech).getType()
					builds.append({"build": info.getType(), "tech": szTech, "haveTech": iTech < 0 or team.isHasTech(iTech)})
			connectors[iBonus] = builds
		iOwner = plot.getOwner()
		iImprovement = plot.getImprovementType()
		if bFog:
			iOwner = plot.getRevealedOwner(iTeam, False)
			iImprovement = plot.getRevealedImprovementType(iTeam, False)
		entry = {"x": plot.getX(), "y": plot.getY(), "bonus": gc.getBonusInfo(iBonus).getType(), "owner": iOwner, "improvement": _typeOrNone(gc.getImprovementInfo, iImprovement), "builds": connectors[iBonus]}
		# <!-- custom: Whether the resource reaches our network, for our own plots: at turn 90 of the turn-0 game the user saw the Banana by London still unconnected, as were the two Pigs, all improved but with no route from their plot to a city (2026-11-14). The list showed the Plantation and nothing about the link, and the agent took improved for connected. The resource bar shows a player this. (Claude code Opus 5.5) -->
		# <!-- custom: Whether this plot supplies the resource: its network carries it (isPlotGroupConnectedBonus) and the plot itself feeds it, by a city or an improvement that trades it. The network test alone counts every source in the group, so an unimproved Cow beside a pastured one on the same roads read as connected (Codex's review, round 35). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if iOwner == player.getID():
			bFeeds = plot.isCity() or (plot.getImprovementType() >= 0 and gc.getImprovementInfo(plot.getImprovementType()).isImprovementBonusTrade(iBonus))
			entry["connected"] = bool(bFeeds and plot.isPlotGroupConnectedBonus(player.getID(), iBonus))
		result.append(entry)
	result.sort(lambda a, b: cmp((a["owner"] != player.getID(), a["owner"] >= 0, a["bonus"]), (b["owner"] != player.getID(), b["owner"] >= 0, b["bonus"])))
	return {"resources": result}


_HELP["scout"] ="Where a scout could step next: each plot next to the unit it can enter now, with how many unknown plots it would reveal (seeing one plot around, two from hills), its defense bonus, and the animals and barbarians we see within two plots of it, in a fixed order (north-west first, row by row). Also the unit's damage. Facts only: 'advise about=scout' ranks the steps. args: unit, player."


def cmd_scout(args):
	# <!-- custom: Automated exploring lost a Warrior at turn 35 of the turn-0 game (2026-11-14): it beat a Lion at 22% attacker odds, kept exploring at 15 HP and a Panther killed it, as automation neither heals nor avoids animals. The user's advice: scout by hand, avoid animals unless the odds are great (they are strong in SAS and give little), end on hills or forest.
	# So this lays out each next step with what it reveals and how safe it is, from what the team knows only, and leaves the choice to the agent. (Claude code Opus 5.5) -->
	unit = _unit(args)
	# <!-- custom: Codex's review: under fog, a rival's unit would show what that rival sees. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_requireOwnTeamUnderFog(args, gc.getPlayer(unit.getOwner()), "scouting")
	iTeam = unit.getTeam()
	kMap = gc.getMap()
	enemies = []
	for dx in range(-4, 5):
		for dy in range(-4, 5):
			plot = kMap.plot(unit.getX() + dx, unit.getY() + dy)
			if plot.isNone() or not plot.isVisible(iTeam, False):
				continue
			for i in range(plot.getNumUnits()):
				other = plot.getUnit(i)
				# <!-- custom: Only units the window would draw: not one invisible to our team, nor one carried as cargo (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if other.isBarbarian() and not other.isInvisible(iTeam, False) and not other.isCargo():
					enemies.append((plot.getX(), plot.getY(), gc.getUnitInfo(other.getUnitType()).getType(), other.isAnimal()))
	steps = []
	for dx in (-1, 0, 1):
		for dy in (-1, 0, 1):
			if dx == 0 and dy == 0:
				continue
			plot = kMap.plot(unit.getX() + dx, unit.getY() + dy)
			# <!-- custom: A plot the team has never seen gives no terrain or defense (Codex's review); a unit's neighbours are almost always revealed. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if plot.isNone() or not plot.isRevealed(iTeam, False) or not unit.canMoveInto(plot, False, False, False):
				continue
			iSight = 1
			if plot.isHills():
				iSight = 2
			iReveal = 0
			for sx in range(-iSight, iSight + 1):
				for sy in range(-iSight, iSight + 1):
					seen = kMap.plot(plot.getX() + sx, plot.getY() + sy)
					if not seen.isNone() and not seen.isRevealed(iTeam, False):
						iReveal += 1
			near = []
			for (ex, ey, szType, bAnimal) in enemies:
				if max(abs(ex - plot.getX()), abs(ey - plot.getY())) <= 2:
					near.append({"x": ex, "y": ey, "type": szType, "animal": bAnimal})
			steps.append({"x": plot.getX(), "y": plot.getY(), "reveals": iReveal, "defense": plot.defenseModifier(iTeam, False, False), "hills": plot.isHills(), "feature": _typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "enemiesNear": near})
	# <!-- custom: The ranking (most revealed, then fewest enemies near, then the best defense) moved to 'advise about=scout', as a judgment of ours: the user's facts-versus-advice split (2026-11-14). The steps keep the loop's order, so the same position gives the same list. (Claude code Opus 5.5) -->
	return {"unit": unit.getID(), "x": unit.getX(), "y": unit.getY(), "damage": unit.getDamage(), "movesLeft": unit.movesLeft(), "steps": steps}


_HELP["bonustrade"] = "The Foreign Advisor's Bonuses tab: our resources with how many we have (spare when more than one) and who would import each; and per leader met, whether our trade networks connect, the most gold per turn they would pay (when gold trading is open and they will talk), and which resources they would import from us, will export, won't export, and which we do not need. A resource sale or swap starts here; 'price' then asks the deal's price. args: player."


def cmd_bonustrade(args):
	# <!-- custom: The user advised at turn 111 of the turn-0 game (2026-11-14) trading spare resources actively, for gold or what we lack, and pointed to the Foreign Advisor's Bonuses tab and its hover over our resources ("Will import: Augustus (4)" in 1.514_foreign_advisor (2).JPG). The agent had asked four leaders one by one with 'price' and learned only that nobody wanted a Pig. This follows CvForeignAdvisor.drawResourceDeals (advc.036, advc.073) for an AI-facing player: the same tests, so what it lists is what the tab shows. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	_requireOwnTeamUnderFog(args, player, "the resource trade table")
	team = gc.getTeam(player.getTeam())
	tradeData = TradeData()
	tradeData.ItemType = TradeableItems.TRADE_RESOURCES
	ours = []
	for iBonus in range(gc.getNumBonusInfos()):
		iCount = player.getNumTradeableBonuses(iBonus)
		if iCount > 0:
			ours.append({"bonus": gc.getBonusInfo(iBonus).getType(), "have": iCount, "importers": []})
	byBonus = dict([(entry["bonus"], entry) for entry in ours])
	leaders = []
	for iOther in range(gc.getMAX_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.isBarbarian() or other.isMinorCiv() or not team.isHasMet(other.getTeam()):
			continue
		bWillTalk = bool(other.AI_isWillingToTalk(player.getID()))
		row = {"player": iOther, "name": other.getName(), "connected": bool(player.canTradeNetworkWith(iOther)), "willTalk": bWillTalk, "willImport": [], "willExport": [], "wontExport": [], "weDontNeed": []}
		if (team.isGoldTrading() or gc.getTeam(other.getTeam()).isGoldTrading()) and bWillTalk:
			row["maxGoldPerTurn"] = other.AI_maxGoldPerTurnTrade(player.getID())
		for iBonus in range(gc.getNumBonusInfos()):
			tradeData.iData = iBonus
			szBonus = gc.getBonusInfo(iBonus).getType()
			# <!-- custom: Would import: we can put it on the table, and it passes the AI's own test of a deal it would take (the tab's "surplus" test with bTestDenial). (Claude code Opus 5.5) -->
			if player.canTradeItem(iOther, tradeData, False) and player.canTradeItem(iOther, tradeData, not other.isHuman()):
				row["willImport"].append(szBonus)
				# <!-- custom: As the hover lists them: only leaders willing to talk, and with their overall gold-per-turn cap, labelled as such, not a price for this resource, which comes from CvPlayerAI::AI_goldForBonus and is not exposed to Python (Codex's review, round 36). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if byBonus.has_key(szBonus) and bWillTalk:
					byBonus[szBonus]["importers"].append({"player": iOther, "name": other.getName(), "leaderMaxGoldPerTurn": row.get("maxGoldPerTurn")})
			if other.canTradeItem(player.getID(), tradeData, False):
				iDenial = other.getTradeDenial(player.getID(), tradeData)
				if iDenial == DenialTypes.DENIAL_JOKING:
					row["weDontNeed"].append(szBonus)
				elif iDenial == DenialTypes.NO_DENIAL and bWillTalk:
					row["willExport"].append(szBonus)
				else:
					row["wontExport"].append(szBonus)
		leaders.append(row)
	return {"ours": ours, "leaders": leaders}


_HELP["deals"] = "The Foreign Advisor's active deals: each running deal of ours, with the leader, the turn it began, what we give and what we get, by item as 'diplo' shows offers. A resource we export leaves our network: the capital's plot group subtracts it, so 'resources' reads it as unconnected. args: player."


def _dealItems(deal, bFirst):
	if bFirst:
		iLength = deal.getLengthFirstTrades()
	else:
		iLength = deal.getLengthSecondTrades()
	items = []
	for i in range(iLength):
		if bFirst:
			item = deal.getFirstTrade(i)
		else:
			item = deal.getSecondTrade(i)
		if not item:
			continue
		entry = {"item": _enumName(TradeableItems, item.ItemType), "data": item.iData}
		szWhat = _tradeDataName(item.ItemType, item.iData)
		if szWhat is not None:
			entry["what"] = szWhat
		items.append(entry)
	return items


def cmd_deals(args):
	# <!-- custom: At turn 125 of the turn-0 game (2026-11-14) the mined and roaded Iron diagonal to London read unconnected, and no city could train a Swordsman. The trade network itself connected (two roaded plots, CvPlot::isTradeNetworkConnected); CvPlot::updatePlotGroupBonus subtracts the capital's exports, so a resource given away in a deal reads as missing. The pilot had no way to list deals, which the Foreign Advisor's Active tab shows a player (CvForeignAdvisor's deal loop). (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	iPlayer = player.getID()
	game = gc.getGame()
	deals = []
	for i in range(game.getIndexAfterLastDeal()):
		deal = game.getDeal(i)
		if deal.isNone():
			continue
		if deal.getFirstPlayer() == iPlayer:
			iOther = deal.getSecondPlayer()
			bWeFirst = True
		elif deal.getSecondPlayer() == iPlayer:
			iOther = deal.getFirstPlayer()
			bWeFirst = False
		else:
			continue
		deals.append({"id": deal.getID(), "with": iOther, "name": gc.getPlayer(iOther).getName(), "sinceTurn": deal.getInitialGameTurn(), "turnsToCancel": max(0, _dealTurnsToCancel(deal)), "weGive": _dealItems(deal, bWeFirst), "weGet": _dealItems(deal, not bWeFirst)})
	return {"deals": deals}


def _dealTurnsToCancel(deal):
	# <!-- custom: CvDeal::turnsToCancel, which Python cannot call: the deal's first turn plus PEACE_TREATY_LENGTH, less the current turn (advc.034 shortens it for a disengagement, which this leaves out, so for one it can say later than the game, never earlier, as Codex's review noted in round 37). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	return deal.getInitialGameTurn() + gc.getDefineINT("PEACE_TREATY_LENGTH") - gc.getGame().getGameTurn()


_HELP["canceldeal"] = "Cancel one of our deals, as the Foreign Advisor's cancel button does: it raises the same confirmation popup, which 'answer' then confirms (button 0) or declines (button 1). Refused before the game allows it ('deals' gives turnsToCancel) and for deals holding a vassal item. args: deal (ID from 'deals')."


def cmd_canceldeal(args):
	# <!-- custom: Our only Iron went to Gilgamesh inside a Pig sale at turn 118 of the turn-0 game (2026-11-14), and the pilot could not cancel a deal. CvDLLWidgetData::doDealKill tests CvDeal::isCancelable, then raises BUTTONPOPUP_DEAL_CANCELED, whose Yes sends the kill as a network message; isCancelable is not exposed, so its turn rule is checked here and vassal deals, which it may refuse, are left to the window. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_activePlayerId())
	iDeal = int(args["deal"])
	deal = gc.getGame().getDeal(iDeal)
	if deal is None or deal.isNone() or player.getID() not in (deal.getFirstPlayer(), deal.getSecondPlayer()):
		raise ValueError("deal %d is not one of ours; see 'deals'" % iDeal)
	for bFirst in (True, False):
		for item in _dealItems(deal, bFirst):
			if item["item"] in ("TRADE_VASSAL", "TRADE_SURRENDER"):
				raise ValueError("deal %d holds a vassal item; cancel it from the Foreign Advisor" % iDeal)
	iTurns = _dealTurnsToCancel(deal)
	if iTurns > 0:
		raise ValueError("deal %d can be cancelled in %d turns" % (iDeal, iTurns))
	popupInfo = CyPopupInfo()
	popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DEAL_CANCELED)
	popupInfo.setData1(iDeal)
	popupInfo.setOption1(False)
	popupInfo.addPopup(player.getID())
	return {"deal": iDeal, "popup": "BUTTONPOPUP_DEAL_CANCELED", "next": "'popups' lists it; 'answer' button 0 cancels the deal, 1 keeps it"}


_HELP["scores"] = "The Info screen's Score tab, per player met and ourselves: score and its change since last turn, techs known, land share, power and power per city where the demographics are visible (as the scoreboard's ratio), cities seen, state religion and holy city, vassal status, will to talk, and current research and progress where espionage lets it be seen. args: player."


def cmd_scores(args):
	# <!-- custom: The user pointed to the Info screen's Score tab at turn 150 of the turn-0 game (2026-11-14): it showed at a glance that we knew 27 techs against 29 to 37 for every rival, that Pericles gained +42 score a turn, and power totals per city, which no pilot command gave together. Follows CvInfoScreen.drawScoreTab: the same tests decide what is visible. (Claude code Opus 5.5) -->
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
		if not bUs:
			row["willTalk"] = bool(other.AI_isWillingToTalk(player.getID()) and player.AI_isWillingToTalk(iOther))
		if player.canSeeResearch(iOther) or bUs:
			iTech = other.getCurrentResearch()
			if iTech >= 0:
				row["research"] = gc.getTechInfo(iTech).getType()
				row["researchPercent"] = 100 * otherTeam.getResearchProgress(iTech) / max(1, otherTeam.getResearchCost(iTech))
		rows.append(row)
	rows.sort(lambda a, b: cmp(b["score"], a["score"]))
	return {"players": rows}


_HELP["demographics"] = "The Info screen's Demographics tab: for soldiers (military power), land, population, economy (commerce), industry (production) and agriculture (food), our value, our rank among us and our rivals (1 is best), and the rivals' best, average and worst. Rivals are every living non-Barbarian player of another team, met or not, as the tab counts them; their economy, industry and agriculture are last turn's, as the tab shows them (advc.077). args: player."


def cmd_demographics(args):
	# <!-- custom: The user pointed out at turn 90 of the turn-0 game (2026-11-14) that we were falling behind militarily, and that a player sees it on the Info screen's Demographics tab; the pilot had no command for it, and 'relations' hides power under fog. This follows CvInfoScreen.drawDemographicsTab (advc.077): the same rivals, current power, land and population for all, history for the rivals' economy, industry and agriculture. (Claude code Opus 5.5) -->
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
		# <!-- custom: Under fog, the tab's own display rules with its default settings (bRanksAmongKnown, bShowBestKnown): the first version gave exact rival best, worst and average before meeting anyone (Codex's review, round 35). The rank counts only players we have met; best and worst only met rivals whose demographics we can see, best with one such rival and worst with two; the average all rivals, met or not, shown above 3 rivals and rounded to a multiple of 5 (of 5,000 for the values scaled by 1,000). Without fog, exact values for every rival, for debugging. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
	# <!-- custom: The user's facts-versus-advice idea (2026-11-14), with their own example as its first rule: avoid an animal that is faster than you while you are weaker; animals are strong in SAS and give little. A command of its own, so tuning a rule never touches the fact commands that replays compare against. (Claude code Opus 5.5) -->
	szAbout = args.get("about")
	if szAbout == "scout":
		result = cmd_scout(args)
		result["rule"] = "most plots revealed first, then fewest animals and barbarians within two plots, then the best defense"
		result["steps"].sort(lambda a, b: cmp((-a["reveals"], len(a["enemiesNear"]), -a["defense"]), (-b["reveals"], len(b["enemiesNear"]), -b["defense"])))
		return result
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
				# <!-- custom: Odds only for an attack that can happen: the first version gave a Settler beside an animal weWinPerMille, and a Galley reach advice about a land animal from distance and moves alone (Codex's review, round 33). An attack needs an attacker that can attack and both units in one domain. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				bSameDomain = other.getDomainType() == unit.getDomainType()
				# <!-- custom: And an animal cannot enter owned land (CvUnit::canMoveInto, CvUnit.cpp:2687), so it cannot attack a unit there: a Lion beside a Settler on our land showed couldReach and certain death (Codex's review, round 34). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				bTheyCanAttack = bSameDomain and other.canAttack() and not (other.isAnimal() and unit.plot().isOwned())
				bWeCanAttack = bSameDomain and unit.canAttack()
				# <!-- custom: Reach by plots, one per move point: terrain costs and roads are left out, so this is the reach on open ground, which is how the rule may be wrong. (Claude code Opus 5.5) -->
				bReach = bTheyCanAttack and iDistance <= iTheirMoves
				# <!-- custom: getCombatOdds(attacker, defender) is the window's hover odds; both ways, as an animal attacks on its own turn. A unit that cannot fight, such as a Settler or Worker, is captured or killed if attacked, so they win for certain. (Claude code Opus 5.5) -->
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


_HELP["routes"] = "A text map of the player's land, row by row from the north, to see the route network as the window shows it at a glance: C city, # railroad, = road, . own land with no route, ~ own water, x another's land, space unowned; columns are x from 'x0', rows y from 'y1' down. Plus each city's connection to the capital. args: margin (plots around our land, default 1), player."


def cmd_routes(args):
	# <!-- custom: The pilot gave plots one by one and no picture of the network: at turn 281 of the modern baseline (2026-11-14) the user spotted a marsh at (11,42) with no route between a railroad and two roads, which the agent had not noticed. A row of characters per map row shows such a gap the way the map does. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_playerId(args))
	iTeam = _fogTeam(args)
	# <!-- custom: Under fog, player= naming another team still drew the map's edges from all its plots and listed every city with its coordinates and capital connection, although the rows hid unrevealed tiles (Codex's review, 2026-11-14). Refuse it, as 'odds' does for foreign units. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	_requireOwnTeamUnderFog(args, player, "the route map")
	kMap = gc.getMap()
	iRail = gc.getInfoTypeForString("ROUTE_RAILROAD")
	owned = []
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if plot.getOwner() == player.getID():
			owned.append((plot.getX(), plot.getY()))
	if not owned:
		raise ValueError("player %d owns no plots" % player.getID())
	iMargin = int(args.get("margin", 1))
	x0 = max(0, min([x for (x, y) in owned]) - iMargin)
	x1 = min(kMap.getGridWidth() - 1, max([x for (x, y) in owned]) + iMargin)
	y0 = max(0, min([y for (x, y) in owned]) - iMargin)
	y1 = min(kMap.getGridHeight() - 1, max([y for (x, y) in owned]) + iMargin)
	rows = []
	for y in range(y1, y0 - 1, -1):
		line = []
		for x in range(x0, x1 + 1):
			plot = kMap.plot(x, y)
			if iTeam >= 0 and not plot.isRevealed(iTeam, False):
				line.append("?")
			elif plot.getOwner() != player.getID():
				if plot.getOwner() >= 0:
					line.append("x")
				else:
					line.append(" ")
			elif plot.isCity():
				line.append("C")
			elif plot.isWater():
				line.append("~")
			elif plot.getRouteType() == iRail:
				line.append("#")
			elif plot.getRouteType() >= 0:
				line.append("=")
			else:
				line.append(".")
		rows.append("%3d %s" % (y, "".join(line)))
	cities = []
	(city, iterator) = player.firstCity(False)
	while city:
		cities.append({"name": city.getName(), "x": city.getX(), "y": city.getY(), "connectedToCapital": city.isConnectedToCapital(player.getID())})
		(city, iterator) = player.nextCity(iterator, False)
	return {"x0": x0, "y1": y1, "rows": rows, "cities": cities}


_QUEUE_PLAIN_MISSIONS = ("MISSION_SKIP", "MISSION_SLEEP", "MISSION_FORTIFY", "MISSION_HEAL", "MISSION_SENTRY", "MISSION_SENTRY_HEAL", "MISSION_FOUND", "MISSION_PILLAGE", "MISSION_PLUNDER")


def _checkMissionData(eMission, iData1, iData2, bQueued):
	# <!-- custom: A queued mission skips canStartMission, so its data reach CvSelectionGroup::startMission unchecked later: a MISSION_MOVE_TO off the map would have the game dereference a missing plot (Codex's review). Check what does not depend on where the group will be: a plot on the map for a move or route, a BUILD_ index for a build, no data for the plain missions; refuse other missions in a queue, as their data mean different things. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	szMission = gc.getMissionInfo(int(eMission)).getType()
	if szMission in ("MISSION_MOVE_TO", "MISSION_ROUTE_TO"):
		plot = CyMap().plot(iData1, iData2)
		if plot is None or plot.isNone():
			raise ValueError("no plot at %d,%d" % (iData1, iData2))
	elif szMission == "MISSION_BUILD":
		if iData1 < 0 or iData1 >= gc.getNumBuildInfos():
			raise ValueError("%s is not a BUILD_ index" % iData1)
	elif not bQueued:
		return
	elif szMission in _QUEUE_PLAIN_MISSIONS:
		if iData1 != -1 or iData2 != -1:
			raise ValueError("%s takes no data" % szMission)
	else:
		raise ValueError("%s cannot be queued behind other missions by the pilot; give it when the queue is empty" % szMission)


_HELP["group"] = "Group units on one plot as selecting them together does, so they move and take missions as one: with=<unit> joins 'unit' to that unit's group; without it, 'unit' leaves its group. Then order the group through any of its units. args: unit, with, player."


def cmd_group(args):
	# <!-- custom: At turn 91 of the fog-on playthrough (2026-11-13) a Settler had to go where Barbarian Archers had pillaged, and the pilot could not escort it: Python has no joinGroup. See joinSASPilotGroup in CvGameInterface.cpp. (Claude code Opus 5.5) -->
	unit = _unit(args)
	iHead = -1
	if args.get("with") is not None:
		iHead = _unit({"unit": args["with"], "player": args.get("player")}).getID()
	text = _pilotGame("joinSASPilotGroup").joinSASPilotGroup(unit.getOwner(), unit.getID(), iHead)
	if text == "null":
		raise ValueError("unit %d cannot join unit %s's group: both must be the player's, on one plot and of one domain" % (unit.getID(), args.get("with")))
	group = unit.getGroup()
	return {"group": unit.getGroupID(), "units": [_unitBrief(group.getUnitAt(i)) for i in range(group.getNumUnits())]}


_HELP["freetech"] = "Choose a free tech, such as the Oracle's, as the tech chooser does: 'todo' lists the held BUTTONPOPUP_CHOOSETECH with data1 above 0 while one is owed. Without tech: the techs it may be. args: tech (TECH_ type)."


def cmd_freetech(args):
	# <!-- custom: The Oracle's free tech at turn 105 of the fog-on playthrough (2026-11-13) waited in a held choose-tech popup that 'todo' hid, as it left out every choose-tech popup while research was set; 'answer' only drops it. The count of techs owed is the popup's data1. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_activePlayerId())
	if not _pilotGame("isSASPilotChoosingFreeTech").isSASPilotChoosingFreeTech():
		raise ValueError("no free tech is owed now")
	# <!-- custom: Held choosers only: the DLL cannot close one on display, and Codex's review found that a spent displayed chooser becomes usable again with a later award. Holding starts at the load, so one on display is rare; it is then the window's to answer. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	held = [popup for popup in _popups() if popup["state"] == "HELD" and popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0]
	if not held:
		raise ValueError("the free-tech chooser is on display, not held; choose in the window")
	if args.get("tech") is None:
		return {"owed": held[0]["data1"], "techs": [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if player.canResearch(i, False)]}
	iTech = _typedIndex(args["tech"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	# <!-- custom: The DLL now takes the chooser's ID (-1 for the one on display), reads the count from it and removes only that one: closing choosers by type and count could discard a second award (Codex's review). Needs a DLL built after 2026-11-13's round 7. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if not _pilotGame("chooseSASPilotFreeTech").chooseSASPilotFreeTech(iTech, held[0]["id"]):
		raise ValueError("%s cannot be the free tech" % args["tech"])
	return {"chosen": args["tech"]}


_HELP["diplo"] = "The diplomacy screen, when an AI has contacted the player or the player has contacted an AI: open, who, the AI's line (aiComment type and text), the numbered replies the screen offers, and the deal on the table. 'reply n=' answers. args: none."


def _diploState():
	# <!-- custom: CvDiplomacy.py records what the screen shows in SASPilotScreen, as CyDiplomacy has no getter for the AI's line or the replies; the EXE imports that module itself, so this reads the same state. (Claude code Opus 5.5) -->
	import CvDiplomacy
	state = CvDiplomacy.SASPilotScreen
	# <!-- custom: Declaring war through the screen closed it without passing the branch that clears "open", and the next 'diplo' raised "unidentifiable C++ exception" from CyDiplomacy.atWar on the closed screen (2026-11-13). getWhoTradingWith gives -1 once the screen is closed and the partner while it is open, so it decides. (Claude code Opus 5.5) -->
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


# <!-- custom: A contact the pilot queued is (leader, fill columns, time) until its screen opens; the EXE opens it on later frames, so 'menu' could load in between (Codex's review). Forgotten after CONTACT_PENDING_SECONDS, in case the screen never opens. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
# <!-- custom: Timed with time.clock(), not time.time(): Direct3D sets the process's FPU to single precision, so inside Civ4 time.time() (about 1.79e9) moves in 128-second steps, and 1794652928.0 + 1.5 printed 1794652928.0 (turn 291, 2026-11-14). A contact queued by a failed 'price' then never expired and blocked every later contact. time.clock() counts from the process start, small enough to stay precise. See KI#1093. (Claude code Opus 5.5) -->
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
	# <!-- custom: Codex's round-15 review: the conversation was counted only when a pilot read found the screen newly open, so a close and reopen between reads was missed; CvDiplomacy.py now counts each conversation as it begins.
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


# <!-- custom: Trade kinds whose data is an XML entry: (type prefix, count getter, info getter). 'trade', 'diplo' and 'propose' each had their own chain of name comparisons for these kinds, and 'propose' resolved the data with the untyped _infoIndex, so TRADE_TECHNOLOGIES:BONUS_IRON would have sent Iron's index as a tech.
# Keyed by the TradeableItems value, as Codex suggested, so the names stay only in replies and arguments. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
_TRADE_INFO_TABLES = {
	int(TradeableItems.TRADE_TECHNOLOGIES): ("TECH_", "getNumTechInfos", "getTechInfo"),
	int(TradeableItems.TRADE_RESOURCES): ("BONUS_", "getNumBonusInfos", "getBonusInfo"),
	int(TradeableItems.TRADE_CIVIC): ("CIVIC_", "getNumCivicInfos", "getCivicInfo"),
	int(TradeableItems.TRADE_RELIGION): ("RELIGION_", "getNumReligionInfos", "getReligionInfo"),
}


def _tradeDataName(eKind, iData):
	# <!-- custom: Pacal's first offer through 'diplo' read TRADE_TECHNOLOGIES 2 for 5 (2026-11-13); name the data as 'trade' does. A city keeps its ID, as the giver is not known here. (Claude code Opus 5.5) -->
	table = _TRADE_INFO_TABLES.get(int(eKind))
	if table is None:
		return None
	return _typeOrNone(getattr(gc, table[2]), iData)


def cmd_diplo(args):
	# <!-- custom: Seven AI contacts reached the pilot's player in the 97-turn fog-on game (2026-11-13): tech offers, Open Borders, and Zara Yaqob pressing for Paganism, which refusing can anger. They opened the diplomacy screen in the window, unseen; Moctezuma's first-contact screen was still open at turn 97. (Claude code Opus 5.5) -->
	state = _diploState()
	if not state["open"]:
		return {"open": False}
	diplo = CyDiplomacy()
	iWho = state["who"]
	result = {"open": True, "screen": _diploToken(state), "who": iWho, "whoName": gc.getPlayer(iWho).getName(), "aiComment": _typeOrNone(gc.getDiplomacyInfo, state["aiComment"]), "aiText": _plainText(state["aiText"]), "aiArgs": [_plainText(unicode(arg)) for arg in (state.get("aiArgs") or ())]}
	result["replies"] = [{"n": i, "comment": gc.getDiplomacyInfo(response["comment"]).getType(), "data1": response["data1"], "data2": response["data2"], "text": _plainText(response["text"])} for (i, response) in enumerate(state["responses"])]
	result["theyOffer"] = _diploOffer(diplo.getTheirTradeOffer)
	result["weOffer"] = _diploOffer(diplo.getPlayerTradeOffer)
	result["atWar"] = bool(diplo.atWar())
	# <!-- custom: Which conversation this is, counted as each begins (see CvDiplomacy.SASPilotScreen), so a client sequence such as SASPilotClient.py's 'price' can stop when another leader's screen takes over (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	result["conversation"] = state.get("conversation", 0)
	return result


_HELP["contact"] = "Open the diplomacy screen with an AI player, as clicking its leader does; then 'diplo' shows its greeting and the replies, such as declaring war or asking for peace, and 'reply' answers. The screen opens on the next frames. With give= and/or take= (items as on 'propose'), it opens on the trade table with that deal on it, as Ctrl+clicking the leader and clicking the items does; 'diplo' then lists Propose and 'What would you want?'. args: with (player ID), give (list), take (list)."


def cmd_contact(args):
	# <!-- custom: A person declares war or asks for peace by talking to a leader; CyPlayer.contact opens that screen (tested at turn 97 of the fog-on playthrough, 2026-11-13), so war and peace go through the screen's own replies instead of commands of their own. (Claude code Opus 5.5) -->
	player = gc.getPlayer(_activePlayerId())
	# <!-- custom: An out-of-range ID would reach GET_PLAYER in the DLL, and a human target is not what the screen is for here (Codex's review); the checks now live in _otherAiId, shared with 'trade' and 'propose'. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iOther = _otherAiId(player, args["with"])
	if _diploState()["open"]:
		raise ValueError("a diplomacy screen is already open; see 'diplo'")
	# <!-- custom: One queued contact at a time, so a second cannot replace the first's pending record (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _pendingContact() is not None:
		raise ValueError("a contact is already queued; read 'diplo' once its screen opens")
	give = args.get("give", [])
	take = args.get("take", [])
	if not give and not take:
		player.contact(iOther)
		_state["contactPending"] = (iOther, False, time.clock())
		return {"contacted": _who(iOther)}
	# <!-- custom: With give= or take=, the screen opens on its trade table with those items on it, as Ctrl+clicking the leader and clicking the items does, so the screen's own replies answer the deal: Propose, and "What would you want?" with the AI's counter-offer, which 'propose' skips (2026-11-13). (Claude code Opus 5.5) -->
	szWeGive = ",".join([_tradeArg(item, player) for item in give])
	szTheyGive = ",".join([_tradeArg(item, gc.getPlayer(iOther)) for item in take])
	if not _pilotGame("tableSASPilotDeal").tableSASPilotDeal(player.getID(), iOther, szWeGive, szTheyGive):
		raise ValueError("not a deal player %d can put on the table with player %d: check the items against 'trade'" % (player.getID(), iOther))
	_state["contactPending"] = (iOther, True, time.clock())
	return {"contacted": _who(iOther), "table": True}


_HELP["reply"] = "Answer the diplomacy screen with one of the replies 'diplo' lists, as clicking it does; returns the screen after, which may show a new AI line and replies or be closed. screen is the number 'diplo' gave: a reply to a screen that has changed since is refused. comment= names the reply instead of n (USER_DIPLOCOMMENT_ prefix optional), which is safer: the list changes with the table, such as FISH_FOR_DEAL and GIFT when only our side is filled. args: n, comment, screen."


def cmd_reply(args):
	# <!-- custom: Calls CvDiplomacy.handleUserResponse with the reply's comment and data, the same handler the EXE calls for a click, so war, peace, deals and the screen closing all follow the screen's own rules. (Claude code Opus 5.5) -->
	# <!-- custom: Through CvDiplomacyInterface, the module the EXE calls: BUG extends its handleUserResponse (Assets/Config/init.xml) to send its diplomacy events, which calling CvDiplomacy directly skipped (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	import CvDiplomacyInterface
	state = _diploState()
	if not state["open"]:
		raise ValueError("no diplomacy screen is open")
	# <!-- custom: Required, as Codex's review found a reply chosen from one 'diplo' could land on a newer screen, such as a second AI contact opening after the first closed; the replies list alone does not tell them apart. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: An older number is accepted when that screen showed exactly what this one shows (AI line, replies, both sides of the table): after a counter-offer the EXE refreshes the screen once more, and 'reply' to the screen 'diplo' had just read was refused as stale although nothing had changed (2026-11-13, screen 14 then 15). (Claude code Opus 5.5) -->
	if args.get("screen") is None:
		raise ValueError("screen is required; read 'diplo' for it")
	iScreen = int(args["screen"])
	content = _screenContent(state)
	if _state.get("diploSeen", {}).get(iScreen) != content:
		raise ValueError("the screen no longer shows what read %s showed; read 'diplo' again" % iScreen)
	if (("truncated", True),) in [item for side in content[-2:] for item in side]:
		raise ValueError("the deal has more than %d items on a side, too many to check; answer in the window" % DIPLO_OFFER_MAX_ITEMS)
	# <!-- custom: The screen's partner as well, as Codex's review suggested: the count is per screen this module filled, and the partner is what the EXE shows now. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if CyDiplomacy().getWhoTradingWith() != state["who"]:
		raise ValueError("the screen is now with player %d, not %d; read 'diplo' again" % (CyDiplomacy().getWhoTradingWith(), state["who"]))
	# <!-- custom: By name too: at turn 128 of the turn-0 game (2026-11-14) the agent sent n=1 meaning "What would make this deal work?", as on a screen with both sides filled, but with only our Pig on the table the screen offers FISH_FOR_DEAL and GIFT, and reply 1 gave the Pig away. A comment names the reply, so a different list refuses instead of picking its neighbour. (Claude code Opus 5.5) -->
	comments = [gc.getDiplomacyInfo(response["comment"]).getType() for response in state["responses"]]
	if args.get("comment") is not None:
		szComment = args["comment"]
		if not szComment.startswith("USER_DIPLOCOMMENT_"):
			szComment = "USER_DIPLOCOMMENT_" + szComment
		if szComment not in comments:
			raise ValueError("%s is not offered; the screen offers %s" % (szComment, ", ".join(comments)))
		# <!-- custom: A name can be offered several times with different data, such as one TARGET_CITY reply per city; the first match was taken silently, and the right n for a later one was refused (Codex's review, round 37). Such a name now needs n, which must name that reply. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		matches = [i for i in range(len(comments)) if comments[i] == szComment]
		if args.get("n") is not None:
			iN = int(args["n"])
			if iN not in matches:
				raise ValueError("n=%s is not %s; %s is reply %s" % (args["n"], szComment, szComment, ", ".join([str(i) for i in matches])))
		elif len(matches) > 1:
			raise ValueError("%s is offered %d times (replies %s, with different data); give n as well" % (szComment, len(matches), ", ".join([str(i) for i in matches])))
		else:
			iN = matches[0]
	else:
		iN = int(args["n"])
	if iN < 0 or iN >= len(state["responses"]):
		raise ValueError("reply %d is not offered; 'diplo' lists %d" % (iN, len(state["responses"])))
	response = state["responses"][iN]
	CvDiplomacyInterface.handleUserResponse((response["comment"], response["data1"], response["data2"]))
	return cmd_diplo({})


_HELP["trade"] = "The two columns of the diplomacy screen with another player: what each side could put on the table, and for each item the other player would not give, the game's reason (DENIAL_ type). Gold is the most each side could give. args: with (player ID), player."


def _tradeItemsJson(giver, iReceiver, iKind=-1):
	# <!-- custom: Written in C++ by CyGame.getSASPilotTradeItemsJson since 2026-11-13: the Python loop here, every tradeable item with canTradeItem and getTradeDenial, took 3.5 ms of game time per 'trade' at turn 176 against 0.23 ms for a bare request, the slowest list command measured, and the user prefers the faster version even for a small measured gain. Same entries, in the enum's order. (Claude code Opus 5.5) -->
	return _pilotGame("getSASPilotTradeItemsJson").getSASPilotTradeItemsJson(giver.getID(), iReceiver, iKind)


def _tradeTechs(giver, iReceiver):
	# <!-- custom: The techs giver could put on the table, by ID, with the AI's denial (None when it would trade). (Claude code Opus 5.5) -->
	result = {}
	# <!-- custom: Tech rows only: reading the whole table for them made 'techs' take 3.3 ms against 0.77 ms before the port (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	for entry in fromJson(_tradeItemsJson(giver, iReceiver, int(TradeableItems.TRADE_TECHNOLOGIES))):
		result[entry["data"]] = entry.get("denial")
	return result


_HELP["techs"] = "The tech market across the players met: each tech the player lacks that some of them have, with its research cost, whether the XML lets it be traded at all (bTrade; SAS turns that off for some techs), and per holder whether it can be traded now and the AI's answer (DENIAL_ type, or null when it would trade). Then the techs we can research that none of them has (nobodyHas, research these and trade them on; unseenPlayers counts met players whose techs the fog hides), and per player met, the techs the player could give them. A holder at war ('atWar') can still answer for a tech put in the same deal as a peace treaty, as the diplomacy screen allows. args: player."


def cmd_techs(args):
	# <!-- custom: Buying techs well needs the whole market: who has what, which techs the XML forbids trading (32 in SAS by bTrade, such as Bronze Working, Iron Working, Engineering, Gunpowder and Code of Laws), and which holder would trade. 'trade' answered one leader at a time; the user asked for a view to get the best deals (2026-11-13). (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	# <!-- custom: Under fog, as the Foreign Advisor's tech tab shows it (CvForeignAdvisor.py): a met player's techs only when canSeeTech allows, and a tech they hold but cannot trade only when we could research it. The first version listed every met player's techs, which Codex's review found reveals more than the window (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iFogTeam = _fogTeam(args)
	if iFogTeam >= 0 and player.getTeam() != iFogTeam:
		raise ValueError("with fog on, 'techs' is only for the viewing team")
	others = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and not gc.getPlayer(i).isMinorCiv() and team.isHasMet(gc.getPlayer(i).getTeam())]
	iMet = len(others)
	if iFogTeam >= 0:
		others = [other for other in others if player.canSeeTech(other.getID())]
	wanted = []
	nobodyHas = []
	offers = dict([(other.getID(), []) for other in others])
	# <!-- custom: One C++ table read per player and direction, rather than canTradeItem and getTradeDenial per tech and player. (Claude code Opus 5.5) -->
	theyCan = dict([(other.getID(), _tradeTechs(other, player.getID())) for other in others])
	weCan = dict([(other.getID(), _tradeTechs(player, other.getID())) for other in others])
	for iTech in range(gc.getNumTechInfos()):
		info = gc.getTechInfo(iTech)
		if team.isHasTech(iTech):
			for other in others:
				if iTech in weCan[other.getID()]:
					offers[other.getID()].append(info.getType())
			continue
		holders = []
		for other in others:
			if not gc.getTeam(other.getTeam()).isHasTech(iTech):
				continue
			entry = {"player": other.getID(), "name": other.getName(), "atWar": bool(team.isAtWar(other.getTeam())), "canTrade": iTech in theyCan[other.getID()]}
			if iFogTeam >= 0 and not entry["canTrade"] and not player.canResearch(iTech, False):
				continue
			if entry["canTrade"] and not other.isHuman():
				entry["denial"] = theyCan[other.getID()][iTech]
				# <!-- custom: canTradeItem says the tech may go in a deal, not that its holder would: the advisor marks "Will Trade" only with no denial and a leader willing to talk (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				entry["willTalk"] = bool(other.AI_isWillingToTalk(player.getID()))
			holders.append(entry)
		if holders:
			wanted.append({"tech": info.getType(), "cost": team.getResearchCost(iTech), "progress": team.getResearchProgress(iTech), "xmlTradeable": bool(info.isTrade()), "canResearch": bool(player.canResearch(iTech, False)), "holders": holders})
		# <!-- custom: Techs we can research that no player listed here has: the user pointed out at turn 139 of the turn-0 game (2026-11-14) that the agent kept researching techs every neighbour had, which trade buys far cheaper (Zara sold Philosophy, 425 beakers, for 70 gold), while a tech nobody has can be traded to several leaders. Players whose techs the fog hides are not listed, so 'unseenPlayers' says how many could still hold these. (Claude code Opus 5.5) -->
		elif player.canResearch(iTech, False):
			nobodyHas.append({"tech": info.getType(), "cost": team.getResearchCost(iTech), "progress": team.getResearchProgress(iTech), "xmlTradeable": bool(info.isTrade())})
	weCouldGive = []
	for other in others:
		entry = {"player": other.getID(), "name": other.getName(), "techs": offers[other.getID()]}
		# <!-- custom: The gold each leader could pay at once, as the Foreign Advisor's Techs tab shows it under its coin column (AI_maxGoldTrade, when either side has gold trading and the leader will talk): the user pointed to the tab at turn 140 of the turn-0 game (2026-11-14), where Zara Yaqob held 590, a buyer for a tech nobody else has. (Claude code Opus 5.5) -->
		if not other.isHuman() and other.AI_isWillingToTalk(player.getID()) and (team.isGoldTrading() or gc.getTeam(other.getTeam()).isGoldTrading()):
			entry["maxGoldTrade"] = other.AI_maxGoldTrade(player.getID())
		weCouldGive.append(entry)
	return {"wanted": wanted, "nobodyHas": nobodyHas, "unseenPlayers": iMet - len(others), "weCouldGive": weCouldGive}


def cmd_trade(args):
	# <!-- custom: The AI announced "Pacal II will trade Agriculture, Mysticism" in the fog-on playthrough (2026-11-13), but the pilot could not see the diplomacy screen's table. These are the same per-item checks the screen makes (canTradeItem, getTradeDenial); proposing a deal is not covered. (Claude code Opus 5.5) -->
	player = _player(args)
	other = gc.getPlayer(_otherAiId(player, args["with"]))
	return {"we": RawJson(_tradeItemsJson(player, other.getID())), "they": RawJson(_tradeItemsJson(other, player.getID())), "attitude": _enumName(AttitudeTypes, other.AI_getAttitude(player.getID()))}


_HELP["propose"] = "Propose a deal to an AI, as the diplomacy screen's Propose button does: the AI accepts or refuses, and an accepted deal is handed to the game to carry out ('accepted' is the AI's answer; the deal itself can still be refused by the game, so read the result back). Not in network games. Items as on 'trade', e.g. give=[\"TRADE_TECHNOLOGIES:TECH_METAL_CASTING\"] take=[\"TRADE_TECHNOLOGIES:TECH_MYSTICISM\",\"TRADE_OPEN_BORDERS\"]; data is a type, a city name, a team or an amount. args: with (player ID), give (list), take (list), player."


def _tradeArg(szItem, giver):
	# <!-- custom: An item as "TRADE_KIND" or "TRADE_KIND:data", data being what 'trade' shows under "what" (an XML type or a city name) or a number (gold, a team); turned into the "kind:data" numbers proposeSASPilotDeal reads. (Claude code Opus 5.5) -->
	if ":" in szItem:
		(szKind, szData) = szItem.split(":", 1)
	else:
		(szKind, szData) = (szItem, "0")
	eKind = int(_enum(TradeableItems, szKind))
	table = _TRADE_INFO_TABLES.get(eKind)
	if szData.lstrip("-").isdigit():
		iData = int(szData)
	elif eKind == int(TradeableItems.TRADE_CITIES):
		iData = _city({"city": szData, "player": giver.getID()}).getID()
	elif table is not None:
		iData = _typedIndex(szData, table[0], getattr(gc, table[1])(), getattr(gc, table[2]))
	else:
		raise ValueError("%s takes a number, not %s" % (szKind, szData))
	return "%d:%d" % (eKind, iData)


def _who(iPlayer):
	# <!-- custom: A player as ID, leader name and civilization XML type, as the BBAI and SASGameRecord rows give an ID beside a name: replies such as {"contacted": 2} needed a lookup to tell it was Kublai (the user, 2026-11-14). The ID stays what commands take; the name and type say who it is.
	# Only the ID is unique: with duplicate leaders or civilizations allowed (game options, scenarios, mod-mods), two players can share both name and civilization (the user, 2026-11-14). (Claude code Opus 5.5) -->
	player = gc.getPlayer(iPlayer)
	return {"player": iPlayer, "name": player.getName(), "civ": _typeOrNone(gc.getCivilizationInfo, player.getCivilizationType())}


def cmd_propose(args):
	# <!-- custom: The second half of trading after 'trade' (fog-on playthrough, 2026-11-13); asking the AI and making the deal need the DLL, see proposeSASPilotDeal in CvGameInterface.cpp. (Claude code Opus 5.5) -->
	player = _player(args)
	other = gc.getPlayer(_otherAiId(player, args["with"]))
	szWeGive = ",".join([_tradeArg(item, player) for item in args.get("give", [])])
	szTheyGive = ",".join([_tradeArg(item, other) for item in args.get("take", [])])
	text = _pilotGame("proposeSASPilotDeal").proposeSASPilotDeal(player.getID(), other.getID(), szWeGive, szTheyGive)
	if text == "null":
		raise ValueError("not a deal player %d can propose to player %d: check the items against 'trade'" % (player.getID(), other.getID()))
	result = fromJson(text)
	result["with"] = _who(other.getID())
	return result


_HELP["odds"] = "The odds the window shows when a unit is pointed at a plot to attack: the defender the game would pick, both strengths, and the chance to win in per mille. args: unit, x, y, player."


def cmd_odds(args):
	# <!-- custom: A person sees the combat odds on hovering an enemy before attacking; the pilot had moves and paths but no odds (fog-on playthrough, 2026-11-13). The defender is the one the game would pick against this attacker, as getBestDefender does for the hover text; with fog on, only a plot in sight. (Claude code Opus 5.5) -->
	unit = _unit(args)
	plot = _plot(args)
	iTeam = _fogTeam(args)
	if iTeam >= 0 and not plot.isVisible(iTeam, False):
		raise ValueError("plot %d,%d is not in sight; fog is on" % (plot.getX(), plot.getY()))
	# <!-- custom: The game picks the defender with the attacker's own sight, so with player= naming another team's unit, a defender the viewing team cannot see could be named under fog (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if iTeam >= 0 and unit.getTeam() != iTeam:
		raise ValueError("with fog on, odds are only given for the viewing team's own units")
	# <!-- custom: CyPlot.getBestDefender names its last argument bTestCanMove, but passes it to CvPlot::getBestDefender's bTestVisible; with False an invisible defender on a visible plot could be named under fog (Codex's review). Pass whether fog is on. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	defender = plot.getBestDefender(PlayerTypes.NO_PLAYER, unit.getOwner(), unit, True, False, iTeam >= 0)
	if defender is None or defender.isNone():
		# <!-- custom: At turn 155 two withdrawn Catapults left two Aztec Trebuchets at 75 damage, the Catapult's combat limit, and the other Catapults got only "no unit at 29,28 that it could attack" although both stood there; Longbowmen then finished them (2026-11-13). The refusal now names the limit when it is the reason. (Claude code Opus 5.5) -->
		# <!-- custom: Only units the player can see, and none aboard a ship: Codex's review mocked an invisible enemy at 75 damage on a visible plot, and the first version named the limit, revealing it. Phrased as possible, as the game's own test also covers hidden nationality and the air combat limit. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		iLimit = unit.combatLimit()
		limited = []
		for i in range(plot.getNumUnits()):
			other = plot.getUnit(i)
			if other.isCargo() or (iTeam >= 0 and other.isInvisible(iTeam, False)):
				continue
			if gc.getTeam(unit.getTeam()).isAtWar(other.getTeam()) and other.getDamage() >= iLimit:
				limited.append(other)
		if iLimit < 100 and limited:
			raise ValueError("no unit at %d,%d that %d could attack; possibly its combat limit: %d, and enemies there are already damaged that much, which a unit without a limit can still attack" % (plot.getX(), plot.getY(), unit.getID(), iLimit))
		raise ValueError("no unit at %d,%d that %d could attack" % (plot.getX(), plot.getY(), unit.getID()))
	result = {"defender": _unitBrief(defender), "defenderStrength": defender.currCombatStrFloat(plot, unit), "oddsPerMille": getCombatOdds(unit, defender)}
	# <!-- custom: The attacker's own strength is currCombatStr(NULL, NULL) in C++, but CyUnit's wrapper dereferenced both pointers, so unit.currCombatStrFloat(None, None) raised "unidentifiable C++ exception" (2026-11-13); the wrapper now passes NULL through, and a DLL without that fix leaves the field out. (Claude code Opus 5.5) -->
	try:
		result["attackerStrength"] = unit.currCombatStrFloat(None, None)
	except RuntimeError:
		pass
	return result


_HELP["sites"] = "The city sites the window circles when this Settler is selected: the player's recommended sites it reaches within 7 turns, best first, each with its plot, found value, rank in the player's list and path turns. args: unit, player."


def cmd_sites(args):
	# <!-- custom: At the first Settler of the fog-on playthrough (2026-11-13) the pilot had plots and yields but not the green circles BtS draws for a selected Settler; this reads the same list in C++, as Python cannot reach it. (Claude code Opus 5.5) -->
	unit = _unit(args)
	text = _pilotGame("getSASPilotCitySitesJson").getSASPilotCitySitesJson(unit.getOwner(), unit.getID())
	if text == "null":
		raise ValueError("unit %d cannot found a city" % unit.getID())
	return RawJson(text)


_HELP["builds"] = "What a unit could build on a plot, as the window's buttons offer once the unit stands there: each build with its turns for this unit once it stands there, the improvement or route it makes, and the improvement's yield change on that plot. With refused=1, also each build this unit type can make that the plot refuses, with the reason. args: unit, x, y (default the unit's plot), refused, player."


def cmd_builds(args):
	# <!-- custom: 'unit' lists builds for the unit's own plot only, so choosing where to send a new Worker in the fog-on playthrough (2026-11-13) meant moving it first or a 'py' call per plot; a person sees a tile's options before sending it. (Claude code Opus 5.5) -->
	unit = _unit(args)
	if args.get("x") is None:
		plot = unit.plot()
	else:
		plot = _plot(args)
	iTeam = _fogTeam(args)
	if iTeam >= 0 and not plot.isRevealed(iTeam, False):
		raise ValueError("plot %d,%d is not revealed; fog is on" % (plot.getX(), plot.getY()))
	result = []
	for i in range(gc.getNumBuildInfos()):
		if not unit.canBuild(plot, i, False):
			continue
		info = gc.getBuildInfo(i)
		entry = {"build": info.getType(), "turns": plot.getBuildTurnsLeft(i, unit.getOwner(), unit.workRate(True), unit.workRate(True)), "improvement": _typeOrNone(gc.getImprovementInfo, info.getImprovement()), "route": _typeOrNone(gc.getRouteInfo, info.getRoute())}
		if info.getImprovement() >= 0:
			entry["yieldChange"] = [plot.calculateImprovementYieldChange(info.getImprovement(), YieldTypes(j), unit.getOwner(), False) for j in range(YieldTypes.NUM_YIELD_TYPES)]
		# <!-- custom: The hammers a build that clears the plot's feature gives the city, as the window's build hover says: in the scouting trial (2026-11-14) the user and the agent weighed chopping forests into a Settler, and only the XML (30 per forest, with Masonry in SAS) and the DLL (chop hammers take the city's production multipliers, so a settler bonus would double them; Justinian has none in SAS) answered it.
		# CyPlot.getFeatureProduction fills a city pointer it does not return, so the receiving city is not named here; the amount already counts distance and the team's techs. (Claude code Opus 5.5) -->
		if plot.getFeatureType() >= 0 and info.isFeatureRemove(plot.getFeatureType()):
			entry["featureProduction"] = plot.getFeatureProduction(i, unit.getTeam(), CyCity())
		result.append(entry)
	if not args.get("refused"):
		return result
	# <!-- custom: Why a Worker cannot build somewhere, which twice took 'py' snippets in the turn-0 game (2026-11-14): a road at 26,28 was refused because in SAS a road drains Marsh, a feature removal that AdvCiv allows on unclaimed land only with CAN_CHOP_UNOWNED_FEATURES (advc.119). The user asked that such a question become reusable.
	# The reasons follow CvPlayer::canBuild and CvPlot::canBuild in their order; a build refused for none of them is refused by the plot itself, such as a Mine off hills. (Claude code Opus 5.5) -->
	player = gc.getPlayer(unit.getOwner())
	team = gc.getTeam(unit.getTeam())
	infoUnit = gc.getUnitInfo(unit.getUnitType())
	iFeature = plot.getFeatureType()
	iOwner = plot.getOwner()
	if iTeam >= 0:
		iOwner = plot.getRevealedOwner(iTeam, False)
	refused = []
	for i in range(gc.getNumBuildInfos()):
		if not infoUnit.getBuilds(i) or unit.canBuild(plot, i, False):
			continue
		info = gc.getBuildInfo(i)
		if info.getImprovement() < 0 and info.getRoute() < 0 and (iFeature < 0 or not info.isFeatureRemove(iFeature)):
			continue
		iTech = info.getTechPrereq()
		# <!-- custom: In CvPlayer::canBuild's order, from the game's own checks where Python has them: the plot's (CyPlot.canBuild), then the build's tech, the feature's tech and the gold. The first version asked the tech before the plot and the XML gold cost, which ignored inflation and that a build already begun costs nothing more (CvPlayer::getBuildCost), so a resumed build could read as too dear (Codex's review, round 32). calculateInflationRate and getBuildProgress were exposed all along. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if not plot.canBuild(i, unit.getOwner(), False):
			# <!-- custom: The plot's reasons, as the plot check gives no reason of its own; CvPlot::canBuild asks canHaveImprovement before the feature, so a Mine on flat Marsh is refused for the terrain, not for draining the Marsh. (Claude code Opus 5.5) -->
			if info.getImprovement() >= 0 and not plot.canHaveImprovement(info.getImprovement(), unit.getTeam(), True):
				reason = "%s cannot be on this plot (terrain, feature or another rule)" % gc.getImprovementInfo(info.getImprovement()).getType()
			elif iFeature >= 0 and info.isFeatureRemove(iFeature) and iOwner < 0 and not gc.getDefineINT("CAN_CHOP_UNOWNED_FEATURES"):
				reason = "removes %s, which unclaimed land does not allow (advc.119, CAN_CHOP_UNOWNED_FEATURES)" % gc.getFeatureInfo(iFeature).getType()
			elif iFeature >= 0 and info.isFeatureRemove(iFeature) and iOwner >= 0 and gc.getPlayer(iOwner).getTeam() != unit.getTeam():
				reason = "removes %s on another team's land" % gc.getFeatureInfo(iFeature).getType()
			else:
				reason = "the plot does not take it (terrain, feature, existing improvement or route)"
		elif iTech >= 0 and not team.isHasTech(iTech):
			reason = "needs %s" % gc.getTechInfo(iTech).getType()
		elif iFeature >= 0 and info.getFeatureTech(iFeature) >= 0 and not team.isHasTech(info.getFeatureTech(iFeature)):
			reason = "needs %s to work on %s" % (gc.getTechInfo(info.getFeatureTech(iFeature)).getType(), gc.getFeatureInfo(iFeature).getType())
		else:
			# <!-- custom: CvPlayer::getBuildCost: nothing once begun, else the XML cost with inflation. (Claude code Opus 5.5) -->
			iCost = 0
			if plot.getBuildProgress(i) <= 0:
				iCost = max(0, info.getCost() * (100 + player.calculateInflationRate())) / 100
			if max(0, player.getGold()) < iCost:
				reason = "costs %d gold, inflation included" % iCost
			else:
				reason = "this unit cannot start it here now (the player could)"
		refused.append({"build": info.getType(), "reason": reason})
	return {"builds": result, "refused": refused}


_HELP["workers"] = "Planning Workers by hand. Without city: each Worker with where it is, whether automated and its current mission; per city the worked plots with no improvement and the city AI's three most valued builds; and per leader we can trade with whether their capital is on our trade network (no road link means no foreign trade routes with them). With city: each plot of its radius with terrain, feature, bonus, river, improvement, route, yields, whether worked, the city AI's best build and value, and every improvement build a Worker could make there with its yield change and turns for one Worker. The AI's choice is a reference to compare with, not an order. args: city, player."


def _workerTurns(plot, iBuild, player):
	# <!-- custom: Turns for one ordinary Worker, as the plot's own build progress counts them: the Worker's XML work rate with the player's worker speed modifier. (Claude code Opus 5.5) -->
	iWorker = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_WORKER"))
	if iWorker < 0:
		return None
	iRate = gc.getUnitInfo(iWorker).getWorkRate() * (100 + player.getWorkerSpeedModifier()) / 100
	if iRate <= 0:
		return None
	return plot.getBuildTurnsLeft(iBuild, player.getID(), iRate, iRate)


def _improvable(plot, player):
	# <!-- custom: An unimproved plot some improvement build could go on now. (Claude code Opus 5.5) -->
	if plot.getImprovementType() >= 0:
		return False
	for i in range(gc.getNumBuildInfos()):
		if gc.getBuildInfo(i).getImprovement() >= 0 and player.canBuild(plot, i, False, False):
			return True
	return False


def cmd_workers(args):
	# <!-- custom: The pilot only automated Workers until the user asked it to plan them itself and compare its choices with the AI's (2026-11-14): yields, rivers, roads to neighbours for trade. The city AI's per-plot best build comes from getSASPilotCityBuildsJson, as Python had no getter; the rest is read here. (Claude code Opus 5.5) -->
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "Worker planning")
	if not hasattr(gc.getGame(), "getSASPilotCityBuildsJson"):
		raise ValueError("this DLL predates getSASPilotCityBuildsJson; build or install a current one")
	bAdvice = _adviceAllowed()
	if args.get("city") is not None:
		city = _city(args)
		aiRows = fromJson(_pilotGame("getSASPilotCityBuildsJson").getSASPilotCityBuildsJson(player.getID(), city.getID()))
		plots = []
		for row in aiRows:
			plot = gc.getMap().plot(row["x"], row["y"])
			if plot.getOwner() != player.getID():
				continue
			entry = {"x": row["x"], "y": row["y"], "worked": row["worked"], "terrain": _typeOrNone(gc.getTerrainInfo, plot.getTerrainType()), "feature": _typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "bonus": _typeOrNone(gc.getBonusInfo, plot.getBonusType(player.getTeam())), "river": bool(plot.isRiver()), "hills": bool(plot.isHills()), "improvement": _typeOrNone(gc.getImprovementInfo, plot.getImprovementType()), "route": _typeOrNone(gc.getRouteInfo, plot.getRouteType()), "yields": [plot.getYield(YieldTypes(j)) for j in range(YieldTypes.NUM_YIELD_TYPES)]}
			# <!-- custom: The city AI's pick is advice no screen shows, so only where the session's role allows advice (the facts-versus-advice split, 2026-11-14). (Claude code Opus 5.5) -->
			if bAdvice:
				entry["aiBuild"] = row["bestBuild"]
				entry["aiValue"] = row["bestValue"]
			options = []
			for i in range(gc.getNumBuildInfos()):
				info = gc.getBuildInfo(i)
				# <!-- custom: CyPlayer.canBuild, not CyPlot.canBuild: the plot's check skips the player's tech, feature-removal tech and gold, so builds the player could not start were offered (Codex's review); the same in _improvable and routeGain. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				if info.getImprovement() < 0 or not player.canBuild(plot, i, False, False):
					continue
				change = [plot.calculateImprovementYieldChange(info.getImprovement(), YieldTypes(j), player.getID(), False) for j in range(YieldTypes.NUM_YIELD_TYPES)]
				# <!-- custom: yieldChange is against the bare plot, so at Hippo (turn 287) a Farm showed +1 food where it would replace a Town worth +6 commerce; netChange subtracts what the current improvement gives. (Claude code Opus 5.5) -->
				current = [0] * YieldTypes.NUM_YIELD_TYPES
				if plot.getImprovementType() >= 0:
					current = [plot.calculateImprovementYieldChange(plot.getImprovementType(), YieldTypes(j), player.getID(), False) for j in range(YieldTypes.NUM_YIELD_TYPES)]
				# <!-- custom: A build that clears the plot's feature also loses the feature's yields, as the build tooltip counts (Codex's review), e.g. a Farm on a forest loses its production. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				iFeature = plot.getFeatureType()
				if iFeature >= 0 and info.isFeatureRemove(iFeature):
					current = [current[j] + gc.getFeatureInfo(iFeature).getYieldChange(j) for j in range(YieldTypes.NUM_YIELD_TYPES)]
				options.append({"build": info.getType(), "yieldChange": change, "netChange": [change[j] - current[j] for j in range(YieldTypes.NUM_YIELD_TYPES)], "removesFeature": bool(iFeature >= 0 and info.isFeatureRemove(iFeature)), "turns": _workerTurns(plot, i, player)})
			entry["options"] = options
			plots.append(entry)
		return {"city": city.getName(), "plots": plots}
	workers = []
	for unit in _units(player):
		if gc.getUnitInfo(unit.getUnitType()).getWorkRate() <= 0 or unit.getDomainType() != DomainTypes.DOMAIN_LAND:
			continue
		group = unit.getGroup()
		row = {"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "automated": bool(group.isAutomated())}
		if group.getLengthMissionQueue() > 0:
			row["mission"] = gc.getMissionInfo(group.getMissionType(0)).getType()
			if row["mission"] == "MISSION_BUILD":
				row["build"] = gc.getBuildInfo(group.getMissionData1(0)).getType()
		workers.append(row)
	cities = []
	for city in _cities(player):
		aiRows = fromJson(_pilotGame("getSASPilotCityBuildsJson").getSASPilotCityBuildsJson(player.getID(), city.getID()))
		# <!-- custom: Water without a resource takes no improvement, and listed coastal cities' ocean plots as "unimproved" on the first try (turn 286, 2026-11-14). (Claude code Opus 5.5) -->
		unimproved = [[row["x"], row["y"]] for row in aiRows if row["worked"] and _improvable(gc.getMap().plot(row["x"], row["y"]), player) and not (row["x"] == city.getX() and row["y"] == city.getY())]
		suggestions = [row for row in aiRows if row["bestBuild"] and gc.getMap().plot(row["x"], row["y"]).getOwner() == player.getID()]
		suggestions.sort(lambda a, b: cmp(b["bestValue"], a["bestValue"]))
		# <!-- custom: The city AI's best builds leave out routes, yet a railroad adds +1 production to SAS's mines, lumbermills and quarries (ImprovementInfo RouteYieldChanges); on turn 287 of the modern baseline every such plot already had one (2026-11-14). Listed for any route that adds yield to the plot's improvement. (Claude code Opus 5.5) -->
		routeGain = []
		for row in aiRows:
			plot = gc.getMap().plot(row["x"], row["y"])
			if plot.getOwner() != player.getID() or plot.getImprovementType() < 0:
				continue
			info = gc.getImprovementInfo(plot.getImprovementType())
			for iRoute in range(gc.getNumRouteInfos()):
				# <!-- custom: The tech a route needs is on its build, not its RouteInfo, so ask whether some build of that route can go on the plot. (Claude code Opus 5.5) -->
				if iRoute == plot.getRouteType() or not [i for i in range(gc.getNumBuildInfos()) if gc.getBuildInfo(i).getRoute() == iRoute and player.canBuild(plot, i, False, False)]:
					continue
				gain = [info.getRouteYieldChanges(iRoute, j) for j in range(YieldTypes.NUM_YIELD_TYPES)]
				if max(gain) > 0:
					routeGain.append({"x": row["x"], "y": row["y"], "route": gc.getRouteInfo(iRoute).getType(), "yieldChange": gain, "worked": row["worked"]})
		entry = {"id": city.getID(), "name": city.getName(), "workedUnimproved": unimproved, "routeGain": routeGain}
		if bAdvice:
			entry["aiTop"] = [{"x": r["x"], "y": r["y"], "build": r["bestBuild"], "value": r["bestValue"], "worked": r["worked"]} for r in suggestions[:3]]
		cities.append(entry)
	# <!-- custom: Foreign trade routes need the two capitals on one trade network, roads or rivers or coast; a missing road link to a neighbour is a Worker job a person might take. Only capitals the team has revealed are listed, so fog hides nothing more than the map does. (Claude code Opus 5.5) -->
	# <!-- custom: CyCity.isConnectedTo, not CyPlot.isTradeNetworkConnected: the plot test checks a single network edge, so two roaded capitals could read as connected with a gap between them (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	trade = []
	capital = player.getCapitalCity()
	iTeam = player.getTeam()
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.isBarbarian() or not gc.getTeam(iTeam).isHasMet(other.getTeam()) or gc.getTeam(iTeam).isAtWar(other.getTeam()):
			continue
		theirs = other.getCapitalCity()
		# <!-- custom: The capital itself revealed, not only its plot, as in 'relations' (Codex's review, round 35). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if capital is None or theirs is None or theirs.isNone() or not theirs.isRevealed(iTeam, False):
			continue
		trade.append({"player": iOther, "name": other.getName(), "capital": theirs.getName(), "x": theirs.getX(), "y": theirs.getY(), "connected": bool(capital.isConnectedTo(theirs)), "openBorders": bool(gc.getTeam(iTeam).isOpenBorders(other.getTeam()))})
	return {"workers": workers, "cities": cities, "tradeLinks": trade}


_HELP["move"] = "Move a unit to a plot (MISSION_MOVE_TO); continues over later turns. args: unit, x, y, player."


def cmd_move(args):
	unit = _unit(args)
	plot = _plot(args)
	# <!-- custom: Checked with Python's CyUnit.generatePath first. At turn 81 of the fog-on playthrough (2026-11-13), right after Open Borders with Ethiopia were signed, 'path' found a 7-turn route for a Warrior inside Ethiopia's borders while 'move' said it had no path; the same pathfinder as 'path', GroupPathFinder, now decides both, so they cannot disagree. (Claude code Opus 5.5) -->
	if not fromJson(_pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), 0)).get("found"):
		raise ValueError("unit %d has no path to %d,%d" % (unit.getID(), plot.getX(), plot.getY()))
	if _state.get("follow", True):
		_lookAt(plot)
	return cmd_mission({"unit": args["unit"], "player": args.get("player"), "mission": "MISSION_MOVE_TO", "data1": plot.getX(), "data2": plot.getY()})


_HELP["look"] = "Turn the window's camera to a plot, a unit or a city, as clicking the minimap does, so a person watching sees what the pilot acts on. Following is on by default: each 'move' (attacks included) looks at its destination first, and an order on one of our units or cities (mission, command, group, spy, targets, hurry, produce, dequeue, citizens, work, specialist, emphasize) looks at it; follow=0 stops that and follow=1 restores it. zoom sets the camera's distance (the EXE's scale; the window starts near 1). args: x, y, unit, city, follow, zoom, player."


def _lookAt(plot):
	CyCamera().JustLookAtPlot(plot)


# <!-- custom: Orders on one of our units or cities that follow=1 looks at first. Following only 'move' left the camera on a far fog-covered city while production, missions and a spy's work went on elsewhere (the user, turn 285, 2026-11-14). (Claude code Opus 5.5) -->
FOLLOW_UNIT_ORDERS = ("mission", "command", "group", "spy", "targets", "hurry")
FOLLOW_CITY_ORDERS = ("produce", "dequeue", "hurry", "citizens", "work", "specialist", "emphasize")


def _followOrder(name, args):
	# <!-- custom: Only the active player's own units and cities, so the camera never shows a place fog hides; a bad argument is left to the command's own error. (Claude code Opus 5.5) -->
	try:
		plot = None
		if name in FOLLOW_UNIT_ORDERS and args.get("unit") is not None:
			unit = _unit(args)
			if unit.getOwner() == gc.getGame().getActivePlayer():
				plot = unit.plot()
		elif name in FOLLOW_CITY_ORDERS and args.get("city") is not None:
			city = _city(args)
			if city.getOwner() == gc.getGame().getActivePlayer():
				plot = city.plot()
		if plot is not None:
			_lookAt(plot)
	except Exception:
		pass


def cmd_look(args):
	# <!-- custom: The user watches the playthrough in the window, and the pilot never moved the camera: when Paper was discovered the view was too far from the action to follow it (2026-11-13). The camera changes only what is drawn, not the game. (Claude code Opus 5.5) -->
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
	# <!-- custom: Looked up again by ID afterwards: upgrading a Spearman to a Bazooka at turn 265 of the modern baseline (2026-11-14) worked, but reading the old object then raised an unidentifiable C++ exception, as an upgrade replaces the unit with a new one, like the used-up Work Boat in cmd_mission. The new unit is the one of the target type with the highest ID on that plot. (Claude code Opus 5.5) -->
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


_HELP["produce"] = "Put an item in a city's build queue: a UNIT_, BUILDING_, PROJECT_ or PROCESS_ type. By default it replaces the queue; append=1 adds at the end, first=1 puts it first and keeps the rest. args: city, item, append, first, player."


def cmd_produce(args):
	city = _city(args)
	szItem = args["item"]
	iItem = _infoIndex(szItem)
	if szItem.startswith("UNIT_"):
		eOrder = OrderTypes.ORDER_TRAIN
		bCan = city.canTrain(iItem, False, False)
	elif szItem.startswith("BUILDING_"):
		eOrder = OrderTypes.ORDER_CONSTRUCT
		bCan = city.canConstruct(iItem, False, False, False)
	elif szItem.startswith("PROJECT_"):
		eOrder = OrderTypes.ORDER_CREATE
		bCan = city.canCreate(iItem, False, False)
	elif szItem.startswith("PROCESS_"):
		eOrder = OrderTypes.ORDER_MAINTAIN
		bCan = city.canMaintain(iItem, False)
	else:
		raise ValueError("%s is not a UNIT_, BUILDING_, PROJECT_ or PROCESS_ type" % szItem)
	if not bCan:
		# <!-- custom: At turn 71 of the fog-on playthrough (2026-11-13) Carthage could not train a Settler and the error said no more; the window shows such an item greyed with its hover text, which held the reason, "National Unit: 0 Left", as the Settler on its way still counted. Give that text when the item is shown in the window at all. (Claude code Opus 5.5) -->
		szHelp = None
		if eOrder == OrderTypes.ORDER_TRAIN and city.canTrain(iItem, False, True):
			szHelp = CyGameTextMgr().getUnitHelp(iItem, False, False, False, city)
		elif eOrder == OrderTypes.ORDER_CONSTRUCT and city.canConstruct(iItem, False, True, False):
			szHelp = CyGameTextMgr().getBuildingHelp(iItem, False, False, False, city)
		elif eOrder == OrderTypes.ORDER_CREATE and city.canCreate(iItem, False, True):
			szHelp = CyGameTextMgr().getProjectHelp(iItem, False, city)
		# <!-- custom: 'produce item=BUILDING_MONUMENT' in a city that had one was refused with no reason, as the window hides a built building (turn 94, 2026-11-13). (Claude code Opus 5.5) -->
		if eOrder == OrderTypes.ORDER_CONSTRUCT and city.getNumRealBuilding(iItem) > 0:
			raise ValueError("%s already has %s" % (city.getName(), szItem))
		if szHelp:
			raise ValueError("%s cannot produce %s now; the window's hover text: %s" % (city.getName(), szItem, _plainText(szHelp).replace(u"\n", u" | ")))
		# <!-- custom: An item the window does not list at all has no hover text: Kerkouane's Archer at turn 129 of the fog-on playthrough (2026-11-13) was refused with no more said, as the Longbowman had made it obsolete. (Claude code Opus 5.5) -->
		raise ValueError("%s cannot produce %s now: the window does not offer it, for instance obsolete or missing its tech or resource; 'city' lists what it offers" % (city.getName(), szItem))
	bAppend = bool(args.get("append", False))
	# <!-- custom: Putting a Galley ahead of a half-built Library at turn 105 of the fog-on playthrough (2026-11-13) meant replacing the queue or appending; first=1 inserts at the front and keeps the rest, as the city screen's ctrl-click does. CyCity.pushOrder with bAppend false inserts at position 0. (Claude code Opus 5.5) -->
	bFirst = bool(args.get("first", False))
	if not bAppend and not bFirst:
		city.clearOrderQueue()
	city.pushOrder(eOrder, iItem, -1, False, False, bAppend, False)
	return _cityBrief(city)


_HELP["dequeue"] = "Remove one item from a city's build queue, as clicking it in the city screen's queue does; production put into it stays with the city as for any change. index is its place in the queue as 'city' lists it (0 is what is being built now). args: city, index, player."


def cmd_dequeue(args):
	# <!-- custom: The city screen removes any queued item with a click, while 'produce' could only replace the queue, append or put first, so dropping one item meant rebuilding the rest (2026-11-14). CyCity.popOrder with bFinish and bChoose off is what that click does. (Claude code Opus 5.5) -->
	city = _city(args)
	iIndex = int(args["index"])
	if iIndex < 0 or iIndex >= city.getOrderQueueLength():
		raise ValueError("%s has no queue item %d; its queue: %s" % (city.getName(), iIndex, _cityBrief(city)["queue"]))
	city.popOrder(iIndex, False, False)
	return _cityBrief(city)


_HELP["finance"] = "The Domestic Advisor's Finance tab: treasury and net gold per turn, the sliders, gross gold, trade routes split into domestic and foreign, gold from deals with other players, and the expenses with inflation as the tab adds them (unit cost, unit supply, city maintenance, civic upkeep). args: player."


def cmd_finance(args):
	# <!-- custom: The Finance tab breaks gold down into income and expenses, which the pilot had only as two totals in 'player' (turn 265 of the modern baseline, 2026-11-14, visual pass over the advisors). The expense arithmetic is the tab's own (CvDomesticAdvisor.py), inflation applied per line and once overall. (Claude code Opus 5.5) -->
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
		# <!-- custom: More of the advisor's overview pages, as the user asked at turn 157 of the turn-0 game (2026-11-14): defense and garrison and the revolt chance from page 1 (advc.ctr's column; Orleans showed 9.2% to Pericles's culture at turn 139, which the pilot learned only from a turn message), food stored against the growth threshold from page 2, war weariness from page 3, and the turn founded from page 4. Revolt in per mille, an integer, as floats lose precision inside Civ4 (KI#1093). (Claude code Opus 5.5) -->
		row["defensePercent"] = city.getDefenseModifier(False)
		row["garrison"] = city.plot().getNumDefenders(city.getOwner())
		row["revoltPerMille"] = int(1000 * city.revoltProbability())
		row["foodStored"] = city.getFood()
		row["growthThreshold"] = city.growthThreshold()
		row["warWearinessPercent"] = city.getWarWearinessModifier()
		row["foundedTurn"] = city.getGameTurnFounded()
		rows.append(row)
	summary = {"cities": len(rows), "coastal": len([r for r in rows if r["coastal"]]), "unhealthy": [r["name"] for r in rows if r["healthMargin"] < 0], "atHealthCap": [r["name"] for r in rows if r["healthMargin"] == 0], "unhappy": [r["name"] for r in rows if r["happyMargin"] < 0], "atHappyCap": [r["name"] for r in rows if r["happyMargin"] == 0], "starving": [r["name"] for r in rows if r["food"] < 0]}
	return {"greatPeopleThreshold": player.greatPeopleThreshold(False), "summary": summary, "cities": rows}


_HELP["greatpeople"] = "Great People planning: the threshold for the next one; per city with points, its progress, points per turn, rate modifier, turns left at that rate, and the mix of Great Person types its points came from, with each type's chance (as the city screen's Great People bar shows); and the techs whose first discoverer gets a free Great Person that no team has yet, with whether we can research each now and in how many turns. args: player."


def cmd_greatpeople(args):
	# <!-- custom: The user wanted to plan Great People while watching the bar (2026-11-14): 'domestic' gave each city's progress and rate but not which type it would bring, how soon, or which first-discovery techs are still open. The chance per type is its share of the city's points, which is how CvCity::createGreatPeople picks one. (Claude code Opus 5.5) -->
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


_HELP["military"] ="The Military Advisor's summary as decisions need it: unit counts by domain, military and civilian; where they stand (own cities, own land, neutral land, enemy land, other land); the wounded by ID; every unit that can upgrade now with its targets and cheapest cost, and the total; Great General progress; cities with walls and castles. args: player."


def cmd_military(args):
	# <!-- custom: From a visual pass over SAS's Military Advisor Summary at turn 265 of the modern baseline (2026-11-14): the pilot had the unit list but not what it adds up to, and the Summary's "Upgradeable: 24, total cost 2574" gave no unit IDs to act on. This lists them, cheapest target first; canUpgrade is the game's own check, so an SAS tech gate such as the Rifleman's Military Tradition is respected. (Claude code Opus 5.5) -->
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
		iClass = gc.getInfoTypeForString(szClass)
		if iClass >= 0:
			iBuilding = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationBuildings(iClass)
			defenses[szClass[14:]] = len([city for city in _cities(player) if iBuilding >= 0 and city.getNumBuilding(iBuilding) > 0])
	return {"units": player.getNumUnits(), "military": iMilitary, "byDomain": domains, "where": where, "wounded": wounded, "upgradeable": upgradeable, "upgradeTotalCost": sum([u["cheapest"] for u in upgradeable]), "greatGeneralProgress": player.getCombatExperience(), "greatGeneralThreshold": player.greatPeopleThreshold(True), "cities": player.getNumCities(), "citiesWith": defenses}


_HELP["relations"] ="Each player met, for weighing whom to please or anger: attitude toward the player, whether they will talk, war, peace treaty, open borders and defensive pact, the shortest distance between the two empires' cities and how many of their cities lie within 10 plots of ours, their score, their power against ours in per mille (powerRatioPerMille, 1489 is 1.489 times ours) wherever the scoreboard shows that ratio, and without fog their power. With graph=1 return player nodes and directed attitude edges, keyed by IDs. args: graph, player."


def _attitudeCount(iFrom, iTo):
	# <!-- custom: The number the Glance tab shows: the sum of the hover's modifiers, as AttitudeUtil.getAttitudeCount reads them, since AI_getAttitudeVal is not exposed to Python. (Claude code Opus 5.5) -->
	iTotal = 0
	for szLine in _plainText(CyGameTextMgr().getAttitudeString(iFrom, iTo)).split(u"\n"):
		match = re.match(u"^\\s*([-+][0-9]+)\\s?:", szLine)
		if match:
			iTotal += int(match.group(1))
	return iTotal


def _addRelationLink(edge, source, target):
	# <!-- custom: The F3 links are team relationships. Keep direction for vassalage and retain both treaties when the screen draws two lines. (GPT-6.1-Sol) -->
	iTarget = target.getID()
	edge["sameTeam"] = source.getID() == iTarget
	edge["vassalOfTarget"] = bool(source.isVassal(iTarget))
	edge["openBorders"] = bool(source.isOpenBorders(iTarget))
	edge["defensivePact"] = bool(source.isDefensivePact(iTarget))


def cmd_relations(args):
	# <!-- custom: Refusing Roosevelt's demand to stop trading with Kublai at turn 265 (2026-11-14) was weighed on power alone; the user pointed out that attitude and nearness matter as much: angering a strong rival far away costs less than angering a weak neighbour. One reply now gives them side by side. Under fog, distances use only the cities the player has seen, and power, which the window shows only through espionage, is left out. (Claude code Opus 5.5) -->
	player = _player(args)
	_requireOwnTeamUnderFog(args, player, "relations")
	team = gc.getTeam(player.getTeam())
	iFogTeam = _fogTeam(args)
	ours = _cities(player)
	result = []
	bGraph = bool(args.get("graph"))
	nodes = [{"id": player.getID(), "team": player.getTeam(), "name": player.getName()}]
	edges = []
	for iOther in range(gc.getMAX_CIV_PLAYERS()):
		other = gc.getPlayer(iOther)
		if iOther == player.getID() or not other.isAlive() or other.isBarbarian() or not team.isHasMet(other.getTeam()):
			continue
		if bGraph and other.isMinorCiv():
			continue
		# <!-- custom: The city, not its plot: a plot seen before the city was founded on it counted the city, so Gilgamesh's city 4 plots away was in citiesSeen and closestCityDistance while 'map' showed none (Codex's review, round 35). The window shows a city once the city itself is revealed, as 'map' and 'cities' check. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		theirs = [city for city in _cities(other) if iFogTeam < 0 or city.isRevealed(iFogTeam, False)]
		distances = [plotDistance(a.getX(), a.getY(), b.getX(), b.getY()) for a in ours for b in theirs]
		near = [b for b in theirs if [a for a in ours if plotDistance(a.getX(), a.getY(), b.getX(), b.getY()) <= 10]]
		entry = {"player": iOther, "name": other.getName(), "team": other.getTeam(), "attitude": _enumName(AttitudeTypes, other.AI_getAttitude(player.getID())), "willTalk": bool(other.AI_isWillingToTalk(player.getID())), "atWar": bool(team.isAtWar(other.getTeam())), "peaceTreaty": bool(team.isForcePeace(other.getTeam())), "openBorders": bool(team.isOpenBorders(other.getTeam())), "defensivePact": bool(team.isDefensivePact(other.getTeam())), "score": gc.getGame().getPlayerScore(iOther), "citiesSeen": len(theirs), "citiesWithin10": len(near)}
		if distances:
			entry["closestCityDistance"] = min(distances)
		if iFogTeam < 0:
			entry["power"] = other.getPower()
		# <!-- custom: Their power against ours, as the scoreboard shows it beside each leader (1.9 is nearly twice as strong) wherever canSeeDemographics allows, which is the scoreboard's own condition (CvMainInterface, K-Mod), so under fog too: the user pointed to the scoreboard at turn 90 of the turn-0 game (2026-11-14), where Gilgamesh showed 1.9 and Zara Yaqob 2.0, while this command left power out under fog. (Claude code Opus 5.5) -->
		# <!-- custom: The attitude's modifiers as the hover over a met leader lists them (CvGameTextMgr::getAttitudeString), such as border tension or a shared religion: the user advised at turn 100 of the turn-0 game (2026-11-14) that settling by a strong neighbour, as Hastings was, costs attitude, and that these modifiers show it, so settling and trading choices can steer them. Plain lines, the first being the attitude itself. (Claude code Opus 5.5) -->
		entry["attitudeModifiers"] = [szLine for szLine in _plainText(CyGameTextMgr().getAttitudeString(iOther, player.getID())).split(u"\n") if szLine.strip()]
		# <!-- custom: In integer per mille (1489 for 1.489): a float came back as 1.4889999628067017, as Direct3D sets the FPU to single precision inside Civ4 (as for time.time(), see KI#1093). (Claude code Opus 5.5) -->
		if (iFogTeam < 0 or player.canSeeDemographics(iOther)) and player.getPower() > 0:
			entry["powerRatioPerMille"] = other.getPower() * 1000 / player.getPower()
		# <!-- custom: How this leader sees each other player we have met, as the Foreign Advisor's Glance tab shows it; the user noted attitudes are not symmetric (2026-11-14), and a weak target is best one its own neighbours dislike, so none comes to its aid. (Claude code Opus 5.5) -->
		if bGraph:
			nodes.append({"id": iOther, "team": other.getTeam(), "name": other.getName()})
		views = {}
		for iThird in range(gc.getMAX_CIV_PLAYERS()):
			third = gc.getPlayer(iThird)
			if iThird == iOther or not third.isAlive() or third.isBarbarian() or not gc.getTeam(other.getTeam()).isHasMet(third.getTeam()):
				continue
			if iThird != player.getID() and not team.isHasMet(third.getTeam()):
				continue
			if bGraph and third.isMinorCiv():
				continue
			# <!-- custom: The Glance tab's cell, not just the category: the user had the agent compare the tab with this reply at turn 127 of the turn-0 game (2026-11-14), and it showed numbers (+11 against +1 for the same Cautious-to-Pleased range), the worst-enemy icon, war and forced peace, and whether the leader would join a war against that player if asked (advc.152), all of which help pick a war target and its likely friends. Computed as AttitudeUtil.getAttitudeText does. (Claude code Opus 5.5) -->
			otherTeam = gc.getTeam(other.getTeam())
			bSameTeam = other.getTeam() == third.getTeam()
			cell = {"attitude": _enumName(AttitudeTypes, other.AI_getAttitude(iThird))[9:], "value": _attitudeCount(iOther, iThird), "worstEnemy": bool(not bSameTeam and not otherTeam.isHuman() and other.getWorstEnemyName() and other.getWorstEnemyName() == gc.getTeam(third.getTeam()).getName()), "atWar": bool(otherTeam.isAtWar(third.getTeam()))}
			# <!-- custom: Only the guards AttitudeUtil.getAttitudeText applies: forced peace only where our team is one side, and the war-trade test only between two other teams, neither human, not the same team. The first version asked a team to declare war on its own teammate, which trips AI_declareWarTrade's assertions, and showed peace between two third parties, which the tab hides (Codex's review, round 37). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if third.getTeam() == player.getTeam() and otherTeam.isForcePeace(third.getTeam()):
				cell["peaceTreaty"] = True
			if not bSameTeam and other.getTeam() != player.getTeam() and third.getTeam() != player.getTeam() and not otherTeam.isHuman() and not cell["atWar"] and otherTeam.AI_declareWarTrade(third.getTeam(), player.getTeam()) == -1:
				cell["wouldJoinWarIfAsked"] = True
			if bGraph:
				_addRelationLink(cell, otherTeam, gc.getTeam(third.getTeam()))
				cell["from"] = iOther
				cell["to"] = iThird
				edges.append(cell)
			else:
				views[third.getName()] = cell
		if bGraph:
			edge = {"from": player.getID(), "to": iOther, "atWar": entry["atWar"], "peaceTreaty": entry["peaceTreaty"]}
			_addRelationLink(edge, team, gc.getTeam(other.getTeam()))
			edges.append(edge)
		else:
			entry["viewsOf"] = views
		entry["attitudeValue"] = _attitudeCount(iOther, player.getID())
		result.append(entry)
	if bGraph:
		return {"viewer": player.getID(), "turn": gc.getGame().getGameTurn(), "nodes": nodes, "edges": edges}
	result.sort(lambda a, b: cmp(a.get("closestCityDistance", 999), b.get("closestCityDistance", 999)))
	return {"ourScore": gc.getGame().getPlayerScore(player.getID()), "players": result}


_HELP["espionage"] ="The espionage screen: per team met, the points gathered against it, the spending weight given to it and its counterespionage against us. With team and weight, set that weight, as the screen's +/- buttons do. args: team, weight, player."


def cmd_espionage(args):
	# <!-- custom: The pilot had nothing for espionage (2026-11-14): no points per rival, no spending weights, which the Espionage Advisor sets with its +/- buttons. (Claude code Opus 5.5) -->
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
	# <!-- custom: A spy sent to Madrid at turn 274 of the modern baseline (2026-11-14) arrived after Kublai had captured it, and 'spy' gave a bare [] there: the 40 points held against Kublai paid for no mission, as the window's popup lists only those it could. Name the plot's owner and the points against that team, so an empty list says why. (Claude code Opus 5.5) -->
	iOwner = unit.plot().getOwner()
	if iOwner < 0:
		return {"target": None, "points": None, "missions": missions}
	iTargetTeam = gc.getPlayer(iOwner).getTeam()
	reply = {"target": iOwner, "targetName": gc.getPlayer(iOwner).getName(), "points": gc.getTeam(unit.getTeam()).getEspionagePointsAgainstTeam(iTargetTeam), "missions": missions}
	# <!-- custom: At Oporto on turn 283 (2026-11-14), with 901 points against Roosevelt, 'spy' still gave no missions: the spy had moved that turn, and CvUnit::canEspionage refuses a spy that moved or attacked this turn, or one the target team can see. 'blocked' names the first such reason, so the agent waits a turn instead of guessing. (Claude code Opus 5.5) -->
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


_HELP["hurry"] = "Hurry a city's production. Without hurry, lists each HURRY_ type with whether the city can use it now and its gold and population cost, as the window's buttons show. args: city, hurry (HURRY_ type), player."


def cmd_hurry(args):
	city = _city(args)
	# <!-- custom: 'hurry city=Gondar' without a type raised a bare KeyError while looking for a way to rush a Trireme (2026-11-13, turn 154); like 'freetech' and 'research', it now lists the choices instead. (Claude code Opus 5.5) -->
	if args.get("hurry") is None:
		# <!-- custom: maxHurryPopulation, the most citizens a whip may take (half the city in CvCity::maxHurryPopulation): in the scouting trial (2026-11-14) a size-3 Constantinople read can=false for a 2-citizen whip with no reason given, and the DLL's canHurry showed the cap. (Claude code Opus 5.5) -->
		return {"city": city.getName(), "gold": gc.getPlayer(city.getOwner()).getGold(), "population": city.getPopulation(), "maxHurryPopulation": city.maxHurryPopulation(), "hurries": [{"hurry": gc.getHurryInfo(i).getType(), "can": bool(city.canHurry(i, False)), "goldCost": city.hurryGold(i), "populationCost": city.hurryPopulation(i)} for i in range(gc.getNumHurryInfos())]}
	iHurry = _typedIndex(args["hurry"], "HURRY_", gc.getNumHurryInfos(), gc.getHurryInfo)
	if not city.canHurry(iHurry, False):
		raise ValueError("%s cannot hurry with %s now" % (city.getName(), args["hurry"]))
	city.hurry(iHurry)
	return _cityBrief(city)


_HELP["endturn"] = "End the active player's turn, as the End Turn button does once nothing waits for orders."


def cmd_endturn(args):
	player = gc.getPlayer(_activePlayerId())
	if not player.isTurnActive():
		raise ValueError("it is not the active player's turn")
	# <!-- custom: In the fog-on playthrough (2026-11-13) three turns ended with no research set, as 'endturn' said nothing about what still waited. It still ends the turn, as Ctrl+Enter does in the window, but reports in 'skipped' what 'todo' listed, so a caller sees what it left. (Claude code Opus 5.5) -->
	# <!-- custom: Moctezuma's war declaration at turn 148 stayed open on the diplomacy screen while three 'endturn' calls went through, each reporting it under 'skipped' (2026-11-13); in the window that screen covers the End Turn button until it is answered, so 'endturn' refuses as well. (Claude code Opus 5.5) -->
	if _diploState()["open"]:
		raise ValueError("a diplomacy screen waits for an answer; see 'diplo' and 'reply'")
	# <!-- custom: A contact the pilot queued opens on later frames, so an 'endturn' right after it could slip past the check above (Codex's review); refused as 'menu' does. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
	# <!-- custom: Messages are stamped with the turn they were made in, and those made as a turn starts carry that turn, so "Pacal II will trade Agriculture, Mysticism" showed in the digests of turns 41 and 42 (fog-on playthrough, 2026-11-13). The digest now leaves out messages it already showed; 'messages' itself still lists everything since the turn asked for. (Claude code Opus 5.5) -->
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
	# <!-- custom: The scoreboard's power ratios in every turn's digest: the user advised watching military power every turn, as it decides much of the game and our rivals' ratios fell from 1.2-2.2 to 0.9-1.5 times ours over turns 90 to 106 of the turn-0 game (2026-11-14). Per met player whose ratio the scoreboard shows (canSeeDemographics), their power against ours in per mille, as in 'relations'. (Claude code Opus 5.5) -->
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
	# <!-- custom: A held popup that only informs: the "feat" popups of CvAdvisorUtils.py, such as "you have trained your first Archery unit", whose callback only opens an advisor or does nothing. One came at turn 60 of the fog-on playthrough (2026-11-13), listed in 'todo' as waiting while 'answer' could not take it, as it is a Python popup. (Claude code Opus 5.5) -->
	if popup["state"] == "HELD" and popup["onClicked"] == "featAccomplishedOnClickedCallback":
		return True
	# <!-- custom: A plain text popup, such as the Apostolic Palace's election result at turn 138 of the fog-on playthrough (2026-11-13): its only button is OK, and CvDLLButtonPopup::OnOkClicked does nothing for it, so it waited in 'todo' with no button 'answer' could take. (Claude code Opus 5.5) -->
	if popup["state"] == "HELD" and popup["type"] == "BUTTONPOPUP_TEXT":
		return True
	# <!-- custom: The tech splash, era and wonder movie screens only show what happened. The hold lets screens through, and AdvCiv's Minimize Pop-Ups kept them queued until every unit had moved, so twelve had piled up by turn 97 of the fog-on playthrough (2026-11-13); closing one diplomacy screen brought up the Animal Husbandry splash of turn 14. Queued ones are notices; one already on display stays until clicked in the window. (Claude code Opus 5.5) -->
	return popup["state"] == "QUEUED" and popup["type"] == "BUTTONPOPUP_PYTHON_SCREEN" and popup["text"] in _INFO_SCREENS


_INFO_SCREENS = ("showTechSplash", "showEraMovie", "showWonderMovie")


def _closeInfoScreens(bClose=True):
	# <!-- custom: A tech splash on display kept the diplomacy screen from opening at turn 97 of the fog-on playthrough (2026-11-13): 'contact' opened nothing until it was closed, and a tech traded right after showed its splash at once. These screens only inform, so close one on display as its Continue or OK button does, by hiding it under the name it was shown with (CvTechSplashScreen.py, CvWonderMovieScreen.py, CvEraMovieScreen.py), and report it as a notice. (Claude code Opus 5.5) -->
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
		# <!-- custom: data3 is 0 for a wonder, 1 for a religion founded and 2 for a project (CvEventManager.py). The first version read every one as a building, and the Hinduism movie came out as "Wonder movie: BUILDING_CITY_CENTER". (Claude code Opus 5.5) -->
		if popup["data3"] == 1:
			return u"Religion movie: %s" % _typeOrNone(gc.getReligionInfo, popup["data1"])
		if popup["data3"] == 2:
			return u"Project movie: %s" % _typeOrNone(gc.getProjectInfo, popup["data1"])
		return u"Wonder movie: %s" % _typeOrNone(gc.getBuildingInfo, popup["data1"])
	return _plainText(szText)


def _takeNotices():
	# <!-- custom: Gives each notice's text once and drops it, as a person reads it and clicks OK. (Claude code Opus 5.5) -->
	# <!-- custom: Dropped one by one with dropSASPilotPopup: a held notice by its ID, a queued one by type, data1, data3 and text. The first version went through closeSASPilotPopups, which matches only type and data1 and runs killAll, and killAll recalls and relaunches the popups on display (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
	# <!-- custom: Saving over an existing file made the EXE ask "already exists. Press OK to proceed, overwriting the file" in the window, which the pilot cannot answer, and the reply still said exists for the old file (2026-11-13). So an existing file is refused unless overwrite=true, and then removed first, which is what that OK does. (Claude code Opus 5.5) -->
	# <!-- custom: With overwrite, the new save is written beside the old one and replaces it only once it exists: the first version removed the old file first, so a failed write would have lost both (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if os.path.isfile(args["path"]):
		if args.get("overwrite") is not True:
			raise ValueError("%s exists; pass overwrite=true to replace it" % args["path"])
		# <!-- custom: The second version still used one fixed ".new" name, so a file left by an earlier failed attempt could pass the size check and be installed stale, and it removed the old save before the rename, so a failed rename left only the temporary file (Codex's review). Both side files now get names unused at that moment, and the old save is only renamed aside until the new one is in place; Python 2.4 on Windows has no atomic replace, since os.rename refuses an existing target. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		szNew = _unusedSibling(args["path"], "new")
		gc.getGame().saveGame(str(szNew))
		if not os.path.isfile(szNew) or os.path.getsize(szNew) == 0:
			raise ValueError("the new save was not written; %s is unchanged" % args["path"])
		# <!-- custom: Codex's round-16 review, with mocked failures: when putting the old save back failed too, the error did not say it was kept as the .old file, and a failed removal of that file after the new save was in place reported the whole save as failed. Each outcome now names where the files are. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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


_HELP["menu"] = "Leave the game for the main menu; with path, load that save instead. The reply is written first; the pilot answers again once a game runs. args: path."


def cmd_menu(args):
	# <!-- custom: Leaving a Huge turn-305 game this way crashed Civ4 in the EXE every time (2026-11-13), whatever was loaded next; in big games close the client and start it with the save instead. See KI#1084. (Claude code Opus 5.5) -->
	# <!-- custom: The EXE's binding takes (path, bool) although its help string shows the path alone; False loaded the save in the same process. What the bool changes is not known. (Claude code Fable 5.2) -->
	# <!-- custom: Refused while a diplomacy screen is open, as the window does, its screen being modal: loaded from under an open screen, the screen stayed open over the new game with the old partner and offers, and 1 of 4 such loads crashed Civ4 with the diplomacy screen on the stack, while 8 of 8 loads with it closed worked (2026-11-13). See KI#1088. (Claude code Opus 5.5) -->
	if _diploState()["open"]:
		raise ValueError("a diplomacy screen is open; close it first ('diplo', then 'reply' with its Farewell), as the window allows no load while it is open")
	# <!-- custom: Also while a contact is queued but its screen not yet open, which would then open over the loaded game (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if _pendingContact() is not None:
		raise ValueError("a diplomacy screen is about to open; read 'diplo' and close it first")
	CyInterface().exitingToMainMenu(str(args.get("path", "")), False)
	return None


_HELP["screen"] = "Call a CvScreensInterface function, e.g. name=showDomesticAdvisor, name=pediaJumpToUnit args=[UNIT_ index], name=pediaShow. args: name, args (list, optional)."


# <!-- custom: Fixed arguments for the play screens that index an argument list, as the play role allows them only without args and the None retry below failed for them (Codex's review, round 34): the Info Screen's first tab outside the end of a game, the Hall of Fame without replays, the Sevopedia's first category. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
# <!-- custom: showForeignAdvisorScreen too: called with None it passed None as the tab to SASGameRecordActions.logScreenAction, whose DLL binding takes an int, and failed (turn 114 of the turn-0 game, 2026-11-14); -1 is its own default tab. (Claude code Opus 5.5) -->
_SCREEN_DEFAULT_ARGS = {"showInfoScreen": [0, 0], "showHallOfFame": [0], "pediaMain": [0], "showForeignAdvisorScreen": [-1]}


def cmd_screen(args):
	function = getattr(CvScreensInterface, args["name"])
	if "args" not in args and _SCREEN_DEFAULT_ARGS.has_key(args["name"]):
		function(_SCREEN_DEFAULT_ARGS[args["name"]])
	elif "args" in args:
		function(args["args"])
	else:
		try:
			function()
		except TypeError:
			function(None)
	return None


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
	# <!-- custom: The window says "Adopt Caste System?", while the held CHANGECIVIC popup at turn 70 of the fog-on playthrough (2026-11-13) gave data1 2 and data2 12 with no text. Name what the data stand for in the popups the pilot answers, from each launcher's use of them in CvDLLButtonPopup.cpp. (Claude code Opus 5.5) -->
	szType = popup["type"]
	if szType == "BUTTONPOPUP_CHANGECIVIC":
		popup["about"] = {"civicOption": _typeOrNone(gc.getCivicOptionInfo, popup["data1"]), "civic": _typeOrNone(gc.getCivicInfo, popup["data2"])}
	elif szType == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0:
		popup["about"] = {"freeTechs": popup["data1"], "use": "freetech"}
	elif szType == "BUTTONPOPUP_DECLAREWARMOVE":
		# <!-- custom: Declaring war in the diplomacy screen raised this confirmation, held by the pilot, with the target team in data1 (2026-11-13). (Claude code Opus 5.5) -->
		popup["about"] = {"team": popup["data1"], "leaders": [gc.getPlayer(i).getName() for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and gc.getPlayer(i).getTeam() == popup["data1"]]}
	elif szType == "BUTTONPOPUP_CHANGERELIGION":
		popup["about"] = {"religion": _typeOrNone(gc.getReligionInfo, popup["data1"])}
	elif szType == "BUTTONPOPUP_DIPLOVOTE":
		# <!-- custom: The resolution the window shows, which the DLL puts in the text (getSASPilotPopups); 'todo' lists 'about', not the text. A TEAM_<id> button elects that team. (Claude code Opus 5.5) -->
		popup["about"] = {"resolution": _plainText(popup["text"])}
	elif szType in ("BUTTONPOPUP_RAZECITY", "BUTTONPOPUP_CHOOSEPRODUCTION"):
		city = gc.getPlayer(_activePlayerId()).getCity(popup["data1"])
		if city is not None and not city.isNone():
			popup["about"] = {"city": city.getName()}
	elif szType == "BUTTONPOPUP_PYTHON" and popup.get("onClicked") == CITY_TIP_CALLBACK:
		# <!-- custom: The advisor's tip to build something, such as Hippo's Colosseum or Utica's Punic Agora (turns 155 and 174, 2026-11-13): data1 is the city, data2 the order type and data3 the item. Its buttons come from the DLL (getSASPilotPopupButtons), which 'answer' then uses as for any other popup. (Claude code Opus 5.5) -->
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


_HELP["popups"] = "The active player's popups. HELD ones were kept from the window while the pilot drives and can be answered by their id; DISPLAYED and QUEUED ones are in the window. Each has state, id (-1 unless held), type (BUTTONPOPUP_ name), data1-3, flags, options, buttons (the ones 'answer' takes now, by number and name) and text. args: held (optional, 1 or 0, to switch holding on or off first; switching it off hands the held popups back to the window)."


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
	# <!-- custom: By id rather than list position: Codex's review found a position could name another popup after the list shifted. The DLL prunes and looks the id up again before answering. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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


# City screen

def _cityPlots(city):
	plots = []
	for i in range(gc.getNUM_CITY_PLOTS()):
		plot = city.getCityIndexPlot(i)
		if plot is None or plot.isNone():
			continue
		plots.append({"index": i, "x": plot.getX(), "y": plot.getY(), "worked": city.isWorkingPlot(plot), "canWork": city.canWork(plot), "yields": _yields(plot.getYield)})
	return plots


def _citizens(city):
	result = {"city": city.getName(), "population": city.getPopulation(), "angry": city.angryPopulation(0), "automated": city.isCitizensAutomated(), "foodDifference": city.foodDifference(True), "yieldRate": _yields(city.getYieldRate)}
	result["plots"] = _cityPlots(city)
	specialists = {}
	for i in range(gc.getNumSpecialistInfos()):
		iCount = city.getSpecialistCount(i)
		iMax = city.getMaxSpecialistCount(i)
		if iCount > 0 or iMax > 0 or city.isSpecialistValid(i, 1):
			specialists[gc.getSpecialistInfo(i).getType()] = {"count": iCount, "max": iMax, "forced": city.getForceSpecialistCount(i), "canAdd": city.isSpecialistValid(i, 1), "free": city.getFreeSpecialistCount(i)}
	result["specialists"] = specialists
	result["emphasize"] = [gc.getEmphasizeInfo(i).getType() for i in range(gc.getNumEmphasizeInfos()) if city.AI_isEmphasize(i)]
	return result


_HELP["citizens"] = "A city's screen: each plot in its radius with whether it is worked and can be, its specialists with their limits, whether the governor assigns citizens, and its emphasis buttons. With automated=1 or 0, switch the governor first. args: city, automated, player."


def cmd_citizens(args):
	# <!-- custom: The city screen's controls go through CvCity::doTask, as its buttons do, so the governor reacts as it would for a person: a hand-picked plot is kept as an override, and freed citizens are reassigned. (Claude code Fable 5.2) -->
	city = _city(args)
	if args.get("automated") is not None:
		city.doTask(TaskTypes.TASK_SET_AUTOMATED_CITIZENS, -1, -1, bool(args["automated"]))
	return _citizens(city)


_HELP["work"] = "Click a plot in a city's radius, as on the city screen: a worked plot is freed, a free one is worked (taking a citizen from elsewhere), the city's own plot switches the governor back on, and a plot of the player's that another city works is claimed for this city. args: city, x, y, player."


def cmd_work(args):
	city = _city(args)
	plot = _plot(args)
	iIndex = city.getCityPlotIndex(plot)
	if iIndex < 0 or iIndex >= gc.getNUM_CITY_PLOTS():
		raise ValueError("%d,%d is outside %s's radius" % (plot.getX(), plot.getY(), city.getName()))
	# <!-- custom: Every click is TASK_CHANGE_WORKING_PLOT, as on the city screen, whose handler CvCity::alterWorkingPlot switches the governor back on for the city's own plot and, for a plot the city cannot work but owns, claims it from the city working it.
	# The first version sent TASK_CLEAR_WORKING_OVERRIDE for the city's own plot and refused plots the city could not work; Codex's review pointed out the difference. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	city.doTask(TaskTypes.TASK_CHANGE_WORKING_PLOT, iIndex, -1, False)
	return _citizens(city)


_HELP["specialist"] = "Add or remove a city's specialists, as the plus and minus buttons do. args: city, type (SPECIALIST_ type), change (default 1; negative removes), player."


def cmd_specialist(args):
	city = _city(args)
	iSpecialist = _typedIndex(args["type"], "SPECIALIST_", gc.getNumSpecialistInfos(), gc.getSpecialistInfo)
	iChange = int(args.get("change", 1))
	if iChange > 0 and not city.isSpecialistValid(iSpecialist, iChange):
		raise ValueError("%s cannot take %d more %s" % (city.getName(), iChange, args["type"]))
	if iChange < 0 and city.getSpecialistCount(iSpecialist) < -iChange:
		raise ValueError("%s has only %d %s" % (city.getName(), city.getSpecialistCount(iSpecialist), args["type"]))
	city.doTask(TaskTypes.TASK_CHANGE_SPECIALIST, iSpecialist, iChange, False)
	return _citizens(city)


_HELP["emphasize"] = "Switch one of a city's emphasis buttons, such as EMPHASIZE_FOOD or EMPHASIZE_AVOID_GROWTH. args: city, type (EMPHASIZE_ type), on (default 1), player."


def cmd_emphasize(args):
	city = _city(args)
	city.doTask(TaskTypes.TASK_SET_EMPHASIZE, _typedIndex(args["type"], "EMPHASIZE_", gc.getNumEmphasizeInfos(), gc.getEmphasizeInfo), -1, bool(args.get("on", True)))
	return _citizens(city)


# Empire choices

_HELP["civics"] = "Without set: each civic option with the current civic and the ones the player can adopt, and whether a revolution is possible now. With set: adopt those civics, one per option at most, as the civics screen's Revolution button does. args: set (list of CIVIC_ types), player."


def cmd_civics(args):
	player = _player(args)
	civics = [player.getCivics(i) for i in range(gc.getNumCivicOptionInfos())]
	if args.get("set") is None:
		options = {}
		for iOption in range(gc.getNumCivicOptionInfos()):
			available = [gc.getCivicInfo(i).getType() for i in range(gc.getNumCivicInfos()) if gc.getCivicInfo(i).getCivicOptionType() == iOption and player.canDoCivics(i)]
			options[gc.getCivicOptionInfo(iOption).getType()] = {"current": gc.getCivicInfo(civics[iOption]).getType(), "available": available}
		return {"options": options, "canRevolution": player.canRevolution(0), "revolutionTimer": player.getRevolutionTimer(), "anarchyTurns": player.getAnarchyTurns()}
	wanted = args["set"]
	if isinstance(wanted, (str, unicode)):
		wanted = [wanted]
	for szCivic in wanted:
		iCivic = _typedIndex(szCivic, "CIVIC_", gc.getNumCivicInfos(), gc.getCivicInfo)
		# <!-- custom: canAdopt (CvPlayer::canRevolution) only checks that a revolution is possible and changes something, not that each civic is available: the first test adopted Slavery on turn 0, without its tech (2026-11-13). The civics screen never offers such a civic, so check it here. (Claude code Fable 5.2) -->
		if not player.canDoCivics(iCivic):
			raise ValueError("player %d cannot adopt %s; 'civics' lists the available ones" % (player.getID(), szCivic))
		civics[gc.getCivicInfo(iCivic).getCivicOptionType()] = iCivic
	if not player.canAdopt(civics):
		# <!-- custom: After enemy spies imposed Despotism at turn 113 of the fog-on playthrough (2026-11-13), restoring Hereditary Rule was refused with no reason; the revolution timer was at 4. Say so. (Claude code Opus 5.5) -->
		raise ValueError("player %d cannot start a revolution to %s now (revolution timer %d, anarchy turns %d)" % (player.getID(), ", ".join(wanted), player.getRevolutionTimer(), player.getAnarchyTurns()))
	iAnarchy = player.getCivicAnarchyLength(civics)
	# <!-- custom: Applied directly rather than with CyMessageControl().sendUpdateCivics, which the civics screen uses: the net message is handled after the reply is written, so the first test's reply still showed the old civics. Both end in CvPlayer::revolution; a network game would need the message. (Claude code Fable 5.2) -->
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


_HELP["religion"] = "Without args: the state religion and the religions the player can convert to now. With convert: convert to it (NO_RELIGION: none). args: convert (RELIGION_ type), player."


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
	return {"stateReligion": _typeOrNone(gc.getReligionInfo, player.getStateReligion()), "canConvertTo": [gc.getReligionInfo(i).getType() for i in range(gc.getNumReligionInfos()) if player.canConvert(i)], "anarchyLength": player.getReligionAnarchyLength()}


# Sevopedia

_reMarkup = re.compile(r"<[^>]*>")


# <!-- custom: Static facts are in the XML files, which an agent can read directly; what the files lack is the effects text the DLL composes from them and from its own rules, as the Sevopedia shows it, so 'pedia' returns that (the user's point, 2026-11-13).
# One function per kind, with differing arguments. (Claude code Fable 5.2) -->
def _pediaEffects(szPrefix, iType):
	mgr = CyGameTextMgr()
	if szPrefix == "UNIT_":
		return mgr.getUnitHelp(iType, True, False, False, None)
	if szPrefix == "BUILDING_":
		return mgr.getBuildingHelp(iType, True, False, False, None)
	if szPrefix == "PROJECT_":
		return mgr.getProjectHelp(iType, True, None)
	if szPrefix == "TECH_":
		return mgr.getTechHelp(iType, True, False, False, False, -1)
	if szPrefix == "PROMOTION_":
		return mgr.getPromotionHelp(iType, True)
	if szPrefix == "BONUS_":
		return mgr.getBonusHelp(iType, True)
	if szPrefix == "IMPROVEMENT_":
		return mgr.getImprovementHelp(iType, True)
	if szPrefix == "TERRAIN_":
		return mgr.getTerrainHelp(iType, True)
	if szPrefix == "FEATURE_":
		return mgr.getFeatureHelp(iType, True)
	if szPrefix == "CIVIC_":
		return mgr.parseCivicInfo(iType, True, False, True)
	if szPrefix == "RELIGION_":
		return mgr.parseReligionInfo(iType, True)
	if szPrefix == "CORPORATION_":
		return mgr.parseCorporationInfo(iType, True)
	if szPrefix == "SPECIALIST_":
		return mgr.getSpecialistHelp(iType, True)
	return None


_PEDIA_KINDS = (
	("UNIT_", "getNumUnitInfos", "getUnitInfo"),
	("BUILDING_", "getNumBuildingInfos", "getBuildingInfo"),
	("PROJECT_", "getNumProjectInfos", "getProjectInfo"),
	("TECH_", "getNumTechInfos", "getTechInfo"),
	("PROMOTION_", "getNumPromotionInfos", "getPromotionInfo"),
	("BONUS_", "getNumBonusInfos", "getBonusInfo"),
	("IMPROVEMENT_", "getNumImprovementInfos", "getImprovementInfo"),
	("TERRAIN_", "getNumTerrainInfos", "getTerrainInfo"),
	("FEATURE_", "getNumFeatureInfos", "getFeatureInfo"),
	("CIVIC_", "getNumCivicInfos", "getCivicInfo"),
	("RELIGION_", "getNumReligionInfos", "getReligionInfo"),
	("CORPORATION_", "getNumCorporationInfos", "getCorporationInfo"),
	("SPECIALIST_", "getNumSpecialistInfos", "getSpecialistInfo"),
	("LEADER_", "getNumLeaderHeadInfos", "getLeaderHeadInfo"),
	("CIVILIZATION_", "getNumCivilizationInfos", "getCivilizationInfo"),
	("TRAIT_", "getNumTraitInfos", "getTraitInfo"),
	("BUILD_", "getNumBuildInfos", "getBuildInfo"),
	("ROUTE_", "getNumRouteInfos", "getRouteInfo"),
	("HANDICAP_", "getNumHandicapInfos", "getHandicapInfo"),
	("ERA_", "getNumEraInfos", "getEraInfo"),
)


def _pediaKind(szType):
	for kind in _PEDIA_KINDS:
		if szType.startswith(kind[0]):
			return kind
	raise ValueError("no Sevopedia kind for %s; kinds: %s" % (szType, " ".join([kind[0] for kind in _PEDIA_KINDS])))


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


_HELP["types"] = "The XML types of one kind, to browse as the Sevopedia's lists: kind is a prefix such as UNIT_, BUILDING_, TECH_, CIVIC_, BONUS_, PROMOTION_; without it, the kinds. args: kind."


def cmd_types(args):
	if args.get("kind") is None:
		return [kind[0] for kind in _PEDIA_KINDS]
	kind = _pediaKind(args["kind"])
	return [getattr(gc, kind[2])(i).getType() for i in range(getattr(gc, kind[1])())]


_HELP["pedia"] = "A type's Sevopedia entry as text: its name, the effects text the Sevopedia shows beside it, and its help and strategy texts, with markup removed. 'info' gives the same type's raw getters. args: type (e.g. UNIT_WARRIOR), long (1 to include the Civilopedia text, default 0)."


def cmd_pedia(args):
	szType = args["type"]
	kind = _pediaKind(szType)
	iType = _infoIndex(szType)
	info = getattr(gc, kind[2])(iType)
	# <!-- custom: Checked by the entry's own type, as a BUILDINGCLASS_ or UNITCLASS_ type also starts with BUILDING or UNIT. (Claude code Fable 5.2) -->
	if info is None or info.getType() != szType:
		raise ValueError("%s is not a %s type" % (szType, kind[0]))
	result = {"type": szType, "name": info.getDescription(), "effects": None}
	szEffects = _pediaEffects(kind[0], iType)
	if szEffects is not None:
		result["effects"] = _plainText(szEffects)
	result["help"] = _plainText(info.getHelp())
	result["strategy"] = _plainText(info.getStrategy())
	if args.get("long"):
		result["civilopedia"] = _plainText(info.getCivilopedia())
	return result


_HELP["batch"] = "Run several commands in one request, in order, stopping at the first failure. args: commands (list of {cmd, args}). From the CLI: SASPilotClient.py batch 'commands=[{\"cmd\":\"units\"},{\"cmd\":\"cities\"}]'."


def cmd_batch(args):
	# <!-- custom: A request waited for the next game update, about 250 ms each when measured (2026-11-13), so a turn's worth of orders was far quicker as one request; served every frame it is now about 2 ms, which still makes one request cheaper. (Claude code Fable 5.2 + Opus 5.5) -->
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


_HELP["py"] = "Run Python inside the game and return what it printed, plus the value of 'result' if the code sets it, or of the code itself when it is one expression. The namespace persists between calls and has gc, game, map, interface, player (active), describe() and everything from CvPythonExtensions. args: code."


def cmd_py(args):
	namespace = _state["py"]
	if "gc" not in namespace:
		# <!-- custom: Was the statement form exec "..." in namespace, which Python 2.4 runs but Ruff's modern parser cannot read, so CI's Ruff stopped on this file (Codex found it). eval of a code object compiled in "exec" mode runs the statements in both, checked with C:\Python24. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		eval(compile("from CvPythonExtensions import *\n", "<pilot>", "exec"), namespace)
	namespace["gc"] = gc
	namespace["game"] = gc.getGame()
	namespace["map"] = CyMap()
	namespace["interface"] = CyInterface()
	namespace["describe"] = describe
	namespace["pilot"] = sys.modules.get(__name__) or globals()
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
			compiled = compile(code, "<pilot>", "eval")
		except SyntaxError:
			compiled = None
		if compiled is not None:
			namespace["result"] = eval(compiled, namespace)
		else:
			# <!-- custom: The game's Python is 2.4, without "a if c else b": three agent sessions in a row wrote one into 'py' code on 2026-11-13 and read the bare "invalid syntax" each time. Name the likely cause when the failing line has that shape. (Claude code Opus 5.5) -->
			# <!-- custom: eval of an "exec" code object and sys.exc_info() replace exec ... in and "except SyntaxError, error", which Ruff cannot parse; see the namespace setup above. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			try:
				eval(compile(code + "\n", "<pilot>", "exec"), namespace)
			except SyntaxError:
				error = sys.exc_info()[1]
				szLine = error.text or ""
				if " if " in szLine and " else " in szLine:
					raise SyntaxError("%s; Python 2.4 has no 'a if c else b': use an if statement or (c and [a] or [b])[0]" % error)
				raise
	finally:
		sys.stdout = stdout
	return {"output": "".join(capture.parts), "result": namespace.get("result")}
