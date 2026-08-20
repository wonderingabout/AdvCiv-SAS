#
#	FILE:	 Shuffle.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - Return of Civ3's "random" map option.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005, 2006 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

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

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_SHUFFLE_DESCR"
	
def getDescriptionTitle():
	return "The map is based on the fractal engine and will usually fall in one of the categories : "

def getDescriptionTitleTwo():
	return "1 fractal (much like balanced map), 2 fractal with a rift (2 continents) or more fractals and a more sinuous type lof land, 3 fractal for patchy island and more rarely many very small islands"

def getDescriptionMain():
	return "A map used a lot for 'Random' type of games"

def getDescriptionSecond():#Script tip : (on TOP)
	return ""	
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Ideal for Random/Random and teamer, used a lot for 2v2"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""		
	
def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 7

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"BTG New Resources",
		3:	"Dice Preset Type",
		4:  "Preset Selection",
		5:	"BTG Spectator Notes",
		6:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2,
		2:	2,
		3:	2,
		4:	8,
		5:	2,
		6:	1
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
			},
		2:	{
			0: "No",
			1: "Yes - Normal"
			},
		3:	{
			0: "Default - Normal Shuffle",
			1: "Select - Within  presets"
			},	
		4:	{
			0: "1 - 1 grain - 1 Large Landmass",
			1: "2 - 2 grains and rift - 2 Continents",
			2: "3 - 3 Grains  - Middle Size Islands",			
			3: "4 - 4 Grains - Archipelago",
			4: "5 - 2 Grains no rift - Largish continent(s)",
			5: "6 - 1 grain - 1 Large Landmass",
			6: "7 - 2 grains and rift - 2 Continents",
			7: "8 - 3 Grains  - Middle Size Islands",		
			},				
		5:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in FIRST slot"
			},	
		6:	{
			0: "Penny for Beyond the Game - Works for BTS, BTG Options have no effect"		
			}				
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:  1,
		2:	0,
		3:	0,
		4:	-1,
		5:	0,
		6:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	False,
		1:  False,
		2:	False,
		3:  False,
		4:  True,
		5:	False,
		6:	False
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)
	
def beforeGeneration():#2.22
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	

def normalizeAddExtras():
	if (CyMap().getCustomMapOption(1) == 1):
		balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	if isBTPon:
		if (CyMap().getCustomMapOption(2) == 0):
			if (type_string in balancer.newResourcesBTP) or (type_string in balancer.newStrategicBTP):
				return None

	if (CyMap().getCustomMapOption(1) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Shuffle) ...")
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	fractal_world = FractalWorld()
	grainRoll = 1 + dice.get(8, "Fractal Grain - Shuffle PYTHON")

	#2.32 Superseed with option selection
	if (CyMap().getCustomMapOption(3) == 1):
		grainRoll = 1 + CyMap().getCustomMapOption(4)

	if grainRoll > 5: grainRoll -= 5
	if grainRoll == 2:
		fractal_world.initFractal(polar = True)
		return fractal_world.generatePlotTypes(water_percent=75)
	else:
		if grainRoll == 5: grainRoll -= 3
		fractal_world.initFractal(continent_grain = grainRoll, rift_grain = -1, has_center_rift = False, polar = True)
		return fractal_world.generatePlotTypes()

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Shuffle) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Shuffle) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0
