import math
from CvPythonExtensions import CyGlobalContext

# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Shared helpers for ARENA/SAS world sizes in map scripts. (GPT-5.2-Codex) -->

SAS_HUGE_CUSTOM_MAX_PLAYERS = 18
SAS_SIMPLE_GAME_STALE_OPTION_WARNED = False

# <!-- custom: AdvCiv-SAS added ARENA before Duel in CIV4WorldInfo, so runtime world-size indices are ARENA=0..Huge=6 while the old hardcoded WorldSizeTypes enum still has WORLDSIZE_HUGE=5. Direct runtime dictionaries keyed by argsList[0] / CyMap().getWorldSize() must use these indices, or sizes shift by one and ARENA collides with Duel. We fixed empirical grid-size cases such as Water.py and PerfectMongoose.py, and use the same pattern preventively for direct grid/grain/start-variance tables while leaving percentage-scaling scripts such as Pangaea for separate behavior-based review. CvMapGeneratorUtil.py mirrors these values with a local MAPGEN_SAS_WORLDSIZE_* prefix because it should not import this PrivateMaps helper and the prefix is easy to grep. (GPT-5.5) -->
SAS_WORLDSIZE_ARENA = 0
SAS_WORLDSIZE_DUEL = 1
SAS_WORLDSIZE_TINY = 2
SAS_WORLDSIZE_SMALL = 3
SAS_WORLDSIZE_STANDARD = 4
SAS_WORLDSIZE_LARGE = 5
SAS_WORLDSIZE_HUGE = 6
SAS_WORLDSIZE_SAS24 = 7
SAS_WORLDSIZE_SAS32 = 8
SAS_WORLDSIZE_SAS40 = 9
SAS_WORLDSIZE_SAS48 = 10
SAS_WORLDSIZE_LARGEST = SAS_WORLDSIZE_SAS48

def sas_huge_custom_max_players():
	return SAS_HUGE_CUSTOM_MAX_PLAYERS

def sas_default_sizevalues():
	return {
		SAS_WORLDSIZE_ARENA:  1,
		SAS_WORLDSIZE_DUEL:  1,
		SAS_WORLDSIZE_TINY:  1,
		SAS_WORLDSIZE_SMALL:  1,
		SAS_WORLDSIZE_STANDARD:  2,
		SAS_WORLDSIZE_LARGE:  2,
		SAS_WORLDSIZE_HUGE:  3,
		SAS_WORLDSIZE_SAS24:  4,
		SAS_WORLDSIZE_SAS32:  5,
		SAS_WORLDSIZE_SAS40:  6,
		SAS_WORLDSIZE_SAS48: 7,
	}

# <!-- custom: Shared compact profile for almost-all-land maps. Base tiers are fixed; SAS24/32/40/48 are calibrated from Huge anchor using Huge baseline of 18 max players (custom game can reach 18) to keep ratio and tiles-per-player closer to Huge while reducing spacing for underpopulated starts further. See also SAS_MAP_SCRIPT_NAMES_ALMOST_ALL_LAND (GPT-5.3-Codex) -->
def sas_compact_almost_all_land_grid_sizes():
	return {
		SAS_WORLDSIZE_ARENA:  (2, 2),
		SAS_WORLDSIZE_DUEL:  (3, 2),
		SAS_WORLDSIZE_TINY:  (4, 3),
		SAS_WORLDSIZE_SMALL:  (6, 4),
		SAS_WORLDSIZE_STANDARD:  (8, 6),
		SAS_WORLDSIZE_LARGE:  (11, 8),
		SAS_WORLDSIZE_HUGE:  (15, 11),
	}

def sas_get_compact_almost_all_land_grid_size(eWorldSize):
	return sas_lookup_world_size_with_calibrated_sas(eWorldSize, sas_compact_almost_all_land_grid_sizes(), SAS_HUGE_CUSTOM_MAX_PLAYERS)

def sas_lookup_world_size(eWorldSize, values):
	iWorldSize = int(eWorldSize)
	if iWorldSize in values:
		return values[iWorldSize]
	return values[max(values.keys())]

