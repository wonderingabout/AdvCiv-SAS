# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: moved to a separate files these we compute these only once fairly independently from external variables, and return a list at the end anyway, which seems much cleaner to do as a separate file rather, with the help of ChatGPT-5.2 Thinking thanks a lot -->
#
# SevoPedia main-list grouping helpers.
# - Purpose: keep SevoPediaMain.py smaller/cleaner by moving "grouping once" logic here.
# - Design: NO imports from SevoPediaMain (avoids circular deps). Callers pass `gc` + a few flags.
# - Python: keep Civ4/BUG Python 2.4 compatibility (xrange, cmp sorts, etc.).
#
# Expected usage from SevoPediaMain:
#   import _sevopedia_main_groupings as SAS_MainGroupings
#   ... then call SAS_MainGroupings.<func>(..., gc, self.isSortLists(), ...)
#

from CvPythonExtensions import *
from _sevopedia_helpers import SAS_isFeatureRemovable

def SAS_isFoodYieldImprovement(iImprovement, gc):
	# Check if improvement provides food yields from any bonus.
	info = gc.getImprovementInfo(iImprovement)
	if not info or info.isGraphicalOnly():
		return False

	for iBonus in range(gc.getNumBonusInfos()):
		bInfo = gc.getBonusInfo(iBonus)
		if bInfo and bInfo.isGraphicalOnly():
			continue
		# Check if this improvement gives food yield from this bonus
		if info.getImprovementBonusYield(iBonus, YieldTypes.YIELD_FOOD) > 0:
			return True

	return False

# <!-- custom: in sevopedia improvement list, group improvements by whether their terrain is a water type or not (e.g. Land Improvements -> Farm/Pasture, Water Improvements -> Fishing Boats/Offshore Platform) an idea i got from seeing ingame how it is in the Middle-Earth mod which i find very polished and took ideas from btw  thanks; plus other subgroups we added in advciv-sas. Implemented with chatgpt 5.2's help as for as of now the other ones thanks a lot -->
# Group improvements as:
# - Land (Growth): land improvements in an upgrade chain (e.g. Cottage -> Hamlet -> Village -> Town)
# - Land (Bonus-capable): land improvements that can interact with bonuses (trade/connect or bonus yields)
# - Land (Other): remaining land improvements
# - Water (Food): water improvements that provide food (Fishing Boats, Whaling Boats)
# - Water (Other): other water improvements (Offshore Platform)

def SAS_isBonusCapableImprovement(iImprovement, gc):
	info = gc.getImprovementInfo(iImprovement)
	if not info or info.isGraphicalOnly():
		return False

	# If it connects/trades any bonus, it's bonus-capable.
	for iBonus in range(gc.getNumBonusInfos()):
		bInfo = gc.getBonusInfo(iBonus)
		if bInfo and bInfo.isGraphicalOnly():
			continue

		if hasattr(info, "isBonusTrade"):
			if info.isBonusTrade(iBonus):
				return True
		else:
			if info.isImprovementBonusTrade(iBonus):
				return True

	# Some mods may give bonus yields even if trade flags are odd.
	for iBonus in range(gc.getNumBonusInfos()):
		bInfo = gc.getBonusInfo(iBonus)
		if bInfo and bInfo.isGraphicalOnly():
			continue
		for iYield in range(YieldTypes.NUM_YIELD_TYPES):
			if info.getImprovementBonusYield(iBonus, iYield) != 0:
				return True

	return False

# Helper: get ALL improvements that make a bonus tradable (i.e. "improve/connect" it).
# This is used for Sevopedia Main list grouping, similar to RFC DoC's Resource grouping.
# Unlike a "primary improvement" heuristic, we keep multi-improvement cases exhaustive by using
# a combined header like: "Well, Offshore Platform".
def SAS_getTradingImprovementsForBonus(iBonus, gc):
	bInfo = gc.getBonusInfo(iBonus)
	if not bInfo or bInfo.isGraphicalOnly():
		return []
	r = []
	for iImprovement in range(gc.getNumImprovementInfos()):
		imprInfo = gc.getImprovementInfo(iImprovement)
		if not imprInfo or imprInfo.isGraphicalOnly():
			continue
		# Support both wrapper styles (RFC often exposes isBonusTrade; BtS/AdvCiv uses isImprovementBonusTrade).
		if hasattr(imprInfo, "isBonusTrade"):
			bTrades = imprInfo.isBonusTrade(iBonus)
		else:
			bTrades = imprInfo.isImprovementBonusTrade(iBonus)
		if bTrades:
			r.append(iImprovement)
	return r

# Group bonuses by the improvement(s) that connect them:
#   Farm -> Corn/Wheat/...
#   Pasture -> Sheep/Horse/...
# For multi-improvement bonuses (e.g. Oil: Well + Offshore Platform), we use a combined header.
# <!-- custom: we did this change because RFC DOC used another water/land tie breaker logic that would display Oil only under "Well", but the player needs to know too that "Offshore Platform" is another improvement trades for Oil. Also, if some mod mod added another improvement trades on land (e.g. Farm + Pasture for Milk (imaginary example)) then the water/land tie breaking would not be effective as well, and we'd miss the info that both improvements support this. This is the only case in our mod (Oil) that has more than one improvement trades., so we don't need to complicate the logic further, while hopefully providing this logic in a bit cleaner or more relevant way to us than in RFC DOC mod (although their code helps lot and with chatgpt 5.2's help too and my help too xd i mean thanks to them and me xd as well) -->

def SAS_getTerrainsGroupedByLandWater_fromBaseList(baseList, gc, bSortLists, highIds):
	r = []
	landFlat = []
	graphicalOnlyHigh = []
	water = []

	# Terrain IDs considered "GraphicalOnly (High)" purely for UI grouping (e.g. Hills/Peaks).

	for (szName, iTerrain) in baseList:
		info = gc.getTerrainInfo(iTerrain)

		# IMPORTANT:
		# In your CIV4TerrainInfos.xml, TERRAIN_HILL and TERRAIN_PEAK have <bWater>1</bWater>. Therefore info.isWater() returns True for them. For Sevopedia grouping we still want them under GraphicalOnly (High), so we treat LAND_HIGH as a deliberate UI override.
		if iTerrain in highIds:
			graphicalOnlyHigh.append((szName, iTerrain))
		elif info and info.isWater():
			water.append((szName, iTerrain))
		else:
			landFlat.append((szName, iTerrain))

	# Optional sorting if BUG Sort Lists is on
	if bSortLists:
		landFlat.sort()
		graphicalOnlyHigh.sort()
		water.sort()

	# Emit headers + items in alphabetical order by header name
	if graphicalOnlyHigh:
		r.append(("GraphicalOnly (High)", -1))
		for x in graphicalOnlyHigh:
			r.append(x)

	if graphicalOnlyHigh and landFlat:
		r.append(("", -1))

	if landFlat:
		r.append(("Land", -1))
		for x in landFlat:
			r.append(x)

	if (graphicalOnlyHigh or landFlat) and water:
		r.append(("", -1))

	if water:
		r.append(("Water", -1))
		for x in water:
			r.append(x)

	return r

