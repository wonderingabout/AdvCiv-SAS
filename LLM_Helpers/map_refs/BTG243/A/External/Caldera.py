#
# FILE: Caldera.py
# AUTHOR: Zholef (username at forums.civfanatics.com)
# PURPOSE: Civ4 map script - Losely based on the Mediterranean Sea.
#
# VERSION 1.0 Initial release
# VERSION 1.1 Fixed resource balancing.
# VERSION 1.2 Made to reset river-related defines after use.
# VERSION 1.3 Improved starting plot assignment.
# VERSION 1.4 New option: Start on islands.
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import *
import Oasis
import Boreal
import Arboria
import Rainforest
import Great_Plains
import Inland_Sea

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_CALDERA_DESCR"
def isAdvancedMap():
	return 0
def isClimateMap():
	return 0
def getNumCustomMapOptions():
	n = 10
	if not hasattr(CvMapGeneratorUtil,'BonusBalancer'): n -= 1
	return n
def getNumHiddenCustomMapOptions():
	n = 9
	if not hasattr(CvMapGeneratorUtil,'BonusBalancer'): n -= 1
	return n
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MENU_CLIMATE",
		1:	"TXT_KEY_CONCEPT_STARTING_LOCATIONS",
		2:	"TXT_KEY_CONCEPT_NEW_WORD_CREATION",
		3:	"TXT_KEY_CONCEPT_MAP_SHAPE",
		4:	"TXT_KEY_CONCEPT_SIZE_FACTOR",
		5:	"TXT_KEY_CONCEPT_COASTS",
		6:	"TXT_KEY_CONCEPT_GROUND",
		7:	"TXT_KEY_CONCEPT_EXTRA_RIVERS",
		8:	"TXT_KEY_CONCEPT_SAME_TILE",
		9:	"TXT_KEY_CONCEPT_RESOURCES",
		}
	return unicode(CyTranslator().getText(option_names[iOption],()))
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	9,
		1:	3,
		2:	2,
		3:	3,
		4:	3,
		5:	4,
		6:	4,
		7:	2,
		8:	2,
		9:	2,
		}
	return option_values[iOption]
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0:	"TXT_KEY_CLIMATE_TEMPERATE",
			1:	"TXT_KEY_CLIMATE_TROPICAL",
			2:	"TXT_KEY_CLIMATE_ARID",
			3:	"TXT_KEY_CLIMATE_COLD",
			4:	"TXT_KEY_CLIMATE_BOREAL",
			5:	"TXT_KEY_CLIMATE_ARBORIA",
			6:	"TXT_KEY_CLIMATE_RAINFOREST",
			7:	"TXT_KEY_CLIMATE_GREAT_PLAINS",
			8:	"TXT_KEY_CLIMATE_OASIS",
			},
		1:	{
			0:	"TXT_KEY_MAP_SCRIPT_ON_LARGEST_LANDMASS",
			1:	"TXT_KEY_MAP_SCRIPT_START_ANYWHERE",
			2:	"TXT_KEY_MAP_SCRIPT_ISLANDS",
			},
		2:	{
			0:	"TXT_KEY_MAP_SCRIPT_ENCOURAGE_NEW_WORLD",
			1:	"TXT_KEY_MAP_SCRIPT_DISCOURAGE_NEW_WORLD",
			},
		3:	{
			0:	"TXT_KEY_MAP_SCRIPT_RECTANGLE",
			1:	"TXT_KEY_MAP_SCRIPT_SQUARE",
			2:	"TXT_KEY_MAP_SCRIPT_TILTED_RECTANGLE",
			},
		4:	{
			0:	"TXT_KEY_WORLD_STANDARD",
			1:	"TXT_KEY_WORLD_LARGE",
			2:	"TXT_KEY_WORLD_HUGE",
			},
		5:	{
			0:	"TXT_KEY_MAP_SCRIPT_STEEP",
			1:	"TXT_KEY_MAP_SCRIPT_NARROW",
			2:	"TXT_KEY_MAP_SCRIPT_WIDE",
			3:	"TXT_KEY_MAP_SCRIPT_VERY_WIDE",
			},
		6:	{
			0:	"TXT_KEY_MAP_SCRIPT_NORMAL",
			1:	"TXT_KEY_MAP_SCRIPT_ROCKY_ISLANDS",
			2:	"TXT_KEY_MAP_SCRIPT_ROCKY_CONTINENTS",
			3:	"TXT_KEY_MAP_SCRIPT_ALL_ROCKY",
			},
		7:	{
			0:	"TXT_KEY_MAP_SCRIPT_NO",
			1:	"TXT_KEY_MAP_SCRIPT_YES",
			},
		8:	{
			0:	"TXT_KEY_MAP_SCRIPT_SPEAD_OUT",
			1:	"TXT_KEY_MAP_SCRIPT_SAME_TILE",
			},
		9:	{
			0:	"TXT_KEY_WORLD_STANDARD",
			1:	"TXT_KEY_MAP_BALANCED",
			},
		}
	translated_text = unicode(CyTranslator().getText(
	                          selection_names[iOption][iSelection],()))
	return translated_text
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	-1,
		1:	0,
		2:	-1,
		3:	0,
		4:	0,
		5:	1,
		6:	1,
		7:	-1,
		8:	0,
		9:	0,
		}
	return option_defaults[iOption]
