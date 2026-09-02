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
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return "Similar to Grid, but players are linked North-South exlusively (1 line band), however they are linked East to another hub empty of any opponent"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "The 'link' to your second hub is normally slow (Alaska option ; Hilly Ice bands), make sure to get started on it very soon!"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Make sure to select carefully what type of hubs are on the east part fo the map; are they closed hubs (Option Caribeean) or are are they linking to each other (Option North America)?"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Map dedicated to Ironman and CTON, where you will have space to expand"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""			

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def getNumCustomMapOptions():
	return 20
	
def getNumHiddenCustomMapOptions():
	return 0

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:	"Mirrored Hubs",
		2:	"TXT_KEY_MAP_SCRIPT_SPOKE_WIDTH",
		3:	"Lines Count",
		4:	"Oil and Aluminium",
		5:	"Elephant",
		6:	"Precious Metal",
		7:	"Empty Land",
		8:	"Forest Density",
		9:	"Start Distance",
		10:	"Desert",
		11:	"BTG Resources",
		12:	"BTG Forest Type",			
		13: "Starting Units",
		14:	"Americas Shape",		
		15:	"Americas Link",
		16: "Land Size",
		17:	"BTG Spectator Notes",		
		18:	"Notes",
		19:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	4,
		2:	6,
		3:	1,
		4:	2,
		5:	2,
		6:	2,
		7:	1,
		8:	4,
		9:	3,
		10:	3,
		11: 3,
		12:	5,
		13: 2,	
		14:	2,
		15:	3,
		16:	2,
		17:	2,
		18:	1,
		19:	1
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
			0: "No",
			1: "Yes - Shape only (not position)",
			2: "Yes - Shape and position",
			3: "Yes - Mirrored"
			},
		2:	{
			0: "TXT_KEY_MAIN_MENU_NONE",
			1: "TXT_KEY_MAP_SCRIPT_1_PLOT_WIDE",
			2: "TXT_KEY_MAP_SCRIPT_2_PLOTS_WIDE",
			3: "TXT_KEY_MAP_SCRIPT_3_PLOTS_WIDE",
			4: "TXT_KEY_MAP_SCRIPT_4_PLOTS_WIDE",
			5: "TXT_KEY_MAP_SCRIPT_5_PLOTS_WIDE"			
			},
		3:	{
			0: "1 Line  Flat"
			},
		4:	{
			0: "Standard",
			1: "Within 5 tiles"
			},
		5:	{
			0: "Standard",
			1: "Within 7 tiles"
			},
		6:	{
			0: "Standard",
			1: "Within 7 tiles"
			},
		7:	{
			0: "No - Fill in the space as if there would be someone"
			},
		8:	{
			0: "High - 60% (Game base)",
			1: "Standard - 40% (map base)",
			2: "Scarce - 25%",
			3: "Rare - 10%"
			},
		9:	{
			0: "Normal - 16 Tiles away",
			1: "Far - 20 Tiles away",
			2: "Far Mixed - 20 Tiles Horizontal, 16 Vertical"
			},	
		10:	{
			0: "Normal",
			1: "None - replace by grassland",
			2: "None - replace by marsh (BTG)"
			},
		11:	{
			0: "No",
			1: "Yes - Normal & Each Strat Resource every 3 players (minimum once)",
			2: "Yes - Normal & above option & Sulphur on capital"	
			},	
		12:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},	
		13:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},
		14:	{
			0: "North Americas - Continent",
			1: "Caribbean - Islands (not if full mirror)"
			},				
		15:	{
			0: "None - Water",
			1: "Alaska - Hilly Ice Band",
			2: "Savanna - Plains/Marsh(BTG) Band"	
			},	
		16:	{
			0: "Normal - via Size Option (Max 7)",
			1: "Based on amount of players (Max 10)"
			},			
		17:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"
			},				
		18:	{
			0: "Max 6 ! 1 Line [2] [3] [4] [5] [6] [x]"
			},
		19:	{
			0: "Penny for BTG - Works for BTS, BTG Options have no effect"		
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	2,
		2:	3,
		3:	0,
		4:	1,
		5:	0,
		6:	0,
		7:	0,
		8:	1,
		9:	2,
		10:	1,
		11:	1,
		12:	0,
		13: 0,
		14:	1,
		15:	1,
		16: 1,
		17: 0,
		18: 0,
		19:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	false,
		2:	false,
		3:	false,
		4:	true,
		5:	true,
		6:	true,
		7:	false,
		8:	true,
		9:	true,
		10: true,
		11:	true,
		12:	true,
		13:	true,
		14: false,
		15:	false,
		16: false,
		17: false,
		18:	false,
		19: false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)
	
