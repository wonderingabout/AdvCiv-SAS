#
# FILE: Caldera.py
# AUTHOR: Zholef (username at forums.civfanatics.com)
# PURPOSE: Civ4 map script - Losely based on the Mediterranean Sea.
#
# 2020 - Updated for BTP 2.16
# 2024 -- Mega Transformation and simplification in BTG 2.38, see 2.37 or before for other version (in 2.37 crashes because of function on Colony)

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import *
import sys
import random

#2.17Add
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
balancer = BonusBalancer()
balancer.resourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM','BONUS_COAL')
balancer.resourcesToEliminate = ('', )
#End 2.17

def getDescription():
	return "Beyond the Game map based on Caldera from Zholef at Civfanatics"
	
def getDescriptionTitle():
	return "Based on Caldera from Zholef, gives each player a 'peak of island of land in a shape where they can be linked via the external coast, and have a short, naval, distance to the lands of the middle"

def getDescriptionTitleTwo():
	return "Land distances are actually quite far for what it looks like initially, but boat distances are very short"

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return "Explore well at beginning, the inner sea can sometimes be very blocked by land, but sometimes very porous making the actual naviguated distances even shorter "	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "By selecting 'Encourage' on option 'New World Creation', you are forcing empty seas at the very middle of the map, making the sea open to boating even more important"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Teamers shine in era where establishing naval supremancy is important, Renaissance, Industrial (very aggressive start) and to a lesser extent Medieval"	

def getDescriptionBalance():#Balance : (at the bottom)"
	return "Ban Mediterranean naval powers - SPAIN and OTTOMANS, and PHOENICIA for map reveal, exploring is too important here"	
	
def isAdvancedMap():
	return 0
def isClimateMap():
	return 0
def getNumCustomMapOptions():
	n = 15
	if not hasattr(CvMapGeneratorUtil,'BonusBalancer'): n -= 1
	return n
def getNumHiddenCustomMapOptions():
	n = 9
	if not hasattr(CvMapGeneratorUtil,'BonusBalancer'): n -= 1
	return n
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Starting locations:",
		1:	"New World creation:",
		2:	"Map shape:",
		3:	"Size factor:",
		4:	"Coasts:",
		5:	"Ground:",
		6:	"Extra rivers:",
		7:	"Resources:",
		8:  "Central Islands",
		9:	"BTG Resources",		
		10:	"BTG Free Unit",
		11: "BTG Amt Free Unit",
		12:	"Notes",
		13:	"BTG Spectator Notes",
		14:	"Credit",		
		}
	return unicode(CyTranslator().getText(option_names[iOption],()))
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:	2,
		2:	3,
		3:	3,
		4:	6,
		5:	4,
		6:	2,	
		7:	3,
		8:  4,
		9:  2,
		10:	4,
		11:	4,		
		12: 3,
		13: 2,
		14:	1,
		}
	return option_values[iOption]
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0:	"On the largest landmass",
			1:	"TXT_KEY_MAP_SCRIPT_START_ANYWHERE",
			2:	"TXT_KEY_MAP_SCRIPT_ISLANDS",
			3:	"On Main Landmass - Avoid Coastal"
			},
		1:	{
			0:	"Encourage - Centre of map is Water",
			1:	"Discourage - Centre of map is Sinous long islands",
			},
		2:	{
			0:	"Rectangle",
			1:	"Square",
			2:	"Tilted rectangle",
			},
		3:	{
			0:	"TXT_KEY_WORLD_STANDARD",
			1:	"TXT_KEY_WORLD_LARGE",
			2:	"TXT_KEY_WORLD_HUGE",
			},
		4:	{
			0:	"Steep",
			1:	"Narrow",
			2:	"Wide",
			3:	"Very Wide",
			4:	"Super Wide",
			5:	"Uber Wide",
			},
		5:	{
			0:	"Normal",
			1:	"Rocky islands",
			2:	"Rocky continents",
			3:	"Rocky everywhere",
			},
		6:	{
			0:	"No",
			1:	"Yes",
			},
		7:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "Balanced - Including Marble",
			2: "Balanced - Extra food"
			},
		8:	{
			0: "Normal",
			1: "Arctic - Frozen",
			2: "Sticky - Marsh/Plains",
			3: "Flat Land Only",
			},
		9:	{
			0: "No",
			1: "Yes - Balanced for Jade and Nickel, Normal for others"	
			},	
		10:	{
			0: "None",
			1: "Lumberjack",
			2: "TXT_KEY_UNIT_FRENCH_MUSKETEER",
			3: "TXT_KEY_UNIT_MACHINE_GUN",
			},
		11:	{
			0: "0",
			1: "1",
			2: "2",
			3: "3"
			},				
		12:	{
			0: "3v3 (small) and 2v2 (tiny) with either Rectangle or Square, large coast (default)",
			1: "'Size factor' on 'large' for when early access to water (Indus+), otherwise 'normal'",
			2: "'New World' on 'discouraged' for colonies in center. Otherwise larger water mass",			
			},
		13:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"		
			},
		14:	{
			0: "Based on Caldera from Zholef, credit to him for helping us on this",
			}				
		}
	translated_text = unicode(CyTranslator().getText(
	                          selection_names[iOption][iSelection],()))
	return translated_text
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	3,
		1:	0,
		2:	1,#2.42
		3:	1,
		4:	4,
		5:	0,
		6:	1,
		7:	2,
		8:  3,
		9:  1,
		10:	0,
		11:	0,
		12:	0,
		13:	0,
		14:	0
		}
	return option_defaults[iOption]
