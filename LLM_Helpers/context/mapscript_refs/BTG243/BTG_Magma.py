### by Penny for Beyond the Game
## v2 - 2.36 - Make default Toroidal and work the ice

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
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return "This land map offers a land of regular shape so that the 2 teams are top versus bottom and players of the same team can link to each other but not that easily"

def getDescriptionTitleTwo():
	return "on a single strip of land on the back of their respective land, surrounded by water. Lot of capturable land is placed in the middle of the map"

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "The map plays completely differently if it is Toroidal and not just cylindrical"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Size of the player land is defined by option. The height is a single value and the map width is decided by the amount of players by team"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Any teamer with a focus on early (ancient, classical) starts. Game will be relatively short and violent, it will be hard to advance far in the tech path"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""	

def getNumCustomMapOptions():
	return 12

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "Height",
		2:	"Length",
		3:	"Water",
		4:	"BTG Forest Type",
		5:	"BTG Start Position",
		6:	"BTG Resources",
		7:  "Starting Units",
		8:	"BTG Music",
		9:	"Notes",
		10:	"BTG Spectator Notes",
		11: "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:  6,
		2:	3,
		3:	4,
		4:	2,
		5:	3,
		6:	2,
		7:	2,
		8:	3,
		9:	3,
		10:	2,
		11: 1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "Titled Axis",
			3: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "24 Tiles",
			1: "28 Tiles",
			2: "32 Tiles",
			3: "36 Tiles",
			4: "40 Tiles",
			5: "44 Tiles"
			},
		2:	{
			0: "8 Tiles by Player Pair",
			1: "12 Tiles by Player Pair",
			2: "16 Tiles by Player Pair"
			},			
		3:	{
			0: "Normal Coast and Ocean",
			1: "All Shallow Water",
			2: "All Magma/Ice in Lagoon",
			3: "Some Magma/Ice in Shallow Water"
			},	
		4:	{
			0: "Normal Forest",
			1: "Palm Forest always"		
			},				
		5:	{
			0: "Normal",
			1: "Top v Bottom",
			2: "Anywhere"
			},			
		6:	{
			0: "No",
			1: "Balanced Amber, Lead, Nickel"
			},				
		7:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},
		8:	{
			0: "Normal",
			1: "Age of Agriculture",
			2: "Age of Robotics"
			},					
		9:	{
			0: "Map Size has no impact, it's all on Height and Length",
			1: "Default size are 32 Tiles high and 12 Large by player",
			2: "If 12 tiles, land width will be 6-10 land and rest water"
			},			
		10:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"	
			},
		11:	{
			0: "Penny for Beyond The Game - Works for BTS, BTG Options have no effect"		
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	3,
		1:  3,
		2:	1,
		3:	3,
		4:	0,
		5:	1,
		6:	1,
		7:	0,
		8:	1,
		9:	0,
		10:	0,
		11:	0
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
		7:	false,
		8:	false,		
		9:	false,
		10:  false,
		11:  false	
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 3)	
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2 or map.getCustomMapOption(0) == 3)	
	
def normalizeAddExtras():

	#if (CyMap().getCustomMapOption(1) >= 1):
	#Always on for this map
	balancer.normalizeAddExtras()
		
	#BTG
	BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),10,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),10,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),6,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
	#End Map Specific

	if isBTPon and CyMap().getCustomMapOption(6) == 1:#2.38
		listToBalance = ["BONUS_LEAD","BONUS_NICKEL","BONUS_AMBER"]
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if isBTPon:
		#if CyMap().getCustomMapOption(6) == 0):
		#Actually place really nothing, I do all manual
		if type_string in balancer.newResourcesBTP or type_string in balancer.newStrategicBTP:
			return None	

	#if (CyMap().getCustomMapOption(1) >= 1):
	#Alwaus on this map
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
	
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	iPairPlayers = (iPlayers+1) / 2 #+1 because of the round down
	
	x = iPairPlayers * ( 2 + CyMap().getCustomMapOption(2))
	
	y = CyMap().getCustomMapOption(1) + 6
	
	return (x, y) 

