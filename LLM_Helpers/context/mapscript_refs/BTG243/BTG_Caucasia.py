### by Penny for Beyond the Game - September 2023, BTG 2.36 ###
# V3 - Nov 2023 - Option to remove when lots of desert
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
	return "Beyond the Game map by Penny, inspired by the Caucasus"	
def getDescriptionTitle():
	return "A very structured map which puts the first players on a main band of land facing each other and the next two players of the team on the main sea"
def getDescriptionTitleTwo():
	return "Player 4 and 5 of a team will be spawned less centrally (in the grassland part of map)"
def getDescriptionMain():
	return "The map is purposefully very tall, so that you are invited to extend vertically, you'll have to decide if it's worth travalling to locations of extreme latitude to settle cities"
def getDescriptionSecond():#Script tip : (on TOP)
	return "Be mindful to the likely two 'bridges' that are created at 0 / 90 latitude which allows you to cross the land as a titled axis"	
def getDescriptionThird():#Option : (at the bottom)"
	return "Default is forcing Top versus Bottom"	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Teamer 3v3 or 4v4 with access to water, Industrial Era start is the best"	
def getDescriptionBalance():#Balance : (at the bottom)"
	return "AGRICULTURAL strong since you're spawning near a lot of desert"	

'''0.1)     getNumHiddenCustomMapOptions() '''
def getNumHiddenCustomMapOptions():
	return 2

'''0.2 getNumCustomMapOptions()'''
def getNumCustomMapOptions():
	return 12

'''0.3)     getCustomMapOptionDefault()'''
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:  0,
		2:	0,
		3:	0,
		4:	1,
		5:	0,
		6:	1,
		7:	0,
		8:	0,
		9:	0,
		10:	0,		
		11:	0
		}
	return option_defaults[iOption]

'''0.4)     isAdvancedMap()'''

'''0.5)     getCustomMapOptionName()'''
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "Map Size",
		2:	"Seas",
		3:	"Sea Center",
		4:	"Resources",
		5:	"Starts",
		6:	"Team Starts",	
		7:	"BTG Free Unit",
		8:  "BTG Amt Free Unit",			
		9:	"Notes",
		10:	"Spectator Notes",
		11:  "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
'''0.6)     getNumCustomMapOptionValues()'''
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:  1,
		2:	1,
		3:	1,
		4:	2,
		5:	1,
		6:	2,
		7:	5,
		8:  4,			
		9:	2,
		10:	2,
		11: 1
		}
	return option_values[iOption]

'''0.7)     isRandomCustomMapOption()'''
def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	False,
		1:	False,
		2:	False,
		3:  False,
		4:	False,
		5:	False,
		6:	False,
		7:	False,
		8:	False,
		9:	False,
		10:	False,
		11:	False		
		}
	return option_random[iOption]
	
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
			0: "Fixed in all cases",		
			},
		2:	{
			0: "One Sea",
			},	
		3:	{
			0: "Peak"
			},	
		4:	{
			0: "Tactical for Caucasia",
			1: "Tactical for Causasia - Extra Plains/Marsh instead of flat Desert",
			},				
		5:	{
			0: "Defined Centrally",
			},				
		6:	{
			0: "Normal Process by distance",
			1: "Top vs Bottom"
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
			0: "Balanced for Amber, Lead and Nickel",	
			1: "Map size is always 28x48 tiles",	
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

'''0.9)     - Get Map-Types'''
'''0.9.1)     isClimateMap()'''
def isClimateMap(): return False

'''0.9.2)     isSeaLevelMap()'''
def isSeaLevelMap(): return False

'''1)     beforeInit()'''
def beforeInit():#2.36 this is handy to find in code

	## General BTG Initialization ##
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False		
	## Map Specific BTG defines ##


'''2)     - Initialize Map'''
'''2.2)     getGridSize()'''
def getGridSize(argsList):

	if (CyMap().getCustomMapOption(1) == 0):
		return (7, 12)	
		
'''2.3.1)   getTopLatitude()            # always use both'''
'''2.3.2)   getBottomLatitude()         # always use both'''

'''2.4.1)   getWrapX()                  # always use both'''
'''2.4.2)   getWrapY()                  # always use both'''
def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)

