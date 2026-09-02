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
#	BugUtil.debug("Team_Battleground: getDescription")
	return "UUMadness dedicated Map by Penny for BTG"

def getDescriptionTitle():
	return "The map is designed to offer limited (but all strategic) resources near the player start location. All the other resources are calculated from the middle : "

def getDescriptionTitleTwo():
	return "starting with the rarest resources forced centrally (like Sulphur very close to the Volcano middle tile), and further from center for less rare resources"

def getDescriptionMain():
	return "The map design is all optimised for UUMadness scenarios where you fight for rare resources"

def getDescriptionSecond():#Script tip : (on TOP)
	return "Know well which resource come how many times by player, in smaller number, some only come 1 every 2 players or 1 every 3 players"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "For all types of UUMadness, Duel, CTON, and teamers. Supports up to 4v4 and 5v5. Avoid 7 and 9 Player games"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""		

def getNumCustomMapOptions():
#	BugUtil.debug("Team_Battleground: getNumCustomMapOptions")
	return 14
	
def getNumHiddenCustomMapOptions():
	return 0
	
def getCustomMapOptionName(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionName")
	[iOption] = argsList
	option_names = {
		0:	"External Land",
		1:	"BTG Resources",		
		2:	"BTG Forest Type",
		3:	"Forest Density",
		4:  "Starting Units",
		5:	"Size 1 notch smaller",
		6:	"Bonus Distribution",
		7:	"Start Position",
		8:	"BTG Seas",
		9:	"BTG Free Unit",
		10: "BTG Amt Free Unit",
		11:	"Notes",
		12:	"BTG Spectator Notes",
		13: "Credit"	
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2,
		2:	5,
		3:	2,
		4:	2,
		5:	3,
		6:	2,
		7:  2,
		8:	4,
		9:	5,
		10:  4,		
		11:	6,
		12:	2,
		13:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDescAt")
	[iOption, iSelection] = argsList

	selection_names = {
		0:	{
			0: "Land",
			1: "Ocean",
			2: "Arctic - Frozen"
			},		
		1:	{
			0: "Amber and Sulphur"	,
			1: "Amber,Sulphur, Olive, Tea, Salt, Potato, Diamond, Jade and Obsidian"
			},	
		2:	{
			0: "Normal Forest",
			1: "75% Forest - 25% Palm",
			2: "50% Forest - 50% Palms",
			3: "25% Forest - 75% Palms",
			4: "Palm Forest always"		
			},
		3:	{
			0: "Normal",
			1: "60% of Normal"
			},				
		4:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},			
		5:	{
			0: "No",
			1: "Yes",
			2: "Yes - 2 notches"
			},	
		6:	{
			0: "Balanced Distribution",
			1: "From the Center depending on quality"
			},	
		7:	{
			0: "Normal",
			1: "Two Teams - Left v Right"
			},	
		8:	{
			0: "No",
			1: "Yes - All Lagoons",
			2: "Yes - Lagoons on coast",
			3: "Yes - Balanced Lagoons and Deep sea"
			},	
		9:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			4: "Great Legend"
			},
		10:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},				
		11:	{
			0: "Duel - 2P and 3P",
			1: "Tiny - 4P and 5P",
			2: "Small - 6P (large for 5P)",
			3: "Standard - 8P",
			4: "7P and 9P - One in middle",
			5: "10P Good for Two teams only"
			},
		12:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"
			},
		13:	{
			0: "Penny for BTG - Ideal for UUMadness - Different Distrib for BTS"		
			}				
		}

	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDefault")
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	1,
		2:	0,
		3:	1,
		4:	0,
		5:	1,
		6:	1,
		7:	1,
		8:	3,
		9:	4,
		10:	0,
		11:	0,
		12:	0,
		13: 0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
#	BugUtil.debug("Team_Battleground: isRandomCustomMapOption")
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	false,
		2:	true,
		3:	true,
		4:	true,
		5:	false,
		6:	true,
		7:	false,
		8:	true,
		9:	false,
		10: false,
		11:	false,
		12:	false,
		13:	false
		}
	return option_random[iOption]

def getWrapX():
	map = CyMap()
	return False
	
