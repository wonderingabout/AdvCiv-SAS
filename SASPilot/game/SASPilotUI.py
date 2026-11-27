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
# <!-- custom: re takes the icon names out of a list box entry's text. (Claude code Opus 5.5) -->
import re
# <!-- custom: copy keeps the main interface's start-time record apart from each 'uimain' record. (Claude code Opus 5.5) -->
import copy
# <!-- custom: sys reads the error a recording raised. (Claude code Opus 5.5) -->
import sys
# <!-- custom: SASUtils draws every advisor's footer tabs, which 'uitabs' records (_TabRecorder). (Claude code Opus 5.5) -->
import SASUtils
# <!-- custom: SASVisualUtils holds the scroll arrows' art, which 'uiscroll' finds them by. (Claude code Opus 5.5) -->
import SASVisualUtils
# <!-- custom: SASTextScale owns the session font preview and its cached tags. (GPT-6.2-Sol) -->
import SASTextScale

gc = CyGlobalContext()


# <!-- custom: Recorder (Claude code Opus 5.5) -->

# <!-- custom: Methods that only add items to an existing widget, or lines to a drawing, so the first argument is not a new widget. (Claude code Opus 5.5) -->
_NOT_CREATORS = ("addItemToTableGFC", "addTableHeaderGFC", "addLineGFC", "addPullDownString", "addListBoxString", "addDropDownBoxString")
_SET_CREATORS = ("setText", "setLabel", "setTextAt", "setLabelAt", "setButtonGFC", "setImageButton", "setImageButtonAt")


# <!-- custom: Methods that change a recorded widget's state rather than create one. (Claude code Opus 5.5) -->
_STATE_METHODS = ("deleteWidget", "hideScreen", "hide", "show", "enable", "appendMultiListButton", "clearMultiList", "disableMultiListButton", "addPullDownString", "clearListBoxGFC", "appendListBoxString", "appendListBoxStringNoUpdate")


# <!-- custom: The drop-down creators, whose arguments are kept so a choice can rebuild the box with that entry selected (see _chooseOption). (Claude code Opus 5.5) -->
_DROPDOWN_CREATORS = ("addDropDownBoxGFC", "attachDropDownBoxGFC")


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


class _TabRecorder(object):
	# <!-- custom: In place of SASUtils.drawAdvisorFooterTabRows, which every footer tab row goes through (drawAdvisorFooterTabs calls it from SASUtils' own namespace), so the tabs of each advisor are known by widget name, label and page, and which one is active.
	# Always installed: it runs once per advisor draw.
	# The drawing goes first, and a recording error never reaches it, as with _BoundRecorded. (Claude code Opus 5.5) -->
	def __init__(self, original):
		self.original = original

	def __call__(self, *args):
		result = self.original(*args)
		try:
			_noteTabs(args[0], args[1], args[2])
		except Exception:
			pilot._state["uiRecordError"] = "drawAdvisorFooterTabRows: %s" % sys.exc_info()[1]
		return result


def _noteTabs(screen, aTabRows, iActivePageID):
	iScreen = screen.getPythonFileID()
	_beginPressScreenRecord(iScreen)
	tabs = [{"widget": row[0], "label": row[1], "page": row[3]} for row in aTabRows]
	pilot._state.setdefault("uiTabs", {})[iScreen] = {"tabs": tabs, "active": iActivePageID}


def _installTabs():
	# <!-- custom: The original is kept in the loader's state, so a reload of this file wraps it again rather than wrapping the previous wrapper. (Claude code Opus 5.5) -->
	original = pilot._state.get("uiTabOriginal")
	if original is None:
		original = SASUtils.drawAdvisorFooterTabRows
		pilot._state["uiTabOriginal"] = original
	SASUtils.drawAdvisorFooterTabRows = _TabRecorder(original)


def _registry():
	return pilot._state.setdefault("uiWidgets", {})


def _clearScreenRecord(iScreen):
	_registry().pop(iScreen, None)
	pilot._state.get("uiTabs", {}).pop(iScreen, None)
	listed = pilot._state.get("uiItemsListed", {})
	for key in listed.keys():
		if key[0] == iScreen:
			del listed[key]


# <!-- custom: A widget can open a screen from its Python or DLL action.
# Start a fresh record on its first draw, since a persistent screen's last recorded tab can differ from what this press opens.
# Already open screens keep their records for incremental updates. (GPT-6.2-Sol) -->
def _beginPressScreenRecord(iScreen):
	seen = pilot._state.get("uiPressScreens")
	if seen is not None and iScreen not in seen:
		seen.add(iScreen)
		_clearScreenRecord(iScreen)


def _note(screen, szMethod, args):
	iScreen = screen.getPythonFileID()
	# <!-- custom: The main interface redraws often and is not a screen SASPilotUI opens, so it is recorded only during 'uimain', which redraws it whole once. (Claude code Opus 5.5) -->
	if iScreen == CvScreenEnums.MAIN_INTERFACE and not pilot._state.get("uiRecordMain"):
		return
	_beginPressScreenRecord(iScreen)
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
	# <!-- custom: A drop-down's entries, in order, with the one shown selected: the advisors' grouping and page boxes, the Hall of Fame filters, the debug player list. (Claude code Opus 5.5) -->
	if szMethod == "addPullDownString":
		if len(args) > 4 and widgets.has_key(args[0]):
			widgets[args[0]].setdefault("options", []).append({"text": args[1], "type": args[2], "data": args[3], "selected": bool(args[4])})
		return
	# <!-- custom: A list box's entries, such as the Sevopedia's categories (WIDGET_PEDIA_MAIN with the category as data1), kept as items one per row, as 'uipress item=' sends the row a click on it sends (2026-11-20). (Claude code Opus 5.5) -->
	if szMethod == "clearListBoxGFC":
		if args and widgets.has_key(args[0]):
			widgets[args[0]]["items"] = []
		return
	if szMethod in ("appendListBoxString", "appendListBoxStringNoUpdate"):
		if len(args) > 4 and widgets.has_key(args[0]):
			items = widgets[args[0]].setdefault("items", [])
			items.append({"button": "", "row": len(items), "widget": int(args[2]), "data1": args[3], "data2": args[4], "option": False, "text": args[1], "listBox": True})
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
	# <!-- custom: addCheckBoxGFCAt names its parent first too, as every call does (the Policy Advisor's religions and corporations, the Foreign Advisor's leaders), although the BUG API listing omits the parent.
	# Taken as the name, the parent was recorded once per button and each re-record dropped its children, so the Religions tab kept none of its buttons and labels but the last (2026-11-20). (Claude code Opus 5.5) -->
	if szMethod.startswith("attach") or szMethod == "addCheckBoxGFCAt":
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
	# <!-- custom: An image button shows only its art, kept so 'uiscroll' finds the scroll arrows by it: the Foreign Advisor's grids name theirs with a running counter and give them no text (2026-11-20).
	# setImageButtonAt names its parent before the art. (Claude code Opus 5.5) -->
	if szMethod in ("setImageButton", "setImageButtonAt"):
		iArt = 1
		if szMethod == "setImageButtonAt":
			iArt = 2
		if len(args) > iArt and isinstance(args[iArt], str):
			entry["art"] = args[iArt]
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
	# <!-- custom: Kept as the original tuple, Boost enums and all, and not on the main interface, whose record is deep-copied (_refreshMain), which Codex's review doubted would copy those enums. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if szMethod in _DROPDOWN_CREATORS and iScreen != CvScreenEnums.MAIN_INTERFACE:
		entry["createArgs"] = tuple(args)
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
		_clearScreenRecord(iScreen)


def _uninstall():
	originals = pilot._state.get("uiOriginals", {})
	for szMethod in originals.keys():
		setattr(CyGInterfaceScreen, szMethod, originals[szMethod])
	pilot._state["uiInstalled"] = False


# <!-- custom: The recorder follows screens that 'uiopen' or 'uipress' opens.
# The bridge tick removes it when the watched screen closes; a permanent install added about 8 ms to a full HUD redraw in the 2026-11-20 test. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def _tick():
	if not pilot._state.get("uiInstalled") or pilot._state.get("uiAlways") or pilot._state.get("uiPressScreens") is not None:
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
	_installTabs()


def _activeScreens():
	return [iScreen for iScreen in CvScreensInterface.HandleInputMap.keys() if iScreen != CvScreenEnums.MAIN_INTERFACE and _isOpen(iScreen)]


