# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotExpansion: where to look and where to settle: exploration ('directions' around a city, 'scout' steps and frontiers for a land unit, 'seareach' for a ship) and expansion ('sites' a selected Settler circles, 'plansites' planned ahead).
# Split from SASPilotCommands.py on 2026-11-28, the sixth part moved out by concept; Codex (GPT-6.2-Sol) grouped exploration and expansion apart, and they share one module here as the two are small (under 400 lines together) and both answer where the empire grows next, which keeps the file count down, the user's caution against many small files.
# The map helpers they share, such as _coastLaneRows and _revealedLandmass, stay in SASPilotCommands.py and are reached as saspilot.; 'advise', '_remindHomeUnknown' and '_remindSitesChanged' there call these commands through _command. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

from CvPythonExtensions import *

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}
def _seaReach(unit, iCandidates):
	# <!-- custom: For each direction from the ship (by the larger of its east-west and north-south offsets, the seam of a wrapping map counted), the nearest revealed water plots that border unrevealed ones, and whether the ship can reach them and in how many turns, by the pathfinder 'path' uses (fog respected: our own unit, default flags).
	# iCandidates plots per direction are tried, nearest first. (Claude code Opus 5.5) -->
	player = gc.getPlayer(unit.getOwner())
	iTeam = player.getTeam()
	kMap = gc.getMap()
	iWidth = kMap.getGridWidth()
	iHeight = kMap.getGridHeight()
	bWrapX = kMap.isWrapX()
	bWrapY = kMap.isWrapY()
	frontier = {"north": [], "south": [], "east": [], "west": []}
	lanes = saspilot._coastLaneRows(player)
	infoUnit = gc.getUnitInfo(unit.getUnitType())
	for i in range(kMap.numPlots()):
		plot = kMap.plotByIndex(i)
		if not plot.isWater() or not plot.isRevealed(iTeam, False):
			continue
		# <!-- custom: Only water the ship may enter: the first version tried the nearest edges east of a Work Boat, which were open ocean, and called a direction unreachable that a path of 5 turns reached. (Claude code Opus 5.5) -->
		if infoUnit.getTerrainImpassable(plot.getTerrainType()):
			continue
		bEdge = False
		for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
			adjacent = plotDirection(plot.getX(), plot.getY(), DirectionTypes(iDirection))
			if adjacent is not None and not adjacent.isNone() and not adjacent.isRevealed(iTeam, False):
				bEdge = True
				break
		if not bEdge:
			continue
		dx = plot.getX() - unit.getX()
		dy = plot.getY() - unit.getY()
		if bWrapX:
			dx = (dx + iWidth / 2) % iWidth - iWidth / 2
		if bWrapY:
			dy = (dy + iHeight / 2) % iHeight - iHeight / 2
		if abs(dx) >= abs(dy):
			szWay = (dx >= 0 and "east") or "west"
		else:
			szWay = (dy > 0 and "north") or "south"
		# <!-- custom: On a map with known coast lanes, unknown coast on a lane row comes first, nearest first within each group. (Claude code Opus 5.5) -->
		frontier[szWay].append((lanes and plot.getY() not in lanes, max(abs(dx), abs(dy)), plot.getX(), plot.getY()))
	result = {}
	for (szWay, plots) in frontier.items():
		plots.sort()
		row = {"frontierPlots": len(plots), "reachable": None}
		for (bOffLane, iDistance, x, y) in plots[:iCandidates]:
			path = saspilot.fromJson(saspilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), x, y, 0))
			if path and path.get("found"):
				row["reachable"] = {"x": x, "y": y, "turns": path.get("turns")}
				# <!-- custom: Near the edge of a map that does not wrap north-south: at turn 78 of the islands replay (2026-11-15) the boat went round Suleiman's island by the north, where the ice cap and the map's edge end the way, as on our own island; the user pointed out it should have gone south.
				# Weighed as 5 turns: with 3 it tied the 4-turn way south and lost on the direction's name. (Claude code Opus 5.5) -->
				if not bWrapY and (y >= iHeight - 4 or y <= 3):
					row["reachable"]["nearMapEdge"] = True
				# <!-- custom: Beyond the lane rows on the side of the nearer map edge: the edge test alone still sent the boat to (130,27), the first step of the way north round Suleiman's island, as row 27 is not yet near the edge.
				# Our row's lanes (24 to 26) lie near the north edge, so leaving them northward heads for the ice. (Claude code Opus 5.5) -->
				if lanes and not bWrapY:
					bNorthEdge = (iHeight - 1 - lanes[1]) < lanes[1]
					if (bNorthEdge and y > lanes[-1]) or (not bNorthEdge and y < lanes[0]):
						row["reachable"]["towardMapEdge"] = True
				if lanes:
					row["reachable"]["onLane"] = not bOffLane
				# <!-- custom: Whether that coast lies in a met rival's waters, by its revealed owner: at turn 68 of the islands replay (2026-11-15) the user called the Work Boat's tour of Greece's north shore needless once Pericles was known, and asked that scouting hunt unexplored coast first. (Claude code Opus 5.5) -->
				iOwner = kMap.plot(x, y).getRevealedOwner(iTeam, False)
				if iOwner >= 0 and gc.getPlayer(iOwner).getTeam() != iTeam and gc.getTeam(iTeam).isHasMet(gc.getPlayer(iOwner).getTeam()):
					row["reachable"]["metRivalWaters"] = gc.getPlayer(iOwner).getName()
				break
		if plots and row["reachable"] is None:
			# <!-- custom: "No known route", not "ocean": the pathfinder plans only through revealed plots, so at turn 75 of the islands replay the agent read a failed path west as ocean and claimed the west reachable only round the world, while SAS_Large_Facing_Islands links east-west neighbours by coast lanes (its "E-W Coast Bands" option; see mapOptionsAll in 'geography').
			# The user caught it. (Claude code Opus 5.5) -->
			row["note"] = "no route through revealed plots reaches the %d nearest unknown coast plot(s) here; unrevealed water may still connect (see the map options in 'geography')" % min(len(plots), iCandidates)
		result[szWay] = row
	return result


