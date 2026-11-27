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
	return "TXT_KEY_MAP_SCRIPT_DONUT_DESCR"

def getNumCustomMapOptions():
	return 11

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"Edges Type",
		3:	"TXT_MAP_NEW_RESOURCE",
		4:	"TXT_KEY_FOREST_TYPE",
		5:	"TXT_KEY_MAP_STARTING_POSITION",
		6:  "TXT_KEY_MAP_SAME_TILE",
		7:	"BTG Music",
		8:	"Notes",
		9:	"TXT_KEY_MAP_NOTES_SPECTATOR",
		10:  "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:  4,
		2:	7,
		3:	2,
		4:	2,
		5:	3,
		6:	2,
		7:	3,
		8:	1,
		9:	1,
		10: 1
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
			1: "TXT_KEY_MAP_BALANCED",
			2: "TXT_KEY_MAP_BALANCED_ENRICHED",
			3: "Balanced for Pandemonium"
			},
		2:	{
			0: "All desert",
			1: "Set with Impassable",
			2: "Set with Impassable and Water",
			3: "Set with Water",
			4: "Randomized both Types",
			5: "Randomized all Water",
			6: "Randomized Heavy water"
			},			
		3:	{
			0: "TXT_KEY_MAP_NORMAL_VIA_OPTION",
			1: "TXT_KEY_MAP_NO_EXCLUDED"
			},	
		4:	{
			0: "TXT_KEY_FOREST_TYPE_ALL_FOREST",
			1: "TXT_KEY_FOREST_TYPE_ALL_PALM"			
			},				
		5:	{
			0: "TXT_KEY_MAP_NORMAL",
			1: "TXT_KEY_START_LEFT_V_RIGHT",
			2: "Anywhere"
			},
		6:	{
			0: "TXT_KEY_MAP_NORMAL_TILE",
			1: "TXT_KEY_MAP_TOGETHER_TILE"
			},
		7:	{
			0: "Normal",
			1: "Age of Agriculture",
			2: "Age of Robotics"
			},					
		8:	{
			0: "For 6 players ONLY"
			},			
		9:	{
			0: "TXT_KEY_MAP_SPECTATOR_SOLO_GOOD_ONE",
			1: "TXT_KEY_MAP_SPECTATOR_TEAM_GOOD_ONE"
			},
		10:	{
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
		2:	2,
		3:	0,
		4:	0,
		5:	0,
		6:	0,
		7:	1,
		8:	0,
		9:	0,
		10:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	false,
		2:	false,
		3:  false,
		4:	false,
		5:	false,
		6:	false,
		7:  false,
		8:  false,		
		9:  false,		
		10:	false		
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
	if isBTPon:
		CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
		CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
		
		if (CyMap().getCustomMapOption(1) >= 2):	
			CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,3,False,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
			CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
			CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
						
	#2.25 Map Specific
	if isBTPon and (CyMap().getCustomMapOption(1) == 3):
	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_AMBER"),4,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"))
		
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(25,True,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
		
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_WINE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SILK"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
		CvMapGeneratorUtil.BTPMapUtil().BTPForceEnrichFood(40,True,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
		
	#End Map Specific		
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):

	doFillEdges()

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.25 Map Specific -- Mostly from Eldorado
	BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')#2.18
	#BTPResourcesToEliminate = ('BONUS_SULPHUR','BONUS_AMBER','BONUS_IVORY','BONUS_MARBLE','BONUS_STONE','BONUS_GEMS','BONUS_SILVER','BONUS_GOLD') #From Eldorado
	#BTPalsoOff = ('BONUS_WHEAT','BONUS_WINE','BONUS_SILK','BONUS_SPICE','BONUS_DYE','BONUS_SUGAR','BONUS_BANANA') #From Eldorado
	BTPResourcesToEliminate = ('BONUS_GEMS','BONUS_SILVER','BONUS_GOLD')
	BTPalsoOff = ('BONUS_WINE','BONUS_SILK','BONUS_SPICE','BONUS_DYE')

	if isBTPon and (CyMap().getCustomMapOption(1) == 3):
		if (type_string in BTPResourcesToBalance) or (type_string in BTPResourcesToEliminate) or (type_string in BTPalsoOff):
			return None # don't place any of this bonus randomly	
	#End Map Specific
	
	else:
		if isBTPon:
			if not CyGlobalContext().getGame().isOption(GameOptionTypes.GAMEOPTION_NEW_STRATEGIC_RESOURCE) or (CyMap().getCustomMapOption(3) == 1):#all excluded
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
	
	return (9, 13) 

def minStartingDistanceModifier():
	return -12

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
				if (iProba < 20):
					self.plotTypes[i] = PlotTypes.PLOT_HILLS
				else :
					self.plotTypes[i] = PlotTypes.PLOT_LAND
			
		doListEdges()# I list manually
									
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
		elif iProba <= 4:#changed, don't want "normal marsh"
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_MARSH")
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
	
	global listEdge0
	global listEdge1 
	global listEdge2 
	global listEdge3
	global listEdge4 
	global listEdge5 
	global listEdge6 
	global listEdge7 
	global listEdge8 
	global listEdge9
	global listEdge10 
	global listEdge11 
	global listEdge12
	global listEdge13
	global listEdge14
	global listEdge15
	global listEdge16
	global listEdge17
	global listEdge18
	global listEdge19
	global listEdge20
	global listEdge21
	global listEdge22
	global listEdge23
	global listEdge24
	global listEdgeAll 

	listEdge0 = []	
	listEdge1 = []	
	listEdge2 = []
	listEdge3 = []	
	listEdge4 = []	
	listEdge5 = []	
	listEdge6 = []	
	listEdge7 = []	
	listEdge8 = []
	listEdge9 = []	
	listEdge10 = []	
	listEdge11 = []	
	listEdge12 = []	
	listEdge13 = []	
	listEdge14 = []
	listEdge15 = []	
	listEdge16 = []	
	listEdge17 = []	
	listEdge18 = []	
	listEdge19 = []	
	listEdge20 = []
	listEdge21 = []	
	listEdge22 = []	
	listEdge23 = []	
	listEdge24 = []		
	listEdgeAll = []


	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
				
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTemplateRoll = 0#Because only 1 template for each
	
	#2.23 - Debug because it crashes if too close
	fVar = 3
	
	templates = {(1,0): {0: [0.50, 0.20, int(0.5 * iW), int(0.5 * iH)]},
				 (2,0): {0: [0.15, 0.50, fVar, int(0.5 * iH)],
						 1: [0.85, 0.50, fVar, int(0.5 * iH)]},
				 (3,0): {0: [0.15, 0.50, fVar, fVar],
						 1: [0.85, 0.50, fVar, fVar],
						 2: [0.50, 0.75, fVar, fVar]},
				 (4,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.25, 0.80, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.75, 0.80, fVar, fVar]},
				 (5,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.50, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.85, 0.50, fVar, fVar],
						 4: [0.50, 0.75, fVar, fVar]},
				 (6,0): {0: [0.25, 0.16, fVar, fVar],
						 1: [0.25, 0.50, fVar, fVar],
						 2: [0.25, 0.83, fVar, fVar],
						 3: [0.78, 0.33, fVar, fVar],
						 4: [0.78, 0.66, fVar, fVar],
						 5: [0.78, 0.98, fVar, fVar]},	
				 (7,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.85, 0.35, fVar, fVar],
						 4: [0.50, 0.75, fVar, fVar],
						 5: [0.15, 0.65, fVar, fVar],
						 6: [0.85, 0.65, fVar, fVar]},	
				 (8,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar],
						 6: [0.15, 0.65, fVar, fVar],
						 7: [0.85, 0.65, fVar, fVar]},							 	
				 (9,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.50, 0.75, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.15, 0.65, fVar, fVar],
						 6: [0.85, 0.65, fVar, fVar],
						 7: [0.10, 0.10, fVar, fVar],
						 8: [0.90, 0.10, fVar, fVar]},	
				 (10,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar],
						 6: [0.15, 0.65, fVar, fVar],
						 7: [0.85, 0.65, fVar, fVar],
						 8: [0.10, 0.10, fVar, fVar],
						 9: [0.90, 0.10, fVar, fVar]},							 
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
		
	if (isBTPon and CyMap().getCustomMapOption(5) == 1):
		CvMapGeneratorUtil.BTPMapUtil().BTPLeftRightTwoTeams()		
	elif (CyMap().getCustomMapOption(5) == 2):
		return
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case	

