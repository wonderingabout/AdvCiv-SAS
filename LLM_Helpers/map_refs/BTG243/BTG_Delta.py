from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer
import random

balancer = BonusBalancer()

def getDescription():#The BTS description, used in general game setup, not the MapPreview screen in game from BTS
	return "Beyond the Game map by Penny"
	
def getDescriptionTitle():
	return "A map deisgned for two sides, the top players will be far from each other and you will have to choose to move forward and create an access to the sea or not"

def getDescriptionTitleTwo():
	return ""

def getDescriptionMain():
	return "The middle is a lot of impassable land so you will have to be clever on how to use the sea accesses"

def getDescriptionSecond():#Script tip : (on TOP)
	return "The coast and lands around are randomized, make sure if you can cross at some unexpected place"
	
def getDescriptionThird():#Option : (at the bottom)"
	return "Play with the option 'Fresh water is coastal cities' so you can build boats at the back of the map"	
	
def getDescriptionScenario():#Scenario : (at the bottom)"
	return "Made for 3v3 ideally, 4v4 good. Renaissance starts shines with option Alchemy"

def getDescriptionBalance():#Balance : (at the bottom)"
	return ""	
	

def getNumCustomMapOptions():
	return 15

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_CENTER_REGION",
		1:	"Center Tile",
		2:	"TXT_KEY_MAP_WORLD_WRAP",
		3:  "TXT_KEY_CONCEPT_RESOURCES",
		4:	"BTG Resources",
		5:	"BTG Forest Type",
		6:	"BTG Start Position",
		7:  "Starting Units",
		8:	"Size 1 notch smaller",
		9:	"BTG Seas",
		10:	"Extra Water Top Sea",
		11:	"Start Type",
		12:	"Notes",
		13:	"BTG Spectator Notes",
		14: "Credit"		
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:	3,
		2:	2,#it crashes for 6 players for Toro/Cylindrical, am too lazy to do, I don't think we'll use it
		3:  3,
		4:	4,
		5:	2,
		6:	2,
		7:	2,
		8:	3,
		9:	4,
		10:	2,
		11:	2,	
		12:	1,
		13:	2,
		14:	1,		
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "Peaks / Lava [BTG]",
			1: "Ice",
			},
		1:	{
			0: "Ocean",
			1: "Impassable",
			2: "Ice / Volcano [BTG]"
			},
		2:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "Titled Axis",
			},
		3:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED",
			2: "Balanced - Increased Food"
			},
		4:	{
			0: "No",
			1: "Yes - Balanced for Diamond, Obsidian and Sulphur - 2 Jade/Sapphire/Nickel",
			2: "Yes - Balanced for Sulphur, Nickel - 1 Diamond/Obsidian/Jade/Sapphire",
			3: "Yes - Balanced for Sulphur, Nickel, Tea, Sheep - 1 Obsidian/Lead"
			},	
		5:	{
			0: "Normal Forest",
			1: "Palm Forest always"			
			},				
		6:	{
			0: "Normal",
			1: "Left vs Right"
			},
		7:	{
			0: "Normal - Scattered",
			1: "Special - Together Same Tile"
			},	
		8:	{
			0: "No",
			1: "Yes",
			2: "Yes - 2 notches"
			},
		9:	{
			0: "No",
			1: "Yes - All Lagoons",
			2: "Yes - Lagoons on coast",
			3: "Yes - Balanced Lagoons and Deep sea"
			},
		10:	{
			0: "No",
			1: "Yes",
			},			
		11:	{
			0: "Coastal - South player near coast, 1v1 too",
			1: "Central - South player central, 1v1 middle"
			},			
		12:	{
			0: "Up to 10 players"
			},			
		13:	{
			0: "Solo - 1 Spectator good in any slot",
			1: "Team - 1 Spectator good in any slot"
			},
		14:	{
			0: "Penny for BTG - Works for BTS, BTG Options have no effect"
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:	1,
		2:	1,
		3:  2,
		4:	3,
		5:	0,
		6:	1,
		7:	0,
		8:	1,
		9:	0,
		10:	1,
		11:	0,
		12:	0,
		13:	0,
		14:	0,
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	false,
		2:	false,
		3:  false,
		4:	false,
		5:	false,
		6:	false,
		7:  false,
		8:	false,
		9:	true,
		10:	true,
		11:	true,
		12:	false,
		13: false,
		14: false,
		}
	return option_random[iOption]