def getWrapY():
	map = CyMap()
	return False 
		

def beforeGeneration():
	#copy /inspied by inland			
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()	

	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
			

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
	
	# Templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [X, Y, xVariance, yVariance]}}
	templates = {(1,0): {0: [0.50, 0.05, int(0.5 * iW), int(0.5 * iH)]},
	             (2,0): {0: [0.50, 0.05, fVar, fVar],
	                     1: [0.50, 0.95, fVar, fVar]},
	             (3,0): {0: [0.50, 0.92, fVar, fVar],
	                     1: [0.18, 0.18, fVar, fVar],
	                     2: [0.82, 0.18, fVar, fVar]},
	             (4,0): {0: [0.50, 0.05, fVar, fVar],
	                     1: [0.50, 0.95, fVar, fVar],
	                     2: [0.05, 0.50, fVar, fVar],
	                     3: [0.95, 0.50, fVar, fVar]},
	             (5,0): {0: [0.50, 0.90, fVar, fVar],
	                     1: [0.10, 0.58, fVar, fVar],
	                     2: [0.90, 0.58, fVar, fVar],
	                     3: [0.30, 0.15, fVar, fVar],
	                     4: [0.70, 0.15, fVar, fVar]},
	             (6,0): {0: [0.05, 0.50, fVar, fVar],
	                     1: [0.95, 0.50, fVar, fVar],
	                     2: [0.30, 0.85, fVar, fVar],
	                     3: [0.70, 0.85, fVar, fVar],
	                     4: [0.30, 0.15, fVar, fVar],
	                     5: [0.70, 0.15, fVar, fVar]},
	             (7,0): {0: [0.05, 0.50, fVar, fVar],
	                     1: [0.95, 0.50, fVar, fVar],
	                     2: [0.30, 0.85, fVar, fVar],
	                     3: [0.70, 0.85, fVar, fVar],
	                     4: [0.30, 0.15, fVar, fVar],
	                     5: [0.70, 0.15, fVar, fVar],
	                     6: [0.50, 0.50, fVar, fVar]},
	             (8,0): {0: [0.05, 0.30, fVar, fVar],
	                     1: [0.05, 0.70, fVar, fVar],
	                     2: [0.95, 0.30, fVar, fVar],
	                     3: [0.95, 0.70, fVar, fVar],
	                     4: [0.30, 0.95, fVar, fVar],
	                     5: [0.30, 0.05, fVar, fVar],	
	                     6: [0.70, 0.05, fVar, fVar],
	                     7: [0.70, 0.95, fVar, fVar]},
	             (9,0): {0: [0.05, 0.30, fVar, fVar],
	                     1: [0.05, 0.70, fVar, fVar],
	                     2: [0.95, 0.30, fVar, fVar],
	                     3: [0.95, 0.70, fVar, fVar],
	                     4: [0.30, 0.95, fVar, fVar],
	                     5: [0.30, 0.05, fVar, fVar],
	                     6: [0.70, 0.05, fVar, fVar],
	                     7: [0.70, 0.95, fVar, fVar],
						 8: [0.50, 0.50, fVar, fVar]},
	             (10,0): {0: [0.05, 0.30, fVar, fVar],
	                     1: [0.05, 0.70, fVar, fVar],
	                     2: [0.95, 0.30, fVar, fVar],
	                     3: [0.95, 0.70, fVar, fVar],
	                     4: [0.30, 0.95, fVar, fVar],
	                     5: [0.30, 0.05, fVar, fVar],
	                     6: [0.70, 0.05, fVar, fVar],
	                     7: [0.70, 0.95, fVar, fVar],
	                     8: [0.25, 0.50, fVar, fVar],						 
						 9: [0.75, 0.50, fVar, fVar]},						 
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
	
def minStartingDistanceModifier():
	return 0
	
def assignStartingPlots():
	CyPythonMgr().allowDefaultImpl()
	
def findStartingPlot(argsList):
	# Set up for maximum of 18 players! If more, use default implementation.
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if iPlayers >= 11:
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

	if (CyMap().getCustomMapOption(5) == 0):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8,8),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
			WorldSizeTypes.WORLDSIZE_SMALL:		(9,9),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(10,10),
			WorldSizeTypes.WORLDSIZE_LARGE:		(11,11),
			WorldSizeTypes.WORLDSIZE_HUGE:		(12,12)
		}
	
	if (CyMap().getCustomMapOption(5) == 1):#make  1 notch smaller
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,7),
			WorldSizeTypes.WORLDSIZE_TINY:		(7,7),
			WorldSizeTypes.WORLDSIZE_SMALL:		(8,8),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(9,9),
			WorldSizeTypes.WORLDSIZE_LARGE:		(10,10),
			WorldSizeTypes.WORLDSIZE_HUGE:		(11,11)
		}

	if (CyMap().getCustomMapOption(5) == 2):#make 2 notch smaller
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
			WorldSizeTypes.WORLDSIZE_TINY:		(6,6),
			WorldSizeTypes.WORLDSIZE_SMALL:		(7,7),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(8,8),
			WorldSizeTypes.WORLDSIZE_LARGE:		(9,9),
			WorldSizeTypes.WORLDSIZE_HUGE:		(10,10)
		}		
	
	
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	grid_size = grid_sizes[eWorldSize]

	gc = CyGlobalContext()
	return grid_size


