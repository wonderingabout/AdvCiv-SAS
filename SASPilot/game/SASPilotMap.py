# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotMap: the map as the player knows it: plots ('plot', 'plots', 'potential', 'grid'), the drawn map and its signs ('map', 'signs', 'mark'), its lands and seas ('geography', 'shore'), borders, the resources known and how to connect them ('resources', 'routes').
# Split from SASPilotCommands.py on 2026-11-28, the fifth part moved out by topic; the user suggested the map, and resources with it, and Codex (GPT-6.2-Sol) grouped them, resources answering where they lie and how to connect them.
# Exploration ('directions', 'scout', 'seareach') and expansion ('sites', 'plansites') stay apart, and the map helpers they share, such as _coastLaneRows, stay there and are reached as saspilot.
# SASPilotCommands.py loads it from beside itself, again whenever it changes, and adds its commands and help, so commands there that call one of these, such as 'research' calling 'resources', still find it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from CvPythonExtensions import *
# <!-- custom: os finds a map script's preview files; SASCurrentDefines reads the tech diffusion defines 'geography' explains; getInfoTypeOrFail finds forest, jungle, ocean and railroad, as in SASPilotCommands. (Claude code Opus 5.5) -->
import os
import SASCurrentDefines
from SASUtils import getInfoTypeOrFail

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}


_HELP["plot"] = "One plot in full, with its units. args: x, y."


def cmd_plot(args):
	plot = saspilot._plot(args)
	text = saspilot._plotsJson(plot.getX(), plot.getY(), 0, saspilot._fogTeam(args))
	if text == "[]":
		raise ValueError("plot %d,%d is not revealed; fog is on" % (plot.getX(), plot.getY()))
	return saspilot.RawJson(text[1:-1])


_HELP["plots"] = "The plots within a radius, in full. With fog on, only the plots the active team has revealed, each as it last saw it and with units only where it sees now. Center it on coordinates, one of our units, a city or the plot the camera looks at (camera=1). args: x, y, unit, city, camera, radius (default 1; the larger map side covers the whole map), fog (optional, overrides the 'fog' switch for this request), player."


def cmd_plots(args):
	_cameraCenter(args)
	anchors = sum([args.get(key) is not None for key in ("x", "unit", "city")])
	if anchors != 1 or (args.get("x") is None) != (args.get("y") is None):
		raise ValueError("give x and y, a unit, or a city as the center")
	if args.get("unit") is not None or args.get("city") is not None:
		saspilot._requireOwnTeamUnderFog(args, saspilot._player(args), "the map center")
		if args.get("unit") is not None:
			plot = saspilot._unit(args).plot()
		else:
			plot = saspilot._city(args).plot()
	else:
		plot = saspilot._plot(args)
	return saspilot.RawJson(saspilot._plotsJson(plot.getX(), plot.getY(), int(args.get("radius", 1)), saspilot._fogTeam(args)))


_HELP["potential"] = "What each revealed plot of a square could yield once improved, for judging sites and Workers by more than today's yields: each plot's yields now, and every improvement the player could build there, with its yields as [food, production, commerce] and now=true when it can start today (false: a tech is missing). Yields count the player's techs now, so later tech bonuses (a Cottage growing, Farms with Biology) are not in them. Center as for 'plots': x and y, unit, city or camera=1; radius (default 2, a city's square). args: x, y, unit, city, camera, radius, player."


def cmd_potential(args):
	# <!-- custom: The user's point at turn 59 of the islands replay (2026-11-15): judging plots by today's yields rated a site with two Clams below plain coast, as an unimproved Clam reads as coast until Fishing Boats; the same holds for grassland a Cottage would make commercial.
	# Each improvement build the player could make (CyPlayer.canBuild; bTestVisible=True skips its tech and gold checks, for builds a tech away), and the yields it gives: the nature yield, without the feature when the build removes it, plus CyPlot.calculateImprovementYieldChange.
	# That binding takes a fourth argument, bOptimal, but AdvCiv's C++ has three and always counts the owner's current techs, so future tech bonuses are not counted.
	# Under fog a build that only a hidden bonus makes valid is left out, as canBuild reads the true bonus and would reveal it. (Claude code Opus 5.5) -->
	_cameraCenter(args)
	player = saspilot._player(args)
	iTeam = player.getTeam()
	iFogTeam = saspilot._fogTeam(args)
	if args.get("unit") is not None:
		center = saspilot._unit(args).plot()
	elif args.get("city") is not None:
		center = saspilot._city(args).plot()
	else:
		center = saspilot._plot(args)
	iRadius = int(args.get("radius", 2))
	kMap = gc.getMap()
	# <!-- custom: Bounded: a negative radius returned nothing silently and a mistyped large one could stall the game thread (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	if iRadius < 0 or iRadius > 15:
		raise ValueError("radius must be between 0 and 15")
	builds = [i for i in range(gc.getNumBuildInfos()) if gc.getBuildInfo(i).getImprovement() >= 0]
	result = []
	for dy in range(-iRadius, iRadius + 1):
		for dx in range(-iRadius, iRadius + 1):
			plot = plotXY(center.getX(), center.getY(), dx, dy)
			if plot is None or plot.isNone() or not plot.isRevealed(iTeam, False):
				continue
			iFeature = plot.getFeatureType()
			iTrueBonus = plot.getBonusType(-1)
			bHiddenBonus = iFogTeam >= 0 and iTrueBonus >= 0 and plot.getBonusType(iTeam) != iTrueBonus
			options = []
			for iBuild in builds:
				if not player.canBuild(plot, iBuild, False, True):
					continue
				info = gc.getBuildInfo(iBuild)
				iImprovement = info.getImprovement()
				# <!-- custom: Left out only when nothing but that bonus makes the improvement valid here: the first filter also dropped improvements the terrain or feature allows anyway, and their absence hinted at the bonus (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
				kImprovement = gc.getImprovementInfo(iImprovement)
				if bHiddenBonus and kImprovement.isImprovementBonusMakesValid(iTrueBonus) and not (kImprovement.getTerrainMakesValid(plot.getTerrainType()) or (iFeature >= 0 and kImprovement.getFeatureMakesValid(iFeature)) or (plot.isHills() and kImprovement.isHillsMakesValid()) or (plot.isFreshWater() and kImprovement.isFreshWaterMakesValid()) or (plot.isRiverSide() and kImprovement.isRiverSideMakesValid())):
					continue
				bRemove = iFeature >= 0 and info.isFeatureRemove(iFeature)
				yields = [plot.calculateNatureYield(YieldTypes(j), TeamTypes(iTeam), bRemove) + plot.calculateImprovementYieldChange(ImprovementTypes(iImprovement), YieldTypes(j), PlayerTypes(player.getID()), False) for j in range(YieldTypes.NUM_YIELD_TYPES)]
				options.append({"build": info.getType(), "improvement": gc.getImprovementInfo(iImprovement).getType(), "yields": yields, "now": bool(player.canBuild(plot, iBuild, False, False))})
			# <!-- custom: Out of sight, the yields the team would see: nature yield plus the improvement it last saw there, not the live one, which showed an improvement a rival had built out of sight (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			bVisible = iFogTeam < 0 or plot.isVisible(iFogTeam, False)
			if bVisible:
				yields = saspilot._yields(plot.getYield)
			else:
				iSeen = plot.getRevealedImprovementType(iFogTeam, False)
				yields = []
				for j in range(YieldTypes.NUM_YIELD_TYPES):
					iYield = plot.calculateNatureYield(YieldTypes(j), TeamTypes(iTeam), False)
					if iSeen >= 0:
						iYield += plot.calculateImprovementYieldChange(ImprovementTypes(iSeen), YieldTypes(j), PlayerTypes(player.getID()), False)
					yields.append(iYield)
			result.append({"x": plot.getX(), "y": plot.getY(), "yields": yields, "visible": bool(bVisible), "options": options})
	return result


