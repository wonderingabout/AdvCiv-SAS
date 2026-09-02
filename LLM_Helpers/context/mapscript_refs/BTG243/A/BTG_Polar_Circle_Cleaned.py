
# Penny for BTG Winter 2024 ##

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
import random

balancer = BonusBalancer()

'''0 -- Map Options --'''
'''0.0 -- BTG Description -- '''	
def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return ""

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return ""
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return ""

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""	



'''0.1)     getNumHiddenCustomMapOptions() '''
def getNumHiddenCustomMapOptions():
	return 2

'''0.2 getNumCustomMapOptions()'''	
def getNumCustomMapOptions():
	return 19

'''0.3)     getCustomMapOptionDefault()'''	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	2,
		2:	1,
		3:	0,
		4:  2,
		5:	1,
		6:	4,
		7:	1,
		8:	0,
		9:	1,
		10:	1,
		11:	0,
		12:	0,
		13:	0,
		14:	0,
		15:	0,
		16:	0,
		17:	0,
		18:	0
		}
	return option_defaults[iOption]	
	
'''0.4)     isAdvancedMap()'''
def isAdvancedMap(): return True 	

'''0.5)     getCustomMapOptionName()'''
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_CENTER_REGION",
		1:	"External Regio",
		2:	"TXT_KEY_FEATURE_JUNGLE",
		3:	"TXT_KEY_MAP_WORLD_WRAP",
		4:  "TXT_KEY_CONCEPT_RESOURCES",
		5:	"Land Type",
		6:	"Eldorado Islands",
		7:	"BTG Resources",
		8:	"BTG Forest Type",
		9:	"Starting Plot",		
		10:	"BTG Start Position",
		11: "Starting Units",
		12:	"Size 1 notch smaller",
		13:	"Notes",
		14:	"BTG Free Unit",
		15: "BTG Amt Free Unit",
		16:	"BTG Spectator Notes",
		17:	"Balance",
		18:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
'''0.6)     getNumCustomMapOptionValues()'''	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:  3,
		2:	3,
		3:	1,
		4:  3,
		5:	2,
		6:	5,
		7:	3,
		8:	5,
		9:	2,
		10:	2,
		11:	2,
		12:	3,
		13:	1,
		14:	4,
		15:	4,
		16:	2,
		17:	1,
		18:	1
		}
	return option_values[iOption]
	
'''0.7)     isRandomCustomMapOption()'''
def isRandomCustomMapOption(argsList): return False

'''0.8)     getCustomMapOptionDescAt()'''	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_OCEAN",
			1: "Snowy",
			2: "Artic - Frozen",
			},
		1:	{
			0: "Ocean",
			1: "Snowy",
			2: "Artic - Frozen",
			},			
		2:	{
			0: "Jungle",
			1: "Some Jungle",
			2: "No Jungle",
			},
		3:	{
			0: "Flat"
			},
		4:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "Balanced - Including Marble",		
			},
		5:	{
			0: "Donut Logic",
			1: "Polar Circle Logic"
			},
		6:	{
			0: "No",
			1: "Yes - 4x4 in the corners",
			2: "Yes - Wealthier Islands",
			3: "Yes - Larger Islands",
			4: "Yes - Larger and Wealthier Islands"
			},
		7:	{
			0: "No",
			1: "Yes - Balanced for Obsidian, Jade, Potato",
			2: "Yes - Balanced as above, Sulphurs fixed"
			},	
		8:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},				
		9:	{
			0: "Coastal Starts",
			1: "Inland Starts"
			},
		10:	{
			0: "Normal",
			1: "Top v Bottom"
			},	
		11:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},	
		12:	{
			0: "No",
			1: "Yes",
			2: "Yes - 2 Notches"
			},
		13:	{
			0: "Up to 10 players"
			},			
		14:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			},
		15:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},				
		16:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"			
			},
		17:	{
			0: getDescriptionBalance()		
			},			
		18:	{
			0: "Penny for Beyond The Game - Works for BTS, BTG Options have no effect"		
			}					
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text


'''0.9)     - Get Map-Types'''
'''0.9.1)     isClimateMap()'''
def isClimateMap(): return False

'''0.9.2)     isSeaLevelMap()'''
def isSeaLevelMap(): return False


'''1)     beforeInit()'''

def beforeInitOptionsValue():
	global iOptionValue_Wrap
	
	iOptionValue_Wrap = CyMap().getCustomMapOption(0)

def beforeInit():#2.36 this is handy to find in code

	### Call Option Cleaner ##	
	beforeInitOptionsValue()

	## General BTG Initialization ##
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	

