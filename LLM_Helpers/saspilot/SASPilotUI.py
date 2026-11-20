# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: SASPilotUI: screens, tabs and buttons by name, as a click would use them, without coordinates, hotkeys or screenshots (the user's idea, 2026-11-20).
# SASPilotCommands.py loads this file from disk, like itself, and adds its cmd_ functions and help; 'pilot' in this module's namespace is that command module.
# Screens cannot list their widgets, so the recorder below notes each one as a screen creates it; 'uipress' then hands the screen the input a click on it sends. (Claude code Opus 5.5) -->

# <!-- custom: CvScreensInterface holds the screen objects and handleInput; CvScreenEnums names the screen IDs. (Claude code Opus 5.5) -->
from CvPythonExtensions import *
import CvScreenEnums
import CvScreensInterface
# <!-- custom: copy keeps the main interface's start-time record apart from each 'uimain' record. (Claude code Opus 5.5) -->
import copy
# <!-- custom: sys reads the error a recording raised. (Claude code Opus 5.5) -->
import sys

gc = CyGlobalContext()


# <!-- custom: Recorder (Claude code Opus 5.5) -->

# <!-- custom: Methods that only add items to an existing widget, or lines to a drawing, so the first argument is not a new widget. (Claude code Opus 5.5) -->
_NOT_CREATORS = ("addItemToTableGFC", "addTableHeaderGFC", "addLineGFC", "addPullDownString", "addListBoxString", "addDropDownBoxString")
_SET_CREATORS = ("setText", "setLabel", "setTextAt", "setLabelAt", "setButtonGFC", "setImageButton", "setImageButtonAt")


# <!-- custom: Methods that change a recorded widget's state rather than create one. (Claude code Opus 5.5) -->
_STATE_METHODS = ("deleteWidget", "hideScreen", "hide", "show", "enable", "appendMultiListButton", "clearMultiList", "disableMultiListButton")


def _isCell(szMethod):
	# <!-- custom: setTableText, setTableInt and the like: table, column, row, then the cell's text and widget, which a click on the cell sends (the Domestic Advisor's city column is WIDGET_ZOOM_CITY with owner and city ID). (Claude code Opus 5.5) -->
	return szMethod.startswith("setTable") and szMethod not in ("setTableColumnHeader", "setTableRowHeight")


def _isCreator(szMethod):
	if szMethod in _NOT_CREATORS:
		return False
	return szMethod.startswith("add") or szMethod.startswith("attach") or szMethod in _SET_CREATORS


class _Recorded(object):
	# <!-- custom: A descriptor in place of the screen class's method, so screen.setText(...) still reaches the EXE's method; a class rather than a nested function, as AGENTS.md asks Civ4 Python to avoid closures. (Claude code Opus 5.5) -->
	def __init__(self, szMethod, original):
		self.szMethod = szMethod
		self.original = original

	def __get__(self, screen, owner):
		return _BoundRecorded(self, screen)


class _BoundRecorded(object):
	def __init__(self, recorded, screen):
		self.recorded = recorded
		self.screen = screen

	def __call__(self, *args):
		result = self.recorded.original(self.screen, *args)
		# <!-- custom: A recording error must not reach the screen drawing: in the first test, this module's freed globals broke the main interface's setText and raised a Python exception popup in the window.
		# Kept for 'uiscreens' instead. (Claude code Opus 5.5) -->
		try:
			_note(self.screen, self.recorded.szMethod, args)
		except Exception:
			pilot._state["uiRecordError"] = "%s: %s" % (self.recorded.szMethod, sys.exc_info()[1])
		return result


def _registry():
	return pilot._state.setdefault("uiWidgets", {})


def _note(screen, szMethod, args):
	iScreen = screen.getPythonFileID()
	# <!-- custom: The main interface redraws often and is not a screen SASPilotUI opens, so it is recorded only during 'uimain', which redraws it whole once. (Claude code Opus 5.5) -->
	if iScreen == CvScreenEnums.MAIN_INTERFACE and not pilot._state.get("uiRecordMain"):
		return
	widgets = _registry().setdefault(iScreen, {})
	if szMethod == "deleteWidget":
		if args and widgets.has_key(args[0]):
			_dropChildren(widgets, args[0])
			del widgets[args[0]]
		return
	# <!-- custom: A persistent screen, such as the Tech Chooser, keeps its widgets while hidden and only updates them on the next open, so its record stays too. (Claude code Opus 5.5) -->
	if szMethod == "hideScreen":
		if not screen.isPersistent():
			_registry()[iScreen] = {}
		return
	# <!-- custom: Advisors hide a tab's widgets rather than delete them: the Battles table stayed listed after a press on the Composition tab in the first test. (Claude code Opus 5.5) -->
	if szMethod in ("hide", "show"):
		if args and widgets.has_key(args[0]):
			widgets[args[0]]["hidden"] = (szMethod == "hide")
		return
	# <!-- custom: A disabled widget cannot be clicked in the window, so 'uipress' refuses it (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if szMethod == "enable":
		if len(args) > 1 and widgets.has_key(args[0]):
			widgets[args[0]]["disabled"] = not args[1]
		return
	# <!-- custom: The main interface's unit actions and city builds are items of a multi-list (BottomButtonList), appended with their own widget: WIDGET_ACTION with the action, WIDGET_TRAIN with the unit and so on. Kept per list, in order, as 'uipress item=' numbers them. (Claude code Opus 5.5) -->
	if szMethod == "clearMultiList":
		if args and widgets.has_key(args[0]):
			widgets[args[0]]["items"] = []
		return
	# <!-- custom: The city screen greys out builds it cannot start yet with disableMultiListButton(list, row, position in row, texture), and Codex's review found such items still pressable. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if szMethod == "disableMultiListButton":
		if len(args) > 2 and widgets.has_key(args[0]):
			rowItems = [item for item in widgets[args[0]].get("items", []) if item["row"] == args[1]]
			if 0 <= args[2] < len(rowItems):
				rowItems[args[2]]["disabled"] = True
		return
	if szMethod == "appendMultiListButton":
		if len(args) > 6 and widgets.has_key(args[0]):
			widgets[args[0]].setdefault("items", []).append({"button": args[1], "row": args[2], "widget": int(args[3]), "data1": args[4], "data2": args[5], "option": bool(args[6])})
		return
	if _isCell(szMethod):
		if len(args) > 2 and widgets.has_key(args[0]):
			for i in range(3, len(args)):
				if isinstance(args[i], WidgetTypes) and i + 2 < len(args):
					widgets[args[0]].setdefault("cells", {})["%d,%d" % (args[1], args[2])] = (int(args[i]), args[i + 1], args[i + 2])
					break
		return
	iName = 0
	if szMethod.startswith("attach"):
		iName = 1
	if len(args) <= iName:
		return
	entry = {"name": args[iName], "method": szMethod, "order": len(widgets)}
	if iName == 1:
		entry["attachTo"] = args[0]
	# <!-- custom: The *At creators (setTextAt, addDDSGFCAt and the like) name their parent second; kept when it is a recorded widget, so a child of a hidden panel counts as hidden (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	elif szMethod.endswith("At") and len(args) > 1 and isinstance(args[1], str) and widgets.has_key(args[1]):
		entry["attachTo"] = args[1]
	# <!-- custom: The widget type and its two data follow each other in every creator's arguments; a click hands them to handleInput, where advisors read them (the Military Advisor's tabs are WIDGET_GENERAL with the page in data1). (Claude code Opus 5.5) -->
	for i in range(len(args)):
		if isinstance(args[i], WidgetTypes):
			entry["widget"] = int(args[i])
			if i + 2 < len(args):
				entry["data1"] = args[i + 1]
				entry["data2"] = args[i + 2]
			break
	for value in args[iName + 1:]:
		if isinstance(value, unicode):
			entry["text"] = value
			break
	# <!-- custom: Widgets created with an empty name, such as the Foreign Advisor's leader buttons (attachImageButton(panel, "", ...)), overwrote each other in this record, which kept one leader of many (2026-11-20).
	# Each gets a stand-in name from its parent and its place among the parent's unnamed children, and keeps its real name for what a press sends. (Claude code Opus 5.5) -->
	if entry["name"] == "":
		parent = widgets.get(entry.get("attachTo"))
		iUnnamed = 0
		if parent is not None:
			iUnnamed = parent.get("unnamedChildren", 0)
			parent["unnamedChildren"] = iUnnamed + 1
		entry["realName"] = ""
		entry["name"] = "%s#%d" % (entry.get("attachTo", "?"), iUnnamed)
	if widgets.has_key(entry["name"]):
		entry["order"] = widgets[entry["name"]]["order"]
		_dropChildren(widgets, entry["name"])
	widgets[entry["name"]] = entry


