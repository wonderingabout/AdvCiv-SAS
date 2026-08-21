#
#	FILE:	 Team_Battleground.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Andy Szybalski
#	PURPOSE: Regional map script - Ideal for quick MP team games.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#
#
# Ruff - Desert Bridge & Round Start
#  Additional options added by Ruff_Hi from
#        - Civilization Fanatics (http://forums.civfanatics.com/member.php?u=64034)
#        - Deviant Minds (http://deviantminds.us/forum/memberlist.php?mode=viewprofile&u=8)
#        - Realms Beyond (http://realmsbeyond.net/forums/member.php?u=555)
#    - Left v Right with a desert land bridge
#    - round with starting locations uniformly spread around the circle
#    - donut - same as round but with water at the center


from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import HintedWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

from CvMapGeneratorUtil import BonusBalancer

balancer = BonusBalancer()

from math import sqrt
from math import cos
from math import sin
from math import radians

import random

iAncientStartOptionValue = 5
try:
	bMyTest = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
except:
	iAncientStartOptionValue -= 1

def getDescription():
#	BugUtil.debug("Team_Battleground: getDescription")
	return "TXT_KEY_MAP_SCRIPT_TEAM_BATTLEGROUND_DESCR"
	
def getDescriptionTitle():
	return "A very popular BTS multiplayer map which see two side face each other as a top versus bottom configuration and separated by a large band of desert in the middle"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return "There is a popular option in competitive teamers to have the starting location 'separated', in 5v5, 3 on top and 2 on bottom for each team"

def getDescriptionSecond():#Script tip : (on TOP)
	return ""	
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Any teamer with a focus on early (ancient, classical) starts. Game will be relatively short and violent, it will be hard to advance far in the tech path "	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Immediate impact traits are strong, AGGRESSIVE and EXPANSIVE leading the way"		

def getNumCustomMapOptions():
#	BugUtil.debug("Team_Battleground: getNumCustomMapOptions")
	return 13
	
def getNumHiddenCustomMapOptions():
	return 1
	
def getCustomMapOptionName(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionName")
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_TEAM_PLACEMENT",
		1:	"TXT_KEY_MAP_SCRIPT_TEAM_SETTING",
		2:  "TXT_KEY_MAP_WORLD_WRAP",
		3:	"Ancient Starts",
		4:	"Elephants",
		5:	"Wonder Resources",		
		6:	"BTG Free Unit",
		7:  "BTG Amt Free Unit",
		8:	"Land Color",
		9:	"Extreme Latitudes",
		10:	"BTG Type of Forest",
		11:  "BTG Spectator Notes",
		12:	"Credit"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	6,
		1:	3,
		2:	3,
		3:	iAncientStartOptionValue,
		4:	4,
		5:	3,		
		6:	5,
		7:	4,
		8:	3,
		9:	2,
		10:	2,
		11:	2,
		12:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDescAt")
	[iOption, iSelection] = argsList

	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_LEFT_VS_RIGHT",
			1: "TXT_KEY_MAP_SCRIPT_TOP_VS_BOTTOM",
			2: "TXT_KEY_MAP_SCRIPT_FOUR_CORNERS",
			3: "TXT_KEY_MAP_SCRIPT_LEFT_VS_RIGHT_BRIDGE",
			4: "TXT_KEY_MAP_SCRIPT_ROUND",
			5: "TXT_KEY_MAP_SCRIPT_DONUT"
			},
		1:	{
			0: "TXT_KEY_MAP_SCRIPT_START_TOGETHER",
			1: "TXT_KEY_MAP_SCRIPT_START_SEPARATED",
			2: "TXT_KEY_MAP_SCRIPT_START_ANYWHERE"
			},
		2:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		3:	{
			0: "Normal - BTS default implementation",
			1: "Free Hunting Tech",
			2: "Free 6 Base Ancient Techs",
			3: "Free Hunting Tech, if team has it, gives Fishing instead",
			4: "BTG Option active no Warrior Start"
			},				
		4:	{
			0: "Normal - BTS default implementation",
			1: "No Elephants",
			2: "Balanced bewteen 3 and 4 tiles away",
			3: "Balanced bewteen 4 and 6 tiles away"
			},	
		5:	{
			0: "Normal Stone & Marble",
			1: "No Stone & Marble at all on map",
			2: "Bottom of map is Stone, Top of map is Marble",
			},			
		6:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			4: "Great Legend"
			},
		7:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},					
		8:	{
			0: "Normal Color",
			1: "Green Land",
			2: "Super Green - No Desert (except middle band)"
			},	
		9:	{
			0: "Normal Color - Tundra and Ice",
			1: "Green Land"
			},		
		10:	{
			0: "Normal Forest",
			1: "Palm Forest everywhere"
			},				
		11:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in FIRST slot - Only Top V Bottom"
			},	
		12:	{
			0: "Penny for Beyond The Game - Works for BTS, BTG Options have no effect"		
			}			
		}

	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
