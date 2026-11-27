## Edited by Junuxx 2008
## Modified to yield more usable terrain in unmodded Civ BtS
##############################################################################
## File: Creation.py version 1.04
## Author: Rich Marinaccio
## Copyright 2007 Rich Marinaccio
##############################################################################
## This map script is intended for use with the Fall from Heaven 2 mod for
## Civilization 4
##############################################################################
## Version History
## 1.04 - Added a tuning variable called SoftenPeakPercent which allows you to
## turn a percentage of peaks into hills to perforate the valleys and make
## them less like fortresses. Fixed a bug in detecting network games.
##
## 1.03 - Cleared forest and jungle from 1 tile around starting plot. This mod
## requires high tech levels to clear them and this can be a large hindrance.
## Civ preference with allowForestStart = True(Elves) will not clear the forest.
##
## 1.02 - Added a new civ placement scheme for FFH2 civs. Added a similar scheme
## for FFH2 unique improvements. Improved the way ancient towers are placed.
## Shrank the map yet again due the high percentage of playable land. Softened
## the effect of non-sea level land touching coast.
##
## 1.01 - Improved water area generation to more consistently make interesting
## map shapes. Water spread used to paint itself into a corner, this has been
## fixed. Prevented seas from being divided by small isthmuses. Only peaks and
## ocean will touch the map edge. Filled unreachable areas with peaks, we
## don't want Hyborem spawning there and you know he will if you let him.
## Shrank each map size, as there was too much room to expand for the default
## number of civs for each map size, resulting in no reason to go to war until
## late game. Temporarily added David Reichert's flavour map mod until I can
## do something with starting regions.

##############################################################################
# Tunable variables
##############################################################################

#Decides whether to use the Python random generator or the one that is
#intended for use with civ maps. The Python random has much higher precision
#than the civ one. 53 bits for Python result versus 16 for getMapRand. The
#rand they use is actually 32 bits, but they shorten the result to 16 bits.
#However, the problem with using the Python random is that it may create
#syncing issues for multi-player now or in the future, therefore it must
#be optional.
UsePythonRandom = True

#This variable turns on things that only make sense with Fall from Heaven 2
FFHSpecific = False

#This variable will make a percentage of peaks into hills in order to break
#up the worlds valleys. I set this to zero because I feel it diminishes the
#illusion of differing climates between valleys and looks bad.
SoftenPeakPercent = 0.03

#This variable decides how many tiles of drainage is needed to create a
#river.
RiverThreshold = 5.0

#The amount of rainfall in the dryest desert. Must be between 1.0 and 0.0
MinRainfall = .05

#This number is multiplied by the RiverThreshold to determine when a river
#is large enough to have a 100% chance to flatten nearby hills and peaks.
RiverFactorFlattensAll = 10.0

RiverAddsMoistureRange = .20
RiverAddsMoistureMax = 10.0

#These variables control the frequency of hills and peaks at the lowest
#and highest altitudes
HillChanceAtZero = .15
HillChanceAtOne = .90
PeakChanceAtZero = .0
PeakChanceAtOne = .20

#These valiables control the moisture thresholds for desert and plains
JungleThreshold = .90
PlainsThreshold = .65
DesertThreshold = .25

#These variables control the altitude of tundra and ice. Also, in Civ,
#deserts are supposed to be hot, so we'll limit the altitude for deserts
TundraThreshold = .90
IceThreshold = .93
MaxDesertAltitude = .55

#The type of trees are controlled by altitude. Snowy trees use TundraThreshold.
#Lower than leafy is Jungle.
LeafyAltitude = .30
EvergreenAltitude = .60

#Chance for an oasis to appear in desert
OasisChance = .08

#Map constants - I'm making a point on this map to hardcode nothing, so some
#of these may seem a bit obscure.
#-------------------------------------------------------------------
RegionsPerPlot = 0.008      #Map regions(valleys, seas) per map plot
WaterRegionsPerPlot = 0.002 #Water regions per map plot
MinSeedRange = 5            #Closest that a region seed can be placed to another
MinEdgeRange = 5            #Closest that a region seed can be to map edge
ChanceToGrow = 0.25         #Base chance for each tile in region to grow
EdgeLimit = 2               #Region stops growing this far from edge 
RiverAltitudeSubtraction = 2.0 #Amount subtracted from a plots altitude depending on river size
RiverAltRangeFactor = 2.0   #Amount of RiverThreshold to use for altitude calc
MinRegionSizeStart = 40     #Minimum region size for a starting plot
MinRegionSizeTower = 30     #Minimum region size for a tower placement
WrapX = False               #Dont touch these, this map has no wrap
WrapY = False

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil


from array import array
from random import random,randint,seed
import math
import sys

def GetCivPreferences():
##  Civs without preferences will use default values.
##
##  Civ Name from XML
##  pref = CivPreference(GetInfoType("CIVILIZATION_MALAKIM"))
##
##  Self explanatory.
##  pref.idealMoisture = 0.1
##  pref.idealAltitude = 0.25
##
##  These weights influence the effect of each preference. moistureWeight
##  is hard coded as 1.0 for civ placement
##  pref.altitudeWeight = 0.25
##  pref.distanceWeight = 0.25 #how hard to try to start away from other civs
##  pref.needCoastalStart = False
    
    civPreferenceList = list()
# deleted list content  - Junuxx
    return civPreferenceList

def GetImprovementPreferences():
    #These values are similar to the way civs work except distanceWeight is
    #hardcoded as 1.0
    impPreferenceList = list()
# deleted list contents, no use in BtS - Junuxx    
    return impPreferenceList
    
class ImprovementPreference :
    def __init__(self,improvement):
        self.improvement = improvement
        self.idealAltitude = .5
        self.idealMoisture = .6
        self.altitudeWeight = 1.0
        self.moistureWeight = 1.0
        self.needCoast = False
        self.needWater = False
        self.needHill = False
        self.needFlat = False
        
class CivPreference :
    def __init__(self,civ):
        self.civ = civ
        self.idealAltitude = 0.35
        self.idealMoisture = 0.7
        self.needCoastalStart = False
        self.allowForestStart = True ## Junuxx 
        self.altitudeWeight = 1.0
        self.distanceWeight = 2.0 #distance is most important for generic civs
        return
class PythonRandom :
    def __init__(self):
        return
    def seed(self):
        #Python randoms are not usable in network games.
        if UsePythonRandom:
            self.usePR = True
        else:
            self.usePR = False
        if self.usePR and CyGame().isNetworkMultiPlayer():
            print "Detecting network game. Setting UsePythonRandom to False."
            self.usePR = False
        if self.usePR:
            # Python 'long' has unlimited precision, while the random generator
            # has 53 bits of precision, so I'm using a 53 bit integer to seed the map!
            seed() #Start with system time
            seedValue = randint(0,9007199254740991)
            seed(seedValue)
            print "Random seed (Using Python rands) for this map is %(s)20d" % {"s":seedValue}
            
##            seedValue = 70450052590418
##            seed(seedValue)
##            print "Pre-set seed (Using Pyhon rands) for this map is %(s)20d" % {"s":seedValue}
        else:
            gc = CyGlobalContext()
            self.mapRand = gc.getGame().getMapRand()
            
            seedValue = self.mapRand.get(65535,"Seeding mapRand - PerfectWorld.py")
            self.mapRand.init(seedValue)
            print "Random seed (Using getMapRand) for this map is %(s)20d" % {"s":seedValue}
            
##            seedValue = 56870
##            self.mapRand.init(seedValue)
##            print "Pre-set seed (Using getMapRand) for this map is %(s)20d" % {"s":seedValue}
        return
    def random(self):
        if self.usePR:
            return random()
        else:
            #This formula is identical to the getFloat function in CvRandom. It
            #is not exposed to Python so I have to recreate it.
            fResult = float(self.mapRand.get(65535,"Getting float -PerfectWorld.py"))/float(65535)
#            print fResult
            return fResult
    def randint(self,rMin,rMax):
        #if rMin and rMax are the same, then return the only option
        if rMin == rMax:
            return rMin
        #returns a number between rMin and rMax inclusive
        if self.usePR:
            return randint(rMin,rMax)
        else:
            #mapRand.get() is not inclusive, so we must make it so
            return rMin + self.mapRand.get(rMax + 1 - rMin,"Getting a randint - PerfectWorld.py")
#Set up random number system for global access
PRand = PythonRandom()
#This function converts x and y to an index. Useful in case of future wrapping.
def GetIndex(x,y):
    #Check X for wrap
    if WrapX == True:
        xx = x % mapSize.MapWidth
    elif x < 0 or x >= mapSize.MapWidth:
        return -1
    else:
        xx = x
    #Check y for wrap
    if WrapY == True:
        yy = y % mapSize.MapHeight
    elif y < 0 or y >= mapSize.MapHeight:
        return -1
    else:
        yy = y

    i = yy * mapSize.MapWidth + xx
    return i
#This function converts x and y to an index on river crossing maps.
def GetRxIndex(x,y):
    #Check X for wrap
    if WrapX == True:
        xx = x % (mapSize.MapWidth + 1)
    elif x < 0 or x >= (mapSize.MapWidth + 1):
        return -1
    else:
        xx = x
    #Check y for wrap
    if WrapY == True:
        yy = y % (mapSize.MapHeight + 1)
    elif y < 0 or y >= (mapSize.MapHeight + 1):
        return -1
    else:
        yy = y

    i = yy * (mapSize.MapWidth + 1) + xx
    return i

class MapSize :
    def __init__(self):
        self.MapWidth = 0
        self.MapHeight = 0
        
mapSize = MapSize()

class RegionMap :
    def __init__(self):
        return
    def createRegions(self):
        #Growing the regions directly according to the map size created
        #unsolvable problems for the river system. Instead, I am growing
        #on a map (regionRxMap) that corresponds to rivers rather than
        #map tiles. This ensures rivers have a path from region to
        #region.
        self.L = 0
        self.N = 1
        self.S = 2
        self.E = 3
        self.W = 4
        self.NE = 5
        self.NW = 6
        self.SE = 7
        self.SW = 8
        self.highestRegionAltitude = 0
        numTiles = mapSize.MapWidth*mapSize.MapHeight
        numRx = (mapSize.MapWidth + 1)*(mapSize.MapHeight + 1)
        print "MapWidth = %(mw)d,MapHeight = %(mh)d" % {"mw":mapSize.MapWidth,"mh":mapSize.MapHeight}
        self.regionMap = array('i')
        self.regionRxMap = array('i')
        self.regionList = list()
        self.regionPlotList = list()
        #initialize map
        #The value for unplayable areas will remain -1. playable regions
        #will stop growing when they touch a map edge.
        for i in range(numTiles):
            self.regionMap.append(-1)
        for i in range(numRx):
            self.regionRxMap.append(-1)
        numRegions = int(float(numTiles) * RegionsPerPlot)
        print "numTiles = %(n)d, numRegions = %(w)d" % {"n":numTiles,"w":numRegions}
        for i in range(numRegions):
            #first find a random seed point that is not blocked by
            #previous points
            iterations = 0
            while(True):
                iterations += 1
                if iterations > 10000:
                    raise ValueError, "endless loop in region seed placement"
                seedX = PRand.randint(0,mapSize.MapWidth + 1)
                seedY = PRand.randint(0,mapSize.MapHeight + 1)
                if self.isSeedBlocked(seedX,seedY) == False:
                    region = Region(i,seedX,seedY)
                    self.regionList.append(region)
                    n = GetRxIndex(seedX,seedY)
                    self.regionRxMap[n] = i
                    plot = RegionPlot(i,seedX,seedY)
                    self.regionPlotList.append(plot)
                    #Now fill a 3x3 area to insure a minimum region size
                    for direction in range(1,9,1):
                        xx,yy = self.getXYFromDirection(seedX,seedY,direction)
                        nn = GetRxIndex(xx,yy)
                        self.regionRxMap[nn] = i
                        plot = RegionPlot(i,xx,yy)
                        self.regionPlotList.append(plot)

                    break
