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
		2:	"TBD",
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
	'''if isBTPon and (CyMap().getCustomMapOption(1) == 3):'''
	
		
	#End Map Specific		
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):

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
