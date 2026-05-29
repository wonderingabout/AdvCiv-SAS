#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
import sys
from SAS_WorldSizes import *

def getDescription():
	"Description shown in the main menu"
	return "Smallest possible map used for debugging"

def isAdvancedMap():
	"This map should show up in simple mode, but only in debug builds"
	return not CyGlobalContext().isDebugBuild()

def getGridSize(argsList):
	"Because this is such a land-heavy map, override getGridSize() to make the map smaller"
	# <!-- custom: Added ARENA and SAS sizes (24, 32, 40, 48 players) using runtime world-size indices for compatibility; see SASMagicNumbers.SAS_MAGIC_WORLDSIZE_* rationale. (Claude code Opus 4.5; GPT-5.5) -->
	grid_sizes = {
		SAS_MAGIC_WORLDSIZE_ARENA: (5, 5),
		SAS_MAGIC_WORLDSIZE_DUEL: (5, 5),
		SAS_MAGIC_WORLDSIZE_TINY: (5, 5),
		SAS_MAGIC_WORLDSIZE_SMALL: (5, 5),
		SAS_MAGIC_WORLDSIZE_STANDARD: (5, 5),
		SAS_MAGIC_WORLDSIZE_LARGE: (5, 5),
		SAS_MAGIC_WORLDSIZE_HUGE: (5, 5),
		SAS_MAGIC_WORLDSIZE_SAS24: (5, 5),
		SAS_MAGIC_WORLDSIZE_SAS32: (5, 5),
		SAS_MAGIC_WORLDSIZE_SAS40: (5, 5),
		SAS_MAGIC_WORLDSIZE_SAS48: (5, 5),
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	# <!-- custom: Convert enum to int for lookup, with fallback for unknown sizes (Claude code Opus 4.5) -->
	return sas_lookup_world_size(eWorldSize, grid_sizes)

def getWrapX(): return False
def getWrapY(): return False

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Continents) ...")
	fractal_world = FractalWorld()
	fractal_world.initFractal()
	return fractal_world.generatePlotTypes()

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Continents) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Continents) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0
