#### To do list
#v1 - 6th September 2023 - Tested 18th Sept 3v3 Classical
#v2 - 

# Verify all player countes execpt 6 ### Do a much cleaner logic position start
# Matth - I forgot - An option distance 1 -2 -3 pour starts
# What makes cost so high


### by Penny for Beyond the Game - September 2023, BTG 2.36 ###

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
def getDescription():
	return "Beyond the Game map by Penny, inspired by the Scandinavian forest and the island of Gotland"	
def getDescriptionTitle():
	return "A very structured map which puts each player of the team vis-a-vis an opponent in one 'band' of land separate by snowy forests."
def getDescriptionTitleTwo():
	return ""	
def getDescriptionTitleTwo():
	return "There are also key bridges made of peaks for you to explore with early boats"
def getDescriptionMain():
	return "The map is very tall, so that you are invited to extend vertically, you'll have to decide if it's worth settling far away and play the water game or not. You'll have 4/5 tiles of snowy forest then 2 tiles of tundra before the seas"
def getDescriptionSecond():#Script tip : (on TOP)
	return "There are no extra boost on water resources, so if you're settling for extra cities in the tundra and forests regions for the deers, you don't have to defend the water tiles with boats, you can be defending more passively"	
def getDescriptionThird():#Option : (at the bottom)"
	return "Default is forcing Top versus Bottom"	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Teamer for eras without immediate Ocean access, Classi/Medi/Reny"	
def getDescriptionBalance():#Balance : (at the bottom)"
	return "BAN Forest-Agile UU's. INDIA strong since you're spawning near a lot of forest"	

'''0.1)     getNumHiddenCustomMapOptions() '''
def getNumHiddenCustomMapOptions():
	return 2

'''0.2 getNumCustomMapOptions()'''
def getNumCustomMapOptions():
	return 17

'''0.3)     getCustomMapOptionDefault()'''
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	3,
		2:  1,
		3:	1,
		4:	1,
		5:	1,
		6:	3,
		7:	1,
		8:	1,
		9:  0,
		10:	0,
		11:	2,
		12:	1,
		13:	0,
		14:	0,		
		15:	0,
		16:	0
		}
	return option_defaults[iOption]

'''0.4)     isAdvancedMap()'''

'''0.5)     getCustomMapOptionName()'''
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "BTG Tech Modifier",
		2:  "Map Size",
		3:	"Main Sea Island",
		4:	"Sea Junctions",
		5:	"Bay Area",
		6:	"BTG Lagoons",
		7:	"Deers",
		8:	"BTG Potatoes",
		9:	"Resource Madness",
		10:	"Forest Type",
		11:	"Player Starts",
		12:	"Team Starts",	
		13:	"BTG Free Unit",		
		14:	"Notes",
		15:	"BTG Spectators",
		16:  "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
'''0.6)     getNumCustomMapOptionValues()'''
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	11,
		2:  2,
		3:	3,
		4:	3,
		5:	2,
		6:	4,
		7:	2,
		8:	2,
		9:	3,
		10:  2,
		11:  3,
		12:	2,
		13: 4,			
		14:	1,
		15: 1,
		16: 1
		}
	return option_values[iOption]

'''0.7)     isRandomCustomMapOption()'''
def isRandomCustomMapOption(argsList):
	return False
	
