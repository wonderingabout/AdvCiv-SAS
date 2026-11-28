# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotOptions: the settings a player changes in Civ4's Options screen and BUG's, as plain commands: 'options' lists them, 'option' sets one.
# Before (2026-11-28), only BUG's screen was reachable, through the UI recorder ('uioptions', 'uioption'), and only for the controls the screen draws; Civ4's own Options screen had no command, and 'resolution' alone covered one of its settings.
# The user asked for every Civ4 and BUG option as a command after the city screen; Codex (GPT-6.2-Sol) proposed one module with an adapter per source, source-qualified names, the configured and effective value where they differ, whether a change applies now or needs a reload or restart, reads in play and writes in the all role, and saving made explicit, as another client may share the files.
# Tested the same day: Civ4's profile (AppData/Local/My Games/beyond the sword/Profiles/<name>.pfl) is written only on request, so a change stays in memory until save=1, which rewrote it byte for byte when nothing had changed; BUG's INI files, however, are written within a quarter second by the main interface itself (CvMainInterface.updateScreen calls BugOptions.write every 250 ms), not when BUG's screen closes as we first assumed, so a BUG change is saved at once (Advanced Combat Odds.ini changed one second after 'option name=bug:ACO__Enabled').
# Each change goes through the call the screen's own callback makes (CvOptionsScreenCallbackInterface.py, BugOptionsScreen.py), so what the game does on a change, such as BUG's change handlers, still runs. (Claude code Opus 5.5 + GPT-6.2-Sol) -->

# <!-- custom: BugOptions holds BUG's option registry, g_options, which 'options' iterates; it is BUG's own module, loaded at game start. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import BugOptions

gc = CyGlobalContext()

# <!-- custom: The loader binds the command module before the first command. (Claude code Opus 5.5) -->
saspilot = None

# <!-- custom: This module's command help, which the loader adds to the command module's. (Claude code Opus 5.5) -->
_HELP = {}

# <!-- custom: The Options screen's dropdowns, sliders and checkboxes kept in the profile, as (name, getter, setter, kind, choices, applies): the screen's callbacks show a restart popup after the globe view (reload) and graphics level (restart); the screen draws no graphics level, so it is left out.
# Resolution is listed read-only, as 'resolution' answers the EXE's keep dialog the change needs. (Claude code Opus 5.5) -->
_LEVELS = ("high", "medium", "low")
_PROFILE_SETTINGS = (
	("renderQuality", "getRenderQualityLevel", "setRenderQualityLevel", "choice", _LEVELS, "now"),
	("globeView", "getGlobeViewRenderLevel", "setGlobeViewRenderLevel", "choice", _LEVELS, "reload"),
	("movieQuality", "getMovieQualityLevel", "setMovieQualityLevel", "choice", _LEVELS, "now"),
	("mainMenu", "getMainMenu", "setMainMenu", "choice", None, "now"),
	("antiAliasing", "getAntiAliasing", "setAntiAliasing", "choice", None, "now"),
	("masterVolume", "getMasterVolume", "setMasterVolume", "volume", None, "now"),
	("musicVolume", "getMusicVolume", "setMusicVolume", "volume", None, "now"),
	("soundEffectsVolume", "getSoundEffectsVolume", "setSoundEffectsVolume", "volume", None, "now"),
	("speechVolume", "getSpeechVolume", "setSpeechVolume", "volume", None, "now"),
	("ambienceVolume", "getAmbienceVolume", "setAmbienceVolume", "volume", None, "now"),
	("interfaceVolume", "getInterfaceVolume", "setInterfaceVolume", "volume", None, "now"),
	("masterNoSound", "isMasterNoSound", "setMasterNoSound", "boolean", None, "now"),
	("musicNoSound", "isMusicNoSound", "setMusicNoSound", "boolean", None, "now"),
	("soundEffectsNoSound", "isSoundEffectsNoSound", "setSoundEffectsNoSound", "boolean", None, "now"),
	("speechNoSound", "isSpeechNoSound", "setSpeechNoSound", "boolean", None, "now"),
	("ambienceNoSound", "isAmbienceNoSound", "setAmbienceNoSound", "boolean", None, "now"),
	("interfaceNoSound", "isInterfaceNoSound", "setInterfaceNoSound", "boolean", None, "now"),
	("clockOn", "isClockOn", "setClockOn", "boolean", None, "now"),
	("clock24Hours", "is24Hours", "set24Hours", "boolean", None, "now"),
	("resolution", "getResolution", None, "choice", None, "use 'resolution'"),
)
_SOURCES = ("player", "graphic", "profile", "bug")


