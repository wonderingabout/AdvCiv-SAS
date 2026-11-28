# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotUnits: commanding units as a player does: reading them ('units', 'unit'), where they can go and what they can hit ('path', 'targets', 'odds'), moving them ('move', 'step', 'mission', 'group') and a Worker's builds ('builds', 'buildsteps', 'workers').
# Split from SASPilotCommands.py on 2026-11-28, the fourth part moved out by topic, as Codex (GPT-6.2-Sol) proposed after the cities; the rules every command shares stay there, the fog's _requireSeen and the role's _adviceAllowed included although only these commands call them, as are the selection and camera helpers other orders use, and are reached as saspilot.
# SASPilotCommands.py loads it from beside itself, again whenever it changes, and adds its commands and help. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from CvPythonExtensions import *
# <!-- custom: SASCurrentDefines reads CAN_CHOP_UNOWNED_FEATURES for a Worker's builds; getInfoTypeOrFail finds UNITCLASS_WORKER, as in SASPilotCommands. (Claude code Opus 5.5) -->
import SASCurrentDefines
from SASUtils import getInfoTypeOrFail

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}


def _unitActions(unit):
	# <!-- custom: What the unit's buttons would offer on its own plot: missions and commands with bTestVisible off, plus builds, promotions and upgrades.
	# Target missions such as MISSION_MOVE_TO are listed when startable at all; the target is checked when the order is given. (Claude code Fable 5.2) -->
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
	# <!-- custom: COMMAND_AUTOMATE was missing from 'commands', as it is tested with data1 -1 there, so the Explore button a person clicks for a scout had no listed equivalent (fog-on playthrough, 2026-11-13).
	# List each automation the unit's buttons would offer. (Claude code Opus 5.5) -->
	# <!-- custom: Missions that take a type as data were tested with -1 only, so a Great Scientist born at turn 105 of the fog-on playthrough (2026-11-13) listed no "Join City" or "Build Academy".
	# Test each specialist and building as the unit's buttons do and list them as MISSION:TYPE. (Claude code Opus 5.5) -->
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


_HELP["units"] = "A player's units, briefly, or every living player's with player=all. Each has its state, as its hover help shows it (for every unit in the full view, for our own under fog): activity, automate, head mission and its target plot (missionPlot; a unit target only while in sight), fortifyTurns and promotionReady. args: player."


def cmd_units(args):
	# <!-- custom: Written in C++ by CyGame.getSASPilotUnitsJson: on a Huge map at turn 300, Python took 8 ms for the 876 units of all players, 6 of them writing JSON (2026-11-13). (Claude code Opus 5.5) -->
	# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
	if args.get("player") == "all":
		iPlayer = -1
	else:
		iPlayer = saspilot._playerId(args)
	text = saspilot._pilotGame("getSASPilotPathJson").getSASPilotUnitsJson(iPlayer, saspilot._fogTeam(args))
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("no player %d" % iPlayer)
	return saspilot.RawJson(text)


_HELP["unit"] = "One unit in full, with the orders it can take now. A wounded unit of ours also gets heal: healing where it stands against walking first to the best plot inside our borders (friendly) or to our best city within 4 plots, each with travel, heal and total turns, defense, whether it is inside our borders (animals cannot enter) and the hostiles in sight within 2 plots. args: unit (ID), player."


def cmd_unit(args):
	unit = saspilot._unit(args)
	if saspilot._requireSeen(args, unit.getOwner(), unit.plot(), "unit %d" % unit.getID()):
		# <!-- custom: 'units' left out invisible units such as spies and submarines, but 'unit' by ID still gave them, and a rival unit's orders and mission queue with them (Codex's review). (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		if unit.isInvisible(saspilot._fogTeam(args), False):
			raise ValueError("unit %d is not in sight; fog is on" % unit.getID())
		result = saspilot._unitBrief(unit, saspilot._fogTeam(args))
		result["strength"] = unit.baseCombatStr()
		result["promotions"] = [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if unit.isHasPromotion(i)]
		return result
	result = saspilot._unitFull(unit, saspilot._fogTeam(args))
	result["actions"] = _unitActions(unit)
	heal = _healOptions(unit)
	if heal is not None:
		result["heal"] = heal
	return result


# <!-- custom: A wounded unit's choices: heal where it stands, or walk to the best friendly plot or our nearest city first, each with travel and heal turns and the danger a player sees there.
# At turn 22 of the Continents replay (2026-11-19) a Warrior at 25 HP walked 3 turns home to heal at 15 a turn, the same 8 turns as resting where it stood at 10, and lost those turns of scouting; the user asked for the calculation, and that danger counts too. (Claude code Opus 5.5) -->
HEAL_SEARCH_RADIUS = 4


