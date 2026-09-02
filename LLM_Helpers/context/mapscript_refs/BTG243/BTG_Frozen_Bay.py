#
#	FILE:	 Inland_Sea.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Soren Johnson, Andy Szybalski
#	PURPOSE: Regional map script - Loosely simulates a Mediterranean type
#	         temperate zone with civs ringing a central sea.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
import random#2.18
from CvMapGeneratorUtil import HintedWorld
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()


hinted_world = None

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "TXT_KEY_MAP_SCRIPT_INLAND_SEA_DESCR"
	
def getDescriptionTitle():
	return "A copy of Inland Sea but with a different spin on resource placement, making it different to micromanage the land"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "Canada makes the land very focused on Tundra but with lots of deers, Afghanistan makes it very based on sugar and salt"
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Central Sea let's you put back the normal inland sea, but by default it's all frozen with 2 chains of mountains in middle"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Best suited for 3v3 Medieval and Renaissance Start, or CTON."

def getDescriptionBalance():#Balance : (at the bottom)"
	return "AGRICULTURAL has to be banned because of Deers"		

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 13

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES",
		2:	"Country Type",		
		3:	"Starting Position",
		4:  "Central Sea",
		5:	"Central Mountain",	
		6:	"BTG Resources",		
		7:	"BTG Forest Type",
		8:	"Starting Units",
		9:	"BTG Spectator Notes",
		10:	"Notes",
		11:	"Notes Balance",
		12:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	1,
		1:	3,#2.17
		2:	3,
		3:	4,
		4:  4,
		5:	2,
		6:	3,
		7:	5,
		8:	2,
		9:	1,
		10:	1,
		11:	1,
		12:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			},
		1:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "Balanced - Including Marble",
			},
		2:	{
			0: "Canada",
			1: "Afghanistan",
			2: "Hudson Bay",#2.36
			},			
		3:	{
			0: "Any Template",
			1: "Template 1 - < Shape [6 or 8 players]",
			2: "Template 2 - L Shape [6 or 8 players]",
			3: "Template 3 - Top vs Bottom [3v3 or 4v4]"
			},		
		4:	{
			0: "Water",
			1: "Snow",
			2: "Salted Lake",
			3: "Country Depending"
			},		
		5:	{
			0: "No",
			1: "Yes if not water"
			},	
		6:	{
			0: "No",
			1: "Yes - Normal distribution",
			2: "Yes - Amber & Sulphur on tile in center"
			},				
		7:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},	
		8:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},					
		9:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"		
			},
		10:	{
			0: "Inland Sea which changed tile colors"			
			},
		11:	{
			0: "AGRICULTURAL Leader should be banned"			
			},			
		12:	{
			0: "Penny for BTG - Works for BTS, BTG Options have no effect"		
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:  2,
		2:	2,
		3:	0,
		4:	3,
		5:	1,
		6:	2,
		7:	0,
		8:	0,
		9:	0,
		10:	0,
		11:	0,
		12:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:  false,
		2:	true,
		3:	false,
		4:	true,
		5:	true,
		6:	true,
		7:	true,
		8:	false,
		9:	false,
		10:	false,
		11:	false,
		12:	false
		}
	return option_random[iOption]

def getWrapX():
	return False
	
def getWrapY():
	return False

def normalizeAddExtras():
	if (CyMap().getCustomMapOption(1) == 1 or CyMap().getCustomMapOption(1) == 2):
		balancer.normalizeAddExtras()
		
	#2.18 Moved here, last thing to do
	if isBTPon:				
			
		if (CyMap().getCustomMapOption(6) == 2):
			
			p = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*50/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))		
			p.setFeatureType(-1, -1)	
		
		if (CyMap().getCustomMapOption(6) == 2):

			p = CyMap().plot(CyMap().getGridWidth()*50/100 -4,CyMap().getGridHeight()*50/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))		
			p.setFeatureType(-1, -1)		

			p = CyMap().plot(CyMap().getGridWidth()*50/100 +3,CyMap().getGridHeight()*50/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))		
			p.setFeatureType(-1, -1)				

	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride
	

