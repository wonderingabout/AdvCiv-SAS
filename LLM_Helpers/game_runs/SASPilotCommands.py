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
PILOT_REVISION = 4

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
		_writeAtomic(os.path.join(mailbox, "hello.json"), toJson({"pid": os.getpid(), "pilotRevision": PILOT_REVISION}))
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
		try:
			handle = open(path, "rb")
			text = handle.read()
			handle.close()
			os.remove(path)
		except (IOError, OSError):
			continue  # <!-- custom: still being written or already taken; the next tick retries (Claude code Fable 5.2) -->
		reply = _serve(text)
		state["served"] = state["served"] + 1
		szReply = toJson(reply)
		szReply = szReply[:-1] + ',"gameMs":' + repr((time.clock() - fStart) * 1000.0) + ',"tick":"' + state.get("lastTick", "") + '"}'
		_writeAtomic(os.path.join(mailbox, "rep_" + name[4:]), szReply)


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


def _serve(text):
	reply = {"ok": False}
	try:
		request = fromJson(text)
		reply["id"] = request.get("id")
		name = request["cmd"]
		args = request.get("args") or {}
		reply["result"] = _checkedHandler(name, args)(args)
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
	return {"id": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "owner": unit.getOwner(), "movesLeft": unit.movesLeft(), "damage": unit.getDamage(), "group": unit.getGroupID()}


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
	return {"missions": missions, "builds": builds, "commands": commands, "promotions": promotions, "upgrades": upgrades, "automations": automations}


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
_HELP = {}

_HELP["help"] = "List the commands with their one-line descriptions."


def cmd_help(args):
	return _HELP


_HELP["ping"] = "Bridge and game state: revision, PID, whether a game runs, turn, active player and whether it is that player's turn."


def cmd_ping(args):
	game = gc.getGame()
	iActive = game.getActivePlayer()
	result = {"pilotRevision": PILOT_REVISION, "pid": os.getpid(), "served": _state["served"], "loads": _state.get("loads"), "ticks": _state["ticks"], "reloadError": _state.get("reloadError"), "tickError": _state.get("tickError")}
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
	return result


_HELP["player"] = "One player's empire summary. args: player (default: the active player)."


def cmd_player(args):
	return _playerFull(_player(args))


_HELP["players"] = "Every player ever alive, as in 'player'."


def cmd_players(args):
	return [_playerFull(gc.getPlayer(i)) for i in range(gc.getMAX_PLAYERS()) if gc.getPlayer(i).isEverAlive()]


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


_HELP["plot"] = "One plot in full, with its units. args: x, y."


def cmd_plot(args):
	plot = _plot(args)
	text = _plotsJson(plot.getX(), plot.getY(), 0, _fogTeam(args))
	if text == "[]":
		raise ValueError("plot %d,%d is not revealed; fog is on" % (plot.getX(), plot.getY()))
	return RawJson(text[1:-1])


_HELP["plots"] = "The plots within a radius, in full. With fog on, only the plots the active team has revealed, each as it last saw it and with units only where it sees now. args: x, y, radius (default 1; the larger map side covers the whole map), fog (optional, overrides the 'fog' switch for this request)."


def cmd_plots(args):
	plot = _plot(args)
	return RawJson(_plotsJson(plot.getX(), plot.getY(), int(args.get("radius", 1)), _fogTeam(args)))


_HELP["fog"] = "Without args: whether fog is on. With on=1 or 0: switch it. With fog on, 'plots', 'plot', 'units', 'unit', 'cities' and 'city' give only what the active player's team knows or sees, as a person at the window would; off (the default) gives everything, for debugging. Other commands, such as 'players' and 'py', are not limited. args: on."


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
			result["diplomacy"] = {"screen": _diploToken(state), "who": state["who"], "aiComment": _typeOrNone(gc.getDiplomacyInfo, state["aiComment"]), "replies": [gc.getDiplomacyInfo(response["comment"]).getType() for response in state["responses"]]}
		# <!-- custom: A tech bought from Pacal at turn 148 (2026-11-13) put its splash on display at once, and 'todo' reported nothing while the window waited on Continue; only 'turn' closes such screens, as notices. Listed here unclosed, so a check of 'todo' alone sees the window is blocked. (Claude code Opus 5.5) -->
		screens = _closeInfoScreens(False)
		if screens:
			result["infoScreens"] = screens
	# <!-- custom: A free-tech chooser already on display, as after loading a save before the pilot held popups again, is not in heldPopups, so 'endturn --turns' did not stop for it (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	# <!-- custom: Only while the game still counts a free tech as owed: after 'freetech' took one through a displayed chooser, the chooser stayed on screen, and listing it kept 'todo' waiting for good (2026-11-13). (Claude code Opus 5.5) -->
	if player.getID() == gc.getGame().getActivePlayer() and hasattr(gc.getGame(), "getSASPilotPathJson"):
		displayed = [popup for popup in _popups() if popup["state"] == "DISPLAYED" and popup["type"] == "BUTTONPOPUP_CHOOSETECH" and popup["data1"] > 0]
		if displayed and _pilotGame("isSASPilotChoosingFreeTech").isSASPilotChoosingFreeTech():
			result["freeTechOwed"] = displayed[0]["data1"]
	return result