'''0.8)     getCustomMapOptionDescAt()'''
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "0% - Default Value",
			1: "+10%",
			2: "+20%",
			3: "+30% - Suggested Scandinavia Value",
			4: "+40%",
			5: "+50%",
			6: "+60%",
			7: "+70%",
			8: "+80%",
			9: "+90%",			
			10: "+100%",			
			},				
		2:	{
			0: "Small - 40 Tiles Height, Width 12 Tiles by TeamPlayer & 8 Tiles of Sea ",		
			1: "Large - 48 Tiles Height, Width 14 Tiles by TeamPlayer & 12 Tiles of Sea ",		
			},
		3:	{
			0: "No",
			1: "Yes - Gotland (Sheeps [5/6], Copper/Whale/Pearls [2/3])",		
			2: "Yes - 1 Group of Peaks",
			},	
		4:	{
			0: "No - Just ocean",
			1: "Yes - Peaks",		
			2: "Yes - Peaks & Snow/Lava in other sea regions",	
			},	
		5:	{
			0: "No",
			1: "Yes - Lagoons",
			},				
		6:	{
			0: "No",
			1: "Yes - All Lagoons",
			2: "Yes - Lagoons on coast",
			3: "Yes - Balanced Lagoons and Deep sea"
			},				
		7:	{
			0: "No - Normal",
			1: "Yes - Numerous in Tundra and Forests",
			},				
		8:	{
			0: "No - Nothing on Horizontal middle",
			1: "Yes - Many Potatoes in middle",
			},
		9:	{
			0: "No - Normal Game",
			1: "Yes - Madness Resource in Middle/Potato Layer",
			2: "Yes - Madness Resource Everywhere",
			},				
		10:	{
			0: "Strategical Zones - Snowy Forests",
			1: "Strategical Zones - Palms (BTG)",
			},			
		11:	{
			0: "Far Away - Near the Snow Forest",
			1: "Close - Near the Potatoes",
			2: "Central - And Variable",
			},				
		12:	{
			0: "Normal Process by distance",
			1: "Top vs Bottom"
			},	
		13:	{
			0: "0 Lumberjack",
			1: "1 Lumberjack",
			2: "2 Lumberjacks",
			3: "3 Lumberjacks"
			},				
		14:	{
			0: "Balanced for Amber, Lead and Nickel",	
			},			
		15:	{
			0: "Compatible with 1 spectator in any slot or team",
			},
		16:	{
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

def beforeInitOptionsValue():#2.36 this is handy to find in code
	global iOptionValue_Wrap
	global iOptionValue_Size
	global iOptionValue_Island
	global iOptionValue_BayArea
	global iOptionValue_Junction
	global iOptionValue_Lagoon
	global iOptionValue_Deer
	global iOptionValue_Potatoes
	global iOptionValue_Madness
	global iOptionValue_Palms
	global iOptionValue_TopBottom
	global iOptionValue_Lumberjack
	global iOptionValue_PlayerStart
	global iOptionValue_TechModif#2.42a
	
	iOptionValue_Wrap = CyMap().getCustomMapOption(0)
	iOptionValue_TechModif = CyMap().getCustomMapOption(1)
	iOptionValue_Size = CyMap().getCustomMapOption(2)
	iOptionValue_Island = CyMap().getCustomMapOption(3)
	iOptionValue_Junction = CyMap().getCustomMapOption(4)
	iOptionValue_BayArea = CyMap().getCustomMapOption(5)
	iOptionValue_Lagoon = CyMap().getCustomMapOption(6)
	iOptionValue_Deer = CyMap().getCustomMapOption(7)
	iOptionValue_Potatoes = CyMap().getCustomMapOption(8)
	iOptionValue_Madness = CyMap().getCustomMapOption(9)
	iOptionValue_Palms = CyMap().getCustomMapOption(10)
	iOptionValue_PlayerStart = CyMap().getCustomMapOption(11)	
	iOptionValue_TopBottom = CyMap().getCustomMapOption(12)
	iOptionValue_Lumberjack = CyMap().getCustomMapOption(13)	
	

def beforeInit():#2.36 this is handy to find in code

	### Call Option Cleaner ##	
	beforeInitOptionsValue()

	## General BTG Initialization ##
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False		
	
	## Map Specific BTG defines ##
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	global iPairPlayers
	global iWidthWaterColumn
	global iWidthFullColumn
	global iWidthLastPlayerColumn
	global iWidthMap
	global iHeightMap
	global iGlobalLandPeakRatio
	global iGlobalLandHillRatio
	global iIslandRadius
	global xIslandCenter
	global yIslandCenter
	global centerXWaterPeak
	global iShiftXWaterPeak
	global iPeakRatioIsland
	global iPeakRatioIslandWaterMountain #2.42
	global iPeakRatioSideJunction
	global iPeakRatioMiddleJunction
	global iWaterBandWith
	global iTundraBandThickness
	global iHorizontalForestLayer
	global iVerticalForestThickness
	global minYForestColumn
	global maxYForestColumn
	global iForestRatioForestRegion
	global iProbaTundraDeer
	global iProbaForestDeer
	global iProbaPotatoMiddle
	global iPeakify
	global iBayAreaRay#2.42
	global iPeakRatioBayArea #2.42
	global lBorderBayPlotList #2.42
	global iBayAreaProbaFish
	global iBayAreaProbaPearl
	
	lBorderBayPlotList = []
	
	iPeakify = 13
		
	iPairPlayers = (iPlayers+1) / 2
	if (iOptionValue_Size == 0):
		iWidthWaterColumn = 8
		iWidthFullColumn = 12
		iVerticalForestThickness = 4
		iHeightMap = 40		
	elif (iOptionValue_Size == 1):
		iWidthWaterColumn = 12
		iWidthFullColumn = 14
		iVerticalForestThickness = 5
		iHeightMap = 48
	iWidthLastPlayerColumn = iWidthFullColumn - iVerticalForestThickness
	iWidthMap = iWidthWaterColumn + ((iPairPlayers-1) * iWidthFullColumn) + iWidthLastPlayerColumn
	if iWidthMap % 4 == 3:#it's like 63 for 8 players
		iWidthMap += 1
	
	iGlobalLandPeakRatio = 5
	iGlobalLandHillRatio = 30

	if (iOptionValue_Size == 0):	
		iIslandRadius = 3
	elif (iOptionValue_Size == 1):
		iIslandRadius = 4		
	xIslandCenter = iWidthWaterColumn / 2
	yIslandCenter = iHeightMap / 2
	centerXWaterPeak = ((iWidthMap - iWidthWaterColumn) / 2 + iWidthWaterColumn)
	iShiftXWaterPeak = 5#v2 from 3 to 5
	
	iBayAreaRay = (iWidthFullColumn/2) - 2
	
	iPeakRatioIsland = 33
	iPeakRatioIslandWaterMountain = 19
	iPeakRatioSideJunction = 25
	iPeakRatioMiddleJunction = 20
	iPeakRatioBayArea = 10
	iBayAreaProbaFish = 16
	iBayAreaProbaPearl = 3
	
	if (iOptionValue_Size == 0):	
		iWaterBandWith = 3
		iTundraBandThickness = 2
		iHorizontalForestLayer = 4
		iSpaceTransitTeam = 3
	elif (iOptionValue_Size == 1):	
		iWaterBandWith = 3
		iTundraBandThickness = 2
		iHorizontalForestLayer = 5
		iSpaceTransitTeam = 4
	minYForestColumn = iWaterBandWith + iTundraBandThickness + iHorizontalForestLayer + iSpaceTransitTeam
	maxYForestColumn = iHeightMap - minYForestColumn
	iForestRatioForestRegion = 80
	
	iProbaTundraDeer = 35
	iProbaForestDeer = 7
	iProbaPotatoMiddle = 30#v2 from 25 to 30
		
	## Map Specific BTG Bonuses ##
	global listBonusEliminateNatural
	global listToBalance
	listBonusEliminateNatural = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')
	if isBTPon:
		listBonusEliminateNatural += ('BONUS_SULPHUR','BONUS_AMBER')
		listToBalance = ["BONUS_LEAD","BONUS_NICKEL","BONUS_AMBER"]	
		if iOptionValue_Madness :
			listToBalance.append("BONUS_SULPHUR")
			iProbaPotatoMiddle = 10
	#2.43
	global listToBalance5
	global listToBalance4
	listToBalance5 = ('BONUS_ALUMINUM', 'BONUS_COAL', 'BONUS_HORSE', 'BONUS_OIL', 'BONUS_URANIUM')
	listToBalance4 = ('BONUS_COPPER', 'BONUS_IRON')

'''2)     - Initialize Map'''
'''2.2)     getGridSize()'''
def getGridSize(argsList):
	x = iWidthMap / 4
	y = iHeightMap / 4
	return (x, y)
		
'''2.3.1)   getTopLatitude()            # always use both'''
'''2.3.2)   getBottomLatitude()         # always use both'''

'''2.4.1)   getWrapX()                  # always use both'''
'''2.4.2)   getWrapY()                  # always use both'''
def getWrapX():
	map = CyMap()
	return (iOptionValue_Wrap == 1 or iOptionValue_Wrap == 2)
def getWrapY():
	map = CyMap()
	return (iOptionValue_Wrap == 2)

'''3)     beforeGeneration()	'''
def beforeGeneration():
	
	## General BTS Initialization ##
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()

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

'''4)     - Generate Map'''
'''4.1)     generatePlotTypes()'''
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = ScandinaviaFractalWorld()
	return fractal_world.generatePlotTypes()					
class ScandinaviaFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=False, grain_amount=3):
		
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
			
				bPeak = False
				bLand = True
				iProbaBeWater = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeWater")				
			
			
				i = y*self.iNumPlotsX + x
				
				### Block 1 - Left Sea ###
				if x == xIslandCenter and y == yIslandCenter:
					fDistance = 0
				else:
					fDistance = sqrt(((x - xIslandCenter) ** 2) + ((y - yIslandCenter) ** 2))	

				if fDistance <= iIslandRadius and iOptionValue_Island == 1:					
					bLand = True
				
				#v2 New Case
				elif (abs(x - xIslandCenter) <= iIslandRadius and abs(y - yIslandCenter) <= iIslandRadius) and iOptionValue_Island == 2:
					if iProbaBeWater <= iPeakRatioIsland:
						bPeak = True
					else:
						bLand = False
						
				#2.42 Some peaks to go help the island
				#elif (abs(xIslandCenter - abs(x))) <= iIslandRadius * 2 and (abs(yIslandCenter - abs(y))) <= iIslandRadius * 2 and iOptionValue_Island == 1:
				elif x <= iWidthWaterColumn and (abs(yIslandCenter - abs(y))) <= (iIslandRadius * 2) - 3 and iOptionValue_Island == 1:
					if iProbaBeWater <= iPeakRatioIslandWaterMountain:
						bPeak = True
					else:
						bLand = False						
						
				elif x <= iWidthWaterColumn :
					bLand = False



				

				###Block 2 - Top Bottom seas water band + in the middle 
				if y < iWaterBandWith or y >= iHeightMap - iWaterBandWith:
					bLand = False
					if x <= iWidthWaterColumn and iProbaBeWater <= iPeakRatioSideJunction and iOptionValue_Junction:
						bPeak = True
					if x <= centerXWaterPeak + iShiftXWaterPeak and x >= centerXWaterPeak - iShiftXWaterPeak and iProbaBeWater <= iPeakRatioMiddleJunction and iOptionValue_Junction:
						bPeak = True						
					

				### 2.42 the Bay Area logic ##
				if iOptionValue_BayArea:
					xCenterPlayerArea = (iWidthMap - iWidthWaterColumn)/2 + iWidthWaterColumn
					yThisCircle = iWaterBandWith
					if x == xCenterPlayerArea and y == yThisCircle:
						fDistance = 0
					else:
						fDistance = sqrt(((x - xCenterPlayerArea) ** 2) + ((y - yThisCircle) ** 2))	
					if fDistance <= iBayAreaRay:					
						if iProbaBeWater <= iPeakRatioBayArea and iOptionValue_Junction:
							bPeak = True
						else:
							bLand = False
						if fDistance >= iBayAreaRay -2 and y not in (-1,0,1):#-2 because the "0" border it's not each time, it's quite rare
							p = CyMap().plot(x,y)
							lBorderBayPlotList.append(p)
						
					
					yThisCircle = iHeightMap - iWaterBandWith
					if x == xCenterPlayerArea and y == yThisCircle:
						fDistance = 0
					else:
						fDistance = sqrt(((x - xCenterPlayerArea) ** 2) + ((y - yThisCircle) ** 2))	
					if fDistance <= iBayAreaRay:	
						if iProbaBeWater <= iPeakRatioBayArea and iOptionValue_Junction:
							bPeak = True
						else:
							bLand = False	
						if fDistance >= iBayAreaRay -2 and y not in (-1,0,1):#-2 because the "0" border it's not each time, it's quite rare
							p = CyMap().plot(x,y)
							lBorderBayPlotList.append(p)							
						
						
				######## Process this now ######
				if bPeak:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK
		
				elif bLand :
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba < iGlobalLandPeakRatio):
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
					elif (iProba < iGlobalLandHillRatio):
						self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else :
						self.plotTypes[i] = PlotTypes.PLOT_LAND
						
				else:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN			
				
						
		return self.plotTypes