def generatePlotTypes():
#	BugUtil.debug("Team_Battleground: generatePlotTypes")
	NiTextOut("Setting Plot Types (Python Team Battleground) ...")
	global hinted_world, mapRand
	global fractal_world
	gc = CyGlobalContext()
	map = CyMap()
	mapRand = gc.getGame().getMapRand()
	
	hinted_world = HintedWorld()
	plotTypes = hinted_world.generatePlotTypes(20)
	dice = gc.getGame().getMapRand()

	for x in range(map.getGridWidth()):
		for y in range(map.getGridHeight()):
			i = map.plotNum(x,y)			
			iChance = dice.get(20, "Hills on spokes - Grid PYTHON")		
			if iChance == 0:
				plotTypes[i] = PlotTypes.PLOT_PEAK
			elif iChance <= 5:
				plotTypes[i] = PlotTypes.PLOT_HILLS			
			else:
				plotTypes[i] = PlotTypes.PLOT_LAND	

	return plotTypes
	
def generateTerrainTypes():#BTP - From Grid
	terraingen = TerrainGenerator()
	terraingen.__init__(iDesertPercent=0, iPlainsPercent=25,
		fSnowLatitude=2.0, fTundraLatitude=2.0, fGrassLatitude=0.0, 
		fDesertBottomLatitude=0.0, fDesertTopLatitude=0.0)
	terrainTypes = terraingen.generateTerrain()

	# Eliminate snow and tundra completely (they still get placed sometimes at extreme latitudes)
	for i in range(len(terrainTypes)):
		if (terrainTypes[i] == terraingen.terrainIce) or (terrainTypes[i] == terraingen.terrainTundra):
			terrainTypes[i] = terraingen.terrainPlains

	return terrainTypes
	
def addRivers():

	#BTP - I call the function just because it's the one after GenerateTerrainType in chronological order
	if (CyMap().getCustomMapOption(0) > 0):
		forceBarrenLand()
	
	CyPythonMgr().allowDefaultImpl()
	