def addBonusType(argsList):

	

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.21y
	if isBTPon:
		if (CyMap().getCustomMapOption(6) == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
				
		if (CyMap().getCustomMapOption(6) == 2):#exclude the strategic ones because strat is function above (and commo is okay)
			if (type_string in balancer.newStrategicBTP):
				return None			

	if (CyMap().getCustomMapOption(1) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
			
	if (CyMap().getCustomMapOption(1) == 2):
		BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM')#2.17
		#BTPresourcesToEliminate = ('')#2.17	
		#if (type_string in BTPResourcesToBalance) or (type_string in BTPResourcesToEliminate):
		if (type_string in BTPResourcesToBalance):#2.18 since the list is empty, simplify
			return None # don't place any of this bonus randomly			
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def beforeGeneration():
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()
	
	global isBTPon#2.22
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	

	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 6, 4, 3, 2, 2, 2, 4, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1]
	
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
	#2.15
	if (CyMap().getCustomMapOption(3) == 1):
		iTemplateRoll = 0#overrides
	if (CyMap().getCustomMapOption(3) == 2 or CyMap().getCustomMapOption(3) == 3):
		iTemplateRoll = min(1,iNumTemplates-1)#overrides- Minus 1 because the real number of a template start at 0
	
	# Set variance for start plots according to map size vs number of players.
	map_size = CyMap().getWorldSize()
	sizevalues = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(2, 3),
		WorldSizeTypes.WORLDSIZE_TINY:		(2, 3),
		WorldSizeTypes.WORLDSIZE_SMALL:		(3, 4),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(4, 7),
		WorldSizeTypes.WORLDSIZE_LARGE:		(5, 10),
		WorldSizeTypes.WORLDSIZE_HUGE:		(6, 15)
		}
	(threeVar, twoVar) = sizevalues[map_size]
	if iPlayers <= threeVar:
		fVar = 3
	elif iPlayers <= twoVar:
		fVar = 2
	else:
		fVar = 1
	
	# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
	templates = {(1,0): {0: [0.5, 0.5, int(0.5 * iW), int(0.5 * iH)]},
	             (2,0): {0: [0.1, 0.5, fVar, int(0.5 * iH)],
	                     1: [0.9, 0.5, fVar, int(0.5 * iH)]},
	             (2,1): {0: [0.5, 0.167, int(0.3 * iW), fVar],
	                     1: [0.5, 0.833, int(0.3 * iW), fVar]},
	             (2,2): {0: [0.3, 0.167, int(0.3 * iW), fVar],
	                     1: [0.7, 0.833, int(0.3 * iW), fVar]},
	             (2,3): {0: [0.7, 0.167, int(0.3 * iW), fVar],
	                     1: [0.3, 0.833, int(0.3 * iW), fVar]},
	             (2,4): {0: [0.2, 0.333, int(0.2 * iW), int(0.333 * iH)],
	                     1: [0.8, 0.667, int(0.2 * iW), int(0.333 * iH)]},
	             (2,5): {0: [0.8, 0.333, int(0.2 * iW), int(0.333 * iH)],
	                     1: [0.2, 0.677, int(0.2 * iW), int(0.333 * iH)]},
	             (3,0): {0: [0.1, 0.5, fVar, fVar],
	                     1: [0.7, 0.167, fVar, fVar],
	                     2: [0.7, 0.833, fVar, fVar]},
	             (3,1): {0: [0.9, 0.5, fVar, fVar],
	                     1: [0.3, 0.167, fVar, fVar],
	                     2: [0.3, 0.833, fVar, fVar]},
	             (3,2): {0: [0.5, 0.167, fVar, fVar],
	                     1: [0.1, 0.833, fVar, fVar],
	                     2: [0.9, 0.833, fVar, fVar]},
	             (3,3): {0: [0.5, 0.833, fVar, fVar],
	                     1: [0.1, 0.167, fVar, fVar],
	                     2: [0.9, 0.167, fVar, fVar]},
	             (4,0): {0: [0.1, 0.5, fVar, fVar],
	                     1: [0.5, 0.167, fVar, fVar],
	                     2: [0.9, 0.5, fVar, fVar],
	                     3: [0.5, 0.833, fVar, fVar]},
	             (4,1): {0: [0.1, 0.167, fVar, fVar],
	                     1: [0.7, 0.167, fVar, fVar],
	                     2: [0.9, 0.833, fVar, fVar],
	                     3: [0.3, 0.833, fVar, fVar]},
	             (4,2): {0: [0.1, 0.833, fVar, fVar],
	                     1: [0.7, 0.833, fVar, fVar],
	                     2: [0.9, 0.167, fVar, fVar],
	                     3: [0.3, 0.167, fVar, fVar]},
	             (5,0): {0: [0.5, 0.167, fVar, fVar],
	                     1: [0.125, 0.333, fVar, fVar],
	                     2: [0.25, 0.833, fVar, fVar],
	                     3: [0.75, 0.833, fVar, fVar],
	                     4: [0.875, 0.333, fVar, fVar]},
	             (5,1): {0: [0.5, 0.833, fVar, fVar],
	                     1: [0.125, 0.667, fVar, fVar],
	                     2: [0.25, 0.167, fVar, fVar],
	                     3: [0.75, 0.167, fVar, fVar],
	                     4: [0.875, 0.667, fVar, fVar]},
	             (6,0): {0: [0.1, 0.5, fVar, fVar],
	                     1: [0.3, 0.167, fVar, fVar],
	                     2: [0.7, 0.167, fVar, fVar],
	                     3: [0.9, 0.5, fVar, fVar],
	                     4: [0.7, 0.833, fVar, fVar],
	                     5: [0.3, 0.833, fVar, fVar]},
	             (6,1): {0: [0.1, 0.167, fVar, fVar],
	                     1: [0.5, 0.167, fVar, fVar],
	                     2: [0.9, 0.167, fVar, fVar],
	                     3: [0.9, 0.833, fVar, fVar],
	                     4: [0.5, 0.833, fVar, fVar],
	                     5: [0.1, 0.833, fVar, fVar]},
	             (7,0): {0: [0.1, 0.5, fVar, fVar],
	                     1: [0.2, 0.125, fVar, fVar],
	                     2: [0.6, 0.125, fVar, fVar],
	                     3: [0.9, 0.25, fVar, fVar],
	                     4: [0.9, 0.75, fVar, fVar],
	                     5: [0.6, 0.875, fVar, fVar],
	                     6: [0.2, 0.875, fVar, fVar]},
	             (7,1): {0: [0.9, 0.5, fVar, fVar],
	                     1: [0.8, 0.125, fVar, fVar],
	                     2: [0.4, 0.125, fVar, fVar],
	                     3: [0.1, 0.25, fVar, fVar],
	                     4: [0.1, 0.75, fVar, fVar],
	                     5: [0.4, 0.875, fVar, fVar],
	                     6: [0.8, 0.875, fVar, fVar]},
	             (8,0): {0: [0.583, 0.125, fVar, fVar],
	                     1: [0.25, 0.125, fVar, fVar],
	                     2: [0.083, 0.375, fVar, fVar],
	                     3: [0.083, 0.875, fVar, fVar],
	                     4: [0.417, 0.875, fVar, fVar],
	                     5: [0.75, 0.875, fVar, fVar],
	                     6: [0.917, 0.625, fVar, fVar],
	                     7: [0.917, 0.125, fVar, fVar]},
	             (8,1): {0: [0.417, 0.125, fVar, fVar],
	                     1: [0.083, 0.125, fVar, fVar],
	                     2: [0.083, 0.625, fVar, fVar],
	                     3: [0.25, 0.875, fVar, fVar],
	                     4: [0.583, 0.875, fVar, fVar],
	                     5: [0.917, 0.875, fVar, fVar],
	                     6: [0.917, 0.375, fVar, fVar],
	                     7: [0.75, 0.125, fVar, fVar]},
	             (8,2): {0: [0.1, 0.5, fVar, fVar],
	                     1: [0.2, 0.125, fVar, fVar],
	                     2: [0.5, 0.125, fVar, fVar],
	                     3: [0.8, 0.125, fVar, fVar],
	                     4: [0.9, 0.5, fVar, fVar],
	                     5: [0.8, 0.875, fVar, fVar],
	                     6: [0.5, 0.875, fVar, fVar],
	                     7: [0.2, 0.875, fVar, fVar]},
	             (8,3): {0: [0.1, 0.75, fVar, fVar],
	                     1: [0.1, 0.25, fVar, fVar],
	                     2: [0.333, 0.125, fVar, fVar],
	                     3: [0.667, 0.125, fVar, fVar],
	                     4: [0.9, 0.25, fVar, fVar],
	                     5: [0.9, 0.75, fVar, fVar],
	                     6: [0.667, 0.875, fVar, fVar],
	                     7: [0.333, 0.875, fVar, fVar]},
	             (9,0): {0: [0.833, 0.15, fVar, fVar],
	                     1: [0.5, 0.15, fVar, fVar],
	                     2: [0.167, 0.15, fVar, fVar],
	                     3: [0.08, 0.412, fVar, fVar],
	                     4: [0.08, 0.775, fVar, fVar],
	                     5: [0.35, 0.85, fVar, fVar],
	                     6: [0.65, 0.85, fVar, fVar],
	                     7: [0.92, 0.775, fVar, fVar],
	                     8: [0.92, 0.412, fVar, fVar]},
	             (9,1): {0: [0.833, 0.85, fVar, fVar],
	                     1: [0.5, 0.85, fVar, fVar],
	                     2: [0.167, 0.85, fVar, fVar],
	                     3: [0.08, 0.588, fVar, fVar],
	                     4: [0.08, 0.225, fVar, fVar],
	                     5: [0.35, 0.15, fVar, fVar],
	                     6: [0.65, 0.15, fVar, fVar],
	                     7: [0.92, 0.225, fVar, fVar],
	                     8: [0.92, 0.588, fVar, fVar]},
	             (10,0): {0: [0.875, 0.15, fVar, fVar],
	                      1: [0.625, 0.15, fVar, fVar],
	                      2: [0.375, 0.15, fVar, fVar],
	                      3: [0.125, 0.15, fVar, fVar],
	                      4: [0.08, 0.5, fVar, fVar],
	                      5: [0.125, 0.85, fVar, fVar],
	                      6: [0.375, 0.85, fVar, fVar],
	                      7: [0.625, 0.85, fVar, fVar],
	                      8: [0.875, 0.85, fVar, fVar],
	                      9: [0.92, 0.5, fVar, fVar]},
	             (10,1): {0: [0.75, 0.15, fVar, fVar],
	                      1: [0.5, 0.15, fVar, fVar],
	                      2: [0.25, 0.15, fVar, fVar],
	                      3: [0.08, 0.33, fVar, fVar],
	                      4: [0.08, 0.67, fVar, fVar],
	                      5: [0.25, 0.85, fVar, fVar],
	                      6: [0.5, 0.85, fVar, fVar],
	                      7: [0.75, 0.85, fVar, fVar],
	                      8: [0.92, 0.67, fVar, fVar],
	                      9: [0.92, 0.33, fVar, fVar]},
	             (11,0): {0: [0.875, 0.15, fVar, fVar],
	                      1: [0.625, 0.15, fVar, fVar],
	                      2: [0.375, 0.15, fVar, fVar],
	                      3: [0.125, 0.15, fVar, fVar],
	                      4: [0.08, 0.45, fVar, fVar],
	                      5: [0.08, 0.75, fVar, fVar],
	                      6: [0.28, 0.85, fVar, fVar],
	                      7: [0.5, 0.85, fVar, fVar],
	                      8: [0.72, 0.85, fVar, fVar],
	                      9: [0.92, 0.75, fVar, fVar],
	                      10: [0.92, 0.45, fVar, fVar]},
	             (11,1): {0: [0.875, 0.85, fVar, fVar],
	                      1: [0.625, 0.85, fVar, fVar],
	                      2: [0.375, 0.85, fVar, fVar],
	                      3: [0.125, 0.85, fVar, fVar],
	                      4: [0.08, 0.55, fVar, fVar],
	                      5: [0.08, 0.25, fVar, fVar],
	                      6: [0.28, 0.15, fVar, fVar],
	                      7: [0.5, 0.15, fVar, fVar],
	                      8: [0.72, 0.15, fVar, fVar],
	                      9: [0.92, 0.25, fVar, fVar],
	                      10: [0.92, 0.55, fVar, fVar]},
	             (12,0): {0: [0.7, 0.15, fVar, fVar],
	                      1: [0.5, 0.15, fVar, fVar],
	                      2: [0.3, 0.15, fVar, fVar],
	                      3: [0.1, 0.15, fVar, fVar],
	                      4: [0.08, 0.5, fVar, fVar],
	                      5: [0.1, 0.85, fVar, fVar],
	                      6: [0.3, 0.85, fVar, fVar],
	                      7: [0.5, 0.85, fVar, fVar],
	                      8: [0.7, 0.85, fVar, fVar],
	                      9: [0.9, 0.85, fVar, fVar],
	                      10: [0.92, 0.5, fVar, fVar],
	                      11: [0.9, 0.15, fVar, fVar]},
	             (13,0): {0: [0.7, 0.125, fVar, fVar],
	                      1: [0.5, 0.125, fVar, fVar],
	                      2: [0.3, 0.125, fVar, fVar],
	                      3: [0.1, 0.125, fVar, fVar],
	                      4: [0.08, 0.425, fVar, fVar],
	                      5: [0.08, 0.725, fVar, fVar],
	                      6: [0.2, 0.875, fVar, fVar],
	                      7: [0.4, 0.875, fVar, fVar],
	                      8: [0.6, 0.875, fVar, fVar],
	                      9: [0.8, 0.875, fVar, fVar],
	                      10: [0.92, 0.725, fVar, fVar],
	                      11: [0.92, 0.425, fVar, fVar],
	                      12: [0.9, 0.125, fVar, fVar]},
	             (13,1): {0: [0.7, 0.875, fVar, fVar],
	                      1: [0.5, 0.875, fVar, fVar],
	                      2: [0.3, 0.875, fVar, fVar],
	                      3: [0.1, 0.875, fVar, fVar],
	                      4: [0.08, 0.575, fVar, fVar],
	                      5: [0.08, 0.275, fVar, fVar],
	                      6: [0.2, 0.125, fVar, fVar],
	                      7: [0.4, 0.125, fVar, fVar],
	                      8: [0.6, 0.125, fVar, fVar],
	                      9: [0.8, 0.125, fVar, fVar],
	                      10: [0.92, 0.275, fVar, fVar],
	                      11: [0.92, 0.575, fVar, fVar],
	                      12: [0.9, 0.875, fVar, fVar]},
	             (14,0): {0: [0.7, 0.125, fVar, fVar],
	                      1: [0.5, 0.125, fVar, fVar],
	                      2: [0.3, 0.125, fVar, fVar],
	                      3: [0.1, 0.125, fVar, fVar],
	                      4: [0.08, 0.375, fVar, fVar],
	                      5: [0.08, 0.625, fVar, fVar],
	                      6: [0.1, 0.875, fVar, fVar],
	                      7: [0.3, 0.875, fVar, fVar],
	                      8: [0.5, 0.875, fVar, fVar],
	                      9: [0.7, 0.875, fVar, fVar],
	                      10: [0.9, 0.875, fVar, fVar],
	                      11: [0.92, 0.625, fVar, fVar],
	                      12: [0.92, 0.375, fVar, fVar],
	                      13: [0.9, 0.125, fVar, fVar]},
	             (15,0): {0: [0.583, 0.125, fVar, fVar],
	                      1: [0.417, 0.125, fVar, fVar],
	                      2: [0.25, 0.125, fVar, fVar],
	                      3: [0.083, 0.125, fVar, fVar],
	                      4: [0.083, 0.4, fVar, fVar],
	                      5: [0.083, 0.65, fVar, fVar],
	                      6: [0.1, 0.9, fVar, fVar],
	                      7: [0.3, 0.875, fVar, fVar],
	                      8: [0.5, 0.875, fVar, fVar],
	                      9: [0.7, 0.875, fVar, fVar],
	                      10: [0.9, 0.9, fVar, fVar],
	                      11: [0.917, 0.65, fVar, fVar],
	                      12: [0.917, 0.4, fVar, fVar],
	                      13: [0.917, 0.125, fVar, fVar],
	                      14: [0.75, 0.125, fVar, fVar]},
	             (15,1): {0: [0.583, 0.875, fVar, fVar],
	                      1: [0.417, 0.875, fVar, fVar],
	                      2: [0.25, 0.875, fVar, fVar],
	                      3: [0.083, 0.875, fVar, fVar],
	                      4: [0.083, 0.6, fVar, fVar],
	                      5: [0.083, 0.35, fVar, fVar],
	                      6: [0.1, 0.1, fVar, fVar],
	                      7: [0.3, 0.125, fVar, fVar],
	                      8: [0.5, 0.125, fVar, fVar],
	                      9: [0.7, 0.125, fVar, fVar],
	                      10: [0.9, 0.1, fVar, fVar],
	                      11: [0.917, 0.35, fVar, fVar],
	                      12: [0.917, 0.6, fVar, fVar],
	                      13: [0.917, 0.875, fVar, fVar],
	                      14: [0.75, 0.875, fVar, fVar]},
	             (16,0): {0: [0.583, 0.125, fVar, fVar],
	                      1: [0.417, 0.125, fVar, fVar],
	                      2: [0.25, 0.125, fVar, fVar],
	                      3: [0.083, 0.125, fVar, fVar],
	                      4: [0.083, 0.375, fVar, fVar],
	                      5: [0.083, 0.625, fVar, fVar],
	                      6: [0.083, 0.875, fVar, fVar],
	                      7: [0.25, 0.875, fVar, fVar],
	                      8: [0.417, 0.875, fVar, fVar],
	                      9: [0.583, 0.875, fVar, fVar],
	                      10: [0.75, 0.875, fVar, fVar],
	                      11: [0.917, 0.875, fVar, fVar],
	                      12: [0.917, 0.625, fVar, fVar],
	                      13: [0.917, 0.375, fVar, fVar],
	                      14: [0.917, 0.125, fVar, fVar],
	                      15: [0.75, 0.125, fVar, fVar]},
	             (17,0): {0: [0.5, 0.125, fVar, fVar],
	                      1: [0.35, 0.125, fVar, fVar],
	                      2: [0.2, 0.125, fVar, fVar],
	                      3: [0.05, 0.175, fVar, fVar],
	                      4: [0.083, 0.45, fVar, fVar],
	                      5: [0.083, 0.7, fVar, fVar],
	                      6: [0.083, 0.95, fVar, fVar],
	                      7: [0.25, 0.875, fVar, fVar],
	                      8: [0.417, 0.875, fVar, fVar],
	                      9: [0.583, 0.875, fVar, fVar],
	                      10: [0.75, 0.875, fVar, fVar],
	                      11: [0.917, 0.95, fVar, fVar],
	                      12: [0.917, 0.7, fVar, fVar],
	                      13: [0.917, 0.45, fVar, fVar],
	                      14: [0.95, 0.175, fVar, fVar],
	                      15: [0.8, 0.125, fVar, fVar],
	                      16: [0.65, 0.125, fVar, fVar]},
	             (17,1): {0: [0.5, 0.875, fVar, fVar],
	                      1: [0.35, 0.875, fVar, fVar],
	                      2: [0.2, 0.875, fVar, fVar],
	                      3: [0.05, 0.825, fVar, fVar],
	                      4: [0.083, 0.65, fVar, fVar],
	                      5: [0.083, 0.3, fVar, fVar],
	                      6: [0.083, 0.05, fVar, fVar],
	                      7: [0.25, 0.125, fVar, fVar],
	                      8: [0.417, 0.125, fVar, fVar],
	                      9: [0.583, 0.125, fVar, fVar],
	                      10: [0.75, 0.125, fVar, fVar],
	                      11: [0.917, 0.05, fVar, fVar],
	                      12: [0.917, 0.3, fVar, fVar],
	                      13: [0.917, 0.65, fVar, fVar],
	                      14: [0.95, 0.825, fVar, fVar],
	                      15: [0.8, 0.875, fVar, fVar],
	                      16: [0.65, 0.875, fVar, fVar]},
	             (18,0): {0: [0.5, 0.125, fVar, fVar],
	                      1: [0.35, 0.125, fVar, fVar],
	                      2: [0.2, 0.125, fVar, fVar],
	                      3: [0.05, 0.125, fVar, fVar],
	                      4: [0.075, 0.375, fVar, fVar],
	                      5: [0.075, 0.625, fVar, fVar],
	                      6: [0.05, 0.875, fVar, fVar],
	                      7: [0.2, 0.875, fVar, fVar],
	                      8: [0.35, 0.875, fVar, fVar],
	                      9: [0.5, 0.875, fVar, fVar],
	                      10: [0.65, 0.875, fVar, fVar],
	                      11: [0.8, 0.875, fVar, fVar],
	                      12: [0.95, 0.875, fVar, fVar],
	                      13: [0.925, 0.625, fVar, fVar],
	                      14: [0.925, 0.375, fVar, fVar],
	                      15: [0.95, 0.125, fVar, fVar],
	                      16: [0.8, 0.125, fVar, fVar],
	                      17: [0.65, 0.125, fVar, fVar]}
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
	return 0

def minStartingDistanceModifier():
	numPlrs = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if numPlrs  <= 18:
		return -95
	else:
		return -50

def findStartingPlot(argsList):
	# Set up for maximum of 18 players! If more, use default implementation.
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if iPlayers > 18:
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

	getStartingPlot(playerID, isValid)
	if plotSuccess:
		return plotValue
	else:
		CyPythonMgr().allowDefaultImpl()
		return

def getStartingPlot(playerID, validFn = None):
	gc = CyGlobalContext()
	map = CyMap()
	player = gc.getPlayer(playerID)
	global plotSuccess
	global plotValue
	plotSuccess = false
	plotValue = -1

	player.AI_updateFoundValues(True)

	iRange = player.startingPlotRange()
	iPass = 0

	while (iPass < 50):
		iBestValue = 0
		pBestPlot = None
		
		for iX in range(map.getGridWidth()):
			for iY in range(map.getGridHeight()):
				if validFn != None and not validFn(playerID, iX, iY):
					continue
				pLoopPlot = map.plot(iX, iY)

				val = pLoopPlot.getFoundValue(playerID)

				if val > iBestValue:
				
					valid = True
					
					for iI in range(gc.getMAX_CIV_PLAYERS()):
						if (gc.getPlayer(iI).isAlive()):
							if (iI != playerID):
								if gc.getPlayer(iI).startingPlotWithinRange(pLoopPlot, playerID, iRange, iPass):
									valid = False
									break

					if valid:
							iBestValue = val
							pBestPlot = pLoopPlot

		if pBestPlot != None:
			plotSuccess = true
			plotValue = map.plotNum(pBestPlot.getX(), pBestPlot.getY())
			break
			
		print "player", playerID, "pass", iPass, "failed"
		
		iPass += 1

	return -1

def getTopLatitude():
	return 60
def getBottomLatitude():
	return -60

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

# Subclasses to fix the FRAC_POLAR zero row bugs.
class ISFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True, 
	                      grain_amount=3):
		# Check for changes to User Input variances.
		self.checkForOverrideDefaultUserInputVariances()
		
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, 0, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, 0, self.fracXExp, self.fracYExp)

		water_percent += self.seaLevelChange
		water_percent = min(water_percent, self.seaLevelMax)
		water_percent = max(water_percent, self.seaLevelMin)

		iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
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

