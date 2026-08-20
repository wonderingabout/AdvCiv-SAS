#
#	FILE:	 Hemispheres.py
#	AUTHOR:  Ben Sarsgard
#	PURPOSE: Global map script - Hemisphere or quadrant split with oceanic divide
#		Mostly adapted from Sirian's Big_and_Small
#	VERSION: 1.20
#-----------------------------------------------------------------------------
#	Copyright (c) 2007 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Hemispheres - a fractal map"
	
def getDescriptionTitle():
	return "A fractal map, original untouched from BTS. Best to play with the big aggregate of the fractal engine"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return ""

def getDescriptionSecond():#Script tip : (on TOP)
	return ""
	
def getDescriptionThird():#Option : (at the bottom)"
	return ""	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Be very clear in the amount and size of continents. By default it's 2 and is the exact same as the Continents map"

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""		

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 11
	
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_CONTINENTS_SIZE",
		1:	"TXT_KEY_MAP_SCRIPT_ISLANDS_SIZE",
		2:	"TXT_KEY_MAP_SCRIPT_NUMBER_OF_CONTINENTS",
		3:	"Mirror",
		4:	"Circumnavigation",
		5:	"Wonder Resources",
		6:  "Normalisation",
		7:	"BTG Bans",
		8:	"BTG Seas",
		9:	"BTG Spectators",
		10:	"Credit",
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:	2,
		2:	5,
		3:	2,
		4:	2,
		5:	3,
		6:	3,
		7:	6,
		8:	4,
		9:	1,
		10:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_MASSIVE_CONTINENTS",
			1: "TXT_KEY_MAP_SCRIPT_NORMAL_CONTINENTS",
			2: "TXT_KEY_MAP_SCRIPT_SNAKY_CONTINENTS",
			3: "TXT_KEY_MAP_SCRIPT_VARIED"
			},
		1:	{
			0: "TXT_KEY_MAP_SCRIPT_ISLANDS",
			1: "TXT_KEY_MAP_SCRIPT_TINY_ISLANDS"
			},
		2:	{
			0: "2",
			1: "3",
			2: "4",
			3: "5",
			4: "6"
			},
		3:	{
			0: "No",
			1: "Yes - Starts work for 2 continents"
			},	
		4:	{
			0: "Normal",
			1: "Disabled (BTS Hardcoded, BTG via option)"
			},				
		5:	{
			0: "Normal Stone & Marble",
			1: "No Stone & Marble at all on map",
			2: "Left of map is Stone, right of map is Marble",
			},	
		6:	{
			0: "Normal - Add Food/Hills/River/Lake in some cases, imperfect mirroring",
			1: "No - Blocked, LDeska style",
			2: "Yes - Penny Logic, Deer to equalise low food start  & min 3 hills",
			},				
		7:	{
			0: "No Ban",
			1: "Ban ORACLE",
			2: "Ban GREAT LIGHTHOUSE",
			3: "Ban ORACLE and GREAT LIGHTHOUSE",
			4: "Ban ORACLE, GREAT LIGHTHOUSE, COLOSSUS",
			5: "Ban all World Wonders"
			},
		8:	{
			0: "No",
			1: "Yes - All Lagoons",
			2: "Yes - Lagoons on coast",
			3: "Yes - Balanced Lagoons and Deep sea"
			},			
		9:	{
			0: "1 Spectator in any Slot or Team, even for Mirror"
			},
		10:	{
			0: "Original BTS map"
			}
		}
	if (iOption < 3):
		translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	else:
		translated_text = selection_names[iOption][iSelection]
	return translated_text

def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:	1,
		2:	0,
		3:	0,
		4:	0,
		5:	0,
		6:	2,
		7:	1,
		8:	2,
		9:	0,
		10:	0
		}
	return option_defaults[iOption]
	
def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	True,
		1:	True,
		2:	True,
		3:	False,
		4:	False,
		5:	False,
		6:	False,
		7:	False,
		8:	False,
		9:	False,
		10:	False,
		}
	return option_random[iOption]

def minStartingDistanceModifier():
	return -12