def getWrapX():
	#map = CyMap()
	#return (map.getCustomMapOption(2) == 1 or map.getCustomMapOption(2) == 2)
	return False
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(2) == 1)
	
def normalizeAddExtras():

	if (CyMap().getCustomMapOption(3) >= 1):
		#balancer.normalizeAddExtras()
		listToBalance = ["BONUS_ALUMINUM", "BONUS_COAL", "BONUS_COPPER", "BONUS_HORSE", "BONUS_IRON", "BONUS_OIL", "BONUS_URANIUM"]
		BTPnormalizeAddExtrasSpecificAera(listToBalance,6,0,100,True)

		#There is enough tundra
		#BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_OIL"),8,2,False,CyGlobalContext().getInfoTypeForString("TERRAIN_DESERT"))	
		


	
	if (CyMap().getCustomMapOption(3) >= 2):	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),7,5,False,iBrown)	
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_PIG"),6,3,True,iBrown)
		BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_WHEAT"),7,3,True,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))				
		
		
	#BTG
	if isBTPon:
		
						
		#2.34
		if (CyMap().getCustomMapOption(4) == 1):
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_NICKEL"),1,0,3)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,3)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_NICKEL"),1,0,3)
			
		if (CyMap().getCustomMapOption(4) == 1):#2.35
			#listToBalance = ["BONUS_DIAMOND","BONUS_OBSIDIAN","BONUS_SULPHUR"]
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_DIAMOND",5,3,100)
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_OBSIDIAN",7,4,100)
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_SULPHUR",6,2,100)
		
		if (CyMap().getCustomMapOption(4) == 2):#2.36v3
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_DIAMOND"),1,0,-1)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,-1)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_JADE"),1,0,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_SAPPHIRES"),1,0,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_DIAMOND"),1,0,-1)
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,-1)			
			
		if (CyMap().getCustomMapOption(4) == 2):#2.36v3
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_SULPHUR",5,2,100)			
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_NICKEL",5,2,100)		
			
		if (CyMap().getCustomMapOption(4) == 3):#2.42 We always use the "Bottom Branch"	don't need the boost on Paladins nor Grenadiers
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,-1)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_OBSIDIAN"),1,0,-1)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 10 / 100,CyMap().getGridWidth() * 40 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_LEAD"),1,0,-1)			
			CvMapGeneratorUtil.BTPMapUtil().BTPResourceInBox(CyMap().getGridWidth() * 60 / 100,CyMap().getGridWidth() * 90 / 100, CyMap().getGridHeight()  * 10 / 100, CyMap().getGridHeight()  * 80 / 100, False, CyGlobalContext().getInfoTypeForString("BONUS_LEAD"),1,0,-1)				
			
		if (CyMap().getCustomMapOption(4) == 3):#2.42 We always use the "Bottom Branch", since I removed so many strong items I buff the land a bit
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_SULPHUR",5,2,100)			
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_NICKEL",5,2,100)				
			balancer.BTPnormalizeAddExtrasSpecific("BONUS_TEA",6,3,100)	
			BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_SHEEP"),6,4,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))		
			#BTPForceEnrichFood(100,True,CyGlobalContext().getInfoTypeForString("BONUS_DEER"),8,6,False,CyGlobalContext().getInfoTypeForString("TERRAIN_GRASS"))#Actually One buff at a time, never tried this
			
			
	doDeltaBuild()#after bonus otherwise the Jad etc. all in the middle ice when it's ice			
		
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()
	
	if isBTPon :
		if (CyMap().getCustomMapOption(4) == 0):#all excluded
			if (type_string in balancer.newResourcesBTP):
				return None
		if (CyMap().getCustomMapOption(4) == 1 or CyMap().getCustomMapOption(4) == 2):#all excluded				
			if (type_string == "BONUS_SULPHUR"):
				return None
				
		if (CyMap().getCustomMapOption(4) == 3):#I reinsert them manually
			if (type_string in ('BONUS_SULPHUR','BONUS_NICKEL','BONUS_OBSIDIAN','BONUS_LEAD','BONUS_JADE','BONUS_SAPPHIRES','BONUS_DIAMOND','BONUS_TEAD')):
				return None				

	if (CyMap().getCustomMapOption(3) >= 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def isClimateMap():
	return 0

def isSeaLevelMap():
	return 0

def getGridSize(argsList):
	"Override Grid Size function to make the maps square."
	
	if (CyMap().getCustomMapOption(8) == 0):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(9,9),
			WorldSizeTypes.WORLDSIZE_TINY:		(10,10),
			WorldSizeTypes.WORLDSIZE_SMALL:		(11,11),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(12,12),
			WorldSizeTypes.WORLDSIZE_LARGE:		(14,14),
			WorldSizeTypes.WORLDSIZE_HUGE:		(16,16)
		}
		
	if (CyMap().getCustomMapOption(8) == 1):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(8,8),
			WorldSizeTypes.WORLDSIZE_TINY:		(9,9),
			WorldSizeTypes.WORLDSIZE_SMALL:		(10,10),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(11,11),
			WorldSizeTypes.WORLDSIZE_LARGE:		(13,13),
			WorldSizeTypes.WORLDSIZE_HUGE:		(15,15)
		}	
	
	if (CyMap().getCustomMapOption(8) == 2):
		grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		(7,7),
			WorldSizeTypes.WORLDSIZE_TINY:		(8,8),
			WorldSizeTypes.WORLDSIZE_SMALL:		(9,9),
			WorldSizeTypes.WORLDSIZE_STANDARD:	(10,10),
			WorldSizeTypes.WORLDSIZE_LARGE:		(12,12),
			WorldSizeTypes.WORLDSIZE_HUGE:		(14,14)
		}		

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def minStartingDistanceModifier():
	return -12

class DonutFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=False, grain_amount=3):
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)
		
		iCenterX = int(self.iNumPlotsX / 2)
		iCenterY = int(self.iNumPlotsY / 2)
		iRadius = min((iCenterX - 4), (iCenterY - 4))
		iHoleRadius = int(iRadius / 2)
		iHoleRadiusBias = 3#2.36
		iHoleRadius += iHoleRadiusBias#2.23
		userInputCenter = self.map.getCustomMapOption(0)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
					
					
				if fDistance > iRadius:#Outside
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					#2.23 - Rule 2 - The top 4 lines is water					
					if (y >= self.iNumPlotsY - 5):
						self.plotTypes[i] = PlotTypes.PLOT_OCEAN
					
					#2.23 - Rule 4 - Border are half water (useful for Toroidal/Cylindrical
					elif (x <= 3 or x >= self.iNumPlotsX - 4):
						if (y >= iCenterY + 5 or y <= iCenterY - 5):		
						#b version - but not in middle height of map					
							if (x == 0 or x == self.iNumPlotsX -1):
								if (iProba <= 85):
									self.plotTypes[i] = PlotTypes.PLOT_OCEAN						
								else:
									self.plotTypes[i] = PlotTypes.PLOT_LAND						
							elif (x == 1 or x == self.iNumPlotsX - 2):
								if (iProba <= 65):
									self.plotTypes[i] = PlotTypes.PLOT_OCEAN						
								else:
									self.plotTypes[i] = PlotTypes.PLOT_LAND	
							elif (x == 2 or x == self.iNumPlotsX - 3):
								if (iProba <= 45):
									self.plotTypes[i] = PlotTypes.PLOT_OCEAN						
								else:
									self.plotTypes[i] = PlotTypes.PLOT_LAND		
							elif (x == 3 or x == self.iNumPlotsX - 4):
								if (iProba <= 30):
									self.plotTypes[i] = PlotTypes.PLOT_OCEAN						
								else:
									self.plotTypes[i] = PlotTypes.PLOT_LAND
						else:#the 5 layer around middle I always want land
							hillVal = self.hillsFrac.getHeight(x,y)
							if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
								peakVal = self.peaksFrac.getHeight(x,y)
								if (peakVal <= iPeakThreshold):
									self.plotTypes[i] = PlotTypes.PLOT_PEAK
								else:
									self.plotTypes[i] = PlotTypes.PLOT_HILLS
							else:
								self.plotTypes[i] = PlotTypes.PLOT_LAND						
						
					#2.23 - Rule 3 - Bottom Outside is watery
					elif (x >= iCenterX - 6 and x <= iCenterX + 6 and iProba <= 70):
						self.plotTypes[i] = PlotTypes.PLOT_OCEAN
					elif (x >= iCenterX - 12 and x <= iCenterX + 12 and iProba <= 40 and y <= 3):
						self.plotTypes[i] = PlotTypes.PLOT_OCEAN	
					#b version - and it links up the super bottom
					elif ((x < iCenterX - 12 or x > iCenterX + 12) and iProba <= 90 and y <= 0):
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
						
				elif fDistance < iHoleRadius: # Plot is in hole of donut.
					
					
					#2.36 -- Very specific few 4 tiles to build "teeth" in ---- I never got this to work, so I've put it at the end of the process
					'''if ((x == iCenterX - 2 or x == iCenterX - 3 or x == iCenterX + 2 or x == iCenterX + 3) and (y >= iCenterY + 7) and (fDistance >= iHoleRadius -iHoleRadiusBias -2)):###Look at the biasAbove
					#if ((x == iCenterX - 2 or x == iCenterX - 3 or x == iCenterX + 2 or x == iCenterX + 3) and (y >= iCenterY + 7) and (fDistance >= iHoleRadius -2)):
						self.plotTypes[i] = PlotTypes.PLOT_PEAK					'''
					
					#2.23 - Rule 1 - Crossed middle
					if (x == iCenterX or x == iCenterX - 1 or x == iCenterX + 1 or y == iCenterY or y == iCenterY - 1 or y == iCenterY + 1):
						#if (y >= iCenterY + 7 and fDistance >= iHoleRadius -3):
						#if (y >= iCenterY + 7 and fDistance >= iHoleRadius -2):#2.36 Building "teeth" in
						if (y >= iCenterY + 7 and fDistance >= iHoleRadius - 3 + CyMap().getCustomMapOption(10)):#2.36 Building "teeth" with the option
							hillVal = self.hillsFrac.getHeight(x,y)
							if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
								peakVal = self.peaksFrac.getHeight(x,y)
								if (peakVal <= iPeakThreshold):
									self.plotTypes[i] = PlotTypes.PLOT_PEAK
								else:
									self.plotTypes[i] = PlotTypes.PLOT_HILLS
							else:
								self.plotTypes[i] = PlotTypes.PLOT_LAND
						else:
							self.plotTypes[i] = PlotTypes.PLOT_OCEAN
							
				
					elif (y >= iCenterY + 7 and fDistance >= iHoleRadius -3):
						hillVal = self.hillsFrac.getHeight(x,y)
						if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
							peakVal = self.peaksFrac.getHeight(x,y)
							if (peakVal <= iPeakThreshold):
								self.plotTypes[i] = PlotTypes.PLOT_PEAK
							else:
								self.plotTypes[i] = PlotTypes.PLOT_HILLS
						else:
							self.plotTypes[i] = PlotTypes.PLOT_LAND

					elif (y >= iCenterY + 4 and fDistance >= iHoleRadius - 6 and x >= iCenterX - 4 and x <= iCenterX + 4):
						#2.23 - Last Rule 5, I re-write the top delta to give more water contact to it	-- need to be in 1 line otherwise missing peaks				
						iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
						if (iProba <= 85):
							self.plotTypes[i] = PlotTypes.PLOT_OCEAN							
						else:
							self.plotTypes[i] = PlotTypes.PLOT_LAND
							
					else:#BTP normally never
						self.plotTypes[i] = PlotTypes.PLOT_PEAK
						
				elif ((y < iCenterY ) and (x >= iCenterX - 3) and (x <= iCenterX + 3)):
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
					#2.23 - Rule 4 - Link the water
					if (iProba <= 85):
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
					
				#2.23 - Make left right delta better
				elif ((fDistance <= iHoleRadius + 3) and y <= iCenterY +3 and y >= iCenterY - 3):
					iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")				
					if (iProba <= 80):
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

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Donut) ...")
	fractal_world = DonutFractalWorld()
	return fractal_world.generatePlotTypes()

