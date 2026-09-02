
# Penny for BTG Winter 2024 ##

## Option to do -- Lagoon, and reduce peak proba ?

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
def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Beyond the Game map by Penny - Representing Lake Victoria in surrounding Tanzania, Uganda"
	
def getDescriptionTitle():
	return "A map based on Donuts originally and building on Polar Circle, ideal for Medieval start and perhaps Renaissance"

def getDescriptionTitleTwo():
	return "The map has 2 small water paths at the cardinal location accessible by galley, so don't forget it's a toroidal map"

def getDescriptionMain():
	return "Savanna's are very light production features, but be careful the ennemy could quickly cross through them"

def getDescriptionSecond():#Script tip : (on TOP)
	return "The lagoon in the middle has enhanced chances of having Fish, crab & clam resources"
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Teamer for eras without immediate Ocean access, Classi/Medi/Reny"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "SCIENTIFIC extra features is strong, so is KHMER since there is lots of Elephants"	

'''0.1)     getNumHiddenCustomMapOptions() '''
def getNumHiddenCustomMapOptions():
	return 2

'''0.2 getNumCustomMapOptions()'''	
def getNumCustomMapOptions():
	return 6

'''0.3)     getCustomMapOptionDefault()'''	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	3,
		1:	2,
		2:	1,
		3:	1,
		4:	1,
		5:	2,
		}
	return option_defaults[iOption]	
	
'''0.4)     isAdvancedMap()'''
def isAdvancedMap(): return True 	

'''0.5)     getCustomMapOptionName()'''
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:	"MapSize Tweak",
		2:	"Outer Sea Paths",
		3:	"Lagoons",
		4:	"Forest Type",
		5:	"Special Feature",
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
'''0.6)     getNumCustomMapOptionValues()'''	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:	4,
		2:	4,
		3:	2,
		4:	2,
		5:	4,
		}
	return option_values[iOption]
	
'''0.7)     isRandomCustomMapOption()'''
def isRandomCustomMapOption(argsList): return False

'''0.8)     getCustomMapOptionDescAt()'''	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2:	"Titled Axis",
			3: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "Slightly Smaller - [24x24] [32x32] [40x40] [48x48] [56x56] [64x64]",
			1: "Slightly Bigger  - [28x28] [36x36] [44x44] [52x52] [60x60] [68x68]",
			2: "Much Bigger 	 - [32x32] [40x40] [48x48] [56x56] [64x64] [72x72]",
			3: "Super Sized	  - [36x36] [44x44] [52x52] [60x60] [68x68] [76x76]",
			},				
		2:	{
			0: "Very Narrow - 1 Tile",
			1: "Narrow  - 2 Tiles",
			2: "Average - 3 Tiles",
			3: "Very Wide - More than 10 Tiles",
			},	
		3:	{
			0: "No",
			1: "Yes in Lake Victoria",
			},	
		4:	{
			0: "Forest",
			1: "Savannas",
			},	
		5:	{
			0: "None",
			1: "Oasis",
			2: "Kilimanjaro",
			3: "Green Kilimanjaro",
			},				
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text


'''0.9)     - Get Map-Types'''
'''0.9.1)     isClimateMap()'''
def isClimateMap(): return False

'''0.9.2)     isSeaLevelMap()'''
def isSeaLevelMap(): return False


'''1)     beforeInit()'''
def beforeInitOptionsValue():
	global iOptionValue_Wrap
	global iOptionValue_Size	
	global iOptionValue_SeaPath
	global iOptionValue_Lagoon
	global iOptionValue_FeatureForest
	global iOptionValue_Kilimanjaro

	iOptionValue_Wrap = CyMap().getCustomMapOption(0)
	iOptionValue_Size = CyMap().getCustomMapOption(1)
	iOptionValue_SeaPath = CyMap().getCustomMapOption(2)
	iOptionValue_Lagoon = CyMap().getCustomMapOption(3)
	iOptionValue_FeatureForest = CyMap().getCustomMapOption(4)
	iOptionValue_Kilimanjaro = CyMap().getCustomMapOption(5)
	
def beforeInit():
	### Call Option Cleaner ##	
	beforeInitOptionsValue()
	
	## General BTG Initialization ##
	global isBTPon
	global iBrown	
	global iGreen
	global iBrownTypeFeature
	global iGreenTypeFeature
	
	iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
	iGreen = CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")
	
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	

	if isBTPon and 	iOptionValue_FeatureForest:
		iGreenTypeFeature = CyGlobalContext().getInfoTypeForString("FEATURE_PALM_FOREST")
		if CvMapGeneratorUtil.BTGInfo().BTG_Version() > 39:
			iBrownTypeFeature = CyGlobalContext().getInfoTypeForString("FEATURE_SAVANNA")
		else:
			iBrownTypeFeature = CyGlobalContext().getInfoTypeForString("FEATURE_PALM_FOREST")
	else:
		iBrownTypeFeature =  CyGlobalContext().getInfoTypeForString("FEATURE_FOREST")
		iGreenTypeFeature = CyGlobalContext().getInfoTypeForString("FEATURE_FOREST")
		
'''2)     - Initialize Map'''
'''2.2)     getGridSize()'''
def getGridSize(argsList):
	"Override Grid Size function to make the maps square."

	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(6 +iOptionValue_Size,6 +iOptionValue_Size),
		WorldSizeTypes.WORLDSIZE_TINY:		(8 +iOptionValue_Size,8 +iOptionValue_Size),
		WorldSizeTypes.WORLDSIZE_SMALL:		(10+iOptionValue_Size,10+iOptionValue_Size),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(12+iOptionValue_Size,12+iOptionValue_Size),
		WorldSizeTypes.WORLDSIZE_LARGE:		(14+iOptionValue_Size,14+iOptionValue_Size),
		WorldSizeTypes.WORLDSIZE_HUGE:		(16+iOptionValue_Size,16+iOptionValue_Size)
	}
		
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

'''2.3.1)   getTopLatitude()            # always use both'''
def getTopLatitude(): return 10 #Don't want Snow on trees
'''2.3.2)   getBottomLatitude()         # always use both'''
def getBottomLatitude(): return -10 #Don't want Snow on trees

'''2.4.1)   getWrapX()                  # always use both'''
'''2.4.2)   getWrapY()                  # always use both'''
def getWrapX():	return (iOptionValue_Wrap in (1,3))
def getWrapY():	return (iOptionValue_Wrap in (2,3))

