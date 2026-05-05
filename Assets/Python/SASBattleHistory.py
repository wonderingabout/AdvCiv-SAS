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
_CAPTURE_DATA_START = 13
_END_STRENGTH_DATA_START = 16

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


def _getEntryWithCapture(entry, iCapturingPlayer, iCapturedUnitType):
	# <!-- custom: capture info is stored after the combat-log strength block; pad rare/no-strength rows so older tuple parsing keeps its fixed offsets. (GPT-5.5) -->
	aEntry = list(entry)
	while len(aEntry) < _CAPTURE_DATA_START:
		aEntry.append(0)
	if len(aEntry) >= _CAPTURE_DATA_START + 3:
		if aEntry[_CAPTURE_DATA_START] == iCapturingPlayer and aEntry[_CAPTURE_DATA_START + 1] == iCapturedUnitType:
			aEntry[_CAPTURE_DATA_START + 2] += 1
		else:
			aEntry[_CAPTURE_DATA_START] = iCapturingPlayer
			aEntry[_CAPTURE_DATA_START + 1] = iCapturedUnitType
			aEntry[_CAPTURE_DATA_START + 2] = 1
	else:
		aEntry.extend([iCapturingPlayer, iCapturedUnitType, 1])
	return tuple(aEntry)


def _getUnitEndCombatStr(pUnit, iMaxCombatStr):
	if iMaxCombatStr <= 0 or pUnit.maxHitPoints() <= 0:
		return 0
	return (iMaxCombatStr * pUnit.currHitPoints()) / pUnit.maxHitPoints()


def _matchesCapturedBattle(entry, iCapturingPlayer, iOldOwner, iOldUnitType):
	if len(entry) < 7:
		return False
	# <!-- custom: don't require plot equality here; combatResult may record the winner's pre-advance plot, while unitCaptured fires after the captured unit is created on the loser's plot. Scan newest-first within the same turn instead. (GPT-5.5) -->
	return (entry[0] == CyGame().getGameTurn() and entry[1] == iCapturingPlayer and entry[2] == iOldOwner and entry[4] == iOldUnitType)


def _patchCapturedEntry(entries, iCapturingPlayer, iOldOwner, iOldUnitType, iCapturedUnitType):
	iIndex = len(entries) - 1
	while iIndex >= 0:
		if _matchesCapturedBattle(entries[iIndex], iCapturingPlayer, iOldOwner, iOldUnitType):
			entries[iIndex] = _getEntryWithCapture(entries[iIndex], iCapturingPlayer, iCapturedUnitType)
			return True
		iIndex -= 1
	return False


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
		# <!-- custom: only attach combat-log strength data when its attacker/defender owners match this combat result, so a stale pending tuple from an interrupted/odd combat cannot corrupt the next row. Credit: Claude code Opus 4.7 review. (GPT-5.5) -->
		if (iAttacker == iWinner and iDefender == iLoser) or (iAttacker == iLoser and iDefender == iWinner):
			entry += _PENDING_COMBAT_ACTORS
			iAttackerEndStr = 0
			iDefenderEndStr = 0
			# <!-- custom: combatResult fires after combat damage is applied, so store battle-end effective strength here; capture data still lives before this block for compatibility with the previous saved tuple layout. (GPT-5.5) -->
			if iAttacker == iWinner:
				iAttackerEndStr = _getUnitEndCombatStr(pWinner, _PENDING_COMBAT_ACTORS[3])
			else:
				iDefenderEndStr = _getUnitEndCombatStr(pWinner, _PENDING_COMBAT_ACTORS[5])
			while len(entry) < _END_STRENGTH_DATA_START:
				entry += (0,)
			entry += (iAttackerEndStr, iDefenderEndStr)
	_PENDING_COMBAT_ACTORS = None
	entriesByPlayer = _getEntriesByPlayer()
	_appendEntry(entriesByPlayer, iWinner, entry, iMaxEntries)
	if iLoser != iWinner:
		_appendEntry(entriesByPlayer, iLoser, entry, iMaxEntries)
	_saveEntriesByPlayer(entriesByPlayer)


def recordUnitCaptured(iOldOwner, iOldUnitType, pNewUnit):
	# <!-- custom: cast event args to plain int; PlayerTypes/UnitTypes arrive as enum/SWIG wrappers from CyArgsList, which makes str(iOldOwner) miss the "3"-style per-player key and entry[2] == iOldOwner fail on int-vs-enum comparison, leaving Cap# / Cap blank. Same pattern as noteCombatActors. (Claude Code Opus 4.7) -->
	iOldOwner = int(iOldOwner)
	iOldUnitType = int(iOldUnitType)
	iCapturingPlayer = int(pNewUnit.getOwner())
	iCapturedUnitType = int(pNewUnit.getUnitType())
	entriesByPlayer = _getEntriesByPlayer()
	bChanged = False
	for iPlayer in (iCapturingPlayer, iOldOwner):
		szPlayer = str(iPlayer)
		entries = entriesByPlayer.get(szPlayer, [])
		if _patchCapturedEntry(entries, iCapturingPlayer, iOldOwner, iOldUnitType, iCapturedUnitType):
			entriesByPlayer[szPlayer] = entries
			bChanged = True
	if bChanged:
		_saveEntriesByPlayer(entriesByPlayer)


def getEntriesForPlayer(iPlayer):
	entriesByPlayer = _getEntriesByPlayer()
	entries = entriesByPlayer.get(str(iPlayer), [])
	if isinstance(entries, list):
		return entries
	return []