# <!-- custom: in sevopedia feature list, group features by Land (Removable), Land (Other), and Water. Added with the help of chatgpt 5.2 thanks. -->
# Implementation note:
# - We detect "Water" features by checking if the feature can appear on any true water terrain using FeatureInfo.isTerrain(iTerrain).
# - We detect "Removable" land features by scanning CvBuildInfo for a build that removes that feature.
#
# IMPORTANT MOD-SPECIFIC NOTE:
# - In our CIV4TerrainInfos.xml, TERRAIN_HILL and TERRAIN_PEAK have <bWater>1</bWater>.
# - Many land features are valid on hills, so if we treat every isWater terrain as water here,
#   we'd misclassify many land features as "Water".
# - Therefore we exclude our GraphicalOnly (High) terrains from the water-terrain scan used here. -->
def SAS_getFeaturesGroupedByLandWater_fromBaseList(baseList, gc, bSortLists, graphicalOnlyHighIds):
	r = []
	landRemovable = []
	landOther = []
	water = []

	# Exclude our GraphicalOnly (High) terrains (e.g. Hill/Peak) even if XML marks them as water.

	# Build list of "true water terrains" for feature classification.
	waterTerrainIds = []
	for iTerrain in range(gc.getNumTerrainInfos()):
		tInfo = gc.getTerrainInfo(iTerrain)
		if tInfo and tInfo.isWater() and (iTerrain not in graphicalOnlyHighIds):
			waterTerrainIds.append(iTerrain)

	for (szName, iFeature) in baseList:
		fInfo = gc.getFeatureInfo(iFeature)

		# Water feature if it can appear on at least one true water terrain.
		bIsWaterFeature = False
		for iTerrain in waterTerrainIds:
			if fInfo.isTerrain(iTerrain):
				bIsWaterFeature = True
				break

		if bIsWaterFeature:
			water.append((szName, iFeature))
		else:
			# Land feature: split removable vs other
			if SAS_isFeatureRemovable(iFeature, gc):
				landRemovable.append((szName, iFeature))
			else:
				landOther.append((szName, iFeature))

	# Optional sorting if BUG Sort Lists is on
	if bSortLists:
		landRemovable.sort()
		landOther.sort()
		water.sort()

	# Emit headers + items in alphabetical order by header name
	if landOther:
		r.append(("Land (Other)", -1))
		for x in landOther:
			r.append(x)

	if landOther and landRemovable:
		r.append(("", -1))

	if landRemovable:
		r.append(("Land (Removable)", -1))
		for x in landRemovable:
			r.append(x)

	if (landOther or landRemovable) and water:
		r.append(("", -1))

	if water:
		r.append(("Water", -1))
		for x in water:
			r.append(x)

	return r

# Group bonuses by the improvement(s) that connect them:
#   Farm -> Corn/Wheat/...
#   Pasture -> Sheep/Horse/...
# For multi-improvement bonuses (e.g. Oil: Well + Offshore Platform), we use a combined header.
# <!-- custom: we did this change because RFC DOC used another water/land tie breaker logic that would display Oil only under "Well", but the player needs to know too that "Offshore Platform" is another improvement trades for Oil. Also, if some mod mod added another improvement trades on land (e.g. Farm + Pasture for Milk (imaginary example)) then the water/land tie breaking would not be effective as well, and we'd miss the info that both improvements support this. This is the only case in our mod (Oil) that has more than one improvement trades., so we don't need to complicate the logic further, while hopefully providing this logic in a bit cleaner or more relevant way to us than in RFC DOC mod (although their code helps lot and with chatgpt 5.2's help too and my help too xd i mean thanks to them and me xd as well) -->
def SAS_getBonusesGroupedByImprovement_fromBaseList(baseList, gc, bSortLists):
	bonusesList = []

	noImprovement = []
	groups = {}  # key tuple(iImprovement, ...) -> [(szName, iBonus), ...]

	# One pass over bonuses preserves XML order within each group when Sort Lists is OFF.
	for (szName, iBonus) in baseList:
		lImpr = SAS_getTradingImprovementsForBonus(iBonus, gc)
		if not lImpr:
			noImprovement.append((szName, iBonus))
			continue

		# Keep improvement ids in XML order (already in-order due to the loop in SAS_getTradingImprovementsForBonus).
		key = tuple(lImpr)
		tmp = groups.get(key, None)
		if tmp is None:
			tmp = []
			groups[key] = tmp
		tmp.append((szName, iBonus))

	# Optional sorting within each improvement-group (when BUG "Sort Lists" is ON)
	if bSortLists:
		for k in groups.keys():
			groups[k].sort()
		noImprovement.sort()

	# Order headers:
	#  - primarily by first improvement id (so this generally follows ImprovementInfos XML order),
	#  - then by key length (single-improvement headers first),
	#  - then by the key itself (stable).
	keys = groups.keys()
	def _cmpKeys(a, b):
		ta = (a[0], len(a), a)
		tb = (b[0], len(b), b)
		if ta < tb:
			return -1
		if ta > tb:
			return 1
		return 0
	keys.sort(_cmpKeys)

	for key in keys:
		tmp = groups.get(key, None)
		if not tmp:
			continue

		if bonusesList:
			bonusesList.append(("", -1))

		# Header text: single improvement name OR "A, B, C" for multi-improvement bonuses.
		parts = []
		for iImprovement in key:
			imprInfo = gc.getImprovementInfo(iImprovement)
			if imprInfo:
				parts.append(imprInfo.getDescription())
		szHeader = "Improvement"
		if parts:
			szHeader = ", ".join(parts)
		bonusesList.append((szHeader, -1))

		for x in tmp:
			bonusesList.append(x)

	# Fallback bucket for bonuses that have no connecting/trade improvement (rare)
	if noImprovement:
		if bonusesList:
			bonusesList.append(("", -1))
		bonusesList.append(("Other", -1))
		for x in noImprovement:
			bonusesList.append(x)

	return bonusesList