def _healOptions(unit):
	if not unit.isHurt() or not hasattr(unit, "healTurnsAt"):
		return None
	iTeam = unit.getTeam()
	team = gc.getTeam(iTeam)
	here = unit.plot()

	def option(plot, iTravel):
		iHeal = unit.healTurnsAt(plot.getX(), plot.getY())
		hostiles = []
		for dx in range(-2, 3):
			for dy in range(-2, 3):
				near = CyMap().plot(plot.getX() + dx, plot.getY() + dy)
				if near.isNone() or not near.isVisible(iTeam, False):
					continue
				for i in range(near.getNumUnits()):
					other = near.getUnit(i)
					if other.getTeam() != iTeam and (gc.getPlayer(other.getOwner()).isBarbarian() or team.isAtWar(other.getTeam())) and not other.isInvisible(iTeam, False):
						hostiles.append({"type": gc.getUnitInfo(other.getUnitType()).getType(), "x": near.getX(), "y": near.getY()})
		bHeals = iHeal >= 0 and iHeal < MAX_HEAL_TURNS
		return {"x": plot.getX(), "y": plot.getY(), "travelTurns": iTravel, "healTurns": bHeals and iHeal or None, "totalTurns": bHeals and iTravel + iHeal or None, "defensePct": plot.defenseModifier(iTeam, False, False), "insideOurBorders": plot.getTeam() == iTeam, "hostilesWithin2": hostiles}

	def travel(plot):
		path = saspilot.fromJson(saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), 0))
		if path is None or not path.get("found"):
			return None
		return path["turns"]

	result = {"damage": unit.getDamage(), "here": option(here, 0)}
	best = {}
	for dx in range(-HEAL_SEARCH_RADIUS, HEAL_SEARCH_RADIUS + 1):
		for dy in range(-HEAL_SEARCH_RADIUS, HEAL_SEARCH_RADIUS + 1):
			plot = CyMap().plot(here.getX() + dx, here.getY() + dy)
			if plot.isNone() or (dx == 0 and dy == 0) or plot.getTeam() != iTeam or not plot.isRevealed(iTeam, False):
				continue
			kind = plot.isCity() and "city" or "friendly"
			iTravel = travel(plot)
			if iTravel is None:
				continue
			entry = option(plot, iTravel)
			if entry["totalTurns"] is not None and (kind not in best or entry["totalTurns"] < best[kind]["totalTurns"]):
				best[kind] = entry
	result.update(best)
	return result


# <!-- custom: CvUnit::healTurns returns MAX_INT when a plot does not heal the unit at all. (Claude code Opus 5.5) -->
MAX_HEAL_TURNS = 10000


_HELP["path"] = "The route a unit would take to a plot, before ordering it: each step's plot, the turn it is reached on (1 is this turn) and the moves left there, and the total turns. args: unit, x, y, flags (MovementFlags number, default 0), player."


def cmd_path(args):
	unit = saspilot._unit(args)
	plot = saspilot._plot(args)
	iFlags = int(args.get("flags", 0))
	iTeam = saspilot._fogTeam(args)
	# <!-- custom: With fog on, only the team's own units and the default movement flags, as some flags change what the search treats as known (Codex's review); with fog off any unit and flags, for debugging. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	if iTeam >= 0 and (gc.getPlayer(unit.getOwner()).getTeam() != iTeam or iFlags != 0):
		raise ValueError("with fog on, 'path' takes the team's own units and no flags")
	text = saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), iFlags)
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("no path query for unit %d to %d,%d" % (unit.getID(), plot.getX(), plot.getY()))
	# <!-- custom: A bare {"found": false} hid why: a goody-hut Catapult on Marsh found no path even to the next plot, because SAS makes Jungle, Forest and Marsh impassable to siege off roads (KI#1076; JOAO turn-112 save, 2026-11-22).
	# Name what blocks it, as the window shows the terrain. See KI#1076.2. (Claude code Opus 5.5) -->
	if text.replace(" ", "") == '{"found":false}':
		return _pathBlocked(unit, plot, iTeam)
	return saspilot.RawJson(text)


def _pathBlocked(unit, target, iTeam):
	info = gc.getUnitInfo(unit.getUnitType())
	impassable = [gc.getFeatureInfo(i).getType() for i in range(gc.getNumFeatureInfos()) if info.getFeatureImpassable(i)] + [gc.getTerrainInfo(i).getType() for i in range(gc.getNumTerrainInfos()) if info.getTerrainImpassable(i)]
	here = unit.plot()
	exits = []
	for iDir in range(DirectionTypes.NUM_DIRECTION_TYPES):
		adj = plotDirection(here.getX(), here.getY(), DirectionTypes(iDir))
		if adj is None or adj.isNone() or (iTeam >= 0 and not adj.isVisible(iTeam, False)):
			continue
		if unit.canMoveInto(adj, False, False, False):
			exits.append({"x": adj.getX(), "y": adj.getY()})
	result = {"found": False, "impassableFor": impassable, "enterableNext": exits, "routeLifts": info.getDomainType() == DomainTypes.DOMAIN_LAND}
	# <!-- custom: A failed path may be caused by another unit in the group.
	# Inspect only visible plots under fog, and describe the single-unit checks without attributing the whole path failure to them. (GPT-6.2-Sol) -->
	result["note"] = "no group path found; enterableNext only checks this unit"
	if iTeam >= 0:
		result["note"] += " and only lists adjacent plots in sight"
	if iTeam < 0 or target.isVisible(iTeam, False):
		pTeam = gc.getTeam(unit.getTeam())
		if not (result["routeLifts"] and target.isRoute()):
			iFeature = target.getFeatureType()
			if iFeature >= 0 and info.getFeatureImpassable(iFeature):
				iTech = info.getFeaturePassableTech(iFeature)
				if iTech < 0 or not pTeam.isHasTech(iTech):
					result["blockedFeature"] = gc.getFeatureInfo(iFeature).getType()
			iTerrain = target.getTerrainType()
			if info.getTerrainImpassable(iTerrain):
				iTech = info.getTerrainPassableTech(iTerrain)
				if iTech < 0 or not pTeam.isHasTech(iTech):
					result["blockedTerrain"] = gc.getTerrainInfo(iTerrain).getType()
	return result


