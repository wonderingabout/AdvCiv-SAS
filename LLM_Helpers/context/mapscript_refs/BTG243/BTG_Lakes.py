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
import random#2.22l

gc = CyGlobalContext()

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_LAKES_DESCR"
	
def getDescriptionTitle():
	return "A very popular BTS multiplayer map which has good starting balance for two teams and varities of land available"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return "There is a popular option in competitive teamers to have the starting location 'separated', in 5v5, 3 on top and 2 on bottom for each team"

def getDescriptionSecond():#Script tip : (on TOP)
	return ""	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "This BTG option offers the possibilities to remove the tundra and ice, easier to consider toroidal with this"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Game will be relatively short and violent has proximity is high and land though to manage to get to high population, it will be hard to advance far in the tech path"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Immediate impact traits are strong, AGGRESSIVE and EXPANSIVE leading the way"		

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 9

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"Water Content",
		3:	"Land Color",
		4:	"Extreme Latitudes",
		5:	"BTG Type of Forest",
		6:  "Adjust Grid Size",
		7:  "BTG Spectator Notes",
		8:	"Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	3,
		2:	4,
		3:	3,
		4:	2,
		5:	2,
		6:	2,
		7:	2,
		8:	1
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
			1: "TXT_KEY_MAP_BALANCED",
			2: "UU Madness Resources - Lots of extras"
			},
		2:	{
			0: "Normal",
			1: "Artic Frozen",
			2: "Ice - Some",
			3: "Ice - All"
			},
		3:	{
			0: "Normal Color",
			1: "Green Land",
			2: "Super Green"
			},	
		4:	{
			0: "Normal Color - Tundra and Ice",
			1: "Green Land"
			},		
		5:	{
			0: "Normal Forest",
			1: "Palm Forest everywhere"
			},		
		6:	{
			0: "Normal Lake Size",
			1: "Slightly Larger Size than default"
			},			
		7:	{
			0: "Solo - 1 Spectator good in any slot",
            1:"Team - 1 Spectator good in any slot"
			},	
		8:	{
			0: "Penny for Beyon The Game - Works for BTS, BTG Options have no effect"		
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:  2,
		2:  0,
		3:	0,
		4:	0,
		5:	0,
		6:	1,
		7:	0,
		8:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:  false,
		2:  false,
		3:	false,
		4:	false,
		5:	false,
		6:	false,
		7:	false,
		8:	false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)

