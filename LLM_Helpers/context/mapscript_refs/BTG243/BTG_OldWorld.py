#	Penny 2022 for BT 2.28
#	It's basically Shuffle but with specific usage of Fractal World

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()

'''
This map script type added by popular demand.
The function is very similar to what "random" map type would provide in Civ3.

- Bob Thomas	October 30, 2005 // January 10, 2006
'''

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Old World - a fractal map"
	
def getDescriptionTitle():
	return "A fractal map, favors fragmented sinous continent, which sometimes require galleys to be reached"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return "The map offers a randomization for the X and Y wrap, and an option for randomizing the size as well, so that you really don't know where you are and the size of the map"

def getDescriptionSecond():#Script tip : (on TOP)
	return "Leave the ice and tundra option on 'removed' so that it doesn't help you figure out where you are on the map"
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Best suited for 'Old School mapmaking' or any type of game where you don't know the map and have to explore and discover (good for random team random era too for example)"

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""			
	
def isAdvancedMap():
	"This map should show up in simple mode"
	return 1

def getNumCustomMapOptions():
	return 11

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Wrap X",
		1:	"Wrap Y",
		2:  "Continent Grain",
		3:	"Water Percent",
		4:	"Ice & Tundra",
		5:	"Start Position",
		6:	"Map Size",
		7:	"Size Variation",
		8:	"Uniform land",
		9:	"Spectator Notes",
		10:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:	2,
		2:	5,
		3:	6,
		4:	2,
		5:	2,
		6:	3,
		7:	3,
		8:	2,
		9:	2,
		10:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "No - Titled Axis or Flat",
			1: "Yes - Toroidal or Cylindrical",
			},
		1:	{
			0: "No - Cylindrical or Flat",
			1: "Yes - Toroidal or Titled Axis",
			},			
		2:	{
			0: "1 Fractal - Very big blocks",
			1: "2 Fractals - Big blocks",
			2: "3 Fractals - Sinuous land",
			3: "4 Fractals - Small islands",		
			4: "5 Fractals - Archipelagos",		
			},
		3:	{
			0: "35% - Very filled",			
			1: "45% - Not Much water",
			2: "55% - Balance Amount",
			3: "60% - Target Water Amount",			
			4: "65% - More Water",
			5: "75% - Water map (default Shuffle)",
			},
		4:	{
			0: "Normal - Above 70 latitude",
			1: "Removed"
			},				
		5:	{
			0: "Normal - Teams are close",
			1: "Separated - All shuffled"
			},	
		6:	{
			0: "Smaller - 1 notch smaller",
			1: "Normal - Default BTS values",
			2: "Big - 1 notch larger",			
			},	
		7:	{
			0: "No Variation of Size",
			1: "Yes - Up to 1 notch both sides and direction",
			2: "Yes - Up to 2 notches both sides and direction",			
			},
		8:	{
			0: "No - Land depends of latitude",
			1: "Yes - Same type of land regardless of latitude"	
			},			
		9:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in FIRST slot"
			},	
		10:	{
			0: "Penny for Beyond The Game - Works for BTS, ideal for OldSchoolMode"		
			}				
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	-1,
		1:	-1,
		2:  2,
		3:	3,
		4:	1,
		5:	1,
		6:	1,
		7:	1,
		8:	1,
		9:  0,
		10:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	True,
		1:	True,
		2:  True,
		3:	True,
		4:	True,
		5:  False,
		6:	True,
		7:  True,
		8:	True,
		9:	False,
		10:	False
		}
	return option_random[iOption]

def getWrapX():
	return CyMap().getCustomMapOption(0)
	
def getWrapY():
	return CyMap().getCustomMapOption(1)
	
def beforeGeneration():#2.22
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
		
def getGridSize(argsList):

	dX = 0
	dY = 0
	if (CyMap().getCustomMapOption(7) > 0):
		dice = CyGlobalContext().getGame().getMapRand()
		if (CyMap().getCustomMapOption(7) ==  1):
			fractal_world = FractalWorld()
			diceX = dice.get(3, "0_1_2")
			dX = diceX - 1
			diceY = dice.get(3, "Repeat for Y")
			dY = diceY - 1
		if (CyMap().getCustomMapOption(7) ==  2):
			fractal_world = FractalWorld()
			diceX = dice.get(5, "0_1_2_3_4")
			dX = diceX - 2
			diceY = dice.get(5, "More values")
			dY = diceY - 2			
	
	if (CyMap().getCustomMapOption(6) == 0):#2.21z
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8 + dX,5 + dY),
			WorldSizeTypes.WORLDSIZE_TINY:		(12+ dX,7 + dY),
			WorldSizeTypes.WORLDSIZE_SMALL:		(15+ dX,9 + dY),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(18+ dX,12+ dY),
			WorldSizeTypes.WORLDSIZE_LARGE:		(24+ dX,15+ dY),
			WorldSizeTypes.WORLDSIZE_HUGE:		(30+ dX,18+ dY)
		}
		
	if (CyMap().getCustomMapOption(6) == 1):#Those are the Beyond the Sword default values
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(10+ dX,6 + dY),
			WorldSizeTypes.WORLDSIZE_TINY:		(13+ dX,8 + dY),
			WorldSizeTypes.WORLDSIZE_SMALL:		(16+ dX,10+ dY),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(21+ dX,13+ dY),
			WorldSizeTypes.WORLDSIZE_LARGE:		(26+ dX,16+ dY),
			WorldSizeTypes.WORLDSIZE_HUGE:		(32+ dX,20+ dY)
		}		
	
	if (CyMap().getCustomMapOption(6) == 2):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(11+ dX,7 + dY),
			WorldSizeTypes.WORLDSIZE_TINY:		(14+ dX,9 + dY),
			WorldSizeTypes.WORLDSIZE_SMALL:		(17+ dX,11+ dY),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(23+ dX,14+ dY),
			WorldSizeTypes.WORLDSIZE_LARGE:		(28+ dX,17+ dY),
			WorldSizeTypes.WORLDSIZE_HUGE:		(34+ dX,22+ dY)
		}	

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]		

