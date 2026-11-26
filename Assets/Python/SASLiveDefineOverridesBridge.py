# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Applies the overrides in the mod's SASLiveDefineOverrides/SASLiveDefineOverrides.txt to SAS defines while Civ4 runs, so a value, such as a font size, can be tried without a restart.
# Every define keeps its home, value and comment in GlobalDefines_advciv_sas.xml; a line in the file wins over it, and deleting the line brings the XML value back.
# Each override is pushed with setDefineINT, setDefineFLOAT or setDefineSTRING by the type of its XML tag; setDefineINT also updates AdvCiv's enum cache, so DLL and Python readers that read at use time see it; a value kept in a static or an attribute does not.
# The file sits outside Assets because Civ4 reinitializes its Python when a file under Assets changes, as SASPilot found on 2026-11-13, and like SASPilot it is read as data through a bridge. See KI#128.5. (Claude code Opus 5.5) -->
# <!-- custom: os and re read and parse the files; sys gives the EXE's folder and reports a failed read; CyGlobalContext gives the mod's path and the defines; CyInterface redraws the main interface after a change; SASPythonLogging writes records without importing CvUtil, which Sevopedia modules import before this one. (Claude code Opus 5.5) -->
from CvPythonExtensions import CyGlobalContext, CyInterface
import os
import re
import sys
import SASPythonLogging

# <!-- custom: The file is data, not Python: Codex's review (GPT-6.2-Sol, 2026-11-25) pointed out that a file run with eval(compile(...)), as SASPilot's commands are, can already have done part of its work when an error stops it.
# Here a candidate is parsed and checked whole before anything is applied, so a bad file changes nothing; a push that fails midway is rolled back as far as the setters allow, as refresh describes. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_LINE = re.compile(r"^(SAS_[A-Z0-9_]+)\s*=\s*(.*?)\s*$")
# <!-- custom: A line's value is read by its define's type in the XML, so a float or string define is ready for an override when one is needed (the user's request, 2026-11-26): an integer as 4, a float as 1.5 and a string in double quotes, with \" and \\ for a quote and a backslash inside. (Claude code Opus 5.5) -->
_INT_VALUE = re.compile(r"^-?[0-9]+$")
_FLOAT_VALUE = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
_STRING_VALUE = re.compile(r'^"((?:[^"\\]|\\.)*)"$')
_STRING_ESCAPE = re.compile(r"\\(.)")
_FILE = ("SASLiveDefineOverrides", "SASLiveDefineOverrides.txt")
_XML = ("Assets", "XML", "GlobalDefines_advciv_sas.xml")
_NO_ENTRY = ("SASLiveDefineOverrides", "SASLiveDefineOverridesNoEntry.txt")
# <!-- custom: The defines the mod supports live, apart from the values file, so adding a line cannot make a define live; any other define is refused. See KI#128.7. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_ALLOWED = ("SASLiveDefineOverrides", "SASLiveDefineOverridesAllowed.txt")
_NO_ENTRY_LINE = re.compile(r"^([A-Z0-9_]+):\s*(.*?)\s*$")
# <!-- custom: XML comments are removed before the defines are matched: Codex's review (GPT-6.2-Sol) reproduced a <Define> inside a comment being read as a real one. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_XML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_XML_DEFINE = re.compile(r"<DefineName>\s*(SAS_\w+)\s*</DefineName>\s*<(iDefineIntVal|fDefineFloatVal|DefineTextVal)>([^<]*)</\2>")
_XML_KINDS = {"iDefineIntVal": "INT", "fDefineFloatVal": "FLOAT", "DefineTextVal": "STRING"}
_KIND_NAMES = {"INT": "an integer", "FLOAT": "a float", "STRING": "a quoted string"}
# <!-- custom: The bridge only carries values: it checks that each line names a SAS define and fits its type, never whether a value is sensible for its use; its readers decide, as SASTextScale raises on a font size outside 1 to 4. See KI#128.5. (Claude code Opus 5.5) -->
# <!-- custom: gameUpdate calls between rereads during play, when no screen asks; SASPilot's 20 ticks, as the embedded Python clock moves in coarse steps. (Claude code Opus 5.5) -->
_GAME_UPDATE_TICKS = 20

