# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

from CvPythonExtensions import *
import BugData


gc = CyGlobalContext()

_TABLE_ID = "AdvCivSASBattleHistory"
_ENTRIES_KEY = "entries"
_MAX_ENTRIES = None
_PENDING_COMBAT_ACTORS = None

# <!-- custom: BugData persists this table in the save without DLL or save-format changes; old saves simply start with no rows and record battles from the first combat after loading. Store rows per player because advisor perspective can change. (GPT-5.5) -->

def _getMaxEntries():
	global _MAX_ENTRIES
	if _MAX_ENTRIES is None:
		_MAX_ENTRIES = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_BATTLE_HISTORY_MAX_ENTRIES")
	return _MAX_ENTRIES


def _getEntriesByPlayer():
	table = BugData.getTable(_TABLE_ID)
	if table.hasValue(_ENTRIES_KEY):
		entries = table.getValue(_ENTRIES_KEY)
		if isinstance(entries, dict):
			return _sanitizeEntriesByPlayer(entries)
	return {}


def _saveEntriesByPlayer(entriesByPlayer):
	BugData.getTable(_TABLE_ID).setValue(_ENTRIES_KEY, _sanitizeEntriesByPlayer(entriesByPlayer))


def _sanitizeEntry(entry):
	# <!-- custom: BugData pickles this table; Civ4 enum objects such as PlayerTypes are not pickle-safe, so force stored rows to plain Python ints. (GPT-5.5) -->
	#
	# Traceback (most recent call last):
	# File "CvEventInterface", line 35, in onEvent
	# File "BugEventManager", line 346, in handleEvent
	# File "BugEventManager", line 351, in _dispatchEvent
	# File "BugEventManager", line 390, in _handleOnPreSaveEvent
	# File "BugData", line 92, in save
	# File "BugData", line 116, in save
	# File "BugData", line 119, in save
	# File "BugData", line 261, in _save
	#
	aValues = []
	for value in entry:
		aValues.append(int(value))
	return tuple(aValues)


def _sanitizeEntriesByPlayer(entriesByPlayer):
	safeEntriesByPlayer = {}
	for szPlayer, entries in entriesByPlayer.items():
		if isinstance(entries, list):
			safeEntries = []
			for entry in entries:
				safeEntries.append(_sanitizeEntry(entry))
			safeEntriesByPlayer[str(szPlayer)] = safeEntries
	return safeEntriesByPlayer


def _appendEntry(entriesByPlayer, iPlayer, entry, iMaxEntries):
	szPlayer = str(iPlayer)
	entries = entriesByPlayer.get(szPlayer, [])
	entries.append(entry)
	if iMaxEntries > 0 and len(entries) > iMaxEntries:
		entries = entries[-iMaxEntries:]
	entriesByPlayer[szPlayer] = entries


def noteCombatActors(cdAttacker, cdDefender):
	global _PENDING_COMBAT_ACTORS
	_PENDING_COMBAT_ACTORS = (
		int(cdAttacker.eOwner),
		int(cdDefender.eOwner),
		int(cdAttacker.iCurrCombatStr),
		int(cdAttacker.iMaxCombatStr),
		int(cdDefender.iCurrCombatStr),
		int(cdDefender.iMaxCombatStr),
	)


def recordCombatResult(pWinner, pLoser):
	global _PENDING_COMBAT_ACTORS
	iMaxEntries = _getMaxEntries()
	if iMaxEntries == 0:
		return
	iWinner = pWinner.getOwner()
	iLoser = pLoser.getOwner()
	if iWinner < 0 or iLoser < 0:
		return
	entry = (
		CyGame().getGameTurn(),
		iWinner,
		iLoser,
		pWinner.getUnitType(),
		pLoser.getUnitType(),
		pWinner.getX(),
		pWinner.getY(),
	)
	if _PENDING_COMBAT_ACTORS is not None:
		iAttacker, iDefender = _PENDING_COMBAT_ACTORS[:2]
		# <!-- custom: only attach combat-log strength data when its attacker/defender owners match this combat result, so a stale pending tuple from an interrupted/odd combat cannot corrupt the next row. Credit: Claude Code Opus 4.7 review. (GPT-5.5) -->
		if (iAttacker == iWinner and iDefender == iLoser) or (iAttacker == iLoser and iDefender == iWinner):
			entry += _PENDING_COMBAT_ACTORS
	_PENDING_COMBAT_ACTORS = None
	entriesByPlayer = _getEntriesByPlayer()
	_appendEntry(entriesByPlayer, iWinner, entry, iMaxEntries)
	if iLoser != iWinner:
		_appendEntry(entriesByPlayer, iLoser, entry, iMaxEntries)
	_saveEntriesByPlayer(entriesByPlayer)


def getEntriesForPlayer(iPlayer):
	entriesByPlayer = _getEntriesByPlayer()
	entries = entriesByPlayer.get(str(iPlayer), [])
	if isinstance(entries, list):
		return entries
	return []
