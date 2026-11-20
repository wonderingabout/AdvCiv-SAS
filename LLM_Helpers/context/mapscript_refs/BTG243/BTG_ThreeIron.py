# 2024 - Penny for BTG - Because we're too often 3 Players for an Ironman
#
from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
import random
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

listToBalanceNormal 		 = ["BONUS_IRON"]	
listToSmoothForce			 = ["BONUS_COPPER","BONUS_HORSE"]
listToBalanceStrategicOne	 = ["BONUS_LEAD","BONUS_NICKEL","BONUS_AMBER"]	#Forced
#listToBalanceStrategicTwo	 = ["BONUS_SAPPHIRES","BONUS_OBSIDIAN","BONUS_JADE","BONUS_DIAMONDS"]	#Unused
#listToBalanceStrategicThree  = ["BONUS_POTATO","BONUS_PEARLS"]	 Unused

'''0 -- Map Options --'''
'''0.0 -- BTG Description -- '''
def getDescription():
#	BugUtil.debug("Team_Battleground: getDescription")
	return "Beyond the Game map by Penny"

def getDescriptionTitle():
	return "The 3 players version of the Grid map providing 9 hubs in all circumstances"

def getDescriptionTitleTwo():
	return "The 3 players will always start in diagonal hubs (both diagonal configuration possible) so opponents will never be in adjacent hubs"

def getDescriptionMain():
	return "Resources are not balanced as per usual, they're very land type dependent and you won't be guaranteed any resource, except that you will have 3 irons"

def getDescriptionSecond():#Script tip : (on TOP)
	return "Make sure to scout very properly to know where tundra and desert tiles could be for future oil and resources placement"	
	
def getDescriptionThird():#Option : (at the bottom)"
	return "The option to include all new resources of BTG is by default on, so it's a good map for UUMadness"
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "3 players is ideal, but it works for 4P (mostly 2v2) and 6 or 9 players too"

def getDescriptionBalance():#Balance : (at the bottom)"
	return "You might not get a super key resources (horse, oil, aluminium), so do not hesitate to 'terminate' a game early and expand everywhere"		

'''0.1)     getNumHiddenCustomMapOptions() '''
def getNumHiddenCustomMapOptions():	return 0
'''0.2 getNumCustomMapOptions()'''
def getNumCustomMapOptions(): return 10

'''0.3)     getCustomMapOptionDefault()'''
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	4,
		1:	1,
		2:	4,
		3:	5,
		4:	0,
		5:	1,
		6:	0,
		7:	2,
		8:	0,
		9:	0
		}
	return option_defaults[iOption]

'''0.4)     isAdvancedMap()'''
def isAdvancedMap(): return True

'''0.5)     getCustomMapOptionName()'''
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Distance Cost",
		1:	"Map Size",
		2:	"TXT_KEY_MAP_SCRIPT_SPOKE_WIDTH",
		3:	"Mirrored Hubs",
		4:	"Resources",
		5:	"UUMadness",
		6:  "Forest",
		7:	"Starting Units",
		8:	"Notes",	
		9:	"Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
'''0.6)     getNumCustomMapOptionValues()'''	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	10,
		1:	10,
		2:	6,
		3:	6,
		4:	2,
		5:	3,
		6:	3,
		7:	3,
		8:	4,
		9:	1
		}
	return option_values[iOption]

'''0.7)     isRandomCustomMapOption()'''
def isRandomCustomMapOption(argsList): return False
	