'''3)     beforeGeneration()	'''	
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
	configs = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
	
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
	#2.23 - Debug rare crashes
	fVar = 2
	
	templates = {(1,0): {0: [0.50, 0.25, int(0.5 * iW), int(0.5 * iH)]},#AfricaY
				 (2,0): {0: [0.50, 0.25, fVar, int(0.5 * iH)],#AfricaY
						 1: [0.50, 0.75, fVar, int(0.5 * iH)]},#AfricaY
				 (3,0): {0: [0.25, 0.33, fVar, fVar],
						 1: [0.75, 0.33, fVar, fVar],
						 2: [0.50, 0.77, fVar, fVar]},
				 #(4,0): {0: [0.25, 0.33, fVar, fVar],#2.42 was too close, even now it's just about
				 #		 1: [0.75, 0.33, fVar, fVar],
				 #		 2: [0.25, 0.67, fVar, fVar],
				 #		 3: [0.75, 0.67, fVar, fVar]},
				 (4,0): {0: [0.30, 0.30, fVar, fVar],
				 		 1: [0.70, 0.30, fVar, fVar],
				 		 2: [0.30, 0.70, fVar, fVar],
				 		 3: [0.70, 0.70, fVar, fVar]},				 
				 (5,0): {0: [0.25, 0.375, fVar, fVar],
						 1: [0.75, 0.375, fVar, fVar],
						 2: [0.50, 0.25, fVar, fVar],
						 3: [0.25, 0.625, fVar, fVar],
						 4: [0.75, 0.625, fVar, fVar]},
				 (6,0): {0: [0.25, 0.35, fVar, fVar],#AfricaY
						 1: [0.75, 0.35, fVar, fVar],#AfricaY
						 2: [0.50, 0.25, fVar, fVar],#AfricaY
						 3: [0.25, 0.65, fVar, fVar],#AfricaY
						 4: [0.75, 0.65, fVar, fVar],#AfricaY
						 5: [0.50, 0.75, fVar, fVar]},##AfricaY	
				 (7,0): {0: [0.25, 0.33, fVar, fVar],
						 1: [0.75, 0.33, fVar, fVar],
						 2: [0.40, 0.22, fVar, fVar],
						 3: [0.25, 0.67, fVar, fVar],
						 4: [0.75, 0.67, fVar, fVar],
						 5: [0.60, 0.22, fVar, fVar],							 
						 6: [0.50, 0.80, fVar, fVar]},	
				 (8,0): {0: [0.30, 0.35, fVar, fVar],#AfricaX Mostly Y too
						 1: [0.70, 0.35, fVar, fVar],#AfricaX Mostly Y too
						 2: [0.40, 0.28, fVar, fVar],#Africa Y little
						 3: [0.30, 0.65, fVar, fVar],
						 4: [0.70, 0.65, fVar, fVar],
						 5: [0.40, 0.72, fVar, fVar],#Africa Y little	
						 6: [0.60, 0.28, fVar, fVar],#Africa Y little							 
						 7: [0.60, 0.72, fVar, fVar]},#Africa Y little		
				 (9,0): {0: [0.25, 0.33, fVar, fVar],
						 1: [0.75, 0.33, fVar, fVar],
						 2: [0.40, 0.22, fVar, fVar],
						 3: [0.25, 0.67, fVar, fVar],
						 4: [0.75, 0.67, fVar, fVar],
						 5: [0.40, 0.78, fVar, fVar],
						 6: [0.60, 0.22, fVar, fVar],
						 7: [0.60, 0.78, fVar, fVar],
						 8: [0.50, 0.12, fVar, fVar]},
				 (10,0): {0: [0.28, 0.35, fVar, fVar],#Africa X 25 to 30 - 33 to 35
						 1: [0.72, 0.35, fVar, fVar],#Africa X 25 to 30 - 33 to 35
						 2: [0.32, 0.28, fVar, fVar],#Was 0.40 - 0.22
						 3: [0.28, 0.65, fVar, fVar],#Africa X 25 to 30 - 33 to 35
						 4: [0.72, 0.65, fVar, fVar],#Africa X 25 to 30 - 33 to 35
						 5: [0.32, 0.72, fVar, fVar],
						 6: [0.68, 0.28, fVar, fVar],
						 7: [0.68, 0.72, fVar, fVar],
						 8: [0.50, 0.16, fVar, fVar],#0.12 was crashing (in the sea)
						 9: [0.50, 0.84, fVar, fVar]},#0.12 was crashing (in the sea)					 
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
		
		
	beforeGenerationMeasurements()
	beforeGenerationProbaBonus()	
	beforeGenerationBonusList()
		
	return None	
	
def beforeGenerationMeasurements():
	global iCenterX
	global iCenterY
	global iRadius
	global iHoleRadius
	global iMegaRadiusPower
		
	iCenterX = int(CyMap().getGridWidth() / 2)
	iCenterY = int(CyMap().getGridHeight() / 2)
	iRadius = int(CyMap().getGridWidth() * 35 / 100) + 1 
	iHoleRadius = int(CyMap().getGridWidth() / 8) + 1
	iMegaRadius = int(CyMap().getGridWidth() / 2) + (iOptionValue_SeaPath == 3)
	iMegaRadiusPower = iMegaRadius ** 2 + (iOptionValue_SeaPath == 3)
	
	global iY_EquatorTop
	global iY_EquatorBottom
	global iY_Middle
	global iX_Middle

	iY_EquatorTop	 = CyMap().getGridHeight() * 60 / 100
	iY_Middle		 = CyMap().getGridHeight() * 50 / 100
	iX_Middle		 = CyMap().getGridWidth() * 50 / 100
	iY_EquatorBottom = CyMap().getGridHeight() * 40 / 100

	global iProbaLakeVictoriaPeak
	iProbaLakeVictoriaPeak = 10	
	
	global iPeakThreshold
	global iHillThreshold
	
	iPeakThreshold = 1
	iHillThreshold = 18
	
	global iProbaDesert
	global iProbaBrown
	global iProbaGreenFeature
	global iProbaBrownFeature
	global iProbaJungle
	
	iProbaDesert = 10
	iProbaBrown = 70
	iProbaJungle = 20
	iProbaGreenFeature = 40
	iProbaBrownFeature = 20	

def beforeGenerationProbaBonus():	
	global iProbaBonusInternalSeaWhale
	global iProbaBonusInternalSeaFish
	global iProbaBonusInternalSeaCrab
	global iProbaBonusInternalSeaClam
	global iProbaBonusExternalSeaFish
	global iProbaBonusExternalSeaCrab
	global iProbaBonusExternalSeaClam

	iProbaBonusInternalSeaWhale = 15
	iProbaBonusInternalSeaFish = 11 #9  - 2.40 up
	iProbaBonusInternalSeaCrab = 10 #8  - 2.40 up
	iProbaBonusInternalSeaClam = 10 #8  - 2.40 up
	iProbaBonusExternalSeaFish = 7
	iProbaBonusExternalSeaCrab = 5
	iProbaBonusExternalSeaClam	= 5
	
	global iProbaGreenBananaFree
	global iProbaGreenDeerFree
	global iProbaGreenBananaAdjacent
	global iProbaGreenDeerAdjacent

	iProbaGreenBananaFree = 50
	iProbaGreenDeerFree = 50
	iProbaGreenBananaAdjacent = 0
	iProbaGreenDeerAdjacent = 0
	
def beforeGenerationBonusList():
	global lBonusSpecificLogic
	
	global lBonusNormalApply
	global lBonusBalanceDefault
	global lBonusBalanceSpecific
	global lBonusSpecificLogic
	global lBonusExcludedOfMap	
	global lBonusBTGStrategic
	global lBonusWater

	lBonusBTGStrategic = ['BONUS_SULPHUR', 'BONUS_LEAD' , 'BONUS_NICKEL']
	
	lBonusNormalApply = []
	lBonusBalanceDefault = []
	lBonusBalanceSpecific = []
	lBonusSpecificLogic = []
	lBonusExcludedOfMap = []	
	
	#############################
	lBonusBalanceDefault += ['BONUS_ALUMINUM']
	lBonusBalanceDefault += ['BONUS_COAL']
	lBonusBalanceDefault += ['BONUS_COPPER']
	lBonusBalanceDefault += ['BONUS_HORSE']
	lBonusBalanceDefault += ['BONUS_IRON']
	lBonusBalanceDefault += ['BONUS_OIL']
	lBonusBalanceDefault += ['BONUS_URANIUM']	
	
	#############################
	lBonusNormalApply += ['BONUS_INCENSE']
	lBonusNormalApply += ['BONUS_SPICES']
	lBonusNormalApply += ['BONUS_SUGAR']
	lBonusNormalApply += ['BONUS_SILK']
	lBonusNormalApply += ['BONUS_DYE']
	
	lBonusNormalApply += ['BONUS_GEMS']
	
	lBonusNormalApply += ['BONUS_MARBLE']
	lBonusNormalApply += ['BONUS_STONE']	
	
			#Normal applies but generally very little, circa one
	lBonusNormalApply += ['BONUS_COW']		
	lBonusNormalApply += ['BONUS_RICE']
	lBonusNormalApply += ['BONUS_PIG']
	lBonusNormalApply += ['BONUS_CORN']
	
	#####################################
	lBonusExcludedOfMap += ['BONUS_WINE']
	lBonusExcludedOfMap += ['BONUS_FUR']
	lBonusExcludedOfMap += ['BONUS_PEARLS']	
	if isBTPon:
		lBonusExcludedOfMap += ['BONUS_AMBER','BONUS_SALT' , 'BONUS_OLIVES' , 'BONUS_TEA', 'BONUS_POTATO', 'BONUS_SAPPHIRES', 'BONUS_DIAMOND', 'BONUS_JADE', 'BONUS_OBSIDIAN', 'BONUS_PEARLS']
	
	#############################
	lBonusBalanceSpecific += ['BONUS_IVORY']
	lBonusBalanceSpecific += ['BONUS_GOLD']
	lBonusBalanceSpecific += ['BONUS_SILVER']	
	

	#############################
	lBonusSpecificLogic = ['BONUS_FISH','BONUS_CLAM','BONUS_CRAB','BONUS_WHALE']	
	lBonusWater = lBonusSpecificLogic
	
	#On Green
	lBonusSpecificLogic += ['BONUS_BANANA']
	lBonusSpecificLogic += ['BONUS_DEER']
	#Box Top
	lBonusSpecificLogic += ['BONUS_SHEEP']
	#Overall
	lBonusSpecificLogic += ['BONUS_WHEAT']	

'''4)     - Generate Map'''
'''4.1)     generatePlotTypes()'''	
def generatePlotTypes():return AfricaFractalWorld().generatePlotTypes()	
class AfricaFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=5):	
		for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				i = y*CyMap().getGridWidth() + x
				if x == iCenterX and y == iCenterY:
					fDistance = 0
					fDistancePower = 0
				else:
					fDistancePower = ((x - iCenterX) ** 2) + ((y - iCenterY) ** 2)
					fDistance = sqrt(fDistancePower)
					
				#Lake Victoria
				if fDistance < iHoleRadius:
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if iProba <= iProbaLakeVictoriaPeak:
							self.plotTypes[i] = PlotTypes.PLOT_PEAK										
					else:
						self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				
				elif fDistance < iRadius:
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if (iProba <= iPeakThreshold):
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
					elif (iProba <= iHillThreshold):
						self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						self.plotTypes[i] = PlotTypes.PLOT_LAND
	
				# Not declaring code is for Sea (normal sea)
				
				
				# Special case for the options 3 Narrow, we had 2 in each	
				#We do this before the Peak declaration
				elif iOptionValue_SeaPath in (1,2) and x  == CyMap().getGridWidth()/2 - 1 and y == 0:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				elif iOptionValue_SeaPath == 2 and x  == CyMap().getGridWidth()/2 + 1 and y == 0:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN					
				elif iOptionValue_SeaPath in (1,2) and x == 0 and y == CyMap().getGridHeight()/2 - 1:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN				
				elif iOptionValue_SeaPath == 2 and x == 0 and y == CyMap().getGridHeight()/2 + 1:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN									
				#Outer Sea block peak
				elif fDistancePower > iMegaRadiusPower:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK	
					
				#2 Anchor Peaks for Galleys each gap
				elif x == CyMap().getGridWidth()/2 and y in (3,CyMap().getGridHeight()-3):
					self.plotTypes[i] = PlotTypes.PLOT_PEAK	
				elif x in (3,CyMap().getGridWidth()-3) and y == CyMap().getGridHeight()/2:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK			

				elif x == CyMap().getGridWidth()/2 and y in (5,CyMap().getGridHeight()-5) and CyMap().getGridHeight() > 42: #with 40 one set is enough, 44 it's not 
					self.plotTypes[i] = PlotTypes.PLOT_PEAK	
				elif x in (5,CyMap().getGridWidth()-5) and y == CyMap().getGridHeight()/2 and CyMap().getGridHeight() > 42:
					self.plotTypes[i] = PlotTypes.PLOT_PEAK	

				
					
						
		return self.plotTypes	
		
