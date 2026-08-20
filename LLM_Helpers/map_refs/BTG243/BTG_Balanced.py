#
#	FILE:	 Balanced.py
#	AUTHOR:  Andy Szybalski
#	PURPOSE: Global map script - Solid pangaea, balanced strategic resources.
#-----------------------------------------------------------------------------
#	Copyright (c) 2004, 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import random
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import HintedWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_BALANCED_DESCR"
	
def getDescriptionTitle():
	return "A BTS fractal map which has only 1 fractal so produces 1 big piece of land, more or less round with strong latitude component for land type"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return ""	
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Traditional map for 3v3 Future Start, also good for ancient / Classical start for a bit of variation and something more randome"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""		

def getNumCustomMapOptions():
	return 9

def getNumHiddenCustomMapOptions():
	return 1

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:	"Starting Units",
		2:	"BTG Type of Forest",
		3:	"BTG Resources",
		4:	"1 notch Bigger",
		5:	"BTG Music",
		6:  "BTG Spectator Notes",
		7:	"Notes",
		8:	"Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text	
	
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2,
		2:	2,
		3:	1,
		4:	3,
		5:	3,
		6:	2,
		7:	1,
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
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},	
		2:	{
			0: "Normal Forest",
			1: "Palm Forest everywhere"
			},				
		3:	{
			0: "Yes - Normal Distribution"
			},
		4:	{
			0: "No - Normal Size",
            1: "Yes - 1 notch bigger",
			2: "Yes - 2 notches bigger"
			},
		5:	{
			0: "Normal",
			1: "Age of Agriculture",
			2: "Age of Robotics"
			},					
		6:	{
			0: "Solo - 1 Spectator good in any slot",
            1: "Team - 1 Spectator good in any slot"
			},	
		7:	{
			0: "Size - Suggest 2 notches bigger for Futur and CTON"		
			},				
		8:	{
			0: "Penny for BTG - Works for BTS, BTG Options have no effect"		
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	0,
		2:	0,
		3:	0,
		4:	0,
		5:	2,
		6:	0,
		7:	0,
		8:	0
		}
	return option_defaults[iOption]
	
def isRandomCustomMapOption(argsList):
	return false

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)

def getTopLatitude():
	return 70
def getBottomLatitude():
	return -70

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Balanced) ...")
	global hinted_world
	hinted_world = HintedWorld(16,8)

	mapRand = CyGlobalContext().getGame().getMapRand()

	numBlocks = hinted_world.w * hinted_world.h
	numBlocksLand = int(numBlocks*0.25)
	cont = hinted_world.addContinent(numBlocksLand,mapRand.get(5, "Generate Plot Types PYTHON")+4,mapRand.get(3, "Generate Plot Types PYTHON")+2)
	if not cont:
		print "Couldn't create continent! Reverting to C implementation."
		CyPythonMgr().allowDefaultImpl()
	else:		
		for x in range(hinted_world.w):
			for y in (0, hinted_world.h - 1):
				hinted_world.setValue(x,y, 1) # force ocean at poles
		hinted_world.buildAllContinents()
		return hinted_world.generatePlotTypes(shift_plot_types=True)

# subclass TerrainGenerator to eliminate arctic, equatorial latitudes

class BTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
		lat = CvMapGeneratorUtil.TerrainGenerator.getLatitudeAtPlot(self, iX, iY) 	# range [0,1]
		lat = 0.05 + 0.75*lat				# range [0.05, 0.75]
		return lat

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Balanced) ...")
	terraingen = BTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

# subclass FeatureGenerator to eliminate arctic, equatorial latitudes
	
class BFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
		lat = CvMapGeneratorUtil.FeatureGenerator.getLatitudeAtPlot(self, iX, iY) 	# range [0,1]
		lat = 0.05 + 0.75*lat				# range [0.05, 0.75]
		return lat
	
def addFeatures():
	NiTextOut("Adding Features (Python Balanced) ...")
	featuregen = BFeatureGenerator()
	featuregen.addFeatures()
	return 0

def normalizeAddExtras():
	balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride
	
def beforeGeneration():#2.22
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False

def addBonusType(argsList):#2.21z
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	if isBTPon: 
		if not CyGlobalContext().getGame().isOption(GameOptionTypes.GAMEOPTION_NEW_STRATEGIC_RESOURCE):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
	
	if (not balancer.isSkipBonus(iBonusType)):
		CyPythonMgr().allowDefaultImpl() 

		
def startHumansOnSameTile():#2.22

	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon :
		if (CyMap().getCustomMapOption(2) > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)
			
	if (CyMap().getCustomMapOption(1) == 1):
		return True	


def BTGSong():

	if (CyMap().getCustomMapOption(5) > 0):
		CyGame().setMapTriggerSound(CyMap().getCustomMapOption(5))
		return 1 # Has to be 1 to activate	
	else:
		return 0		
		
		
def findStartingPlot(argsList):#2.22 testing for spectator, this wasn't there before

	'''if isBTPon:#2.22
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		if iNumSpectators > 0:
			[playerID] = argsList
			CvMapGeneratorUtil.findStartingPlot(playerID)
		else:
			CyPythonMgr().allowDefaultImpl()
	else:'''
	CyPythonMgr().allowDefaultImpl()#of all the tries, the default is still the best layout	


def getGridSize(argsList):#2.26 - doesn't exist in normal balanced map but I'll just use the same as XML file
	"Override Grid Size function to make the maps square."
	
	if (CyMap().getCustomMapOption(4) == 0):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(10,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(13,8),
			WorldSizeTypes.WORLDSIZE_SMALL:		(16,10),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(21,13),
			WorldSizeTypes.WORLDSIZE_LARGE:		(26,16),
			WorldSizeTypes.WORLDSIZE_HUGE:		(32,20)
		}
		
	if (CyMap().getCustomMapOption(4) == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(11,7),
			WorldSizeTypes.WORLDSIZE_TINY:		(14,9),
			WorldSizeTypes.WORLDSIZE_SMALL:		(18,11),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(23,14),
			WorldSizeTypes.WORLDSIZE_LARGE:		(29,18),
			WorldSizeTypes.WORLDSIZE_HUGE:		(35,21)
		}	
	
	if (CyMap().getCustomMapOption(4) == 2):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(12,8),
			WorldSizeTypes.WORLDSIZE_TINY:		(15,10),
			WorldSizeTypes.WORLDSIZE_SMALL:		(20,12),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(25,15),
			WorldSizeTypes.WORLDSIZE_LARGE:		(32,20),
			WorldSizeTypes.WORLDSIZE_HUGE:		(38,22)
		}		

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]