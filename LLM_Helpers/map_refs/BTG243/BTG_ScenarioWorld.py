#
#	FILE:	 ScenarioWorld.py
#	AUTHOR:  Vadus
#	PURPOSE: Map Script, which reads a MapFile and places features randomly
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
import ConfigParser
import re
import os

class PropertiesFiles:
	def __init__(self):
		self.filenames = []
		self.mapnames = []
		self.filename = "SCNWRLD_VadusWorld.properties"
		#self.mapsize
		#self.data
		#self.civs
		#read all configured map scripts
		#print "Searching for Mapfiles in ", os.listdir('.\\PublicMaps\\')
		dirList = os.listdir("PublicMaps\WB_Maps\\")
		for fname in dirList:
			if(fname.startswith("SCNWRLD_") and fname.endswith(".properties")):
				self.filenames.append(fname)
				self.mapnames.append(fname[fname.find('_')+1:fname.rfind('.')])

	
	def loadMapFile(self):
		gc = CyGlobalContext()
		mmap = gc.getMap()
		selectionID = mmap.getCustomMapOption(0)
		self.filename = self.filenames[selectionID]
		
		print "Loading ", self.filename
		props = ConfigParser.ConfigParser()
		props.read("PublicMaps\WB_Maps\\%s"%self.filename)
		print props.get("file", "savefile")
		
		file = open(props.get("file", "savefile"), 'r')
		self.data = file.readlines()
		file.close()
		
		sizeX = int(props.get("map", "sizeX"))
		sizeY = int(props.get("map", "sizeY"))
		
		self.mapsize = (sizeX,sizeY)
		
		self.civs = {}
	
		for civ in props.options("civs"):
		    startLoc = props.get("civs", civ)
		    xy = startLoc.split(',')
		    self.civs[civ] = (int(xy[0]), int(xy[1]))
		
	
props = PropertiesFiles()	


def getDescription():
	return "Beyond the Game map by Penny, inspired by the Scandinavian forest and the island of Gotland"	
def getDescriptionTitle():
	return ""	
def getDescriptionTitleTwo():
	return ""	
def getDescriptionMain():
	return ""	
def getDescriptionSecond():#Script tip : (on TOP)
	return ""		
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return ""		
def getDescriptionBalance():#Balance : (at the bottom)"
	return ""	

def getDescription():
	return "Select one of your Mapfiles and play them with correct start locations!"

def getNumCustomMapOptions():
	return 1
	
def getCustomMapOptionName(argsList):
	return "Mapfile"
	
def getNumCustomMapOptionValues(argsList):
	return len(props.filenames)
	
def getCustomMapOptionDescAt(argsList):
	iSelection = argsList[1]
	return props.mapnames[iSelection]
	
def getCustomMapOptionDefault(argsList):
	return 0

def isRandomCustomMapOption(argsList):
	# Disable default Random and implement custom "weighted" Random.
	return false

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

"""
def prepareMap():
	global mapsize
	global data
	global civs
	
	#read the configured map script
	#print "Searchin for Mapfiles in ", os.listdir('.')
	props = ConfigParser.ConfigParser()
	props.read("PublicMaps\\ScenarioWorld.properties")
	print "Loading MapFile ", props.get("file", "savefile")
	
	
	file = open(props.get("file", "savefile"), 'r')
	data = file.readlines()
	file.close()
	
	sizeX = int(props.get("map", "sizeX"))
	sizeY = int(props.get("map", "sizeY"))
	
	mapsize = (sizeX,sizeY)
	
	civs = {}

	for civ in props.options("civs"):
	    startLoc = props.get("civs", civ)
	    xy = startLoc.split(',')
	    civs[civ] = (int(xy[0]), int(xy[1]))
"""

def getGridSize(argsList):
    if (argsList[0] == -1): # (-1,) is passed to function on loads
    	return []
    
    print "ScenarioWorld.getGridSize: ", props.mapsize
    gridsize = (props.mapsize[0]/4, props.mapsize[1]/4)
    print "ScenarioWorld.getGridSize: gridsize = ", gridsize
    return gridsize
    """
    prepareMap()
    print "ScenarioWorld.getGridSize: mapzize = ", mapsize
    gridsize = (mapsize[0]/4, mapsize[1]/4)
    print "ScenarioWorld.getGridSize: gridsize = ", gridsize
    return gridsize
    """