'''4.2)     generateTerrainTypes()		'''		
def generateTerrainTypes(): return AfricaTerrainGenerator().generateTerrain()		
class AfricaTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1, grain_amount=7):
		self.grain_amount = grain_amount + CyGlobalContext().getWorldInfo(CyMap().getWorldSize()).getTerrainGrainChange()
		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
		self.terrain=CyFractal()
		self.fracXExp = fracXExp
		self.fracYExp = fracYExp
		self.initFractals()

	def initFractals(self):
		self.terrain.fracInit(CyMap().getGridWidth(), CyMap().getGridHeight(), self.grain_amount, CyGlobalContext().getGame().getMapRand(), self.iFlags, self.fracXExp, self.fracYExp)
		self.iGrassBottom = self.terrain.getHeightFromPercent(12)		

	def getLatitudeAtPlot(self, iX, iY):
		return None

	def generateTerrain(self):		
		terrainData = [0]*(CyMap().getGridWidth()*CyMap().getGridHeight())
		for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				iI = y*CyMap().getGridWidth()+ x
				terrain = self.generateTerrainAtPlot(x, y)
				terrainData[iI] = terrain
		return terrainData

	def generateTerrainAtPlot(self,iX,iY):
		if (CyMap().plot(iX, iY).isWater()):
			return CyMap().plot(iX, iY).getTerrainType()

		### Africa
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
		if iProba <= iProbaDesert:
			terrainVal = CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT")
		elif iProba <= iProbaDesert + iProbaBrown:
			terrainVal = iBrown		
		else:
			terrainVal = CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")
			
		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal	
	
'''4.3)     addRivers()'''
'''4.4)     addLakes()'''
def addLakes():
	riverGenerator = riversFromSea()
	riverGenerator.seedRivers()
	#CyPythonMgr().allowDefaultImpl()#Africa - I remove because I did the Oasis bit

'''4.5)     addFeatures()'''
def addFeatures():
	AfricaFeatureGenerator().addFeatures()
	return 0	
class AfricaFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		ice = 0	# We don' need no steeking ice. M'kay? Alrighty then.

	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		 #Normal Jungles
		if pPlot.canHaveFeature(self.featureJungle):
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba <= iProbaJungle:
				pPlot.setFeatureType(self.featureJungle, -1)
				
	def addForestsAtPlot(self, pPlot, iX, iY, lat):### Special For Africa
		#forest = 0
		if not pPlot.isHills() and not pPlot.isImpassable():
			if pPlot.canHaveFeature(self.featureForest):
				iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
				if pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"):
					if iProba <= iProbaGreenFeature:
						pPlot.setFeatureType(iGreenTypeFeature,-1)
				else:
					if iProba <= iProbaBrownFeature:
						pPlot.setFeatureType(iBrownTypeFeature,-1)					

