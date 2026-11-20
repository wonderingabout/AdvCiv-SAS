from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

import random #2.25

balancer = BonusBalancer()

def getDescription():
	return "Beyond the Game map by Penny based on idea of PandoraRevenge"
	
def getDescriptionTitle():
	return "This land map offers a land of hexagonal shape imbricated so that all players have a similarly shaped start"

def getDescriptionTitleTwo():
	return "The hexagone size are constant, so the map size changes in HEIGHT depending on amount of players"

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "The start positions of teams are left versus right, so be mindful that you are meant to have the same ennemies both side of you, offering 4 fronts to 2 different ennemies"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "The edges are normally made of impassable terrain but you can make them water if you wish"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Any teamer with a focus on early (ancient, classical) starts. Game will be relatively short and violent, it will be hard to advance far in the tech path"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Immediate impact traits are strong, AGGRESSIVE and EXPANSIVE leading the way"	

def getNumCustomMapOptions():
	return 16

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"Edges Count",
		3:	"Edges Type",
		4:	"Edges Size",
		5:	"Map Size",
		6:	"BTG Resources",
		7:	"BTG Forest Type",
		8:	"Start Position",
		9:	"BTG Free Unit",
		10: "BTG Amt Free Unit",		
		11:  "Starting Units",
		12:	"BTG Music",
		13:	"Notes",
		14:	"BTG Spectator Notes",
		15:  "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:  4,
		2:	2,
		3:	2,
		4:	3,
		5:	6,
		6:	2,
		7:	2,
		8:	3,
		9:	5,
		10:  4,			
		11:	2,
		12:	3,
		13:	1,
		14:	1,
		15: 1
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
			0: "TXT_KEY_WORLD_STANDARD",
			1: "Balanced - Including Oil",
			2: "Balanced Enriched - Including Oil ",
			3: "Balanced for Pandemonium"
			},
		2:	{
			0: "0 Edge - All desert",
			1: "2 Edges"
			},	
		3:	{
			0: "Water",
			1: "Impassable"
			},	
		4:	{
			0: "Small Edges",
			1: "Normal Edges",
			2: "Very Large Edges",
			},				
		5:	{
			0: "Very Very small - 20 tiles wide, 12 tiles high by player",
			1: "Very Small - 24 Tiles wide, 14 tiles high by player",
			2: "Small - 28 Tiles wide, 16 tiles high by player",
			3: "Normal - 32 Tiles wide, 18 tiles high by player",
			4: "Large - 36 Tiles wide, 20 tiles high by player",
			5: "Super Large - 40 Tiles wide, 22 tiles high by player",
			},				
		6:	{
			0: "No",
			1: "Yes - Balanced for Lead and Amber, Normal for others"
			},	
		7:	{
			0: "Normal Forest",
			1: "Palm Forest always"			
			},				
		8:	{
			0: "Normal, Close together",
			1: "Left vs Right",
			2: "Anywhere"
			},
		9:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			4: "Great Legend"
			},
		10:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},				
		11:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},
		12:	{
			0: "Normal",
			1: "Age of Agriculture",
			2: "Age of Robotics"
			},					
		13:	{
			0: "For an EVEN number of players up to TEN"
			},			
		14:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"
			},
		15:	{
			0: "Penny for BTG - from PandoraRevenge's idea"
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:  3,
		2:	1,
		3:	1,
		4:	1,
		5:	2,
		6:	1,
		7:	0,
		8:	1,
		9:	4,
		10:	0,		
		11:	0,
		12:	1,
		13:	0,
		14:	0,
		15:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	false,
		2:	true,
		3:  true,
		4:	true,
		5:	true,
		6:	false,
		7:  false,
		8:  false,		
		9:  false,		
		10:	false,
		11:	false,
		12:	false,
		13:	false,
		14:	false,
		15:	false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)	
	
