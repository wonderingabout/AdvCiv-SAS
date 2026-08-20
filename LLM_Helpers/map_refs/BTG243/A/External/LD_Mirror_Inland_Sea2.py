#
#	FILE:	 LD_Mirror_Inland_Sea.py
#	AUTHOR:  Leszek Deska ldeska@wp.pl, based on Inland_Sea 
# by Bob Thomas (Sirian) and Mirror also by Bob Thomas (Sirian)
#	CONTRIB: Bob Thomas (Sirian), Soren Johnson, Andy Szybalski
#	PURPOSE: Regional map script - Loosely simulates a Mediterranean type
#	         temperate zone with civs ringing a central sea, modified to be ideally
#          mirrored, so left half of map is reflected and put on right side.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import HintedWorld

hinted_world = None

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_INLAND_SEA_DESCR"

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 0

def getNumHiddenCustomMapOptions():
	return 0

def getWrapX():
	return false
	
def getWrapY():
	return false

def normalizeAddExtras():
	return None

def beforeGeneration():
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	global team_num
	team_num = []
	team_index = 0
	for teamCheckLoop in range(18):
		if CyGlobalContext().getTeam(teamCheckLoop).isEverAlive():
			team_num.append(team_index)
			team_index += 1
		else:
			team_num.append(-1)

	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()

	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 6, 4, 3, 2, 2, 2, 4, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1]
	
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
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

class ISFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
		lat = CvMapGeneratorUtil.FeatureGenerator.getLatitudeAtPlot(self, iX, iY) 	# range [0,1]
		lat = 0.07 + 0.56*lat				# range [0.07, 0.56]
		return lat
	
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

def generateTerrainTypes():
	# MIRRORIZE PLOTS
	gc = CyGlobalContext()
	map = CyMap()
	
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY

	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setPlotType(rPlot.getPlotType(), false, false)
	
	# Smooth any graphical glitches these changes may have produced.
	map.recalculateAreas()

	NiTextOut("Generating Terrain (Python Inland Sea) ...")
	terraingen = ISTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addLakes():
	# MIRRORIZE TERRAIN
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY

	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setTerrainType(rPlot.getTerrainType(), false, false)

	# MIRRORIZE RIVERS
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY
	reflect_z = lambda x: iW - iX - 2
	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			pPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
			if iX != (iW / 2) - 1:
				pPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			sPlot = map.plot(reflect_z(iX), reflect_y(iY))
			if rPlot.isNOfRiver():
				if rPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
					rivDir = CardinalDirectionTypes.CARDINALDIRECTION_WEST
				else:
					rivDir = CardinalDirectionTypes.CARDINALDIRECTION_EAST
				pPlot.setNOfRiver(true, rivDir)
			if sPlot.isWOfRiver():
				rivDir = sPlot.getRiverNSDirection()
				pPlot.setWOfRiver(true, rivDir)

	return CyPythonMgr().allowDefaultImpl()

def addFeatures():
	# MIRRORIZE LAKES
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY

	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			if pPlot.getPlotType() != rPlot.getPlotType():
				pPlot.setPlotType(rPlot.getPlotType(), false, false)

	# Smooth any graphical glitches these changes may have produced.
	map.recalculateAreas()

	NiTextOut("Adding Features (Python Inland Sea) ...")
	featuregen = ISFeatureGenerator()
	featuregen.addFeatures()
	return 0

def addGoodies():
	# MIRRORIZE FEATURES AND BONUSES
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY

	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setFeatureType(rPlot.getFeatureType(), -1)
			pPlot.setBonusType(rPlot.getBonusType(-1))
	
	# Now add the goodies.
	return CyPythonMgr().allowDefaultImpl()

def afterGeneration():
	# MIRRORIZE GOODIES
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iW - iX - 1
	reflect_y = lambda y: iY

	for iX in range(iW / 2):
		for iY in range(iH):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setImprovementType(rPlot.getImprovementType())
	
	# All done!
	return None

def normalizeAddRiver():
	return None

