#
#	FILE:	 Wheel.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Soren Johnson, Andy Szybalski
#	PURPOSE: Regional map script - Player areas linked in a wheel pattern.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import math
from CvMapGeneratorUtil import MultilayeredFractal
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
import random#2.38

balancer = BonusBalancer()

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_WHEEL_DESCR"
	
def getDescriptionTitle():
	return "A popular BTS map which has the shape of a wheel : players get their own circled amount of land linked to the other players via an external and an inner band of land as well as a central land"
	
def getDescriptionTitleTwo():
	return ""	

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "Make the Ring width 3 for space, but consider making the Spoke width 2 so that you can make the boats move more easily."	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Play Tiny size for 3v3.  You might also want to increase the amount of marshes to make it possible to cross without culture or cities"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Traditional map for 3v3 Classical Start, with Toroidal option, sometimes Renaissance. Also decent map for Ironman. You will want to pay attention to the settings of the middle land"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""		

def getNumCustomMapOptions():
	"""
	Number of different user-defined options for this map
	"""
	return 20
	
def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	"""
	Returns name of specified option
	argsList[0] is Option ID (int)
	"""
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_AREAS_PER_PLAYER",
		1:	"TXT_KEY_MAP_SCRIPT_LAND_SHAPE",
		2:	"TXT_KEY_MAP_SCRIPT_RING_WIDTH",
		3:	"TXT_KEY_MAP_SCRIPT_SPOKE_WIDTH",
		4:  "TXT_KEY_MAP_WORLD_WRAP",
		5:  "TXT_KEY_CONCEPT_RESOURCES",
		6:	"BTG Marsh",
		7:	"Land Color",
		8:	"BTG Central Hub",
		9:	"BTG Resources",
		10:	"BTG Forest Type",		
		11: "Starting Units",
		12: "BTG Start Position",
		13:	"Size 1 notch smaller",
		14:	"BTG Free Unit",
		15: "BTG Amt Free Unit",
		16:	"BTG Seas",		
		17: "Circumnavigation",
		18:	"BTG Spectator Notes",
		19:	"Credit"				
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:	3,
		2:	3,
		3:	3,
		4:  3,
		5:  2,
		6:	3,
		7:  3,
		8:	4,
		9:	2,
		10:	5,		
		11: 2,
		12: 2,
		13:	3,
		14:	4,
		15:	4,
		16: 4,
		17:	2,
		18: 2,
		19:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_1_PER_PLAYER",
			1: "TXT_KEY_MAP_SCRIPT_2_10_PLAYERS_MAX"
			},
		1:	{
			0: "TXT_KEY_MAP_SCRIPT_NATURAL",
			1: "TXT_KEY_MAP_SCRIPT_PRESSED",
			2: "TXT_KEY_MAP_SCRIPT_SOLID"
			},
		2:	{
			0: "TXT_KEY_MAP_SCRIPT_1_PLOT_WIDE",
			1: "TXT_KEY_MAP_SCRIPT_2_PLOTS_WIDE",
			2: "TXT_KEY_MAP_SCRIPT_3_PLOTS_WIDE"
			},
		3:	{
			0: "TXT_KEY_MAP_SCRIPT_1_PLOT_WIDE",
			1: "TXT_KEY_MAP_SCRIPT_2_PLOTS_WIDE",
			2: "TXT_KEY_MAP_SCRIPT_3_PLOTS_WIDE"
			},
		4:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		5:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "Balanced - Including Marble",		
			},
		6:	{
			0: "Yes - Many Marsh",
			1: "Yes - Some Marsh",
			2: "No - No Marsh",
			},			
		7:	{
			0: "Normal Color",
			1: "Green Land",
			2: "Super Green - No Desert"
			},
		8:	{
			0: "Normal - Ice and Tundra",
			1: "Tundra Only",
			2: "Plains Only",
			3: "Grassland Only"
			},
		9:	{
			0: "No",
			1: "Yes - Balanced for Lead and Amber, Normal for others"
			},	
		10:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},				
		11:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},	
		12:	{
			0: "Normal",
			1: "Top v Bottom"
			},
		13:	{
			0: "No",
			1: "Yes",
			2: "Yes - 2 Notches"
			},	
		14:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			},
		15:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},	
		16:	{
			0: "No",
			1: "Yes - All Lagoons",
			2: "Yes - Lagoons on coast",
			3: "Yes - Balanced Lagoons and Deep sea"
			},	
		17:	{
			0: "Normal",
			1: "Disabled (BTS Hardcoded, BTG via option)"
			},				
		18:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"			
			},
		19:	{
			0: "Penny for Beyond the Game - Works for BTS, BTG Options have no effect"	
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:	2,
		2:	2,
		3:	1,
		4:  1,
		5:  1,
		6:	2,
		7:	1,
		8:	0,
		9:	1,
		10:	0,
		11:	0,
		12:	0,
		13:	0,
		14:	0,
		15:	0,
		16:	0,
		17:	1,
		18:	0,
		19:	0
		}
	return option_defaults[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(4) == 1 or map.getCustomMapOption(4) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(4) == 2)

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	true,
		2:	true,
		3:	true,
		4:  false,
		5:  false,
		6:	true,
		7:  true,
		8:	true,
		9:	true,
		10:	true,
		11:	true,
		12:	false,
		13:	true,
		14:	false,
		15:	false,
		16:	true,
		17: false,
		18:	false,
		19: false
		}
	return option_random[iOption]