# subclass TerrainGenerator to create a lush grassland utopia.
class DonutTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1, grain_amount=5):
		self.gc = CyGlobalContext()
		self.map = CyMap()

		self.grain_amount = grain_amount + self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()

		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

		self.terrain=CyFractal()

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()

		self.iCenterX = int(self.map.getGridWidth() / 2)
		self.iCenterY = int(self.map.getGridHeight() / 2)
		self.iRadius = min((self.iCenterX - 4), (self.iCenterY - 4))
		self.iHoleRadius = int(self.iRadius / 2)
		self.iHoleRadius += 3#2.23
		self.userInputCenter = self.map.getCustomMapOption(0)
		
	def initFractals(self):
		self.terrain.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iGrassBottom = self.terrain.getHeightFromPercent(12)

		self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
		self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
		self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")

	def getLatitudeAtPlot(self, iX, iY):
		return None

	def generateTerrain(self):		
		terrainData = [0]*(self.iWidth*self.iHeight)
		for x in range(self.iWidth):
			for y in range(self.iHeight):
				iI = y*self.iWidth + x
				terrain = self.generateTerrainAtPlot(x, y)
				terrainData[iI] = terrain
		return terrainData

	def generateTerrainAtPlot(self,iX,iY):
		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		#version B - Simplified
		val = self.terrain.getHeight(iX, iY)
		iProba = CyGlobalContext().getGame().getMapRandNum(100,"iProba")
		if iProba <= 2:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_DESERT")		
		if iProba <= 6:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
		elif iProba <= 12:
			terrainVal = iBrown
		elif iProba <= 32:
			terrainVal = self.gc.getInfoTypeForString("TERRAIN_PLAINS")				
		else:#then normal
			if val >= self.iGrassBottom:
				terrainVal = self.terrainGrass
			else:
				terrainVal = self.terrainPlains	

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Donut) ...")
	terraingen = DonutTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class DonutFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def addIceAtPlot(self, pPlot, iX, iY, lat):
		# We don' need no steeking ice. M'kay? Alrighty then.
		ice = 0
		
	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		jungle = 0	

