#
#	FILE:	 LD_Mirror_Battleground.py
#	AUTHOR: Leszek Deska LDeska@wp.pl [POL][KAC]LDeska
#       www.civilization.org.pl 
#	CONTRIB: Bob Thomas (Sirian), Andy Szybalski
#	PURPOSE: Regional map script - Ideal for quick MP team games, mirrored
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import HintedWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_TEAM_BATTLEGROUND_DESCR"

def getNumCustomMapOptions():
	return 0
	
def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def isSeaLevelMap():
	return 0

def getWrapX():
	return False
def getWrapY():
	return False
	
def getTopLatitude():
	return 80
def getBottomLatitude():
	return -80
	
def minStartingDistanceModifier():
	return -65

def beforeGeneration():
	global equator
	global team_num
	team_num = []
	team_index = 0
	topVsBottomCheck = 1
	if topVsBottomCheck == 1:
		equator = CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT")
	else:
		equator = CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")
	for teamCheckLoop in range(18):
		if CyGlobalContext().getTeam(teamCheckLoop).isEverAlive():
			team_num.append(team_index)
			team_index += 1
		else:
			team_num.append(-1)
	return None

def getGridSize(argsList):
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(3,6),
		WorldSizeTypes.WORLDSIZE_TINY:		(4,7),
		WorldSizeTypes.WORLDSIZE_SMALL:		(5,8),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(6,10),
		WorldSizeTypes.WORLDSIZE_LARGE:		(8,13),
		WorldSizeTypes.WORLDSIZE_HUGE:		(10,16)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Team Battleground) ...")
	global hinted_world, mapRand
	global fractal_world
	gc = CyGlobalContext()
	map = CyMap()
	mapRand = gc.getGame().getMapRand()
	userInputPlots = 1
	
	if userInputPlots == 2: # Four Corners
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

		# Set all blocks to land except a strip in the center
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
		plotTypes = hinted_world.generatePlotTypes(20)
	
		# Remove any land bridge that exists
		centerplotx = (iNumPlotsX - 1)//2
		dx = 1
		for x in range(centerplotx-dx, centerplotx+dx+1):
			for y in range(iNumPlotsY):
				i = map.plotNum(x, y)
				if plotTypes[i] != PlotTypes.PLOT_OCEAN:
					plotTypes[i] = PlotTypes.PLOT_OCEAN
		centerploty = (iNumPlotsY - 1)//2
		dy = 1
		for y in range(centerploty-dy, centerploty+dy+1):
			for x in range(iNumPlotsX):
				i = map.plotNum(x, y)
				if plotTypes[i] != PlotTypes.PLOT_OCEAN:
					plotTypes[i] = PlotTypes.PLOT_OCEAN
		
		# Now add the bridge across the center!
		sizekey = map.getWorldSize()
		sizevalues = {
			WorldSizeTypes.WORLDSIZE_DUEL:		3,
			WorldSizeTypes.WORLDSIZE_TINY:		4,
			WorldSizeTypes.WORLDSIZE_SMALL:		5,
			WorldSizeTypes.WORLDSIZE_STANDARD:	6,
			WorldSizeTypes.WORLDSIZE_LARGE:		8,
			WorldSizeTypes.WORLDSIZE_HUGE:		10
			}
		shift = sizevalues[sizekey]
		linewidth = 3
		offsetstart = 0 - int(linewidth/2)
		offsetrange = range(offsetstart, offsetstart + linewidth)
		westX1, southY1, eastX1, northY1 = centerplotx - shift, centerploty - shift, centerplotx + shift, centerploty + shift
		westX2, southY2, eastX2, northY2 = centerplotx - shift, centerploty - shift, centerplotx + shift, centerploty + shift
		bridge_data = [[westX1, southY1, eastX1, northY1], [westX2, northY2, eastX2, southY2]]
		for bridge_loop in range(2):
			[startx, starty, endx, endy] = bridge_data[bridge_loop]

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
							plotTypes[i] = PlotTypes.PLOT_LAND
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
							plotTypes[i] = PlotTypes.PLOT_LAND
					x += slope
		
		return plotTypes

	elif userInputPlots == 1: # Top vs Bottom
		fractal_world = FractalWorld(fracXExp=6, fracYExp=6)
		fractal_world.initFractal(continent_grain = 4, rift_grain = -1, has_center_rift = False, invert_heights = True)
		plot_types = fractal_world.generatePlotTypes(water_percent = 8)
		return plot_types

	else: # Left vs Right
		iNumPlotsX = map.getGridWidth()
		iNumPlotsY = map.getGridHeight()
	
		hinted_world = HintedWorld(4,2)
		centerx = (hinted_world.w - 1)//2	
		centery = (hinted_world.h - 1)//2
		bridgey = centery

		# set all blocks to land except a strip in the center
		for x in range(hinted_world.w):
			for y in range(hinted_world.h):
				if x == centerx:
					if y == bridgey:
						hinted_world.setValue(x,y,128) # coast
					else:
						hinted_world.setValue(x,y,0)
				else:
					hinted_world.setValue(x,y,255)
		
		hinted_world.buildAllContinents()
		plotTypes = hinted_world.generatePlotTypes(20)
	
		#fix any land bridge that exists
		centerplotx = (iNumPlotsX - 1)//2
		dx = 1
		for x in range(centerplotx-dx, centerplotx+dx+1):
			for y in range(iNumPlotsY):
				i = map.plotNum(x, y)
				if plotTypes[i] != PlotTypes.PLOT_OCEAN:
					plotTypes[i] = PlotTypes.PLOT_OCEAN
		return plotTypes

class TeamBGTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def generateTerrainAtPlot(self, iX, iY):
		global equator
		lat = 0.8 * self.getLatitudeAtPlot(iX,iY)

		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		terrainVal = self.terrainGrass

		if lat >= self.fSnowLatitude:
			terrainVal = self.terrainIce
		elif lat >= self.fTundraLatitude:
			terrainVal = self.terrainTundra
		elif lat < self.fGrassLatitude:
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

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
	# MIRRORIZE PLOTS
	gc = CyGlobalContext()
	map = CyMap()
	
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	reflect_x = lambda x: iX
	reflect_y = lambda y: iH - iY - 1

	for iX in range(iW):
		for iY in range(iH / 2):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setPlotType(rPlot.getPlotType(), false, false)
	
	# Smooth any graphical glitches these changes may have produced.
	map.recalculateAreas()

	NiTextOut("Generating Terrain (Python Team Battleground) ...")
	terraingen = TeamBGTerrainGenerator()
	terraingen.__init__(iDesertPercent=15)
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class TeamBGFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns a value in the range of 0.0 (tropical) to 1.0 (polar)"
		return 0.8 * (abs((self.iGridH/2) - iY)/float(self.iGridH/2))

def addFeatures():
	# MIRRORIZE LAKES
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iX
	reflect_y = lambda y: iH - iY - 1

	for iX in range(iW):
		for iY in range(iH / 2):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			if pPlot.getPlotType() != rPlot.getPlotType():
				pPlot.setPlotType(rPlot.getPlotType(), false, false)

	# Smooth any graphical glitches these changes may have produced.
	map.recalculateAreas()

	NiTextOut("Adding Features (Python Team Battleground) ...")
	featuregen = TeamBGFeatureGenerator()
	featuregen.addFeatures()
	return 0

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
		reflect_x = lambda x: iX
		reflect_y = lambda y: iH - iY - 1
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
		if iPlayers > 2 and userInputPlots <= 1 and y <= iH * 0.4:
			return true
		if iPlayers > 2 and userInputPlots >= 2 and y >= iH * 0.1 and y <= iH * 0.4:
			return true
		# 1 vs 1 game, so make sure the players start farther apart!
		# LDeska and in the middle (horizontally)
		if iPlayers == 2 and userInputPlots <= 1 and y <= iH * 0.2 and x >= iW * 0.35 and x <= iW * 0.65:
			return true
		if iPlayers == 2 and userInputPlots >= 2 and y >= iH * 0.2 and y <= iH * 0.3:
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
			if teamID == 0 and shuffle and y >= iH * 0.75:
				return true
			if teamID == 1 and not shuffle and y >= iH * 0.75:
				return true
			if teamID == 0 and not shuffle and y <= iH * 0.25:
				return true
			if teamID == 1 and shuffle and y <= iH * 0.25:
				return true
			return false

		# Three or Four Teams
		else:
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

def getRiverStartCardinalDirection(argsList):
	"Returns the cardinal direction of the first river segment."
	pPlot = argsList[0]
	print pPlot
	map = CyMap()
	x, y = pPlot.getX(), pPlot.getY()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	if y < iH/2:
		return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
	else:
		return CardinalDirectionTypes.CARDINALDIRECTION_NORTH

	userInputPlots = 1

	if userInputPlots == 0:
		if x < iW/2:
			return CardinalDirectionTypes.CARDINALDIRECTION_EAST
		else:
			return CardinalDirectionTypes.CARDINALDIRECTION_WEST
	elif userInputPlots == 2:
		if y < iH/2:
			return CardinalDirectionTypes.CARDINALDIRECTION_NORTH
		else:
			return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
	else:
		CyPythonMgr().allowDefaultImpl()

def addLakes():
	# MIRRORIZE TERRAIN
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iX
	reflect_y = lambda y: iH - iY - 1

	for iX in range(iW):
		for iY in range(iH / 2):
			pPlot = map.plot(iX, iY)
			rPlot = map.plot(reflect_x(iX), reflect_y(iY))
			pPlot.setTerrainType(rPlot.getTerrainType(), false, false)

	# MIRRORIZE RIVERS
	for iY in range(iH / 2):
		for iX in range(iW):
			pPlot = map.plot(iX, iH / 2 - iY - 1)
			rPlot = map.plot(iX, iH / 2 + iY )
			sPlot = map.plot(iX, iH / 2 - iY )
			pPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
			pPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
			if rPlot.isWOfRiver():
				if rPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
					rivDir = CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
				else:
					rivDir = CardinalDirectionTypes.CARDINALDIRECTION_NORTH
				pPlot.setWOfRiver(true, rivDir)
			if rPlot.isNOfRiver():
				rivDir = rPlot.getRiverWEDirection()
				sPlot.setNOfRiver(true, rivDir)
	map.recalculateAreas()

	return CyPythonMgr().allowDefaultImpl()

def addGoodies():
	# MIRRORIZE FEATURES AND BONUSES
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	reflect_x = lambda x: iX
	reflect_y = lambda y: iH - iY - 1

	for iX in range(iW):
		for iY in range(iH / 2):
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
	
	reflect_x = lambda x: iX
	reflect_y = lambda y: iH - iY - 1

	for iX in range(iW):
		for iY in range(iH / 2):
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
