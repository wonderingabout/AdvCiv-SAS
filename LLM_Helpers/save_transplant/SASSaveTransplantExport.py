# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Runs inside Civ4 (Python 2.4), in any build old or new: sas_save_transplanter.py copies it into a source build's Assets/Python and hooks CvEventInterface.onEvent, so the build that wrote a save also reads it and writes its world out as text.
# It uses only the stock BtS Python API and the build's own CvWBDesc, as a 4986 build has no SASPilot, SASGameRecord or SASUtils. (Claude code Fable 5.2) -->

# <!-- custom: CvPythonExtensions is the game API; CvWBDesc is the build's own WorldBuilder writer; os and traceback write the result files. SASSaveTransplantRequest is generated beside this file by sas_save_transplanter.py and holds the output path. (Claude code Fable 5.2) -->
from CvPythonExtensions import *
import os
import traceback

gc = CyGlobalContext()

_bDone = False


def _quote(value):
	szOut = u'"'
	for ch in unicode(value):
		iCode = ord(ch)
		if ch == u'"' or ch == u"\\":
			szOut += u"\\" + ch
		elif iCode < 32 or iCode > 126:
			szOut += u"\\u%04x" % iCode
		else:
			szOut += ch
	return szOut + u'"'


# <!-- custom: Python 2.4 has no json module. (Claude code Fable 5.2) -->
def toJson(value):
	if value is None:
		return u"null"
	if value is True:
		return u"true"
	if value is False:
		return u"false"
	if isinstance(value, (int, long)):
		return unicode(value)
	if isinstance(value, float):
		return unicode(repr(value))
	if isinstance(value, (str, unicode)):
		if isinstance(value, str):
			value = value.decode("latin-1")
		return _quote(value)
	if isinstance(value, (list, tuple)):
		return u"[" + u",".join([toJson(item) for item in value]) + u"]"
	if isinstance(value, dict):
		keys = value.keys()
		keys.sort()
		return u"{" + u",".join([_quote(key) + u":" + toJson(value[key]) for key in keys]) + u"}"
	return _quote(repr(value))


def _typeOrNone(getInfo, iType):
	if iType < 0:
		return None
	return getInfo(iType).getType()


def _attempt(facts, key, function):
	# <!-- custom: Old builds lack some calls, so one missing call costs one fact, named under "missing", not the export. (Claude code Fable 5.2) -->
	try:
		facts[key] = function()
	except Exception, error:
		facts.setdefault("missing", {})[key] = str(error)


