### by Penny for Beyond the Game - June 2022, BTG 2.28 ###

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

def getDescription():
	return "Beyond the Game map by Penny, inspired by the Gulf of Mexico"
	
def getDescriptionTitle():
	return "A very structured map which puts the first players on a main land to the west of the map, and then the rest on 4 large islands to the east of the map. "

def getDescriptionTitleTwo():
	return "Everything is relatively symmetrical for top v bottom"

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "There are impassable peaks at very key locations, it should make it possible to navigate it all with galleys, and the central peaks are at key distances for galleons and transports"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Default is forcing Top versus Bottom, you can select an option to favor Islands starts as opposed to land"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Teamer 3v3 or 4v4 with access to water, Industrial Era start is the best"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Ban Mediterranean naval powers - SPAIN and OTTOMANS"	

def getNumCustomMapOptions():
	return 12

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "Map Size",
		2:	"Main Sea Center",
		3:	"Main Island Center",
		4:	"Junction Type",
		5:	"Flavor Starts",
		6:	"Team Starts",
		7:	"BTG Free Unit",
		8:  "BTG Amt Free Unit",			
		9:	"Notes",
		10:	"BTG Spectator Notes",
		11:  "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:  5,
		2:	1,
		3:	1,
		4:	1,
		5:	2,
		6:	2,
		7:	5,
		8:	4,		
		9:	3,
		10:	2,
		11:  1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "Flat",
			1: "Titled Axis"
			},
		1:	{
			0: "Very Small",
			1: "Small",
			2: "Normal",
			3: "Large",
			4: "Super Large",			
			},
		2:	{
			0: "Few Peaks"
			},	
		3:	{
			0: "Few Peaks"
			},	
		4:	{
			0: "Few Peaks"
			},				
		5:	{
			0: "Favor Land",
			1: "Favor Island"
			},				
		6:	{
			0: "Normal Process by distance",
			1: "Top vs Bottom 2 Teams"
			},	
		7:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			4: "Great Legend"
			},
		8:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},				
		9:	{
			0: "BTG Resources - Amber, Lead and Nickel",
			1: "Large is default size for any player count",
			2: "For an EVEN number of players up to 8"			
			},			
		10:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"
			},
		11:	{
			0: "Penny for Beyond the Game "
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:  3,
		2:	1,
		3:	1,
		4:	1,
		5:	0,
		6:	1,
		7:	3,
		8:	0,		
		9:	0,
		10:	1,
		11:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	True,
		2:	false,
		3:  false,
		4:	false,
		5:	true,
		6:	false,
		7:	false,
		8:	false,
		9:	false,
		10:	false,
		11: false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)	
	
def normalizeAddExtras():

	balancer.normalizeAddExtras()
		
	
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
					

	BTPForceEnrichFood(100,False,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),7,3,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	
	
	if isBTPon:
		#2.35
		listToBalance = ["BONUS_LEAD","BONUS_NICKEL","BONUS_AMBER"]
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)

	doSeaFoodIslands()
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride


def doSeaFoodIslands():
	
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))

	plotsIslandOneTop = []
	plotsIslandOneBot = []
	plotsIslandTwoTop = []
	plotsIslandTwoBot = []
	plotsIslandThreeTop = []
	plotsIslandThreeBot = []
	plotsIslandFourTop = []
	plotsIslandFourBot = []	
	
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			
			if x >= CyMap().getGridWidth() * 3 / 8 and x <= CyMap().getGridWidth() * 5 / 9:
				if y >= CyMap().getGridHeight() * 7 / 9:
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:
							plotsIslandOneTop.append(p)	
		
				elif y >= CyMap().getGridHeight() * 11 / 18 - 2 and y < CyMap().getGridHeight() * 11 / 18 :
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:
							plotsIslandOneBot.append(p)	
				
				elif y >= CyMap().getGridHeight() * 7 / 18 -1 and y <= CyMap().getGridHeight() * 7 / 18 +1 :
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandTwoTop.append(p)
				elif y <= CyMap().getGridHeight() * 2 / 9 + 1:
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandTwoBot.append(p)							

			if x >= CyMap().getGridWidth() * 2 / 3 and x <= CyMap().getGridWidth() * 8 / 9:
				if y >= CyMap().getGridHeight() * 7 / 9:
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandThreeTop.append(p)					
				elif y >= CyMap().getGridHeight() * 11 / 18 - 2 and y < CyMap().getGridHeight() * 11 / 18 :
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandThreeBot.append(p)	
				
				elif y >= CyMap().getGridHeight() * 7 / 18 -1 and y <= CyMap().getGridHeight() * 7 / 18 +1 :
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandFourTop.append(p)
				elif y <= CyMap().getGridHeight() * 2 / 9 + 1:
					p = CyMap().plot(x,y)
					if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"):
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(x+tx-1,y+ty-1)
								if (testP.getBonusType(-1) != -1):
									iBonusCount += 1					
						if iBonusCount == 0:						
							plotsIslandFourBot.append(p)	

	processFoodList(plotsIslandOneTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandOneBot,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandTwoTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandTwoBot,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandThreeBot,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandFourTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandFourBot,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)	
	
	processFoodList(plotsIslandOneTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandOneBot,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandTwoTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandTwoBot,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandThreeBot,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandFourTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandFourBot,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)		
	
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)	
	processFoodList(plotsIslandFourBot,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)	

def processFoodList(plots,iResourceType,iForceTerrain,iData):	
	
	random.shuffle(plots) 		
	for p in plots:
		if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
			if iForceTerrain > - 1:
				p.setTerrainType(iForceTerrain, True, True)			
			if iResourceType > - 1:
				p.setBonusType(iResourceType)
				p.setFeatureType(-1, -1)
			break

def addBonusType(argsList):

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')
	if isBTPon:
		BTPResourcesToBalance += ('BONUS_LEAD','BONUS_NICKEL','BONUS_AMBER')

	if (type_string in BTPResourcesToBalance):
		return None # don't place any of this bonus randomly	

		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isClimateMap():
	return 0

def isSeaLevelMap():
	return 0

def getGridSize(argsList):
	"Override Grid Size function to make the maps square."

	if (CyMap().getCustomMapOption(1) == 0):
		return (12, 6)		
	if (CyMap().getCustomMapOption(1) == 1):
		return (14, 7)
	if (CyMap().getCustomMapOption(1) == 2):
		return (16, 8)
	if (CyMap().getCustomMapOption(1) == 3):
		return (18, 9)
	if (CyMap().getCustomMapOption(1) == 4):
		return (20, 10)
		