'''4.6)     addBonuses()	'''
def addBonusType(argsList):
	[iBonusType] = argsList
	type_string = CyGlobalContext().getBonusInfo(iBonusType).getType()
	sX = CyMap().getGridWidth() / 10
	fX = CyMap().getGridWidth() * 9 / 10
	lowY = CyMap().getGridHeight() / 10
	highY = CyMap().getGridHeight() * 9 / 10	
	listToBalance = []

	if (type_string in lBonusNormalApply):
		return CyPythonMgr().allowDefaultImpl()
		
	elif (type_string in lBonusBalanceDefault):#Balance after StartingPlot
		return None		
			
	elif (type_string in (lBonusSpecificLogic)):
		if type_string == 'BONUS_WHEAT':		
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom,False,type_string,0,3 + iOptionValue_Size,6, False, True,'TERRAIN_PLAINS',False,True)
			BTPResourceInZone(sX,fX,iY_EquatorTop,highY,False,type_string,0,3 + iOptionValue_Size ,6, False, True,'TERRAIN_PLAINS',False,True)	
			if iOptionValue_Size == 1:
				BTPResourceInZone(sX,iX_Middle,iY_EquatorBottom,iY_Middle - 1,False,type_string,0,1,0, False, True,'TERRAIN_GRASS',False,True)
				BTPResourceInZone(sX,iX_Middle,iY_Middle + 1 ,iY_EquatorTop,False,type_string,0,1,0, False, True,'TERRAIN_GRASS',False,True)
				BTPResourceInZone(iX_Middle,fX,iY_EquatorBottom,iY_Middle - 1,False,type_string,0,1,0, False, True,'TERRAIN_GRASS',False,True)
				BTPResourceInZone(iX_Middle,fX,iY_Middle + 1 ,iY_EquatorTop,False,type_string,0,1,0, False, True,'TERRAIN_GRASS',False,True)					
		if type_string == 'BONUS_SHEEP':	
			BTPResourceInZone(sX,fX,iY_EquatorBottom,iY_Middle - 1,False,type_string,0,3,6, False, True,'TERRAIN_GRASS',True,False)
			BTPResourceInZone(sX,fX,iY_Middle + 1 ,iY_EquatorTop,False,type_string,0,3,6, False, True,'TERRAIN_GRASS',True,False)	

	elif (type_string in (lBonusBalanceSpecific)):
		if type_string == 'BONUS_IVORY':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,2,2, False, True,'TERRAIN_PLAINS',False,True)
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,2,2, False, True,'TERRAIN_PLAINS',False,True)			
		if type_string == 'BONUS_SILVER':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,1,8, False, True,'TERRAIN_PLAINS',True,False)	
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,1,8, False, True,'TERRAIN_PLAINS',True,False)						
		if type_string == 'BONUS_GOLD':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,1,8, False, True,'TERRAIN_PLAINS',True,False)	
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,1,8, False, True,'TERRAIN_PLAINS',True,False)					
		
	elif (type_string in (lBonusBTGStrategic) and isBTPon):
		if type_string == 'BONUS_SULPHUR':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,1,8, False, False,'TERRAIN_PLAINS',True,False)	
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,1,8, False, False,'TERRAIN_PLAINS',True,False)		
		if type_string == 'BONUS_LEAD':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,1,8, False, False,'TERRAIN_PLAINS',True,False)	
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,1,8, False, False,'TERRAIN_PLAINS',True,False)		
		if type_string == 'BONUS_NICKEL':
			BTPResourceInZone(sX,fX,lowY,iY_EquatorBottom-1,False,type_string,0,0,2, False, False,'TERRAIN_PLAINS',True,False)	
			BTPResourceInZone(sX,fX,iY_EquatorTop+1,highY,False,type_string,0,0,2, False, False,'TERRAIN_PLAINS',True,False)		
				
	elif (type_string in (lBonusExcludedOfMap)):
		return None
	else:
		return None
		
		
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

'''7)     - Normalize Starting-Plots'''
'''7.1)     normalizeStartingPlotLocations()+'''
def normalizeStartingPlotLocations():
	if isBTPon :
		BTPTopBottomTwoTeams(True)		
	else:
		BTPTopBottomTwoTeams(False)

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
def normalizeAddRiver():return None
def normalizeRemovePeaks():	return None
def normalizeAddLakes(): return CyPythonMgr().allowDefaultImpl()

def normalizeRemoveBadFeatures():return None
def normalizeRemoveBadTerrain():return None
def normalizeAddFoodBonuses():return None
def normalizeGoodTerrain():return None

def normalizeAddExtras():

	BTPnormalizeAddExtrasSpecific(lBonusBalanceDefault,5,1,100)	
	normalizeAddAfricaFood()	
	normalizeAddAfricaFeatures()	
	BTGnormalizeAddExtrasHills(4,False)
	BTGnormalizeAddExtrasFoodStart(False,False,3,'BONUS_DEER',0, False,'TERRAIN_GRASS')		
	CleanForestAndImpassableAfrica()
	
	return False ##CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride	


def CleanForestAndImpassableAfrica():
	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()		
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)
						
						if pPlot.isImpassable() and pPlot.getFeatureType() != -1:
							pPlot.setFeatureType(-1,-1)

						if iOptionValue_FeatureForest == 1 and pPlot.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"):
							pPlot.setTerrainType(iBrown, True, True)#Actually just make tile brown too
							if pPlot.getTerrainType() == iBrown:
								pPlot.setFeatureType(iBrownTypeFeature,-1)	
							if pPlot.getTerrainType() == iGreen:
								pPlot.setFeatureType(iGreenTypeFeature,-1)								


def normalizeAddAfricaFood():

	for y in range(CyMap().getGridHeight()):#Flipped to make the 'drift bias' to the left, not the top bottom
		for x in range(CyMap().getGridWidth()):
		
			fDistancePower = ((x - iCenterX) ** 2) + ((y - iCenterY) ** 2)
			fDistance = sqrt(fDistancePower)
			p = CyMap().plot(x,y)
			iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
				
			################# Lagoons ### #### Sea Food Balancing ####
			iAdjacentBonusCount = 0
			for tx in range(3):
				for ty in range(3):
					testP = CyMap().plot(x+tx-1,y+ty-1)
					if (testP.getBonusType(-1) != -1):
						iAdjacentBonusCount += 1	

			
			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")):
				if fDistance < iHoleRadius:#Lake Victoria, smart code not to spam the middle
					if isBTPon and iOptionValue_Lagoon:
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAGOON"), True, True)	
				
				if iAdjacentBonusCount < 2: 
					if fDistance <= iHoleRadius and fDistance > iHoleRadius - 3: #Lake Victoria, smart code not to spam the middle
						if iProba <= iProbaBonusInternalSeaFish:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_FISH"))
						elif iProba <= iProbaBonusInternalSeaFish + iProbaBonusInternalSeaCrab:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_CRAB"))
						elif iProba <= iProbaBonusInternalSeaFish + iProbaBonusInternalSeaCrab + iProbaBonusInternalSeaClam:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_CLAM"))
							
					elif fDistance < iRadius + 2 :#Outer Sea	but on the continent not in the peaks
						if iProba <= iProbaBonusExternalSeaFish:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_FISH"))
						elif iProba <= iProbaBonusExternalSeaFish + iProbaBonusExternalSeaCrab:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_CRAB"))
						elif iProba <= iProbaBonusExternalSeaFish + iProbaBonusExternalSeaCrab + iProbaBonusExternalSeaClam:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_CLAM"))
						

			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_OCEAN")):
				if fDistance < iHoleRadius:#Lake Victoria
					if isBTPon and iOptionValue_Lagoon:
						p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAGOON"), True, True)	
					if iAdjacentBonusCount < 2 :
						if iProba <= iProbaBonusInternalSeaWhale:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_WHALE"))

			
			############ Bonus Specific Logic
			#### Greens
			if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")):
				if p.getFeatureType() == -1 and not p.isHills() and not p.isImpassable() and p.getBonusType(-1) == -1:
					if iAdjacentBonusCount == 0:
						if iProba <= iProbaGreenBananaFree:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_BANANA"))
						elif iProba <= iProbaGreenBananaFree + iProbaGreenDeerFree:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_DEER"))
					else:
						if iProba <= iProbaGreenBananaAdjacent:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_BANANA"))
						elif iProba <= iProbaGreenBananaAdjacent + iProbaGreenDeerAdjacent:
							p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_DEER"))	