def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	true,
		2:	true,
		3:	true,
		4:	true,
		5:	true,
		6:	true,
		7:	true,
		8:	false,
		9:	false,
		}
	return option_random[iOption]

class MapVariables:
	def __init__(self):
		# Settings from the menu
		self.climate = "temperate"
		self.new_world_creation = "encouraged"
		self.sea_level_change = 0
		self.start = "old_world_mainland"
		self.shape = "rectangular"
		self.size_mod = "standard"
		self.connection_width = 1
		self.rocky = "islands"
		self.extra_rivers = False
		self.same_tile = False
		self.balancer = None
		self.balanced = False
		# Variables for starting plot assignment
		self.initial_angle = 0
		self.players = 0
		self.starting_order = []
		self.checked_plots = []
		self.completed_passes = 0
		self.too_close_to_peaks = False
		# Save original river define values
		gc = CyGlobalContext()
		self.orig_ppre = gc.getDefineINT("PLOTS_PER_RIVER_EDGE")
		self.orig_rsmrr = gc.getDefineINT("RIVER_SOURCE_MIN_RIVER_RANGE")
		self.orig_rsmsr = gc.getDefineINT("RIVER_SOURCE_MIN_SEAWATER_RANGE")
	def addBalancer(self):
		self.balancer = CvMapGeneratorUtil.BonusBalancer()
		self.balanced = True
mv = MapVariables()

def beforeInit():
	gc = CyGlobalContext()
	map = CyMap()
	print; print "Generating Caldera with the following settings."
	slc = gc.getSeaLevelInfo(map.getSeaLevel()).getSeaLevelChange()
	if   slc == 0: mv.sea_level_change =   0
	elif slc  > 0: mv.sea_level_change =  10
	elif slc  < 0: mv.sea_level_change = -10
	print "sea_level_change: " + str(mv.sea_level_change)
	if   map.getCustomMapOption(0) == 0: mv.climate = "temperate"
	elif map.getCustomMapOption(0) == 1: mv.climate = "tropical"
	elif map.getCustomMapOption(0) == 2: mv.climate = "arid"
	elif map.getCustomMapOption(0) == 3: mv.climate = "cold"
	elif map.getCustomMapOption(0) == 4: mv.climate = "boreal"
	elif map.getCustomMapOption(0) == 5: mv.climate = "arboria"
	elif map.getCustomMapOption(0) == 6: mv.climate = "rainforest"
	elif map.getCustomMapOption(0) == 7: mv.climate = "great_plains"
	elif map.getCustomMapOption(0) == 8: mv.climate = "oasis"
	print "climate: " + mv.climate
	if   map.getCustomMapOption(1) == 0: mv.start = "old_world_mainland"
	elif map.getCustomMapOption(1) == 1: mv.start = "anywhere"
	elif map.getCustomMapOption(1) == 2: mv.start = "on_islands"
	print "start: " + mv.start
	if   map.getCustomMapOption(2) == 0: mv.new_world_creation = "encouraged"
	elif map.getCustomMapOption(2) == 1: mv.new_world_creation = "discouraged"
	print "new_world_creation: " + mv.new_world_creation
	if   map.getCustomMapOption(3) == 0: mv.shape = "rectangular"
	elif map.getCustomMapOption(3) == 1: mv.shape = "squared"
	elif map.getCustomMapOption(3) == 2: mv.shape = "tilted"
	print "shape: " + mv.shape
	if   map.getCustomMapOption(4) == 0: mv.size_mod = "standard"
	elif map.getCustomMapOption(4) == 1: mv.size_mod = "large"
	elif map.getCustomMapOption(4) == 2: mv.size_mod = "huge"
	print "size_mod: " + mv.size_mod
	if   map.getCustomMapOption(5) == 0: mv.connection_width = 0.0
	elif map.getCustomMapOption(5) == 1: mv.connection_width = 0.5
	elif map.getCustomMapOption(5) == 2: mv.connection_width = 1.0
	elif map.getCustomMapOption(5) == 3: mv.connection_width = 1.5
	print "connection_width: " + str(mv.connection_width)
	if   map.getCustomMapOption(6) == 0: mv.rocky = "normal"
	elif map.getCustomMapOption(6) == 1: mv.rocky = "islands"
	elif map.getCustomMapOption(6) == 2: mv.rocky = "continents"
	elif map.getCustomMapOption(6) == 3: mv.rocky = "everything"
	print "rocky: " + mv.rocky
	if   map.getCustomMapOption(7) == 0: mv.extra_rivers = False
	elif map.getCustomMapOption(7) == 1: mv.extra_rivers = True
	print "extra_rivers: " + str(mv.extra_rivers)
	if   map.getCustomMapOption(8) == 0: mv.same_tile = False
	elif map.getCustomMapOption(8) == 1: mv.same_tile = True
	print "same_tile: " + str(mv.same_tile)
	if hasattr(CvMapGeneratorUtil,'BonusBalancer'):
		if   map.getCustomMapOption(9) == 0: mv.balanced = False
		elif map.getCustomMapOption(9) == 1: mv.addBalancer()
		print "balanced: " + str(mv.balanced)