'''4.2)     generateTerrainTypes()		'''
def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python BTG) ...")
	terrainTypes = BTGTerrainGenerator().generateTerrain()
	return terrainTypes	
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
		val = self.terrain.getHeight(iX, iY)
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		
		###### Layer Bottom Special design for this map #########
		bTundraZone = False
		if iY >= iWaterBandWith and iY < iWaterBandWith + iTundraBandThickness:
			bTundraZone = True
			
		elif iY < iHeightMap - iWaterBandWith and iY >= iHeightMap - iWaterBandWith - iTundraBandThickness:
			bTundraZone = True


		if bTundraZone:
			if iProba <= 50:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
			else:
				if isBTPon:
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_MARSH")
				else:
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
					
		##### Normal group - The "heart"
		else:	
			'''if iProba <= 0:#changed, don't want "normal desert"
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")		
			elif iProba <= 0:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
			elif iProba <= 0:#changed, don't want "normal marsh"
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_MARSH")
			elif iProba <= 50:'''
			
			if iProba <= 5:#2.38 Otherwise no oil	
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")	
			elif iProba <= 10:#2.38 Otherwise no aluminium
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")				
			elif iProba <= 50:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")				
			else:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_GRASS")


		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

'''4.3)     addRivers()'''
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

'''4.4)     addLakes()'''
'''4.5)     addFeatures()'''
def addFeatures():
	NiTextOut("Adding Features (Python Donut) ...")
	featuregen = ScandinaviaFeatureGenerator()
	#featuregen = FeatureGenerator()
	featuregen.__init__(iJunglePercent=0, iForestPercent=75,jungle_grain=5, forest_grain=6)#Copied on Grid 60 is normal forest, this is low amount
	featuregen.addFeatures()
	doForestLayers()#Scandinavia MapSpecial
	return 0
		