def normalizeAddExtras():
	balancer.normalizeAddExtras()
	
	BTPCleanFeature(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"))	
	
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	
	if (CyMap().getCustomMapOption(4) == 1):
		doCleanIce()
	
	if (CyMap().getCustomMapOption(8) == 1):#Uniformized land removes jungle
		doCleanJungle()
	
	if isBTPon:
		if not CyGlobalContext().getGame().isOption(GameOptionTypes.GAMEOPTION_NEW_STRATEGIC_RESOURCE):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None	

	# 2.28 in all cases
	if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
		return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Shuffle) ...")
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	fractal_world = FractalWorld()
	
	iContinentGrain = (CyMap().getCustomMapOption(2) + 1)
	
	if (CyMap().getCustomMapOption(3) == 0):
		iWaterChosen = 35
	elif (CyMap().getCustomMapOption(3) == 1):		
		iWaterChosen = 45	
	elif (CyMap().getCustomMapOption(3) == 2):		
		iWaterChosen = 55	
	elif (CyMap().getCustomMapOption(3) == 3):		
		iWaterChosen = 60	
	elif (CyMap().getCustomMapOption(3) == 4):		
		iWaterChosen = 65
	elif (CyMap().getCustomMapOption(3) == 5):		
		iWaterChosen = 75
		
	#Rift is not nice, even with good setting it will just slice you cubes, not worth it
	'''if (CyMap().getCustomMapOption(8) == 0):
		bRift = False
	else:
		bRift = True'''
	
	fractal_world.initFractal(continent_grain = iContinentGrain, rift_grain = 0, has_center_rift = False, polar = True)
	return fractal_world.generatePlotTypes(water_percent=iWaterChosen)


def minStartingDistanceModifier():
	return 75
	
def normalizeStartingPlotLocations():

	if (CyMap().getCustomMapOption(5) == 0):
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case			


def addFeatures():
	NiTextOut("Adding Features (Python Shuffle) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0


def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Old World) ...")
	terraingen = OldWorldTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes
	
	
def BTPCleanFeature(iFeature):
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)	
			if p.getFeatureType() == iFeature:
				p.setFeatureType(-1, -1)	