# <!-- custom: Export canonical coordinates for the desktop map renderer.
# Under fog, use the game's remembered ownership, improvements and routes, and withhold fields without a last-seen accessor until the tile is visible. (GPT-6.1-Sol) -->
_TRADE_NEIGHBORS = ((1, 0), (0, 1), (1, 1), (-1, 1))


def _cameraCenter(args):
	# <!-- custom: camera=1 centers a request on the plot the main view looks at, as the user asked (2026-11-15) for the area around where a player looks. CyCamera.GetLookAt fills a point it is given, and CyMap.pointToPlot turns that into a plot; the first try, GetLookAt() with no argument, did not match its C++ signature. (Claude code Opus 5.5) -->
	if not args.get("camera"):
		return
	point = NiPoint3(0.0, 0.0, 0.0)
	CyCamera().GetLookAt(point)
	plot = CyMap().pointToPlot(point.x, point.y)
	if plot is None or plot.isNone():
		raise ValueError("the camera looks at no plot")
	del args["camera"]
	args["x"] = plot.getX()
	args["y"] = plot.getY()


def _gridBounds(kMap, args):
	_cameraCenter(args)
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
			plot = saspilot._city(args).plot()
		elif "unit" in args:
			plot = saspilot._unit(args).plot()
		else:
			plot = saspilot._plot(args)
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


_HELP["signs"] = "The map's signs a player sees, as the window shows them: each with its plot, caption and owner (-1 for a sign everyone sees). The user's signs are read here too. args: player."


def cmd_signs(args):
	# <!-- custom: Checking the city-site signs 'mark' placed (islands replay, 2026-11-15) took a 'py' call: 'grid' lists the dot map but not signs, and the user marks the map with signs too.
	# A player sees their own signs and those placed for everyone (player -1). (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	engine = CyEngine()
	result = []
	for i in range(engine.getNumSigns()):
		sign = engine.getSignByIndex(i)
		# <!-- custom: int(): getPlayerType returns a PlayerTypes value, which the first reply wrote as the string "0". (Claude code Opus 5.5) -->
		iOwner = int(sign.getPlayerType())
		if iOwner != -1 and iOwner != player.getID():
			continue
		plot = sign.getPlot()
		result.append({"x": plot.getX(), "y": plot.getY(), "caption": sign.getCaption(), "owner": iOwner})
	return result


_HELP["mark"] = "Mark a candidate city site the way a player does with BUG's dot map (Alt+X): a city dot and cross at x, y in that overlay, which the player sees, edits and keeps with the save, plus a sign when text is given; 'grid' lists the dot map's cities, the player's own included. clear=1 removes the dot (and sign) at x, y. Cosmetic: nothing in the game changes. args: x, y, text, color (COLOR_ type, or contrast: the colour farthest from our civ's colours; default contrast on one of our cities, else COLOR_GREEN), layer (dot-map layer, default 0), clear."


def cmd_mark(args):
	# <!-- custom: The user's idea in the scouting trial (2026-11-14): the agent compared city sites only in JSON, so the user watching could not see which plots it meant.
	# A first version drew its own dots on the overlay layer, until the user asked whether the agent had Alt+X: BUG's dot map is the player's tool for exactly this, so marks now go into it through addCityAt, the same game message an Alt+X click sends, and the player can see and edit them. (Claude code Opus 5.5) -->
	import CvStrategyOverlay
	dotMap = CvStrategyOverlay.getDotMap()
	player = gc.getPlayer(saspilot._activePlayerId())
	plot = gc.getMap().plot(int(args["x"]), int(args["y"]))
	if plot is None or plot.isNone():
		raise ValueError("no plot at %s,%s" % (args["x"], args["y"]))
	point = (plot.getX(), plot.getY())
	if args.get("clear"):
		dotMap.removeCityAt(point)
		CyEngine().removeSign(plot, player.getID())
	else:
		# <!-- custom: Only a COLOR_ type in the colour table: getInfoTypeForString accepts types of any table, so color=TECH_AGRICULTURE passed and stored an unrelated index in BUG's dot map (Codex's review, round 38). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		szColor = args.get("color")
		# <!-- custom: The user at turn 54 of the 2026-11-19 validation run: white marks on our own white cities were hard to read; use a colour that contrasts with ours.
		# color=contrast picks it from our civ's colours, and is the default for a mark on one of our cities, so it works for any civ. (Claude code Opus 5.5) -->
		if szColor is None:
			city = plot.getPlotCity()
			if city is not None and not city.isNone() and city.getOwner() == player.getID():
				szColor = "contrast"
			else:
				szColor = "COLOR_GREEN"
		# <!-- custom: sas-ci-string-compare-exemption: The mailbox protocol accepts stable command and argument keys. (GPT-6.2-Sol) -->
		if szColor == "contrast":
			szColor = saspilot._contrastColor(player)
		iColor = saspilot._findOptionalInfoType(szColor)
		# <!-- custom: The check first also compared iColor with gc.getNumColorInfos, which Python does not have: every 'mark' failed with an AttributeError (islands replay, 2026-11-15).
		# Type names are unique across tables, so a COLOR_ name that resolves is a colour; its type is compared back. (Claude code Opus 5.5) -->
		if not szColor.startswith("COLOR_") or iColor < 0 or gc.getColorInfo(iColor).getType() != szColor:
			raise ValueError("unknown color %s; give a COLOR_ type" % szColor)
		dotMap.addCityAt(point, iColor, int(args.get("layer", 0)))
		if args.get("text"):
			CyEngine().removeSign(plot, player.getID())
			CyEngine().addSign(plot, player.getID(), args["text"])
		dotMap.show()
	return {"note": "the dot map applies the change through a game message, so it shows in the next reply", "dotMap": saspilot._dotMapCities(player.getID())}


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