#	BugUtil.debug("Team_Battleground: getCustomMapOptionDefault")
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:	1,
		2:  1,
		3:	iAncientStartOptionValue - 1 ,
		4:	0,
		5:	0,
		6:	0,
		7:	0,
		8:	0,
		9:	0,
		10:	0,
		11:	1,
		12:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
#	BugUtil.debug("Team_Battleground: isRandomCustomMapOption")
	[iOption] = argsList
	option_random = {
		0:	True,
		1:	False,
		2:  False,
		3:	False,
		4:	False,
		5:	False,
		6:	False,
		7:	False,
		8:	False,
		9:	False,
		10:	False,
		11: False,
		12:	False
		}
	return option_random[iOption]

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def isSeaLevelMap():
	return 0

def getWrapX():	return (iOptionValue_Wrap == 1 or iOptionValue_Wrap == 2)
	
def getWrapY():	return (iOptionValue_Wrap == 2)
	
def getTopLatitude():
	return 80
def getBottomLatitude():
	return -80
	
def minStartingDistanceModifier():
	return -65
	
def beforeInit():#2.41

	beforeInitOptionsValue()	
	
	#2.22
	global isBTPon
	global iNumSpectators
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		
	except:
		isBTPon = False
		iNumSpectators = 0	
		
		
def beforeInitOptionsValue():#2.41
	
	global iOptionValue_TeamPlacement
	global iOptionValue_TeamSettings
	global iOptionValue_Wrap	
	global iOptionValue_Elephant	
	global iOptionValue_WonderResources	
	global iOptionValue_StartingUnit
	global iOptionValue_StartingUnitCount	
	global iOptionValue_LandGreen
	global iOptionValue_LandExtreme
	global iOptionValue_ForestType
	global iOptionValue_AncientStart#2.42
	
	iOptionValue_TeamPlacement = CyMap().getCustomMapOption(0)
	iOptionValue_TeamSettings = CyMap().getCustomMapOption(1)
	iOptionValue_Wrap = CyMap().getCustomMapOption(2)	
	iOptionValue_AncientStart = CyMap().getCustomMapOption(3)
	iOptionValue_Elephant = CyMap().getCustomMapOption(4)
	iOptionValue_WonderResources = CyMap().getCustomMapOption(5)
	iOptionValue_StartingUnit = CyMap().getCustomMapOption(6)
	iOptionValue_StartingUnitCount = CyMap().getCustomMapOption(7)
	iOptionValue_LandGreen = CyMap().getCustomMapOption(8)	
	iOptionValue_LandExtreme = CyMap().getCustomMapOption(9)	
	iOptionValue_ForestType = CyMap().getCustomMapOption(10)
						

def beforeGeneration():
	
#	BugUtil.debug("Team_Battleground: beforeGeneration")
	global equator
	global team_num
	team_num = []
	team_index = 0
	topVsBottomCheck = CyMap().getCustomMapOption(0)
	if topVsBottomCheck == 1:
		equator = CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT")
	else:
		equator = CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS")
		
	#2.22
	'''if iNumSpectators > 0 and gc.getGame().countCivTeamsEverAlive() == 2:
		team_num.append(1)
		team_num.append(2)
		#I hardcode there are 2 teams'''
		
	#else :''' #normal base TBG case
	#for teamCheckLoop in range(18):
	#2.24
	if isBTPon:
		iRange = 41
	else:
		iRange = 18
	
	#for teamCheckLoop in range(iRange):#2.23a
	for teamCheckLoop in range(CyGlobalContext().getMAX_CIV_PLAYERS()):#2.35 when you reduce to 12 players... cannot hardcode this
		if CyGlobalContext().getTeam(teamCheckLoop).isEverAlive():
			team_num.append(team_index)
			team_index += 1
		else:
			team_num.append(-1)
			
						
	return None