# <!-- custom: in sevopedia improvement list, group improvements by whether their terrain is a water type or not (e.g. Land Improvements -> Farm/Pasture, Water Improvements -> Fishing Boats/Offshore Platform) an idea i got from seeing ingame how it is in the Middle-Earth mod which i find very polished and took ideas from btw  thanks; plus other subgroups we added in advciv-sas. Implemented with chatgpt 5.2's help as for as of now the other ones thanks a lot -->
# Group improvements as:
# - Land (Growth): land improvements in an upgrade chain (e.g. Cottage -> Hamlet -> Village -> Town)
# - Land (Bonus-capable): land improvements that can interact with bonuses (trade/connect or bonus yields)
# - Land (Other): remaining land improvements
# - Water (Food): water improvements that provide food (Fishing Boats, Whaling Boats)
# - Water (Other): other water improvements (Offshore Platform)
def SAS_getImprovementsGroupedByTerrain_fromBaseList(baseList, gc, bSortLists):
	r = []
	landGrowth = []
	landBonusCapable = []
	landOther = []
	waterFood = []
	waterOther = []

	# Build set of improvements that are upgraded *to* by something (to detect chain membership, incl. final node).
	dUpgradeTargets = {}
	for (szName, iImprovement) in baseList:
		info = gc.getImprovementInfo(iImprovement)
		if info and hasattr(info, "getImprovementUpgrade"):
			iUp = info.getImprovementUpgrade()
			if iUp != -1:
				dUpgradeTargets[iUp] = 1

	# Cache bonus-capability per improvement to avoid re-scanning bonuses repeatedly.
	dBonusCapable = {}

	# Build improvement -> build tech prereq era mapping for water improvements sorting
	dImprToEra = {}
	for iBuild in xrange(gc.getNumBuildInfos()):
		buildInfo = gc.getBuildInfo(iBuild)
		if buildInfo:
			iImpr = buildInfo.getImprovement()
			if iImpr >= 0:
				iTech = buildInfo.getTechPrereq()
				if iTech >= 0:
					dImprToEra[iImpr] = gc.getTechInfo(iTech).getEra()
				elif iImpr not in dImprToEra:
					dImprToEra[iImpr] = -1

	for (szName, iImprovement) in baseList:
		info = gc.getImprovementInfo(iImprovement)

		if info and info.isWater():
			# Check if water improvement provides food yields from any bonus
			bFood = SAS_isFoodYieldImprovement(iImprovement, gc)
			iEra = dImprToEra.get(iImprovement, -1)
			if bFood:
				waterFood.append((iEra, szName, iImprovement))
			else:
				waterOther.append((iEra, szName, iImprovement))
			continue

		# Land
		bGrowth = False
		if info and hasattr(info, "getImprovementUpgrade"):
			iUp = info.getImprovementUpgrade()
			if iUp != -1 or dUpgradeTargets.has_key(iImprovement):
				bGrowth = True

		if bGrowth:
			landGrowth.append((szName, iImprovement))
		else:
			if dBonusCapable.has_key(iImprovement):
				bBonusCapable = dBonusCapable[iImprovement]
			else:
				bBonusCapable = SAS_isBonusCapableImprovement(iImprovement, gc)
				dBonusCapable[iImprovement] = bBonusCapable

			if bBonusCapable:
				landBonusCapable.append((szName, iImprovement))
			else:
				landOther.append((szName, iImprovement))

	# Sort Land (Growth) by upgrade chain order, not alphabetically
	# Find chain root(s) and walk the upgrade path
	def sortByUpgradeChain(growthList):
		if not growthList:
			return growthList
		# Build upgrade map: iImprovement -> iUpgrade
		upgradeMap = {}
		allIds = set()
		for (szName, iImprovement) in growthList:
			allIds.add(iImprovement)
			info = gc.getImprovementInfo(iImprovement)
			if info and hasattr(info, "getImprovementUpgrade"):
				iUp = info.getImprovementUpgrade()
				if iUp != -1:
					upgradeMap[iImprovement] = iUp
		# Find roots (improvements not upgraded to by anything in our list)
		roots = []
		for (szName, iImprovement) in growthList:
			isRoot = True
			for tgt in upgradeMap.values():
				if tgt == iImprovement:
					isRoot = False
					break
			if isRoot:
				roots.append(iImprovement)
		# Walk chains from roots
		result = []
		visited = set()
		for root in roots:
			current = root
			while current is not None and current not in visited:
				visited.add(current)
				for (szName, iImprovement) in growthList:
					if iImprovement == current:
						result.append((szName, iImprovement))
						break
				current = upgradeMap.get(current, None)
		# Add any remaining (shouldn't happen, but safety)
		for item in growthList:
			if item[1] not in visited:
				result.append(item)
		return result

	landGrowth = sortByUpgradeChain(landGrowth)

	# Sort water improvements by tech prereq era, then extract (szName, iImprovement)
	waterFood.sort(key=lambda x: (x[0], x[1]))  # sort by (iEra, szName)
	waterFood = [(item[1], item[2]) for item in waterFood]

	waterOther.sort(key=lambda x: (x[0], x[1]))  # sort by (iEra, szName)
	waterOther = [(item[1], item[2]) for item in waterOther]

	# Optional sorting if BUG Sort Lists is on
	# Keep special order for: landGrowth (chain), waterFood/waterOther (era)
	if bSortLists:
		landBonusCapable.sort()
		landOther.sort()

	# Emit headers + items in alphabetical order by header name
	if landBonusCapable:
		r.append(("Land (Bonus-capable)", -1))
		for x in landBonusCapable:
			r.append(x)

	if landBonusCapable and (landGrowth or landOther or waterFood or waterOther):
		r.append(("", -1))

	if landGrowth:
		r.append(("Land (Growth)", -1))
		for x in landGrowth:
			r.append(x)

	if landGrowth and (landOther or waterFood or waterOther):
		r.append(("", -1))

	if landOther:
		r.append(("Land (Other)", -1))
		for x in landOther:
			r.append(x)

	if (landBonusCapable or landGrowth or landOther) and (waterFood or waterOther):
		r.append(("", -1))

	if waterFood:
		r.append(("Water (Food)", -1))
		for x in waterFood:
			r.append(x)

	if waterFood and waterOther:
		r.append(("", -1))

	if waterOther:
		r.append(("Water (Other)", -1))
		for x in waterOther:
			r.append(x)

	return r