def _profileChoices(szName, profile):
	# <!-- custom: The screen's own labels: anti-aliasing's samples per index, the main menus' descriptions, the resolutions' strings. (Claude code Opus 5.5) -->
	if szName == "antiAliasing":
		return [str((0, 2, 4, 8, 16)[i]) for i in range(profile.getAntiAliasingMaxMultiSamples() + 1)]
	if szName == "mainMenu":
		return [gc.getMainMenus(i).getDescription() for i in range(gc.getNumMainMenus())]
	# <!-- custom: sas-ci-string-compare-exemption: The profile setting names are this module's own stable keys. (Claude code Opus 5.5) -->
	if szName == "resolution":
		return [profile.getResolutionString(i) for i in range(profile.getResolutionMaxModes())]
	return None


def _graphicApplies(iOption):
	# <!-- custom: CvOptionsScreenCallbackInterface.isImmediate's rule (advc.076): single unit graphics and fullscreen need a restart, the terrain and texture resolutions a reload, the rest apply at once. (Claude code Opus 5.5) -->
	if iOption in (GraphicOptionTypes.GRAPHICOPTION_SINGLE_UNIT_GRAPHICS, GraphicOptionTypes.GRAPHICOPTION_FULLSCREEN):
		return "restart"
	if iOption in (GraphicOptionTypes.GRAPHICOPTION_HIRES_TERRAIN, GraphicOptionTypes.GRAPHICOPTION_LOWRES_TEXTURES):
		return "reload"
	return "now"


def _bugIsList(option):
	return hasattr(option, "getValues") and hasattr(option, "setIndex")


def _bugRow(option):
	row = {"name": "bug:" + option.getID(), "source": "bug", "type": option.getType(), "applies": "now"}
	# <!-- custom: BUG returns "XML key TXT_KEY_BUG_OPT_..._TEXT not found" as the title of an option with no title text, such as ACO__Debug, which its screen does not show, or one whose text base AdvCiv commented out as unused (advc.004), such as the GP bar types; null says there is none. (Claude code Opus 5.5) -->
	row["title"] = option.getTitle()
	if row["title"].startswith("XML key ") and row["title"].endswith(" not found"):
		row["title"] = None
	# <!-- custom: enabled is false for an option BUG turned off (one needing a DLL feature it lacks) or one whose master switch (andId) is off, which the screen greys out. (Claude code Opus 5.5) -->
	row["enabled"] = bool(option.isEnabled() and option.getAndOptionValue())
	if hasattr(option, "getFile"):
		row["ini"] = "%s [%s] %s" % (option.getFile().id, option.getSection(), option.getKey())
	# <!-- custom: A parameterized option, one value per player or per item (its INI key holds %s), has no single value to list or set. (Claude code Opus 5.5) -->
	if hasattr(option, "isParameterized") and option.isParameterized():
		row["parameterized"] = True
		return row
	row["value"] = option.getRealValue()
	row["default"] = option.getDefault()
	if _bugIsList(option):
		row["choices"] = [str(value) for value in option.getDisplayValues()]
		row["index"] = option.getIndex()
	return row


def _rows(szSource):
	profile = CyUserProfile()
	rows = []
	if szSource in (None, "player"):
		# <!-- custom: No active player yet, as before a game is set up, gives value null rather than gc.getPlayer(-1), which asserts in the DLL and returns null, failing the whole listing (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iActive = gc.getGame().getActivePlayer()
		player = None
		if iActive >= 0:
			player = gc.getPlayer(iActive)
		for i in range(PlayerOptionTypes.NUM_PLAYEROPTION_TYPES):
			info = gc.getPlayerOptionsInfoByIndex(i)
			# <!-- custom: configured is the profile's setting, effective the active player's flag the game uses; sendPlayerOption changes the flag, and the two can differ, as on a loaded save. (Claude code Opus 5.5) -->
			value = None
			if player is not None:
				value = bool(player.isOption(i))
			rows.append({"name": "player:" + info.getType(), "source": "player", "title": info.getDescription(), "type": "boolean", "value": value, "configured": bool(profile.getPlayerOption(i)), "applies": "now"})
	if szSource in (None, "graphic"):
		for i in range(GraphicOptionTypes.NUM_GRAPHICOPTION_TYPES):
			info = gc.getGraphicOptionsInfoByIndex(i)
			rows.append({"name": "graphic:" + info.getType(), "source": "graphic", "title": info.getDescription(), "type": "boolean", "value": bool(profile.getGraphicOption(i)), "applies": _graphicApplies(i)})
	if szSource in (None, "profile"):
		for (szName, szGetter, szSetter, szKind, choices, szApplies) in _PROFILE_SETTINGS:
			row = {"name": "profile:" + szName, "source": "profile", "type": szKind, "value": getattr(profile, szGetter)(), "applies": szApplies}
			# <!-- custom: sas-ci-string-compare-exemption: The kinds are this module's own stable keys. (Claude code Opus 5.5) -->
			if szKind == "choice":
				row["choices"] = list(choices or _profileChoices(szName, profile))
			# <!-- custom: sas-ci-string-compare-exemption: The kinds are this module's own stable keys. (Claude code Opus 5.5) -->
			if szKind == "volume":
				row["range"] = [0, profile.getVolumeStops()]
			if szSetter is None:
				row["readOnly"] = True
			rows.append(row)
	if szSource in (None, "bug"):
		options = BugOptions.getOptions().options
		for szId in sorted(options.keys()):
			rows.append(_bugRow(options[szId]))
	return rows