def getGridSize(argsList):
#	BugUtil.debug("Team_Battleground: getGridSize")
	"Different grids, depending on the choice of Team Placement. Very small worlds."
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []

	# Get user input.
	grid_choice = CyMap().getCustomMapOption(0)  # 0 = left v right, 1 = top v bottom, 2 = four corners, 3 = left v right with land bridge, 4 = round, 5 = donut
	if grid_choice == 2:
		grid_choice = 1

	if grid_choice == 3: # left v right with land bridge defaults to same as left v right
		grid_choice = 0
	
	if (grid_choice == 4   # round
	or  grid_choice == 5): # donut
		grid_choice = 1
	
	grid_sizes = [{WorldSizeTypes.WORLDSIZE_DUEL:		(5,3),
	               WorldSizeTypes.WORLDSIZE_TINY:		(6,4),
	               WorldSizeTypes.WORLDSIZE_SMALL:		(8,5),
	               WorldSizeTypes.WORLDSIZE_STANDARD:	(10,6),
	               WorldSizeTypes.WORLDSIZE_LARGE:		(13,8),
	               WorldSizeTypes.WORLDSIZE_HUGE:		(16,10)
				   },
	              {WorldSizeTypes.WORLDSIZE_DUEL:		(4,4),
	               WorldSizeTypes.WORLDSIZE_TINY:		(5,5),
	               WorldSizeTypes.WORLDSIZE_SMALL:		(6,6),
	               WorldSizeTypes.WORLDSIZE_STANDARD:	(8,8),
	               WorldSizeTypes.WORLDSIZE_LARGE:		(10,10),
	               WorldSizeTypes.WORLDSIZE_HUGE:		(13,13)
				   }
	]

	[eWorldSize] = argsList
	return grid_sizes[grid_choice][eWorldSize]

def generatePlotTypes():
#	BugUtil.debug("Team_Battleground: generatePlotTypes")
	NiTextOut("Setting Plot Types (Python Team Battleground) ...")
	global hinted_world, mapRand
	global fractal_world
	gc = CyGlobalContext()
	map = CyMap()
	mapRand = gc.getGame().getMapRand()
	userInputPlots = map.getCustomMapOption(0)
	
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

	if (userInputPlots == 4   # round
	or  userInputPlots == 5): # donut
		hinted_world = HintedWorld()
		iNumPlotsX = map.getGridWidth()
		iNumPlotsY = map.getGridHeight()

		centery = (iNumPlotsY - 1)//2
		centerx = (iNumPlotsX - 1)//2
		radii = centery - 1

		# Set all blocks to ocean except the inner circle
		for x in range(iNumPlotsX):
			for y in range(iNumPlotsY):
				dist_xy_c = sqrt( (x - centerx) ** 2 + (y - centery) ** 2)
				if dist_xy_c < radii:
					hinted_world.setValue(x,y,255)
				else:
					hinted_world.setValue(x,y,0) # ocean

		hinted_world.buildAllContinents()
		plotTypes = hinted_world.generatePlotTypes(water_percent = 0)

		if userInputPlots == 5: # donut
			# get the size of the hole
			map_size = map.getWorldSize()
			sizevalues = {
				WorldSizeTypes.WORLDSIZE_DUEL:		2,
				WorldSizeTypes.WORLDSIZE_TINY:		3,
				WorldSizeTypes.WORLDSIZE_SMALL:		4,
				WorldSizeTypes.WORLDSIZE_STANDARD:	5,
				WorldSizeTypes.WORLDSIZE_LARGE:		7,
				WorldSizeTypes.WORLDSIZE_HUGE:		8
				}
			hole_radii = sizevalues[map_size]

		# Set all blocks to ocean except the inner circle
		for x in range(iNumPlotsX):
			for y in range(iNumPlotsY):
				i = map.plotNum(x, y)
				dist_xy_c = sqrt( (x - centerx) ** 2 + (y - centery) ** 2)

#				if (dist_xy_c < radii):
#					if not (plotTypes[i] == PlotTypes.PLOT_LAND
#					and plotTypes[i] == PlotTypes.PLOT_PEAK
#					and plotTypes[i] == PlotTypes.PLOT_HILLS):
#						plotTypes[i] = PlotTypes.PLOT_LAND
#				else:
#					plotTypes[i] = PlotTypes.PLOT_OCEAN

				if (dist_xy_c >= radii):
					plotTypes[i] = PlotTypes.PLOT_OCEAN

				if (userInputPlots == 5 # donut
				and dist_xy_c < hole_radii):
					plotTypes[i] = PlotTypes.PLOT_OCEAN

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

		if userInputPlots == 3: # Left v Right with bridge
			centerplotx = (iNumPlotsX)//2
			centerploty = (iNumPlotsY)//2
			dy = 1
			for x in range(iNumPlotsX):
				for y in range(centerploty-dy, centerploty+dy+1):
					i = map.plotNum(x, y)
					if plotTypes[i] == PlotTypes.PLOT_OCEAN:
						plotTypes[i] = PlotTypes.PLOT_LAND

		return plotTypes

class TeamBGTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def generateTerrainAtPlot(self, iX, iY):
#		BugUtil.debug("Team_Battleground: generateTerrainAtPlot")
		global equator
		lat = 0.8 * self.getLatitudeAtPlot(iX,iY)

		if not self.map.plot(iX, iY).isWater():
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

		map = CyMap()
		userInputPlots = map.getCustomMapOption(0)
		if userInputPlots == 3: # Left v Right with bridge
			if (iY - 3 > 0
			and iY + 3 < map.getGridHeight()):
				if (self.map.plot(iX, iY - 3).isWater()
				and self.map.plot(iX, iY + 3).isWater()):
					terrainVal = self.terrainDesert
				elif (self.map.plot(iX, iY - 3).isWater()
				or    self.map.plot(iX, iY + 3).isWater()):
					terrainVal = self.terrainPlains

		if (userInputPlots == 4   # round
		or  userInputPlots == 5): # donut
			centery = (map.getGridHeight() - 1)//2
			centerx = (map.getGridWidth() - 1)//2
			radii = centery - 1
			dist_xy_c = sqrt( (iX - centerx) ** 2 + (iY - centery) ** 2)

			if userInputPlots == 5: # donut
				# get the size of the hole
				map_size = map.getWorldSize()
				sizevalues = {
					WorldSizeTypes.WORLDSIZE_DUEL:		2,
					WorldSizeTypes.WORLDSIZE_TINY:		3,
					WorldSizeTypes.WORLDSIZE_SMALL:		4,
					WorldSizeTypes.WORLDSIZE_STANDARD:	5,
					WorldSizeTypes.WORLDSIZE_LARGE:		7,
					WorldSizeTypes.WORLDSIZE_HUGE:		8
					}
				hole_radii = sizevalues[map_size]
			else:
				hole_radii = -1

			# Set all blocks to ocean except the inner circle
			if (dist_xy_c < radii
			and dist_xy_c > hole_radii
			and self.map.plot(iX, iY).isWater()):
				return self.terrainPlains

		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
#	BugUtil.debug("Team_Battleground: generateTerrainTypes")
	NiTextOut("Generating Terrain (Python Team Battleground) ...")
	terraingen = TeamBGTerrainGenerator()
	
	if iOptionValue_LandGreen == 0:#normal case
		terraingen.__init__(iDesertPercent=15)
	elif iOptionValue_LandGreen == 1:#green case
		terraingen.__init__(iDesertPercent=15, iPlainsPercent=0)
	elif iOptionValue_LandGreen == 2:#super green
		terraingen.__init__(iDesertPercent=0, iPlainsPercent=0)
			
	terrainTypes = terraingen.generateTerrain()
	
	if iOptionValue_LandExtreme > 0:
		# Eliminate snow and tundra completely (they still get placed sometimes at extreme latitudes)
		for i in range(len(terrainTypes)):
			if (terrainTypes[i] == terraingen.terrainIce) or (terrainTypes[i] == terraingen.terrainTundra):
				terrainTypes[i] = terraingen.terrainGrass		
	
	return terrainTypes

class TeamBGFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns a value in the range of 0.0 (tropical) to 1.0 (polar)"
		return 0.8 * (abs((self.iGridH/2) - iY)/float(self.iGridH/2))

def addFeatures():
#	BugUtil.debug("Team_Battleground: addFeatures")
	NiTextOut("Adding Features (Python Team Battleground) ...")
	featuregen = TeamBGFeatureGenerator()
	featuregen.addFeatures()
	return 0

def assignStartingPlots():
#	BugUtil.debug("Team_Battleground: assignStartingPlots1")
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	global shuffle
	global shuffledTeams
	global assignedPlayers

#	BugUtil.debug("Team_Battleground: assignStartingPlots2 %i %i %i %i", gc.getGame().countCivTeamsEverAlive(), gc.getGame().countCivTeamsAlive(), gc.getGame().countCivPlayersAlive(), gc.getGame().countCivPlayersEverAlive())

	assignedPlayers = [0] * gc.getGame().countCivPlayersAlive()