_HELP["seareach"] = "Where a ship can still explore: for each direction from it (north, south, east, west), how many seen water plots border the unknown there and the nearest one it can reach with its turns, or that no route through revealed plots reaches the nearest (unrevealed water may still connect; 'geography' gives the map script's options, such as coast lanes). For choosing a direction nobody has scouted rather than coasts already known: a reachable coast in a met rival's waters is marked (metRivalWaters), and recommend picks the nearest reachable unknown coast by turns: crossing a rival's waters toward the unknown is fine, touring its known shore is not. args: unit, candidates (plots tried per direction, default 4), player."


def cmd_seareach(args):
	# <!-- custom: At turn 75 of the islands replay (2026-11-15) both Work Boats explored automatically into the waters of Greece, already met, while the map script puts rivals east, west and facing north or south; the user pointed out that unknown directions teach more, and that a ship deep in a rival's borders depends on open borders.
	# Working out which unknown coast each boat could reach took five 'path' calls: south was ocean, west 213 turns round the world, east past Greece 5 turns. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	if unit.getDomainType() != DomainTypes.DOMAIN_SEA:
		raise ValueError("unit %d is not a ship" % unit.getID())
	if saspilot._fogTeam(args) >= 0 and unit.getTeam() != saspilot._fogTeam(args):
		raise ValueError("with fog on, 'seareach' takes the team's own ships")
	directions = _seaReach(unit, int(args.get("candidates", 4)))
	# <!-- custom: The direction to take: the nearest reachable unknown coast, by turns.
	# A first version ranked a met rival's waters last, which sent a Work Boat at turn 71 of the islands replay 5 turns back west over known water while the only way east, toward the unmet, ran along Greek coast 2 turns away; the user called it the same mistake again.
	# Touring a known rival's shore is what to avoid, not crossing its waters toward the unknown, so the mark stays as information only. (Claude code Opus 5.5) -->
	# <!-- custom: Lanes weigh as 3 turns, not as an absolute first: at turn 77 of the islands replay (2026-11-15) the boat reached the end of the lane at Suleiman's island, and the strict lane-first rule sent it 10 turns back west along the known lane instead of 1 turn round his coast toward the next lane. (Claude code Opus 5.5) -->
	options = [(row["reachable"]["turns"] + (row["reachable"].get("onLane", True) and 0 or 3) + (row["reachable"].get("nearMapEdge") and 5 or 0) + (row["reachable"].get("towardMapEdge") and 4 or 0), szWay) for (szWay, row) in directions.items() if row["reachable"]]
	options.sort()
	recommend = None
	if options:
		szWay = options[0][1]
		recommend = {"direction": szWay, "x": directions[szWay]["reachable"]["x"], "y": directions[szWay]["reachable"]["y"], "turns": directions[szWay]["reachable"]["turns"]}
	return {"unit": unit.getID(), "x": unit.getX(), "y": unit.getY(), "laneRows": saspilot._coastLaneRows(gc.getPlayer(unit.getOwner())), "directions": directions, "recommend": recommend}