def _install():
	# <!-- custom: The originals are kept in the loader's state, which outlives reloads of this file, so a reload wraps them again rather than wrapping the wrapper. (Claude code Opus 5.5) -->
	originals = pilot._state.setdefault("uiOriginals", {})
	# <!-- custom: Only methods not yet kept: the class attribute of one already wrapped is the wrapper. (Claude code Opus 5.5) -->
	for szMethod in dir(CyGInterfaceScreen):
		if not originals.has_key(szMethod) and (_isCreator(szMethod) or _isCell(szMethod) or szMethod in _STATE_METHODS):
			originals[szMethod] = getattr(CyGInterfaceScreen, szMethod)
	# <!-- custom: All or nothing: Codex's review saw that a failure partway through left some of the class's methods wrapped by a module that could then be freed, the cause of the 479 popups.
	# The wrappers are built first, and any failure while setting them gives the class its originals back. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	wrappers = [(szMethod, _Recorded(szMethod, originals[szMethod])) for szMethod in originals.keys()]
	try:
		for (szMethod, wrapper) in wrappers:
			setattr(CyGInterfaceScreen, szMethod, wrapper)
	except Exception:
		_uninstall()
		raise
	pilot._state["uiInstalled"] = True
	return len(originals)


def _dropChildren(widgets, szParent):
	# <!-- custom: A recreated or deleted parent takes its old children with it: Codex's review saw that a parent redrawn with two unnamed buttons where it had three kept the third's stand-in name pressable. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	children = [szName for (szName, entry) in widgets.items() if entry.get("attachTo") == szParent]
	for szName in children:
		if widgets.has_key(szName):
			_dropChildren(widgets, szName)
			del widgets[szName]


def _isShown(widgets, entry):
	# <!-- custom: Hidden itself or through a parent: Codex's review saw that checking only the widget's own flag let a child of a hidden panel pass. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for i in range(32):
		if entry.get("hidden"):
			return False
		parent = widgets.get(entry.get("attachTo"))
		if parent is None:
			return True
		entry = parent
	return True


def _forget(iScreen):
	# <!-- custom: A screen closed by the EXE (Esc, or its Exit, which the EXE handles) or redrawn while the recorder was off leaves a stale record, as Codex's review pointed out; a non-persistent screen's record is dropped when its watch ends and before 'uiopen' draws it anew. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not CyGInterfaceScreen("", iScreen).isPersistent():
		_registry()[iScreen] = {}


def _uninstall():
	originals = pilot._state.get("uiOriginals", {})
	for szMethod in originals.keys():
		setattr(CyGInterfaceScreen, szMethod, originals[szMethod])
	pilot._state["uiInstalled"] = False


# <!-- custom: The recorder is installed only while a screen 'uiopen' opened is up, unless 'uirecord on=1' keeps it: installed for good, every main interface call passed through the wrappers, and a full main interface redraw took about 8 ms longer (24 to 31 ms against 16 to 23, 2026-11-20).
# So 'uiopen' installs it and names the screen it opened, and the bridge's tick, every frame, removes it once that screen is no longer active: one isActive call per frame while installed, nothing otherwise. (Claude code Opus 5.5) -->
def _tick():
	if pilot._state.get("uiAlways"):
		return
	iWatched = pilot._state.get("uiWatched")
	if iWatched is None or not CyGInterfaceScreen("", iWatched).isActive():
		_uninstall()
		if iWatched is not None:
			_forget(iWatched)
		pilot._state["uiWatched"] = None


def _reloaded():
	# <!-- custom: After this file reloads, the class still holds the previous version's wrappers, so they are replaced by this version's, or removed. (Claude code Opus 5.5) -->
	if pilot._state.get("uiInstalled") or pilot._state.get("uiAlways"):
		_install()
	else:
		_uninstall()


def _activeScreens():
	return [iScreen for iScreen in CvScreensInterface.HandleInputMap.keys() if iScreen != CvScreenEnums.MAIN_INTERFACE and _isOpen(iScreen)]


# <!-- custom: Screens (Claude code Opus 5.5) -->

# <!-- custom: The screens a player opens from the window, by a short name after SAS's titles (BtS's single Foreign Advisor is SAS's Foreign Trade and Foreign Diplomacy Advisors, as the user pointed out), with the CvScreensInterface function their button calls (pediaShow for the Sevopedia, which reopens the last page); under the play role, 'uiopen' passes the same check as 'screen'. (Claude code Opus 5.5) -->
_OPENERS = (("tech", "showTechChooser"), ("policy", "showPolicyAdvisorScreen"), ("religion", "showReligionScreen"), ("corporation", "showCorporationScreen"), ("foreigntrade", "showForeignAdvisorScreen"), ("foreigndiplomacy", "showForeignDiplomacyAdvisor"), ("domestic", "showDomesticAdvisor"), ("military", "showMilitaryAdvisor"), ("espionage", "showEspionageAdvisor"), ("info", "showInfoScreen"), ("world", "showWorldAdvisorScreen"), ("victory", "showVictoryScreen"), ("halloffame", "showHallOfFame"), ("pedia", "pediaShow"))


def _screenNames():
	# <!-- custom: Each screen ID's CvScreenEnums name, such as MILITARY_ADVISOR. (Claude code Opus 5.5) -->
	# <!-- custom: Sevopedia's IDs (class SevoScreenEnums) overlap the vanilla pedia's, and SAS uses Sevopedia, so its names win: its main screen, 200, read PEDIA_TECH, the vanilla name, in the first test. (Claude code Opus 5.5) -->
	names = {}
	for enums in (CvScreenEnums, CvScreenEnums.SevoScreenEnums):
		for szName in dir(enums):
			value = getattr(enums, szName)
			if szName.isupper() and isinstance(value, int):
				names[value] = szName
	return names