def startHumansOnSameTile():
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(4) > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)


	if (CyMap().getCustomMapOption(6) == 1):
		return True	


def BTGSong():

	if (CyMap().getCustomMapOption(7) > 0):
		CyGame().setMapTriggerSound(CyMap().getCustomMapOption(7))
		return 1 # Has to be 1 to activate	
	else:
		return 0


def doFillEdges():

	listOfList = [listEdge1,listEdge2,listEdge3,listEdge4,listEdge5,listEdge6,listEdge7,listEdge8,listEdge9,listEdge10,listEdge11,listEdge12,listEdge13,listEdge14,listEdge15,listEdge16,listEdge17,listEdge18,listEdge19,listEdge20,listEdge21,listEdge22,listEdge23,listEdge24]
	
	if (CyMap().getCustomMapOption(2) == 0):#Option Deserts

		for iListNo in listOfList:
			for iPlotLoop in iListNo:
				p = CyMap().plotByIndex(iPlotLoop)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)	
		
		
	if (CyMap().getCustomMapOption(2) > 0):		
		#Option 1  +2 + 3
		
		if (CyMap().getCustomMapOption(2) <= 3): 
			ListOfWater = [listEdge2,listEdge6,listEdge9,listEdge12]
			ListOfLava  = [listEdge1,listEdge5,listEdge16,listEdge17,listEdge19,listEdge20]
			ListOfRest	= [listEdge3,listEdge4,listEdge7,listEdge8,listEdge10,listEdge11,listEdge13,listEdge14,listEdge15,listEdge18,listEdge21,listEdge22,listEdge23,listEdge24]

		if (CyMap().getCustomMapOption(2) >= 4):#we will re-create/re-shuffle them
			
			random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
			random.shuffle(listOfList)
			
			ListOfLava = []
			ListOfRest = []
			ListOfWater = []
			ListOfRest = listOfList[:6]
			'''ListOfLava  = listOfList[18:]
			ListOfRest	= listOfList[7:17]'''
			
		if (CyMap().getCustomMapOption(2) == 3):
			iImpassable = CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")	
		elif isBTPon:
			iImpassable = CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA")
		else:
			iImpassable = CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK")
		
		if (CyMap().getCustomMapOption(2) == 1 or CyMap().getCustomMapOption(2) == 5 or CyMap().getCustomMapOption(2) == 6):			
			iWater = iImpassable
		else:
			iWater = CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")
		
		
		for iListNo in ListOfRest:
			for iPlotLoop in iListNo:
				p = CyMap().plotByIndex(iPlotLoop)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)	

		for iListNo in ListOfLava:
			for iPlotLoop in iListNo:
				p = CyMap().plotByIndex(iPlotLoop)
				p.setTerrainType(iImpassable, True, True)	
			
		for iListNo in ListOfWater:
			for iPlotLoop in iListNo:
				p = CyMap().plotByIndex(iPlotLoop)
				p.setTerrainType(iWater, True, True)					