# <!-- custom: Screens (Claude code Opus 5.5) -->

# <!-- custom: The screens a player opens from the window, by a short name after SAS's titles (BtS's single Foreign Advisor is SAS's Foreign Trade and Foreign Diplomacy Advisors, as the user pointed out), with the CvScreensInterface function their button calls (pediaShow for the Sevopedia, which reopens the last page); under the play role, 'uiopen' passes the same check as 'screen'. (Claude code Opus 5.5) -->
_OPENERS = (("tech", "showTechChooser"), ("policy", "showPolicyAdvisorScreen"), ("religion", "showReligionScreen"), ("corporation", "showCorporationScreen"), ("foreigntrade", "showForeignAdvisorScreen"), ("foreigndiplomacy", "showForeignDiplomacyAdvisor"), ("domestic", "showDomesticAdvisor"), ("military", "showMilitaryAdvisor"), ("espionage", "showEspionageAdvisor"), ("info", "showInfoScreen"), ("world", "showWorldAdvisorScreen"), ("victory", "showVictoryScreen"), ("halloffame", "showHallOfFame"), ("pedia", "pediaShow"))


# <!-- custom: The control each short name's key sends (CvGame::doControl in CvGameInterface.cpp).
# Not the Policy Advisor's: CONTROL_CIVICS_SCREEN first kills every waiting change-civic popup (advc.004x), so opening it could remove a popup before a check saw it (Codex's review); its show function draws it fully. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_OPENER_CONTROLS = {"tech": "CONTROL_TECH_CHOOSER", "foreigntrade": "CONTROL_FOREIGN_SCREEN", "foreigndiplomacy": "CONTROL_FOREIGN_DIPLOMACY_SCREEN", "domestic": "CONTROL_DOMESTIC_SCREEN", "military": "CONTROL_MILITARY_SCREEN", "espionage": "CONTROL_ESPIONAGE_SCREEN", "info": "CONTROL_INFO", "world": "CONTROL_WORLD_ADVISOR_SCREEN", "victory": "CONTROL_VICTORY_SCREEN", "halloffame": "CONTROL_HALL_OF_FAME", "pedia": "CONTROL_CIVILOPEDIA"}


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


_HELP["uirecord"] = "The widget recorder: installed (now recording), always, the screen opened by 'uiopen' or 'uipress' that keeps it installed, and startRecord, the widgets recorded when the main interface was built at game start (0 if the client started with SASPilot off). By default it records only while that screen is up, so screens a person opens are not recorded; on=1 keeps it installed for good (each main interface redraw then costs more), on=0 goes back to the default and removes it. args: on."


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


# <!-- custom: The Tech Chooser keeps its cached tree across opens.
# When SASPilot opens it, rebuild so the recorder sees the tech boxes and their links, as well as the icons the cached path updates. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def _prepareTechOpen():
	CyInterface().setDirty(InterfaceDirtyBits.Tech_Screen_DIRTY_BIT, True)


_HELP["uiopen"] = "Open a screen as its button in the window does, by short name ('uiscreens' lists them: tech, military, domestic, foreigntrade, foreigndiplomacy, ...). Returns the screen and its recorded widget count. Without a name lists the screen shortcuts. args: name."


def cmd_uiopen(args):
	# <!-- custom: Listing shortcuts is a successful read; invalid names still fail in _openScreen. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if args.get("name") is None:
		return {"open": [szShort for szShort, _ in _OPENERS]}
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
	if szName == "tech":
		_prepareTechOpen()
		if bRecord:
			_clearScreenRecord(CvScreenEnums.TECH_CHOOSER)
	before = _activeScreens()
	for iScreen in _screenIdsFor(szShow):
		if iScreen not in before:
			_forget(iScreen)
	if bRecord:
		_install()
	# <!-- custom: Through the screen's control, as its key does, where it has one: opened by calling showMilitaryAdvisor from the bridge, the Military Advisor's Map tab showed an empty minimap, black or blue, until the tab was pressed again, while F5 and 'control control=CONTROL_MILITARY_SCREEN' drew it at once (2026-11-20).
	# Religion and Corporation have no control since SAS moved them into the Policy Advisor, so they keep the call, as does the Policy Advisor (see _OPENER_CONTROLS). (Claude code Opus 5.5) -->
	szControl = _OPENER_CONTROLS.get(args["name"])
	if szControl is not None:
		gc.getGame().doControl(getattr(ControlTypes, szControl))
	else:
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
	iWatched = pilot._state["uiWatched"]
	result = {"opened": args["name"], "called": szShow, "control": szControl, "screen": _screenNames().get(iWatched)}
	if bRecord:
		result["widgets"] = len(_registry().get(iWatched, {}))
	return result


# <!-- custom: Each event screen by short name, its XML info table and optional CvWonderMovieScreen kind, and the screen ID it draws. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
_SPLASHES = (("era", "ERA", "Era", None, "ERA_MOVIE_SCREEN"), ("dawnofman", None, None, None, "DAWN_OF_MAN"), ("wonder", "BUILDING", "Building", 0, "WONDER_MOVIE_SCREEN"), ("religion", "RELIGION", "Religion", 1, "WONDER_MOVIE_SCREEN"), ("project", "PROJECT", "Project", 2, "WONDER_MOVIE_SCREEN"), ("techsplash", "TECH", "Tech", None, "TECH_SPLASH"))
# <!-- custom: Greatest Civilizations stays on the normal turn path: it draws synchronized random numbers and writes its ranking to the Timeline and SASGameRecord. (Claude code Opus 5.5) -->


_HELP["uisplash"] = "Preview an event screen on the map without waiting for its event: era item=ERA_RENAISSANCE, dawnofman, wonder item=BUILDING_PYRAMID, religion item=RELIGION_JUDAISM, project item=PROJECT_APOLLO_PROGRAM, techsplash item=TECH_WRITING. The preview bypasses the SAS_UI_*_ON switches and respects the screen's own player options. The recorder follows it for uiwidgets, uihover and uipress; use the returned close widget name with uipress widget=. Without a name lists the previews. args: name, item."


def cmd_uisplash(args):
	szName = args.get("name")
	if szName is None:
		return {"splash": [entry[0] for entry in _SPLASHES]}
	entry = None
	for candidate in _SPLASHES:
		if candidate[0] == szName:
			entry = candidate
			break
	if entry is None:
		raise ValueError("unknown splash %s; one of %s" % (szName, ", ".join([entry[0] for entry in _SPLASHES])))
	(szShort, szPrefix, szInfo, iKind, szScreen) = entry
	iScreen = getattr(CvScreenEnums, szScreen)
	if gc.getGame().getActivePlayer() < 0:
		raise ValueError("a splash preview needs an active player")
	_requireHudInput()
	# <!-- custom: Two previews can share a screen ID, or stack over different event screens.
	# Check each open splash before starting another. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	for szOpen in set(entry[4] for entry in _SPLASHES):
		if _isOpen(getattr(CvScreenEnums, szOpen)):
			raise ValueError("%s is open; close it before previewing another splash" % szOpen)
	iItem = -1
	if szPrefix is not None:
		szItem = args.get("item")
		if szItem is None or not str(szItem).startswith(szPrefix + "_"):
			raise ValueError("%s takes item=%s_..." % (szName, szPrefix))
		iNum = getattr(gc, "getNum%sInfos" % szInfo)()
		iItem = pilot._typedIndex(str(szItem), szPrefix, iNum, getattr(gc, "get%sInfo" % szInfo))
	_clearScreenRecord(iScreen)
	bWasRecording = pilot._state.get("uiInstalled")
	if not bWasRecording:
		_install()
	try:
		if szName == "era":
			CvScreensInterface.eraMovie.interfaceScreen(iItem)
		elif szName == "dawnofman":
			CvScreensInterface.dawnOfMan.interfaceScreen(True)
		elif szName == "techsplash":
			if CvScreensInterface.techSplashScreen is None:
				CvScreensInterface.createTechSplash()
			CvScreensInterface.techSplashScreen.interfaceScreen(iItem)
		else:
			CvScreensInterface.wonderMovie.interfaceScreen(iItem, -1, iKind)
	finally:
		if not bWasRecording and not _registry().get(iScreen):
			_uninstall()
	# <!-- custom: Judged by what was drawn, not by the screen being up: the era splash reads as open only from the next frame, so the first version reported it as not shown (2026-11-21).
	# The close button is returned, as 'uipress widgettype=WIDGET_CLOSE_SCREEN' without a widget name does not reach these screens. (Claude code Opus 5.5) -->
	widgets = _registry().get(iScreen, {})
	if widgets:
		pilot._state["uiWatched"] = iScreen
	result = {"shown": None, "screen": szScreen, "widgets": len(widgets), "close": [szWidget for szWidget in widgets.keys() if widgets[szWidget].get("widget") == int(WidgetTypes.WIDGET_CLOSE_SCREEN)]}
	if not widgets:
		# <!-- custom: The screen returned before drawing: No Movies for the movie screens, or the tech splash's own option. (Claude code Opus 5.5) -->
		result["note"] = "nothing drawn; check player options and whether the item has a movie"
	else:
		result["shown"] = szName
	if widgets and not result["close"]:
		# <!-- custom: The wonder screen adds its OK button when its movie starts, from its update after a delay (CvWonderMovieScreen.playMovie). (Claude code Opus 5.5) -->
		result["note"] = "its close button comes with the movie, a moment later; 'uiwidgets' then lists it"
	return result


