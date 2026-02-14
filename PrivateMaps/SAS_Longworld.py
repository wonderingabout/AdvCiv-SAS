# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# FILE: SAS_Longworld.py
# PURPOSE: Lightweight long-format world map for AdvCiv-SAS.
#
# AUTHORS: wonderingabout & GPT-5.3-Codex
# <!-- custom: inspired by the Ringworld3 v1.02 map -->


from CvPythonExtensions import *
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator


def getVersion():
	return "1.00"


def getDescription():
	return "A lightweight long-format world for AdvCiv-SAS: one connected horizontal landmass with wavy borders, inspired by Ringworld3_102_mst.py but heavily simplified."


def isAdvancedMap():
	"This map should show up in Simple Game."
	# <!-- custom: No custom map options in this script, so the stale multi-option/Simple Game cache guard is not needed (empirically verified in-game). (GPT-5.3-Codex) -->
	return 0


def getWrapX():
	return True


def getWrapY():
	return False


def getTopLatitude():
	return 70


def getBottomLatitude():
	return -70


def minStartingDistanceModifier():
	# <!-- custom: Tight long-strip maps need very low min start distance so high player-count games don't fail start assignment. (GPT-5.3-Codex) -->
	return -95


def getStripBounds(iH):
	# <!-- custom: Keep one connected horizontal land strip, but thicken it on taller maps to avoid overly cramped land. (GPT-5.3-Codex) -->
	iBandHeight = 2
	if iH >= 8:
		iBandHeight = 5
	elif iH >= 6:
		iBandHeight = 4
	elif iH >= 5:
		iBandHeight = 3

	iTopRow = max(1, (iH / 2) - (iBandHeight / 2))
	iBottomRow = iTopRow + iBandHeight - 1
	if iBottomRow > iH - 2:
		iBottomRow = iH - 2
		iTopRow = max(1, iBottomRow - iBandHeight + 1)
	return (iTopRow, iBottomRow)


def findStartingPlot(argsList):
	# <!-- custom: Force starts onto the long central strip with even horizontal spacing so high player-count games always get valid starts. (GPT-5.3-Codex) -->
	[playerID] = argsList
	gc = CyGlobalContext()
	map_obj = CyMap()
	iW = map_obj.getGridWidth()
	iH = map_obj.getGridHeight()
	(iTopRow, iBottomRow) = getStripBounds(iH)
	strip_rows = range(iTopRow, iBottomRow + 1)

	player_ids = []
	for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.isAlive():
			player_ids.append(iPlayer)

	if len(player_ids) == 0:
		CyPythonMgr().allowDefaultImpl()
		return

	player_ids.sort()
	if playerID not in player_ids:
		CyPythonMgr().allowDefaultImpl()
		return

	iIndex = player_ids.index(playerID)
	iCount = len(player_ids)
	iMargin = 2
	iSpan = max(1, iW - 2 * iMargin)
	iX = iMargin + (iIndex * iSpan) / iCount
	if iX >= iW:
		iX = iW - 1
	iY = strip_rows[iIndex % len(strip_rows)]

	pPlot = map_obj.plot(iX, iY)
	if pPlot.isWater() or pPlot.isImpassable():
		for dx in range(iW):
			iTryX = (iX + dx) % iW
			for iTryY in strip_rows:
				pTry = map_obj.plot(iTryX, iTryY)
				if not pTry.isWater() and not pTry.isImpassable():
					return map_obj.plotNum(iTryX, iTryY)
		CyPythonMgr().allowDefaultImpl()
		return

	return map_obj.plotNum(iX, iY)