def doListEdges():
		
	listEdge24.append(0)
	listEdge18.append(1)
	listEdge18.append(2)
	listEdge18.append(3)
	listEdge1.append(4)
	listEdge1.append(5)
	listEdge1.append(6)
	listEdge1.append(7)
	listEdge1.append(8)
	listEdge1.append(9)
	listEdge1.append(10)
	listEdge1.append(11)
	listEdge1.append(12)
	listEdge1.append(13)
	listEdge1.append(14)
	listEdge1.append(15)
	listEdge12.append(16)
	listEdge12.append(17)
	listEdge12.append(18)
	listEdge12.append(19)
	listEdge24.append(36)
	listEdge18.append(37)
	listEdge18.append(38)
	listEdge18.append(39)
	listEdge1.append(40)
	listEdge1.append(41)
	listEdge1.append(42)
	listEdge1.append(43)
	listEdge1.append(44)
	listEdge1.append(45)
	listEdge1.append(46)
	listEdge1.append(47)
	listEdge1.append(48)
	listEdge1.append(49)
	listEdge1.append(50)
	listEdge1.append(51)
	listEdge12.append(52)
	listEdge12.append(53)
	listEdge12.append(54)
	listEdge12.append(55)
	listEdge24.append(72)
	listEdge18.append(73)
	listEdge18.append(74)
	listEdge18.append(75)
	listEdge12.append(89)
	listEdge12.append(90)
	listEdge12.append(91)
	listEdge12.append(92)
	listEdge24.append(108)
	listEdge18.append(109)
	listEdge18.append(110)
	listEdge12.append(126)
	listEdge12.append(127)
	listEdge12.append(128)
	listEdge24.append(144)
	listEdge18.append(145)
	listEdge18.append(146)
	listEdge12.append(163)
	listEdge12.append(164)
	listEdge24.append(179)
	listEdge24.append(180)
	listEdge18.append(181)
	listEdge18.append(182)
	listEdge12.append(199)
	listEdge12.append(200)
	listEdge24.append(215)
	listEdge24.append(216)
	listEdge18.append(217)
	listEdge12.append(235)
	listEdge12.append(236)
	listEdge12.append(237)
	listEdge24.append(250)
	listEdge24.append(251)
	listEdge18.append(252)
	listEdge18.append(253)
	listEdge12.append(271)
	listEdge12.append(272)
	listEdge12.append(273)
	listEdge6.append(274)
	listEdge6.append(275)
	listEdge6.append(276)
	listEdge6.append(277)
	listEdge6.append(278)
	listEdge6.append(279)
	listEdge6.append(280)
	listEdge6.append(281)
	listEdge6.append(282)
	listEdge6.append(283)
	listEdge6.append(284)
	listEdge6.append(285)
	listEdge24.append(286)
	listEdge24.append(287)
	listEdge18.append(288)
	listEdge18.append(289)
	listEdge12.append(307)
	listEdge12.append(308)
	listEdge12.append(309)
	listEdge6.append(310)
	listEdge6.append(311)
	listEdge6.append(312)
	listEdge6.append(313)
	listEdge6.append(314)
	listEdge6.append(315)
	listEdge6.append(316)
	listEdge6.append(317)
	listEdge6.append(318)
	listEdge6.append(319)
	listEdge6.append(320)
	listEdge6.append(321)
	listEdge24.append(322)
	listEdge24.append(323)
	listEdge23.append(324)
	listEdge23.append(325)
	listEdge11.append(343)
	listEdge11.append(344)
	listEdge11.append(345)
	listEdge6.append(346)
	listEdge6.append(347)
	listEdge6.append(348)
	listEdge6.append(349)
	listEdge6.append(350)
	listEdge6.append(351)
	listEdge6.append(352)
	listEdge6.append(353)
	listEdge6.append(354)
	listEdge6.append(355)
	listEdge6.append(356)
	listEdge6.append(357)
	listEdge23.append(358)
	listEdge23.append(359)
	listEdge23.append(360)
	listEdge23.append(361)
	listEdge11.append(379)
	listEdge11.append(380)
	listEdge11.append(381)
	listEdge23.append(394)
	listEdge23.append(395)
	listEdge23.append(396)
	listEdge23.append(397)
	listEdge23.append(398)
	listEdge11.append(415)
	listEdge11.append(416)
	listEdge23.append(431)
	listEdge23.append(432)
	listEdge23.append(433)
	listEdge17.append(434)
	listEdge11.append(451)
	listEdge11.append(452)
	listEdge23.append(467)
	listEdge23.append(468)
	listEdge23.append(469)
	listEdge17.append(470)
	listEdge11.append(486)
	listEdge11.append(487)
	listEdge11.append(488)
	listEdge23.append(504)
	listEdge23.append(505)
	listEdge17.append(506)
	listEdge11.append(521)
	listEdge11.append(522)
	listEdge11.append(523)
	listEdge11.append(524)
	listEdge23.append(540)
	listEdge23.append(541)
	listEdge17.append(542)
	listEdge17.append(543)
	listEdge3.append(544)
	listEdge3.append(545)
	listEdge3.append(546)
	listEdge3.append(547)
	listEdge3.append(548)
	listEdge3.append(549)
	listEdge3.append(550)
	listEdge3.append(551)
	listEdge3.append(552)
	listEdge3.append(553)
	listEdge3.append(554)
	listEdge3.append(555)
	listEdge11.append(556)
	listEdge11.append(557)
	listEdge11.append(558)
	listEdge11.append(559)
	listEdge23.append(576)
	listEdge23.append(577)
	listEdge17.append(578)
	listEdge17.append(579)
	listEdge3.append(580)
	listEdge3.append(581)
	listEdge3.append(582)
	listEdge3.append(583)
	listEdge3.append(584)
	listEdge3.append(585)
	listEdge3.append(586)
	listEdge3.append(587)
	listEdge3.append(588)
	listEdge3.append(589)
	listEdge3.append(590)
	listEdge3.append(591)
	listEdge11.append(592)
	listEdge11.append(593)
	listEdge11.append(594)
	listEdge11.append(595)
	listEdge23.append(612)
	listEdge23.append(613)
	listEdge17.append(614)
	listEdge17.append(615)
	listEdge3.append(616)
	listEdge3.append(617)
	listEdge3.append(618)
	listEdge3.append(619)
	listEdge3.append(620)
	listEdge3.append(621)
	listEdge3.append(622)
	listEdge3.append(623)
	listEdge3.append(624)
	listEdge3.append(625)
	listEdge3.append(626)
	listEdge3.append(627)
	listEdge11.append(628)
	listEdge11.append(629)
	listEdge11.append(630)
	listEdge11.append(631)
	listEdge22.append(648)
	listEdge23.append(649)
	listEdge16.append(650)
	listEdge16.append(651)
	listEdge3.append(652)
	listEdge3.append(653)
	listEdge3.append(654)
	listEdge3.append(655)
	listEdge3.append(656)
	listEdge3.append(657)
	listEdge3.append(658)
	listEdge3.append(659)
	listEdge3.append(660)
	listEdge3.append(661)
	listEdge3.append(662)
	listEdge3.append(663)
	listEdge10.append(664)
	listEdge10.append(665)
	listEdge10.append(666)
	listEdge10.append(667)
	listEdge22.append(684)
	listEdge22.append(685)
	listEdge16.append(686)
	listEdge16.append(687)
	listEdge10.append(701)
	listEdge10.append(702)
	listEdge10.append(703)
	listEdge22.append(720)
	listEdge22.append(721)
	listEdge16.append(722)
	listEdge16.append(723)
	listEdge10.append(738)
	listEdge10.append(739)
	listEdge10.append(740)
	listEdge22.append(756)
	listEdge22.append(757)
	listEdge16.append(758)
	listEdge16.append(759)
	listEdge10.append(775)
	listEdge10.append(776)
	listEdge22.append(791)
	listEdge22.append(792)
	listEdge22.append(793)
	listEdge16.append(794)
	listEdge10.append(811)
	listEdge10.append(812)
	listEdge22.append(827)
	listEdge22.append(828)
	listEdge22.append(829)
	listEdge10.append(847)
	listEdge10.append(848)
	listEdge10.append(849)
	listEdge22.append(862)
	listEdge22.append(863)
	listEdge22.append(864)
	listEdge22.append(865)
	listEdge10.append(883)
	listEdge10.append(884)
	listEdge10.append(885)
	listEdge5.append(886)
	listEdge5.append(887)
	listEdge5.append(888)
	listEdge5.append(889)
	listEdge5.append(890)
	listEdge5.append(891)
	listEdge5.append(892)
	listEdge5.append(893)
	listEdge5.append(894)
	listEdge5.append(895)
	listEdge5.append(896)
	listEdge5.append(897)
	listEdge22.append(898)
	listEdge22.append(899)
	listEdge15.append(900)
	listEdge15.append(901)
	listEdge10.append(919)
	listEdge10.append(920)
	listEdge10.append(921)
	listEdge5.append(922)
	listEdge5.append(923)
	listEdge5.append(924)
	listEdge5.append(925)
	listEdge5.append(926)
	listEdge5.append(927)
	listEdge5.append(928)
	listEdge5.append(929)
	listEdge5.append(930)
	listEdge5.append(931)
	listEdge5.append(932)
	listEdge5.append(933)
	listEdge22.append(934)
	listEdge22.append(935)
	listEdge15.append(936)
	listEdge15.append(937)
	listEdge9.append(955)
	listEdge9.append(956)
	listEdge9.append(957)
	listEdge5.append(958)
	listEdge5.append(959)
	listEdge5.append(960)
	listEdge5.append(961)
	listEdge5.append(962)
	listEdge5.append(963)
	listEdge5.append(964)
	listEdge5.append(965)
	listEdge5.append(966)
	listEdge5.append(967)
	listEdge5.append(968)
	listEdge5.append(969)
	listEdge22.append(970)
	listEdge22.append(971)
	listEdge21.append(972)
	listEdge15.append(973)
	listEdge15.append(974)
	listEdge9.append(991)
	listEdge9.append(992)
	listEdge9.append(993)
	listEdge5.append(994)
	listEdge5.append(995)
	listEdge5.append(996)
	listEdge5.append(997)
	listEdge5.append(998)
	listEdge5.append(999)
	listEdge5.append(1000)
	listEdge5.append(1001)
	listEdge5.append(1002)
	listEdge5.append(1003)
	listEdge5.append(1004)
	listEdge5.append(1005)
	listEdge21.append(1006)
	listEdge21.append(1007)
	listEdge21.append(1008)
	listEdge15.append(1009)
	listEdge15.append(1010)
	listEdge9.append(1027)
	listEdge9.append(1028)
	listEdge21.append(1043)
	listEdge21.append(1044)
	listEdge15.append(1045)
	listEdge15.append(1046)
	listEdge9.append(1063)
	listEdge9.append(1064)
	listEdge21.append(1079)
	listEdge21.append(1080)
	listEdge15.append(1081)
	listEdge15.append(1082)
	listEdge9.append(1098)
	listEdge9.append(1099)
	listEdge21.append(1116)
	listEdge15.append(1117)
	listEdge15.append(1118)
	listEdge15.append(1119)
	listEdge9.append(1133)
	listEdge9.append(1134)
	listEdge9.append(1135)
	listEdge21.append(1152)
	listEdge15.append(1153)
	listEdge15.append(1154)
	listEdge15.append(1155)
	listEdge2.append(1156)
	listEdge2.append(1157)
	listEdge2.append(1158)
	listEdge2.append(1159)
	listEdge2.append(1160)
	listEdge2.append(1161)
	listEdge2.append(1162)
	listEdge2.append(1163)
	listEdge2.append(1164)
	listEdge2.append(1165)
	listEdge2.append(1166)
	listEdge2.append(1167)
	listEdge9.append(1168)
	listEdge9.append(1169)
	listEdge9.append(1170)
	listEdge9.append(1171)
	listEdge21.append(1188)
	listEdge15.append(1189)
	listEdge15.append(1190)
	listEdge15.append(1191)
	listEdge2.append(1192)
	listEdge2.append(1193)
	listEdge2.append(1194)
	listEdge2.append(1195)
	listEdge2.append(1196)
	listEdge2.append(1197)
	listEdge2.append(1198)
	listEdge2.append(1199)
	listEdge2.append(1200)
	listEdge2.append(1201)
	listEdge2.append(1202)
	listEdge2.append(1203)
	listEdge9.append(1204)
	listEdge9.append(1205)
	listEdge9.append(1206)
	listEdge9.append(1207)
	listEdge14.append(1224)
	listEdge14.append(1225)
	listEdge14.append(1226)
	listEdge14.append(1227)
	listEdge2.append(1228)
	listEdge2.append(1229)
	listEdge2.append(1230)
	listEdge2.append(1231)
	listEdge2.append(1232)
	listEdge2.append(1233)
	listEdge2.append(1234)
	listEdge2.append(1235)
	listEdge2.append(1236)
	listEdge2.append(1237)
	listEdge2.append(1238)
	listEdge2.append(1239)
	listEdge8.append(1240)
	listEdge8.append(1241)
	listEdge8.append(1242)
	listEdge8.append(1243)
	listEdge14.append(1260)
	listEdge14.append(1261)
	listEdge14.append(1262)
	listEdge14.append(1263)
	listEdge2.append(1264)
	listEdge2.append(1265)
	listEdge2.append(1266)
	listEdge2.append(1267)
	listEdge2.append(1268)
	listEdge2.append(1269)
	listEdge2.append(1270)
	listEdge2.append(1271)
	listEdge2.append(1272)
	listEdge2.append(1273)
	listEdge2.append(1274)
	listEdge2.append(1275)
	listEdge8.append(1276)
	listEdge8.append(1277)
	listEdge8.append(1278)
	listEdge8.append(1279)
	listEdge14.append(1296)
	listEdge14.append(1297)
	listEdge14.append(1298)
	listEdge14.append(1299)
	listEdge8.append(1313)
	listEdge8.append(1314)
	listEdge8.append(1315)
	listEdge14.append(1332)
	listEdge14.append(1333)
	listEdge14.append(1334)
	listEdge8.append(1350)
	listEdge8.append(1351)
	listEdge8.append(1352)
	listEdge20.append(1367)
	listEdge14.append(1368)
	listEdge14.append(1369)
	listEdge14.append(1370)
	listEdge8.append(1387)
	listEdge8.append(1388)
	listEdge20.append(1403)
	listEdge14.append(1404)
	listEdge14.append(1405)
	listEdge14.append(1406)
	listEdge8.append(1423)
	listEdge8.append(1424)
	listEdge20.append(1439)
	listEdge14.append(1440)
	listEdge14.append(1441)
	listEdge8.append(1459)
	listEdge8.append(1460)
	listEdge8.append(1461)
	listEdge20.append(1474)
	listEdge20.append(1475)
	listEdge14.append(1476)
	listEdge14.append(1477)
	listEdge8.append(1495)
	listEdge8.append(1496)
	listEdge8.append(1497)
	listEdge4.append(1498)
	listEdge4.append(1499)
	listEdge4.append(1500)
	listEdge4.append(1501)
	listEdge4.append(1502)
	listEdge4.append(1503)
	listEdge4.append(1504)
	listEdge4.append(1505)
	listEdge4.append(1506)
	listEdge4.append(1507)
	listEdge4.append(1508)
	listEdge4.append(1509)
	listEdge20.append(1510)
	listEdge20.append(1511)
	listEdge14.append(1512)
	listEdge14.append(1513)
	listEdge8.append(1531)
	listEdge8.append(1532)
	listEdge8.append(1533)
	listEdge4.append(1534)
	listEdge4.append(1535)
	listEdge4.append(1536)
	listEdge4.append(1537)
	listEdge4.append(1538)
	listEdge4.append(1539)
	listEdge4.append(1540)
	listEdge4.append(1541)
	listEdge4.append(1542)
	listEdge4.append(1543)
	listEdge4.append(1544)
	listEdge4.append(1545)
	listEdge20.append(1546)
	listEdge20.append(1547)
	listEdge13.append(1548)
	listEdge13.append(1549)
	listEdge7.append(1567)
	listEdge7.append(1568)
	listEdge7.append(1569)
	listEdge4.append(1570)
	listEdge4.append(1571)
	listEdge4.append(1572)
	listEdge4.append(1573)
	listEdge4.append(1574)
	listEdge4.append(1575)
	listEdge4.append(1576)
	listEdge4.append(1577)
	listEdge4.append(1578)
	listEdge4.append(1579)
	listEdge4.append(1580)
	listEdge4.append(1581)
	listEdge19.append(1582)
	listEdge19.append(1583)
	listEdge13.append(1584)
	listEdge13.append(1585)
	listEdge7.append(1603)
	listEdge7.append(1604)
	listEdge7.append(1605)
	listEdge19.append(1618)
	listEdge19.append(1619)
	listEdge13.append(1620)
	listEdge13.append(1621)
	listEdge13.append(1622)
	listEdge7.append(1639)
	listEdge7.append(1640)
	listEdge19.append(1655)
	listEdge13.append(1656)
	listEdge13.append(1657)
	listEdge13.append(1658)
	listEdge7.append(1675)
	listEdge7.append(1676)
	listEdge19.append(1691)
	listEdge13.append(1692)
	listEdge13.append(1693)
	listEdge13.append(1694)
	listEdge7.append(1710)
	listEdge7.append(1711)
	listEdge7.append(1712)
	listEdge13.append(1728)
	listEdge13.append(1729)
	listEdge13.append(1730)
	listEdge7.append(1746)
	listEdge7.append(1747)
	listEdge7.append(1748)
	listEdge13.append(1764)
	listEdge13.append(1765)
	listEdge13.append(1766)
	listEdge13.append(1767)
	listEdge7.append(1781)
	listEdge7.append(1782)
	listEdge7.append(1783)
	listEdge13.append(1800)
	listEdge13.append(1801)
	listEdge13.append(1802)
	listEdge13.append(1803)
	listEdge1.append(1804)
	listEdge1.append(1805)
	listEdge1.append(1806)
	listEdge1.append(1807)
	listEdge1.append(1808)
	listEdge1.append(1809)
	listEdge1.append(1810)
	listEdge1.append(1811)
	listEdge1.append(1812)
	listEdge1.append(1813)
	listEdge1.append(1814)
	listEdge1.append(1815)
	listEdge7.append(1816)
	listEdge7.append(1817)
	listEdge7.append(1818)
	listEdge7.append(1819)
	listEdge13.append(1836)
	listEdge13.append(1837)
	listEdge13.append(1838)
	listEdge13.append(1839)
	listEdge1.append(1840)
	listEdge1.append(1841)
	listEdge1.append(1842)
	listEdge1.append(1843)
	listEdge1.append(1844)
	listEdge1.append(1845)
	listEdge1.append(1846)
	listEdge1.append(1847)
	listEdge1.append(1848)
	listEdge1.append(1849)
	listEdge1.append(1850)
	listEdge1.append(1851)
	listEdge7.append(1852)
	listEdge7.append(1853)
	listEdge7.append(1854)
	listEdge7.append(1855)