def _sourceArg(args):
	szSource = args.get("source")
	if szSource is not None and szSource not in _SOURCES:
		raise ValueError("source %r: one of %s" % (szSource, ", ".join(_SOURCES)))
	return szSource


_HELP["options"] = "The settings of Civ4's Options screen and BUG's options, each under a name naming its source: player:PLAYEROPTION_... (the Game tab's checkboxes; value is the flag the game uses, configured the profile's), graphic:GRAPHICOPTION_..., profile:<name> (dropdowns, volumes, sound and clock switches, resolution read-only) and bug:<id> (every BUG option, also those its screen does not draw, with its INI file, section and key, default, and choices with the current index for a list; enabled=false where BUG greys it out; parameterized ones have no single value). applies says when a change takes effect: now, reload (load a save) or restart. Each with its title. 'option' sets one. args: source (player, graphic, profile or bug), match (part of a name or title, any case)."


def cmd_options(args):
	rows = _rows(_sourceArg(args))
	szMatch = args.get("match")
	if szMatch:
		# <!-- custom: As unicode, so a localized title matches: str() of an accented match= such as qualite with its accent raised UnicodeEncodeError in Python 2.4 (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		if not isinstance(szMatch, unicode):
			szMatch = str(szMatch).decode("utf-8")
		szMatch = szMatch.lower()
		rows = [row for row in rows if szMatch in row["name"].lower() or szMatch in (u"%s" % (row.get("title") or u"")).lower()]
	return {"options": rows, "profile": CyUserProfile().getProfileName()}


def _boolean(value):
	# <!-- custom: Only 1 or 0, as 'uioption' takes for a checkbox: Codex found 2 read as true there. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if str(value) not in ("0", "1"):
		raise ValueError("a switch takes 1 or 0, not %r" % (value,))
	return str(value) == "1"


def _wholeNumber(value, iMin, iMax):
	if isinstance(value, bool) or not str(value).lstrip("-").isdigit():
		raise ValueError("value must be a whole number, not %r" % (value,))
	iValue = int(value)
	if not iMin <= iValue <= iMax:
		raise ValueError("value %d is outside %d to %d" % (iValue, iMin, iMax))
	return iValue


def _findType(szName, iCount, getInfo):
	for i in range(iCount):
		if getInfo(i).getType() == szName:
			return i
	raise ValueError("no option %s; 'options' lists them" % szName)


def _setPlayer(szType, value):
	iOption = _findType(szType, PlayerOptionTypes.NUM_PLAYEROPTION_TYPES, gc.getPlayerOptionsInfoByIndex)
	if gc.getGame().getActivePlayer() < 0:
		raise ValueError("no active player yet to send player:%s to" % szType)
	# <!-- custom: As the Game tab's checkbox does (handleGameOptionsClicked): a game message, which sets the player's flag when the game next processes its messages, so the reply reads the flag then ('options' shows it). (Claude code Opus 5.5) -->
	CyMessageControl().sendPlayerOption(iOption, _boolean(value))
	return "player:" + szType


def _setGraphic(szType, value):
	iOption = _findType(szType, GraphicOptionTypes.NUM_GRAPHICOPTION_TYPES, gc.getGraphicOptionsInfoByIndex)
	CyUserProfile().setGraphicOption(iOption, _boolean(value))
	return "graphic:" + szType


def _setProfile(szName, value):
	profile = CyUserProfile()
	found = [row for row in _PROFILE_SETTINGS if row[0] == szName]
	if not found:
		raise ValueError("no option profile:%s; 'options source=profile' lists them" % szName)
	(szName, szGetter, szSetter, szKind, choices, szApplies) = found[0]
	if szSetter is None:
		raise ValueError("profile:%s is read-only here: %s" % (szName, szApplies))
	# <!-- custom: sas-ci-string-compare-exemption: The kinds are this module's own stable keys. (Claude code Opus 5.5) -->
	if szKind == "boolean":
		getattr(profile, szSetter)(_boolean(value))
	# <!-- custom: sas-ci-string-compare-exemption: The kinds are this module's own stable keys. (Claude code Opus 5.5) -->
	elif szKind == "volume":
		getattr(profile, szSetter)(_wholeNumber(value, 0, profile.getVolumeStops()))
	else:
		getattr(profile, szSetter)(_wholeNumber(value, 0, len(choices or _profileChoices(szName, profile)) - 1))
	return "profile:" + szName