def addFeatures():
	NiTextOut("Adding Features (Python Donut) ...")
	featuregen = DonutFeatureGenerator()
	featuregen.addFeatures()
	return 0
	
	
def beforeGeneration():
	#copy /inspired by inland			
	"Set up global variables for start point templates"
	global templates
	global shuffledPlayers
	global iTemplateRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()

	global isBTPon
	global iBrown
	try:
		isBTPon = CvMapGeneratorUtil.BTGInfo().BTG_Version() > 0
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_MARSH")
	except:
		isBTPon = False	
		iBrown = CyGlobalContext().getInfoTypeForString("TERRAIN_PLAINS")
				
	# Choose a Template to be used for this game.
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	
	#2.26
	configs = [0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
	iNumTemplates = configs[iPlayers]
	iTemplateRoll = dice.get(iNumTemplates, "Template Selection - Inland Sea PYTHON")
	
	if (CyMap().getCustomMapOption(11) == 0):
		iTemplateRoll = 0#overrides
	if (CyMap().getCustomMapOption(11) == 1):
		iTemplateRoll = min(1,iNumTemplates-1)#overrides- Minus 1 because the real number of a template start at 0
	
	#2.23 - Debug because it crashes if too close
	fVar = 2
	
	templates = {(1,0): {0: [0.50, 0.20, int(0.5 * iW), int(0.5 * iH)]},
				 (2,0): {0: [0.33, 0.20, 2, 2],
						 1: [0.66, 0.20, 2, 2]},
				 (2,1): {0: [0.15, 0.50, 2, 3],
						 1: [0.85, 0.50, 2, 3]},
				 (3,0): {0: [0.15, 0.50, fVar, fVar],
						 1: [0.85, 0.50, fVar, fVar],
						 2: [0.50, 0.75, fVar, fVar]},
				 (4,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.25, 0.80, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.75, 0.80, fVar, fVar]},
				 (4,1): {0: [0.16, 0.16, fVar, fVar],
						 1: [0.25, 0.80, fVar, fVar],
						 2: [0.84, 0.16, fVar, fVar],
						 3: [0.75, 0.80, fVar, fVar]},						 
				 (5,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.50, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.85, 0.50, fVar, fVar],
						 4: [0.50, 0.75, fVar, fVar]},
				 (6,0): {0: [0.33, 0.20, 1,    3   ],
						 1: [0.15, 0.50, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.68, 0.20, 1,    3   ],
						 4: [0.85, 0.50, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar]},
				 (6,1): {0: [0.16, 0.16, fVar, fVar],
						 1: [0.15, 0.50, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.84, 0.16, fVar, fVar],
						 4: [0.85, 0.50, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar]},						 
				 (7,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.66, 0.20, fVar, fVar],
						 3: [0.85, 0.35, fVar, fVar],
						 4: [0.50, 0.75, fVar, fVar],
						 5: [0.15, 0.65, fVar, fVar],
						 6: [0.85, 0.65, fVar, fVar]},	
				 (8,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar],
						 6: [0.15, 0.65, fVar, fVar],
						 7: [0.85, 0.65, fVar, fVar]},	
				 (8,1): {0: [0.16, 0.16, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.84, 0.16, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar],
						 6: [0.15, 0.65, fVar, fVar],
						 7: [0.85, 0.65, fVar, fVar]},							 
				 (9,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.50, 0.75, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.15, 0.65, fVar, fVar],
						 6: [0.85, 0.65, fVar, fVar],
						 7: [0.10, 0.10, fVar, fVar],
						 8: [0.90, 0.10, fVar, fVar]},	
				 (10,0): {0: [0.33, 0.20, fVar, fVar],
						 1: [0.15, 0.35, fVar, fVar],
						 2: [0.25, 0.80, fVar, fVar],
						 3: [0.66, 0.20, fVar, fVar],
						 4: [0.85, 0.35, fVar, fVar],
						 5: [0.75, 0.80, fVar, fVar],
						 6: [0.15, 0.65, fVar, fVar],
						 7: [0.85, 0.65, fVar, fVar],
						 8: [0.10, 0.10, fVar, fVar],
						 9: [0.90, 0.10, fVar, fVar]},					 
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
			
				
		
	return None		
	