class OldWorldTerrainGenerator:
	"If iDesertPercent=35, then about 35% of all land will be desert. Plains is similar. \
	Note that all percentages are approximate, as values have to be roughened to achieve a natural look."
	
	def __init__(self, iDesertPercent=32, iPlainsPercent=18,
	             fSnowLatitude=0.7, fTundraLatitude=0.6,
	             fGrassLatitude=0.1, fDesertBottomLatitude=0.2,
	             fDesertTopLatitude=0.5, fracXExp=-1,
	             fracYExp=-1, grain_amount=4):
		
		self.gc = CyGlobalContext()
		self.map = CyMap()

		grain_amount += self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()
		
		self.grain_amount = grain_amount

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()
		
		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
		if self.map.isWrapX(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_X
		if self.map.isWrapY(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_Y

		self.deserts=CyFractal()
		self.plains=CyFractal()
		self.variation=CyFractal()
		
		if (CyMap().getCustomMapOption(8) == 1): #Override terrain data to make it uniform
			iDesertPercent = 18
			iPlainsPercent = 32
			fGrassLatitude = 0.05
			fDesertBottomLatitude = 0.0
			fDesertTopLatitude = 1.0

		iDesertPercent += self.gc.getClimateInfo(self.map.getClimate()).getDesertPercentChange()
		iDesertPercent = min(iDesertPercent, 100)
		iDesertPercent = max(iDesertPercent, 0)

		self.iDesertPercent = iDesertPercent
		self.iPlainsPercent = iPlainsPercent

		self.iDesertTopPercent = 100
		self.iDesertBottomPercent = max(0,int(100-iDesertPercent))
		self.iPlainsTopPercent = 100
		self.iPlainsBottomPercent = max(0,int(100-iDesertPercent-iPlainsPercent))
		self.iMountainTopPercent = 75
		self.iMountainBottomPercent = 60

		fSnowLatitude += self.gc.getClimateInfo(self.map.getClimate()).getSnowLatitudeChange()
		fSnowLatitude = min(fSnowLatitude, 1.0)
		fSnowLatitude = max(fSnowLatitude, 0.0)
		self.fSnowLatitude = fSnowLatitude
		
		fTundraLatitude += self.gc.getClimateInfo(self.map.getClimate()).getTundraLatitudeChange()
		fTundraLatitude = min(fTundraLatitude, 1.0)
		fTundraLatitude = max(fTundraLatitude, 0.0)
		self.fTundraLatitude = fTundraLatitude
		
		if (CyMap().getCustomMapOption(4) == 1):#Option Remove Snow & Tundra
			self.fTundraLatitude = 1.0
			self.fSnowLatitude = 1.0

		fGrassLatitude += self.gc.getClimateInfo(self.map.getClimate()).getGrassLatitudeChange()
		fGrassLatitude = min(fGrassLatitude, 1.0)
		fGrassLatitude = max(fGrassLatitude, 0.0)
		self.fGrassLatitude = fGrassLatitude

		#2.28 - a bit less desert ## Rollback a bit unnateral and bland
		'''fDesertBottomLatitude=0.25 #0.2
		fDesertTopLatitude=0.45 #0.5'''		
		
		fDesertBottomLatitude += self.gc.getClimateInfo(self.map.getClimate()).getDesertBottomLatitudeChange()
		fDesertBottomLatitude = min(fDesertBottomLatitude, 1.0)
		fDesertBottomLatitude = max(fDesertBottomLatitude, 0.0)
		self.fDesertBottomLatitude = fDesertBottomLatitude

		fDesertTopLatitude += self.gc.getClimateInfo(self.map.getClimate()).getDesertTopLatitudeChange()
		fDesertTopLatitude = min(fDesertTopLatitude, 1.0)
		fDesertTopLatitude = max(fDesertTopLatitude, 0.0)
		self.fDesertTopLatitude = fDesertTopLatitude
		
		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()
		
	def initFractals(self):
		self.deserts.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iDesertTop = self.deserts.getHeightFromPercent(self.iDesertTopPercent)
		self.iDesertBottom = self.deserts.getHeightFromPercent(self.iDesertBottomPercent)

		self.plains.fracInit(self.iWidth, self.iHeight, self.grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iPlainsTop = self.plains.getHeightFromPercent(self.iPlainsTopPercent)
		self.iPlainsBottom = self.plains.getHeightFromPercent(self.iPlainsBottomPercent)

		self.variation.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
		self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
		self.terrainIce = self.gc.getInfoTypeForString("TERRAIN_SNOW")
		self.terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
		self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")

	def getLatitudeAtPlot(self, iX, iY):
		"""given a point (iX,iY) such that (0,0) is in the NW,
		returns a value between 0.0 (tropical) and 1.0 (polar).
		This function can be overridden to change the latitudes; for example,
		to make an entire map have temperate terrain, or to make terrain change from east to west
		instead of from north to south"""
		lat = abs((self.iHeight / 2) - iY)/float(self.iHeight/2) # 0.0 = equator, 1.0 = pole

		# Adjust latitude using self.variation fractal, to mix things up:
		lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)

		# Limit to the range [0, 1]:
		if lat < 0:
			lat = 0.0
		if lat > 1:
			lat = 1.0

		return lat

	def generateTerrain(self):		
		terrainData = [0]*(self.iWidth*self.iHeight)
		for x in range(self.iWidth):
			for y in range(self.iHeight):
				iI = y*self.iWidth + x
				terrain = self.generateTerrainAtPlot(x, y)
				terrainData[iI] = terrain
		return terrainData

	def generateTerrainAtPlot(self,iX,iY):
		lat = self.getLatitudeAtPlot(iX,iY)

		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		terrainVal = self.terrainGrass

		if lat >= self.fSnowLatitude:
			terrainVal = self.terrainIce
		elif lat >= self.fTundraLatitude:
			terrainVal = self.terrainTundra
		elif lat < self.fGrassLatitude:
			terrainVal = self.terrainGrass
		else:
			desertVal = self.deserts.getHeight(iX, iY)
			plainsVal = self.plains.getHeight(iX, iY)
			if ((desertVal >= self.iDesertBottom) and (desertVal <= self.iDesertTop) and (lat >= self.fDesertBottomLatitude) and (lat < self.fDesertTopLatitude)):
				terrainVal = self.terrainDesert
			elif ((plainsVal >= self.iPlainsBottom) and (plainsVal <= self.iPlainsTop)):
				terrainVal = self.terrainPlains

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal


def doCleanIce():	

	dice = CyGlobalContext().getGame().getMapRand()
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)
			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW")):
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"),True,True)
	

def doCleanJungle():	

	dice = CyGlobalContext().getGame().getMapRand()
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)
			if (p.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_JUNGLE")):
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
				if ((p.getBonusType(-1) != -1) or iProba >= 38):			
					#p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_PALM_FOREST"), -1)	
					p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), -1)	
				else:
					#p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FUJI"), 0)			
					p.setFeatureType(-1,-1)			