'''2)     - Initialize Map'''
'''2.2)     getGridSize()'''
def getGridSize(argsList):
	"Override Grid Size function to make the maps square."

	if (CyMap().getCustomMapOption(12) == 0):#2.22
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8,8),
			WorldSizeTypes.WORLDSIZE_TINY:		(9,9),
			WorldSizeTypes.WORLDSIZE_SMALL:		(10,10),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(12,12),
			WorldSizeTypes.WORLDSIZE_LARGE:		(14,14),
			WorldSizeTypes.WORLDSIZE_HUGE:		(16,16)
		}
		
	if (CyMap().getCustomMapOption(12) == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,7),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
			WorldSizeTypes.WORLDSIZE_SMALL:		(9,9),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(11,11),
			WorldSizeTypes.WORLDSIZE_LARGE:		(13,13),
			WorldSizeTypes.WORLDSIZE_HUGE:		(15,15)
		}	
	
	if (CyMap().getCustomMapOption(12) == 2):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(7,7),
			WorldSizeTypes.WORLDSIZE_SMALL:		(8,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(10,10),
			WorldSizeTypes.WORLDSIZE_LARGE:		(12,12),
			WorldSizeTypes.WORLDSIZE_HUGE:		(14,14)
		}	
		
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

'''2.3.1)   getTopLatitude()            # always use both'''
def getTopLatitude(): return 10 #Don't want Snow on trees
'''2.3.2)   getBottomLatitude()         # always use both'''
def getBottomLatitude(): return -10 #Don't want Snow on trees

'''2.4.1)   getWrapX()                  # always use both'''
'''2.4.2)   getWrapY()                  # always use both'''
def getWrapX():	return (CyMap().getCustomMapOption(3) == 1 or CyMap().getCustomMapOption(3) == 2)
def getWrapY():	return (CyMap().getCustomMapOption(3) == 2)


