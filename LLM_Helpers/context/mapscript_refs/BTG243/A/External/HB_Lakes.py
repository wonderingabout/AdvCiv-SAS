#
#	FILE:	 Lakes.py
#	AUTHOR:  Andy Szybalski
#	CONTRIB: Bob Thomas (Sirian)
#	PURPOSE: Global map script - An oceanless planet.
#-----------------------------------------------------------------------------
#	Copyright (c) 2004, 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()

gc = CyGlobalContext()

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_LAKES_DESCR"


resourcesToBalance = ('BONUS_IRON', 'BONUS_HORSE', 'BONUS_COPPER', 'BONUS_MARBLE', 'BONUS_STONE', 'BONUS_IVORY', 'BONUS_PIG', 'BONUS_RICE', 'BONUS_SHEEP', 'BONUS_GOLD', 'BONUS_WHEAT', 'BONUS_CORN', 'BONUS_GEMS')
stratresourcesToBalance = ('BONUS_OIL', 'BONUS_URANIUM', 'BONUS_ALUMINUM', 'BONUS_COAL')
resourcesToEliminate = ('BONUS_SILVER')

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 2

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED"
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:  0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:  false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)

def normalizeAddExtras():
	gc = CyGlobalContext()
	map = CyMap()
	for i in range(gc.getMAX_CIV_PLAYERS()):
		if (gc.getPlayer(i).isAlive()):
			start_plot = gc.getPlayer(i).getStartingPlot() # returns a CyPlot
			startx, starty = start_plot.getX(), start_plot.getY()
			
			plots = [] # build a list of the plots near the starting plot
			for dx in range(-2,3):
				for dy in range(-2,3):
					x,y = startx+dx, starty+dy
					pLoopPlot = map.plot(x,y)
					if not pLoopPlot.isNone():
						plots.append(pLoopPlot)
			
			resources_placed = []
			for pass_num in range(7):
				bIgnoreUniqueRange  = pass_num >= 1
				bIgnoreOneArea 		= pass_num >= 2
				bIgnoreAdjacent 	= pass_num >= 3
				
				for bonus in range(gc.getNumBonusInfos()):
					type_string = gc.getBonusInfo(bonus).getType()
					if (type_string not in resources_placed) and (type_string in resourcesToBalance):
						for (pLoopPlot) in plots:
							if (pLoopPlot.canHaveBonus(bonus, True)):
								if isBonusValid(bonus, pLoopPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
									pLoopPlot.setBonusType(bonus)
									resources_placed.append(type_string)
									#print "placed", type_string, "on pass", pass_num
									break # go to the next bonus


	for i in range(gc.getMAX_CIV_PLAYERS()):
		if (gc.getPlayer(i).isAlive()):
			start_plot = gc.getPlayer(i).getStartingPlot() # returns a CyPlot
			startx, starty = start_plot.getX(), start_plot.getY()
			
			plots = [] # build a list of the plots near the starting plot
			for dx in range(-3,4):
				for dy in range(-3,4):
					x,y = startx+dx, starty+dy
					pLoopPlot = map.plot(x,y)
					if not pLoopPlot.isNone():
						plots.append(pLoopPlot)
			
			resources_placed = []
			for pass_num in range(4):
				bIgnoreUniqueRange  = pass_num >= 1
				bIgnoreOneArea 		= pass_num >= 2
				bIgnoreAdjacent 	= pass_num >= 3
				
				for bonus in range(gc.getNumBonusInfos()):
					type_string = gc.getBonusInfo(bonus).getType()
					if (type_string not in resources_placed) and (type_string in stratresourcesToBalance):
						for (pLoopPlot) in plots:
							if (pLoopPlot.canHaveBonus(bonus, True)):
								if isBonusValid(bonus, pLoopPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
									pLoopPlot.setBonusType(bonus)
									resources_placed.append(type_string)
									#print "placed", type_string, "on pass", pass_num
									break # go to the next bonus

	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride
	
def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if (type_string in resourcesToBalance) or (type_string in resourcesToEliminate):
		return None # don't place any of this bonus randomly
	else:
		CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way
		

def isBonusValid(eBonus, pPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
	"Returns true if we can place a bonus here"
	map = CyMap()
	gc = CyGlobalContext()

	iX, iY = pPlot.getX(), pPlot.getY()

	if (not bIgnoreOneArea) and gc.getBonusInfo(eBonus).isOneArea():
		if map.getNumBonuses(eBonus) > 0:
			if map.getArea(pPlot.getArea()).getNumBonuses(eBonus) == 0:
				return False
				
	if not bIgnoreAdjacent:
		for iI in range(DirectionTypes.NUM_DIRECTION_TYPES):
			pLoopPlot = plotDirection(iX, iY, DirectionTypes(iI))
			if not pLoopPlot.isNone():
				if (pLoopPlot.getBonusType(-1) != -1) and (pLoopPlot.getBonusType(-1) != eBonus):
					return False

	if not bIgnoreUniqueRange:
		uniqueRange = gc.getBonusInfo(eBonus).getUniqueRange()
		for iDX in range(-uniqueRange, uniqueRange+1):
			for iDY in range(-uniqueRange, uniqueRange+1):
				pLoopPlot = plotXY(iX, iY, iDX, iDY)
				if not pLoopPlot.isNone() and pLoopPlot.getBonusType(-1) == eBonus:
					return False
	
	return True



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

def minStartingDistanceModifier():
	return -15

def findStartingArea(argsList):
	"make sure all players are on the biggest area"
	[playerID] = argsList
	return gc.getMap().findBiggestArea(False).getID()

# Subclass to customize sea level effects.
class LakesFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=9, shift_plot_types=True, 
	                      grain_amount=3):
		# Check for changes to User Input variances.
		self.checkForOverrideDefaultUserInputVariances()
		
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, 0, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, 0, self.fracXExp, self.fracYExp)

		water_percent += self.seaLevelChange
		water_percent = min(water_percent, 14)
		water_percent = max(water_percent, 7)

		iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				
				# Adding a row of water (ice) at the poles, at Barry's request.
				if y == 0 or y == self.iNumPlotsY - 1:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
					continue
					
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

		if shift_plot_types:
			self.shiftPlotTypes()
		
		

		return self.plotTypes

def generatePlotTypes():
	"generate a very grainy world for lots of little lakes"
	NiTextOut("Setting Plot Types (Python Lakes) ...")
	global fractal_world
	fractal_world = LakesFractalWorld()
	fractal_world.initFractal(continent_grain = 3, rift_grain = -1, has_center_rift = False, invert_heights = True)
	plot_types = fractal_world.generatePlotTypes(water_percent = 10)
	return plot_types

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Lakes) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Lakes) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0