'''0.8)     getCustomMapOptionDescAt()'''
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "20%",
			1: "40%",
			2: "60%",
			3: "80% - Suggested BTG ThreeIron Value",
			4: "100% - Normal BTS Value",
			5: "120%",
			6: "140%",
			7: "160%",
			8: "180%",
			9: "200%",
			},	
		1:	{
			0: "24x24 [Max 1 Iron]",
			1: "28x28 - Default value for Proxy 3 players game [Max 2 Iron]",
			2: "32x32",
			3: "36x36 - Recommended 12 spaces apart for large 3 players or 2v2",
			4: "40x40",
			5: "44x44",
			6: "48x48 - Recommended 16 spaces for 6 or 9 players",
			7: "52x52",
			8: "56x56",
			9: "60x60 - Recommended 20 spaces for 9 Players",
			},
		2:	{
			0: "None",
			1: "1 Plot Wide",
			2: "2 Plots Wide",
			3: "3 Plots Wide",
			4: "4 Plots Wide",
			5: "5 Plots Wide"			
			},			
		3:	{
			0: "No - All Hubs different",
			1: "Mix - Shape only (not position)",
			2: "Mix - Shape and position",
			3: "Yes - Mirrored [9 Hubs]",
			4: "Yes - Only Starting hubs [3 Hubs total][3 Players]",
			5: "Yes - By Columns [3x3 Columns][3 Players]"
			},
		4:	{
			0: "Smooth - 3 Irons [100%] Oil/Copper/Horse[Natural+80%] Lead/Nickel/Amber [100%] ",
			1: "Smooth as above - With [100%] Balanced for Oil, Copper, Horses"
			},
		5:	{
			0: "No - Only BTS Strategic Resources ",
			1: "Yes - Includes all other BTG Strategic Resources on top",
			2:  "Yes - Includes 2x amount of other BTG Strategic Resources"
			},
		6:	{
			0: "Slightly Light",
			1: "Slightly Heavy",
			2: "Palm Trees [BTG]"
			},	
		7:	{
			0: "Normal - Scattered",
			1: "Special - Same Tile",
			2: "Only Same tile if Hub is Mirrored"
			},			
		8:	{
			0: "Map Specifically designed for 3 Players",
			1: "Setup works for 4 players, 2V2, 5,6 or 9 players",
			2: "Size done with above option, not map size",			
			3: "Spectator works with 1 player in any slot"	
			},
		9:	{
			0: "Penny for BTG - Works for BTS, UUM Option and Palms would have no effect"
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
'''0.9)     - Get Map-Types'''
'''0.9.1)     isClimateMap()'''
def isClimateMap(): return False

'''0.9.2)     isSeaLevelMap()'''
def isSeaLevelMap(): return False	

'''1)     beforeInit()'''
def beforeInit():

	beforeInitOptionsValue()
	
	global isBTPon
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
	except:
		isBTPon = False	
		
	global iForceTundraPercent
	global iForceJunglePercent
	
	iForceTundraPercent = 3
	iForceJunglePercent = 5

def beforeInitOptionsValue():#2.36 this is handy to find in code

	global iOptionValue_DistanceModifier
	global iOptionValue_Size
	global iOptionValue_Mirror
	global iOptionValue_Spoke
	global iOptionValue_Madness
	global iOptionValue_Resource
	global iOptionValue_ForestDensity
	global iOptionValue_StartingUnit
	
	global iOptionValue_Temp_Oil
	global iOptionValue_Temp_Ele
	global iOptionValue_Temp_Precious

	iOptionValue_DistanceModifier = CyMap().getCustomMapOption(0)
	iOptionValue_Size = CyMap().getCustomMapOption(1)
	iOptionValue_Spoke = CyMap().getCustomMapOption(2)
	iOptionValue_Mirror = CyMap().getCustomMapOption(3)
	iOptionValue_Resource = CyMap().getCustomMapOption(4)
	iOptionValue_Madness = CyMap().getCustomMapOption(5)
	iOptionValue_ForestDensity = CyMap().getCustomMapOption(6)
	iOptionValue_StartingUnit = CyMap().getCustomMapOption(7)
	
	iOptionValue_Temp_Oil = True
	iOptionValue_Temp_Ele = True
	iOptionValue_Temp_Precious = True
	
	
	global iDimension
	global iDimensionFull
	global iDimensionRest
	
	iDimension = 6 + iOptionValue_Size
	iDimensionFull = iDimension * 4
	iDimensionRest = iDimensionFull % 3
	
'''2)     - Initialize Map'''
'''2.2)     getGridSize()'''
def getGridSize(argsList): return (iDimension,iDimension)	
	
'''2.3.1)   getTopLatitude()            # always use both'''
'''2.3.2)   getBottomLatitude()         # always use both'''

'''2.4.1)   getWrapX()                  # always use both'''
'''2.4.2)   getWrapY()                  # always use both'''	
def getWrapX(): return True
def getWrapY(): return True

'''3)     beforeGeneration()	'''
def beforeGeneration():
	global iNumRegions
	global regions_in_use
	global remaining_regions
	global remaining_regionsTwo#2.21z Cheezy	
	global iTemplateRoll#2.38 for Mirror
	
	global iPlayers
	global iPlayersCount
			
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	iPlayersCount = gc.getGame().countCivPlayersEverAlive()
	
	
	global iNumSpectators 
	if isBTPon:
		iNumSpectators = gc.getGame().countCivPlayersEverSpectator()
	else:
		iNumSpectators = 0		
	

	# Number of regions # Fixed for ThreeIron
	configs = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
	iNumRegions = configs[iPlayersCount]	
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	
	iNumTemplates = 2
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")	
	
	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		return None
		

	# Some regions may go unused. We need to track the ones that have been used.
	regions_in_use = []
	remaining_regions = []
	remaining_regionsTwo = []#2.21z Cheezey	
	for loopy in range(iNumRegions):
		remaining_regions.append(loopy)
		remaining_regionsTwo.append(loopy)#2.21z Cheezey		

	# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
	if iPlayers <= 3 or iPlayers == 5 :
		if iTemplateRoll == 1:
			templates =  {		 
					 9: {0: [0.000, 0.334, 0.000, 0.334],
						 1: [0.334, 0.667, 0.334, 0.667],
						 2: [0.667, 1.000, 0.667, 1.000],	
						 3: [0.000, 0.334, 0.667, 1.000],
						 4: [0.667, 1.000, 0.000, 0.334],
						 5: [0.000, 0.334, 0.334, 0.667],
						 6: [0.334, 0.667, 0.667, 1.000],
						 7: [0.334, 0.667, 0.000, 0.334],
						 8: [0.667, 1.000, 0.334, 0.667],},
				}			
		else:
			templates =  {		 
					 9: {0: [0.000, 0.334, 0.667, 1.000],
						 1: [0.334, 0.667, 0.334, 0.667],
						 2: [0.667, 1.000, 0.000, 0.334],	
						 3: [0.000, 0.334, 0.000, 0.334],
						 4: [0.667, 1.000, 0.667, 1.000],
						 5: [0.000, 0.334, 0.334, 0.667],
						 6: [0.334, 0.667, 0.667, 1.000],
						 7: [0.334, 0.667, 0.000, 0.334],
						 8: [0.667, 1.000, 0.334, 0.667],},
				}				
	elif iPlayers == 4:
		templates =  {		 
				 9: {0: [0.0, 0.334, 0.334, 0.667],
					 1: [0.667, 1.0, 0.334, 0.667],
					 2: [0.334, 0.667, 0.0, 0.334],	
					 3: [0.334, 0.667, 0.667, 1.0],
					 4: [0.334, 0.667, 0.334, 0.667],				 
					 5: [0.0, 0.334, 0.0, 0.334],
					 6: [0.667, 1.0, 0.0, 0.334], 
					 7: [0.0, 0.334, 0.667, 1.0],
					 8: [0.667, 1.0, 0.667, 1.0]},
			}
	else:#basically  for case of 6 players in line on 2 bands
		templates =  {		 
				 9: {0: [0.000, 0.334, 0.000, 0.334],
					 1: [0.334, 0.667, 0.000, 0.334],
					 2: [0.667, 1.000, 0.000, 0.334],	
					 3: [0.000, 0.334, 0.334, 0.667],
					 4: [0.334, 0.667, 0.334, 0.667],				 
					 5: [0.667, 1.000, 0.334, 0.667],
					 6: [0.000, 0.334, 0.667, 1.000], 
					 7: [0.334, 0.667, 0.667, 1.000],
					 8: [0.667, 1.000, 0.667, 1.000]},
			}			
	# End of template data.

	# List region_coords: [WestLon, EastLon, SouthLat, NorthLat]
	global region_coords
	region_coords = templates[iNumRegions]

'''4)     - Generate Map'''
'''4.1)     generatePlotTypes()'''
def generatePlotTypes():
	#iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	#I've already declared this

	# Check for valid number of players.
	if iPlayers > 0 and iPlayers < 19: pass
	else: # Error catching.
		fractal_world = FractalWorld()
		fractal_world.initFractal(polar = True)
		plotTypes = fractal_world.generatePlotTypes()
		return plotTypes

	fractal_world = GridMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

class GridMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def addLandPlot(self, i):
		if self.wholeworldPlotTypes[i] == PlotTypes.PLOT_OCEAN:
			if self.dice.get(5, "Hills on spokes - Grid PYTHON") == 0:
				self.wholeworldPlotTypes[i] = PlotTypes.PLOT_HILLS
			else:
				self.wholeworldPlotTypes[i] = PlotTypes.PLOT_LAND

	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		# iPlayers = self.gc.getGame().countCivPlayersEverAlive()
		# I Want this as a global definition
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		# Add the land (two fractals per region to ensure cohesion).
		global region_coords
		global regions_in_use
		global remaining_regions
        	global region_duplicated
        	global other_regions

        	region_duplicated = [0 for i in range(5)]

		for region_loop in range(len(remaining_regions)):
			[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[region_loop]
			iWestX = int(self.iW * fWestLon)
			iEastX = int(self.iW * fEastLon) - 1
			iSouthY = int(self.iH * fSouthLat)
			iNorthY = int(self.iH * fNorthLat) -1
			iWidth = iEastX - iWestX + 1
			iHeight = iNorthY - iSouthY + 1

			if region_duplicated[3] == 0 : region_duplicated = [region_loop, iWestX, iSouthY, iWidth, iHeight]
			elif (iWidth > region_duplicated[3]) and ((iWidth > region_duplicated[3]) < region_duplicated[3]) : region_duplicated = [region_loop, iWestX, iSouthY, iWidth, iHeight]
			
                region_roll = region_duplicated[0]
                thisRegion = remaining_regions[region_roll]
                regions_in_use.append(thisRegion)
                del remaining_regions[region_roll]

                # Region dimensions
                [fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
                iWestX = int(self.iW * fWestLon)
                iEastX = int(self.iW * fEastLon) - 1
                iSouthY = int(self.iH * fSouthLat)
                iNorthY = int(self.iH * fNorthLat) -1
                iWidth = iEastX - iWestX + 1
                iHeight = iNorthY - iSouthY + 1

                # Each landmass only takes up approximately 64% of the space in its region.
                # This space is further divided between land and water.
                # Choose a pattern for this region
                landPattern = self.dice.get(3, "Land Pattern - Grid PYTHON")
                if landPattern == 1: # Tall
                        regWestX = iWestX + int(iWidth * 0.18)
                        regSouthY = iSouthY
                        regWidth = int(iWidth * 0.64)
                        regHeight = iHeight
                elif landPattern == 2: # Wide
                        regWestX = iWestX
                        regSouthY = iSouthY + int(iHeight * 0.18)
                        regWidth = iWidth
                        regHeight = int(iHeight * 0.64)
                else: # landPattern == 0, Square
                        regWestX = iWestX + int(iWidth * 0.1)
                        regSouthY = iSouthY + int(iHeight * 0.1)
                        regWidth = int(iWidth * 0.8)
                        regHeight = int(iHeight * 0.8)

                self.generatePlotsInRegion(45 + sea,
                                           regWidth, regHeight,
                                           regWestX, regSouthY,
                                           1, 4,
                                           self.iRoundFlags, self.iTerrainFlags,
                                           6, 6,
                                           True, 3,
                                           -1, False,
                                           False
                                           )

                # Core fractal to increase cohesion
                coreWestX = regWestX + int(regWidth * 0.25)
                coreEastX = coreWestX + int(regWidth * 0.5)
                coreSouthY = regSouthY + int(regHeight * 0.25)
                coreNorthY = coreSouthY + int(regHeight * 0.5)
                coreWidth = coreEastX - coreWestX + 1
                coreHeight = coreNorthY - coreSouthY + 1

                self.generatePlotsInRegion(25,
                                           coreWidth, coreHeight,
                                           coreWestX, coreSouthY,
                                           1, 3,
                                           self.iHorzFlags, self.iTerrainFlags,
                                           5, 5,
                                           True, 3,
                                           -1, False,
                                           False
                                           )
										   
										   
		#2.21z - the 'Open part'
		if (iOptionValue_Mirror == 0):

			for region_loop in range(iNumRegions):#2.15
				# Choose an unused region
				region_roll = self.dice.get(len(remaining_regionsTwo), "Region Roll - Grid PYTHON")
				thisRegion = remaining_regionsTwo[region_roll]
				regions_in_use.append(thisRegion)
				del remaining_regionsTwo[region_roll]

				# Region dimensions
				[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * fWestLon)
				iEastX = int(self.iW * fEastLon) - 1
				iSouthY = int(self.iH * fSouthLat)
				iNorthY = int(self.iH * fNorthLat) -1
				iWidth = iEastX - iWestX + 1
				iHeight = iNorthY - iSouthY + 1

				# Each landmass only takes up approximately 64% of the space in its region.
				# This space is further divided between land and water.
				# Choose a pattern for this region
				landPattern = self.dice.get(3, "Land Pattern - Grid PYTHON")
				if landPattern == 1: # Tall
					regWestX = iWestX + int(iWidth * 0.18)
					regSouthY = iSouthY
					regWidth = int(iWidth * 0.64)
					regHeight = iHeight
				elif landPattern == 2: # Wide
					regWestX = iWestX
					regSouthY = iSouthY + int(iHeight * 0.18)
					regWidth = iWidth
					regHeight = int(iHeight * 0.64)
				else: # landPattern == 0, Square
					regWestX = iWestX + int(iWidth * 0.1)
					regSouthY = iSouthY + int(iHeight * 0.1)
					regWidth = int(iWidth * 0.8)
					regHeight = int(iHeight * 0.8)

				self.generatePlotsInRegion(45 + sea,
										   regWidth, regHeight,
										   regWestX, regSouthY,
										   1, 4,
										   self.iRoundFlags, self.iTerrainFlags,
										   6, 6,
										   True, 3,
										   -1, False,
										   False
										   )

				# Core fractal to increase cohesion
				coreWestX = regWestX + int(regWidth * 0.25)
				coreEastX = coreWestX + int(regWidth * 0.5)
				coreSouthY = regSouthY + int(regHeight * 0.25)
				coreNorthY = coreSouthY + int(regHeight * 0.5)
				coreWidth = coreEastX - coreWestX + 1
				coreHeight = coreNorthY - coreSouthY + 1

				self.generatePlotsInRegion(25,
										   coreWidth, coreHeight,
										   coreWestX, coreSouthY,
										   1, 3,
										   self.iHorzFlags, self.iTerrainFlags,
										   5, 5,
										   True, 3,
										   -1, False,
										   False
										   )		
		
		#2.21z - Back to common part										   

		# Generate spokes
		map = CyMap()
		spoke_width = iOptionValue_Spoke
		if spoke_width > 0:
		
			for regionLoop in range(len(regions_in_use)):
				
				#2.10o
				#if regionLoop >= 0:
				
				thisRegion = regions_in_use[regionLoop]
				# Region dimensions
				[iWestLon, iEastLon, iSouthLat, iNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * iWestLon)
				iEastX = int(self.iW * iEastLon) - 1
				iSouthY = int(self.iH * iSouthLat)
				iNorthY = int(self.iH * iNorthLat) -1
				iCenterX = int((iWestX + iEastX) / 2)
				iCenterY = int((iSouthY + iNorthY) / 2)

				for x in range(iWestX, iEastX+1):
					i = iCenterY*self.iW + x
					self.addLandPlot(i)
					if spoke_width > 1:
						self.addLandPlot(i + self.iW)
					if spoke_width > 2:
						self.addLandPlot(i - self.iW)
					if spoke_width > 3:#2.21z
						self.addLandPlot(i + self.iW + self.iW)
					if spoke_width > 4:#2.21z
						self.addLandPlot(i - self.iW - self.iW)						
		
				for y in range(iSouthY, iNorthY+1):
					i = y*self.iW + iCenterX
					self.addLandPlot(i)
					if spoke_width > 1:
						self.addLandPlot(i + 1)
					if spoke_width > 2:
						self.addLandPlot(i - 1)
					if spoke_width > 3:#2.21z
						self.addLandPlot(i + 2)
					if spoke_width > 4:#2.21z
						self.addLandPlot(i - 2)

		# Add the land (two fractals per region to ensure cohesion).
		if (iOptionValue_Mirror >= 1):

			#duplicate land for other used regions
			other_regions = []
			#for region_loop in range(iPlayers - 1):#2.10 Out
				# Choose an unused region
				#region_roll = self.dice.get(len(remaining_regions), "Region Roll - Grid PYTHON")
				#thisRegion = remaining_regions[region_roll]
				#regions_in_use.append(thisRegion)
				#del remaining_regions[region_roll]
				
			for region_loop in range(iNumRegions):
				#region_roll = self.dice.get(len(remaining_regions), "Region Roll - Grid PYTHON")
				thisRegion = region_loop
				regions_in_use.append(thisRegion)
				#del remaining_regions[region_roll]
				

				# Region dimensions
				[fWestLon, fEastLon, fSouthLat, fNorthLat] = region_coords[thisRegion]
				iWestX = int(self.iW * fWestLon)
				iEastX = int(self.iW * fEastLon) - 1
				iSouthY = int(self.iH * fSouthLat)
				iNorthY = int(self.iH * fNorthLat) -1
				iWidth = iEastX - iWestX + 1
				iHeight = iNorthY - iSouthY + 1

				other_regions.append([thisRegion, iWestX, iSouthY, iWidth, iHeight])
				iD, iWestXD, iSouthYD, iWidthD, iHeightD = region_duplicated

				for x in range(iWidth):
					wholeworldX = x + iWestX
					wholeworldXD = x + iWestXD
					for y in range(iHeight):
						wholeworldY = y + iSouthY
						iWorld = wholeworldY*self.iW + wholeworldX
						wholeworldYD = y + iSouthYD
						iWorldD = wholeworldYD*self.iW + wholeworldXD
						self.wholeworldPlotTypes[iWorld] = self.wholeworldPlotTypes[iWorldD]

		return self.wholeworldPlotTypes

'''4.2)     generateTerrainTypes()		'''
def generateTerrainTypes():
	terraingen = TerrainGenerator()
	#### Those where the values of Cross ###
	'''terraingen.__init__(iDesertPercent=8, iPlainsPercent=25,
		fSnowLatitude=2.0, fTundraLatitude=2.0, fGrassLatitude=0.0, 
		fDesertBottomLatitude=0.0, fDesertTopLatitude=2.0)
	terrainTypes = terraingen.generateTerrain()'''
	terraingen.__init__(iDesertPercent=8, iPlainsPercent=30,
		fSnowLatitude=2.0, fTundraLatitude=2.0, fGrassLatitude=0.0, 
		fDesertBottomLatitude=0.0, fDesertTopLatitude=2.0)
	terrainTypes = terraingen.generateTerrain()

	# Eliminate snow and tundra completely (they still get placed sometimes at extreme latitudes)
	for i in range(len(terrainTypes)):
		if (terrainTypes[i] == terraingen.terrainIce) or (terrainTypes[i] == terraingen.terrainTundra):
			terrainTypes[i] = terraingen.terrainPlains

	return terrainTypes

'''4.3)     addRivers()'''
'''4.4)     addLakes()'''
'''4.5)     addFeatures()'''
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

	if (iOptionValue_ForestDensity == 0):
		featuregen.__init__(iJunglePercent=3, iForestPercent=68,
			jungle_grain=5, forest_grain=6)#, iIcePercent=0)
	elif (iOptionValue_ForestDensity == 1):
		featuregen.__init__(iJunglePercent=3, iForestPercent=55,
			jungle_grain=5, forest_grain=6)#, iIcePercent=0)			
	elif (iOptionValue_ForestDensity == 2):
		featuregen.__init__(iJunglePercent=3, iForestPercent=60,
			jungle_grain=5, forest_grain=6)#, iIcePercent=0)

	featuregen.addFeatures()
	
	doFixTerrainBeforeBonus()
	
	## 2.10 do it after the general calc otherwise doesn't work
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isWater():
			pPlot.setFeatureType(-1, -1)# -1 is nothing
	#2.10 end
			
	
	return 0

def doFixTerrainBeforeBonus():### Used for ThreeIron Rare #####
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()				
	for iX in range(iW):
		for iY in range(iH):
			pPlot = CyMap().plot(iX, iY)
			if pPlot.getBonusType(-1) == -1 and pPlot.getFeatureType() == -1 and not pPlot.isWater() and not pPlot.isImpassable():
			
				if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"):
					iRandomTundra = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeTundra")
					if iRandomTundra <= iForceTundraPercent:
						pPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"), True, True)
						#if not pPlot.isHills(): # No because then no Silver
							#pPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_FOREST"), 2)#Snow variation #Out because of oil
							
					if not pPlot.getTerrainType() == CyGlobalContext().getInfoTypeForString("TERRAIN_TUNDRA"):
						iRandomJungle = CyGlobalContext().getGame().getMapRandNum(100,"iProbaBeTundra")
						if iRandomJungle <= iForceJunglePercent:					
							pPlot.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"), True, True)					
							pPlot.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_JUNGLE"), -1)#Snow variation #Out because of oil
					

'''4.6)     addBonuses()	''' ## This is called multiple times, don't put other stuff here###
def addBonusType(argsList): ### Three Iron very rare setup - all the resources are placed automatically, only Iron is cleaned

	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	if (type_string in listToBalanceNormal):
			return None # don't place any of this bonus randomly
			
	if (type_string in listToSmoothForce and iOptionValue_Resource == 1):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

'''4.6.1)     isBonusIgnoreLatitude()*'''
def isBonusIgnoreLatitude():
	return True
'''4.7)     addGoodies()'''

'''5)     afterGeneration()'''

'''6)     - Select Starting-Plots'''
'''6.1)     minStartingDistanceModifier()'''
'''6.2)     assignStartingPlots()'''
def assignStartingPlots():

	# Custom start plot finder
	global iNumRegions
	global region_coords
	global regions_in_use
        global region_duplicated#2.15
        global other_regions#2.15
	global shuffledPlayers
		
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	#iPlayers = gc.getGame().countCivPlayersEverAlive()
	#I've already declared this
	
	# Error catching.
	if iPlayers < 1 or iPlayers > 18:
		CyPythonMgr().allowDefaultImpl()
		return

	# Obtain the minimum crow-flies distance figures [minX, minY] for this map size and number of players.
	minimums = {2: [0.15, 0.3],
				3: [0.15, 0.17], #added penny
				4: [0.15, 0.15],
				5: [0.125, 0.16], #added penny
	            6: [0.1, 0.15],
				7: [0.08, 0.15], #added penny
	            8: [0.07, 0.15],
	            9: [0.1, 0.1],
				10: [0.09, 0.1], #added penny
				11: [0.08, 0.1], #added penny
	            12: [0.07, 0.1],
	            15: [0.06, 0.1],
	            16: [0.07, 0.07],
	            18: [0.05, 0.1]}
	[minLon, minLat] = minimums[iNumRegions]
	minX = max(3, int(minLon * iW))
	minY = max(3, int(minLat * iH))

	# region_data: [WestX, EastX, SouthY, NorthY, 
	# numLandPlotsinRegion, numCoastalPlotsinRegion,
	# numOceanPlotsinRegion, iRegionNetYield, 
	# iNumLandAreas, iNumPlotsinRegion]
	global region_data
	region_data = {}
	region_best_areas = {}
	region_yields = []
	sorting_regions = []
	for regionLoop in range(len(regions_in_use)):
		thisRegion = regions_in_use[regionLoop]
		# Region dimensions
		[iWestLon, iEastLon, iSouthLat, iNorthLat] = region_coords[thisRegion]
		iWestX = int(iW * iWestLon)
		iEastX = int(iW * iEastLon) - 1
		iSouthY = int(iH * iSouthLat)
		iNorthY = int(iH * iNorthLat) -1
		# Plot and Area info.
		iNumLandPlots = 0
		iNumCoastalPlots = 0
		iNumOceanPlots = 0
		iRegionNetYield = 0
		iNumLandAreas = 0
		iNumPlotsinRegion = 0
		land_areas = []
		land_area_plots = {}
		land_area_yield = {}
		# Cycle through all plots in the region.
		for x in range(iWestX, iEastX + 1):
			for y in range(iSouthY, iNorthY + 1):
				iNumPlotsinRegion += 1
				i = y * iW + x
				pPlot = map.plot(x, y)
				if pPlot.getBonusType(-1) != -1: # Count any bonus resource as added value
					iRegionNetYield += 2
				if pPlot.isWater(): # Water plot
					iFertileCheck = pPlot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM)
					if iFertileCheck > 1: # If the plot has extra food, count it.
						iRegionNetYield += (2 * (iFertileCheck - 1))
					if pPlot.isAdjacentToLand(): # Coastal plot
						if pPlot.isFreshWater:
							iNumCoastalPlots += 1
							iRegionNetYield += 2
						else:
							iNumCoastalPlots += 1
							iRegionNetYield += 1
					else:
						iNumOceanPlots += 1
				else: # Land plot
					iNumLandPlots += 1
					iArea = pPlot.getArea()
					iPlotYield = pPlot.calculateTotalBestNatureYield(TeamTypes.NO_TEAM)
					iFertileCheck = pPlot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM)
					if iFertileCheck > 1: # If the plot has extra food, count the extra as double value!
						iPlotYield += (iFertileCheck - 1)
					iRegionNetYield += iPlotYield
					if pPlot.isHills(): iRegionNetYield += 1 # Add a bonus point for Hills plots.
					if not iArea in land_areas: # This plot is the first detected in its AreaID.
						iNumLandAreas += 1
						land_areas.append(iArea)
						land_area_plots[iArea] = 1
						land_area_yield[iArea] = iPlotYield
					else: # This AreaID already known.
						land_area_plots[iArea] += 1
						land_area_yield[iArea] += iPlotYield
		# Sort areas, achieving a list of AreaIDs with best areas first.
		area_yields = land_area_yield.values()
		area_yields.sort()
		area_yields.reverse()
		best_areas = []
		for areaTestLoop in range(iNumLandAreas):
			for landLoop in range(len(land_areas)):
				if area_yields[areaTestLoop] == land_area_yield[land_areas[landLoop]]:
					best_areas.append(land_areas[landLoop])
					del land_areas[landLoop]
					break
		# Store infos to regional lists.
		region_data[thisRegion] = [iWestX, iEastX, iSouthY, iNorthY, 
								   iNumLandPlots, iNumCoastalPlots,
								   iNumOceanPlots, iRegionNetYield,
								   iNumLandAreas, iNumPlotsinRegion]
		region_best_areas[thisRegion] = best_areas
		region_yields.append(iRegionNetYield)
		sorting_regions.append(iRegionNetYield)
		
	# Now sort the regions
	best_regions = []
	region_numbers = regions_in_use
	sorting_regions.sort()
	sorting_regions.reverse()
	for regionTestLoop in range(iNumRegions):
		for yieldLoop in range(len(region_numbers)):
			if sorting_regions[regionTestLoop] == region_yields[yieldLoop]:
				best_regions.append(region_numbers[yieldLoop])
				del region_numbers[yieldLoop]
				del region_yields[yieldLoop]
				break
		
	# Need to discard the worst regions and then reverse the region order.
	# Of the regions that will be used, the worst will be assigned first.
	best_regions.reverse()

	# Obtain player numbers. (Account for possibility of Open slots!)
	player_list = []
	for plrCheckLoop in range(gc.getMAX_CIV_PLAYERS()):#2.35 when you reduce to 12 players... cannot hardcode this
		#2.22 Protecting for BTS
		if isBTPon:
			if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive() and not CyGlobalContext().getPlayer(plrCheckLoop).isSpectator():
				player_list.append(plrCheckLoop)
		else:
			if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
				player_list.append(plrCheckLoop)

	# Shuffle start points so that players are assigned regions at random.
	shuffledPlayers = []
	for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Regions - Grid PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]

	# Now assign the start plots!
	plot_assignments = {}
	min_dist = []
	
	dX = 0
	dY = 0
	
	if (iOptionValue_Mirror == 1 or iOptionValue_Mirror == 0):#2.21z
	
		# Loop through players/regions.
		for assignLoop in range(iPlayers):
		# for assignLoop in range(iNumRegions):
			#---- Below 2 lines normal code, full shuffle ----#
			#playerID = shuffledPlayers[assignLoop]#2.10test
			#reg = best_regions[assignLoop]
			
			#2.10 I need global declare teams -- Akira
			iNumTeams = gc.getGame().countCivTeamsEverAlive()
			iTeam = gc.getPlayer(assignLoop).getTeam()
				
			### ThreeIron Simplified cases of Cross ###
			if iNumTeams == iPlayers:
				playerID = shuffledPlayers[assignLoop]
				reg = assignLoop	

			elif iNumTeams == 2 and iNumSpectators > 0:	
				#2.18 -- It wasn't working with Spectator, I kinda force the scenario for when spectator watches 2 teams
				playerID = shuffledPlayers[assignLoop]
				reg = assignLoop			
				
			else:
				playerID = assignLoop
				reg = assignLoop
					
			[wX, eX, sY, nY] = region_data[reg][0:4]
			# Only consider the inner part of the region
			iWidth = eX - wX + 1
			iHeight = nY - sY + 1
			
			westX = wX + int(iWidth * 0.2)
			eastX = eX - int(iWidth * 0.2)
			southY = sY + int(iHeight * 0.2)
			northY = nY - int(iHeight * 0.2)

			if dX == 0 :
			 
				iNumAreas = region_data[reg][8]
				area_list = region_best_areas[reg]
				# Print Data for debugging
				# Error Handling (if valid start plot not found, reduce MinDistance)
				while (true):
					iBestValue = 0
					pBestPlot = None
					# Loop through best areas in this region
					for areaLoop in range(iNumAreas):
						areaID = area_list[areaLoop]
						player = gc.getPlayer(playerID)
						player.AI_updateFoundValues(True)
						iRange = player.startingPlotRange()
						iPass = 0
						validFn = None
						# Loop through all plots in the region.
						for iX in range(westX, eastX + 1):
							for iY in range(southY, northY + 1):
								pPlot = map.plot(iX, iY)
								if pPlot.isWater(): continue
								# if not pPlot.isCoastalLand(): continue
								if areaID != pPlot.getArea(): continue
								if validFn != None and not validFn(playerID, iX, iY): continue
								val = pPlot.getFoundValue(playerID)
								if pPlot.isFreshWater:
									val += 1000
								if val > iBestValue:
									valid = True
									for invalid in min_dist:
										[invalidX, invalidY] = invalid
										if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
											valid = False
											break
									if valid:
										for iI in range(gc.getMAX_CIV_PLAYERS()):
											if (gc.getPlayer(iI).isAlive()):
												if (iI != playerID):
													if gc.getPlayer(iI).startingPlotWithinRange(pPlot, playerID, iRange, iPass):
														valid = False
														break
									if valid:
										iBestValue = val
										pBestPlot = pPlot

						if pBestPlot != None:
							min_dist.append([pBestPlot.getX(), pBestPlot.getY()])
							sPlot = map.plot(pBestPlot.getX(), pBestPlot.getY())
							plrID = gc.getPlayer(playerID)
							plrID.setStartingPlot(sPlot, true)
							break # Valid start found, stop checking areas and plots.
						else: pass # This area too close to somebody, try the next area.
					
					# Check to see if a valid start was found in ANY areaID.
					if pBestPlot == None:
						print "player", playerID, "pass", iPass, "failed"
						iPass += 1
						if iPass <= max(player.startingPlotRange() + eastX - westX, player.startingPlotRange() + northY - southY):
							continue
						else: # A region has failed to produce any valid starts!
							bSuccessFlag = False
							print "---"
							print "A region has failed"
							print "---"
							# Regional start plot assignment has failed. Reverting to default.
							CyPythonMgr().allowDefaultImpl()
							return
					else: break # This player has been assigned a start plot.
				
		# Successfully assigned start plots, continue back to C++
		return None
	
	elif (iOptionValue_Mirror >= 2):	
	
		# Loop through players/regions.
		dX = 0
		dY = 0

		if region_duplicated[0] in best_regions :
					tpR = [region_duplicated[0]]
					for item in best_regions :
							if not item in tpR : tpR.append(item)
					best_regions = tpR
		else :
			print "you missed something there O.o"

		for assignLoop in range(iPlayers):# -Penny ; Not necessary for condition
		# for assignLoop in range(iNumRegions):
			#---- Below 2 lines normal code, full shuffle ----#
			#playerID = shuffledPlayers[assignLoop]#2.10test
			#reg = best_regions[assignLoop]
			
			#2.10 I need global declare teams -- Akira
			iNumTeams = gc.getGame().countCivTeamsEverAlive()
			iTeam = gc.getPlayer(assignLoop).getTeam()
					
			### ThreeIron Simplified cases of Cross ###
			if iNumTeams == iPlayers:
				playerID = shuffledPlayers[assignLoop]
				reg = assignLoop	

			elif iNumTeams == 2 and iNumSpectators > 0:	
				#2.18 -- It wasn't working with Spectator, I kinda force the scenario for when spectator watches 2 teams
				playerID = shuffledPlayers[assignLoop]
				reg = assignLoop			
				
			else:
				playerID = assignLoop
				reg = assignLoop
					
			[wX, eX, sY, nY] = region_data[reg][0:4]
			# Only consider the inner part of the region
			iWidth = eX - wX + 1
			iHeight = nY - sY + 1
			
			
			#### 2.38 --- In this config I need to force the start position quite central
			if iOptionValue_Mirror == 4:
				westX = wX + int(iWidth * 0.40)
				eastX = eX - int(iWidth * 0.40)
				southY = sY + int(iHeight * 0.40)
				northY = nY - int(iHeight * 0.40)			
			#### End new case
			else:
				westX = wX + int(iWidth * 0.2)
				eastX = eX - int(iWidth * 0.2)
				southY = sY + int(iHeight * 0.2)
				northY = nY - int(iHeight * 0.2)

			if dX == 0 :
							 
				iNumAreas = region_data[reg][8]
				area_list = region_best_areas[reg]
				# Print Data for debugging
				# Error Handling (if valid start plot not found, reduce MinDistance)
				while (true):
					iBestValue = 0
					pBestPlot = None
					# Loop through best areas in this region
					for areaLoop in range(iNumAreas):
						areaID = area_list[areaLoop]
						player = gc.getPlayer(playerID)
						player.AI_updateFoundValues(True)
						iRange = player.startingPlotRange()
						iPass = 0
						validFn = None
						# Loop through all plots in the region.
						for iX in range(westX, eastX + 1):
							for iY in range(southY, northY + 1):
								pPlot = map.plot(iX, iY)
								if pPlot.isWater(): continue
								# if not pPlot.isCoastalLand(): continue
								if areaID != pPlot.getArea(): continue
								if validFn != None and not validFn(playerID, iX, iY): continue
								val = pPlot.getFoundValue(playerID)
								if pPlot.isFreshWater:
									val += 1000
								if val > iBestValue:
									valid = True
									for invalid in min_dist:
										[invalidX, invalidY] = invalid
										if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
											valid = False
											break
									if valid:
										for iI in range(gc.getMAX_CIV_PLAYERS()):
											if (gc.getPlayer(iI).isAlive()):
												if (iI != playerID):
													if gc.getPlayer(iI).startingPlotWithinRange(pPlot, playerID, iRange, iPass):
														valid = False
														break
									if valid:
										iBestValue = val
										pBestPlot = pPlot

						if pBestPlot != None:
							min_dist.append([pBestPlot.getX(), pBestPlot.getY()])
							sPlot = map.plot(pBestPlot.getX(), pBestPlot.getY())
							plrID = gc.getPlayer(playerID)
							plrID.setStartingPlot(sPlot, true)
							dX = pBestPlot.getX() - wX
							dY = pBestPlot.getY() - sY
							break # Valid start found, stop checking areas and plots.
						else: pass # This area too close to somebody, try the next area.
					
					# Check to see if a valid start was found in ANY areaID.
					if pBestPlot == None:
							print "player", playerID, "pass", iPass, "failed"
							iPass += 1
							if iPass <= max(player.startingPlotRange() + eastX - westX, player.startingPlotRange() + northY - southY):
								continue
							else: # A region has failed to produce any valid starts!
								bSuccessFlag = False
								print "---"
								print "A region has failed"
								print "---"
								# Regional start plot assignment has failed. Reverting to default.
								CyPythonMgr().allowDefaultImpl()
								return
					else: break # This player has been assigned a start plot.
			
			else :
				sPlot = map.plot(wX + dX, sY + dY)
				plrID = gc.getPlayer(playerID)
				plrID.setStartingPlot(sPlot, true)
				
		# Successfully assigned start plots, continue back to C++'''
		return None
	
