#
# 2018 - Penny - Start from TBG map and add pieces
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import HintedWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

import math
import sys
import random
from CvMapGeneratorUtil import MultilayeredFractal
from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()#2.18


#import BugUtil

def getDescription():
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return "A complete redesign of what Battleground 4 corners option was aiming to do. Here the land of each player is perfectly squared-shaped and is linked to the other ones diagonally. "

def getDescriptionTitleTwo():
	return "The map can be toroidal, and each player should have its own square land, so it can be 4, 6 or 8 squares"

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "The choice of the 'bridge's terrain' will have a huge impact on the actual proximity of the teams, it might even be marsh making water access also much quicker"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Look at the notes to know how many territories and which sizes to choose"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Good for larger teamers, toroidal will be much more aggressive than just cylindrical wrap"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Units that go through hilly land (Impis, Keshiks, Fast Workers...) will be extremely valuable to go through the middle"

def getNumCustomMapOptions():
#	BugUtil.debug("Team_Battleground: getNumCustomMapOptions")
	return 15
	
def getNumHiddenCustomMapOptions():
	return 0
	
def getCustomMapOptionName(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionName")
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:	"Territories",
		2:  "Bridge Count",
		3:	"Bridge Terrain",
		4:	"Oil and Aluminium",
		5:	"Elephant",
		6:	"Precious Metal",
		7:	"BTG Resources",		
		8:	"BTG Forest Type",
		9:	"BTG Start Position",
		10: "Starting Units",
		11:	"Player Land Size",		
		12:	"Notes",	
		13:	"BTG Spectator Notes",
		14:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	3,
		2:	4,
		3:	7,
		4:	2,
		5:	2,
		6:	2,
		7:	3,
		8:	5,
		9:	3,
		10:	2,
		11:	4,
		12:	4,
		13:	2,
		14:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDescAt")
	[iOption, iSelection] = argsList

	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "4 Territories",
			1: "6 Territories",
			2: "8 Territories"			
			},
		2:	{
			0: "Yes - All bridges (4, 6 or 8)",
			1: "Yes - Central and corner bridges (2, 4 or 6)",
			2: "Yes - Central only (1, 2 or 3)",
			3: "No - 0 Bridge"
			},
		3:	{
			0: "Normal Land",
			1: "Jungle",
			2: "Hills",
			3: "Marsh",
			4: "Peaks",
			5: "Jungle and Marsh",
			6: "Jungle of 2 lines middle on Marsh",			
			},
		4:	{
			0: "Standard",
			1: "Within 5 Tiles"
			},
		5:	{
			0: "Standard",
			1: "Within 7 Tiles"
			},
		6:	{
			0: "Standard",
			1: "Within 7 Tiles"
			},
		7:	{
			0: "No",
			1: "Yes - Obsidian balanced, small odds Jade & Sapphires",
			2: "Yes - Strategic only on fixed, predetermined, tiles"		
			},	
		8:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},	
		9:	{
			0: "Normal",
			1: "Top v Bottom",
			2: "Left v Right"
			},				
		10:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},	
		11:	{
			0: "8 Tiles Square by Player",
			1: "10 Tiles Square by Player",
			2: "12 Tiles Square by Player",
			3: "14 Tiles Square by Player"
			},				
		12:	{
			0: "Ideal for 4, 6, 8 players positions",
			1: "4 Players - 4 Territories - Tiny",
			2: "6 Players - 6 Territories - Tiny",
			3: "8 Players - 4 Territories - Standard",
			4: "8 Players - 8 Territories - Tiny"			
			},		
		13:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"			
			},
		14:	{
			0: "Penny for Beyond The Game - Works for BTS, BTG Options have no effect"		
			}				
		}

	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDefault")
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:	1,
		2:  0,
		3:	6,
		4:	0,
		5:	0,
		6:	0,
		7:	1,
		8:	0,
		9:	1,
		10:	0,
		11:	1,
		12:	0,
		13:	0,
		14:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
#	BugUtil.debug("Team_Battleground: isRandomCustomMapOption")
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	false,
		2:  false,
		3:	false,
		4:	false,
		5:	false,
		6:	false,
		7:	true,
		8:	true,
		9:	true,
		10:	true,
		10:	false,
		11:	false,
		12:	false,
		13:	false,
		14:	false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)
		

