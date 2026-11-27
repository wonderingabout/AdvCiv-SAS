from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_CONTINENTS_DESCR"
	
def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1

def generatePlotTypes():
	life_world = LifeWorld()
	return life_world.generatePlotTypes()

def generateTerrainTypes():
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

class LifeWorld:
	def __init__(self):
		self.gc = CyGlobalContext()
		self.map = self.gc.getMap()
		self.iNumPlotsX = self.map.getGridWidth()
		self.iNumPlotsY = self.map.getGridHeight()
		self.mapRand = self.gc.getGame().getMapRand()

		self.seaLevelChange = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()

		self.plotTypes = [PlotTypes.PLOT_OCEAN] * (self.iNumPlotsX*self.iNumPlotsY)
		self.savePlots = [PlotTypes.PLOT_OCEAN] * (self.iNumPlotsX*self.iNumPlotsY)

		self.seaLevelChange = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		self.hillRange = self.gc.getClimateInfo(self.map.getClimate()).getHillRange()
		self.peakPercent = self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent()

		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			if (self.mapRand.get(100,"PlotGen Chooser - Ice Age PYTHON")>50+self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()/2):
				self.plotTypes[i] = PlotTypes.PLOT_LAND
				
	def generatePlotTypes(self):
		for i in range(100):
			self.step()
		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			if ((self.plotTypes[i] == PlotTypes.PLOT_LAND) and (self.mapRand.get(10,"PlotGen Chooser - Ice Age PYTHON")>=self.hillRange)):
				self.plotTypes[i] = PlotTypes.PLOT_HILLS
		for i in range(10):
			self.step2()
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				n = self.countNeighbours(x,y,PlotTypes.PLOT_HILLS)
				if ((n>2) and (self.mapRand.get(100,"PlotGen Chooser - Ice Age PYTHON")<self.peakPercent)):
					self.plotTypes[y*self.iNumPlotsX+x] = PlotTypes.PLOT_PEAK;
		return self.plotTypes

	def step(self):
		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			self.savePlots[i] = self.plotTypes[i]
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				n = self.countNeighbours(x,y,PlotTypes.PLOT_LAND)
				if ((self.plotTypes[y*self.iNumPlotsX+x] == PlotTypes.PLOT_LAND) and (n<4)):
					self.savePlots[y*self.iNumPlotsX+x] = PlotTypes.PLOT_OCEAN
				if ((self.plotTypes[y*self.iNumPlotsX+x] == PlotTypes.PLOT_OCEAN) and (n>4)):
					self.savePlots[y*self.iNumPlotsX+x] = PlotTypes.PLOT_LAND
		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			self.plotTypes[i] = self.savePlots[i]

	def step2(self):
		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			self.savePlots[i] = self.plotTypes[i]
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				n = self.countNeighbours(x,y,PlotTypes.PLOT_HILLS)
				if ((self.plotTypes[y*self.iNumPlotsX+x] == PlotTypes.PLOT_HILLS) and (n>2)):
					self.savePlots[y*self.iNumPlotsX+x] = PlotTypes.PLOT_LAND
				if ((self.plotTypes[y*self.iNumPlotsX+x] == PlotTypes.PLOT_LAND) and (n==3)):
					self.savePlots[y*self.iNumPlotsX+x] = PlotTypes.PLOT_HILLS
		for i in range(self.iNumPlotsX*self.iNumPlotsY):
			self.plotTypes[i] = self.savePlots[i]

	def countNeighbours(self,x,y,tile):
		ret = 0
		if (x>0):
			if (self.plotTypes[y*self.iNumPlotsX+x-1] == tile):
				ret+=1
			if (y>0):
				if (self.plotTypes[(y-1)*self.iNumPlotsX+x-1] == tile):
					ret+=1		
			if (y<self.iNumPlotsY-1):
				if (self.plotTypes[(y+1)*self.iNumPlotsX+x-1] == tile):
					ret+=1	
		if (x<self.iNumPlotsX-1):
			if (self.plotTypes[y*self.iNumPlotsX+x+1] == tile):
				ret+=1
			if (y>0):
				if (self.plotTypes[(y-1)*self.iNumPlotsX+x+1] == tile):
					ret+=1		
			if (y<self.iNumPlotsY-1):
				if (self.plotTypes[(y+1)*self.iNumPlotsX+x+1] == tile):
					ret+=1	
		if (y>0):
			if (self.plotTypes[(y-1)*self.iNumPlotsX+x] == tile):
				ret+=1		
		if (y<self.iNumPlotsY-1):
			if (self.plotTypes[(y+1)*self.iNumPlotsX+x] == tile):
				ret+=1	
		return ret