'''3)     beforeGeneration()	'''	
def beforeGeneration():
	#copy /inspired by inland			
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()

	global isBTPon
	global iBrown	
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
	except:
		isBTPon = False	
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")	

	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
	
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
	#2.23 - Debug rare crashes
	fVar = 2
	
	if (CyMap().getCustomMapOption(9) == 0):#Coastal
	
		# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
			templates = {(1,0): {0: [0.50, 0.32, int(0.5 * iW), int(0.5 * iH)]},
					 (2,0): {0: [0.50, 0.32, fVar, int(0.5 * iH)],
							 1: [0.50, 0.68, fVar, int(0.5 * iH)]},
					 (3,0): {0: [0.16, 0.30, fVar, fVar],
							 1: [0.84, 0.30, fVar, fVar],
							 2: [0.50, 0.68, fVar, fVar]},
					 (4,0): {0: [0.16, 0.30, fVar, fVar],
							 1: [0.84, 0.30, fVar, fVar],
							 2: [0.16, 0.70, fVar, fVar],
							 3: [0.84, 0.70, fVar, fVar]},
					 (5,0): {0: [0.16, 0.30, fVar, fVar],
							 1: [0.84, 0.30, fVar, fVar],
							 2: [0.50, 0.32, fVar, fVar],
							 3: [0.16, 0.70, fVar, fVar],
							 4: [0.84, 0.70, fVar, fVar]},
					 (6,0): {0: [0.18, 0.27, fVar, fVar],
							 1: [0.82, 0.27, fVar, fVar],
							 2: [0.50, 0.33, fVar, fVar],
							 3: [0.18, 0.73, fVar, fVar],
							 4: [0.82, 0.73, fVar, fVar],
							 5: [0.50, 0.68, fVar, fVar]},							 
					 (7,0): {0: [0.18, 0.27, fVar, fVar],
							 1: [0.82, 0.27, fVar, fVar],
							 2: [0.50, 0.33, fVar, fVar],
							 3: [0.18, 0.73, fVar, fVar],
							 4: [0.82, 0.73, fVar, fVar],
							 5: [0.50, 0.68, fVar, fVar],							 
							 6: [0.50, 0.12, fVar, fVar]},	
					 (8,0): {0: [0.18, 0.27, fVar, fVar],
							 1: [0.82, 0.27, fVar, fVar],
							 2: [0.50, 0.33, fVar, fVar],
							 3: [0.18, 0.73, fVar, fVar],
							 4: [0.82, 0.73, fVar, fVar],
							 5: [0.50, 0.68, fVar, fVar],							 
							 6: [0.50, 0.12, fVar, fVar],							 
							 7: [0.50, 0.89, fVar, fVar]},
					 (9,0): {0: [0.18, 0.27, fVar, fVar],
							 1: [0.82, 0.27, fVar, fVar],
							 2: [0.50, 0.33, fVar, fVar],
							 3: [0.18, 0.73, fVar, fVar],
							 4: [0.82, 0.73, fVar, fVar],
							 5: [0.50, 0.68, fVar, fVar],							 
							 6: [0.37, 0.12, fVar, fVar],							 
							 7: [0.37, 0.89, fVar, fVar],							 
							 8: [0.63, 0.12, fVar, fVar]},								 
					 (10,0): {0: [0.18, 0.27, fVar, fVar],
							 1: [0.82, 0.27, fVar, fVar],
							 2: [0.50, 0.33, fVar, fVar],
							 3: [0.18, 0.73, fVar, fVar],
							 4: [0.82, 0.73, fVar, fVar],
							 5: [0.50, 0.68, fVar, fVar],							 
							 6: [0.37, 0.12, fVar, fVar],							 
							 7: [0.37, 0.89, fVar, fVar],							 
							 8: [0.63, 0.12, fVar, fVar],							 
							 9: [0.63, 0.89, fVar, fVar]},								 
		}
	
	if (CyMap().getCustomMapOption(9) == 1):#Inland
	
		templates = {(1,0): {0: [0.50, 0.20, int(0.5 * iW), int(0.5 * iH)]},
					 (2,0): {0: [0.50, 0.20, fVar, int(0.5 * iH)],
							 1: [0.50, 0.77, fVar, int(0.5 * iH)]},
					 (3,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.50, 0.77, fVar, fVar]},
					 (4,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.25, 0.67, fVar, fVar],
							 3: [0.75, 0.67, fVar, fVar]},
					 (5,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.50, 0.20, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar]},
					 (6,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.50, 0.20, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar],
							 5: [0.50, 0.80, fVar, fVar]},		
					 (7,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.40, 0.22, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar],
							 5: [0.60, 0.22, fVar, fVar],							 
							 6: [0.50, 0.80, fVar, fVar]},	
					 (8,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.40, 0.22, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar],
							 5: [0.40, 0.78, fVar, fVar],	
							 6: [0.60, 0.22, fVar, fVar],							 
							 7: [0.60, 0.78, fVar, fVar]},		
					 (9,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.40, 0.22, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar],
							 5: [0.40, 0.78, fVar, fVar],
							 6: [0.60, 0.22, fVar, fVar],
							 7: [0.60, 0.78, fVar, fVar],
							 8: [0.50, 0.12, fVar, fVar]},
					 (10,0): {0: [0.25, 0.33, fVar, fVar],
							 1: [0.75, 0.33, fVar, fVar],
							 2: [0.40, 0.22, fVar, fVar],
							 3: [0.25, 0.67, fVar, fVar],
							 4: [0.75, 0.67, fVar, fVar],
							 5: [0.40, 0.78, fVar, fVar],
							 6: [0.60, 0.22, fVar, fVar],
							 7: [0.60, 0.78, fVar, fVar],
							 8: [0.50, 0.12, fVar, fVar],
							 9: [0.50, 0.89, fVar, fVar]},					 
		}
		# End of Templates data.

	# Shuffle start points so that players are assigned templateIDs at random.
	player_list = []
	for playerLoop in range(CyGlobalContext().getGame().countCivPlayersEverAlive()):
		player_list.append(playerLoop)
	shuffledPlayers = []
	for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Template IDs - Inland Sea PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]
		
			
	#end copy		
	
	global islandPlotList
	islandPlotList = []
	iIslandSize = 3
	iIslandSecondPart = 0
	if CyMap().getCustomMapOption(6) >= 3:
		iIslandSecondPart = 2
	iMaxIslandSize = iIslandSize + iIslandSecondPart
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			if x <= iMaxIslandSize + 1:
				if y <= iMaxIslandSize + 1:
					iHub = 0
				else:
					iHub = 1
			else:
				if y <= iMaxIslandSize + 1:
					iHub = 2
				else:
					iHub = 3				
		
			if (x <= iIslandSize or x >= (CyMap().getGridWidth() - iIslandSize - 1)) and (y <= iIslandSize or y >= (CyMap().getGridHeight() - iIslandSize - 1)):
				islandPlotList.append([x,y,iHub])
			if (x <= (iIslandSize - iIslandSecondPart) or x >= (CyMap().getGridWidth() - iIslandSize - 1 + iIslandSecondPart)) and (y <= (iIslandSize + iIslandSecondPart) or y >= (CyMap().getGridHeight() - iIslandSize - 1 - iIslandSecondPart)):
				islandPlotList.append([x,y,iHub])
			if (x <= (iIslandSize + iIslandSecondPart) or x >= (CyMap().getGridWidth() - iIslandSize - 1 - iIslandSecondPart)) and (y <= (iIslandSize - iIslandSecondPart) or y >= (CyMap().getGridHeight() - iIslandSize - 1 + iIslandSecondPart)):
				islandPlotList.append([x,y,iHub])				
		
	return None	
	
'''4)     - Generate Map'''
'''4.1)     generatePlotTypes()'''	
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()	

class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	#def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=3):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=5):
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)
		
		iCenterX = int(self.iNumPlotsX / 2)
		iCenterY = int(self.iNumPlotsY / 2)
		iRadius = min((iCenterX - 4), (iCenterY - 4))
		iHoleRadius = int(iRadius / 2)
		userInputCenter = self.map.getCustomMapOption(0)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
				if fDistance > iRadius:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				elif fDistance < iHoleRadius:
					if userInputCenter == 0:#BTP
						self.plotTypes[i] = PlotTypes.PLOT_OCEAN
					elif userInputCenter == 1:#BTP
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if iProba <= 23:
							self.plotTypes[i] = PlotTypes.PLOT_LAND
					elif userInputCenter == 2:#BTP
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if iProba <= 23:
							self.plotTypes[i] = PlotTypes.PLOT_LAND							
					else:#BTP normally never
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
				else:
					hillVal = self.hillsFrac.getHeight(x,y)
					if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
						peakVal = self.peaksFrac.getHeight(x,y)
						if (peakVal <= iPeakThreshold):
							self.plotTypes[i] = PlotTypes.PLOT_PEAK
						else:
							self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						self.plotTypes[i] = PlotTypes.PLOT_LAND

		#Eldorado Island
		if self.map.getCustomMapOption(6) >= 1:
			for p in range(len(islandPlotList)):
				x =  islandPlotList[p][0]			
				y =  islandPlotList[p][1]
				i =  y*self.iNumPlotsX + x
				
				iHillTest = CyGame().getSorenRandNum(100, "a Quarter is HILL")	
				if iHillTest <= 30:
					self.plotTypes[i] = PlotTypes.PLOT_HILLS
				else:
					self.plotTypes[i] = PlotTypes.PLOT_LAND				
		#end		



		if shift_plot_types:
			self.shiftPlotTypes()

		return self.plotTypes	
		
		