def minStartingDistanceModifier():
	return -12

class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	#def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=3):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=False, grain_amount=3):#Magma - Important to put the shift at FALSE, otherwise go crazy
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)
		
		iCenterX = int(self.iNumPlotsX / 2)
		iCenterY = int(self.iNumPlotsY / 2)
		
		iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		iPairPlayers = (iPlayers+1) / 2 #+1 because of the round down	
		
				
		iWidthX = CyMap().getGridWidth()
		iHeightY = CyMap().getGridHeight()	
				
		iHalfWidthX = iWidthX / 2
		iQuarterBottomY = iHeightY / 4 - 1 # 1 shift for 0 start
		iQuarterTopY = iHeightY * 3 / 4
		iTopCentralY = iHeightY * 575 / 1000
		iBottomCentralY =  iHeightY * 425 / 1000
		
		for iPair in range(iPairPlayers):
			startX = iWidthX * (iPair) / iPairPlayers
			endX =  iWidthX * (iPair + 1) / iPairPlayers
			iHalfWidthX = (startX + endX) / 2
			for x in range(startX,endX,1):
				for y in range(self.iNumPlotsY):
					#i = y*self.iNumPlotsX + x	
					i = CyMap().plotNum(x,y) # Same Results

					#The mini bridge in the middle
					if y == iQuarterBottomY or y == iQuarterTopY:
							p = CyMap().plot(x,y)
							iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
							if (iProba < 18):
								self.plotTypes[i] = PlotTypes.PLOT_HILLS
							else :
								self.plotTypes[i] = PlotTypes.PLOT_LAND	
							if x > iHalfWidthX + 1:
								pPlotMarshBridge.append(p)
								
					elif y >= iBottomCentralY and y <= iTopCentralY:
							iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
							if (iProba < 3):
								self.plotTypes[i] = PlotTypes.PLOT_PEAK					
							elif (iProba < 18):
								self.plotTypes[i] = PlotTypes.PLOT_HILLS
							else :
								self.plotTypes[i] = PlotTypes.PLOT_LAND	
								
					else:
						#First the general columns
						if x <= iHalfWidthX:
							iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
							if (iProba < 3):
								self.plotTypes[i] = PlotTypes.PLOT_PEAK					
							elif (iProba < 18):
								self.plotTypes[i] = PlotTypes.PLOT_HILLS
							else :
								self.plotTypes[i] = PlotTypes.PLOT_LAND					
							if y <= 1 or y >= iHeightY - 2:#v2
								p = CyMap().plot(x,y)
								iProbaMountain = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
								if (iProbaMountain < 85):
									self.plotTypes[i] = PlotTypes.PLOT_HILLS
								pPlotIceGroup.append(p)												

						elif x == iHalfWidthX + 1 or x == iWidthX :
							iProbaFirst = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
							if iProbaFirst <= 50:
								iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
								if (iProba < 3):
									self.plotTypes[i] = PlotTypes.PLOT_PEAK					
								elif (iProba < 18):
									self.plotTypes[i] = PlotTypes.PLOT_HILLS
								else :
									self.plotTypes[i] = PlotTypes.PLOT_LAND	
								if y <= 1 or y >= iHeightY - 2:#v2
									p = CyMap().plot(x,y)
									iProbaMountain = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
									if (iProbaMountain < 85):
										self.plotTypes[i] = PlotTypes.PLOT_HILLS
									pPlotIceGroup.append(p)											

						elif x == iHalfWidthX + 2 or x == iWidthX - 1:
							iProbaFirst = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
							if iProbaFirst <= 20:
								iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
								if (iProba < 3):
									self.plotTypes[i] = PlotTypes.PLOT_PEAK					
								elif (iProba < 18):
									self.plotTypes[i] = PlotTypes.PLOT_HILLS
								else :
									self.plotTypes[i] = PlotTypes.PLOT_LAND	
								if y <= 1 or y >= iHeightY - 2:#v2
									p = CyMap().plot(x,y)
									iProbaMountain = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
									if (iProbaMountain < 85):
										self.plotTypes[i] = PlotTypes.PLOT_HILLS
									pPlotIceGroup.append(p)											
									
						else:
							self.plotTypes[i] = PlotTypes.PLOT_OCEAN						
							
	
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
		
		self.iRadius = int(self.map.getGridHeight() / 2)
		self.iHoleRadius = int(self.map.getGridHeight() / 2)
		
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
		if iProba <= 3:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")
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
		