def _isOpen(iScreen):
	# <!-- custom: Asked of the screen itself: CyInterface().isScreenUp also said yes for the hidden Tech Chooser and Sevopedia tech page in the first test. (Claude code Opus 5.5) -->
	return bool(CyGInterfaceScreen("", iScreen).isActive())


def _screenId(szScreen):
	# <!-- custom: A screen by its CvScreenEnums name or number; None is the open one if only one is, or the main interface when none is, as every main interface command took screen=MAIN_INTERFACE (the user, 2026-11-20). (Claude code Opus 5.5) -->
	if szScreen is None:
		up = [iScreen for iScreen in CvScreensInterface.HandleInputMap.keys() if iScreen != CvScreenEnums.MAIN_INTERFACE and _isOpen(iScreen)]
		if not up:
			return CvScreenEnums.MAIN_INTERFACE
		if len(up) != 1:
			raise ValueError("%d screens are open (%s); name one with screen=" % (len(up), ", ".join([_screenNames().get(i, str(i)) for i in up])))
		return up[0]
	if isinstance(szScreen, int):
		return szScreen
	value = getattr(CvScreenEnums.SevoScreenEnums, str(szScreen).upper(), None)
	if not isinstance(value, int):
		value = getattr(CvScreenEnums, str(szScreen).upper(), None)
	if not isinstance(value, int):
		raise ValueError("unknown screen %s; 'uiscreens' lists them" % szScreen)
	return value


_HELP = {}

_HELP["uiscreens"] = "The screens SASPilotUI knows: each with its CvScreenEnums name and number, whether it is open, how many widgets the recorder holds for it, and for those a player opens from the window, the short name 'uiopen' takes."


def cmd_uiscreens(args):
	names = _screenNames()
	openers = {}
	for (szShort, szShow) in _OPENERS:
		openers[szShow] = szShort
	result = []
	for iScreen in CvScreensInterface.HandleInputMap.keys():
		if iScreen == CvScreenEnums.MAIN_INTERFACE:
			continue
		result.append({"screen": names.get(iScreen, str(iScreen)), "id": iScreen, "open": _isOpen(iScreen), "widgets": len(_registry().get(iScreen, {}))})
	result.sort(lambda a, b: cmp(a["screen"], b["screen"]))
	return {"screens": result, "open": [szShort for (szShort, szShow) in _OPENERS], "recorderMethods": len(pilot._state.get("uiOriginals", {})), "recorder": cmd_uirecord({}), "recorderError": pilot._state.get("uiRecordError")}


_HELP["uirecord"] = "The widget recorder: installed (now recording), always, the screen 'uiopen' opened that keeps it installed, and startRecord, the widgets recorded when the main interface was built at game start (0 if the client started with SASPilot off). By default it records only while that screen is up, so screens a person opens are not recorded; on=1 keeps it installed for good (each main interface redraw then costs more), on=0 goes back to the default and removes it. args: on."


def cmd_uirecord(args):
	if args.get("on") is not None:
		pilot._state["uiAlways"] = bool(args["on"])
		if args["on"]:
			_install()
		else:
			_uninstall()
			pilot._state["uiWatched"] = None
	# <!-- custom: startRecord, the widgets recorded while the main interface was built at game start (0 when the client started with SASPilot off), was read with 'py' while testing that record (2026-11-20). (Claude code Opus 5.5) -->
	return {"installed": bool(pilot._state.get("uiInstalled")), "always": bool(pilot._state.get("uiAlways")), "watched": _screenNames().get(pilot._state.get("uiWatched")), "startRecord": len(pilot._state.get("uiMainStatic", {}))}


def _screenIdsFor(szShow):
	# <!-- custom: The screens a show function may open, from the screen objects HandleInputMap maps; unknown until opened once, then the record of a closed one is dropped before it is drawn again. (Claude code Opus 5.5) -->
	return [iScreen for iScreen in pilot._state.get("uiOpenedBy", {}).get(szShow, [])]


# <!-- custom: Persistent screens and the dirty bit that makes them rebuild on open. (Claude code Opus 5.5) -->
_REBUILD_BITS = {"tech": "Tech_Screen_DIRTY_BIT"}


_HELP["uiopen"] = "Open a screen as its button in the window does, by short name ('uiscreens' lists them: tech, military, domestic, foreigntrade, foreigndiplomacy, ...). Returns the screen and its widgets' count once drawn. args: name."


def cmd_uiopen(args):
	return _openScreen(args["name"], True)


def _openScreen(szName, bRecord):
	# <!-- custom: bRecord False opens without installing the recorder, for 'uibench''s runs without it. (Claude code Opus 5.5) -->
	args = {"name": szName}
	szShow = None
	for (szShort, szCandidate) in _OPENERS:
		if szShort == args["name"]:
			szShow = szCandidate
	if szShow is None:
		raise ValueError("unknown screen %s; one of %s" % (args["name"], ", ".join([szShort for (szShort, szShow) in _OPENERS])))
	pilot._checkRole("screen", {"name": szShow})
	# <!-- custom: The Tech Chooser built its tree once, before the recorder was installed, and on later opens only updated it (advc.068 checks this dirty bit), so 'uiwidgets' found 11 Great Person icons and no tech (2026-11-20).
	# Setting the bit rebuilds the tree, and the recorder sees it. (Claude code Opus 5.5) -->
	if _REBUILD_BITS.has_key(args["name"]):
		CyInterface().setDirty(getattr(InterfaceDirtyBits, _REBUILD_BITS[args["name"]]), True)
	before = _activeScreens()
	for iScreen in _screenIdsFor(szShow):
		if iScreen not in before:
			_forget(iScreen)
	if bRecord:
		_install()
	pilot.cmd_screen({"name": szShow})
	after = _activeScreens()
	opened = [iScreen for iScreen in after if iScreen not in before]
	for iScreen in opened:
		known = pilot._state.setdefault("uiOpenedBy", {}).setdefault(szShow, [])
		if iScreen not in known:
			known.append(iScreen)
	# <!-- custom: An already open screen did not redraw from scratch, so its record is kept; a newly opened one was just drawn whole. (Claude code Opus 5.5) -->
	if opened:
		pilot._state["uiWatched"] = opened[0]
	elif len(after) == 1:
		pilot._state["uiWatched"] = after[0]
	else:
		pilot._state["uiWatched"] = None
	return {"opened": args["name"], "called": szShow, "screen": _screenNames().get(pilot._state["uiWatched"])}


_HELP["uiwidgets"] = "The widgets an open screen created, in creation order, as the recorder saw them: name, method, text, widget (WidgetTypes number and name), data1, data2, attachTo. Only widgets drawn while the recorder was installed (see uirecord) are known; hidden ones, themselves or through a parent, are left out unless hidden=1 (all role). args: screen (CvScreenEnums name, default the open one), match (part of the name or text, optional), hidden (optional)."