def getGridSize(argsList):
	grid_sizes = {
		"standard": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(6,4),
				WorldSizeTypes.WORLDSIZE_TINY:		(8,5),
				WorldSizeTypes.WORLDSIZE_SMALL:		(13,8),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(16,10),
				WorldSizeTypes.WORLDSIZE_LARGE:		(21,13),
				WorldSizeTypes.WORLDSIZE_HUGE:		(26,16)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(5,5),
				WorldSizeTypes.WORLDSIZE_TINY:		(6,6),
				WorldSizeTypes.WORLDSIZE_SMALL:		(8,8),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,10),
				WorldSizeTypes.WORLDSIZE_LARGE:		(13,13),
				WorldSizeTypes.WORLDSIZE_HUGE:		(20,20)},
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(4,6),
				WorldSizeTypes.WORLDSIZE_TINY:		(5,8),
				WorldSizeTypes.WORLDSIZE_SMALL:		(8,13),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,16),
				WorldSizeTypes.WORLDSIZE_LARGE:		(13,21),
				WorldSizeTypes.WORLDSIZE_HUGE:		(16,26)},
			},
		"large": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(8,5),
				WorldSizeTypes.WORLDSIZE_TINY:		(13,8),
				WorldSizeTypes.WORLDSIZE_SMALL:		(16,10),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(21,13),
				WorldSizeTypes.WORLDSIZE_LARGE:		(26,16),
				WorldSizeTypes.WORLDSIZE_HUGE:		(32,20)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
				WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
				WorldSizeTypes.WORLDSIZE_SMALL:		(10,10),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(13,13),
				WorldSizeTypes.WORLDSIZE_LARGE:		(17,17),
				WorldSizeTypes.WORLDSIZE_HUGE:		(25,25)},
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(5,8),
				WorldSizeTypes.WORLDSIZE_TINY:		(8,13),
				WorldSizeTypes.WORLDSIZE_SMALL:		(10,16),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(13,21),
				WorldSizeTypes.WORLDSIZE_LARGE:		(16,26),
				WorldSizeTypes.WORLDSIZE_HUGE:		(20,32)},
			},
		"huge": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(13,8),
				WorldSizeTypes.WORLDSIZE_TINY:		(16,10),
				WorldSizeTypes.WORLDSIZE_SMALL:		(21,13),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(26,16),
				WorldSizeTypes.WORLDSIZE_LARGE:		(32,20),
				WorldSizeTypes.WORLDSIZE_HUGE:		(38,24)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(10,10),
				WorldSizeTypes.WORLDSIZE_TINY:		(13,13),
				WorldSizeTypes.WORLDSIZE_SMALL:		(17,17),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(20,20),
				WorldSizeTypes.WORLDSIZE_LARGE:		(25,25),
				WorldSizeTypes.WORLDSIZE_HUGE:		(30,30)},
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(8,13),
				WorldSizeTypes.WORLDSIZE_TINY:		(10,16),
				WorldSizeTypes.WORLDSIZE_SMALL:		(13,21),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(16,26),
				WorldSizeTypes.WORLDSIZE_LARGE:		(20,32),
				WorldSizeTypes.WORLDSIZE_HUGE:		(24,38)},
			},}
	[eWorldSize] = argsList
	if eWorldSize == -1: return []
	return grid_sizes[mv.size_mod][mv.shape][eWorldSize]
def getTopLatitude():
	if mv.climate in ("boreal"):       return Boreal.getTopLatitude()
	if mv.climate in ("arboria"):      return Arboria.getTopLatitude()
	if mv.climate in ("rainforest"):   return Rainforest.getTopLatitude()
	if mv.climate in ("great_plains"): return Great_Plains.getTopLatitude()
	if mv.climate in ("oasis"):        return Oasis.getTopLatitude()
	if mv.climate in ("cold"):            return  80
	if mv.climate in ("temperate"):       return  50
	if mv.climate in ("tropical","arid"): return  15
	CyPythonMgr().allowDefaultImpl()
def getBottomLatitude():
	if mv.climate in ("boreal"):       return Boreal.getBottomLatitude()
	if mv.climate in ("arboria"):      return Arboria.getBottomLatitude()
	if mv.climate in ("rainforest"):   return Rainforest.getBottomLatitude()
	if mv.climate in ("great_plains"): return Great_Plains.getBottomLatitude()
	if mv.climate in ("oasis"):        return Oasis.getBottomLatitude()
	if mv.climate in ("cold"):            return  80
	if mv.climate in ("temperate"):       return  50
	if mv.climate in ("tropical","arid"): return -15
	CyPythonMgr().allowDefaultImpl()
def isBonusIgnoreLatitude(): return True
def getWrapX(): return False
def getWrapY(): return False
def beforeGeneration():
	mv.players = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if mv.climate == "boreal":
		Boreal.beforeGeneration()
	if mv.climate == "arboria":
		Arboria.beforeGeneration()
	if mv.climate == "rainforest":
		Rainforest.beforeGeneration()
def generatePlotTypes():
	if mv.climate == "temperate":
		return CalderaFractalWorld(0).generateCalderaPlots()
	if mv.climate == "tropical":
		return CalderaFractalWorld(1).generateCalderaPlots()
	if mv.climate == "arid":
		return CalderaFractalWorld(2).generateCalderaPlots()
	if mv.climate == "cold":
		return CalderaFractalWorld(4).generateCalderaPlots()
	return CalderaFractalWorld().generateCalderaPlots()