def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	False,
		1:	True,
		2:	True,
		3:	True,
		4:	True,
		5:	True,
		6:	True,
		7:	False,
		8:  True,
		9:	True,
		10: False,
		11:	False,
		12: False,
		13:	False,
		14:	False
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

	mv.climate = "temperate" #Penny line
	print "climate: " + mv.climate
	if   map.getCustomMapOption(0) == 0: mv.start = "old_world_mainland"
	elif map.getCustomMapOption(0) == 1: mv.start = "anywhere"
	elif map.getCustomMapOption(0) == 2: mv.start = "on_islands"
	elif map.getCustomMapOption(0) == 3: mv.start = "old_world_mainland_inside"#2.38
	print "start: " + mv.start
	if   map.getCustomMapOption(1) == 0: mv.new_world_creation = "encouraged"
	elif map.getCustomMapOption(1) == 1: mv.new_world_creation = "discouraged"
	print "new_world_creation: " + mv.new_world_creation
	if   map.getCustomMapOption(2) == 0: mv.shape = "rectangular"
	elif map.getCustomMapOption(2) == 1: mv.shape = "squared"
	elif map.getCustomMapOption(2) == 2: mv.shape = "tilted"
	print "shape: " + mv.shape
	if   map.getCustomMapOption(3) == 0: mv.size_mod = "standard"
	elif map.getCustomMapOption(3) == 1: mv.size_mod = "large"
	elif map.getCustomMapOption(3) == 2: mv.size_mod = "huge"
	print "size_mod: " + mv.size_mod
	if   map.getCustomMapOption(4) == 0: mv.connection_width = 0.0
	elif map.getCustomMapOption(4) == 1: mv.connection_width = 0.5
	elif map.getCustomMapOption(4) == 2: mv.connection_width = 1.0
	elif map.getCustomMapOption(4) == 3: mv.connection_width = 1.5
	elif map.getCustomMapOption(4) == 4: mv.connection_width = 2.5 # Penny 2.42
	elif map.getCustomMapOption(4) == 5: mv.connection_width = 3.5 # Penny 2.42
	print "connection_width: " + str(mv.connection_width)
	if   map.getCustomMapOption(5) == 0: mv.rocky = "normal"
	elif map.getCustomMapOption(5) == 1: mv.rocky = "islands"
	elif map.getCustomMapOption(5) == 2: mv.rocky = "continents"
	elif map.getCustomMapOption(5) == 3: mv.rocky = "everything"
	print "rocky: " + mv.rocky
	if   map.getCustomMapOption(6) == 0: mv.extra_rivers = False
	elif map.getCustomMapOption(6) == 1: mv.extra_rivers = True
	print "extra_rivers: " + str(mv.extra_rivers)

	if hasattr(CvMapGeneratorUtil,'BonusBalancer'):
		if   map.getCustomMapOption(7) == 0: mv.balanced = False
		elif map.getCustomMapOption(7) == 1: mv.addBalancer()
		elif map.getCustomMapOption(7) == 2: mv.addBalancer()#Penny add
		print "balanced: " + str(mv.balanced)
		
	global iOptionValue_Resource
	iOptionValue_Resource = CyMap().getCustomMapOption(7)#bit of a repeat to above
		
	#2.38
	global iOptionValue_CentralLand
	global iOptionValue_ResourceBTG
	global iOptionValue_StartingUnit
	global iOptionValue_StartingUnitCount
	global iOptionValue_BTGBans

	iOptionValue_CentralLand = CyMap().getCustomMapOption(8)
	iOptionValue_ResourceBTG = CyMap().getCustomMapOption(9)
	iOptionValue_StartingUnit = CyMap().getCustomMapOption(10)
	iOptionValue_StartingUnitCount = CyMap().getCustomMapOption(11)
	iOptionValue_BTGBans = CyMap().getCustomMapOption(12)
	
		