def forceBarrenLand():
	map = CyMap()
	
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()

	
	p = map.plot(map.getGridWidth()*50/100,map.getGridHeight()*50/100)
	if p.isPeak():
		# If a peak is along the coast, change to hills and recalc.
		p.setPlotType(PlotTypes.PLOT_LAND, true, true)		
	p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
	if isBTPon:	
		p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_VOLCANO"), -1)
	else:
		p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)	

	if iPlayers == 8 or iPlayers == 9 or iPlayers == 10:
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)	
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
				p = map.plot(x,y)					
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)					
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)	
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
				p = map.plot(x,y)					
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)					
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)	
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)					
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					

	if iPlayers == 6 or iPlayers == 7:
		for x in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*25/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*40/100,map.getGridHeight()*60/100):
			for y in range(map.getGridWidth()*75/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)				
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*60/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)			
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*60/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					

	if iPlayers == 5:
		for x in range(0,map.getGridWidth()*10/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)
		for x in range(map.getGridWidth()*10/100,map.getGridWidth()*20/100):
			for y in range(map.getGridWidth()*15/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)				
		for x in range(0,map.getGridWidth()*20/100):
			for y in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)
		for x in range(0,map.getGridWidth()*35/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)
		for x in range(map.getGridWidth()*65/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)				
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)
		for x in range(map.getGridWidth()*90/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)	
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*90/100):
			for y in range(map.getGridWidth()*15/100,map.getGridHeight()*40/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*45/100,map.getGridHeight()*55/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)			
			
	if iPlayers == 4:
		for x in range(0,map.getGridWidth()*20/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(0,map.getGridWidth()*20/100):
			for y in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)	
				
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)	

		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)						

		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)	




	if iPlayers == 3:
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
			for y in range(map.getGridWidth()*45/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)			
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*45/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*35/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
		for x in range(map.getGridWidth()*65/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)
		for x in range(map.getGridWidth()*35/100,map.getGridHeight()*65/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)				
				
				
	if iPlayers == 2:
		for x in range(0,map.getGridWidth()*20/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)			
		for x in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		


		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*0/100,map.getGridHeight()*20/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)						

		for x in range(map.getGridWidth()*0/100,map.getGridHeight()*30/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)		
		for x in range(map.getGridWidth()*70/100,map.getGridHeight()*100/100):
			for y in range(map.getGridWidth()*80/100,map.getGridHeight()*100/100):
				p = map.plot(x,y)			
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"), True, True)					
				
				
def addFeatures():
	# Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isPeak() and pPlot.isCoastalLand():
			# If a peak is along the coast, change to hills and recalc.
			pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
			
	# Now add the features.
	featuregen = FeatureGenerator()
		
	'''featuregen.__init__(iJunglePercent=0, iForestPercent=20,
		jungle_grain=0, forest_grain=0)'''
		
	featuregen.__init__(iJunglePercent=0)
		
	featuregen.addFeatures()
	
	doFixTerrainBeforeBonus()
	
	return 0
	
def doFixTerrainBeforeBonus():### Used for ThreeIron Rare - 2.38 into Eldorado to move resources #####
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()				
	for iX in range(iW):
		for iY in range(iH):
			pPlot = CyMap().plot(iX, iY)
			if pPlot.getBonusType(-1) == -1 and pPlot.getFeatureType() == -1 and not pPlot.isWater() and not pPlot.isImpassable():
			
				if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
					iRandomTundra = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeTundra")
					if iRandomTundra <= 5:
						pPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"), True, True)


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

	
	BTS_ResourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')#2.18
	
	BTG_ResourcesToEliminate = ('BONUS_SULPHUR','BONUS_AMBER')
	BTG_NewResources = ('BONUS_TEA','BONUS_OLIVES','BONUS_SALT','BONUS_AMBER','BONUS_SULPHUR')
	
	BTS_ChoiceOFF = ('BONUS_IVORY','BONUS_MARBLE','BONUS_STONE','BONUS_GEMS','BONUS_SILVER','BONUS_GOLD')
	BTS_AlsoOFF = ('BONUS_WHEAT','BONUS_WINE','BONUS_SILK','BONUS_SPICE','BONUS_DYE','BONUS_SUGAR','BONUS_BANANA')

	
	#2.38 - in all cases
	if (type_string in BTS_ResourcesToBalance):
		return None
	
	if isBTPon:
		if (type_string in BTG_ResourcesToEliminate):
			return None		
	
	
	if CyMap().getCustomMapOption(6) == 1:
		if ((type_string in BTS_ChoiceOFF) or (type_string in BTS_AlsoOFF)):
			return None		
		
		if isBTPon:
			if (type_string in BTG_NewResources):
				return None			
	
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way
	