_HELP["targets"] = "The plots a unit's group could pick for an interface mode from 'unit's targetModes, as the window highlights them, e.g. mode=INTERFACEMODE_RECON or INTERFACEMODE_AIRBOMB, with the mission to send: mission unit=<id> mission=<mission> data1=x data2=y. With fog on, only plots the team has revealed. args: unit, mode, player."


def cmd_targets(args):
	# <!-- custom: A scan of all 4368 plots of the turn-271 Large baseline took 2 to 4 ms in Python (2026-11-14), so this stays out of the DLL. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	if not hasattr(gc, "getInterfaceModeInfo"):
		raise ValueError("this DLL predates CyGlobalContext.getInterfaceModeInfo; build or install a current one")
	# <!-- custom: Without mode it raised a bare KeyError for the first Jet Fighter (turn 285, 2026-11-14); like 'hurry', list the choices instead, the unit's targetModes. (Claude code Opus 5.5) -->
	if args.get("mode") is None:
		group = unit.getGroup()
		return {"unit": unit.getID(), "targetModes": [{"mode": gc.getInterfaceModeInfo(i).getType(), "mission": gc.getMissionInfo(gc.getInterfaceModeInfo(i).getMissionType()).getType()} for i in range(int(InterfaceModeTypes.NUM_INTERFACEMODE_TYPES)) if gc.getInterfaceModeInfo(i).getMissionType() >= 0 and group.canDoInterfaceMode(InterfaceModeTypes(i))]}
	eMode =InterfaceModeTypes(int(saspilot._enum(InterfaceModeTypes, args["mode"])))
	info = gc.getInterfaceModeInfo(int(eMode))
	if info.getMissionType() < 0:
		raise ValueError("%s picks no plot for a mission" % args["mode"])
	group = unit.getGroup()
	# <!-- custom: canDoInterfaceModeAt does not recheck that the mode applies: for the SAS Airship, a land unit, INTERFACEMODE_REBASE accepted 4191 plots (2026-11-14).
	# Check the mode first, as the window's button does. (Claude code Opus 5.5) -->
	if not group.canDoInterfaceMode(eMode):
		# <!-- custom: Name the checks a player can see: two Paratroopers that had moved with their stack got only "cannot use INTERFACEMODE_PARADROP now" (turn 304 of the ASOKA Huge save, 2026-11-22); CvUnit::canParadrop needs an unmoved unit on a city or airbase the team knows. (Claude code Opus 5.5) -->
		hints = []
		if unit.hasMoved():
			hints.append("it has moved this turn")
		if eMode == InterfaceModeTypes.INTERFACEMODE_PARADROP and not unit.plot().isCity():
			hints.append("a drop starts from one of our cities or an airbase")
		raise ValueError("unit %d cannot use %s now%s" % (unit.getID(), args["mode"], hints and " (" + "; ".join(hints) + ")" or ""))
	iTeam = saspilot._fogTeam(args)
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


FOUND_GUARD_RADIUS = 3


def _unmovedOthers(unit):
	# <!-- custom: Our units other than this one that still have all their moves and wait for orders: not fortified, asleep, automated or on a mission, nor inside the same group.
	# Only within FOUND_GUARD_RADIUS plots of the Settler: the first version also named a Worker and an Archer 6 plots away in Dublin, which could reveal nothing about the site (Continents replay, turn 53). (Claude code Opus 5.5) -->
	player = gc.getPlayer(unit.getOwner())
	waiting = []
	(loopUnit, iter) = player.firstUnit(False)
	while loopUnit:
		if loopUnit.getID() != unit.getID() and max(abs(loopUnit.getX() - unit.getX()), abs(loopUnit.getY() - unit.getY())) <= FOUND_GUARD_RADIUS and loopUnit.getGroupID() != unit.getGroupID() and loopUnit.canMove() and loopUnit.getMoves() == 0 and loopUnit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_AWAKE and not loopUnit.isAutomated() and loopUnit.getGroup().getLengthMissionQueue() == 0:
			waiting.append(loopUnit)
		(loopUnit, iter) = player.nextUnit(iter, False)
	return waiting


_HELP["mission"] = "Give a unit's group a mission, e.g. mission=MISSION_MOVE_TO data1=x data2=y, MISSION_FORTIFY, MISSION_BUILD data1=BUILD_ type. Under fog, MISSION_MOVE_TO_UNIT (data1=owner, data2=unit) follows only our own team's units. MISSION_FOUND refuses while another of our units still has all its moves and waits for orders, as what it reveals can change the site; anyway=1 founds regardless. args: unit, mission, data1, data2, flags, append, anyway, player."