class ISHintedWorld(CvMapGeneratorUtil.HintedWorld, ISFractalWorld):
	def __doInitFractal(self):
		self.shiftHintsToMap()
		
		# don't call base method, this overrides it.
		size = len(self.data)
		minExp = min(self.fracXExp, self.fracYExp)
		iGrain = None
		for i in range(minExp):
			width = (1 << (self.fracXExp - minExp + i))
			height = (1 << (self.fracYExp - minExp + i))
			if not self.iFlags & CyFractal.FracVals.FRAC_WRAP_X:
				width += 1
			if not self.iFlags & CyFractal.FracVals.FRAC_WRAP_Y:
				height += 1
			if size == width*height:
				iGrain = i
		assert(iGrain != None)
		iFlags = self.map.getMapFractalFlags()
		self.continentsFrac.fracInitHints(self.iNumPlotsX, self.iNumPlotsY, iGrain, self.mapRand, iFlags, self.data, self.fracXExp, self.fracYExp)

	def generatePlotTypes(self, water_percent=-1, shift_plot_types=False):
		for i in range(len(self.data)):
			if self.data[i] == None:
				self.data[i] = self.mapRand.get(48, "Generate Plot Types PYTHON")
		
		self.__doInitFractal()
		if (water_percent == -1):
			numPlots = len(self.data)
			numWaterPlots = 0
			for val in self.data:
				if val < 192:
					numWaterPlots += 1
			water_percent = int(100*numWaterPlots/numPlots)
		
		# Call superclass
		return ISFractalWorld.generatePlotTypes(self, water_percent, shift_plot_types)