_HELP["grid"] = "Fetch structured map tiles, river boundaries and optional trade-network links. With no area, fetch the map. The box is inclusive; a center and radius clip to map bounds. With fog on, fogEdge lists the unrevealed plots next to a revealed one, each with only water true or false, which the coastline art shows a player at the fog's edge; edge=0 leaves it out. args: box ([west,south,east,north]), x, y, city, unit, camera (1: the plot the main view looks at), radius, network, edge, player."


def cmd_grid(args):
	player = saspilot._player(args)
	saspilot._requireOwnTeamUnderFog(args, player, "the map grid")
	iFogTeam = saspilot._fogTeam(args)
	iTeam = player.getTeam()
	kMap = gc.getMap()
	x0, y0, x1, y1 = _gridBounds(kMap, args)
	tiles, network, owners = [], {}, {}
	bNetwork = bool(args.get("network", True))
	# <!-- custom: The fog edge, the user's point at turn 2 of the scouting trial (2026-11-14): the plot two north of the Clam was unrevealed, yet the screen showed its shore, so the water beside it looked like a lake; strong players read the art at the fog's edge, and SASPilot knew nothing there.
	# Civ4 draws each revealed plot's coastline from whether its neighbours are land or water, so that much of an unrevealed neighbour is on screen and stays fair under play.
	# Only water is given: terrain and trees in the fade were not checked against the art. (Claude code Opus 5.5) -->
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
			# <!-- custom: Feature and resource for every revealed plot, not only those in sight: the window draws both on fogged plots, as Civ4 keeps no remembered copy of features and shows a resource once the team has its reveal tech (plot.getBonusType(team) applies that).
			# In the scouting trial (2026-11-14) a goody hut's map revealed Rice at 11,18, which 'resources' listed, yet a city-site query over 'grid' missed it because the bonus was left out off sight.
			# Rivers and yields stay for plots in sight. (Claude code Opus 5.5) -->
			row = {"x": x, "y": y, "visible": visible, "owner": owner,
				"feature": saspilot._typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "bonus": saspilot._typeOrNone(gb, plot.getBonusType(iFogTeam)),
				"terrain": saspilot._typeOrNone(gc.getTerrainInfo, plot.getTerrainType()),
				"hill": bool(plot.isHills()), "peak": bool(plot.isPeak()), "water": bool(plot.isWater()),
				"improvement": saspilot._typeOrNone(gc.getImprovementInfo, improvement), "route": saspilot._typeOrNone(gc.getRouteInfo, route)}
			if owner >= 0 and owner not in owners:
				owners[owner] = gc.getPlayer(owner).getName()
			if visible:
				row["southRiver"] = bool(plot.isNOfRiver())
				row["eastRiver"] = bool(plot.isWOfRiver())
				row["yields"] = saspilot._yields(plot.getYield)
				# <!-- custom: The defence a unit of ours would get here against anyone but the plot's owner, from the game's rule (CvPlot::defenseModifier, buildings left out), for scouts ending a turn on safe ground (the user, 2026-11-14).
				# The XML alone misled: SAS forest is 0 and jungle -25, but both add iRivalDefense 25 outside the attacker's land, so forest gives +25%, jungle 0 and a hill +25 more, as the combat report at 11,15 showed. (Claude code Opus 5.5) -->
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
		"wrapX": bool(kMap.isWrapX()), "wrapY": bool(kMap.isWrapY()), "owners": owners, "tiles": tiles, "tradeLinks": links, "fogEdge": edge, "dotMap": saspilot._dotMapCities(player.getID())}


_HELP["map"] = "A text map of the known world, row by row from the north, as the window's map shows it: C our city, c another's city, ~ water, ^ peak, h hills, f forest or jungle, x another's land, . other land, space unknown; u marks a plot holding one of our units. With owners=1, land shows its owner instead (player IDs as 0-9, a-z, then A-Z without C; * Barbarians; legend in 'owners'; . unowned), to read border shapes. Columns are x from 'x0', rows y from 'y1' down. With fog on, only what the team has revealed, each owner as last seen. args: x0, x1, y0, y1 (default the known area plus one plot), owners, player."


def cmd_map(args):
	# <!-- custom: Planning scouting and city sites needed a picture of what is known: at turn 25 of the turn-0 game (2026-11-14) only 150 of 3168 plots were revealed, which the user's advice to scout first made the question; 'routes' draws only our own land.
	# Written first as a 'py' snippet, then kept as a command. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	# <!-- custom: Codex's review: player= a rival would mark that rival's units under fog. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	saspilot._requireOwnTeamUnderFog(args, player, "the map")
	iTeam = saspilot._fogTeam(args)
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
	iForest = getInfoTypeOrFail("FEATURE_FOREST")
	iJungle = getInfoTypeOrFail("FEATURE_JUNGLE")
	ours = {}
	for unit in saspilot._units(player):
		ours[(unit.getX(), unit.getY())] = True
	# <!-- custom: owners=1, the user's idea at turn 200 of a Large autoplay (2026-11-15): reading a border's shape, who fronts whom and who is boxed in, needs the owner of each land plot, not one x for every rival. Land shows its owner's character from _ownerChar, cities C (ours) and c, water ~ and unowned land . as before. (Claude code Opus 5.5) -->
	bOwners = bool(int(args.get("owners", 0)))
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
			elif bOwners and not plot.isWater() and iOwner >= 0:
				line.append(_ownerChar(iOwner))
			elif bOwners and not plot.isWater():
				line.append(".")
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
	result = {"x0": x0, "y1": y1, "known": len(known), "plots": kMap.numPlots(), "rows": rows}
	if bOwners:
		team = gc.getTeam(player.getTeam())
		result["owners"] = dict([(_ownerChar(i), gc.getPlayer(i).getName()) for i in range(gc.getMAX_PLAYERS()) if gc.getPlayer(i).isEverAlive() and (iTeam < 0 or i == player.getID() or gc.getPlayer(i).isBarbarian() or team.isHasMet(gc.getPlayer(i).getTeam()))])
	return result