def getGridSize(argsList):
	if argsList[0] == -1:
		return []

	grid_sizes = {
		0:									( 7, 4),  # ARENA
		WorldSizeTypes.WORLDSIZE_DUEL:		(10, 4),
		WorldSizeTypes.WORLDSIZE_TINY:		(15, 5),
		WorldSizeTypes.WORLDSIZE_SMALL:		(23, 6),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(29, 6),
		WorldSizeTypes.WORLDSIZE_LARGE:		(34, 6),
		WorldSizeTypes.WORLDSIZE_HUGE:		(44, 6),
	}

	[eWorldSize] = argsList
	if eWorldSize in grid_sizes:
		return grid_sizes[eWorldSize]

	# <!-- custom: For post-Huge SAS sizes, keep long-map height and scale width by default player ratio from Huge anchor. (GPT-5.3-Codex) -->
	gc = CyGlobalContext()
	if eWorldSize > WorldSizeTypes.WORLDSIZE_HUGE and eWorldSize < gc.getNumWorldInfos():
		(iAnchorWidth, iAnchorHeight) = grid_sizes[WorldSizeTypes.WORLDSIZE_HUGE]
		iAnchorPlayers = max(1, gc.getWorldInfo(WorldSizeTypes.WORLDSIZE_HUGE).getDefaultPlayers())
		iTargetPlayers = max(1, gc.getWorldInfo(eWorldSize).getDefaultPlayers())
		iTargetWidth = max(iAnchorWidth + 1, int((float(iAnchorWidth) * float(iTargetPlayers)) / float(iAnchorPlayers) + 0.5))
		return (iTargetWidth, iAnchorHeight)

	return grid_sizes[WorldSizeTypes.WORLDSIZE_HUGE]


def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python SAS_Longworld) ...")
	map_obj = CyMap()
	iW = map_obj.getGridWidth()
	iH = map_obj.getGridHeight()
	dice = CyGlobalContext().getGame().getMapRand()
	plot_types = [PlotTypes.PLOT_OCEAN] * (iW * iH)

	# <!-- custom: Build one continuous horizontal land strip (single connected landmass) centered on the map. (GPT-5.3-Codex) -->
	if iH < 3:
		for x in range(iW):
			plot_types[map_obj.plotNum(x, 0)] = PlotTypes.PLOT_LAND
		return plot_types

	(iTopRow, iBottomRow) = getStripBounds(iH)
	iBaseBandHeight = iBottomRow - iTopRow + 1
	iMinBandHeight = max(3, iBaseBandHeight - 2)
	iPrevTop = iTopRow
	iPrevBottom = iBottomRow
	for x in range(iW):
		iTopTrim = 0
		iBottomTrim = 0
		if dice.get(100, "SAS_Longworld border top trim") < 35:
			iTopTrim = 1
			if dice.get(100, "SAS_Longworld border top trim extra") < 10:
				iTopTrim = 2
		if dice.get(100, "SAS_Longworld border bottom trim") < 35:
			iBottomTrim = 1
			if dice.get(100, "SAS_Longworld border bottom trim extra") < 10:
				iBottomTrim = 2

		iLocalTop = iTopRow + iTopTrim
		iLocalBottom = iBottomRow - iBottomTrim
		if iLocalBottom - iLocalTop + 1 < iMinBandHeight:
			iLocalTop = iTopRow
			iLocalBottom = iBottomRow

		iLocalTop = max(iPrevTop - 1, min(iPrevTop + 1, iLocalTop))
		iLocalBottom = max(iPrevBottom - 1, min(iPrevBottom + 1, iLocalBottom))
		if iLocalBottom - iLocalTop + 1 < iMinBandHeight:
			iLocalTop = iPrevTop
			iLocalBottom = iPrevBottom

		for y in range(iLocalTop, iLocalBottom + 1):
			plot_types[map_obj.plotNum(x, y)] = PlotTypes.PLOT_LAND

		iPrevTop = iLocalTop
		iPrevBottom = iLocalBottom

	# Add sparse hills/peaks on the strip for texture, but keep enough flat plots for starts.
	for x in range(iW):
		for y in range(iTopRow, iBottomRow + 1):
			i = map_obj.plotNum(x, y)
			if plot_types[i] != PlotTypes.PLOT_LAND:
				continue
			iChance = dice.get(20, "SAS_Longworld hills")
			if iChance <= 2:
				plot_types[i] = PlotTypes.PLOT_HILLS

	return plot_types


def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python SAS_Longworld) ...")
	terrain_gen = TerrainGenerator()
	return terrain_gen.generateTerrain()


def addFeatures():
	NiTextOut("Adding Features (Python SAS_Longworld) ...")
	feature_gen = FeatureGenerator()
	feature_gen.addFeatures()
	return 0