def normalizeAddExtras():


	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	everyPlayer = iPlayers
	everyTwoPlayer = max(1,iPlayers/2)
	everyThreePlayer = max(1,iPlayers/3)
	everyFourPlayer = max(1,iPlayers/4)#2.34
	iExtraTile = 0
	if iPlayers >= 4:
		iExtraTile = 1
	if iPlayers >= 6:
		iExtraTile = 2
	if iPlayers >= 7:
		iExtraTile = 3
	if iPlayers >= 9:
		iExtraTile = 4
		
	
	if (CyMap().getCustomMapOption(6) == 0):
		balancer.normalizeAddExtras()		
	
	#2.21
	elif (CyMap().getCustomMapOption(6) == 1):
		#Add External Fishes
		BTPExternalCoastEnrich(14,20,20,80,80)
			
			
		#Balance the capital -- Original start
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_HORSE"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_COPPER"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_IRON"),4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	
		
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_ALUMINUM"),6,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_URANIUM"),6,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_COAL"),6,True,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		

		
		#Balanced around player
		BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))

		#2.34
		if isBTPon:
			BTPForceResourceLand(100,True,CyGlobalContext().getInfoTypeForString("BONUS_POTATO"),5,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))		
			
			#Center Unique
			BTPresourceFromCenter(1,2+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		
		#1 Extra Elephant if 2 players (so 2 basically)
		if iPlayers == 2 or iPlayers == 3:
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
			
			#2.26 - 1 extra Rice
			BTPresourceFromCenter(3,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_RICE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
				
		#Center by player size
		for i in range(everyFourPlayer):#2.34 Reduce frequence of some + added new bits
		
			if (CyMap().getCustomMapOption(1) == 1):#also 3 extra UU resource
			
				if isBTPon:
					BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SALT"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
					BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_TEA"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
					BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_OLIVES"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
					## 2.34 New Block for new resource ####
					BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_DIAMOND"),CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
					BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
					BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))	
					BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH"))
					## 2. 35
					BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_NICKEL"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
					BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_LEAD"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
				
		for i in range(everyThreePlayer):

			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_STONE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			
			## Need to update CvMapGeneratorUtil.BTPMapUtil in order to take this in#
			BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_FISH"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))
			BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_CRAB"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))
			BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_CLAM"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))
			BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_WHALE"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))	

			BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SILVER"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))			
			BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_GEMS"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))			
			BTPresourceFromCenter(1,5+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_GOLD"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	

			## 2. 35
			if isBTPon:
				BTPresourceFromCenter(2,3+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_AMBER"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
				BTPresourceFromCenter(2,7+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))			

			
		for i in range(everyTwoPlayer):
			#2.23 Ivory every two players rather than 3
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
		
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_WINE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SILK"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SPICE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_SUGAR"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_DYE"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
			BTPresourceFromCenter(2,8+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_INCENSE"),CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))
		
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"))				
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_FUR"),CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"))						
			BTPresourceFromCenter(2,6+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))

			BTPresourceFromCenter(1,4+iExtraTile,CyGlobalContext().getInfoTypeForString("BONUS_CORN"),CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))		
	
		#2.41 - Enrich 3 player map back of games of March 2025
		if iPlayers == 3:
			BTPresourceFromPoint(25,25,1,3,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))
			BTPresourceFromPoint(75,25,1,3,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"),CyGlobalContext().getInfoTypeForString("TERRAIN_COAST"))
			BTPresourceFromPoint(25,25,1,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			BTPresourceFromPoint(75,25,1,3,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			BTPresourceFromPoint(25,25,1,4,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
			BTPresourceFromPoint(75,25,1,4,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))
	
	#Clean the ice
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			p = CyMap().plot(x,y)	
			if p.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_ICE"):
				p.setFeatureType(-1, -1)			
			if p.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_JUNGLE"):
				p.setFeatureType(-1, -1)
				
				
	#Forest Density
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	if (CyMap().getCustomMapOption(3) == 1):
		for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				p = CyMap().plot(x,y)	
				if p.getFeatureType() == CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"):
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					if iProba <= 40:
						p.setFeatureType(-1, -1)						
	

	if (CyMap().getCustomMapOption(0) == 2):				
		BTPFreezeOcean(True,20,False)
	
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride
	

def normalizeStartingPlotLocations():

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
		
		
	if (CyMap().getCustomMapOption(7) == 1):
		if isBTPon :
			BTPLeftRightTwoTeams(True)		
		else:
			BTPLeftRightTwoTeams(False)		
				
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case						
	
	
def startHumansOnSameTile():
	map = CyMap()
	
	#doing in normalizeAddExtra was too early -- one problem if spectator is in slot 1 it doesn't work
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(2) > 0):#quicker if don't run when 0
			iProbaTreshold = 25 * CyMap().getCustomMapOption(2) #Gives %age on 100
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(iProbaTreshold)	
		
	if isBTPon:#2.25
		if (CyMap().getCustomMapOption(8) > 0):
			if (CyMap().getCustomMapOption(8)  == 1):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,100,0,0,5)
			if (CyMap().getCustomMapOption(8)  == 2):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,0,5)				
			if (CyMap().getCustomMapOption(8)  == 3):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,100,5)		

	if (CyMap().getCustomMapOption(4) == 1):
		return True			
		
		