_HELP["research"] = "Without args: the techs the player can research now, each with its turns, and the research queue. With tech: research it; a tech not available yet is queued after its missing prerequisites, as a shift-click in the tech tree does. append=1 adds to the queue instead of replacing it. args: tech (TECH_ type), append, player."


def cmd_research(args):
	player = _player(args)
	if args.get("tech") is None:
		# <!-- custom: The list first held only the names, so choosing a tech meant a 'py' call per tech for what the window's tech chooser shows at a glance, its turns (fog-on playthrough, 2026-11-13). Each entry now has its turns at the current rate, its cost and the progress already made. (Claude code Opus 5.5) -->
		team = gc.getTeam(player.getTeam())
		available = [{"tech": gc.getTechInfo(i).getType(), "turns": player.getResearchTurnsLeft(i, True), "cost": team.getResearchCost(i), "progress": team.getResearchProgress(i)} for i in range(gc.getNumTechInfos()) if player.canResearch(i, False)]
		return {"available": available, "queue": _researchQueue(player)}
	iTech = _typedIndex(args["tech"], "TECH_", gc.getNumTechInfos(), gc.getTechInfo)
	# <!-- custom: Only techs available now were taken, so 'tech=TECH_BRONZE_WORKING' was refused while Mining was its one missing prerequisite (fog-on playthrough, 2026-11-13). CvPlayer::pushResearch queues the missing prerequisites first, as the tech tree's shift-click does, so take any tech the player could ever research and does not have. (Claude code Opus 5.5) -->
	if gc.getTeam(player.getTeam()).isHasTech(iTech):
		raise ValueError("player %d already has %s" % (player.getID(), args["tech"]))
	if not player.canEverResearch(iTech):
		raise ValueError("player %d can never research %s" % (player.getID(), args["tech"]))
	# <!-- custom: pushResearch returns false when it could not queue the tech, and a clearing push may then leave the queue empty or partly filled (Codex's review); report it with the queue as it is. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if not player.pushResearch(iTech, not bool(args.get("append", False))):
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
	if not bQueued and not group.canStartMission(eMission, iData1, iData2, plot, False):
		raise ValueError("unit %d cannot start %s (%s, %s) now" % (unit.getID(), args["mission"], iData1, iData2))
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
CONTACT_PENDING_SECONDS = 10


def _pendingContact():
	pending = _state.get("contactPending")
	if pending is not None and time.time() - pending[2] > CONTACT_PENDING_SECONDS:
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
	# <!-- custom: Which conversation this is, counted as each begins (see CvDiplomacy.SASPilotScreen), so a client sequence such as pilot.py's 'price' can stop when another leader's screen takes over (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
		_state["contactPending"] = (iOther, False, time.time())
		return {"contacted": iOther}
	# <!-- custom: With give= or take=, the screen opens on its trade table with those items on it, as Ctrl+clicking the leader and clicking the items does, so the screen's own replies answer the deal: Propose, and "What would you want?" with the AI's counter-offer, which 'propose' skips (2026-11-13). (Claude code Opus 5.5) -->
	szWeGive = ",".join([_tradeArg(item, player) for item in give])
	szTheyGive = ",".join([_tradeArg(item, gc.getPlayer(iOther)) for item in take])
	if not _pilotGame("tableSASPilotDeal").tableSASPilotDeal(player.getID(), iOther, szWeGive, szTheyGive):
		raise ValueError("not a deal player %d can put on the table with player %d: check the items against 'trade'" % (player.getID(), iOther))
	_state["contactPending"] = (iOther, True, time.time())
	return {"contacted": iOther, "table": True}