def getGridSize(argsList):

	#Traditional way
	if (CyMap().getCustomMapOption(16) == 0):
		# Section 1 - if  default option "16 tiles" is clicked
		if (CyMap().getCustomMapOption(9) == 0):
			grid_sizes = {
				WorldSizeTypes.WORLDSIZE_DUEL:		(10,8),
				WorldSizeTypes.WORLDSIZE_TINY:		(10,12),
				WorldSizeTypes.WORLDSIZE_SMALL:		(10,16),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,21),
				WorldSizeTypes.WORLDSIZE_LARGE:		(10,23),
				WorldSizeTypes.WORLDSIZE_HUGE:		(10,26)
			}
				
		elif (CyMap().getCustomMapOption(9) == 1): # Section 2 - if the map is clicked for larger (20)

			grid_sizes = {
				WorldSizeTypes.WORLDSIZE_DUEL:		(12,10),
				WorldSizeTypes.WORLDSIZE_TINY:		(12,15),
				WorldSizeTypes.WORLDSIZE_SMALL:		(12,20),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(12,26),
				WorldSizeTypes.WORLDSIZE_LARGE:		(12,29),
				WorldSizeTypes.WORLDSIZE_HUGE:		(12,32)
			}
				
		else : # Section 3 - if 20x16

			grid_sizes = {
				WorldSizeTypes.WORLDSIZE_DUEL:		(10,10),
				WorldSizeTypes.WORLDSIZE_TINY:		(10,15),
				WorldSizeTypes.WORLDSIZE_SMALL:		(10,20),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,26),
				WorldSizeTypes.WORLDSIZE_LARGE:		(10,29),
				WorldSizeTypes.WORLDSIZE_HUGE:		(10,32)
			}	
			
		if (argsList[0] == -1): # (-1,) is passed to function on loads
			return []
		[eWorldSize] = argsList
		grid_size = grid_sizes[eWorldSize]
		gc = CyGlobalContext()			
			
	#based on amount of players
	if (CyMap().getCustomMapOption(16) == 1):	
	
		nRealPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		if (CyMap().getCustomMapOption(9) == 1):
			nx = 12
		else:
			nx = 10
			
		if (CyMap().getCustomMapOption(9) == 0):
			ny = 4 * nRealPlayers
		else:
			ny = 5 * nRealPlayers
			
		grid_size = (nx,ny)
		
		
	return grid_size