class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=False, grain_amount=3):
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)
		
		
		iMainCircleCenterX = self.iNumPlotsX / 4
		iMainCircleCenterY = self.iNumPlotsY / 2
		iMainCircleHoleRadius = self.iNumPlotsX / 8
		iSmallCircleHoleRadius = self.iNumPlotsY / 9
				
		
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x

				
				# Carribean work Akira		
				
				################# Prep
				bLand = True
				bPeak = False
				iProbaBeWater = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeWater")
				
				# prep 2 - Define large circle
				if x == iMainCircleCenterX and y == iMainCircleCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iMainCircleCenterX) ** 2) + ((y - iMainCircleCenterY) ** 2))	
					
				# prep 3 - Define small circles
				if x == iMainCircleCenterX and y == 0:
					fSmallBottomDistance = 0
				else:
					fSmallBottomDistance = sqrt(((x - iMainCircleCenterX) ** 2) + ((y - 0) ** 2))
					
				if x == iMainCircleCenterX and y == self.iNumPlotsY:
					fSmallTopDistance = 0
				else:
					fSmallTopDistance = sqrt(((x - iMainCircleCenterX) ** 2) + ((y - self.iNumPlotsY) ** 2))					
					
				####### Define ###############
				
				#4 - Small peaks middle big circle
				if abs(x - iMainCircleCenterX) <= 2 and abs(y - iMainCircleCenterY) <= 2:
					if iProbaBeWater <= 70:
						bLand = False
					else:
						bPeak = True
				
				# 3 - Small circles
				elif fSmallBottomDistance <= iSmallCircleHoleRadius + 1 and x >= self.iNumPlotsX / 4:				
					bLand = True
				elif fSmallTopDistance <= iSmallCircleHoleRadius + 2 and x >= self.iNumPlotsX / 4:					
					bLand = True					
					
				#5 - Sets of main central Islands
				#5a
				elif x >= self.iNumPlotsX * 3 / 8 and x <= self.iNumPlotsX * 5 / 9 and y <= self.iNumPlotsY * 7 / 9 and y >= self.iNumPlotsY * 11 / 18:
					bLand = True
				
				elif x >= self.iNumPlotsX * 3 / 8 and x <= self.iNumPlotsX * 5 / 9 and y >= self.iNumPlotsY * 2 / 9 and y <= self.iNumPlotsY * 7 / 18:
					bLand = True

				elif x >= self.iNumPlotsX * 3 / 8 and x <= self.iNumPlotsX * 5 / 9 and y > self.iNumPlotsY * 7 / 18 and y < self.iNumPlotsY * 11 / 18:
					if iProbaBeWater <= 90:
						bLand = False
					else:
						bPeak = True

				#5b
				elif x >= self.iNumPlotsX * 2 / 3 and x <= self.iNumPlotsX * 8 / 9 and y <= self.iNumPlotsY * 7 / 9 and y >= self.iNumPlotsY * 11 / 18:
					bLand = True
				
				elif x >= self.iNumPlotsX * 2 / 3 and x <= self.iNumPlotsX * 8 / 9 and y >= self.iNumPlotsY * 2 / 9 and y <= self.iNumPlotsY * 7 / 18:
					bLand = True

				elif x >= self.iNumPlotsX * 2 / 3 and x <= self.iNumPlotsX * 8 / 9 and y > self.iNumPlotsY * 7 / 18 and y < self.iNumPlotsY * 11 / 18:
					if iProbaBeWater <= 90:
						bLand = False
					else:
						bPeak = True
						
				#5c small peaks in between the sets
				elif x >= self.iNumPlotsX * 5 / 9 and x <= self.iNumPlotsX * 2 / 3 and y >= self.iNumPlotsY * 2 / 9 and y <= self.iNumPlotsY * 7 / 9:
					if iProbaBeWater <= 90:
						bLand = False
					else:
						bPeak = True

				#6 "Transition plots"
				elif x >= iMainCircleCenterX + iSmallCircleHoleRadius / 2 and x <= iMainCircleCenterX + iSmallCircleHoleRadius * 3 / 2 + 1 and y >= iSmallCircleHoleRadius * 4 / 2 and y <= iSmallCircleHoleRadius * 5 / 2:
					if iProbaBeWater <= 75:
						bLand = False
					else:
						bPeak = True
						
				elif x >= iMainCircleCenterX + iSmallCircleHoleRadius / 2 and x <= iMainCircleCenterX + iSmallCircleHoleRadius * 3 / 2 + 1 and y <= self.iNumPlotsY - (iSmallCircleHoleRadius * 4 / 2) and y >= self.iNumPlotsY - (iSmallCircleHoleRadius * 5 / 2):
					if iProbaBeWater <= 75:
						bLand = False
					else:
						bPeak = True						
						
				# 1 - Remove water to the right
				elif x > self.iNumPlotsX / 4:
					bLand = False
				
				# 2 - Remove water main land "Mexico Gulf"
				elif fDistance <= iMainCircleHoleRadius + 1 and x <= self.iNumPlotsX / 4:					
					bLand = False
					
					
				
					
				######## Process this now ######
				if bPeak:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK
		
				elif bLand :
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba < 3):
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
					elif (iProba < 28):
						self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else :
						self.plotTypes[i] = PlotTypes.PLOT_LAND
						
				else:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN

		return self.plotTypes
		
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()

