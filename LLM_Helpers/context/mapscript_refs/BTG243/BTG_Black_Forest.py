#Penny May 2021 for Beyond the Game - based on Polar Circle

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
from CvMapGeneratorUtil import HintedWorld#2.23
import random

balancer = BonusBalancer()

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return "A map based on Donuts where the external, and internal parts are covered in forest. Only the middle layer of the donut is normal land"
	
def getDescriptionTitleTwo():
	return ""	

def getDescriptionMain():
	return "There are so many forest on this map, you're offered the possibility to start with a single lumberjack extra"

def getDescriptionSecond():#Script tip : (on TOP)
	return "Creating double forest units is key, so getting a religion with theocracy, or aiming for Elite barracks is a strategy of choice"
	
def getDescriptionThird():#Option : (at the bottom)"
	return "You can choose if the outer ring and inner ring have just forest or also resource mixed up"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Made for 4v4 ideally, 3v3 good. Classical start favored. Teamers are played top versus bottom"

def getDescriptionBalance():#Balance : (at the bottom)"
	return "SPIRITUAL in 2 turns forest-chop is strong. Should ban AZTEC, ZULU, MONGOL, POLAND, INDIA"	

def getNumCustomMapOptions():
	return 12

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"BTG Free Unit",
		1:  "BTG Amt Free Unit",
		2:	"TXT_KEY_MAP_WORLD_WRAP",
		3:  "TXT_KEY_CONCEPT_RESOURCES",
		4:	"Resources in Forest",
		5:	"BTG Resources",	
		6:	"Start Position",
		7:	"Size 1 notch smaller",
		8:	"BTG Music",
		9:	"Notes",
		10:	"BTG Spectator Note",
		11: "Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:  4,
		2:	3,
		3:  3,
		4:	3,
		5:	2,
		6:	2,
		7:	3,
		8:	1,
		9:	1,
		10:	1,
		11:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			},
		1:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},			
		2:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID",
			},
		3:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "Balanced - Increased Food",			
			},
		4:	{
			0: "No",
			1: "Middle Only",
			2: "Everywhere",
			},
		5:	{
			0: "No",
			1: "Yes - Balanced for Lead and Amber, Normal for others"
			},	
		6:	{
			0: "Normal",
			1: "Top v Bottom",
			},
		7:	{
			0: "No",
			1: "Yes",
			2: "Yes - 2 notches",
			},
		8:	{
			0: "Age of Black Forest",
			},				
		9:	{
			0: "Up to 10 players",
			},			
		10:	{
			0: "Solo or Team - 1 Spectator good in any slot"
			},
		11:	{
			0: "Penny for BTG - Works for BTS, BTG Options have no effect",	
			}				
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:  1,
		2:	0,
		3:  2,
		4:	1,
		5:	1,
		6:	1,
		7:	0,
		8:	0,
		9:	0,
		10:	0,
		11:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	False,
		1:	False,
		2:	False,
		3:  False,
		4:	True,
		5:	True,
		6:	False,
		7:	True,
		8:	False,
		9:	False,
		10: False,
		11:	False
		}
	return option_random[iOption]

def getWrapX(): return (iOptionValue_Wrap == 1 or iOptionValue_Wrap == 2)
	
def getWrapY():	return (iOptionValue_Wrap == 2)
	
def getTopLatitude():
	return 30 #No Snow on forest, except when I want it
	
def getBottomLatitude():	
	return -30 #No Snow on forest, except when I want it
	
	
def beforeInit():

	beforeInitOptionsValue()
	
	global isBTPon
	global iBrown	
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
	except:
		isBTPon = False	
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")	
		

	iForceJunglePercent = 5

def beforeInitOptionsValue():#2.36 this is handy to find in code

	global iOptionValue_StartingUnit
	global iOptionValue_StartingUnitCount
	global iOptionValue_Wrap
	global iOptionValue_Resource
	global iOptionValue_ResourceInForest
	global iOptionValue_ResourceBTG
	global iOptionValue_TopBottom
	global iOptionValue_Size
	

	iOptionValue_StartingUnit = CyMap().getCustomMapOption(0)
	iOptionValue_StartingUnitCount = CyMap().getCustomMapOption(1)
	iOptionValue_Wrap = CyMap().getCustomMapOption(2)
	iOptionValue_Resource = CyMap().getCustomMapOption(3)	
	iOptionValue_ResourceInForest = CyMap().getCustomMapOption(4)
	iOptionValue_ResourceBTG = CyMap().getCustomMapOption(5)
	iOptionValue_TopBottom = CyMap().getCustomMapOption(6)
	iOptionValue_Size = CyMap().getCustomMapOption(7)
	
	
	
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


	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
	#2.23 - Debug because it crashes if too close
	fVar = 2
	
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
				#(6,0): {0: [0.25, 0.33, fVar, fVar],
				#		 1: [0.75, 0.33, fVar, fVar],
				#		 2: [0.50, 0.20, fVar, fVar],
				#		 3: [0.25, 0.67, fVar, fVar],
				#		 4: [0.75, 0.67, fVar, fVar],
				#		 5: [0.50, 0.80, fVar, fVar]},		
				 (6,0): {0: [0.30, 0.30, fVar, fVar],
						 1: [0.70, 0.30, fVar, fVar],
						 2: [0.50, 0.20, fVar, fVar],
						 3: [0.30, 0.70, fVar, fVar],
						 4: [0.70, 0.70, fVar, fVar],
						 5: [0.50, 0.80, fVar, fVar]},								 
				 (7,0): {0: [0.25, 0.33, fVar, fVar],
						 1: [0.75, 0.33, fVar, fVar],
						 2: [0.40, 0.22, fVar, fVar],
						 3: [0.25, 0.67, fVar, fVar],
						 4: [0.75, 0.67, fVar, fVar],
						 5: [0.40, 0.78, fVar, fVar],	
						 6: [0.60, 0.22, fVar, fVar]},	
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
			
				
		
	return None	
	