def _gameFacts():
	game = gc.getGame()
	cyMap = CyMap()
	facts = {}
	_attempt(facts, "gameTurn", game.getGameTurn)
	_attempt(facts, "gameYear", game.getGameTurnYear)
	_attempt(facts, "startYear", game.getStartYear)
	_attempt(facts, "maxTurns", game.getMaxTurns)
	_attempt(facts, "activePlayer", game.getActivePlayer)
	_attempt(facts, "handicap", lambda: _typeOrNone(gc.getHandicapInfo, game.getHandicapType()))
	_attempt(facts, "gameSpeed", lambda: _typeOrNone(gc.getGameSpeedInfo, game.getGameSpeedType()))
	_attempt(facts, "startEra", lambda: _typeOrNone(gc.getEraInfo, game.getStartEra()))
	_attempt(facts, "calendar", lambda: _typeOrNone(gc.getCalendarInfo, game.getCalendar()))
	_attempt(facts, "mapScript", cyMap.getMapScriptName)
	_attempt(facts, "worldSize", lambda: _typeOrNone(gc.getWorldInfo, cyMap.getWorldSize()))
	_attempt(facts, "climate", lambda: _typeOrNone(gc.getClimateInfo, cyMap.getClimate()))
	_attempt(facts, "seaLevel", lambda: _typeOrNone(gc.getSeaLevelInfo, cyMap.getSeaLevel()))
	_attempt(facts, "gridWidth", cyMap.getGridWidth)
	_attempt(facts, "gridHeight", cyMap.getGridHeight)
	_attempt(facts, "wrapX", lambda: bool(cyMap.isWrapX()))
	_attempt(facts, "wrapY", lambda: bool(cyMap.isWrapY()))
	_attempt(facts, "landPlots", cyMap.getLandPlots)
	_attempt(facts, "numAreas", cyMap.getNumAreas)
	_attempt(facts, "gameOptions", lambda: [gc.getGameOptionInfo(i).getType() for i in range(gc.getNumGameOptionInfos()) if game.isOption(i)])
	_attempt(facts, "victories", lambda: [gc.getVictoryInfo(i).getType() for i in range(gc.getNumVictoryInfos()) if game.isVictoryValid(i)])
	# <!-- custom: The two generators' current states: WorldBuilder text holds no seed, so a scenario start draws new ones. sas_save_transplanter.py can set these in the receiving game, which then draws the numbers the source game would have drawn next. (Claude code Fable 5.2) -->
	_attempt(facts, "syncRandSeed", lambda: game.getSorenRand().getSeed())
	_attempt(facts, "mapRandSeed", lambda: game.getMapRand().getSeed())
	_attempt(facts, "maxCivPlayers", gc.getMAX_CIV_PLAYERS)
	_attempt(facts, "countCivPlayersAlive", game.countCivPlayersAlive)
	_attempt(facts, "numCities", game.getNumCities)
	# <!-- custom: How many XML types the build has per kind: a first sign of how far two builds' rules are apart. (Claude code Fable 5.2) -->
	counts = {}
	for szName in ("Terrain", "Feature", "Bonus", "Improvement", "Route", "Unit", "Building", "Tech", "Civic", "Civilization", "LeaderHead", "Promotion", "Handicap", "GameSpeed", "World", "GameOption", "Religion", "Corporation", "Specialist", "Trait"):
		try:
			counts[szName] = getattr(gc, "getNum%sInfos" % szName)()
		except Exception:
			pass
	facts["xmlTypeCounts"] = counts
	# <!-- custom: Every bonus and feature type this build's XML has, so that the receiving build can tell a type the old build did not have (Marsh, Peat) from one the old world merely has none of. (Claude code Fable 5.2) -->
	_attempt(facts, "bonusTypes", lambda: [gc.getBonusInfo(i).getType() for i in range(gc.getNumBonusInfos())])
	_attempt(facts, "featureTypes", lambda: [gc.getFeatureInfo(i).getType() for i in range(gc.getNumFeatureInfos())])
	# <!-- custom: The other kinds of plot content, which the receiving build never adds: a new terrain, improvement or route has no rule saying which existing plots should change, so the transplanter only reports such types. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	_attempt(facts, "terrainTypes", lambda: [gc.getTerrainInfo(i).getType() for i in range(gc.getNumTerrainInfos())])
	_attempt(facts, "improvementTypes", lambda: [gc.getImprovementInfo(i).getType() for i in range(gc.getNumImprovementInfos())])
	_attempt(facts, "routeTypes", lambda: [gc.getRouteInfo(i).getType() for i in range(gc.getNumRouteInfos())])
	return facts