def normalizeAddAfricaFeatures():

	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()		
			possibleKiliPlot = []
			possibleKiliPlotBest = []
			possibleKiliPlotSuperBest = []
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)
						if not pPlot.isWater() and not pPlot.isImpassable() and pPlot.getBonusType(-1) == -1:
							if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"):
								possibleKiliPlot.append(pPlot)
								if not pPlot.isRiver() and pPlot.getFeatureType() == -1 and not pPlot.isRiverSide() and not pPlot.isFreshWater():
									possibleKiliPlotBest.append(pPlot)
			
			#Kilimanjaro Implementation
			if iOptionValue_Kilimanjaro != 0:
				for i in range(2):					
					if len(possibleKiliPlotBest ) > 0:
						pChosenPlot = possibleKiliPlotBest[CyGame().getSorenRandNum(len(possibleKiliPlotBest), "where")]## This is for 1 plot
						possibleKiliPlotBest.remove(pChosenPlot)
					elif len(possibleKiliPlot ) > 0:
						pChosenPlot = possibleKiliPlot[CyGame().getSorenRandNum(len(possibleKiliPlot), "where")]## This is for 1 plot
						possibleKiliPlot.remove(pChosenPlot)
					
					pChosenPlot.setPlotType(PlotTypes.PLOT_LAND, True, True)
					if i == 0:
						pChosenPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)
						pChosenPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_OASIS"),-1)
					if i == 1 and isBTPon and iOptionValue_Kilimanjaro in (2,3): 
						if iOptionValue_Kilimanjaro == 2:
							pChosenPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"), True, True)
						if iOptionValue_Kilimanjaro == 3:
							pChosenPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)
						pChosenPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_KILIMANJARO"),-1)
						
def BTGnormalizeAddExtrasHills(iMinHills, bMirrorLogic):

	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()		
			possiblePlots = []
			iHillCountPlayer = 0
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)

						if pPlot.isHills():
							iHillCountPlayer += 1
						
						elif not pPlot.isWater() and not pPlot.isImpassable() and pPlot.getBonusType(-1) == -1:
							if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
								possiblePlots.append(pPlot)	
			
			iMissingHills = iMinHills - iHillCountPlayer	
			if not bMirrorLogic or start_plot.getX() < CyMap().getGridWidth()/2 :#2.40
				if iMissingHills > 0:
					for i in range(iMissingHills):
						pChosenPlot = possiblePlots[CyGame().getSorenRandNum(len(possiblePlots), "where")]## This is for 1 plot
						pChosenPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)	
						possiblePlots.remove(pChosenPlot)
						
						if bMirrorLogic:#2.40
							pMirrorPlot = CyMap().plot(CyMap().getGridWidth() - pChosenPlot.getX() - 1,pChosenPlot.getY())
							pMirrorPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)							

#def BTGnormalizeAddExtrasFoodStart(bForcePlacement,bAllowedOnHills,iThresholdFood,iBonusType,iForestForceType,bMirrorLogic):
def BTGnormalizeAddExtrasFoodStart(bForcePlacement,bAllowedOnHills,iThresholdFood,iBonusType,iForestForceType,bMirrorLogic,szTerrainType):

	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()	
	
			possiblePlots = []
			iFoodCount = 0
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					#if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 3) and not (dx == 3 and dy == -2) and not (dx == 3 and dy == 3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)
						
						if not pPlot.isWater() and not pPlot.isImpassable() and pPlot.getBonusType(-1) == -1:
							if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
								if not pPlot.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_KILIMANJARO"):
									if not pPlot.isHills() or bAllowedOnHills:
										possiblePlots.append(pPlot)	
									
						elif pPlot.getBonusType(-1) != -1:	
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_DEER") : iFoodCount += 3#Africa
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CLAM") : iFoodCount += 2#Africa
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CRAB") : iFoodCount += 2#Africa
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_FISH") : iFoodCount += 3#Africa
							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CORN") : 
								iFoodCount += 3#Africa
								if pPlot.isRiver():
									iFoodCount += 1
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_WHEAT") : 
								iFoodCount += 3#Africa
								if pPlot.isRiver():
									iFoodCount += 1							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_PIG") : iFoodCount += 3
							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_SHEEP") : 
								iFoodCount += 1
								if pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS") : 
									iFoodCount += 1
					
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_COW") : 
								iFoodCount += 2#Africa
								if pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS") : 
									iFoodCount += 1
									
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_RICE") : 
								iFoodCount += 1
								if pPlot.isRiver():
									iFoodCount += 1
											
			if not bMirrorLogic or start_plot.getX() < CyMap().getGridWidth()/2 :#2.40
											
				#for pChosenPlot in possiblePlots: -- This is to test all the plots
				pChosenPlot = possiblePlots[CyGame().getSorenRandNum(len(possiblePlots), "where")]## This is for 1 plot
				if bForcePlacement or iThresholdFood > iFoodCount :
					pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iBonusType))
					if szTerrainType != - 1:#New For Africa
						pChosenPlot.setTerrainType(CyGlobalContext().getInfoTypeForString(szTerrainType),True,True)
					if iForestForceType == 0:#Remove Forest
						pChosenPlot.setFeatureType(-1, -1)#Snow variation #Out because of oil
					if iForestForceType == 1:#Force Forest
						pChosenPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation #Out because of oil		
						
					if bMirrorLogic:#2.40
						pMirrorPlot = CyMap().plot(CyMap().getGridWidth() - pChosenPlot.getX() - 1,pChosenPlot.getY())
						pMirrorPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iBonusType))
						pMirrorPlot.setTerrainType(pChosenPlot.getTerrainType(), True, True)
						if iForestForceType == 0:#Remove Forest
							pMirrorPlot.setFeatureType(-1, -1)#Snow variation #Out because of oil
						if iForestForceType == 1:#Force Forest
							pMirrorPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation #Out because of oil	
						if iForestForceType == 2:
							pMirrorPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_PALM_FOREST"), -1)#Snow variation #Out because of oil	
						if iForestForceType == 3:
							pMirrorPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_SAVANNA"), -1)#Snow variation #Out because of oil								

'''8 )    startHumansOnSameTile()'''	
def startHumansOnSameTile(): CyPythonMgr().allowDefaultImpl()	

''' 9) Map Depended local logic for Food and Bonus placement'''	
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