def generateTerrainTypes():
	if mv.climate == "temperate":
		return CalderaTerrainGenerator(0).generateTerrain()
	if mv.climate == "tropical":
		return CalderaTerrainGenerator(1).generateTerrain()
	if mv.climate == "arid":
		return CalderaTerrainGenerator(2).generateTerrain()
	if mv.climate == "cold":
		return CalderaTerrainGenerator(4).generateTerrain()
	if mv.climate == "rainforest":
		return Rainforest.RainforestTerrainGenerator().generateTerrain()
	if mv.climate == "arboria":
		return Arboria.ArboriaTerrainGenerator().generateTerrain()
	if mv.climate == "boreal":
		return Boreal.BorealTerrainGenerator().generateTerrain()
	if mv.climate == "great_plains":
		return Great_Plains.GreatPlainsTerrainGenerator().generateTerrain()
	if mv.climate == "oasis":
		return Oasis.OasisTerrainGenerator().generateTerrain()
	CyPythonMgr().allowDefaultImpl()
def addRivers():
	gc = CyGlobalContext()
	if mv.extra_rivers or mv.climate in ("boreal"):
		ppre = mv.orig_ppre * 2/3
		if mv.extra_rivers and mv.climate in ("boreal"): ppre *= 3/4
		gc.setDefineINT("PLOTS_PER_RIVER_EDGE",ppre)
		gc.setDefineINT("RIVER_SOURCE_MIN_RIVER_RANGE",mv.orig_rsmrr*3/4)
		gc.setDefineINT("RIVER_SOURCE_MIN_SEAWATER_RANGE",mv.orig_rsmsr/2)
	CyPythonMgr().allowDefaultImpl()
def getRiverStartCardinalDirection(argsList):
	if argsList[0].getArea() == CyMap().findBiggestArea(False).getID():
		return Inland_Sea.getRiverStartCardinalDirection(argsList)
	CyPythonMgr().allowDefaultImpl()
def getRiverAltitude(argsList):
	if argsList[0].getArea() == CyMap().findBiggestArea(False).getID():
		return Inland_Sea.getRiverAltitude(argsList)
	CyPythonMgr().allowDefaultImpl()
def addLakes(): return None # We'll add our own during plot generation.
def addFeatures():
	if   mv.climate == "temperate":
					CalderaFeatureGenerator(0).addFeatures()
	elif mv.climate == "tropical":
					CalderaFeatureGenerator(1).addFeatures()
	elif mv.climate == "arid":
					CalderaFeatureGenerator(2).addFeatures()
	elif mv.climate == "cold":
					CalderaFeatureGenerator(4).addFeatures()
	elif mv.climate == "boreal":
					Boreal.BorealFeatureGenerator().addFeatures()
	elif mv.climate == "arboria":
					Arboria.ArboriaFeatureGenerator().addFeatures()
	elif mv.climate == "rainforest":
					Rainforest.RainforestFeatureGenerator().addFeatures()
	elif mv.climate == "great_plains":
					Great_Plains.GreatPlainsFeatureGenerator().addFeatures()
	elif mv.climate == "oasis":
					Oasis.OasisFeatureGenerator().addFeatures()
	else:			CyPythonMgr().allowDefaultImpl()
def addBonusType(argsList):
	[iBonusType] = argsList
	type_string = CyGlobalContext().getBonusInfo(iBonusType).getType()
	if mv.balanced:
		if type_string in mv.balancer.resourcesToBalance: return None
	if mv.climate == "boreal" and type_string == "BONUS_CLAM":
		CyPythonMgr().allowDefaultImpl()
	if mv.climate == "boreal":  return Boreal.addBonusType(argsList)
	if mv.climate == "arboria": return Arboria.addBonusType(argsList)
	if mv.climate == "rainforest" and type_string not in \
	                ('BONUS_WHALE','BONUS_CLAM','BONUS_FISH','BONUS_CRAB'):
		return Rainforest.addBonusType(argsList)
	if mv.climate == "great_plains" and type_string not in \
	                ('BONUS_WHALE','BONUS_CLAM','BONUS_FISH','BONUS_CRAB'):
		return Great_Plains.addBonusType(argsList)
	if mv.climate == "oasis" and type_string not in \
	                ('BONUS_WHALE','BONUS_CLAM','BONUS_FISH','BONUS_CRAB'):
		return Oasis.addBonusType(argsList)
	CyPythonMgr().allowDefaultImpl()
def afterGeneration():
	gc = CyGlobalContext()
	# Reset river defines
	gc.setDefineINT("PLOTS_PER_RIVER_EDGE", mv.orig_ppre)
	gc.setDefineINT("RIVER_SOURCE_MIN_RIVER_RANGE", mv.orig_rsmrr)
	gc.setDefineINT("RIVER_SOURCE_MIN_SEAWATER_RANGE", mv.orig_rsmsr)
	# Randomize starting order
	mv.starting_order = []
	r = range(0,mv.players)
	for i in range(0,mv.players):
		iPick = r[gc.getGame().getMapRand().get(
		                                   len(r),"Determine starting order.")]
		mv.starting_order.append(iPick)
		r.remove(iPick)
	mv.too_close_to_peaks = False
def minStartingDistanceModifier():
	if mv.start == "old_world_mainland": return  0
	if mv.size_mod in ("standard"):      return 50
	if mv.size_mod in ("large"):         return 65
	if mv.size_mod in ("huge"):          return 80