def normalizeAddExtras():
	if (CyMap().getCustomMapOption(5) == 1):
		balancer.normalizeAddExtras()
		
	#2.18 Moved here, last thing to do
	if isBTPon :
		if (CyMap().getCustomMapOption(6) == 0):
			CvMapGeneratorUtil.BTPMapUtil().BTPMarshPlacement(1)
			
		if (CyMap().getCustomMapOption(6) == 1):
			CvMapGeneratorUtil.BTPMapUtil().BTPMarshPlacement(2)	

		if (CyMap().getCustomMapOption(9) == 1):#2.35
			listToBalance = ["BONUS_LEAD","BONUS_AMBER"]
			balancer.BTPnormalizeAddExtrasSpecific(listToBalance,6,0,100)
			
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.21y
	if isBTPon :
		if (CyMap().getCustomMapOption(9) == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
				
	if (CyMap().getCustomMapOption(5) == 1):
		#if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
		if (type_string in balancer.resourcesToBalance):#don't want marble out
			return None # don't place any of this bonus randomly
			
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isBonusIgnoreLatitude():
	return True

def getGridSize(argsList):
	
	if (CyMap().getCustomMapOption(13) == 0):#2.21z
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8,5),
			WorldSizeTypes.WORLDSIZE_TINY:		(10,6),
			WorldSizeTypes.WORLDSIZE_SMALL:		(13,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(16,10),
			WorldSizeTypes.WORLDSIZE_LARGE:		(21,13),
			WorldSizeTypes.WORLDSIZE_HUGE:		(26,16)
		}
		
	if (CyMap().getCustomMapOption(13) == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,4),
			WorldSizeTypes.WORLDSIZE_TINY:		(9,5),
			WorldSizeTypes.WORLDSIZE_SMALL:		(12,7),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(14,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(19,12),
			WorldSizeTypes.WORLDSIZE_HUGE:		(24,14)
		}		
	
	if (CyMap().getCustomMapOption(13) == 2):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,4),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,5),
			WorldSizeTypes.WORLDSIZE_SMALL:		(11,7),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(13,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(18,11),
			WorldSizeTypes.WORLDSIZE_HUGE:		(23,14)
		}	

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def beforeGeneration():
	# Set up land mass data for all players (Square Wheels) then access later.
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
	
	# Success flag. Set to false if number of players falls outside legal range.
	global bSuccessFlag
	if iPlayers < 2 or iPlayers > 18:
		bSuccessFlag = False
		return 0
	else:
		bSuccessFlag = True

	# Check Wheel Type. Set templates.
	userInputLandmass = map.getCustomMapOption(0)
	if userInputLandmass == 1 and iPlayers >= 2 and iPlayers <= 10: # Buffered
		# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
		templates = {2: {0: [0.0, 0.333, 0.0, 1.0],
		                 1: [0.667, 1.0, 0.0, 1.0]},
		             3: {0: [0.0, 0.4, 0.667, 1.0],
		                 1: [0.8, 1.0, 0.333, 1.0],
		                 2: [0.2, 0.6, 0.0, 0.333]},
		             4: {0: [0.0, 0.333, 0.333, 0.667],
		                 1: [0.333, 0.667, 0.667, 1.0],
		                 2: [0.667, 1.0, 0.333, 0.667],
		                 3: [0.333, 0.667, 0.0, 0.333]},
		             5: {0: [0.0, 0.167, 0.4, 0.8],
		                 1: [0.333, 0.667, 0.8, 1.0],
		                 2: [0.833, 1.0, 0.4, 0.8],
		                 3: [0.583, 0.917, 0.0, 0.2],
		                 4: [0.083, 0.417, 0.0, 0.2]},
		             6: {0: [0.0, 0.333, 0.8, 1.0],
		                 1: [0.5, 0.833, 0.8, 1.0],
		                 2: [0.833, 1.0, 0.4, 0.8],
		                 3: [0.667, 1.0, 0.0, 0.2],
		                 4: [0.167, 0.5, 0.0, 0.2],
		                 5: [0.0, 0.167, 0.2, 0.6]},
		             7: {0: [0.0, 0.2, 0.75, 1.0],
		                 1: [0.4, 0.6, 0.75, 1.0],
		                 2: [0.8, 1.0, 0.75, 1.0],
		                 3: [0.8, 1.0, 0.25, 0.5],
		                 4: [0.6, 0.8, 0.0, 0.25],
		                 5: [0.2, 0.4, 0.0, 0.25],
		                 6: [0.0, 0.2, 0.25, 0.5]},
		             8: {0: [0.0, 0.2, 0.6, 0.8],
		                 1: [0.2, 0.4, 0.8, 1.0],
		                 2: [0.6, 0.8, 0.8, 1.0],
		                 3: [0.8, 1.0, 0.6, 0.8],
		                 4: [0.8, 1.0, 0.2, 0.4],
		                 5: [0.6, 0.8, 0.0, 0.2],
		                 6: [0.2, 0.4, 0.0, 0.2],
		                 7: [0.0, 0.2, 0.2, 0.4]},
		             9: {0: [0.0, 0.167, 0.6, 0.8],
		                 1: [0.167, 0.333, 0.8, 1.0],
		                 2: [0.5, 0.677, 0.8, 1.0],
		                 3: [0.833, 1.0, 0.8, 1.0],
		                 4: [0.833, 1.0, 0.4, 0.6],
		                 5: [0.833, 1.0, 0.0, 0.2],
		                 6: [0.5, 0.667, 0.0, 0.2],
		                 7: [0.167, 0.333, 0.0, 0.2],
		                 8: [0.0, 0.167, 0.2, 0.4]},
		             10: {0: [0.0, 0.167, 0.667, 0.833],
		                  1: [0.167, 0.333, 0.833, 1.0],
		                  2: [0.5, 0.667, 0.833, 1.0],
		                  3: [0.833, 1.0, 0.833, 1.0],
		                  4: [0.833, 1.0, 0.5, 0.667],
		                  5: [0.833, 1.0, 0.167, 0.333],
		                  6: [0.667, 0.833, 0.0, 0.167],
		                  7: [0.333, 0.5, 0.0, 0.167],
		                  8: [0.0, 0.167, 0.0, 0.167],
		                  9: [0.0, 0.167, 0.333, 0.5]}
		}
		buffers = {2: {0: [0.4, 0.6, 0.1, 0.3],
		               1: [0.4, 0.6, 0.7, 0.9]},
		           3: {0: [0.4, 0.8, 0.667, 1.0],
		               1: [0.6, 1.0, 0.0, 0.333],
		               2: [0.0, 0.2, 0.0, 0.667]},
		           4: {0: [0.0, 0.333, 0.667, 1.0],
		               1: [0.667, 1.0, 0.667, 1.0],
		               2: [0.667, 1.0, 0.0, 0.333],
		               3: [0.0, 0.333, 0.0, 0.333]},
		           5: {0: [0.0, 0.167, 0.2, 0.4],
		               1: [0.167, 0.333, 0.8, 1.0],
		               2: [0.667, 0.833, 0.8, 1.0],
		               3: [0.833, 1.0, 0.2, 0.4],
		               4: [0.417, 0.583, 0.0, 0.2]},
		           6: {0: [0.0, 0.167, 0.6, 0.8],
		               1: [0.333, 0.5, 0.8, 1.0],
		               2: [0.833, 1.0, 0.8, 1.0],
		               3: [0.833, 1.0, 0.2, 0.4],
		               4: [0.5, 0.667, 0.0, 0.2],
		               5: [0.0, 0.167, 0.0, 0.2]},
		           7: {0: [0.2, 0.4, 0.77, 1.0],
		               1: [0.6, 0.8, 0.77, 1.0],
		               2: [0.82, 1.0, 0.5, 0.7],
		               3: [0.8, 1.0, 0.0, 0.25],
		               4: [0.4, 0.6, 0.0, 0.25],
		               5: [0.0, 0.2, 0.0, 0.25],
		               6: [0.0, 0.18, 0.5, 0.7]},
		           8: {0: [0.0, 0.2, 0.8, 1.0],
		               1: [0.4, 0.6, 0.8, 1.0],
		               2: [0.8, 1.0, 0.8, 1.0],
		               3: [0.8, 1.0, 0.4, 0.6],
		               4: [0.8, 1.0, 0.0, 0.2],
		               5: [0.4, 0.6, 0.0, 0.2],
		               6: [0.0, 0.2, 0.0, 0.2],
		               7: [0.0, 0.2, 0.4, 0.6]},
		           9: {0: [0.0, 0.167, 0.8, 1.0],
		               1: [0.333, 0.5, 0.8, 1.0],
		               2: [0.667, 0.81, 0.82, 1.0],
		               3: [0.85, 1.0, 0.6, 0.77],
		               4: [0.85, 1.0, 0.22, 0.4],
		               5: [0.667, 0.81, 0.0, 0.18],
		               6: [0.333, 0.5, 0.0, 0.2],
		               7: [0.0, 0.167, 0.0, 0.2],
		               8: [0.0, 0.167, 0.4, 0.6]},
		           10: {0: [0.0, 0.15, 0.5, 0.65],
		                1: [0.0, 0.167, 0.833, 1.0],
		                2: [0.333, 0.5, 0.833, 1.0],
		                3: [0.667, 0.81, 0.85, 1.0],
		                4: [0.85, 1.0, 0.667, 0.81],
		                5: [0.833, 1.0, 0.333, 0.5],
		                6: [0.833, 1.0, 0.0, 0.167],
		                7: [0.5, 0.667, 0.0, 0.167],
		                8: [0.18, 0.333, 0.0, 0.15],
		                9: [0.0, 0.15, 0.18, 0.333]}
		}
		center_isle = {2: [0.35, 0.65, 0.4, 0.6],
		               3: [0.28, 0.72, 0.4, 0.6],
		               4: [0.38, 0.62, 0.38, 0.62],
		               5: [0.27, 0.73, 0.3, 0.7],
		               6: [0.25, 0.75, 0.3, 0.7],
		               7: [0.3, 0.7, 0.35, 0.65],
		               8: [0.32, 0.68, 0.32, 0.68],
		               9: [0.25, 0.75, 0.3, 0.7],
		               10: [0.25, 0.75, 0.25, 0.75]
		}
		# The wheel is a series of coordinates, line segments drawn from one to the next. [Lon0, Lat0], [Lon1, Lat1], [Lon2, Lat2], etc.
		the_wheel = {2: [[0.167, 0.2], [0.167, 0.8], [0.833, 0.8], [0.833, 0.2]],
		             3: [[0.1, 0.167], [0.1, 0.833], [0.9, 0.833], [0.9, 0.167]],
		             4: [[0.167, 0.167], [0.167, 0.833], [0.833, 0.833], [0.833, 0.167]],
		             5: [[0.083, 0.7], [0.25, 0.9], [0.75, 0.9], [0.917, 0.7], [0.917, 0.3], [0.833, 0.1], [0.167, 0.1], [0.083, 0.3]],
		             6: [[0.083, 0.1], [0.083, 0.9], [0.917, 0.9], [0.917, 0.1]],
		             7: [[0.1, 0.125], [0.1, 0.875], [0.9, 0.875], [0.9, 0.125]],
		             8: [[0.1, 0.1], [0.1, 0.9], [0.9, 0.9], [0.9, 0.1]],
		             9: [[0.083, 0.1], [0.083, 0.9], [0.917, 0.9], [0.917, 0.1]],
		             10: [[0.083, 0.083], [0.083, 0.917], [0.917, 0.917], [0.917, 0.083]]
		}
		# Spokes are drawn line segments: [startLon0, startLat0, endLon0, endLat0], [startLon1, startLat1, endLon1, endLat1], etc.
		the_spokes = {2: [[0.167, 0.2, 0.167, 0.8], [0.833, 0.2, 0.833, 0.8], 
		                  [0.167, 0.5, 0.833, 0.5], [0.5, 0.2, 0.5, 0.8]],
		              3: [[0.2, 0.833, 0.5, 0.5], [0.9, 0.667, 0.5, 0.5], [0.4, 0.167, 0.5, 0.5]],
		              4: [[0.167, 0.5, 0.833, 0.5], [0.5, 0.833, 0.5, 0.167]],
		              5: [[0.083, 0.6, 0.5, 0.5], [0.5, 0.917, 0.5, 0.5], [0.917, 0.6, 0.5, 0.5],
		                  [0.25, 0.083, 0.5, 0.5], [0.75, 0.083, 0.5, 0.5]],
		              6: [[0.083, 0.4, 0.917, 0.6], [0.167, 0.9, 0.833, 0.1], [0.667, 0.9, 0.333, 0.1]],
		              7: [[0.1, 0.875, 0.4, 0.5], [0.3, 0.125, 0.5, 0.5], [0.1, 0.4, 0.4, 0.5],
		                  [0.7, 0.125, 0.5, 0.5], [0.5, 0.875, 0.5, 0.5], [0.9, 0.875, 0.6, 0.5],
		                  [0.9, 0.375, 0.6, 0.5], [0.4, 0.5, 0.6, 0.5]],
		              8: [[0.1, 0.7, 0.9, 0.3], [0.3, 0.9, 0.7, 0.1], 
		                  [0.1, 0.3, 0.9, 0.7], [0.7, 0.9, 0.3, 0.1]],
		              9: [[0.083, 0.7, 0.333, 0.5], [0.083, 0.3, 0.333, 0.5], [0.25, 0.1, 0.417, 0.5], 
		                  [0.25, 0.9, 0.417, 0.5], [0.583, 0.9, 0.583, 0.1], [0.333, 0.5, 0.917, 0.5],
		                  [0.917, 0.9, 0.667, 0.5], [0.917, 0.1, 0.667, 0.5]],
		              10: [[0.25, 0.917, 0.75, 0.083], [0.417, 0.083, 0.583, 0.917], [0.083, 0.083, 0.917, 0.917], 
		                   [0.083, 0.417, 0.917, 0.583], [0.083, 0.75, 0.917, 0.25]]
		}

	else: # Normal.
		# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
		templates = {2: {0: [0.0, 0.333, 0.0, 1.0],
		                 1: [0.667, 1.0, 0.0, 1.0]},
		             3: {0: [0.0, 0.25, 0.25, 0.75],
		                 1: [0.5, 1.0, 0.75, 1.0],
		                 2: [0.5, 1.0, 0.0, 0.25]},
		             4: {0: [0.0, 0.333, 0.333, 0.667],
		                 1: [0.333, 0.667, 0.667, 1.0],
		                 2: [0.667, 1.0, 0.333, 0.667],
		                 3: [0.333, 0.667, 0.0, 0.333]},
		             5: {0: [0.0, 0.25, 0.333, 1.0],
		                 1: [0.25, 0.75, 0.667, 1.0],
		                 2: [0.75, 1.0, 0.333, 1.0],
		                 3: [0.5, 1.0, 0.0, 0.333],
		                 4: [0.0, 0.5, 0.0, 0.333]},
		             6: {0: [0.0, 0.4, 0.667, 1.0],
		                 1: [0.4, 0.8, 0.667, 1.0],
		                 2: [0.8, 1.0, 0.333, 1.0],
		                 3: [0.6, 1.0, 0.0, 0.333],
		                 4: [0.2, 0.6, 0.0, 0.333],
		                 5: [0.0, 0.2, 0.0, 0.667]},
		             7: {0: [0.0, 0.4, 0.75, 1.0],
		                 1: [0.4, 0.8, 0.75, 1.0],
		                 2: [0.8, 1.0, 0.5, 1.0],
		                 3: [0.8, 1.0, 0.0, 0.5],
		                 4: [0.4, 0.8, 0.0, 0.25],
		                 5: [0.0, 0.4, 0.0, 0.25],
		                 6: [0.0, 0.2, 0.25, 0.75]},
		             8: {0: [0.0, 0.3, 0.35, 0.65],
		                 1: [0.0, 0.3, 0.7, 1.0],
		                 2: [0.35, 0.65, 0.7, 1.0],
		                 3: [0.7, 1.0, 0.7, 1.0],
		                 4: [0.7, 1.0, 0.35, 0.65],
		                 5: [0.7, 1.0, 0.0, 0.3],
		                 6: [0.35, 0.65, 0.0, 0.3],
		                 7: [0.0, 0.3, 0.0, 0.3]},
		             9: {0: [0.0, 0.167, 0.6, 1.0],
		                 1: [0.167, 0.5, 0.8, 1.0],
		                 2: [0.5, 0.833, 0.8, 1.0],
		                 3: [0.833, 1.0, 0.6, 1.0],
		                 4: [0.833, 1.0, 0.2, 0.6],
		                 5: [0.667, 1.0, 0.0, 0.2],
		                 6: [0.333, 0.667, 0.0, 0.2],
		                 7: [0.0, 0.333, 0.0, 0.2],
		                 8: [0.0, 0.167, 0.2, 0.6]},
		             10: {0: [0.0, 0.167, 0.5, 0.833],
		                  1: [0.0, 0.333, 0.833, 1.0],
		                  2: [0.333, 0.667, 0.833, 1.0],
		                  3: [0.667, 1.0, 0.833, 1.0],
		                  4: [0.833, 1.0, 0.5, 0.833],
		                  5: [0.833, 1.0, 0.167, 0.5],
		                  6: [0.667, 1.0, 0.0, 0.167],
		                  7: [0.333, 0.667, 0.0, 0.167],
		                  8: [0.0, 0.333, 0.0, 0.167],
		                  9: [0.0, 0.167, 0.167, 0.5]},
		             11: {0: [0.0, 0.2, 0.167, 0.5],
		                  1: [0.0, 0.2, 0.5, 0.833],
		                  2: [0.2, 0.4, 0.667, 1.0],
		                  3: [0.4, 0.6, 0.667, 1.0],
		                  4: [0.6, 0.8, 0.667, 1.0],
		                  5: [0.8, 1.0, 0.667, 1.0],
		                  6: [0.8, 1.0, 0.333, 0.667],
		                  7: [0.8, 1.0, 0.0, 0.333],
		                  8: [0.6, 0.8, 0.0, 0.333],
		                  9: [0.4, 0.6, 0.0, 0.333],
		                  10: [0.2, 0.4, 0.0, 0.333]},
		             12: {0: [0.0, 0.2, 0.333, 0.667],
		                  1: [0.0, 0.2, 0.667, 1.0],
		                  2: [0.2, 0.4, 0.667, 1.0],
		                  3: [0.4, 0.6, 0.667, 1.0],
		                  4: [0.6, 0.8, 0.667, 1.0],
		                  5: [0.8, 1.0, 0.667, 1.0],
		                  6: [0.8, 1.0, 0.333, 0.667],
		                  7: [0.8, 1.0, 0.0, 0.333],
		                  8: [0.6, 0.8, 0.0, 0.333],
		                  9: [0.4, 0.6, 0.0, 0.333],
		                  10: [0.2, 0.4, 0.0, 0.333],
		                  11: [0.0, 0.2, 0.0, 0.333]},
		             13: {0: [0.0, 0.2, 0.375, 0.625],
		                  1: [0.0, 0.2, 0.7, 0.95],
		                  2: [0.2, 0.4, 0.75, 1.0],
		                  3: [0.4, 0.6, 0.75, 1.0],
		                  4: [0.6, 0.8, 0.75, 1.0],
		                  5: [0.8, 1.0, 0.75, 1.0],
		                  6: [0.8, 1.0, 0.5, 0.75],
		                  7: [0.8, 1.0, 0.25, 0.5],
		                  8: [0.8, 1.0, 0.0, 0.25],
		                  9: [0.6, 0.8, 0.0, 0.25],
		                  10: [0.4, 0.6, 0.0, 0.25],
		                  11: [0.2, 0.4, 0.0, 0.25],
		                  12: [0.0, 0.2, 0.05, 0.3]},
		             14: {0: [0.0, 0.2, 0.5, 0.75],
		                  1: [0.0, 0.2, 0.75, 1.0],
		                  2: [0.2, 0.4, 0.75, 1.0],
		                  3: [0.4, 0.6, 0.75, 1.0],
		                  4: [0.6, 0.8, 0.75, 1.0],
		                  5: [0.8, 1.0, 0.75, 1.0],
		                  6: [0.8, 1.0, 0.5, 0.75],
		                  7: [0.8, 1.0, 0.25, 0.5],
		                  8: [0.8, 1.0, 0.0, 0.25],
		                  9: [0.6, 0.8, 0.0, 0.25],
		                  10: [0.4, 0.6, 0.0, 0.25],
		                  11: [0.2, 0.4, 0.0, 0.25],
		                  12: [0.0, 0.2, 0.0, 0.25],
		                  13: [0.0, 0.2, 0.25, 0.5]},
		             15: {0: [0.0, 0.167, 0.375, 0.625],
		                  1: [0.0, 0.167, 0.7, 0.95],
		                  2: [0.167, 0.333, 0.75, 1.0],
		                  3: [0.333, 0.5, 0.75, 1.0],
		                  4: [0.5, 0.667, 0.75, 1.0],
		                  5: [0.667, 0.833, 0.75, 1.0],
		                  6: [0.833, 1.0, 0.75, 1.0],
		                  7: [0.833, 1.0, 0.5, 0.75],
		                  8: [0.833, 1.0, 0.25, 0.5],
		                  9: [0.833, 1.0, 0.0, 0.25],
		                  10: [0.667, 0.833, 0.0, 0.25],
		                  11: [0.5, 0.667, 0.0, 0.25],
		                  12: [0.333, 0.5, 0.0, 0.25],
		                  13: [0.167, 0.333, 0.0, 0.25],
		                  14: [0.0, 0.167, 0.05, 0.3]},
		             16: {0: [0.0, 0.167, 0.5, 0.75],
		                  1: [0.0, 0.167, 0.75, 1.0],
		                  2: [0.167, 0.333, 0.75, 1.0],
		                  3: [0.333, 0.5, 0.75, 1.0],
		                  4: [0.5, 0.667, 0.75, 1.0],
		                  5: [0.667, 0.833, 0.75, 1.0],
		                  6: [0.833, 1.0, 0.75, 1.0],
		                  7: [0.833, 1.0, 0.5, 0.75],
		                  8: [0.833, 1.0, 0.25, 0.5],
		                  9: [0.833, 1.0, 0.0, 0.25],
		                  10: [0.667, 0.833, 0.0, 0.25],
		                  11: [0.5, 0.667, 0.0, 0.25],
		                  12: [0.333, 0.5, 0.0, 0.25],
		                  13: [0.167, 0.333, 0.0, 0.25],
		                  14: [0.0, 0.167, 0.25, 0.5],
		                  15: [0.0, 0.167, 0.0, 0.25]},
		             17: {0: [0.0, 0.167, 0.5, 0.7],
		                  1: [0.0, 0.167, 0.7, 0.9],
		                  2: [0.167, 0.333, 0.8, 1.0],
		                  3: [0.333, 0.5, 0.8, 1.0],
		                  4: [0.5, 0.667, 0.8, 1.0],
		                  5: [0.667, 0.833, 0.8, 1.0],
		                  6: [0.833, 1.0, 0.8, 1.0],
		                  7: [0.833, 1.0, 0.6, 0.8],
		                  8: [0.833, 1.0, 0.4, 0.6],
		                  9: [0.833, 1.0, 0.2, 0.4],
		                  10: [0.833, 1.0, 0.0, 0.2],
		                  11: [0.667, 0.833, 0.0, 0.2],
		                  12: [0.5, 0.667, 0.0, 0.2],
		                  13: [0.333, 0.5, 0.0, 0.2],
		                  14: [0.167, 0.333, 0.0, 0.2],
		                  15: [0.0, 0.167, 0.1, 0.3],
		                  16: [0.0, 0.167, 0.3, 0.5]},
		             18: {0: [0.0, 0.167, 0.6, 0.8],
		                  1: [0.0, 0.167, 0.8, 1.0],
		                  2: [0.167, 0.333, 0.8, 1.0],
		                  3: [0.333, 0.5, 0.8, 1.0],
		                  4: [0.5, 0.667, 0.8, 1.0],
		                  5: [0.667, 0.833, 0.8, 1.0],
		                  6: [0.833, 1.0, 0.8, 1.0],
		                  7: [0.833, 1.0, 0.6, 0.8],
		                  8: [0.833, 1.0, 0.4, 0.6],
		                  9: [0.833, 1.0, 0.2, 0.4],
		                  10: [0.833, 1.0, 0.0, 0.2],
		                  11: [0.667, 0.833, 0.0, 0.2],
		                  12: [0.5, 0.667, 0.0, 0.2],
		                  13: [0.333, 0.5, 0.0, 0.2],
		                  14: [0.167, 0.333, 0.0, 0.2],
		                  15: [0.0, 0.167, 0.0, 0.2],
		                  16: [0.0, 0.167, 0.2, 0.4],
		                  17: [0.0, 0.167, 0.4, 0.6]}
		}
		center_isle = {2: [0.35, 0.65, 0.4, 0.6],
		               3: [0.38, 0.7, 0.35, 0.65],
		               4: [0.37, 0.63, 0.37, 0.63],
		               5: [0.32, 0.68, 0.38, 0.62],
		               6: [0.28, 0.72, 0.38, 0.62],
		               7: [0.28, 0.72, 0.35, 0.65],
		               8: [0.37, 0.63, 0.37, 0.63],
		               9: [0.3, 0.7, 0.35, 0.65],
		               10: [0.3, 0.7, 0.3, 0.7],
		               11: [0.28, 0.72, 0.38, 0.62],
		               12: [0.28, 0.72, 0.38, 0.62],
		               13: [0.3, 0.7, 0.35, 0.65],
		               14: [0.3, 0.7, 0.35, 0.65],
		               15: [0.25, 0.75, 0.35, 0.65],
		               16: [0.25, 0.75, 0.35, 0.65],
		               17: [0.25, 0.75, 0.3, 0.7],
		               18: [0.25, 0.75, 0.3, 0.7]
		}
		# The wheel is a series of coordinates, line segments drawn from one to the next. [Lon0, Lat0], [Lon1, Lat1], [Lon2, Lat2], etc.
		the_wheel = {2: [[0.167, 0.3], [0.167, 0.7], [0.833, 0.7], [0.833, 0.3]],
		             3: [[0.125, 0.375], [0.125, 0.625], [0.625, 0.875], [0.875, 0.875], [0.875, 0.125], [0.625, 0.125]],
		             4: [[0.167, 0.5], [0.5, 0.833], [0.833, 0.5], [0.5, 0.167]],
		             5: [[0.125, 0.167], [0.125, 0.833], [0.875, 0.833], [0.875, 0.167]],
		             6: [[0.1, 0.167], [0.1, 0.833], [0.9, 0.833], [0.9, 0.167]],
		             7: [[0.1, 0.125], [0.1, 0.875], [0.9, 0.875], [0.9, 0.125]],
		             8: [[0.167, 0.167], [0.167, 0.833], [0.833, 0.833], [0.833, 0.167]],
		             9: [[0.083, 0.1], [0.083, 0.9], [0.917, 0.9], [0.917, 0.1]],
		             10: [[0.083, 0.083], [0.083, 0.917], [0.917, 0.917], [0.917, 0.083]],
		             11: [[0.1, 0.333], [0.1, 0.667], [0.3, 0.833], [0.9, 0.833], [0.9, 0.167], [0.3, 0.167]],
		             12: [[0.1, 0.167], [0.1, 0.833], [0.9, 0.833], [0.9, 0.167]],
		             13: [[0.1, 0.175], [0.1, 0.825], [0.3, 0.875], [0.9, 0.875], [0.9, 0.125], [0.3, 0.125]],
		             14: [[0.1, 0.125], [0.1, 0.875], [0.9, 0.875], [0.9, 0.125]],
		             15: [[0.083, 0.175], [0.083, 0.825], [0.25, 0.875], [0.917, 0.875], [0.917, 0.125], [0.25, 0.125]],
		             16: [[0.083, 0.125], [0.083, 0.875], [0.917, 0.875], [0.917, 0.125]],
		             17: [[0.083, 0.2], [0.083, 0.8], [0.25, 0.9], [0.917, 0.9], [0.917, 0.1], [0.25, 0.1]],
		             18: [[0.083, 0.1], [0.083, 0.9], [0.917, 0.9], [0.917, 0.1]]
		}
		# Spokes are drawn line segments: [startLon0, startLat0, endLon0, endLat0], [startLon1, startLat1, endLon1, endLat1], etc.
		the_spokes = {2: [[0.167, 0.2, 0.167, 0.8], [0.833, 0.2, 0.833, 0.8], [0.167, 0.5, 0.833, 0.5]],
		              3: [[0.125, 0.5, 0.5, 0.5], [0.75, 0.125, 0.5, 0.5], [0.75, 0.875, 0.5, 0.5]],
		              4: [[0.167, 0.5, 0.833, 0.5], [0.5, 0.833, 0.5, 0.167]],
		              5: [[0.125, 0.667, 0.375, 0.5], [0.25, 0.167, 0.375, 0.5], [0.375, 0.5, 0.625, 0.5],
		                  [0.5, 0.5, 0.5, 0.833], [0.625, 0.5, 0.75, 0.167], [0.625, 0.5, 0.875, 0.667]],
		              6: [[0.1, 0.333, 0.3, 0.5], [0.7, 0.5, 0.8, 0.167], [0.7, 0.5, 0.9, 0.667], 
		                  [0.4, 0.167, 0.6, 0.833], [0.2, 0.833, 0.3, 0.5], [0.3, 0.5, 0.7, 0.5]],
		              7: [[0.2, 0.875, 0.3, 0.5], [0.2, 0.125, 0.3, 0.5], [0.1, 0.5, 0.7, 0.5],
		                  [0.6, 0.125, 0.5, 0.5], [0.6, 0.875, 0.5, 0.5], [0.9, 0.75, 0.7, 0.5],
		                  [0.9, 0.25, 0.7, 0.5]],
		              8: [[0.167, 0.5, 0.833, 0.5], [0.5, 0.833, 0.5, 0.167], 
		                  [0.167, 0.167, 0.833, 0.833], [0.167, 0.833, 0.833, 0.167]],
		              9: [[0.083, 0.8, 0.375, 0.5], [0.083, 0.4, 0.375, 0.5], [0.167, 0.1, 0.375, 0.5], 
		                  [0.333, 0.9, 0.5, 0.5], [0.667, 0.9, 0.5, 0.5], [0.5, 0.1, 0.5, 0.5],
		                  [0.917, 0.8, 0.625, 0.5], [0.917, 0.4, 0.625, 0.5], [0.833, 0.1, 0.625, 0.5], 
		                  [0.375, 0.5, 0.625, 0.5]],
		              10: [[0.167, 0.917, 0.833, 0.083], [0.5, 0.083, 0.5, 0.917], [0.167, 0.083, 0.833, 0.917], 
		                   [0.083, 0.333, 0.917, 0.667], [0.083, 0.667, 0.917, 0.333]],
		              11: [[0.7, 0.5, 0.9, 0.5], [0.7, 0.5, 0.9, 0.167], [0.7, 0.5, 0.9, 0.833], 
		                   [0.6, 0.5, 0.7, 0.833], [0.6, 0.5, 0.7, 0.167], [0.5, 0.5, 0.5, 0.833],
		                   [0.5, 0.5, 0.5, 0.167], [0.4, 0.5, 0.3, 0.167], [0.4, 0.5, 0.3, 0.833], 
		                   [0.3, 0.5, 0.1, 0.667], [0.3, 0.5, 0.1, 0.333], [0.3, 0.5, 0.7, 0.5]],
		              12: [[0.7, 0.5, 0.9, 0.5], [0.7, 0.5, 0.9, 0.167], [0.7, 0.5, 0.9, 0.833], 
		                   [0.6, 0.5, 0.7, 0.833], [0.6, 0.5, 0.7, 0.167], [0.5, 0.5, 0.5, 0.833],
		                   [0.5, 0.5, 0.5, 0.167], [0.4, 0.5, 0.3, 0.167], [0.4, 0.5, 0.3, 0.833], 
		                   [0.3, 0.5, 0.1, 0.167], [0.3, 0.5, 0.1, 0.833], [0.3, 0.5, 0.1, 0.5], 
		                   [0.3, 0.5, 0.7, 0.5]],
		              13: [[0.3, 0.875, 0.5, 0.125], [0.3, 0.5, 0.6, 0.5], [0.5, 0.875, 0.3, 0.125], 
		                   [0.7, 0.125, 0.9, 0.375], [0.7, 0.875, 0.9, 0.625], [0.9, 0.125, 0.6, 0.5],
		                   [0.9, 0.875, 0.6, 0.5], [0.1, 0.175, 0.3, 0.5], [0.1, 0.5, 0.3, 0.5], 
		                   [0.1, 0.825, 0.3, 0.5]],
		              14: [[0.3, 0.875, 0.1, 0.625], [0.4, 0.5, 0.6, 0.5], [0.1, 0.375, 0.3, 0.125], 
		                   [0.7, 0.125, 0.9, 0.375], [0.7, 0.875, 0.9, 0.625], [0.9, 0.125, 0.6, 0.5],
		                   [0.9, 0.875, 0.6, 0.5], [0.1, 0.125, 0.4, 0.5], [0.1, 0.875, 0.4, 0.5], 
		                   [0.5, 0.125, 0.5, 0.875]],
		              15: [[0.583, 0.125, 0.25, 0.875], [0.25, 0.5, 0.667, 0.5], [0.583, 0.875, 0.25, 0.125], 
		                   [0.75, 0.125, 0.917, 0.375], [0.75, 0.875, 0.917, 0.625], [0.917, 0.125, 0.667, 0.5],
		                   [0.917, 0.875, 0.667, 0.5], [0.083, 0.175, 0.25, 0.5], [0.083, 0.5, 0.25, 0.5], 
		                   [0.083, 0.825, 0.25, 0.5], [0.417, 0.125, 0.417, 0.875]],
		              16: [[0.083, 0.875, 0.417, 0.125], [0.25, 0.5, 0.75, 0.5], [0.417, 0.875, 0.083, 0.125], 
		                   [0.75, 0.125, 0.75, 0.875], [0.25, 0.125, 0.25, 0.875], [0.917, 0.125, 0.583, 0.875],
		                   [0.917, 0.875, 0.583, 0.125], [0.083, 0.625, 0.25, 0.5], [0.083, 0.375, 0.25, 0.5], 
		                   [0.917, 0.375, 0.75, 0.5], [0.917, 0.625, 0.75, 0.5]],
		              17: [[0.25, 0.5, 0.917, 0.5], [0.083, 0.6, 0.25, 0.5], [0.083, 0.4, 0.25, 0.5], 
		                   [0.083, 0.8, 0.333, 0.7], [0.25, 0.9, 0.417, 0.5], [0.417, 0.9, 0.333, 0.7], 
		                   [0.583, 0.9, 0.75, 0.7], [0.75, 0.9, 0.75, 0.7], [0.917, 0.9, 0.583, 0.5], 
		                   [0.917, 0.7, 0.75, 0.5], [0.917, 0.3, 0.75, 0.5], [0.917, 0.1, 0.583, 0.5],
		                   [0.75, 0.1, 0.75, 0.3], [0.583, 0.1, 0.75, 0.3], [0.417, 0.1, 0.333, 0.3], 
		                   [0.25, 0.1, 0.417, 0.5], [0.083, 0.2, 0.333, 0.3]],
		              18: [[0.083, 0.5, 0.917, 0.5], [0.083, 0.7, 0.25, 0.5], [0.083, 0.3, 0.25, 0.5], 
		                   [0.083, 0.9, 0.417, 0.5], [0.25, 0.9, 0.25, 0.7], [0.417, 0.9, 0.25, 0.7], 
		                   [0.583, 0.9, 0.75, 0.7], [0.75, 0.9, 0.75, 0.7], [0.917, 0.9, 0.583, 0.5], 
		                   [0.917, 0.7, 0.75, 0.5], [0.917, 0.3, 0.75, 0.5], [0.917, 0.1, 0.583, 0.5],
		                   [0.75, 0.1, 0.75, 0.3], [0.583, 0.1, 0.75, 0.3], [0.417, 0.1, 0.25, 0.3], 
		                   [0.25, 0.1, 0.25, 0.3], [0.083, 0.1, 0.417, 0.5]]
		}
		# End of Templates data.

	# List region_data: [WestX, EastX, SouthY, NorthY]
	global region_data
	region_data = []
	for regionLoop in range(iPlayers):
		# Region dimensions
		[fWestLon, fEastLon, fSouthLat, fNorthLat] = templates[iPlayers][regionLoop]
		iWestX = int((iW - 1) * fWestLon)
		iEastX = int((iW - 1) * fEastLon) - 1
		iSouthY = int((iH - 1) * fSouthLat)
		iNorthY = int((iH - 1) * fNorthLat) -1
		region_data.append([iWestX, iEastX, iSouthY, iNorthY])

	# If Buffered, list buffer_data: [WestX, EastX, SouthY, NorthY]
	if userInputLandmass == 1 and iPlayers >= 2 and iPlayers <= 10:
		global buffer_data
		buffer_data = []
		for bufferLoop in range(iPlayers):
			# Buffer dimensions
			[fWestLon, fEastLon, fSouthLat, fNorthLat] = buffers[iPlayers][bufferLoop]
			iWestX = int((iW - 1) * fWestLon)
			iEastX = int((iW - 1) * fEastLon) - 1
			iSouthY = int((iH - 1) * fSouthLat)
			iNorthY = int((iH - 1) * fNorthLat) -1
			buffer_data.append([iWestX, iEastX, iSouthY, iNorthY])
	else: pass

	# center_data: [WestX, EastX, SouthY, NorthY]
	global center_data
	[fWestLon, fEastLon, fSouthLat, fNorthLat] = center_isle[iPlayers]
	iWestX = int((iW - 1) * fWestLon)
	iEastX = int((iW - 1) * fEastLon) - 1
	iSouthY = int((iH - 1) * fSouthLat)
	iNorthY = int((iH - 1) * fNorthLat) -1
	center_data = [iWestX, iEastX, iSouthY, iNorthY]

	# List wheel_data: [[X0, Y0], [X1, Y1], [X2, Y2], etc]
	global wheel_data
	wheel_data = []
	for [fLon, fLat] in the_wheel[iPlayers]:
		iX = int((iW - 1) * fLon)
		iY = int((iH - 1) * fLat)
		wheel_data.append([iX, iY])
	# Return to start plot, completing the wheel.
	[fLon, fLat] = the_wheel[iPlayers][0]
	iX = int((iW - 1) * fLon)
	iY = int((iH - 1) * fLat)
	wheel_data.append([iX, iY])

	# List hub_data: [[startX0, startY0, endX0, endY0], [startX1, startY1, endX1, endY1], etc]
	global hub_data
	hub_data = []
	for [fStartLon, fStartLat, fEndLon, fEndLat] in the_spokes[iPlayers]:
		iStartX = int((iW - 1) * fStartLon)
		iStartY = int((iH - 1) * fStartLat)
		iEndX = int((iW - 1) * fEndLon)
		iEndY = int((iH - 1) * fEndLat)
		hub_data.append([iStartX, iStartY, iEndX, iEndY])
	
	# Successfully generated regions, continue back to C++
	return 0

class WheelMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	# Override InRegion to increase hills, make up for those lost to the ring path.
	def generatePlotsInRegion(self, iWaterPercent, 
	                          iRegionWidth, iRegionHeight, 
	                          iRegionWestX, iRegionSouthY, 
	                          iRegionGrain, iRegionHillsGrain, 
	                          iRegionPlotFlags, iRegionTerrainFlags, 
	                          iRegionFracXExp = -1, iRegionFracYExp = -1, 
	                          bShift = True, iStrip = 15, 
	                          rift_grain = -1, has_center_rift = False, 
	                          invert_heights = False):
		# This is the code to generate each fractal.
		# Determine and pass in the appropriate arguments from the controlling function.
		#
		# Init local variables
		water = iWaterPercent
		iWestX = iRegionWestX
		# Note: if you pass bad regional dimensions so that iEastX > self.iW, BOOM! So don't do that. I could close out that possibility, but better that I not, so that you get an error to warn you of erroneous regional parameters. - Sirian
		iSouthY = iRegionSouthY
		
		# Init the plot types array and the regional fractals
		self.plotTypes = [] # reinit the array for each pass
		self.plotTypes = [PlotTypes.PLOT_OCEAN] * (iRegionWidth*iRegionHeight)
		regionContinentsFrac = CyFractal()
		regionHillsFrac = CyFractal()
		regionPeaksFrac = CyFractal()
		regionContinentsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionGrain, self.dice, iRegionPlotFlags, iRegionFracXExp, iRegionFracYExp)
		regionHillsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionHillsGrain, self.dice, iRegionTerrainFlags, iRegionFracXExp, iRegionFracYExp)
		regionPeaksFrac.fracInit(iRegionWidth, iRegionHeight, iRegionHillsGrain+1, self.dice, iRegionTerrainFlags, iRegionFracXExp, iRegionFracYExp)

		iWaterThreshold = regionContinentsFrac.getHeightFromPercent(water)
		
		#2.15 Start
		if (CyMap().getCustomMapOption(7) == 0):#the original line
			iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((23 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((30 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((70 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((77 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iPeakThreshold = regionPeaksFrac.getHeightFromPercent(self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent())		
		
		else:#if it's green or super green
			iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((18 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((35 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((65 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((82 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iPeakThreshold = min(regionPeaksFrac.getHeightFromPercent(self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent()), 10)
		#end 2.15
			
			
		# Loop through the region's plots
		for x in range(iRegionWidth):
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				val = regionContinentsFrac.getHeight(x,y)
				if val <= iWaterThreshold: pass
				else:
					hillVal = regionHillsFrac.getHeight(x,y)
					if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
						peakVal = regionPeaksFrac.getHeight(x,y)
						if (peakVal <= iPeakThreshold):
							self.plotTypes[i] = PlotTypes.PLOT_PEAK
						else:
							self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						self.plotTypes[i] = PlotTypes.PLOT_LAND

		if bShift:
			# Shift plots to obtain a more natural shape.
			self.shiftRegionPlots(iRegionWidth, iRegionHeight, iStrip)

		# Once the plot types for the region have been generated, they must be
		# applied to the global plot array.
		#
		# Default approach is to ignore water and layer the lands over one another.
		# If you want to layer the water, too, or some other combination, then
		# create a subclass and override this function. Customize in your override.
		#
		# Apply the region's plots to the global plot array.
		for x in range(iRegionWidth):
			wholeworldX = x + iWestX
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				if self.plotTypes[i] == PlotTypes.PLOT_OCEAN: continue
				wholeworldY = y + iSouthY
				iWorld = wholeworldY*self.iW + wholeworldX
				self.wholeworldPlotTypes[iWorld] = self.plotTypes[i]

		# This region is done.
		return

	# Custom genPlotsInRegion to overwrite spoke flatlands with hills while generating the center region.
	def generateCenter(self, iWaterPercent, 
	                   iRegionWidth, iRegionHeight, 
	                   iRegionWestX, iRegionSouthY, 
	                   iRegionGrain, iRegionHillsGrain, 
	                   iRegionPlotFlags, iRegionTerrainFlags, 
	                   iRegionFracXExp = -1, iRegionFracYExp = -1, 
	                   bShift = True, iStrip = 15, 
	                   rift_grain = -1, has_center_rift = False, 
	                   invert_heights = False):
		# This is the code to generate each fractal.
		# Determine and pass in the appropriate arguments from the controlling function.
		#
		# Init local variables
		water = iWaterPercent
		iWestX = iRegionWestX
		# Note: if you pass bad regional dimensions so that iEastX > self.iW, BOOM! So don't do that. I could close out that possibility, but better that I not, so that you get an error to warn you of erroneous regional parameters. - Sirian
		iSouthY = iRegionSouthY
		
		# Init the plot types array and the regional fractals
		self.plotTypes = [] # reinit the array for each pass
		self.plotTypes = [PlotTypes.PLOT_OCEAN] * (iRegionWidth*iRegionHeight)
		regionContinentsFrac = CyFractal()
		regionHillsFrac = CyFractal()
		regionContinentsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionGrain, self.dice, iRegionPlotFlags, iRegionFracXExp, iRegionFracYExp)
		regionHillsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionHillsGrain, self.dice, iRegionTerrainFlags, iRegionFracXExp, iRegionFracYExp)

		iWaterThreshold = regionContinentsFrac.getHeightFromPercent(water)
		
		
		#2.15 Start
		if (CyMap().getCustomMapOption(7) == 0):#the original line
			iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((20 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((30 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((70 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((80 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))		
		
		else:#if it's green or super green	
			iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((15 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((35 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
			iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((65 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
			iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((85 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
		#end 2.15		


		# Loop through the region's plots
		for x in range(iRegionWidth):
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				val = regionContinentsFrac.getHeight(x,y)
				if val <= iWaterThreshold: pass
				else:
					hillVal = regionHillsFrac.getHeight(x,y)
					if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
						self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						self.plotTypes[i] = PlotTypes.PLOT_LAND

		if bShift:
			# Shift plots to obtain a more natural shape.
			self.shiftRegionPlots(iRegionWidth, iRegionHeight, iStrip)

		# Once the plot types for the region have been generated, they must be
		# applied to the global plot array.
		#
		# Default approach is to ignore water and layer the lands over one another.
		# If you want to layer the water, too, or some other combination, then
		# create a subclass and override this function. Customize in your override.
		#
		# Apply the region's plots to the global plot array.
		for x in range(iRegionWidth):
			wholeworldX = x + iWestX
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				if self.plotTypes[i] == PlotTypes.PLOT_OCEAN: continue
				wholeworldY = y + iSouthY
				iWorld = wholeworldY*self.iW + wholeworldX
				self.wholeworldPlotTypes[iWorld] = self.plotTypes[i]

		# The center region is done.
		return

	def generatePlotsByRegion(self, wheel_type):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		iPlayers = self.gc.getGame().countCivPlayersEverAlive()
		userInputAreaType = self.map.getCustomMapOption(1)
		area_grain = 3 - userInputAreaType
		buffer_one = [0, 58, 64, 70]
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		# If Buffered map, add buffers (one fractal each).
		
		if wheel_type == 1 and iPlayers < 11 and iPlayers > 1: # Buffered
			# One buffer per player.
			global buffer_data
			for buffer_loop in range(iPlayers):
				[bufWestX, bufEastX, bufSouthY, bufNorthY] = buffer_data[buffer_loop]
				thisBuffer = 1 + self.dice.get(3, "Random Buffer Type - Wheel PYTHON")
				bufWater = sea + buffer_one[thisBuffer]
				bufGrain = thisBuffer + 1
				
				# Generate the buffer.
				bufWidth = bufEastX - bufWestX + 1
				bufHeight = bufNorthY - bufSouthY + 1
				self.generatePlotsInRegion(bufWater,
				                           bufWidth, bufHeight,
				                           bufWestX, bufSouthY,
				                           bufGrain, 3,
				                           self.iRoundFlags, self.iTerrainFlags,
				                           6, 6,
				                           True, 3,
				                           -1, False,
				                           False
				                           )
		else: pass

		# Add players' regions (two fractals each to ensure cohesion).
		global region_data
		for region_loop in range(iPlayers):
			[regWestX, regEastX, regSouthY, regNorthY] = region_data[region_loop]
			# Main fractal
			regWidth = regEastX - regWestX + 1
			regHeight = regNorthY - regSouthY + 1
			self.generatePlotsInRegion(55 + sea,
			                           regWidth, regHeight,
			                           regWestX, regSouthY,
			                           area_grain, 4,
			                           self.iRoundFlags, self.iTerrainFlags,
			                           6, 6,
			                           True, 3,
			                           -1, False,
			                           False
			                           )

			# Core fractal to increase cohesion
			coreWestX = regWestX + int(regWidth * 0.25)
			coreEastX = regEastX - int(regWidth * 0.25)
			coreSouthY = regSouthY + int(regHeight * 0.25)
			coreNorthY = regNorthY - int(regHeight * 0.25)
			coreWidth = coreEastX - coreWestX + 1
			coreHeight = coreNorthY - coreSouthY + 1
			self.generatePlotsInRegion(65,
			                           coreWidth, coreHeight,
			                           coreWestX, coreSouthY,
			                           1, 3,
			                           self.iHorzFlags, self.iTerrainFlags,
			                           5, 5,
			                           True, 3,
			                           -1, False,
			                           False
			                           )

		# Draw the wheel.
		global wheel_data
		linewidth = 1 + self.map.getCustomMapOption(2)
		iWH = self.iW * self.iH
		offsetstart = 0 - int(linewidth/2)
		offsetrange = range(offsetstart, offsetstart + linewidth)

		for wheel_loop in range(len(wheel_data) - 1):
			[startx, starty] = wheel_data[wheel_loop]
			[endx, endy] = wheel_data[wheel_loop + 1]

			if abs(endy-starty) < abs(endx-startx):
				# line is closer to horizontal
				if startx > endx:
					startx, starty, endx, endy = endx, endy, startx, starty # swap start and end
				dx = endx-startx
				dy = endy-starty
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dy)/float(dx)
				y = starty
				for x in range(startx, endx+1):
					for offset in offsetrange:
						if map.isPlot(x, int(round(y+offset))):
							i = map.plotNum(x, int(round(y+offset)))
							self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND
					y += slope
			else:
				# line is closer to vertical
				if starty > endy:
					startx, starty, endx, endy = endx, endy, startx, starty # swap start and end
				dx, dy = endx-startx, endy-starty
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dx)/float(dy)
				x = startx
				for y in range(starty, endy+1):
					for offset in offsetrange:
						if map.isPlot(int(round(x+offset)), y):
							i = map.plotNum(int(round(x+offset)), y)
							self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND
					x += slope
		
		# Draw the spokes.
		global hub_data
		linewidth = 1 + self.map.getCustomMapOption(3)
		iWH = self.iW * self.iH
		offsetstart = 0 - int(linewidth/2)
		offsetrange = range(offsetstart, offsetstart + linewidth)

		for hub_loop in range(len(hub_data)):
			[startx, starty, endx, endy] = hub_data[hub_loop]

			if abs(endy-starty) < abs(endx-startx):
				# line is closer to horizontal
				if startx > endx:
					startx, starty, endx, endy = endx, endy, startx, starty # swap start and end
				dx = endx-startx
				dy = endy-starty
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dy)/float(dx)
				y = starty
				for x in range(startx, endx+1):
					for offset in offsetrange:
						if map.isPlot(x, int(round(y+offset))):
							i = map.plotNum(x, int(round(y+offset)))
							self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND
					y += slope
			else:
				# line is closer to vertical
				if starty > endy:
					startx, starty, endx, endy = endx, endy, startx, starty # swap start and end
				dx, dy = endx-startx, endy-starty
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dx)/float(dy)
				x = startx
				for y in range(starty, endy+1):
					for offset in offsetrange:
						if map.isPlot(int(round(x+offset)), y):
							i = map.plotNum(int(round(x+offset)), y)
							self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND
					x += slope

		# Add center isle(s).
		global center_data
		[cenWestX, cenEastX, cenSouthY, cenNorthY] = center_data
		cenWidth = cenEastX - cenWestX + 1
		cenHeight = cenNorthY - cenSouthY + 1
		thisBuffer = 1 + self.dice.get(3, "Random Buffer Type - Wheel PYTHON")
		bufWater = sea + buffer_one[thisBuffer]
		bufGrain = thisBuffer + 1
		self.generateCenter(bufWater,
		                    cenWidth, cenHeight,
		                    cenWestX, cenSouthY,
		                    bufGrain, 4,
		                    self.iRoundFlags, self.iTerrainFlags,
		                    -1, -1,
		                    True, 5,
		                    -1, False,
		                    False
		                    )

		# All regions have been processed. Plot Type generation completed.
		return self.wholeworldPlotTypes

'''
Regional Variables Key:

iWaterPercent,
iRegionWidth, iRegionHeight,
iRegionWestX, iRegionSouthY,
iRegionGrain, iRegionHillsGrain,
iRegionPlotFlags, iRegionTerrainFlags,
iRegionFracXExp, iRegionFracYExp,
bShift, iStrip,
rift_grain, has_center_rift,
invert_heights
'''

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Wheel) ...")
	gc = CyGlobalContext()
	global map
	map = CyMap()
	
	# Check for valid number of players.
	global bSuccessFlag
	if bSuccessFlag: pass
	else:
		fractal_world = FractalWorld()
		fractal_world.initFractal(polar = True)
		return fractal_world.generatePlotTypes()

	# Player count is valid, produce the map.
	fractal_world = WheelMultilayeredFractal()
	userInputLandmass = map.getCustomMapOption(0)
	if userInputLandmass == 1: # Buffered.
		wheel_type = 1
	else: # Normal
		wheel_type = 0
	return fractal_world.generatePlotsByRegion(wheel_type)

class WheelTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	"If iDesertPercent=35, then about 35% of all land will be desert. Plains is similar. \
	Note that all percentages are approximate, as values have to be roughened to achieve a natural look."
	
	#2.15
	'''def __init__(self, iDesertPercent=10, iPlainsPercent=25,
	             iIcePercent=50, iTundraPercent=35,
	             fracXExp=-1, fracYExp=-1, grain_amount=5):'''#that's legacy GreenWheel
				 
	def __init__(self, iDesertPercent=20, iPlainsPercent=25,
	             iIcePercent=50, iTundraPercent=35,
	             fracXExp=-1, fracYExp=-1, grain_amount=5):#that's original Wheel


		if (CyMap().getCustomMapOption(7) == 1):#green
			iDesertPercent = 10
			iPlainPercent = 25
			
		if (CyMap().getCustomMapOption(7) == 2):#Super green
			iDesertPercent = 0
			iPlainPercent = 25				 

		if (CyMap().getCustomMapOption(8) == 1):#Tundra Only
			iIcePercent=0
			iTundraPercent=90	

		if (CyMap().getCustomMapOption(8) == 2):#Plains Only
			iIcePercent=0
			iTundraPercent=0	

		if (CyMap().getCustomMapOption(8) == 3):#Grassland Only Need an override later
			iIcePercent=0
			iTundraPercent=0			
		
		#end 2.15
		
		self.gc = CyGlobalContext()
		self.map = CyMap()

		global center_data
		[self.cenWestX, self.cenEastX, self.cenSouthY, self.cenNorthY] = center_data

		grain_amount += self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()
		
		self.grain_amount = grain_amount

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()
		
		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
		if self.map.isWrapX(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_X
		if self.map.isWrapY(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_Y

		self.main=CyFractal()
		self.center=CyFractal()

		iDesertPercent += self.gc.getClimateInfo(self.map.getClimate()).getDesertPercentChange()
		if self.gc.getClimateInfo(self.map.getClimate()).getRandIceLatitude() > 0.25: # Cold Climate
			iIcePercent += 10
			iTundraPercent += 5
			iPlainsPercent += 25
		if self.gc.getClimateInfo(self.map.getClimate()).getJungleLatitude() < 5: # Tropical Climate
			iIcePercent = 15
			iTundraPercent = 20

		self.iDesertBottomPercent = 100 - iDesertPercent
		self.iPlainsBottomPercent = self.iDesertBottomPercent - iPlainsPercent
		self.iIceBottomPercent = 100 - iIcePercent
		self.iTundraBottomPercent = self.iIceBottomPercent - iTundraPercent

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()
		
	def initFractals(self):
		self.main.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iDesertBottom = self.main.getHeightFromPercent(self.iDesertBottomPercent)
		self.iPlainsBottom = self.main.getHeightFromPercent(self.iPlainsBottomPercent)

		self.center.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iIceBottom = self.center.getHeightFromPercent(self.iIceBottomPercent)
		self.iTundraBottom = self.center.getHeightFromPercent(self.iTundraBottomPercent)

		self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
		self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
		self.terrainIce = self.gc.getInfoTypeForString("TERRAIN_SNOW")
		self.terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
		self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")

	def generateTerrainAtPlot(self,iX,iY):
		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		if ((iX >= self.cenWestX and iX <= self.cenEastX) and (iY >= self.cenSouthY and iY <= self.cenNorthY)):
			# Center region
			val = self.center.getHeight(iX, iY)
			if val >= self.iIceBottom:
				terrainVal = self.terrainIce
			elif val >= self.iTundraBottom:
				terrainVal = self.terrainTundra
			else:
				#2.15
				if (CyMap().getCustomMapOption(8) == 3):
					terrainVal = self.terrainGrass
				else:
					terrainVal = self.terrainPlains
				#end 2.15
				
		else:
			# Main region
			val = self.main.getHeight(iX, iY)
			if val >= self.iDesertBottom:
				terrainVal = self.terrainDesert
			elif val >= self.iPlainsBottom:
				terrainVal = self.terrainPlains
			else:
				terrainVal = self.terrainGrass

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Wheel) ...")
	terraingen = WheelTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class WheelFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def __init__(self, iJunglePercent=10, iForestPercent=40,
	             forest_grain=6, fracXExp=-1, fracYExp=-1):
		
		self.gc = CyGlobalContext()
		self.map = CyMap()
		self.mapRand = self.gc.getGame().getMapRand()
		self.forests = CyFractal()
		global center_data
		[self.cenWestX, self.cenEastX, self.cenSouthY, self.cenNorthY] = center_data
		
		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
		if self.map.isWrapX(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_X
		if self.map.isWrapY(): self.iFlags += CyFractal.FracVals.FRAC_WRAP_Y

		self.iGridW = self.map.getGridWidth()
		self.iGridH = self.map.getGridHeight()
		self.pineWestX = int(self.cenWestX * 0.7)
		self.pineEastX = self.iGridW - int((self.cenEastX + self.iGridW - 1) * 0.35) - 1
		self.pineSouthY = int(self.cenSouthY * 0.7)
		self.pineNorthY = self.iGridH - int((self.cenNorthY + self.iGridH - 1) * 0.35) - 1

		self.iJunglePercent = iJunglePercent
		self.iForestPercent = iForestPercent
		self.iIceChance = 15
		if self.gc.getClimateInfo(self.map.getClimate()).getJungleLatitude() < 5:
			self.iJunglePercent += 25 # Double jungles if Tropical Climate
			self.iForestPercent -= 10 # Reduce forests if Tropical
			self.iIceChance = 30

		if self.gc.getClimateInfo(self.map.getClimate()).getRandIceLatitude() > 0.25:
			self.iIceChance = 6 # Add more ice if Cold Climate
			self.iJunglePercent -= 10 # Reduce jungles if Cold Climate
			self.iForestPercent += 20 # Add forests if Cold
		
		if self.gc.getClimateInfo(self.map.getClimate()).getDesertPercentChange() >= 10:
			self.iJunglePercent = 15 # Reduce foliage if Arid Climate
			self.iForestPercent = 20

		forest_grain += self.gc.getWorldInfo(self.map.getWorldSize()).getFeatureGrainChange()

		self.forest_grain = forest_grain

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.__initFractals()
		self.__initFeatureTypes()
	
	def __initFractals(self):
		self.forests.fracInit(self.iGridW, self.iGridH, self.forest_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		
		self.iJungleBottom = self.forests.getHeightFromPercent(100 - self.iJunglePercent)
		self.iForestLevel = self.forests.getHeightFromPercent(self.iForestPercent)

	def __initFeatureTypes(self):
		self.featureIce = self.gc.getInfoTypeForString("FEATURE_ICE")
		self.featureJungle = self.gc.getInfoTypeForString("FEATURE_JUNGLE")
		self.featureForest = self.gc.getInfoTypeForString("FEATURE_FOREST")
		self.featureOasis = self.gc.getInfoTypeForString("FEATURE_OASIS")
	
	def addFeaturesAtPlot(self, iX, iY):
		"adds any appropriate features at the plot (iX, iY) where (0,0) is in the SW"
		pPlot = self.map.sPlot(iX, iY)

		for iI in range(self.gc.getNumFeatureInfos()):
			if pPlot.canHaveFeature(iI):
				if self.mapRand.get(10000, "Add Feature PYTHON") < self.gc.getFeatureInfo(iI).getAppearanceProbability():
					pPlot.setFeatureType(iI, -1)

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addIceAtPlot(pPlot, iX, iY)
			
		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addJunglesAtPlot(pPlot, iX, iY)
			
		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addForestsAtPlot(pPlot, iX, iY)
		
		
		
	def addIceAtPlot(self, pPlot, iX, iY):
		if pPlot.isWater() and ((iX >= self.cenWestX and iX <= self.cenEastX) and (iY >= self.cenSouthY and iY <= self.cenNorthY)):
			rand = self.mapRand.get(self.iIceChance, "Add Ice PYTHON")
			if rand == 4:
				pPlot.setFeatureType(self.featureIce, -1)
	
	def addJunglesAtPlot(self, pPlot, iX, iY):
		# Warning! This version of Jungles is using the forest fractal!
		if pPlot.canHaveFeature(self.featureJungle) and not ((iX >= self.cenWestX and iX <= self.cenEastX) and (iY >= self.cenSouthY and iY <= self.cenNorthY)):
			iJungleHeight = self.forests.getHeight(iX, iY)
			if iJungleHeight >= self.iJungleBottom:
				pPlot.setFeatureType(self.featureJungle, -1)
	
	def addForestsAtPlot(self, pPlot, iX, iY):
		if pPlot.canHaveFeature(self.featureForest):
			if self.forests.getHeight(iX, iY) <= self.iForestLevel:
				if ((iX >= self.cenWestX and iX <= self.cenEastX) and (iY >= self.cenSouthY and iY <= self.cenNorthY)):
					forestVar = 2
				elif (iX <= self.pineWestX or iX >= self.pineEastX or iY <= self.pineSouthY or iY >= self.pineNorthY):
					forestVar = 0
				else:
					forestVar = 1
				pPlot.setFeatureType(self.featureForest, forestVar)

def addFeatures():
	NiTextOut("Adding Features (Python Wheel) ...")
	featuregen = WheelFeatureGenerator()
	featuregen.addFeatures()
	return 0
	
def assignStartingPlots():
	global bSuccessFlag
	if bSuccessFlag == False:
		CyPythonMgr().allowDefaultImpl()
	
	global start_plots
	global iPlotShift
	global shuffledPlayers
	global region_data
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	start_plots = []
	shuffledPlayers = []

	# Set variance for start plots according to map size vs number of players.
	map_size = map.getWorldSize()
	sizevalues = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(2, 3),
		WorldSizeTypes.WORLDSIZE_TINY:		(2, 4),
		WorldSizeTypes.WORLDSIZE_SMALL:		(3, 6),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(4, 10),
		WorldSizeTypes.WORLDSIZE_LARGE:		(6, 12),
		WorldSizeTypes.WORLDSIZE_HUGE:		(6, 18)
		}
	(threeVar, twoVar) = sizevalues[map_size]
	if iPlayers <= threeVar:
		iPlotShift = 3
	elif iPlayers <= twoVar:
		iPlotShift = 2
	else:
		iPlotShift = 1

	# Assign start plots for each player area.
	for region_loop in range(iPlayers):
		[regWestX, regEastX, regSouthY, regNorthY] = region_data[region_loop]
		# Main fractal
		regWidth = regEastX - regWestX + 1
		regHeight = regNorthY - regSouthY + 1
		iStartX = regWestX + int(regWidth / 2)
		iStartY = regSouthY + int(regHeight / 2)
		start_plots.append([iStartX, iStartY])

	# Shuffle start points so that players are assigned templateIDs at random.
	player_list = []
	for playerLoop in range(gc.getGame().countCivPlayersEverAlive()):
		player_list.append(playerLoop)
	shuffledPlayers = []
	for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Template IDs - Hub PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]
	
	# Done setting up variables. Proceed to normal process.
	CyPythonMgr().allowDefaultImpl()

def minStartingDistanceModifier():
	global bSuccessFlag
	if bSuccessFlag == True:
		return -95
	else:
		return -50

def findStartingPlot(argsList):
	# Set up for maximum of 18 players! If more, use default implementation.
	global bSuccessFlag
	if bSuccessFlag == False:
		return CvMapGeneratorUtil.findStartingPlot(playerID, true)

	[playerID] = argsList
	
	if isBTPon:#2.22
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		if iNumSpectators > 0:
			if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
			#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
				return -1		

	def isValid(playerID, x, y):
		gc = CyGlobalContext()
		map = CyMap()
		pPlot = map.plot(x, y)
		# Check to ensure the plot is on the main landmass.
		if (pPlot.getArea() != map.findBiggestArea(False).getID()):
			return false

		iW = map.getGridWidth()
		iH = map.getGridHeight()
		iPlayers = gc.getGame().countCivPlayersEverAlive()
		global start_plots
		global iPlotShift
		global shuffledPlayers
		playerTemplateAssignment = shuffledPlayers[playerID]
		[iStartX, iStartY] = start_plots[playerTemplateAssignment]
		
		# Now check for eligibility according to the defintions found in the template.
		westX = max(2, iStartX - iPlotShift)
		eastX = min(iW - 3, iStartX + iPlotShift)
		southY = max(2, iStartY - iPlotShift)
		northY = min(iH - 3, iStartY + iPlotShift)
		if x < westX or x > eastX or y < southY or y > northY:
			return false
		else:
			return true

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)

def normalizeRemovePeaks():
	return None

def normalizeRemoveBadTerrain():
	return None

def normalizeAddGoodTerrain():
	return None
	
def startHumansOnSameTile():

	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(10) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(10) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)
			
	if isBTPon:#2.25
		if (CyMap().getCustomMapOption(16) > 0):
			if (CyMap().getCustomMapOption(16)  == 1):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,100,0,0,5)
			if (CyMap().getCustomMapOption(16)  == 2):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,0,5)				
			if (CyMap().getCustomMapOption(16)  == 3):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,100,5)			


	if (CyMap().getCustomMapOption(17) > 0):
		if isBTPon:
			iOption = CyGlobalContext().getInfoTypeForString("GAMEOPTION_DISABLE_CIRCUMNAVIGATION")
			CyGlobalContext().getGame().setOption(iOption, True)
		else:
			CyGlobalContext().getGame().makeCircumnavigated()

	if (CyMap().getCustomMapOption(11) == 1):
		return True	

def normalizeStartingPlotLocations():

	if (CyMap().getCustomMapOption(12) == 1):
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
	else:
		CyPythonMgr().allowDefaultImpl()	
		

def BTGFreeUnit():

	if (CyMap().getCustomMapOption(14) == 0):
		return -1
	elif (CyMap().getCustomMapOption(14) == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (CyMap().getCustomMapOption(14) == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (CyMap().getCustomMapOption(14) == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():

	iCount = CyMap().getCustomMapOption(15)	
		
	return iCount	
	
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