def normalizeAddExtras():

	if (CyMap().getCustomMapOption(1) >= 1):
		balancer.normalizeAddExtras()
		
	#BTG
	if CyMap().getCustomMapOption(1) >= 1:
	
		BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
	
		if (CyMap().getCustomMapOption(1) <= 2):#I don't want it for option balanced Pandemonium
			BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
	
		if (CyMap().getCustomMapOption(1) >= 2):	
			BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,3,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
			BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
						
	#2.25 Map Specific
	if CyMap().getCustomMapOption(1) == 3:
	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),7,6,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	

		#BTPMapUtil().BTPForceEnrichFood(25,True,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))#2.32
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_WINE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SILK"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		
	if isBTPon and (CyMap().getCustomMapOption(1) == 3):		
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_AMBER"),4,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
		
	#End Map Specific		
	if isBTPon :
		if (CyMap().getCustomMapOption(6) == 1):#2.35
			listToBalance = ["BONUS_LEAD","BONUS_AMBER"]
			balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):

	doFillEdges()#2.28
	doCleanLava()#2.28

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.25 Map Specific -- Mostly from Eldorado
	BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')#2.18
	#BTPResourcesToEliminate = ('BONUS_SULPHUR','BONUS_AMBER','BONUS_IVORY','BONUS_MARBLE','BONUS_STONE','BONUS_GEMS','BONUS_SILVER','BONUS_GOLD') #From Eldorado
	#BTPalsoOff = ('BONUS_WHEAT','BONUS_WINE','BONUS_SILK','BONUS_SPICE','BONUS_DYE','BONUS_SUGAR','BONUS_BANANA') #From Eldorado
	#BTPResourcesToEliminate = ('BONUS_GEMS','BONUS_SILVER','BONUS_GOLD')
	BTPResourcesToEliminate = ('BONUS_GEMS','BONUS_SILVER','BONUS_GOLD','BONUS_IVORY')#2.32
	BTPalsoOff = ('BONUS_WINE','BONUS_SILK','BONUS_SPICE','BONUS_DYE')

	if isBTPon and (CyMap().getCustomMapOption(1) == 3):
		if (type_string in BTPResourcesToBalance) or (type_string in BTPResourcesToEliminate) or (type_string in BTPalsoOff):
			return None # don't place any of this bonus randomly	
	#End Map Specific
	
	else:
		if isBTPon:
			if (CyMap().getCustomMapOption(6) == 0):#all excluded
				if (type_string in balancer.newResourcesBTP):
					return None

		if (CyMap().getCustomMapOption(1) >= 1):
			if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
				return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def isClimateMap():
	return 0

def isSeaLevelMap():
	return 0

def getGridSize(argsList):
	"Override Grid Size function to make the maps square."
	if (CyMap().getCustomMapOption(5) == 0):
		x = 6		
	if (CyMap().getCustomMapOption(5) == 1):
		x = 7
	if (CyMap().getCustomMapOption(5) == 2):
		x = 8
	if (CyMap().getCustomMapOption(5) == 3):
		x = 9
	if (CyMap().getCustomMapOption(5) == 4):
		x = 10
	if (CyMap().getCustomMapOption(5) == 5):
		x = 11		
		
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	y = x * iPlayers / 4
	
	#because those are circles
	x = x - 1
	
	return (x, y)		


class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=3):
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
		iHoleRadius += 3#2.23
		userInputCenter = self.map.getCustomMapOption(0)
		
		
		
		
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x

				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
				if (iProba < 3):#2.28
					self.plotTypes[i] = PlotTypes.PLOT_PEAK
				elif (iProba < 22):
					self.plotTypes[i] = PlotTypes.PLOT_HILLS
				else :
					self.plotTypes[i] = PlotTypes.PLOT_LAND
		
									
		if shift_plot_types:
			self.shiftPlotTypes()

		return self.plotTypes
		
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()

# subclass TerrainGenerator to create a lush grassland utopia.
class DonutTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1, grain_amount=5):
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
		self.iHoleRadius += 3#2.23
		self.userInputCenter = self.map.getCustomMapOption(0)
		
	def initFractals(self):
		self.terrain.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iGrassBottom = self.terrain.getHeightFromPercent(12)

		self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
		self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
		self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")

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

		#version B - Simplified
		val = self.terrain.getHeight(iX, iY)
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= 0:#changed, don't want "normal desert"
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")		
		if iProba <= 4:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
		elif iProba <= 32:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")				
		else:#then normal
			if val >= self.iGrassBottom:
				terrainVal = self.terrainGrass
			else:
				terrainVal = self.terrainPlains	

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Donut) ...")
	terraingen = DonutTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class DonutFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		# We don' need no steeking ice. M'kay? Alrighty then.
		ice = 0
		
	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		jungle = 0	