_enabled = None
_xmlValues = None
_noEntry = None
_allowed = None
_values = {}
_text = None
_pending = None
_changeCount = 0
_gameUpdates = 0
_redrawnChangeCount = 0


def _modPath(parts):
	# <!-- custom: BugPath.getModDir() is None at the main menu, as the first Sevopedia test showed ("TypeError: len() of unsized object"); the DLL's mod path in the Civ4 folder is known from the start. See KI#128.5. (Claude code Opus 5.5) -->
	return os.path.join(os.path.dirname(sys.executable), CyGlobalContext().getModPathInRoot(), *parts)


def _readBytes(parts):
	handle = open(_modPath(parts), "rb")
	text = handle.read()
	handle.close()
	return text


def _parseXml(text):
	# <!-- custom: Each SAS define of GlobalDefines_advciv_sas.xml as name -> (kind, value), kind INT, FLOAT or STRING by its value tag; a text value's XML entities are decoded.
	# Shared with CI, so both read the XML alike. (Claude code Opus 5.5) -->
	xmlValues = {}
	for name, tag, raw in _XML_DEFINE.findall(_XML_COMMENT.sub("", text)):
		kind = _XML_KINDS[tag]
		if kind == "INT":
			xmlValues[name] = (kind, int(raw.strip()))
		elif kind == "FLOAT":
			xmlValues[name] = (kind, float(raw.strip()))
		else:
			xmlValues[name] = (kind, raw.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&"))
	return xmlValues


def _parseValue(kind, raw):
	# <!-- custom: Returns the line's value as the define's type, or None when it does not fit it. (Claude code Opus 5.5) -->
	if kind == "INT":
		if _INT_VALUE.match(raw):
			return int(raw)
	elif kind == "FLOAT":
		if _FLOAT_VALUE.match(raw):
			return float(raw)
	else:
		match = _STRING_VALUE.match(raw)
		if match is not None:
			return _STRING_ESCAPE.sub(r"\1", match.group(1))
	return None


def _show(kind, value):
	if kind == "STRING":
		return '"%s"' % value.replace("\\", "\\\\").replace('"', '\\"')
	if kind == "FLOAT":
		return repr(value)
	return "%d" % value


def _parseNamedReasons(text):
	# <!-- custom: Each define SASLiveDefineOverridesNoEntry.txt or SASLiveDefineOverridesAllowed.txt names, as name -> reason; comment and blank lines are skipped.
	# CI checks the file's form, so a line that does not match is skipped here rather than failing the bridge. (Claude code Opus 5.5) -->
	noEntry = {}
	for line in text.replace("\r\n", "\n").split("\n"):
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		match = _NO_ENTRY_LINE.match(line)
		if match is not None:
			noEntry[match.group(1)] = match.group(2)
	# <!-- custom: A family's later lines say "same reason as" its first; the reason itself is logged, as the first in-game test logged only the pointer (2026-11-26). (Claude code Opus 5.5) -->
	for name in noEntry.keys():
		reason = noEntry[name]
		if reason.startswith("same reason as ") and reason[len("same reason as "):] in noEntry:
			noEntry[name] = noEntry[reason[len("same reason as "):]]
	return noEntry


# <!-- custom: allowed was added with SASLiveDefineOverridesAllowed.txt, as name -> reason; None skips the check, which the CI tests rely on. See KI#128.7. (Claude code Opus 5.5) -->
def _parse(text, xmlValues, noEntry=None, allowed=None):
	# <!-- custom: Raises ValueError naming the line of the first problem: a line that is not SAS_NAME = value, a name set twice, a name that is no SAS define of GlobalDefines_advciv_sas.xml, or a value that does not fit the define's type.
	# The name matters as setDefineINT creates an entry for any name, so a typo would otherwise apply to nothing, silently. (Claude code Opus 5.5) -->
	values = {}
	lines = {}
	iLine = 0
	for line in text.replace("\r\n", "\n").split("\n"):
		iLine += 1
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		match = _LINE.match(line)
		if match is None:
			raise ValueError("line %d: expected SAS_NAME = value, got %r" % (iLine, line))
		key = match.group(1)
		if key in values:
			raise ValueError("line %d: %s already set on line %d" % (iLine, key, lines[key]))
		if key not in xmlValues:
			raise ValueError("line %d: %s is no define in GlobalDefines_advciv_sas.xml" % (iLine, key))
		# <!-- custom: NoEntry was a signpost CI alone enforced, so a local line could still reach a privacy opt-in or a define whose readers keep their value; Codex's review (GPT-6.2-Sol) advised enforcing it here too, and the user agreed on 2026-11-26, so the list decides in game as well. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if noEntry and key in noEntry:
			raise ValueError("line %d: %s is in SASLiveDefineOverridesNoEntry.txt: %s" % (iLine, key, noEntry[key]))
		# <!-- custom: A define outside the allowed list may have readers that keep their first value, so its override could apply and reach nothing, silently; refusing it says so instead.
		# NoEntry is checked first, so a define listed there gets its own reason. See KI#128.7. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if allowed is not None and key not in allowed:
			raise ValueError("line %d: %s is not in SASLiveDefineOverridesAllowed.txt, so live overrides are unsupported for it: change it in GlobalDefines_advciv_sas.xml and restart Civ4" % (iLine, key))
		kind = xmlValues[key][0]
		value = _parseValue(kind, match.group(2))
		if value is None:
			raise ValueError("line %d: %s takes %s, got %r" % (iLine, key, _KIND_NAMES[kind], match.group(2)))
		values[key] = value
		lines[key] = iLine
	return values


def _getDefine(gc, kind, key):
	if kind == "INT":
		return gc.getDefineINT(key)
	if kind == "FLOAT":
		return gc.getDefineFLOAT(key)
	return gc.getDefineSTRING(key)


def _setDefine(gc, kind, key, value):
	# <!-- custom: setDefineINT refreshes the define's enum cache entry, setDefineFLOAT refreshes all of AdvCiv's cached floats, and setDefineSTRING only sets the define, as no cache keeps strings. (Claude code Opus 5.5) -->
	if kind == "INT":
		gc.setDefineINT(key, value)
	elif kind == "FLOAT":
		gc.setDefineFLOAT(key, value)
	else:
		gc.setDefineSTRING(key, value)


def _isEnabled():
	# <!-- custom: SAS_LIVE_DEFINE_OVERRIDES_ON is read once, so 0 never opens the file nor reads the XML for names. (Claude code Opus 5.5) -->
	global _enabled
	if _enabled is None:
		_enabled = CyGlobalContext().getDefineINT("SAS_LIVE_DEFINE_OVERRIDES_ON") > 0
		SASPythonLogging.writeRecord("SAS_LIVE_DEFINE_OVERRIDES", "outcome=%s" % (_enabled and "ENABLED" or "DISABLED"))
	return _enabled


def refresh(bSettle=False):
	# <!-- custom: Rereads the file and applies a changed set that parses; returns the change count, which grows by one per applied change, so code that built something once from a define, such as SASTextScale's tags or the Sevopedia's layout, knows to build it again.
	# The file is small, so comparing its whole text cannot miss an edit, unlike SASPilot's size and mtime stamp.
	# A save in progress can make the read fail; the next call retries.
	# With bSettle, a changed text applies only once a second call reads the same text: Codex's review (GPT-6.2-Sol, 2026-11-26) pointed out that a save caught midway, such as an emptied file, parses as valid and would apply as deleted lines, then apply again when the save ends.
	# The game-update polls settle, at the cost of one more poll per edit; the reads at a game's start and at a Sevopedia jump apply at once, as a reader waits on them, so a save caught midway by one of those reads still applies.
	# A failed read forgets the pending text, so the two reads are consecutive polls, not two successful reads around a failed one, as Codex's review (GPT-6.2-Sol) reproduced.
	# A bad file keeps the defines as they were and is logged, as the XML values underneath keep the game working. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	global _xmlValues, _noEntry, _allowed, _values, _text, _pending, _changeCount
	if not _isEnabled():
		return _changeCount
	try:
		text = _readBytes(_FILE)
		# <!-- custom: Kept only once read whole: the first version set the dictionary before opening the XML, so a failed first read left it empty and rejected every line for good, as Codex's review (GPT-6.2-Sol) reproduced. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		# <!-- custom: Read as bytes, not decoded: Python 2.4 then hands setDefineSTRING a plain string, and a str of UTF-8 bytes matches the same patterns. (Claude code Opus 5.5) -->
		if _xmlValues is None:
			# <!-- custom: The NoEntry and allowed lists are read with the XML, once; all three are kept only once all were read whole. (Claude code Opus 5.5) -->
			noEntry = _parseNamedReasons(_readBytes(_NO_ENTRY))
			allowed = _parseNamedReasons(_readBytes(_ALLOWED))
			_xmlValues = _parseXml(_readBytes(_XML))
			_noEntry = noEntry
			_allowed = allowed
	except (IOError, OSError):
		_pending = None
		SASPythonLogging.writeRecord("SAS_LIVE_DEFINE_OVERRIDES", "outcome=READ_RETRY error=\"%s\"" % str(sys.exc_info()[1]).replace("\"", "'"))
		return _changeCount
	if text == _text:
		_pending = None
		return _changeCount
	if bSettle and text != _pending:
		_pending = text
		return _changeCount
	_pending = None
	_text = text
	try:
		values = _parse(text, _xmlValues, _noEntry, _allowed)
	except ValueError:
		SASPythonLogging.writeRecord("SAS_LIVE_DEFINE_OVERRIDES", "outcome=REJECTED keptChangeCount=%d reason=\"%s\"" % (_changeCount, str(sys.exc_info()[1]).replace("\"", "'")))
		return _changeCount
	if values == _values:
		return _changeCount
	gc = CyGlobalContext()
	names = dict(values)
	names.update(_values)
	# <!-- custom: list() so the same code also runs under Python 3, where CI's refresh test runs it. (Claude code Opus 5.5) -->
	names = list(names.keys())
	names.sort()
	changes = []
	# <!-- custom: Deleting a line pushes the XML file's own value back, so the XML is restored without a restart.
	# The value is read from the file rather than kept from the define before the first override: Civ4 reinitializes this module when a file under Assets changes, while the DLL keeps the overridden define, so a kept value could be the override itself.
	# Limits, from Codex's review (GPT-6.2-Sol): a module XML loaded after GlobalDefines_advciv_sas.xml could set the same define, which deletion would not restore, though no SAS module sets one; and after such a reinitialization this module no longer knows the overrides the DLL still holds, so a line deleted before its first reread stays applied until Civ4 restarts. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: A push that raises rolls back the defines already pushed to the values they held just before, and leaves the read text unset, so the next reread tries again, even if the rollback itself fails.
	# Kept from the first design: Codex's review (GPT-6.2-Sol) reproduced a setter that raised leaving part of a change applied and the file never retried, as its text already counted as read. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	done = []
	before = {}
	try:
		for key in names:
			if key in values:
				if values[key] == _values.get(key):
					continue
				kind = _xmlValues[key][0]
				before[key] = _getDefine(gc, kind, key)
				_setDefine(gc, kind, key, values[key])
				if key in _values:
					szFrom = _show(kind, _values[key])
				else:
					szFrom = "xml" + _show(kind, _xmlValues[key][1])
				changes.append("%s:%s->%s" % (key, szFrom, _show(kind, values[key])))
			else:
				kind = _xmlValues[key][0]
				before[key] = _getDefine(gc, kind, key)
				_setDefine(gc, kind, key, _xmlValues[key][1])
				changes.append("%s:%s->xml%s" % (key, _show(kind, _values[key]), _show(kind, _xmlValues[key][1])))
			done.append(key)
		# <!-- custom: Lets the DLL rebuild state it built once from defines, such as BBAI's category levels; one call for every family, which the DLL dispatches.
		# Inside the push, so a failure rolls the change back and the file is retried: a first draft called it after the change was counted and logged, so, as Codex's review (GPT-6.2-Sol) found, a failing call, such as with a DLL older than this bridge, raised out of preGameStart and the refill was never retried. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		gc.onSASLiveDefineOverridesApplied()
	except:
		szError = str(sys.exc_info()[1]).replace("\"", "'")
		_text = None
		try:
			for key in done:
				_setDefine(gc, _xmlValues[key][0], key, before[key])
			# <!-- custom: Refills again from the restored values, so DLL state matches the defines after a rollback too. (Claude code Opus 5.5) -->
			gc.onSASLiveDefineOverridesApplied()
		except:
			szError = szError + "; rollback failed: " + str(sys.exc_info()[1]).replace("\"", "'")
		SASPythonLogging.writeRecord("SAS_LIVE_DEFINE_OVERRIDES", "outcome=PUSH_FAILED keptChangeCount=%d reason=\"%s\"" % (_changeCount, szError))
		return _changeCount
	_values = values
	_changeCount += 1
	active = ["%s=%s" % (key, _show(_xmlValues[key][0], values[key])) for key in names if key in values]
	SASPythonLogging.writeRecord("SAS_LIVE_DEFINE_OVERRIDES", "outcome=APPLIED changeCount=%d changes=%s active=%s" % (_changeCount, ",".join(changes), ",".join(active) or "-"))
	return _changeCount


def onGameUpdate(argsList=None):
	# <!-- custom: Rereads the file every _GAME_UPDATE_TICKS game updates, so an edit reaches readers no screen rebuild asks for, such as the DLL's hover text.
	# It counts game updates, the DLL's CvGame::update steps, not time: Codex's review (GPT-6.2-Sol) found that CvGame.cpp can run many per frame, and sends none between turns or in WorldBuilder.
	# Measured on 2026-11-25 in an idle turn-0 game, an edit applied 4.3 seconds after the save, six times in a row; since these polls settle, an edit applies one poll later. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	global _gameUpdates, _redrawnChangeCount
	if not _isEnabled():
		return
	_gameUpdates += 1
	if _gameUpdates >= _GAME_UPDATE_TICKS:
		_gameUpdates = 0
		# <!-- custom: Tested on 2026-11-26 with SAS_UI_FONT_LABEL = 4 in a turn-150 game: only the turn line, redrawn each update, followed, while the scoreboard, research bar and unit panel kept size 3 until their own dirty bits were set.
		# So after each change the whole main interface is marked dirty: makeInterfaceDirty is far costlier than one dirty bit, as AdvCiv notes in CvPlayer.cpp, but it runs only on a change, and it reaches any define the interface reads, not only fonts.
		# The count is compared rather than refresh's result, so a change the Sevopedia applied first is redrawn here too. Advisors already lay themselves out at each opening. See KI#128.5. (Claude code Opus 5.5) -->
		if refresh(True) != _redrawnChangeCount:
			_redrawnChangeCount = _changeCount
			CyInterface().makeInterfaceDirty()


def getChangeCount():
	return _changeCount