DIRECTION_NAMES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _sectorName(dx, dy):
	# <!-- custom: 2.414 is tan(67.5 degrees): within 22.5 degrees of an axis counts as that axis. (Claude code Opus 5.5) -->
	if abs(dx) * 100 > abs(dy) * 241:
		return dx > 0 and "E" or "W"
	if abs(dy) * 100 > abs(dx) * 241:
		return dy > 0 and "N" or "S"
	return (dy > 0 and "N" or "S") + (dx > 0 and "E" or "W")


_HELP["directions"] = "What we know in each of 8 compass sectors around a city (the capital by default) within radius plots (12 by default), to pick where scouting or the next cities pay: known land and water, good land (natural food plus production at least 2), poor land (tundra, desert, peaks and such), fresh-water land, revealed resources, plots rivals own, and the unknown edge (unrevealed plots next to known land, where more land may lie). value is a rough sort: good land, resources twice, fresh water and the unknown edge half, poor land minus half; rival plots are left out of it, as a contested side can be the urgent one. North is +y. args: city, radius, player."


def cmd_directions(args):
	# <!-- custom: The user's idea at turn 24 of the 2026-11-19 validation run: the Warrior had walked into the south-east, tundra and plains of little value, which the known map already showed; a per-direction summary lets scouting go where the land promises more. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	iTeam = saspilot._fogTeam(args)
	if iTeam < 0:
		iTeam = player.getTeam()
	if args.get("city") is not None:
		center = saspilot._city(args)
	else:
		center = player.getCapitalCity()
		if center is None or center.isNone():
			raise ValueError("no capital: give city=")
	iRadius = int(args.get("radius", 12))
	if iRadius < 3 or iRadius > 25:
		raise ValueError("radius must be between 3 and 25")
	sectors = {}
	for name in DIRECTION_NAMES:
		sectors[name] = {"direction": name, "knownLand": 0, "water": 0, "goodLand": 0, "poorLand": 0, "freshWaterLand": 0, "resources": [], "rivalPlots": 0, "unknownEdge": 0}
	for dy in range(-iRadius, iRadius + 1):
		for dx in range(-iRadius, iRadius + 1):
			if dx == 0 and dy == 0:
				continue
			plot = plotXY(center.getX(), center.getY(), dx, dy)
			if plot is None or plot.isNone():
				continue
			entry = sectors[_sectorName(dx, dy)]
			if not plot.isRevealed(iTeam, False):
				for ndy in (-1, 0, 1):
					for ndx in (-1, 0, 1):
						near = plotXY(plot.getX(), plot.getY(), ndx, ndy)
						if near is not None and not near.isNone() and near.isRevealed(iTeam, False) and not near.isWater():
							entry["unknownEdge"] += 1
							break
					else:
						continue
					break
				continue
			if plot.getOwner() >= 0 and plot.getTeam() != player.getTeam():
				entry["rivalPlots"] += 1
			iBonus = plot.getBonusType(iTeam)
			if iBonus >= 0:
				entry["resources"].append("%s@%d,%d" % (gc.getBonusInfo(iBonus).getType(), plot.getX(), plot.getY()))
			if plot.isWater():
				entry["water"] += 1
				continue
			entry["knownLand"] += 1
			iFoodProd = plot.calculateNatureYield(YieldTypes.YIELD_FOOD, TeamTypes(iTeam), False) + plot.calculateNatureYield(YieldTypes.YIELD_PRODUCTION, TeamTypes(iTeam), False)
			if iFoodProd >= 2:
				entry["goodLand"] += 1
			elif iBonus < 0:
				entry["poorLand"] += 1
			if plot.isFreshWater():
				entry["freshWaterLand"] += 1
	result = []
	for name in DIRECTION_NAMES:
		entry = sectors[name]
		entry["value"] = entry["goodLand"] + 2 * len(entry["resources"]) + (entry["freshWaterLand"] + entry["unknownEdge"]) / 2 - entry["poorLand"] / 2
		result.append(entry)
	result.sort(key=lambda e: -e["value"])
	return {"city": center.getName(), "x": center.getX(), "y": center.getY(), "radius": iRadius, "sectors": result}