'''7)     - Normalize Starting-Plots'''
'''7.1)     normalizeStartingPlotLocations()+'''
def minStartingDistanceModifier():
	return 20

'''7.2)     normalizeAddRiver()'''
'''7.3)     normalizeRemovePeaks()'''
def normalizeRemovePeaks():
	return None

'''7.4)     normalizeAddLakes()'''
'''7.5)     normalizeRemoveBadFeatures()+'''
'''7.6)     normalizeRemoveBadTerrain()+'''
'''7.7)     normalizeAddFoodBonuses()+'''
'''7.7.1)     isBonusIgnoreLatitude()*'''
'''7.8)     normalizeGoodTerrain()+'''
'''7.9)     normalizeAddExtras()'''
def normalizeAddExtras():

	#2.39 Addition for Closeness
	iClosenessAdjustment = 0
	if iOptionValue_Size == 1 or iOptionValue_Size == 0 :
		iClosenessAdjustment += 1
		#Below is too much
		#if iOptionValue_Mirror == 3 or iOptionValue_Mirror == 5:## it's small END we doing the full mirror thing by column
		#	iClosenessAdjustment += 1
		
		
	BTPnormalizeAddExtrasSpecific(["BONUS_ALUMINIUM"],5,0,80)
	BTPnormalizeAddExtrasSpecific(["BONUS_ALUMINIUM"],12,0,80)

	# 3 Irons - I space them out
	BTPnormalizeAddExtrasSpecific(["BONUS_IRON"],4-iClosenessAdjustment,0,100)

	# I write the other way arond to include condition on full mirror, it would suck too bad to have a game without those
	if iOptionValue_Resource <> 0:#Forced
		BTPnormalizeAddExtrasSpecific(["BONUS_HORSE"],5-iClosenessAdjustment,0,100)
		BTPnormalizeAddExtrasSpecific(["BONUS_COPPER"],5-iClosenessAdjustment,0,100)	
		BTPnormalizeAddExtrasSpecific(["BONUS_OIL"],5,0,100)
	
	#Smoothen
	else: #iOptionValue_Resource == 0:
		BTPnormalizeAddExtrasSpecific(["BONUS_HORSE"],6,0,80)
		BTPnormalizeAddExtrasSpecific(["BONUS_COPPER"],6,0,80)
		BTPnormalizeAddExtrasSpecific(["BONUS_OIL"],7,0,80)
		
	# 3 Irons - I space them out
	if iClosenessAdjustment == 0 :
		BTPnormalizeAddExtrasSpecific(["BONUS_IRON"],5,0,100)

	if isBTPon:
	
		#########
		BTPnormalizeAddExtrasSpecific(listToBalanceStrategicOne,8,0,100)

		########
	
		minX = 0
		maxX = CyMap().getGridWidth()
		minY = 0
		maxY = CyMap().getGridHeight()
		
		if iOptionValue_Madness == 2: ### Big enough for full 6 or 9 Plaayers
			iRepeat = 2
		else:
			iRepeat = 1		
			
			
		#Water oil as well
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"), 2,2,3)			
		## Rest
		
		
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),iRepeat,0,2)
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),iRepeat,0,2)
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_JADE"),iRepeat,0,2)	
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_DIAMONDS"),iRepeat,0,2)	
		
		CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SULPHUR"),iRepeat,iRepeat,3)	
				
		if iOptionValue_Madness == 1 or iOptionValue_Madness == 2:##Extra for Madness		

			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_OLIVES"),2 * iRepeat,2 * iRepeat,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_SALT"),2 * iRepeat,2 * iRepeat,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_TEA"),2 * iRepeat,2 * iRepeat,-1)	

			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,False,CyGlobalContext().getInfoTypeForString("BONUS_POTATO"),3 * iRepeat,3 * iRepeat,1)
			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(minX,maxX,minY,maxY,True,CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"), 3 * iRepeat,3 * iRepeat,-1)
			
	# 3 Irons - I space them out
	if iOptionValue_Size != 0 :
		BTPnormalizeAddExtrasSpecific(["BONUS_IRON"],5-iClosenessAdjustment,0,100)	

	# 2.40 clean for non-round amount of tiles:
	BTGnormalizeAddExtrasHills(3)
		
	# 2.40 clean for non-round amount of tiles
	if iDimensionRest != 0:
		for x in range(CyMap().getGridWidth()):
			if iDimensionRest == 2:
				y = CyMap().getGridHeight() - 2
				
				p = CyMap().plot(x,y)	
				pLowerPlot = CyMap().plot(x,y-1)
				pHigherPlot = CyMap().plot(x,0)
				if not pLowerPlot.isWater() and not pHigherPlot.isWater() and p.isWater() :
					#p.setTerrainType(pLowerPlot.getTerrainType(), True, True)
					p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)
				
		
			y = CyMap().getGridHeight() - 1#Everycases where there is a rest
			p = CyMap().plot(x,y)	
			pLowerPlot = CyMap().plot(x,y-1)
			pHigherPlot = CyMap().plot(x,0)
			if not pLowerPlot.isWater() and not pHigherPlot.isWater() and p.isWater():
				#p.setTerrainType(pLowerPlot.getTerrainType(), True, True)
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"), True, True)	
				
		if iDimensionRest == 1 and iOptionValue_Mirror == 5:
			for y in range(CyMap().getGridHeight()):
				x = CyMap().getGridWidth() - 1
				pPlot = CyMap().plot(x,y)					
				if pPlot.getBonusType(-1) != -1:
					#pPlot.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_MUSIC"))
					pPlot.setBonusType(-1)				
			
				
	if (iOptionValue_Mirror == 3):
		mirrorizeMap()
	if (iOptionValue_Mirror == 4):
		mirrorizeMapThreeIron(False)
	if (iOptionValue_Mirror == 5):
		mirrorizeMapThreeIron(True)					

	return None
	#CyPythonMgr().allowDefaultImpl()#2.38 - I want the peak out for Inca Iron, and the coastal start is just not fun otherwise ### It doesn't work well with the mirror thing, out again
	

