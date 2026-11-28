# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotCities: running a city as a player does: reading it ('cities', 'city'), what it builds ('buildable', 'trainable', 'produce', 'dequeue', 'hurry') and who works where ('citizens', 'work', 'specialist', 'emphasize').
# Split from SASPilotCommands.py on 2026-11-28, the third part moved out by topic; grouped by concept rather than by the game's screens, as the user asked, so production and citizens share one module as a player manages both from the city.
# The helpers other commands share, such as _city and _cityBrief, stay there and are reached as saspilot.
# SASPilotCommands.py loads it from beside itself, again whenever it changes, and adds its commands and help. (Claude code Opus 5.5) -->

from CvPythonExtensions import *
# <!-- custom: getInfoTypeOrFail finds the unit types 'trainable' lists; the first move left it out, as the name came from SASPilotCommands' own from-import, and 'trainable' raised NameError in game (2026-11-28). (Claude code Opus 5.5) -->
from SASUtils import getInfoTypeOrFail

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}


# <!-- custom: While a Settler or Worker (bFood) is built, foodDifference reads 0 because K-Mod's CvCity::foodDifference caps it there, yet the surplus goes into production.
# At turn 18 of the Continents game (2026-11-19) that 0 led to trading a food for a hammer during the Worker, which changed nothing; the user pointed out that food is production then. (Claude code Opus 5.5) -->
def _foodProduction(city):
	bFoodProduction = city.isFoodProduction()
	result = {"foodProduction": bFoodProduction}
	if bFoodProduction:
		result["foodSurplusToProduction"] = max(0, city.getYieldRate(YieldTypes.YIELD_FOOD) - city.foodConsumption(False, 0))
	return result


def _cityFull(city):
	result = saspilot._cityBrief(city)
	iOwner = city.getOwner()
	result["food"] = city.getFood()
	result["growthThreshold"] = city.growthThreshold()
	result["foodDifference"] = city.foodDifference(True)
	result.update(_foodProduction(city))
	result["production"] = city.getProduction()
	# <!-- custom: With an empty queue the game returns MAX_INT, which came back as 2147483647 (fog-on playthrough, 2026-11-13); give null instead, as nothing is being produced. (Claude code Opus 5.5) -->
	result["productionNeeded"] = None
	if city.getOrderQueueLength() > 0:
		result["productionNeeded"] = city.getProductionNeeded()
	result["yieldRate"] = saspilot._yields(city.getYieldRate)
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
	# <!-- custom: What else the city screen shows: its trade routes with each partner and the commerce it brings, the defense bonus and its bombard damage, and Great People progress.
	# The user asked at turn 141 of the turn-0 game (2026-11-14) whether SASPilot has the city screen's details; trade routes in particular need explored land and contact (a world map widens them), and 'city' had none of these. (Claude code Opus 5.5) -->
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
	# <!-- custom: Units, buildings and projects first came as bare lists of types; the city screen shows each with its turns, which decide most choices (fog-on playthrough, 2026-11-13).
	# They are now type -> turns at the current production. (Claude code Opus 5.5) -->
	units = dict([(gc.getUnitInfo(i).getType(), city.getUnitProductionTurnsLeft(i, 0)) for i in range(gc.getNumUnitInfos()) if city.canTrain(i, False, False)])
	buildings = dict([(gc.getBuildingInfo(i).getType(), city.getBuildingProductionTurnsLeft(i, 0)) for i in range(gc.getNumBuildingInfos()) if city.canConstruct(i, False, False, False)])
	projects = dict([(gc.getProjectInfo(i).getType(), city.getProjectProductionTurnsLeft(i, 0)) for i in range(gc.getNumProjectInfos()) if city.canCreate(i, False, False)])
	processes = [gc.getProcessInfo(i).getType() for i in range(gc.getNumProcessInfos()) if city.canMaintain(i, False)]
	hurries = [gc.getHurryInfo(i).getType() for i in range(gc.getNumHurryInfos()) if city.canHurry(i, False)]
	return {"units": units, "buildings": buildings, "projects": projects, "processes": processes, "hurries": hurries}