def beforeGeneration():

	beforeInitOptionsValue()

	global xShiftRoll
	global yShiftRoll
	global ySplitRoll
	global yPortionRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	
	global isBTPon
	global iNumSpectators
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
		
	except:
		isBTPon = False
		iNumSpectators = 0	

	# Binary shift roll (for horizontal shifting if Island Region Separate).
	xShiftRoll = dice.get(2, "Region Shift, Horizontal - Left and Right PYTHON")
	yShiftRoll = dice.get(2, "Region Shift, Vertical - Left and Right PYTHON")
	ySplitRoll = dice.get(2, "Region Split, Vertical - Left and Right PYTHON")
	yPortionRoll = dice.get(2, "Region Portioning, Vertical - Left and Right PYTHON")
	
	
	#This is from LD Remote COntinent for the mirror feature
	global team_num
	team_num = []
	team_index = 0
	for teamCheckLoop in range(gc.getMAX_CIV_PLAYERS()):
		if CyGlobalContext().getTeam(teamCheckLoop).isEverAlive():
			team_num.append(team_index)
			team_index += 1
		else:
			team_num.append(-1)	
	
	
	print xShiftRoll
	
def beforeInitOptionsValue():#2.39
	
	global iOptionValue_Mirror
	global iOptionValue_Circumnavigation
	global iOptionValue_WonderResources
	global iOptionValue_Normalization
	global iOptionValue_WonderBan
	global iOptionValue_Lagoon
	
	iOptionValue_Mirror = CyMap().getCustomMapOption(3)
	iOptionValue_Circumnavigation = CyMap().getCustomMapOption(4)
	iOptionValue_WonderResources = CyMap().getCustomMapOption(5)
	iOptionValue_Normalization = CyMap().getCustomMapOption(6)
	iOptionValue_WonderBan = CyMap().getCustomMapOption(7)
	iOptionValue_Lagoon = CyMap().getCustomMapOption(8)
	


class BnSMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def generateIslandRegion(self, minTinies, extraTinies, iWestX, iSouthY, iWidth, iHeight, iGrain):
		# Add a few random patches of Tiny Islands first.
		#TODO: Base numTinies on global prevalance option
		numTinies = minTinies + self.dice.get(extraTinies, "Tiny Islands - Custom Continents PYTHON")
		print("Patches of Tiny Islands: ", numTinies)
		if numTinies:
			for tiny_loop in range(numTinies):
				tinyWidth = int(self.iW * 0.15)
				tinyHeight = int(self.iH * 0.15)

				tinyWestX = iWestX + self.dice.get(iWidth - tinyWidth, "Tiny Longitude - Custom Continents PYTHON")
				tinySouthY = iSouthY + self.dice.get(iHeight - tinyHeight, "Tiny Latitude - Custom Continents PYTHON")

				self.generatePlotsInRegion(80,
										   tinyWidth, tinyHeight,
										   tinyWestX, tinySouthY,
										   iGrain, 3,
										   0, self.iTerrainFlags,
										   6, 5,
										   True, 3,
										   -1, False,
										   False
										   )
		return 0

	def generateContinentRegion(self, iWater, iWidth, iHeight, iWestX, iSouthY, iGrain, xExp):
		self.generatePlotsInRegion(iWater,
								   iWidth, iHeight,
								   iWestX, iSouthY,
								   iGrain, 4,
								   self.iRoundFlags, self.iTerrainFlags,
								   xExp, 6,
								   True, 15,
								   -1, False,
								   False
								   )
		return 0

	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		global xShiftRoll
		global yShiftRoll
		global ySplitRoll
		global yPortionRoll

		print("getSeaLevelChange", self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange())

		if (self.map.getCustomMapOption(0) == 3):
			# Generate varied
			iContinentsGrain = 1
			iSecondaryContinentsGrain = 3
			iTertiaryContinentsGrain = 2
			iPrimaryWater = 74
			iSecondaryWater = 79
			iTertiaryWater = 76
		else:
			iContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iSecondaryContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iTertiaryContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iPrimaryWater = 74
			iSecondaryWater = 74
			iTertiaryWater = 74

		iPrimaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		iSecondaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		iTertiaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()

		splitYBigger = 0.5
		splitYSmaller = 0.5
		splitYBuffer = 0.1

		iIslandsGrain = 3 + self.map.getCustomMapOption(1)
		tinyIslandOverlap = 0
		regions = 2 + self.map.getCustomMapOption(2)
		if (regions == 2):
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 0
		elif (regions == 3):
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 1
		elif (regions == 4):
			vSplitPrimary = 1
			vSplitSecondary = 1
			vSplitTertiary = 0
			tripleSplit = 0
		elif (regions == 5):
			vSplitPrimary = 0
			vSplitSecondary = 1
			vSplitTertiary = 1
			tripleSplit = 1
		elif (regions == 6):
			vSplitPrimary = 1
			vSplitSecondary = 1
			vSplitTertiary = 1
			tripleSplit = 1
		else:
			#unexpected
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 0

		# Water variables need to differ if Overlap is set. Defining default here.
		#TODO: Set this from the global option
		#iWater = 74

		# Base values for full map
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		iWestX = 0
		iEastX = self.iW - 1
		iWidth = iEastX - iWestX + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)

		if tinyIslandOverlap:
			self.generateIslandRegion(4, 6, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		# Add the Continents.
		# Horizontal dimensions may be affected by overlap and/or shift.
		# The regions are separate, with continents only in one part, islands only in the other.
		# Set X exponent to square setting:
		xExp = 6
		# Handle horizontal shift for the Continents layer.
		# (This will choose one side or the other for this region then fit it properly in its space).
		if tripleSplit:
			if xShiftRoll:
				westShift = int(0.33 * self.iW)
				eastShift = int(0.33 * self.iW)
			else:
				westShift = 0
				eastShift = int(0.66 * self.iW)
		else:
			if xShiftRoll:
				westShift = int(0.5 * self.iW)
				eastShift = 0
			else:
				westShift = 0
				eastShift = int(0.5 * self.iW)
		
		iWestX = westShift
		iEastX = self.iW - eastShift
		iWidth = iEastX - iWestX

		if vSplitPrimary:
			# Do first in split
			if yPortionRoll:
				if yShiftRoll:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYBigger * self.iH)
				else:
					northShift = int(splitYSmaller * self.iH)
					southShift = int(splitYBuffer * self.iH)
			else:
				if yShiftRoll:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYSmaller * self.iH)
				else:
					northShift = int(splitYBigger * self.iH)
					southShift = int(splitYBuffer * self.iH)

			iSouthY = southShift
			iNorthY = self.iH - northShift
			iHeight = iNorthY - iSouthY

			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iPrimaryWater, iWidth, iHeight, iWestX, iSouthY, iContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(1, 2, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

			# Second in split
			if yPortionRoll:
				if yShiftRoll:
					northShift = int(splitYSmaller * self.iH)
					southShift = int(splitYBuffer * self.iH)
				else:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYBigger * self.iH)
			else:
				if yShiftRoll:
					northShift = int(splitYBigger * self.iH)
					southShift = int(splitYBuffer * self.iH)
				else:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYSmaller * self.iH)

			iSouthY = southShift
			iNorthY = self.iH - northShift
			iHeight = iNorthY - iSouthY

			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iPrimaryWater, iWidth, iHeight, iWestX, iSouthY, iContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(1, 2, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		else:
			# Only one primary region
			iSouthY = 0
			iNorthY = self.iH - 1
			iHeight = iNorthY - iSouthY + 1
			print("Cont West: ", iWestX, "Cont East: ", iEastX, "Cont Width: ", iWidth)
			self.generateContinentRegion(iPrimaryWater, iWidth, iHeight, iWestX, iSouthY, iContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(2, 3, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		# Add the Secondary continents.
		# Horizontal dimensions may be affected by overlap and/or shift.
		# The regions are separate, with continents only in one part, islands only in the other.
		# Set X exponent to square setting:
		xExp = 6
		# Handle horizontal shift for the Continents layer.
		# (This will choose one side or the other for this region then fit it properly in its space).
		if tripleSplit:
			if xShiftRoll:
				westShift = 0
				eastShift = int(0.66 * self.iW)
			else:
				westShift = int(0.33 * self.iW)
				eastShift = int(0.33 * self.iW)
		else:
			if xShiftRoll:
				westShift = 0
				eastShift = int(0.5 * self.iW)
			else:
				westShift = int(0.5 * self.iW)
				eastShift = 0

		iWestX = westShift
		iEastX = self.iW - eastShift
		iWidth = iEastX - iWestX

		if vSplitSecondary:
			# Do first in split
			if yPortionRoll:
				if yShiftRoll:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYBigger * self.iH)
				else:
					northShift = int(splitYSmaller * self.iH)
					southShift = int(splitYBuffer * self.iH)
			else:
				if yShiftRoll:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYSmaller * self.iH)
				else:
					northShift = int(splitYBigger * self.iH)
					southShift = int(splitYBuffer * self.iH)

			iSouthY = southShift
			iNorthY = self.iH - northShift
			iHeight = iNorthY - iSouthY

			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iSecondaryWater, iWidth, iHeight, iWestX, iSouthY, iSecondaryContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(2, 3, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

			# Second in split
			if yPortionRoll:
				if yShiftRoll:
					northShift = int(splitYSmaller * self.iH)
					southShift = int(splitYBuffer * self.iH)
				else:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYBigger * self.iH)
			else:
				if yShiftRoll:
					northShift = int(splitYBigger * self.iH)
					southShift = int(splitYBuffer * self.iH)
				else:
					northShift = int(splitYBuffer * self.iH)
					southShift = int(splitYSmaller * self.iH)

			iSouthY = southShift
			iNorthY = self.iH - northShift
			iHeight = iNorthY - iSouthY

			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iSecondaryWater, iWidth, iHeight, iWestX, iSouthY, iSecondaryContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(2, 3, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)
		else:
			# Only one secondary region
			iSouthY = 0
			iNorthY = self.iH - 1
			iHeight = iNorthY - iSouthY + 1
			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iSecondaryWater, iWidth, iHeight, iWestX, iSouthY, iSecondaryContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(3, 4, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		if tripleSplit:
			# Add the Tertiary continents.
			# Horizontal dimensions may be affected by overlap and/or shift.
			# The regions are separate, with continents only in one part, islands only in the other.
			# Set X exponent to square setting:
			xExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			westShift = int(0.66 * self.iW)
			eastShift = 0
			
			iWestX = westShift
			iEastX = self.iW - eastShift
			iWidth = iEastX - iWestX

			if vSplitTertiary:
				# Do first in split
				if yPortionRoll:
					if yShiftRoll:
						northShift = int(splitYBuffer * self.iH)
						southShift = int(splitYBigger * self.iH)
					else:
						northShift = int(splitYSmaller * self.iH)
						southShift = int(splitYBuffer * self.iH)
				else:
					if yShiftRoll:
						northShift = int(splitYBuffer * self.iH)
						southShift = int(splitYSmaller * self.iH)
					else:
						northShift = int(splitYBigger * self.iH)
						southShift = int(splitYBuffer * self.iH)

				iSouthY = southShift
				iNorthY = self.iH - northShift
				iHeight = iNorthY - iSouthY

				print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
				self.generateContinentRegion(iTertiaryWater, iWidth, iHeight, iWestX, iSouthY, iTertiaryContinentsGrain, xExp)

				if (tinyIslandOverlap == 0):
					self.generateIslandRegion(2, 3, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

				# Second in split
				if yPortionRoll:
					if yShiftRoll:
						northShift = int(splitYSmaller * self.iH)
						southShift = int(splitYBuffer * self.iH)
					else:
						northShift = int(splitYBuffer * self.iH)
						southShift = int(splitYBigger * self.iH)
				else:
					if yShiftRoll:
						northShift = int(splitYBigger * self.iH)
						southShift = int(splitYBuffer * self.iH)
					else:
						northShift = int(splitYBuffer * self.iH)
						southShift = int(splitYSmaller * self.iH)

				iSouthY = southShift
				iNorthY = self.iH - northShift
				iHeight = iNorthY - iSouthY

				print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
				self.generateContinentRegion(iTertiaryWater, iWidth, iHeight, iWestX, iSouthY, iTertiaryContinentsGrain, xExp)

				if (tinyIslandOverlap == 0):
					self.generateIslandRegion(2, 3, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)
			else:
				# Only one tertiary region
				iSouthY = 0
				iNorthY = self.iH - 1
				iHeight = iNorthY - iSouthY + 1
				print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
				self.generateContinentRegion(iTertiaryWater, iWidth, iHeight, iWestX, iSouthY, iTertiaryContinentsGrain, xExp)

				if (tinyIslandOverlap == 0):
					self.generateIslandRegion(3, 4, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		# All regions have been processed. Plot Type generation completed.
		print "Done"
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
	NiTextOut("Setting Plot Types (Python Custom Continents) ...")
	fractal_world = BnSMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

def generateTerrainTypes():

	if (iOptionValue_Mirror == 1):
		# MIRRORIZE PLOTS
		gc = CyGlobalContext()
		map = CyMap()
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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

		for iX in range(iW / 2):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				rPlot = map.plot(reflect_x(iX), reflect_y(iY))
				pPlot.setPlotType(rPlot.getPlotType(), false, false)
		
		# Smooth any graphical glitches these changes may have produced.
		map.recalculateAreas()


	NiTextOut("Generating Terrain (Python Custom Continents) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes
	
def addBonusType(argsList):#Addded in 2.39 for Option Wonder Resource
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
			
	if (iOptionValue_WonderResources == 1):
		if (type_string in ('BONUS_MARBLE','BONUS_STONE')):
			return None # don't place any of this bonus at ALL
			
	CyPythonMgr().allowDefaultImpl()
	
def addLakes():
	if (iOptionValue_Mirror == 1):
		# MIRRORIZE TERRAIN
		gc = CyGlobalContext()
		map = CyMap()
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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

		for iX in range(iW / 2):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				rPlot = map.plot(reflect_x(iX), reflect_y(iY))
				pPlot.setTerrainType(rPlot.getTerrainType(), false, false)
		
		# MIRRORIZE RIVERS
		if userInputPlots == 0: # Reflection
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

		elif userInputPlots == 1: # Inversion
			reflect_x = lambda x: iW - iX - 1
			reflect_y = lambda y: iH - iY - 1
			reflect_z = lambda x: iW - iX - 2
			reflect_w = lambda y: iH - iY
			for iX in range(iW / 2):
				for iY in range(iH):
					pPlot = map.plot(iX, iY)
					pPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
					if iX != (iW / 2) - 1:
						pPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
					sPlot = map.plot(reflect_z(iX), reflect_y(iY))
					if iY > 0:
						rPlot = map.plot(reflect_x(iX), reflect_w(iY))
						if rPlot.isNOfRiver():
							if rPlot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
								rivDir = CardinalDirectionTypes.CARDINALDIRECTION_WEST
							else:
								rivDir = CardinalDirectionTypes.CARDINALDIRECTION_EAST
							pPlot.setNOfRiver(true, rivDir)
					if sPlot.isWOfRiver():
						if sPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
							rivDir = CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
						else:
							rivDir = CardinalDirectionTypes.CARDINALDIRECTION_NORTH
						pPlot.setWOfRiver(true, rivDir)

		elif userInputPlots == 2: # Copy
			reflect_x = lambda x: iX + (iW / 2)
			reflect_y = lambda y: iY
			for iX in range(iW / 2):
				for iY in range(iH):
					pPlot = map.plot(iX, iY)
					pPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
					pPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
					rPlot = map.plot(reflect_x(iX), reflect_y(iY))
					sPlot = map.plot(reflect_x(iX), reflect_y(iY))
					if iY > 0:
						rPlot = map.plot(reflect_x(iX), reflect_y(iY))
						if rPlot.isNOfRiver():
							rivDir = rPlot.getRiverWEDirection()
							if iX == (iW / 2) - 1 and rivDir == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
								rPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
								tPlot = map.plot(reflect_x(iX - 1), reflect_y(iY - 1))
								if tPlot.isWOfRiver():
									tPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
									uPlot = map.plot((iX + 1), (iY - 1))
									if uPlot.isWOfRiver():
										uPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
								rPlot.setPlotType(PlotTypes.PLOT_OCEAN, false, false)
							else:
								pPlot.setNOfRiver(true, rivDir)
					if sPlot.isWOfRiver():
						rivDir = sPlot.getRiverNSDirection()
						pPlot.setWOfRiver(true, rivDir)
			
		else: # userInputPlots == 3: Opposite
			reflect_x = lambda x: iX + (iW / 2)
			reflect_y = lambda y: iH - iY - 1
			reflect_w = lambda y: iH - iY
			for iX in range(iW / 2):
				for iY in range(iH):
					pPlot = map.plot(iX, iY)
					pPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
					pPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
					sPlot = map.plot(reflect_x(iX), reflect_y(iY))
					if iY > 0:
						rPlot = map.plot(reflect_x(iX), reflect_w(iY))
						if rPlot.isNOfRiver():
							rivDir = rPlot.getRiverWEDirection()
							if iX == (iW / 2) - 1 and rivDir == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
								rPlot.setNOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
								tPlot = map.plot(reflect_x(iX - 1), reflect_w(iY - 1))
								if tPlot.isWOfRiver():
									tPlot.setWOfRiver(false, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
								rPlot.setPlotType(PlotTypes.PLOT_OCEAN, false, false)
							else:
								pPlot.setNOfRiver(true, rivDir)
					if sPlot.isWOfRiver():
						if sPlot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
							rivDir = CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
						else:
							rivDir = CardinalDirectionTypes.CARDINALDIRECTION_NORTH
						pPlot.setWOfRiver(true, rivDir)

		# Smooth any graphical glitches these changes may have produced.
		map.recalculateAreas()

	# Now add the lakes.	
	return CyPythonMgr().allowDefaultImpl()	

def addFeatures():
	if (iOptionValue_Mirror == 1):
		# MIRRORIZE LAKES
		gc = CyGlobalContext()
		map = CyMap()
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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

		for iX in range(iW / 2):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				rPlot = map.plot(reflect_x(iX), reflect_y(iY))
				if pPlot.getPlotType() != rPlot.getPlotType():
					pPlot.setPlotType(rPlot.getPlotType(), false, false)

		# If one of the oceanic landmass types, remove all peaks along the coasts.
		#userInputLandmass = map.getCustomMapOption(2)
		userInputLandmass = 1
		global terrainRoll
		if userInputLandmass == 0 or (userInputLandmass == 5 and terrainRoll < 4): # "Lakes" terrain, leave all peaks intact.
			pass
		else: # Oceanic option.
			for plotIndex in range(iW * iH):
				pPlot = map.plotByIndex(plotIndex)
				if pPlot.isPeak() and pPlot.isCoastalLand():
					# If a peak is along the coast, change to hills and recalc.
					pPlot.setPlotType(PlotTypes.PLOT_HILLS, false, false)

		# Smooth any graphical glitches these changes may have produced.
		map.recalculateAreas()

	# Now add the features.
	NiTextOut("Adding Features (Python Custom Continents) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def addGoodies():
	if (iOptionValue_Mirror == 1):
		# MIRRORIZE FEATURES AND BONUSES
		gc = CyGlobalContext()
		map = CyMap()
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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

		for iX in range(iW / 2):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				rPlot = map.plot(reflect_x(iX), reflect_y(iY))
				pPlot.setFeatureType(rPlot.getFeatureType(), -1)
				pPlot.setBonusType(rPlot.getBonusType(-1))
	
	# Now add the goodies.

	return CyPythonMgr().allowDefaultImpl()

def afterGeneration():
	if (iOptionValue_Mirror == 1):
		# MIRRORIZE GOODIES
		gc = CyGlobalContext()
		map = CyMap()
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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

		for iX in range(iW / 2):
			for iY in range(iH):
				pPlot = map.plot(iX, iY)
				rPlot = map.plot(reflect_x(iX), reflect_y(iY))
				pPlot.setImprovementType(rPlot.getImprovementType())
	
	# All done!
	return None

def assignStartingPlots():

	if (iOptionValue_Mirror == 1):

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
				
				'''#2.39a start
				if isBTPon:
					if gc.getTeam(teamLoop).isEverAlive() and not gc.getTeam(teamLoop).isSpectator():
						iChooseTeam = dice.get(len(team_list), "Shuffling Regions - TBG PYTHON")
						shuffledTeams.append(team_list[iChooseTeam])
						del team_list[iChooseTeam]
				
				#2.39a end
				else:'''
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
		#userInputProximity = map.getCustomMapOption(1)
		userInputProximity = 0
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
		for plrCheckLoop in range(gc.getMAX_CIV_PLAYERS()):
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
				#userInputTerrain = CyMap().getCustomMapOption(2)
				userInputTerrain = 1
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
		#userInputPlots = map.getCustomMapOption(0)
		userInputPlots = 0
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
			#userInputTerrain = CyMap().getCustomMapOption(2)
			userInputTerrain = 1
			if userInputTerrain < 3 or (userInputTerrain == 5 and terrainRoll < 6):
				pPlot = CyMap().plot(x, y)
				areaID = pPlot.getArea()
				if areaID not in biggest_areas:
					return false

			#userInputPlots = CyMap().getCustomMapOption(0)
			userInputPlots = 0
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

	CyPythonMgr().allowDefaultImpl()
		
def findStartingPlot(argsList):
	
	if (iOptionValue_Mirror == 1):

		[playerID] = argsList
		global assignedPlayers
		global team_num
		thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
		teamID = team_num[thisTeamID]
		
		assignedPlayers[teamID] += 1
		
		
		#2.39b
		if iNumSpectators > 0:
			if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
			#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
				return -1			
		
		def isValid(playerID, x, y):
			global biggest_areas
			global terrainRoll
			#userInputTerrain = CyMap().getCustomMapOption(2)
			userInputTerrain = 1
			if userInputTerrain < 3 or (userInputTerrain == 5 and terrainRoll < 6):
				pPlot = CyMap().plot(x, y)
				areaID = pPlot.getArea()
				if areaID not in biggest_areas:
					return false

			map = CyMap()
			
			#### start 2.39a
			'''if isBTPon:
				iNumSpectators = CyGlobalContext().getGame().countCivPlayersEverSpectator()
				if iNumSpectators > 0:
					if playerID >= CyGlobalContext().getGame().countCivPlayersEverAlive():
					#Because always the last player that get -1,-1 for starting plot. Also, don't foget first player is [0], that's why there is an "equal"
						return -1				
				else:
					numTeams = CyGlobalContext().getGame().countCivTeamsEverAlive () ## this is a condition now
			else:
				numTeams = CyGlobalContext().getGame().countCivTeamsEverAlive () ## this is a condition now'''
			#### end 2.39a
			
			numTeams = CyGlobalContext().getGame().countCivTeamsEverAlive() ### 2.40 debugging
				
			if numTeams > 4 or numTeams < 2: # Put em anywhere, and let the normalizer sort em out.
				return true
			#userInputProximity = map.getCustomMapOption(1)
			userInputProximity = 0
			if userInputProximity == 2: # Start anywhere!
				return true
			global shuffle
			global shuffledTeams
			global team_num
			thisTeamID = CyGlobalContext().getPlayer(playerID).getTeam()
			teamID = team_num[thisTeamID]
			iW = map.getGridWidth()
			iH = map.getGridHeight()
			
			## 2.39 out - I copy TBG ###
			'''
			# Two Teams, Start Together
			if numTeams == 2 and userInputProximity == 0: # Two teams, Start Together
				if teamID == 0 and shuffle and x >= iW * 0.6:
					return true
				if teamID == 1 and not shuffle and x >= iW * 0.6:
					return true
				if teamID == 0 and not shuffle and x <= iW * 0.4:
					return true
				if teamID == 1 and shuffle and x <= iW * 0.4:
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
				if teamID == 0 and side and x >= iW * 0.6:
					return true
				if teamID == 1 and not side and x >= iW * 0.6:
					return true
				if teamID == 0 and not side and x <= iW * 0.4:
					return true
				if teamID == 1 and side and x <= iW * 0.4:
					return true
				return false

			# All conditions have failed? Wow. Is that even possible? :)
			return true'''
			
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
			
			##### end 2.39
			
			
		return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)	
	
	CyPythonMgr().allowDefaultImpl()
		
def startHumansOnSameTile():
	
	if isBTPon:
		if (iOptionValue_Lagoon > 0):
			if (iOptionValue_Lagoon  == 1):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,100,0,0,5)
			if (iOptionValue_Lagoon  == 2):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,0,5)				
			if (iOptionValue_Lagoon  == 3):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,100,5)		

	if iOptionValue_WonderResources == 2:#2.39
		gc = CyGlobalContext()
		map = CyMap()
		iW = map.getGridWidth()
		iH = map.getGridHeight()
	
		for iX in range(iW):
			for iY in range(iH):
				pPlot = CyMap().plot(iX,iY)
				if iX < iW / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"):
					pPlot.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_STONE"))
				if iX >= iW / 2 and pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_STONE"):
					pPlot.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_MARBLE"))
					
	if iOptionValue_Circumnavigation:#2.41
		if isBTPon:
			iOption = CyGlobalContext().getInfoTypeForString("GAMEOPTION_DISABLE_CIRCUMNAVIGATION")
			CyGlobalContext().getGame().setOption(iOption, True)
		else:
			CyGlobalContext().getGame().makeCircumnavigated()
								

	CyPythonMgr().allowDefaultImpl()

def MapCannotConstruct(argsList):#2.38n

	pCity = argsList[0]
	eBuilding = argsList[1]
	bContinue = argsList[2]
	bTestVisible = argsList[3]
	bIgnoreCost = argsList[4]

	if  eBuilding == CyGlobalContext().getInfoTypeForString("BUILDING_ORACLE") and (iOptionValue_WonderBan == 1 or iOptionValue_WonderBan == 3 or iOptionValue_WonderBan == 4):
		return True
	elif  eBuilding == CyGlobalContext().getInfoTypeForString("BUILDING_GREAT_LIGHTHOUSE") and (iOptionValue_WonderBan == 2 or iOptionValue_WonderBan == 3 or iOptionValue_WonderBan == 4):
		return True
	elif  eBuilding == CyGlobalContext().getInfoTypeForString("BUILDING_COLOSSUS") and (iOptionValue_WonderBan == 4):
		return True
	elif iOptionValue_WonderBan == 5 and isWorldWonderClass(CyGlobalContext().getBuildingInfo(eBuilding).getBuildingClassType()):
		return True
	else:
		return False
		
		
## This is the right way but the lands are too bad	

def normalizeAddRiver():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()
		

def normalizeRemovePeaks():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()

def normalizeAddLakes():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()

def normalizeRemoveBadFeatures():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()

def normalizeRemoveBadTerrain():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()

def normalizeAddFoodBonuses():### I code this Penny Logic
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()

def normalizeGoodTerrain():
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):
		return None
	else:
		return CyPythonMgr().allowDefaultImpl()
		
def normalizeAddExtras():
	
	if iOptionValue_Normalization >= 2:
		BTGnormalizeAddExtrasHills(3, iOptionValue_Mirror)
		BTGnormalizeAddExtrasFoodStart(iOptionValue_Normalization == 3,False,3,'BONUS_DEER',1, iOptionValue_Mirror)		
	
	if (iOptionValue_Normalization == 1 or iOptionValue_Normalization == 2):### I code this Penny Logic best
		return None
	else:
		CyPythonMgr().allowDefaultImpl()
		
''' 11 - BTG local/map Redclaration of MapGeneratorUtil functions for logic '''	
def BTGnormalizeAddExtrasHills(iMinHills, bMirrorLogic):

	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()		
			possiblePlots = []
			iHillCountPlayer = 0
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)

						if pPlot.isHills():
							iHillCountPlayer += 1
						
						elif not pPlot.isWater() and not pPlot.isImpassable() and pPlot.getBonusType(-1) == -1:
							if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
								possiblePlots.append(pPlot)	
			
			iMissingHills = iMinHills - iHillCountPlayer	
			if not bMirrorLogic or start_plot.getX() < CyMap().getGridWidth()/2 :#2.40
				if iMissingHills > 0:
					for i in range(iMissingHills):
						pChosenPlot = possiblePlots[CyGame().getSorenRandNum(len(possiblePlots), "where")]## This is for 1 plot
						pChosenPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)	
						possiblePlots.remove(pChosenPlot)
						
						if bMirrorLogic:#2.40
							pMirrorPlot = CyMap().plot(CyMap().getGridWidth() - pChosenPlot.getX() - 1,pChosenPlot.getY())
							pMirrorPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)							