def findStartingPlot(argsList):
	# Set up for maximum of 18 players! If more, use default implementation.
	iPlayers = CyGlobalContext().getGame().countCivPlayersEverAlive()
	if iPlayers > 10:
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

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)#2.22 Simplified this part by calling common logic	

def normalizeStartingPlotLocations():

	gc = CyGlobalContext()	
	dice = gc.getGame().getMapRand()	
		
	if (CyMap().getCustomMapOption(6) == 1):
		if isBTPon :
			BTPLeftRightTwoTeams(True)		
		else:
			BTPLeftRightTwoTeams(False)			
	else:
		CyPythonMgr().allowDefaultImpl()#this is the bit that puts team together and is normal case	

def startHumansOnSameTile():
	
	#doing in normalizeAddExtra was too early
	#we do this after because default implement does add forest
	if isBTPon:
		if (CyMap().getCustomMapOption(5) > 0):#quicker if don't run when 0
			CvMapGeneratorUtil.BTPMapUtil().BTPforestIntoPalms(100)
			
	if isBTPon:#2.25
		if (CyMap().getCustomMapOption(9) > 0):
			if (CyMap().getCustomMapOption(9)  == 1):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,100,0,0,5)
			if (CyMap().getCustomMapOption(9)  == 2):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,0,5)				
			if (CyMap().getCustomMapOption(9)  == 3):
				CvMapGeneratorUtil.BTPMapUtil().BTPDoLagoon(100,0,0,100,5)	

	if (CyMap().getCustomMapOption(7) == 1):
		return True