def doForestLayers():

	for x in range(iWidthWaterColumn,CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			
			bTransform = False
			bFullForest = False
			#1 Bottom Layers
			if y >= iWaterBandWith + iTundraBandThickness  and y < iWaterBandWith + iTundraBandThickness + iHorizontalForestLayer:
				bTransform = True
			if y < iHeightMap - iWaterBandWith - iTundraBandThickness  and y >= iHeightMap - iWaterBandWith - iTundraBandThickness - iHorizontalForestLayer:
				bTransform = True				
			
			#2 Side forest
			if y >= minYForestColumn and y < maxYForestColumn:
				for iRepeat in range(iPairPlayers):
					if x >= iWidthWaterColumn + iRepeat * iWidthFullColumn - iVerticalForestThickness and x < iWidthWaterColumn + iRepeat * iWidthFullColumn:
						bTransform = True
						bFullForest = True
			
			
			if bTransform:
				p = CyMap().plot(x,y)
				if not p.isImpassable() and not p.isWater():#not good looking on peaks	
					iProbaForest = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if iProbaForest <= iForestRatioForestRegion or bFullForest:
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
						if iOptionValue_Palms :
							p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_PALM_FOREST"), -1)#Snow variation
						else:
							p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation

class ScandinaviaFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		ice = 0	
	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		jungle = 0	
					
				
'''4.6)     addBonuses()	'''
def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
		
	if (type_string in listBonusEliminateNatural):
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

	def isValid(playerID, x, y): #Scandanivia Own writing 2023 v3
		gc = CyGlobalContext()
		map = CyMap()
		pPlot = map.plot(x, y)
		iPlayers = gc.getGame().countCivPlayersEverAlive()
				
		# Use global data set up via beforeGeneration().
		global shuffledPlayers
		playerTemplateAssignment = shuffledPlayers[playerID]


		## Part 1
		if iOptionValue_PlayerStart == 0:
			if playerTemplateAssignment % 2 == 0:
				iY = minYForestColumn
			elif playerTemplateAssignment % 2 == 1:
				iY = maxYForestColumn-1
			varY = 1
			varYFurther = 1
		elif iOptionValue_PlayerStart == 1:
			if playerTemplateAssignment % 2 == 0:
				iY = iHeightMap/2-1-5
			elif playerTemplateAssignment % 2 == 1:
				iY = iHeightMap/2+2+5	
			varY = 1
			varYFurther = 3
		elif iOptionValue_PlayerStart == 2:
			if playerTemplateAssignment % 2 == 0:
				iY_1 = minYForestColumn
				iY_2 = iHeightMap/2-1-5
				iY = (iY_1 + iY_2) / 2
			elif playerTemplateAssignment % 2 == 1:
				iY_1 = maxYForestColumn-1
				iY_2 = iHeightMap/2+2+5
				iY = (iY_1 + iY_2) / 2
			varY = 1
			varYFurther = 3

		## Part 2
		iX = (iWidthWaterColumn + iWidthLastPlayerColumn/2) + max(playerTemplateAssignment/2,0) * iWidthFullColumn
		varX = 2
		if max(playerTemplateAssignment/2,0) == 3:
			iX += 2
				 
		#2.43 Two cases now
		if playerTemplateAssignment % 2 == 0:#The bottom
			if x < iX - varX or x > iX + varX or y < iY - varYFurther or y > iY + varY:
				return False
			else:
				return True
				
		else:#The top
			if x < iX - varX or x > iX + varX or y < iY - varY or y > iY + varYFurther:
				return False
			else:
				return True				
				
				

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)#2.22 Simplified this part by calling common logic	