# <!-- custom: One character per player ID: digits, lowercase, then uppercase without C (our cities), so SAS's 48 players fit; base 36 alone failed on the Barbarian player's ID, past 35, on the first try (2026-11-15).
# Barbarians are *. (Claude code Opus 5.5) -->
_OWNER_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABDEFGHIJKLMNOPQRSTUVWXYZ"


def _ownerChar(iPlayer):
	if gc.getPlayer(iPlayer).isBarbarian():
		return "*"
	return _OWNER_CHARS[iPlayer]


_HELP["borders"] = "Land borders in numbers, to pick a front: per player met (and Barbarians) whose land we have seen, their land plots, our frontier with them (our land plots touching theirs) and theirs with us, the other players their land touches with how many plots (one boxed in by several is stretched), and their seen cities nearest ours with the distance in plots to our nearest city and whether the city is coastal. Sorted by our frontier, longest first. 'map owners=1' draws the same. With fog on, owners as the team last saw them. args: player."


def cmd_borders(args):
	# <!-- custom: The user's idea at turn 200 of a Large autoplay (2026-11-15): most rivals were weaker than us and liked us, so choosing a target came down to geography, and the agent should read border shapes as numbers rather than from the minimap's colors. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	saspilot._requireOwnTeamUnderFog(args, player, "borders")
	iTeam = saspilot._fogTeam(args)
	team = gc.getTeam(player.getTeam())
	kMap = gc.getMap()
	owners = {}
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if plot.isWater() or (iTeam >= 0 and not plot.isRevealed(iTeam, False)):
			continue
		iOwner = plot.getOwner()
		if iTeam >= 0:
			iOwner = plot.getRevealedOwner(iTeam, False)
		if iOwner >= 0:
			owners[(plot.getX(), plot.getY())] = iOwner
	land = {}
	touching = {}
	for (x, y), iOwner in owners.items():
		land[iOwner] = land.get(iOwner, 0) + 1
		seen = {}
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				adjacent = kMap.plot(x + dx, y + dy)
				if adjacent.isNone():
					continue
				iOther = owners.get((adjacent.getX(), adjacent.getY()), -1)
				if iOther >= 0 and iOther != iOwner:
					seen[iOther] = True
		for iOther in seen.keys():
			touching.setdefault(iOwner, {})[iOther] = touching.setdefault(iOwner, {}).get(iOther, 0) + 1
	ours = saspilot._cities(player)
	rows = []
	for iOther in land.keys():
		if iOther == player.getID():
			continue
		other = gc.getPlayer(iOther)
		if iTeam >= 0 and not other.isBarbarian() and not team.isHasMet(other.getTeam()):
			continue
		cities = []
		for city in saspilot._cities(other):
			if iTeam >= 0 and not city.isRevealed(iTeam, False):
				continue
			iDistance = -1
			if ours:
				iDistance = min([plotDistance(city.getX(), city.getY(), mine.getX(), mine.getY()) for mine in ours])
			cities.append({"name": city.getName(), "x": city.getX(), "y": city.getY(), "distance": iDistance, "coastal": bool(city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()))})
		cities.sort(lambda a, b: cmp(a["distance"], b["distance"]))
		theirs = touching.get(iOther, {})
		rows.append({"player": iOther, "name": other.getName(), "landPlots": land[iOther], "frontier": touching.get(player.getID(), {}).get(iOther, 0), "theirFrontier": theirs.get(player.getID(), 0),
			"touches": dict([(gc.getPlayer(i).getName(), n) for (i, n) in theirs.items() if i != player.getID()]), "citiesSeen": len(cities), "nearestCities": cities[:3]})
	rows.sort(lambda a, b: cmp(b["frontier"], a["frontier"]))
	return {"landPlots": land.get(player.getID(), 0), "players": rows}


