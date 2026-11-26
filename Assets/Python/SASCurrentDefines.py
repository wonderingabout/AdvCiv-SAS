# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A cached read of defines that SASLiveDefineOverrides can change during play: one shared cache, emptied when the bridge's change count moves, so a reader using it sees an override without code of its own.
# Before it, each reader kept a define in its own module global or self.
# attribute, which an override never reached, so each needed its own rebuild; the user asked for one universal way instead (2026-11-25), and Codex's review (GPT-6.2-Sol) advised a prototype on the font sizes and one Sevopedia reader.
# It caches only the defines read through it, overridden or not, and is opt-in, for raw defines, SAS or inherited, though the bridge overrides SAS ones only: a value built from a define, such as a font tag or a layout, still belongs to its owner, which rebuilds on the same change count. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
# <!-- custom: Its cache empties on the bridge's writes only, so it does not suit a define that other code changes during play with setDefine*, such as FIELD_OF_VIEW in CvMainInterface.py, MINIMAP_RENDER_SIZE in CvReplayScreen.py or the river values Water.py sets: read those with gc at each use, as Codex's review (GPT-6.2-Sol) pointed out. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
# <!-- custom: The module's name says what a caller gets, the define's current value, override included, whether it comes from the cache or a fresh read: the caches empty whenever an override changes, so both give the same value.
# It was getLiveInt, which the user found suggested a fresh read each time, then SASDefines.getCurrentInt; SASDefines could read as the defines of GlobalDefines_advciv_sas.xml only, so "current" moved into the module's name. (Claude code Opus 5.5) -->
# <!-- custom: getFloat and getString came with the bridge's float and string overrides, ready for a define of either type (the user's request, 2026-11-26); no SAS define is a float, and SAS's text defines are set once.
# Each getter checks the change count itself: a shared helper for it cost a function call, 179 ns a read against 151 ns inline, best of 5 runs of 200,000 under Python 2.4. (Claude code Opus 5.5) -->
# <!-- custom: CyGlobalContext reads the defines; the bridge's change count says when its overrides changed them; both are leaf modules, so any screen or helper can import this one. (Claude code Opus 5.5) -->
from CvPythonExtensions import CyGlobalContext
import SASLiveDefineOverridesBridge

_intCache = {}
_floatCache = {}
_stringCache = {}
_cacheChangeCount = [0]
_gc = []


def _clear(iChangeCount):
	_intCache.clear()
	_floatCache.clear()
	_stringCache.clear()
	_cacheChangeCount[0] = iChangeCount
	if not _gc:
		_gc.append(CyGlobalContext())


def getInt(szName):
	# <!-- custom: A dictionary hit after one change-count comparison; a miss reads the define once, which returns any override the bridge pushed. (Claude code Opus 5.5) -->
	iChangeCount = SASLiveDefineOverridesBridge.getChangeCount()
	if iChangeCount != _cacheChangeCount[0] or not _gc:
		_clear(iChangeCount)
	if szName in _intCache:
		return _intCache[szName]
	value = _gc[0].getDefineINT(szName)
	_intCache[szName] = value
	return value


def getFloat(szName):
	iChangeCount = SASLiveDefineOverridesBridge.getChangeCount()
	if iChangeCount != _cacheChangeCount[0] or not _gc:
		_clear(iChangeCount)
	if szName in _floatCache:
		return _floatCache[szName]
	value = _gc[0].getDefineFLOAT(szName)
	_floatCache[szName] = value
	return value


def getString(szName):
	iChangeCount = SASLiveDefineOverridesBridge.getChangeCount()
	if iChangeCount != _cacheChangeCount[0] or not _gc:
		_clear(iChangeCount)
	if szName in _stringCache:
		return _stringCache[szName]
	value = _gc[0].getDefineSTRING(szName)
	_stringCache[szName] = value
	return value