'''7)     - Normalize Starting-Plots'''
'''7.1)     normalizeStartingPlotLocations()+'''
def normalizeStartingPlotLocations():

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
		
		
	if iOptionValue_TopBottom:
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case		

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

	#balancer.normalizeAddExtras()#2.43 I don't want this, Iron need to be closer
	if not isBTPon:
		balancer.normalizeAddExtras()
	else:
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance5,5,0,100)
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance4,4,0,100)
	
	if isBTPon:
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
		
	if iOptionValue_Deer:
		doDeer()
		
	if iOptionValue_Madness:
		doMadness()
		
	if isBTPon and iOptionValue_Potatoes:
		doPotatoes()

	if iOptionValue_Island == 1:
		#Repeat of Resource depends on map Size (result of option)
		BTPResourceInBox(xIslandCenter-iIslandRadius,xIslandCenter+iIslandRadius,yIslandCenter-iIslandRadius,yIslandCenter+iIslandRadius,False,CyGlobalContext().getInfoTypeForString("BONUS_SHEEP"),5+iOptionValue_Size,0,-1)		
		BTPResourceInBox(xIslandCenter-iIslandRadius,xIslandCenter+iIslandRadius,yIslandCenter-iIslandRadius,yIslandCenter+iIslandRadius,False,CyGlobalContext().getInfoTypeForString("BONUS_COPPER"),2+iOptionValue_Size,0,-1)			
		
		#2.38 - Pearl is condition, adding Whale
		BTPResourceInBox(xIslandCenter-iIslandRadius,xIslandCenter+iIslandRadius,yIslandCenter-iIslandRadius,yIslandCenter+iIslandRadius,True,CyGlobalContext().getInfoTypeForString("BONUS_WHALE"),2+iOptionValue_Size,0,-1)			
		if isBTPon :
			BTPResourceInBox(xIslandCenter-iIslandRadius,xIslandCenter+iIslandRadius,yIslandCenter-iIslandRadius,yIslandCenter+iIslandRadius,True,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),2+iOptionValue_Size,0,-1)	

	if iOptionValue_Junction == 2:
		doPeakify()

	if isBTPon and iOptionValue_Lagoon:
		if iOptionValue_Lagoon == 1:
			CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,100,0,0,5)
		if iOptionValue_Lagoon == 2:
			CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,0,5)				
		if iOptionValue_Lagoon == 3:
			CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,100,5)	
			
	if iOptionValue_BayArea:#2.42
		doBayFishes()			
			
	
	return False #Don't want 18 forests starts on this map
	#CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

