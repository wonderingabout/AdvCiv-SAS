#
#	FILE:	 Islands.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - Generates a world full of random islands.
# Modified by Sam Trenholme to generate a desert world
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#
# 2017 note: While this map script has a proprietary copyright, evidence
#	indicates that it has always been the intention of Fixaxis that 
# 	users make and freely distribute modifieds version of their map 
#	scripts. The Civilization 4 webpage states that Civilization 4 is 
#	"Designed from the ground up for modability" and 2K Games, the 
#	publisher of the original Windows version, distributes third
#	party mods at https://www.2kgames.com/civ4/modcentral.htm and
#       stated they were looking forward to seeing mods at
#       https://www.2kgames.com/civ4/blog_03.htm

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()
heightMap = []

def getTopLatitude():
        return 0
def getBottomLatitude():
        return 0
def addRivers():
        return
def addLakes():
        return

# Map size
def getGridSize(x):
	[y] = x
	if y <= 0:
		return (4,4) # 16x16, DUEL
	elif y == 1:
		return (6,6) # 24x24, TINY
	elif y == 2:
		return (8,8) # 32x32, SMALL
	elif y == 3:
		return (12,12) # 48x48, STANDARD
	elif y == 4:
		return (15,15) # 60x60, LARGE
	elif y == 5:
		return (20,20) # 80x80, HUGE
	else:
		return (y*4, y*4) # Some mods have super-huge map options

def getDescription():
	return "Big desert, isolated livable areas"

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def getNumCustomMapOptions():
	return 4
	
def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Number of large non-desert areas",
		1:	"Number of small non-desert areas",
		2:  "World map",
		3:  "Resources"
		}
	return option_names[iOption]
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	4,
		2:  3,
		3:  2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "One per player",
			1: "Extra large non-deserts",
			2: "Several non-deserts"
			},
		1:	{
			0: "No tiny non-deserts",
			1: "Few tiny non-deserts",
			2: "Some tiny non-deserts",
			3: "Many tiny non-deserts"
			},
		2:	{
			0: "Flat",
			1: "Desert planet",
			2: "Toric"
			},
		3:	{
			0: "Standard",
			1: "Balanced"
			}
		}
	return selection_names[iOption][iSelection]
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	3,
		2:  0,
		3:  0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	true,
		2:	false,
		3:  false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(2) == 1 or map.getCustomMapOption(2) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(2) == 2)
	