def BTGFreeUnit():

	if (CyMap().getCustomMapOption(9) == 0):
		return -1
	elif (CyMap().getCustomMapOption(9) == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (CyMap().getCustomMapOption(9) == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (CyMap().getCustomMapOption(9) == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	elif (CyMap().getCustomMapOption(9) == 4):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_GREAT_LEGEND")				
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():

	iCount = CyMap().getCustomMapOption(10)	
		
	return iCount
	
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

def BTPExternalCoastEnrich(iProbaTreshold,maxX,maxY,minX,minY):	
	
	random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))

	downX = CyMap().getGridWidth() * maxX / 100
	upX = CyMap().getGridWidth() * minX / 100
	downY = CyMap().getGridWidth() * maxY / 100
	upY = CyMap().getGridWidth() * minY / 100
	
	whale = CyGlobalContext().getInfoTypeForString("BONUS_WHALE")
	fish = CyGlobalContext().getInfoTypeForString("BONUS_FISH")
	clam = CyGlobalContext().getInfoTypeForString("BONUS_CLAM")
	crab = CyGlobalContext().getInfoTypeForString("BONUS_CRAB")
	
	waterBonusList = [whale,fish,clam,crab]
	
	for x in range(CyMap().getGridWidth()):
		for y in range(CyMap().getGridHeight()):
			if (x <= downX or x >= upX or y <= downY or y >= upY):
				p = CyMap().plot(x,y)
				if (p.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")):
					if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
						
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if iProba <= iProbaTreshold:					
							random.shuffle(waterBonusList)
							#p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_WHALE"))
							p.setBonusType(waterBonusList[0])

	
	
def BTPresourceFromCenter(minFromCenter,maxFromCenter,iResourceType,iTerrainType):

		centerX = CyMap().getGridWidth()*50/100
		centerY = CyMap().getGridHeight()*50/100
		plotCenter = CyMap().plot(CyMap().getGridWidth()*50/100,CyMap().getGridHeight()*50/100)
		random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
		
		plotsboundaries = []
		plotsboundariesSafe = []
		for dx in range(-maxFromCenter,maxFromCenter):
			for dy in range(-maxFromCenter,maxFromCenter):
				p = CyMap().plot(centerX+dx,centerY+dy)
				#if (((dx >= minFromCenter) or (dx <= -minFromCenter)) and ((dy >= minFromCenter) or (dy <=-minFromCenter))): 
				if ((abs(dx) >= minFromCenter) and (abs(dy) >= minFromCenter)):
					if (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						
						#2.21
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(centerX+dx+tx-1,centerY+dy+ty-1)
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
					p.setTerrainType(iTerrainType,True,True)
					#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"),True,True)#for debug
					p.setBonusType(iResourceType)
					p.setFeatureType(-1, -1)
					break	
			
		else:
			random.shuffle(plotsboundaries)
			for p in plotsboundaries:
				if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
					p.setTerrainType(iTerrainType,True,True)
					p.setBonusType(iResourceType)
					p.setFeatureType(-1, -1)
					break		
	
	
def BTPresourceFromPoint(Xpct,Ypct,minFromCenter,maxFromCenter,iResourceType,iTerrainType):

		centerX = CyMap().getGridWidth()*Xpct/100 #### Special for 3 players extra resources
		centerY = CyMap().getGridHeight()*Ypct/100 #### Special for 3 players extra resources
		plotCenter = CyMap().plot(CyMap().getGridWidth()*Xpct/100,CyMap().getGridHeight()*Ypct/100)
		random.seed(CyGlobalContext().getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
		
		plotsboundaries = []
		plotsboundariesSafe = []
		for dx in range(-maxFromCenter,maxFromCenter):
			for dy in range(-maxFromCenter,maxFromCenter):
				p = CyMap().plot(centerX+dx,centerY+dy)
				#if (((dx >= minFromCenter) or (dx <= -minFromCenter)) and ((dy >= minFromCenter) or (dy <=-minFromCenter))): 
				if ((abs(dx) >= minFromCenter) and (abs(dy) >= minFromCenter)):
					if (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						
						#2.21
						iBonusCount = 0
						for tx in range(3):
							for ty in range(3):
								testP = CyMap().plot(centerX+dx+tx-1,centerY+dy+ty-1)
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
					p.setTerrainType(iTerrainType,True,True)
					#p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"),True,True)#for debug
					p.setBonusType(iResourceType)
					p.setFeatureType(-1, -1)
					break	
			
		else:
			random.shuffle(plotsboundaries)
			for p in plotsboundaries:
				if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
					p.setTerrainType(iTerrainType,True,True)
					p.setBonusType(iResourceType)
					p.setFeatureType(-1, -1)
					break	
	
	
	
def BTPForceResourceLand(iProbaTreshold,bMainLandOnly,iResourceType,iDistance,bMakeHill,iForceTerrain):

	gc = CyGlobalContext()
	map = CyMap()
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))

	for i in range(gc.getMAX_CIV_PLAYERS()):
	
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= iProbaTreshold:
	
			if gc.getPlayer(i).isEverAlive():
				start_plot = gc.getPlayer(i).getStartingPlot()
				startx, starty = start_plot.getX(), start_plot.getY()
				plotsboundaries = []
				plotsboundariesSafe = []
				plotsboundariesSafeNoRiver = []
				has_resource = false
				for dx in range(-iDistance,iDistance):
					for dy in range(-iDistance,iDistance):
						p = map.plot(startx+dx,starty+dy)
						#if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):
						if (bMainLandOnly == True) :
							if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()) and p.getArea() == CyMap().findBiggestArea(False).getID():	
								iBonusCount = 0
								for tx in range(3):
									for ty in range(3):
										testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
										if (testP.getBonusType(-1) != -1):
											iBonusCount += 1		
								if iBonusCount >= 1:
									plotsboundaries.append(p)
								elif not p.isRiver():
									plotsboundariesSafeNoRiver.append(p)
								else :
									plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
								if p.getBonusType(-1) == iResourceType:
									has_resource = True
						if (bMainLandOnly == False) :								
							if ((dx != 0) or (dy != 0)) and (not p.isNone()) and (not p.isImpassable()) and (not p.isWater()):			
								iBonusCount = 0
								for tx in range(3):
									for ty in range(3):
										testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
										if (testP.getBonusType(-1) != -1):
											iBonusCount += 1		
								if iBonusCount >= 1:
									plotsboundaries.append(p)
								elif not p.isRiver():
									plotsboundariesSafeNoRiver.append(p)										
								else :
									plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority
								if p.getBonusType(-1) == iResourceType:
									has_resource = True
									
				if not has_resource:
					if len(plotsboundariesSafeNoRiver) > 0:	#2.34 new block									
						random.shuffle(plotsboundariesSafeNoRiver)	
						for p in plotsboundariesSafeNoRiver:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break						
				
					elif len(plotsboundariesSafe) > 0:										
						random.shuffle(plotsboundariesSafe)	
						for p in plotsboundariesSafe:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break
								
					else:								
						random.shuffle(plotsboundaries)	
						for p in plotsboundaries:
							if (p.getBonusType(-1) == BonusTypes.NO_BONUS):
								if bMakeHill:
									p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
								else:
									p.setPlotType(PlotTypes.PLOT_LAND, True, True)
								p.setTerrainType(iForceTerrain, True, True)
								p.setBonusType(iResourceType)
								p.setFeatureType(-1,-1)#2.34 avoid resource on floodplains transformed into 5F
								has_resource = True
								break	
	
	
	
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