'''4.2)     generateTerrainTypes()		'''		
def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Donut) ...")
	terraingen = DonutTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes		
	
# subclass TerrainGenerator to create a lush grassland utopia.
class DonutTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	#def __init__(self, fracXExp=-1, fracYExp=-1, grain_amount=5):
	def __init__(self, fracXExp=-1, fracYExp=-1, grain_amount=7):
		self.gc = CyGlobalContext()
		self.map = CyMap()

		self.grain_amount = grain_amount + self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()

		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

		self.terrain=CyFractal()

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()

		self.iCenterX = int(self.map.getGridWidth() / 2)
		self.iCenterY = int(self.map.getGridHeight() / 2)
		self.iRadius = min((self.iCenterX - 4), (self.iCenterY - 4))
		self.iHoleRadius = int(self.iRadius / 2)
		self.userInputCenter = self.map.getCustomMapOption(0)
		
	def initFractals(self):
		self.terrain.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iGrassBottom = self.terrain.getHeightFromPercent(12)

		self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
		self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
		self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
		#BTP
		self.terrainSnow = self.gc.getInfoTypeForString("TERRAIN_SNOW")
		self.terrainCoast = self.gc.getInfoTypeForString("TERRAIN_COAST")
		self.terrainOcean = self.gc.getInfoTypeForString("TERRAIN_OCEAN")		

	def getLatitudeAtPlot(self, iX, iY):
		return None

	def generateTerrain(self):		
		terrainData = [0]*(self.iWidth*self.iHeight)
		for x in range(self.iWidth):
			for y in range(self.iHeight):
				iI = y*self.iWidth + x
				terrain = self.generateTerrainAtPlot(x, y)
				terrainData[iI] = terrain
		return terrainData

	def generateTerrainAtPlot(self,iX,iY):
		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		if iX == self.iCenterX and iY == self.iCenterY:
			fDistance = 0
		else:
			fDistance = sqrt(((iX - self.iCenterX) ** 2) + ((iY - self.iCenterY) ** 2))
		if fDistance < self.iHoleRadius:
			if self.userInputCenter == 0:
				return self.map.plot(iX, iY).getTerrainType()
			elif self.userInputCenter == 1:
				terrainVal = self.terrainSnow#BTP 		
			elif self.userInputCenter == 2:
				terrainVal = self.terrainSnow#BTP 					
			else:#Normally never
				terrainVal = self.terrainGrass
		else:
			val = self.terrain.getHeight(iX, iY)
			#BTP - Choices
			if (CyMap().getCustomMapOption(5) == 0):#normal case
				if val >= self.iGrassBottom:
					terrainVal = self.terrainGrass
				else:
					terrainVal = self.terrainPlains
			elif (CyMap().getCustomMapOption(5) == 1):#BTP stuff
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
				if iProba <= 2:
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
				elif iProba <= 5:
					terrainVal = iBrown
				elif iProba <= 30:
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")				
				else:#then normal
					if val >= self.iGrassBottom:
						terrainVal = self.terrainGrass
					else:
						terrainVal = self.terrainPlains			
			
		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal	
	
'''4.3)     addRivers()'''
'''4.4)     addLakes()'''
'''4.5)     addFeatures()'''
def addFeatures():
	NiTextOut("Adding Features (Python Donut) ...")
	featuregen = DonutFeatureGenerator()
	featuregen.addFeatures()
	return 0
	
class DonutFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		# We don' need no steeking ice. M'kay? Alrighty then.
		#ice = 0
		self.iCenterX = int(self.map.getGridWidth() / 2)
		self.iCenterY = int(self.map.getGridHeight() / 2)
		self.iRadius = min((self.iCenterX - 4), (self.iCenterY - 4))
		self.iHoleRadius = int(self.iRadius / 2)		
		
		if (CyMap().getCustomMapOption(0) <> 2): pass#Option BTP Arctic
		else:#Option BTP Arctic
			if iX == self.iCenterX and iY == self.iCenterY:
				fDistance = 0
			else:
				fDistance = sqrt(((iX - self.iCenterX) ** 2) + ((iY - self.iCenterY) ** 2))
				if fDistance < self.iHoleRadius:#BTP
					if (pPlot.getTerrainType() <> self.gc.getInfoTypeForString("TERRAIN_COAST") and pPlot.getTerrainType() <> self.gc.getInfoTypeForString("TERRAIN_OCEAN")):
						pPlot.setFeatureType(self.gc.getInfoTypeForString("FEATURE_ICE"), -1)
		
	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		if (CyMap().getCustomMapOption(2) == 2): pass #No Jungles option
		elif (CyMap().getCustomMapOption(2) == 0):  #Normal Jungles
			if pPlot.canHaveFeature(self.featureJungle):
				iJungleHeight = self.jungles.getHeight(iX, iY)
				if self.iJungleTop >= iJungleHeight >= self.iJungleBottom + (self.iJungleTop - self.iJungleBottom)*self.gc.getClimateInfo(self.map.getClimate()).getJungleLatitude()*lat:
					pPlot.setFeatureType(self.featureJungle, -1)
		else:#then option 1, some Jungle			
			if pPlot.canHaveFeature(self.featureJungle):
				iJungleHeight = self.jungles.getHeight(iX, iY)
				if self.iJungleTop - 1 >= iJungleHeight >= self.iJungleBottom + 1 + (self.iJungleTop - self.iJungleBottom)*self.gc.getClimateInfo(self.map.getClimate()).getJungleLatitude()*lat:
					pPlot.setFeatureType(self.featureJungle, -1)	

'''4.6)     addBonuses()	'''
def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
		
	#2.21y
	if isBTPon:
		if (CyMap().getCustomMapOption(7) == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None	
		if (CyMap().getCustomMapOption(7) == 2):#all excluded
			if (type_string in ("BONUS_SULPHUR")):
				return None	

	if (CyMap().getCustomMapOption(4) >= 1):
		#if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
		if (type_string in balancer.resourcesToBalance):#BTP Because marble is broken
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way	
	
	
'''4.6.1)     isBonusIgnoreLatitude()*'''
'''4.7)     addGoodies()'''

'''5)     afterGeneration()'''

'''6)     - Select Starting-Plots'''
'''6.1)     minStartingDistanceModifier()'''
'''6.2)     assignStartingPlots()'''	
def findStartingPlot(argsList):
	# Set up for maximum of 18 players! If more, use default implementation.
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if iPlayers > 10:
		CyPythonMgr().allowDefaultImpl()
		return
		
	[playerID] = argsList
	
	if isBTPon:#2.22
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		if iNumSpectators > 0:
			if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
			#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
				return -1
	
	global plotSuccess
	global plotValue

	def isValid(playerID, x, y):
		gc = CyGlobalContext()
		map = CyMap()
		pPlot = map.plot(x, y)
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		iPlayers = gc.getGame().countCivPlayersEverAlive()
				
		# Use global data set up via beforeGeneration().
		global templates
		global shuffledPlayers
		global iTemplateRoll
		playerTemplateAssignment = shuffledPlayers[playerID]
		[fLat, fLon, varX, varY] = templates[(iPlayers, iTemplateRoll)][playerTemplateAssignment]
		
		# Check to ensure the plot is on the main landmass.
		if (pPlot.getArea() != map.findBiggestArea(False).getID()):
			return false
		
		# Now check for eligibility according to the defintions found in the template.
		iX = int(iW * fLat)
		iY = int(iH * fLon)
		westX = max(2, iX - varX)
		eastX = min(iW - 3, iX + varX)
		southY = max(2, iY - varY)
		northY = min(iH - 3, iY + varY)
		if x < westX or x > eastX or y < southY or y > northY:
			return false
		else:
			return true

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)#2.22 Simplified this part by calling common logic	