def doDeltaBuild():

	#Make middle "hard" part fire or Ice
	
	if not (CyMap().getCustomMapOption(0) == 0 and not isBTPon):#2.38 now choice 0 is default, and no code is peak
	#if (CyMap().getCustomMapOption(0) >= 1):#Normal case is Peak and no code
		
		iCenterX = int(CyMap().getGridWidth() / 2)
		iCenterY = int(CyMap().getGridHeight() / 2)
		iRadius = min((iCenterX - 4), (iCenterY - 4))
		iHoleRadius = int(iRadius / 2)
		iHoleRadius += 3#2.23

		for x in range(CyMap().getGridWidth()):
			for y in range(CyMap().getGridHeight()):
				if x == iCenterX and y == iCenterY:
					fDistance = 0
				else:
					fDistance = sqrt(((x - iCenterX) ** 2) + ((y - iCenterY) ** 2))
				
				if fDistance < iHoleRadius:#Inside
					if y <= iCenterY + 7:#2.24 so that front doesn't have lava
						p = CyMap().plot(x,y)
						if p.isImpassable() and not p.isWater():#a Peak
							if (CyMap().getCustomMapOption(0) == 1):
								p.setPlotType(PlotTypes.PLOT_LAND,True,True)
								p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)							
							if (CyMap().getCustomMapOption(0) == 0) and isBTPon:#Desactivated for now
								if CvMapGeneratorUtil.BTGInfo().BTG_Version() >= 23:#only has lava from there
									p.setPlotType(PlotTypes.PLOT_LAND,True,True)
									p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)
	
	
				#2.36 testing -- This proved useful	
				if (CyMap().getCustomMapOption(10) == 1):
					if ((x == iCenterX - 2 or x == iCenterX - 3 or x == iCenterX + 2 or x == iCenterX + 3) and (y >= iCenterY + 7) and (fDistance >= iHoleRadius -2)):
						if p.getBonusType(-1) == -1:
							iTerrain = CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")
							if (x == iCenterX - 3 or x == iCenterX + 3):
								p.setPlotType(PlotTypes.PLOT_OCEAN,True,True)
								p.setTerrainType(iTerrain, True, True)
							if (x == iCenterX - 2 or x == iCenterX + 2):
								p.setPlotType(PlotTypes.PLOT_OCEAN,True,True)
								p.setTerrainType(iTerrain, True, True)
								if isBTPon:
									p.setBonusType(CyGlobalContext().getInfoTypeForString("BONUS_PEARLS"))				
	
	#Put volcano on middle tile
	if (CyMap().getCustomMapOption(1) >= 1):
		p = CyMap().plot(int(CyMap().getGridWidth() / 2),int(CyMap().getGridHeight() / 2))
		p.setPlotType(PlotTypes.PLOT_LAND,True,True)
		p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_SNOW"), True, True)
		if (CyMap().getCustomMapOption(1) == 2):
			p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_VOLCANO"), -1)		
		if (CyMap().getCustomMapOption(1) == 1):
			p.setFeatureType(CyGlobalContext().getInfoTypeForString("FEATURE_ICE"), -1)

			#overwrite the impassable if you chose fire - to be written when I'll have Lava Graphics
		if (CyMap().getCustomMapOption(1) == 1) and isBTPon and CyMap().getCustomMapOption(0) == 0:
			if CvMapGeneratorUtil.BTGInfo().BTG_Version() >= 23:#only has lava from there	
				p.setTerrainType(CyGlobalContext().getInfoTypeForString("TERRAIN_LAVA"), True, True)
				p.setFeatureType(-1, -1)							
				
				
				
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
			