def BTPResourceInZone(LeftX,RightX,BottomY,TopY,isWater,szResourceType,iMinInstance,iFixInstance,iByPlayerInstance,bCanHaveOnly,bSeparatedOnly,szMakeTerrain,bMakeHill,bMakeFlat):#2.40

		random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))	
		
		iResourceType = CyGlobalContext().getInfoTypeForString(szResourceType)
		iMakeTerrain = CyGlobalContext().getInfoTypeForString(szMakeTerrain)
		
		plotsLevel3FreeTile = []
		plotsLevel2NotAdjacent = []
		plotsLevel1CanHaveCanAdjacent = []
		plotsLevel0CanHaveNotAdjacent = []
		
		iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		if iByPlayerInstance not in (0,-1):
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
											
										
											
										if iBonusCount >= 1 and not testP.canHaveBonus(iResourceType,True):
											plotsLevel3FreeTile.append(p)
										elif iBonusCount == 0 and not testP.canHaveBonus(iResourceType,True):
											plotsLevel2NotAdjacent.append(p)											
										elif iBonusCount >= 1 and testP.canHaveBonus(iResourceType,True):
											plotsLevel1CanHaveCanAdjacent.append(p)
										elif iBonusCount == 0 and testP.canHaveBonus(iResourceType,True):
											plotsLevel0CanHaveNotAdjacent.append(p)									
			
			p = -1
			if len(plotsLevel0CanHaveNotAdjacent) > 0:		
				random.shuffle(plotsLevel0CanHaveNotAdjacent)
				p = plotsLevel0CanHaveNotAdjacent[0]			
				plotsLevel0CanHaveNotAdjacent.remove(p)
			elif len(plotsLevel1CanHaveCanAdjacent) > 0 and not bSeparatedOnly :
				random.shuffle(plotsLevel1CanHaveCanAdjacent)
				p = plotsLevel1CanHaveCanAdjacent[0]	
				plotsLevel1CanHaveCanAdjacent.remove(p)
			elif len(plotsLevel2NotAdjacent) > 0 and not bCanHaveOnly:
				random.shuffle(plotsLevel2NotAdjacent)
				p = plotsLevel2NotAdjacent[0]	
				plotsLevel2NotAdjacent.remove(p)
			elif len(plotsLevel3FreeTile) > 0 and not bSeparatedOnly and not bCanHaveOnly:
				random.shuffle(plotsLevel3FreeTile)
				p = plotsLevel3FreeTile[0]	
				plotsLevel3FreeTile.remove(p)	
			
			if not p == -1:
				p.setBonusType(iResourceType)
				if bMakeHill:
					p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
				if bMakeFlat:
					p.setPlotType(PlotTypes.PLOT_LAND, True, True)
				if iMakeTerrain != -1:
					p.setTerrainType(CyGlobalContext().getInfoTypeForString(szMakeTerrain), True, True)			


def BTPnormalizeAddExtrasSpecific(listToBalance,iDistanceMax,iDistanceMin,iProbaTreshold):

	gc = CyGlobalContext()	
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	
	for i in range(gc.getMAX_CIV_PLAYERS()):
		if (gc.getPlayer(i).isEverAlive()):
			start_plot = gc.getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()
			
			plots = []
			for dx in range(-iDistanceMax,iDistanceMax+1):
				for dy in range(-iDistanceMax,iDistanceMax+1):
					if ((abs(dx) >= iDistanceMin) and (abs(dy) >= iDistanceMin)):#2.35 My Take
						x,y = startx+dx, starty+dy
						pLoopPlot = CyMap().plot(x,y)
						if not pLoopPlot.isNone():
							plots.append(pLoopPlot)
			
			resources_placed = []
			
			for pass_num in range(5):
				bIgnoreUniqueRange  = pass_num >= 1
				bIgnoreOneArea 		= pass_num >= 2
				bIgnoreWater	 	= pass_num >= 4#2.38 I flip this
				bIgnoreAdjacent 	= pass_num >= 3#2.38 I flip this

				for bonus in range(gc.getNumBonusInfos()):
					type_string = gc.getBonusInfo(bonus).getType()
					if (type_string not in resources_placed)  and (type_string in listToBalance):####This is the line that's different
						bLandValid = False
						for iTerrain in range(gc.getNumTerrainInfos()):
							if gc.getBonusInfo(bonus).isTerrain(iTerrain):
								if not gc.getTerrainInfo(iTerrain).isWater():
									bLandValid = True
						# Randomize placement
						iOffset = gc.getGame().getMapRand().get(len(plots), "BonusBalancer")
						for j in range(0, len(plots)):
							pLoopPlot = plots[(j + iOffset) % len(plots)] # </advc.108c>
							if (pLoopPlot.canHaveBonus(bonus, True)
									# advc.108c:
									and (bIgnoreWater or not pLoopPlot.isWater() or not bLandValid)):
								if isBonusValid(bonus, pLoopPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
									resources_placed.append(type_string)	
									iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
									if iProba <= iProbaTreshold:#2.35 my Take
										pLoopPlot.setBonusType(bonus)
									break # go to the next bonus'''

def isBonusValid(eBonus, pPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
	"Returns true if we can place a bonus here"

	iX, iY = pPlot.getX(), pPlot.getY()

	if (not bIgnoreOneArea) and CyGlobalContext().getBonusInfo(eBonus).isOneArea():
		if CyMap().getNumBonuses(eBonus) > 0:
			if CyMap().getArea(pPlot.getArea()).getNumBonuses(eBonus) == 0:
				return False
				
	if not bIgnoreAdjacent:
		for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
			pLoopPlot = plotDirection(iX, iY, DirectionTypes(iI))
			if not pLoopPlot.isNone():
				if (pLoopPlot.getBonusType(-1) != -1) and (pLoopPlot.getBonusType(-1) != eBonus):
					return False

	if not bIgnoreUniqueRange:
		uniqueRange = CyGlobalContext().getBonusInfo(eBonus).getUniqueRange()
		for iDX in range(-uniqueRange, uniqueRange+1):
			for iDY in range(-uniqueRange, uniqueRange+1):
				pLoopPlot = plotXY(iX, iY, iDX, iDY)
				if not pLoopPlot.isNone() and pLoopPlot.getBonusType(-1) == eBonus:
					return False
	
	return True									
					
''' 12 - BTG Dedicated Always call category'''						
'''def BTGDistanceModifierMap():'''
'''def BTGFreeUnit():'''			
'''def BTGFreeUnitCount():'''
'''def canBuildImprovement(argsList):'''
'''def BTGSong():'''
def BTGSong():
	CyGame().setMapTriggerSound(1) # 1 is Black Forest Song
	return 1 # Has to be 1 to activate

def BTGlistUUM(): 
	
	UUMList = [
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],["BONUS_WHALE"],['BONUS_BANANA'],['BONUS_DEER'],['BONUS_SHEEP'],['BONUS_POTATO'],['BONUS_WHEAT'],
	['BONUS_INCENSE'],['BONUS_SPICES'],['BONUS_SUGAR'],['BONUS_SILK'],['BONUS_DYE'],['BONUS_GEMS'],['BONUS_MARBLE'],['BONUS_STONE'],['BONUS_COW'],['BONUS_RICE'],['BONUS_PIG'],['BONUS_CORN'],
	["BONUS_GOLD"],["BONUS_SILVER"],
	
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],["BONUS_WHALE"],['BONUS_BANANA'],['BONUS_DEER'],['BONUS_SHEEP'],['BONUS_POTATO'],['BONUS_WHEAT'],
	['BONUS_INCENSE'],['BONUS_SPICES'],['BONUS_SUGAR'],['BONUS_SILK'],['BONUS_DYE'],['BONUS_GEMS'],['BONUS_MARBLE'],['BONUS_STONE'],['BONUS_COW'],['BONUS_RICE'],['BONUS_PIG'],['BONUS_CORN'],
	["BONUS_GOLD"],["BONUS_SILVER"],#46
	
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],['BONUS_BANANA'],['BONUS_DEER'],['BONUS_SHEEP'],['BONUS_POTATO'],['BONUS_WHEAT'],#Removed Whale
	['BONUS_INCENSE'],
	['BONUS_SPICES'],['BONUS_SUGAR'],['BONUS_SILK'],['BONUS_DYE'],['BONUS_GEMS'],['BONUS_MARBLE'],['BONUS_STONE'],['BONUS_COW'],['BONUS_RICE'],['BONUS_PIG'],['BONUS_CORN'],
	["BONUS_GOLD"],["BONUS_SILVER"],#68
	
	['BONUS_LEAD'], ['BONUS_NICKEL'], ['BONUS_LEAD'], ['BONUS_NICKEL'],#72
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],#75
	#["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],
	["BONUS_SHEEP"],["BONUS_SHEEP"]#77

	]

	return UUMList