'''7.9.1)     isBonusIgnoreLatitude()*'''

'''8 )    startHumansOnSameTile()'''

def startHumansOnSameTile():

	#Just the thing I call at the end #2.42e Push a special rate of tech
	if isBTPon:
		CyGlobalContext().getGame().setMapSpecialDistanceModifier((iOptionValue_DistanceModifier +1) * 20)	


	if isBTPon:
		if (iOptionValue_ForestDensity == 2):
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)

	if iOptionValue_StartingUnit == 1 or (iOptionValue_StartingUnit == 2 and iOptionValue_Mirror >= 3) :
		return True
	else:
		return False

	
''' 9) Map Depended local logic for Food and Bonus placement'''				
''' 10 BTG Special Logic '''

def mirrorizeMapThreeIron(bFullColumn):
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	
	iBlockSize = iW / 3
	iBlockRemainder = iW % 3
	
	iShift = 0
	iWidthCopy = iBlockSize
	if bFullColumn :
		iHeightCopy = iH
	else:

		iHeightCopy = iBlockSize # if normal shape, starts 0 goes to 10 tile high
		if not iTemplateRoll == 1:
			iShift = iH - iBlockSize # Starts tile 20, for 
	

	for iX in range(iWidthCopy):
		#for iY in range(iBlockSize):#2.39 This was bugged
		for iY in range(iHeightCopy):
		
			if iTemplateRoll == 1: #Normal layout
				p1Plot = map.plot(iX, iY)
				p2Plot = map.plot(iX + iBlockSize, iY + iBlockSize)
				p3Plot = map.plot(iX + iBlockSize * 2, iY + iBlockSize * 2)
			else:
				p1Plot = map.plot(iX, iY + iShift)
				p2Plot = map.plot(iX + iBlockSize, iY + iShift - iBlockSize)
				p3Plot = map.plot(iX + iBlockSize * 2, iY + iShift - iBlockSize * 2)				
			
			p2Plot.setPlotType(p1Plot.getPlotType(), True, True)
			p2Plot.setTerrainType(p1Plot.getTerrainType(), True, True)
			p2Plot.setBonusType(p1Plot.getBonusType(-1))	
			p2Plot.setFeatureType(p1Plot.getFeatureType(), -1)
			p2Plot.setImprovementType(p1Plot.getImprovementType())
			
			p3Plot.setPlotType(p1Plot.getPlotType(), True, True)
			p3Plot.setTerrainType(p1Plot.getTerrainType(), True, True)
			p3Plot.setBonusType(p1Plot.getBonusType(-1))	
			p3Plot.setFeatureType(p1Plot.getFeatureType(), -1)
			p3Plot.setImprovementType(p1Plot.getImprovementType())	
	

			if p1Plot.isNOfRiver():		
				p2Plot.setNOfRiver(True, p1Plot.getRiverWEDirection())						
				p3Plot.setNOfRiver(True, p1Plot.getRiverWEDirection())	
			else :
				p2Plot.setNOfRiver(False, p1Plot.getRiverWEDirection())						
				p3Plot.setNOfRiver(False, p1Plot.getRiverWEDirection())			
			if p1Plot.isWOfRiver():
				p2Plot.setWOfRiver(True, p1Plot.getRiverNSDirection())
				p3Plot.setWOfRiver(True, p1Plot.getRiverNSDirection())		
			else:
				p2Plot.setWOfRiver(False, p1Plot.getRiverNSDirection())
				p3Plot.setWOfRiver(False, p1Plot.getRiverNSDirection())					

	####### When map is not perfecfly dividabel by 3, a player (top right) is moved 1 tile north east on start instread of this
	if iPlayersCount == 3:
		firstPlayerID = shuffledPlayers[0]
		start_plot = gc.getPlayer(firstPlayerID).getStartingPlot()
		startx, starty = start_plot.getX(), start_plot.getY()	
		
		if iTemplateRoll == 1:
			iSignage = 1
		else:
			iSignage = -1
		
		copyPlayerID = shuffledPlayers[1]
		copyPlayer = gc.getPlayer(copyPlayerID)
		NewStartPlot = map.plot(start_plot.getX() + iBlockSize, start_plot.getY() + iBlockSize * iSignage)
		copyPlayer.setStartingPlot(NewStartPlot, True)	
		
		copyPlayerID = shuffledPlayers[2]
		copyPlayer = gc.getPlayer(copyPlayerID)
		NewStartPlot = map.plot(start_plot.getX() + iBlockSize * 2, start_plot.getY() + iBlockSize * 2 * iSignage)
		copyPlayer.setStartingPlot(NewStartPlot, True)		
	