##        self.PrintRegionRxMap(False)
        #Now cause the seeds to grow into regions
        iterations = 0
        while(len(self.regionPlotList) > 0):
            iterations += 1
            if iterations > 200000:
                self.PrintRegionRxMap(False)
                raise ValueError, "endless loop in region growth"
            plot = self.regionPlotList[0]
            region = self.getRegionByID(plot.regionID)
            if region.isGrowing == False:
                del self.regionPlotList[0]
                continue
            roomLeft = False
            for direction in range(1,5,1):
                xx,yy = self.getXYFromDirection(plot.x,plot.y,direction)
                i = GetRxIndex(xx,yy)
                if i == -1 or self.rxTouchesMapEdge(xx,yy):
                    if self.canRegionGrowHere(xx,yy,plot.regionID):
                        self.regionRxMap[i] = plot.regionID
                        newPlot = RegionPlot(plot.regionID,xx,yy)
                        self.regionPlotList.append(newPlot)
                    region.isGrowing = False
                    continue
                if self.canRegionGrowHere(xx,yy,plot.regionID):
                    roomLeft = True
                    if PRand.random() < ChanceToGrow:
                        self.regionRxMap[i] = plot.regionID
                        newPlot = RegionPlot(plot.regionID,xx,yy)
                        self.regionPlotList.append(newPlot)
                
                    
            #move plot to the end of the list if room left, otherwise
            #delete it if no room left
            if roomLeft:
                self.regionPlotList.append(plot)
            del self.regionPlotList[0]
            
##        self.PrintRegionRxMap(False)
        #Now convert regionRxMap to regionMap
        for y in range(mapSize.MapHeight + 1):
            for x in range(mapSize.MapWidth + 1):
                i = GetRxIndex(x,y)
                regionID = self.regionRxMap[i]
                if regionID != -1:
                    region = self.getRegionByID(regionID)
                    for direction in range(5,9,1):
                        xx,yy = self.plotFromRx(x,y,direction)
                        ii = GetIndex(xx,yy)
                        if ii != -1:
                            self.regionMap[ii] = regionID
                            newPlot = RegionPlot(regionID,xx,yy)
                            region.plotList.append(newPlot)
                
        #Mark border tiles and neighbor regions
        for region in self.regionList:
            for plot in region.plotList:
                i = GetIndex(plot.x,plot.y)
                for direction in range(1,5,1):
                    if direction == 1:#N
                        xx = plot.x
                        yy = plot.y + 1
                    elif direction == 2:#S
                        xx = plot.x
                        yy = plot.y - 1
                    elif direction == 3:#E
                        xx = plot.x + 1
                        yy = plot.y
                    else:#W
                        xx = plot.x - 1
                        yy = plot.y
                    ii = GetIndex(xx,yy)
                    if ii != -1 and self.regionMap[ii] != -1 and \
                    self.regionMap[ii] != region.ID:
                        plot.bBorder = True
                        plot.bEdge = True
                        AppendUnique(region.neighborList,self.regionMap[ii])
                    elif self.regionMap[ii] == -1:
                        plot.bEdge = True
                        
                    
##        self.PrintRegionMap(False)
        
        #Now choose areas to be water
        numWaterRegions = int(float(numTiles) * WaterRegionsPerPlot)
        print "numTiles = %(n)d, numWaterRegions = %(w)d" % {"n":numTiles,"w":numWaterRegions}
        self.regionList = ShuffleList(self.regionList)
        #Try to start with the region in the middle (there is a low chance that there isn't one)
        i = GetIndex(mapSize.MapWidth/2, mapSize.MapHeight/2)
        regionID = self.regionMap[i]
        if regionID == -1:
            self.regionList[0].isWater = True
        else:
            region = self.getRegionByID(regionID)
            region.isWater = True
            
        for i in range(numWaterRegions):
            self.regionList = ShuffleList(self.regionList)
            
            for nRegion in self.regionList:
                nRegion.waterNeighborCount = nRegion.getWaterNeighborCount()
                
            self.regionList.sort(lambda x,y:cmp(x.waterNeighborCount,y.waterNeighborCount))

            for nRegion in self.regionList:
                if nRegion.waterNeighborCount > 0 and nRegion.isWater == False:
                    nRegion.isWater = True
                    break
##        self.PrintRegionMap(True)
        
        #Now fill any non-areas adjacent to water with the water area
        for region in self.regionList:
            if region.isWater == False:
                continue
            regionExpanding = True
            while(regionExpanding):
                regionExpanding = region.expandWaterRegion()                    
                                                 
        return
    def canRegionGrowHere(self,x,y,regionID):
        i = GetRxIndex(x,y)
        if self.regionRxMap[i] != -1:
            return False
        region = self.getRegionByID(regionID)
        if not region.isGrowing:
            return False
        assume = True
        for direction in range(1,9,1):
            xx,yy = self.getXYFromDirection(x,y,direction)
            ii = GetRxIndex(xx,yy)
            if ii == -1 or self.regionRxMap[ii] == regionID:
                continue
            elif self.regionRxMap[ii] == -1:
                continue
            else:
                assume = False
        return assume
    def rxTouchesMapEdge(self,x,y):
        if x >= (mapSize.MapWidth + 1) - EdgeLimit or x < EdgeLimit:
            return True
        if y >= (mapSize.MapHeight + 1) - EdgeLimit or y < EdgeLimit:
            return True
        return False
    def plotFromRx(self,rxX,rxY,direction):
        if direction == self.NE:
            x = rxX
            y = rxY
        elif direction == self.NW:
            x = rxX - 1
            y = rxY
        elif direction == self.SE:
            x = rxX
            y = rxY - 1
        else:#SW
            x = rxX - 1
            y = rxY - 1
        #check for validity 
        if x < 0 or x >= mapSize.MapWidth:
            return -1,-1
        if y < 0 or y >= mapSize.MapHeight:
            return -1,-1
        return x,y
        
    def getXYFromDirection(self,x,y,direction):
        xx = x
        yy = y
        if direction == self.N:
            yy += 1
        elif direction == self.S:
            yy -= 1
        elif direction == self.E:
            xx += 1
        elif direction == self.W:
            xx -= 1
        elif direction == self.NW:
            yy += 1
            xx -= 1
        elif direction == self.NE:
            yy += 1
            xx += 1
        elif direction == self.SW:
            yy -= 1
            xx -= 1
        elif direction == self.SE:
            yy -= 1
            xx += 1
        return xx,yy
    def isSeedBlocked(self,seedX,seedY):
        for region in self.regionList:
            if seedX > region.seedX - MinSeedRange and seedX < region.seedX + MinSeedRange:
                if seedY > region.seedY - MinSeedRange and seedY < region.seedY + MinSeedRange:
                    return True
        #Check for edge
        if seedX < MinEdgeRange or seedX >= (mapSize.MapWidth + 1) - MinEdgeRange:
            return True
        if seedY < MinEdgeRange or seedY >= (mapSize.MapHeight + 1) - MinEdgeRange:
            return True
        return False
    
    def getRegionByID(self,ID):
        for region in self.regionList:
            if region.ID == ID:
                return region
        return None
    def PrintRegionMap(self,bShowWater):
        print "Region Map"
        for y in range(mapSize.MapHeight - 1,-1,-1):
            lineString = ""
            for x in range(mapSize.MapWidth):
                mapLoc = self.regionMap[GetIndex(x,y)]
                region = self.getRegionByID(mapLoc)
                if mapLoc == -1:
                    lineString += "X"
                elif bShowWater and region.isWater == True:
                    lineString += " "
                else:
                    lineString += chr(mapLoc + 33)
            print lineString
        lineString = " "
        print lineString
    def PrintRegionRxMap(self,bShowWater):
        print "Region Map"
        for y in range(mapSize.MapHeight,-1,-1):
            lineString = ""
            for x in range(mapSize.MapWidth + 1):
                mapLoc = self.regionRxMap[GetRxIndex(x,y)]
                region = self.getRegionByID(mapLoc)
                if mapLoc == -1:
                    lineString += "X"
                elif bShowWater and region.isWater == True:
                    lineString += " "
                else:
                    lineString += chr(mapLoc + 33)
            print lineString
        lineString = " "
        print lineString
    def PrintRegionList(self):
        print "Number of regions = %(n)d" % {"n":len(self.regionList)}
        for region in self.regionList:
            print str(region)

        return
    
regMap = RegionMap()
class RegionPlot :
    def __init__(self,ID,x,y):
        self.regionID = ID
        self.x = x
        self.y = y
        self.gateRx = -1
        self.bBorder = False
        self.bEdge = False
class Region :
    def __init__(self,ID,seedX,seedY):
        self.ID = ID
        self.seedX = seedX
        self.seedY = seedY
        self.isGrowing = True
        self.neighborList = list()
        self.gateRegion = -1
        self.gatePlot = None
        self.plotList = list()
        self.isWater = False
        self.altitude = 0.0
        self.moisture = 1.0
    def __str__(self):
        string = "ID=%(id)d(%(c)s), size=%(s)d, altitude=%(a)d \n" % {"id":self.ID,"c":chr(self.ID + 33),"s":len(self.plotList),"a":self.altitude}
        string += "gateRegion=%(id)d(%(c)s) \n" % {"id":self.gateRegion,"c":chr(self.gateRegion + 33)}
        string += "    " + self.NeighborListString() + "\n"
        return string
    def NeighborListString(self):
        string = "["
        for ID in self.neighborList: 
            string += chr(ID + 33) + ","
        string += "]"
        return string
    def getWaterNeighborCount(self):
        count = 0
        for regionID in self.neighborList:
            region = regMap.getRegionByID(regionID)
            if region.isWater == True:
                count += 1
        return count
    def getBorderPlotList(self,neighborID):
        borderPlotList = list()
        borderPlotCount = 0
        for plot in self.plotList:
            if plot.bBorder == True:
                borderPlotCount += 1
                for direction in range(1,5,1):
                    if direction == 1:#N
                        xx = plot.x
                        yy = plot.y + 1
                    elif direction == 2:#S
                        xx = plot.x
                        yy = plot.y - 1
                    elif direction == 3:#E
                        xx = plot.x + 1
                        yy = plot.y
                    else:#W
                        xx = plot.x - 1
                        yy = plot.y
                    ii = GetIndex(xx,yy)
                    if ii != -1 and regMap.regionMap[ii] == neighborID:
                        borderPlotList.append(plot)
                        break
        print "borderPlotCount=%(bc)d" % {"bc":borderPlotCount}
        return borderPlotList
    def getGateListToNeighbor(self,neighborID):
        gateListToNeighbor = list()
        for rPlot in self.gateList:
            if riverMap.isRxTouchingRegion(rPlot.x,rPlot.y,neighborID):
                gateListToNeighbor.append(rPlot)