def cmd_mission(args):
	unit = saspilot._unit(args)
	group = unit.getGroup()
	eMission = saspilot._enum(MissionTypes, args["mission"])
	iData1 = args.get("data1", -1)
	if isinstance(iData1, (str, unicode)) and eMission == MissionTypes.MISSION_BUILD:
		iData1 = saspilot._typedIndex(iData1, "BUILD_", gc.getNumBuildInfos(), gc.getBuildInfo)
	elif isinstance(iData1, (str, unicode)):
		iData1 = saspilot._infoIndex(iData1)
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
	# <!-- custom: Founding waits until our other units have moved, the user's rule from the turn-0 games (2026-11-14), as what they reveal can change the site; the scoutBeforeFounding reminder alone did not stop it, and turn 0 of the Ireland replay (2026-11-19) founded Dublin before its Warrior moved. anyway=1 founds regardless. (Claude code Opus 5.5) -->
	if eMission == MissionTypes.MISSION_FOUND and not args.get("anyway"):
		waiting = _unmovedOthers(unit)
		if waiting:
			raise ValueError("move our other units first, as they may reveal a better site: %s; or pass anyway=1" % ", ".join(["%s %d at %d,%d" % (gc.getUnitInfo(other.getUnitType()).getType(), other.getID(), other.getX(), other.getY()) for other in waiting]))
	# <!-- custom: Under fog, a Move To Unit only toward a unit of our own team: the game takes any owner and unit ID, so the order would follow a rival out of sight.
	# A first version accepted a rival in sight, but the queued mission keeps steering toward the target's live position on later turns, so our unit's moves would still track it through fog (Codex's reviews of the unit state, 2026-11-15). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	iFogTeam = saspilot._fogTeam(args)
	if iFogTeam >= 0 and eMission == MissionTypes.MISSION_MOVE_TO_UNIT:
		target = None
		if iData1 >= 0 and iData1 < gc.getMAX_PLAYERS():
			target = gc.getPlayer(iData1).getUnit(iData2)
		if target is None or target.isNone() or target.getTeam() != iFogTeam:
			raise ValueError("under fog, MISSION_MOVE_TO_UNIT follows only our own team's units; for a rival, move to the plot where it is seen")
	# <!-- custom: Nor a new order for a unit with no moves left, which the window takes and starts next turn: at turn 118 of the turn-0 game (2026-11-14) a Worker busy clearing jungle was given a replacement queue, which this check refused as "moves left 0", so its old Mine order stayed.
	# The game checks the order when it starts, as for a queued one. (Claude code Opus 5.5) -->
	if not bQueued and unit.movesLeft() > 0 and not group.canStartMission(eMission, iData1, iData2, plot, False):
		# <!-- custom: Two Field Guns refused a move to Ecbatana on turn 285 (2026-11-14) with no reason given: they were in a 9-unit group that a move of one of its units had already sent there.
		# Say the moves left and the group, so such a refusal explains itself. (Claude code Opus 5.5) -->
		szWhy = "moves left %d, group %d of %d unit(s)" % (unit.movesLeft(), group.getID(), group.getNumUnits())
		if group.getLengthMissionQueue() > 0:
			szWhy += ", whose current mission is %s" % gc.getMissionInfo(group.getMissionType(0)).getType()
		# <!-- custom: A Catapult's MISSION_FORTIFY was refused with only its moves and group, as siege cannot fortify (JOAO turn-114 save, 2026-11-22); list the plain missions it can start here, as the window shows only those buttons. (Claude code Opus 5.5) -->
		canStart = [gc.getMissionInfo(i).getType() for i in range(gc.getNumMissionInfos()) if i != MissionTypes.MISSION_BUILD and group.canStartMission(i, -1, -1, plot, False)]
		if canStart:
			szWhy += "; without data it can start: %s" % ", ".join(canStart)
		raise ValueError("unit %d cannot start %s (%s, %s) now (%s)" % (unit.getID(), args["mission"], iData1, iData2, szWhy))
	# <!-- custom: No mission AI plot or unit, as the window's own orders give none (CvNetPushMission).
	# SASPilot first passed the plot above, which pushMission records as the group's mission AI plot while the group can move: a Work Boat sent by 'move' from (39,32) then had fishing boats appended after arriving with no moves left, and at the next turn the KI#176 stale-target guard in continueMission cancelled the build, as the boat was not at (39,32) (fog-on playthrough, turns 116-118, 2026-11-13). See KI#176.
	# CySelectionGroup.pushMission dereferenced None until that same day's DLL, hence the binding check. (Claude code Opus 5.5) -->
	saspilot._pilotGame("isSASPilotChoosingFreeTech")
	iUnit = unit.getID()
	iOwner = unit.getOwner()
	group.pushMission(eMission, iData1, iData2, int(args.get("flags", 0)), bool(args.get("append", False)), True, MissionAITypes.NO_MISSIONAI, None, None)
	# <!-- custom: Looked up again by ID: a Work Boat building fishing boats is used up at once, and reading the old object then raised an unidentifiable C++ exception instead of reporting it gone (turn 118, 2026-11-13). (Claude code Opus 5.5) -->
	unit = gc.getPlayer(iOwner).getUnit(iUnit)
	if unit is None or unit.isNone() or unit.isDead():
		return {"unitGone": True}
	return saspilot._unitFull(unit)


_HELP["buildsteps"] = "A Worker's plan over several plots in one order, as shift-clicks queue it in the window: steps=BUILD_ROAD@99,26;BUILD_FARM@100,27 moves to each plot and builds there, in order, each through the checks 'mission' makes. It replaces the unit's queue unless append=1. Returns the queue. args: unit, steps, append, player."


def cmd_buildsteps(args):
	# <!-- custom: At turn 66 of the islands replay (2026-11-15) roads to the Sheep and the Cattle took eight 'mission' calls from a shell loop (move, build, move, build); any Worker plan over several plots asks the same. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	steps = []
	for szStep in str(args["steps"]).split(";"):
		szStep = szStep.strip()
		if not szStep:
			continue
		if szStep.count("@") != 1:
			raise ValueError("step %s is not BUILD_TYPE@x,y" % szStep)
		(szBuild, szPlot) = szStep.split("@")
		(szX, szY) = szPlot.split(",")
		steps.append((szBuild.strip(), int(szX), int(szY)))
	if not steps:
		raise ValueError("no steps; give steps=BUILD_TYPE@x,y;BUILD_TYPE@x,y")
	bAppend = bool(args.get("append"))
	for (szBuild, x, y) in steps:
		base = {"unit": unit.getID(), "player": unit.getOwner()}
		move = dict(base)
		move.update({"mission": "MISSION_MOVE_TO", "data1": x, "data2": y, "append": bAppend})
		if (unit.getX(), unit.getY()) != (x, y) or bAppend:
			cmd_mission(move)
			bAppend = True
		build = dict(base)
		build.update({"mission": "MISSION_BUILD", "data1": szBuild, "append": bAppend})
		cmd_mission(build)
		bAppend = True
	return {"unit": unit.getID(), "missions": saspilot._missionQueue(unit.getGroup())}