def _playerFacts(iPlayer, bProbeFreePromotions):
	player = gc.getPlayer(iPlayer)
	facts = {"id": iPlayer}
	_attempt(facts, "team", player.getTeam)
	_attempt(facts, "alive", lambda: bool(player.isAlive()))
	_attempt(facts, "human", lambda: bool(player.isHuman()))
	_attempt(facts, "name", player.getName)
	_attempt(facts, "civilization", lambda: _typeOrNone(gc.getCivilizationInfo, player.getCivilizationType()))
	_attempt(facts, "leader", lambda: _typeOrNone(gc.getLeaderHeadInfo, player.getLeaderType()))
	_attempt(facts, "handicap", lambda: _typeOrNone(gc.getHandicapInfo, player.getHandicapType()))
	_attempt(facts, "gold", player.getGold)
	_attempt(facts, "numCities", player.getNumCities)
	_attempt(facts, "numUnits", player.getNumUnits)
	_attempt(facts, "score", lambda: gc.getGame().getPlayerScore(iPlayer))

	def startingPlot():
		plot = player.getStartingPlot()
		if plot is None or plot.isNone():
			return None
		return [plot.getX(), plot.getY()]
	_attempt(facts, "startingPlot", startingPlot)
	_attempt(facts, "traits", lambda: [gc.getTraitInfo(i).getType() for i in range(gc.getNumTraitInfos()) if player.hasTrait(i)])
	_attempt(facts, "techs", lambda: [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if gc.getTeam(player.getTeam()).isHasTech(i)])
	# <!-- custom: The civilization's free techs under this build's XML: a scenario start adds the loading build's free techs to those in the file, so the 4986 Benin (Mysticism, Fishing) became Mysticism, Fishing, Pottery in current SAS, neither build's start.
	# With both builds' lists, sas_save_transplanter.py can drop the old ones first. (Claude code Fable 5.2) -->
	_attempt(facts, "civFreeTechs", lambda: [gc.getTechInfo(i).getType() for i in range(gc.getNumTechInfos()) if gc.getCivilizationInfo(player.getCivilizationType()).isCivilizationFreeTechs(i)])
	_attempt(facts, "civics", lambda: [_typeOrNone(gc.getCivicInfo, player.getCivics(i)) for i in range(gc.getNumCivicOptionInfos())])

	def units():
		rows = []
		(unit, iterator) = player.firstUnit(False)
		while unit:
			rows.append([unit.getX(), unit.getY(), gc.getUnitInfo(unit.getUnitType()).getType(), unit.getLevel(), unit.getExperience(), unit.getDamage(), [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if unit.isHasPromotion(i)]])
			(unit, iterator) = player.nextUnit(iterator, False)
		rows.sort()
		return rows
	_attempt(facts, "units", units)

	# <!-- custom: The promotions this build gives each of the player's unit types for free, from the unit itself and from the leader's traits. As with civFreeTechs, a scenario start adds the loading build's on top of the file's: a 4986 world's Archers gained City Garrison I in current SAS, their leader now being Protective, and a unit could likewise keep a promotion from a trait its leader has lost. (Claude code Fable 5.2) -->
	def freePromotionsByUnit():
		# <!-- custom: Found by creating one unit of each type and reading what it starts with, then removing it: the first version read the XML, but Python has no call for which unit combats a trait's free promotion applies to (CvTraitInfo has isFreePromotion only), so it failed in both builds.
		# Only where the game is thrown away afterwards, as a new unit takes an ID and a random birthmark. (Claude code Fable 5.2) -->
		result = {}
		seen = []
		(unit, iterator) = player.firstUnit(False)
		while unit:
			if unit.getUnitType() not in seen:
				seen.append(unit.getUnitType())
				probe = player.initUnit(unit.getUnitType(), unit.getX(), unit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
				result[gc.getUnitInfo(unit.getUnitType()).getType()] = [gc.getPromotionInfo(i).getType() for i in range(gc.getNumPromotionInfos()) if probe.isHasPromotion(i)]
				probe.kill(False, -1)
			(unit, iterator) = player.nextUnit(iterator, False)
		return result
	if bProbeFreePromotions:
		_attempt(facts, "freePromotionsByUnit", freePromotionsByUnit)
	return facts


def _plotFacts():
	# <!-- custom: One row per plot in a fixed column order, named in "plotColumns": names keep the 13,000 rows of a Huge map readable by a script without repeating 12 keys in each. (Claude code Fable 5.2) -->
	cyMap = CyMap()
	rows = []
	for iX in range(cyMap.getGridWidth()):
		for iY in range(cyMap.getGridHeight()):
			plot = cyMap.plot(iX, iY)
			area = plot.area()
			rows.append([iX, iY, int(plot.getPlotType()), _typeOrNone(gc.getTerrainInfo, plot.getTerrainType()), _typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), _typeOrNone(gc.getBonusInfo, plot.getBonusType(-1)), _typeOrNone(gc.getImprovementInfo, plot.getImprovementType()), _typeOrNone(gc.getRouteInfo, plot.getRouteType()), plot.getYield(YieldTypes.YIELD_FOOD), plot.getYield(YieldTypes.YIELD_PRODUCTION), plot.getYield(YieldTypes.YIELD_COMMERCE), int(bool(plot.isRiver())), int(bool(plot.isFreshWater())), int(bool(plot.isCoastalLand())), area.getNumTiles(), int(bool(plot.isStartingPlot())), plot.getOwner()])
	return rows


PLOT_COLUMNS = ["x", "y", "plotType", "terrain", "feature", "bonus", "improvement", "route", "food", "production", "commerce", "river", "freshWater", "coastalLand", "areaTiles", "startingPlot", "owner"]