def generatePlotTypes():
	global hinted_world
	gc = CyGlobalContext()
	map = CyMap()
	mapRand = gc.getGame().getMapRand()
	
	NiTextOut("Setting Plot Types (Python Inland Sea) ...")
	
	hinted_world = ISHintedWorld(4,2)
	area = hinted_world.w * hinted_world.h
	
	for y in range(hinted_world.h):
		for x in range(hinted_world.w):
			if x in (0, hinted_world.w-1) or y in (0, hinted_world.h-1):
				hinted_world.setValue(x, y, 200 + mapRand.get(55, "Plot Types - Inland Sea PYTHON"))
			else:
				hinted_world.setValue(x, y, 0)

	hinted_world.buildAllContinents()
	return hinted_world.generatePlotTypes()

# subclass TerrainGenerator to eliminate arctic, equatorial latitudes

class ISTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
		lat = CvMapGeneratorUtil.TerrainGenerator.getLatitudeAtPlot(self, iX, iY) 	# range [0,1]
		lat = 0.07 + 0.56*lat				# range [0.07, 0.56]
		return lat

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Inland Sea) ...")
	terraingen = ISTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

# subclass FeatureGenerator to eliminate arctic, equatorial latitudes
	
class ISFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
		lat = CvMapGeneratorUtil.FeatureGenerator.getLatitudeAtPlot(self, iX, iY) 	# range [0,1]
		lat = 0.07 + 0.56*lat				# range [0.07, 0.56]
		return lat
	