#	BugUtil.debug("Team_Battleground: assignStartingPlots3")

#	print shuffledTeams

	shuffle = gc.getGame().getMapRand().get(2, "Start Location Shuffle - PYTHON")

	global shuffledPlayers
	global player_num

	map = CyMap()
	userInputPlots = map.getCustomMapOption(0)

#	BugUtil.debug("Team_Battleground: assignStartingPlots userInputPlots %i", userInputPlots)

	if (userInputPlots == 4   # round
	or  userInputPlots == 5): # donut

#		BugUtil.debug("Team_Battleground: assignStartingPlots inside if")

# this block of code takes the players and shuffles them
# if the 'teams start together' is selected (ie map.getCustomMapOption(1) = 0)
# then the shuffled players are sorted into teams
# then each player in the shuffled player array is assigned a starting plot 1 in from the coast
# and uniformly spread around the circle

# shuffle the players
		player_num = gc.getGame().countCivPlayersAlive()
		userInputProximity = iOptionValue_TeamPlacement  # team members start together, 0 = True
		shuffleTeams = True # there is an option on screen for this but I don't know how to reference it

		shuffle_Array = []

		# shuffle the players
		for playerLoop in range(player_num):
			if shuffleTeams:
				shuffle_Array.append([dice.get(10000, "Shuffling Players - TBG PYTHON"), playerLoop])  # why 10,000?  Why not?
			else:
				shuffle_Array.append([1, playerLoop])

#			BugUtil.debug("Team_Battleground: assignStartingPlots shuffle array #1")
#			print shuffle_Array

		shuffle_Array.sort()

#		BugUtil.debug("Team_Battleground: assignStartingPlots shuffle array #2")
#		print shuffle_Array

#		print shuffle_Array[1][0]

		# organize the array into team order (if required)
		if userInputProximity == 0: # teams members start together
			for playerLoop in range(player_num):
				player = shuffle_Array[playerLoop][1]
				team = CyGlobalContext().getPlayer(player).getTeam()
				shuffle_Array[playerLoop][0] = team

#			BugUtil.debug("Team_Battleground: assignStartingPlots shuffle array #3")
#			print shuffle_Array
			shuffle_Array.sort()
#			BugUtil.debug("Team_Battleground: assignStartingPlots shuffle array #4")
#			print shuffle_Array

		shuffledPlayers = []
		for playerLoop in range(player_num):
#			print shuffle_Array[playerLoop][1]
			shuffledPlayers.append(shuffle_Array[playerLoop][1])

#		BugUtil.debug("Team_Battleground: assignStartingPlots shuffled player list - final")
#		print shuffledPlayers

# allocate starting plot by player
		iNumPlotsX = map.getGridWidth()
		iNumPlotsY = map.getGridHeight()

		centery = (iNumPlotsY - 1)//2
		centerx = (iNumPlotsX - 1)//2
		radii = centery - 2

		base_theta = 360 / player_num * dice.get(1000, "Starting Plot - base theta") / 1000

		for playerLoop in range(player_num):
			pPlayer = shuffledPlayers[playerLoop]
			theta = base_theta + playerLoop * 360 / player_num
			x = int(centerx + round(radii * cos(radians(theta)),0))
			y = int(centery + round(radii * sin(radians(theta)),0))
			pPlot = map.plot(x, y)
			CyGlobalContext().getPlayer(pPlayer).setStartingPlot(pPlot,True)

	else:
#		BugUtil.debug("Team_Battleground: assignStartingPlots else %i", gc.getGame().countCivTeamsAlive())
		if gc.getGame().countCivTeamsAlive() < 5:
		#if gc.getGame().countCivTeamsEverAlive() < 5:#2.22 -- Proved counterproductive (Test 1-2-2-3-3-4-4)
#			BugUtil.debug("Team_Battleground: assignStartingPlots inside if")
			team_list = [0, 1, 2, 3]
			shuffledTeams = []
			for teamLoop in range(gc.getGame().countCivTeamsAlive()):
			#for teamLoop in range(gc.getGame().countCivTeamsEverAlive()):#2.22 -- Proved counterproductive (Test 1-2-2-3-3-4-4)
				iChooseTeam = dice.get(len(team_list), "Shuffling Regions - TBG PYTHON")
				shuffledTeams.append(team_list[iChooseTeam])
				del team_list[iChooseTeam]

	CyPythonMgr().allowDefaultImpl()
	
