#
#	FILE:	 Continents.py
#	AUTHOR:  Soren Johnson
#	PURPOSE: Global map script - Civ4's default map script
#-----------------------------------------------------------------------------
#	Copyright (c) 2004, 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import random
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_FRACTAL_DESCR"

resourcesToBalance = ('BONUS_IRON', 'BONUS_HORSE', 'BONUS_COPPER', 'BONUS_OIL', 'BONUS_MARBLE', 'BONUS_STONE', 'BONUS_IVORY', 'BONUS_PIG', 'BONUS_RICE', 'BONUS_SHEEP', 'BONUS_GOLD', 'BONUS_WHEAT')
resourcesToEliminate = ('BONUS_WINE', 'BONUS_SILVER')

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Fractal) ...")
	fractal_world = FractalWorld()
	fractal_world.initFractal(rift_grain = -1, has_center_rift = False, polar = True)
	return fractal_world.generatePlotTypes()

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Fractal) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Fractal) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def normalizeAddExtras():
	gc = CyGlobalContext()
	map = CyMap()
	for i in range(gc.getMAX_CIV_PLAYERS()):
		if (gc.getPlayer(i).isAlive()):
			start_plot = gc.getPlayer(i).getStartingPlot() # returns a CyPlot
			startx, starty = start_plot.getX(), start_plot.getY()
			
			plots = [] # build a list of the plots near the starting plot
			for dx in range(-2,4):
				for dy in range(-2,4):
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
					if (type_string not in resources_placed) and (type_string in resourcesToBalance):
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
