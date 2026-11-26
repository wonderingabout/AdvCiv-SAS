# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A cached read of defines that SASLiveDefineOverrides can change during play: one shared cache, emptied when the bridge applies a change, so a reader using it sees an override without code of its own.
# Before it, each reader kept a define in its own module global or self.
# attribute, which an override never reached, so each needed its own rebuild; the user asked for one universal way instead (2026-11-25), and Codex's review (GPT-6.2-Sol) advised a prototype on the font sizes and one Sevopedia reader.
# It caches only the defines read through it, overridden or not, and is opt-in, for raw defines, SAS or inherited, though the bridge overrides SAS ones only: a value built from a define, such as a font tag or a layout, still belongs to its owner, which rebuilds on the same change count. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
# <!-- custom: Its cache empties on the bridge's writes only, so it does not suit a define that other code changes during play with setDefine*, such as FIELD_OF_VIEW in CvMainInterface.py, MINIMAP_RENDER_SIZE in CvReplayScreen.py or the river values Water.py sets: read those with gc at each use, as Codex's review (GPT-6.2-Sol) pointed out. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
# <!-- custom: The module's name says what a caller gets, the define's current value, override included, whether it comes from the cache or a fresh read: the caches empty whenever an override changes, so both give the same value.
# It was getLiveInt, which the user found suggested a fresh read each time, then SASDefines.getCurrentInt; SASDefines could read as the defines of GlobalDefines_advciv_sas.xml only, so "current" moved into the module's name. (Claude code Opus 5.5) -->
# <!-- custom: getFloat and getString came with the bridge's float and string overrides, ready for a define of either type (the user's request, 2026-11-26); no SAS define is a float, and SAS's text defines are set once. (Claude code Opus 5.5) -->
# <!-- custom: The bridge empties the caches when it applies a change, through addChangeListener, so a cached read is one dictionary lookup.
# Until KI#128.9 each getter asked the bridge's change count at each read: measured in game, that read cost 167 ns against 279 ns through gc, and once every Python read by name came through here, the user asked whether it could be faster; under Python 2.4 the same read went from 191 ns to 80 ns, against 39 ns for a lazy attribute and 18 ns for a kept one. (Claude code Opus 5.5) -->
# <!-- custom: CyGlobalContext reads the defines; the bridge tells this module when its overrides changed them; both are leaf modules, so any screen or helper can import this one. (Claude code Opus 5.5) -->
from CvPythonExtensions import CyGlobalContext
import SASLiveDefineOverridesBridge

_intCache = {}
_floatCache = {}
_stringCache = {}
_gc = []


# <!-- custom: Took the change count to remember until KI#128.9; the bridge now calls it after each applied change, so it only empties the caches. (Claude code Opus 5.5) -->
def _clear():
	_intCache.clear()
	_floatCache.clear()
	_stringCache.clear()


SASLiveDefineOverridesBridge.addChangeListener(_clear)


def _context():
	if not _gc:
		_gc.append(CyGlobalContext())
	return _gc[0]


def getInt(szName):
	# <!-- custom: A dictionary hit; a miss reads the define once, which returns any override the bridge pushed. (Claude code Opus 5.5) -->
	try:
		return _intCache[szName]
	except KeyError:
		value = _context().getDefineINT(szName)
		_intCache[szName] = value
		return value


def getFloat(szName):
	try:
		return _floatCache[szName]
	except KeyError:
		value = _context().getDefineFLOAT(szName)
		_floatCache[szName] = value
		return value


def getString(szName):
	try:
		return _stringCache[szName]
	except KeyError:
		value = _context().getDefineSTRING(szName)
		_stringCache[szName] = value
		return value