def beforeGeneration():
#	BugUtil.debug("Team_Battleground: beforeGeneration")
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False


	global equator
	global team_num
	
	#2.18
	global iNumRegions
	iNumRegions = 4
	global regions_in_use
	regions_in_use = []
	
	#2.18 end
	team_num = []
	team_index = 0
	equator = CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")
	for teamCheckLoop in range(CyGlobalContext().getMAX_CIV_PLAYERS()):#2.35 when you reduce to 12 players... cannot hardcode this
		if CyGlobalContext().getTeam(teamCheckLoop).isEverAlive():
			team_num.append(team_index)
			team_index += 1
		else:
			team_num.append(-1)
			
	
	#copy /inspied by inland			
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()			
			

	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	
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
	
	if (CyMap().getCustomMapOption(1) == 0):# 4 Territories
		# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
		templates = {(1,0): {0: [0.25, 0.25, int(0.5 * iW), int(0.5 * iH)]},
					 (2,0): {0: [0.25, 0.25, fVar, int(0.5 * iH)],
							 1: [0.75, 0.75, fVar, int(0.5 * iH)]},
					 (3,0): {0: [0.25, 0.25, 0, 0],
							 1: [0.75, 0.75, 0, 0],
							 2: [0.25, 0.75, 0, 0]},
					 (4,0): {0: [0.25, 0.25, 0, 0],
							 1: [0.75, 0.75, 0, 0],
							 2: [0.25, 0.75, 0, 0],
							 3: [0.75, 0.25, 0, 0]},
					 (5,0): {0: [0.15, 0.25, 0, 0],
							 1: [0.35, 0.25, 0, 0],
							 2: [0.75, 0.75, 0, 0],
							 3: [0.25, 0.75, 0, 0],
							 4: [0.75, 0.25, 0, 0]},							 
					 (6,0): {0: [0.15, 0.25, 0, 0],
							 1: [0.35, 0.25, 0, 0],
							 2: [0.75, 0.75, 0, 0],
							 3: [0.25, 0.75, 0, 0],
							 4: [0.65, 0.25, 0, 0],
							 5: [0.85, 0.25, 0, 0]},	
					 (7,0): {0: [0.15, 0.25, 0, 0],
							 1: [0.35, 0.25, 0, 0],
							 2: [0.65, 0.75, 0, 0],
							 3: [0.85, 0.75, 0, 0],
							 4: [0.15, 0.75, 0, 0],
							 5: [0.35, 0.75, 0, 0],
							 6: [0.65, 0.25, 0, 0]},							 
					 (8,0): {0: [0.15, 0.25, 0, 0],
							 1: [0.35, 0.25, 0, 0],
							 2: [0.65, 0.75, 0, 0],
							 3: [0.85, 0.75, 0, 0],
							 4: [0.15, 0.75, 0, 0],
							 5: [0.35, 0.75, 0, 0],
							 6: [0.65, 0.25, 0, 0],
							 7: [0.85, 0.25, 0, 0]}						 
		}

	elif (CyMap().getCustomMapOption(1) == 1):# 6 Territories
		# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
		templates = {(1,0): {0: [0.33, 0.25, int(0.5 * iW), int(0.5 * iH)]},
					 (2,0): {0: [0.50, 0.25, fVar, int(0.5 * iH)],
							 1: [0.50, 0.75, fVar, int(0.5 * iH)]},
					 (3,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.50, 0.25, 0, 0],
							 2: [0.66, 0.25, 0, 0]},
					 (4,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.50, 0.25, 0, 0],
							 2: [0.84, 0.25, 0, 0],
							 3: [0.50, 0.75, 0, 0]},
					 (5,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.50, 0.25, 0, 0],
							 2: [0.84, 0.25, 0, 0],
							 3: [0.50, 0.75, 0, 0],
							 4: [0.16, 0.75, 0, 0]},							 
					 (6,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.50, 0.25, 0, 0],
							 2: [0.84, 0.25, 0, 0],
							 3: [0.16, 0.75, 0, 0],
							 4: [0.50, 0.75, 0, 0],
							 5: [0.84, 0.75, 0, 0]},
					 (7,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.40, 0.25, 0, 0],
							 2: [0.84, 0.25, 0, 0],
							 3: [0.16, 0.75, 0, 0],
							 4: [0.50, 0.75, 0, 0],
							 5: [0.84, 0.75, 0, 0],
							 6: [0.60, 0.25, 0, 0]},							 
					 (8,0): {0: [0.16, 0.25, 0, 0],
							 1: [0.40, 0.25, 0, 0],
							 2: [0.84, 0.25, 0, 0],
							 3: [0.16, 0.75, 0, 0],
							 4: [0.40, 0.75, 0, 0],
							 5: [0.84, 0.75, 0, 0],
							 6: [0.60, 0.75, 0, 0],							 
							 7: [0.60, 0.25, 0, 0]}								 
		}
		# End of Templates data.	
	
	else:# 8 Territories
		# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
		templates = {(1,0): {0: [0.25, 0.25, int(0.5 * iW), int(0.5 * iH)]},
					 (2,0): {0: [0.375, 0.25, fVar, int(0.5 * iH)],
							 1: [0.625, 0.75, fVar, int(0.5 * iH)]},
					 (3,0): {0: [0.375, 0.25, 0, 0],
							 1: [0.625, 0.25, 0, 0],
							 2: [0.375, 0.75, 0, 0]},
					 (4,0): {0: [0.375, 0.25, 0, 0],
							 1: [0.625, 0.25, 0, 0],
							 2: [0.375, 0.75, 0, 0],
							 3: [0.625, 0.75, 0, 0]},
					 (5,0): {0: [0.125, 0.25, 0, 0],
							 1: [0.375, 0.25, 0, 0],
							 2: [0.625, 0.25, 0, 0],
							 3: [0.375, 0.75, 0, 0],
							 4: [0.625, 0.75, 0, 0]},
					 (6,0): {0: [0.125, 0.25, 0, 0],
							 1: [0.375, 0.25, 0, 0],
							 2: [0.625, 0.25, 0, 0],
							 3: [0.125, 0.75, 0, 0],
							 4: [0.375, 0.75, 0, 0],
							 5: [0.625, 0.75, 0, 0]},
					 (7,0): {0: [0.125, 0.25, 0, 0],
							 1: [0.375, 0.25, 0, 0],
							 2: [0.625, 0.25, 0, 0],
							 3: [0.875, 0.25, 0, 0],
							 4: [0.125, 0.75, 0, 0],
							 5: [0.375, 0.75, 0, 0],
							 6: [0.625, 0.75, 0, 0]},
					 (8,0): {0: [0.125, 0.25, 0, 0],
							 1: [0.375, 0.25, 0, 0],
							 2: [0.625, 0.25, 0, 0],
							 3: [0.875, 0.25, 0, 0],
							 4: [0.125, 0.75, 0, 0],
							 5: [0.375, 0.75, 0, 0],
							 6: [0.625, 0.75, 0, 0],
							 7: [0.875, 0.75, 0, 0]}
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
				
	#end copy		
		
	return None	
	
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

def getGridSize(argsList):
#	BugUtil.debug("Team_Battleground: getGridSize")

	#Old way of doing it - via map size
	'''if (CyMap().getCustomMapOption(1) == 0):# 4 Territories
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(7,7),
			WorldSizeTypes.WORLDSIZE_SMALL:		(8,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(9,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(10,10),
			WorldSizeTypes.WORLDSIZE_HUGE:		(11,11)
		}
	elif (CyMap().getCustomMapOption(1) == 1):# 6 Territories	
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(9,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(10,7),
			WorldSizeTypes.WORLDSIZE_SMALL:		(12,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(13,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(15,10),
			WorldSizeTypes.WORLDSIZE_HUGE:		(16,11)
		}	
	else:# 8 Territories
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(12,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(14,7),
			WorldSizeTypes.WORLDSIZE_SMALL:		(16,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(18,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(20,10),
			WorldSizeTypes.WORLDSIZE_HUGE:		(22,11)
		}
	
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	grid_size = grid_sizes[eWorldSize]'''
	
	
	# Based on option selected
	nSquareSize = 8#smallest size
	if (CyMap().getCustomMapOption(11) == 1):	
		nSquareSize = 10
	elif (CyMap().getCustomMapOption(11) == 2):	
		nSquareSize = 12
	elif (CyMap().getCustomMapOption(11) == 3):	
		nSquareSize = 14

	
	ny = ((nSquareSize + 4) * 2 / 4)
	if (CyMap().getCustomMapOption(1) == 0):# 4 Territories	
		nx = ny

	elif (CyMap().getCustomMapOption(1) == 1):# 6 Territories	
		nx = ((nSquareSize + 4) * 3 / 4)
	
	else:# 8 Territories
		nx = ((nSquareSize + 4) * 4 / 4)	
			
	grid_size = (nx,ny)	

	return grid_size


def generatePlotTypes():
#	BugUtil.debug("Team_Battleground: generatePlotTypes")
	NiTextOut("Setting Plot Types (Python Team Battleground) ...")
	global hinted_world, mapRand
	global fractal_world
	gc = CyGlobalContext()
	map = CyMap()
	mapRand = gc.getGame().getMapRand()
	userInputPlots = map.getCustomMapOption(0)
	

	hinted_world = HintedWorld()
	iNumPlotsX = map.getGridWidth()
	iNumPlotsY = map.getGridHeight()

	centery = (hinted_world.h - 1)//2
	centerx = (hinted_world.w - 1)//2

	iCenterXList = []
	iCenterXList.append(centerx-1)
	iCenterXList.append(centerx)
	iCenterXList.append(centerx+1)

	iCenterYList = []
	iCenterYList.append(centery-1)
	iCenterYList.append(centery)
	iCenterYList.append(centery+1)

	bridgey = centery

	# Set all blocks to land except a strip in the center & start a building block
	for x in range(hinted_world.w):
		for y in range(hinted_world.h):
			if x == centerx:
				if y == bridgey:
					hinted_world.setValue(x,y,128) # coast
				else:
					hinted_world.setValue(x,y,0)
			else:
				hinted_world.setValue(x,y,255)
				if y in iCenterYList:
					hinted_world.setValue(x,y,128) # coast
				if y == centery:
					hinted_world.setValue(x,y,0) # ocean

	hinted_world.buildAllContinents()
	plotTypes = hinted_world.generatePlotTypes(0)#2.23 Changed to 0 from 20 it's important not to have "forced" water
		
	#############################################################
	# Penny - Let's move on to manual design	
	# Layer 1, all land
	for x in range(map.getGridWidth()):
	 	for y in range(map.getGridHeight()):
	 		i = map.plotNum(x, y)
	 		plotTypes[i] = PlotTypes.PLOT_LAND
		
	plotTypes = hinted_world.generatePlotTypes(0)#2.23 Changed to 0 from 20 it's important not to have "forced" water
	
	#2.23 - For some reason some plots are forgotten - the line vertical in the middle
	for x in range(map.getGridWidth()):
		for y in range(map.getGridHeight()):
			if (x == map.getGridWidth()/2):
				if ((y != map.getGridHeight()-1) and (y != map.getGridHeight()-2)):
					if ((y != map.getGridHeight()/2+1) and (y != map.getGridHeight()/2+0) and (y != map.getGridHeight()/2-1) and (y != map.getGridHeight()/2-2)):
						if ((y != 0) and (y != 1)):
							i = map.plotNum(x, y)
							plotTypes[i] = PlotTypes.PLOT_LAND							
		
	# Layer 2, Horizontal Water
	for x in range(map.getGridWidth()):
	# Lines bottom
		i = map.plotNum(x, 0)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
		i = map.plotNum(x, 1)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
	# Lines top
		i = map.plotNum(x,map.getGridHeight()-1)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
		i = map.plotNum(x,map.getGridHeight()-2)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
	# Lines middle
		i = map.plotNum(x,(map.getGridHeight()/2)+1)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
		i = map.plotNum(x,(map.getGridHeight()/2)+0)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
		i = map.plotNum(x,(map.getGridHeight()/2)-1)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN
		i = map.plotNum(x,(map.getGridHeight()/2)-2)
		plotTypes[i] =  PlotTypes.PLOT_OCEAN				
				
	# Layer 3, Vertical Water
	for y in range(map.getGridHeight()):
	# Lines Left
		i = map.plotNum(0, y)
		plotTypes[i] = PlotTypes.PLOT_OCEAN
		i = map.plotNum(1, y)
		plotTypes[i] = PlotTypes.PLOT_OCEAN
	# Lines Right
		i = map.plotNum(map.getGridWidth()-1, y)
		plotTypes[i] = PlotTypes.PLOT_OCEAN			
		i = map.plotNum(map.getGridWidth()-2, y)
		plotTypes[i] = PlotTypes.PLOT_OCEAN	
	# Lines Middle
		if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 Territories or 8 territories
			i = map.plotNum((map.getGridWidth()/2)+1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN			
			i = map.plotNum((map.getGridWidth()/2)+0, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/2)-1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/2)-2, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
		if (CyMap().getCustomMapOption(1) == 1):# 6 Territories
			i = map.plotNum((map.getGridWidth()/3)+1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN			
			i = map.plotNum((map.getGridWidth()/3)+0, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/3)-1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN
			i = map.plotNum((map.getGridWidth()/3)-2, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN
			i = map.plotNum((map.getGridWidth()/3*2)+1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN			
			i = map.plotNum((map.getGridWidth()/3*2)+0, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/3*2)-1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN
			i = map.plotNum((map.getGridWidth()/3*2)-2, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN
		if (CyMap().getCustomMapOption(1) == 2):# 8 Territories
			i = map.plotNum((map.getGridWidth()/4)+1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN			
			i = map.plotNum((map.getGridWidth()/4)+0, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/4)-1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/4)-2, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/4*3)+1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN			
			i = map.plotNum((map.getGridWidth()/4*3)+0, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/4*3)-1, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN	
			i = map.plotNum((map.getGridWidth()/4*3)-2, y)
			plotTypes[i] = PlotTypes.PLOT_OCEAN				
					
	#########################################
	# Now add the bridges ! 
	
	# Bottom left bridge
	if (CyMap().getCustomMapOption(2) <= 1): #
		#BTP 2.18 Fix holes
		i = map.plotNum(3, 2)
		plotTypes[i] = PlotTypes.PLOT_LAND		
		i = map.plotNum(map.getGridWidth()-2, 3)	
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-3, 2)
		plotTypes[i] = PlotTypes.PLOT_LAND			
		i = map.plotNum(map.getGridWidth()-3, 3)
		plotTypes[i] = PlotTypes.PLOT_LAND		
		i = map.plotNum(2, 2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(2, 3)		
		plotTypes[i] = PlotTypes.PLOT_LAND		
		#end BTP Fix
	
		i = map.plotNum(0, 0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(0, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(1, 0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1, 2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(2, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND				
		i = map.plotNum(map.getGridWidth()-1, 0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-1, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-2, 0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2, 2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-3, 1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(0, map.getGridHeight()-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(0, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(1, map.getGridHeight()-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1, map.getGridHeight()-3)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(2, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-1, map.getGridHeight()-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-1, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-2, map.getGridHeight()-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2, map.getGridHeight()-3)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-3, map.getGridHeight()-2)
		plotTypes[i] = PlotTypes.PLOT_LAND					

	# Bottom right bridge
	if (CyMap().getCustomMapOption(2) <= 0): #
		if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 Territories or 8 territories
			#btp 2.18 fix
			i = map.plotNum(map.getGridWidth()/2-3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			i = map.plotNum(map.getGridWidth()/2-4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/2+3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
			i = map.plotNum(map.getGridWidth()/2-3, 4)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-4, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/2+3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			#btp 2.18 fix end
		
			i = map.plotNum(map.getGridWidth()/2+0, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+0, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-2, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+0, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+0, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-2, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-3, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
		if (CyMap().getCustomMapOption(1) == 1):# 6 Territories
			i = map.plotNum(map.getGridWidth()/3-3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			i = map.plotNum(map.getGridWidth()/3-4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/3+3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
			i = map.plotNum(map.getGridWidth()/3-3, 4)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-4, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/3+3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND		
		
			i = map.plotNum(map.getGridWidth()/3+0, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+0, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-2, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+0, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+0, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-2, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-3, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			
			
			i = map.plotNum(map.getGridWidth()/3*2-3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			i = map.plotNum(map.getGridWidth()/3*2-4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/3*2+3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
			i = map.plotNum(map.getGridWidth()/3*2-3, 4)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-4, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/3*2+3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND		
		
			i = map.plotNum(map.getGridWidth()/3*2+0, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+0, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-2, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+0, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+0, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-2, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-3, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
		if (CyMap().getCustomMapOption(1) == 2):# 8 Territories
			#btp 2.18 fix
			i = map.plotNum(map.getGridWidth()/4-3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			i = map.plotNum(map.getGridWidth()/4-4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/4+3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
			i = map.plotNum(map.getGridWidth()/4-3, 4)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-4, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/4+3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			#btp 2.18 fix end
		
			i = map.plotNum(map.getGridWidth()/4+0, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+0, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-2, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+0, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+0, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-2, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-3, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
	
	
			i = map.plotNum(map.getGridWidth()/4*3-3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			i = map.plotNum(map.getGridWidth()/4*3-4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/4*3+3, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			
			i = map.plotNum(map.getGridWidth()/4*3-3, 4)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-4, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+3, 3)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+4, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			i = map.plotNum(map.getGridWidth()/4*3+3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND		
			#btp 2.18 fix end
		
			i = map.plotNum(map.getGridWidth()/4*3+0, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+0, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-1, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-1, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-2, 0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2, 2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-3, 1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+0, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+0, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-1, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-1, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-2, map.getGridHeight()-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2, map.getGridHeight()-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-3, map.getGridHeight()-2)
			plotTypes[i] = PlotTypes.PLOT_LAND		
	
	
	# Middle left bridge
	if (CyMap().getCustomMapOption(2) <= 0): #
		i = map.plotNum(0,map.getGridHeight()/2+0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(0,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(1,map.getGridHeight()/2+0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1,map.getGridHeight()/2+2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(2,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-1,map.getGridHeight()/2+0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-1,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2+0)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2+2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-3,map.getGridHeight()/2+1)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(0,map.getGridHeight()/2-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(0,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(1,map.getGridHeight()/2-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(1,map.getGridHeight()/2-3)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(2,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-1,map.getGridHeight()/2-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-1,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2-1)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND
		i = map.plotNum(map.getGridWidth()-2,map.getGridHeight()/2-3)
		plotTypes[i] = PlotTypes.PLOT_LAND	
		i = map.plotNum(map.getGridWidth()-3,map.getGridHeight()/2-2)
		plotTypes[i] = PlotTypes.PLOT_LAND	

	
	# middle Center
	if (CyMap().getCustomMapOption(2) <= 2): #
		if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 Territories or 8 territories	
			i = map.plotNum(map.getGridWidth()/2+0,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+0,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND

			i = map.plotNum(map.getGridWidth()/2-1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-3,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/2+0,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+0,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2+1,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2+2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/2-1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/2-2,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/2-3,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			
		if (CyMap().getCustomMapOption(1) == 1):# 6 Territories
			i = map.plotNum(map.getGridWidth()/3+0,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+0,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND

			i = map.plotNum(map.getGridWidth()/3-1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-3,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/3+0,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+0,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3+1,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3+2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/3-1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3-2,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3-3,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			
			i = map.plotNum(map.getGridWidth()/3*2+0,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+0,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND

			i = map.plotNum(map.getGridWidth()/3*2-1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-3,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/3*2+0,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+0,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2+1,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2+2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/3*2-1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/3*2-2,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/3*2-3,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND				
			
			
		if (CyMap().getCustomMapOption(1) == 2):# 8 Territories	
			i = map.plotNum(map.getGridWidth()/4+0,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+0,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND

			i = map.plotNum(map.getGridWidth()/4-1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-3,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/4+0,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+0,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4+1,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4+2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/4-1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4-2,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4-3,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			
			i = map.plotNum(map.getGridWidth()/4*3+0,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+0,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND

			i = map.plotNum(map.getGridWidth()/4*3-1,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-1,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2+0)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2+2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-3,map.getGridHeight()/2+1)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/4*3+0,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+0,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3+1,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3+2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	

			i = map.plotNum(map.getGridWidth()/4*3-1,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-1,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2-1)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND
			i = map.plotNum(map.getGridWidth()/4*3-2,map.getGridHeight()/2-3)
			plotTypes[i] = PlotTypes.PLOT_LAND	
			i = map.plotNum(map.getGridWidth()/4*3-3,map.getGridHeight()/2-2)
			plotTypes[i] = PlotTypes.PLOT_LAND			
			
			
	return plotTypes
	
	



class TeamBGTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def generateTerrainAtPlot(self, iX, iY):
#		BugUtil.debug("Team_Battleground: generateTerrainAtPlot")
		global equator
		lat = 0.9 * self.getLatitudeAtPlot(iX,iY)

		if not self.map.plot(iX, iY).isWater():
			terrainVal = self.terrainGrass

	#		if lat >= self.fSnowLatitude:
	#			terrainVal = self.terrainIce
	#		elif lat >= self.fTundraLatitude:
	#			terrainVal = self.terrainTundra
			if lat < self.fGrassLatitude:
				terrainVal = equator # Equator is grass usually, but desert for TvB
			else:
				desertVal = self.deserts.getHeight(iX, iY)
				plainsVal = self.plains.getHeight(iX, iY)
				if ((desertVal >= self.iDesertBottom) and (desertVal <= self.iDesertTop) and (lat >= self.fDesertBottomLatitude) and (lat < self.fDesertTopLatitude)):
					terrainVal = self.terrainDesert
				elif ((plainsVal >= self.iPlainsBottom) and (plainsVal <= self.iPlainsTop)):
					terrainVal = self.terrainPlains
				else:
					terrainVal =self.terrainGrass

		map = CyMap()
				
		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()
			


		return terrainVal

def generateTerrainTypes():
#	BugUtil.debug("Team_Battleground: generateTerrainTypes")
	NiTextOut("Generating Terrain (Python Team Battleground) ...")
	terraingen = TeamBGTerrainGenerator()
	terraingen.__init__(iDesertPercent=5)
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class TeamBGFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns a value in the range of 0.0 (tropical) to 1.0 (polar)"
		return 0.9 * (abs((self.iGridH/2) - iY)/float(self.iGridH/2))

def addFeatures():
#	BugUtil.debug("Team_Battleground: addFeatures")
	NiTextOut("Adding Features (Python Team Battleground) ...")
	featuregen = TeamBGFeatureGenerator()
	featuregen.addFeatures()
	
	BridgeContent() #Call map-made procedure
	
	return 0
	
def BridgeContent():	#Penny - Make the bridge a certain type of land
	map = CyMap()
	gc = CyGlobalContext()
	
	BridgesPlots = []
	for dx in range(-3,3):
		for dy in range(-3,3):
			p = map.plot(0+dx,0+dy)
			BridgesPlots.append(p)
			
	for dx in range(-3,3):
		for dy in range(-3,3):
			p = map.plot(0+dx,map.getGridHeight()/2+dy)
			BridgesPlots.append(p)	

	#2.23 - For flat maps
	for dx in range(-3,3):
		for dy in range(-3,3):
			p = map.plot(map.getGridWidth()+dx,0+dy)
			BridgesPlots.append(p)	
			p = map.plot(0+dx,map.getGridHeight()+dy)
			BridgesPlots.append(p)	
			p = map.plot(map.getGridWidth()+dx,map.getGridHeight()+dy)
			BridgesPlots.append(p)				
	
	if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 Territories or 8 territories
		for dx in range(-3,3):
			for dy in range(-3,3):
				p = map.plot(map.getGridWidth()/2+dx,0+dy)
				BridgesPlots.append(p)

		for dx in range(-3,3):
			for dy in range(-3,3):
				p = map.plot(map.getGridWidth()/2+dx,map.getGridHeight()/2+dy)
				BridgesPlots.append(p)
				
		for dx in range(-3,3):#2.23 for flat
			for dy in range(-3,3):
				p = map.plot(map.getGridWidth()/2+dx,map.getGridHeight()+dy)
				BridgesPlots.append(p)				
				
	if (CyMap().getCustomMapOption(1) == 1):# 6 Territories	
		for dx in range(-3,3):
			for dy in range(-3,3):
				p = map.plot(map.getGridWidth()/3+dx,0+dy)
				BridgesPlots.append(p)
				p = map.plot(map.getGridWidth()/3+dx,map.getGridHeight()/2+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/3*2+dx,0+dy)
				BridgesPlots.append(p)
				p = map.plot(map.getGridWidth()/3*2+dx,map.getGridHeight()/2+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/3+dx,map.getGridHeight()+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/3*2+dx,map.getGridHeight()+dy)
				BridgesPlots.append(p)	

	if (CyMap().getCustomMapOption(1) == 2):# 8 Territories
		for dx in range(-3,3):
			for dy in range(-3,3):
				p = map.plot(map.getGridWidth()/4+dx,0+dy)
				BridgesPlots.append(p)
				p = map.plot(map.getGridWidth()/4+dx,map.getGridHeight()/2+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/4*3+dx,0+dy)
				BridgesPlots.append(p)
				p = map.plot(map.getGridWidth()/4*3+dx,map.getGridHeight()/2+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/4+dx,map.getGridHeight()+dy)
				BridgesPlots.append(p)	
				p = map.plot(map.getGridWidth()/4*3+dx,map.getGridHeight()+dy)
				BridgesPlots.append(p)				
		
	for p in BridgesPlots:
		if not p.isWater():
			if (CyMap().getCustomMapOption(3) == 0):
				if not (p.getFeatureType() == FeatureTypes.NO_FEATURE): #check where there is forest or jungle and make it forest
					p.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"),-1)	
			elif (CyMap().getCustomMapOption(3) == 1): 
				p.setFeatureType(gc.getInfoTypeForString("FEATURE_JUNGLE"),-1)	
			elif (CyMap().getCustomMapOption(3) == 5):#2.23
				if isBTPon :
					p.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)
				else:
					p.setTerrainType(gc.getInfoTypeForString("TERRAIN_PLAINS"), True, True)			
				p.setFeatureType(gc.getInfoTypeForString("FEATURE_JUNGLE"),-1)
			
			elif (CyMap().getCustomMapOption(3) == 6):#2.23c
					if isBTPon :
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)
					else:
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_PLAINS"), True, True)	
					if (p.getY() == map.getGridHeight()/2 or p.getY() == map.getGridHeight()/2 - 1):							
						p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation'''
					elif (p.getY() == 1 or p.getY() == map.getGridHeight() - 2):							
						p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation'''						
					else:
						p.setFeatureType(-1,-1)
				
			elif (CyMap().getCustomMapOption(3) == 2):
				p.setPlotType(PlotTypes.PLOT_HILLS, true, true)
			elif (CyMap().getCustomMapOption(3) == 3):
				if not (p.getFeatureType() == FeatureTypes.NO_FEATURE): #check where there is forest or jungle and make it forest
					p.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"),-1)	
				if isBTPon :
					p.setTerrainType(gc.getInfoTypeForString("TERRAIN_MARSH"), True, True)
				else:
					p.setTerrainType(gc.getInfoTypeForString("TERRAIN_PLAINS"), True, True)					
			else:
				p.setPlotType(PlotTypes.PLOT_OCEAN, true, true)#Just so that it removes forest & jungle on those tile
				p.setPlotType(PlotTypes.PLOT_PEAK, true, true)					
	
	return 0	


	
def assignStartingPlots():
	CyPythonMgr().allowDefaultImpl()

def getRiverStartCardinalDirection(argsList):
	"Returns the cardinal direction of the first river segment."
	pPlot = argsList[0]
	print pPlot
	map = CyMap()
	x, y = pPlot.getX(), pPlot.getY()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	if y < iH/2:
		return CardinalDirectionTypes.CARDINALDIRECTION_NORTH
	else:
		return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH


def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	#2.21y
	if isBTPon:
		if CyMap().getCustomMapOption(7) == 0:#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
				
		if (CyMap().getCustomMapOption(7) == 0 or CyMap().getCustomMapOption(7) == 2):#exclude the strategic ones because strat is function above (and commo is okay)
			if (type_string in balancer.newStrategicBTP):
				return None	
	
	BTPResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM')#2.18
	

	
	if (type_string in BTPResourcesToBalance):
		return None # don't place any of this bonus randomly			
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way
	
	
def BTGExtraBalancer():	

	gc = CyGlobalContext()
	map = CyMap()
	oil = gc.getInfoTypeForString("BONUS_OIL")
	alu = gc.getInfoTypeForString("BONUS_ALUMINUM")
	ivory = gc.getInfoTypeForString("BONUS_IVORY")
	gold = gc.getInfoTypeForString("BONUS_GOLD")
	silver = gc.getInfoTypeForString("BONUS_SILVER")
	gems = gc.getInfoTypeForString("BONUS_GEMS")
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	
	for i in range(0,gc.getMAX_CIV_PLAYERS()):
		#if gc.getPlayer(i).isAlive():
		if gc.getPlayer(i).isEverAlive():#2.22 - Very important - nothing was working with Spectator

			start_plot = gc.getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()
			plotsclose = []
			plotsfurther = []
			plotsboundaries = []
			has_oil = false
			has_alu = false
			has_ivory = false
			has_horse = false
			has_precious = false
			for dx in range(-5,5):
				for dy in range(-5,5):
					p = map.plot(startx+dx,starty+dy)
					if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						plotsclose.append(p)
						if p.getBonusType(-1) == oil:
							has_oil = True
						if p.getBonusType(-1) == alu:
							has_alu = True
							
			for dx in range(-7,7):
				for dy in range(-7,7):
					p = map.plot(startx+dx,starty+dy)
					if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						plotsfurther.append(p)	
						if p.getBonusType(-1) == ivory:
							has_ivory = True
						if p.getBonusType(-1) == gold:
							has_precious = True
						if p.getBonusType(-1) == silver:
							has_precious = True
						if p.getBonusType(-1) == gems:
							has_precious = True				
							
			for dx in range(-6,6):
				for dy in range(-6,6):
					p = map.plot(startx+dx,starty+dy)
					#2.22 This is too restrictive for this map
					if (( abs(dx) >= 5 or abs(dy) >= 5) and not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):#1 notch closer than other maps
						if ((abs(dx) >= 3 and abs(dy) >= 3)):#too tight otherwise on this map
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								plotsboundaries.append(p)						

	
			if (CyMap().getCustomMapOption(4) == 1):
				if not has_oil:

					random.shuffle(plotsclose) 
					for p in plotsclose:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(oil, True):
							p.setBonusType(oil)
							has_oil = True
							break
					if not has_oil:
						p = plotsclose[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(oil)

				if not has_alu:

					random.shuffle(plotsclose) 
					for p in plotsclose:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(alu, True):
							p.setBonusType(alu)
							has_alu = True or CyMap().getCustomMapOption(4) == 0
							break
					if not has_alu:
						p = plotsclose[0]
						p.setPlotType(PlotTypes.PLOT_HILLS, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(alu)
					
			if (CyMap().getCustomMapOption(5) == 1):
				if not has_ivory:

					random.shuffle(plotsfurther) 
					for p in plotsfurther:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(ivory, True):
							p.setBonusType(ivory)
							has_ivory = True
							break
					if not has_ivory:
						p = plotsfurther[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_GRASS"), True, True)
						p.setBonusType(ivory)

			if (CyMap().getCustomMapOption(6) == 1):
				if not has_precious:

					random.shuffle(plotsboundaries) 
					for p in plotsboundaries:
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(silver, True):
							p.setBonusType(silver)
							has_precious = True
							break
					if not has_precious:
						p = plotsboundaries[0]
						p.setPlotType(PlotTypes.PLOT_LAND, True, True)
						p.setTerrainType(gc.getInfoTypeForString("TERRAIN_DESERT"), True, True)
						p.setBonusType(silver)		


def normalizeAddExtras():
	#I don't even want a condition for this, always do it. And soem of it it forced closed in addBonusType
	balancer.normalizeAddExtras()
	
	BTGExtraBalancer()
				
	#2.18
	if isBTPon:

		#2.34
		if CvMapGeneratorUtil.BTGInfo().BTG_Version() >= 34:
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_POTATO"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),5,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(20,True,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),7,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(20,True,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),7,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			
		CvMapGeneratorUtil.BTPMapUtil().BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),4,True,CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
	
		if (CyMap().getCustomMapOption(7) == 2):
			
			if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 territoire or 8
				p = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*50/100)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
				p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))		
				#p.setFeatureType(-1, -1)# I remove them to keep the jungle
			
			else:#6 territoire
			
				p = CyMap().plot(CyMap().getGridWidth()/3*2,CyMap().getGridHeight()*50/100)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
				p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))	
				
				p = CyMap().plot(CyMap().getGridWidth()/3-1,CyMap().getGridHeight()*50/100-1)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
				p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"))					
			
			
			#p = CyMap().plot(0,0)
			p = CyMap().plot(CyMap().getGridWidth()-1,CyMap().getGridHeight()-1) #2.23 - it's better for flat terrain
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))			

			p = CyMap().plot(0,CyMap().getGridHeight()*50/100)
			p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
			p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))		

			if (CyMap().getCustomMapOption(1) == 0 or CyMap().getCustomMapOption(1) == 2):# 4 territoire or 8
				p = CyMap().plot(CyMap().getGridWidth()*50/100,0)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
				p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))	
			else:#6 territoire
				p = CyMap().plot(CyMap().getGridWidth()/3*2,0)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"), True, True)
				p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_AMBER"))				
			

	
	
	BTPCleanFeature(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"))
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride
	
def startHumansOnSameTile():

	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(8) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(8) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)

	if (CyMap().getCustomMapOption(10) == 1):
		return True		

def normalizeStartingPlotLocations():#2.23

	if CyMap().getCustomMapOption(9) == 1:
		if isBTPon :
			BTPTopBottomTwoTeams(True)		
		else:
			BTPTopBottomTwoTeams(False)
			
	elif CyMap().getCustomMapOption(9) == 2:
		if isBTPon :
			BTPLeftRightTwoTeams(True)		
		else:
			BTPLeftRightTwoTeams(False)	
			
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case				
		
		
		
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



def BTPLeftRightTwoTeams(isBTG):			
			
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
		iW = CyMap().getGridWidth()
		halfWidth = iW / 2
		for iI in range(gc.getMAX_CIV_PLAYERS()):
			if isBTG:
				if (gc.getPlayer(iI).isAlive() and not gc.getPlayer(iI).isSpectator()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())
			else:
				if (gc.getPlayer(iI).isAlive()):		
					listPlot.append(gc.getPlayer(iI).getStartingPlot())
					listPlayer.append(gc.getPlayer(iI).getID())				
		
		bDoAgain = False
					
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
				if (gc.getPlayer(iI).getTeam() == teamOne and gc.getPlayer(iI).getStartingPlot().getX() >= halfWidth):						
					random.shuffle(listCurrentPlayer)
					iRoll = listCurrentPlayer[0]
					#while ((gc.getPlayer(iRoll).getStartingPlot().getX() >= halfWidth) or (iRoll == iI)):#I roll until it's a bottom tile
					while ((gc.getPlayer(iRoll).getStartingPlot().getX() >= halfWidth) or (iRoll == iI) or gc.getPlayer(iRoll).getTeam() == teamOne):#2.23
						random.shuffle(listCurrentPlayer)
						iRoll = listCurrentPlayer[0]
					
					spotA = gc.getPlayer(iI).getStartingPlot()
					spotB = gc.getPlayer(iRoll).getStartingPlot()
					gc.getPlayer(iI).setStartingPlot(spotB,True)
					gc.getPlayer(iRoll).setStartingPlot(spotA,True)						
					
					
					
					
def BTPCleanFeature(iFeature):
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)	
			if p.getFeatureType() == iFeature:
				p.setFeatureType(-1, -1)					