def addFeatures():
	NiTextOut("Adding Features (Python Donut) ...")
	featuregen = DonutFeatureGenerator()
	featuregen.addFeatures()
	return 0
	
	
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
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
				
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTemplateRoll = 0#Because only 1 template for each
	
	fVar = 2 #2.28 reduced
	
	templates = {(1,0): {0: [0.50, 0.50, int(0.5 * iW), int(0.5 * iH)]},
				 (2,0): {0: [0.25, 0.37, fVar, int(0.5 * iH)],
						 1: [0.75, 0.73, fVar, int(0.5 * iH)]},
				 (3,0): {0: [0.25, 0.25, fVar, fVar],
						 1: [0.25, 0.75, fVar, fVar],
						 2: [0.75, 0.50, fVar, fVar]},
				 (4,0): {0: [0.25, 0.25, fVar, fVar],
						 1: [0.25, 0.75, fVar, fVar],
						 2: [0.75, 0.50, fVar, fVar],
						 3: [0.75, 0.98, fVar, fVar]},
				 (5,0): {0: [0.25, 0.16, fVar, fVar],
						 1: [0.25, 0.50, fVar, fVar],
						 2: [0.25, 0.83, fVar, fVar],
						 3: [0.75, 0.33, fVar, fVar],
						 4: [0.75, 0.66, fVar, fVar]},
				 (6,0): {0: [0.25, 0.16, fVar, fVar],
						 1: [0.25, 0.50, fVar, fVar],
						 2: [0.25, 0.83, fVar, fVar],
						 3: [0.75, 0.33, fVar, fVar],
						 4: [0.75, 0.66, fVar, fVar],
						 5: [0.75, 0.98, fVar, fVar]},	
				 (7,0): {0: [0.25, 0.12, fVar, fVar],
						 1: [0.25, 0.37, fVar, fVar],
						 2: [0.25, 0.62, fVar, fVar],
						 3: [0.25, 0.87, fVar, fVar],
						 4: [0.75, 0.25, fVar, fVar],
						 5: [0.75, 0.50, fVar, fVar],
						 6: [0.75, 0.75, fVar, fVar]},	
				 (8,0): {0: [0.25, 0.12, fVar, fVar],
						 1: [0.25, 0.37, fVar, fVar],
						 2: [0.25, 0.62, fVar, fVar],
						 3: [0.25, 0.87, fVar, fVar],
						 4: [0.75, 0.25, fVar, fVar],
						 5: [0.75, 0.50, fVar, fVar],
						 6: [0.75, 0.75, fVar, fVar],
						 7: [0.75, 0.98, fVar, fVar]},							 	
				 (9,0): {0: [0.25, 0.10, fVar, fVar],
						 1: [0.25, 0.30, fVar, fVar],
						 2: [0.25, 0.50, fVar, fVar],
						 3: [0.25, 0.70, fVar, fVar],
						 4: [0.25, 0.90, fVar, fVar],
						 5: [0.75, 0.20, fVar, fVar],
						 6: [0.75, 0.40, fVar, fVar],
						 7: [0.75, 0.60, fVar, fVar],
						 8: [0.75, 0.80, fVar, fVar]},	
				 (10,0): {0: [0.25, 0.10, fVar, fVar],
						 1: [0.25, 0.30, fVar, fVar],
						 2: [0.25, 0.50, fVar, fVar],
						 3: [0.25, 0.70, fVar, fVar],
						 4: [0.25, 0.90, fVar, fVar],
						 5: [0.75, 0.20, fVar, fVar],
						 6: [0.75, 0.40, fVar, fVar],
						 7: [0.75, 0.60, fVar, fVar],
						 8: [0.75, 0.80, fVar, fVar],
						 9: [0.75, 0.98, fVar, fVar]},							 
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
			
				
		
	return None		
	

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

def normalizeStartingPlotLocations():

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
	
	if (CyMap().getCustomMapOption(8) == 1):
		if isBTPon :
			BTPLeftRightTwoTeams(True)		
		else:
			BTPLeftRightTwoTeams(False)			
	elif (CyMap().getCustomMapOption(8) == 2):
		return
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case	

def startHumansOnSameTile():
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(7) > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)


	if (CyMap().getCustomMapOption(11) == 1):
		return True	


def BTGSong():

	if (CyMap().getCustomMapOption(12) > 0):
		CyGame().setMapTriggerSound(CyMap().getCustomMapOption(12))
		return 1 # Has to be 1 to activate	
	else:
		return 0