'''7)     - Normalize Starting-Plots'''
'''7.1)     normalizeStartingPlotLocations()+'''
def normalizeStartingPlotLocations():

	if (CyMap().getCustomMapOption(10) == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()
		
'''7.2)     normalizeAddRiver()'''
'''7.3)     normalizeRemovePeaks()'''
'''7.4)     normalizeAddLakes()'''
'''7.5)     normalizeRemoveBadFeatures()+'''
'''7.6)     normalizeRemoveBadTerrain()+'''
'''7.7)     normalizeAddFoodBonuses()+'''
'''7.7.1)     isBonusIgnoreLatitude()*'''
'''7.8)     normalizeGoodTerrain()+'''
'''7.9)     normalizeAddExtras()'''
'''7.9.1)     isBonusIgnoreLatitude()*'''		

	
def normalizeAddExtras():
	if (CyMap().getCustomMapOption(4) >= 1):
		balancer.normalizeAddExtras()
		
	#2.18
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),4,True,iBrown)
		
	if (CyMap().getCustomMapOption(4) >= 2):	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,3,False,iBrown)	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,iBrown)
	#end
			
	#Last chance to do something
	#External Artic part 2.18
	map = CyMap()
	gc = CyGlobalContext()	
	plotOceanLarge = []
	
	
	iCenterX = int(map.getGridWidth() / 2)
	iCenterY = int(map.getGridHeight() / 2)
	iRadius = min((iCenterX - 4), (iCenterY - 4))
	iHoleRadius = int(iRadius / 2)

	if (CyMap().getCustomMapOption(1) <> 0):
	
		for dx in range(0,map.getGridWidth()):
			for dy in range(0,map.getGridHeight()):
				i = dy*map.getGridWidth() + dx
				if dx == iCenterX and dy == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((dx - iCenterX) ** 2) + ((dy - iCenterY) ** 2))
				
				if fDistance > iHoleRadius:#here bigger because it's the opposite of the logic stored elsewhere
			
					p = map.plot(dx,dy)
					if (p.getTerrainType() == gc.getInfoTypeForString("TERRAIN_OCEAN")):
						plotOceanLarge.append(p)
				
		for p in plotOceanLarge:
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba <= 23:	
				#in case of == 1 or == 2
				p.setTerrainType(gc.getInfoTypeForString("TERRAIN_SNOW"), True, True)
				if (CyMap().getCustomMapOption(1) == 2):
					p.setFeatureType(gc.getInfoTypeForString("FEATURE_ICE"), -1)						
		
	if isBTPon:#2.35 we'd missed this "if" clause
		if (CyMap().getCustomMapOption(7) == 2):	
			
			p = CyMap().plot(CyMap().getGridWidth()/2,CyMap().getGridHeight()/2)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))
			p.setFeatureType(-1, -1)
			
			p = CyMap().plot(CyMap().getGridWidth()/20,CyMap().getGridHeight()/2)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))		
			p.setFeatureType(-1, -1)
			
			p = CyMap().plot(CyMap().getGridWidth()/20*19,CyMap().getGridHeight()/2)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))	
			p.setFeatureType(-1, -1)
			
			p = CyMap().plot(CyMap().getGridWidth()/2,CyMap().getGridHeight()/2 + 3)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))
			p.setFeatureType(-1, -1)
			
			p = CyMap().plot(CyMap().getGridWidth()/2,CyMap().getGridHeight()/2 - 3)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))
			p.setFeatureType(-1, -1)
			
		
		if (CyMap().getCustomMapOption(7) >= 1):#2.35
			listToBalance = ["BONUS_OBSIDIAN"]
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_OBSIDIAN",6,4,100)	
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_JADE",6,4,70)	
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_POTATO",7,4,80)	
	


	if (CyMap().getCustomMapOption(6) == 2 or CyMap().getCustomMapOption(6) == 4):#wealthier Eldorado 2.22
		foodList = [["BONUS_PIG"],["BONUS_PIG"],["BONUS_PIG"],["BONUS_CORN"],["BONUS_CORN"],["BONUS_CORN"]]
		metalList = [["BONUS_GOLD"],["BONUS_SILVER"],["BONUS_GEMS"],["BONUS_GOLD"],["BONUS_SILVER"],["BONUS_GEMS"]]
		if isBTPon : 
			folkList = [["BONUS_OLIVES"],["BONUS_OLIVES"],["BONUS_TEA"],["BONUS_TEA"],["BONUS_SALT"],["BONUS_SALT"]]
		else:#2.38
			folkList = [["BONUS_WHEAT"],["BONUS_WHEAT"],["BONUS_WHEAT"],["BONUS_WHEAT"],["BONUS_WHEAT"],["BONUS_WHEAT"]]
		for iThisHub in range(0,4):
			ThisHubList = []
			for p in range(len(islandPlotList)):
				if islandPlotList[p][2] == iThisHub:
					x =  islandPlotList[p][0]			
					y =  islandPlotList[p][1]
					pPlot = CyMap().plot(x,y)
					if (pPlot.getBonusType(-1) == BonusTypes.NO_BONUS):
						ThisHubList.append([x,y])
										
			
			iRandomPlot = CyGame().getSorenRandNum(len(ThisHubList), "a Quarter is HILL")
			x =  ThisHubList[iRandomPlot][0]			
			y =  ThisHubList[iRandomPlot][1]
			ThisHubList.remove([x,y])
			pChosenPlot = CyMap().plot(x,y)
			iRandomBonus = CyGame().getSorenRandNum(len(foodList), "a Quarter is HILL")
			iBonus = foodList[iRandomBonus]
			pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iBonus[0]))
			foodList.remove(iBonus)
				
			iRandomPlot = CyGame().getSorenRandNum(len(ThisHubList), "a Quarter is HILL")
			x =  ThisHubList[iRandomPlot][0]			
			y =  ThisHubList[iRandomPlot][1]
			ThisHubList.remove([x,y])
			pChosenPlot = CyMap().plot(x,y)
			iRandomMetal = CyGame().getSorenRandNum(len(metalList), "a Quarter is HILL")
			iMetal = metalList[iRandomMetal]
			pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iMetal[0]))
			metalList.remove(iMetal)
			
			#if isBTPon:#2.38
			iRandomPlot = CyGame().getSorenRandNum(len(ThisHubList), "a Quarter is HILL")
			x =  ThisHubList[iRandomPlot][0]			
			y =  ThisHubList[iRandomPlot][1]
			ThisHubList.remove([x,y])
			pChosenPlot = CyMap().plot(x,y)
			iRandomFolk = CyGame().getSorenRandNum(len(folkList), "a Quarter is HILL")
			iFolk = folkList[iRandomFolk]
			pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iFolk[0]))
			folkList.remove(iFolk)	

	if (CyMap().getCustomMapOption(6) >= 3):#because the hub is bigger
		
		calendarList = [["BONUS_DYE"],["BONUS_SPICE"],["BONUS_SILK"],["BONUS_SUGAR"],["BONUS_WINE"],["BONUS_BANANA"]]
		for iThisHub in range(0,4):
			ThisHubList = []
			for p in range(len(islandPlotList)):
				if islandPlotList[p][2] == iThisHub:
					x =  islandPlotList[p][0]			
					y =  islandPlotList[p][1]
					pPlot = CyMap().plot(x,y)
					if (pPlot.getBonusType(-1) == BonusTypes.NO_BONUS):
						ThisHubList.append([x,y])			
	
			iRandomPlot = CyGame().getSorenRandNum(len(ThisHubList), "a Quarter is HILL")
			x =  ThisHubList[iRandomPlot][0]			
			y =  ThisHubList[iRandomPlot][1]
			ThisHubList.remove([x,y])
			pChosenPlot = CyMap().plot(x,y)
			iRandomCalendar = CyGame().getSorenRandNum(len(calendarList), "a Quarter is HILL")
			iCalendar = calendarList[iRandomCalendar]
			pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iCalendar[0]))
			calendarList.remove(iCalendar)			
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride



'''8 )    startHumansOnSameTile()'''	
def startHumansOnSameTile():
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(8) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(8) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)


	if (CyMap().getCustomMapOption(11) == 1):
		return True	

''' 9) Map Depended local logic for Food and Bonus placement'''	

''' 11 - BTG local/map Redclaration of MapGeneratorUtil functions for logic '''
def BTPTopBottomTwoTeams(isBTG):							
	gc = CyGlobalContext()	
	
	#2.19 debug		
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))	
				
	iEverAliveTeamCount = 0
	
	for iI in range(gc.getMAX_CIV_TEAMS()):	
		if isBTG:
			if gc.getTeam(iI).isEverAlive() and not gc.getTeam(iI).isSpectator() and not gc.getTeam(iI).isBarbarian():
				iEverAliveTeamCount += 1
		else:
			if gc.getTeam(iI).isEverAlive() and not gc.getTeam(iI).isBarbarian():
				iEverAliveTeamCount += 1			

	if gc.getGame().countCivPlayersEverAlive() <= 3:
		return None			
		
	if (gc.getGame().countCivPlayersEverAlive() % 2) != 0 :#verify it's even number, if not don't apply
		return None	
				
	elif not iEverAliveTeamCount == 2:
		return None
		
	else:
	
		#############################
		#Spectator bit - not amazing if spectator is middle team

	
		listTeams = []
		#2.23 Improve for spectators
		for iI in range(gc.getMAX_CIV_TEAMS()):	
			if isBTG:
				if not gc.getTeam(iI).isSpectator():
					if gc.getTeam(iI).isEverAlive():				
						listTeams.append(gc.getTeam(iI).getID())
			else:
				if gc.getTeam(iI).isEverAlive():				
					listTeams.append(gc.getTeam(iI).getID())				
				
		random.shuffle(listTeams)		
		teamOne = listTeams[0]
		teamTwo = listTeams[1]
		###########################

		listPlot = []
		listPlayer = []
		iH = CyMap().getGridHeight()
		halfHeight = iH / 2
		for iI in range(gc.getMAX_CIV_PLAYERS()):
			if isBTG:
				if (gc.getPlayer(iI).isAlive() and not gc.getPlayer(iI).isSpectator()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())
			else:
				if (gc.getPlayer(iI).isAlive()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())				
		
		#only do team one it will be good 		
		listCurrentPlayer = listPlayer
		for iI in range(gc.getMAX_CIV_PLAYERS()):
			bDoThis = False
			if isBTG:
				if (gc.getPlayer(iI).isAlive() and not gc.getPlayer(iI).isSpectator()):
					bDoThis = True
			else:
				if (gc.getPlayer(iI).isAlive()):
					bDoThis = True				
			if bDoThis:
				if (gc.getPlayer(iI).getTeam() == teamOne and gc.getPlayer(iI).getStartingPlot().getY() >= halfHeight):						
					random.shuffle(listCurrentPlayer)
					iRoll = listCurrentPlayer[0]
					#while ((gc.getPlayer(iRoll).getStartingPlot().getY() >= halfHeight) or (iRoll == iI)):#I roll until it's a bottom tile
					#2.23 - Problem is, on the last "fix" you can send a teammate back on top
					while ((gc.getPlayer(iRoll).getStartingPlot().getY() >= halfHeight) or (iRoll == iI) or gc.getPlayer(iRoll).getTeam() == teamOne):#I roll until it's a bottom tile
						random.shuffle(listCurrentPlayer)
						iRoll = listCurrentPlayer[0]
					
					spotA = gc.getPlayer(iI).getStartingPlot()
					spotB = gc.getPlayer(iRoll).getStartingPlot()
					gc.getPlayer(iI).setStartingPlot(spotB,True)
					gc.getPlayer(iRoll).setStartingPlot(spotA,True)		
					
					
					