def addFeatures():
	NiTextOut("Adding Features (Python Inland Sea) ...")
	featuregen = ISFeatureGenerator()
	featuregen.addFeatures()
	return 0

def getRiverStartCardinalDirection(argsList):
	pPlot = argsList[0]
	map = CyMap()

	if (pPlot.getY() > ((map.getGridHeight() * 2) / 3)):
		return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH

	if (pPlot.getY() < (map.getGridHeight() / 3)):
		return CardinalDirectionTypes.CARDINALDIRECTION_NORTH

	if (pPlot.getX() > (map.getGridWidth() / 2)):
		return CardinalDirectionTypes.CARDINALDIRECTION_WEST

	return CardinalDirectionTypes.CARDINALDIRECTION_EAST

def getRiverAltitude(argsList):
	pPlot = argsList[0]
	map = CyMap()

	CyPythonMgr().allowDefaultImpl()

	return ((abs(pPlot.getX() - (map.getGridWidth() / 2)) + abs(pPlot.getY() - (map.getGridHeight() / 2))) * 20)
	

def normalizeStartingPlotLocations():

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
		
	if (CyMap().getCustomMapOption(3) == 3):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()

	
def startHumansOnSameTile():

	doCountry()#2.28 for Map Countries
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(7) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(7) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)


	if (CyMap().getCustomMapOption(8) == 1):
		return True	
	
		
		
		