def beforeGeneration():
	# Detect whether this game is primarily a team game or not. (1v1 treated as a team game!)
	# Team games, everybody starts on the coast. Otherwise, start anywhere on the pangaea.
	global isTeamGame
	global plots
	
	plots = {} #global variable. is needed everywhere!
	
	gc = CyGlobalContext()
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTeams = gc.getGame().countCivTeamsEverAlive()
	if iPlayers >= iTeams * 2 or iPlayers == 2:
		isTeamGame = True
	else:
		isTeamGame = False
	
	#parse the mapfile data
	
	plot = {}
	riverDirections = {}
	riverPlacements = {}
	width = 0
	height = 0
	inPlot = True
	for line in props.data:
	    if line.startswith("BeginPlot"):
	        plot = {}
	        inPlot = True
	    elif inPlot and line.find("x=") != -1:
	        filter = re.findall("([0-9]+)*", line)
	        w = int(filter[3])
	        h = int(filter[7])
	        plot['x'] = w
	        plot['y'] = h
	        if(w > width):
	            width = w
	        if(h > height):
	            height = h
	    elif inPlot and line.find("TerrainType=") != -1:
	        filter = line.split("=")
	        plot['TerrainType'] = filter[1][0:len(filter[1])-1]
	    elif inPlot and line.find("PlotType=") != -1:
	        filter = line.split("=")
	        plot['PlotType'] = filter[1][0:len(filter[1])-1]
	    elif inPlot and line.find("FeatureType=") != -1:
	        filter = line.split("=")
	        plot['FeatureType'] = filter[1].split(",")[0]
	    elif inPlot and line.find("River") != -1:
	        #river plot has two attributes for each river on it
	        if line.find("RiverNSDirection") != -1:
	            filter = line.split("=")
	            riverDirections['NS'] = filter[1][0:len(filter[1])-1]
	        elif line.find("RiverWEDirection") != -1:
	            filter = line.split("=")
	            riverDirections['WE'] = filter[1][0:len(filter[1])-1]
	        elif line.find("isNOfRiver") != -1:
	            riverPlacements['isNOfRiver'] = line[line.find("is"):len(line)-1]
	        elif line.find("isWOfRiver") != -1:
	            riverPlacements['isWOfRiver'] = line[line.find("is"):len(line)-1]
	    elif inPlot and line.startswith("EndPlot"):
	        inPlot = False
	        plotRivers = []
	        for key in riverPlacements.keys():
	            if key == "isNOfRiver": #to NOfRiver belongs always a WE direction
	                plotRivers.append((key, int(riverDirections['WE'])))
	            elif key == "isWOfRiver": #to WOfRiver belongs always a NS direction
	                plotRivers.append((key, int(riverDirections['NS'])))
	        if len(plotRivers) > 0:
	        	plot['Rivers'] = plotRivers
	        riverPlacements = {}
	        riverDirections = {}
	        plots[(plot['x'], plot['y'])] = plot
	        #print "Added plot from wbs-file: PlotType=", plot['PlotType'], ", TerrainType=", plot['TerrainType'], ", FeatureType"


class FixTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def generateTerrainAtPlot(self,iX,iY):
		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()
		
		plot = plots[(iX, iY)]
		#for plot in plots:
		#if int(plot['x']) == iX and int(plot['y']) == iY:
		#print "generateTerrainPlot at ", iX, ",", iY, ": ", plot['TerrainType']
		if plot['TerrainType'] == "TERRAIN_PLAINS":
			terrainVal = self.terrainPlains
		elif plot['TerrainType'] == "TERRAIN_DESERT":
			terrainVal = self.terrainDesert
		elif plot['TerrainType'] == "TERRAIN_TUNDRA":
			terrainVal = self.terrainTundra
		elif plot['TerrainType'] == "TERRAIN_SNOW":
			terrainVal = self.terrainIce
		else:
			terrainVal = self.terrainGrass
	
		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal
	
class FixFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addFeaturesAtPlot(self, iX, iY):
		"adds any appropriate features at the plot (iX, iY) where (0,0) is in the SW"
		lat = self.getLatitudeAtPlot(iX, iY)
		pPlot = self.map.sPlot(iX, iY)
		
		for iI in range(self.gc.getNumFeatureInfos()):
			if pPlot.canHaveFeature(iI):
				if self.mapRand.get(10000, "Add Feature PYTHON") < self.gc.getFeatureInfo(iI).getAppearanceProbability():
					pPlot.setFeatureType(iI, -1)
		
		plot = plots[(iX, iY)]
		#for plot in plots:
		if plot.has_key('FeatureType'):# and int(plot['x']) == iX and int(plot['y']) == iY:
			if plot['FeatureType'] == "FEATURE_ICE":
				pPlot.setFeatureType(self.featureIce, -1)
			elif plot['FeatureType'] == "FEATURE_JUNGLE":
				pPlot.setFeatureType(self.featureJungle, -1)
			elif plot['FeatureType'] == "FEATURE_FOREST":
				pPlot.setFeatureType(self.featureForest, -1)
				
class FixRiverGenerator:
	def __init__(self):
		self.gc = CyGlobalContext()
		self.map = CyMap()
		self.rivers = {}
	
	def getRiverIdOfPlot(self, tuple):
	    for id in self.rivers.keys():
	        if tuple in self.rivers[id]:
	            return id
	    return -1

	def followUpRiver(self, coords, riverFragment):
	    if coords not in riverFragment:
	        riverFragment.append(coords)
	        plot = plots[coords]
	        for river in plot['Rivers']:
	            if river[0] == 'isNOfRiver':
	                if river[1] == 1: #river flows east
	                    plotEast = (coords[0]+1, coords[1])
	                    if plots.has_key(plotEast):
	                        if plots[plotEast].has_key('Rivers'):
	                            pE = plots[plotEast]
	                            for riv in pE['Rivers']:
	                                if riv[0] == 'isNOfRiver':
	                                    self.followUpRiver(plotEast, riverFragment)
	                    plotSouthEast = (coords[0]+1, coords[1]-1)
	                    if plots.has_key(plotSouthEast):
	                        if plots[plotSouthEast].has_key('Rivers'):
	                            pSW = plots[plotSouthEast]
	                            for riv in pSW['Rivers']:
	                                if riv[0] == 'isWOfRiver':
	                                    self.followUpRiver(plotSouthEast, riverFragment)
	                elif river[1] == 3: #river flows west
	                    plotWest = (coords[0]-1, coords[1])
	                    if plots.has_key(plotWest):
	                        if plots[plotWest].has_key('Rivers'):
	                            pW = plots[plotWest]
	                            for riv in pW['Rivers']:
	                                if riv[0] == 'isNOfRiver':
	                                    self.followUpRiver(plotWest, riverFragment)
	                    plotSouthWest = (coords[0]-1, coords[1]-1)
	                    if plots.has_key(plotSouthWest):
	                        if plots[plotSouthWest].has_key('Rivers'):
	                            pSW = plots[plotSouthWest]
	                            for riv in pSW['Rivers']:
	                                if riv[0] == 'isWOfRiver':
	                                    self.followUpRiver(plotSouthWest, riverFragment)
	            elif river[0] == 'isWOfRiver':
	                if river[1] == 0: #river flows north
	                    plotNorth = (coords[0], coords[1]+1)
	                    if plots.has_key(plotNorth):
	                        if plots[plotNorth].has_key('Rivers'):
	                            pN = plots[plotNorth]
	                            for riv in pN['Rivers']:
	                                if riv[0] == 'isWOfRiver':
	                                    self.followUpRiver(plotNorth, riverFragment)
	                    plotNorthEast = (coords[0]+1, coords[1]+1)
	                    if plots.has_key(plotNorthEast):
	                        if plots[plotNorthEast].has_key('Rivers'):
	                            pNW = plots[plotNorthEast]
	                            for riv in pNW['Rivers']:
	                                if riv[0] == 'isNOfRiver':
	                                    self.followUpRiver(plotNorthEast, riverFragment)
	                elif river[1] == 2: #river flows south
	                    plotSouth = (coords[0], coords[1]-1)
	                    if plots.has_key(plotSouth):
	                        if plots[plotSouth].has_key('Rivers'):
	                            pS = plots[plotSouth]
	                            for riv in pS['Rivers']:
	                                if riv[0] == 'isWOfRiver':
	                                    self.followUpRiver(plotSouth, riverFragment)
	                    plotEast = (coords[0]+1, coords[1])
	                    if plots.has_key(plotEast):
	                        if plots[plotEast].has_key('Rivers'):
	                            pE = plots[plotEast]
	                            for riv in pE['Rivers']:
	                                if riv[0] == 'isNOfRiver':
	                                    self.followUpRiver(plotEast, riverFragment)
	
	def parseRivers(self):
	    for plot in plots:
	        if plots[plot].has_key('Rivers'):
	            if self.getRiverIdOfPlot(plot) == -1:
	                #we have a new river here to seed and follow up
	                river = []
	                self.followUpRiver(plot, river)
	                newRiverID = -1
	                for riverPlot in river:
	                    if self.getRiverIdOfPlot(riverPlot) != -1:
	                        newRiverID = self.getRiverIdOfPlot(riverPlot)
	                if newRiverID == -1:
	                    newRiverID = len(self.rivers.keys())
	                self.rivers[newRiverID] = river
	  
	def setRivers(self):
		#fill rivers map
		self.parseRivers()
		for id in self.rivers:
			riverID = self.gc.getMap().getNextRiverID()
			for coords in self.rivers[id]:
				plot = plots[coords]
				pPlot = self.map.plot(coords[0],coords[1])
				pPlot.setRiverID(riverID)
				for riv in plot['Rivers']:
					if riv[0] == 'isNOfRiver':
						if riv[1] == 1:
							pPlot.setNOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_EAST)
						elif riv[1] == 3:
							pPlot.setNOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_WEST)
					elif riv[0] == 'isWOfRiver':
						if riv[1] == 0:
							pPlot.setWOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
						elif riv[1] == 2:
							pPlot.setWOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Pangaea) ...")
	gc = CyGlobalContext()
	map = gc.getMap()
	mapgen = CyMapGenerator()
	
	iNumPlotsX = props.mapsize[0]
	iNumPlotsY = props.mapsize[1]
	
	print "generating PlotTypes in map %d,%d"%(iNumPlotsX,iNumPlotsY)
	
	plotTypes = [PlotTypes.PLOT_OCEAN] * (map.getGridWidth()*map.getGridHeight())
	
	for x in range(iNumPlotsX):
		for y in range(iNumPlotsY):
			i = y*iNumPlotsX + x
			plot = plots[(x, y)]
			if int(plot["PlotType"]) == 0:
				plotTypes[i] = PlotTypes.PLOT_PEAK
			elif int(plot["PlotType"]) == 1:
				plotTypes[i] = PlotTypes.PLOT_HILLS
			elif int(plot["PlotType"]) == 2:
				plotTypes[i] = PlotTypes.PLOT_LAND
			elif int(plot["PlotType"]) == 3:
				plotTypes[i] = PlotTypes.PLOT_OCEAN
			#print "added PlotType at %d,%d: %s"%(x, y, plotTypes[i])

	print "plotgeneration done. Setting PlotTypes in MapGenerator"
	mapgen.setPlotTypes(plotTypes)
	return plotTypes
	