'''8 )    startHumansOnSameTile()'''
def startHumansOnSameTile():

	#Just the thing I call at the end #2.42e Push a special rate of tech
	if isBTPon:
		CyGlobalContext().getGame().setMapSpecialTechModifier(iOptionValue_TechModif * 10)

	CyPythonMgr().allowDefaultImpl()

''' 9) Map Depended local logic for Food and Bonus placement'''	

def doBayFishes():

	for iPlot in range(len(lBorderBayPlotList)):
		pPlotTest = lBorderBayPlotList[iPlot]
		if pPlotTest.isWater():
			#pPlotTest.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_COPPER"))
			
			iProbaResource = CyGlobalContext().getGame().getMapRandNum(100,"iProbaDeer")	
			if iProbaResource <= iBayAreaProbaPearl:
				pPlotTest.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"))
			elif iProbaResource <= iBayAreaProbaFish:
				#pPlotTest.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_FISH"))
				pPlotTest.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_CLAM"))

def doDeer():
	for x in range(iWidthMap):
		for y in range(iHeightMap):
		
			p = CyMap().plot(x,y)
			bScope = False
			
			#A - Tundra Enrich
			if y >= iWaterBandWith and y < iWaterBandWith + iTundraBandThickness:
				bScope = True
			
			elif y < iHeightMap - iWaterBandWith and y >= iHeightMap - iWaterBandWith - iTundraBandThickness:
				bScope = True
			
			
			if bScope and p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"):
				if p.getBonusType(-1) == -1 and not p.isImpassable() and not p.isWater():
					iProbaDeer = CyGlobalContext().getGame().getMapRandNum(100,"iProbaDeer")	
					if iProbaDeer <= iProbaTundraDeer:
						p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_DEER"))

			# Forest Part
			if y >= iWaterBandWith + iTundraBandThickness  and y < iWaterBandWith + iTundraBandThickness + iHorizontalForestLayer:
				bScope = True
			elif y < iHeightMap - iWaterBandWith - iTundraBandThickness  and y >= iHeightMap - iWaterBandWith - iTundraBandThickness - iHorizontalForestLayer:
				bScope = True	

			if bScope and p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"):
				if p.getBonusType(-1) == -1 and not p.isImpassable() and not p.isWater():
					iProbaDeer = CyGlobalContext().getGame().getMapRandNum(100,"iProbaDeer")	
					if iProbaDeer <= iProbaForestDeer:
						p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_DEER"))