# <!-- custom: in sevopedia build list, group builds mirroring the improvement/feature categories.
# Implemented with claude opus 4.5's help thanks a lot -->
# Group builds as:
# - Land (Growth): builds that create growth-chain improvements (Cottage->Hamlet->Village->Town) - sorted by upgrade chain order
# - Land (Bonus-capable): builds that create bonus-capable improvements (Farm, Mine, etc.)
# - Land (Other): builds that create other land improvements (Fort, Forest Preserve, etc.)
# - Land (Removable): builds that remove features without creating improvements (Chop Down, Remove Jungle, Scrub Fallout)
# - Land (Route): builds that create routes (Road, Railroad)
# - Water (Food): builds that create food-yielding water improvements (Fishing Boats, Whaling Boats)
# - Water (Other): builds that create other water improvements (Offshore Platform)
def SAS_getBuildsGroupedByType_fromBaseList(baseList, gc, bSortLists):
	r = []
	landGrowth = []
	landBonusCapable = []
	landOther = []
	waterFood = []
	waterOther = []
	landRoute = []
	landRemovable = []

	# Build set of improvements that are upgraded *to* by something (to detect chain membership, incl. final node).
	dUpgradeTargets = {}
	for i in xrange(gc.getNumImprovementInfos()):
		info = gc.getImprovementInfo(i)
		if info and hasattr(info, "getImprovementUpgrade"):
			iUp = info.getImprovementUpgrade()
			if iUp != -1:
				dUpgradeTargets[iUp] = 1

	# Also build improvement -> build mapping for chain ordering
	imprToBuild = {}

	for (szName, iBuild) in baseList:
		buildInfo = gc.getBuildInfo(iBuild)
		if not buildInfo:
			continue

		iImprovement = buildInfo.getImprovement()
		iRoute = buildInfo.getRoute()

		if iRoute > -1:
			# Store tech prereq era for sorting (Road before Railroad)
			iTech = buildInfo.getTechPrereq()
			iEra = -1
			if iTech >= 0:
				iEra = gc.getTechInfo(iTech).getEra()
			landRoute.append((iEra, szName, iBuild))
		elif iImprovement > -1:
			imprToBuild[iImprovement] = (szName, iBuild)
			imprInfo = gc.getImprovementInfo(iImprovement)

			# Check if water improvement
			if imprInfo and imprInfo.isWater():
				bFood = SAS_isFoodYieldImprovement(iImprovement, gc)
				# Store tech prereq era for sorting
				iTech = buildInfo.getTechPrereq()
				iEra = -1
				if iTech >= 0:
					iEra = gc.getTechInfo(iTech).getEra()
				if bFood:
					waterFood.append((iEra, szName, iBuild))
				else:
					waterOther.append((iEra, szName, iBuild))
			else:
				# Check if growth-chain improvement
				bGrowth = False
				if imprInfo and hasattr(imprInfo, "getImprovementUpgrade"):
					iUp = imprInfo.getImprovementUpgrade()
					if iUp != -1 or dUpgradeTargets.has_key(iImprovement):
						bGrowth = True

				if bGrowth:
					landGrowth.append((szName, iBuild, iImprovement))  # include iImprovement for chain sorting
				else:
					# Check if bonus-capable
					bBonusCapable = SAS_isBonusCapableImprovement(iImprovement, gc)
					if bBonusCapable:
						landBonusCapable.append((szName, iBuild))
					else:
						landOther.append((szName, iBuild))
		else:
			landRemovable.append((szName, iBuild))

	# Sort Land (Growth) by upgrade chain order, not alphabetically
	def sortBuildsByUpgradeChain(growthList):
		if not growthList:
			return []
		# Build upgrade map: iImprovement -> iUpgrade
		upgradeMap = {}
		allIds = set()
		for item in growthList:
			iImprovement = item[2]
			allIds.add(iImprovement)
			info = gc.getImprovementInfo(iImprovement)
			if info and hasattr(info, "getImprovementUpgrade"):
				iUp = info.getImprovementUpgrade()
				if iUp != -1:
					upgradeMap[iImprovement] = iUp
		# Find roots (improvements not upgraded to by anything in our list)
		roots = []
		for item in growthList:
			iImprovement = item[2]
			isRoot = True
			for tgt in upgradeMap.values():
				if tgt == iImprovement:
					isRoot = False
					break
			if isRoot:
				roots.append(iImprovement)
		# Walk chains from roots
		result = []
		visited = set()
		for root in roots:
			current = root
			while current is not None and current not in visited:
				visited.add(current)
				for item in growthList:
					if item[2] == current:
						result.append((item[0], item[1]))  # (szName, iBuild)
						break
				current = upgradeMap.get(current, None)
		# Add any remaining (shouldn't happen, but safety)
		for item in growthList:
			if item[2] not in visited:
				result.append((item[0], item[1]))
		return result

	landGrowth = sortBuildsByUpgradeChain(landGrowth)

	# Sort by tech prereq era, then extract (szName, iBuild)
	landRoute.sort(key=lambda x: (x[0], x[1]))  # sort by (iEra, szName)
	landRoute = [(item[1], item[2]) for item in landRoute]

	waterFood.sort(key=lambda x: (x[0], x[1]))  # sort by (iEra, szName)
	waterFood = [(item[1], item[2]) for item in waterFood]

	waterOther.sort(key=lambda x: (x[0], x[1]))  # sort by (iEra, szName)
	waterOther = [(item[1], item[2]) for item in waterOther]

	# Optional sorting if BUG Sort Lists is on
	# Keep special order for: landGrowth (chain), landRoute/waterFood/waterOther (era)
	if bSortLists:
		landBonusCapable.sort()
		landOther.sort()
		landRemovable.sort()

	# Emit headers + items in alphabetical order by header name
	if landBonusCapable:
		r.append(("Land (Bonus-capable)", -1))
		for x in landBonusCapable:
			r.append(x)

	if landBonusCapable and (landGrowth or landOther or landRemovable or landRoute or waterFood or waterOther):
		r.append(("", -1))

	if landGrowth:
		r.append(("Land (Growth)", -1))
		for x in landGrowth:
			r.append(x)

	if landGrowth and (landOther or landRemovable or landRoute or waterFood or waterOther):
		r.append(("", -1))

	if landOther:
		r.append(("Land (Other)", -1))
		for x in landOther:
			r.append(x)

	if landOther and (landRemovable or landRoute or waterFood or waterOther):
		r.append(("", -1))

	if landRemovable:
		r.append(("Land (Removable)", -1))
		for x in landRemovable:
			r.append(x)

	if landRemovable and (landRoute or waterFood or waterOther):
		r.append(("", -1))

	if landRoute:
		r.append(("Land (Route)", -1))
		for x in landRoute:
			r.append(x)

	if landRoute and (waterFood or waterOther):
		r.append(("", -1))

	if waterFood:
		r.append(("Water (Food)", -1))
		for x in waterFood:
			r.append(x)

	if waterFood and waterOther:
		r.append(("", -1))

	if waterOther:
		r.append(("Water (Other)", -1))
		for x in waterOther:
			r.append(x)

	return r