##        print "%(ng)d gates from %(s)d to %(n)d" % \
##        {"ng":len(gateListToNeighbor),"s":self.ID,"n":neighborID}
        return gateListToNeighbor
            
    def defineValidGateList(self):
        #This function is called in createFlowMap so the riverMap functions
        #can be called from here. We now complile a list of all possible river
        #gates
        self.gateList = list()
        for rxY in range(mapSize.MapHeight + 1):
            for rxX in range(mapSize.MapWidth + 1):
                if riverMap.isRxTouchingRegion(rxX,rxY,self.ID):
                    if riverMap.isValidFullGate(self.ID,rxX,rxY):
                        rPlot = RiverPlot(rxX,rxY,-1,self.ID)
                        self.gateList.append(rPlot)
        return
    def expandWaterRegion(self):
        expanded = False
        for plot in self.plotList:
            for direction in range(1,5,1):
                if direction == 1:#N
                    xx = plot.x
                    yy = plot.y + 1
                elif direction == 2:#S
                    xx = plot.x
                    yy = plot.y - 1
                elif direction == 3:#E
                    xx = plot.x + 1
                    yy = plot.y
                else:#W
                    xx = plot.x - 1
                    yy = plot.y
                ii = GetIndex(xx,yy)
                if ii != -1 and regMap.regionMap[ii] == -1:
                    naPlot = RegionPlot(self.ID,xx,yy)
                    regMap.regionMap[ii] = self.ID
                    self.plotList.append(naPlot)
                    expanded = True
                    break
        return expanded
    
    def getGatedNeighborList(self):
        gatedList = list()
        for regionID in self.neighborList:
            region = regMap.getRegionByID(regionID)
            if region.isWater or region.gateRegion != -1:
                validGateList = self.getGateListToNeighbor(regionID)
                if len(validGateList) > 0:
                    gatedList.append(region.ID)    
        return gatedList
    
    def getDistanceToClosestBorderPlot(self,plot):
        minDistance = 100.0
        for bPlot in self.plotList:
            if bPlot.bEdge == False:
                continue
            distance = GetDistance(plot.x,plot.y,bPlot.x,bPlot.y)
            if distance < minDistance:
                minDistance = distance
        return minDistance
                
    #In this case the center is the plot farthest from any border
    def getCenter(self):
        maxDistance = 0.0
        center = None
        for plot in self.plotList:
            distance = self.getDistanceToClosestBorderPlot(plot)
            if maxDistance < distance:
                maxDistance = distance
##                print "maxDistance= %(m)f, plot.x= %(x)d, plot.y=%(y)d" % \
##                {"m":maxDistance,"x":plot.x,"y":plot.y}
                center = plot
            
        return center
           
class RiverMap :
    def __init__(self):
        return
    def createRiverMap(self):
        self.createFlowMap()
        self.calculateWetAndDry()
        self.riverMap = array('f')
        for i in range((mapSize.MapHeight + 1) * (mapSize.MapWidth + 1)):
            self.riverMap.append(0)
        for y in range(mapSize.MapHeight + 1):
            for x in range(mapSize.MapWidth + 1):
                i = self.getRiverIndex(x,y)
                direction = self.flowMap[i]
                regionID = self.getRegion(x,y)
                region = regMap.getRegionByID(regionID)
                xx = x
                yy = y
                while direction != -1 and direction != self.L:
                    xx,yy = self.getXYFromDirection(xx,yy,direction)
                    ii = self.getRiverIndex(xx,yy)
                    self.riverMap[ii] += MinRainfall + (1.0 - MinRainfall) * region.moisture
                    direction = self.flowMap[ii]
        
        return
    def createFlowMap(self):
        #Start with an outflow from the region, then randomly decide which neighbors
        #will flow into this square by how many choices that neighbor has. If the
        #neighbor has only one choice, then the chance is 100 percent. At least
        #one neighbor must be chosen unless it is not possible, otherwise the
        #process might end before each tile is set. Then put each chosen neighbor
        #on the stack to be processed the same way.
        self.L = 0
        self.N = 1
        self.S = 2
        self.E = 3
        self.W = 4
        self.NE = 5
        self.NW = 6
        self.SE = 7
        self.SW = 8
        self.heightMap = array('d')
        self.flowMap = array('i')
        for i in range((mapSize.MapHeight + 1) * (mapSize.MapWidth + 1)):
            self.flowMap.append(-1)
            self.heightMap.append(-1.0)
        self.defineGates()
        print "Gates Defined !!!!!!!!!!!!!!!!!!!!!!!!"
        for region in regMap.regionList:
            if region.isWater == True:
                continue
            #randomly choose an outflow gate
##            print "region.gateRegion = %(gr)d" % {"gr":region.gateRegion}
            validGateList = region.getGateListToNeighbor(region.gateRegion)
            if len(validGateList) == 0:
                print "validGateList == 0!!!!!!!!!!!!!!!!!!!!"
                print "region = %(r)s" % {"r":str(region)}
                gRegion = regMap.getRegionByID(region.gateRegion)
                print "gateRegion = %(g)s" % {"g":str(gRegion)}
                raise ValueError, "region has neighbor but no valid gates. see debug file"
            region.gatePlot = validGateList[PRand.randint(0,len(validGateList)-1)]
            rxX = region.gatePlot.x
            rxY = region.gatePlot.y
            rxI = self.getRiverIndex(rxX,rxY)
            #set flow so that it is pointing out of region
            iterations = 0
            while(True):
                iterations += 1
                if iterations > 100:
                    raise ValueError, "endless loop in gate setter"
                gateRegion = regMap.getRegionByID(region.gateRegion)
                if gateRegion.isWater:
                        self.flowMap[rxI] = self.L
                        self.heightMap[rxI] = 0.01
                        break
                #pick random cardinal direction
                direction = PRand.randint(1,4)
##                print direction
                xx,yy = self.getXYFromDirection(rxX,rxY,direction)
                if self.isRxInRegion(xx,yy,region.gateRegion):
                    self.flowMap[rxI] = direction
                    self.heightMap[rxI] = 0.01
                    break
                
        #Now create heightmap. Start from each gate and increase altitude of
        #neighbors by a random percentage, and then place each neighbor on a
        #queue for similar processing. Randomize the queue order for each pass.
        #This method should avoid lakes.

        #Place all gates on queue.
        plotList = list()
        regMap.PrintRegionList()
        for region in regMap.regionList:
            if region.gatePlot == None:
                continue
            rxX = region.gatePlot.x
            rxY = region.gatePlot.y
##            print "rxX=%(x)d, rxY=%(y)d" % {"x":rxX,"y":rxY}
            riverPlot = RiverPlot(rxX,rxY,0,region.ID)
            plotList.append(riverPlot)
##        print "hi"
        while(len(plotList) > 0):
##            print "len plotList = v"
##            print len(plotList)
            count = len(plotList)
            plotList = ShuffleList(plotList)
            for n in range(count):
                thisPlot = plotList.pop(0)#queue method, not stack
##                print "popping"
                rxI = self.getRiverIndex(thisPlot.x,thisPlot.y)
                altitude = self.heightMap[rxI]
                for direction in range(1,5,1):
                    x,y = self.getXYFromDirection(thisPlot.x,thisPlot.y,direction)
                    rxII = self.getRiverIndex(x,y)
##                    print "rxII=%(i)d, x=%(x)d, y=%(y)d, heightMap=%(h)f, isRxInRegion=%(ir)d" % \
##                    {"i":rxII,"x":x,"y":y,"h":self.heightMap[rxII],"ir":self.isRxInRegion(x,y,thisPlot.regionID)}
                    if rxII != -1 and self.heightMap[rxII] == -1.0 and \
                    self.isRxInRegion(x,y,thisPlot.regionID):
                        randomScaler = 1.0 + float(PRand.randint(1,20))/100.0 
                        self.heightMap[rxII] = altitude * randomScaler
                        newPlot = RiverPlot(x,y,0,thisPlot.regionID)
                        plotList.append(newPlot)
##                        print "newPlot appended"
        #Create flow map
        for y in range(mapSize.MapHeight + 1):
            for x in range(mapSize.MapWidth + 1):
                paths = self.getPossiblePaths(x,y)
                if len(paths) > 0:
                    i = self.getRiverIndex(x,y)
                    pathIndex = PRand.randint(0,len(paths)-1)
                    self.flowMap[i] = paths[pathIndex]
                
        return
    #Dryness should be calculated by getting the highest altitude
    #region and making it's base the wettest region. Then eliminate
    #those regions from the list. Then get the highest of the remaining
    #regions and make it's base the dryest region.
    def calculateWetAndDry(self):
        regionList = list()
        for region in regMap.regionList:
            regionList.append(region)

        regionList.sort(lambda x,y:cmp(x.altitude,y.altitude))
        regionList.reverse()

        region = regionList[0]
        while(region.altitude > 0):
            region = regMap.getRegionByID(region.gateRegion)
            if region.altitude == 1:
                self.wetSpot = riverMap.plotFromRx(region.gatePlot.x,region.gatePlot.y,riverMap.SW)

        #Now calculate moisture for each region
        minMoisture = 1.0
        for region in regMap.regionList:
            gate = region.gatePlot
            if gate == None:
                continue
            wetSpotX,wetSpotY = self.wetSpot
            distance = GetDistance(gate.x,gate.y,wetSpotX,wetSpotY)
   #        some degree of randomness in region moisture?   - Junuxx  
            region.moisture = 0.10 + 0.80 * PRand.random()
   #        region.moisture = 0.5 * ( PRand.random() + PRand.random())
            minMoisture = min(region.moisture,minMoisture)
   #     scaler = 1.0/(1.0 - minMoisture)
   #     for region in regMap.regionList:
   #         region.moisture = (region.moisture - minMoisture) * scaler
            
        return
    def defineGates(self):
        #Now each region picks one gate that is not in the current gate line
        #to avoid recursive loops
        numRegions = len(regMap.regionList)
        numGatesPlaced = 0
        iterations = 0
        #water is considered gated for this purpose
        for region in regMap.regionList:
            region.defineValidGateList()
            #regions should always have gates
            if len(region.gateList) == 0:
                print str(region)
                print "has no gates!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                regMap.PrintRegionMap(False)
                raise ValueError, "region has no gates"
        while numGatesPlaced < numRegions:
            if iterations > 500:
                raise ValueError, "Endless loop occured in gate placement"
                break
            else:
                iterations += 1
            regMap.regionList = ShuffleList(regMap.regionList)
            for region in regMap.regionList:
                if region.gateRegion == -1:
                    gatedNeighborList = region.getGatedNeighborList()
                    if len(gatedNeighborList) > 0:
                        gatedNeighborList = ShuffleList(gatedNeighborList)
                        region.gateRegion = gatedNeighborList[0]
                        if region.isWater:
                            region.altitude = 0
                        else:
                            gateRegion = regMap.getRegionByID(region.gateRegion)
                            region.altitude = gateRegion.altitude + 1