def generateTerrainTypes():
	# Now generate Terrain.
	NiTextOut("Generating Terrain (Python Pangaea) ...")
	terraingen = FixTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Pangaea) ...")
	featuregen = FixFeatureGenerator()
	featuregen.addFeatures()
	return 0

def addRivers():
	riverGen = FixRiverGenerator()
	riverGen.setRivers()
	
def findStartingPlot(argsList):
	[playerID] = argsList
	
	gc = CyGlobalContext()
	map = CyMap()
	player = gc.getPlayer(playerID)
	
	for civ in props.civs.keys():
		if (player.getCivilizationType() == gc.getInfoTypeForString(civ.upper())):
			startPlot = map.plot(props.civs[civ][0], props.civs[civ][1])
			print "set startLocation for %s : %d,%d"%(civ, startPlot.getX(), startPlot.getY())
			return map.plotNum(startPlot.getX(), startPlot.getY())

	def isValid(playerID, x, y):
		global isTeamGame
		map = CyMap()
		pPlot = map.plot(x, y)

		if (pPlot.getArea() != map.findBiggestArea(False).getID()):
			return false

		if isTeamGame:
			pWaterArea = pPlot.waterArea()
			if (pWaterArea.isNone()):
				return false
			return not pWaterArea.isLake()
		else:
			return true
	
	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)

def beforeInit():
    print "Initializing Custom Map Options"
    props.loadMapFile()