def beforeGeneration():
	global iNumRegions
	global regions_in_use
	global remaining_regions
	global remaining_regionsTwo#2.21z Cheezy
	
	#2.22
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
	
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	iPlayersCount = gc.getGame().countCivPlayersEverAlive()
	global iPlayers
	
	#2.18 - 2.22
	global iNumSpectators 
	if isBTPon:
		iNumSpectators = gc.getGame().countCivPlayersEverSpectator()
	else:
		iNumSpectators = 0	
	
	# Number of regions - in all cases
	configs = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 20, 20, 20, 20, 20, 20, 20, 20]
	iNumRegions = configs[iPlayersCount]
	
	# Do the real player count now, trick for spoiling number of player / region
	#iPlayers = iNumRegions### Because we want to fill in all#BTP American
	iPlayers = iNumRegions / 2###2.21z - debugging - specific Americas

	
	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		return None

	# Some regions may go unused. We need to track the ones that have been used.
	regions_in_use = []
	remaining_regions = []
	remaining_regionsTwo = []#2.21z Cheezey
	for loopy in range(iNumRegions):
		remaining_regions.append(loopy)
		remaining_regionsTwo.append(loopy)#2.21z Cheezey

	# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
	templates = {2: {0: [0.1, 0.4, 0.0, 1.0],
				 1: [0.6, 0.9, 0.0, 1.0]},
			 4: {0: [0.1, 0.4, 0.0, 0.5],
				 1: [0.1, 0.4, 0.5, 1.0],
				 2: [0.6, 0.9, 0.0, 0.5],
				 3: [0.6, 0.9, 0.5, 1.0]},
			 6: {0: [0.1, 0.4, 0.0, 0.33],
				 1: [0.1, 0.4, 0.33, 0.66],
				 2: [0.1, 0.4, 0.66, 1.0],
				 3: [0.6, 0.9, 0.0, 0.33],
				 4: [0.6, 0.9, 0.33, 0.66],
				 5: [0.6, 0.9, 0.66, 1.0]},
			 8: {0: [0.1, 0.4, 0.0, 0.25],
				 1: [0.1, 0.4, 0.25, 0.50],
				 2: [0.1, 0.4, 0.50, 0.75],
				 3: [0.1, 0.4, 0.75, 1.0],
				 4: [0.6, 0.9, 0.0, 0.25],
				 5: [0.6, 0.9, 0.25, 0.50],
				 6: [0.6, 0.9, 0.50, 0.75],
				 7: [0.6, 0.9, 0.75, 1.0]},			
			10: {0: [0.1, 0.4, 0.0, 0.2],
				 1: [0.1, 0.4, 0.2, 0.4],
				 2: [0.1, 0.4, 0.4, 0.6],
				 3: [0.1, 0.4, 0.6, 0.8],
				 4: [0.1, 0.4, 0.8, 1.0],
				 5: [0.6, 0.9, 0.0, 0.2],
				 6: [0.6, 0.9, 0.2, 0.4],
				 7: [0.6, 0.9, 0.4, 0.6],
				 8: [0.6, 0.9, 0.6, 0.8],			 
				 9: [0.6, 0.9, 0.8, 1.0]},		
			12: {0: [0.1, 0.4, 0.0, 0.166],
				 1: [0.1, 0.4, 0.166, 0.333],
				 2: [0.1, 0.4, 0.333, 0.5],
				 3: [0.1, 0.4, 0.5, 0.666],
				 4: [0.1, 0.4, 0.666, 0.833],
				 5: [0.1, 0.4, 0.833, 1.0],
				 6: [0.6, 0.9, 0.0, 0.166],
				 7: [0.6, 0.9, 0.166, 0.333],
				 8: [0.6, 0.9, 0.333, 0.5],				 
				 9: [0.6, 0.9, 0.5, 0.666],	
				10: [0.6, 0.9, 0.666, 0.833],					 
				11: [0.6, 0.9, 0.833, 1.0]},			
			14: {0: [0.1, 0.4, 0.00, 0.14],
				 1: [0.1, 0.4, 0.14, 0.28],
				 2: [0.1, 0.4, 0.28, 0.42],
				 3: [0.1, 0.4, 0.42, 0.56],
				 4: [0.1, 0.4, 0.56, 0.70],
				 5: [0.1, 0.4, 0.70, 0.85],
				 6: [0.1, 0.4, 0.85, 1.0],
				 7: [0.6, 0.9, 0.00, 0.14],
				 8: [0.6, 0.9, 0.14, 0.28],	
				 9: [0.6, 0.9, 0.28, 0.42],	
				10: [0.6, 0.9, 0.42, 0.56],		
				11: [0.6, 0.9, 0.56, 0.70],	
				12: [0.6, 0.9, 0.70, 0.85],					 
				13: [0.6, 0.9, 0.85, 1.0]},
			16: {0: [0.1, 0.4, 0.00, 0.12],
				 1: [0.1, 0.4, 0.12, 0.25],
				 2: [0.1, 0.4, 0.25, 0.37],
				 3: [0.1, 0.4, 0.37, 0.50],
				 4: [0.1, 0.4, 0.50, 0.62],
				 5: [0.1, 0.4, 0.62, 0.75],
				 6: [0.1, 0.4, 0.75, 0.87],
				 7: [0.1, 0.4, 0.87, 1.0],
				 8: [0.6, 0.9, 0.00, 0.12],
				 9: [0.6, 0.9, 0.12, 0.25],
				10: [0.6, 0.9, 0.25, 0.37],
				11: [0.6, 0.9, 0.37, 0.50],
				12: [0.6, 0.9, 0.50, 0.62],
				13: [0.6, 0.9, 0.62, 0.75],
				14: [0.6, 0.9, 0.75, 0.87],
				15: [0.6, 0.9, 0.87, 1.0]},
			18: {0: [0.1, 0.4, 0.00, 0.11],
				 1: [0.1, 0.4, 0.11, 0.22],
				 2: [0.1, 0.4, 0.22, 0.33],
				 3: [0.1, 0.4, 0.33, 0.44],
				 4: [0.1, 0.4, 0.44, 0.55],
				 5: [0.1, 0.4, 0.55, 0.66],
				 6: [0.1, 0.4, 0.66, 0.77],
				 7: [0.1, 0.4, 0.77, 0.88],
				 8: [0.1, 0.4, 0.88, 1.0],
				 9: [0.6, 0.9, 0.00, 0.11],
				10: [0.6, 0.9, 0.11, 0.22],
				11: [0.6, 0.9, 0.22, 0.33],
				12: [0.6, 0.9, 0.33, 0.44],
				13: [0.6, 0.9, 0.44, 0.55],
				14: [0.6, 0.9, 0.55, 0.66],
				15: [0.6, 0.9, 0.66, 0.77],
				16: [0.6, 0.9, 0.77, 0.88],
				17: [0.6, 0.9, 0.88, 1.0]},
			20: {0: [0.1, 0.4, 0.00, 0.10],
				 1: [0.1, 0.4, 0.10, 0.20],
				 2: [0.1, 0.4, 0.20, 0.30],
				 3: [0.1, 0.4, 0.30, 0.40],
				 4: [0.1, 0.4, 0.40, 0.50],
				 5: [0.1, 0.4, 0.50, 0.60],
				 6: [0.1, 0.4, 0.60, 0.70],
				 7: [0.1, 0.4, 0.70, 0.80],
				 8: [0.1, 0.4, 0.80, 0.90],				 
				 9: [0.1, 0.4, 0.90, 1.0],
				10: [0.6, 0.9, 0.00, 0.10],
				11: [0.6, 0.9, 0.10, 0.20],
				12: [0.6, 0.9, 0.20, 0.30],
				13: [0.6, 0.9, 0.30, 0.40],
				14: [0.6, 0.9, 0.40, 0.50],
				15: [0.6, 0.9, 0.50, 0.60],
				16: [0.6, 0.9, 0.60, 0.70],
				17: [0.6, 0.9, 0.70, 0.80],
				18: [0.6, 0.9, 0.80, 0.90],				
				19: [0.6, 0.9, 0.90, 1.0]},				
	}


	# End of template data.

	# List region_coords: [WestLon, EastLon, SouthLat, NorthLat]
	global region_coords
	region_coords = templates[iNumRegions]

class GridMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def addLandPlot(self, i):
		if self.wholeworldPlotTypes[i] == PlotTypes.PLOT_OCEAN:
			if self.dice.get(5, "Hills on spokes - Grid PYTHON") == 0:
				self.wholeworldPlotTypes[i] = PlotTypes.PLOT_HILLS
			else:
				self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND

	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		# iPlayers = self.gc.getGame().countCivPlayersEverAlive()
		# I Want this as a global definition
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		global region_duplicated
		global other_regions#
		# Add the land (two fractals per region to ensure cohesion).
		#global region_coords
		#global regions_in_use
		#global remaining_regions
		#global remaining_regionsTwo#2.21
		region_duplicated = [0 for i in range(5)]
		for region_loop in range(len(remaining_regions)):
			[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[region_loop]
			iWestX = int(self.iW * fWestLon)
			iEastX = int(self.iW * fEastLon) - 1
			iSouthY = int(self.iH * fSouthLat)
			iNorthY = int(self.iH * fNorthLat) -1
			iWidth = iEastX - iWestX + 1
			iHeight = iNorthY - iSouthY + 1

			if region_duplicated[3] == 0 : 
				region_duplicated = [region_loop, iWestX, iSouthY, iWidth, iHeight]
			elif (iWidth > region_duplicated[3]) and ((iWidth > region_duplicated[3]) < region_duplicated[3]) : 
				region_duplicated = [region_loop, iWestX, iSouthY, iWidth, iHeight]
			
                region_roll = region_duplicated[0]
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

                # Each landmass only takes up approximately 64% of the space in its region.
                # This space is further divided between land and water.
                # Choose a pattern for this region
                landPattern = self.dice.get(3, "Land Pattern - Grid PYTHON")
                if landPattern == 1: # Tall
					regWestX = iWestX + int(iWidth * 0.18)
					regSouthY = iSouthY
					regWidth = int(iWidth * 0.64)
					regHeight = iHeight
                elif landPattern == 2: # Wide
					regWestX = iWestX
					regSouthY = iSouthY + int(iHeight * 0.18)
					regWidth = iWidth
					regHeight = int(iHeight * 0.64)
                else: # landPattern == 0, Square
					regWestX = iWestX + int(iWidth * 0.1)
					regSouthY = iSouthY + int(iHeight * 0.1)
					regWidth = int(iWidth * 0.8)
					regHeight = int(iHeight * 0.8)

                self.generatePlotsInRegion(45 + sea,
                                           regWidth, regHeight,
                                           regWestX, regSouthY,
                                           1, 4,
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

                self.generatePlotsInRegion(25,
                                           coreWidth, coreHeight,
                                           coreWestX, coreSouthY,
                                           1, 3,
                                           self.iHorzFlags, self.iTerrainFlags,
                                           5, 5,
                                           True, 3,
                                           -1, False,
                                           False
                                           )
										   
										   
		#2.21z - the 'Open part'
		if (CyMap().getCustomMapOption(1) == 0):

			for region_loop in range(iNumRegions):#2.15
				# Choose an unused region
				region_roll = self.dice.get(len(remaining_regionsTwo), "Region Roll - Grid PYTHON")
				thisRegion = remaining_regionsTwo[region_roll]
				regions_in_use.append(thisRegion)
				del remaining_regionsTwo[region_roll]

				# Region dimensions
				[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * fWestLon)
				iEastX = int(self.iW * fEastLon) - 1
				iSouthY = int(self.iH * fSouthLat)
				iNorthY = int(self.iH * fNorthLat) -1
				iWidth = iEastX - iWestX + 1
				iHeight = iNorthY - iSouthY + 1

				# Each landmass only takes up approximately 64% of the space in its region.
				# This space is further divided between land and water.
				# Choose a pattern for this region
				landPattern = self.dice.get(3, "Land Pattern - Grid PYTHON")
				if landPattern == 1: # Tall
					regWestX = iWestX + int(iWidth * 0.18)
					regSouthY = iSouthY
					regWidth = int(iWidth * 0.64)
					regHeight = iHeight
				elif landPattern == 2: # Wide
					regWestX = iWestX
					regSouthY = iSouthY + int(iHeight * 0.18)
					regWidth = iWidth
					regHeight = int(iHeight * 0.64)
				else: # landPattern == 0, Square
					regWestX = iWestX + int(iWidth * 0.1)
					regSouthY = iSouthY + int(iHeight * 0.1)
					regWidth = int(iWidth * 0.8)
					regHeight = int(iHeight * 0.8)

				self.generatePlotsInRegion(45 + sea,
										   regWidth, regHeight,
										   regWestX, regSouthY,
										   1, 4,
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

				self.generatePlotsInRegion(25,
										   coreWidth, coreHeight,
										   coreWestX, coreSouthY,
										   1, 3,
										   self.iHorzFlags, self.iTerrainFlags,
										   5, 5,
										   True, 3,
										   -1, False,
										   False
										   )		
		
		#2.21z - Back to common part

		if (CyMap().getCustomMapOption(1) >= 1):

			#duplicate land for other used regions
			other_regions = []
			#for region_loop in range(iPlayers - 1):#2.10 Out
				# Choose an unused region
				#region_roll = self.dice.get(len(remaining_regions), "Region Roll - Grid PYTHON")
				#thisRegion = remaining_regions[region_roll]
				#regions_in_use.append(thisRegion)
				#del remaining_regions[region_roll]
				
			for region_loop in range(iNumRegions):
				#region_roll = self.dice.get(len(remaining_regions), "Region Roll - Grid PYTHON")
				thisRegion = region_loop
				regions_in_use.append(thisRegion)
				#del remaining_regions[region_roll]

				# Region dimensions
				[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * fWestLon)
				iEastX = int(self.iW * fEastLon) - 1
				iSouthY = int(self.iH * fSouthLat)
				iNorthY = int(self.iH * fNorthLat) -1
				iWidth = iEastX - iWestX + 1
				iHeight = iNorthY - iSouthY + 1

				other_regions.append([thisRegion, iWestX, iSouthY, iWidth, iHeight])
				iD, iWestXD, iSouthYD, iWidthD, iHeightD = region_duplicated

				for x in range(iWidth):
					wholeworldX = x + iWestX
					wholeworldXD = x + iWestXD
					for y in range(iHeight):
						wholeworldY = y + iSouthY
						iWorld = wholeworldY*self.iW + wholeworldX
						wholeworldYD = y + iSouthYD
						iWorldD = wholeworldYD*self.iW + wholeworldXD
						self.wholeworldPlotTypes[iWorld] = self.wholeworldPlotTypes[iWorldD]
						
						
		# Generate spokes
		map = CyMap()
		spoke_width = map.getCustomMapOption(2)
		if spoke_width > 0:
		
			#2.21z
			'''iRepeat = len(regions_in_use)
			if map.getCustomMapOption(14) == 1:
				#iRepeat = iNumRegions / 2
				iRepeat = len(regions_in_use) / 2'''
		
			for regionLoop in range(len(regions_in_use)):

				thisRegion = regions_in_use[regionLoop]
				# Region dimensions
				[iWestLon, iEastLon, iSouthLat, iNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * iWestLon)
				iEastX = int(self.iW * iEastLon) - 1
				iSouthY = int(self.iH * iSouthLat)
				iNorthY = int(self.iH * iNorthLat) -1
				iCenterX = int((iWestX + iEastX) / 2)
				iCenterY = int((iSouthY + iNorthY) / 2)
				
				#if map.getCustomMapOption(14) != 1 or iCenterX <= map.getGridWidth() / 2:#to the left is okay#2.21z
				#if map.getCustomMapOption(14) != 1 or 15 <= 30:#to the left is okay#2.21z
				if map.getCustomMapOption(14) != 1 or iEastLon <= 0.5 :#to the left is okay#2.21z
					for x in range(iWestX, iEastX+1):
						i = iCenterY*self.iW + x
						self.addLandPlot(i)
						if spoke_width > 1:
							self.addLandPlot(i + self.iW)
						if spoke_width > 2:
							self.addLandPlot(i - self.iW)
						if spoke_width > 3:#2.21z
							self.addLandPlot(i + self.iW + self.iW)
						if spoke_width > 4:#2.21z
							self.addLandPlot(i - self.iW - self.iW)						
			
					for y in range(iSouthY, iNorthY+1):
						i = y*self.iW + iCenterX
						self.addLandPlot(i)
						if spoke_width > 1:
							self.addLandPlot(i + 1)
						if spoke_width > 2:
							self.addLandPlot(i - 1)
						if spoke_width > 3:#2.21z
							self.addLandPlot(i + 2)
						if spoke_width > 4:#2.21z
							self.addLandPlot(i - 2)				
						

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
	#iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	#I've already declared this

	# Check for valid number of players.
	if iPlayers > 0 and iPlayers < 19: pass
	else: # Error catching.
		fractal_world = FractalWorld()
		fractal_world.initFractal(polar = True)
		plotTypes = fractal_world.generatePlotTypes()
		return plotTypes

	fractal_world = GridMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

def generateTerrainTypes():
	terraingen = TerrainGenerator()
	terraingen.__init__(iDesertPercent=8, iPlainsPercent=25,
		fSnowLatitude=2.0, fTundraLatitude=2.0, fGrassLatitude=0.0, 
		fDesertBottomLatitude=0.0, fDesertTopLatitude=2.0)
	terrainTypes = terraingen.generateTerrain()

	# Eliminate snow and tundra completely (they still get placed sometimes at extreme latitudes)
	for i in range(len(terrainTypes)):
		if (terrainTypes[i] == terraingen.terrainIce) or (terrainTypes[i] == terraingen.terrainTundra):
			terrainTypes[i] = terraingen.terrainPlains

	return terrainTypes

def addFeatures():
	# Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isPeak() and pPlot.isCoastalLand():
			# If a peak is along the coast, change to hills and recalc.
			pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
			
	# Now add the features.
	featuregen = FeatureGenerator()
	
	if (CyMap().getCustomMapOption(8) == 3):
		featuregen.__init__(iJunglePercent=0, iForestPercent=90,
			jungle_grain=5, forest_grain=6)
	elif (CyMap().getCustomMapOption(8) == 2):
		featuregen.__init__(iJunglePercent=0, iForestPercent=75,
			jungle_grain=5, forest_grain=6)
	elif (CyMap().getCustomMapOption(8) == 1):
		featuregen.__init__(iJunglePercent=0, iForestPercent=60,
			jungle_grain=5, forest_grain=6)
	else: 		
		featuregen.__init__(iJunglePercent=0, iForestPercent=40,
			jungle_grain=5, forest_grain=6)	
			
	featuregen.addFeatures()
	return 0

def minStartingDistanceModifier():
	return 20

def assignStartingPlots():

	# Custom start plot finder
	global iNumRegions
	global region_coords
	global regions_in_use
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	#iPlayers = gc.getGame().countCivPlayersEverAlive()
	#I've already declared this
	
	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		CyPythonMgr().allowDefaultImpl()
		return

	# Obtain the minimum crow-flies distance figures [minX, minY] for this map size and number of players.
	minimums = {2: [0.15, 0.3],
				3: [0.15, 0.17], #added penny
				4: [0.15, 0.15],
				5: [0.125, 0.16], #added penny
	            6: [0.1, 0.15],
				7: [0.08, 0.15], #added penny
	            8: [0.07, 0.15],
	            9: [0.1, 0.1],
				10: [0.09, 0.1], #added penny
				11: [0.08, 0.1], #added penny
	            12: [0.07, 0.1],
				13: [0.06, 0.1],#2.23
				14: [0.06, 0.1],#2.23
	            15: [0.06, 0.1],
	            16: [0.07, 0.07],
				17: [0.06, 0.1],#2.23
	            18: [0.05, 0.1],
				19: [0.05, 0.1],#2.23
				20: [0.05, 0.1],#2.23
				}
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
		[iWestLon, iEastLon, iSouthLat, iNorthLat] = region_coords[thisRegion]
		iWestX = int(iW * iWestLon)
		iEastX = int(iW * iEastLon) - 1
		iSouthY = int(iH * iSouthLat)
		iNorthY = int(iH * iNorthLat) -1
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
	for plrCheckLoop in range(gc.getMAX_CIV_PLAYERS()):#2.35 when you reduce to 12 players... cannot hardcode this
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
		iChoosePlayer = dice.get(len(player_list), "Shuffling Regions - Grid PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]

	# Now assign the start plots!
	plot_assignments = {}
	min_dist = []
	
	if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 1):
	
		# Loop through players/regions.
		
		#2.18 A funky way, you double and remove the num of Spec : now the specs are on the left and players on the right
		#iNumSpectators
		'''if iNumSpectators > 0:#Hang on, don't even need this, since it's reverse in C++
			iTotLoop = iPlayers + iNumSpectators
			iStartLoop = iNumSpectators			
		#else :'''
		iTotLoop = iPlayers
		iStartLoop = 0
		iDidLoop = 0
		
		#for assignLoop in range(iPlayers):
		for assignLoop in range(iStartLoop,iTotLoop):
			#playerID = shuffledPlayers[assignLoop]############ PYTHON ERROR #####################
			playerID = shuffledPlayers[iDidLoop]#2.18
			iDidLoop += 1#2.18
			
			#reg = best_regions[assignLoop]#Particularity of the Americas Map
			reg = assignLoop#Americas - Need to be in order, so that all the region on same line are assigned first
			
			[westX, eastX, southY, northY] = region_data[reg][0:4]
			# Only consider the inner part of the region
			iWidth = eastX - westX + 1
			iHeight = northY - southY + 1
			westX = westX + int(iWidth * 0.2)
			eastX = eastX - int(iWidth * 0.2)
			southY = southY + int(iHeight * 0.2)
			northY = northY - int(iHeight * 0.2)
			 
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
							# if not pPlot.isCoastalLand(): continue
							if areaID != pPlot.getArea(): continue
							if validFn != None and not validFn(playerID, iX, iY): continue
							val = pPlot.getFoundValue(playerID)
							if pPlot.isFreshWater:
								val += 1000
							if val > iBestValue:
								valid = True
								for invalid in min_dist:
									[invalidX, invalidY] = invalid
									if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
										valid = False
										break
								if valid:
									for iI in range(gc.getMAX_CIV_PLAYERS()):
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
	
	elif (CyMap().getCustomMapOption(1) >= 2):	
	
		# Loop through players/regions.
		dX = 0
		dY = 0

		if region_duplicated[0] in best_regions :
					tpR = [region_duplicated[0]]
					for item in best_regions :
							if not item in tpR : tpR.append(item)
					best_regions = tpR
		else :
			print "you missed something there O.o"

		#2.18 A funky way, you double and remove the num of Spec : now the specs are on the left and players on the right
		#iNumSpectators
		'''if iNumSpectators > 0:#Hang on, don't even need this, since it's reverse in C++
			iTotLoop = iPlayers + iNumSpectators
			iStartLoop = iNumSpectators			
		#else :'''
		iTotLoop = iPlayers
		iStartLoop = 0
		iDidLoop = 0
		#for assignLoop in range(iPlayers):
		for assignLoop in range(iStartLoop,iTotLoop):	
		#for assignLoop in range(iPlayers):# -Penny ; Not necessary for condition
		# for assignLoop in range(iNumRegions):
			#playerID = shuffledPlayers[assignLoop]############ PYTHON ERROR #####################
			playerID = shuffledPlayers[iDidLoop]#2.18
			iDidLoop += 1#2.18
			#reg = best_regions[assignLoop]#Particularity of the Americas Map
			reg = assignLoop#Americas - Need to be in order, so that all the region on same line are assigned first
			
			
			[wX, eX, sY, nY] = region_data[reg][0:4]
			# Only consider the inner part of the region
			iWidth = eX - wX + 1
			iHeight = nY - sY + 1
			
			westX = wX + int(iWidth * 0.2)
			eastX = eX - int(iWidth * 0.2)
			southY = sY + int(iHeight * 0.2)
			northY = nY - int(iHeight * 0.2)

			if dX == 0 :
							 
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
								# if not pPlot.isCoastalLand(): continue
								if areaID != pPlot.getArea(): continue
								if validFn != None and not validFn(playerID, iX, iY): continue
								val = pPlot.getFoundValue(playerID)
								if pPlot.isFreshWater:
									val += 1000
								if val > iBestValue:
									valid = True
									for invalid in min_dist:
										[invalidX, invalidY] = invalid
										if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
											valid = False
											break
									if valid:
										for iI in range(gc.getMAX_CIV_PLAYERS()):
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
							dX = pBestPlot.getX() - wX
							dY = pBestPlot.getY() - sY
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
			
			else :
				sPlot = map.plot(wX + dX, sY + dY)
				plrID = gc.getPlayer(playerID)
				plrID.setStartingPlot(sPlot, true)
				
		# Successfully assigned start plots, continue back to C++'''
		return None
	
def normalizeRemovePeaks():
	return None

def normalizeAddExtras():

	balancer.normalizeAddExtras()

	# V3 by Axius: Give a land oil and aluminum to each player

	gc = CyGlobalContext()
	map = CyMap()
	oil = gc.getInfoTypeForString("BONUS_OIL")
	alu = gc.getInfoTypeForString("BONUS_ALUMINUM")
	ivory = gc.getInfoTypeForString("BONUS_IVORY")
	gold = gc.getInfoTypeForString("BONUS_GOLD")
	silver = gc.getInfoTypeForString("BONUS_SILVER")
	gems = gc.getInfoTypeForString("BONUS_GEMS")
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	

	

	for i in range(0,gc.getMAX_CIV_PLAYERS()):
		#if gc.getPlayer(i).isAlive():
		if gc.getPlayer(i).isEverAlive():#2.22 - Very important - nothing was working with Spectator

			start_plot = gc.getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()
			plotsclose = []
			plotsfurther = []
			plotsboundaries = []
			has_oil = false
			has_alu = false
			has_ivory = false
			has_horse = false
			has_precious = false
			for dx in range(-5,5):
				for dy in range(-5,5):
					p = map.plot(startx+dx,starty+dy)
					if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						plotsclose.append(p)
						if p.getBonusType(-1) == oil:
							has_oil = True
						if p.getBonusType(-1) == alu:
							has_alu = True
							
			for dx in range(-7,7):
				for dy in range(-7,7):
					p = map.plot(startx+dx,starty+dy)
					if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						plotsfurther.append(p)	
						if p.getBonusType(-1) == ivory:
							has_ivory = True
						if p.getBonusType(-1) == gold:
							has_precious = True
						if p.getBonusType(-1) == silver:
							has_precious = True
						if p.getBonusType(-1) == gems:
							has_precious = True				
							
			for dx in range(-6,6):
				for dy in range(-6,6):
					p = map.plot(startx+dx,starty+dy)
					#2.22 This is too restrictive for this map
					if (( abs(dx) >= 5 or abs(dy) >= 5) and not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):#1 notch closer than other maps
						if ((abs(dx) >= 3 and abs(dy) >= 3)):#too tight otherwise on this map
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								plotsboundaries.append(p)					

	
			if (CyMap().getCustomMapOption(4) == 1):
				if not has_oil:

					random.shuffle(plotsclose) 
					for p in plotsclose:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(oil, True):
							p.setBonusType(oil)
							has_oil = True
							break
					if not has_oil:
						p = plotsclose[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(oil)

				if not has_alu:

					random.shuffle(plotsclose) 
					for p in plotsclose:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(alu, True):
							p.setBonusType(alu)
							has_alu = True or CyMap().getCustomMapOption(4) == 0
							break
					if not has_alu:
						p = plotsclose[0]
						p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(alu)
					
			if (CyMap().getCustomMapOption(5) == 1):
				if not has_ivory:

					random.shuffle(plotsfurther) 
					for p in plotsfurther:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(ivory, True):
							p.setBonusType(ivory)
							has_ivory = True
							break
					if not has_ivory:
						p = plotsfurther[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(ivory)

			if (CyMap().getCustomMapOption(6) == 1):
				if not has_precious:

					random.shuffle(plotsboundaries) 
					for p in plotsboundaries:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(silver, True):
							p.setBonusType(silver)
							has_precious = True
							break
					if not has_precious:
						p = plotsboundaries[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_DESERT"), True, True)
						p.setBonusType(silver)		
	

	
	
	#2020 04 - After player's all stuff
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	

	if (CyMap().getCustomMapOption(10) >= 1):
		for iX in range(iW):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				#if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"):
				if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") and pPlot.getBonusType(-1) == -1 and pPlot.getFeatureType() == -1:
				#if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") and pPlot.getBonusType(-1) == -1:
				#if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") and pPlot.getBonusType(-1) == BonusTypes.NO_BONUS and pPlot.getFeatureType(-1) == FeatureTypes.NO_FEATURE:
					if CyMap().getCustomMapOption(10) == 1 or not isBTPon:#2.22 Extra rule to protect BTS regular game from errors
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
					else:#then it's 2, the marsh
						pPlot.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)
			

	if (CyMap().getCustomMapOption(1) == 3):
		mirrorizeMap() #2020 06 - BTP 2.15 - Restart feature
	
	if isBTPon:
		if (CyMap().getCustomMapOption(11)) == 2:
			for iI in range(gc.getMAX_CIV_PLAYERS()):
					if (gc.getPlayer(iI).isEverAlive()):#not Spectator
						p = gc.getPlayer(iI).getStartingPlot()
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
						p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))	
						p.setFeatureType(-1, -1)
	#2.38 new
	if isBTPon:
		if (CyMap().getCustomMapOption(11) == 1) or (CyMap().getCustomMapOption(11) == 2):
		
			minX = 0
			maxX = CyMap().getGridWidth()
			minY = 0
			maxY = CyMap().getGridHeight()
		
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_DIAMONDS"),1,0,3)	
				
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_NICKEL"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_LEAD"),1,0,3)
			
					
	if (CyMap().getCustomMapOption(15)) > 0:	
	
		for regionLoop in range(iPlayers):
			[iWestLon, iEastLon, iSouthLat, iNorthLat] = region_coords[regionLoop]	
			iW = map.getGridWidth()
			iH = map.getGridHeight()			
			iSouthY = int(iH * iSouthLat)
			iNorthY = int(iH * iNorthLat) -1			
			iWestX = int(iW * 0.4)
			iEastX = int(iW * 0.6) - 1			
			iCenterY = int((iSouthY + iNorthY) / 2)			
					
			iFirstX = iWestX
			iLastX = iEastX + 2
			#2.23 - Case where no spoke even in main land :
			if CyMap().getCustomMapOption(2) == 0:
				iFirstX = iWestX - 3
				iLastX = iEastX + 4
			if CyMap().getCustomMapOption(14) == 1:#the island/carrabiean
				iLastX = iEastX + 4	
					
			for x in range(iFirstX, iLastX):#I Hardcode this because the gap always the same# I also do +3 extra for the case where selecting no spoke, always miss 2/3 tiles
				#p = iCenterY*iW + x
				p = map.plot(x,iCenterY)
				#if (CyMap().getCustomMapOption(15)) == 2 and isBTPon:#2.22
				if (CyMap().getCustomMapOption(15)) == 2:#2.22
					if isBTPon:#2.38
						iTerrain = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
					else:
						iTerrain = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
					p.setPlotType(PlotTypes.PLOT_LAND, True, True)				
					p.setTerrainType(iTerrain, True, True)				
				else:
					iTerrain = CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW")			
					p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
					p.setTerrainType(iTerrain, True, True)					
							
	return None

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	if isBTPon:
		if (CyMap().getCustomMapOption(11) == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
				
		if (CyMap().getCustomMapOption(11) == 0):#exclude the strategic ones because strat is function above (and commo is okay)
			if (type_string in balancer.newStrategicBTP):
				return None

	if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
		return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isBonusIgnoreLatitude():
	return True

def mirrorizeMap():
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()

        region_duplicated_ID, iWestX, iSouthY, iWidth, iHeight = region_duplicated
        #make sure larger duplicated land doesn't get extra bonuses/goodies
        minW = min([item[3] for item in other_regions])
        minH = min([item[4] for item in other_regions])

	for iX in range(iW):
		for iY in range(iH):
                        if iX >= iWestX and iX < iWestX + minW and iY >= iSouthY and iY < iSouthY + minH : continue
			pPlot = map.plot(iX, iY)

			pPlot.setImprovementType(-1)
			pPlot.setBonusType(-1)	
			pPlot.setFeatureType(-1, -1)
			pPlot.setNOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
                        pPlot.setWOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
                        pPlot.setRiverID (-1)

        #reflect plot types (addlake)
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                pPlot.setPlotType(rPlot.getPlotType(), True, True)
	
	map.recalculateAreas()

        #reflect terrain
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                pPlot.setTerrainType(rPlot.getTerrainType(), True, True)
	
	map.recalculateAreas()

        #rearrange river IDs
	initRiverID = 0
	riverID = {}
        for dX in range(iWidth):
                for dY in range(iHeight):
                        pPlot = map.plot(iWestX + dX, iSouthY + dY)
                        rID = pPlot.getRiverID()
                        if rID != -1 :
                                if rID in riverID.keys() :
                                        pPlot.setRiverID(riverID[rID])
                                else :
                                        riverID[rID] = initRiverID
                                        pPlot.setRiverID(riverID[rID])
                                        initRiverID += 1

        iRivers = len(riverID.keys())
        incr = 0

        #mirrorize rivers
	for region_ID, wX, sY, rW, rH in other_regions:
                incr += 1
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                        
                                if rPlot.isNOfRiver():
                                        pPlot.setNOfRiver(True, rPlot.getRiverWEDirection())
                                if rPlot.isWOfRiver():
                                        pPlot.setWOfRiver(True, rPlot.getRiverNSDirection())

                                rID = rPlot.getRiverID()
                                if rID != -1 :
                                        pPlot.setRiverID(rID + incr * iRivers)
	
	map.recalculateAreas()

	# mirrorize features
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setFeatureType(rPlot.getFeatureType(), -1)

	
	map.recalculateAreas()

	# mirrorize bonuses
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setBonusType(rPlot.getBonusType(-1))	

	map.recalculateAreas()

	# mirrorize goodies
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setImprovementType(rPlot.getImprovementType())

	map.recalculateAreas()

	return None
	
def startHumansOnSameTile():

	if isBTPon :
		if (CyMap().getCustomMapOption(12) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(12) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)

	if (CyMap().getCustomMapOption(13) == 1):
		return True
	