def getGridSize(argsList):
	grid_sizes = {
		"standard": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(7,5),
				WorldSizeTypes.WORLDSIZE_TINY:		(9,7),
				WorldSizeTypes.WORLDSIZE_SMALL:		(12,8),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(16,10),
				WorldSizeTypes.WORLDSIZE_LARGE:		(21,13),
				WorldSizeTypes.WORLDSIZE_HUGE:		(26,16)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(6,6),
				WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
				WorldSizeTypes.WORLDSIZE_SMALL:		(9,9),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,10),
				WorldSizeTypes.WORLDSIZE_LARGE:		(13,13),
				WorldSizeTypes.WORLDSIZE_HUGE:		(20,20)},
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(5,7),
				WorldSizeTypes.WORLDSIZE_TINY:		(7,9),
				WorldSizeTypes.WORLDSIZE_SMALL:		(8,12),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(10,16),
				WorldSizeTypes.WORLDSIZE_LARGE:		(13,21),
				WorldSizeTypes.WORLDSIZE_HUGE:		(16,26)},
			},
		"large": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(9,7),
				WorldSizeTypes.WORLDSIZE_TINY:		(11,8),
				WorldSizeTypes.WORLDSIZE_SMALL:		(14,9),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(21,13),
				WorldSizeTypes.WORLDSIZE_LARGE:		(26,16),
				WorldSizeTypes.WORLDSIZE_HUGE:		(32,20)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(7,7),
				WorldSizeTypes.WORLDSIZE_TINY:		(9,9),
				WorldSizeTypes.WORLDSIZE_SMALL:		(12,12),#
				WorldSizeTypes.WORLDSIZE_STANDARD:	(15,15),
				WorldSizeTypes.WORLDSIZE_LARGE:		(19,19),
				WorldSizeTypes.WORLDSIZE_HUGE:		(22,22)},				
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(7,9),
				WorldSizeTypes.WORLDSIZE_TINY:		(8,11),
				WorldSizeTypes.WORLDSIZE_SMALL:		(9,14),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(13,21),
				WorldSizeTypes.WORLDSIZE_LARGE:		(16,26),
				WorldSizeTypes.WORLDSIZE_HUGE:		(20,32)},
			},
		"huge": {
			"rectangular": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(10,7),
				WorldSizeTypes.WORLDSIZE_TINY:		(13,9),
				WorldSizeTypes.WORLDSIZE_SMALL:		(16,10),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(26,16),
				WorldSizeTypes.WORLDSIZE_LARGE:		(32,20),
				WorldSizeTypes.WORLDSIZE_HUGE:		(38,24)},
			"squared": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(9,9),
				WorldSizeTypes.WORLDSIZE_TINY:		(11,11),
				WorldSizeTypes.WORLDSIZE_SMALL:		(12,12),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(28,28),
				WorldSizeTypes.WORLDSIZE_LARGE:		(22,22),
				WorldSizeTypes.WORLDSIZE_HUGE:		(28,28)},
			"tilted": {
				WorldSizeTypes.WORLDSIZE_DUEL:		(7,10),
				WorldSizeTypes.WORLDSIZE_TINY:		(9,13),
				WorldSizeTypes.WORLDSIZE_SMALL:		(10,16),
				WorldSizeTypes.WORLDSIZE_STANDARD:	(16,26),
				WorldSizeTypes.WORLDSIZE_LARGE:		(20,32),
				WorldSizeTypes.WORLDSIZE_HUGE:		(24,38)},
			},}
	[eWorldSize] = argsList
	if eWorldSize == -1: return []
	return grid_sizes[mv.size_mod][mv.shape][eWorldSize]
def getTopLatitude():  return  15	
def getBottomLatitude():  return -15
def isBonusIgnoreLatitude(): return True
def getWrapX(): return False
def getWrapY(): return False
def beforeGeneration():
	global isBTPon
	global iBrown
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
	except:
		isBTPon = False
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
		
	mv.players = CyGlobalContext().getGame().countCivPlayersEverAlive()

def generatePlotTypes():return CalderaFractalWorld(0).generateCalderaPlots()
def generateTerrainTypes(): return CalderaTerrainGenerator(0).generateTerrain()