def cmd_uiwidgets(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		_mainRecord(False)
	szMatch = args.get("match")
	widgets = _registry().get(iScreen, {}).values()
	widgets.sort(lambda a, b: cmp(a["order"], b["order"]))
	result = []
	bHidden = bool(args.get("hidden"))
	if bHidden and pilot._state.get("role") not in (None, "all"):
		raise ValueError("hidden=1 lists widgets the window does not show; the all role allows it")
	byName = _registry().get(iScreen, {})
	for entry in widgets:
		if not bHidden and not _isShown(byName, entry):
			continue
		if szMatch is not None and entry["name"].find(szMatch) < 0 and entry.get("text", u"").find(szMatch) < 0:
			continue
		item = {}
		for (szKey, value) in entry.items():
			if szKey == "cells":
				item["cellWidgets"] = len(value)
			elif szKey == "items":
				item["items"] = len(value)
			elif szKey not in ("order", "unnamedChildren"):
				item[szKey] = value
		if entry.has_key("widget"):
			item["widgetType"] = pilot._enumName(WidgetTypes, entry["widget"])
		result.append(item)
	return {"screen": _screenNames().get(iScreen, str(iScreen)), "widgets": result}


_HELP["uipress"] = "Click a widget of an open screen by name, as a mouse click does: the screen's handleInput gets what the EXE sends it (the function name and trailing number, left-button flags, the recorded widget type and data), then a typed widget's own action runs through the DLL, as it does after a click whatever the screen returned (pedia links, slider buttons, techs); an Exit (WIDGET_CLOSE_SCREEN) hides the screen, as the EXE does. right=1 clicks with the right button, whose DLL action is the alternate one. With row and column, a table cell is clicked (row as data and mouse Y, column as mouse X) with that cell's own widget; with item, a multi-list item ('uiitems' numbers them), such as a unit action or a city build. widgettype, data1, data2 and option replace the recorded values, or stand in for a widget the recorder did not see; they need the all role, as they can send what no click can. args: widget, item, row, column, right, screen (default the open one), widgettype (WidgetTypes name), data1, data2, option."


# <!-- custom: Screens the play role cannot click or read, whoever opened them: WorldBuilder and debug screens change or show what a player may not (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_NOT_PLAY_SCREENS = ("WORLDBUILDER", "WORLD_BUILDER", "DEBUG")


def _requirePlayable(iScreen, bClick):
	# <!-- custom: Under a role other than all, only what is on display: a closed screen's record can be stale, and a click on it cannot happen (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	szName = _screenNames().get(iScreen, str(iScreen))
	if pilot._state.get("role") in (None, "all"):
		if bClick and not _isOpen(iScreen):
			raise ValueError("%s is not open; 'uiopen' opens it" % szName)
		return
	if not _isOpen(iScreen):
		raise ValueError("%s is not open; 'uiopen' opens it" % szName)
	for szPart in _NOT_PLAY_SCREENS:
		if szName.find(szPart) >= 0:
			raise ValueError("%s is not a play screen; the all role allows it" % szName)


def _target(iScreen, args, bPress):
	# <!-- custom: The widget a command acts on, as a click on it would send it: a plain widget, a multi-list item (item=) or a table cell (row=, column=), with its widget type, data, notify code, flags and mouse values. Shared by 'uipress' and 'uihover', so the two cannot disagree on what a name points at. (Claude code Opus 5.5) -->
	szWidget = str(args["widget"])
	szScreen = _screenNames().get(iScreen, str(iScreen))
	# <!-- custom: Recorded anew first when it may be stale, so it matches the current selection and state: it replaced a refusal when the selection had changed since 'uimain' (Codex's review), which left the agent running 'uimain' before every press. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		_mainRecord(bPress)
	entry = _registry().get(iScreen, {}).get(szWidget)
	if entry is not None and not _isShown(_registry().get(iScreen, {}), entry):
		raise ValueError("%s is hidden on %s" % (szWidget, szScreen))
	# <!-- custom: Disabled widgets refuse a press only: a greyed-out build's tooltip says what it still needs, which a player reads there (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if bPress and entry is not None and entry.get("disabled"):
		raise ValueError("%s is disabled on %s" % (szWidget, szScreen))
	if entry is None:
		if args.get("widgettype") is None:
			raise ValueError("no widget %s on %s; 'uiwidgets' lists them, or give widgettype= and its data" % (szWidget, szScreen))
		entry = {}
	target = {"name": szWidget, "sent": str(entry.get("realName", szWidget))}
	iWidget = int(entry.get("widget", int(WidgetTypes.WIDGET_GENERAL)))
	bOption = False
	# <!-- custom: What a real click sent, logged by wrapping handleInput on 2026-11-20: a left click on a Tech Chooser box came as NOTIFY_CLICKED with flags 16384 (MOUSE_LBUTTONUP); a Sevopedia list row as NOTIFY_LISTBOX_ITEM_SELECTED with flags 0, the row as getData() and getMouseY() and the column as getMouseX().
	# The first version sent flags 0 for clicks, so the Foreign Advisor's leader click, which tests MOUSE_LBUTTONUP, would have missed (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	eNotify = NotifyCode.NOTIFY_CLICKED
	iFlags = int(MouseFlags.MOUSE_LBUTTONUP)
	if args.get("right"):
		iFlags = int(MouseFlags.MOUSE_RBUTTONUP)
	iData = 0
	iMouseX = 0
	iMouseY = 0
	# <!-- custom: A real click on a multi-list item (the Worker's Sleep and Go To buttons, 2026-11-20) came as NOTIFY_LISTBOX_ITEM_SELECTED with flags 0, the list's name, ID 0, the item's widget and data, and its position within its row as data: 0 for Sleep, 2 for Go To. (Claude code Opus 5.5) -->
	if args.get("item") is not None:
		items = entry.get("items", [])
		iItem = int(args["item"])
		if iItem < 0 or iItem >= len(items):
			raise ValueError("%s has %d items; 'uiitems' lists them" % (szWidget, len(items)))
		item = items[iItem]
		if bPress and item.get("disabled"):
			raise ValueError("item %d of %s is disabled in the window" % (iItem, szWidget))
		# <!-- custom: The list may have changed since 'uiitems' numbered it, so the same item= would press another action or build (Codex's review); a press checks the item is still the one listed. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		listed = pilot._state.get("uiItemsListed", {}).get((iScreen, szWidget))
		if bPress and listed is not None and (iItem >= len(listed) or listed[iItem] != _itemKey(item)):
			raise ValueError("item %d of %s changed since 'uiitems' listed it; list it again" % (iItem, szWidget))
		target["about"] = _itemAbout(item)
		eNotify = NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
		iFlags = 0
		iData = len([other for other in items[:iItem] if other["row"] == item["row"]])
		iWidget = item["widget"]
		bOption = item["option"]
		entry = {"data1": item["data1"], "data2": item["data2"]}
	elif args.get("row") is not None:
		eNotify = NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
		iFlags = 0
		iData = int(args["row"])
		iMouseX = int(args.get("column", 0))
		iMouseY = iData
		cell = entry.get("cells", {}).get("%d,%d" % (iMouseX, iData))
		if cell is None:
			raise ValueError("%s has no recorded cell at column %d, row %d" % (szWidget, iMouseX, iData))
		(iWidget, iCellData1, iCellData2) = cell
		entry = {"data1": iCellData1, "data2": iCellData2}
	if args.get("widgettype") is not None:
		iWidget = int(pilot._enum(WidgetTypes, args["widgettype"]))
	if args.get("option") is not None:
		bOption = bool(args["option"])
	target.update({"widget": iWidget, "data1": int(args.get("data1", entry.get("data1", 0))), "data2": int(args.get("data2", entry.get("data2", 0))), "option": bOption, "notify": eNotify, "flags": iFlags, "data": iData, "mouseX": iMouseX, "mouseY": iMouseY})
	return target


def cmd_uipress(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, True)
	target = _target(iScreen, args, True)
	szWidget = target["name"]
	szScreen = _screenNames().get(iScreen, str(iScreen))
	iWidget = target["widget"]
	iData1 = target["data1"]
	iData2 = target["data2"]
	bOption = target["option"]
	bRight = bool(args.get("right"))
	eNotify = target["notify"]
	iFlags = target["flags"]
	iData = target["data"]
	iMouseX = target["mouseX"]
	iMouseY = target["mouseY"]
	result = {"pressed": szWidget, "widget": pilot._enumName(WidgetTypes, iWidget), "data1": iData1, "data2": iData2}
	if target.get("about") is not None:
		result["about"] = target["about"]
	# <!-- custom: The EXE closes a screen on its own for this widget, without a Python or DLL handler: executeAction has no case for it. (Claude code Opus 5.5) -->
	if iWidget == int(WidgetTypes.WIDGET_CLOSE_SCREEN):
		CyGInterfaceScreen("", iScreen).hideScreen()
		result["closed"] = szScreen
		return result
	# <!-- custom: The EXE splits a widget name's trailing digits off as its ID, so screens compare the function name without them.
	# A table cell keeps the table's name, which the Military and World Advisors' row handlers compare, although the real Sevopedia row click sent an empty name. (Claude code Opus 5.5) -->
	szSent = target["sent"]
	szFunction = szSent.rstrip("0123456789")
	iID = 0
	if len(szFunction) < len(szSent):
		iID = int(szSent[len(szFunction):])
	argsList = [eNotify, iData, iFlags, iID, iScreen, szFunction, False, False, False, iMouseX, iMouseY, iWidget, iData1, iData2, bOption]
	result["function"] = szFunction
	result["id"] = iID
	result["screenHandled"] = bool(CvScreensInterface.handleInput(argsList))
	# <!-- custom: The first version ran the DLL action only when the screen returned 0, guessing the EXE did the same.
	# Codex's review found both failures this risked: the Domestic Advisor returns 1 on a slider button without changing the rate, so the rate would not change, and the Tech Chooser's route link returns None after opening the page itself, so it would open twice.
	# A real click then showed what the EXE does: on the Domestic Advisor's Gold +10 button its Python returned 1 while gold was still 0%, and gold was 10% after the click; on a Tech Chooser box Python saw the old research, and the new one was set afterwards.
	# So the EXE runs the widget's DLL action after the screen's Python, whatever it returned, and 'uipress' does the same, to do what the window does, the route link's double opening included. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: dllHandled is executeAction's own return, false for nearly every widget ("Game will run with this = false"): pressing Pottery reported false while research became Pottery (2026-11-20), so whether the action was called is dllAction. (Claude code Opus 5.5) -->
	result["dllAction"] = False
	if iWidget not in (int(WidgetTypes.WIDGET_GENERAL), int(WidgetTypes.WIDGET_PYTHON)):
		result["dllHandled"] = bool(pilot._pilotGame("executeSASPilotWidget").executeSASPilotWidget(iWidget, iData1, iData2, bOption, bRight))
		result["dllAction"] = True
	return result


_HELP["uiread"] = "Read a table of an open screen as rows of cell text, or a recorded widget's text, as plain text: font tags and the advisors' invisible sort keys removed, game-font icons named such as [YIELD_FOOD]; raw=1 gives the text as the screen set it. args: widget, screen (default the open one), raw."


# <!-- custom: The Battles table's icon cells read as ten invisible characters each, such as u"\u200b\u200b...", which the user noticed as wasted space (2026-11-20): SASUtils.getAdvisorIconSortKey writes a base-5 sort key in U+200B to U+200F so icon-only cells sort, invisible in the window.
# Removed for the agent, with the font tags; pilot._plainText names the game-font icons. (Claude code Opus 5.5) -->
_SORT_KEY_CHARS = (u"\u200b", u"\u200c", u"\u200d", u"\u200e", u"\u200f")


def _plainCell(text, bRaw):
	if bRaw:
		return text
	text = unicode(text)
	for ch in _SORT_KEY_CHARS:
		text = text.replace(ch, u"")
	# <!-- custom: Hover texts escape markup characters, so the Technology Advisor's read "&lt;F6>" (2026-11-20); unescaped after the tags are gone, &amp; last. (Claude code Opus 5.5) -->
	return pilot._plainText(text).replace(u"&lt;", u"<").replace(u"&gt;", u">").replace(u"&amp;", u"&")


def cmd_uiread(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	szWidget = str(args["widget"])
	entry = _registry().get(iScreen, {}).get(szWidget)
	if entry is not None and pilot._state.get("role") not in (None, "all") and not _isShown(_registry().get(iScreen, {}), entry):
		raise ValueError("%s is hidden on %s" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	if entry is not None and entry["method"].find("Table") >= 0:
		screen = CyGInterfaceScreen("", iScreen)
		iColumns = screen.getTableNumColumns(szWidget)
		rows = []
		for iRow in range(screen.getTableNumRows(szWidget)):
			rows.append([_plainCell(screen.getTableText(szWidget, iColumn, iRow), args.get("raw")) for iColumn in range(iColumns)])
		return {"widget": szWidget, "columns": iColumns, "rows": rows}
	if entry is None:
		raise ValueError("no widget %s on %s; 'uiwidgets' lists them" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	return {"widget": szWidget, "text": _plainCell(entry.get("text") or u"", args.get("raw"))}


_HELP["uibench"] = "Time the recorder's cost: a full draw of a screen (opened as 'uiopen' does, then hidden; the Tech Chooser rebuilt) and a main interface redraw with every dirty bit set, each with the recorder off and on, alternating, repeat times. Milliseconds per draw. Opening the screen closes any other advisor, as in the window. Leaves the recorder as it was. args: name (default tech), repeat (default 3)."


def cmd_uibench(args):
	# <!-- custom: Was two 'py' snippets on 2026-11-20 while measuring the recorder (see 'What the recorder costs' in the SASPilot Guide); the user asked that reused measuring code become a command. (Claude code Opus 5.5) -->
	szName = args.get("name", "tech")
	iRepeat = int(args.get("repeat", 3))
	bits = [getattr(InterfaceDirtyBits, szBit) for szBit in dir(InterfaceDirtyBits) if szBit.endswith("_DIRTY_BIT")]
	result = {"screen": szName, "off": {"screenMs": [], "mainRedrawMs": []}, "on": {"screenMs": [], "mainRedrawMs": []}}
	bAlways = pilot._state.get("uiAlways")
	bInstalled = pilot._state.get("uiInstalled")
	iWatched = pilot._state.get("uiWatched")
	pilot._state["uiAlways"] = True
	# <!-- custom: Restored in finally, so a draw that fails does not leave the recorder installed for good; all three values, as restoring only uiAlways dropped the watch on a screen 'uiopen' had opened (Codex's reviews). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	try:
		_benchRuns(szName, iRepeat, bits, result)
	finally:
		pilot._state["uiAlways"] = bAlways
		pilot._state["uiInstalled"] = bInstalled
		pilot._state["uiWatched"] = iWatched
		_reloaded()
	return result


def _benchRuns(szName, iRepeat, bits, result):
	import time
	# <!-- custom: Both draws grew slower over the repeats, so a fixed off-then-on order made "on" look slower than it was (2026-11-20); the order alternates. (Claude code Opus 5.5) -->
	for i in range(iRepeat):
		order = ("off", "on")
		if i % 2:
			order = ("on", "off")
		for szKey in order:
			if szKey == "on":
				_install()
			else:
				_uninstall()
			fStart = time.clock()
			_openScreen(szName, szKey == "on")
			result[szKey]["screenMs"].append(round((time.clock() - fStart) * 1000.0, 1))
			iScreen = _screenId(None)
			CyGInterfaceScreen("", iScreen).hideScreen()
			fStart = time.clock()
			for j in range(10):
				for eBit in bits:
					CyInterface().setDirty(eBit, True)
				CvScreensInterface.mainInterface.redraw()
			result[szKey]["mainRedrawMs"].append(round((time.clock() - fStart) * 100.0, 2))


_HELP["uiprobe"] = "Log what real clicks in the window send the screens: with on=1, each call of CvScreensInterface.handleInput is kept with its notify code, function name and ID, flags, mouse X and Y, widget type, data1, data2 and what the screen returned, up to the last 200; on=0 stops. Without on, the log so far; clear=1 empties it. For mapping a new kind of widget: switch it on, click it in the window, read it. args: on, clear."


def _probeHandleInput(argsList):
	# <!-- custom: A plain function, as the EXE calls only that: the first 'uiprobe' installed an instance of a class with __call__, which 'uipress' reached, but real clicks and hovers in the window never did, while the 'py' probe before it, a function, logged them all (2026-11-20).
	# The original is read from the bridge's state rather than kept in a closure, as AGENTS.md asks. (Claude code Opus 5.5) -->
	returned = pilot._state["uiProbeOriginal"](argsList)
	try:
		log = pilot._state.setdefault("uiProbeLog", [])
		log.append({"turn": gc.getGame().getGameTurn(), "notify": pilot._enumName(NotifyCode, argsList[0]), "data": argsList[1], "flags": argsList[2], "id": argsList[3], "screen": _screenNames().get(argsList[4], str(argsList[4])), "function": argsList[5], "mouseX": argsList[9], "mouseY": argsList[10], "widget": pilot._enumName(WidgetTypes, argsList[11]), "data1": argsList[12], "data2": argsList[13], "option": argsList[14], "returned": returned})
		del log[:-200]
	except Exception:
		pilot._state["uiRecordError"] = "uiprobe: %s" % sys.exc_info()[1]
	return returned


def _probeOn():
	return getattr(CvScreensInterface.handleInput, "__name__", "") == "_probeHandleInput"


def cmd_uiprobe(args):
	# <!-- custom: Was a 'py' snippet on 2026-11-20 that settled how the EXE dispatches a click (screen first, then the DLL action whatever the screen returned); the user asked that it become a command for the next widget to map. (Claude code Opus 5.5) -->
	if args.get("clear"):
		pilot._state["uiProbeLog"] = []
	if args.get("on") is not None:
		if args["on"] and not _probeOn():
			pilot._state["uiProbeOriginal"] = CvScreensInterface.handleInput
			CvScreensInterface.handleInput = _probeHandleInput
		elif not args["on"] and _probeOn():
			CvScreensInterface.handleInput = pilot._state["uiProbeOriginal"]
	bOn = _probeOn()
	return {"on": bOn, "log": pilot._state.get("uiProbeLog", [])}


_HELP["uimain"] = "Record the main interface, which the recorder otherwise skips for its cost: its record is cleared, every dirty bit set and the main interface redrawn once with recording on, so its widgets (advisor buttons, research, sliders, unit actions, and the city screen while one is open) can then be listed, read and pressed with screen=MAIN_INTERFACE. Run it again after the view changes, such as a city screen opened or a unit selected. The buttons made only when the game starts (advisors, minimap, globe, scoreboard toggles, event log) come from SASPilot's record of that build, so a client must have started with SASPilot on. Returns the number of widgets recorded."


def cmd_uimain(args):
	pilot._state["uiMainKey"] = None
	_mainRecord(False)
	return {"screen": "MAIN_INTERFACE", "widgets": len(_registry().get(CvScreenEnums.MAIN_INTERFACE, {})), "cityScreen": bool(CyInterface().isCityScreenUp())}


def _mainRecord(bPress):
	# <!-- custom: Codex's review: refreshing the main interface for every command cost three full redraws for a list, a hover and a press, each rebuilding the production chooser, and the main interface could be refreshed and pressed while the diplomacy screen or a popup owned input.
	# So input elsewhere refuses, and the record is redrawn only when it may be stale: another selection, turn or city screen state, or a press since, which can change the interface (a toggle hid the scoreboard button). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if pilot._diploState()["open"] or pilot._pendingContact() is not None:
		raise ValueError("the diplomacy screen owns input; 'diplo' reads it")
	if hasattr(gc.getGame(), "getSASPilotPopups"):
		for popup in pilot._popups():
			if popup["state"] == "DISPLAYED":
				raise ValueError("a %s popup on display owns input; 'popups' lists it" % popup["type"])
	key = (_selectionKey(), gc.getGame().getGameTurn())
	# <!-- custom: A press always records anew: Codex's next review saw that a manual toggle or a change within the selected group leaves this key unchanged while the controls change, so a press could act on an old record; the item check then compares the listing with the fresh record. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if bPress or pilot._state.get("uiMainKey") != key or pilot._state.get("uiMainPressed"):
		_refreshMain()
		pilot._state["uiMainKey"] = key
		pilot._state["uiMainPressed"] = False
	if bPress:
		pilot._state["uiMainPressed"] = True


def _refreshMain():
	# <!-- custom: The main interface holds most of the buttons a player uses, but recording it on every redraw cost about 8 ms per full redraw (2026-11-20), so it is recorded on demand: by 'uimain', and by every ui command on the main interface first, as each press can change it (a toggle hid the scoreboard button) and the agent repeated 'uimain' before each press (the user, 2026-11-20). (Claude code Opus 5.5) -->
	bInstalled = pilot._state.get("uiInstalled")
	iMain = CvScreenEnums.MAIN_INTERFACE
	# <!-- custom: Starts from the record of the main interface's build at game start, as those buttons are not drawn again; a 'full=1' that reran the build blanked the minimap (2026-11-20). (Claude code Opus 5.5) -->
	_registry()[iMain] = copy.deepcopy(pilot._state.get("uiMainStatic", {}))
	_install()
	pilot._state["uiRecordMain"] = True
	try:
		# <!-- custom: The first version set every dirty bit itself, and on Babylon's city screen the scoreboard was then drawn over the city screen's right panel (2026-11-20), which a city screen opened normally did not show, so it was not a regression in the main interface.
		# A hand-picked list of bits was the next fix; the user asked for what the game itself runs instead, so this is the game's own full refresh, makeInterfaceDirty, which the DLL calls when the active player changes (CvPlayer.cpp), followed by the redraw the EXE calls (forceScreenRedraw). (Claude code Opus 5.5) -->
		CyInterface().makeInterfaceDirty()
		CvScreensInterface.forceScreenRedraw([CvScreenEnums.MAIN_INTERFACE])
	finally:
		pilot._state["uiRecordMain"] = False
		if not bInstalled:
			_uninstall()
	pilot._state["uiMainSelection"] = _selectionKey()


def _aroundMainBuild(bBefore):
	# <!-- custom: The main interface's build at game start, recorded as its static part: SASPilot.py calls this around CvMainInterface.interfaceScreen. (Claude code Opus 5.5) -->
	iMain = CvScreenEnums.MAIN_INTERFACE
	if bBefore:
		pilot._state["uiMainBuildInstalled"] = pilot._state.get("uiInstalled")
		_registry()[iMain] = {}
		_install()
		pilot._state["uiRecordMain"] = True
		return
	pilot._state["uiRecordMain"] = False
	pilot._state["uiMainStatic"] = copy.deepcopy(_registry().get(iMain, {}))
	if not pilot._state.get("uiMainBuildInstalled") and not pilot._state.get("uiAlways"):
		_uninstall()


def _selectionKey():
	# <!-- custom: What the main interface's actions and builds belong to: Codex's review saw that a Worker's recorded action could be pressed after another unit was selected, acting on that one. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	ui = CyInterface()
	unit = ui.getHeadSelectedUnit()
	city = ui.getHeadSelectedCity()
	key = [bool(ui.isCityScreenUp())]
	if unit is not None and not unit.isNone():
		key.extend([unit.getOwner(), unit.getID()])
	if city is not None and not city.isNone():
		key.extend([city.getOwner(), city.getID()])
	return tuple(key)


_HELP["uiitems"] = "The items of a multi-list, such as the main interface's BottomButtonList with the selected unit's actions or the open city's builds, numbered as 'uipress item=' takes them: widget type and data, with the action, unit, building, project or process it stands for. The main interface is recorded anew first. args: widget, screen (default the open one, or the main interface)."


def cmd_uiitems(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		_mainRecord(False)
	szWidget = str(args["widget"])
	entry = _registry().get(iScreen, {}).get(szWidget)
	if entry is None:
		raise ValueError("no widget %s on %s; 'uiwidgets' lists them" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	if pilot._state.get("role") not in (None, "all") and not _isShown(_registry().get(iScreen, {}), entry):
		raise ValueError("%s is hidden on %s" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	result = []
	pilot._state.setdefault("uiItemsListed", {})[(iScreen, szWidget)] = [_itemKey(item) for item in entry.get("items", [])]
	for i in range(len(entry.get("items", []))):
		item = entry["items"][i]
		row = {"item": i, "row": item["row"], "widget": pilot._enumName(WidgetTypes, item["widget"]), "data1": item["data1"], "data2": item["data2"]}
		if item.get("disabled"):
			row["disabled"] = True
		szAbout = _itemAbout(item)
		if szAbout is not None:
			row["about"] = szAbout
		result.append(row)
	return {"widget": szWidget, "items": result}


# <!-- custom: What an item's data1 names, by its widget type, read from the XML info the screen took it from. (Claude code Opus 5.5) -->
_ITEM_INFOS = (("WIDGET_ACTION", "getActionInfo", "getNumActionInfos"), ("WIDGET_CREATE", "getProjectInfo", "getNumProjectInfos"), ("WIDGET_MAINTAIN", "getProcessInfo", "getNumProcessInfos"))


def _actionAbout(info):
	# <!-- custom: CvActionInfo has no getType in Python (the first version called a getHotKeyDescription that does not exist); an action is one of a mission, command, automation, interface mode or control, so it is named by that, with a Build's type for MISSION_BUILD. (Claude code Opus 5.5) -->
	if info.getMissionType() >= 0:
		szName = pilot._enumName(MissionTypes, info.getMissionType())
		if info.getMissionType() == int(MissionTypes.MISSION_BUILD) and info.getMissionData() >= 0:
			return "%s %s" % (szName, gc.getBuildInfo(info.getMissionData()).getType())
		return szName
	if info.getCommandType() >= 0:
		szName = pilot._enumName(CommandTypes, info.getCommandType())
		# <!-- custom: The three Worker automations all read COMMAND_AUTOMATE; their command data is the AutomateTypes. (Claude code Opus 5.5) -->
		if info.getCommandType() == int(CommandTypes.COMMAND_AUTOMATE) and info.getCommandData() >= 0:
			return "%s %s" % (szName, pilot._enumName(AutomateTypes, info.getCommandData()))
		return szName
	if info.getAutomateType() >= 0:
		return pilot._enumName(AutomateTypes, info.getAutomateType())
	if info.getInterfaceModeType() >= 0:
		return pilot._enumName(InterfaceModeTypes, info.getInterfaceModeType())
	if info.getControlType() >= 0:
		return pilot._enumName(ControlTypes, info.getControlType())
	return None


def _itemKey(item):
	return (item["row"], item["widget"], item["data1"], item["data2"])


def _itemAbout(item):
	# <!-- custom: A build button's data1 is a unit or building class, which doTrain and doConstruct turn into the active civ's own unit or building: labelled first as a unit index, item 3 read UNIT_SCOUT, and pressing it queued a Spy, class 10 (2026-11-20). (Claude code Opus 5.5) -->
	civ = gc.getCivilizationInfo(gc.getGame().getActiveCivilizationType())
	if item["widget"] == int(WidgetTypes.WIDGET_TRAIN) and 0 <= item["data1"] < gc.getNumUnitClassInfos():
		return pilot._typeOrNone(gc.getUnitInfo, civ.getCivilizationUnits(item["data1"]))
	if item["widget"] == int(WidgetTypes.WIDGET_CONSTRUCT) and 0 <= item["data1"] < gc.getNumBuildingClassInfos():
		return pilot._typeOrNone(gc.getBuildingInfo, civ.getCivilizationBuildings(item["data1"]))
	for (szWidget, szGetter, szCount) in _ITEM_INFOS:
		if item["widget"] == int(getattr(WidgetTypes, szWidget)) and 0 <= item["data1"] < getattr(gc, szCount)():
			info = getattr(gc, szGetter)(item["data1"])
			if szWidget == "WIDGET_ACTION":
				return _actionAbout(info)
			return info.getType()
	return None


_HELP["uiselect"] = "Select as a click on the map does: unit= selects that unit and its group, so its actions fill the main interface; city= opens that city's screen. Then 'uimain' records what the main interface shows. Own units and cities only, unless player= names another under the all role. args: unit, city, player."


def cmd_uiselect(args):
	# <!-- custom: A unit's actions and a city's builds appear in the main interface only for the selection, which in the window is a map click; this makes that step by name. (Claude code Opus 5.5) -->
	# <!-- custom: Our own player only outside the all role: the shared player= check allows a teammate, whom a player cannot select (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if pilot._state.get("role") not in (None, "all") and args.get("player") is not None and int(args["player"]) != gc.getGame().getActivePlayer():
		raise ValueError("only our own units and cities can be selected; the all role allows player=")
	if args.get("unit") is not None:
		unit = pilot._unit(args)
		CyInterface().selectUnit(unit, True, False, False)
		return {"selected": unit.getID(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY()}
	if args.get("city") is not None:
		city = pilot._city(args)
		CyInterface().selectCity(city, True)
		return {"selected": city.getName(), "cityScreen": bool(CyInterface().isCityScreenUp())}
	raise ValueError("give unit= or city=")


_HELP["uistate"] = "Where the window is now, as one reply: active player, civilization, leader, turn and whether it is our turn; the scoreboard (visible, expanded, background style, lock, autocenter, scroll), the map toggles (grid, yields, bare map), the globe view and the commerce sliders; the interface mode (INTERFACEMODE_GO_TO waits for a map click, for example); the selected unit, its group's units and plot; the selected city and whether its screen is open; the open screens; and the recorder's state. Read it before pressing anything."


def cmd_uistate(args):
	# <!-- custom: Asked again and again through 'py' while building SASPilotUI, such as gc.getGame().getActiveCivilizationType() for the build labels; the user asked for one command giving the active context (2026-11-20). (Claude code Opus 5.5) -->
	game = gc.getGame()
	iPlayer = game.getActivePlayer()
	result = {"turn": game.getGameTurn(), "player": iPlayer}
	if iPlayer >= 0:
		player = gc.getPlayer(iPlayer)
		result["team"] = player.getTeam()
		result["civ"] = pilot._typeOrNone(gc.getCivilizationInfo, player.getCivilizationType())
		result["leader"] = pilot._typeOrNone(gc.getLeaderHeadInfo, player.getLeaderType())
		result["turnActive"] = bool(player.isTurnActive())
	ui = CyInterface()
	result["interfaceMode"] = pilot._enumName(InterfaceModeTypes, ui.getInterfaceMode())
	result["selectedUnit"] = None
	unit = ui.getHeadSelectedUnit()
	# <!-- custom: Another player's selected unit (a debug selection) is named, but not its group, outside the all role (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if unit is not None and not unit.isNone() and unit.getOwner() != iPlayer and pilot._state.get("role") not in (None, "all"):
		result["selectedUnit"] = {"owner": unit.getOwner(), "type": gc.getUnitInfo(unit.getUnitType()).getType()}
		unit = None
	if unit is not None and not unit.isNone():
		group = []
		for i in range(unit.getGroup().getNumUnits()):
			member = unit.getGroup().getUnitAt(i)
			group.append({"id": member.getID(), "type": gc.getUnitInfo(member.getUnitType()).getType()})
		result["selectedUnit"] = {"id": unit.getID(), "owner": unit.getOwner(), "type": gc.getUnitInfo(unit.getUnitType()).getType(), "x": unit.getX(), "y": unit.getY(), "group": group}
	city = ui.getHeadSelectedCity()
	result["selectedCity"] = None
	if city is not None and not city.isNone():
		result["selectedCity"] = {"id": city.getID(), "owner": city.getOwner(), "name": city.getName()}
	result["cityScreen"] = bool(ui.isCityScreenUp())
	# <!-- custom: The main interface's toggles and sliders, read with 'py' after each press while testing them (2026-11-20).
	# The globe view's state lags a press by a few frames while the camera zooms. (Claude code Opus 5.5) -->
	# <!-- custom: The scoreboard's toggles and the minimap's map toggles, each read with 'py' after a press while testing them (2026-11-20): expanded is advc.085's hover expansion; bgStyle, locked (the lock button's bScoreAlwaysExpand), autocenter and scroll are SAS's, kept by the main interface. (Claude code Opus 5.5) -->
	main = CvScreensInterface.mainInterface
	result["scoreboard"] = {"visible": bool(ui.isScoresVisible()), "bgStyle": getattr(main, "iScoreBgStyleLevel", None), "bgStyles": len(getattr(main, "aScoreBgStyleLevels", [])), "locked": getattr(main, "bScoreAlwaysExpand", None), "autocenter": getattr(main, "bScoreScrollAutocenterActivePlayer", None), "scroll": getattr(main, "iScoreScrollOffset", None)}
	if iPlayer >= 0:
		result["scoreboard"]["expanded"] = bool(gc.getPlayer(iPlayer).isScoreboardExpanded())
	profile = CyUserProfile()
	result["map"] = {"grid": bool(profile.getGrid()), "yields": bool(profile.getYields()), "bareMap": bool(profile.getMap())}
	result["globeView"] = bool(CyEngine().isGlobeviewUp())
	if iPlayer >= 0:
		result["commercePercent"] = dict([(pilot._enumName(CommerceTypes, i), gc.getPlayer(iPlayer).getCommercePercent(CommerceTypes(i))) for i in range(CommerceTypes.NUM_COMMERCE_TYPES)])
	result["openScreens"] = [_screenNames().get(iScreen, str(iScreen)) for iScreen in _activeScreens()]
	result["recorder"] = cmd_uirecord({})
	return result


_HELP["uihover"] = "The hover text the window shows for a widget, a multi-list item (item=) or a table cell (row=, column=), as plain text; read through the DLL for typed widgets, so it is the tooltip a player sees. A WIDGET_GENERAL widget has none of its own. args: widget, item, row, column, screen (default the open one), raw."


def cmd_uihover(args):
	# <!-- custom: Tooltips hold much of what a player reads (a build's cost and effects, a leader's attitude, a slider's step), and Python cannot ask the EXE for them; CyGame.getSASPilotWidgetHelp calls the DLL's parseHelp, which the EXE calls on a real hover. (Claude code Opus 5.5) -->
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	target = _target(iScreen, args, False)
	szHelp = pilot._pilotGame("getSASPilotWidgetHelp").getSASPilotWidgetHelp(target["widget"], target["data1"], target["data2"], target["option"])
	# <!-- custom: Widgets BUG's WidgetUtil created, such as SAS's scoreboard style and lock buttons, have their tooltip in Python (WidgetUtil.setWidgetHelpFunction), so the DLL returned nothing for them (2026-11-20); asked there when the DLL has no text. (Claude code Opus 5.5) -->
	if not szHelp:
		import WidgetUtil
		szHelp = WidgetUtil.getWidgetHelp((WidgetTypes(target["widget"]), target["data1"], target["data2"], target["option"])) or u""
	return {"widget": target["name"], "type": pilot._enumName(WidgetTypes, target["widget"]), "data1": target["data1"], "data2": target["data2"], "help": _plainCell(szHelp, args.get("raw"))}