# subclass TerrainGenerator to create a lush grassland utopia.
class BTGTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
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

	def initFractals(self):
		self.terrain.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

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
			if val >= self.terrain.getHeightFromPercent(12):
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_GRASS")
			else:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python BTG) ...")
	terrainTypes = BTGTerrainGenerator().generateTerrain()
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
	
	if (CyMap().getCustomMapOption(5) == 0):
	
		templates = {(1,0): {0: [0.22, 0.15, fVar, fVar]},
					 (2,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar]},
					 (3,0): {0: [0.22, 0.25, fVar, fVar],
							 1: [0.22, 0.75, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar]},
					 (4,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar]},
					 (5,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar]},
					 (6,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar],
							 5: [0.10, 0.70, fVar, fVar]},	
					 (7,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar],
							 5: [0.10, 0.70, fVar, fVar],
							 6: [0.75, 0.30, fVar, fVar]},	
					 (8,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar],
							 5: [0.10, 0.70, fVar, fVar],
							 6: [0.75, 0.30, fVar, fVar],
							 7: [0.75, 0.70, fVar, fVar]},							 
		}
		
	else:#Option is == 1 and it's favor sea
	
		templates = {(1,0): {0: [0.22, 0.15, fVar, fVar]},
					 (2,0): {0: [0.45, 0.30, fVar, fVar],
							 1: [0.45, 0.70, fVar, fVar]},
					 (3,0): {0: [0.22, 0.25, fVar, fVar],
							 1: [0.22, 0.75, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar]},
					 (4,0): {0: [0.75, 0.30, fVar, fVar],
							 1: [0.75, 0.70, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar]},
					 (5,0): {0: [0.75, 0.30, fVar, fVar],
							 1: [0.75, 0.70, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.22, 0.15, fVar, fVar]},
					 (6,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.75, 0.30, fVar, fVar],
							 5: [0.75, 0.70, fVar, fVar]},	
					 (7,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar],
							 5: [0.10, 0.70, fVar, fVar],
							 6: [0.75, 0.30, fVar, fVar]},	
					 (8,0): {0: [0.22, 0.15, fVar, fVar],
							 1: [0.22, 0.85, fVar, fVar],
							 2: [0.45, 0.30, fVar, fVar],
							 3: [0.45, 0.70, fVar, fVar],
							 4: [0.10, 0.30, fVar, fVar],
							 5: [0.10, 0.70, fVar, fVar],
							 6: [0.75, 0.30, fVar, fVar],
							 7: [0.75, 0.70, fVar, fVar]},							 
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
		
		
	if (CyMap().getCustomMapOption(6) == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case		



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
				
    
    
def getRiverStartCardinalDirection(argsList):#BTG For this map
    pPlot = argsList[0]
    map = CyMap()
    
    if (pPlot.getX() > ((map.getGridHeight() * 2) / 3)):
        return CardinalDirectionTypes.CARDINALDIRECTION_WEST
    elif (pPlot.getY() < (map.getGridHeight() / 3)):
        return CardinalDirectionTypes.CARDINALDIRECTION_NORTH
    elif (pPlot.getY() < ((map.getGridHeight() * 2) / 3)):
        return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH  
    else:
        return CardinalDirectionTypes.CARDINALDIRECTION_EAST
	
	
	
	
		
def BTGFreeUnit():

	if (CyMap().getCustomMapOption(7) == 0):
		return -1
	elif (CyMap().getCustomMapOption(7) == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (CyMap().getCustomMapOption(7) == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (CyMap().getCustomMapOption(7) == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	elif (CyMap().getCustomMapOption(7) == 4):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_GREAT_LEGEND")				
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():

	iCount = CyMap().getCustomMapOption(8)	
		
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