def _nearestOwnCityDistance(iPlayer, iX, iY):
	player = gc.getPlayer(iPlayer)
	best = None
	(city, it) = player.firstCity(False)
	while city:
		iDistance = max(abs(city.getX() - iX), abs(city.getY() - iY))
		if best is None or iDistance < best:
			best = iDistance
		(city, it) = player.nextCity(it, False)
	return best


# <!-- custom: Far targets 'scout' gives, the nearest known land bordering the unknown. (Claude code Opus 5.5) -->
SCOUT_FRONTIER_TARGETS = 6


_HELP["scout"] ="Where a scout could step next: each plot next to the unit it can enter now, with how many unknown plots it would reveal (seeing one plot around, two from hills), its defense bonus, and the animals and barbarians we see within two plots of it, in a fixed order (north-west first, row by row). Also the unit's damage, and frontiers: the nearest known land of our landmass bordering the unknown, by distance from the unit, with how many unknown plots touch each and its direction, as far targets when the steps around reveal little, and frontierSectors: per direction from the unit, how many frontier plots lie there and the nearest, most first, to show where most of the unknown is. Facts only: 'advise about=scout' ranks the steps. args: unit, player."


def cmd_scout(args):
	# <!-- custom: Automated exploring lost a Warrior at turn 35 of the turn-0 game (2026-11-14): it beat a Lion at 22% attacker odds, kept exploring at 15 HP and a Panther killed it, as automation neither heals nor avoids animals.
	# The user's advice: scout by hand, avoid animals unless the odds are great (they are strong in SAS and give little), end on hills or forest.
	# So this lays out each next step with what it reveals and how safe it is, from what the team knows only, and leaves the choice to the agent. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	# <!-- custom: Codex's review: under fog, a rival's unit would show what that rival sees. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	saspilot._requireOwnTeamUnderFog(args, gc.getPlayer(unit.getOwner()), "scouting")
	iTeam = unit.getTeam()
	kMap = gc.getMap()
	iHereDistance = _nearestOwnCityDistance(unit.getOwner(), unit.getX(), unit.getY())
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
			step = {"x": plot.getX(), "y": plot.getY(), "reveals": iReveal, "defense": plot.defenseModifier(iTeam, False, False), "hills": plot.isHills(), "feature": saspilot._typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), "enemiesNear": near}
			# <!-- custom: Each step's distance from our nearest city and whether it goes outward, sideways or back toward it: at turn 10 of the Continents replay (2026-11-19) the user weighed a hill revealing 9 but one plot back toward Dublin against forests revealing 2 outward, and asked for it beside the reveal. (Claude code Opus 5.5) -->
			iCityDistance = _nearestOwnCityDistance(unit.getOwner(), plot.getX(), plot.getY())
			if iCityDistance is not None and iHereDistance is not None:
				step["fromOurCity"] = iCityDistance
				step["direction"] = iCityDistance > iHereDistance and "outward" or iCityDistance < iHereDistance and "back" or "sideways"
			steps.append(step)
	# <!-- custom: The ranking (most revealed, then fewest enemies near, then the best defense) moved to 'advise about=scout', as a judgment of ours: the user's facts-versus-advice split (2026-11-14). The steps keep the loop's order, so the same position gives the same list. (Claude code Opus 5.5) -->
	# <!-- custom: At turn 60 of the 2026-11-19 validation run every step next to the Scout revealed 0 to 2 plots, so it drifted back toward home, while land to the north and the interior north of Persia were still unknown; the user asked whether the landmass was done.
	# So the nearest known land of our landmass bordering the unknown is given too, by distance from the unit, as far targets. (Claude code Opus 5.5) -->
	frontiers = []
	for (fx, fy) in saspilot._revealedLandmass(gc.getPlayer(unit.getOwner())).keys():
		iUnknownNear = 0
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				near = kMap.plot(fx + dx, fy + dy)
				if (dx or dy) and not near.isNone() and not near.isRevealed(iTeam, False):
					iUnknownNear += 1
		if iUnknownNear > 0:
			frontiers.append((plotDistance(unit.getX(), unit.getY(), fx, fy), -iUnknownNear, fx, fy))
	frontiers.sort()
	targets = [{"x": fx, "y": fy, "distance": iDistance, "unknownNear": -iNegUnknown, "direction": _sectorName(fx - unit.getX(), fy - unit.getY())} for (iDistance, iNegUnknown, fx, fy) in frontiers[:SCOUT_FRONTIER_TARGETS]]
	# <!-- custom: Nearest-first showed only 1-plot pockets near the Scout at turn 64, while the large unknown areas north and east lay farther; per direction, how many frontier plots lie there and the nearest one shows where most of the unknown is. (Claude code Opus 5.5) -->
	sectors = {}
	for (iDistance, iNegUnknown, fx, fy) in frontiers:
		szSector = _sectorName(fx - unit.getX(), fy - unit.getY())
		if not sectors.has_key(szSector):
			sectors[szSector] = {"direction": szSector, "plots": 0, "nearest": {"x": fx, "y": fy, "distance": iDistance}}
		sectors[szSector]["plots"] += 1
	bySector = sectors.values()
	bySector.sort(lambda a, b: cmp(b["plots"], a["plots"]))
	return {"unit": unit.getID(), "x": unit.getX(), "y": unit.getY(), "damage": unit.getDamage(), "movesLeft": unit.movesLeft(), "steps": steps, "frontiers": targets, "frontierSectors": bySector}