_QUEUE_PLAIN_MISSIONS = ("MISSION_SKIP", "MISSION_SLEEP", "MISSION_FORTIFY", "MISSION_HEAL", "MISSION_SENTRY", "MISSION_SENTRY_HEAL", "MISSION_FOUND", "MISSION_PILLAGE", "MISSION_PLUNDER")


def _checkMissionData(eMission, iData1, iData2, bQueued):
	# <!-- custom: A queued mission skips canStartMission, so its data reach CvSelectionGroup::startMission unchecked later: a MISSION_MOVE_TO off the map would have the game dereference a missing plot (Codex's review).
	# Check what does not depend on where the group will be: a plot on the map for a move or route, a BUILD_ index for a build, no data for the plain missions; refuse other missions in a queue, as their data mean different things. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
		raise ValueError("%s cannot be queued behind other missions by SASPilot; give it when the queue is empty" % szMission)


_HELP["group"] = "Group units on one plot as selecting them together does, so they move and take missions as one: with=<unit> joins 'unit' to that unit's group; without it, 'unit' leaves its group. Then order the group through any of its units. args: unit, with, player."


def cmd_group(args):
	# <!-- custom: At turn 91 of the fog-on playthrough (2026-11-13) a Settler had to go where Barbarian Archers had pillaged, and SASPilot could not escort it: Python has no joinGroup.
	# See joinSASPilotGroup in CvGameInterface.cpp. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	iHead = -1
	if args.get("with") is not None:
		iHead = saspilot._unit({"unit": args["with"], "player": args.get("player")}).getID()
	text = saspilot._pilotGame("joinSASPilotGroup").joinSASPilotGroup(unit.getOwner(), unit.getID(), iHead)
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("unit %d cannot join unit %s's group: both must be the player's, on one plot and of one domain" % (unit.getID(), args.get("with")))
	group = unit.getGroup()
	return {"group": unit.getGroupID(), "units": [saspilot._unitBrief(group.getUnitAt(i)) for i in range(group.getNumUnits())]}


_HELP["odds"] = "The odds the window shows when a unit is pointed at a plot to attack: the defender the game would pick, both strengths, and the chance to win in per mille. With stack=1, every unit of ours on the unit's plot that could attack, best odds first, each with the defender it would meet, its group's size and the path's turns (attacksThisTurn when the attack comes this turn; a unit in a group moves the whole group), as hovering a stack over a target shows the attacker the game would send. args: unit, x, y, stack, player."