def findStartingPlot(argsList):
	[playerID] = argsList
	def isValid(playerID,iX,iY):
		pPlot = CyMap().plot(iX,iY)
		vPlot = toPolar(fromAbsolutes(iX,iY))
		if vPlot in mv.checked_plots:
			mv.checked_plots = []
			mv.completed_passes += 1
		mv.checked_plots.append(vPlot)
		if mv.completed_passes < 1:
			if vPlot[1] >= 1-(5*getPlotThicknessAtAngle(vPlot[0])):
				return False
		else: mv.too_close_to_peaks = True
		if mv.completed_passes < 2:
			if pPlot.area().getNumTiles() < 11: return False
		if mv.completed_passes < 3:
			if mv.start == "on_islands":
				if pPlot.getArea() == CyMap().findBiggestArea(False).getID():
					return False
			if mv.start == "old_world_mainland":
				if pPlot.getArea() != CyMap().findBiggestArea(False).getID():
					return False
				pos = mv.starting_order[playerID]
				left_angle = mv.initial_angle-0.5*pi
				left_angle += pos*((2*pi)/mv.players)
				left_angle += (7*pi/8)/mv.players
				left_angle %= 2*pi
				right_angle = mv.initial_angle-0.5*pi
				right_angle += pos*((2*pi)/mv.players)
				right_angle += (9*pi/8)/mv.players
				right_angle %= 2*pi
				if vPlot[0] > right_angle > left_angle: return False
				if right_angle > left_angle > vPlot[0]: return False
				if left_angle > vPlot[0] > right_angle: return False
		return True
	mv.checked_plots = []
	mv.completed_passes = 0
	return CvMapGeneratorUtil.findStartingPlot(playerID,isValid)
def normalizeAddRiver():
	if mv.climate in ("boreal"): return None
	CyPythonMgr().allowDefaultImpl()
def normalizeRemovePeaks():
	if mv.too_close_to_peaks == True: return None
	CyPythonMgr().allowDefaultImpl()
def normalizeAddLakes():
	if mv.too_close_to_peaks == True: return None
	CyPythonMgr().allowDefaultImpl()
def normalizeRemoveBadFeatures():
	if mv.climate in ("arboria","great_plains"): return None
	CyPythonMgr().allowDefaultImpl()
def normalizeRemoveBadTerrain():
	if mv.climate in ("oasis","great_plains"): return None
	CyPythonMgr().allowDefaultImpl()
#def normalizeAddFoodBonuses(): return None
def normalizeAddGoodTerrain():
	if mv.climate in ("boreal","oasis"): return None
	if mv.too_close_to_peaks == True: return None
	CyPythonMgr().allowDefaultImpl()
def normalizeAddExtras():
	if mv.balanced:
		mv.balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()
def startHumansOnSameTile(): return mv.same_tile

#   Coordinates toolbox
# Civ4 primarily uses cartesian coordinates with an origin in the bottom left
# corner of the map (in the following referred to as "absolutes"). However, in
# this script we primarily use normalized cartesian coordinates with an origin
# in the center of the map (meaning the map center is described as (0,0) and
# map corners as (1,1), (1,-1), (-1,1) and (-1,-1)), and sometimes we use polar
# coordinates.
def fromAbsolutes(iX,iY):
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()
	x = (2*iX/float(iW-1))-1
	y = (2*iY/float(iH-1))-1
	return x,y
#def toAbsolutes(xy): # Haven't needed that yet.
def fromPolar(angle,length):
	x = sin(angle)*length
	y = cos(angle)*length
	return x,y
def toPolar(xy):
	length = getDistanceToCenter(xy)
	angle = asin(xy[0]/length)
	if xy[1] < 0: angle = pi-angle
	angle %= 2*pi
	return angle,length
def getAngle(xy):
	return toPolar(xy)[0]
def getDistanceToCenter(xy):
	return sqrt(xy[0]**2+xy[1]**2)
def getAbsoluteDistanceToCenter(xy):
	v = toPolar(xy)
	return v[1]*getMaxEllipseRadiusAtAngle(v[0])
def getPlotThicknessAtAngle(angle):
	t = getAbsolutePlotThicknessAtAngle(angle)
	r = getMaxEllipseRadiusAtAngle(angle)
	return t/r
def getAbsolutePlotThicknessAtAngle(angle): # Range: 1.0 to sqrt(2)
	return abs(sin(angle))+abs(cos(angle))
def getEllipseRadiusAtAngle(width,height,angle):
	return abs(sin(angle)*(width/2.))+abs(cos(angle)*(height/2.))
def getMaxEllipseRadiusAtAngle(angle):
	return getEllipseRadiusAtAngle(
		CyMap().getGridWidth(),CyMap().getGridHeight(),angle)
def add(xy,ab):
	return xy[0]+ab[0],xy[1]+ab[1]
def rotate(xy,angle):
	v = toPolar(xy)
	new_angle = v[0]+angle
	return fromPolar(new_angle,v[1])
def drawDisk(xy,radius,outside,inside):
	if getDistanceToCenter(xy) < radius:    return inside
	else:                                   return outside
def drawMantledDisk(xy,radius,mantle_plots,outside,inside):
	mantle = mantle_plots * getPlotThicknessAtAngle(getAngle(xy))
	return drawDisk(xy,radius+mantle,outside,inside)

class BasicFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def __init__(self,iClimate=-1,
				 fracXExp=CyFractal.FracVals.DEFAULT_FRAC_X_EXP,
				 fracYExp=CyFractal.FracVals.DEFAULT_FRAC_Y_EXP):
		CvMapGeneratorUtil.FractalWorld.__init__(self,fracXExp,fracYExp)
		if iClimate > -1:
			self.hillGroupOneRange = \
				self.gc.getClimateInfo(iClimate).getHillRange()
			self.hillGroupTwoRange = \
				self.gc.getClimateInfo(iClimate).getHillRange()
			self.peakPercent = \
				self.gc.getClimateInfo(iClimate).getPeakPercent()


class CalderaFractalWorld(BasicFractalWorld):

	def __init__(self,iClimate=-1,
				 fracXExp=CyFractal.FracVals.DEFAULT_FRAC_X_EXP,
				 fracYExp=CyFractal.FracVals.DEFAULT_FRAC_Y_EXP):
		BasicFractalWorld.__init__(self,iClimate,fracXExp,fracYExp)
		self.seaLevelChange = 0 # We'll handle that ourselves.
		if mv.rocky == "everything":
			self.hillGroupOneRange += 2
			self.hillGroupTwoRange += 2
			self.peakPercent += 10

	class PlotMap:
		def __init__(self,width,height):
			self.w = width
			self.h = height
			self.plots = []
			for i in range(height):
				self.plots.append([0]*width)
			return
		def getPlots(self):
			plots = []
			for row in self.plots:
				for p in row:
					plots.append([p])
			return plots
		def getRows(self):
			return self.plots
		def setPlot(self,width,height,value):
			self.plots[height][width] = value

	def generatePlotAtLocation(self,iX,iY,iPeninsulas,angle):
		xy = fromAbsolutes(iX,iY)
		pen = float(iPeninsulas)
		pt = getPlotThicknessAtAngle(getAngle(xy))
		pieceOfPie = (2*pi)/(2*pen)
		outerSlopeFactor = 4.0
		upperInnerSlopeFactor = mv.connection_width * 1.0
		lowerInnerSlopeFactor = mv.connection_width * 1.5
		innerSlopeFactor = upperInnerSlopeFactor + lowerInnerSlopeFactor
		slopeFactor = outerSlopeFactor + innerSlopeFactor
		upperInnerSlope = 0.99
		lowerInnerSlope = upperInnerSlope - pt * upperInnerSlopeFactor
		craterBottom = lowerInnerSlope - pt * lowerInnerSlopeFactor
		# Ever wondered how big a cake fits into a slice of a larger cake?
		gulfAndPeninsula = \
			craterBottom*tan(pi/(2*pen))*tan(((pi/2)-(pi/(2*pen)))/2)
		shallowLake = craterBottom - gulfAndPeninsula
		r = drawDisk(xy,shallowLake,'outer_ocean','shallow_lake')
		for iI in range(1,iPeninsulas+1):
			relativeToGulfCenter      = \
				add(xy,rotate((shallowLake,0),angle+(iI*((2*pi)/pen))))
			relativeToPeninsulaCenter = \
				add(xy,rotate((shallowLake,0),angle+(iI*((2*pi)/pen)+pi/pen)))
			if r in ('outer_ocean'):
				r = drawMantledDisk(relativeToGulfCenter,gulfAndPeninsula,
						slopeFactor,r,'gulf_peaks')
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,slopeFactor,r,'peninsula_peaks')
			if r in ('gulf_peaks','peninsula_peaks'):
				r = drawMantledDisk(relativeToGulfCenter,gulfAndPeninsula,
						innerSlopeFactor,r,'gulf_high_slope')
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,innerSlopeFactor,r,
						'peninsula_high_slope')
			if r in ('gulf_high_slope','peninsula_high_slope'):
				r = drawMantledDisk(relativeToGulfCenter,gulfAndPeninsula,
						lowerInnerSlopeFactor,r,'gulf_low_slope')
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,lowerInnerSlopeFactor,r,
						'peninsula_low_slope')
			if r not in ('shallow_lake'):
				r = drawMantledDisk(relativeToGulfCenter,gulfAndPeninsula,0,r,
						'gulf_green_water')
			if r in ('shallow_lake'):
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,2,r,'peninsula_green_water')
			if r in ('peninsula_green_water'):
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,0,r,'peninsula_coast')
			if True:
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,-1,r,'peninsula_core')
				r = drawMantledDisk(relativeToPeninsulaCenter,
						gulfAndPeninsula,-3.5,r,'peninsula_lake_zone')
				r = drawMantledDisk(relativeToGulfCenter,gulfAndPeninsula,-2,
						r,'gulf_core')
		maxNewWorldOcean = shallowLake-gulfAndPeninsula - pt*2
		minNewWorldOcean = pt*6
		if maxNewWorldOcean < minNewWorldOcean:
			mv.new_world_creation = "discouraged"
		if mv.new_world_creation != "discouraged":
			newWorldOcean = (maxNewWorldOcean+minNewWorldOcean)/2.
			newWorldIslandZone = newWorldOcean - pt*6
			newWorldCoastalZone = newWorldIslandZone * .66
			newWorldMainland = newWorldCoastalZone * .66
			newWorldLakeZone = newWorldMainland - pt*2
			r = drawDisk(xy,newWorldOcean,r,'new_world_ocean')
			r = drawDisk(xy,newWorldIslandZone,r,'new_world_islands')
			r = drawDisk(xy,newWorldCoastalZone,r,'new_world_mainland_coast')
			r = drawDisk(xy,newWorldMainland,r,'new_world_mainland_core')
			r = drawDisk(xy,newWorldLakeZone,r,'new_world_lake_zone')
		return r

	def generateCalderaPlots(self):
		map = CyMap()
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		mv.initial_angle = CyGlobalContext().getGame().getMapRand().get(
		                      65535,"How far should we turn the wheel?")/65535.
		mv.initial_angle *= 2*pi
		pm = self.PlotMap(iW,iH)
		for x in range(iW):
			for y in range(iH):
				pm.setPlot(x,y,self.generatePlotAtLocation(
				                              x,y,mv.players,mv.initial_angle))
		plots = [PlotTypes.PLOT_OCEAN] * len(pm.getPlots())
		counter = 0
		for row in pm.getRows():
			for i in row:
				if   i in (
						   'gulf_peaks',
						   'peninsula_peaks',
						   ):
					plots[counter] = PlotTypes.PLOT_PEAK
				elif i in (
						   'gulf_high_slope',
						   'peninsula_high_slope',
						   'gulf_low_slope',
						   'peninsula_low_slope',
						   'peninsula_core',
						   'peninsula_lake_zone',
						   'new_world_mainland_core',
						   'new_world_lake_zone',
						   ):
					plots[counter] = PlotTypes.PLOT_LAND
				elif i in (
						   'outer_ocean',
						   'shallow_lake',
						   'gulf_core',
						   'peninsula_green_water',
						   'gulf_green_water',
						   'peninsula_coast',
						   'new_world_ocean',
						   'new_world_islands',
						   'new_world_mainland_coast',
						   ):
					plots[counter] = PlotTypes.PLOT_OCEAN
				counter += 1
		if mv.rocky == "islands":
			self.hillGroupOneRange += 8
			self.hillGroupTwoRange += 8
			self.peakPercent += 10
		if mv.rocky == "everything":
			self.hillGroupOneRange += 6
			self.hillGroupTwoRange += 6
		iWater = 60+mv.sea_level_change
		self.initFractal(continent_grain = 4, rift_grain = -1,
			has_center_rift = False, polar = True)
		temp_plots = self.generatePlotTypes(water_percent = iWater,
			grain_amount = 4)
		counter = 0
		for row in pm.getRows():
			for i in row:
				if i in (
						 'shallow_lake',
						 'peninsula_coast',
						 'gulf_core',
						 'new_world_islands',
						 ):
					plots[counter] = temp_plots[counter]
				counter += 1
		iWater = 80+mv.sea_level_change
		self.initFractal(continent_grain = 4, rift_grain = -1,
			has_center_rift = False, polar = True)
		temp_plots = self.generatePlotTypes(water_percent = iWater,
			grain_amount = 4)
		counter = 0
		for row in pm.getRows():
			for i in row:
				if i in (
						 'new_world_mainland_coast',
						 ):
					plots[counter] = temp_plots[counter]
				counter += 1
		if mv.rocky == "islands":
			self.hillGroupOneRange -= 8
			self.hillGroupTwoRange -= 8
			self.peakPercent -= 10
		if mv.rocky == "everything":
			self.hillGroupOneRange -= 6
			self.hillGroupTwoRange -= 6
		if mv.rocky == "continents":
			self.hillGroupOneRange += 2
			self.hillGroupTwoRange += 2
			self.peakPercent += 10
		iWater = 0
		self.initFractal(continent_grain = 1, rift_grain = -1,
			has_center_rift = False, polar = True)
		temp_plots = self.generatePlotTypes(water_percent = iWater)
		counter = 0
		for row in pm.getRows():
			for i in row:
				if i in (
						 'peninsula_core',
						 'peninsula_lake_zone',
						 'new_world_mainland',
						 'new_world_lake_zone',
						 ) and temp_plots[counter] != PlotTypes.PLOT_OCEAN:
							plots[counter] = temp_plots[counter]
				counter += 1
		iWater = 85
		self.initFractal(continent_grain = 4, rift_grain = -1,
			has_center_rift = False, polar = True)
		temp_plots = self.generatePlotTypes(water_percent = iWater,
			grain_amount = 4)
		counter = 0
		for row in pm.getRows():
			for i in row:
				if i in (
						 'peninsula_lake_zone',
						 'new_world_lake_zone',
						 ) and temp_plots[counter] != PlotTypes.PLOT_OCEAN:
							plots[counter] = PlotTypes.PLOT_OCEAN
				counter += 1
		iWater = 0
		self.hillGroupOneRange += 12
		self.hillGroupTwoRange += 12
		self.initFractal(continent_grain = 1, rift_grain = -1,
			has_center_rift = False, polar = True)
		temp_plots = self.generatePlotTypes(water_percent = iWater)
		counter = 0
		for row in pm.getRows():
			for i in row:
				if i in (
						 'gulf_high_slope',
						 'peninsula_high_slope',
						 ) \
				and temp_plots[counter] in (
											PlotTypes.PLOT_HILLS,
											PlotTypes.PLOT_PEAK,
											):
					plots[counter] = PlotTypes.PLOT_HILLS
				if i in (
						 'gulf_low_slope',
						 'peninsula_low_slope',
						 ) \
				and temp_plots[counter] in (
											PlotTypes.PLOT_PEAK,
											):
					plots[counter] = PlotTypes.PLOT_HILLS
				counter += 1
		return plots

class BasicTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self,iClimate):
		CvMapGeneratorUtil.TerrainGenerator.__init__(self)
		self.iClimate = iClimate
		self.iDesertPercent += \
			self.gc.getClimateInfo(iClimate).getDesertPercentChange()
		self.iDesertPercent = min(self.iDesertPercent,100)
		self.iDesertPercent = max(self.iDesertPercent,0)
		self.fSnowLatitude += \
			self.gc.getClimateInfo(iClimate).getSnowLatitudeChange()
		self.fSnowLatitude = min(self.fSnowLatitude,1.0)
		self.fSnowLatitude = max(self.fSnowLatitude,0.0)
		self.fTundraLatitude += \
			self.gc.getClimateInfo(iClimate).getTundraLatitudeChange()
		self.fTundraLatitude = min(self.fTundraLatitude,1.0)
		self.fTundraLatitude = max(self.fTundraLatitude,0.0)
		self.fGrassLatitude += \
			self.gc.getClimateInfo(iClimate).getGrassLatitudeChange()
		self.fGrassLatitude = min(self.fGrassLatitude,1.0)
		self.fGrassLatitude = max(self.fGrassLatitude,0.0)
		self.fDesertBottomLatitude += \
			self.gc.getClimateInfo(iClimate).getDesertBottomLatitudeChange()
		self.fDesertBottomLatitude = min(self.fDesertBottomLatitude,1.0)
		self.fDesertBottomLatitude = max(self.fDesertBottomLatitude,0.0)
		self.fDesertTopLatitude += \
			self.gc.getClimateInfo(iClimate).getDesertTopLatitudeChange()
		self.fDesertTopLatitude = min(self.fDesertTopLatitude,1.0)
		self.fDesertTopLatitude = max(self.fDesertTopLatitude,0.0)