def _cityAsSeen(city):
	# <!-- custom: What the map shows of a rival's city; its build queue, food and the like are on its city screen, which a player cannot open. (Claude code Fable 5.2) -->
	return {"id": city.getID(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "owner": city.getOwner(), "population": city.getPopulation()}


_HELP["cities"] = "A player's cities, briefly. args: player."


def cmd_cities(args):
	player = saspilot._player(args)
	iTeam = saspilot._fogTeam(args)
	if iTeam >= 0 and player.getTeam() != iTeam:
		# <!-- custom: With fog on, a rival's cities are the ones the active team has revealed, with what the map shows of them. (Claude code Fable 5.2) -->
		return [{"id": city.getID(), "name": city.getName(), "x": city.getX(), "y": city.getY(), "owner": city.getOwner()} for city in saspilot._cities(player) if city.isRevealed(iTeam, False)]
	return [saspilot._cityBrief(city) for city in saspilot._cities(player)]


_HELP["city"] = "One city in full, with what it can produce now. args: city (ID or name), player."


def cmd_city(args):
	city = saspilot._city(args)
	iTeam = saspilot._fogTeam(args)
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


_HELP["buildable"] = "The buildings a city can build now, as its build menu offers them: each with its cost, the hammers already in it and the turns at the current rate; 'trainable' is the same for units. args: city, player."


def cmd_buildable(args):
	# <!-- custom: At the founding of The Hague at turn 57 of the islands replay (2026-11-15), choosing its first build took a 'py' call for the buildings it could make; every new city asks it again. (Claude code Opus 5.5) -->
	city = saspilot._city(args)
	player = gc.getPlayer(city.getOwner())
	result = []
	for i in range(gc.getNumBuildingInfos()):
		if not city.canConstruct(i, False, False, False):
			continue
		# <!-- custom: With what the building gives a city where it counts most often: happiness, health and culture, as at turn 81 of the islands replay (2026-11-15) Utrecht reached its happiness limit and choosing a building to lift it took the XML.
		# CyCity.getBuildingHappiness and getBuildingHealth give the amount in this city. (Claude code Opus 5.5) -->
		info = gc.getBuildingInfo(i)
		# <!-- custom: movesCapital flags a Palace, as its hover says it moves the capital: at turn 306 of the ASOKA Huge save (2026-11-22) a happiness-first pick queued Brandenburg's Palace, as it gives happiness and every build there took 1 turn. (Claude code Opus 5.5) -->
		row = {"building": info.getType(), "cost": player.getBuildingProductionNeeded(i), "stored": city.getBuildingProduction(i), "turns": city.getBuildingProductionTurnsLeft(i, 0), "happiness": city.getBuildingHappiness(i), "health": city.getBuildingHealth(i), "culture": info.getObsoleteSafeCommerceChange(CommerceTypes.COMMERCE_CULTURE)}
		if info.isCapital():
			row["movesCapital"] = True
		result.append(row)
	result.sort(lambda a, b: cmp(a["turns"], b["turns"]))
	return {"city": city.getName(), "buildings": result}


_HELP["trainable"] = "The units a city can train now, for choosing value per hammer: each with its turns, cost, strength, moves, strength per 100 hammers (strengthPer100Hammers, integer), and what strength alone does not show: first strikes and their chance, collateral damage and how many units it reaches, withdrawal chance, bombard rate, city attack and defense bonuses, and bonuses against unit types (versus, in percent). Military units first, sorted by strength per 100 hammers, which misleads for siege: cityAttackPer100Hammers (with the city attack bonus), combatLimit (a siege unit cannot kill) and the effects weigh as much. args: city, player."


def cmd_trainable(args):
	# <!-- custom: The user advised at turn 100 of the turn-0 game (2026-11-14) weighing units by strength against cost, as an Axeman for 35 hammers is strong early, and by the effects strength leaves out, as a Trebuchet's strength is low but it bombards and harms several defenders.
	# 'city' gave the trainable units with their turns only.
	# These are the XML's facts, as the city screen's hover shows them; which to build stays the agent's choice. (Claude code Opus 5.5) -->
	city = saspilot._city(args)
	player = gc.getPlayer(city.getOwner())
	result = []
	for i in range(gc.getNumUnitInfos()):
		if not city.canTrain(i, False, False):
			continue
		info = gc.getUnitInfo(i)
		iCost = player.getUnitProductionNeeded(i)
		entry = {"unit": info.getType(), "turns": city.getUnitProductionTurnsLeft(i, 0), "cost": iCost, "strength": info.getCombat(), "moves": info.getMoves(), "combatType": saspilot._typeOrNone(gc.getUnitCombatInfo, info.getUnitCombatType())}
		if iCost > 0:
			entry["strengthPer100Hammers"] = info.getCombat() * 10000 / iCost
		# <!-- custom: Whether huts give this unit no bad result, such as Barbarians: in the Continents replay (2026-11-19) an Archer was built as filler while Dublin grew, and the user pointed out that a Scout costs 15 hammers instead of 25, has 2 moves instead of 1 and is safe at huts, which a hut-hunting opening needs. (Claude code Opus 5.5) -->
		if info.isNoBadGoodies():
			entry["noBadGoodies"] = True
		for (szKey, iValue) in (("firstStrikes", info.getFirstStrikes()), ("chanceFirstStrikes", info.getChanceFirstStrikes()), ("collateralDamage", info.getCollateralDamage()), ("collateralMaxUnits", info.getCollateralDamageMaxUnits()), ("withdrawalPct", info.getWithdrawalProbability()), ("bombardRate", info.getBombardRate()), ("cityAttackPct", info.getCityAttackModifier()), ("cityDefensePct", info.getCityDefenseModifier())):
			if iValue:
				entry[szKey] = iValue
		# <!-- custom: The user's follow-up: strength per hammer misleads for siege, as a Trebuchet (4 strength, about 80 hammers) has +100% city attack, collateral damage and bombard, yet defends badly unlike a Catapult.
		# So, beside the plain ratio, the strength against a city per 100 hammers for units with a city attack bonus, and the combat limit (a siege unit stops at that damage and cannot kill), with cityDefensePct shown when negative too. (Claude code Opus 5.5) -->
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
		info = gc.getUnitInfo(getInfoTypeOrFail(entry["unit"]))
		if info.getAirCombat() > 0:
			entry["airStrength"] = info.getAirCombat()
			if entry["cost"] > 0:
				entry["airStrengthPer100Hammers"] = info.getAirCombat() * 10000 / entry["cost"]
	result.sort(lambda a, b: cmp((a["strength"] <= 0 and not a.get("airStrength"), -a.get("strengthPer100Hammers", 0)), (b["strength"] <= 0 and not b.get("airStrength"), -b.get("strengthPer100Hammers", 0))))
	return {"city": city.getName(), "units": result}


_HELP["produce"] = "Put an item in a city's build queue: a UNIT_, BUILDING_, PROJECT_ or PROCESS_ type. By default it replaces the queue; append=1 adds at the end, first=1 puts it first and keeps the rest. args: city, item, append, first, player."


def cmd_produce(args):
	city = saspilot._city(args)
	szItem = args["item"]
	iItem = saspilot._infoIndex(szItem)
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
		# <!-- custom: At turn 71 of the fog-on playthrough (2026-11-13) Carthage could not train a Settler and the error said no more; the window shows such an item greyed with its hover text, which held the reason, "National Unit: 0 Left", as the Settler on its way still counted.
		# Give that text when the item is shown in the window at all. (Claude code Opus 5.5) -->
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
			raise ValueError("%s cannot produce %s now; the window's hover text: %s" % (city.getName(), szItem, saspilot._plainText(szHelp).replace(u"\n", u" | ")))
		# <!-- custom: An item the window does not list at all has no hover text: Kerkouane's Archer at turn 129 of the fog-on playthrough (2026-11-13) was refused with no more said, as the Longbowman had made it obsolete. (Claude code Opus 5.5) -->
		raise ValueError("%s cannot produce %s now: the window does not offer it, for instance obsolete or missing its tech or resource; 'city' lists what it offers" % (city.getName(), szItem))
	bAppend = bool(args.get("append", False))
	# <!-- custom: Putting a Galley ahead of a half-built Library at turn 105 of the fog-on playthrough (2026-11-13) meant replacing the queue or appending; first=1 inserts at the front and keeps the rest, as the city screen's ctrl-click does. CyCity.pushOrder with bAppend false inserts at position 0. (Claude code Opus 5.5) -->
	bFirst = bool(args.get("first", False))
	if not bAppend and not bFirst:
		city.clearOrderQueue()
	city.pushOrder(eOrder, iItem, -1, False, False, bAppend, False)
	return saspilot._cityBrief(city)


_HELP["dequeue"] = "Remove one item from a city's build queue, as clicking it in the city screen's queue does; production put into it stays with the city as for any change. index is its place in the queue as 'city' lists it (0 is what is being built now). args: city, index, player."


def cmd_dequeue(args):
	# <!-- custom: The city screen removes any queued item with a click, while 'produce' could only replace the queue, append or put first, so dropping one item meant rebuilding the rest (2026-11-14).
	# CyCity.popOrder with bFinish and bChoose off is what that click does. (Claude code Opus 5.5) -->
	city = saspilot._city(args)
	iIndex = int(args["index"])
	if iIndex < 0 or iIndex >= city.getOrderQueueLength():
		raise ValueError("%s has no queue item %d; its queue: %s" % (city.getName(), iIndex, saspilot._cityBrief(city)["queue"]))
	city.popOrder(iIndex, False, False)
	return saspilot._cityBrief(city)


_HELP["hurry"] = "Hurry a city's production. Without hurry, lists each HURRY_ type with whether the city can use it now and its gold and population cost, as the window's buttons show. args: city, hurry (HURRY_ type), player."


def cmd_hurry(args):
	city = saspilot._city(args)
	# <!-- custom: 'hurry city=Gondar' without a type raised a bare KeyError while looking for a way to rush a Trireme (2026-11-13, turn 154); like 'freetech' and 'research', it now lists the choices instead. (Claude code Opus 5.5) -->
	if args.get("hurry") is None:
		# <!-- custom: maxHurryPopulation, the most citizens a whip may take (half the city in CvCity::maxHurryPopulation): in the scouting trial (2026-11-14) a size-3 Constantinople read can=false for a 2-citizen whip with no reason given, and the DLL's canHurry showed the cap. (Claude code Opus 5.5) -->
		result = {"city": city.getName(), "gold": gc.getPlayer(city.getOwner()).getGold(), "population": city.getPopulation(), "maxHurryPopulation": city.maxHurryPopulation(), "hurries": [{"hurry": gc.getHurryInfo(i).getType(), "can": bool(city.canHurry(i, False)), "goldCost": city.hurryGold(i), "populationCost": city.hurryPopulation(i)} for i in range(gc.getNumHurryInfos())]}
		# <!-- custom: What a whip trades: at turn 38 of the 2026-11-19 validation run 1 citizen (a 24-food bar to regrow) saved about 3 turns of a food-production Settler, which the user called a last resort at that stage.
		# Hammers it would add and turns saved, against the food bar a citizen costs. (Claude code Opus 5.5) -->
		if city.getOrderQueueLength() > 0:
			iLeft = city.getProductionNeeded() - city.getProduction()
			iRate = max(1, city.getCurrentProductionDifference(False, True))
			result["whipTrade"] = {"hammersLeft": iLeft, "turnsSaved": (iLeft + iRate - 1) / iRate - 1, "foodToRegrowOneCitizen": city.growthThreshold(), "note": "worth it when the turns saved matter (a contested site, a defender in time) or the city is at its happy or health cap; otherwise growing is usually better"}
		return result
	iHurry = saspilot._typedIndex(args["hurry"], "HURRY_", gc.getNumHurryInfos(), gc.getHurryInfo)
	if not city.canHurry(iHurry, False):
		raise ValueError("%s cannot hurry with %s now" % (city.getName(), args["hurry"]))
	city.hurry(iHurry)
	return saspilot._cityBrief(city)


def _cityPlots(city):
	plots = []
	for i in range(gc.getNUM_CITY_PLOTS()):
		plot = city.getCityIndexPlot(i)
		if plot is None or plot.isNone():
			continue
		entry = {"index": i, "x": plot.getX(), "y": plot.getY(), "worked": city.isWorkingPlot(plot), "canWork": city.canWork(plot), "yields": saspilot._yields(plot.getYield)}
		# <!-- custom: Match the city UI's known ownership, competing city and work requirements.
		# A visible enemy can make a tile unsafe, but canWork also tests siege and blockades, so a generic enemy on the tile alone does not explain a refusal. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if not entry["canWork"] and i != gc.getCITY_HOME_PLOT():
			iTeam = gc.getPlayer(city.getOwner()).getTeam()
			if not plot.isRevealed(iTeam, False):
				entry["why"] = "not revealed"
			else:
				iOwner = plot.getRevealedOwner(iTeam, False)
				if iOwner != city.getOwner():
					entry["why"] = iOwner < 0 and "unowned" or "owned by player %d" % iOwner
				elif plot.isVisible(iTeam, False):
					working = plot.getWorkingCity()
					if working is not None and not working.isNone() and working.getOwner() == city.getOwner() and working.getID() != city.getID():
						entry["why"] = "assigned to %s" % working.getName()
						entry["workedBy"] = working.getID()
					elif plot.isWater() and not gc.getTeam(iTeam).isWaterWork():
						entry["why"] = "water work is not unlocked"
					elif not plot.hasYield():
						entry["why"] = "yields nothing"
		plots.append(entry)
	return plots


def _citizens(city):
	result = {"city": city.getName(), "population": city.getPopulation(), "angry": city.angryPopulation(0), "automated": city.isCitizensAutomated(), "foodDifference": city.foodDifference(True), "yieldRate": saspilot._yields(city.getYieldRate)}
	result.update(_foodProduction(city))
	result["plots"] = _cityPlots(city)
	# <!-- custom: A citizen neither on a plot nor a specialist, as the city that lost the Sheep to 'work' had in the islands replay (2026-11-15) until its governor reassigned it; a click in that moment made it a specialist instead of working the plot clicked. (Claude code Opus 5.5) -->
	result["unassigned"] = city.getPopulation() - city.getWorkingPopulation() - city.getSpecialistPopulation()
	specialists = {}
	for i in range(gc.getNumSpecialistInfos()):
		iCount = city.getSpecialistCount(i)
		iMax = city.getMaxSpecialistCount(i)
		if iCount > 0 or iMax > 0 or city.isSpecialistValid(i, 1):
			specialists[gc.getSpecialistInfo(i).getType()] = {"count": iCount, "max": iMax, "forced": city.getForceSpecialistCount(i), "canAdd": city.isSpecialistValid(i, 1), "free": city.getFreeSpecialistCount(i)}
	result["specialists"] = specialists
	result["emphasize"] = [gc.getEmphasizeInfo(i).getType() for i in range(gc.getNumEmphasizeInfos()) if city.AI_isEmphasize(i)]
	swaps = _tileSwaps(city, result["plots"])
	if swaps is not None:
		result["swaps"] = swaps
	return result


# <!-- custom: What each single swap of a worked plot for a free one does to the current build and to growth, so a trade such as stalling growth for a faster build is computed rather than played out.
# At turn 0 of the Continents replay (2026-11-19) the user had Dublin work a 0/3/0 forested hill instead of a 1/2/0 hill: growth stalled, and the Fish's Work Boat came out on turn 7 instead of 9; the user then asked for the calculation in the API.
# Production uses the city's own modifier; food counts as production while a Settler or Worker is built.
# Plots with yields shown as they are now. (Claude code Opus 5.5) -->
SWAPS_SHOWN = 6


SWAPS_SHOWN_GROWTH = 3


def _tileSwaps(city, plots):
	if city.getOrderQueueLength() == 0:
		return None
	iNeeded = city.getProductionNeeded() - city.getProduction()
	iBaseHammers = city.getBaseYieldRate(YieldTypes.YIELD_PRODUCTION)
	iModifier = city.getBaseYieldRateModifier(YieldTypes.YIELD_PRODUCTION, 0)
	iFood = city.getYieldRate(YieldTypes.YIELD_FOOD)
	iEat = city.foodConsumption(False, 0)
	iGrowthLeft = city.growthThreshold() - city.getFood()
	bFoodProduction = city.isFoodProduction()

	def outcome(iHammers, iFoodNow):
		iSurplus = iFoodNow - iEat
		iRate = iHammers * iModifier / 100 + (bFoodProduction and max(0, iSurplus) or 0)
		entry = {"turns": iRate > 0 and (iNeeded + iRate - 1) / iRate or None, "foodSurplus": iSurplus}
		entry["growsIn"] = (not bFoodProduction and iSurplus > 0) and (iGrowthLeft + iSurplus - 1) / iSurplus or None
		return entry

	result = {"build": str(saspilot._orderData(city.getOrderFromQueue(0))), "now": outcome(iBaseHammers, iFood), "swaps": []}
	worked = [p for p in plots if p["worked"] and (p["x"], p["y"]) != (city.getX(), city.getY())]
	free = [p for p in plots if not p["worked"] and p["canWork"]]
	for w in worked:
		for f in free:
			entry = outcome(iBaseHammers - w["yields"][1] + f["yields"][1], iFood - w["yields"][0] + f["yields"][0])
			entry["free"] = [w["x"], w["y"]]
			entry["work"] = [f["x"], f["y"]]
			result["swaps"].append(entry)
	result["swaps"].sort(key=lambda e: (e["turns"] is None, e["turns"], -e["foodSurplus"]))
	# <!-- custom: Fastest builds alone hid the improved Fish at turn 9 of the 2026-11-19 validation run (+5 food, 0 hammers), so the most food is listed too. (Claude code Opus 5.5) -->
	byBuild = result["swaps"][:SWAPS_SHOWN]
	byFood = [e for e in sorted(result["swaps"], key=lambda e: -e["foodSurplus"]) if e not in byBuild][:SWAPS_SHOWN_GROWTH]
	result["swaps"] = byBuild
	result["growthSwaps"] = byFood
	return result


_HELP["citizens"] = "A city's screen: each plot in its radius with whether it is worked and can be, its specialists with their limits, whether the governor assigns citizens, and its emphasis buttons. While it builds something, swaps gives the build's turns, food surplus and turns to grow now and after each single swap of a worked plot for a free one, fastest build first, so a trade such as stalling growth for a faster build is computed. With automated=1 or 0, switch the governor first. args: city, automated, player."


def cmd_citizens(args):
	# <!-- custom: The city screen's controls go through CvCity::doTask, as its buttons do, so the governor reacts as it would for a person: a hand-picked plot is kept as an override, and freed citizens are reassigned. (Claude code Fable 5.2) -->
	city = saspilot._city(args)
	if args.get("automated") is not None:
		city.doTask(TaskTypes.TASK_SET_AUTOMATED_CITIZENS, -1, -1, bool(args["automated"]))
	return _citizens(city)


_HELP["work"] = "Click a plot in a city's radius, as on the city screen: a worked plot is freed, a free one is worked (taking a citizen from elsewhere), the city's own plot switches the governor back on, and a plot of the player's that another city works is claimed for this city (claimOnly then says to click again in a new request to work it, as the game applies the click after the reply); that city's screen then comes as claimedFrom, as its freed citizen stays unassigned until its governor runs (click a plot for it, or wait for the turn). args: city, x, y, player."


def cmd_work(args):
	city = saspilot._city(args)
	plot = saspilot._plot(args)
	iIndex = city.getCityPlotIndex(plot)
	if iIndex < 0 or iIndex >= gc.getNUM_CITY_PLOTS():
		raise ValueError("%d,%d is outside %s's radius" % (plot.getX(), plot.getY(), city.getName()))
	# <!-- custom: Every click is TASK_CHANGE_WORKING_PLOT, as on the city screen, whose handler CvCity::alterWorkingPlot switches the governor back on for the city's own plot and, for a plot the city cannot work but owns, claims it from the city working it.
	# The first version sent TASK_CLEAR_WORKING_OVERRIDE for the city's own plot and refused plots the city could not work; Codex's review pointed out the difference. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	# <!-- custom: When the click claims a plot another city works, that city is shown too, as its freed citizen waits unassigned until its governor runs (islands replay, 2026-11-15).
	# Only another city of the same player, and only when the claim took the plot from it: for a rival's city the game refuses the claim, and returning its screen anyway would show a rival's specialists and yields (Codex's review). (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	other = None
	if plot.isBeingWorked() and plot.getWorkingCity() and plot.getWorkingCity().getID() != city.getID() and plot.getWorkingCity().getOwner() == city.getOwner():
		other = plot.getWorkingCity()
	# <!-- custom: A click on a plot the city cannot work (another of our cities holds it) only claims it, and the citizen it moves may land in a specialist slot: at turn 74 of the islands replay (2026-11-15) The Hague claimed the Rice and worked neither it nor its Horses.
	# A second click works it, but in a later request: doTask sends a game message applied after this request returns, so a second click sent here saw the old state and never fired.
	# The reply says claimOnly so the agent clicks again. (Claude code Opus 5.5) -->
	bClaim = not city.canWork(plot) and plot.getOwner() == city.getOwner() and iIndex != 0
	city.doTask(TaskTypes.TASK_CHANGE_WORKING_PLOT, iIndex, -1, False)
	result = _citizens(city)
	if bClaim:
		result["claimOnly"] = "the click claimed %d,%d for %s; click again in a new request to work it" % (plot.getX(), plot.getY(), city.getName())
	if other is not None and not other.isWorkingPlot(plot):
		result["claimedFrom"] = _citizens(other)
	return result


_HELP["specialist"] = "Add or remove a city's specialists, as the plus and minus buttons do. args: city, type (SPECIALIST_ type), change (default 1; negative removes), player."


def cmd_specialist(args):
	city = saspilot._city(args)
	iSpecialist = saspilot._typedIndex(args["type"], "SPECIALIST_", gc.getNumSpecialistInfos(), gc.getSpecialistInfo)
	iChange = int(args.get("change", 1))
	if iChange > 0 and not city.isSpecialistValid(iSpecialist, iChange):
		raise ValueError("%s cannot take %d more %s" % (city.getName(), iChange, args["type"]))
	if iChange < 0 and city.getSpecialistCount(iSpecialist) < -iChange:
		raise ValueError("%s has only %d %s" % (city.getName(), city.getSpecialistCount(iSpecialist), args["type"]))
	city.doTask(TaskTypes.TASK_CHANGE_SPECIALIST, iSpecialist, iChange, False)
	return _citizens(city)


_HELP["emphasize"] = "Switch one of a city's emphasis buttons, such as EMPHASIZE_FOOD or EMPHASIZE_AVOID_GROWTH. args: city, type (EMPHASIZE_ type), on (default 1), player."


def cmd_emphasize(args):
	city = saspilot._city(args)
	city.doTask(TaskTypes.TASK_SET_EMPHASIZE, saspilot._typedIndex(args["type"], "EMPHASIZE_", gc.getNumEmphasizeInfos(), gc.getEmphasizeInfo), -1, bool(args.get("on", True)))
	return _citizens(city)