def _seaCrossing(player, team, iTeam, cyMap, iOcean, areas):
	# <!-- custom: The user's point on the SAS48 islands save (2026-11-15): the AI there needed to explore other islands, and whether rows of islands can be crossed before ocean ships depends on the map and the rules, so ask the engine rather than guess from the script.
	# Ships: each of our civilization's sea units, whether it may enter ocean (CvUnitInfo's TerrainImpassable, unless its TerrainPassableTech is known), and the tech path to it, as 'research' would queue it. (Claude code Opus 5.5) -->
	ships = []
	memo = {}
	civ = gc.getCivilizationInfo(player.getCivilizationType())
	for iClass in range(gc.getNumUnitClassInfos()):
		iUnit = civ.getCivilizationUnits(iClass)
		if iUnit == -1:
			continue
		info = gc.getUnitInfo(iUnit)
		if info.getDomainType() != DomainTypes.DOMAIN_SEA:
			continue
		bOcean = not info.getTerrainImpassable(iOcean)
		iPassTech = info.getTerrainPassableTech(iOcean)
		if not bOcean and iPassTech != -1 and team.isHasTech(iPassTech):
			bOcean = True
		techs = [info.getPrereqAndTech()] + [info.getPrereqAndTechs(i) for i in range(gc.getNUM_UNIT_AND_TECH_PREREQS())]
		techs = [i for i in techs if i >= 0]
		path = []
		seen = {}
		for iTech in techs:
			saspilot._techPathVisit(player, team, iTech, path, seen, memo)
		# <!-- custom: getResearchTurnsLeft gives -1 with no research rate, as before the first city: the turn-0 run summed them to "-22 turns", so turns stay None then. (Claude code Opus 5.5) -->
		turns = [player.getResearchTurnsLeft(i, True) for i in path]
		iTurns = None
		if -1 not in turns:
			iTurns = sum(turns)
		ships.append({"unit": info.getType(), "canEnterOcean": bOcean, "techs": [gc.getTechInfo(i).getType() for i in techs], "techsMissing": len(path), "pathBeakers": sum([team.getResearchCost(i) - team.getResearchProgress(i) for i in path]), "pathTurns": iTurns})
	ships.sort(lambda a, b: cmp(a["pathBeakers"], b["pathBeakers"]))
	# <!-- custom: Reach along seen coast and lakes: from the water next to our landmasses, through revealed water that is not open ocean, which other seen landmasses touch it.
	# Unrevealed water stops the walk, so a landmass absent here may still be reachable; a ship that cannot enter ocean is held to this. (Claude code Opus 5.5) -->
	ourAreas = {}
	for a in areas.values():
		if a["ours"]:
			ourAreas[a["area"]] = True
	frontier = []
	visited = {}
	for i in range(cyMap.numPlots()):
		plot = cyMap.plotByIndex(i)
		if plot.isWater() or not ourAreas.has_key(plot.getArea()) or not plot.isRevealed(iTeam, False):
			continue
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
			if adjacent is not None and not adjacent.isNone() and adjacent.isWater() and adjacent.isRevealed(iTeam, False) and adjacent.getTerrainType() != iOcean:
				iIndex = cyMap.plotNum(adjacent.getX(), adjacent.getY())
				if not visited.has_key(iIndex):
					visited[iIndex] = True
					frontier.append(adjacent)
	reached = {}
	while frontier:
		plot = frontier.pop()
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
			if adjacent is None or adjacent.isNone() or not adjacent.isRevealed(iTeam, False):
				continue
			if not adjacent.isWater():
				if not ourAreas.has_key(adjacent.getArea()):
					reached[adjacent.getArea()] = True
				continue
			if adjacent.getTerrainType() == iOcean:
				continue
			iIndex = cyMap.plotNum(adjacent.getX(), adjacent.getY())
			if not visited.has_key(iIndex):
				visited[iIndex] = True
				frontier.append(adjacent)
	coastReach = [{"area": iArea, "landPlotsSeen": areas[iArea]["landPlotsSeen"], "owners": areas[iArea]["owners"].keys()} for iArea in reached.keys() if areas.has_key(iArea)]
	return {"ships": ships, "coastWaterSeen": len(visited), "landmassesReachedAlongCoast": coastReach}


_HELP["geography"] = "The map's composition as our team knows it, with takeaways. From the plots we have revealed: land and water seen (open ocean apart), each landmass seen with its land plots, our cities and each owner's plots and seen cities on it, unowned land, and whether it is fully explored (no seen land plot of it next to an unrevealed plot); then each met rival, whether it shares a landmass with us and whether we have open borders. Beside them the settings that describe the map: script, size and grid, sea level, non-default map options, and the AI's landHeavy / navalHeavy reading, which changes its unit choices. 'takeaways' turns these into short strategic notes: rivals on our landmass or none, room left to settle, exploration left, and what contact gives (research speed from met teams knowing a tech, trades) and open borders overseas (trade routes, entry into their waters). 'landmasses' counts those seen with the mean and median size of the fully explored ones; 'bonusesSeen' the bonuses on seen plots that our techs reveal, with their share. 'seaCrossing' lists our civilization's ships, whether each may enter ocean and the tech path to it, and the seen landmasses our coast reaches through seen water that is not open ocean. 'preview' gives the script's World Picker image, as every player sees it at setup. args: player."