def sas_grid_ratio(iWidth, iHeight):
	return float(iWidth) / float(max(1, iHeight))

def sas_tiles_per_player(iWidth, iHeight, iMaxPlayers):
	return float(iWidth * iHeight) / float(max(1, iMaxPlayers))

def sas_world_default_players(iWorldSize, iFallbackPlayers):
	gc = CyGlobalContext()
	iWorld = int(iWorldSize)
	if iWorld >= 0 and iWorld < gc.getNumWorldInfos():
		return max(1, gc.getWorldInfo(iWorld).getDefaultPlayers())
	return max(1, iFallbackPlayers)

def sas_warn_simple_game_stale_option_once(iOption, iRealCount):
	# <!-- custom: Shared one-time warning for stale Simple Game custom-option cache indices (KI#106); keep implementation minimal with a single boolean flag. (GPT-5.3-Codex) -->
	global SAS_SIMPLE_GAME_STALE_OPTION_WARNED
	if SAS_SIMPLE_GAME_STALE_OPTION_WARNED:
		return
	SAS_SIMPLE_GAME_STALE_OPTION_WARNED = True
	raise KeyError("Notice: if you started this map from Simple Game, you'll likely encounter a stale custom option index KeyError on next Simple Game launch. Workaround: press Esc key many times (or faster keep it pressed several seconds), or play Custom Game to avoid this issue entirely. See KI#106. (requested option %d, real options %d)" % (iOption, iRealCount))

# <!-- custom: Helper for map-size tuning: keep anchor ratio and tiles-per-player roughly stable when extrapolating to larger player caps. Intended for script calibration by maintainers. (GPT-5.3-Codex) -->
def sas_calibrate_grid_from_anchor(iAnchorWidth, iAnchorHeight, iAnchorMaxPlayers, iTargetMaxPlayers):
	fRatio = sas_grid_ratio(iAnchorWidth, iAnchorHeight)
	fTilesPerPlayer = sas_tiles_per_player(iAnchorWidth, iAnchorHeight, iAnchorMaxPlayers)
	fTargetTiles = fTilesPerPlayer * float(max(1, iTargetMaxPlayers))
	iTargetHeight = max(1, int(math.sqrt(fTargetTiles / max(0.0001, fRatio)) + 0.5))
	iTargetWidth = max(1, int((float(iTargetHeight) * fRatio) + 0.5))
	return (iTargetWidth, iTargetHeight)

# <!-- custom: For map-size calibration workflows, compute only the requested world size: base tiers return directly; SAS24/32/40/48 are calibrated on demand from the last base tier (usually Huge) and anchor max players. (GPT-5.3-Codex) -->
def sas_lookup_world_size_with_calibrated_sas(eWorldSize, base_grid_sizes, iAnchorMaxPlayers):
	iWorldSize = int(eWorldSize)
	if iWorldSize in base_grid_sizes:
		return base_grid_sizes[iWorldSize]

	iAnchorWorldSize = max(base_grid_sizes.keys())
	if iWorldSize > iAnchorWorldSize and iWorldSize <= SAS_WORLDSIZE_LARGEST:
		(iAnchorWidth, iAnchorHeight) = base_grid_sizes[iAnchorWorldSize]
		iAnchorPlayers = sas_world_default_players(iAnchorWorldSize, iAnchorMaxPlayers)
		iTargetPlayers = sas_world_default_players(iWorldSize, 0)
		return sas_calibrate_grid_from_anchor(iAnchorWidth, iAnchorHeight, iAnchorPlayers, iTargetPlayers)
	return base_grid_sizes[max(base_grid_sizes.keys())]

# <!-- custom: our helpers actually appears to be a flat grass map that is almost land so kept as such as a playable map then -->
def getDescription():
	return "TXT_KEY_MAP_SCRIPT_SAS_WORLD_SIZES_DESCR"

# <!-- custom: If this helper is selected as a map script, use compact almost-all-land sizing to avoid oversized flat-grass starts. (GPT-5.3-Codex) -->
def getGridSize(argsList):
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return sas_get_compact_almost_all_land_grid_size(eWorldSize)