def addRivers():
	gc = CyGlobalContext()
	if mv.extra_rivers:
		ppre = mv.orig_ppre * 2/3
		if mv.extra_rivers and mv.climate in ("boreal"): ppre *= 3/4
		gc.setDefineINT("PLOTS_PER_RIVER_EDGE",ppre)
		gc.setDefineINT("RIVER_SOURCE_MIN_RIVER_RANGE",mv.orig_rsmrr*3/4)
		gc.setDefineINT("RIVER_SOURCE_MIN_SEAWATER_RANGE",mv.orig_rsmsr/2)
	CyPythonMgr().allowDefaultImpl()
	
def getRiverStartCardinalDirection(argsList):
	if argsList[0].getArea() == CyMap().findBiggestArea(False).getID():
		#Penny from underlying map
		pPlot = argsList[0]
		map = CyMap()

		if (pPlot.getY() > ((map.getGridHeight() * 2) / 3)):
			return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH

		if (pPlot.getY() < (map.getGridHeight() / 3)):
			return CardinalDirectionTypes.CARDINALDIRECTION_NORTH

		if (pPlot.getX() > (map.getGridWidth() / 2)):
			return CardinalDirectionTypes.CARDINALDIRECTION_WEST

		return CardinalDirectionTypes.CARDINALDIRECTION_EAST
		#end Penny
		
	CyPythonMgr().allowDefaultImpl()
def getRiverAltitude(argsList):
	if argsList[0].getArea() == CyMap().findBiggestArea(False).getID():
		#Penny from underlying map
		pPlot = argsList[0]
		map = CyMap()

		CyPythonMgr().allowDefaultImpl()

		return ((abs(pPlot.getX() - (map.getGridWidth() / 2)) + abs(pPlot.getY() - (map.getGridHeight() / 2))) * 20)
		#end Penny
	CyPythonMgr().allowDefaultImpl()
def addLakes(): return None # We'll add our own during plot generation.

def addFeatures():

	CalderaFeatureGenerator(0).addFeatures()	
		
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
	if mv.start == "old_world_mainland" or mv.start == "old_world_mainland_inside" : return  0
	if mv.size_mod in ("standard"):      return 50
	if mv.size_mod in ("large"):         return 65
	if mv.size_mod in ("huge"):          return 80
def findStartingPlot(argsList):
	[playerID] = argsList
	
	if isBTPon:#2.22
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		if iNumSpectators > 0:
			if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
			#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
				return -1		
	
	def isValid(playerID,iX,iY):
		#if CyGlobalContext().getPlayer(playerID).isSpectator():#2.18
		#	return True## Commented out because I need to "make the mistake" since I fix it in C++
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
			if mv.start == "old_world_mainland" or mv.start == "old_world_mainland_inside":
				if pPlot.getArea() != CyMap().findBiggestArea(False).getID():
					return False
					
				#2.38 Reject tiles with 4 water around
				if mv.start == "old_world_mainland_inside":
					iWaterCount = 0
					startx, starty = pPlot.getX(), pPlot.getY()	
					for dx in range(-2,3):
						for dy in range(-2,3):					
					#for dx in range(-1,2):
					#	for dy in range(-1,2):
							pTest = CyMap().plot(startx+dx,starty+dy)
							if pTest.isWater():			
								iWaterCount +=1
					if iWaterCount >= 2:
						return False
				#2.38end
				
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
	
def addBonusType(argsList):
	[iBonusType] = argsList
	type_string = CyGlobalContext().getBonusInfo(iBonusType).getType()
	
	#2.21y
	if isBTPon:
		if (iOptionValue_ResourceBTG == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
			
	if (iOptionValue_Resource >= 1):#balanced or superbalanced
		if (type_string in balancer.resourcesToBalance):#BTP Because marble is broken
			return None # don't place any of this bonus randomly			
			
	CyPythonMgr().allowDefaultImpl()	
	
def normalizeAddExtras():
	
	if mv.balanced:
		#mv.balancer.normalizeAddExtras()
		listToBalance = ["BONUS_ALUMINUM", "BONUS_COAL", "BONUS_COPPER", "BONUS_HORSE", "BONUS_IRON", "BONUS_OIL", "BONUS_URANIUM"]
		BTPnormalizeAddExtrasSpecificAera(listToBalance,6,0,100,True)
		
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),8,2,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))		

	if iOptionValue_ResourceBTG == 1 and isBTPon :#2.35
		listToBalanceBTG = ["BONUS_JADE","BONUS_NICKEL"]
		BTPnormalizeAddExtrasSpecificAera(listToBalanceBTG,7,3,100,True)			
	
		
			
							
	if (iOptionValue_Resource >= 2):	
		#Scaling down a bit
		#BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),8,4,False,iBrown)
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),8,4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_BANANA"),5,0,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))	

	
	BTPMarshMinorLand(False,iOptionValue_CentralLand)		

	CyPythonMgr().allowDefaultImpl()
		
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
		return 0.55

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
		return 0.55