def normalizeRemovePeaks():
	return None

def normalizeAddLakes():
	return None

def normalizeRemoveBadFeatures():
	return None

def normalizeRemoveBadTerrain():
	return None

def normalizeAddFoodBonuses():
	return None

def normalizeAddGoodTerrain():
	return None

def assignStartingPlots():
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	global shuffle
	global shuffledTeams
	global assignedPlayers
	assignedPlayers = [0] * gc.getGame().countCivTeamsEverAlive()
	print assignedPlayers
	shuffle = gc.getGame().getMapRand().get(2, "Start Location Shuffle - PYTHON")
	if gc.getGame().countCivTeamsEverAlive() < 5:
		team_list = [0, 1, 2, 3]
		shuffledTeams = []
		for teamLoop in range(gc.getGame().countCivTeamsEverAlive()):
			iChooseTeam = dice.get(len(team_list), "Shuffling Regions - TBG PYTHON")
			shuffledTeams.append(team_list[iChooseTeam])
			del team_list[iChooseTeam]

	# For Lakes and Continents settings, ensure that starts are all placed on the biggest landmass on each side.
	global biggest_areas
	biggest_areas = []
	areas = CvMapGeneratorUtil.getAreas()
	area_sizes = [(area.getNumTiles(), area.getID()) for area in areas if not area.isWater()]
	area_sizes.sort() # sort by size -- biggest areas last.
	
	# pop the biggest two areas off the list.
	area_size, area_ID = area_sizes.pop()
	biggest_areas.append(area_ID)
	if area_sizes != []:
		area_size, area_ID = area_sizes.pop()
		biggest_areas.append(area_ID)

	# First check to see if teams chose to "Start Separated" or "Start Anywhere".
	map = CyMap()
	userInputProximity = 0#map.getCustomMapOption(1)
	if userInputProximity == 1: # Teams set to Start Separated. Use default impl.
		CyPythonMgr().allowDefaultImpl()
		return

	# Shuffle the players.
	global playersOnTeamOne
	global playersOnTeamTwo
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	playersOnTeamOne = []
	playersOnTeamTwo = []
	
	player_list = []
	for plrCheckLoop in range(18):
		if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
			player_list.append(plrCheckLoop)
	shuffledPlayers = []
	for playerLoopTwo in range(iPlayers):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Player Order - Mirror PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]

	if userInputProximity == 2: # Teams set to Start Anywhere!
		def isValidToStartAnywhere(playerID, x, y):
			global biggest_areas
			global terrainRoll
			userInputTerrain = 0#CyMap().getCustomMapOption(2)
			if userInputTerrain < 3 or (userInputTerrain == 5 and terrainRoll < 6):
				pPlot = CyMap().plot(x, y)
				areaID = pPlot.getArea()
				if areaID not in biggest_areas:
					return false
			return true

		# Since the default alternates by team, must use the shuffled players list to assign starting locs.
		# This will provide a truly random order, which may or may not be "fair". But hey, starting anywhere means ANYwhere. OK?
		for playerID in shuffledPlayers:
			player = gc.getPlayer(playerID)
			startPlot = CvMapGeneratorUtil.findStartingPlot(playerID, isValidToStartAnywhere)
			sPlot = map.plotByIndex(startPlot)
			player.setStartingPlot(sPlot, true)
		# All done.
		return None

	# OK, so the teams have chosen to Start Together.
	#
	# Check for the special case of two teams with even players.
	# If found, force perfect mirrorization of start plots!
	#
	# (This is necessary because the default start plot process 
	# resolves "ties" differently on each side due to minor
	# differences in the order of operations. Odd but true!)
	#
	iTeams = gc.getGame().countCivTeamsEverAlive()
	if iTeams != 2:
		CyPythonMgr().allowDefaultImpl()
		return
	team_one = gc.getTeam(0)
	team_two = gc.getTeam(1)
	if team_one.getNumMembers() != team_two.getNumMembers():
		CyPythonMgr().allowDefaultImpl()
		return

	# We are dealing with two teams who are evenly matched.
	# Assign all start plots for the first team, then mirrorize the locations for the second team!
	# Start by determining which players are on which teams.
	for iLoop in range(iPlayers):
		thisPlayerID = shuffledPlayers[iLoop]
		this_player = gc.getPlayer(thisPlayerID)
		teamID = gc.getPlayer(thisPlayerID).getTeam()
		print("Player: ", thisPlayerID, " Team: ", teamID)
		if teamID == 1:
			playersOnTeamTwo.append(shuffledPlayers[iLoop])
		else:
			playersOnTeamOne.append(shuffledPlayers[iLoop])
	
	# Now we pick a team to assign to the left side and assign them there.
	userInputPlots = 0#map.getCustomMapOption(0)
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	if userInputPlots == 0: # Reflection
		reflect_x = lambda x: iW - iX - 1
		reflect_y = lambda y: iY
	elif userInputPlots == 1: # Inversion
		reflect_x = lambda x: iW - iX - 1
		reflect_y = lambda y: iH - iY - 1
	elif userInputPlots == 2: # Copy
		reflect_x = lambda x: iX + (iW / 2)
		reflect_y = lambda y: iY
	else: # userInputPlots == 3: Opposite
		reflect_x = lambda x: iX + (iW / 2)
		reflect_y = lambda y: iH - iY - 1

	def isValidForMirror(playerID, x, y):
		global biggest_areas
		global terrainRoll
		userInputTerrain = 0#CyMap().getCustomMapOption(2)
		if userInputTerrain < 3 or (userInputTerrain == 5 and terrainRoll < 6):
			pPlot = CyMap().plot(x, y)
			areaID = pPlot.getArea()
			if areaID not in biggest_areas:
				return false

		userInputPlots = 0#CyMap().getCustomMapOption(0)
		iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
		teamID = CyGlobalContext().getPlayer(playerID).getTeam()
		iW = CyMap().getGridWidth()

		# Two Evenly-Matched Teams, Start Together
		if iPlayers > 2 and userInputPlots <= 1 and x <= iW * 0.4:
			return true
		if iPlayers > 2 and userInputPlots >= 2 and x >= iW * 0.1 and x <= iW * 0.4:
			return true
		# 1 vs 1 game, so make sure the players start farther apart!
		if iPlayers == 2 and userInputPlots <= 1 and x <= iW * 0.2:
			return true
		if iPlayers == 2 and userInputPlots >= 2 and x >= iW * 0.2 and x <= iW * 0.3:
			return true
		# if not true, then false! (Duh? Well, the program still has to be told.)
		return false

	if shuffle: # We will put team two on the left.
		teamOneIndex = 0
		for thisPlayer in playersOnTeamTwo:
			player = gc.getPlayer(thisPlayer)
			startPlot = CvMapGeneratorUtil.findStartingPlot(thisPlayer, isValidForMirror)
			sPlot = map.plotByIndex(startPlot)
			player.setStartingPlot(sPlot, true)
			iX = sPlot.getX()
			iY = sPlot.getY()
			mirror_x = reflect_x(iX)
			mirror_y = reflect_y(iY)
			opposite_player = gc.getPlayer(playersOnTeamOne[teamOneIndex])
			oppositePlot = map.plot(mirror_x, mirror_y)
			opposite_player.setStartingPlot(oppositePlot, true)
			teamOneIndex += 1
	else: # will put team one on the left.
		teamTwoIndex = 0
		for thisPlayer in playersOnTeamOne:
			player = gc.getPlayer(thisPlayer)
			startPlot = CvMapGeneratorUtil.findStartingPlot(thisPlayer, isValidForMirror)
			sPlot = map.plotByIndex(startPlot)
			player.setStartingPlot(sPlot, true)
			iX = sPlot.getX()
			iY = sPlot.getY()
			mirror_x = reflect_x(iX)
			mirror_y = reflect_y(iY)
			opposite_player = gc.getPlayer(playersOnTeamTwo[teamTwoIndex])
			oppositePlot = map.plot(mirror_x, mirror_y)
			opposite_player.setStartingPlot(oppositePlot, true)
			teamTwoIndex += 1
			
	# All done.
	return None
	