# ---------------------------------------------------------------------------
# Era / category grouping helpers (Techs, Units, Buildings, Projects, Religions, Corporations, Specialists, Civics)
#
# Notes:
# - Callers pass `gc` explicitly (no globals, no SevoPediaMain imports).
# - `localText` is optional; if omitted we create/use a CyTranslator() instance.
# - For era-tiered lists that depend on "availability era" logic, callers pass a callback:
#     getEraFn(itemId, *extraCounts) -> iEra (>=0), -1 for "no tech prereq", or None to skip.
# ---------------------------------------------------------------------------

try:
	_SAS_localText = CyTranslator()
except:
	_SAS_localText = None

def _SAS_getLocalText(localText):
	if localText is not None:
		return localText
	if _SAS_localText is not None:
		return _SAS_localText
	return CyTranslator()

# ---------------------------------------------------------------------------
# Availability-era helpers (used by era groupings)
# These were previously methods on SevoPediaMain; moved here to keep groupings self-contained.

_SAS_cacheCorporationHQBuildingByCorp = None

# In AdvCiv-SAS, your corporations are effectively gated by the founding building (the BUILDING_CORPORATION_X that has <FoundsCorporation>CORPORATION_X</FoundsCorporation> and has <PrereqTech> / <TechTypes>), while the corresponding CIV4CorporationInfo.xml often has <TechPrereq>NONE</TechPrereq>. So the clean “era” for a corporation should be the availability era of its founding building.
# This reuses your existing SAS_getBuildingAvailabilityEra(iBuilding, iNumAndTechs) helper (the one that already accounts for SpecialBuilding tech + religion founding tech).
# Map each corporation to its founding (HQ) building once, then reuse; used for grouping corporations by era.
def SAS_getCorporationHQBuilding(iCorporation, gc):
	global _SAS_cacheCorporationHQBuildingByCorp
	if _SAS_cacheCorporationHQBuildingByCorp is None:
		m = {}
		for iBuilding in range(gc.getNumBuildingInfos()):
			bInfo = gc.getBuildingInfo(iBuilding)
			if not bInfo or bInfo.isGraphicalOnly():
				continue
			iFounds = bInfo.getFoundsCorporation()
			if iFounds >= 0:
				m[iFounds] = iBuilding
		_SAS_cacheCorporationHQBuildingByCorp = m
	return _SAS_cacheCorporationHQBuildingByCorp.get(iCorporation, -1)

def SAS_getBuildingAvailabilityEra(iBuilding, iNumAndTechs, gc):
	info = gc.getBuildingInfo(iBuilding)
	if not info or info.isGraphicalOnly():
		return None  # caller should skip

	iEra = -1

	# Main AND prereq tech (<PrereqTech>)
	# <!-- custom: it seems getPrereqOrTechs does not exist causing a python error, but with the help of chatgpt 5.2 found the correct way to fetch tech prereqs that addresses and fixes it and that works as intended in displaying the building at latest tech prereq of the building's corresponding era. Seems to run fine in testing/empirically -->
	# When first implementing era-tiered building lists, we hit a crash: AttributeError: 'CvBuildingInfo' object has no attribute 'getPrereqOrTechs' (Python traceback from SevoPediaMain.getBuildingList). We verified the cause by inspecting our exported Cy/Cv infos (see as of now Sevopedia/Debug/): CvBuildingInfo in this DLL exposes getPrereqAndTech() + getPrereqAndTechs(i), but NOT getPrereqOrTechs(i) (unlike some other mods / DLLs). (Mapping to our XML schema: <PrereqTech> maps to getPrereqAndTech(), and <TechTypes><PrereqTech>...</PrereqTech></TechTypes> maps to getPrereqAndTechs(i).)
	# Fix: compute the building "availability era" using only these AND-tech prereqs: start with getPrereqAndTech(), then scan additional prereqs via getPrereqAndTechs(i) for i in range(gc.getNUM_BUILDING_AND_TECH_PREREQS()). We bucket the building into the LATEST (max) era among these prereq techs, so it shows up in the era when it actually becomes buildable.
	# Empirical sanity check: we tested a building with two widely separated PrereqTech and TechTypes (e.g. TECH_MATHEMATICS (Classical) and TECH_FUSION (Future)) in both permutations (A then B, and B then A), and in both cases the building was listed under the later era (Future), confirming the "max era of prereqs" rule behaves correctly in practice.
	# Additional sanity check: we also tested <PrereqTech>NONE</PrereqTech> with an existing TechTypes prereq (i.e. only the <TechTypes> prereq was set), and the building was still listed under the correct era, confirming the fallback scan of getPrereqAndTechs(i) works even when the main <PrereqTech> is NONE. -->
	iTech = info.getPrereqAndTech()
	if iTech >= 0:
		iEra = gc.getTechInfo(iTech).getEra()

	# Extra AND tech prereqs (<TechTypes><PrereqTech>...)
	for j in range(iNumAndTechs):
		iTech2 = info.getPrereqAndTechs(j)
		if iTech2 >= 0:
			iEra2 = gc.getTechInfo(iTech2).getEra()
			if iEra2 > iEra:
				iEra = iEra2

	# SpecialBuilding tech prereq (eg monasteries gated by SPECIALBUILDING tech)
	# <!-- custom: special buildings need also to be checked for a tech prereq. For example the buddhist monastery as of now has no TechPrereq and TechTypes NONE, but the parent specialbuilding_monastery requires TECH_MONARCHY. Yet, without taking special buildings into account, the buddhist monastery is incorrectly listed at the "No Tech Prereq" part instead of at the "Classical Era" part. Fix this by taking their actual tech prereq into account properly with the help of chatgpt 5.2 thanks -->
	# Yep — that’s exactly why: for “special buildings” (Temple/Cathedral/Monastery/etc.), the real tech gate often lives in CIV4SpecialBuildingInfos.xml (e.g. SPECIALBUILDING_MONASTERY has TechPrereq = TECH_MONARCHY). So your era-bucketing currently sees “no building tech prereq” and dumps it into All Eras.
	# Also consider SpecialBuilding tech prereq (e.g. Monastery -> TECH_MONARCHY in CIV4SpecialBuildingInfos.xml)
	iSpecialBuildingType = info.getSpecialBuildingType()
	if iSpecialBuildingType >= 0:
		iSpecialTech = gc.getSpecialBuildingInfo(iSpecialBuildingType).getTechPrereq()
		if iSpecialTech >= 0:
			iSpecialEra = gc.getTechInfo(iSpecialTech).getEra()
			if iSpecialEra > iEra:
				iEra = iSpecialEra

	# Also consider PrereqReligion tech prereq (religion founding tech).
	# Example: Islamic Temple may have no building tech prereq, but RELIGION_ISLAM is founded by TECH_LATER_ABRAHAMISM (Medieval Era), so the building effectively cannot exist before that era (except via conquest/trade of a religion-enabled city).
	iPrereqReligion = info.getPrereqReligion()
	if iPrereqReligion >= 0:
		iReligionTech = gc.getReligionInfo(iPrereqReligion).getTechPrereq()
		if iReligionTech >= 0:
			iReligionEra = gc.getTechInfo(iReligionTech).getEra()
			if iReligionEra > iEra:
				iEra = iReligionEra

	return iEra  # -1 means "no tech prereq bucket"