def findStartingPlot(argsList):
#	BugUtil.debug("Team_Battleground: findStartingPlot1")
	[playerID] = argsList
	global assignedPlayers
	global team_num

#	BugUtil.debug("Team_Battleground: findStartingPlot2")
	map = CyMap()
	userInputPlots = map.getCustomMapOption(0)
	if (userInputPlots == 4   # round
	or  userInputPlots == 5): # donut ... starting position already set - return plotnum
		pPlot = CyGlobalContext().getPlayer(playerID).getStartingPlot()
		return map.plotNum(pPlot.getX(), pPlot.getY())

#	BugUtil.debug("Team_Battleground: findStartingPlot3")

	thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
	if iNumSpectators > 0 and CyGlobalContext().getGame().countCivTeamsEverAlive() == 2 :
		teamID = thisTeamID #a Hack, but I have no choice, not finding solutions
	else:
		teamID = team_num[thisTeamID]
	
	assignedPlayers[teamID] += 1

#	BugUtil.debug("Team_Battleground: findStartingPlot4")

	#2.22
	if iNumSpectators > 0:
		if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
		#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
			return -1	

	def isValid(playerID, x, y):

#		BugUtil.debug("Team_Battleground: isValid")
		map = CyMap()
		#numTeams = CyGlobalContext().getGame().countCivTeamsAlive()
		numTeams = CyGlobalContext().getGame().countCivTeamsEverAlive()#2.22 - I don't want to count spectator
		if numTeams > 4 or numTeams < 2: # Put em anywhere, and let the normalizer sort em out.
			return true
		userInputProximity = iOptionValue_TeamPlacement
		if userInputProximity == 2: # Start anywhere!
			return true

		global shuffle
		global shuffledTeams
		global team_num
		global shuffledPlayers
		global player_num

		thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
		if iNumSpectators > 0 and numTeams == 2 :
			teamID = thisTeamID #a Hack, but I have no choice, not finding solutions
		else:		
			teamID = team_num[thisTeamID]
		userInputPlots = map.getCustomMapOption(0)
		iW = map.getGridWidth()
		iH = map.getGridHeight()

#		BugUtil.debug("Team_Battleground: isValid teams %i, prox %i", numTeams, userInputProximity)
			
		# Two Teams, Start Together
		if numTeams == 2 and userInputProximity == 0: # Two teams, Start Together
			if userInputPlots == 1: # TvB
				if iNumSpectators == 0:#2.22 - This is BTS normal
					if teamID == 0 and shuffle and y >= iH * 0.6:
						return true
					if teamID == 1 and not shuffle and y >= iH * 0.6:
						return true
					if teamID == 0 and not shuffle and y <= iH * 0.4:
						return true
					if teamID == 1 and shuffle and y <= iH * 0.4:
						return true
				else:#2.22 - This is hack-ish, am basically saying don't shuffle, put team 2 on top. And also, spectator on top
					 #Since I know LAST player will flip with spectator (in C++), am good !
					if teamID == 2 and y >= iH * 0.6:
						return true
					if teamID == 1 and y <= iH * 0.4:
						return true					
					if teamID == 0 and y >= iH * 0.6:
						return true#has to be done - spectator gets this if there is any
				#return true
				return false

			elif (userInputPlots == 0   # LvR
			or    userInputPlots == 3): # LvR with land bridge
				if teamID == 0 and shuffle and x >= iW * 0.6:
					return true
				if teamID == 1 and not shuffle and x >= iW * 0.6:
					return true
				if teamID == 0 and not shuffle and x <= iW * 0.4:
					return true
				if teamID == 1 and shuffle and x <= iW * 0.4:
					return true
				return false

			else: # 4C
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
			
			#2.22 - Common block
			if iNumSpectators == 0:#2.22 - This is BTS normal
				if (shuffle and teamID == 0) or (not shuffle and teamID == 1):
					side = assignedPlayers[teamID]
				else:
					side = 1 + assignedPlayers[teamID]
				while side >= 2:
					side -= 2
			else:#Spectator
				side = assignedPlayers[teamID]#remove the randomness
				while side >= 2:
					side -= 2				
				
			if userInputPlots == 1: # TvB
				if iNumSpectators == 0:#2.22 - This is BTS normal
					if teamID == 0 and side and y >= iH * 0.6:
						return true
					if teamID == 1 and not side and y >= iH * 0.6:
						return true
					if teamID == 0 and not side and y <= iH * 0.4:
						return true
					if teamID == 1 and side and y <= iH * 0.4:
						return true
				else:#2.22 - This is hack-ish, am basically saying don't shuffle, put team 2 on top. And also, spectator on top
					 #Since I know LAST player will flip with spectator (in C++), am good !				
					if teamID == 1 and side and y >= iH * 0.6:
						return true
					if teamID == 2 and not side and y >= iH * 0.6:
						return true
					if teamID == 1 and not side and y <= iH * 0.4:
						return true
					if teamID == 2 and side and y <= iH * 0.4:
						return true				
					if teamID == 0 and y >= iH * 0.6 and (((CyGlobalContext().getGame().countCivPlayersAlive() /2) % 2) == 0):#even Number of players by team - 4v4
						return true
					if teamID == 0 and y <= iH * 0.4 and (((CyGlobalContext().getGame().countCivPlayersAlive() /2) % 2) != 0):#odd Number of players by team - 5v5
						return true								
				return false

			elif (userInputPlots == 0   # LvR
			or    userInputPlots == 3): # LvR with land bridge
				if teamID == 0 and side and x >= iW * 0.6:
					return true
				if teamID == 1 and not side and x >= iW * 0.6:
					return true
				if teamID == 0 and not side and x <= iW * 0.4:
					return true
				if teamID == 1 and side and x <= iW * 0.4:
					return true
				return false

			else: # 4C
				corner = shuffledTeams[side]
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
	userInputProximity = iOptionValue_TeamPlacement
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
	userInputPlots = CyMap().getCustomMapOption(0)

	if (userInputPlots == 0 # LvR
	or  userInputPlots == 3): # LvR with land bridge
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
		
		
		