def doFillEdges():
	
	if (CyMap().getCustomMapOption(5) == 0):
		xSize = 7
	if (CyMap().getCustomMapOption(5) == 1):
		xSize = 8
	if (CyMap().getCustomMapOption(5) == 2):
		xSize = 9
	if (CyMap().getCustomMapOption(5) == 3):
		xSize = 10
	if (CyMap().getCustomMapOption(5) == 4):
		xSize = 11

	global templates
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	

	for iLoopPlayer in range(iPlayers+1):#+1 for the special pass of the top right slot
	
		currentPlotList = []
		widePlotList = []
		highPlotList = []
	
		if iLoopPlayer < iPlayers:
			[fLat, fLon, varX, varY] = templates[(iPlayers, 0)][iLoopPlayer]
			iCenterX = int(CyMap().getGridWidth() * fLat)
			iCenterY = int(CyMap().getGridHeight() * fLon)
		else:
			iCenterX = int(CyMap().getGridWidth() * 0.75)
			iCenterY = 0 #because the last template normally is 1.00, it only does the bottom arc, and I want the top arc too			
			
		iRadius = xSize+1
		iHoleRadius = xSize-2

		##### This needs work, more condition ######
		#Almost perfect but I'm missing the 6th TOP RIGHT loop because of counting convention
		for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				i = y*CyMap().getGridWidth() + x			
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
								
				if fDistance <= iRadius and fDistance >= iHoleRadius:
					p = CyMap().plotByIndex(i)#2.28
					##### This needs work, more condition ######
					if abs(x - iCenterX) >= (xSize / 2) + CyMap().getCustomMapOption(4):#Adding value at the end "thickens" the edge
						widePlotList.append(p)
					elif abs(y - iCenterY) >= xSize / 2:
						highPlotList.append(p)
					else:
						currentPlotList.append(p)
					
		iDesert = CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT")
		iCoast = CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")
		if isBTPon:
			iImpassable = CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA")
		else:
			iImpassable = CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK")
			
		if (CyMap().getCustomMapOption(3) == 0):
			iChosen = iCoast	
		if (CyMap().getCustomMapOption(3) == 1):
			iChosen = iImpassable	
		#The shuffle crashes for some reason, I think when a type overlaps another
		'''if (CyMap().getCustomMapOption(3) == 2):
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba < 50:
				iChosen = iImpassable			
			else:
				iChosen = iCoast'''			
			
			
		if (CyMap().getCustomMapOption(2) == 0):
			iWide = iDesert
			iHigh = iDesert
		if (CyMap().getCustomMapOption(2) == 1):
			iWide = iDesert
			iHigh = iChosen		
			
		for iPlotLoop in currentPlotList:
			iPlotLoop.setTerrainType(iDesert, True, True)
		for iPlotLoop in widePlotList:
			if iWide == CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK"): #Helps with BTS otherwise glitch of peak in water
				iPlotLoop.setPlotType(PlotTypes.PLOT_PEAK, True, True)
			else:
				iPlotLoop.setTerrainType(iWide, True, True)	
		for iPlotLoop in highPlotList:
			if iHigh == CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK"): #Helps with BTS otherwise glitch of peak in water
				iPlotLoop.setPlotType(PlotTypes.PLOT_PEAK, True, True)
			else:
				iPlotLoop.setTerrainType(iHigh, True, True)		


	#Spectator
	#Impassable should be larger
	
def doCleanLava():	
	if isBTPon:
		for x in range(CyMap().getGridWidth()):
				for y in range(CyMap().getGridHeight()):
					p = CyMap().plot(x,y)
					if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA")):
						p.setFeatureType(-1, -1)
	

	for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				p = CyMap().plot(x,y)
				if p.isPeak():
					p.setFeatureType(-1, -1)	
	
	
def BTPLeftRightTwoTeams(isBTG):			
			
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
		iW = CyMap().getGridWidth()
		halfWidth = iW / 2
		for iI in range(gc.getMAX_CIV_PLAYERS()):
			if isBTG:
				if (gc.getPlayer(iI).isAlive() and not gc.getPlayer(iI).isSpectator()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())
			else:
				if (gc.getPlayer(iI).isAlive()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())				
		
		bDoAgain = False
					
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
				if (gc.getPlayer(iI).getTeam() == teamOne and gc.getPlayer(iI).getStartingPlot().getX() >= halfWidth):						
					random.shuffle(listCurrentPlayer)
					iRoll = listCurrentPlayer[0]
					#while ((gc.getPlayer(iRoll).getStartingPlot().getX() >= halfWidth) or (iRoll == iI)):#I roll until it's a bottom tile
					while ((gc.getPlayer(iRoll).getStartingPlot().getX() >= halfWidth) or (iRoll == iI) or gc.getPlayer(iRoll).getTeam() == teamOne):#2.23
						random.shuffle(listCurrentPlayer)
						iRoll = listCurrentPlayer[0]
					
					spotA = gc.getPlayer(iI).getStartingPlot()
					spotB = gc.getPlayer(iRoll).getStartingPlot()
					gc.getPlayer(iI).setStartingPlot(spotB,True)
					gc.getPlayer(iRoll).setStartingPlot(spotA,True)		
					
def BTGFreeUnit():

	if (CyMap().getCustomMapOption(9) == 0):
		return -1
	elif (CyMap().getCustomMapOption(9) == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (CyMap().getCustomMapOption(9) == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (CyMap().getCustomMapOption(9) == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	elif (CyMap().getCustomMapOption(9) == 4):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_GREAT_LEGEND")				
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():

	iCount = CyMap().getCustomMapOption(10)	
		
	return iCount						
	
	
	
	
	
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