def SAS_getUnitAvailabilityEra(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs, gc):
	info = gc.getUnitInfo(iUnit)
	if not info or info.isGraphicalOnly():
		return None  # caller should skip

	iEra = -1

	# Unit tech prereqs: <PrereqTech> + <TechTypes>
	iTech = info.getPrereqAndTech()
	if iTech >= 0:
		iEra = gc.getTechInfo(iTech).getEra()

	for j in range(iNumUnitAndTechs):
		iTech2 = info.getPrereqAndTechs(j)
		if iTech2 >= 0:
			iEra2 = gc.getTechInfo(iTech2).getEra()
			if iEra2 > iEra:
				iEra = iEra2

	# PrereqBuilding availability era (reuses building-era helper, so it includes SpecialBuilding tech + religion tech, etc.)
	iPrereqBuilding = info.getPrereqBuilding()
	if iPrereqBuilding >= 0:
		iBuildingEra = SAS_getBuildingAvailabilityEra(iPrereqBuilding, iNumBuildingAndTechs, gc)
		if iBuildingEra is not None and iBuildingEra > iEra:
			iEra = iBuildingEra

	# PrereqReligion tech prereq (religion founding tech).
	# (Mostly redundant for missionaries in your setup since they already require a monastery building, but harmless and fixes any unit that uses PrereqReligion without a building gate.)
	iPrereqReligion = info.getPrereqReligion()
	if iPrereqReligion >= 0:
		iReligionTech = gc.getReligionInfo(iPrereqReligion).getTechPrereq()
		if iReligionTech >= 0:
			iReligionEra = gc.getTechInfo(iReligionTech).getEra()
			if iReligionEra > iEra:
				iEra = iReligionEra

	# <!-- custom: note: executives's tech actual requirement not implemented here, as in advciv-sas they also have a prereq tech (see XML code comments or main changes guide or such for rationale). Otherwise the implementation so they are listed at e.g. "Industrial" Era and not "No Tech Prerequisite" (which does not reflect their effective ingame availabilty: not until later eras) would be tedious from what i understand of chatgpt 5.2's explanation and solution (plus we don't need to so better not); check if accurate -->
	# Yes — for your mod, adding a tech prereq directly on Executive units is the simplest and arguably the cleanest fix, and it also matches the design logic you already used for shrines (“captured thing exists locally, but you can’t mass-produce/spread it without understanding the tech”).

	return iEra  # -1 means "no tech prereq bucket"

# Compute the "availability era" for a corporation, based on its founding building's prereq tech era.
def SAS_getCorporationAvailabilityEra(iCorporation, iNumBuildingAndTechs, gc):
	cInfo = gc.getCorporationInfo(iCorporation)
	if not cInfo or cInfo.isGraphicalOnly():
		return None  # caller should skip

	iEra = -1

	# In AdvCiv-SAS, corporations are typically gated by the founding building techs (see CIV4BuildingInfos.xml <FoundsCorporation>).
	iHQBuilding = SAS_getCorporationHQBuilding(iCorporation, gc)
	if iHQBuilding >= 0:
		iBuildingEra = SAS_getBuildingAvailabilityEra(iHQBuilding, iNumBuildingAndTechs, gc)
		if iBuildingEra is not None and iBuildingEra > iEra:
			iEra = iBuildingEra

	return iEra  # -1 means "No Tech Prerequisite" bucket



def SAS_getTechsGroupedByEra(gc, bSortLists, localText=None):
	lt = _SAS_getLocalText(localText)

	techsList = []

	iNumEras = gc.getNumEraInfos()
	groups = {}  # iEra -> [(szName, iTech), ...]

	# One pass over TechInfos preserves XML order when Sort Lists is OFF
	iNumTechs = gc.getNumTechInfos()
	for iTech in range(iNumTechs):
		info = gc.getTechInfo(iTech)
		if info.isGraphicalOnly():
			continue

		iEra = info.getEra()
		szName = info.getDescription()

		if iEra not in groups:
			groups[iEra] = []
		groups[iEra].append((szName, iTech))

	# Optional sorting within each era group
	if bSortLists:
		for k in groups.keys():
			groups[k].sort()

	# Emit era groups in order
	for iEra in range(iNumEras):
		tmp = groups.get(iEra, None)
		if not tmp:
			continue

		if techsList:
			techsList.append(("", -1))  # spacer between eras
		techsList.append((gc.getEraInfo(iEra).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))

		for x in tmp:
			techsList.append(x)

	return techsList