def _setBug(szId, value):
	option = BugOptions.findOption(szId)
	if option is None:
		raise ValueError("no option bug:%s; 'options source=bug' lists them" % szId)
	if not (option.isEnabled() and option.getAndOptionValue()):
		raise ValueError("bug:%s is greyed out: BUG turned it off or its master switch is off" % szId)
	if hasattr(option, "isParameterized") and option.isParameterized():
		raise ValueError("bug:%s holds one value per item, which 'option' does not set" % szId)
	# <!-- custom: Through setValue and setIndex, as BugOptionsScreen's callbacks do, so BUG's change handlers and dirty bits still redraw what the option shows (Codex's advice). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if _bugIsList(option):
		option.setIndex(_wholeNumber(value, 0, len(option.getValues()) - 1))
	elif option.isBoolean():
		option.setValue(_boolean(value))
	elif option.isInt():
		option.setValue(_wholeNumber(value, -2147483647, 2147483647))
	elif option.isFloat():
		option.setValue(float(value))
	else:
		# <!-- custom: Strings and colors are typed as text; a color is a key such as COLOR_RED, as in BUG's INI files. (Claude code Opus 5.5) -->
		option.setValue(str(value))
	return "bug:" + szId


_SETTERS = {"player": _setPlayer, "graphic": _setGraphic, "profile": _setProfile, "bug": _setBug}


def _save():
	# <!-- custom: The profile file, as the Options screen's resets and main menu choice write it (CvOptionsScreenCallbackInterface.saveProfile), and BUG's changed INI files, which the main interface writes within 250 ms anyway, so this only matters where it is not drawn.
	# Another client sharing these files keeps its own copy in memory and can write it back over this one. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	profile = CyUserProfile()
	szProfile = profile.getProfileName()
	if szProfile:
		profile.writeToFile(szProfile)
	BugOptions.write()
	# <!-- custom: BUG's write catches an IOError and leaves the file dirty, so the files still dirty are named rather than claiming success (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	files = BugOptions.getOptions().files
	unwritten = [szId for szId in sorted(files.keys()) if files[szId].isDirty()]
	return {"profile": szProfile or None, "bugUnwritten": unwritten}


_HELP["option"] = "Set one setting 'options' lists, through the call its screen's control makes, and read it back: a switch takes 1 or 0, a choice or BUG list the index of its choice, a volume 0 to its range, a BUG number or text its value. A player option is sent as a game message, as the Game tab sends it, and is set once the game processes it, so the reply may show it pending (pending=true until the flag the game uses shows it). Saving: BUG's changed INI files are normally written by the main interface's next update, within 250 ms; a Civ4 setting stays in memory until save=1 writes the profile now (Civ4's Options screen also saves it on close; whether the game writes it at exit was not checked), and another client may share it; save=1 alone (no name) writes it, and bugUnwritten names BUG files a failed write left unwritten. Changes the player's own settings, so it needs the all role. args: name (e.g. graphic:GRAPHICOPTION_NO_MOVIES, bug:MainInterface__Clock), value, save."


def cmd_option(args):
	result = {}
	if args.get("name") is not None:
		if args.get("value") is None:
			raise ValueError("option needs value with name")
		szName = str(args["name"])
		if ":" not in szName or szName.split(":", 1)[0] not in _SETTERS:
			raise ValueError("name %r: source:name, the source one of %s" % (szName, ", ".join(_SOURCES)))
		(szSource, szKey) = szName.split(":", 1)
		before = [row for row in _rows(szSource) if row["name"] == szName]
		_SETTERS[szSource](szKey, args["value"])
		after = [row for row in _rows(szSource) if row["name"] == szName]
		result["before"] = before and before[0] or None
		result["after"] = after and after[0] or None
		# <!-- custom: sas-ci-string-compare-exemption: The source names are this module's own stable keys. (Claude code Opus 5.5) -->
		if szSource == "player":
			# <!-- custom: Nonblocking, as Codex advised: pending says the flag the game uses does not show the value yet; 'options' shows it once the game processed the message. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
			result["pending"] = bool(result["after"]["value"] != _boolean(args["value"]))
			result["note"] = "sent as a game message; the next 'options source=player' shows the flag once the game has processed it"
	elif not args.get("save"):
		raise ValueError("option needs name and value, or save=1")
	if args.get("save"):
		result["saved"] = _save()
	else:
		result["saved"] = None
	return result