def collectFacts(bProbeFreePromotions):
	facts = {"format": "SASSaveTransplantFacts", "formatVersion": 1}
	_attempt(facts, "game", _gameFacts)
	_attempt(facts, "players", lambda: [_playerFacts(i, bProbeFreePromotions) for i in range(gc.getMAX_CIV_PLAYERS()) if gc.getPlayer(i).isEverAlive()])
	facts["plotColumns"] = PLOT_COLUMNS
	_attempt(facts, "plots", _plotFacts)
	return facts


def export(szPrefix, bProbeFreePromotions):
	# <!-- custom: Writes <prefix>.CivBeyondSwordWBSave with the build's own WorldBuilder writer, then <prefix>.facts.json with what that file does not hold (who is human, plot yields under this build's rules, area sizes), and <prefix>.done last, so a waiting script reads only finished files. (Claude code Fable 5.2) -->
	szError = ""
	try:
		import CvWBDesc
		CvWBDesc.CvWBDesc().write(szPrefix)
	except Exception:
		szError += "WBSAVE: " + traceback.format_exc()
	try:
		handle = open(szPrefix + ".facts.json", "wb")
		handle.write(toJson(collectFacts(bProbeFreePromotions)).encode("ascii"))
		handle.close()
	except Exception:
		szError += "FACTS: " + traceback.format_exc()
	handle = open(szPrefix + ".done", "wb")
	if szError:
		handle.write("FAILED\n" + szError)
	else:
		handle.write("SUCCEEDED\n")
	handle.close()
	return szError


def keepSourceGrants(techsByTeam, unitsByPlayer):
	# <!-- custom: For sas_save_transplanter.py's "source" policy, run in the receiving game after the scenario start: removes the techs and promotions that start added beyond the source's own.
	# techsByTeam maps a team to its source techs; unitsByPlayer maps a player to source rows of [x, y, unit type, promotions], and each unit there is matched to one row of its plot and type. (Claude code Fable 5.2) -->
	removed = []
	for iTeam in techsByTeam.keys():
		team = gc.getTeam(int(iTeam))
		for iTech in range(gc.getNumTechInfos()):
			if team.isHasTech(iTech) and gc.getTechInfo(iTech).getType() not in techsByTeam[iTeam]:
				team.setHasTech(iTech, False, -1, False, False)
				removed.append(["team", int(iTeam), gc.getTechInfo(iTech).getType()])
	for iPlayer in unitsByPlayer.keys():
		player = gc.getPlayer(int(iPlayer))
		rows = list(unitsByPlayer[iPlayer])
		(unit, iterator) = player.firstUnit(False)
		while unit:
			szType = gc.getUnitInfo(unit.getUnitType()).getType()
			for row in rows:
				if row[0] == unit.getX() and row[1] == unit.getY() and row[2] == szType:
					rows.remove(row)
					for iPromotion in range(gc.getNumPromotionInfos()):
						if unit.isHasPromotion(iPromotion) and gc.getPromotionInfo(iPromotion).getType() not in row[3]:
							unit.setHasPromotion(iPromotion, False)
							removed.append(["unit", int(iPlayer), szType, unit.getX(), unit.getY(), gc.getPromotionInfo(iPromotion).getType()])
					break
			(unit, iterator) = player.nextUnit(iterator, False)
	return removed


class _Holder:
	pass


def _plotContent(plot):
	# <!-- custom: What updateMap may change on a plot: feature with its variety, and bonus. (Claude code Fable 5.2) -->
	return [_typeOrNone(gc.getFeatureInfo, plot.getFeatureType()), plot.getFeatureVariety(), _typeOrNone(gc.getBonusInfo, plot.getBonusType(-1))]