def BTGlistWWM(): 

	WWMList = []
	WWMList += lBonusSpecificLogic #9
	WWMList += lBonusNormalApply #12
	WWMList += lBonusSpecificLogic #9
	WWMList += lBonusWater #4
	WWMList += lBonusBalanceSpecific #3 - Gems Ivory Gold
	#WWMList += lBonusBTGStrategic #3 ['BONUS_SULPHUR', 'BONUS_LEAD' , 'BONUS_NICKEL']
	
	WWMList = [
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],["BONUS_WHALE"],['BONUS_BANANA'],['BONUS_DEER'],['BONUS_SHEEP'],['BONUS_POTATO'],['BONUS_WHEAT'],
	['BONUS_INCENSE'],['BONUS_SPICES'],['BONUS_SUGAR'],['BONUS_SILK'],['BONUS_DYE'],['BONUS_GEMS'],['BONUS_MARBLE'],['BONUS_STONE'],['BONUS_COW'],['BONUS_RICE'],['BONUS_PIG'],['BONUS_CORN'],
	#["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],#["BONUS_WHALE"],
	["BONUS_GOLD"],["BONUS_SILVER"],#["BONUS_IVORY"]
	["BONUS_FISH"],["BONUS_CLAM"],["BONUS_CRAB"],['BONUS_BANANA'],['BONUS_DEER'],['BONUS_SHEEP'],['BONUS_POTATO'],['BONUS_WHEAT']#Removed Whale
	,["BONUS_COW"]#2.42 - Terracotta Count
	]
	
	return WWMList
	