def doPotatoes():
	for x in range(iWidthWaterColumn,iWidthMap,1):
		for y in range(iHeightMap/2-1,iHeightMap/2+2):
			p = CyMap().plot(x,y)
			if p.getBonusType(-1) == -1 and not p.isImpassable() and not p.isWater() and p.getFeatureType() == -1:
				iProbaPotato = CyGlobalContext().getGame().getMapRandNum(100,"iProbaPotato")	
				if iProbaPotato <= iProbaPotatoMiddle:
					p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_POTATO"))
								
def doPeakify():#2.38			
			
			
	pPlotOceanList = []
	for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				p = CyMap().plot(x,y)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_OCEAN")):
					#pPlotOceanList.append(p)
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if iProba <= iPeakify:				
						if isBTPon:
							#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK"), True, True)
							p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)
						else:
							p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
							p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)							
						
						
def doMadness():

	minX = iWidthWaterColumn ### if you choose Gotland, don't put even more Stuff there
	maxX = CyMap().getGridWidth()
	minY = 0
	maxY = CyMap().getGridHeight()
	if iOptionValue_Madness == 1:#In the potato zone
		minY = iHeightMap/2-5
		maxY = iHeightMap/2+6
		
	#Not here but in balancing by player : Sulphur		

	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),3,0,-1)
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),1,0,-1)
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_OLIVES"),1,0,-1)	
	
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),1,0,3)
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),1,0,3)

	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),1,0,3)	
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SUGAR"),1,0,3)	
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),1,0,3)	
	BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_INCENSE"),1,0,3)	

	BTPResourceInBox(minX,maxX,minY,maxY,True,CyGlobalContext().getInfoTypeForString("BONUS_WHALE"),6,0,-1)	

	if isBTPon:
	
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SALT"),1,0,4)
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_TEA"),1,0,4)
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_DIAMOND"),1,0,4)
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,4)
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,4)	
		BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,4)	

		BTPResourceInBox(minX,maxX,minY,maxY,True,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),6,0,-1)	
	
			
	
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

