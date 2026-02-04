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



def sas_lookup_world_size(eWorldSize, values):
	iWorldSize = int(eWorldSize)
	if iWorldSize in values:
		return values[iWorldSize]
	return values[SAS_WORLDSIZE_LARGEST]