def SAS_getUnitsGroupedByEra_fromBaseList(baseList, gc, bSortLists, localText=None, getUnitAvailabilityEraFn=None):
	# getUnitAvailabilityEraFn signature:
	#   fn(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs) -> iEra / -1 / None
	lt = _SAS_getLocalText(localText)

	# Default to the shared availability-era helper in this module (no SevoPediaMain dependency).
	if getUnitAvailabilityEraFn is None:
		def getUnitAvailabilityEraFn(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs):
			return SAS_getUnitAvailabilityEra(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs, gc)

	unitsList = []

	iNumEras = gc.getNumEraInfos()
	iNumUnitAndTechs = gc.getNUM_UNIT_AND_TECH_PREREQS()
	iNumBuildingAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

	noTech = []
	groups = {}  # iEra -> [(szName, iUnit), ...]

	# One pass: compute era once and bucket
	for (szName, iUnit) in baseList:
		iEra = getUnitAvailabilityEraFn(iUnit, iNumUnitAndTechs, iNumBuildingAndTechs)
		if iEra is None:
			continue

		if iEra == -1:
			noTech.append((szName, iUnit))
		else:
			if iEra not in groups:
				groups[iEra] = []
			groups[iEra].append((szName, iUnit))

	# Optional sorting within each bucket
	if bSortLists:
		noTech.sort()
		for k in groups.keys():
			groups[k].sort()

	# "No Tech Prerequisite" group first
	if noTech:
		unitsList.append((lt.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
		for x in noTech:
			unitsList.append(x)

	# Era groups in order
	for iEraLoop in range(iNumEras):
		tmp = groups.get(iEraLoop, None)
		if not tmp:
			continue

		if unitsList:
			unitsList.append(("", -1))

		unitsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))
		for x in tmp:
			unitsList.append(x)

	return unitsList

def SAS_getBuildingsGroupedByEra_fromBaseList(baseList, gc, bSortLists, localText=None, getBuildingAvailabilityEraFn=None):
	# getBuildingAvailabilityEraFn signature:
	#   fn(iBuilding, iNumAndTechs) -> iEra / -1 / None
	lt = _SAS_getLocalText(localText)

	# Default to the shared availability-era helper in this module (no SevoPediaMain dependency).
	if getBuildingAvailabilityEraFn is None:
		def getBuildingAvailabilityEraFn(iBuilding, iNumAndTechs):
			return SAS_getBuildingAvailabilityEra(iBuilding, iNumAndTechs, gc)

	buildingsList = []

	iNumEras = gc.getNumEraInfos()
	iNumAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

	noTech = []
	groups = {}  # iEra -> [(szName, iBuilding), ...]

	# One pass: compute era once and bucket
	for (szName, iBuilding) in baseList:
		iEra = getBuildingAvailabilityEraFn(iBuilding, iNumAndTechs)
		if iEra is None:
			continue  # graphical-only or invalid

		if iEra == -1:
			noTech.append((szName, iBuilding))
		else:
			if iEra not in groups:
				groups[iEra] = []
			groups[iEra].append((szName, iBuilding))

	# Optional sorting within each bucket
	if bSortLists:
		noTech.sort()
		for k in groups.keys():
			groups[k].sort()

	# "No Tech Prereq" group first
	if noTech:
		buildingsList.append((lt.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
		for x in noTech:
			buildingsList.append(x)

	# Era groups in order
	for iEraLoop in range(iNumEras):
		tmp = groups.get(iEraLoop, None)
		if not tmp:
			continue

		if buildingsList:
			buildingsList.append(("", -1))

		buildingsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))
		for x in tmp:
			buildingsList.append(x)

	return buildingsList

def SAS_getProjectsGroupedByEra_fromBaseList(baseList, gc, bSortLists, localText=None, getProjectAvailabilityEraFn=None):
	# getProjectAvailabilityEraFn signature:
	#   fn(iProject) -> iEra / -1 / None
	lt = _SAS_getLocalText(localText)

	projectsList = []

	iNumEras = gc.getNumEraInfos()

	noTech = []
	groups = {}  # iEra -> [(szName, iProject), ...]

	# One pass: compute era once and bucket
	for (szName, iProject) in baseList:
		iEra = getProjectAvailabilityEraFn(iProject)
		if iEra is None:
			continue

		if iEra == -1:
			noTech.append((szName, iProject))
		else:
			if iEra not in groups:
				groups[iEra] = []
			groups[iEra].append((szName, iProject))

	# Optional sorting within each bucket
	if bSortLists:
		noTech.sort()
		for k in groups.keys():
			groups[k].sort()

	# "No Tech Prereq" group first
	if noTech:
		projectsList.append((lt.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
		for x in noTech:
			projectsList.append(x)

	# Era groups in order
	for iEraLoop in range(iNumEras):
		tmp = groups.get(iEraLoop, None)
		if not tmp:
			continue

		if projectsList:
			projectsList.append(("", -1))

		projectsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))
		for x in tmp:
			projectsList.append(x)

	return projectsList

def SAS_getReligionsGroupedByEra_fromBaseList(baseList, gc, bSortLists, localText=None, getReligionAvailabilityEraFn=None):
	# getReligionAvailabilityEraFn signature:
	#   fn(iReligion) -> iEra / -1 / None
	lt = _SAS_getLocalText(localText)

	religionsList = []

	iNumEras = gc.getNumEraInfos()

	noTech = []
	groups = {}  # iEra -> [(szName, iReligion), ...]

	# One pass: compute era once and bucket
	for (szName, iReligion) in baseList:
		iEra = getReligionAvailabilityEraFn(iReligion)
		if iEra is None:
			continue

		if iEra == -1:
			noTech.append((szName, iReligion))
		else:
			# Keep has_key style for Py2.4 familiarity / consistency
			if not groups.has_key(iEra):
				groups[iEra] = []
			groups[iEra].append((szName, iReligion))

	# Optional sorting within each bucket
	if bSortLists:
		noTech.sort()
		for k in groups.keys():
			groups[k].sort()

	# "No Tech Prerequisite" group first
	if noTech:
		religionsList.append((lt.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
		for x in noTech:
			religionsList.append(x)

	# Era groups in order
	for iEraLoop in range(iNumEras):
		tmp = groups.get(iEraLoop, None)
		if not tmp:
			continue

		if religionsList:
			religionsList.append(("", -1))

		religionsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))
		for x in tmp:
			religionsList.append(x)

	return religionsList