def BTPResourceInBox(LeftX,RightX,BottomY,TopY,isWater,iResourceType,iMinInstance,iFixInstance,iByPlayerInstance):#2.34

		random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))	
		
		plotsboundaries = []
		plotsboundariesSafe = []
		
		iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		if iByPlayerInstance != -1:
			iPlayerInstanceCount = iPlayers/iByPlayerInstance
		else:
			iPlayerInstanceCount = 0
		iTotalInstance = max(iMinInstance,iFixInstance+iPlayerInstanceCount)
		
		for iInstance in range(iTotalInstance):#2.35
		
			for x in range(CyMap().getGridWidth()):
				for y in range(CyMap().getGridHeight()):
					if (x <= RightX and x >= LeftX):
						if (y <= TopY and y >= BottomY):
							p = CyMap().plot(x,y)
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if not p.isImpassable() and p.getFeatureType() == -1:
									if p.isWater() == isWater :

										iBonusCount = 0
										for tx in range(3):
											for ty in range(3):
												testP = CyMap().plot(x+tx-1,y+ty-1)
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
						p.setBonusType(iResourceType)
						p.setFeatureType(-1, -1)
						break	
						
			else:
				random.shuffle(plotsboundaries)
				for p in plotsboundaries:
					if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
						p.setBonusType(iResourceType)
						p.setFeatureType(-1, -1)
						break		
					
''' 12 - BTG Dedicated Always call category'''	
def BTGFreeUnit():
	return CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	
def BTGFreeUnitCount():
	iCount = iOptionValue_Lumberjack	
	return iCount	
	