_HELP["uiwidgets"] ="The widgets an open screen created, in creation order, as the recorder saw them: name, method, text, widget (WidgetTypes number and name), data1, data2, attachTo. Only widgets drawn while the recorder was installed (see uirecord) are known; hidden ones, themselves or through a parent, are left out unless hidden=1 (all role). args: screen (CvScreenEnums name, default the open one), match (part of the name or text, optional), hidden (optional)."


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


_HELP["uitabs"] = "The footer tabs of an open advisor (Domestic, Military, Foreign, Info, Policy, Victory, World), as the screen last drew them: each tab's widget name for 'uipress widget=', its label as plain text and whether it is the active one. Recorded from SAS's shared footer tab drawing whatever the recorder's state; a screen without footer tabs, such as the Tech Chooser, has none. args: screen (default the open one)."


def cmd_uitabs(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	record = pilot._state.get("uiTabs", {}).get(iScreen)
	tabs = []
	if record is not None:
		for tab in record["tabs"]:
			tabs.append({"widget": tab["widget"], "label": _plainCell(tab["label"], False), "active": tab["page"] == record["active"]})
	return {"screen": _screenNames().get(iScreen, str(iScreen)), "tabs": tabs}


_HELP["uiscroll"] = "Scroll a list of an open screen with its arrow buttons, as a click on them does: dir= up, down, pageup, pagedown, top or bottom, such as the Foreign Advisor's Bonuses, Techs and Cities grids. An arrow at its end is hidden, as in the window, so it is refused; without dir, the arrows shown now. Afterwards, the arrows still shown, so 'up' missing means the list is at its top. args: dir, screen (default the open one)."

# <!-- custom: Each direction and the InterfaceArt its arrow shows (IconGrid_BUG's six arrows). (Claude code Opus 5.5) -->
_SCROLL_ARROWS = (("top", "SCROLL_TOP_ARROW"), ("pageup", "SCROLL_PAGE_UP_ARROW"), ("up", "SCROLL_UP_ARROW"), ("down", "SCROLL_DOWN_ARROW"), ("pagedown", "SCROLL_PAGE_DOWN_ARROW"), ("bottom", "SCROLL_BOTTOM_ARROW"))


def _scrollArrows(iScreen):
	# <!-- custom: The shown arrows by direction, matched by the art path SASVisuals gives IconGrid_BUG. (Claude code Opus 5.5) -->
	paths = {}
	for (szDir, szArt) in _SCROLL_ARROWS:
		paths[getattr(SASVisualUtils.InterfaceArt, szArt)] = szDir
	widgets = _registry().get(iScreen, {})
	result = {}
	for entry in widgets.values():
		szDir = paths.get(entry.get("art"))
		if szDir is not None and _isShown(widgets, entry):
			result.setdefault(szDir, []).append(entry["name"])
	return result


def _arrowOrder(arrows):
	return [szDir for (szDir, szArt) in _SCROLL_ARROWS if arrows.has_key(szDir)]


def cmd_uiscroll(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, True)
	arrows = _scrollArrows(iScreen)
	szDir = args.get("dir")
	result = {"screen": _screenNames().get(iScreen, str(iScreen))}
	if szDir is None:
		result["arrows"] = _arrowOrder(arrows)
		return result
	if szDir not in [szName for (szName, szArt) in _SCROLL_ARROWS]:
		raise ValueError("dir is one of %s" % ", ".join([szName for (szName, szArt) in _SCROLL_ARROWS]))
	if not arrows.has_key(szDir):
		raise ValueError("no %s arrow shown on %s: the list is at that end, or the screen has no scroll arrows; shown: %s" % (szDir, result["screen"], ", ".join(_arrowOrder(arrows)) or "none"))
	if len(arrows[szDir]) != 1:
		raise ValueError("%d %s arrows are shown (%s); press one with 'uipress widget='" % (len(arrows[szDir]), szDir, ", ".join(arrows[szDir])))
	cmd_uipress({"widget": arrows[szDir][0], "screen": iScreen})
	result["pressed"] = szDir
	result["arrows"] = _arrowOrder(_scrollArrows(iScreen))
	return result


_HELP["uipress"] ="Click a widget of an open screen by name, as a mouse click does: the screen's handleInput gets what the EXE sends it (the function name and trailing number, left-button flags, the recorded widget type and data), then a typed widget's own action runs through the DLL, as it does after a click whatever the screen returned (pedia links, slider buttons, techs); an Exit (WIDGET_CLOSE_SCREEN) hides the screen, as the EXE does. right=1 clicks with the right button, whose DLL action is the alternate one. With row and column, a table cell is clicked (row as data and mouse Y, column as mouse X) with that cell's own widget; with item, a multi-list item ('uiitems' numbers them), such as a unit action or a city build. widgettype, data1, data2 and option replace the recorded values, or stand in for a widget the recorder did not see; they need the all role, as they can send what no click can. text= names the widget by what it shows instead of widget=, such as text=Augustus for his scoreboard row: an exact match, else the one widget containing it, without case; several are listed. about= names a multi-list item by what it does, such as about=INTERFACEMODE_GO_TO or about=UNIT_WARRIOR, rather than by number: the list changes as the unit moves, and a stale number once pressed Delete. choice= picks a drop-down's entry, by its number from 'uiitems' or by its text: the box is rebuilt with that entry selected, as Python cannot select it otherwise, then the selection is sent as a click sends it. args: widget, text, item, about, choice, row, column, right, screen (default the open one), widgettype (WidgetTypes name), data1, data2, option."


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
	szScreen = _screenNames().get(iScreen, str(iScreen))
	# <!-- custom: Recorded anew first when it may be stale, so it matches the current selection and state: it replaced a refusal when the selection had changed since 'uimain' (Codex's review), which left the agent running 'uimain' before every press. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		_mainRecord(bPress)
	szWidget = _widgetArg(iScreen, args)
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
	if args.get("item") is not None or args.get("about") is not None:
		items = entry.get("items", [])
		if args.get("item") is None:
			iItem = _itemByAbout(szWidget, items, args["about"])
		else:
			iItem = int(args["item"])
		if iItem < 0 or iItem >= len(items):
			raise ValueError("%s has %d items; 'uiitems' lists them" % (szWidget, len(items)))
		item = items[iItem]
		if bPress and item.get("disabled"):
			raise ValueError("item %d of %s is disabled in the window" % (iItem, szWidget))
		# <!-- custom: The list may have changed since 'uiitems' numbered it, so the same item= would press another action or build (Codex's review); a press checks the item is still the one listed. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		listed = pilot._state.get("uiItemsListed", {}).get((iScreen, szWidget))
		if bPress and args.get("item") is not None and listed is not None and (iItem >= len(listed) or listed[iItem] != _itemKey(item)):
			raise ValueError("item %d of %s changed since 'uiitems' listed it; list it again" % (iItem, szWidget))
		target["about"] = _itemAbout(item)
		eNotify = NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
		iFlags = 0
		iData = len([other for other in items[:iItem] if other["row"] == item["row"]])
		# <!-- custom: A list box sends its row, a multi-list the position within the row. (Claude code Opus 5.5) -->
		if item.get("listBox"):
			iData = item["row"]
		iWidget = item["widget"]
		bOption = item["option"]
		entry = {"data1": item["data1"], "data2": item["data2"]}
	# <!-- custom: A drop-down choice: the advisors' handlers read the chosen index as the event's data (CvBUGMilitaryAdvisor's grouping boxes, CvCustomizableDomesticAdvisor's pages), others the box's own selection through getSelectedPullDownID, which cmd_uipress sets by rebuilding the box first. (Claude code Opus 5.5) -->
	elif args.get("choice") is not None:
		options = entry.get("options")
		if not options:
			raise ValueError("%s is not a drop-down with recorded entries; 'uiitems' lists a drop-down's entries" % szWidget)
		iChoice = _optionIndex(szWidget, options, args["choice"])
		target["choice"] = iChoice
		target["about"] = _plainCell(options[iChoice]["text"], False)
		eNotify = NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED
		iFlags = 0
		iData = iChoice
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
	# <!-- custom: Wrap the dispatch itself so a press from the HUD or another advisor captures the destination as it opens.
	# A press that stays on the same screen keeps its previous watch. (GPT-6.2-Sol) -->
	before = set(_activeScreens())
	if not pilot._state.get("uiInstalled"):
		_install()
	pilot._state["uiPressScreens"] = before | set((CvScreenEnums.MAIN_INTERFACE,))
	try:
		_dispatchPress(iScreen, szWidget, argsList, target, bRight, result)
	finally:
		seen = pilot._state.pop("uiPressScreens")
		opened = [iOpened for iOpened in _activeScreens() if iOpened not in before]
		for iOpened in opened:
			if iOpened not in seen:
				# <!-- custom: A persistent screen may reopen without emitting any widget calls, so a screen this press opened but drew nothing for loses its stale record. (GPT-6.2-Sol + Claude code Opus 5.5) -->
				_clearScreenRecord(iOpened)
		if opened:
			pilot._state["uiWatched"] = opened[0]
			result["openedScreens"] = [_screenNames().get(iOpened, str(iOpened)) for iOpened in opened]
		_tick()
	return result


def _dispatchPress(iScreen, szWidget, argsList, target, bRight, result):
	if target.get("choice") is not None:
		result["choice"] = target["choice"]
		result["rebuilt"] = _chooseOption(iScreen, szWidget, target["choice"])
	result["function"] = argsList[5]
	result["id"] = argsList[3]
	result["screenHandled"] = bool(CvScreensInterface.handleInput(argsList))
	# <!-- custom: The first version ran the DLL action only when the screen returned 0, guessing the EXE did the same.
	# Codex's review found both failures this risked: the Domestic Advisor returns 1 on a slider button without changing the rate, so the rate would not change, and the Tech Chooser's route link returns None after opening the page itself, so it would open twice.
	# A real click then showed what the EXE does: on the Domestic Advisor's Gold +10 button its Python returned 1 while gold was still 0%, and gold was 10% after the click; on a Tech Chooser box Python saw the old research, and the new one was set afterwards.
	# So the EXE runs the widget's DLL action after the screen's Python, whatever it returned, and 'uipress' does the same, to do what the window does, the route link's double opening included. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	# <!-- custom: dllHandled is executeAction's own return, false for nearly every widget ("Game will run with this = false"): pressing Pottery reported false while research became Pottery (2026-11-20), so whether the action was called is dllAction. (Claude code Opus 5.5) -->
	iWidget = target["widget"]
	result["dllAction"] = iWidget not in (int(WidgetTypes.WIDGET_GENERAL), int(WidgetTypes.WIDGET_PYTHON))
	if result["dllAction"]:
		# <!-- custom: The HUD button and any other widget carrying this control use the same rebuild as 'uiopen tech'.
		# Only a left click on the control can open it through executeAction. (GPT-6.2-Sol) -->
		if not bRight and iWidget == int(WidgetTypes.WIDGET_ACTION) and target["data1"] == gc.getControlInfo(ControlTypes.CONTROL_TECH_CHOOSER).getActionInfoIndex() and not _isOpen(CvScreenEnums.TECH_CHOOSER):
			_prepareTechOpen()
		result["dllHandled"] = bool(pilot._pilotGame("executeSASPilotWidget").executeSASPilotWidget(iWidget, target["data1"], target["data2"], target["option"], bRight))


_HELP["uiread"] = "Read a table of an open screen as rows of cell text, or a recorded widget's text, as plain text: font tags and the advisors' invisible sort keys removed, game-font icons named such as [YIELD_FOOD]; raw=1 gives the text as the screen set it. text= names the widget by what it shows instead of widget=, such as text=Augustus for his scoreboard row: an exact match, else the one widget containing it, without case; several are listed. args: widget, text, screen (default the open one), raw, cells (1 to include recorded table cell actions)."


# <!-- custom: The Battles table's icon cells read as ten invisible characters each, such as u"\u200b\u200b...", which the user noticed as wasted space (2026-11-20): SASUtils.getAdvisorIconSortKey writes a base-5 sort key in U+200B to U+200F so icon-only cells sort, invisible in the window.
# Removed for the agent, with the font tags; pilot._plainText names the game-font icons. (Claude code Opus 5.5) -->
_SORT_KEY_CHARS = (u"\u200b", u"\u200c", u"\u200d", u"\u200e", u"\u200f")


# <!-- custom: A widget named by what it shows, as a player finds it: opening diplomacy with Augustus took his scoreboard row's name, ScoreText28, read first through 'uiwidgets match=' (2026-11-20).
# The shown text, tags and sort keys removed, is compared without case: an exact match wins, else the one widget containing it; several are listed rather than one guessed. (Claude code Opus 5.5) -->
def _widgetArg(iScreen, args):
	if args.get("widget") is None and args.get("text") is not None:
		return _widgetByText(iScreen, args["text"])
	# <!-- custom: Neither given raised a bare KeyError 'widget', as for 'uipress widgettype=WIDGET_CLOSE_SCREEN' while no screen was open (2026-11-21). (Claude code Opus 5.5) -->
	if args.get("widget") is None:
		raise ValueError("name the widget with widget= or text= on %s; 'uiwidgets' lists them" % _screenNames().get(iScreen, str(iScreen)))
	return str(args["widget"])


def _widgetByText(iScreen, text):
	widgets = _registry().get(iScreen, {})
	szWanted = unicode(text).strip().lower()
	# <!-- custom: An empty or blank text= is in every text, so with one shown widget it would press that one (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not szWanted:
		raise ValueError("text= is empty; give the text the widget shows")
	exact = []
	partial = []
	for name, entry in widgets.items():
		if not entry.get("text") or not _isShown(widgets, entry):
			continue
		szShown = _plainCell(entry["text"], False).strip().lower()
		if szShown == szWanted:
			exact.append(name)
		elif szShown.find(szWanted) >= 0:
			partial.append(name)
	found = exact
	if not found:
		found = partial
	if len(found) == 1:
		return found[0]
	szScreen = _screenNames().get(iScreen, str(iScreen))
	if not found:
		raise ValueError("no shown widget on %s reads %r; 'uiwidgets' lists them" % (szScreen, text))
	found.sort()
	raise ValueError("%d widgets on %s read %r, give widget= instead: %s" % (len(found), szScreen, text, ", ".join(["%s (%s)" % (name, _plainCell(widgets[name]["text"], False).strip()) for name in found[:12]])))


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
	szWidget = _widgetArg(iScreen, args)
	entry = _registry().get(iScreen, {}).get(szWidget)
	if entry is not None and pilot._state.get("role") not in (None, "all") and not _isShown(_registry().get(iScreen, {}), entry):
		raise ValueError("%s is hidden on %s" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	if entry is not None and entry["method"].find("Table") >= 0:
		screen = CyGInterfaceScreen("", iScreen)
		iColumns = screen.getTableNumColumns(szWidget)
		rows = []
		for iRow in range(screen.getTableNumRows(szWidget)):
			rows.append([_plainCell(screen.getTableText(szWidget, iColumn, iRow), args.get("raw")) for iColumn in range(iColumns)])
		result = {"widget": szWidget, "columns": iColumns, "rows": rows}
		if args.get("cells"):
			result["cells"] = _tableCellActions(entry, len(rows), iColumns)
		return result
	if entry is None:
		raise ValueError("no widget %s on %s; 'uiwidgets' lists them" % (szWidget, _screenNames().get(iScreen, str(iScreen))))
	return {"widget": szWidget, "text": _plainCell(entry.get("text") or u"", args.get("raw"))}


# <!-- custom: These are the drawing coordinates 'uipress row= column=' uses. Returning actions separately lets callers distinguish link rows from headers before pressing. (GPT-6.2-Sol) -->
def _tableCellActions(entry, iRows, iColumns):
	cells = []
	names = {}
	for szPosition, (iType, iData1, iData2) in entry.get("cells", {}).items():
		iColumn, iRow = [int(iIndex) for iIndex in szPosition.split(",")]
		if 0 <= iRow < iRows and 0 <= iColumn < iColumns:
			if iType not in names:
				names[iType] = pilot._enumName(WidgetTypes, iType)
			cells.append({"row": iRow, "column": iColumn, "widgetType": names[iType], "data1": iData1, "data2": iData2})
	cells.sort(key=lambda cell: (cell["row"], cell["column"]))
	return cells


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


_HELP["uifont"] = "Read or preview the Python UI text sizes in this client. With no arguments shows the sizes. On the map, set tiny, body, label or title to a whole size 1 to 4, or reset=1 to restore the configured sizes. Changes need the all role and last until reset or exit. Open advisors again to build them at the preview size. Native hover text is unchanged. args: tiny, body, label, title, reset."


def cmd_uifont(args):
	# <!-- custom: Reuse the map HUD redraw and invalidate its widget record without rebuilding the main interface, which clears the minimap mid-game. (GPT-6.2-Sol) -->
	dSizes = dict((szRole, args[szRole]) for szRole in ("tiny", "body", "label", "title") if szRole in args)
	bReset = args.get("reset", False)
	if type(bReset) not in (bool, int) or bReset not in (0, 1) or (bReset and dSizes):
		raise ValueError("use reset=1 by itself or pass font sizes")
	if dSizes or bReset:
		_requireHudInput()
		if not _isOpen(CvScreenEnums.MAIN_INTERFACE) or CyInterface().isCityScreenUp() or _activeScreens():
			raise ValueError("return to the map before changing the font preview")
		SASTextScale.setUIFontPreview(dSizes, bReset)
		CvScreensInterface.mainInterface.setCommerceAdjustRects()
		pilot._state["uiMainKey"] = None
		CyInterface().makeInterfaceDirty()
		CvScreensInterface.forceScreenRedraw([CvScreenEnums.MAIN_INTERFACE])
	return SASTextScale.getUIFontSizes()


# <!-- custom: While diplomacy or a displayed popup owns input, no click reaches the main interface or the map; shared by the main interface's record and 'uiplot' (Codex's review found 'uiplot' without it). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def _requireHudInput():
	if pilot._diploState()["open"] or pilot._pendingContact() is not None:
		raise ValueError("the diplomacy screen owns input; 'diplo' reads it")
	# <!-- custom: BUG's options dialog is modal, and not a screen _activeScreens lists (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if _optionsOpen():
		raise ValueError("BUG's options dialog owns input; 'uioptions close=1' closes it")
	if hasattr(gc.getGame(), "getSASPilotPopups"):
		for popup in pilot._popups():
			if popup["state"] == "DISPLAYED":
				raise ValueError("a %s popup on display owns input; 'popups' lists it" % popup["type"])


def _mainRecord(bPress):
	# <!-- custom: Codex's review: refreshing the main interface for every command cost three full redraws for a list, a hover and a press, each rebuilding the production chooser, and the main interface could be refreshed and pressed while the diplomacy screen or a popup owned input.
	# So input elsewhere refuses, and the record is redrawn only when it may be stale: another selection, turn or city screen state, or a press since, which can change the interface (a toggle hid the scoreboard button). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	_requireHudInput()
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


_HELP["uiitems"] = "The items of a multi-list, such as the main interface's BottomButtonList with the selected unit's actions or the open city's builds, numbered as 'uipress item=' takes them: widget type and data, with the action, unit, building, project or process it stands for. The main interface is recorded anew first. text= names the widget by what it shows instead of widget=, such as text=Augustus for his scoreboard row: an exact match, else the one widget containing it, without case; several are listed. For a drop-down, its entries instead, numbered for 'uipress choice=', with the one selected. args: widget, text, screen (default the open one, or the main interface)."


def cmd_uiitems(args):
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, False)
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		_mainRecord(False)
	szWidget = _widgetArg(iScreen, args)
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
		# <!-- custom: Named by its text, so the items listed are not compared by number alone. (Claude code Opus 5.5) -->
		if item.get("listBox"):
			row["text"] = szAbout
			# <!-- custom: A Sevopedia category entry names its category screen, such as PEDIA_MOVIES, the same in every language. (Claude code Opus 5.5) -->
			if item["widget"] == int(WidgetTypes.WIDGET_PEDIA_MAIN):
				row["category"] = _screenNames().get(item["data1"], str(item["data1"]))
		if szAbout is not None:
			row["about"] = szAbout
		result.append(row)
	if entry.get("options") is not None:
		# <!-- custom: The selection is read from the box itself, as screens read it (getSelectedPullDownID gives the entry's index): the recorded flags are those it was built with, which a mouse choice or a rebuild while the recorder was off left stale (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		iSelected = CyGInterfaceScreen("", iScreen).getSelectedPullDownID(szWidget)
		return {"widget": szWidget, "choices": [{"choice": i, "text": _plainCell(entry["options"][i]["text"], False), "selected": i == iSelected} for i in range(len(entry["options"]))]}
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


# <!-- custom: An item named by what it does, such as about=INTERFACEMODE_GO_TO, rather than by its place: on 2026-11-20 a Maceman's Go To was item 3 until it moved, after which item 3 was Delete, and pressing it by number asked to delete the unit (the confirmation was refused).
# The name is compared without case and must match exactly one item; the list is read when pressed, so it cannot be stale. (Claude code Opus 5.5) -->
def _itemByAbout(szWidget, items, about):
	szWanted = str(about).strip().upper()
	# <!-- custom: Items with no name are left out: str(None) made about=None match them (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	found = [i for i in range(len(items)) if _itemAbout(items[i]) is not None and str(_itemAbout(items[i])).upper() == szWanted]
	if len(found) == 1:
		return found[0]
	if not found:
		raise ValueError("no item of %s does %s now: %s" % (szWidget, about, ", ".join([str(_itemAbout(item)) for item in items])))
	raise ValueError("%d items of %s do %s; give item= from 'uiitems'" % (len(found), szWidget, about))


def _optionIndex(szWidget, options, choice):
	# <!-- custom: Normalized to Unicode once: str() of an accented label raised under Python 2.4, and a blank choice was in every entry (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if isinstance(choice, (int, long)):
		choice = unicode(choice)
	szChoice = unicode(choice).strip()
	if not szChoice:
		raise ValueError("choice= is empty; give the entry's number or text")
	if szChoice.isdigit():
		iChoice = int(szChoice)
		if iChoice < 0 or iChoice >= len(options):
			raise ValueError("%s has %d entries; 'uiitems' lists them" % (szWidget, len(options)))
		return iChoice
	szWanted = szChoice.lower()
	shown = [_plainCell(option["text"], False).strip().lower() for option in options]
	found = [i for i in range(len(shown)) if shown[i] == szWanted]
	if not found:
		found = [i for i in range(len(shown)) if shown[i].find(szWanted) >= 0]
	if len(found) == 1:
		return found[0]
	if not found:
		raise ValueError("no entry of %s reads %r: %s" % (szWidget, choice, ", ".join(shown)))
	raise ValueError("%d entries of %s read %r; give its number from 'uiitems'" % (len(found), szWidget, choice))


# <!-- custom: Python cannot set a drop-down's selection (CyGInterfaceScreen has getSelectedPullDownID but no setter), so a choice rebuilds the box from its recorded creation and entries with the chosen one selected, which the window then shows and getSelectedPullDownID returns. (Claude code Opus 5.5) -->
def _chooseOption(iScreen, szWidget, iChoice):
	entry = _registry().get(iScreen, {}).get(szWidget)
	if entry is None or entry.get("createArgs") is None:
		return False
	options = entry.get("options", [])
	screen = CyGInterfaceScreen("", iScreen)
	screen.deleteWidget(szWidget)
	getattr(screen, entry["method"])(*entry["createArgs"])
	for i in range(len(options)):
		screen.addPullDownString(szWidget, options[i]["text"], options[i]["type"], options[i]["data"], i == iChoice)
	return True


def _itemAbout(item):
	# <!-- custom: A list box entry by its text, without its icons, such as Techs for the Sevopedia's category. (Claude code Opus 5.5) -->
	if item.get("listBox"):
		return re.sub(r"\[[A-Z0-9_]+\]", "", _plainCell(item["text"], False)).strip()
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


_HELP["uiselect"] = "Select as a click on the map does: unit= selects that unit and its group, so its actions fill the main interface; city= opens that city's screen. Then 'uimain' records what the main interface shows. Own units and cities only, unless player= names another under the all role. close=1 closes the city screen, as Esc does; its exit arrow is the EXE's. args: unit, close, city, player."


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
	# <!-- custom: The city screen's exit arrow is the EXE's, so the recorder never sees it, and CONTROL_ENDTURN did nothing while the screen was open, as in the window (the 2026-11-20 ui-only turn); Esc clears the selected city, which this does. (Claude code Opus 5.5) -->
	if args.get("close"):
		bWasUp = bool(CyInterface().isCityScreenUp())
		CyInterface().clearSelectedCities()
		return {"closed": bWasUp, "cityScreen": bool(CyInterface().isCityScreenUp())}
	raise ValueError("give unit=, city= or close=1")


_HELP["uistate"] = "Where the window is now, as one reply: active player, civilization, leader, turn and whether it is our turn; the scoreboard (visible, expanded, background style, lock, autocenter, scroll), the map toggles (grid, yields, bare map), the globe view and the commerce sliders; the interface mode (INTERFACEMODE_GO_TO waits for a map click, for example); the selected unit, its group's units and plot; the selected city and whether its screen is open; the open screens, and the diplomacy partner while the EXE's diplomacy screen is up ('diplo' reads and answers it); and the recorder's state. Read it before pressing anything."


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
	# <!-- custom: The Sevopedia's page: category (its SevoScreenEnums name) and item, as the screen holds them, so a press can be checked to have opened the page it aimed at (Codex's review of SASPilotUISweep.py, 2026-11-20).
	# Read from iCategory and iItem: SAS_lastPediaJump, read first, stayed at PEDIA_MAIN for the index, the hints and the charts, which do not go through pediaJump. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	pedia = CvScreensInterface.pediaMainScreen
	if pedia is not None and _isOpen(CvScreenEnums.SevoScreenEnums.PEDIA_MAIN):
		result["pedia"] = {"category": _screenNames().get(pedia.iCategory, str(pedia.iCategory)), "item": pedia.iItem}
	# <!-- custom: Diplomacy is the EXE's own screen, not a Python one, so openScreens left it out after a scoreboard press opened it (2026-11-20); its partner comes from the state 'diplo' reads. (Claude code Opus 5.5) -->
	diplo = pilot._diploState()
	if diplo["open"]:
		result["diplomacy"] = {"who": diplo["who"], "whoName": gc.getPlayer(diplo["who"]).getName()}
	result["bugOptions"] = _optionsOpen()
	# <!-- custom: The main interface's own screen: a test loop that hid every screen but number 0 hid it too (it is 99), the HUD stayed drawn but reported inactive, and its presses were refused (2026-11-20); SASPilotUISweep.py checks it after each screen closes. (Claude code Opus 5.5) -->
	result["mainInterfaceActive"] = _isOpen(CvScreenEnums.MAIN_INTERFACE)
	result["recorder"] = cmd_uirecord({})
	return result


_HELP["uiplot"] = "Click a map plot while the window waits for one, after a unit action such as Go To, Air Strike or Recon has set its interface mode ('uistate' interfaceMode): the mode's own mission (from its XML) goes to the selected group at that plot through 'mission' and its checks, and the mode returns to selection, as after a click. append=1 queues it, as a shift-click does. Without x and y, lists the plots the mode accepts, as 'targets' does. Go To Type and Go To All move the group their press made of the head's type, or of every unit of ours on its plot. Under fog, the plot-checked modes take only revealed plots. A plot with no path for Go To or Route To is refused, as the click would do nothing; cancel=1 leaves the mode, as Esc does. A mode with no mission, such as a sign or a ping, is refused. args: x, y, append, cancel."


_PLOT_CHECKED_MODES = ("INTERFACEMODE_AIRLIFT", "INTERFACEMODE_NUKE", "INTERFACEMODE_RECON", "INTERFACEMODE_PARADROP", "INTERFACEMODE_AIRBOMB", "INTERFACEMODE_RANGE_ATTACK", "INTERFACEMODE_AIRSTRIKE", "INTERFACEMODE_REBASE")


_HELP["uitype"] = "Type into the open screen as the keyboard does, such as the Sevopedia's search: each key reaches the screen's handleInput as NOTIFY_CHARACTER, key down then key up, as real keys were logged. text= types letters (capitals with Shift), digits, spaces and - . , ' /; keys= sends named keys, comma-separated InputTypes names with or without KB_, such as BACKSPACE, RETURN, LEFT. Python screens only: the main interface's hotkeys are the EXE's. args: text, keys, screen (default the open one)."


# <!-- custom: Characters text= can type, beyond letters and digits, by their InputTypes key. (Claude code Opus 5.5) -->
_TYPED_KEYS = {u" ": "KB_SPACE", u"-": "KB_MINUS", u".": "KB_PERIOD", u",": "KB_COMMA", u"'": "KB_APOSTROPHE", u"/": "KB_SLASH"}


def cmd_uitype(args):
	# <!-- custom: Typed keys came as two NOTIFY_CHARACTER events per key, logged with 'uiprobe' from real keys in the Sevopedia (2026-11-20): the key's InputTypes code as data (19 for G, 40 for Backspace), ID 1 on key down and 0 on key up, an empty function name, flags 0 and WIDGET_GENERAL.
	# The pair matters: the Sevopedia's per-key debounce skips every second event of a key, which is the key up, so a single event per key would type only every other repeated letter. (Claude code Opus 5.5) -->
	iScreen = _screenId(args.get("screen"))
	_requirePlayable(iScreen, True)
	if iScreen == CvScreenEnums.MAIN_INTERFACE:
		raise ValueError("the main interface's keys are the EXE's hotkeys; type into a Python screen such as the Sevopedia")
	keys = []
	for ch in unicode(args.get("text") or u""):
		if u"a" <= ch <= u"z" or u"A" <= ch <= u"Z":
			keys.append((int(InputTypes.KB_A) + ord(ch.lower()) - ord(u"a"), ch.isupper()))
		elif u"0" <= ch <= u"9":
			keys.append((int(InputTypes.KB_0) + ord(ch) - ord(u"0"), False))
		elif _TYPED_KEYS.has_key(ch):
			keys.append((int(getattr(InputTypes, _TYPED_KEYS[ch])), False))
		else:
			raise ValueError("cannot type %r; text= takes letters, digits, spaces and - . , ' /, and keys= named keys" % ch)
	if args.get("keys"):
		for szKey in str(args["keys"]).split(","):
			szName = szKey.strip().upper()
			if not szName.startswith("KB_"):
				szName = "KB_" + szName
			if not hasattr(InputTypes, szName):
				raise ValueError("no key %s in InputTypes" % szName)
			keys.append((int(getattr(InputTypes, szName)), False))
	if not keys:
		raise ValueError("give text= or keys=")
	# <!-- custom: A key can close the screen or bring up a popup, as Esc or Enter does in the Replay screen on the key down; the remaining events then went to a screen that no longer had input (Codex's review), so each waits until the screen is still up and nothing modal owns input. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	iSent = 0
	for (iKey, bShift) in keys:
		if not _screenTakesKeys(iScreen):
			return {"screen": _screenNames().get(iScreen, str(iScreen)), "keys": iSent, "stopped": "the screen closed or lost input after %d of %d keys" % (iSent, len(keys))}
		for iID in (1, 0):
			CvScreensInterface.handleInput([NotifyCode.NOTIFY_CHARACTER, iKey, 0, iID, iScreen, "", bShift, False, False, 0, 0, int(WidgetTypes.WIDGET_GENERAL), 0, 0, False])
			if iID == 1 and not _screenTakesKeys(iScreen):
				break
		iSent = iSent + 1
	return {"screen": _screenNames().get(iScreen, str(iScreen)), "keys": iSent}


def _screenTakesKeys(iScreen):
	if not CyGInterfaceScreen("", iScreen).isActive() or pilot._diploState()["open"]:
		return False
	if hasattr(gc.getGame(), "getSASPilotPopups"):
		for popup in pilot._popups():
			if popup["state"] == "DISPLAYED":
				return False
	return True


_GROUND_MOVE_MODES = ("INTERFACEMODE_GO_TO", "INTERFACEMODE_GO_TO_TYPE", "INTERFACEMODE_GO_TO_ALL", "INTERFACEMODE_ROUTE_TO")


def cmd_uiplot(args):
	# <!-- custom: A unit action such as Go To only sets an interface mode and waits for a map click, which the EXE then turns into the mode's mission (CvInterfaceModeInfo::getMissionType); SASPilotUI had no way to give that click (2026-11-20).
	# The mission goes through 'mission', so its checks (moves left, fog, data range) apply as to any order, and 'targets' lists the plots, as the window highlights them. (Claude code Opus 5.5) -->
	_requirePlayable(CvScreenEnums.MAIN_INTERFACE, True)
	_requireHudInput()
	eMode = CyInterface().getInterfaceMode()
	szMode = pilot._enumName(InterfaceModeTypes, int(eMode))
	info = gc.getInterfaceModeInfo(int(eMode))
	# <!-- custom: After a refused plot the window still waits in the mode, with the unit's action list hidden (2026-11-20); Esc leaves any mode in the window, cancel=1 here, so it comes before the check for a mission (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if args.get("cancel"):
		CyInterface().setInterfaceMode(InterfaceModeTypes.INTERFACEMODE_SELECTION)
		return {"mode": szMode, "cancelled": True}
	if int(eMode) == int(InterfaceModeTypes.INTERFACEMODE_SELECTION) or info.getMissionType() < 0:
		raise ValueError("the window waits for no plot (interface mode %s); press a unit action such as Go To first" % szMode)
	unit = CyInterface().getHeadSelectedUnit()
	if unit is None or unit.isNone():
		raise ValueError("no unit is selected for %s" % szMode)
	# <!-- custom: The selection is our own outside the all role, as for 'uiselect': 'mission' and 'targets' were called with the unit's owner, which skipped the player= check (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if pilot._state.get("role") not in (None, "all") and unit.getOwner() != gc.getGame().getActivePlayer():
		raise ValueError("the selected unit is player %d's, not ours; the all role allows it" % unit.getOwner())
	szMission = gc.getMissionInfo(info.getMissionType()).getType()
	# <!-- custom: The selection can change while a mode waits, so the group must still be able to use it, as 'targets' checks first; canDoInterfaceModeAt accepts any plot for the ground modes, so it does not catch this (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if not unit.getGroup().canDoInterfaceMode(eMode):
		raise ValueError("the selected group cannot use %s now; cancel=1 leaves the mode" % szMode)
	if args.get("x") is None or args.get("y") is None:
		# <!-- custom: CvSelectionGroup::canDoInterfaceModeAt checks the plot only for these modes and accepts any other, so for Go To the list held all 16,632 plots of the SAS48 map (2026-11-20); the mission then decides on arrival. (Claude code Opus 5.5) -->
		if szMode not in _PLOT_CHECKED_MODES:
			return {"mode": szMode, "mission": szMission, "plots": "any plot; the mission checks the path when given"}
		return pilot.cmd_targets({"unit": unit.getID(), "player": unit.getOwner(), "mode": szMode})
	plot = CyMap().plot(int(args["x"]), int(args["y"]))
	if plot is None or plot.isNone():
		raise ValueError("no plot %s,%s on the map" % (args["x"], args["y"]))
	# <!-- custom: Under fog, a plot-checked mode answers only for plots our team has seen, as 'targets' lists them: whether a paradrop or air strike takes an unseen plot would tell what is there (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	iFogTeam = pilot._fogTeam(args)
	if iFogTeam >= 0 and szMode in _PLOT_CHECKED_MODES and not plot.isRevealed(iFogTeam, False):
		raise ValueError("plot %d,%d is unrevealed to our team; with fog on, %s takes only revealed plots" % (plot.getX(), plot.getY(), szMode))
	if not unit.getGroup().canDoInterfaceModeAt(eMode, plot):
		raise ValueError("%s does not take plot %d,%d; uiplot without x and y lists the plots it does" % (szMode, plot.getX(), plot.getY()))
	# <!-- custom: A Go To Type onto an ocean plot was taken, reported, and silently dropped, as a click with no path does in the window (2026-11-20), so the ground moves ask the pathfinder 'move' and 'path' use first.
	# By mode, not mission: Air Strike and Rebase also give MISSION_MOVE_TO, but fly straight, and GroupPathFinder asserts against air units (Codex's review).
	# An appended move starts where the queue ends, which this path from the unit does not see, so the mission checks it. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	if szMode in _GROUND_MOVE_MODES and not (args.get("append") and unit.getGroup().getLengthMissionQueue() > 0):
		path = pilot.fromJson(pilot._pilotGame("getSASPilotPathJson").getSASPilotPathJson(unit.getOwner(), unit.getID(), plot.getX(), plot.getY(), 0))
		if not path.get("found"):
			raise ValueError("unit %d has no path to %d,%d, so the click would do nothing" % (unit.getID(), plot.getX(), plot.getY()))
	# <!-- custom: Go To Type and Go To All move more than the selected group: their XML sets bSelectType or bSelectAll, and pressing them already joined two Modern Infantry of separate groups into one (2026-11-20), so the mission goes to that group.
	# A first version also joined them here, through 'group', which Codex's review found could leave units regrouped when the mission was then refused. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	reply = pilot.cmd_mission({"unit": unit.getID(), "player": unit.getOwner(), "mission": szMission, "data1": plot.getX(), "data2": plot.getY(), "append": bool(args.get("append"))})
	CyInterface().setInterfaceMode(InterfaceModeTypes.INTERFACEMODE_SELECTION)
	return {"mode": szMode, "mission": szMission, "x": plot.getX(), "y": plot.getY(), "result": reply}


# <!-- custom: BUG's options screen (Ctrl+Alt+O, its button beside the advisors) is not a CyGInterfaceScreen but a modal CyGTabCtrl, so the widget recorder does not see it.
# Each control names a Python callback, module and function, called with (value, option ID) when the player changes it, as BugOptionsScreen.handleBugCheckboxClicked takes them; so the controls are recorded as the screen builds them, and a change calls that callback. (Claude code Opus 5.5) -->
class _OptionRecorded(object):
	def __init__(self, szMethod, original):
		self.szMethod = szMethod
		self.original = original

	def __get__(self, ctrl, owner):
		return _BoundOptionRecorded(self, ctrl)


class _BoundOptionRecorded(object):
	def __init__(self, recorded, ctrl):
		self.recorded = recorded
		self.ctrl = ctrl

	def __call__(self, *args):
		result = self.recorded.original(self.ctrl, *args)
		try:
			_noteOption(self.recorded.szMethod, args)
		except Exception:
			pilot._state["uiRecordError"] = "%s: %s" % (self.recorded.szMethod, sys.exc_info()[1])
		return result


# <!-- custom: Each control kind: where its callback module, function and option ID sit in the arguments (CyGTabCtrl's attach methods). (Claude code Opus 5.5) -->
_OPTION_KINDS = {"attachCheckBox": ("checkbox", 3), "attachRadioButton": ("radio", 3), "attachDropDown": ("dropdown", 4), "attachHSlider": ("slider", 2), "attachVSlider": ("slider", 2), "attachSpinner": ("spinner", 2), "attachEdit": ("edit", 3), "attachButton": ("button", 3)}


def _noteOption(szMethod, args):
	record = pilot._state["uiOptions"]
	if szMethod == "attachTabItem":
		record["tabs"].append({"name": args[0], "label": args[1]})
		return
	if szMethod == "setEnabled":
		if len(args) > 1 and record["controls"].has_key(args[0]):
			record["controls"][args[0]]["enabled"] = bool(args[1])
		return
	# <!-- custom: Each control takes the tab built last: BUG builds its tabs one after another, and its panel names repeat from tab to tab (TopCol0, TopHBox), so following the parents by name put the General tab's Tick Marks on the Map tab in the first test. (Claude code Opus 5.5) -->
	if len(args) >= 2 and _OPTION_KINDS.has_key(szMethod):
		(szKind, iCallback) = _OPTION_KINDS[szMethod]
		szTab = None
		if record["tabs"]:
			szTab = record["tabs"][-1]["label"]
		record["controls"][args[1]] = {"control": args[1], "kind": szKind, "module": args[iCallback], "function": args[iCallback + 1], "id": args[iCallback + 2], "order": len(record["controls"]), "enabled": True, "tab": szTab}
		# <!-- custom: A slider's bounds follow its option ID: attachHSlider(parent, name, module, function, id, min, max, value). (Claude code Opus 5.5) -->
		if szKind == "slider" and len(args) > iCallback + 4:
			record["controls"][args[1]]["min"] = args[iCallback + 3]
			record["controls"][args[1]]["max"] = args[iCallback + 4]


def _optionsScreen():
	# <!-- custom: BugOptionsScreen holds BUG's options dialog; imported where used, as BUG loads it only once the game runs. (Claude code Opus 5.5) -->
	import BugOptionsScreen
	return BugOptionsScreen.getOptionsScreen()


def _optionsOpen():
	screen = _optionsScreen()
	return getattr(screen, "pTabControl", None) is not None


def _optionsRecord():
	record = pilot._state.get("uiOptions")
	if record is None or not record["controls"] or record.get("ctrl") is not _optionsScreen().pTabControl:
		raise ValueError("this options dialog was not opened through SASPilot; close it ('uioptions close=1') and open it with open=1")
	return record


def _optionDescribe(record, control):
	# <!-- custom: Title, value and choices from BUG's option itself, so they are current: the recorded arguments hold only what the screen was built with. (Claude code Opus 5.5) -->
	# <!-- custom: findOption, as a button's ID, such as GeneralHelp_Button, is no option: getOption raised for it in the first test. (Claude code Opus 5.5) -->
	option = _optionsScreen().options.findOption(control["id"])
	row = {"id": control["id"], "kind": control["kind"], "tab": _plainCell(control["tab"] or u"", False)}
	if not control["enabled"]:
		row["enabled"] = False
	if option is None:
		return row
	row["title"] = _plainCell(option.getTitle(), False)
	if control["kind"] == "dropdown":
		row["value"] = option.getIndex()
		row["choices"] = [_plainCell(unicode(value), False) for value in option.getDisplayValues()]
	else:
		row["value"] = option.getValue()
	return row


_HELP["uioptions"] = "BUG's options screen, the modal tab control the advisors' BUG button and Ctrl+Alt+O open: open=1 opens it, as its button does, recording its controls as it builds them; then its controls, each with its tab, title, kind (checkbox, dropdown, slider, ...), option id for 'uioption', value (a dropdown's as the index of its choices) and enabled=false when greyed out. close=1 presses its Exit, which saves the options to BUG's ini files, as in the window. args: open, close, tab (part of a tab label), match (part of a title or id)."


def cmd_uioptions(args):
	if args.get("open"):
		if _optionsOpen():
			raise ValueError("BUG's options screen is already open")
		# <!-- custom: Not over the diplomacy screen or a popup on display, as its button cannot be reached then (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		_requireHudInput()
		pilot._state["uiOptions"] = {"tabs": [], "controls": {}}
		originals = {}
		for szMethod in dir(CyGTabCtrl):
			if szMethod.startswith("attach") or szMethod == "setEnabled":
				originals[szMethod] = getattr(CyGTabCtrl, szMethod)
		# <!-- custom: Wrapped only while the screen is built, which showBugOptionsScreen does at once, and given back even if the build fails. (Claude code Opus 5.5) -->
		# <!-- custom: Only the methods actually replaced are given back (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		replaced = []
		try:
			for (szMethod, original) in originals.items():
				setattr(CyGTabCtrl, szMethod, _OptionRecorded(szMethod, original))
				replaced.append(szMethod)
			CvScreensInterface.showBugOptionsScreen()
		finally:
			for szMethod in replaced:
				setattr(CyGTabCtrl, szMethod, originals[szMethod])
		# <!-- custom: The recording belongs to this dialog: closed and reopened by hand, a new dialog has other controls and callbacks, and the old record would have served it (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		pilot._state["uiOptions"]["ctrl"] = _optionsScreen().pTabControl
	if not _optionsOpen():
		raise ValueError("BUG's options screen is not open; open=1 opens it")
	if args.get("close"):
		# <!-- custom: BugOptionsScreen's Exit handler closes the dialog and writes the options, as its Exit button does. (Claude code Opus 5.5) -->
		import BugOptionsScreen
		BugOptionsScreen.handleBugExitButtonInput([""])
		pilot._state["uiOptions"] = None
		return {"closed": True}
	record = _optionsRecord()
	controls = record["controls"].values()
	controls.sort(lambda a, b: cmp(a["order"], b["order"]))
	rows = []
	for control in controls:
		row = _optionDescribe(record, control)
		if args.get("tab") is not None and row["tab"].upper().find(str(args["tab"]).upper()) < 0:
			continue
		if args.get("match") is not None and (row.get("title", u"") + u" " + row["id"]).upper().find(unicode(args["match"]).upper()) < 0:
			continue
		rows.append(row)
	return {"tabs": [_plainCell(tab["label"], False) for tab in record["tabs"]], "controls": rows}


_HELP["uioption"] = "Change one control of BUG's options screen, as a click does: its callback gets (value, id), as the screen calls it, so BUG sets the option and applies it; the screen's own drawing of the control is not refreshed until it is reopened. A checkbox takes 1 or 0, a dropdown the index of its choice ('uioptions' lists them), a slider a number. The change is saved to BUG's ini files when the screen closes ('uioptions close=1'). args: id, value."


def cmd_uioption(args):
	if not _optionsOpen():
		raise ValueError("BUG's options screen is not open; 'uioptions open=1' opens it")
	record = _optionsRecord()
	found = [control for control in record["controls"].values() if control["id"] == args["id"]]
	if len(found) != 1:
		raise ValueError("%d controls have the option id %s; 'uioptions' lists them" % (len(found), args["id"]))
	control = found[0]
	if not control["enabled"]:
		raise ValueError("%s is greyed out in the window" % args["id"])
	if control["kind"] not in ("checkbox", "dropdown", "slider"):
		raise ValueError("%s is a %s; only checkboxes, dropdowns and sliders are set this way" % (args["id"], control["kind"]))
	# <!-- custom: Whole numbers only, and a checkbox 0 or 1: the first version made 2 true and 1.9 the index 1 (Codex's review). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	value = args["value"]
	if isinstance(value, bool) or not (isinstance(value, int) or (isinstance(value, str) and value.lstrip("-").isdigit())):
		raise ValueError("value must be a whole number, not %r" % (value,))
	value = int(value)
	if control["kind"] == "checkbox":
		if value not in (0, 1):
			raise ValueError("a checkbox takes 1 or 0, not %d" % value)
		value = bool(value)
	before = _optionDescribe(record, control)
	# <!-- custom: Only what the control offers: the first test set a three-choice dropdown to 9, which BUG stored.
	# A slider keeps the bounds it was built with. (Claude code Opus 5.5) -->
	if control["kind"] == "dropdown" and not 0 <= value < len(before.get("choices", [])):
		raise ValueError("%s has %d choices, 0 to %d" % (args["id"], len(before.get("choices", [])), len(before.get("choices", [])) - 1))
	if control["kind"] == "slider" and not control["min"] <= value <= control["max"]:
		raise ValueError("%s takes %d to %d" % (args["id"], control["min"], control["max"]))
	module = __import__(control["module"])
	getattr(module, control["function"])((value, control["id"]))
	return {"before": before, "after": _optionDescribe(record, control)}


_HELP["uihover"] ="The hover text the window shows for a widget, a multi-list item (item=) or a table cell (row=, column=), as plain text; read through the DLL for typed widgets, so it is the tooltip a player sees. A WIDGET_GENERAL widget has none of its own. text= names the widget by what it shows instead of widget=, such as text=Augustus for his scoreboard row: an exact match, else the one widget containing it, without case; several are listed. about= names a multi-list item by what it does, such as about=INTERFACEMODE_GO_TO or about=UNIT_WARRIOR, rather than by number: the list changes as the unit moves, and a stale number once pressed Delete. args: widget, text, item, about, row, column, screen (default the open one), raw."


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
