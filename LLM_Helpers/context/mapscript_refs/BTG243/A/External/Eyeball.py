#
#   FILE:       Eyeball.py
#   AUTHOR:     LPlate
#   BASIS:      Discworld.py by Terkhen
#   PURPOSE:    Generates a tidally locked planet
#-----------------------------------------------------------------------------
# CHANGELOG
#-----------------------------------------------------------------------------
#   0.1.1:
#       - Revised initial release to improve scaling - giving ~ 50 cities on the Standard maps
#       - Latitude calculation for cold eyeball adjusted to allow for some jungles around central ocean.


from CvPythonExtensions import *
import CvMapGeneratorUtil
import math
import sys

gc = CyGlobalContext()
iPeak = gc.getInfoTypeForString('PLOT_PEAK')
iLand = gc.getInfoTypeForString('PLOT_LAND')
iOcean = gc.getInfoTypeForString('PLOT_OCEAN')
iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')

# Global values that determine how the MapScript works.


fSnowRadius = 0.10
"""
Amount of the Eyeball radius in which the terrain will be snow.
"""


fTundraRadius = 0.2
"""
Amount of the Eyeball radius in which the terrain will be tundra.
"""


iTerrainGrain = 3
"""
Grain used for terrainVarFractal.
"""


iFeatureGrain = 4
"""
Grain used for featuresVarFractal.
"""


lStartingPlotAreas = list()
"""
List of map area polygons (see MapAreaPolygon class definition in this file) in which civilizations can start playing
the game.
"""


map = CyGlobalContext().getMap()
"""
Access to map global context.
"""


game = CyGlobalContext().getGame()
"""
Access to game global context.
"""

terrainVarFractal = None
"""
Fractal used to introduce random variations to terrain types depending on their distance to the center of the disc.
"""


featuresVarFractal = None
"""
Fractal used to introduce random variations to feature types depending on their distance to the center of the disc.
"""
### Eyeball Options ###
def getDescription():
	return "Eyeball"

def getNumCustomMapOptions():
	return 1
	