def updateMap(sourceFeatureTypes, sourceBonusTypes):
	# <!-- custom: For sas_save_transplanter.py's --map-variants update, run in the receiving game: places only the feature and bonus types that the source build's XML did not have, by the current build's own rules, and leaves every plot that already holds a feature or bonus as it is. The user asked whether a transplanted world should get such content (Camel, Marsh) for balance; "preserve" keeps the world, and this is the other variant.
	# Returns every plot it changed with its content before and after, read from the map itself, so that the caller can check that nothing else changed; the first version returned counts only (Codex (GPT-6.1-Sol)'s 2026-11-16 review).
	# Plots with a starting position or units get nothing, as nothing normalizes starts afterwards. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
	cyMap = CyMap()
	plots = [cyMap.plotByIndex(i) for i in range(cyMap.numPlots())]
	before = [_plotContent(plot) for plot in plots]
	result = {"newFeatureTypes": [], "newBonusTypes": [], "notPlaced": [], "bonusPlacement": {}, "removedFromStartsAndUnits": []}
	for iFeature in range(gc.getNumFeatureInfos()):
		szType = gc.getFeatureInfo(iFeature).getType()
		if szType in sourceFeatureTypes:
			continue
		result["newFeatureTypes"].append(szType)
		holder = _Holder()
		for plot in plots:
			if plot.isStartingPlot() or plot.getNumUnits() > 0 or plot.getFeatureType() != -1 or plot.getBonusType(-1) != -1:
				continue
			if szType == "FEATURE_MARSH":
				# <!-- custom: Marsh has its own fractal in CvMapGeneratorUtil.FeatureGenerator.addMarshesAtPlot, which sets itself up on first use, so it is called on a bare object rather than a generator built for a map script.
				# On a new map Marsh is placed before Forest; here Forests are already in place and keep their plots, so Marsh gets fewer than on a new map. marshFractalPlotsHeldByOtherFeatures counts those. (Claude code Fable 5.2) -->
				import CvMapGeneratorUtil
				CvMapGeneratorUtil.FeatureGenerator.addMarshesAtPlot.im_func(holder, plot, plot.getX(), plot.getY())
			elif plot.canHaveFeature(iFeature) and gc.getGame().getMapRand().get(10000, "SASSaveTransplant feature") < gc.getFeatureInfo(iFeature).getAppearanceProbability():
				plot.setFeatureType(iFeature, -1)
		if szType == "FEATURE_MARSH" and getattr(holder, "marshes", None) is not None:
			iHeld = 0
			for plot in plots:
				if plot.getFeatureType() != -1 and plot.getFeatureType() != iFeature and plot.getBonusType(-1) == -1 and plot.isFlatlands() and gc.getFeatureInfo(iFeature).isTerrain(plot.getTerrainType()) and holder.marshes.getHeight(plot.getX(), plot.getY()) >= holder.iMarshLevel:
					iHeld += 1
			result["marshFractalPlotsHeldByOtherFeatures"] = iHeld
	generator = CyMapGenerator()
	for iOrder in range(gc.getNumBonusInfos()):
		for iBonus in range(gc.getNumBonusInfos()):
			info = gc.getBonusInfo(iBonus)
			if info.getPlacementOrder() != iOrder or info.getType() in sourceBonusTypes:
				continue
			result["newBonusTypes"].append(info.getType())
			# <!-- custom: The same choice as CvMapGenerator::addBonuses: isOneArea. The first version chose by unique range, and Camel and Peat (a range above 0, bArea 0) would have gone to addUniqueBonusType, which asserts a one-area bonus; found by Codex (GPT-6.1-Sol)'s review before it ever ran. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
			if info.isOneArea():
				generator.addUniqueBonusType(iBonus)
				result["bonusPlacement"][info.getType()] = "addUniqueBonusType"
			else:
				generator.addNonUniqueBonusType(iBonus)
				result["bonusPlacement"][info.getType()] = "addNonUniqueBonusType"
			# <!-- custom: The DLL's placement knows no starting plots, which a new map only picks afterwards, so a bonus it put under a start or a unit is taken off again. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
			for iPlot in range(len(plots)):
				plot = plots[iPlot]
				if plot.getBonusType(-1) == iBonus and before[iPlot][2] is None and (plot.isStartingPlot() or plot.getNumUnits() > 0):
					plot.setBonusType(-1)
					result["removedFromStartsAndUnits"].append([plot.getX(), plot.getY(), info.getType()])
	# <!-- custom: Rows of [x, y, feature, variety, bonus before, feature, variety, bonus after]. (Claude code Fable 5.2) -->
	changes = []
	counts = {}
	for iPlot in range(len(plots)):
		after = _plotContent(plots[iPlot])
		if after != before[iPlot]:
			changes.append([plots[iPlot].getX(), plots[iPlot].getY()] + before[iPlot] + after)
			for szType in (after[0], after[2]):
				if szType is not None and szType not in (before[iPlot][0], before[iPlot][2]):
					counts[szType] = counts.get(szType, 0) + 1
	result["changes"] = changes
	result["counts"] = counts
	for szType in result["newFeatureTypes"] + result["newBonusTypes"]:
		if szType not in counts:
			result["notPlaced"].append(szType)
	return result


