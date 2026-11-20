#
#	FILE:	 Equal Islands V2.py
#	AUTHOR:  Axius
#	CONTRIB: Bob Thomas (Sirian)
#	PURPOSE: Based on Sirian's Islands script, but all islands are identical.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
import random
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()
balancer.resourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM')
balancer.resourcesToEliminate = ('', )

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_ISLANDS_DESCR"
	
def getDescriptionTitle():
	return "A traditional BTS Map"
	
def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return ""	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Play 'Mirror Hub' for 'Equal Island' start (OCC, Peace CTON...), you may want to choose 'Resource - Extra' for that too"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Best suited for peacul development, either Ironman, OCC, or Peace CTON"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "It's a long term map so long term traits (like Financial or Philosophical) and Civilization will be proportionally stronger here"		

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def getNumCustomMapOptions():
	return 13
	
def getNumHiddenCustomMapOptions():
	return 0

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "Circumnavigation",
		2:	"TXT_KEY_CONCEPT_RESOURCES",
		3:	"Mirrored Hubs",
		4:	"Land Size",			
		5:	"Desert and Tundra",
		6:	"Island Shape",
		7:	"BTG Resources",		
		8:	"BTG Forest Type",		
		9: 	"Starting Units",
		10:	"BTG Spectator Notes",
		11:	"Notes",
		12:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2,
		2:	3,
		3:	2,
		4:	3,
		5:	3,
		6:	5,
		7:	2,
		8:	5,
		9:	2,
		10:	2,
		11:	1,
		12:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "Normal (Off if not enough land)",
			1: "Forced Disabled (BTS Hardcoded, BTG via option)"
			},				
		2:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "TXT_KEY_MAP_SCRIPT_EXTRAS"
			},
		3:	{
			0: "No",
			1: "Yes"
			},			
		4:	{
			0: "Normal",
			1: "More Land, less water",
			2: "Much More Land, limited water"
			},
		5:	{
			0: "Normal",
			1: "None - replace by grassland",
			2: "None - replace by marsh (BTG)"
			},	
		6:	{
			0: "Any shape",
			1: "Squared Islands",
			2: "Tall Islands",
			3: "Wide Islands",
			4: "Squared and centered Islands"		
			},
		7:	{
			0: "No",
			1: "Yes - Strategic only on fixed, predetermined, tiles"		
			},	
		8:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},			
		9:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},
		10:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in FIRST slot"			
			},			
		11:	{
			0: "Land size overrides sea level, it reduces sea even lower if you choose not normal"
			},
		12:	{
			0: "Penny for Beyond The Game - Works for BTS, BTG Options have no effect"		
			}				
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	0,
		2:	1,
		3:	0,
		4:	1,
		5:	1,
		6:	1,
		7:	0,
		8:	0,
		9:	0,
		10:	0,
		11:	0,
		12:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	False,
		1:	False,
		1:	False,
		2:	True,
		3:	True,
		4:	True,
		5:	False,
		6:	True,
		7:	False,
		8:	True,
		9:	False,
		10: False,
		11:	False,
		12:	False,
		}
	return option_random[iOption]

def getWrapX():	return (iOptionValue_Wrap == 1 or iOptionValue_Wrap == 2)
	
def getWrapY():	return (iOptionValue_Wrap == 2)
	
def beforeInit():#2.41

	beforeInitOptionsValue()	
	
	global isBTPon#2.22
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False		
	
def beforeInitOptionsValue():#2.41
	
	global iOptionValue_Wrap
	global iOptionValue_Circumnavigation
	global iOptionValue_Resources	
	global iOptionValue_Mirror	
	global iOptionValue_LandSize
	global iOptionValue_DesertTundra
	global iOptionValue_IslandShape
	global iOptionValue_ResourcesBTG
	global iOptionValue_ForestType
	global iOptionValue_StartingUnit
		
	iOptionValue_Wrap = CyMap().getCustomMapOption(0)
	iOptionValue_Circumnavigation = CyMap().getCustomMapOption(1)
	iOptionValue_Resources = CyMap().getCustomMapOption(2)
	iOptionValue_Mirror = CyMap().getCustomMapOption(3)
	iOptionValue_LandSize = CyMap().getCustomMapOption(4)
	iOptionValue_DesertTundra = CyMap().getCustomMapOption(5)
	iOptionValue_IslandShape = CyMap().getCustomMapOption(6)
	iOptionValue_ResourcesBTG = CyMap().getCustomMapOption(7)
	iOptionValue_ForestType = CyMap().getCustomMapOption(8)
	iOptionValue_StartingUnit = CyMap().getCustomMapOption(9)
	