def cmd_odds(args):
	# <!-- custom: stack=1 ranks every unit on the attacker's plot: at turn 302 of the ASOKA Huge save (2026-11-22) choosing among 26 units in Babylon against Dur-Kurigalzu took one 'odds' call per unit, while the window shows the best attacker on one hover. (Claude code Opus 5.5) -->
	if args.get("stack"):
		lead = saspilot._unit(args)
		target = saspilot._plot(args)
		iTeam = saspilot._fogTeam(args)
		saspilot._requireOwnTeamUnderFog(args, gc.getPlayer(lead.getOwner()), "stack odds")
		if iTeam >= 0 and not target.isVisible(iTeam, False):
			raise ValueError("plot %d,%d is not in sight; fog is on" % (target.getX(), target.getY()))
		rows = []
		paths = {}
		plot = lead.plot()
		for i in range(plot.getNumUnits()):
			other = plot.getUnit(i)
			if other.getOwner() != lead.getOwner() or not other.canAttack() or other.isCargo():
				continue
			one = dict(args)
			del one["stack"]
			one["unit"] = other.getID()
			try:
				reply = cmd_odds(one)
			except ValueError, error:
				rows.append({"unit": other.getID(), "type": gc.getUnitInfo(other.getUnitType()).getType(), "refused": str(error)})
				continue
			# <!-- custom: Each row also gives the unit's group size and the path's turns to the target: the first version showed a Modern Tank at 1000 per mille, but it led a 28-unit group 4 turns away, so 'move' on it marched the whole Babylon stack out of the city (2026-11-22).
			# The window's hover shows the path's turns. (Claude code Opus 5.5) -->
			group = other.getGroup()
			iGroup = group.getID()
			if iGroup not in paths:
				path = saspilot.fromJson(saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(other.getOwner(), other.getID(), target.getX(), target.getY(), 0))
				paths[iGroup] = path and path.get("found") and path.get("turns") or None
			iTurns = paths[iGroup]
			# <!-- custom: Group ETA is shared.
			# This unit must still have moves and be eligible to attack, even if other members can reach and attack this turn. (GPT-6.2-Sol) -->
			bReady = other.canMove() and (not other.isMadeAttack() or other.isBlitz())
			bAttacksThisTurn = iTurns == 1 and bReady and other.canMoveInto(target, True, False, False)
			rows.append({"unit": other.getID(), "type": gc.getUnitInfo(other.getUnitType()).getType(), "damage": other.getDamage(), "movesLeft": other.movesLeft(), "oddsPerMille": reply["oddsPerMille"], "defender": reply["defender"]["type"], "defenderStrength": reply["defenderStrength"], "groupSize": group.getNumUnits(), "pathTurns": iTurns, "attacksThisTurn": bAttacksThisTurn})
		rows.sort(lambda a, b: cmp(b.get("oddsPerMille", -1), a.get("oddsPerMille", -1)))
		return {"x": int(args["x"]), "y": int(args["y"]), "attackers": rows}
	# <!-- custom: A person sees the combat odds on hovering an enemy before attacking; SASPilot had moves and paths but no odds (fog-on playthrough, 2026-11-13).
	# The defender is the one the game would pick against this attacker, as getBestDefender does for the hover text; with fog on, only a plot in sight. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	plot = saspilot._plot(args)
	iTeam = saspilot._fogTeam(args)
	if iTeam >= 0 and not plot.isVisible(iTeam, False):
		raise ValueError("plot %d,%d is not in sight; fog is on" % (plot.getX(), plot.getY()))
	# <!-- custom: The game picks the defender with the attacker's own sight, so with player= naming another team's unit, a defender the viewing team cannot see could be named under fog (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if iTeam >= 0 and unit.getTeam() != iTeam:
		raise ValueError("with fog on, odds are only given for the viewing team's own units")
	# <!-- custom: CyPlot.getBestDefender names its last argument bTestCanMove, but passes it to CvPlot::getBestDefender's bTestVisible; with False an invisible defender on a visible plot could be named under fog (Codex's review).
	# Pass whether fog is on. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	defender = plot.getBestDefender(PlayerTypes.NO_PLAYER, unit.getOwner(), unit, True, False, iTeam >= 0)
	if defender is None or defender.isNone():
		# <!-- custom: At turn 155 two withdrawn Catapults left two Aztec Trebuchets at 75 damage, the Catapult's combat limit, and the other Catapults got only "no unit at 29,28 that it could attack" although both stood there; Longbowmen then finished them (2026-11-13).
		# The refusal now names the limit when it is the reason. (Claude code Opus 5.5) -->
		# <!-- custom: Only units the player can see, and none aboard a ship: Codex's review mocked an invisible enemy at 75 damage on a visible plot, and the first version named the limit, revealing it.
		# Phrased as possible, as the game's own test also covers hidden nationality and the air combat limit. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
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
	result = {"defender": saspilot._unitBrief(defender, iTeam), "defenderStrength": defender.currCombatStrFloat(plot, unit), "oddsPerMille": getCombatOdds(unit, defender)}
	# <!-- custom: The attacker's own strength is currCombatStr(NULL, NULL) in C++, but CyUnit's wrapper dereferenced both pointers, so unit.currCombatStrFloat(None, None) raised "unidentifiable C++ exception" (2026-11-13); the wrapper now passes NULL through, and a DLL without that fix leaves the field out. (Claude code Opus 5.5) -->
	try:
		result["attackerStrength"] = unit.currCombatStrFloat(None, None)
	except RuntimeError:
		pass
	return result


_HELP["builds"] = "What a unit could build on a plot, as the window's buttons offer once the unit stands there: each build with its turns for this unit once it stands there, the improvement or route it makes, and the improvement's yield change on that plot. With refused=1, also each build this unit type can make that the plot refuses, with the reason. args: unit, x, y (default the unit's plot), refused, player."