def finishImport(request):
	# <!-- custom: The receiving side for a build without SASPilot, such as base AdvCiv or an older AdvCiv-SAS: the user asked whether a current world could also go into those. Run by the hook once the scenario has started, it does what sas_save_transplanter.py's import_world does through SASPilot in the current build: source grants, seeds, map update, re-export, save.
	# Writes <prefix>.import.json with each step's result and <prefix>.import.done last. CyGame.saveGame is in the stock BtS API. (Claude code Fable 5.2) -->
	szPrefix = request.OUT_PREFIX
	result = {}
	szError = ""
	try:
		game = gc.getGame()
		result["humanName"] = gc.getPlayer(game.getActivePlayer()).getName()
		result["activePlayer"] = game.getActivePlayer()
		if getattr(request, "KEEP_GRANTS", None) is not None:
			result["grantsRemovedAfterLoad"] = keepSourceGrants(request.KEEP_GRANTS[0], request.KEEP_GRANTS[1])
		if getattr(request, "SEEDS", None) is not None:
			game.getSorenRand().init(request.SEEDS[0])
			game.getMapRand().init(request.SEEDS[1])
			result["seedsSet"] = [game.getSorenRand().getSeed(), game.getMapRand().getSeed()]
		if getattr(request, "MAP_UPDATE", None) is not None:
			result["mapUpdate"] = updateMap(request.MAP_UPDATE[0], request.MAP_UPDATE[1])
		szExportError = export(szPrefix + "_reexport", False)
		if szExportError:
			szError += szExportError
		# <!-- custom: A name changed by stray typing on the setup screens is the caller's reason to import again, so no save is written for it; see import_world. (Claude code Fable 5.2) -->
		if (getattr(request, "HUMAN_NAME", None) is None or result["humanName"] == request.HUMAN_NAME) and (getattr(request, "HUMAN_SLOT", None) is None or result["activePlayer"] == request.HUMAN_SLOT):
			game.saveGame(str(request.SAVE_PATH))
			result["save"] = request.SAVE_PATH
	except Exception:
		szError += "IMPORT: " + traceback.format_exc()
	if szError:
		result["error"] = szError
	handle = open(szPrefix + ".import.json", "wb")
	handle.write(toJson(result).encode("ascii"))
	handle.close()
	handle = open(szPrefix + ".import.done", "wb")
	handle.write("DONE\n")
	handle.close()


def onEvent(argsList):
	# <!-- custom: Called before the build's own onEvent. The export runs once, on the first gameUpdate after the save has loaded: at OnLoad itself the EXE has not finished setting up the game for display. (Claude code Fable 5.2) -->
	global _bDone
	if _bDone:
		return
	if argsList[0] != "gameUpdate":
		return
	if gc.getGame().isFinalInitialized() == False:
		return
	_bDone = True
	try:
		# <!-- custom: A request is served once: the first version left it armed in the copy, so a later launch of that copy by hand would have exported another game over the last run's files (Codex (GPT-6.1-Sol)'s 2026-11-16 review).
		# sas_save_transplanter.py removes the request once Civ4 has closed; should that not happen, the finished run's .done file makes the hook do nothing. The hook does not delete the request itself, as a changed .py under Assets makes a running Civ4 reload its Python. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
		try:
			import SASSaveTransplantRequest
		except ImportError:
			return
		# <!-- custom: MODE "import" makes this build the receiving one. (Claude code Fable 5.2) -->
		bImport = getattr(SASSaveTransplantRequest, "MODE", "export") == "import"
		if bImport and os.path.isfile(SASSaveTransplantRequest.OUT_PREFIX + ".import.done"):
			return
		if not bImport and os.path.isfile(SASSaveTransplantRequest.OUT_PREFIX + ".done"):
			return
		if bImport:
			finishImport(SASSaveTransplantRequest)
		else:
			export(SASSaveTransplantRequest.OUT_PREFIX, True)
	except Exception:
		try:
			handle = open(os.path.join(os.environ.get("TEMP", "."), "SASSaveTransplantExport_error.txt"), "wb")
			handle.write(traceback.format_exc())
			handle.close()
		except Exception:
			pass