class CalderaTerrainGenerator(BasicTerrainGenerator):
	def getLatitudeAtPlot(self,iX,iY):
		d = getDistanceToCenter(fromAbsolutes(iX,iY))
		if d > 1.0: d = 1.0
		#Temperate:
		if self.iClimate == 0: return \
			(CyGlobalContext().getGame().getMapRand().get(
			5,"Add cold terrain in random locations."))*0.01+0.56
		#Tropical:
		if self.iClimate == 1: return 0.22
		#Arid:
		if self.iClimate == 2: return d*0.35+0.14
		#Cold:
		if self.iClimate == 4: return \
			(CyGlobalContext().getGame().getMapRand().get(
			6,"Add cold terrain in random locations.")**2)*0.01+0.40

class BasicFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def __init__(self,iClimate):
		CvMapGeneratorUtil.FeatureGenerator.__init__(self)
		self.iClimate = iClimate
	def addIceAtPlot(self,pPlot,iX,iY,lat):
		if pPlot.canHaveFeature(self.featureIce):
			if (self.map.isWrapX() and not self.map.isWrapY()) \
			and (iY == 0 or iY == self.iGridH - 1):
				pPlot.setFeatureType(self.featureIce, -1)
			elif (self.map.isWrapY() and not self.map.isWrapX()) \
			and (iX == 0 or iX == self.iGridW - 1):
				pPlot.setFeatureType(self.featureIce, -1)
			else:
				rand = self.mapRand.get(100,"Add ice in random locations.")
				rand /= 100.0
				randIceLatitude = \
					self.gc.getClimateInfo(self.iClimate).getRandIceLatitude()
				if rand < 8 * (lat - (1.0 - (randIceLatitude / 2.0))):
					pPlot.setFeatureType(self.featureIce, -1)
				elif rand < 4 * (lat - (1.0 - randIceLatitude)):
					pPlot.setFeatureType(self.featureIce, -1)
	def addJunglesAtPlot(self,pPlot,iX,iY,lat):
		if pPlot.canHaveFeature(self.featureJungle):
			iJungleHeight = self.jungles.getHeight(iX,iY)
			iJungleBottom = self.iJungleTop - self.iJungleBottom
			iJungleBottom *= \
				self.gc.getClimateInfo(self.iClimate).getJungleLatitude() * lat
			iJungleBottom += self.iJungleBottom
			if self.iJungleTop >= iJungleHeight >= iJungleBottom:
				pPlot.setFeatureType(self.featureJungle, -1)

class CalderaFeatureGenerator(BasicFeatureGenerator):
	def getLatitudeAtPlot(self,iX,iY):
		d = getDistanceToCenter(fromAbsolutes(iX,iY))
		if d > 1.0: d = 1.0
		#Temperate:
		if self.iClimate == 0: return \
			(CyGlobalContext().getGame().getMapRand().get(
			5,"Add cold terrain in random locations."))*0.01+0.56
		#Tropical:
		if self.iClimate == 1: return 0.22
		#Arid:
		if self.iClimate == 2: return d*0.35+0.14
		#Cold:
		if self.iClimate == 4: return 0.55

# vim: ts=4