def cmd_geography(args):
	# <!-- custom: The user's point (2026-11-15): record the map's composition with takeaways, not flags: navalHeavy means snaky continents on Archipelago and islets with its Tiny Islands option, and on SAS Large Facing Islands, where every met rival lay over water, little army is needed, though an unexpected one can surprise.
	# Observed geography decides the notes rather than the script's name, which only hints; the script and options are returned beside them. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	cyMap = gc.getMap()
	g = gc.getGame()
	iOcean = getInfoTypeOrFail("TERRAIN_OCEAN")
	iLandSeen = 0
	iWaterSeen = 0
	iOceanSeen = 0
	areas = {}
	bonuses = {}
	for i in range(cyMap.numPlots()):
		plot = cyMap.plotByIndex(i)
		if not plot.isRevealed(iTeam, False):
			continue
		# <!-- custom: getBonusType(team) hides a bonus whose reveal tech the team lacks, as the map does for a player. (Claude code Opus 5.5) -->
		iBonus = plot.getBonusType(iTeam)
		if iBonus != -1:
			szBonus = gc.getBonusInfo(iBonus).getType()
			bonuses[szBonus] = bonuses.get(szBonus, 0) + 1
		if plot.isWater():
			iWaterSeen += 1
			if plot.getTerrainType() == iOcean:
				iOceanSeen += 1
			continue
		iLandSeen += 1
		iArea = plot.getArea()
		if not areas.has_key(iArea):
			areas[iArea] = {"area": iArea, "landPlotsSeen": 0, "ourCities": 0, "owners": {}, "citiesSeen": {}, "unownedPlots": 0, "explored": True}
		area = areas[iArea]
		area["landPlotsSeen"] += 1
		iOwner = plot.getRevealedOwner(iTeam, False)
		if iOwner == -1:
			area["unownedPlots"] += 1
		else:
			szOwner = gc.getPlayer(iOwner).getName()
			area["owners"][szOwner] = area["owners"].get(szOwner, 0) + 1
		if plot.isCity() and plot.getPlotCity().isRevealed(iTeam, False):
			iCityOwner = plot.getRevealedOwner(iTeam, False)
			if iCityOwner != -1 and gc.getPlayer(iCityOwner).getTeam() == iTeam:
				area["ourCities"] += 1
			elif iCityOwner != -1:
				szOwner = gc.getPlayer(iCityOwner).getName()
				area["citiesSeen"][szOwner] = area["citiesSeen"].get(szOwner, 0) + 1
		# <!-- custom: A landmass is fully explored when none of its seen land touches an unrevealed plot: beyond one, it may go on. (Claude code Opus 5.5) -->
		if area["explored"]:
			for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
				adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
				if adjacent is not None and not adjacent.isNone() and not adjacent.isRevealed(iTeam, False):
					area["explored"] = False
					break
	# <!-- custom: Ours are the landmasses with our cities, or, before the first city, those our land units stand on: at turn 0 of the islands replay our own island counted as another landmass. (Claude code Opus 5.5) -->
	for a in areas.values():
		a["ours"] = a["ourCities"] > 0
	if not [a for a in areas.values() if a["ours"]]:
		(unit, it) = player.firstUnit(False)
		while unit:
			if unit.getDomainType() == DomainTypes.DOMAIN_LAND and areas.has_key(unit.plot().getArea()):
				areas[unit.plot().getArea()]["ours"] = True
			(unit, it) = player.nextUnit(it, False)
	ours = [a for a in areas.values() if a["ours"]]
	others = [a for a in areas.values() if not a["ours"]]
	ours.sort(lambda a, b: cmp(b["landPlotsSeen"], a["landPlotsSeen"]))
	others.sort(lambda a, b: cmp(b["landPlotsSeen"], a["landPlotsSeen"]))
	# <!-- custom: The user's follow-up: how many landmasses, their typical size and the bonus mix.
	# Sizes are exact only for landmasses fully explored, so the mean and median count those alone. (Claude code Opus 5.5) -->
	exploredSizes = [a["landPlotsSeen"] for a in areas.values() if a["explored"]]
	exploredSizes.sort()
	landmasses = {"seen": len(areas), "fullyExplored": len(exploredSizes), "exploredMean": None, "exploredMedian": None}
	if exploredSizes:
		landmasses["exploredMean"] = sum(exploredSizes) / float(len(exploredSizes))
		# <!-- custom: The middle size, or the mean of the two middle ones: the first version took the upper one, so a Huge Pangaea's two explored landmasses of 3 and 1495 plots gave a median of 1495. (Claude code Opus 5.5) -->
		iMid = len(exploredSizes) / 2
		if len(exploredSizes) % 2:
			landmasses["exploredMedian"] = float(exploredSizes[iMid])
		else:
			landmasses["exploredMedian"] = (exploredSizes[iMid - 1] + exploredSizes[iMid]) / 2.0
	iBonusTotal = sum(bonuses.values())
	bonusMix = [{"bonus": szBonus, "plots": iCount, "percent": iCount * 100.0 / iBonusTotal} for szBonus, iCount in bonuses.items()]
	bonusMix.sort(lambda a, b: cmp(b["plots"], a["plots"]))
	rivals = []
	for iLoop in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(iLoop)
		if not loopPlayer.isAlive() or loopPlayer.getTeam() == iTeam or loopPlayer.isMinorCiv() or not team.isHasMet(loopPlayer.getTeam()):
			continue
		szName = loopPlayer.getName()
		bShares = False
		for a in ours:
			if a["owners"].has_key(szName) or a["citiesSeen"].has_key(szName):
				bShares = True
		rivals.append({"player": iLoop, "name": szName, "sharesOurLandmass": bShares, "openBorders": bool(team.isOpenBorders(loopPlayer.getTeam())), "atWar": bool(team.isAtWar(loopPlayer.getTeam()))})
	mapOptions = []
	for i in range(cyMap.getNumCustomMapOptions()):
		szDesc = cyMap.getNonDefaultCustomMapOptionDesc(i)
		if len(szDesc) > 0:
			mapOptions.append(szDesc)
	crossing = _seaCrossing(player, team, iTeam, cyMap, iOcean, areas)
	takeaways = []
	landRivals = [r["name"] for r in rivals if r["sharesOurLandmass"]]
	bOursExplored = len(ours) > 0
	iRoom = 0
	for a in ours:
		bOursExplored = bOursExplored and a["explored"]
		iRoom += a["unownedPlots"]
	if landRivals:
		takeaways.append("Land neighbours on our landmass: %s. A war can come over land; keep defenders where our borders meet." % ", ".join(landRivals))
	elif bOursExplored:
		takeaways.append("No met rival on our landmass, and all of it is seen: an invasion must come by sea, which needs transports and shows its ships first. Defend the coastal cities that face rivals and keep the army light; for the same reason a rival may not expect an army of ours.")
	else:
		takeaways.append("No met rival seen on our landmass yet, but it is not fully explored: explore before judging how safe it is.")
	# <!-- custom: Room only from a 3x3 block of unowned land up: the first run, at turn 120 of the SAS48 islands save, called a single unowned plot "room to settle". (Claude code Opus 5.5) -->
	# <!-- custom: Shared with rivals, unowned plots are mostly gaps between borders, not room: at turn 300 of a Huge Pangaea, 58 of them lay between 14 neighbours, which the first wording called room to settle before rivals arrive. (Claude code Opus 5.5) -->
	if iRoom >= 9 and not landRivals:
		takeaways.append("%d unowned land plots seen on our landmass: room to settle before rivals arrive." % iRoom)
	elif iRoom >= 9:
		takeaways.append("%d unowned land plots seen on our landmass, shared with rivals: mostly gaps between borders; 'sites' tells whether any is worth a city." % iRoom)
	elif ours:
		takeaways.append("Our landmass is nearly all ours (%d unowned plots seen): further growth means settling overseas or taking cities." % iRoom)
	iRivalsAlive = len([1 for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isAlive() and not gc.getPlayer(i).isMinorCiv() and gc.getPlayer(i).getTeam() != iTeam])
	# <!-- custom: The user's point (2026-11-15): contact is more than trade; the islands autoplay was far behind for lacking it.
	# With TECH_DIFFUSION_ENABLE off, as in SAS, CvPlayer::calculateResearchModifier adds TECH_COST_TOTAL_KNOWN_TEAM_MODIFIER times the met teams knowing a tech over all teams alive, met or not: there 30 x 2 / 48, at most 1.25% faster research on any tech, against up to 30% with every team met. (Claude code Opus 5.5) -->
	iTeamsAlive = len([1 for i in range(gc.getMAX_CIV_TEAMS()) if gc.getTeam(i).isAlive() and not gc.getTeam(i).isMinorCiv() and not gc.getTeam(i).isBarbarian()])
	iMetTeams = len([1 for i in range(gc.getMAX_CIV_TEAMS()) if i != iTeam and gc.getTeam(i).isAlive() and not gc.getTeam(i).isMinorCiv() and not gc.getTeam(i).isBarbarian() and team.isHasMet(i)])
	szContact = "We have seen %d%% of the map and met %d of %d rivals." % ((iLandSeen + iWaterSeen) * 100 / max(1, cyMap.numPlots()), len(rivals), iRivalsAlive)
	if not SASCurrentDefines.getInt("TECH_DIFFUSION_ENABLE"):
		iMax = SASCurrentDefines.getInt("TECH_COST_TOTAL_KNOWN_TEAM_MODIFIER")
		# <!-- custom: Our own team counts among the teams alive but never knows the tech it researches, so everyone met gives (teams alive - 1) / teams alive of the modifier: 28% of 30 with 15 teams, not the 30% the first wording said. (Claude code Opus 5.5) -->
		szContact += " Contact speeds research: each met team knowing a tech adds %d%% / %d teams alive to it, so ours tops out at %.2f%% against %.2f%% with everyone met; met teams also trade techs, open borders and resources." % (iMax, iTeamsAlive, iMax * iMetTeams / float(max(1, iTeamsAlive)), iMax * (iTeamsAlive - 1) / float(max(1, iTeamsAlive)))
	takeaways.append(szContact)
	overseas = [r["name"] for r in rivals if not r["sharesOurLandmass"] and not r["openBorders"] and not r["atWar"]]
	if overseas:
		# <!-- custom: CvTeam::isFreeTrade needs open borders for foreign trade routes, CvCity adds OVERSEAS_TRADE_MODIFIER to a route to another landmass, and CvUnit::canEnterTerritory keeps our units and ships out of their borders without open borders or war. (Claude code Opus 5.5) -->
		takeaways.append("No open borders with overseas rivals %s: open borders allow foreign trade routes, which to another landmass also earn the overseas bonus (%d%%), and let our ships and units enter their borders, to explore past them or reach further rivals." % (", ".join(overseas), SASCurrentDefines.getInt("OVERSEAS_TRADE_MODIFIER")))
	oceanShips = [s for s in crossing["ships"] if s["canEnterOcean"]]
	if others and not landRivals:
		if crossing["landmassesReachedAlongCoast"]:
			takeaways.append("%d other seen landmass(es) reached along coast without open ocean: ships that cannot enter ocean (Work Boats, early galleys) can get there." % len(crossing["landmassesReachedAlongCoast"]))
		else:
			takeaways.append("No other seen landmass reached along seen coast: open ocean, or water not yet seen, lies between.")
		if oceanShips:
			first = oceanShips[0]
			if first["techsMissing"] == 0:
				takeaways.append("%s can enter ocean and needs no new tech: build it to explore and meet rivals." % first["unit"])
			else:
				szTurns = "no research rate yet"
				if first["pathTurns"] is not None:
					szTurns = "about %d turns at the current rate" % first["pathTurns"]
				takeaways.append("The first ocean-going ship, %s, is %d techs away (%d beakers, %s): the way to explore past the ocean and meet the rivals there." % (first["unit"], first["techsMissing"], first["pathBeakers"], szTurns))
	if g.isNavalHeavyMapnameCached() and not g.isLandHeavyMapnameCached():
		takeaways.append("The AI reads this map as naval-heavy: it scraps land units first, pays more to upgrade them, and favours coastal city sites and naval targets.")
	elif g.isLandHeavyMapnameCached() and not g.isNavalHeavyMapnameCached():
		takeaways.append("The AI reads this map as land-heavy: it scraps naval units first and pays more to upgrade them.")
	# <!-- custom: The World Picker's preview of the script, which every player sees at setup, for an agent to look at (the user's suggestion): a sample of the script, not this game's map, but it shows the shape, rows of islands, snaky continents or islets.
	# Renders by map_preview_dds.py are listed too, as an image reader may not open DDS. (Claude code Opus 5.5) -->
	import BugPath
	szScript = cyMap.getMapScriptName()
	preview = {"dds": None, "png": []}
	szDds = os.path.join(BugPath.getModDir(), "Assets", "Art", "AdvCiv_SAS", "Maps", szScript, "FLAT_" + szScript + ".dds")
	if os.path.isfile(szDds):
		preview["dds"] = szDds
	szPngDir = os.path.join(BugPath.getModDir(), "LLM_Helpers", "outputs", "map_previews")
	if os.path.isdir(szPngDir):
		preview["png"] = [os.path.join(szPngDir, n) for n in os.listdir(szPngDir) if n.startswith("FLAT_" + szScript + "_") and n.endswith(".png")]
		preview["png"].sort()
	return {"seaCrossing": crossing, "landmasses": landmasses, "bonusesSeen": bonusMix, "preview": preview, "settings": {"mapScript": cyMap.getMapScriptName(), "mapDescription": _mapDescription(cyMap.getMapScriptName()), "mapOptionsAll": saspilot._mapOptionsAll(cyMap.getMapScriptName()), "coastLaneRows": saspilot._coastLaneRows(player), "worldSize": gc.getWorldInfo(cyMap.getWorldSize()).getType(), "grid": [cyMap.getGridWidth(), cyMap.getGridHeight()], "seaLevel": gc.getSeaLevelInfo(cyMap.getSeaLevel()).getType(), "mapOptions": mapOptions, "landHeavy": bool(g.isLandHeavyMapnameCached()), "navalHeavy": bool(g.isNavalHeavyMapnameCached())}, "seen": {"plots": iLandSeen + iWaterSeen, "ofMap": cyMap.numPlots(), "land": iLandSeen, "water": iWaterSeen, "ocean": iOceanSeen}, "ourLandmasses": ours, "otherLandmasses": others, "rivals": rivals, "takeaways": takeaways}