##                        print "region %(r)d gateRegion is %(g)d" % \
##                        {"r":region.ID,"g":region.gateRegion}
                        numGatesPlaced += 1            
    def isValidHalfGate(self,regionID,rxX,rxY):
        #A valid half gate is a rx that is not in a region, touches
        #only 2 regions and is 4-connected to an rx that is in the region
        regionList = list()
        for direction in range(5,9,1):
            px,py = self.plotFromRx(rxX,rxY,direction)
            i = GetIndex(px,py)
            pRegID = regMap.regionMap[i]
            if pRegID == -1:
                return False
            AppendUnique(regionList,pRegID)
        if len(regionList) != 2:
            return False
        if self.isRxInRegion(rxX,rxY,regionID):
            return False
        for direction in range(1,5,1):
            xx,yy = self.getXYFromDirection(rxX,rxY,direction)
            if self.isRxInRegion(xx,yy,regionID):
                return True
        return False
    def isValidFullGate(self,regionID,rxX,rxY):
        if not self.isValidHalfGate(regionID,rxX,rxY):
            return False
        region = regMap.getRegionByID(regionID)
        for nRegionID in region.neighborList:
            if self.isValidHalfGate(nRegionID,rxX,rxY):
                return True
            for direction in range(1,5,1):
                xx,yy = self.getXYFromDirection(rxX,rxY,direction)
                if self.isValidHalfGate(nRegionID,rxX,rxY):
                    return True
        return False
                
    def getPossiblePaths(self,rxX,rxY):
        possiblePaths = list()
        regionID = self.getRegion(rxX,rxY)
        if regionID == -1:
            return possiblePaths
        region = regMap.getRegionByID(regionID)
        if region.isWater == True:
            return possiblePaths
        rxI = self.getRiverIndex(rxX,rxY)
        altitude = self.heightMap[rxI]
        rejectedDirection = self.L
        for direction in range(1,5,1):
            x,y = self.getXYFromDirection(rxX,rxY,direction)
            i = self.getRiverIndex(x,y)
            if self.isRxInRegion(x,y,regionID):
                if self.heightMap[i] > altitude:
                    if rejectedDirection == self.L:
                        rejectedDirection = self.getOppositeDirection(direction)
                    else:
                        rejectedDirection = self.L
            
        for direction in range(1,5,1):
            x,y = self.getXYFromDirection(rxX,rxY,direction)
            if self.isRxInRegion(x,y,regionID) or \
            (x == region.gatePlot.x and y == region.gatePlot.y) :
                i = self.getRiverIndex(x,y)
                if i != -1 and self.heightMap[i] < altitude:
                    possiblePaths.append(direction)

        if len(possiblePaths) > 1:
            for n in range(len(possiblePaths)):
                if rejectedDirection == possiblePaths[n]:
                    del possiblePaths[n]
                    break
            
        return possiblePaths
    def fillInLake(self,rxX,rxY):
        rxI = self.getRiverIndex(rxX,rxY)
        altitude = self.heightMap[rxI]
        regionID = self.getRegion(rxX,rxY)
        lowestNeighbor = 1.0
        for direction in range(1,5,1):
            x,y = self.getXYFromDirection(rxX,rxY,direction)
            i = self.getRiverIndex(x,y)
            if self.isRxInRegion(x,y,regionID) == True:
                if self.heightMap[i] < lowestNeighbor:
                    lowestNeighbor = self.heightMap[i]
        if altitude < lowestNeighbor:
            self.heightMap[rxI] = altitude + ((lowestNeighbor - altitude)/2.0)
        else:
            self.heightMap[rxI] = altitude * 1.05
    def isLake(self,rxX,rxY):
        rxI = self.getRiverIndex(rxX,rxY)
        altitude = self.heightMap[rxI]
        regionID = self.getRegion(rxX,rxY)
        lowestNeighbor = 1.0
        for direction in range(1,5,1):
            x,y = self.getXYFromDirection(rxX,rxY,direction)
            i = self.getRiverIndex(x,y)
            if self.isRxInRegion(x,y,regionID) == True:
                if self.heightMap[i] < lowestNeighbor:
                    lowestNeighbor = self.heightMap[i]
        if lowestNeighbor >= altitude:
            return True
        return False
    def isOutFlowGate(self,rxX,rxY):
        for region in regMap.regionList:
            if region.isWater == False:
                gateRxX,gateRxY = self.rxFromPlot(region.gatePlot.x,region.gatePlot.y,self.SW)
                if gateRxX == rxX and gateRxY == rxY:
                    return True
        return False

    def getOppositeDirection(self,direction):
        opposite = self.L
        if direction == self.N:
            opposite = self.S
        elif direction == self.S:
            opposite = self.N
        elif direction == self.E:
            opposite = self.W
        elif direction == self.W:
            opposite = self.E
        return opposite
    def getXYFromDirection(self,x,y,direction):
        xx = x
        yy = y
        if direction == self.N:
            yy += 1
        elif direction == self.S:
            yy -= 1
        elif direction == self.E:
            xx += 1
        elif direction == self.W:
            xx -= 1
        return xx,yy
    def getRiverIndex(self,x,y):
        if x < 0 or x >= mapSize.MapWidth + 1:
            return -1
        else:
            xx = x
        if y < 0 or y >= mapSize.MapHeight + 1:
            return -1
        else:
            yy = y

        i = yy * (mapSize.MapWidth + 1) + xx
        return i
    def isRxInRegion(self,x,y,regionID):
        #Rxs on the border are not in region. All plots touching rx must
        #be in region
        for direction in range(5,9,1):
            xx,yy = self.plotFromRx(x,y,direction)
            i = GetIndex(xx,yy)
            if i == -1 or regMap.regionMap[i] != regionID:
                return False
        return True
    def getRegion(self,x,y):
        #Rxs on the border are not in region. All plots touching rx must
        #be in region, unless this is the gate for that region
        xx,yy = self.plotFromRx(x,y,self.SW)
        i = GetIndex(xx,yy)
        regionID = regMap.regionMap[i]
        invalidRegion = False
        for direction in range(5,9,1):
            xx,yy = self.plotFromRx(x,y,direction)
            i = GetIndex(xx,yy)
            nRegionID = regMap.regionMap[i]
            if nRegionID == -1:
                continue
            #test if this main plot is gate for this region
            nRegion = regMap.getRegionByID(nRegionID)
            if nRegion.gatePlot != None and \
            x == nRegion.gatePlot.x and y == nRegion.gatePlot.y:
                return nRegionID
            if nRegionID != regionID:
                invalidRegion = True
        if invalidRegion:
            return -1
        return regionID
    def isRxTouchingRegion(self,x,y,regionID):
        #Check all four plots
        plotX,plotY = self.plotFromRx(x,y,self.NW)
        i = GetIndex(plotX,plotY)
        if i != -1 and regMap.regionMap[i] == regionID:
            return True
        plotX,plotY = self.plotFromRx(x,y,self.NE)
        i = GetIndex(plotX,plotY)
        if i != -1 and regMap.regionMap[i] == regionID:
            return True
        plotX,plotY = self.plotFromRx(x,y,self.SW)
        i = GetIndex(plotX,plotY)
        if i != -1 and regMap.regionMap[i] == regionID:
            return True
        plotX,plotY = self.plotFromRx(x,y,self.SE)
        i = GetIndex(plotX,plotY)
        if i != -1 and regMap.regionMap[i] == regionID:
            return True
        return False
    def rxFromPlot(self,plotX,plotY,direction):
        if direction == self.SW:
            x = plotX
            y = plotY
        elif direction == self.SE:
            x = plotX + 1
            y = plotY
        elif direction == self.NW:
            x = plotX
            y = plotY + 1
        else:#NE
            x = plotX + 1
            y = plotY + 1
        #check for validity 
        if x < 0 or x >= mapSize.MapWidth + 1:
            return -1,-1
        if y < 0 or y >= mapSize.MapHeight + 1:
            return -1,-1
        return x,y

    def plotFromRx(self,rxX,rxY,direction):
        if direction == self.NE:
            x = rxX
            y = rxY
        elif direction == self.NW:
            x = rxX - 1
            y = rxY
        elif direction == self.SE:
            x = rxX
            y = rxY - 1
        else:#SW
            x = rxX - 1
            y = rxY - 1
        #check for validity 
        if x < 0 or x >= mapSize.MapWidth:
            return -1,-1
        if y < 0 or y >= mapSize.MapHeight:
            return -1,-1
        return x,y
    def PrintFlowMap(self):
        print "Flow Map"
        for y in range(mapSize.MapHeight,-1,-1):
            lineString = ""
            for x in range(mapSize.MapWidth + 1):
                mapLoc = self.flowMap[self.getRiverIndex(x,y)]
                if mapLoc == -1:
                    lineString += "X"
                elif mapLoc == self.N:
                    lineString += "N"
                elif mapLoc == self.S:
                    lineString += "S"
                elif mapLoc == self.E:
                    lineString += "E"
                elif mapLoc == self.W:
                    lineString += "W"
                else:
                    lineString += "X"
            print lineString
        lineString = " "
        print lineString
    
riverMap = RiverMap()
class RiverPlot :
    def __init__(self,x,y,direction,regionID):
        self.x = x
        self.y = y
        self.direction = direction
        self.regionID = regionID
        return
class PlotMap :
    def __init__(self):
        return
    def createPlotMap(self):
        self.OCEAN = 0
        self.LAND = 1
        self.HILLS = 2
        self.PEAK = 3
        self.L = 0
        self.N = 1
        self.S = 2
        self.E = 3
        self.W = 4
        self.NE = 5
        self.NW = 6
        self.SE = 7
        self.SW = 8
        
        self.plotMap = array('i')
        scrambledPlotList = list()
        regMap.regionList.sort(lambda n,m: cmp(n.altitude,m.altitude))
        regMap.regionList.reverse()
        regMap.highestRegionAltitude = regMap.regionList[0].altitude

        for y in range(mapSize.MapHeight):
            for x in range(mapSize.MapWidth):
                self.plotMap.append(self.OCEAN)
                scrambledPlotList.append((x,y))
        scrambledPlotList = ShuffleList(scrambledPlotList)
        
        for n in range(len(scrambledPlotList)):
            x,y = scrambledPlotList[n]
            i = GetIndex(x,y)
            if self.shouldPlacePeak(x,y):
                if self.plotMap[i] != self.HILLS:
                    self.plotMap[i] = self.PEAK
            else:
                regionID = regMap.regionMap[i]
                region = regMap.getRegionByID(regionID)
                if not region.isWater:
                    self.plotMap[i] = self.LAND
                self.placeLandInWater(x,y)
                
        for n in range(len(scrambledPlotList)):
            x,y = scrambledPlotList[n]
            i = GetIndex(x,y)
            regionID = regMap.regionMap[i]
            if regionID == -1:
                continue
            region = regMap.getRegionByID(regionID)
            if region.isWater and plotMap.plotMap[i] != plotMap.OCEAN:
                for direction in range(1,5,1):
                    xx,yy = self.getXYFromDirection(x,y,direction)
                    ii = GetIndex(xx,yy)
                    nRegionID = regMap.regionMap[ii]
                    if nRegionID == -1:
                        continue
                    nRegion = regMap.getRegionByID(nRegionID)
                    if not nRegion.isWater:
                        regMap.regionMap[i] = nRegionID
                        break                   
                        
        for n in range(len(scrambledPlotList)):
            x,y = scrambledPlotList[n]
            i = GetIndex(x,y)
            #Decide if hill or peak should be here
            if self.plotMap[i] == self.LAND:
                altitude = GetPlotAltitude(x,y)
                hillChanceRange = HillChanceAtOne - HillChanceAtZero
                hillChance = HillChanceAtZero + (altitude * hillChanceRange)
                if PRand.random() < hillChance:
                    self.plotMap[i] = self.HILLS
                peakChanceRange = PeakChanceAtOne - PeakChanceAtZero
                peakChance = PeakChanceAtZero + (altitude * peakChanceRange)
                if PRand.random() < peakChance:
                    self.plotMap[i] = self.PEAK
                #now there's a chance to flatten it again!
                if self.plotMap[i] != self.LAND:
                    riverSize = GetRiverSize(x,y)
                    maxRiverSize = float(RiverThreshold) * RiverFactorFlattensAll
                    riverSize = min(maxRiverSize,riverSize)
                    flattenChance = riverSize/maxRiverSize
##                    print flattenChance
                    if PRand.random() < flattenChance:
                        self.plotMap[i] = self.LAND
            #now make sure that rivers are not flowing between peaks
            if self.plotMap[i] == self.PEAK:
                if self.shouldFlattenRiverPeak(x,y):
                    riverSize = GetRiverSize(x,y)
                    maxRiverSize = float(RiverThreshold) * RiverFactorFlattensAll
                    if riverSize > maxRiverSize:
                        self.plotMap[i] = self.LAND
                    else:
                        self.plotMap[i] = self.HILLS
                        
        #Now for SoftenPeakPercent of peaks, make them hills
        for y in range(1,mapSize.MapHeight - 1):
            for x in range(1,mapSize.MapWidth - 1):
                i = GetIndex(x,y)
                if self.plotMap[i] == self.PEAK:
                    if SoftenPeakPercent >= PRand.random():
                        self.plotMap[i] = self.HILLS
        
        #Now make sure there are no passable areas that are blocked in