def beforeGeneration():
	global iNumRegions
	global regions_in_use
	global remaining_regions
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	iPlayers = gc.getGame().countCivPlayersEverAlive()


	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		return None

	# Number of Large Islands: One per Player
	configs = [0, 4, 4, 4, 4, 6, 6, 8, 8, 12, 15, 15, 15, 15, 20, 20, 20, 24, 24]
		
	# Choose a "Large Islands" template.
	iNumRegions = configs[iPlayers]
	# Some regions may go unused. We need to track the ones that have been used.
	regions_in_use = []
	remaining_regions = []
	for loopy in range(iNumRegions): 
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

	# Translate region_coords to actual X,Y
	global regionWidth
	global regionHeight
	regionWidth,regionHeight = 1000,1000
	for reg in range(len(region_coords)):
		[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[reg]
		iWestX = int(iW * fWestLon)
		iEastX = int(iW * fEastLon) - 1
		iSouthY = int(iH * fSouthLat)
		iNorthY = int(iH * fNorthLat) -1
		region_coords[reg] = [iWestX, iEastX, iSouthY, iNorthY]
		iWidth = iEastX - iWestX + 1
		iHeight = iNorthY - iSouthY + 1
		if iWidth < regionWidth:
			regionWidth = iWidth
		if iHeight < regionHeight:
			regionHeight = iHeight
		
class IslandsMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		iPlayers = self.gc.getGame().countCivPlayersEverAlive()
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		#2.15 this is an override
		if (iOptionValue_LandSize == 1):		
			sea = -12
		if (iOptionValue_LandSize == 2):		
			sea = -25
			
		# Add the Large Islands (two fractals each to ensure cohesion).
		global region_coords
		global regionWidth
		global regionHeight
		global regions_in_use
		global remaining_regions
		for region_loop in range(iPlayers):
			# Choose an unused region in which to place a Large Island.
			region_roll = self.dice.get(len(remaining_regions), "Extra Islands - Islands PYTHON")
			thisRegion = remaining_regions[region_roll]
			regions_in_use.append(thisRegion)
			del remaining_regions[region_roll]

			# Region dimensions
			[iWestX, iEastX, iSouthY, iNorthY] = region_coords[thisRegion]

			# Each island only takes up approximately 63% of the space in its region.
			# This space is further divided between land and water. (These islands are fairly small!)
			# Islands get different shapes and offsets to vary their appearance and placement.
			# Choose a pattern for this Large Island.
			
			thisIslandPattern = self.dice.get(4, "Island Pattern - Islands PYTHON")
			
			#2.15 don't let this random
			if (iOptionValue_IslandShape >= 1):
				thisIslandPattern = iOptionValue_IslandShape#1-2-3 is ok just copy, 0 is random, and 4 is forced "the else" case
			
			
			if thisIslandPattern == 1: # Square island, offset.
				iOffSetX = self.dice.get(int(regionWidth * 0.2) + 1, "Island Offset - Islands PYTHON")
				iOffSetY = self.dice.get(int(regionHeight * 0.2) + 1, "Island Offset - Islands PYTHON")
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(regionWidth * 0.8)
				regHeight = int(regionHeight * 0.8)
			elif thisIslandPattern == 2: # Tall island, offset.
				iOffSetX = self.dice.get(int(regionWidth * 0.37) + 1, "Island Offset - Islands PYTHON")
				iOffSetY = 0
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(regionWidth * 0.63)
				regHeight = regionHeight
			elif thisIslandPattern == 3: # Wide island, offset.
				iOffSetX = 0
				iOffSetY = self.dice.get(int(regionHeight * 0.37) + 1, "Island Offset - Islands PYTHON")
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = regionWidth
				regHeight = int(regionHeight * 0.63)
			else: # thisIslandPattern == 0, Square island, centered.
				iOffSetX = int(regionWidth * 0.1)
				iOffSetY = int(regionHeight * 0.1)
				regWestX = iWestX + iOffSetX
				regSouthY = iSouthY + iOffSetY
				regWidth = int(regionWidth * 0.8)
				regHeight = int(regionHeight * 0.8)

			# Don't allow the islands to reach the region boundary
			if regWestX <= iWestX:
				regWestX = iWestX + 1
			if regWestX + regWidth >= iWestX + regionWidth:
				regWidth = iWestX + regionWidth - 1 - regWestX
			if regSouthY < iSouthY:
				regSouthY = iSouthY + 1
			if regSouthY + regHeight >= iSouthY + regionHeight:
				regHeight = iSouthY + regionHeight - 1 - regSouthY

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
	if iPlayers > 0 and iPlayers < 19: pass
	else: # Error catching.
		fractal_world = FractalWorld()
		fractal_world.initFractal(polar = True)
		plotTypes = fractal_world.generatePlotTypes()
		return plotTypes

	fractal_world = IslandsMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

def generateTerrainTypes():
	print "terrain"
	NiTextOut("Generating Terrain (Python Islands) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	print "features"
	NiTextOut("Adding Features (Python Islands) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def assignStartingPlots():
	# Custom start plot finder for Islands.
	global iNumRegions
	global region_coords
	global regionWidth
	global regionHeight
	global regions_in_use
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	
	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		CyPythonMgr().allowDefaultImpl()
		return

	# Obtain the minimum crow-flies distance figures [minX, minY] for this map size and number of players.
	minimums = {4: [0.15, 0.1],
	            6: [0.1, 0.1],
	            8: [0.07, 0.1],
	            12: [0.07, 0.07],
	            15: [0.06, 0.07],
	            20: [0.06, 0.05],
	            24: [0.05, 0.05]}
	[minLon, minLat] = minimums[iNumRegions]
	minX = max(3, int(minLon * iW))
	minY = max(3, int(minLat * iH))

	# region_data: [WestX, EastX, SouthY, NorthY, 
	# numLandPlotsinRegion, numCoastalPlotsinRegion,
	# numOceanPlotsinRegion, iRegionNetYield, 
	# iNumLandAreas, iNumPlotsinRegion]
	global region_data
	region_data = {}
	region_best_areas = {}
	region_yields = []
	sorting_regions = []
	for regionLoop in range(len(regions_in_use)):
		thisRegion = regions_in_use[regionLoop]
		# Region dimensions
		[iWestX, iEastX, iSouthY, iNorthY] = region_coords[thisRegion]
		iEastX = iWestX + regionWidth - 1
		iNorthY = iSouthY + regionHeight - 1
		# Plot and Area info.
		iNumLandPlots = 0
		iNumCoastalPlots = 0
		iNumOceanPlots = 0
		iRegionNetYield = 0
		iNumLandAreas = 0
		iNumPlotsinRegion = 0
		land_areas = []
		land_area_plots = {}
		land_area_yield = {}
		# Cycle through all plots in the region.
		for x in range(iWestX, iEastX + 1):
			for y in range(iSouthY, iNorthY + 1):
				iNumPlotsinRegion += 1
				i = y * iW + x
				pPlot = map.plot(x, y)
				if pPlot.getBonusType(-1) != -1: # Count any bonus resource as added value
					iRegionNetYield += 2
				if pPlot.isWater(): # Water plot
					iFertileCheck = pPlot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM)
					if iFertileCheck > 1: # If the plot has extra food, count it.
						iRegionNetYield += (2 * (iFertileCheck - 1))
					if pPlot.isAdjacentToLand(): # Coastal plot
						if pPlot.isFreshWater:
							iNumCoastalPlots += 1
							iRegionNetYield += 2
						else:
							iNumCoastalPlots += 1
							iRegionNetYield += 1
					else:
						iNumOceanPlots += 1
				else: # Land plot
					iNumLandPlots += 1
					iArea = pPlot.getArea()
					iPlotYield = pPlot.calculateTotalBestNatureYield(TeamTypes.NO_TEAM)
					iFertileCheck = pPlot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM)
					if iFertileCheck > 1: # If the plot has extra food, count the extra as double value!
						iPlotYield += (iFertileCheck - 1)
					iRegionNetYield += iPlotYield
					if pPlot.isHills(): iRegionNetYield += 1 # Add a bonus point for Hills plots.
					if not iArea in land_areas: # This plot is the first detected in its AreaID.
						iNumLandAreas += 1
						land_areas.append(iArea)
						land_area_plots[iArea] = 1
						land_area_yield[iArea] = iPlotYield
					else: # This AreaID already known.
						land_area_plots[iArea] += 1
						land_area_yield[iArea] += iPlotYield
		# Sort areas, achieving a list of AreaIDs with best areas first.
		area_yields = land_area_yield.values()
		area_yields.sort()
		area_yields.reverse()
		best_areas = []
		for areaTestLoop in range(iNumLandAreas):
			for landLoop in range(len(land_areas)):
				if area_yields[areaTestLoop] == land_area_yield[land_areas[landLoop]]:
					best_areas.append(land_areas[landLoop])
					del land_areas[landLoop]
					break
		# Store infos to regional lists.
		region_data[thisRegion] = [iWestX, iEastX, iSouthY, iNorthY, 
		                           iNumLandPlots, iNumCoastalPlots,
		                           iNumOceanPlots, iRegionNetYield,
		                           iNumLandAreas, iNumPlotsinRegion]
		region_best_areas[thisRegion] = best_areas
		region_yields.append(iRegionNetYield)
		sorting_regions.append(iRegionNetYield)
		
	# Now sort the regions
	best_regions = []
	region_numbers = regions_in_use
	sorting_regions.sort()
	sorting_regions.reverse()
	for regionTestLoop in range(iNumRegions):
		for yieldLoop in range(len(region_numbers)):
			if sorting_regions[regionTestLoop] == region_yields[yieldLoop]:
				best_regions.append(region_numbers[yieldLoop])
				del region_numbers[yieldLoop]
				del region_yields[yieldLoop]
				break
		
	# Need to discard the worst regions and then reverse the region order.
	# Of the regions that will be used, the worst will be assigned first.
	best_regions.reverse()

	# Obtain player numbers. (Account for possibility of Open slots!)
	player_list = []
	for plrCheckLoop in range(CyGlobalContext().getMAX_CIV_PLAYERS()):#2.35 when you reduce to 12 players... cannot hardcode this
		#2.22 Protecting for BTS
		if isBTPon:
			if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive() and not CyGlobalContext().getPlayer(plrCheckLoop).isSpectator():
				player_list.append(plrCheckLoop)
		else:
			if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
				player_list.append(plrCheckLoop)

	# Shuffle start points so that players are assigned regions at random.
	shuffledPlayers = []
	for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Regions - Islands PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]

	# Find the oceans. We want all civs to start along the coast of a salt water body.
	oceans = []
	for i in range(map.getIndexAfterLastArea()):
		area = map.getArea(i)
		if not area.isNone():
			if area.isWater() and not area.isLake():
				oceans.append(area)
	
	# Now assign the start plots!
	plot_assignments = {}
	min_dist = []
	# Loop through players/regions.
	for assignLoop in range(iPlayers):
		playerID = shuffledPlayers[assignLoop]
		reg = best_regions[assignLoop]
		[westX, eastX, southY, northY] = region_data[reg][0:4]
		iNumAreas = region_data[reg][8]
		area_list = region_best_areas[reg]
		# Print Data for debugging
		# Error Handling (if valid start plot not found, reduce MinDistance)
		while (true):
			iBestValue = 0
			pBestPlot = None
			# Loop through best areas in this region
			for areaLoop in range(iNumAreas):
				areaID = area_list[areaLoop]
				player = gc.getPlayer(playerID)
				player.AI_updateFoundValues(True)
				iRange = player.startingPlotRange()
				iPass = 0
				validFn = None
				# Loop through all plots in the region.
				for iX in range(westX, eastX + 1):
					for iY in range(southY, northY + 1):
						pPlot = map.plot(iX, iY)
						if pPlot.isWater(): continue
						if not pPlot.isCoastalLand(): continue
						if areaID != pPlot.getArea(): continue
						if validFn != None and not validFn(playerID, iX, iY): continue
						val = pPlot.getFoundValue(playerID)
						if val > iBestValue:
							valid = True
							for invalid in min_dist:
								[invalidX, invalidY] = invalid
								if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
									valid = False
									break
							if valid:
								oceanside = False
								for ocean in oceans:
									if pPlot.isAdjacentToArea(ocean):
										oceanside = True
										break
								if not oceanside:
									valid = False # Not valid unless adjacent to an ocean!
							if valid:
								for iI in range(gc.getMAX_CIV_PLAYERS()):
									
									if isBTPon:#2.22 Protecting errors from BTS
										if (gc.getPlayer(iI).isAlive() and not gc.getPlayer(iI).isSpectator()):
											if (iI != playerID):
												if gc.getPlayer(iI).startingPlotWithinRange(pPlot, playerID, iRange, iPass):
													valid = False
													break
										else:
											if (gc.getPlayer(iI).isAlive()):
												if (iI != playerID):
													if gc.getPlayer(iI).startingPlotWithinRange(pPlot, playerID, iRange, iPass):
														valid = False
														break													
													
							if valid:
								iBestValue = val
								pBestPlot = pPlot

				if pBestPlot != None:
					min_dist.append([pBestPlot.getX(), pBestPlot.getY()])
					sPlot = map.plot(pBestPlot.getX(), pBestPlot.getY())
					plrID = gc.getPlayer(playerID)
					plrID.setStartingPlot(sPlot, true)
					break # Valid start found, stop checking areas and plots.
				else: pass # This area too close to somebody, try the next area.
			
			# Check to see if a valid start was found in ANY areaID.
			if pBestPlot == None:
				print "player", playerID, "pass", iPass, "failed"
				iPass += 1
				if iPass <= max(player.startingPlotRange() + eastX - westX, player.startingPlotRange() + northY - southY):
					continue
				else: # A region has failed to produce any valid starts!
					bSuccessFlag = False
					print "---"
					print "A region has failed"
					print "---"
					# Regional start plot assignment has failed. Reverting to default.
					CyPythonMgr().allowDefaultImpl()
					return
			else: break # This player has been assigned a start plot.
			
	# Successfully assigned start plots, continue back to C++
	return None
	