_HELP["shore"] = "A plot's relation to water, for choosing a city site on an island or a coast: coastal (a city there can build ships and harbours), fresh water, river, lake, how many adjacent plots are water and how many ocean, and for a Farm whether the plot is irrigated or can take irrigation now (fresh water or an irrigated neighbour). Only plots the team has revealed, as the map shows them. 'sites' (served by the DLL) does not give these. args: x, y, player."


def cmd_shore(args):
	# <!-- custom: At turn 0 of the islands replay (2026-11-15) the capital site was chosen between (98,25) and (99,25), and whether either could build boats took a 'py' snippet; on an island map that question comes at every founding, so it is a command (the user's rule: a snippet a later game would ask again). (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	iTeam = player.getTeam()
	plot = gc.getMap().plot(int(args["x"]), int(args["y"]))
	if plot is None or plot.isNone():
		raise ValueError("no plot at %s,%s" % (args["x"], args["y"]))
	if saspilot._fogTeam(args) >= 0 and not plot.isRevealed(iTeam, False):
		raise ValueError("plot %s,%s is not revealed to our team" % (args["x"], args["y"]))
	iOcean = getInfoTypeOrFail("TERRAIN_OCEAN")
	iWater = 0
	iOceanAdjacent = 0
	iUnknown = 0
	for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
		adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
		if adjacent is None or adjacent.isNone():
			continue
		if saspilot._fogTeam(args) >= 0 and not adjacent.isRevealed(iTeam, False):
			iUnknown += 1
			continue
		if adjacent.isWater():
			iWater += 1
			if adjacent.getTerrainType() == iOcean:
				iOceanAdjacent += 1
	# <!-- custom: At turn 61 of the islands replay, whether Farms at (100,27) and (95,25) would be watered took a 'py' snippet: (100,27) had fresh water, while the Rice at (95,25) had neither water nor an irrigated neighbour. (Claude code Opus 5.5) -->
	return {"x": plot.getX(), "y": plot.getY(), "water": bool(plot.isWater()), "coastal": bool(plot.isCoastalLand()), "freshWater": bool(plot.isFreshWater()), "river": bool(plot.isRiver()), "lake": bool(plot.isLake()), "adjacentWater": iWater, "adjacentOcean": iOceanAdjacent, "adjacentUnrevealed": iUnknown, "irrigated": bool(plot.isIrrigated()), "irrigationAvailable": bool(plot.isIrrigationAvailable(False))}