'''3)     beforeGeneration()	'''
def beforeGeneration():
	
	## General BTS Initialization ##
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()
		
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTemplateRoll = 0#Because only 1 template for each	
	fVar = 2
	
	#2.33
	TopTeam = dice.get(2, "Shuffling Template IDs - Inland Sea PYTHON")
	if TopTeam == 1:
		XTopTeam = 0.990
	else:
		XTopTeam = 0.000
	BottomTeam = dice.get(2, "Shuffling Template IDs - Inland Sea PYTHON")
	if BottomTeam == 1:
		XBottomTeam = 0.990
	else:
		XBottomTeam = 0.000	
	
	templates = {(1,0): {0: [0.000, 0.375, fVar, fVar]},
				 (2,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar]},
				 (3,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.500, 0.325, fVar, fVar]},
				 (4,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.500, 0.325, fVar, fVar],
						 3: [0.500, 0.675, fVar, fVar]},
				 (5,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],},
				 (6,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],
						 5: [0.666, 0.675, fVar, fVar]},
				 (7,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],
						 5: [0.666, 0.675, fVar, fVar],
						 6: [0.000, 0.200, fVar, fVar]},	
				 (8,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],
						 5: [0.666, 0.675, fVar, fVar],
						 6: [0.000, 0.200, fVar, fVar],
						 7: [0.000, 0.800, fVar, fVar]},
				 (9,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],
						 5: [0.666, 0.675, fVar, fVar],
						 6: [0.250, 0.200, fVar, fVar],
						 7: [0.250, 0.800, fVar, fVar],
						 8: [0.750, 0.200, fVar, fVar]},
				 (10,0): {0: [XBottomTeam, 0.375, fVar, fVar],
						 1: [XTopTeam, 0.625, fVar, fVar],
						 2: [0.333, 0.325, fVar, fVar],
						 3: [0.333, 0.675, fVar, fVar],
						 4: [0.666, 0.325, fVar, fVar],
						 5: [0.666, 0.675, fVar, fVar],
						 6: [0.250, 0.200, fVar, fVar],
						 7: [0.250, 0.800, fVar, fVar],
						 8: [0.750, 0.200, fVar, fVar],
						 9: [0.750, 0.800, fVar, fVar]},					 
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

'''4)     - Generate Map'''
'''4.1)     generatePlotTypes()'''
def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()					
class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=False, grain_amount=3):
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)
		
		
		iSmallCircleHoleRadius = self.iNumPlotsY / 9
		
		##### Penny 2023 ### Settings for this map
		iMainCircleCenterX = self.iNumPlotsX / 2
		iMainCircleCenterY = self.iNumPlotsY / 2		
		iMainCircleHoleRadius = self.iNumPlotsX / 4		
		
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x

				
				# Caucasia work Akira		
				
				################# Prep
				bLand = True
				bPeak = False
				iProbaBeWater = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeWater")
				
				# Prep 1 - Define large circle
				if x == iMainCircleCenterX and y == iMainCircleCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iMainCircleCenterX) ** 2) + ((y - iMainCircleCenterY) ** 2))	
							
					
				####### Define ###############
				
				#2a - Small peaks middle big circle
				if abs(x - iMainCircleCenterX) <= 2 and abs(y - iMainCircleCenterY) <= 2:
					if iProbaBeWater <= 85:
						bLand = False
					else:
						bPeak = True
				
				# 2 Main - Remove water main land "Mexico Gulf"
				elif fDistance <= iMainCircleHoleRadius + 1:					
					bLand = False
					
				# 3 Band d'eau nord / Sud
				elif y >= self.iNumPlotsY * 0.95 or y <= self.iNumPlotsY * 0.05 :
					if x >= self.iNumPlotsX * 0.95 or  x <= self.iNumPlotsX * 0.05 or ( x >= self.iNumPlotsX * 0.45 and x <= self.iNumPlotsX * 0.55) :
						if iProbaBeWater <= 25:# 2 mini bridges forced
							bLand = False
					elif iProbaBeWater <= 85:# normal proba
						bLand = False
				
		
				######## Process this now ######
				if bPeak:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK
		
				elif bLand :
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba < 6):
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
					elif (iProba < 30):
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
		
		
		###### Layer Bottom #########
		if iY >= self.iHeight * 0.05 and iY <= self.iHeight * 0.20 :
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_GRASS")	
		elif iY >= self.iHeight * 0.80 and iY <= self.iHeight * 0.95 :
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_GRASS")			
		
		###### Layer Sand #########
		elif iY >= self.iHeight * 0.20 and iY <= self.iHeight * 0.28 :
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")	
		elif iY >= self.iHeight * 0.72 and iY <= self.iHeight * 0.80 :
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")			
		
		else :
		##### Normal group - The "heart"

			
			if iProba <= 0:#changed, don't want "normal desert"
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")		
			if iProba <= 2:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
			elif iProba <= 35:
				terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")				
			else:#then normal
				if val >= self.terrain.getHeightFromPercent(12):
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_GRASS")
				else:
					terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")

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
	
	# Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isPeak() and pPlot.isCoastalLand():
			# If a peak is along the coast, change to hills and recalc.
			
			#2.23 Attention not in the middle
			if pPlot.getY()>= CyMap().getGridHeight() * 0.80 or pPlot.getY() <= CyMap().getGridHeight() * 0.20:
				pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)

	### 2.33 Taken from grid for this, because otherwise the peak tend to block the chance of doing Y wrap	
	featuregen = DonutFeatureGenerator()
	featuregen.addFeatures()
	return 0

class DonutFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		# We don' need no steeking ice. M'kay? Alrighty then.
		ice = 0		
	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		jungle = 0	
				
'''4.6)     addBonuses()	'''
def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')
	BTPResourcesToBalance += ('BONUS_LEAD','BONUS_NICKEL','BONUS_AMBER')
	
	if (type_string in BTPResourcesToBalance or type_string == 'BONUS_SULPHUR'):
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

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
		
		
	if (CyMap().getCustomMapOption(6) == 1):
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

	balancer.normalizeAddExtras()
	
	iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
	if isBTPon:
		CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,False,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")			
	
	#Each Free Extra, it's for the 4 locations / Corners
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
	
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_HORSE"),iBrown)		
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_HORSE"),iBrown)		
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_HORSE"),iBrown)				
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_HORSE"),iBrown)
	
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),iBrown)			
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.100,0,3,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),iBrown)				
	BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),iBrown)			
	BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.900,0,3,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),iBrown)	
	
	if isBTPon:
		BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.100,3,4,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),iBrown)				
		BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.100,3,4,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),iBrown)				
		BTPresourceFromTile(CyMap().getGridWidth() * 0.25 ,CyMap().getGridHeight() * 0.900,3,4,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),iBrown)				
		BTPresourceFromTile(CyMap().getGridWidth() * 0.75 ,CyMap().getGridHeight() * 0.900,3,4,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),iBrown)		
		
		
		#2.35
	if isBTPon:
		listToBalance = ["BONUS_LEAD","BONUS_NICKEL","BONUS_AMBER"]
		balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
		
	doSeaFoodIslands()
	
	#2.36 - v3
	if (CyMap().getCustomMapOption(4)):
		doExtraMarshInsteadDesert()

	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

'''8 )    startHumansOnSameTile()'''

''' 9) Map Depended local logic for Food and Bonus placement'''	
def BTPresourceFromTile(fX, fY, minFromCenter,maxFromCenter,iResourceType,iTerrainType):
		random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
		plotsboundaries = []
		plotsboundariesSafe = []
		
		centerX = int(fX)
		centerY = int(fY)
		
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
def doSeaFoodIslands():
	
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))

	plotsIslandOneTop = []
	plotsIslandTwoTop = []
	plotsIslandThreeTop = []
	plotsIslandFourTop = []
	
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			
			if x >= CyMap().getGridWidth() * 0.00 and x < CyMap().getGridWidth() * 0.50 :
				if y >= CyMap().getGridHeight() * 0.02 and y <= CyMap().getGridHeight() * 0.07:
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
		
				elif y >= CyMap().getGridHeight() * 0.93 and y <= CyMap().getGridHeight() * 1.00 :
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
				
			if x >= CyMap().getGridWidth() * 0.50 and x <= CyMap().getGridWidth() * 1.00 :
				if y >= CyMap().getGridHeight() * 0.02 and y <= CyMap().getGridHeight() * 0.07:
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
				elif y >= CyMap().getGridHeight() * 0.93 and y <= CyMap().getGridHeight() * 1.00 :
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
							
							
	processFoodList(plotsIslandOneTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandTwoTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	processFoodList(plotsIslandFourTop,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),-1,-1)
	
	processFoodList(plotsIslandOneTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandTwoTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	processFoodList(plotsIslandFourTop,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),-1,-1)
	
	processFoodList(plotsIslandOneTop,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandTwoTop,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandThreeTop,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
	processFoodList(plotsIslandFourTop,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),-1,-1)
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
			
			
def doExtraMarshInsteadDesert():#2.36 v3	
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			
			p = CyMap().plot(x,y)
			bDoIt = False
			if y >= CyMap().getGridHeight() * 0.20 and y <= CyMap().getGridHeight() * 0.28:
				bDoIt = True
			if y >= CyMap().getGridHeight() * 0.72 and y <= CyMap().getGridHeight() * 0.80:
				bDoIt = True
				
			if bDoIt:
				if p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
					if not p.isRiver() and not p.isHills() and not p.isImpassable():
						if (p.getFeatureType() == -1 and p.getBonusType(-1) == -1):
							if isBTPon:
								p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"),True,True)
							else:
								p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"),True,True)


				
			

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
					
''' 12 - BTG Dedicated Always call category'''	
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