# Helper to group corporations by era for Sevopedia lists, mirroring the building/unit/tech patterns.
def SAS_getCorporationsGroupedByEra_fromBaseList(baseList, gc, bSortLists, localText=None, getCorporationAvailabilityEraFn=None):
	# getCorporationAvailabilityEraFn signature:
	#   fn(iCorporation, iNumBuildingAndTechs) -> iEra / -1 / None
	lt = _SAS_getLocalText(localText)

	# Default to the shared availability-era helper in this module (no SevoPediaMain dependency).
	if getCorporationAvailabilityEraFn is None:
		def getCorporationAvailabilityEraFn(iCorporation, iNumBuildingAndTechs):
			return SAS_getCorporationAvailabilityEra(iCorporation, iNumBuildingAndTechs, gc)

	corpsList = []

	iNumEras = gc.getNumEraInfos()
	iNumBuildingAndTechs = gc.getNUM_BUILDING_AND_TECH_PREREQS()

	noTech = []
	groups = {}  # iEra -> [(szName, iCorporation), ...]

	for (szName, iCorporation) in baseList:
		iEra = getCorporationAvailabilityEraFn(iCorporation, iNumBuildingAndTechs)
		if iEra is None:
			continue

		if iEra == -1:
			noTech.append((szName, iCorporation))
		else:
			if iEra not in groups:
				groups[iEra] = []
			groups[iEra].append((szName, iCorporation))

	if bSortLists:
		noTech.sort()
		for k in groups.keys():
			groups[k].sort()

	if noTech:
		corpsList.append((lt.getText("TXT_KEY_PEDIA_NO_TECH_PREREQUISITE", ()), -1))
		for x in noTech:
			corpsList.append(x)

	for iEraLoop in range(iNumEras):
		tmp = groups.get(iEraLoop, None)
		if not tmp:
			continue

		if corpsList:
			corpsList.append(("", -1))

		corpsList.append((gc.getEraInfo(iEraLoop).getDescription() + " " + lt.getText("TXT_KEY_PEDIA_ERA", ()), -1))
		for x in tmp:
			corpsList.append(x)

	return corpsList

# <!-- custom: in sevopedia specialists, group specialists by type: regular specialists vs great specialists (those whose <Type> contains "GREAT_"), based on RFC DOC mod's code thanks. Added with the help of chatgpt 5.2 thanks -->
# Notes (kept conservative)
# 	- “Great specialists” detection is exactly RFC’s convention: getType().find("GREAT_") > -1. 
# 	- I reused TXT_KEY_PEDIA_CATEGORY_SPECIALIST for the regular header (so it’s localized), and I used the literal string "Great Specialists" for the great header (since your mod likely doesn’t have RFC’s TXT_KEY_PEDIA_HEADER_GREAT_SPECIALIST). If you want, you can later add your own TXT_KEY and swap that line to localText.getText("TXT_KEY_PEDIA_HEADER_GREAT_SPECIALIST", ()).
def SAS_getSpecialistsGroupedByType(gc, bSortLists, localText=None):
	lt = _SAS_getLocalText(localText)

	specialistsList = []
	greatSpecialistsList = []

	# One pass: preserve XML order when Sort Lists is OFF.
	for iSpecialist in range(gc.getNumSpecialistInfos()):
		info = gc.getSpecialistInfo(iSpecialist)
		if not info or info.isGraphicalOnly():
			continue

		szName = info.getDescription()
		szType = info.getType()

		if szType and (szType.find("GREAT_") > -1):
			greatSpecialistsList.append((szName, iSpecialist))
		else:
			specialistsList.append((szName, iSpecialist))

	# Optional sorting within each group
	if bSortLists:
		specialistsList.sort()
		greatSpecialistsList.sort()

	outList = []

	if specialistsList:
		# Reuse the category label for a localized "Specialists" header.
		outList.append((lt.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST", ()), -1))
		for x in specialistsList:
			outList.append(x)

	if specialistsList and greatSpecialistsList:
		outList.append(("", -1))  # spacer between groups

	if greatSpecialistsList:
		outList.append(("Great Specialists", -1))
		for x in greatSpecialistsList:
			outList.append(x)

	return outList

# <!-- custom: in sevopedia civics, order civics by civic type (e.g. Government, Economy, etc.), as RFC DOC mod does and that this code is based on, with the help of chatgpt 5.2 thanks -->
# Step 2: Replace getCivicList() with “category + era tiers” (behind a SAS define)
# Right now your civics list is just getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo) (optionally alphabetical via BUG).
# In RFC DoC, placeCivics() at least groups by civic option category using header rows. They also show how they do era tier grouping for other lists (e.g., wonders/buildings grouped by prereq tech era).
def SAS_getCivicsGroupedByCivicOption(gc, bSortLists):
	civicsList = []
	iNumCivics = gc.getNumCivicInfos()
	iNumOptions = gc.getNumCivicOptionInfos()

	# One pass: bucket civics by option (preserves XML order naturally)
	groups = [[] for _ in range(iNumOptions)]
	for iCivic in range(iNumCivics):
		info = gc.getCivicInfo(iCivic)
		if info.isGraphicalOnly():
			continue
		iOption = info.getCivicOptionType()
		if iOption >= 0 and iOption < iNumOptions:
			groups[iOption].append((info.getDescription(), iCivic))

	# Emit in option order (Government, Legal, Labor, etc.)
	for iOption in range(iNumOptions):
		tmp = groups[iOption]
		if not tmp:
			continue

		# If BUG "Sort Lists" is ON, alphabetize within each option group
		if bSortLists:
			tmp.sort()

		if civicsList:
			civicsList.append(("", -1))  # spacer between groups
		civicsList.append((gc.getCivicOptionInfo(iOption).getDescription(), -1))  # header

		for x in tmp:
			civicsList.append(x)

	return civicsList