def _mapDescription(szScript):
	# <!-- custom: The map script's own description of its layout, as its menu entry shows it: at turn 75 of the islands replay (2026-11-15) SAS_Large_Facing_Islands said "rivals on the east and west sides, and a rival facing north or south", which told where to scout.
	# Some scripts return a text key, which is translated; a script that cannot be imported gives null. (Claude code Opus 5.5) -->
	try:
		szText = __import__(szScript).getDescription()
	except Exception:
		return None
	if szText and szText.startswith("TXT_KEY"):
		szText = CyTranslator().getText(szText, ())
	return szText


_HELP["resources"] ="Every resource the team knows of: plot, type, owner (-1 unclaimed), improvement, and each build that connects it with its tech and whether we have that tech; resources on our land first. Shows what a tech would open, e.g. Agriculture's Plantations. args: player."


def cmd_resources(args):
	# <!-- custom: The user's advice at turn 37 of the turn-0 game (2026-11-14), on seeing a Banana: check resources first.
	# A 'py' listing showed the Banana needs a Plantation, which SAS gives with Agriculture, as do five more resources nearby, so Agriculture moved ahead of Masonry; kept as a command, as that check belongs to every opening.
	# Under fog, the resources and owners the team has seen, as the map shows them. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	# <!-- custom: Codex's review: player= a rival would read that rival's revealed plots and techs under fog. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	saspilot._requireOwnTeamUnderFog(args, player, "the resource list")
	iTeam = player.getTeam()
	team = gc.getTeam(iTeam)
	bFog = saspilot._fogTeam(args) >= 0
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
		entry = {"x": plot.getX(), "y": plot.getY(), "bonus": gc.getBonusInfo(iBonus).getType(), "owner": iOwner, "improvement": saspilot._typeOrNone(gc.getImprovementInfo, iImprovement), "builds": connectors[iBonus]}
		# <!-- custom: Whether the resource reaches our network, for our own plots: at turn 90 of the turn-0 game the user saw the Banana by London still unconnected, as were the two Pigs, all improved but with no route from their plot to a city (2026-11-14).
		# The list showed the Plantation and nothing about the link, and the agent took improved for connected.
		# The resource bar shows a player this. (Claude code Opus 5.5) -->
		# <!-- custom: Whether this plot supplies the resource: its network carries it (isPlotGroupConnectedBonus) and the plot itself feeds it, by a city or an improvement that trades it.
		# The network test alone counts every source in the group, so an unimproved Cow beside a pastured one on the same roads read as connected (Codex's review, round 35). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		if iOwner == player.getID():
			bFeeds = plot.isCity() or (plot.getImprovementType() >= 0 and gc.getImprovementInfo(plot.getImprovementType()).isImprovementBonusTrade(iBonus))
			entry["connected"] = bool(bFeeds and plot.isPlotGroupConnectedBonus(player.getID(), iBonus))
		# <!-- custom: What the resource gives the empire and whether we have it already: at turn 71 of the islands replay (2026-11-15) the user pointed out that a Whale, new to us and +1 happiness, beat a second Clam, whose health we already had from other food; that took a 'py' call.
		# A second source of a resource adds only its plot's yields. (Claude code Opus 5.5) -->
		info = gc.getBonusInfo(iBonus)
		entry["happiness"] = info.getHappiness()
		entry["health"] = info.getHealth()
		entry["weHaveAvailable"] = player.getNumAvailableBonuses(iBonus)
		result.append(entry)
	result.sort(lambda a, b: cmp((a["owner"] != player.getID(), a["owner"] >= 0, a["bonus"]), (b["owner"] != player.getID(), b["owner"] >= 0, b["bonus"])))
	return {"resources": result}


_HELP["routes"] = "A text map of the player's land, row by row from the north, to see the route network as the window shows it at a glance: C city, # railroad, = road, . own land with no route, ~ own water, x another's land, space unowned; columns are x from 'x0', rows y from 'y1' down. Plus each city's connection to the capital. args: margin (plots around our land, default 1), player."


def cmd_routes(args):
	# <!-- custom: SASPilot gave plots one by one and no picture of the network: at turn 281 of the modern baseline (2026-11-14) the user spotted a marsh at (11,42) with no route between a railroad and two roads, which the agent had not noticed.
	# A row of characters per map row shows such a gap the way the map does. (Claude code Opus 5.5) -->
	player = gc.getPlayer(saspilot._playerId(args))
	iTeam = saspilot._fogTeam(args)
	# <!-- custom: Under fog, player= naming another team still drew the map's edges from all its plots and listed every city with its coordinates and capital connection, although the rows hid unrevealed tiles (Codex's review, 2026-11-14). Refuse it, as 'odds' does for foreign units. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	saspilot._requireOwnTeamUnderFog(args, player, "the route map")
	kMap = gc.getMap()
	iRail = getInfoTypeOrFail("ROUTE_RAILROAD")
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
