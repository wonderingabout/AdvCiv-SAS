#
#	FILE:	 Water.py
#	AUTHOR:  Sean McCarthy
#	PURPOSE: Loosely adapted from Lakes.py, emphasizing many small bodies of water, extra rivers, and chokepoints.
#-----------------------------------------------------------------------------

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

gc = CyGlobalContext()

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_LAKES_DESCR"

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getGridSize(argsList):
	"Because this is such a land-heavy map, override getGridSize() to make the map smaller"
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(6,4),
		WorldSizeTypes.WORLDSIZE_TINY:		(8,5),
		WorldSizeTypes.WORLDSIZE_SMALL:		(10,6),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(13,8),
		WorldSizeTypes.WORLDSIZE_LARGE:		(16,10),
		WorldSizeTypes.WORLDSIZE_HUGE:		(21,13)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def getWrapX(): return True
def getWrapY(): return False

def minStartingDistanceModifier():
	return -15

def findStartingArea(argsList):
	"make sure all players are on the biggest area"
	[playerID] = argsList
	return gc.getMap().findBiggestArea(False).getID()

# Subclass to customize sea level effects.
class WaterFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=30, shift_plot_types=False, 
	                      grain_amount=3):
		# Check for changes to User Input variances.
		self.checkForOverrideDefaultUserInputVariances()
		
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, 0, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, 0, self.fracXExp, self.fracYExp)

		water_percent += self.seaLevelChange
		water_percent = min(water_percent, 40)
		water_percent = max(water_percent, 20)

		hill1range =  int(25 * increase(self.hillGroupOneRange/25.0, 1.6))
		hill2range =  int(25 * increase(self.hillGroupTwoRange/25.0, 1.6))

		iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - hill1range), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + hill1range), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - hill2range), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + hill2range), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(int(100*increase(self.peakPercent/100.0, 2.3)))

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				
				# Continuing on with plot generation.
				val = self.continentsFrac.getHeight(x,y)
				if val <= iWaterThreshold:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
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

		# Convert 1-tile lakes into flatland. We have plenty of larger lakes, and having the 1-tile lakes too really limits space for rivers.
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				if self.plotTypes[i] == PlotTypes.PLOT_OCEAN and self.isSurroundedByLand(x, y):
					self.plotTypes[i] = PlotTypes.PLOT_LAND	
							

		if shift_plot_types:
			self.shiftPlotTypes()
		
		

		return self.plotTypes

	def isSurroundedByLand(self, x, y):
		for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
			j = ((y+dy) % self.iNumPlotsY)*self.iNumPlotsX + (x+dx) % self.iNumPlotsX
			if self.plotTypes[j] == PlotTypes.PLOT_OCEAN:
				return False
		return True

def generatePlotTypes():
	"generate a very grainy world for lots of little lakes"
	NiTextOut("Setting Plot Types (Python Water) ...")
	global fractal_world
	fractal_world = WaterFractalWorld()
	fractal_world.initFractal(continent_grain = 4, rift_grain = -1, has_center_rift = False, invert_heights = True)
	plot_types = fractal_world.generatePlotTypes(water_percent = 30)
	return plot_types

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Lakes) ...")
	terraingen = TerrainGenerator(iDesertPercent=25, iPlainsPercent=13,
	             fSnowLatitude=1.00, fTundraLatitude=0.89,
	             fGrassLatitude=0.13, fDesertBottomLatitude=0.23,
	             fDesertTopLatitude=0.63, fracXExp=-1,
	             fracYExp=-1, grain_amount=5)
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Lakes) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def increase(fraction, multiplier):
	"(0 <= fraction <= 1, 1 < multiplier): for very small frac this is equivalent to multiplying by multiplier. for larger fraction, the effect is smaller, such that the return value always stays below 1"
	return 1 - (1 - fraction) ** multiplier

def addRivers():
	# More rivers!
	CyGlobalContext().setDefineINT("PLOTS_PER_RIVER_EDGE", int(CyGlobalContext().getDefineINT("PLOTS_PER_RIVER_EDGE") / 2))
	CyGlobalContext().setDefineINT("RIVER_SOURCE_MIN_RIVER_RANGE", 1)
	CyGlobalContext().setDefineINT("RIVER_SOURCE_MIN_SEAWATER_RANGE", 2)
	CyPythonMgr().allowDefaultImpl()

# Do not add any lakes! We have enough.
def normalizeAddLakes():
	return

def addLakes():
	return