def normalizeAddExtras():
	if (CyMap().getCustomMapOption(3) == 1):
		balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if (CyMap().getCustomMapOption(3) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def beforeGeneration():
	global iNumRegions
	global iExtras
	global regions_in_use
	global remaining_regions
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	userInputLargeIslands = map.getCustomMapOption(0)
	iPlayers = gc.getGame().countCivPlayersEverAlive()

	# Error catching.
	if iPlayers < 1 or iPlayers > 9:
		return None

	# Number of Large Islands: templates.
	if userInputLargeIslands == 0: # One per Player
		configs = [0, 4, 4, 4, 6, 8, 8, 12, 12, 12, 15, 15, 15, 15, 20, 20, 20, 24, 24]
		iExtras = 0
	elif userInputLargeIslands == 2: # Several Extras
		configs = [0, 4, 4, 6, 8, 8, 12, 12, 12, 15, 15, 15, 20, 20, 20, 24, 24, 24, 24]
		extras_min_list = [0, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 3, 4, 4, 4, 4]
		extras_max_list = [0, 3, 2, 3, 3, 3, 5, 5, 4, 6, 5, 4, 7, 7, 6, 8, 8, 7, 6]
		extras_min = extras_min_list[iPlayers]
		extras_max = extras_max_list[iPlayers]
		if extras_min == extras_max:
			iExtras = extras_min
		else:
			extras_range = dice.get((extras_max - extras_min + 1), "Extra Islands - Islands PYTHON")
			iExtras = extras_min + extras_range
	else:
		configs = [0, 4, 4, 6, 6, 8, 8, 12, 12, 12, 15, 15, 15, 15, 20, 20, 20, 24, 24]
		extras_min_list = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 2]
		extras_max_list = [0, 2, 1, 2, 2, 2, 2, 3, 3, 2, 3, 3, 3, 2, 3, 4, 4, 4, 4]
		extras_min = extras_min_list[iPlayers]
		extras_max = extras_max_list[iPlayers]
		if extras_min == extras_max:
			iExtras = extras_min
		else:
			extras_range = dice.get((extras_max - extras_min + 1), "Extra Islands - Islands PYTHON")
			iExtras = extras_min + extras_range
		
	# Choose a "Large Islands" template.
	iNumRegions = configs[iPlayers]
	# Some regions may go unused. We need to track the ones that have been used.
	regions_in_use = []
	remaining_regions = []
	for loopy in range(iNumRegions): # I'm going LOOPY! Loopy, I tell you. ;)
		remaining_regions.append(loopy)

	# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
	templates = {4: {0: [0.0, 0.5, 0.1, 0.45],
	                 1: [0.5, 1.0, 0.1, 0.45],
	                 2: [0.0, 0.5, 0.55, 0.9],
	                 3: [0.5, 1.0, 0.55, 0.9]},
	             6: {0: [0.0, 0.333, 0.1, 0.45],
	                 1: [0.333, 0.667, 0.1, 0.45],
	                 2: [0.667, 1.0, 0.1, 0.45],
	                 3: [0.0, 0.333, 0.55, 0.9],
	                 4: [0.333, 0.667, 0.55, 0.9],
	                 5: [0.667, 1.0, 0.55, 0.9]},
	             8: {0: [0.0, 0.25, 0.1, 0.45],
	                 1: [0.25, 0.5, 0.1, 0.45],
	                 2: [0.5, 0.75, 0.1, 0.45],
	                 3: [0.75, 1.0, 0.1, 0.45],
	                 4: [0.0, 0.25, 0.55, 0.9],
	                 5: [0.25, 0.5, 0.55, 0.9],
	                 6: [0.5, 0.75, 0.55, 0.9],
	                 7: [0.75, 1.0, 0.55, 0.9]},
	             12: {0: [0.0, 0.25, 0.1, 0.35],
	                  1: [0.25, 0.5, 0.1, 0.35],
	                  2: [0.5, 0.75, 0.1, 0.35],
	                  3: [0.75, 1.0, 0.1, 0.35],
	                  4: [0.0, 0.25, 0.4, 0.6],
	                  5: [0.25, 0.5, 0.4, 0.6],
	                  6: [0.5, 0.75, 0.4, 0.6],
	                  7: [0.75, 1.0, 0.4, 0.6],
	                  8: [0.0, 0.25, 0.65, 0.9],
	                  9: [0.25, 0.5, 0.65, 0.9],
	                  10: [0.5, 0.75, 0.65, 0.9],
	                  11: [0.75, 1.0, 0.65, 0.9]},
	             15: {0: [0.0, 0.2, 0.1, 0.35],
	                  1: [0.2, 0.4, 0.1, 0.35],
	                  2: [0.4, 0.6, 0.1, 0.35],
	                  3: [0.6, 0.8, 0.1, 0.35],
	                  4: [0.8, 1.0, 0.1, 0.35],
	                  5: [0.0, 0.2, 0.4, 0.6],
	                  6: [0.2, 0.4, 0.4, 0.6],
	                  7: [0.4, 0.6, 0.4, 0.6],
	                  8: [0.6, 0.8, 0.4, 0.6],
	                  9: [0.8, 1.0, 0.4, 0.6],
	                  10: [0.0, 0.2, 0.65, 0.9],
	                  11: [0.2, 0.4, 0.65, 0.9],
	                  12: [0.4, 0.6, 0.65, 0.9],
	                  13: [0.6, 0.8, 0.65, 0.9],
	                  14: [0.8, 1.0, 0.65, 0.9]},
	             20: {0: [0.0, 0.2, 0.1, 0.29],
	                  1: [0.2, 0.4, 0.1, 0.29],
	                  2: [0.4, 0.6, 0.1, 0.29],
	                  3: [0.6, 0.8, 0.1, 0.29],
	                  4: [0.8, 1.0, 0.1, 0.29],
	                  5: [0.0, 0.2, 0.33, 0.48],
	                  6: [0.2, 0.4, 0.33, 0.48],
	                  7: [0.4, 0.6, 0.33, 0.48],
	                  8: [0.6, 0.8, 0.33, 0.48],
	                  9: [0.8, 1.0, 0.33, 0.48],
	                  10: [0.0, 0.2, 0.52, 0.67],
	                  11: [0.2, 0.4, 0.52, 0.67],
	                  12: [0.4, 0.6, 0.52, 0.67],
	                  13: [0.6, 0.8, 0.52, 0.67],
	                  14: [0.8, 1.0, 0.52, 0.67],
	                  15: [0.0, 0.2, 0.71, 0.9],
	                  16: [0.2, 0.4, 0.71, 0.9],
	                  17: [0.4, 0.6, 0.71, 0.9],
	                  18: [0.6, 0.8, 0.71, 0.9],
	                  19: [0.8, 1.0, 0.71, 0.9]},
	             24: {0: [0.0, 0.167, 0.1, 0.29],
	                  1: [0.167, 0.333, 0.1, 0.29],
	                  2: [0.333, 0.5, 0.1, 0.29],
	                  3: [0.5, 0.667, 0.1, 0.29],
	                  4: [0.667, 0.833, 0.1, 0.29],
	                  5: [0.833, 1.0, 0.1, 0.29],
	                  6: [0.0, 0.167, 0.33, 0.48],
	                  7: [0.167, 0.333, 0.33, 0.48],
	                  8: [0.333, 0.5, 0.33, 0.48],
	                  9: [0.5, 0.667, 0.33, 0.48],
	                  10: [0.667, 0.833, 0.33, 0.48],
	                  11: [0.833, 1.0, 0.33, 0.48],
	                  12: [0.0, 0.167, 0.52, 0.67],
	                  13: [0.167, 0.333, 0.52, 0.67],
	                  14: [0.333, 0.5, 0.52, 0.67],
	                  15: [0.5, 0.667, 0.52, 0.67],
	                  16: [0.667, 0.833, 0.52, 0.67],
	                  17: [0.833, 1.0, 0.52, 0.67],
	                  18: [0.0, 0.167, 0.71, 0.9],
	                  19: [0.167, 0.333, 0.71, 0.9],
	                  20: [0.333, 0.5, 0.71, 0.9],
	                  21: [0.5, 0.667, 0.71, 0.9],
	                  22: [0.667, 0.833, 0.71, 0.9],
	                  23: [0.833, 1.0, 0.71, 0.9]}
	}
	# End of template data.

	# List region_coords: [WestLon, EastLon, SouthLat, NorthLat]
	global region_coords
	region_coords = templates[iNumRegions]
		
class IslandsMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		iPlayers = self.gc.getGame().countCivPlayersEverAlive()
		userInputTinyIslands = self.map.getCustomMapOption(1)
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		# Add the Tiny Islands first (if appropriate).
		if userInputTinyIslands == 0: pass # No tinies.
		else:
			tiny_one = [[-1, -1], [92, 6], [91, 5], [85, 5]]
			[tinyWater, tinyGrain] = tiny_one[userInputTinyIslands]
			self.generatePlotsInRegion(tinyWater,
			                           self.iW, self.iH,
			                           0, 0,
			                           tinyGrain, 4,
			                           self.iHorzFlags, self.iTerrainFlags,
			                           7, 6,
			                           True, 15,
			                           -1, False,
			                           False
			                           )

		# Add the Large Islands (two fractals each to ensure cohesion).
		global iExtras
		global region_coords
		global regions_in_use
		global remaining_regions
		for region_loop in range(iPlayers + iExtras):
			# Choose an unused region in which to place a Large Island.
			region_roll = self.dice.get(len(remaining_regions), "Extra Islands - Islands PYTHON")
			thisRegion = remaining_regions[region_roll]
			regions_in_use.append(thisRegion)
			del remaining_regions[region_roll]

			# Region dimensions
			[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
			iWestX = int(self.iW * fWestLon)
			iEastX = int(self.iW * fEastLon) - 1
			iSouthY = int(self.iH * fSouthLat)
			iNorthY = int(self.iH * fNorthLat) -1
			iWidth = iEastX - iWestX + 1
			iHeight = iNorthY - iSouthY + 1

			# Each island only takes up approximately 63% of the space in its region.
			# This space is further divided between land and water. (These islands are fairly small!)
			# Islands get different shapes and offsets to vary their appearance and placement.
			# Choose a pattern for this Large Island.
			thisIslandPattern = self.dice.get(4, "Island Pattern - Islands PYTHON")
			if thisIslandPattern == 1: # Square island, offset.
				iOffSetX = self.dice.get(int(iWidth * 0.2) + 1, "Island Offset - Islands PYTHON")
				iOffSetY = self.dice.get(int(iHeight * 0.2) + 1, "Island Offset - Islands PYTHON")
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(iWidth * 0.8)
				regHeight = int(iHeight * 0.8)
			elif thisIslandPattern == 2: # Tall island, offset.
				iOffSetX = self.dice.get(int(iWidth * 0.37) + 1, "Island Offset - Islands PYTHON")
				iOffSetY = 0
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(iWidth * 0.63)
				regHeight = iHeight
			elif thisIslandPattern == 3: # Wide island, offset.
				iOffSetX = 0
				iOffSetY = self.dice.get(int(iHeight * 0.37) + 1, "Island Offset - Islands PYTHON")
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = iWidth
				regHeight = int(iHeight * 0.63)
			else: # thisIslandPattern == 0, Square island, centered.
				iOffSetX = int(iWidth * 0.1)
				iOffSetY = int(iHeight * 0.1)
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(iWidth * 0.8)
				regHeight = int(iHeight * 0.8)

			# Vary the shoreline
			shore_grain = 1 + self.dice.get(3, "Random Shoreline Type - Islands PYTHON")

			self.generatePlotsInRegion(55 + sea,
			                           regWidth, regHeight,
			                           regWestX, regSouthY,
			                           shore_grain, 4,
			                           self.iRoundFlags, self.iTerrainFlags,
			                           6, 6,
			                           True, 3,
			                           -1, False,
			                           False
			                           )

			# Core fractal to increase cohesion
			coreWestX = regWestX + int(regWidth * 0.25)
			coreEastX = coreWestX + int(regWidth * 0.5)
			coreSouthY = regSouthY + int(regHeight * 0.25)
			coreNorthY = coreSouthY + int(regHeight * 0.5)
			coreWidth = coreEastX - coreWestX + 1
			coreHeight = coreNorthY - coreSouthY + 1

			self.generatePlotsInRegion(65,
			                           coreWidth, coreHeight,
			                           coreWestX, coreSouthY,
			                           1, 3,
			                           self.iHorzFlags, self.iTerrainFlags,
			                           5, 5,
			                           True, 3,
			                           -1, False,
			                           False
			                           )

		# All regions have been processed. Plot Type generation completed.
		return self.wholeworldPlotTypes

'''
Regional Variables Key:

iWaterPercent,
iRegionWidth, iRegionHeight,
iRegionWestX, iRegionSouthY,
iRegionGrain, iRegionHillsGrain,
iRegionPlotFlags, iRegionTerrainFlags,
iRegionFracXExp, iRegionFracYExp,
bShift, iStrip,
rift_grain, has_center_rift,
invert_heights
'''

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Islands) ...")
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()

	# Check for valid number of players.
	if iPlayers > 0 and iPlayers < 10: pass
	else: # Error catching.
		fractal_world = FractalWorld()
		fractal_world.initFractal(polar = True)
		plotTypes = fractal_world.generatePlotTypes()
		return plotTypes

	fractal_world = IslandsMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	qPlotTypes = []
	for square in plotTypes:
		if square==PlotTypes.PLOT_OCEAN:
			square = PlotTypes.PLOT_LAND
			heightMap.append(0)
		else:
			heightMap.append(1)
		qPlotTypes.append(square)
	return qPlotTypes

def generateTerrainTypes():
	print "terrain"
	NiTextOut("Generating Terrain (Python Islands) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	rTerrain = []
	b = 0
	for a in terrainTypes:
		if heightMap[b] != 1:
			rTerrain.append(2) # Desert
		elif a == 3 or a == 4: # Tundra or snow
			rTerrain.append(0) # Grassland
		else:
			rTerrain.append(a)
		b = b + 1
	return rTerrain

def addFeatures():
	print "features"
	NiTextOut("Adding Features (Python Islands) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

#def assignStartingPlots():
#	return None
	
def normalizeRemovePeaks():
	return None