_HELP["sites"] = "The city sites the window circles when this Settler is selected: the player's recommended sites it reaches within 7 turns, best first, each with its plot, found value, rank in the player's list and path turns. args: unit, player."


def cmd_sites(args):
	# <!-- custom: At the first Settler of the fog-on playthrough (2026-11-13) SASPilot had plots and yields but not the green circles BtS draws for a selected Settler; this reads the same list in C++, as Python cannot reach it. (Claude code Opus 5.5) -->
	unit = saspilot._unit(args)
	text = saspilot._pilotGame("getSASPilotCitySitesJson").getSASPilotCitySitesJson(unit.getOwner(), unit.getID())
	# <!-- custom: sas-ci-string-compare-exemption: The DLL bridge returns the JSON null sentinel as text. (GPT-6.2-Sol) -->
	if text == "null":
		raise ValueError("unit %d cannot found a city" % unit.getID())
	return saspilot.RawJson(text)


# <!-- custom: Plots a rival city may be farther from a site than our nearest city for the site to count as contested. (Claude code Opus 5.5) -->
SITE_CONTEST_MARGIN = 2


# <!-- custom: Plots from our nearest city within which a new city can be held: units reach it in a few turns. (Claude code Opus 5.5) -->
SITE_HOLD_DISTANCE = 6


# <!-- custom: Plots from our nearest government center beyond which an uncontested site waits until the ring around the capital is filled. (Claude code Opus 5.5) -->
SITE_RADIAL_DISTANCE = 8


# <!-- custom: Food at SITE_FOOD_SIZE at or under which a site is marked as poor in food. (Claude code Opus 5.5) -->
SITE_POOR_FOOD = 2