def BTGnormalizeAddExtrasFoodStart(bForcePlacement,bAllowedOnHills,iThresholdFood,iBonusType,iForestForceType,bMirrorLogic):

	for i in range(CyGlobalContext().getMAX_CIV_PLAYERS()):
		if (CyGlobalContext().getPlayer(i).isEverAlive()):
			start_plot = CyGlobalContext().getPlayer(i).getStartingPlot()
			startx, starty = start_plot.getX(), start_plot.getY()	
	
			possiblePlots = []
			iFoodCount = 0
			
			for dx in range (-2,3):
				for dy in range (-2,3):
					#if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 3) and not (dx == 3 and dy == -2) and not (dx == 3 and dy == 3):
					if not (dx == -2 and dy == -2) and not (dx == -2 and dy == 2) and not (dx == 2 and dy == -2) and not (dx == 2 and dy == 2) and not (dx == 0 and dy == 0):
						pPlot = CyMap().plot(startx+dx,starty + dy)
						
						if not pPlot.isWater() and not pPlot.isImpassable() and pPlot.getBonusType(-1) == -1:
							if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
								if not pPlot.isHills() or bAllowedOnHills:
									possiblePlots.append(pPlot)	
									
						elif pPlot.getBonusType(-1) != -1:	
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_DEER") : iFoodCount += 1
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CLAM") : iFoodCount += 1
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CRAB") : iFoodCount += 1
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_FISH") : iFoodCount += 2
							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_CORN") : 
								iFoodCount += 2
								if pPlot.isRiver():
									iFoodCount += 1
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_WHEAT") : 
								iFoodCount += 2
								if pPlot.isRiver():
									iFoodCount += 1							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_PIG") : iFoodCount += 3
							
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_SHEEP") : 
								iFoodCount += 1
								if pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS") : 
									iFoodCount += 1
					
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_COW") : 
								iFoodCount += 1
								if pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS") : 
									iFoodCount += 1
									
							if pPlot.getBonusType(-1) == CyGlobalContext().getInfoTypeForString("BONUS_RICE") : 
								iFoodCount += 1
								if pPlot.isRiver():
									iFoodCount += 1
											
			if not bMirrorLogic or start_plot.getX() < CyMap().getGridWidth()/2 :#2.40
											
				#for pChosenPlot in possiblePlots: -- This is to test all the plots
				pChosenPlot = possiblePlots[CyGame().getSorenRandNum(len(possiblePlots), "where")]## This is for 1 plot
				if bForcePlacement or iThresholdFood > iFoodCount :
					pChosenPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iBonusType))
					if iForestForceType == 0:#Remove Forest
						pChosenPlot.setFeatureType(-1, -1)#Snow variation #Out because of oil
					if iForestForceType == 1:#Force Forest
						pChosenPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation #Out because of oil		
						
					if bMirrorLogic:#2.40
						pMirrorPlot = CyMap().plot(CyMap().getGridWidth() - pChosenPlot.getX() - 1,pChosenPlot.getY())
						pMirrorPlot.setBonusType(CyGlobalContext().getInfoTypeForString(iBonusType))
						pMirrorPlot.setTerrainType(pChosenPlot.getTerrainType(), False, False)
						if iForestForceType == 0:#Remove Forest
							pMirrorPlot.setFeatureType(-1, -1)#Snow variation #Out because of oil
						if iForestForceType == 1:#Force Forest
							pMirrorPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation #Out because of oil												