def BTGFreeUnit():

	if (iOptionValue_StartingUnit == 0):
		return -1
	elif (iOptionValue_StartingUnit == 1):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_LUMBERJACK")
	elif (iOptionValue_StartingUnit == 2):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_FRENCH_MUSKETEER")
	elif (iOptionValue_StartingUnit == 3):
		iNewType = CyGlobalContext().getInfoTypeForString("UNIT_MACHINE_GUN")		
	else:
		return -1
		
	return iNewType
	
def BTGFreeUnitCount():	return iOptionValue_StartingUnitCount	



def BTPMarshMinorLand(bFindBiggestArea,iTerrainType):

	map = CyMap()
	gc = CyGlobalContext()
	plotNonMainArea = []
	
	if iTerrainType == 1:
		iNewTerrain = gc.getInfoTypeForString("TERRAIN_SNOW")
	if iTerrainType == 2:
		iNewTerrain = iBrown
	
	if iTerrainType > 0:# 0 is do Nothing / Normal
	
		for dx in range(1,map.getGridWidth()-2):
			for dy in range(1,map.getGridHeight()-2):
				p = map.plot(dx,dy)
				if (p.getArea() != CyMap().findBiggestArea(False).getID() and bFindBiggestArea == False):
					plotNonMainArea.append(p)
				### I haven't done test with the area = True yet	
					

		for p in plotNonMainArea:	
			#if not p.isWater():	
			if not p.isWater() and not p.isPeak():#2.42 - was visible when flatten not good
				#2.42 New Case, just flatten the land
				if iTerrainType == 3:
					p.setPlotType(PlotTypes.PLOT_LAND, True, True)
					continue
				# Else the pre 2-42 logic
			
				p.setTerrainType(iNewTerrain, True, True)
				if iTerrainType == 1:
					p.setFeatureType(gc.getInfoTypeForString("FEATURE_ICE"), -1)


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

def BTPnormalizeAddExtrasSpecificAera(listToBalance,iDistanceMax,iDistanceMin,iProbaTreshold,bMainAreaOnly):
	gc = CyGlobalContext()	
	random.seed(gc.getGame().getMapRand().get(30000, "Shuffle Plots - PYTHON"))
	
	for i in range(gc.getMAX_CIV_PLAYERS()):
		if (gc.getPlayer(i).isEverAlive()):
			start_plot = gc.getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()
			
			plots = []
			for dx in range(-iDistanceMax,iDistanceMax+1):
				for dy in range(-iDistanceMax,iDistanceMax+1):
					if ((abs(dx) >= iDistanceMin) and (abs(dy) >= iDistanceMin)):#2.35 My Take
						x,y = startx+dx, starty+dy
						pLoopPlot = CyMap().plot(x,y)
						if not pLoopPlot.isNone():
							plots.append(pLoopPlot)
			
			resources_placed = []
			
			for pass_num in range(5):
				bIgnoreUniqueRange  = pass_num >= 1
				bIgnoreOneArea 		= pass_num >= 2
				bIgnoreWater	 	= pass_num >= 4#2.38 I flip this
				bIgnoreAdjacent 	= pass_num >= 3#2.38 I flip this

				for bonus in range(gc.getNumBonusInfos()):
					type_string = gc.getBonusInfo(bonus).getType()
					if (type_string not in resources_placed)  and (type_string in listToBalance):####This is the line that's different
						bLandValid = False
						for iTerrain in range(gc.getNumTerrainInfos()):
							if gc.getBonusInfo(bonus).isTerrain(iTerrain):
								if not gc.getTerrainInfo(iTerrain).isWater():
									bLandValid = True
						# Randomize placement
						iOffset = gc.getGame().getMapRand().get(len(plots), "BonusBalancer")
						for j in range(0, len(plots)):
							pLoopPlot = plots[(j + iOffset) % len(plots)] # </advc.108c>
							if (pLoopPlot.canHaveBonus(bonus, True)
									# advc.108c:
									and (bIgnoreWater or not pLoopPlot.isWater() or not bLandValid)):
								#### 2.39 ######
								if not bMainAreaOnly or pLoopPlot.getArea() == CyMap().findBiggestArea(False).getID():
								#################
									if balancer.isBonusValid(bonus, pLoopPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
										resources_placed.append(type_string)	
										iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
										if iProba <= iProbaTreshold:#2.35 my Take
											pLoopPlot.setBonusType(bonus)
										break # go to the next bonus'''	