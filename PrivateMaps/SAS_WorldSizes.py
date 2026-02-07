# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# <!-- custom: Shared helpers for ARENA/SAS world sizes in map scripts. (GPT-5.2-Codex) -->



SAS_WORLDSIZE_LARGEST = 10
SAS_MAX_PLAYERS = 52



def sas_max_players():
	return SAS_MAX_PLAYERS



def sas_default_sizevalues():
	return {
		0:  1,   # ARENA
		1:  1,   # DUEL
		2:  1,   # TINY
		3:  1,   # SMALL
		4:  2,   # STANDARD
		5:  2,   # LARGE
		6:  3,   # HUGE
		7:  4,   # SAS24
		8:  5,   # SAS32
		9:  6,   # SAS40
		10: 7,   # SAS48
	}



def sas_compact_almost_all_land_grid_sizes():
	# <!-- custom: Shared compact grid profile for almost entirely land maps where default city spacing is too wide (Great Plains baseline), including ARENA and SAS sizes. (GPT-5.3-Codex) -->
	return {
		0:  (4, 3),    # ARENA
		1:  (5, 3),    # DUEL
		2:  (6, 4),    # TINY
		3:  (8, 6),    # SMALL
		4:  (11, 8),   # STANDARD
		5:  (14, 11),  # LARGE
		6:  (18, 14),  # HUGE
		7:  (22, 17),  # SAS24
		8:  (26, 20),  # SAS32
		9:  (30, 23),  # SAS40
		10: (34, 26),  # SAS48
	}



def sas_get_compact_almost_all_land_grid_size(eWorldSize):
	return sas_lookup_world_size(eWorldSize, sas_compact_almost_all_land_grid_sizes())



def sas_lookup_world_size(eWorldSize, values):
	iWorldSize = int(eWorldSize)
	if iWorldSize in values:
		return values[iWorldSize]
	return values[SAS_WORLDSIZE_LARGEST]



# <!-- custom: our helpers actually appears to be a flat grass map that is almost land so kept as such as a playable map then -->
def getDescription():
	return "TXT_KEY_MAP_SCRIPT_SAS_WORLD_SIZES_DESCR"



def getGridSize(argsList):
	# <!-- custom: If this helper is selected as a map script, use compact almost-all-land sizing to avoid oversized flat-grass starts. (GPT-5.3-Codex) -->
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return sas_get_compact_almost_all_land_grid_size(eWorldSize)