def doCountry():#2.28 for Map Countries		


	#Canada
	if (CyMap().getCustomMapOption(2) == 0):
		doRedesignColor(100,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"), 30, CyGlobalContext().getInfoTypeForString("BONUS_DEER"), 10, CyGlobalContext().getInfoTypeForString("BONUS_FUR"), False)
		doChangeMiddle('Canada')
		
		
	if (CyMap().getCustomMapOption(2) == 1):
		doRedesignColor(100,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), 40, CyGlobalContext().getInfoTypeForString("BONUS_SUGAR"), 10, CyGlobalContext().getInfoTypeForString("BONUS_SPICES"), False)

		doChangeMiddle('Afghanistan')	
		
	if (CyMap().getCustomMapOption(2) == 2):
		doRedesignColor(100,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"), 25, CyGlobalContext().getInfoTypeForString("BONUS_DEER"), 10, CyGlobalContext().getInfoTypeForString("BONUS_FUR"), False)
		#2.36 - 25% not 30%
		doChangeMiddle('Hudson Bay')
		if isBTPon:
			iNewTile = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
		else:
			iNewTile = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
		doRedesignColor(50,True,CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"),iNewTile, 0, -1, 0, -1, True)		
		#2.36 - 50% of the Tundra NOT next to river, are marsh
		
def doChangeMiddle(sCountry):
	#if isBTPon:#2.38 this is out too
	if (CyMap().getCustomMapOption(4) != 0):#that's water
	#Contition (3) depends on country you chose
	
		if ((CyMap().getCustomMapOption(4) == 1 or sCountry == 'Canada' or sCountry == 'Hudson Bay') and not (CyMap().getCustomMapOption(4) == 2)):
			#CvMapGeneratorUtil.BTPMapUtil().BTPFreezeOcean(False,100,True)		
			BTPFreezeOcean(False,100,True)#2.38 for BTS compability
		
		if (CyMap().getCustomMapOption(4) == 2 or sCountry == 'Afghanistan'):
			makeSaltLake(100,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"),30,CyGlobalContext().getInfoTypeForString("BONUS_SALT"))	
		
		
		if (CyMap().getCustomMapOption(5) == 1):
			
			for y in range(CyMap().getGridHeight()/2-4,CyMap().getGridHeight()/2+3,1):					
				p = CyMap().plot(CyMap().getGridWidth()/3 + 1,y)
				#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK"), True, True)
				p.setPlotType(PlotTypes.PLOT_PEAK, True, True)
				p = CyMap().plot(CyMap().getGridWidth() * 2 / 3 - 1,y)
				#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_PEAK"), True, True)
				p.setPlotType(PlotTypes.PLOT_PEAK, True, True)					
				
				
def doRedesignColor(iProbaChangeRedesign,bBonusAvoid, iTerrainChange,iTerrainNew,iProbaBonOne,iBonusOne,iProbaBonTwo,iBonusTwo,bOnlyNotRiver):#2.28 for Map Countries			
	
	#Unused bBonusAvoid

	pPlotList = []
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)
			if (p.getTerrainType() == iTerrainChange and not p.isImpassable()):#2.36 small addition for Deer not to appear top of mountain
				if not (bBonusAvoid and p.getBonusType(-1) != -1):
					if not bOnlyNotRiver or not p.isRiver():
						pPlotList.append(p)
					
	for p in pPlotList:
		iProbaToChange = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProbaToChange <= iProbaChangeRedesign:	
			p.setTerrainType(iTerrainNew, True, True)
			iProba1 = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			iProba2 = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
			if iProba2 <= iProbaBonTwo:
				p.setBonusType(iBonusTwo)			
			if iProba1 <= iProbaBonOne:
				p.setBonusType(iBonusOne)	

	
	
def makeSaltLake(iProbaHappen,iNewTerrain,iBonusProba,iBonusType):
									
	pPlotList = []
	for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				p = CyMap().plot(x,y)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_OCEAN")):
					pPlotList.append(p)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")):
					pPlotList.append(p)
					
	for p in pPlotList:
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= iProbaHappen and not p.isImpassable():	
			p.setTerrainType(iNewTerrain, True, True)
			if iProba <= iBonusProba:	
				p.setBonusType(iBonusType)		


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