# <!-- custom: Unknown radius plots from which a site is to be scouted before it is judged. (Claude code Opus 5.5) -->
SITE_SCOUT_UNKNOWN = 4


_HELP["plansites"] = "Plan city sites ahead, as a player does before a Settler exists: each revealed plot of our landmasses where the player could found a city, rated by the AI's found value (CvPlayerAI::AI_foundValue), with whether it is coastal (sea, not lake), the revealed food bonuses and open coast in its radius, and how many of its plots our cities already reach. Best first; spread=N (default 3) keeps only sites at least N plots from each other and from our cities, as a plan. legal=1 also keeps sites the AI values at 0 (it gives 0 near our cities), ranked then by open coast and fewest shared plots, for planning a tight coastal fill: the AI's value is a reference, not the answer, as it follows general rules (on an isolated island, coast claimed by corner cities can outweigh the overlap it avoids). 'mark' puts a chosen one on the dot map. Each site also gives its distance to our nearest government center (toGovCenter) and our nearest city, the nearest seen rival city, whether it is nearer than ours and whether the site is contested (a rival city at most 2 plots farther than ours), withinReach (within 6 plots of our nearest city), foodAtSize6 (the centre's and best tiles' natural food less what 6 citizens eat) and priority: scout first (4+ radius plots unknown), skip (food 0 or less), first (contested and within reach), dart only (contested beyond reach: it needs defenders and a reason), later (uncontested and more than 8 plots from our government center: radial growth fills the ring around the capital first) or can wait (uncontested and near), the happiness resources in its radius (happyBonuses), each plot it shares with our cities with its yields and bonus (sharedPlots; strong with a bonus or 4+ total yield, counted in sharedStrong), and its radius plots still unknown (unknownPlots); upkeepReference gives the distance upkeep our cities pay now at their distances. How to weigh them: weigh more than value: a close site keeps upkeep low and the empire compact and defensible; avoid sharing strong plots (a bonus, or 4+ total yield) when another site shares fewer; a site nearer a rival city than ours is hard to hold early; grow radially: settle contested sites within 6 plots of our cities first (a rival city at most 2 plots farther than ours), as uncontested ones can wait while scouting finds better and a contested site out of reach is built for the rival to take, unless a dart with defenders claims a chokepoint or the map edge; unknownPlots counts radius plots still in fog, so scout those before settling. args: limit (default 8), spread, legal, player."