##        self.PrintPlotMap()
        areaMap = Areamap(mapSize.MapWidth,mapSize.MapHeight)
        areaMap.findImpassableAreas()
##        areaMap.PrintAreaMap()
        for i in range(mapSize.MapWidth*mapSize.MapHeight):
            if areaMap.areaMap[i] == 0:
                if self.plotMap[i] != self.PEAK:
                    self.plotMap[i] = self.PEAK
                else:
                    areaMap.areaMap[i] = 1
                
##        areaMap.PrintAreaMap()
                        
    def shouldFlattenRiverPeak(self,x,y):
        direction = riverMap.NW 
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        if riverMap.riverMap[rxI] > RiverThreshold:
            pDir = direction
            xx,yy = self.getXYFromDirection(x,y,pDir)
            ii = GetIndex(xx,yy)
            if self.plotMap[ii] == self.PEAK:
                return True
            if riverMap.flowMap[rxI] == riverMap.E:
                pDir = self.N
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
            if riverMap.flowMap[rxI] == riverMap.S:
                pDir = self.W
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
                
        direction = riverMap.NE 
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        if riverMap.riverMap[rxI] > RiverThreshold:
            pDir = direction
            xx,yy = self.getXYFromDirection(x,y,pDir)
            ii = GetIndex(xx,yy)
            if self.plotMap[ii] == self.PEAK:
                return True
            if riverMap.flowMap[rxI] == riverMap.W:
                pDir = self.N
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
            if riverMap.flowMap[rxI] == riverMap.S:
                pDir = self.E
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
                
        direction = riverMap.SE 
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        if riverMap.riverMap[rxI] > RiverThreshold:
            pDir = direction
            xx,yy = self.getXYFromDirection(x,y,pDir)
            ii = GetIndex(xx,yy)
            if self.plotMap[ii] == self.PEAK:
                return True
            if riverMap.flowMap[rxI] == riverMap.W:
                pDir = self.S
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
            if riverMap.flowMap[rxI] == riverMap.N:
                pDir = self.E
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
                
        direction = riverMap.SW 
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        if riverMap.riverMap[rxI] > RiverThreshold:
            pDir = direction
            xx,yy = self.getXYFromDirection(x,y,pDir)
            ii = GetIndex(xx,yy)
            if self.plotMap[ii] == self.PEAK:
                return True
            if riverMap.flowMap[rxI] == riverMap.E:
                pDir = self.S
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
            if riverMap.flowMap[rxI] == riverMap.N:
                pDir = self.W
                xx,yy = self.getXYFromDirection(x,y,pDir)
                ii = GetIndex(xx,yy)
                if self.plotMap[ii] == self.PEAK:
                    return True
                
        return False
    
    def placeLandInWater(self,x,y):
        i = GetIndex(x,y)
        regionID = regMap.regionMap[i]
        if regionID == -1:
            return False 
        region = regMap.getRegionByID(regionID)
        borderPlotIsLand = False 
        for direction in range(1,5,1):
            xx,yy = self.getXYFromDirection(x,y,direction)
            ii = GetIndex(xx,yy)
            if ii == -1:
                continue
            if self.plotMap[ii] != self.OCEAN and \
            regMap.regionMap[ii] != regionID:
                if IsPlotTouchingRiver(x,y):
                    oceanNeighborTouchingRiver = False
                    for dir2 in range(1,5,1):
                        xxx,yyy = self.getXYFromDirection(x,y,dir2)
                        iii = GetIndex(xxx,yyy)
                        if self.plotMap[iii] == self.OCEAN and \
                        IsPlotTouchingRiver(xxx,yyy):
                            oceanNeighborTouchingRiver = True
                    if oceanNeighborTouchingRiver == False:       
                        continue
                oppDirection = self.getOppositeDirection(direction)
                xxx,yyy = self.getXYFromDirection(x,y,oppDirection)
                if not IsPlotSurroundedByOcean(xxx,yyy):
                    continue
                if PRand.randint(0,1) == 0:
                    nRegion = regMap.getRegionByID(regMap.regionMap[ii])
                    if nRegion != None:
                        print "placing land in water"
                        if nRegion.altitude < 2:
                            self.plotMap[i] = self.LAND
                        elif nRegion.altitude < 3 and regMap.highestRegionAltitude >= 3:
                            self.plotMap[i] = self.HILLS
                        else:
                            self.plotMap[i] = self.PEAK

        return False
    def getOppositeDirection(self,direction):
        opposite = self.L
        if direction == self.N:
            opposite = self.S
        elif direction == self.S:
            opposite = self.N
        elif direction == self.E:
            opposite = self.W
        elif direction == self.W:
            opposite = self.E
        return opposite
                   
    def shouldPlacePeak(self,x,y):
        i = GetIndex(x,y)
        regionID = regMap.regionMap[i]
        if regionID == -1:
            return True #Plots without a region are always peaks
        region = regMap.getRegionByID(regionID)
        if region.isWater:
            return False #Water regions have no peaks
        #if neighbor in different region not peak, then return True
        for direction in range(1,9,1):
            xx,yy = self.getXYFromDirection(x,y,direction)
            ii = GetIndex(xx,yy)
            if ii == -1:
                return True #Land plots on map edge are peaks, water handled above
            if self.plotMap[ii] != self.PEAK:
                nRegionID = regMap.regionMap[ii]
                if nRegionID == -1:
                    continue
##                if nRegionID == region.gateRegion:
                nRegion = regMap.getRegionByID(nRegionID)
                if nRegion.isWater and region.altitude < 2:
                    return False
                elif nRegion.isWater and region.altitude < 3 and \
                regMap.highestRegionAltitude >= 3:
                    self.plotMap[i] = self.HILLS #Cheating sorta
                    return True
                if nRegionID != regionID:
                    return True

        return False
    def getXYFromDirection(self,x,y,direction):
        xx = x
        yy = y
        if direction == self.N:
            yy += 1
        elif direction == self.S:
            yy -= 1
        elif direction == self.E:
            xx += 1
        elif direction == self.W:
            xx -= 1
        elif direction == self.NW:
            yy += 1
            xx -= 1
        elif direction == self.NE:
            yy += 1
            xx += 1
        elif direction == self.SW:
            yy -= 1
            xx -= 1
        elif direction == self.SE:
            yy -= 1
            xx += 1
        return xx,yy
    def PrintPlotMap(self):
        print "Plot Map"
        for y in range(mapSize.MapHeight - 1,-1,-1):
            lineString = ""
            for x in range(mapSize.MapWidth):
                mapLoc = self.plotMap[GetIndex(x,y)]
                if mapLoc == self.OCEAN:
                    lineString += "O"
                elif mapLoc == self.PEAK:
                    lineString += "P"
                elif mapLoc == self.HILLS:
                    lineString += "H"
                elif mapLoc == self.LAND:
                    lineString += "L"

            print lineString
        lineString = " "
        print lineString
plotMap = PlotMap()

class TerrainMap :
    def __init__(self):
        return
    def createTerrainMap(self):
        self.L = 0
        self.N = 1
        self.S = 2
        self.E = 3
        self.W = 4
        self.NE = 5
        self.NW = 6
        self.SE = 7
        self.SW = 8
        
        self.DESERT = 0
        self.PLAINS = 1
        self.ICE = 2
        self.TUNDRA = 3
        self.GRASS = 4
        self.HILL = 5
        self.COAST = 6
        self.OCEAN = 7
        self.PEAK = 8
        self.terrainMap = array('i')
        #initialize terrainMap with OCEAN
        for i in range(0,mapSize.MapHeight*mapSize.MapWidth):
            self.terrainMap.append(self.OCEAN)
        for y in range(mapSize.MapHeight):
            for x in range(mapSize.MapWidth):
                i = GetIndex(x,y)
                if plotMap.plotMap[i] != plotMap.OCEAN:
                    self.terrainMap[i] = self.GRASS
                else:
                    for direction in range(1,9,1):
                        xx,yy = self.getXYFromDirection(x,y,direction)
                        ii = GetIndex(xx,yy)
                        if ii != -1 and plotMap.plotMap[ii] != plotMap.OCEAN:
                            self.terrainMap[i] = self.COAST
                            
        for y in range(mapSize.MapHeight):
            for x in range(mapSize.MapWidth):
                i = GetIndex(x,y)
                if plotMap.plotMap[i] != plotMap.OCEAN:
                    rainFall = GetRainfall(x,y)
                    if rainFall < DesertThreshold:
                        if rainFall < ((PRand.random()*DesertThreshold)/2.0) + (DesertThreshold/2.0):
                            self.terrainMap[i] = self.DESERT
                        else:
                            self.terrainMap[i] = self.PLAINS
                    elif rainFall < PlainsThreshold:
                        if rainFall < ((PRand.random() * (PlainsThreshold - DesertThreshold))/2.0) +\
                           DesertThreshold + ((PlainsThreshold - DesertThreshold)/2.0):
                            self.terrainMap[i] = self.PLAINS
                        else:
                            self.terrainMap[i] = self.GRASS
                    else:
                        self.terrainMap[i] = self.GRASS
                    altitude = GetPlotAltitude(x,y)
                    if altitude > IceThreshold:
                        self.terrainMap[i] = self.ICE
                    elif altitude > TundraThreshold:
                        self.terrainMap[i] = self.TUNDRA
                    elif altitude > MaxDesertAltitude and self.terrainMap[i] == self.DESERT:
                        self.terrainMap[i] = self.PLAINS
			
        
    def getXYFromDirection(self,x,y,direction):
        xx = x
        yy = y
        if direction == self.N:
            yy += 1
        elif direction == self.S:
            yy -= 1
        elif direction == self.E:
            xx += 1
        elif direction == self.W:
            xx -= 1
        elif direction == self.NW:
            yy += 1
            xx -= 1
        elif direction == self.NE:
            yy += 1
            xx += 1
        elif direction == self.SW:
            yy -= 1
            xx -= 1
        elif direction == self.SE:
            yy -= 1
            xx += 1
        return xx,yy

terrainMap = TerrainMap()
##############################################################################
## Seed filler class
##############################################################################
class Areamap :
    def __init__(self,width,height):
        self.mapWidth = width
        self.mapHeight = height
        self.areaMap = array('i')
        #initialize map with zeros
        for i in range(0,self.mapHeight*self.mapWidth):
            self.areaMap.append(0)
        return
    def findImpassableAreas(self):
#        self.areaSizes = array('i')
##        starttime = time.clock()
        #make sure map is erased in case it is used multiple times
        for i in range(0,self.mapHeight*self.mapWidth):
            self.areaMap[i] = 0
#        for i in range(0,1):
        for i in range(0,self.mapHeight*self.mapWidth):
            if plotMap.plotMap[i] == plotMap.OCEAN: #not assigned to an area yet
                areaSize = self.fillArea(i)

##        endtime = time.clock()
##        elapsed = endtime - starttime
##        print "defineAreas time ="
##        print elapsed
##        print

        return
    def fillArea(self,index):
        #first divide index into x and y
        y = index/self.mapWidth
        x = index%self.mapWidth
        #We check 8 neigbors for land,but 4 for water. This is because
        #the game connects land squares diagonally across water, but
        #water squares are not passable diagonally across land
        self.segStack = list()
        self.size = 0
        #place seed on stack for both directions
        seg = LineSegment(y,x,x,1)
        self.segStack.append(seg) 
        seg = LineSegment(y+1,x,x,-1)
        self.segStack.append(seg) 
        while(len(self.segStack) > 0):
            seg = self.segStack.pop()
            self.scanAndFillLine(seg)
        
        return self.size
    def scanAndFillLine(self,seg):
        #check for y + dy being off map
        i = GetIndex(seg.xLeft,seg.y + seg.dy)
        if i < 0:
##            print "scanLine off map ignoring",str(seg)
            return
        debugReport = False
##        if (seg.y < 8 and seg.y > 4) or (seg.y < 70 and seg.y > 64):
##        if (areaID == 4):
##            debugReport = True
        #landOffset = 1 for 8 connected neighbors, 0 for 4 connected neighbors
        landOffset = 1
        lineFound = False
        #first scan and fill any left overhang
        if debugReport:
            print ""
            print str(seg)
            print "Going left"
        for xLeftExtreme in range(seg.xLeft - landOffset,-1 ,-1):
            i = GetIndex(xLeftExtreme,seg.y + seg.dy)
            if debugReport:
                print "xLeftExtreme = %(xl)4d" % {'xl':xLeftExtreme}
            if self.areaMap[i] == 0 and plotMap.plotMap[i] != plotMap.PEAK:
                self.areaMap[i] = 1
                self.size += 1
                lineFound = True
            else:
                #if no line was found, then xLeftExtreme is fine, but if
                #a line was found going left, then we need to increment
                #xLeftExtreme to represent the inclusive end of the line
                if lineFound:
                    xLeftExtreme += 1
                break
        if debugReport:
            print "xLeftExtreme finally = %(xl)4d" % {'xl':xLeftExtreme}
            print "Going Right"
        #now scan right to find extreme right, place each found segment on stack
#        xRightExtreme = seg.xLeft - landOffset #needed sometimes? one time it was not initialized before use.
        xRightExtreme = seg.xLeft #needed sometimes? one time it was not initialized before use.
        for xRightExtreme in range(seg.xLeft,self.mapWidth,1):
            if debugReport:            
                print "xRightExtreme = %(xr)4d" % {'xr':xRightExtreme}
            i = GetIndex(xRightExtreme,seg.y + seg.dy)
            if self.areaMap[i] == 0 and plotMap.plotMap[i] != plotMap.PEAK:
                self.areaMap[i] = 1
                self.size += 1
                if lineFound == False:
                    lineFound = True
                    xLeftExtreme = xRightExtreme #starting new line
                    if debugReport:
                        print "starting new line at xLeftExtreme= %(xl)4d" % {'xl':xLeftExtreme}
            elif lineFound == True: #found the right end of a line segment!                
                lineFound = False
                #put same direction on stack
                newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,seg.dy)
                self.segStack.append(newSeg)
                if debugReport:
                    print "same direction to stack",str(newSeg)
                #determine if we must put reverse direction on stack
                if xLeftExtreme < seg.xLeft or xRightExtreme >= seg.xRight:
                    #out of shadow so put reverse direction on stack also
                    newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,-seg.dy)
                    self.segStack.append(newSeg)
                    if debugReport:
                        print "opposite direction to stack",str(newSeg)
                if xRightExtreme >= seg.xRight + landOffset:
                    if debugReport:
                        print "finished with line"
                    break; #past the end of the parent line and this line ends
            elif lineFound == False and xRightExtreme >= seg.xRight + landOffset:
                if debugReport:
                    print "no additional lines found"
                break; #past the end of the parent line and no line found
            else:
                continue #keep looking for more line segments
        if lineFound == True: #still a line needing to be put on stack
            if debugReport:
                print "still needing to stack some segs"
            lineFound = False
            #put same direction on stack
            newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,seg.dy)
            self.segStack.append(newSeg)
            if debugReport:
                print str(newSeg)
            #determine if we must put reverse direction on stack
            if xLeftExtreme < seg.xLeft or xRightExtreme - 1 > seg.xRight:
                #out of shadow so put reverse direction on stack also
                newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,-seg.dy)
                self.segStack.append(newSeg)
                if debugReport:
                    print str(newSeg)
        
        return
    #for debugging
    def PrintAreaMap(self):
        
        print "Area Map"
        for y in range(self.mapHeight - 1,-1,-1):
            lineString = ""
            for x in range(self.mapWidth):
                mapLoc = self.areaMap[GetIndex(x,y)]
                if mapLoc + 34 > 127:
                    mapLoc = 127 - 34
                lineString += chr(mapLoc + 34)
            lineString += "-" + str(y)
            print lineString
        lineString = " "
        print lineString

        return
    
class LineSegment :
    def __init__(self,y,xLeft,xRight,dy):
        self.y = y
        self.xLeft = xLeft
        self.xRight = xRight
        self.dy = dy
    def __str__ (self):
        string = "y = %(y)3d, xLeft = %(xl)3d, xRight = %(xr)3d, dy = %(dy)2d" % \
        {'y':self.y,'xl':self.xLeft,'xr':self.xRight,'dy':self.dy}
        return string
class StartRegion :
    def __init__(self,region):
        self.region = region
        self.differenceFromIdeal = -1.0
class StartingPlotFinder :
    def __init__(self):
        return
    def initialize(self):
        self.availableRegionList = list()
        self.occupiedRegionList = list()

    def assignStartingPlots(self):
        gc = CyGlobalContext()
        gameMap = CyMap()

        #Shuffle players so the same player doesn't always get the first pick.
        playerList = list()
        for plrCheckLoop in range(gc.getMAX_CIV_PLAYERS()):
                if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
                        playerList.append(plrCheckLoop)
        playerList = ShuffleList(playerList)

        for region in regMap.regionList:
            if not region.isWater:
                startRegion = StartRegion(region)
                self.availableRegionList.append(startRegion)

        civPreferenceList = GetCivPreferences()
        
        for playerIndex in playerList:
            player = gc.getPlayer(playerIndex)
            player.AI_updateFoundValues(True)
            civType = player.getCivilizationType()
            civInfo = gc.getCivilizationInfo(civType)
            print "Civ = %(c)s" % {"c":civInfo.getType()}
            civPref = self.getCivPreference(civPreferenceList,civType)
            bestRegion = self.getBestStartRegion(self.availableRegionList,self.occupiedRegionList,civPref)
            startPlot = self.getStartPlotInRegion(bestRegion.region,player,civPref)
            DeleteFromList(self.availableRegionList,bestRegion)
            self.occupiedRegionList.append(bestRegion)
            player.setStartingPlot(startPlot,True)
            
        return

    def getStartPlotInRegion(self,region,player,civPref):
        gc = CyGlobalContext()
        gameMap = CyMap()
        bestValue = 0
        bestPlot = None
        for plot in region.plotList:
            startPlot = gameMap.plot(plot.x,plot.y)
            if civPref.needCoastalStart and not isCoast(startPlot):
                continue
            if startPlot.isPeak() == True:
                continue
            value = startPlot.getFoundValue(player.getID())
            if value > bestValue:
                bestValue = value
                bestPlot = startPlot        
        if bestPlot == None:
            raise ValueError, "best plot in region is null"
        return bestPlot

    def getBestStartRegion(self,availableRegionList,occupiedRegionList,civPref):
        bestRegionList = list()        
        for startRegion in availableRegionList:
            #first make sure region has a water gateRegion if coastal start
            #is desired
            if civPref.needCoastalStart:
                gateRegion = regMap.getRegionByID(startRegion.region.gateRegion)
                if not gateRegion.isWater:
                    continue
            if len(startRegion.region.plotList) < MinRegionSizeStart:
                continue
            bestRegionList.append(startRegion)
            
        for startRegion in bestRegionList:
            normalizedAlt = startRegion.region.altitude/regMap.highestRegionAltitude
            altitudeDiff = abs(normalizedAlt - civPref.idealAltitude)
            
            moistureDiff = abs(startRegion.region.moisture - civPref.idealMoisture)
            
            maxDistance = GetDistance(0,0,mapSize.MapWidth - 1,mapSize.MapHeight - 1)
            distanceToNearest = self.getDistToNearestOccRegion(occupiedRegionList,startRegion)
            distanceFactor = 1.0 - (distanceToNearest/maxDistance)
            
            weightedAverageDiff = ((civPref.altitudeWeight * altitudeDiff) + (distanceFactor * civPref.distanceWeight) + moistureDiff)/(civPref.altitudeWeight + civPref.distanceWeight + 1)
##            print "regionID = %(r)d, altitudeDiff= %(ad)f, moistureDiff= %(md)f, altitudeWeight= %(aw)f, weightedAverageDiff= %(wd)f" % \
##            {"r":startRegion.region.ID,"ad":altitudeDiff,"md":moistureDiff,"aw":civPref.altitudeWeight,"wd":weightedAverageDiff}
            startRegion.differenceFromIdeal = weightedAverageDiff
            
        bestRegionList.sort(lambda x,y:cmp(x.differenceFromIdeal,y.differenceFromIdeal))
        startRegion = bestRegionList[0]
        print "chosen regionID = %(r)d" % {"r":startRegion.region.ID}
        return startRegion

    def getDistToNearestOccRegion(self,occupiedRegionList,startRegion):
        minDistance = GetDistance(0,0,mapSize.MapWidth - 1,mapSize.MapHeight - 1)
        for occRegion in occupiedRegionList:
            startGatePlot = startRegion.region.gatePlot
            if startGatePlot == None:
                continue
            occGatePlot = occRegion.region.gatePlot
            distance = GetDistance(startGatePlot.x,startGatePlot.y,occGatePlot.x,occGatePlot.y)
            minDistance = min(distance,minDistance)
        return minDistance

    def getCivPreference(self,civPreferenceList,civType):
        for civPref in civPreferenceList:
            if civPref.civ == civType:
                return civPref
        #None defined so let's make a generic one
        civPref = CivPreference(civType)
        return civPref
    
    def replaceUniqueImprovements(self):
        gc = CyGlobalContext()
        gameMap = CyMap()
        impPrefList = GetImprovementPreferences()
        availableRegionList = list()
        occupiedRegionList = list()
        for region in regMap.regionList:
            startRegion = StartRegion(region)
            availableRegionList.append(startRegion)
        for y in range(mapSize.MapHeight):
            for x in range(mapSize.MapWidth):
                plot = gameMap.plot(x,y)
                impType = plot.getImprovementType()
                impInfo = gc.getImprovementInfo(impType)
                if impInfo == None:
                    continue
                print "Found %(i)s" % {"i":impInfo.getType()}
                impPref = None
                #Find impType in preference list
                for foundImpPref in impPrefList:
                    if foundImpPref.improvement == impType:
                        impPref = foundImpPref
                        break
                if impPref == None:
                    continue
                impInfo = gc.getImprovementInfo(impType)
                print "Removing %(i)s at %(x)d, %(y)d" % {"i":impInfo.getType(),"x":x,"y":y}
                plot.setImprovementType(GetInfoType("NO_IMPROVEMENT"))
                numUnits = plot.getNumUnits()
                unitList = list()
                for n in range(numUnits):
                    unit = plot.getUnit(n)
                    unitList.append(unit)
                plot.setBonusType(GetInfoType("NO_BONUS"))
                bestRegion = self.getBestImprovementRegion(availableRegionList,occupiedRegionList,impPref)
                DeleteFromList(availableRegionList,bestRegion)
                occupiedRegionList.append(bestRegion)
                bestPlot = self.getBestImpPlotInRegion(bestRegion.region,impPref)
                DeleteFromList(impPrefList,impPref)
                print "Adding %(i)s at %(x)d, %(y)d" % {"i":impInfo.getType(),"x":bestPlot.getX(),"y":bestPlot.getY()}
                bestPlot.setImprovementType(impType)
                for n in range(numUnits):
                    unit = unitList[n]
                    unit.setXY(bestPlot.getX(),bestPlot.getY(),False,True,False)
                    
    def getBestImprovementRegion(self,availableRegionList,occupiedRegionList,impPref):
        bestRegionList = list()        
        for startRegion in availableRegionList:
            #first make sure region has a water gateRegion if coastal plot
            #is desired
            if impPref.needCoast:
                gateRegion = regMap.getRegionByID(startRegion.region.gateRegion)
                if not gateRegion.isWater:
                    continue
            if impPref.needWater:
                if not startRegion.region.isWater:
                    continue
            if startRegion.region.isWater:
                continue #water regions not supported right now
            if len(startRegion.region.plotList) < MinRegionSizeTower:
                continue
            bestRegionList.append(startRegion)
            
        for startRegion in bestRegionList:
            normalizedAlt = startRegion.region.altitude/regMap.highestRegionAltitude
            altitudeDiff = abs(normalizedAlt - impPref.idealAltitude)
            
            moistureDiff = abs(startRegion.region.moisture - impPref.idealMoisture)
            
            maxDistance = GetDistance(0,0,mapSize.MapWidth - 1,mapSize.MapHeight - 1)
            distanceToNearest = self.getDistToNearestOccRegion(occupiedRegionList,startRegion)
            distanceFactor = 1.0 - (distanceToNearest/maxDistance)
            
            weightedAverageDiff = ((impPref.altitudeWeight * altitudeDiff) + distanceFactor + (moistureDiff * impPref.moistureWeight))/(impPref.altitudeWeight + impPref.moistureWeight + 1)
            print "regionID = %(r)d, altitudeDiff= %(ad)f, moistureDiff= %(md)f, altitudeWeight= %(aw)f, weightedAverageDiff= %(wd)f" % \
            {"r":startRegion.region.ID,"ad":altitudeDiff,"md":moistureDiff,"aw":impPref.altitudeWeight,"wd":weightedAverageDiff}
            startRegion.differenceFromIdeal = weightedAverageDiff
            
        bestRegionList.sort(lambda x,y:cmp(x.differenceFromIdeal,y.differenceFromIdeal))
        startRegion = bestRegionList[0]
        print "chosen regionID = %(r)d" % {"r":startRegion.region.ID}
        return startRegion
    
    def getBestImpPlotInRegion(self,region,impPref):
        gc = CyGlobalContext()
        gameMap = CyMap()
        midPoint = region.getCenter()