_HELP["reply"] = "Answer the diplomacy screen with one of the replies 'diplo' lists, as clicking it does; returns the screen after, which may show a new AI line and replies or be closed. screen is the number 'diplo' gave: a reply to a screen that has changed since is refused. args: n, screen."


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


_HELP["techs"] = "The tech market across the players met: each tech the player lacks that some of them have, with its research cost, whether the XML lets it be traded at all (bTrade; SAS turns that off for some techs), and per holder whether it can be traded now and the AI's answer (DENIAL_ type, or null when it would trade). Then per player met, the techs the player could give them. A holder at war ('atWar') can still answer for a tech put in the same deal as a peace treaty, as the diplomacy screen allows. args: player."


def cmd_techs(args):
	# <!-- custom: Buying techs well needs the whole market: who has what, which techs the XML forbids trading (32 in SAS by bTrade, such as Bronze Working, Iron Working, Engineering, Gunpowder and Code of Laws), and which holder would trade. 'trade' answered one leader at a time; the user asked for a view to get the best deals (2026-11-13). (Claude code Opus 5.5) -->
	player = _player(args)
	team = gc.getTeam(player.getTeam())
	# <!-- custom: Under fog, as the Foreign Advisor's tech tab shows it (CvForeignAdvisor.py): a met player's techs only when canSeeTech allows, and a tech they hold but cannot trade only when we could research it. The first version listed every met player's techs, which Codex's review found reveals more than the window (2026-11-13). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iFogTeam = _fogTeam(args)
	if iFogTeam >= 0 and player.getTeam() != iFogTeam:
		raise ValueError("with fog on, 'techs' is only for the viewing team")
	others = [gc.getPlayer(i) for i in range(gc.getMAX_CIV_PLAYERS()) if i != player.getID() and gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isBarbarian() and not gc.getPlayer(i).isMinorCiv() and team.isHasMet(gc.getPlayer(i).getTeam())]
	if iFogTeam >= 0:
		others = [other for other in others if player.canSeeTech(other.getID())]
	wanted = []
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
	return {"wanted": wanted, "weCouldGive": [{"player": other.getID(), "name": other.getName(), "techs": offers[other.getID()]} for other in others]}


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


def cmd_propose(args):
	# <!-- custom: The second half of trading after 'trade' (fog-on playthrough, 2026-11-13); asking the AI and making the deal need the DLL, see proposeSASPilotDeal in CvGameInterface.cpp. (Claude code Opus 5.5) -->
	player = _player(args)
	other = gc.getPlayer(_otherAiId(player, args["with"]))
	szWeGive = ",".join([_tradeArg(item, player) for item in args.get("give", [])])
	szTheyGive = ",".join([_tradeArg(item, other) for item in args.get("take", [])])
	text = _pilotGame("proposeSASPilotDeal").proposeSASPilotDeal(player.getID(), other.getID(), szWeGive, szTheyGive)
	if text == "null":
		raise ValueError("not a deal player %d can propose to player %d: check the items against 'trade'" % (player.getID(), other.getID()))
	return fromJson(text)


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


_HELP["builds"] = "What a unit could build on a plot, as the window's buttons offer once the unit stands there: each build with its turns for this unit once it stands there, the improvement or route it makes, and the improvement's yield change on that plot. args: unit, x, y (default the unit's plot), player."


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
		result.append(entry)
	return result


_HELP["move"] = "Move a unit to a plot (MISSION_MOVE_TO); continues over later turns. args: unit, x, y, player."


def cmd_move(args):
	unit = _unit(args)
	plot = _plot(args)
	# <!-- custom: Checked with Python's CyUnit.generatePath first. At turn 81 of the fog-on playthrough (2026-11-13), right after Open Borders with Ethiopia were signed, 'path' found a 7-turn route for a Warrior inside Ethiopia's borders while 'move' said it had no path; the same pathfinder as 'path', GroupPathFinder, now decides both, so they cannot disagree. (Claude code Opus 5.5) -->
	if not fromJson(_pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), 0)).get("found"):
		raise ValueError("unit %d has no path to %d,%d" % (unit.getID(), plot.getX(), plot.getY()))
	if _state.get("follow"):
		_lookAt(plot)
	return cmd_mission({"unit": args["unit"], "player": args.get("player"), "mission": "MISSION_MOVE_TO", "data1": plot.getX(), "data2": plot.getY()})