def addRivers():#Lagoon 2.26 -- Adding this because it's direct after Generate plot and before the bonuses

	#Polish the Terrain Type
	for p in pPlotMarshBridge:
		if isBTPon:
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
		else:
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"), True, True)
		
	for p in pPlotIceGroup:
		p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)		

		iProbaForestMountain = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
		if (iProbaForestMountain < 75 and p.isHills()):
			p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation	
					
	#Need to finish by doing normal rivers
	CyPythonMgr().allowDefaultImpl()				

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
	
	global pPlotMarshBridge
	global pPlotIceGroup
	pPlotMarshBridge = []
	pPlotIceGroup = []	
	
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
				
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTemplateRoll = 0#Because only 1 template for each
		
	
	fVarX = 2
	#fVarY = 1 #2.38 this crashes all the time
	fVarY = 3
	
	templates = {(1,0): {0: [0.50, 0.50, 4, 4]},
				 (2,0): {0: [0.25, 0.25, fVarX, fVarY],
						 1: [0.25, 0.75, fVarX, fVarY]},
				 (3,0): {0: [0.125, 0.25, fVarX, fVarY],
						 1: [0.625, 0.75, fVarX, fVarY],
						 2: [0.625, 0.25, fVarX, fVarY]},
				 (4,0): {0: [0.125, 0.25, fVarX, fVarY],
						 1: [0.625, 0.75, fVarX, fVarY],
						 2: [0.625, 0.25, fVarX, fVarY],
						 3: [0.125, 0.75, fVarX, fVarY]},
				 (5,0): {0: [0.08, 0.25, fVarX, fVarY],
						 1: [0.08, 0.75, fVarX, fVarY],
						 2: [0.41, 0.25, fVarX, fVarY],
						 3: [0.41, 0.75, fVarX, fVarY],
						 4: [0.74, 0.25, fVarX, fVarY]},	
				 (6,0): {0: [0.08, 0.25, fVarX, fVarY],
						 1: [0.08, 0.75, fVarX, fVarY],
						 2: [0.41, 0.25, fVarX, fVarY],
						 3: [0.41, 0.75, fVarX, fVarY],
						 4: [0.74, 0.25, fVarX, fVarY],
						 5: [0.74, 0.75, fVarX, fVarY]},	
				 (7,0): {0: [0.06, 0.25, fVarX, fVarY],
						 1: [0.06, 0.75, fVarX, fVarY],
						 2: [0.31, 0.25, fVarX, fVarY],
						 3: [0.31, 0.75, fVarX, fVarY],
						 4: [0.56, 0.25, fVarX, fVarY],
						 5: [0.56, 0.75, fVarX, fVarY],	
						 6: [0.82, 0.25, fVarX, fVarY]},			
				 (8,0): {0: [0.06, 0.25, fVarX, fVarY],
						 1: [0.06, 0.75, fVarX, fVarY],
						 2: [0.31, 0.25, fVarX, fVarY],
						 3: [0.31, 0.75, fVarX, fVarY],
						 4: [0.56, 0.25, fVarX, fVarY],
						 5: [0.56, 0.75, fVarX, fVarY],	
						 6: [0.82, 0.25, fVarX, fVarY],
						 7: [0.82, 0.75, fVarX, fVarY]},							 	
				 (9,0): {0: [0.05, 0.25, fVarX, fVarY],
						 1: [0.05, 0.75, fVarX, fVarY],
						 2: [0.25, 0.25, fVarX, fVarY],
						 3: [0.25, 0.75, fVarX, fVarY],
						 4: [0.45, 0.25, fVarX, fVarY],
						 5: [0.45, 0.75, fVarX, fVarY],	
						 6: [0.65, 0.25, fVarX, fVarY],
						 7: [0.65, 0.75, fVarX, fVarY],	
						 8: [0.85, 0.25, fVarX, fVarY]},	
				 (10,0): {0: [0.05, 0.25, fVarX, fVarY],
						 1: [0.05, 0.75, fVarX, fVarY],
						 2: [0.25, 0.25, fVarX, fVarY],
						 3: [0.25, 0.75, fVarX, fVarY],
						 4: [0.45, 0.25, fVarX, fVarY],
						 5: [0.45, 0.75, fVarX, fVarY],	
						 6: [0.65, 0.25, fVarX, fVarY],
						 7: [0.65, 0.75, fVarX, fVarY],	
						 8: [0.85, 0.25, fVarX, fVarY],
						 9: [0.85, 0.75, fVarX, fVarY]},		 
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
		
	#2.38 Debut uneven mount -- Removing because it's even worse ?
	'''iCheck = iPlayers / 2
	if not (iCheck * 2 == iPlayers):
		CyPythonMgr().allowDefaultImpl()
		return			'''
		
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
		#2.26 Lagoon - This makes it crash !
		#if (pPlot.getArea() != map.findBiggestArea(False).getID()):
		#	return false

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
		
	if (CyMap().getCustomMapOption(5) == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)	
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
			


	if (CyMap().getCustomMapOption(3)  == 1):
		BTPDoMagma(True,False,0)	
	if (CyMap().getCustomMapOption(3)  == 2):
		BTPDoMagma(False,True,100)	
	if (CyMap().getCustomMapOption(3)  == 3):
		BTPDoMagma(True,True,25)		
		
	BTPDoMiddleMagma()#2.38 new
				
				
	if (CyMap().getCustomMapOption(7) == 1):
		return True	


def BTGSong():

	if (CyMap().getCustomMapOption(8) > 0):
		CyGame().setMapTriggerSound(CyMap().getCustomMapOption(8))
		return 1 # Has to be 1 to activate	
	else:
		return 0		
	
def BTPDoMiddleMagma():#2.38 new

	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()/2-2,CyMap().getGridHeight()/2+1):
			p = CyMap().plot(x,y)
			if p.getBonusType(-1) == -1 and p.getFeatureType() == -1 and not p.isImpassable() and not p.isWater():
				iProbaMiddleMagma = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
				if iProbaMiddleMagma <= 2:
					if isBTPon :
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)
					else:
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
						p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)	

				elif iProbaMiddleMagma <= 7:
					bHasNoBonusAround = True
					for dx in range (-1,2):
						for dy in range(-1,2):
							pTest = CyMap().plot(x + dx,y + dy)
							if pTest.getBonusType(-1) != -1:
								bHasNoBonusAround = False
					
					if bHasNoBonusAround == True:
						p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_DEER"))
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
						
	
def BTPDoMagma(bOceanShallow,bOceanMagama,iMagmaOdds):#2.25				
					
	pPlotOceanList = []
	pPlotCoastList = []
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)
			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_OCEAN")):
				pPlotOceanList.append(p)
			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")):
				pPlotCoastList.append(p)
	
	if isBTPon:
		for p in pPlotCoastList:
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAGOON"), True, True)						
	
	
	for p in pPlotOceanList:	
	
		if bOceanShallow:
			if isBTPon :
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAGOON"), True, True)			
			else:
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		

		if bOceanMagama:
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba <= iMagmaOdds:
				if isBTPon :
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)			
				else:
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
					p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)
			
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