##        print "midPoint.x= %(mx)d, midPoint.y= %(my)d" % {"mx":midPoint.x,"my":midPoint.y}
        minDistance = 100.0
        bestPlot = gameMap.plot(midPoint.x,midPoint.y)
        region.plotList = ShuffleList(region.plotList)
        for plot in region.plotList:
            i = GetIndex(plot.x,plot.y)
            gamePlot = gameMap.plot(plot.x,plot.y)
            if gamePlot.getBonusType(TeamTypes.NO_TEAM) != GetInfoType("NO_BONUS"):
                continue
            if gamePlot.isPeak() == True:
                continue
            if impPref.needHill and plotMap.plotMap[i] != plotMap.HILLS:
                continue
            if impPref.needFlat and plotMap.plotMap[i] != plotMap.LAND:
                continue
            if impPref.needCoast and not isCoast(gamePlot):
                continue
            bestPlot = gameMap.plot(plot.x,plot.y)
            break

        return bestPlot
    def collectAllWatchtowers(self):
        gc = CyGlobalContext()
        gameMap = CyMap()
        count = 0
        for y in range(mapSize.MapHeight):
            for x in range(mapSize.MapWidth):
                plot = gameMap.plot(x,y)
                impType = plot.getImprovementType()
                if impType == GetInfoType("IMPROVEMENT_TOWER"):
                    count += 1
                    plot.setImprovementType(GetInfoType("NO_IMPROVEMENT"))
        print "razed %(t)d watchtowers" % {"t":count}
        return count
        
    def replaceWatchtowers(self,count):
##        regMap.PrintRegionMap(False)
        gc = CyGlobalContext()
        gameMap = CyMap()
        towersPlacedAtChoke = 0
        towersPlacedInMiddle = 0
        for region in regMap.regionList:
            if region.isWater:
                continue
            if len(region.plotList) < MinRegionSizeTower:
                continue
            if PRand.randint(0,3) == 0:
                continue #not all regions should have a tower
##            print "placing towers in region %(r)d" % {"r":region.ID}
            if PRand.randint(0,1) == 0:
                chokePoint = self.findChokePoint(region)
                if chokePoint != None:
                    chokePoint.setImprovementType(GetInfoType("IMPROVEMENT_TOWER"))
                    towersPlacedAtChoke += 1
                    continue #regions should not have a choke tower and mid tower or else they might appear together

            #If a chokepoint is not found or if mid tower is randomly selected,
            #place tower in the middle of a region
            midPoint = region.getCenter()
##            print "midPoint.x= %(mx)d, midPoint.y= %(my)d" % {"mx":midPoint.x,"my":midPoint.y}
            minDistance = 100.0
            bestPlot = None
            for plot in region.plotList:
                i = GetIndex(plot.x,plot.y)
                gamePlot = gameMap.plot(plot.x,plot.y)
                if gamePlot.getBonusType(TeamTypes.NO_TEAM) != GetInfoType("NO_BONUS"):
                    continue

                if plotMap.plotMap[i] == plotMap.HILLS:
                    distance = GetDistance(plot.x,plot.y,midPoint.x,midPoint.y)
                    if minDistance > distance:
                        bestPlot = plot
                        minDistance = distance
            if bestPlot != None:
                midHill = gameMap.plot(bestPlot.x,bestPlot.y)
                midHill.setImprovementType(GetInfoType("IMPROVEMENT_TOWER"))
                towersPlacedInMiddle += 1
        print "towersPlacedAtChoke= %(c)d, towersPlacedInMiddle= %(m)d, total= %(t)d" % \
        {"c":towersPlacedAtChoke,"m":towersPlacedInMiddle,"t":towersPlacedAtChoke + towersPlacedInMiddle}
                
    def findChokePoint(self,region):
        gc = CyGlobalContext()
        gameMap = CyMap()
        
        for plot in region.plotList:
            i = GetIndex(plot.x,plot.y)
            if plotMap.plotMap[i] == plotMap.PEAK:
                continue
            gamePlot = gameMap.plot(plot.x,plot.y)
            if gamePlot.getBonusType(TeamTypes.NO_TEAM) != GetInfoType("NO_BONUS"):
                continue
            oppositePeaks = False
            for direction in range(1,5,1):
                xx,yy = plotMap.getXYFromDirection(plot.x,plot.y,direction)
                ii = GetIndex(xx,yy)
                if plotMap.plotMap[ii] == plotMap.PEAK:
                    oppDir = plotMap.getOppositeDirection(direction)
                    xxx,yyy = plotMap.getXYFromDirection(plot.x,plot.y,oppDir)
                    iii = GetIndex(xxx,yyy)
                    if plotMap.plotMap[iii] == plotMap.PEAK:
                        oppositePeaks = True
                        
            oppositePass = False
            for direction in range(1,5,1):
                xx,yy = plotMap.getXYFromDirection(plot.x,plot.y,direction)
                ii = GetIndex(xx,yy)
                if plotMap.plotMap[ii] != plotMap.PEAK:
                    oppDir = plotMap.getOppositeDirection(direction)
                    xxx,yyy = plotMap.getXYFromDirection(plot.x,plot.y,oppDir)
                    iii = GetIndex(xxx,yyy)
                    if plotMap.plotMap[iii] != plotMap.PEAK:
                        oppositePass = True
            if oppositePeaks and oppositePass:
                chokePoint = gameMap.plot(plot.x,plot.y)
                if chokePoint.isRiverSide() == True:
                    return chokePoint
                        
        return None                                        
                
spf = StartingPlotFinder()
    
#######################################################################################
## Global Functions
#######################################################################################
#This function appends an item to a list only if it is not already
#in the list
def isCoast(plot):
    WaterArea = plot.waterArea()
    if not WaterArea.isNone():
        if not WaterArea.isLake():
            return True
    return False

def AppendUnique(theList,newItem):
    if IsInList(theList,newItem) == False:
        theList.append(newItem)
    return

def IsInList(theList,newItem):
    itemFound = False
    for item in theList:
        if item == newItem:
            itemFound = True
            break
    return itemFound

def DeleteFromList(theList,oldItem):
    for n in range(len(theList)):
        if theList[n] == oldItem:
            del theList[n]
            break
    return  
    
def ShuffleList(theList):
        preshuffle = list()
        shuffled = list()
        numElements = len(theList)
        for i in range(numElements):
            preshuffle.append(theList[i])
        for i in range(numElements):
                n = PRand.randint(0,len(preshuffle)-1)
                shuffled.append(preshuffle[n])
                del preshuffle[n]
        return shuffled
    
def GetInfoType(string):
	cgc = CyGlobalContext()
	return cgc.getInfoTypeForString(string)

def GetPlotAltitude(x,y):
    #calculate highest region altitude if necessary and save it for later
    if regMap.highestRegionAltitude == 0:
        regMap.regionList.sort(lambda n,m: cmp(n.altitude,m.altitude))
        regMap.regionList.reverse()
        regMap.highestRegionAltitude = regMap.regionList[0].altitude
    i = GetIndex(x,y)
    regionID = regMap.regionMap[i]
    if regionID == -1:
        return -1.0
    region = regMap.getRegionByID(regionID)
##    print "GetPlotAltitude"
    regionAlt = float(region.altitude + 1)/float(regMap.highestRegionAltitude + 1)
##    print "regionAlt = %(ra)f" % {"ra":regionAlt}
    riverAltRange = RiverAltRangeFactor * float(RiverThreshold)
    riverSize = GetRiverSize(x,y)
    if riverSize > riverAltRange:
        riverSize = riverAltRange
##    print "riverSize = %(r)f" % {"r":riverSize}
    riverSubtract = riverSize * ((RiverAltitudeSubtraction/riverAltRange)/float(regMap.highestRegionAltitude + 1))
##    print "riverSubtract = %(rs)f" % {"rs":riverSubtract}

    altitude = regionAlt - riverSubtract
##    print "altitude = %(a)f" % {"a":altitude}
##    print ""
    return altitude
def GetRiverSize(x,y):
    riverAverage = 0.0
    for direction in range(5,9,1):
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        riverAverage += float(riverMap.riverMap[rxI])
    riverAverage = riverAverage/4.0
    return riverAverage

def IsPlotTouchingRiver(x,y):
    for direction in range(5,9,1):
        rxX,rxY = riverMap.rxFromPlot(x,y,direction)
        rxI = riverMap.getRiverIndex(rxX,rxY)
        if riverMap.riverMap[rxI] > RiverThreshold:
            return True
    return False

def IsPlotSurroundedByOcean(x,y):
    for direction in range(1,9,1):
        xx,yy = regMap.getXYFromDirection(x,y,direction)
        i = GetIndex(xx,yy)
        if plotMap.plotMap[i] != plotMap.OCEAN:            
            return False
    return True

def GetRainfall(x,y):
        rainfall = 0
        i = GetIndex(x,y)
        regionID = regMap.regionMap[i]
        if regionID != -1:
            region = regMap.getRegionByID(regionID)
            rainfall = region.moisture
            riverSize = GetRiverSize(x,y)
            riverSizeMax = float(RiverThreshold) * RiverAddsMoistureMax 
            riverSize = min(riverSize,riverSizeMax)
            rainfall += (riverSize/riverSizeMax) * RiverAddsMoistureRange
            rainfall = .8*rainfall+.45*PRand.random()
        
        return rainfall
def GetDistance(x,y,dx,dy):
    distance = math.sqrt(abs((float(x - dx) * float(x - dx)) + (float(y - dy) * float(y - dy))))
    return distance
###############################################################################     
#functions that civ is looking for
###############################################################################    
def getDescription():
	"""
	A map's Description is displayed in the main menu when players go to begin a game.
	For no description return an empty string.
	"""
	return "Random map that creates a region of a fantasy type world "+\
        "where much of the world is unknown and irrelevant. It allows terrain " +\
        "to be created on a smaller, more detailed scale than planetary maps."