def cmd_builds(args):
	# <!-- custom: 'unit' lists builds for the unit's own plot only, so choosing where to send a new Worker in the fog-on playthrough (2026-11-13) meant moving it first or a 'py' call per plot; a person sees a tile's options before sending it. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	if args.get("x") is None:
		plot = unit.plot()
	else:
		plot = saspilot._plot(args)
	iTeam = saspilot._fogTeam(args)
	if iTeam >= 0 and not plot.isRevealed(iTeam, False):
		raise ValueError("plot %d,%d is not revealed; fog is on" % (plot.getX(), plot.getY()))
	result = []
	for i in range(gc.getNumBuildInfos()):
		if not unit.canBuild(plot, i, False):
			continue
		info = gc.getBuildInfo(i)
		entry = {"build": info.getType(), "turns": plot.getBuildTurnsLeft(i, unit.getOwner(), unit.workRate(True), unit.workRate(True)), "improvement": saspilot._typeOrNone(gc.getImprovementInfo, info.getImprovement()), "route": saspilot._typeOrNone(gc.getRouteInfo, info.getRoute())}
		if info.getImprovement() >= 0:
			entry["yieldChange"] = [plot.calculateImprovementYieldChange(info.getImprovement(), YieldTypes(j), unit.getOwner(), False) for j in range(YieldTypes.NUM_YIELD_TYPES)]
		# <!-- custom: The hammers a build that clears the plot's feature gives the city, as the window's build hover says: in the scouting trial (2026-11-14) the user and the agent weighed chopping forests into a Settler, and only the XML (30 per forest, with Masonry in SAS) and the DLL (chop hammers take the city's production multipliers, so a settler bonus would double them; Justinian has none in SAS) answered it.
		# CyPlot.getFeatureProduction fills a city pointer it does not return, so the receiving city is not named here; the amount already counts distance and the team's techs. (Claude code Opus 5.5) -->
		if plot.getFeatureType() >= 0 and info.isFeatureRemove(plot.getFeatureType()):
			entry["featureProduction"] = plot.getFeatureProduction(i, unit.getTeam(), CyCity())
			# <!-- custom: The hammers go to whatever that city builds when the chop ends: at turn 32 of the 2026-11-19 validation run a chop meant for the Settler fed a filler Work Boat.
			# The city working the plot is named as the likely receiver. (Claude code Opus 5.5) -->
			city = plot.getWorkingCity()
			if city is not None and not city.isNone() and city.getOrderQueueLength() > 0:
				entry["featureProductionTo"] = {"city": city.getName(), "buildingNow": str(saspilot._orderData(city.getOrderFromQueue(0))), "note": "hammers go to the city's build when the chop ends: have the intended build first by then"}
		result.append(entry)
	if not args.get("refused"):
		return result
	# <!-- custom: Why a Worker cannot build somewhere, which twice took 'py' snippets in the turn-0 game (2026-11-14): a road at 26,28 was refused because in SAS a road drains Marsh, a feature removal that AdvCiv allows on unclaimed land only with CAN_CHOP_UNOWNED_FEATURES (advc.119).
	# The user asked that such a question become reusable.
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
		# <!-- custom: In CvPlayer::canBuild's order, from the game's own checks where Python has them: the plot's (CyPlot.canBuild), then the build's tech, the feature's tech and the gold.
		# The first version asked the tech before the plot and the XML gold cost, which ignored inflation and that a build already begun costs nothing more (CvPlayer::getBuildCost), so a resumed build could read as too dear (Codex's review, round 32).
		# calculateInflationRate and getBuildProgress were exposed all along. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if not plot.canBuild(i, unit.getOwner(), False):
			# <!-- custom: The plot's reasons, as the plot check gives no reason of its own; CvPlot::canBuild asks canHaveImprovement before the feature, so a Mine on flat Marsh is refused for the terrain, not for draining the Marsh. (Claude code Opus 5.5) -->
			if info.getImprovement() >= 0 and not plot.canHaveImprovement(info.getImprovement(), unit.getTeam(), True):
				reason = "%s cannot be on this plot (terrain, feature or another rule)" % gc.getImprovementInfo(info.getImprovement()).getType()
			elif iFeature >= 0 and info.isFeatureRemove(iFeature) and iOwner < 0 and not SASCurrentDefines.getInt("CAN_CHOP_UNOWNED_FEATURES"):
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


def _workerTurns(plot, iBuild, player):
	# <!-- custom: Turns for one ordinary Worker, as the plot's own build progress counts them: the Worker's XML work rate with the player's worker speed modifier. (Claude code Opus 5.5) -->
	iWorker = gc.getCivilizationInfo(player.getCivilizationType()).getCivilizationUnits(getInfoTypeOrFail("UNITCLASS_WORKER"))
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


_HELP["workers"] = "Planning Workers by hand. Without city: each Worker with where it is, whether automated and its current mission; per city the worked plots with no improvement and the city AI's three most valued builds; and per leader we can trade with whether their capital is on our trade network (no road link means no foreign trade routes with them). With city: each plot of its radius with terrain, feature, bonus, river, improvement, route, yields, whether worked, the city AI's best build and value, and every improvement build a Worker could make there with its yield change and turns for one Worker. The AI's choice is a reference to compare with, not an order. args: city, player."


def cmd_workers(args):
	# <!-- custom: SASPilot only automated Workers until the user asked it to plan them itself and compare its choices with the AI's (2026-11-14): yields, rivers, roads to neighbours for trade.
	# The city AI's per-plot best build comes from getSASPilotCityBuildsJson, as Python had no getter; the rest is read here. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	saspilot._requireOwnTeamUnderFog(args, player, "Worker planning")
	if not hasattr(gc.getGame(), "getSASPilotCityBuildsJson"):
		raise ValueError("this DLL predates getSASPilotCityBuildsJson; build or install a current one")
	bAdvice = saspilot._adviceAllowed()
	if args.get("city") is not None:
		city = saspilot._city(args)
		aiRows = saspilot.fromJson(saspilot._pilotGame("getSASPilotCityBuildsJson").getSASPilotCityBuildsJson(player.getID(), city.getID()))
		plots = []
		for row in aiRows:
			plot = gc.getMap().plot(row["x"], row["y"])
			if plot.getOwner() != player.getID():
				continue
			entry = {"x": row["x"], "y": row["y"], "worked": row["worked"], "terrain": saspilot._typeOrNone(gc.getTerrainInfo, plot.getTerrainType()), "feature": saspilot._typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "bonus": saspilot._typeOrNone(gc.getBonusInfo, plot.getBonusType(player.getTeam())), "river": bool(plot.isRiver()), "hills": bool(plot.isHills()), "improvement": saspilot._typeOrNone(gc.getImprovementInfo, plot.getImprovementType()), "route": saspilot._typeOrNone(gc.getRouteInfo, plot.getRouteType()), "yields": [plot.getYield(YieldTypes(j)) for j in range(YieldTypes.NUM_YIELD_TYPES)]}
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
	for unit in saspilot._units(player):
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
	for city in saspilot._cities(player):
		aiRows = saspilot.fromJson(saspilot._pilotGame("getSASPilotCityBuildsJson").getSASPilotCityBuildsJson(player.getID(), city.getID()))
		# <!-- custom: Water without a resource takes no improvement, and listed coastal cities' ocean plots as "unimproved" on the first try (turn 286, 2026-11-14). (Claude code Opus 5.5) -->
		unimproved = [[row["x"], row["y"]] for row in aiRows if row["worked"] and _improvable(gc.getMap().plot(row["x"], row["y"]), player) and not (row["x"] == city.getX() and row["y"] == city.getY())]
		suggestions = [row for row in aiRows if row["bestBuild"] and gc.getMap().plot(row["x"], row["y"]).getOwner() == player.getID()]
		suggestions.sort(lambda a, b: cmp(b["bestValue"], a["bestValue"]))
		# <!-- custom: The city AI's best builds leave out routes, yet a railroad adds +1 production to SAS's mines, lumbermills and quarries (ImprovementInfo RouteYieldChanges); on turn 287 of the modern baseline every such plot already had one (2026-11-14).
		# Listed for any route that adds yield to the plot's improvement. (Claude code Opus 5.5) -->
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
	# <!-- custom: Foreign trade routes need the two capitals on one trade network, roads or rivers or coast; a missing road link to a neighbour is a Worker job a person might take.
	# Only capitals the team has revealed are listed, so fog hides nothing more than the map does. (Claude code Opus 5.5) -->
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