def mirrorizeMap():
        global region_duplicated
        global other_regions
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()

        region_duplicated_ID, iWestX, iSouthY, iWidth, iHeight = region_duplicated
        #make sure larger duplicated land doesn't get extra bonuses/goodies
        minW = min([item[3] for item in other_regions])
        minH = min([item[4] for item in other_regions])

	for iX in range(iW):
		for iY in range(iH):
                        if iX >= iWestX and iX < iWestX + minW and iY >= iSouthY and iY < iSouthY + minH : continue
			pPlot = map.plot(iX, iY)

			pPlot.setImprovementType(-1)
			pPlot.setBonusType(-1)	
			pPlot.setFeatureType(-1, -1)
			pPlot.setNOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_WEST)
                        pPlot.setWOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
                        pPlot.setRiverID (-1)

        #reflect plot types (addlake)
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                pPlot.setPlotType(rPlot.getPlotType(), True, True)
	
	map.recalculateAreas()

        #reflect terrain
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                pPlot.setTerrainType(rPlot.getTerrainType(), True, True)
	
	map.recalculateAreas()

        #rearrange river IDs
	initRiverID = 0
	riverID = {}
        for dX in range(iWidth):
                for dY in range(iHeight):
                        pPlot = map.plot(iWestX + dX, iSouthY + dY)
                        rID = pPlot.getRiverID()
                        if rID != -1 :
                                if rID in riverID.keys() :
                                        pPlot.setRiverID(riverID[rID])
                                else :
                                        riverID[rID] = initRiverID
                                        pPlot.setRiverID(riverID[rID])
                                        initRiverID += 1

        iRivers = len(riverID.keys())
        incr = 0

        #mirrorize rivers
	for region_ID, wX, sY, rW, rH in other_regions:
                incr += 1
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
                                        
                                if rPlot.isNOfRiver():
                                        pPlot.setNOfRiver(True, rPlot.getRiverWEDirection())
                                if rPlot.isWOfRiver():
                                        pPlot.setWOfRiver(True, rPlot.getRiverNSDirection())

                                rID = rPlot.getRiverID()
                                if rID != -1 :
                                        pPlot.setRiverID(rID + incr * iRivers)
	
	map.recalculateAreas()

	# mirrorize features
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setFeatureType(rPlot.getFeatureType(), -1)

	
	map.recalculateAreas()

	# mirrorize bonuses
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setBonusType(rPlot.getBonusType(-1))	

	map.recalculateAreas()

	# mirrorize goodies
	for region_ID, wX, sY, rW, rH in other_regions:
                for dX in range(rW):
                        for dY in range(rH):
                                pPlot = map.plot(wX + dX, sY + dY)
                                rPlot = map.plot(iWestX + dX, iSouthY + dY)
        			pPlot.setImprovementType(rPlot.getImprovementType())

	map.recalculateAreas()

	return None
	
''' 11 - BTG local/map Redclaration of MapGeneratorUtil functions for logic '''
def BTPnormalizeAddExtrasSpecific(listToBalance,iDistanceMax,iDistanceMin,iProbaTreshold):

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
								if BonusBalancer().isBonusValid(bonus, pLoopPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent):
									resources_placed.append(type_string)	
									iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
									if iProba <= iProbaTreshold:#2.35 my Take
										pLoopPlot.setBonusType(bonus)
									break # go to the next bonus'''


def BTGnormalizeAddExtrasHills(iMinHills):

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
			if iMissingHills > 0:
				for i in range(iMissingHills):
					pChosenPlot = possiblePlots[CyGame().getSorenRandNum(len(possiblePlots), "where")]## This is for 1 plot
					pChosenPlot.setPlotType(PlotTypes.PLOT_HILLS, True, True)	
					possiblePlots.remove(pChosenPlot)									

''' 12 - BTG Dedicated Always call category'''	
'''def BTGFreeUnit():'''
'''def BTGFreeUnitCount():'''
'''def canBuildImprovement(argsList):'''