class riversFromSea:
	def __init__(self):
		self.gc = CyGlobalContext()
		self.dice = self.gc.getGame().getMapRand()
		self.map = CyMap()
		self.width = self.map.getGridWidth()
		self.height = self.map.getGridHeight()
		self.straightThreshold = 3
		if (self.width * self.height > 400):
			self.straightThreshold = 2

	def seedRivers(self):
	
		##### Africa forced ######
		climate = 2
		userInputLandmass = 0
		##### Africa end ####
		
		if (climate == 0):                 # Arid
			divider = 6
		elif (climate == 1):               # Normal
			divider = 3
		elif (climate == 2):               # Wet
			divider = 2
		elif (climate == 3):               # No ice
			divider = 3
		maxNumber = (self.width + self.height) / divider
		
		riversNumber = 1 + maxNumber
		if (userInputLandmass == 1):       # Pangaea
			riversNumber = maxNumber/2
		self.coasts = self.collateCoasts()
		coastsNumber = len(self.coasts)
		if (coastsNumber == 0):
			return
		coastShare = coastsNumber/riversNumber
		for i in range(riversNumber):
			(x,y,flow) = self.generateRiver(i,coastShare)
			if (flow != CardinalDirectionTypes.NO_CARDINALDIRECTION):
				riverID = self.gc.getMap().getNextRiverID()
				self.addRiverFrom(x,y,flow,riverID)

	def collateCoasts(self):
		result = []
		for x in range(self.width):
			for y in range(self.height):
				plot = self.map.plot(x,y)
				if (plot.isCoastalLand()):
					result.append(plot)
		return result

	def generateRiver(self,i,coastShare):
		choiceCoast = coastShare * i + self.dice.get(coastShare,"Pick a coast for the river")
		plot = self.coasts[choiceCoast]
		FlowDirection = CardinalDirectionTypes.NO_CARDINALDIRECTION
		x = plot.getX()
		y = plot.getY()
		if ((y < 1 or y >= self.height - 1) or plot.isNOfRiver() or plot.isWOfRiver()):
			return (x,y,FlowDirection)
		eastX = self.eastX(x)
		westX = self.westX(x)
		otherPlot = True
		eastPlot = self.map.plot(eastX,y)
		if (eastPlot.isCoastalLand()):
			seaPlot = self.map.plot(x,y+1)
			if ((self.map.plot(x,y+1).isWater()) or (self.map.plot(eastX,y+1).isWater())):
				landPlot1 = self.map.plot(x,y-1)
				landPlot2 = self.map.plot(eastX,y-1)
				if (landPlot1.isWater() or landPlot2.isWater()):
					otherPlot = True
				else:
					FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_NORTH
					otherPlot = False
			if (otherPlot == True):
				if ((self.map.plot(x,y-1).isWater()) or (self.map.plot(eastX,y-1).isWater())):
					landPlot1 = self.map.plot(x,y+1)
					landPlot2 = self.map.plot(eastX,y+1)
					if (landPlot1.isWater() or landPlot2.isWater()):
						otherPlot = True
					else:
						FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
						otherPlot = False
		if (otherPlot == True):
			southPlot = self.map.plot(x,y-1)
			if (southPlot.isCoastalLand()):
				if ((self.map.plot(eastX,y).isWater()) or (self.map.plot(eastX,y-1).isWater())):
					landPlot1 = self.map.plot(westX,y)
					landPlot2 = self.map.plot(westX,y-1)
					if (landPlot1.isWater() or landPlot2.isWater()):
						otherPlot = True
					else:
						FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_EAST
						otherPlot = False
				if (otherPlot == True):
					if ((self.map.plot(westX,y).isWater()) or (self.map.plot(westX,y-1).isWater())):
						landPlot1 = self.map.plot(eastX,y)
						landPlot2 = self.map.plot(eastX,y-1)
						if (landPlot1.isWater() or landPlot2.isWater()):
							otherPlot = True
						else:
							FlowDirection = CardinalDirectionTypes.CARDINALDIRECTION_WEST
		return (x,y,FlowDirection)

	# prevent rivers from crossing each other
	def preventRiversFromCrossing(self,x,y,flow,riverID):
		plot = self.map.plot(x,y)
		eastX = self.eastX(x)
		westX = self.westX(x)
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
			if (plot.isNOfRiver()):
				return true
			if (self.map.plot(eastX,y).isNOfRiver()):
				return true
			southPlot = self.map.plot(x,y-1)
			if (southPlot.isWOfRiver() and southPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
				return true
			if (plot.isWOfRiver() and plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
				return true
			if (self.map.plot(eastX,y).isWater()):
				return true
			if (self.map.plot(x,y-1).isWater()):
				return true
			if (self.map.plot(eastX,y-1).isWater()):
				return true
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
			if (plot.isNOfRiver()):
				return true
			if (self.map.plot(westX,y).isNOfRiver()):
				return true
			southPlot = self.map.plot(westX,y-1)
			if (southPlot.isWOfRiver() and southPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
				return true
			westPlot = self.map.plot(westX,y)
			if (westPlot.isWOfRiver() and westPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
				return true
			if (self.map.plot(westX,y).isWater()):
				return true
			if (self.map.plot(x,y-1).isWater()):
				return true
			if (self.map.plot(westX,y-1).isWater()):
				return true
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
			if (plot.isWOfRiver()):
				return true
			eastPlot = self.map.plot(eastX,y)
			if (eastPlot.isNOfRiver() and eastPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
				return true
			if (plot.isNOfRiver() and plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
				return true
			if (self.map.plot(x,y-1).isWOfRiver()):
				return true
			if (self.map.plot(x,y-1).isWater()):
				return true
			if (self.map.plot(x+1,y).isWater()):
				return true
			if (self.map.plot(x+1,y-1).isWater()):
				return true
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
			if (plot.isWOfRiver()):
				return true
			eastPlot = self.map.plot(eastX,y+1)
			if (eastPlot.isNOfRiver() and eastPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
				return true
			northPlot = self.map.plot(x,y+1)
			if (northPlot.isNOfRiver() and northPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
				return true
			if (self.map.plot(x,y+1).isWOfRiver()):
				return true
			if (self.map.plot(x,y+1).isWater()):
				return true
			if (self.map.plot(x+1,y).isWater()):
				return true
			if (self.map.plot(x+1,y+1).isWater()):
				return true
		return false


	def addRiverFrom(self,x,y,flow,riverID):
		plot = self.map.plot(x,y)
		if (plot.isWater()):
			return
		eastX = self.eastX(x)
		westX = self.westX(x)
		if (self.preventRiversFromCrossing(x,y,flow,riverID)):
			return
		plot.setRiverID(riverID)
		if ((flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST)):
			plot.setNOfRiver(True,flow)
		else:
			plot.setWOfRiver(True,flow)
		xShift = 0
		yShift = 0
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
			xShift = 1
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST):
			xShift = -1
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
			yShift = -1
		if (flow == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH):
			yShift = 1
		nextX = x + xShift
		nextY = y + yShift
		if (nextX >= self.width):
			nextX = 0
		if (nextY >= self.height):
			return
		nextI = nextY*self.width + nextX
		if (self.canFlowFrom(plot,self.map.plot(nextX,nextY)) == False):
			return
		if (plot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW") and self.dice.get(10,"Stop on ice") > 3):
			return
		flatDesert = (plot.getPlotType() == PlotTypes.PLOT_LAND) and (plot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
		#Prevent Uturns in rivers
		turnThreshold = 16
		if flatDesert:
			turnThreshold = 18
		turned = False
		northY = y + 1
		southY = y - 1
		if ((flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST)):
			if ((northY < self.height) and (self.dice.get(20,"branch from north") > turnThreshold)):
				nextI = northY*self.width + x
				if (self.canFlowFrom(plot,self.map.plot(x,northY)) and self.canFlowFrom(self.map.plot(self.eastX(x),y),self.map.plot(self.eastX(x),northY))):
					turned = True
					if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
						self.addRiverFrom(x,y,CardinalDirectionTypes.CARDINALDIRECTION_SOUTH,riverID)
					else:
						westPlot = self.map.plot(westX,y)
						westPlot.setRiverID(riverID)
						self.addRiverFrom(westX,y,CardinalDirectionTypes.CARDINALDIRECTION_SOUTH,riverID)
			if ((not turned) and (southY >= 0) and (self.dice.get(20,"branch from south") > turnThreshold)):
				nextI = southY*self.width + x
				if (self.canFlowFrom(plot,self.map.plot(x,southY)) and self.canFlowFrom(self.map.plot(self.eastX(x),y),self.map.plot(self.eastX(x),southY))):
					turned = True
					if (flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST):
						southPlot = self.map.plot(x,y-1)
						southPlot.setRiverID(riverID)
						self.addRiverFrom(x,southY,CardinalDirectionTypes.CARDINALDIRECTION_NORTH,riverID)
					else:
						westPlot = self.map.plot(westX,southY)
						westPlot.setRiverID(riverID)
						self.addRiverFrom(westX,southY,CardinalDirectionTypes.CARDINALDIRECTION_NORTH,riverID)
		else:
			nextI = y*self.width + eastX
			if (self.canFlowFrom(plot,self.map.plot(eastX,y)) and self.canFlowFrom(self.map.plot(x,southY),self.map.plot(eastX,y)) and (self.dice.get(20,"branch from east") > turnThreshold)):
				turned = True
				if (flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
					eastPlot = self.map.plot(eastX,y)
					eastPlot.setRiverID(riverID)
					self.addRiverFrom(eastX,y,CardinalDirectionTypes.CARDINALDIRECTION_WEST,riverID)
				else:
					northEastPlot = self.map.plot(eastX,y+1)
					northEastPlot.setRiverID(riverID)
					self.addRiverFrom(eastX,y+1,CardinalDirectionTypes.CARDINALDIRECTION_WEST,riverID)
			nextI = y*self.width + westX
			if ((not turned) and self.canFlowFrom(plot,self.map.plot(westX,y)) and self.canFlowFrom(self.map.plot(x,southY),self.map.plot(westX,southY)) and (self.dice.get(20,"branch from west") > turnThreshold)):
				turned = True
				if (flow == CardinalDirectionTypes.CARDINALDIRECTION_NORTH):
					self.addRiverFrom(x,y,CardinalDirectionTypes.CARDINALDIRECTION_EAST,riverID)
				else:
					northPlot = self.map.plot(x,y+1)
					northPlot.setRiverID(riverID)
					self.addRiverFrom(x,y+1,CardinalDirectionTypes.CARDINALDIRECTION_EAST,riverID)
		spawnInDesert = (not turned) and flatDesert
		if ((self.dice.get(10,"straight river") > self.straightThreshold) or spawnInDesert):
			self.addRiverFrom(nextX,nextY,flow,riverID)
		else:
			if (not turned):
				plot = self.map.plot(nextX,nextY)
				if ((plot.getPlotType() == PlotTypes.PLOT_LAND) and (self.dice.get(10,"Rivers start in hills") > 3)):
					plot.setPlotType(PlotTypes.PLOT_HILLS,true,true)
					if ((flow == CardinalDirectionTypes.CARDINALDIRECTION_WEST) or (flow == CardinalDirectionTypes.CARDINALDIRECTION_EAST)):
						if southY > 0:
							self.map.plot(nextX,southY).setPlotType(PlotTypes.PLOT_HILLS,true,true)
					else:
						self.map.plot(eastX,nextY).setPlotType(PlotTypes.PLOT_HILLS,true,true)

	def canFlowFrom(self,plot,upperPlot):
		if (plot.isWater()):
			return False
		if (plot.getPlotType() == PlotTypes.PLOT_PEAK):
			return False
		if (plot.getPlotType() == PlotTypes.PLOT_HILLS):
			if ((upperPlot.getPlotType() == PlotTypes.PLOT_HILLS) or (upperPlot.getPlotType() == PlotTypes.PLOT_PEAK)):
				return True
			else:
				return False
		if (plot.getPlotType() == PlotTypes.PLOT_LAND):
			if (upperPlot.isWater()):
				return False
		return True
	
	def westX(self,x):
		westX = x - 1
		if (westX < 0):
			westX = self.width
		return westX

	def eastX(self,x):
		eastX = x + 1
		if (eastX >= self.width):
			eastX = 0
		return eastX