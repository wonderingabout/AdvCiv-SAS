# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
# <!-- custom: Adapted from Beyond the Game mod map script, version 2.43. (GPT-5.3-Codex) -->



from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
from SAS_WorldSizes import *

import random #2.25



balancer = BonusBalancer()
isBTPon = False

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Modified BTG_Lagoon map from the Beyond the Game mod (by Penny). Adapted for AdvCiv-SAS: upscaled, non-AdvCiv options removed, and SAS48/high player counts supported."
	
def getDescriptionTitle():
	return "A map deisgned for two sides, as a top v bottom. There will be 1 player of each team in a very rich central donut"

def getDescriptionTitleTwo():
	return "other players will be on the side of the map and far apart, and will have to choose to come to the middle or not. Middle will be very difficult to reach on foot, easier by boat"

def getDescriptionMain():
	return "Center design keeps early conflict limited while preserving a reachable central objective on larger AdvCiv-SAS world sizes."

def getDescriptionSecond():#Script tip : (on TOP)
	return "The 'size factor' option has a huge impact, it determines if the donut in the center can be reach by a very thin 1 tile layer at the bottom, or if boats will be necessary "
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Perfect for 4v4, with favoring a 'non-bridge' configuration, so that the bottom and top players will have to decide to build galleys very quickly or not."	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "On 3v3 also good, will make more sense to leave a band of land in that case. Don't play other player counts"

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""	

def getNumCustomMapOptions():
	return 6

def getNumHiddenCustomMapOptions():
	return 0

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Size Factor",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"Types of Start",
		3:	"Center Resources",
		4:	"Start Position",
		5:	"TXT_KEY_MAP_WORLD_WRAP"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:  3,
		2:	2,
		3:	2,
		4:	3,
		5:	3
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "Normal - Island is separated",
			1: "1 Size small - Creates little bridges"
			},
		1:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "Balanced - Including Marble"
			},
		2:	{
			0: "1 Player by Team on Island",
			1: "All Outer land"
			},			
		3:	{
			0: "Normal Resources",
			1: "Extra Resources"
		},	
		4:	{
			0: "Normal",
			1: "Top v Bottom",
			2: "Anywhere"
			},				
		5:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:  2,
		2:	0,
		3:	1,
		4:	1,
		5:	0
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
		5:	false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(5) == 1 or map.getCustomMapOption(5) == 2)	
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(5) == 2)
	
def normalizeAddExtras():

	if (CyMap().getCustomMapOption(1) >= 1):
		balancer.normalizeAddExtras()
		

	if isBTPon:
		if (CyMap().getCustomMapOption(8) == 1):
			listToBalance = ["BONUS_LEAD"]
			balancer.BTPnormalizeAddExtrasSpecific(listToBalance,5,2,100)				
		
	#BTG
	# Moving from 4 to 8 because there are lots of tundras etc.
	BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),10,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
	BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),10,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		
	if (CyMap().getCustomMapOption(1) >= 2):	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,3,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),5,4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))				
						
	if isBTPon:
		if (CyMap().getCustomMapOption(3) >= 1):	
			doUUCenter()
		
	#End Map Specific		
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride


def doUUCenter():
	iExtraTile = 0
	
	#Center Unique	
	if isBTPon and CyMap().getCustomMapOption(8) == 1:
		BTPresourceFromCenter(2,3+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_AMBER"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		BTPresourceFromCenter(1,2+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	
	
	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SALT"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_TEA"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_OLIVES"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))


			
	BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_STONE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	
	BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_WHALE"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))

	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))			
	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))			
	BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
	
	
	#2.23 Ivory every two players rather than 3
	BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		

	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_WINE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SILK"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SUGAR"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
	BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_INCENSE"),CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))

	BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"))				
	BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_FUR"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"))						