_HELP["move"] = "Move a unit to a plot (MISSION_MOVE_TO). Only to a plot one step away unless whole=1, which orders the whole path, continuing over later turns: moves over several plots go a plot at a time with 'step', to react to what each reveals. args: unit, x, y, whole, player."


def cmd_move(args):
	unit = saspilot._unit(args)
	plot = saspilot._plot(args)
	# <!-- custom: Checked with Python's CyUnit.generatePath first.
	# At turn 81 of the fog-on playthrough (2026-11-13), right after Open Borders with Ethiopia were signed, 'path' found a 7-turn route for a Warrior inside Ethiopia's borders while 'move' said it had no path; the same pathfinder as 'path', GroupPathFinder, now decides both, so they cannot disagree. (Claude code Opus 5.5) -->
	path = saspilot.fromJson(saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), 0))
	if not path.get("found"):
		raise ValueError("unit %d has no path to %d,%d" % (unit.getID(), plot.getX(), plot.getY()))
	# <!-- custom: One plot unless whole=1, the user's rule (2026-11-15): any movement over several plots goes a plot at a time, reacting to what each step reveals, and a guard holds better than a habit; a Work Boat sent round Suleiman's island in one order went north into the ice. 'step' moves one plot toward a far target. (Claude code Opus 5.5) -->
	if len(path.get("steps") or []) > 1 and not args.get("whole"):
		raise ValueError("%d,%d is %d plots away: move one plot at a time ( 'step unit=%d x=%d y=%d' ), or pass whole=1 to order the whole path" % (plot.getX(), plot.getY(), len(path["steps"]), unit.getID(), plot.getX(), plot.getY()))
	if saspilot._state.get("follow", True):
		saspilot._lookAt(plot)
	return cmd_mission({"unit": args["unit"], "player": args.get("player"), "mission": "MISSION_MOVE_TO", "data1": plot.getX(), "data2": plot.getY()})


_HELP["step"] = "Move a unit one plot along its path toward x, y, and report what that step showed, so the next can react: where it stands, moves left, the steps of the path still to go, how many plots it newly revealed, and the foreign units now in sight within two plots. For any move over several plots in a turn (a scout, a mounted unit, roads), as each plot can reveal what changes the plan. args: unit, x, y, player."


def cmd_step(args):
	# <!-- custom: The user's rule (2026-11-15): any movement over several plots in a turn goes one plot at a time, not a long path in one order, to react, retreat or change course on what each step reveals; a Work Boat sent round Suleiman's island in one order went north into the ice before the next look. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	iTeam = unit.getTeam()
	if saspilot._fogTeam(args) >= 0 and iTeam != saspilot._fogTeam(args):
		raise ValueError("with fog on, 'step' takes the team's own units")
	target = saspilot._plot(args)
	path = saspilot.fromJson(saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), target.getX(), target.getY(), 0))
	if not path or not path.get("found") or not path.get("steps"):
		raise ValueError("unit %d has no path to %d,%d" % (unit.getID(), target.getX(), target.getY()))
	first = path["steps"][0]
	kMap = gc.getMap()
	before = 0
	for i in range(kMap.numPlots()):
		if kMap.plotByIndex(i).isRevealed(iTeam, False):
			before += 1
	cmd_move({"unit": unit.getID(), "player": unit.getOwner(), "x": first["x"], "y": first["y"]})
	after = 0
	for i in range(kMap.numPlots()):
		if kMap.plotByIndex(i).isRevealed(iTeam, False):
			after += 1
	foreign = []
	for dy in range(-2, 3):
		for dx in range(-2, 3):
			plot = plotXY(unit.getX(), unit.getY(), dx, dy)
			if plot is None or plot.isNone() or not plot.isVisible(iTeam, False):
				continue
			for i in range(plot.getNumUnits()):
				other = plot.getUnit(i)
				if other.getTeam() != iTeam and not other.isInvisible(iTeam, False):
					foreign.append({"owner": other.getOwner(), "type": gc.getUnitInfo(other.getUnitType()).getType(), "x": plot.getX(), "y": plot.getY(), "atWar": bool(gc.getTeam(iTeam).isAtWar(other.getTeam()))})
	return {"unit": unit.getID(), "x": unit.getX(), "y": unit.getY(), "movesLeft": unit.movesLeft(), "stepsLeft": len(path["steps"]) - 1, "newlyRevealed": after - before, "foreignNear": foreign}