def findStartingPlot(argsList):
	[playerID] = argsList
	global assignedPlayers
	global team_num
	thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
	teamID = team_num[thisTeamID]
	
	assignedPlayers[teamID] += 1

	def isValid(playerID, x, y):
		global biggest_areas
		global terrainRoll
		userInputTerrain = 0#CyMap().getCustomMapOption(2)
		if userInputTerrain < 3 or (userInputTerrain == 5 and terrainRoll < 6):
			pPlot = CyMap().plot(x, y)
			areaID = pPlot.getArea()
			if areaID not in biggest_areas:
				return false

		map = CyMap()
		numTeams = CyGlobalContext().getGame().countCivTeamsAlive()
		if numTeams > 4 or numTeams < 2: # Put em anywhere, and let the normalizer sort em out.
			return true
		userInputProximity = 0#map.getCustomMapOption(1)
		if userInputProximity == 2: # Start anywhere!
			return true
		global shuffle
		global shuffledTeams
		global team_num
		thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
		teamID = team_num[thisTeamID]
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		
		# Two Teams, Start Together
		if numTeams == 2 and userInputProximity == 0: # Two teams, Start Together
			if teamID == 0 and shuffle and x >= iW * 0.75:
				return true
			if teamID == 1 and not shuffle and x >= iW * 0.75:
				return true
			if teamID == 0 and not shuffle and x <= iW * 0.25:
				return true
			if teamID == 1 and shuffle and x <= iW * 0.25:
				return true
			return false

		# Three or Four Teams
		elif (numTeams == 3 or numTeams == 4) and userInputProximity == 0: # 3 or 4 teams, Start Together
			corner = shuffledTeams[teamID]
			if corner == 0 and x <= iW * 0.4 and y <= iH * 0.4:
				return true
			if corner == 1 and x >= iW * 0.6 and y <= iH * 0.4:
				return true
			if corner == 2 and x <= iW * 0.4 and y >= iH * 0.6:
				return true
			if corner == 3 and x >= iW * 0.6 and y >= iH * 0.6:
				return true
			return false
		elif (numTeams == 3 or numTeams == 4) and userInputProximity == 1: # 3 or 4 teams, Start Separated
			corner = shuffledTeams[teamID] + assignedPlayers[teamID]
			while corner >= 4:
				corner -= 4
			if corner == 0 and x <= iW * 0.4 and y <= iH * 0.4:
				return true
			if corner == 1 and x >= iW * 0.6 and y <= iH * 0.4:
				return true
			if corner == 2 and x <= iW * 0.4 and y >= iH * 0.6:
				return true
			if corner == 3 and x >= iW * 0.6 and y >= iH * 0.6:
				return true
			return false

		# Two Teams, Start Separated
		elif numTeams == 2 and userInputProximity == 1: # Two teams, Start Separated
			if (shuffle and teamID == 0) or (not shuffle and teamID == 1):
				side = assignedPlayers[teamID]
			else:
				side = 1 + assignedPlayers[teamID]
			while side >= 2:
				side -= 2
			if teamID == 0 and side and x >= iW * 0.75:
				return true
			if teamID == 1 and not side and x >= iW * 0.75:
				return true
			if teamID == 0 and not side and x <= iW * 0.25:
				return true
			if teamID == 1 and side and x <= iW * 0.25:
				return true
			return false

		# All conditions have failed? Wow. Is that even possible? :)
		return true
	
	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)

def normalizeStartingPlotLocations():
	numTeams = CyGlobalContext().getGame().countCivTeamsAlive()
	userInputProximity = 0#CyMap().getCustomMapOption(1)
	if (numTeams > 4 or numTeams < 2) and userInputProximity == 0:
		CyPythonMgr().allowDefaultImpl()
	else:
		return None