def normalizeAddExtras():
	if (CyMap().getCustomMapOption(1) == 1 or CyMap().getCustomMapOption(1) == 2):
		balancer.normalizeAddExtras()	
			
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))	
	if (CyMap().getCustomMapOption(2) == 1):				
		BTPFreezeOcean(True,33,True)			
	elif (CyMap().getCustomMapOption(2) == 2):
		BTPFreezeOcean(False,33,True)			
	elif (CyMap().getCustomMapOption(2) == 3):
		BTPFreezeOcean(False,100,True)			
		
	#2.35 for UU Madness - Whole new block
	if CyMap().getCustomMapOption(1) == 2:
		iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		everyPlayer = iPlayers
		everyTwoPlayer = max(1,iPlayers/2)
		everyThreePlayer = max(1,iPlayers/3)
		everyFourPlayer = max(1,iPlayers/4)#2.34	
	
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
		if isBTPon:
			iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_POTATO"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,False,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
		#Balanced around player
		
		
		#Center Unique
		'''CvMapGeneratorUtil.BTPMapUtil().BTPresourceFromCenter(1,2+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))'''
		
		#1 Extra Elephant if 2 players (so 2 basically)
		if iPlayers == 2 or iPlayers == 3:
		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),1,0,-1)
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_RICE"),1,0,-1)			
				
		#Center by player size
		#for i in range(everyFourPlayer):
		if isBTPon:
			for i in range(everyThreePlayer):
			
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SALT"),1,0,-1)
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_TEA"),1,0,-1)
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_OLIVES"),1,0,-1)
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_DIAMOND"),1,0,-1)
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,-1)			
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,-1)			
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,-1)				
				
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_NICKEL"),1,0,-1)				
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_LEAD"),1,0,-1)				
					
		for i in range(everyThreePlayer):

			if isBTPon:
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_AMBER"),1,0,-1)	
				
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"),1,0,-1)	
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_STONE"),1,0,-1)							
			
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),True,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),1,0,-1)
			
			for j in range(2):#This map needs more
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),True,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),1,0,-1)	
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),True,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),1,0,-1)	
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),True,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),1,0,-1)	
				BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),True,CyGlobalContext().getInfoTypeForString("BONUS_WHALE"),1,0,-1)	
						
					

			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),1,0,-1)	
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),1,0,-1)	
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),1,0,-1)				
		
			
		#for i in range(everyTwoPlayer):
		for i in range(everyThreePlayer):
		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),1,0,-1)		
			
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_WINE"),1,0,-1)	
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SILK"),1,0,-1)		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),1,0,-1)		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_SUGAR"),1,0,-1)		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),1,0,-1)		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_INCENSE"),1,0,-1)		

			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),1,0,-1)	
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_FUR"),1,0,-1)		
			BTPResourceInBox(0,CyMap().getGridWidth(),0,CyMap().getGridHeight(),False,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),1,0,-1)					

	
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.21z - #2.22
	if isBTPon :
		if (type_string in balancer.newResourcesBTP):
			return None		

	if (CyMap().getCustomMapOption(1) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly

	if ( CyMap().getCustomMapOption(1) == 2):
		if (type_string in balancer.resourcesToBalance):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def getGridSize(argsList):
	"Because this is such a land-heavy map, override getGridSize() to make the map smaller"
	
	if (CyMap().getCustomMapOption(6) == 0):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(6,4),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,5),
			WorldSizeTypes.WORLDSIZE_SMALL:		(10,6),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(13,8),
			WorldSizeTypes.WORLDSIZE_LARGE:		(16,10),
			WorldSizeTypes.WORLDSIZE_HUGE:		(21,13)
		}
		
	if (CyMap().getCustomMapOption(6) == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,5),
			WorldSizeTypes.WORLDSIZE_TINY:		(9,6),
			WorldSizeTypes.WORLDSIZE_SMALL:		(11,7),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(14,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(17,11),
			WorldSizeTypes.WORLDSIZE_HUGE:		(22,14)
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
	
	#2.22
	if CyMap().getCustomMapOption(3) == 1:#green case
		terraingen.__init__(iDesertPercent=15,iPlainsPercent=0)
	elif CyMap().getCustomMapOption(3) == 2:#super green
		terraingen.__init__(iDesertPercent=0, iPlainsPercent=0)	
	
	terrainTypes = terraingen.generateTerrain()
	
	if CyMap().getCustomMapOption(4) > 0:
		# Eliminate snow and tundra completely (they still get placed sometimes at extreme latitudes)
		for i in range(len(terrainTypes)):
			if (terrainTypes[i] == terraingen.terrainIce) or (terrainTypes[i] == terraingen.terrainTundra):
				terrainTypes[i] = terraingen.terrainGrass		
	
	
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Lakes) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def beforeGeneration():#2.22
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False

def startHumansOnSameTile():#2.22

	if isBTPon :
		if (CyMap().getCustomMapOption(5) > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)
			
	CyPythonMgr().allowDefaultImpl()
		
		
		
		
def BTPFreezeOcean(bFrozen,iProbaSnow,bAlsoCoast):
	
	pPlotOceanList = []
	for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				p = CyMap().plot(x,y)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_OCEAN")):
					pPlotOceanList.append(p)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST") and bAlsoCoast):#2.22l
					pPlotOceanList.append(p)
					
	for p in pPlotOceanList:
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= iProbaSnow:	
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
			if (bFrozen):
				p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)			

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