# 2020 - Reboot Grid into super simple for mini tests

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import sys
import random
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from CvMapGeneratorUtil import BonusBalancer

gc = CyGlobalContext()

globalMapWidth = 3
globalMapHeigth = 3
globalSquareWidth = 12
globalSquareHeight = 12

balancer = BonusBalancer()
balancer.resourcesToBalance = ('BONUS_ALUMINUM', 'BONUS_COPPER', 'BONUS_HORSE', 'BONUS_IRON', 'BONUS_OIL', 'BONUS_URANIUM')
balancer.resourcesToEliminate = ('', )

def getDescription():
	return "for Test and Reboot"

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def getNumCustomMapOptions():
	return 3
	
def getNumHiddenCustomMapOptions():
	return 0

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"Size",
		1:	"Type of land",
		2:	"Notes"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	2,
		1:	3,
		2:	1
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "MiniMini [12x12]",
			1: "Playable [24x24]"
			},
		1:	{
			0: "All Green",
			1: "Bonuses Forced",
			2: "Default Implementation"
			},
		2:	{
			0: "Only for testing and 4Players max"
			}			
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	0,
		1:	0,
		2:	0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:	false,
		2:	false
		}
	return option_random[iOption]

def getWrapX():
	#map = CyMap()
	#return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	return False
	
def getWrapY():
	#map = CyMap()
	#return (map.getCustomMapOption(0) == 2)
	return False
	
def getGridSize(argsList):
	map = CyMap()
	if map.getCustomMapOption(0) >= 5:
		test = 1
		'''globalMapWidth = 6
		globalMapHeigth = 6
		globalSquareWidth = 24
		globalSquareHeight = 24'''
		
	return (globalMapWidth,globalMapHeigth) # Tiny 12x12 map	

###def beforeGeneration():


def generatePlotTypes():
	out = []
	for a in range(globalSquareWidth * globalSquareWidth):
			out.append(PlotTypes.PLOT_LAND)
	return out

def generateTerrainTypes():
	out = []
	for a in range(globalSquareWidth * globalSquareWidth):
			if a != 27 and a != 116:
					#out.append(2) # Desert in fact, Marsh
					out.append(0) # Grassland
			else:
					out.append(0) # Grassland
	return out

def addFeatures():
	return

def minStartingDistanceModifier():
	return

def assignStartingPlots():

	map = gc.getMap()
	player1 = gc.getPlayer(0)
	plot = map.plot(3,3)
	player1.setStartingPlot(plot, true)
	player2 = gc.getPlayer(1)
	plot = map.plot(9,9)
	player2.setStartingPlot(plot, true)
	player3 = gc.getPlayer(2)
	plot = map.plot(3,9)
	player3.setStartingPlot(plot, true)
	player4 = gc.getPlayer(3)
	plot = map.plot(9,3)
	player4.setStartingPlot(plot, true)	
	
def normalizeRemovePeaks():
	return

def normalizeAddExtras():
	return

def addBonusType(argsList):
	'''if map.getCustomMapOption(1) == 2:
		CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way
	else :'''
	'''if map.getCustomMapOption(1) == 0:
		return'''
		
	#if map.getCustomMapOption(1) == 1:
		
	oil = gc.getInfoTypeForString("BONUS_OIL")
	pig = gc.getInfoTypeForString("BONUS_PIG")
	
	'''for a in range(globalSquareWidth * globalSquareWidth):
		iApplyChance = gc.getGame().getSorenRandNum(100,"Happens")# BTG addition 	
		if iApplyChance > 60:
			a.setBonusType(pig)'''
		
	'''else :
		return#nothing'''

	CyPythonMgr().allowDefaultImpl()

def isBonusIgnoreLatitude():
	return True
	
#from Simple	
def normalizeAddRiver():
        return
def normalizeAddLakes():
        return
def normalizeAddGoodTerrain():
        return
def normalizeRemoveBadTerrain():
        return
def normalizeRemoveBadFeatures():
        return
def normalizeAddFoodBonuses():
        return
def normalizeAddExtras():
        return
def normalizeRemovePeaks():
        return	