def BTPForceResourceLand(iProbaTreshold,bMainLandOnly,iResourceType,iDistance,bMakeHill,iForceTerrain):

	gc = CyGlobalContext()
	map = CyMap()
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))

	for i in range(gc.getMAX_CIV_PLAYERS()):
	
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= iProbaTreshold:
	
			if gc.getPlayer(i).isEverAlive():
				start_plot = gc.getPlayer(i).getStartingPlot()
				startx, starty = start_plot.getX(), start_plot.getY()
				plotsboundaries = []
				plotsboundariesSafe = []
				plotsboundariesSafeNoRiver = []
				has_resource = false
				for dx in range(-iDistance,iDistance):
					for dy in range(-iDistance,iDistance):
						p = map.plot(startx+dx,starty+dy)
						#if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						if (bMainLandOnly == True) :
							if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()) and p.getArea() == CyMap().findBiggestArea(False).getID():	
								iBonusCount = 0
								for tx in range(3):
									for ty in range(3):
										testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
										if (testP.getBonusType(-1) != -1):
											iBonusCount += 1		
								if iBonusCount >= 1:
									plotsboundaries.append(p)
								elif not p.isRiver():
									plotsboundariesSafeNoRiver.append(p)
								else :
									plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
								if p.getBonusType(-1) == iResourceType:
									has_resource = True
						if (bMainLandOnly == False) :								
							if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):			
								iBonusCount = 0
								for tx in range(3):
									for ty in range(3):
										testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
										if (testP.getBonusType(-1) != -1):
											iBonusCount += 1		
								if iBonusCount >= 1:
									plotsboundaries.append(p)
								elif not p.isRiver():
									plotsboundariesSafeNoRiver.append(p)										
								else :
									plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
								if p.getBonusType(-1) == iResourceType:
									has_resource = True
									
				if not has_resource:
					if len(plotsboundariesSafeNoRiver) > 0:	#2.34 new block									
						random.shuffle(plotsboundariesSafeNoRiver)	
						for p in plotsboundariesSafeNoRiver:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break						
				
					elif len(plotsboundariesSafe) > 0:										
						random.shuffle(plotsboundariesSafe)	
						for p in plotsboundariesSafe:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break
								
					else:								
						random.shuffle(plotsboundaries)	
						for p in plotsboundaries:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break					
								
								
								
								
def BTPForceEnrichFood(iProbaTreshold,bMainLandOnly,iResourceType,iMaxDistance,iMinDistance,bMakeHill,iForceTerrain):		

		gc = CyGlobalContext()
		map = CyMap()
		random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
		
		
		for i in range(gc.getMAX_CIV_PLAYERS()):
			
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba <= iProbaTreshold:
		
				if gc.getPlayer(i).isEverAlive():
					start_plot = gc.getPlayer(i).getStartingPlot()
					startx, starty = start_plot.getX(), start_plot.getY()
					plotsboundaries = []
					plotsboundariesSafe = []
					for dx in range(-iMaxDistance,iMaxDistance):
						for dy in range(-iMaxDistance,iMaxDistance):
							p = map.plot(startx+dx,starty+dy)
							if (bMainLandOnly == True) :
								if ((dx != 0) or (dy != 0)) and (not p.isImpassable()) and (not p.isWater()) and p.getArea() == CyMap().findBiggestArea(False).getID():				
									if ((abs(dx) >= iMinDistance) and (abs(dy) >= iMinDistance)):
										iBonusCount = 0
										for tx in range(3):
											for ty in range(3):
												testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
												if (testP.getBonusType(-1) != -1):
													iBonusCount += 1		
										if iBonusCount >= 1:
											plotsboundaries.append(p)
										else :
											plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
	
							if (bMainLandOnly == False) :
								if ((dx != 0) or (dy != 0)) and (not p.isImpassable()) and (not p.isWater()):				
									if ((abs(dx) >= iMinDistance) and (abs(dy) >= iMinDistance)):
										iBonusCount = 0
										for tx in range(3):
											for ty in range(3):
												testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
												if (testP.getBonusType(-1) != -1):
													iBonusCount += 1		
										if iBonusCount >= 1:
											plotsboundaries.append(p)
										else :
											plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority								
										

					if len(plotsboundariesSafe) > 0:
										
						random.shuffle(plotsboundariesSafe)	
						for p in plotsboundariesSafe:
							#if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(iResourceType, True):
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):#I don't care, I make my own plot anyway
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)#I Like to see it in this case too					
								p.setBonusType(iResourceType)
								p.setFeatureType(-1, -1)#2.25 -- Need remove floodplains, and forest then	
								break
								
					else:	
						random.shuffle(plotsboundaries)
						for p in plotsboundaries:
							#if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(iResourceType, True):
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):#I don't care, I make my own plot anyway
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)#I Like to see it in this case too					
								p.setBonusType(iResourceType)
								p.setFeatureType(-1, -1)#2.25 -- Need remove floodplains, and forest then	
								break								
								
								
								
''' 12 - BTG Dedicated Always call category'''	
def BTGFreeUnit():

	if (CyMap().getCustomMapOption(14) == 0):
		return -1
	elif (CyMap().getCustomMapOption(14) == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (CyMap().getCustomMapOption(14) == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (CyMap().getCustomMapOption(14) == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():

	iCount = CyMap().getCustomMapOption(15)	
		
	return iCount									