def addBonusType(argsList):

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if isBTPon:
		if (CyMap().getCustomMapOption(8) == 1):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
			

	if (CyMap().getCustomMapOption(1) >= 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isAdvancedMap():
	"This map should not show up in simple mode"
	# <!-- custom: keep this at 0 so BTG_Lagoon appears in Play Now/simple mode map lists; return 1 hides it from simple mode. (GPT-5.3-Codex (summarized)) -->
	return 0

def isClimateMap():
	return 0

def isSeaLevelMap():
	return 0

def getGridSize(argsList):
	"Override Grid Size function to make the maps square."
	
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
		WorldSizeTypes.WORLDSIZE_TINY:		(7,7),
		WorldSizeTypes.WORLDSIZE_SMALL:		(8,8),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(9,9),
		WorldSizeTypes.WORLDSIZE_LARGE:		(10,10),
		WorldSizeTypes.WORLDSIZE_HUGE:		(11,11)		
	}			
		
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return sas_lookup_world_size_with_calibrated_sas(
		eWorldSize,
		grid_sizes,
		sas_huge_custom_max_players()
	)
	
	#return (10, 10) 

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
		
		
		#Default Value work well with Grid Size 10, 10, which is the value of large map, which is 4
		iShiftBias = 4
		iShift = iShiftBias - (int(CyMap().getWorldSize()))
		
		iRadius = int(self.map.getGridHeight() / 4)
		iHoleRadius = int(self.map.getGridHeight() / 4)
		iWidthSize = max(7 - (iShift),4) + (CyMap().getCustomMapOption(0)) #This option is worth 1 if bridge activated
		if int(CyMap().getWorldSize()) >= 2:#for Small and bigger
			iSmallWidthSize = max(5 - (iShift),4) + (CyMap().getCustomMapOption(0)) #This option is worth 1 if bridge activated
		if int(CyMap().getWorldSize()) < 2:#else
			iSmallWidthSize = max(5 - (iShift),3) + (CyMap().getCustomMapOption(0)) #This option is worth 1 if bridge activated
			
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
				if fDistance > iRadius:#outside
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				elif fDistance < iHoleRadius:#inside

					if fDistance == iHoleRadius - 1:#Specific Lagoon map, makes edge blurry and boatable
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")						
						if (iProba < 60):
							self.plotTypes[i] = PlotTypes.PLOT_LAND					
					elif fDistance == iHoleRadius - 2:#Specific Lagoon map, makes edge blurry and boatable
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")						
						if (iProba < 80):
							self.plotTypes[i] = PlotTypes.PLOT_LAND						
					else:#that's the normal one
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if (iProba < 18):
							self.plotTypes[i] = PlotTypes.PLOT_HILLS
						else :
							self.plotTypes[i] = PlotTypes.PLOT_LAND			

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
		
		
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x	
				
				#A - Extreme sides solid
				if x <= iSmallWidthSize or x >= self.map.getGridWidth() - iSmallWidthSize or y <= iSmallWidthSize or y >= self.map.getGridWidth() - iSmallWidthSize:
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba < 18):
						self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else :
						self.plotTypes[i] = PlotTypes.PLOT_LAND
				
				#B Next to that, less solid
				if x <= iWidthSize or x >= self.map.getGridWidth() - iWidthSize or y <= iWidthSize or y >= self.map.getGridWidth() - iWidthSize:
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba < 40):
						iSecondProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if (iSecondProba < 18):
							self.plotTypes[i] = PlotTypes.PLOT_HILLS
						else :
							self.plotTypes[i] = PlotTypes.PLOT_LAND
							
				#C make a bridge for the lagoon
				if (CyMap().getCustomMapOption(0) == 0): #This option is worth 1 if bridge activated
					if x >= iCenterX -1 and x <= iCenterX +1:				
						if ((y >= iWidthSize and y <= iWidthSize + 1) or (y >= self.map.getGridHeight() - iWidthSize - 1 and y <= self.map.getGridHeight() - iWidthSize)):
							iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
							if (iProba < 40):
								self.plotTypes[i] = PlotTypes.PLOT_HILLS
				if (CyMap().getCustomMapOption(0) == 1): #this is WITH the bridge, I want to make sure it's there
					if x >= iCenterX - 2 and x <= iCenterX +2:				
						if ((y >= iWidthSize -1 and y <= iWidthSize + 1) or (y >= self.map.getGridHeight() - iWidthSize - 1 and y <= self.map.getGridHeight() - iWidthSize + 1)):
							iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
							if (iProba < 95):
								self.plotTypes[i] = PlotTypes.PLOT_HILLS					
						
									
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
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			if (x == 0 or y == 0 or x == CyMap().getGridWidth()-1 or y == CyMap().getGridHeight()-1):
				if not (CyMap().getCustomMapOption(5) == 1 or CyMap().getCustomMapOption(5) == 2):#it's not nice when there is cylindrical wrap
					p = CyMap().plot(x,y)
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"), True, True)
			if (x >= CyMap().getGridWidth()/2 -3 and x <= CyMap().getGridWidth()/2 +2 and y >= CyMap().getGridHeight()/2 -1 and y <= CyMap().getGridHeight()/2):
				p = CyMap().plot(x,y)
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")							
				if (iProba < 75):
					if isBTPon:				
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)			
					else:
						p.setPlotType(PlotTypes.PLOT_PEAK,True,True)			
				else:
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)	
					
						
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
	
	global isBTPon
	# <!-- custom: BTG-only runtime hooks are disabled in AdvCiv-SAS; keep gameplay options in this script self-contained. (GPT-5.3-Codex) -->
	isBTPon = False	
				
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTemplateRoll = 0#Because only 1 template for each
	
	#2.23 - Debug because it crashes if too close
	
	if (CyMap().getCustomMapOption(2) == 0):#Normal with people inside
	
		fVar = 2
		
		templates = {(1,0): {0: [0.50, 0.50, 4, 4]},
					 (2,0): {0: [0.50, 0.10, fVar, fVar],
							 1: [0.50, 0.90, fVar, fVar]},
					 (3,0): {0: [0.50, 0.10, fVar, fVar],
							 1: [0.50, 0.30, fVar, fVar],
							 2: [0.50, 0.90, fVar, fVar]},
					 (4,0): {0: [0.50, 0.30, fVar, fVar],
							 1: [0.50, 0.70, fVar, fVar],
							 2: [0.50, 0.10, fVar, fVar],
							 3: [0.50, 0.90, fVar, fVar]},
					 (5,0): {0: [0.50, 0.30, fVar, fVar],
							 1: [0.50, 0.70, fVar, fVar],
							 2: [0.50, 0.10, fVar, fVar],
							 3: [0.50, 0.90, fVar, fVar],
							 4: [0.10, 0.25, fVar, fVar]},
					 (6,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.50, 0.30, fVar, fVar],
							 5: [0.50, 0.70, fVar, fVar]},	
					 (7,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.50, 0.30, fVar, fVar],
							 5: [0.50, 0.70, fVar, fVar],	
							 6: [0.50, 0.10, fVar, fVar]},	
					 (8,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.50, 0.30, fVar, fVar],
							 5: [0.50, 0.70, fVar, fVar],	
							 6: [0.50, 0.10, fVar, fVar],
							 7: [0.50, 0.90, fVar, fVar]},							 	
					 (9,0): {0: [0.33, 0.20, fVar, fVar],
							 1: [0.15, 0.35, fVar, fVar],
							 2: [0.50, 0.75, fVar, fVar],
							 3: [0.66, 0.20, fVar, fVar],
							 4: [0.85, 0.35, fVar, fVar],
							 5: [0.15, 0.65, fVar, fVar],
							 6: [0.85, 0.65, fVar, fVar],
							 7: [0.10, 0.10, fVar, fVar],
							 8: [0.90, 0.10, fVar, fVar]},	
					 (10,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.50, 0.30, fVar, fVar],
							 5: [0.50, 0.70, fVar, fVar],	
							 6: [0.30, 0.10, fVar, fVar],
							 7: [0.30, 0.90, fVar, fVar],	
							 8: [0.70, 0.10, fVar, fVar],
							 9: [0.70, 0.90, fVar, fVar]},							 
		}
		
	if (CyMap().getCustomMapOption(2) == 1):#Only outside
	
		fVar = 2
		
		templates = {(1,0): {0: [0.50, 0.50, 4, 4]},
					 (2,0): {0: [0.10, 0.10, fVar, fVar],
							 1: [0.10, 0.90, fVar, fVar]},
					 (3,0): {0: [0.10, 0.10, fVar, fVar],
							 1: [0.90, 0.10, fVar, fVar],
							 2: [0.10, 0.90, fVar, fVar]},
					 (4,0): {0: [0.10, 0.90, fVar, fVar],
							 1: [0.90, 0.10, fVar, fVar],
							 2: [0.10, 0.10, fVar, fVar],
							 3: [0.90, 0.90, fVar, fVar]},
					 (5,0): {0: [0.10, 0.90, fVar, fVar],
							 1: [0.90, 0.10, fVar, fVar],
							 2: [0.10, 0.10, fVar, fVar],
							 3: [0.90, 0.90, fVar, fVar],
							 4: [0.50, 0.50, fVar, fVar]},
					 (6,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.50, 0.10, fVar, fVar],
							 5: [0.50, 0.90, fVar, fVar]},	
					 (7,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.70, 0.10, fVar, fVar],
							 5: [0.70, 0.90, fVar, fVar],	
							 6: [0.30, 0.10, fVar, fVar],
							 7: [0.30, 0.90, fVar, fVar],	
							 8: [0.50, 0.50, fVar, fVar]},	
					 (8,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.70, 0.10, fVar, fVar],
							 5: [0.70, 0.90, fVar, fVar],	
							 6: [0.30, 0.10, fVar, fVar],
							 7: [0.30, 0.90, fVar, fVar]},							 	
					 (9,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.75, 0.10, fVar, fVar],
							 5: [0.75, 0.90, fVar, fVar],	
							 6: [0.25, 0.10, fVar, fVar],
							 7: [0.25, 0.90, fVar, fVar],		
							 8: [0.50, 0.50, fVar, fVar]},	
					 (10,0): {0: [0.10, 0.25, fVar, fVar],
							 1: [0.10, 0.75, fVar, fVar],
							 2: [0.90, 0.25, fVar, fVar],
							 3: [0.90, 0.75, fVar, fVar],
							 4: [0.75, 0.10, fVar, fVar],
							 5: [0.75, 0.90, fVar, fVar],	
							 6: [0.25, 0.10, fVar, fVar],
							 7: [0.25, 0.90, fVar, fVar],		
							 8: [0.50, 0.10, fVar, fVar],
							 9: [0.50, 0.90, fVar, fVar]},							 
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
		
	if (CyMap().getCustomMapOption(4) == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)	
	elif (CyMap().getCustomMapOption(4) == 2):
		return
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case	