def getCustomMapOptionName(argsList):
	translated_text = unicode(CyTranslator().getText("Eyeball type", ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	return 3
	
def getCustomMapOptionDescAt(argsList):
	iSelection = argsList[1]
	selection_names = ["Cold",
			   "Warm",
			   "Hot"]
	translated_text = unicode(CyTranslator().getText(selection_names[iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	return -1

### End Eyeball Options - above tested and successfully gives option of selecting Cold, Warm or Hot as the eyeball type
### Cold = no central desert
### Warm = 50% of diameter is central desert
### Hot = 70% of diameter is central desert

def isAdvancedMap():
	"""
	This map should not show up in simple mode.
	:return: The map is an advanced map.
	"""
	return 1


def isClimateMap():
	"""
	Eyeball uses the climate options.
	:return: True
	"""
	return True


def isSeaLevelMap():
	"""
	Eyeball uses the sea level options.
	:return: True
	"""
	return True


def getGridSize(argsList):
	"""
	On the Eyeball planet, the playable area is reduced as the corners of the rectangle are cut to form a round border. The
	grid size is scaled up to let the disc have the same playable area than a rectangular map of the same world size.
	However, for a warm/hot Eyeball, the centre is also not playable and so the calculation needs to allow for the annulus of useable play area.
	:param argsList: List containing the chosen world size as its single element. This element can be -1 on loads.
	:return: tuple with the chosen map width and height.
	"""

	map = CyGlobalContext().getMap()
	
	# Get user input.
	iEyeballType = map.getCustomMapOption(0)

	iAnnulus = 100
## Eyeball 1.1 edit - adding in factors to scale from Pangaea to Cold, Warm and Hot
	iPangaeaScale = 13
	if iEyeballType == 1:
		iAnnulus = 75
		iPangaeaScale = 15
	if iEyeballType == 2:
		iAnnulus = 40
		iPangaeaScale = 25

	print "[EYEBALL] -- getGridSize()"

	[eWorldSize] = argsList
	# Eyeball map should have a similar playable area to the chosen world size.

## Eyeball 1.1 edit. Rescale as there's less ocean.
## Eyeball 1.1 playable area based on Pangaea map playable area
## Eyeball 1.1 getting 85+ cities on standard maps based on Pangaea starting dimensions.  Scaling from 16 to 10 works to give approsimately 50 citeis on cold but 70+ on warm and 100+ on hot

#1.1	iOrigWidth = CyGlobalContext().getWorldInfo(eWorldSize).getGridWidth()
#1.1	iOrigHeight = CyGlobalContext().getWorldInfo(eWorldSize).getGridHeight()
#1.1	iOrigArea = iOrigWidth * iOrigHeight

	area_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(8*5),
		WorldSizeTypes.WORLDSIZE_TINY:		(10*6),
		WorldSizeTypes.WORLDSIZE_SMALL:		(13*8),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(16*10),
		WorldSizeTypes.WORLDSIZE_LARGE:		(21*13),
		WorldSizeTypes.WORLDSIZE_HUGE:		(26*16)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	iOrigArea = area_sizes[eWorldSize]

	iWorldDiam = int(math.ceil(2 * math.sqrt(iOrigArea / math.pi)))
	iWorldDiam = iWorldDiam * 100 / iAnnulus

	iWorldDiam = iWorldDiam * 10 / iPangaeaScale

## End Eyeball 1.1 edit.

	return iWorldDiam, iWorldDiam

def getWrapX():
	"""
	The Eyeball is impassable on the cold, night side of the planet.
	:return: False
	"""
	return False


def getWrapY():
	"""
	The Eyeball is impassable on the cold, night side of the planet.
	:return: False
	"""
	return False


def isBonusIgnoreLatitude():
	"""
	The latitude calculations made in Civilization IV are not appropiate for placing bonuses on a flat disc.
	:return:
	"""
	return True

def generatePlotTypes():
	"""
	Generates the PlotTypes for all plots in the map. See EyeballMultilayeredFractal for details. This method also
	creates the border of the Eyeball.
	:return: List of the PlotTypes generated for each plot of the map.
	"""
	print "[EYEBALL] -- generatePlotTypes()"

	plotGenerator = EyeballMultilayeredFractal()

	plotTypes = plotGenerator.generatePlotsByRegion()

	# Create Eyeball border first pass: water and centre impassable peaks
	for iX in range(map.getGridWidth()):
		for iY in range(map.getGridHeight()):
			if isOutsideDisc(iX, iY):
				plotTypes[iY * map.getGridWidth() + iX] = PlotTypes.PLOT_OCEAN

			elif isDesertDisc(iX, iY):
				plotTypes[iY * map.getGridWidth() + iX] = PlotTypes.PLOT_PEAK

	return plotTypes


def generateTerrainTypes():
	"""
	Generates terrain types for all the plots of the map. These reflect the central desert (for warm and hot eyeballs) moving out to the cold circumference where it goes into the night side.
	:return: List of generated terrain types.
	"""
	print "[EYEBALL] -- generateTerrainTypes()"

	global terrainVarFractal
	terrainVarFractal = getVariationFractal(iTerrainGrain)
	terrainGen = EyeballTerrainGenerator(fSnowLatitude = 1.0 - fSnowRadius, fTundraLatitude = 1.0 - fTundraRadius)
	terrainTypes = terrainGen.generateTerrain()

	for iX in range(map.getGridWidth()):
		for iY in range(map.getGridHeight()):
			if isDesertDisc(iX, iY):
				pPlot = map.plot(iX, iY)
				pPlot.setTerrainType(iDesert, False, False)
				terrainTypes[iY * map.getGridWidth() + iX] = iDesert
	return terrainTypes


def addFeatures():
	"""
	Generates feature types for all the plots of the map. These reflect the central desert (for warm and hot eyeballs) moving out to the cold circumference where it goes into the night side.
	This method also removes all rivers from the central desert, peak area.	"""
	print "[EYEBALL] -- addFeatures()"

	# Create Eyeball border second pass: Add ice.
	iFeatureIce = CyGlobalContext().getInfoTypeForString("FEATURE_ICE")

	# Add other features.
	global featuresVarFractal
	featuresVarFractal = getVariationFractal(iFeatureGrain)
	featureGen = EyeballFeatureGenerator()
	featureGen.addFeatures()

	for iX in range(map.getGridWidth()):
		for iY in range(map.getGridHeight()):
			if isDesertDisc(iX, iY):
				map.plot(iX, iY).setNOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
				map.plot(iX, iY).setWOfRiver(False, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)

			elif isOutsideDisc(iX, iY):
				map.plot(iX, iY).setFeatureType(iFeatureIce, -1)  

	return 0


def findStartingPlot(argsList):
	"""
	Find starting plot for a certain player.
	:param argsList: List that contains the playerID of the player.
	:return: Starting plot
	"""
	[playerID] = argsList

	def isInsidePlayableRegion(pID, iX, iY):
		global lStartingPlotAreas
		for mapAreaPolygon in lStartingPlotAreas:
			if mapAreaPolygon.isInside(iX, iY):
				return True

		return False

	return CvMapGeneratorUtil.findStartingPlot(playerID, isInsidePlayableRegion)


# All utility classes and methods used by the MapScript are implemented below.

class EyeballMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	"""
	Multilayered fractal customized for Eyeball. Warm and Hot Eyeballs have a central desert.

	Along with MapAreaPolygon, this implementation of MultilayeredFractal allows to place regions with arbitrary
	polygonal shapes, and to rotate them along the center of the disc for any angle. These shapes are distorted and
	randomized slightly to make them appear more natural (see MapAreaPolygon).
	"""

	def generatePlotsByRegion(self):
		"""
		Generate all of the regions of the Eyeball.
		:return: Plots generated.
		"""
		# Remove all elements from the starting plot areas list.
		del lStartingPlotAreas[:]
		iBaseSeaLevel = 70 + self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()

		fMainAngle = math.radians(game.getMapRand().get(360, "[Eyeball] - Angle of the main continent."))
	
		self.generatePlotsMainContinent(iBaseSeaLevel, fMainAngle)

		fSecondAngle = fMainAngle +  math.radians(120)
		fSecondAngle += math.radians(game.getMapRand().get(40, "[Eyeball] - Randomization of the angle of the second continent.") - 20.0)
		fThirdAngle = fMainAngle +  math.radians(240)
		fThirdAngle += math.radians(game.getMapRand().get(40, "[Eyeball] - Randomization of the angle of the third continent.") - 20.0)
		self.generatePlotsMainContinent(iBaseSeaLevel, fSecondAngle)
		self.generatePlotsMainContinent(iBaseSeaLevel, fThirdAngle)

		fCentreAngle1 = fMainAngle +  math.radians(45)
		fCentreAngle1 += math.radians(game.getMapRand().get(40, "[Eyeball] - Randomization of the angle of the second continent.") - 20.0)

		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 45)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 90)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 135)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 180)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 235)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 270)
		self.generatePlotsCentreContinent(iBaseSeaLevel, fCentreAngle1 + 315)

		return self.wholeworldPlotTypes

	def generatePlotsMainContinent(self, iBaseSeaLevel, fMainAngle):
		"""
		The main continent is the biggest landmass on the Eyeball. It occupies almost half of the annulus and as it is repeated, this can result in one large single continent that stretches around a lot of the planet, or up to three largish continents.  They may be separated by sea but linked by the central desert.
		:param iBaseSeaLevel: Base sea level.
		:return: Angle in radians in which the land of the main continent will be placed.
		"""
		iMainContinentGrain = 2
		iMainContinentHillsGrain = 4


		fMiddleX = self.iW / 2.0
		fMiddleY = self.iH / 2.0

		iEyeballType = map.getCustomMapOption(0)

		fMinRad = 15.0 * self.iW / 100

		if iEyeballType == 1:
			fMinRad = 30.0 * self.iW / 100
		if iEyeballType == 2:
			fMinRad = 35.0 * self.iW / 100

		lMainContinentPolygon = [
			[fMiddleX + fMinRad, fMiddleY],
			[fMiddleX + fMinRad / 1.4, fMiddleY + fMinRad / 1.4],
			[fMiddleX , fMiddleY + fMinRad],
			[fMiddleX - fMinRad / 1.4, fMiddleY + fMinRad / 1.4],
			[fMiddleX - fMiddleX / 1.4, fMiddleY + fMiddleY / 1.4],
			[fMiddleX , fMiddleY + fMiddleY/1.1],
			[fMiddleX + fMiddleX / 1.4, fMiddleY + fMiddleY / 1.4],
			[fMiddleX + fMiddleX / 1.1, fMiddleY],
		]
		# Create the map area polygon.
		mainContinentMapArea = MapAreaPolygon("Main Continent", lMainContinentPolygon, fMainAngle)

		# Add the area to the list of regions in which civilizations can start.
		global lStartingPlotAreas
		lStartingPlotAreas.append(mainContinentMapArea)

		self.generatePlotsInMapAreaPolygon(
			iBaseSeaLevel - 15, mainContinentMapArea, iMainContinentGrain, iMainContinentHillsGrain, self.iRoundFlags,
			self.iTerrainFlags, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP
		)

		return

	def generatePlotsCentreContinent(self, iBaseSeaLevel, fCentreAngle):
		"""
		These are to create some rough edges around the central desert so it is not a perfect circular landmass
		:param iBaseSeaLevel: Base sea level.
		:return: Angle in radians in which the land of the main continent will be placed.
		"""

		iCentreContinentGrain = 2
		iCentreContinentHillsGrain = 4

		fMiddleX = self.iW / 2.0
		fMiddleY = self.iH / 2.0

		iEyeballType = map.getCustomMapOption(0)

		fContRad = 15.0 * self.iW / 100

		if iEyeballType == 1:
			fContRad = 24.0 * self.iW / 100
		if iEyeballType == 2:
			fContRad = 34.0 * self.iW / 100

		lCentreContinentPolygon = [
			[fMiddleX + fContRad, fMiddleY],
			[fMiddleX + fContRad, fMiddleY + 10],
			[fMiddleX + fContRad + 10, fMiddleY + 10],
			[fMiddleX + fContRad + 10, fMiddleY],
		]                        


		# Create the map area polygon.
		CentreContinentMapArea = MapAreaPolygon("Centre Continent", lCentreContinentPolygon, fCentreAngle)

		self.generatePlotsInMapAreaPolygon(
			iBaseSeaLevel - 15, CentreContinentMapArea, iCentreContinentGrain, iCentreContinentHillsGrain, self.iRoundFlags,
			self.iTerrainFlags, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP
		)

		return

	def generatePlotsInMapAreaPolygon(self, iWaterPercent, mapArea, iRegionGrain, iRegionHillsGrain, iRegionPlotFlags,
					  iRegionTerrainFlags, iRegionFracXExp = -1, iRegionFracYExp = -1):
		"""
		Generate plots in a region that is not a rectangle, but an arbitrary polygon. See MapAreaPolygon for details.
		:param iWaterPercent:
		:param mapArea: Polygonal shape inside which the region will be created.
		:type mapArea: MapAreaPolygon
		:param iRegionGrain: Fractal grain used for generating the terrain.
		:param iRegionHillsGrain: Fractal grain used for generating hills and peaks.
		:param iRegionPlotFlags: Flags used for the plot fractal.
		:param iRegionTerrainFlags: Flags used for the hills and peaks fractals.
		:param iRegionFracXExp:
		:param iRegionFracYExp:
		:return:
		"""
		# Obtain size and position from the map area.
		iRegionWidth = mapArea.iRegionWidth
		iRegionHeight = mapArea.iRegionHeight
		fMinX = mapArea.fMinX
		fMinY = mapArea.fMinY

		# Init the plot types array and the regional fractals
		self.plotTypes = [] # reinit the array for each pass
		self.plotTypes = [PlotTypes.PLOT_OCEAN] * (iRegionWidth * iRegionHeight)
		regionContinentsFrac = CyFractal()
		regionHillsFrac = CyFractal()
		regionPeaksFrac = CyFractal()
		regionContinentsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionGrain, self.dice, iRegionPlotFlags, iRegionFracXExp, iRegionFracYExp)
		regionHillsFrac.fracInit(iRegionWidth, iRegionHeight, iRegionHillsGrain, self.dice, iRegionTerrainFlags, iRegionFracXExp, iRegionFracYExp)
		regionPeaksFrac.fracInit(iRegionWidth, iRegionHeight, iRegionHillsGrain+1, self.dice, iRegionTerrainFlags, iRegionFracXExp, iRegionFracYExp)

		iWaterThreshold = regionContinentsFrac.getHeightFromPercent(iWaterPercent)
		iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((25 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
		iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((25 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
		iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((75 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
		iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((75 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
		iPeakThreshold = regionPeaksFrac.getHeightFromPercent(self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent())

		# Loop through the region's plots
		for iRegionX in range(iRegionWidth):
			for iRegionY in range(iRegionHeight):
				val = regionContinentsFrac.getHeight(iRegionX, iRegionY)
				if val <= iWaterThreshold:
					pass
				else:
					# Checking if the plot is inside the polygon is expensive, so it is done here at the last possible
					# chance.
					if mapArea.isInside(iRegionX + fMinX, iRegionY + fMinY):
						iPlotIndex = iRegionY * iRegionWidth + iRegionX
						hillVal = regionHillsFrac.getHeight(iRegionX, iRegionY)
						if hillVal >= iHillsBottom1 and hillVal <= iHillsTop1 or hillVal >= iHillsBottom2 and hillVal <= iHillsTop2:
							peakVal = regionPeaksFrac.getHeight(iRegionX, iRegionY)
							if peakVal <= iPeakThreshold:
								self.plotTypes[iPlotIndex] = PlotTypes.PLOT_PEAK
							else:
								self.plotTypes[iPlotIndex] = PlotTypes.PLOT_HILLS
						else:
							self.plotTypes[iPlotIndex] = PlotTypes.PLOT_LAND

		# Apply the region's plots to the global plot array.
		for iRegionX in range(iRegionWidth):
			iWholeworldX = int(iRegionX + fMinX)
			if iWholeworldX < 0 or iWholeworldX > (self.iW - 1):
				continue
			for iRegionY in range(iRegionHeight):
				iWholeworldY = int(iRegionY + fMinY)
				if iWholeworldY < 0 or iWholeworldY > (self.iH - 1):
					continue
				iPlotIndex = iRegionY * iRegionWidth + iRegionX
				if self.plotTypes[iPlotIndex] == PlotTypes.PLOT_OCEAN:
					continue
				iWorld = iWholeworldY * self.iW + iWholeworldX
				self.wholeworldPlotTypes[iWorld] = self.plotTypes[iPlotIndex]

		# This region is done.
		return


class EyeballTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	"""
	Terrain generator customized for Eyeball. This means creating terrain as if the "latitude" starts at edge of central desert at equivalent latitude to earth's deserts, and it increases progressively until it reaches 1 right at the border.
	"""

	def getLatitudeAtPlot(self, iX, iY):
		"""
		Given a plot (iX,iY) such that (0,0) is in the NW, returns a value between 0.0 (tropical) and 1.0 (polar). In
		Eyeball, this "latitude" starts at edge of central desert at equivalent latitude to earth's deserts, and it increases progressively until it reaches 1 right at the border.
		:param iX: x coordinate of the plot
		:param iY: y coordinate of the plot.
		:return: Calculated latitude.
		"""
		return getInvertedDistanceToCenter(iX, iY, terrainVarFractal)


class EyeballFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	"""
	Feature generator customized for Eyeball. This means placing features as if the "latitude" starts at edge of central desert at equivalent latitude to earth's deserts, and it increases progressively until it reaches 1 right at the border.
	"""

	def getLatitudeAtPlot(self, iX, iY):
		"""
		Given a plot (iX,iY) such that (0,0) is in the NW, returns a value between 0.0 (tropical) and 1.0 (polar). In
		Eyeball, this "latitude" starts at edge of central desert at equivalent latitude to earth's deserts, and it increases progressively until it reaches 1 right at the border.
		:param iX: x coordinate of the plot.
		:param iY: y coordinate of the plot.
		:return: Calculated latitude.
		"""
		return getInvertedDistanceToCenter(iX, iY, featuresVarFractal)


	def addIceAtPlot(self, pPlot, iX, iY, lat):
		"""
		Randomly add ice at plot. Eyeball has less ice than normal maps.
		:param pPlot: Plot
		:param iX: x coordinate of the plot.
		:param iY: y coordinate of the plot.
		:param lat: Latitude of the plot.
		:return:
		"""
		if pPlot.canHaveFeature(self.featureIce):
			rand = self.mapRand.get(100, "[EYEBALL] - Add ice") / 100.0
			if rand < 7 * (lat - (1.0 - (self.gc.getClimateInfo(self.map.getClimate()).getRandIceLatitude() / 2.0))):
				pPlot.setFeatureType(self.featureIce, -1)


class MapAreaPolygon:
	"""
	Class that defines a map area that can have any polygonal shape. Randomized distortion using both fractals and
	coordinate changes is applied, to make sure that the final area shape is not too regular and unpredictable, while
	still following roughly the desired shape.
	Uses the PNPOLY algorithm. See: https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
	"""

	__DISPLACEMENT_FRACTAL_GRAIN = 2
	"""
	Grain used for the displacement fractals.
	"""


	def __init__(self, sRegionName, lOriginalPolygonPoints, fAngle):
		"""
		Initializes the polygonal map area.
		:param lOriginalPolygonPoints: List of tuples that contain the x and y coordinates of each of the points.
		:param fAngle: The polygon will be rotated by this angle.
		"""
		if len(lOriginalPolygonPoints) < 3:
			raise Exception("[Eyeball] - " + sRegionName + " - A polygon must have at least three vertices.")

		# Rotate the polygon and apply random displacement.
		lPolygonPoints = list()

		self.__iRandomDisplacement = int(max(2.0, map.getGridWidth() / 12.0))
		fMiddleX = map.getGridWidth() / 2.0
		fMiddleY = map.getGridHeight() / 2.0
		fSinAngle = math.sin(fAngle)
		fCosAngle = math.cos(fAngle)

		for pX, pY in lOriginalPolygonPoints:
			pXInitial = pX - fMiddleX
			pYInitial = pY - fMiddleY
			pXRotated = pXInitial * fCosAngle - pYInitial * fSinAngle + fMiddleX + self.__getRandomDisplacement()
			pYRotated = pXInitial * fSinAngle + pYInitial * fCosAngle + fMiddleY + self.__getRandomDisplacement()
			lPolygonPoints.append([pXRotated, pYRotated])

		# Calculate the rest of the values that depend on the shape of the polygon.
		self.__fMinX = sys.maxint
		self.__fMinY = sys.maxint
		self.__fMaxX = -sys.maxint - 1
		self.__fMaxY = -sys.maxint - 1

		for pX, pY in lPolygonPoints:
			self.__fMinX = min(self.__fMinX, pX)
			self.__fMinY = min(self.__fMinY, pY)
			self.__fMaxX = max(self.__fMaxX, pX)
			self.__fMaxY = max(self.__fMaxY, pY)

		# Give room for fractal displacement.
		self.__fMinX -= 4.0
		self.__fMinY -= 4.0
		self.__fMaxX += 4.0
		self.__fMaxY += 4.0

		# Used for creating displacement fractals and initial isInside checks.
		self.__iRegionWidth = int(self.__fMaxX - self.__fMinX + 1)
		self.__iRegionHeight = int(self.__fMaxY - self.__fMinY + 1)

		# Perfect polygons are boring. These fractals are used to distort the shape of the resulting landmass slightly.
		self.__horizontalDisplacementFrac = CyFractal()
		self.__horizontalDisplacementFrac.fracInit(
			self.__iRegionWidth, self.__iRegionHeight, self.__DISPLACEMENT_FRACTAL_GRAIN, game.getMapRand(),
			CyFractal.FracVals.FRAC_POLAR, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP
		)

		self.__verticalDisplacementFrac = CyFractal()
		self.__verticalDisplacementFrac.fracInit(
			self.__iRegionWidth, self.__iRegionHeight, self.__DISPLACEMENT_FRACTAL_GRAIN, game.getMapRand(),
			CyFractal.FracVals.FRAC_POLAR, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP
		)

		# Since all points need to be accessed at least once, they can be calculated on init.
		self.__bInsideMatrix = [[False for iY in range(self.__iRegionHeight)] for iX in range(self.__iRegionWidth)]

		# PNPOLY algorithm for determining if a given plot is inside of the polygon or not.
		for iX in range(self.__iRegionWidth):
			for iY in range(self.__iRegionHeight):
				# Apply displacement values between -4.0 and 4.0.
				fHorizontalDisp = self.__horizontalDisplacementFrac.getHeight(iX, iY) / 32.0 - 4.0
				fVerticalDisp = self.__verticalDisplacementFrac.getHeight(iX, iY) / 32.0 - 4.0

				fRealX = self.__fMinX + iX + fHorizontalDisp
				fRealY = self.__fMinY + iY + fVerticalDisp

				iPoint = 0
				jPoint = len(lPolygonPoints) - 1
				bInside = False

				while iPoint < len(lPolygonPoints):
					lFirstPoint = lPolygonPoints[iPoint]
					lSecondPoint = lPolygonPoints[jPoint]
					if (lFirstPoint[1] > fRealY) != (lSecondPoint[1] > fRealY):
						fValue = float(lSecondPoint[0] - lFirstPoint[0])
						fValue *= fRealY - lFirstPoint[1]
						fValue /= lSecondPoint[1] - lFirstPoint[1]
						fValue += lFirstPoint[0]
						if fRealX < fValue:
							bInside = not bInside

					# Prepare the next pair of points.
					jPoint = iPoint
					iPoint += 1

				if bInside:
					self.__bInsideMatrix[iX][iY] = True

		# Uncommenting this code displays all regions in the log.
		"""
		print "[Eyeball] - " + sRegionName + " - MapAreaPolygon map area:"
		for iY in range(self.__iRegionHeight - 1, -1, -1):
			sLine = ""
			for iX in range(self.__iRegionWidth):
				if self.__bInsideMatrix[iX][iY]:
					sLine += "#"
				else:
					sLine += " "
			print sLine
		"""


	def __getRandomDisplacement(self):
		"""
		Allows to apply a random displacement to one of the coordinates of one of the points of the polygon.
		:return: Calculated displacement.
		"""
		return self.__iRandomDisplacement / 2 - game.getMapRand().get(
			self.__iRandomDisplacement,
			"[Eyeball] - Randomization of the points of one of the areas.")


	@property
	def iRegionWidth(self):
		return self.__iRegionWidth


	@property
	def iRegionHeight(self):
		return self.__iRegionHeight


	@property
	def fMinX(self):
		return self.__fMinX


	@property
	def fMinY(self):
		return self.__fMinY


	def isInside(self, fX, fY):
		"""
		Checks if the point (fX, fY) is inside of the polygon.
		:param fX: x coordinate of the point.
		:param fY: y coordinate of the point.
		:return: True if the point is inside of the polygon, false otherwise.
		"""
		iRealX = int(fX - self.__fMinX)
		iRealY = int(fY - self.__fMinY)

		if iRealX < 0 or iRealX >= self.__iRegionWidth:
			return False
		if iRealY < 0 or iRealY >= self.__iRegionHeight:
			return False

		return self.__bInsideMatrix[iRealX][iRealY]


def getVariationFractal(iGrain):
	"""
	Initializes a fractal that can be used to introduce random variations.
	:return: New fractal.
	"""
	varFractal = CyFractal()
	iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

	varFractal.fracInit(
		map.getGridWidth(), map.getGridHeight(), iGrain, game.getMapRand(), iFlags,
		# The Eyeball has the same width and height.
		CyFractal.FracVals.DEFAULT_FRAC_Y_EXP, CyFractal.FracVals.DEFAULT_FRAC_Y_EXP
	)

	return varFractal


def getEyeballLatitude(iX, iY, varFractal=None):
	"""
	Calculates an approximate distance from the point to the center of the disc.
	:param iX: x coordinate of the plot
	:param iY: y coordinate of the plot.
	:param varFractal: Fractal used to introduce random variations in the calculated distance.
	:return: Calculated distance.
	"""
	fHorizontal = ((map.getGridWidth() - 1) / 2.0 - iX) / ((map.getGridWidth() - 1) / 2.0)
	fVertical = ((map.getGridHeight() - 1) / 2.0 - iY) / ((map.getGridHeight() - 1) / 2.0)

	fDistance = math.sqrt(fHorizontal * fHorizontal + fVertical * fVertical)

	iEyeballType = map.getCustomMapOption(0)

	fDesertDistance = 0.0
	if iEyeballType == 1:
		fDesertDistance = 0.5
	if iEyeballType == 2:
		fDesertDistance = 0.7

	fLatitude = (((fDistance - fDesertDistance) / (1.0 - fDesertDistance)) * 0.8) + 0.2
	if fDistance < fDesertDistance:
		fLatitude = 0.2
## Eyeball 1.1 to allow for jungles on cold eyeball
	if iEyeballType == 0:
# Rem fMinRad = 15.0 * self.iW / 100
		fOceanDistance = 0.2
		fLatitude = ((fDistance - fOceanDistance) / (1.0 - fOceanDistance))
## End Eyeball 1.1                

	# Adjust value using the variation fractal, to mix things up:
	if varFractal is not None:
		fDistance += (128 - varFractal.getHeight(iX, iY)) / (255.0 * 5.0)

## Eyeball 1.1 to allow for jungles on cold eyeball
#	if  fLatitude < 0.2:
	if iEyeballType == 0 and fLatitude < 0.0:
		fLatitude = 0.0
	if iEyeballType > 0 and fLatitude < 0.2:
## End Eyeball 1.1
		fLatitude = 0.2
	elif fLatitude > 1.0:
		fLatitude = 1.0

	return fLatitude

def getInvertedDistanceToCenter(iX, iY, varFractal):
	"""
	Hangover from Discworld - removing it resulted in too much snow and was working so left it in
	:param iX: x coordinate of the plot
	:param iY: y coordinate of the plot.
	:param varFractal: Fractal used to introduce random variations in the calculated distance.
	:return: Calculated distance, limited between 0.0 and 1.0.
	"""
	fDistance = getEyeballLatitude(iX, iY, varFractal)

	# Limit to the range [0, 1]:
	if fDistance < 0:
		fDistance = 0.0
	elif fDistance > 1:
		fDistance = 1.0
	return fDistance

def isOutsideDisc(iX, iY):
	"""
	Checks if a specific plot is outside of the disc, i.e. cold, night side of planet
	:param iX: x coordinate of the plot
	:param iY: y coordinate of the plot.
	:return: True if the plot is outside of the disc, False otherwise.
	"""
	return getEyeballLatitude(iX, iY) == 1.0


def isDesertDisc(iX, iY):
	"""
	Checks if a specific plot is inside, central desert disc, i.e. impassable due to heat of sun.
	:param iX: x coordinate of the plot
	:param iY: y coordinate of the plot.
	:return: True if the plot is outside of the disc, False otherwise.
	"""

	fLatitude = getEyeballLatitude(iX, iY)

	fHorizontal = ((map.getGridWidth() - 1) / 2.0 - iX) / ((map.getGridWidth() - 1) / 2.0)
	fVertical = ((map.getGridHeight() - 1) / 2.0 - iY) / ((map.getGridHeight() - 1) / 2.0)

	fDistance = math.sqrt(fHorizontal * fHorizontal + fVertical * fVertical)

	iEyeballType = map.getCustomMapOption(0)

	fDesertDistance = 0.0
	if iEyeballType == 1:
		fDesertDistance = 0.5
	if iEyeballType == 2:
		fDesertDistance = 0.7

	fEquatorDistance = ((1.0 - fDesertDistance) / 4) + fDesertDistance
	bDesertDisc = 0

## Eyeball 1.1 - allowing for jungles on cold eyeball

	if iEyeballType > 0 and fDistance < fEquatorDistance and fLatitude == 0.2:
#1.1	if fDistance < fEquatorDistance and fLatitude == 0.2:
		bDesertDisc = 1

	return bDesertDisc