def addBonusType(argsList):#2.21z
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	#2.21z - #2.22
	if isBTPon :
		bOptionOn = CyGlobalContext().getGame().isOption(GameOptionTypes.GAMEOPTION_NEW_STRATEGIC_RESOURCE)
		if not bOptionOn:#all excluded
			if (type_string in balancer.newResourcesBTP or type_string in balancer.newBoostBTP):
				return None	

	if (iOptionValue_Elephant >= 1):#2.32 - Ivory Option
		if iBonusType == CyGlobalContext().getInfoTypeForString("BONUS_IVORY"):
			return None
			
	if (iOptionValue_WonderResources == 1):#2.41
		if (type_string in ('BONUS_MARBLE','BONUS_STONE')):
			return None # don't place any of this bonus at ALL			
				
	CyPythonMgr().allowDefaultImpl()
	
	
	
def normalizeAddExtras():#2.32 - Am adding this to handle the Ivory option
	
	AncientStartLogic()#2.42 - I need to do this in a call that is done once at game level (not in startHumansOnSameTile done at player level)
	
	if (iOptionValue_Elephant == 2):#2.32 - Ivory Option		
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),4,3,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))	
	if (iOptionValue_Elephant == 3):#2.32 - Ivory Option	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_IVORY"),6,4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS"))
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride


def AncientStartLogic():#2.42	

	if iOptionValue_AncientStart > 0 and CyGlobalContext().getGame().getStartEra() == 0 and iOptionValue_AncientStart != 4 :
	
		iHunting = CyGlobalContext().getInfoTypeForString("TECH_HUNTING")
		for iI in range(CyGlobalContext().getMAX_TEAMS()):
			for iJ in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
				if CyGlobalContext().getPlayer(iJ).getTeam() == iI :			
					if CyGlobalContext().getPlayer(iJ).isEverAlive() and CyGlobalContext().getTeam(iI).isEverAlive():
						if iOptionValue_AncientStart == 3:
							if CyGlobalContext().getTeam(iI).isHasTech(iHunting):
								CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_FISHING"),True,iJ,1,1)		

						if iOptionValue_AncientStart == 2 :
							CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_FISHING"),True,iJ,False,False)
							CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_AGRICULTURE"),True,iJ,False,False)
							CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_MYSTICISM"),True,iJ,False,False)
							CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_MINING"),True,iJ,False,False)
							CyGlobalContext().getTeam(iI).setHasTech(CyGlobalContext().getInfoTypeForString("TECH_THE_WHEEL"),True,iJ,False,False)

		for iI in range(CyGlobalContext().getMAX_TEAMS()):#Another loop otherwise you can give both Hunting and Fishing
			for iJ in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
				if CyGlobalContext().getPlayer(iJ).getTeam() == iI :			
					if CyGlobalContext().getPlayer(iJ).isEverAlive() and CyGlobalContext().getTeam(iI).isEverAlive():
						CyGlobalContext().getTeam(iI).setHasTech(iHunting,True,iJ,1,1)#in all 3 cases

	if iOptionValue_AncientStart == 4 and isBTPon :
		iOptionScope = CyGlobalContext().getInfoTypeForString("GAMEOPTION_FREE_SCOUT")
		CyGlobalContext().getGame().setOption(iOptionScope, True)
		