def getWrapX():
	return WrapX
	
def getWrapY():
	return WrapY
    
def generatePlotTypes():
    NiTextOut("Generating Plot Types  ...")
    print "Adding Terrain"
    gc = CyGlobalContext()
    mmap = gc.getMap()
    mapSize.MapWidth = mmap.getGridWidth()
    mapSize.MapHeight = mmap.getGridHeight()
    PRand.seed()
    print "MapWidth = %(mw)d,MapHeight = %(mh)d" % {"mw":mapSize.MapWidth,"mh":mapSize.MapHeight}
    plotTypes = [PlotTypes.PLOT_OCEAN] * (mapSize.MapWidth*mapSize.MapHeight)
    NumberOfPlayers = gc.getGame().countCivPlayersEverAlive()
    regMap.createRegions()
    riverMap.createRiverMap()
    plotMap.createPlotMap()

    for i in range(mapSize.MapWidth*mapSize.MapHeight):
        mapLoc = plotMap.plotMap[i]
        if mapLoc == plotMap.PEAK:
            plotTypes[i] = PlotTypes.PLOT_PEAK
        elif mapLoc == plotMap.HILLS:
            plotTypes[i] = PlotTypes.PLOT_HILLS
        elif mapLoc == plotMap.LAND:
            plotTypes[i] = PlotTypes.PLOT_LAND
        else:
            plotTypes[i] = PlotTypes.PLOT_OCEAN
    print "Finished generating plot types."         
    return plotTypes

def generateTerrainTypes():
    NiTextOut("Generating Terrain  ...")
    print "Adding Terrain"
    gc = CyGlobalContext()
    terrainDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
    terrainPlains = gc.getInfoTypeForString("TERRAIN_PLAINS")
    terrainIce = gc.getInfoTypeForString("TERRAIN_SNOW")
    terrainTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
    terrainGrass = gc.getInfoTypeForString("TERRAIN_GRASS")
    terrainHill = gc.getInfoTypeForString("TERRAIN_HILL")
    terrainCoast = gc.getInfoTypeForString("TERRAIN_COAST")
    terrainOcean = gc.getInfoTypeForString("TERRAIN_OCEAN")
    terrainPeak = gc.getInfoTypeForString("TERRAIN_PEAK")
    terrainMap.createTerrainMap()
    terrainTypes = [0]*(mapSize.MapWidth*mapSize.MapHeight)
    for i in range(mapSize.MapWidth*mapSize.MapHeight):
        if terrainMap.terrainMap[i] == terrainMap.OCEAN:
            terrainTypes[i] = terrainOcean
        elif terrainMap.terrainMap[i] == terrainMap.COAST:
            terrainTypes[i] = terrainCoast
        elif terrainMap.terrainMap[i] == terrainMap.DESERT:
            terrainTypes[i] = terrainDesert
        elif terrainMap.terrainMap[i] == terrainMap.PLAINS:
            terrainTypes[i] = terrainPlains
        elif terrainMap.terrainMap[i] == terrainMap.GRASS:
            terrainTypes[i] = terrainGrass
        elif terrainMap.terrainMap[i] == terrainMap.TUNDRA:
            terrainTypes[i] = terrainTundra
        elif terrainMap.terrainMap[i] == terrainMap.ICE:
            terrainTypes[i] = terrainIce
    print "Finished generating terrain types."
    return terrainTypes

def addRivers():
    NiTextOut("Adding Rivers....")
    print "Adding Rivers"
    gc = CyGlobalContext()
    pmap = gc.getMap()
    for y in range(mapSize.MapHeight):
        for x in range(mapSize.MapWidth):
            placeRiversInPlot(x,y)
    
def placeRiversInPlot(x,y):
    gc = CyGlobalContext()
    pmap = gc.getMap()
    plot = pmap.plot(x,y)
    #NE
    xx,yy = riverMap.rxFromPlot(x,y,riverMap.NE)
    ii = riverMap.getRiverIndex(xx,yy)
    if riverMap.riverMap[ii] > RiverThreshold and riverMap.flowMap[ii] == riverMap.S:
        plot.setWOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
    #SW
    xx,yy = riverMap.rxFromPlot(x,y,riverMap.SW)
    ii = riverMap.getRiverIndex(xx,yy)
    if riverMap.riverMap[ii] > RiverThreshold and riverMap.flowMap[ii] == riverMap.E:
        plot.setNOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_EAST)
    #SE
    xx,yy = riverMap.rxFromPlot(x,y,riverMap.SE)
    ii = riverMap.getRiverIndex(xx,yy)
    if riverMap.riverMap[ii] > RiverThreshold and riverMap.flowMap[ii] == riverMap.N:
        plot.setWOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
    elif riverMap.riverMap[ii] > RiverThreshold and riverMap.flowMap[ii] == riverMap.W:
        plot.setNOfRiver(True,CardinalDirectionTypes.CARDINALDIRECTION_WEST)
        
def addFeatures():
    NiTextOut("Generating Features  ...")
    print "Adding Features"
    gc = CyGlobalContext()
    mmap = gc.getMap()
    featureIce = gc.getInfoTypeForString("FEATURE_ICE")
    featureJungle = gc.getInfoTypeForString("FEATURE_JUNGLE")
    featureOasis = gc.getInfoTypeForString("FEATURE_OASIS")
    featureFloodPlains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
    featureForest = gc.getInfoTypeForString("FEATURE_FOREST")
    FORESTLEAFY = 0
    FORESTEVERGREEN = 1
    FORESTSNOWY = 2
    #Now plant forest or jungle and place floodplains and oasis
    for y in range(mapSize.MapHeight):
        for x in range(mapSize.MapWidth):
            i = GetIndex(x,y)
            plot = mmap.plot(x,y)
            #forest and jungle
            if plot.isWater() == False and terrainMap.terrainMap[i] != terrainMap.DESERT and\
            plotMap.plotMap[i] != plotMap.PEAK:
                #Chance for trees based on rainfall
                rainfall = GetRainfall(x,y)
                if rainfall >= PRand.random()+.25:#Trees are present
                    altitude = GetPlotAltitude(x,y)
                    if altitude < LeafyAltitude:
                        if rainfall >= JungleThreshold:
                            if PRand.random() > 0.3:
                                plot.setFeatureType(featureJungle,0)
                            else:
                                plot.setFeatureType(featureForest,FORESTLEAFY)
                        else:
                            plot.setFeatureType(featureForest,FORESTLEAFY)
                    elif altitude < EvergreenAltitude:
                        plot.setFeatureType(featureForest,FORESTLEAFY)
                    elif altitude < TundraThreshold:
                        plot.setFeatureType(featureForest,FORESTEVERGREEN)
                    else:
                        plot.setFeatureType(featureForest,FORESTSNOWY)
                        
            #floodplains and Oasis
            elif terrainMap.terrainMap[i] == terrainMap.DESERT and plotMap.plotMap[i] != plotMap.HILLS and\
            plotMap.plotMap[i] != plotMap.PEAK and plot.isWater() == False:
                if plot.isRiver() == True:
                    plot.setFeatureType(featureFloodPlains,0)
                else:
                    #is this square surrounded by desert?
                    foundNonDesert = False
                    #print "trying to place oasis"
                    for yy in range(y - 1,y + 2):
                        for xx in range(x - 1,x + 2):
                            ii = GetIndex(xx,yy)
                            surPlot = mmap.plot(xx,yy)
                            if (terrainMap.terrainMap[ii] != terrainMap.DESERT and \
                            plotMap.plotMap[ii] != plotMap.PEAK):
                                #print "non desert neighbor"
                                foundNonDesert = True
                            elif surPlot == 0:
                                #print "neighbor off map"
                                foundNonDesert = True
                            elif surPlot.isWater() == True:
                                #print "water neighbor"
                                foundNonDesert = True
                            elif surPlot.getFeatureType() == featureOasis:
                                #print "oasis neighbor"
                                foundNonDesert = True
                    if foundNonDesert == False:
                        if PRand.random() < OasisChance:
                            #print "placing oasis"
                            plot.setFeatureType(featureOasis,0)
                       # else:
                            #print "oasis failed random check"
            
    return
        

#This doesn't work with my river system so it is disabled. Some civs
#might start without a river. Boo hoo.
def normalizeAddRiver():
    return
def normalizeAddLakes():
    return
def normalizeAddGoodTerrain():
    return
def normalizeRemoveBadTerrain():
    return
def normalizeRemoveBadFeatures():
    gc = CyGlobalContext()
    gameMap = CyMap()

    civPrefList = GetCivPreferences()

    playerList = list()
    for playerIndex in range(gc.getMAX_CIV_PLAYERS()):
        player = gc.getPlayer(playerIndex)
        if player.isEverAlive():
            civType = player.getCivilizationType()
            civPref = spf.getCivPreference(civPrefList,civType)
            if civPref.allowForestStart == True:
                continue
            plot = player.getStartingPlot()
            featureType = plot.getFeatureType()
            if featureType == GetInfoType("FEATURE_FOREST") or \
            featureType == GetInfoType("FEATURE_JUNGLE"):
                plot.setFeatureType(GetInfoType("NO_FEATURE"),0)
            for direction in range(1,9,1):
                xx,yy = plotMap.getXYFromDirection(plot.getX(),plot.getY(),direction)
                nPlot = gameMap.plot(xx,yy)
                featureType = nPlot.getFeatureType()
                if featureType == GetInfoType("FEATURE_FOREST") or \
                featureType == GetInfoType("FEATURE_JUNGLE"):
                    nPlot.setFeatureType(GetInfoType("NO_FEATURE"),0)

    return
##def normalizeAddFoodBonuses():
##    return
##def normalizeAddExtras():
##    return
def normalizeRemovePeaks():
    return
##def addLakes():
##    return
def isAdvancedMap():
	"""
	Advanced maps only show up in the map script pulldown on the advanced menu.
	Return 0 if you want your map to show up in the simple singleplayer menu
	"""
	return 0
def isClimateMap():
	"""
	Uses the Climate options
	"""
	return 0
	
def isSeaLevelMap():
	"""
	Uses the Sea Level options
	"""
	return 0
def getTopLatitude():
	"Default is 90. 75 is past the Arctic Circle"
	return 90

def getBottomLatitude():
	"Default is -90. -75 is past the Antartic Circle"
	return -90
def isBonusIgnoreLatitude():
    return True
def getGridSize(argsList):
	"Adjust grid sizes for optimum results"
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(8,8),
		WorldSizeTypes.WORLDSIZE_TINY:		(9,9),
		WorldSizeTypes.WORLDSIZE_SMALL:		(10,10),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(13,13),
		WorldSizeTypes.WORLDSIZE_LARGE:		(15,15),
		WorldSizeTypes.WORLDSIZE_HUGE:		(18,18)
	}
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def afterGeneration():#This comes before starting plot assignment
    spf.initialize()
    if FFHSpecific == False:
        return
    count = spf.collectAllWatchtowers()
    if count > 0:#Might not be FFH, so dont try to place towers if not
        spf.replaceWatchtowers(count)
        spf.replaceUniqueImprovements()
    return
    
def assignStartingPlots():
    spf.assignStartingPlots()
    return
    


##mapSize.MapWidth = 68
##mapSize.MapHeight = 68
##regMap.createRegions()
####regMap.PrintRegionMap(False)
####regMap.PrintRegionList()
####regMap.PrintRegionMap(True)
##riverMap.createRiverMap()
##riverMap.PrintFlowMap()
##plotMap.createPlotMap()
##plotMap.PrintPlotMap()
##regMap.PrintRegionRxMap(False)
##regMap.PrintRegionMap(True)