def cmd_plansites(args):
	# <!-- custom: At turn 57 of the islands replay (2026-11-15) the user asked for our city sites marked early, as a strong player plans them, but 'sites' reads the green circles of a selected Settler and refused without one. (Claude code Opus 5.5) -->
	player = saspilot._player(args)
	iTeam = player.getTeam()
	kMap = gc.getMap()
	iLimit = int(args.get("limit", 8))
	iSpread = int(args.get("spread", 3))
	# <!-- custom: legal=1 keeps sites the AI values at 0: AI_foundValue gives 0 to sites close to our cities, so with the user's plan for the island (claim coast by settling its corners, overlap accepted) only one site came back; sorted then by open coast and fewest shared plots. (Claude code Opus 5.5) -->
	bLegal = bool(args.get("legal"))
	ourCities = saspilot._cities(player)
	cityPlots = [(city.getX(), city.getY()) for city in ourCities]
	# <!-- custom: The 2026-11-19 validation run ranked sites by their own value only, and the agent leaned toward a Crab site 11 plots from the capital and a Corn site past Persia; the user: weigh empire shape, distance to the capital or government center, and avoid sharing strong plots where a site with less overlap exists.
	# So each site also gives its distance to our nearest government center (distance upkeep grows with it; 'upkeepReference' gives what our cities pay now at their distances), the nearest seen rival city (a site nearer a rival than to us is hard to hold), each plot it shares with our cities with its yields, and the plots of its radius still unknown (a site at the fog's edge may be better or worse than its value says). (Claude code Opus 5.5) -->
	govCenters = [(city.getX(), city.getY()) for city in ourCities if city.isGovernmentCenter()]
	rivalCities = []
	for i in range(gc.getMAX_PLAYERS()):
		rival = gc.getPlayer(i)
		if i == player.getID() or not rival.isAlive() or gc.getPlayer(i).getTeam() == iTeam:
			continue
		for city in saspilot._cities(rival):
			if city.plot().isRevealed(iTeam, False):
				rivalCities.append((city.getX(), city.getY(), city.getName()))
	# <!-- custom: Our landmass by revealed connection, not the game's area IDs, which would tell whether explored patches connect through fog (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	rated = []
	for (x, y) in saspilot._revealedLandmass(player).keys():
		plot = kMap.plot(x, y)
		if not player.canFound(x, y):
			continue
		iValue = player.AI_foundValue(plot.getX(), plot.getY(), -1, False)
		if iValue <= 0 and not bLegal:
			continue
		food = []
		iCoast = 0
		iShared = 0
		iUnknown = 0
		shared = []
		foods = []
		happy = []
		for j in range(gc.getNUM_CITY_PLOTS()):
			other = plotCity(plot.getX(), plot.getY(), j)
			if other is None or other.isNone():
				continue
			if not other.isRevealed(iTeam, False):
				iUnknown += 1
				continue
			if j > 0:
				foods.append(other.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes(iTeam)))
			iBonus = other.getBonusType(iTeam)
			if iBonus >= 0 and gc.getBonusInfo(iBonus).getYieldChange(YieldTypes.YIELD_FOOD) > 0:
				food.append(gc.getBonusInfo(iBonus).getType())
			# <!-- custom: 'limits' showed the Gold at 20,14, +1 happiness while happiness bound first, inside site 20,12's radius, which only foodBonuses had not named (2026-11-19 validation run). (Claude code Opus 5.5) -->
			if iBonus >= 0 and gc.getBonusInfo(iBonus).getHappiness() > 0:
				happy.append(gc.getBonusInfo(iBonus).getType())
			if other.isWater() and not other.isLake() and not other.isImpassable():
				iCoast += 1
			for (cx, cy) in cityPlots:
				if max(abs(other.getX() - cx), abs(other.getY() - cy)) <= 2 and plotDistance(other.getX(), other.getY(), cx, cy) <= 2:
					iShared += 1
					yields = [other.getYield(YieldTypes(k)) for k in range(YieldTypes.NUM_YIELD_TYPES)]
					shared.append({"x": other.getX(), "y": other.getY(), "yields": yields, "bonus": saspilot._typeOrNone(gc.getBonusInfo, iBonus), "strong": bool(iBonus >= 0 or sum(yields) >= saspilot.SHARED_STRONG_YIELD)})
					break
		site = {"x": plot.getX(), "y": plot.getY(), "value": iValue, "coastal": bool(plot.isCoastalLand()), "foodBonuses": food, "happyBonuses": happy, "openCoast": iCoast, "sharedWithOurCities": iShared, "sharedPlots": shared, "sharedStrong": len([1 for row in shared if row["strong"]]), "unknownPlots": iUnknown}
		if govCenters:
			site["toGovCenter"] = min([plotDistance(x, y, gx, gy) for (gx, gy) in govCenters])
		if cityPlots:
			site["toOurNearestCity"] = min([plotDistance(x, y, cx, cy) for (cx, cy) in cityPlots])
		if rivalCities:
			(iRival, szRival) = min([(plotDistance(x, y, rx, ry), name) for (rx, ry, name) in rivalCities])
			site["nearestRivalCity"] = {"name": szRival, "distance": iRival}
			site["nearerRivalThanUs"] = bool(cityPlots and iRival < site["toOurNearestCity"])
			# <!-- custom: The user, same turn: the east was low value and uncontested, so no rush, while the north-west needed scouting; a contested site is settled first, an uncontested one can wait for scouting.
			# Contested when a rival city is at most SITE_CONTEST_MARGIN plots farther than our nearest city. (Claude code Opus 5.5) -->
			site["contested"] = bool(not cityPlots or iRival <= site["toOurNearestCity"] + SITE_CONTEST_MARGIN)
		# <!-- custom: The user, next: 24,22 read as contested, yet it lay 9 plots from our nearest city and nearer Pasargadae, so we could not defend it and would build and improve it for Persia to take.
		# Growth is usually radial; a dart ahead (a chokepoint, the map's edge) goes only with defenders.
		# So priority: "first" for a contested site within SITE_HOLD_DISTANCE of our nearest city, "dart only" for a contested one beyond it, "can wait" for an uncontested one. (Claude code Opus 5.5) -->
		bHoldable = bool(not cityPlots or site["toOurNearestCity"] <= SITE_HOLD_DISTANCE)
		site["withinReach"] = bHoldable
		# <!-- custom: The user, next: the plains around 28,19 had very low food and no bonus, so no city there would grow, nor bridge to our land short of taking Pasargadae; marking it was pointless.
		# calculateBestNatureYield takes a TeamTypes, not a plain int: the first version raised a Boost ArgumentError.
		# Food at size SITE_FOOD_SIZE: the centre's and the best tiles' natural food (revealed bonuses included, improvements and the city tile's own bonus not) less what the citizens eat; at 0 or less the site gets priority "skip". (Claude code Opus 5.5) -->
		foods.sort()
		foods.reverse()
		iFood = plot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes(iTeam)) + sum(foods[:saspilot.SITE_FOOD_SIZE]) - saspilot.SITE_FOOD_SIZE * gc.getFOOD_CONSUMPTION_PER_POPULATION()
		site["foodAtSize%d" % saspilot.SITE_FOOD_SIZE] = iFood
		# <!-- custom: The food check first called the sites west and east of Dublin (14,10 and 26,8) skip, though 8 of their radius plots were unknown; the user: exploring near the capital comes first.
		# With SITE_SCOUT_UNKNOWN unknown plots or more, the site is judged after scouting. (Claude code Opus 5.5) -->
		if iUnknown >= SITE_SCOUT_UNKNOWN:
			site["priority"] = "scout first: %d radius plots unknown" % iUnknown
		elif iFood <= 0:
			site["priority"] = "skip: its tiles cannot feed a city of %d" % saspilot.SITE_FOOD_SIZE
		elif site.get("contested"):
			site["priority"] = (bHoldable and "first") or "dart only"
		# <!-- custom: The user, turn 80: unless exceptionally good, grow radially from the capital; the east, far and unimpressive, waits.
		# An uncontested site beyond SITE_RADIAL_DISTANCE of our nearest government center reads "later" rather than "can wait". (Claude code Opus 5.5) -->
		elif site.get("toGovCenter") is not None and site["toGovCenter"] > SITE_RADIAL_DISTANCE:
			site["priority"] = "later"
		else:
			site["priority"] = "can wait"
		# <!-- custom: The user, turn 80: the west's plains and tundra were low on food, 13,11 at +1 at size 6; a site this weak is marked, not skipped, as a coastal or whip city can still use it. (Claude code Opus 5.5) -->
		if iFood > 0 and iFood <= SITE_POOR_FOOD and not site["priority"].startswith("scout") and not site["priority"].startswith("skip"):
			site["priority"] += " (poor food)"
		rated.append(site)
	rated.sort(lambda a, b: cmp((b["value"], b["openCoast"], -b["sharedWithOurCities"]), (a["value"], a["openCoast"], -a["sharedWithOurCities"])))
	plan = []
	for site in rated:
		if iSpread > 0 and [1 for (x, y) in cityPlots + [(s["x"], s["y"]) for s in plan] if plotDistance(site["x"], site["y"], x, y) < iSpread]:
			continue
		plan.append(site)
		if len(plan) >= iLimit:
			break
	upkeep = []
	for city in ourCities:
		row = {"city": city.getName(), "distanceUpkeepX100": city.calculateDistanceMaintenanceTimes100()}
		if govCenters:
			row["toGovCenter"] = min([plotDistance(city.getX(), city.getY(), gx, gy) for (gx, gy) in govCenters])
		upkeep.append(row)
	# <!-- custom: The reasoning for weighing these fields is in the help text, not each reply: the user found the same advice line repeated in every reply (2026-11-19). (Claude code Opus 5.5) -->
	return {"spread": iSpread, "sites": plan, "upkeepReference": upkeep}