_HELP["look"] = "Turn the window's camera to a plot, a unit or a city, as clicking the minimap does, so a person watching sees what the pilot acts on. With follow=1, each 'move' (attacks included) looks at its destination first; follow=0 stops that. zoom sets the camera's distance (the EXE's scale; the window starts near 1). args: x, y, unit, city, follow, zoom, player."


def _lookAt(plot):
	CyCamera().JustLookAtPlot(plot)


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
	result = {"follow": bool(_state.get("follow", False))}
	if plot is not None:
		result["x"] = plot.getX()
		result["y"] = plot.getY()
	return result


_HELP["command"] = "Give a unit a command, e.g. COMMAND_PROMOTION data1=PROMOTION_ type, COMMAND_DELETE, COMMAND_AUTOMATE data1=AUTOMATE_EXPLORE ('unit' lists the automations it can take). args: unit, command, data1, data2, player."


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
	if not unit.canDoCommand(eCommand, iData1, iData2, False):
		raise ValueError("unit %d cannot do %s (%s, %s) now" % (unit.getID(), args["command"], iData1, iData2))
	unit.doCommand(eCommand, iData1, iData2)
	if unit.isNone() or unit.isDead():
		return {"unitGone": True}
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


_HELP["hurry"] = "Hurry a city's production. Without hurry, lists each HURRY_ type with whether the city can use it now and its gold and population cost, as the window's buttons show. args: city, hurry (HURRY_ type), player."


def cmd_hurry(args):
	city = _city(args)
	# <!-- custom: 'hurry city=Gondar' without a type raised a bare KeyError while looking for a way to rush a Trireme (2026-11-13, turn 154); like 'freetech' and 'research', it now lists the choices instead. (Claude code Opus 5.5) -->
	if args.get("hurry") is None:
		return {"city": city.getName(), "gold": gc.getPlayer(city.getOwner()).getGold(), "hurries": [{"hurry": gc.getHurryInfo(i).getType(), "can": bool(city.canHurry(i, False)), "goldCost": city.hurryGold(i), "populationCost": city.hurryPopulation(i)} for i in range(gc.getNumHurryInfos())]}
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


_HELP["turn"] = "What a person sees at the start of a turn: turn and year, what waits for orders (as 'todo') and the messages since the previous turn (as 'messages'). 'pilot.py endturn' prints it for the new turn. args: player."


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


_HELP["save"] ="Save the game; through pilot.py a bare name goes to Saves/single with the .CivBeyondSwordSave extension, else a full path. An existing file is refused unless overwrite=true. args: path, overwrite."


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


def cmd_screen(args):
	function = getattr(CvScreensInterface, args["name"])
	if "args" in args:
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


_HELP["batch"] = "Run several commands in one request, in order, stopping at the first failure. args: commands (list of {cmd, args}). From the CLI: pilot.py batch 'commands=[{\"cmd\":\"units\"},{\"cmd\":\"cities\"}]'."


def cmd_batch(args):
	# <!-- custom: A request waited for the next game update, about 250 ms each when measured (2026-11-13), so a turn's worth of orders was far quicker as one request; served every frame it is now about 2 ms, which still makes one request cheaper. (Claude code Fable 5.2 + Opus 5.5) -->
	results = []
	for item in args["commands"]:
		try:
			handler = _checkedHandler(item["cmd"], item.get("args") or {})
		except ValueError, error:
			raise ValueError("%s, after %d done" % (error, len(results)))
		results.append(handler(item.get("args") or {}))
	return results


_HELP["profile"] = "Run a command and time its parts: reading the game (gatherMs) and writing the JSON (encodeMs), each the best of 'repeat' runs. args: cmd, args (dict, optional), repeat (default 3)."


def cmd_profile(args):
	# <!-- custom: Found 441 plots spending 3 ms reading the game and 28 ms writing JSON (2026-11-13), which pointed at the writer rather than the game or Python as a whole; kept as a command so the next slow command is split the same way. (Claude code Opus 5.5) -->
	commandArgs = args.get("args") or {}
	handler = _checkedHandler(args["cmd"], commandArgs)
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
