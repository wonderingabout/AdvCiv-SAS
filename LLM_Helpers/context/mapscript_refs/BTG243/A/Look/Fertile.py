#
#	FILE:	 Fertile.py
#	AUTHOR:  Thalassicus
#	PURPOSE: Global map script - Generates a world with fewer useless tiles
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
userInputLandmass = 0

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_FERTILE_DESCR"

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 2
	
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_LANDMASS_TYPE",
		1:	"TXT_KEY_MAP_SCRIPT_OCEAN_RIFTS"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:	2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_RANDOM",
			1: "TXT_KEY_MAP_SCRIPT_ARCHIPELAGO",
			2: "TXT_KEY_MAP_SCRIPT_SMALL_CONTINENTS",
			3: "TXT_KEY_MAP_SCRIPT_MASSIVE_CONTINENTS"
			},
		1:	{
			0: "TXT_KEY_MAIN_MENU_NONE",
			1: "TXT_KEY_MAP_SCRIPT_RIFTS_SEVERAL"
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text

def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	false,
		1:	true
		}
	return option_defaults[iOption]

def getGridSize(argsList):
	"Reduced number of plots by 25% (Reduce grid sizes by 10%)"
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(9,6),
		WorldSizeTypes.WORLDSIZE_TINY:		(11,7),
		WorldSizeTypes.WORLDSIZE_SMALL:	        (14,9),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(17,11),
		WorldSizeTypes.WORLDSIZE_LARGE:		(22,14),
		WorldSizeTypes.WORLDSIZE_HUGE:		(27,17)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]
    
class FertileFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def checkForOverrideDefaultUserInputVariances(self):
                self.seaLevelChange = self.seaLevelChange - 15
                if (userInputLandmass != 3): # Not Massive Continents
        		# Overriding peak value to counterbalance not having any peaks along the coasts.
        		extraPeaks = 1 + CyMap().getCustomMapOption(0)
        		self.peakPercent = min(100, self.peakPercent + (15 * extraPeaks))
        		self.peakPercent = max(0, self.peakPercent)
        		# Note, the peaks along the coast are not removed until addFeatures()

		return

def generatePlotTypes():
	"Generates very grainy hills and mountains for smaller landmasses."
	gc = CyGlobalContext()
	map = CyMap()
	fractal_world = FertileFractalWorld()
	NiTextOut("Setting Plot Types (Python Fertile) ...")

	# Get user input.
	userInputRifts = map.getCustomMapOption(1)
        userInputLandmass = CyMap().getCustomMapOption(0)

        if userInputLandmass == 0:
                iSelection = []
                
                # Random Options
                if False: iSelection.append(1) # Archipelago
                if True: iSelection.append(2) # Small Continents
                if True: iSelection.append(3) # Massive Continents
                        
                if len(iSelection) > 0:
                        #userInputLandmass = 3
                        userInputLandmass = iSelection[CyRandom().get(len(iSelection) - 1,"Random Selection")]
                else:
                        #userInputLandmass = 3
                        userInputLandmass = iSelection[CyRandom().get(2,"Random Selection")]
                        

        if userInputRifts == 1: # Several
                iRiftGrain = 2
                bCenterRift = True
        else: # None
                iRiftGrain = -1
                bCenterRift = False
	
	if userInputLandmass == 1: # Archipelego
		fractal_world.initFractal(continent_grain = 4, rift_grain = iRiftGrain, has_center_rift = bCenterRift, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)

	elif userInputLandmass == 3: # Massive Continents
		fractal_world.initFractal(continent_grain = 2, rift_grain = iRiftGrain, has_center_rift = bCenterRift, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 3)

	else: # Small Continents
		fractal_world.initFractal(continent_grain = 3, rift_grain = iRiftGrain, has_center_rift = bCenterRift, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)

class FertileTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
        # Decreased snow, tundra, and desert (from 0.7, 0.6, and 35)
	def __init__(self, iDesertPercent=30, iPlainsPercent=20,
	             fSnowLatitude=0.8, fTundraLatitude=0.7,
	             fGrassLatitude=0.1, fDesertBottomLatitude=0.2,
	             fDesertTopLatitude=0.5, fracXExp=-1,
	             fracYExp=-1, grain_amount=4):
		
		self.gc = CyGlobalContext()
		self.map = CyMap()

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()
		self.iFlags = self.map.getMapFractalFlags()

		self.grain_amount = grain_amount + self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()

		self.deserts=CyFractal()
		self.plains=CyFractal()
		self.variation=CyFractal()

		self.iDesertTopPercent = 100
		self.iDesertBottomPercent = max(0,int(100-iDesertPercent))
		self.iPlainsTopPercent = 100
		self.iPlainsBottomPercent = max(0,int(100-iDesertPercent-iPlainsPercent))
		self.iMountainTopPercent = 75
		self.iMountainBottomPercent = 60

		self.fSnowLatitude = fSnowLatitude
		self.fTundraLatitude = fTundraLatitude
		self.fGrassLatitude = fGrassLatitude
		self.fDesertBottomLatitude = fDesertBottomLatitude
		self.fDesertTopLatitude = fDesertTopLatitude

		self.iDesertPercent = iDesertPercent
		self.iPlainsPercent = iPlainsPercent
		
		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()
		
	def __initFractals(self):
		self.jungles.fracInit(self.iGridW, self.iGridH, self.jungle_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.forests.fracInit(self.iGridW, self.iGridH, self.forest_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		self.iJungleBottom = self.jungles.getHeightFromPercent((100 - self.iJunglePercent)/2)
		self.iJungleTop = self.jungles.getHeightFromPercent(100 - (self.iJunglePercent/2))
		self.iForestLevel = self.forests.getHeightFromPercent(self.iForestPercent)

	def __initFeatureTypes(self):
		self.featureIce = self.gc.getInfoTypeForString("FEATURE_ICE")
		self.featureJungle = self.gc.getInfoTypeForString("FEATURE_JUNGLE")
		self.featureForest = self.gc.getInfoTypeForString("FEATURE_FOREST")
		self.featureOasis = self.gc.getInfoTypeForString("FEATURE_OASIS")

	def getLatitudeAtPlot(self, iX, iY):
		lat = abs((self.iHeight / 2) - iY)/float(self.iHeight/2) # 0.0 = equator, 1.0 = pole

		# Adjust latitude using self.variation fractal, to mix things up:
		lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)

		#lat = lat * 1.0

		# Limit to the range [0, 1]:
		if lat < 0:
			lat = 0.0
		if lat > 1:
			lat = 1.0

		return lat

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Fertile) ...")
	terraingen = FertileTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()

        if (userInputLandmass != 3): # Not Massive Continents
                # Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
                # The peaks bisect too many islands.
        	for plotIndex in range(iW * iH):
        		pPlot = map.plotByIndex(plotIndex)
        		if pPlot.isPeak() and pPlot.isCoastalLand():
        			# If a peak is along the coast, change to hills and recalc.
        			pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
	
	# Now add Features.
	NiTextOut("Adding Features (Python Fertile) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def normalizeRemovePeaks():
	return None