def normalizeRemovePeaks():
	return None

def normalizeAddExtras():
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	global region_coords
	global regionWidth
	global regionHeight
	forest = gc.getInfoTypeForString("FEATURE_FOREST")
	ice = gc.getInfoTypeForString("FEATURE_ICE")
	grass = gc.getInfoTypeForString("TERRAIN_GRASS")
	plains = gc.getInfoTypeForString("TERRAIN_PLAINS")
	desert = gc.getInfoTypeForString("TERRAIN_DESERT")
	ocean = gc.getInfoTypeForString("TERRAIN_OCEAN")
	regMask = []
	regMask = [0] * (iW*iH)
	
	
	#2.15 MEga block 1, if mirror
	if (iOptionValue_Mirror == 1):	
		# Find starting location with a river and the most land around, preferably with most rivers
		best = 0
		player0 = 0
		for i in range(0,gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(i).isAlive():
				start_plot = gc.getPlayer(i).getStartingPlot()
				startx, starty = start_plot.getX(), start_plot.getY()
				quality = 0
				if start_plot.isRiver():
					quality = 100
				for dx in range(-3,4):
					for dy in range(-3,4):
						if dx*dx + dy*dy < 13:
							p = map.plot(startx+dx,starty+dy)
							if not p.isNone():
								if (not p.isImpassable()) and (not p.isWater()):
									quality += 1
									if p.isRiver():
										quality += 1
				if quality > best:
					best = quality
					player0 = i

		start_plot = gc.getPlayer(player0).getStartingPlot() 
		startx0, starty0 = start_plot.getX(), start_plot.getY()

		# find region by location
		westX0, eastX0, southY0, northY0 = 0,1,0,1
		
		
		for reg in range(len(region_coords)):
			[westX0, eastX0, southY0, northY0] = region_coords[reg]
			if (startx0 >= westX0) and (startx0 <= eastX0) and (starty0 >= southY0) and (starty0 <= northY0):
				eastX0 = westX0 + regionWidth - 1
				northY0 = southY0 + regionHeight - 1
				break
				
		# mask region
		for x in range(westX0,eastX0+1):
			for y in range(southY0,northY0+1):
				regMask[y*iW + x] = 1

		if (iOptionValue_Resources == 1):
			balancer.normalizeAddExtras()
		if (iOptionValue_Resources == 2):
			# these are randomly dropped within the city limits on 1st pass:
			resourcesInCity = ('BONUS_GOLD', 'BONUS_GEMS', 'BONUS_CORN', 'BONUS_PIG', 'BONUS_RICE', 'BONUS_SHEEP', 'BONUS_WHEAT', 'BONUS_DEER', 'BONUS_BANANA', 'BONUS_FISH', 'BONUS_CLAM', 'BONUS_CRAB')
			# these are randomly dropped within 2 culture expansions around the city on 2nd pass:
			resourcesNearCity = ('BONUS_COPPER', 'BONUS_IRON', 'BONUS_HORSE', 'BONUS_STONE', 'BONUS_MARBLE', 'BONUS_IVORY', 'BONUS_OIL', 'BONUS_ALUMINUM', 'BONUS_COAL', 'BONUS_URANIUM')
			# these are forcibly added on 3rd pass. only supports land-based resources
			resourcesMustHave = ('BONUS_IRON', 'BONUS_OIL', 'BONUS_ALUMINUM')

			random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots and Bonuses - PYTHON"))

			# Build a list of bonuses
			bonuses = []
			for bonus in range(gc.getNumBonusInfos()):
				bonuses += [bonus]
			random.shuffle(bonuses) # place bonuses in random order

			# Build a list of plots around the city
			plots_city = [] # plots within the city radius
			plots_near = [] # plots within 2 culture expansions
			for dx in range(-3,4):
				for dy in range(-3,4):
					dd = dx*dx + dy*dy
					if (dd > 0) and (dd < 13):
						# check that the tile is in the same region!
						if (startx0+dx >= westX0) and (startx0+dx <= eastX0) and (starty0+dy >= southY0) and (starty0+dy <= northY0):
							p = map.plot(startx0+dx,starty0+dy)
							if not p.isNone():
								plots_near.append(p)
								if dd < 8:
									plots_city.append(p)
			random.shuffle(plots_city) # try plots in random order
			random.shuffle(plots_near)

			# Prepare: remove all existing listed bonuses from the area
			for p in plots_near:
				bonus = p.getBonusType(-1)
				if bonus != BonusTypes.NO_BONUS:
					type_string = gc.getBonusInfo(bonus).getType()
					if (type_string in resourcesInCity) or (type_string in resourcesNearCity):
						p.setBonusType(BonusTypes.NO_BONUS)

			# 1st pass: place bonuses within the city radius
			for bonus in bonuses:
				type_string = gc.getBonusInfo(bonus).getType()
				if type_string in resourcesInCity:
					for p in plots_city:
						if p.canHaveBonus(bonus, True):
							p.setBonusType(bonus)
							break

			# 2nd pass: place bonuses nearby
			for bonus in bonuses:
				type_string = gc.getBonusInfo(bonus).getType()
				if type_string in resourcesNearCity:
					for p in plots_near:
						if p.canHaveBonus(bonus, True):
							p.setBonusType(bonus)
							break

			# 3rd pass: forcibly place the "must have" bonuses
			iPlot = 0
			for bonus in bonuses:
				bInfo = gc.getBonusInfo(bonus)
				type_string = bInfo.getType()
				if type_string in resourcesMustHave:
					have_it = false
					for p in plots_near:
						if p.getBonusType(-1) == bonus:
							have_it = True
							break
					if not have_it:
						p = plots_near[iPlot]
						while ( p.isWater() and (iPlot < len(plots_near)-1) ):
							iPlot += 1
							p = plots_near[iPlot]
						if bInfo.isFlatlands() or not bInfo.isHills():
							p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						elif bInfo.isHills():
							p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
						if not bInfo.isTerrain(p.getTerrainType()):
							tryTerrain = grass
							if not bInfo.isTerrain(tryTerrain):
								tryTerrain = plains
								if not bInfo.isTerrain(tryTerrain):
									tryTerrain = desert
							p.setTerrainType(tryTerrain, True, True)
						p.setFeatureType(FeatureTypes.NO_FEATURE, -1)
						p.setBonusType(bonus)
						iPlot += 1

			# 4th pass: fill any unused plots with forests
			for p in plots_near:
				if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and (p.getFeatureType() == FeatureTypes.NO_FEATURE) and p.canHaveFeature(forest):
					p.setFeatureType(forest, -1)

		# Copy the best starting location to everybody else (entire region)
		
		#2.15 this is the mirror part
		
		for i in range(0,gc.getMAX_CIV_PLAYERS()):
			if (i != player0) and gc.getPlayer(i).isAlive():

				start_plot = gc.getPlayer(i).getStartingPlot()
				startx, starty = start_plot.getX(), start_plot.getY()

				# find region by location
				westX, eastX, southY, northY = 0,1,0,1
				dx = 0
				dy = 0
				for reg in range(len(region_coords)):
					[westX, eastX, southY, northY] = region_coords[reg]
					if (startx >= westX) and (startx <= eastX) and (starty >= southY) and (starty <= northY):
						eastX = westX + regionWidth - 1
						northY = southY + regionHeight - 1
						dx = westX - westX0
						dy = southY - southY0
						break
				# mask region
				for x in range(westX,eastX+1):
					for y in range(southY,northY+1):
						regMask[y*iW + x] = 1

				# copy land
				
				for x in range(westX0,eastX0+1):
					for y in range(southY0,northY0+1):
						p0 = map.plot(x,y)
						p = map.plot(x+dx,y+dy)
						if (not p0.isNone()) and (not p.isNone()):
							p.setPlotType(p0.getPlotType(), True, True)
							p.setTerrainType(p0.getTerrainType(), True, True)
							p.setBonusType(p0.getBonusType(-1))
							p.setImprovementType(p0.getImprovementType())
							# don't change ice
							if p.getFeatureType() != ice:
								f0 = p0.getFeatureType()
								if f0 != ice:
									p.setFeatureType(f0, -1)


				# copy rivers after land, otherwise river crossing counts might be set wrong
				for x in range(westX0,eastX0+1):
					for y in range(southY0,northY0+1):
						p0 = map.plot(x,y)
						p = map.plot(x+dx,y+dy)
						if (not p0.isNone()) and (not p.isNone()):
							p.setNOfRiver(p0.isNOfRiver(), p0.getRiverWEDirection())
							p.setWOfRiver(p0.isWOfRiver(), p0.getRiverNSDirection())

				# move starting location
				start_plot = map.plot(startx0+dx, starty0+dy)
				gc.getPlayer(i).setStartingPlot(start_plot, True)
		

				
				
		# Clear everything outside of the used regions
		for x in range(iW):
			for y in range(iH):
				if regMask[y*iW + x] == 0:
					map.plot(x,y).setBonusType(BonusTypes.NO_BONUS)
					
############################ Part 2 :
	else:## Ok this case I'll change it's the "non-mirro"
	
		# Find starting location with a river and the most land around, preferably with most rivers
		best = 0
		player0 = 0
		for i in range(0,gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(i).isAlive():
				start_plot = gc.getPlayer(i).getStartingPlot()
				startx, starty = start_plot.getX(), start_plot.getY()
				quality = 0
				if start_plot.isRiver():
					quality = 100
				for dx in range(-3,4):
					for dy in range(-3,4):
						if dx*dx + dy*dy < 13:
							p = map.plot(startx+dx,starty+dy)
							if not p.isNone():
								if (not p.isImpassable()) and (not p.isWater()):
									quality += 1
									if p.isRiver():
										quality += 1
				if quality > best:
					best = quality
					player0 = i

		
		#2.15 Okay new bit for this big subpart.... you need to do this for ALL PLAYERS
		
		if (iOptionValue_Resources == 1):
			balancer.normalizeAddExtras()
					
		for i in range(0,gc.getMAX_CIV_PLAYERS()):
			if gc.getPlayer(i).isAlive():

			
				#start_plot = gc.getPlayer(player0).getStartingPlot() 
				start_plot = gc.getPlayer(i).getStartingPlot() 
				startx0, starty0 = start_plot.getX(), start_plot.getY()

				# find region by location
				westX0, eastX0, southY0, northY0 = 0,1,0,1
				
				
				for reg in range(len(region_coords)):
					[westX0, eastX0, southY0, northY0] = region_coords[reg]
					if (startx0 >= westX0) and (startx0 <= eastX0) and (starty0 >= southY0) and (starty0 <= northY0):
						eastX0 = westX0 + regionWidth - 1
						northY0 = southY0 + regionHeight - 1
						break
						
				# This commented out. Because otherwise you will do the Loop for each player. Moving to above
				'''if (CyMap().getCustomMapOption(1) == 1):
					balancer.normalizeAddExtras()'''
				if (iOptionValue_Resources == 2):
					# these are randomly dropped within the city limits on 1st pass:
					resourcesInCity = ('BONUS_GOLD', 'BONUS_GEMS', 'BONUS_CORN', 'BONUS_PIG', 'BONUS_RICE', 'BONUS_SHEEP', 'BONUS_WHEAT', 'BONUS_DEER', 'BONUS_BANANA', 'BONUS_FISH', 'BONUS_CLAM', 'BONUS_CRAB')
					# these are randomly dropped within 2 culture expansions around the city on 2nd pass:
					resourcesNearCity = ('BONUS_COPPER', 'BONUS_IRON', 'BONUS_HORSE', 'BONUS_STONE', 'BONUS_MARBLE', 'BONUS_IVORY', 'BONUS_OIL', 'BONUS_ALUMINUM', 'BONUS_COAL', 'BONUS_URANIUM')
					# these are forcibly added on 3rd pass. only supports land-based resources
					resourcesMustHave = ('BONUS_IRON', 'BONUS_OIL', 'BONUS_ALUMINUM')

					random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots and Bonuses - PYTHON"))

					# Build a list of bonuses
					bonuses = []
					for bonus in range(gc.getNumBonusInfos()):
						bonuses += [bonus]
					random.shuffle(bonuses) # place bonuses in random order

					# Build a list of plots around the city
					plots_city = [] # plots within the city radius
					plots_near = [] # plots within 2 culture expansions
					for dx in range(-3,4):
						for dy in range(-3,4):
							dd = dx*dx + dy*dy
							if (dd > 0) and (dd < 13):
								# check that the tile is in the same region!
								if (startx0+dx >= westX0) and (startx0+dx <= eastX0) and (starty0+dy >= southY0) and (starty0+dy <= northY0):
									p = map.plot(startx0+dx,starty0+dy)
									if not p.isNone():
										plots_near.append(p)
										if dd < 8:
											plots_city.append(p)
					random.shuffle(plots_city) # try plots in random order
					random.shuffle(plots_near)

					# Prepare: remove all existing listed bonuses from the area
					for p in plots_near:
						bonus = p.getBonusType(-1)
						if bonus != BonusTypes.NO_BONUS:
							type_string = gc.getBonusInfo(bonus).getType()
							if (type_string in resourcesInCity) or (type_string in resourcesNearCity):
								p.setBonusType(BonusTypes.NO_BONUS)

					# 1st pass: place bonuses within the city radius
					for bonus in bonuses:
						type_string = gc.getBonusInfo(bonus).getType()
						if type_string in resourcesInCity:
							for p in plots_city:
								if p.canHaveBonus(bonus, True):
									p.setBonusType(bonus)
									break

					# 2nd pass: place bonuses nearby
					for bonus in bonuses:
						type_string = gc.getBonusInfo(bonus).getType()
						if type_string in resourcesNearCity:
							for p in plots_near:
								if p.canHaveBonus(bonus, True):
									p.setBonusType(bonus)
									break

					# 3rd pass: forcibly place the "must have" bonuses
					iPlot = 0
					for bonus in bonuses:
						bInfo = gc.getBonusInfo(bonus)
						type_string = bInfo.getType()
						if type_string in resourcesMustHave:
							have_it = false
							for p in plots_near:
								if p.getBonusType(-1) == bonus:
									have_it = True
									break
							if not have_it:
								p = plots_near[iPlot]
								while ( p.isWater() and (iPlot < len(plots_near)-1) ):
									iPlot += 1
									p = plots_near[iPlot]
								if bInfo.isFlatlands() or not bInfo.isHills():
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								elif bInfo.isHills():
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
								if not bInfo.isTerrain(p.getTerrainType()):
									tryTerrain = grass
									if not bInfo.isTerrain(tryTerrain):
										tryTerrain = plains
										if not bInfo.isTerrain(tryTerrain):
											tryTerrain = desert
									p.setTerrainType(tryTerrain, True, True)
								p.setFeatureType(FeatureTypes.NO_FEATURE, -1)
								p.setBonusType(bonus)
								iPlot += 1

					# 4th pass: fill any unused plots with forests
					for p in plots_near:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and (p.getFeatureType() == FeatureTypes.NO_FEATURE) and p.canHaveFeature(forest):
							p.setFeatureType(forest, -1)

				# Copy the best starting location to everybody else (entire region)
				
				#2.15 this is the mirror part
				
				'''for i in range(0,gc.getMAX_CIV_PLAYERS()):
					if (i != player0) and gc.getPlayer(i).isAlive():

						start_plot = gc.getPlayer(i).getStartingPlot()
						startx, starty = start_plot.getX(), start_plot.getY()

						# find region by location
						westX, eastX, southY, northY = 0,1,0,1
						dx = 0
						dy = 0
						for reg in range(len(region_coords)):
							[westX, eastX, southY, northY] = region_coords[reg]
							if (startx >= westX) and (startx <= eastX) and (starty >= southY) and (starty <= northY):
								eastX = westX + regionWidth - 1
								northY = southY + regionHeight - 1
								dx = westX - westX0
								dy = southY - southY0
								break
						# mask region
						for x in range(westX,eastX+1):
							for y in range(southY,northY+1):
								regMask[y*iW + x] = 1'''

						
						
				# Clear everything outside of the used regions
				'''for x in range(iW):
					for y in range(iH):
						if regMask[y*iW + x] == 0:
							map.plot(x,y).setBonusType(BonusTypes.NO_BONUS)	'''				
					
					

	#2.15 in all cases				
	if (iOptionValue_DesertTundra >= 1):
		for iX in range(iW):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") and pPlot.getBonusType(-1) == -1 and pPlot.getFeatureType() == -1:
					if iOptionValue_DesertTundra == 1 or not isBTPon:#2.22
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
					else:#then it's 2, the marsh
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)	

				if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_TUNDRA") and pPlot.getBonusType(-1) == -1:
					if iOptionValue_DesertTundra == 1 or not isBTPon:#2.22
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
					else:#then it's 2, the marsh
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)		

				if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_ICE") and pPlot.getBonusType(-1) == -1:
					if iOptionValue_DesertTundra == 1 or not isBTPon:#2.22
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
					else:#then it's 2, the marsh
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)						
					

	if isBTPon:
		if (iOptionValue_ResourcesBTG == 1):
			
			#p = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*50/100)
			p = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*2/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))		
			p.setFeatureType(-1, -1)	

			#p = CyMap().plot(CyMap().getGridWidth()*35/100,CyMap().getGridHeight()*50/100)
			p = CyMap().plot(CyMap().getGridWidth()*28/100,CyMap().getGridHeight()*2/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))		
			p.setFeatureType(-1, -1)		

			#p = CyMap().plot(CyMap().getGridWidth()*65/100,CyMap().getGridHeight()*50/100)
			p = CyMap().plot(CyMap().getGridWidth()*72/100,CyMap().getGridHeight()*2/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))		
			p.setFeatureType(-1, -1)	

	return None

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.21y
	if isBTPon:
		if (iOptionValue_ResourcesBTG == 1):#all excluded
			if (type_string in balancer.newResourcesBTP) or (type_string in balancer.newStrategicBTP):
				return None
				
	if (iOptionValue_Resources == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

	
def startHumansOnSameTile():

	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (iOptionValue_ForestType > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * iOptionValue_ForestType #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)
			
	if iOptionValue_Circumnavigation:
		if isBTPon:
			iOption = CyGlobalContext().getInfoTypeForString("GAMEOPTION_DISABLE_CIRCUMNAVIGATION")
			CyGlobalContext().getGame().setOption(iOption, True)
		else:
			CyGlobalContext().getGame().makeCircumnavigated()
			
	return iOptionValue_StartingUnit