def startHumansOnSameTile():#2.22


	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon :
		if (iOptionValue_ForestType > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)
				
	if iOptionValue_WonderResources == 2:#2.39
		gc = CyGlobalContext()
		map = CyMap()
		iW = map.getGridWidth()
		iH = map.getGridHeight()
	
		for iX in range(iW):
			for iY in range(iH):
				pPlot = CyMap().plot(iX,iY)
				##if iX < iW / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"):
				if iY < iH / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"):
					pPlot.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_STONE"))
				##if iX >= iW / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_STONE"):
				if iY >= iH / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_STONE"):
					pPlot.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"))			
		
	CyPythonMgr().allowDefaultImpl()
	
	#AncientStartLogicErase()#Need to be after the implementation of the units, it doesn't work it's early

def BTGFreeUnit():

	if (iOptionValue_StartingUnit == 0):
		return -1
	elif (iOptionValue_StartingUnit == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (iOptionValue_StartingUnit == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (iOptionValue_StartingUnit == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")	
	elif (iOptionValue_StartingUnit == 4):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_GREAT_LEGEND")			
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount(): return iOptionValue_StartingUnitCount	


def BTPForceEnrichFood(iProbaTreshold,bMainLandOnly,iResourceType,iMaxDistance,iMinDistance,bMakeHill,iForceTerrain):		

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
				for dx in range(-iMaxDistance,iMaxDistance):
					for dy in range(-iMaxDistance,iMaxDistance):
						p = map.plot(startx+dx,starty+dy)
						if (bMainLandOnly == True) :
							if ((dx != 0) or (dy != 0)) and (not p.isImpassable()) and (not p.isWater()) and p.getArea() == CyMap().findBiggestArea(False).getID():				
								if ((abs(dx) >= iMinDistance) and (abs(dy) >= iMinDistance)):
									iBonusCount = 0
									for tx in range(3):
										for ty in range(3):
											testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
											if (testP.getBonusType(-1) != -1):
												iBonusCount += 1		
									if iBonusCount >= 1:
										plotsboundaries.append(p)
									else :
										plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority

						if (bMainLandOnly == False) :
							if ((dx != 0) or (dy != 0)) and (not p.isImpassable()) and (not p.isWater()):				
								if ((abs(dx) >= iMinDistance) and (abs(dy) >= iMinDistance)):
									iBonusCount = 0
									for tx in range(3):
										for ty in range(3):
											testP = CyMap().plot(startx+dx+tx-1,starty+dy+ty-1)
											if (testP.getBonusType(-1) != -1):
												iBonusCount += 1		
									if iBonusCount >= 1:
										plotsboundaries.append(p)
									else :
										plotsboundariesSafe.append(p)#all the tiles are no bonus, this has priority								
									

				if len(plotsboundariesSafe) > 0:
									
					random.shuffle(plotsboundariesSafe)	
					for p in plotsboundariesSafe:
						#if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(iResourceType, True):
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS):#I don't care, I make my own plot anyway
							if bMakeHill:
								p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
							else:
								p.setPlotType(PlotTypes.PLOT_LAND, True, True)
							p.setTerrainType(iForceTerrain, True, True)#I Like to see it in this case too					
							p.setBonusType(iResourceType)
							p.setFeatureType(-1, -1)#2.25 -- Need remove floodplains, and forest then	
							break
							
				else:	
					random.shuffle(plotsboundaries)
					for p in plotsboundaries:
						#if (p.getBonusType(-1) == BonusTypes.NO_BONUS) and p.canHaveBonus(iResourceType, True):
						if (p.getBonusType(-1) == BonusTypes.NO_BONUS):#I don't care, I make my own plot anyway
							if bMakeHill:
								p.setPlotType(PlotTypes.PLOT_HILLS, True, True)						
							else:
								p.setPlotType(PlotTypes.PLOT_LAND, True, True)
							p.setTerrainType(iForceTerrain, True, True)#I Like to see it in this case too					
							p.setBonusType(iResourceType)
							p.setFeatureType(-1, -1)#2.25 -- Need remove floodplains, and forest then	
							break		