def startHumansOnSameTile():
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	CyPythonMgr().allowDefaultImpl()


def BTGSong():
	return 0






			
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



def BTPresourceFromCenter(minFromCenter,maxFromCenter,iResourceType,iTerrainType):

	centerX = CyMap().getGridWidth()*50/100
	centerY = CyMap().getGridHeight()*50/100
	plotCenter = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*50/100)
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	
	plotsboundaries = []
	plotsboundariesSafe = []
	for dx in range(-maxFromCenter,maxFromCenter):
		for dy in range(-maxFromCenter,maxFromCenter):
			p = CyMap().plot(centerX+dx,centerY+dy)
			#if (((dx >= minFromCenter) or (dx <= -minFromCenter)) and ((dy >= minFromCenter) or (dy <=-minFromCenter))): 
			if ((abs(dx) >= minFromCenter) and (abs(dy) >= minFromCenter)):
				if (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
					
					#2.21
					iBonusCount = 0
					for tx in range(3):
						for ty in range(3):
							testP = CyMap().plot(centerX+dx+tx-1,centerY+dy+ty-1)
							if (testP.getBonusType(-1) != -1):
								iBonusCount += 1		
								
					if iBonusCount >= 1:
						plotsboundaries.append(p)
					else :
						plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
						
	
	if len(plotsboundariesSafe) > 0:
	
		random.shuffle(plotsboundariesSafe)	
		for p in plotsboundariesSafe:
			if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
				p.setTerrainType(iTerrainType,True,True)
				#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"),True,True)#for debug
				p.setBonusType(iResourceType)
				p.setFeatureType(-1, -1)
				break	
		
	else:
		random.shuffle(plotsboundaries)
		for p in plotsboundaries:
			if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
				p.setTerrainType(iTerrainType,True,True)
				p.setBonusType(iResourceType)
				p.setFeatureType(-1, -1)
				break	