def minStartingDistanceModifier():
	#return -12 #Original value
	return 30#BTP	


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
	
def normalizeAddExtras():

	doDarkForestHole()#we do it now because we erase the resource but we cannot erase copper, oil etc.	

	if (iOptionValue_Resource >= 1):
		balancer.normalizeAddExtras()
		
	#2.18

	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),4,False,iBrown)
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),4,True,iBrown)
	
	if (iOptionValue_Resource >= 2):	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),5,3,False,iBrown)	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,iBrown)
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,3,False,iBrown)			
	#end
	if isBTPon:
		if (iOptionValue_ResourceBTG == 1):#2.35
			listToBalance = ["BONUS_LEAD","BONUS_AMBER"]
			balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
		
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride


def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
		
	#2.21y
	if isBTPon :
		if (iOptionValue_ResourceBTG == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None

	if (iOptionValue_Resource >= 1):
		#if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
		if (type_string in balancer.resourcesToBalance):#BTP Because marble is broken
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

	if (iOptionValue_Size == 0):#2.22
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8,8),
			WorldSizeTypes.WORLDSIZE_TINY:		(9,9),
			WorldSizeTypes.WORLDSIZE_SMALL:		(10,10),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(12,12),
			WorldSizeTypes.WORLDSIZE_LARGE:		(14,14),
			WorldSizeTypes.WORLDSIZE_HUGE:		(16,16)
		}
		
	if (iOptionValue_Size == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,7),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
			WorldSizeTypes.WORLDSIZE_SMALL:		(9,9),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(11,11),
			WorldSizeTypes.WORLDSIZE_LARGE:		(13,13),
			WorldSizeTypes.WORLDSIZE_HUGE:		(15,15)
		}	
	
	if (iOptionValue_Size == 2):
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

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
				if fDistance > iRadius:#outside
					self.plotTypes[i] = PlotTypes.PLOT_LAND#2.23 - no Hills
				elif fDistance < iHoleRadius:#inside
					self.plotTypes[i] = PlotTypes.PLOT_LAND#2.23 - no Hills

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


		if shift_plot_types:
			self.shiftPlotTypes()

		return self.plotTypes
	
	
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()	

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
			terrainVal = self.terrainGrass#2.23

		else:
			val = self.terrain.getHeight(iX, iY)

			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
			if iProba <= 2:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
			elif iProba <= 5:
				terrainVal = iBrown#2.38
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

def normalizeStartingPlotLocations():

	if (iOptionValue_TopBottom == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()
		
	
def BTGSong():

	CyGame().setMapTriggerSound(1) # 1 is Black Forest Song

	return 1 # Has to be 1 to activate


def BTGFreeUnit():

	if (iOptionValue_StartingUnit == 0):
		return -1
	elif (iOptionValue_StartingUnit == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (iOptionValue_StartingUnit == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (iOptionValue_StartingUnit == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():	return iOptionValue_StartingUnitCount	


def doDarkForestHole():
	iCenterX = int(CyMap().getGridWidth() / 2)
	iCenterY = int(CyMap().getGridHeight() / 2)
	iRadius = min((iCenterX - 4), (iCenterY - 4))
	iHoleRadius = int(iRadius / 2)

	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			if x == iCenterX and y == iCenterY:
				fDistance = 0
			else:
				fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
			
			if fDistance < iHoleRadius:#Inside
				p = CyMap().plot(x,y)
				if iOptionValue_ResourceInForest == 0:
					p.setBonusType(-1)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
				
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
				if iProba <= 9 and p.getBonusType(-1) == BonusTypes.NO_BONUS:
					p.setPlotType(PlotTypes.PLOT_PEAK,True,True)	
					p.setFeatureType(-1, -1)					
				else:
					p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation				

			elif fDistance > iRadius:#Outside
				p = CyMap().plot(x,y)
				if iOptionValue_ResourceInForest <> 2:
					p.setBonusType(-1)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
				
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
				if iProba <= 9 and p.getBonusType(-1) == BonusTypes.NO_BONUS:
					p.setPlotType(PlotTypes.PLOT_PEAK,True,True)
					p.setFeatureType(-1, -1)						
				else:
					p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation'''
			
			elif y == iCenterY:#a line of forest in between players	
				p = CyMap().plot(x,y)
				if not p.isImpassable():#not good looking on peaks				
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
					p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation
					
					
					
					
					
					
					
					
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