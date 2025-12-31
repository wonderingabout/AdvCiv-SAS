# ccgs - Custom Custom Game Screen for AdvCiv-SAS
# Based on @f1rpo's CuCuGS proof of concept: https://forums.civfanatics.com/threads/replacing-the-custom-game-screen-proof-of-concept.670307/
#
# Python 2.4 compatibility requirements:
# - No nested functions with closures - Python 2.4 doesn't support closures properly
# - No ternary operators (x if condition else y) - Not available in Python 2.4
# - All variables must be defined before use - Python 2.4 is strict about scoping
# - Use tabs for indentation (not spaces) - Civ4 codebase standard
# - Text keys defined in Assets/XML/Text/CuCuGs.xml - Localization support
# - Use os.path operations for cross-platform compatibility
# - Wrap risky operations in try/except blocks - Civ4 Python can be fragile
#
# Map script discovery:
# - Uses os.getcwd() approach proven in BugHelp.py (chatgpt 5.2 solution for known issue #87 - BUG menu help not showing)
# - Searches both mod directories (PrivateMaps/PublicMaps) AND base BTS directories for map scripts
# - Filters out files starting with underscore (helper modules)
# - Note: This approach relies on CWD being the "Beyond the Sword" directory, which works for Steam users but may need adjustment for non-Steam installations

from CvPythonExtensions import *
import GenericDecoratedScreen
import CvUtil
import ScreenInput
import CvScreenEnums


gc = CyGlobalContext()
#ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

# If we also want to replace the Custom Scenario screen (and maybe Hotseat and Staging Room), then I think this should be turned into an abstract class with derived classes for each of the specific game setup screens.
class CustomGameScreen(GenericDecoratedScreen.GenericDecoratedScreen):

	def __init__(self):
		GenericDecoratedScreen.GenericDecoratedScreen.__init__(self)
		self.iScreenID = CvScreenEnums.CUSTOM_GAME_SCREEN


	def getScreen(self): # override
		return CyGInterfaceScreen("CustomGameScreen", self.iScreenID)


	def interfaceScreen(self):
		screen = self.getScreen()
		self.initDimensions()
		self.addBackgroundHeaderFooter(localText.getText("TXT_KEY_CUSTOM_GAME_TITLE", ()))

		self.MAIN_PANEL_ID = "MainPanel"
		mainPanelMargin = 10
		mainPanelWidth = self.wScreen - 2 * mainPanelMargin
		mainPanelHeight = self.hScreen - 2 * mainPanelMargin - self.hHeader - self.hFooter
		screen.addPanel(self.MAIN_PANEL_ID, "", "", True, True,
				mainPanelMargin, mainPanelMargin + self.hFooter, mainPanelWidth, mainPanelHeight,
				PanelStyles.PANEL_STYLE_MAIN)

		centerX = mainPanelWidth / 2
		centerY = mainPanelHeight / 2

		# Grid layout for dropdowns - 2 columns, 3 rows
		dropdownWidth = 200
		labelWidth = 100
		rowHeight = 40
		columnSpacing = 350  # Space between columns
		col1X = centerX - 330  # Left column
		col2X = col1X + columnSpacing  # Right column
		startY = centerY - 60  # Start position

		# Row 0 - Left: World Size, Right: Climate
		self.WORLDSIZE_DROPDOWN_ID = "WorldSizeDropDown"
		x = col1X
		y = startY + 0 * rowHeight
		screen.setLabel("WorldSizeLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_WORLD_SIZE", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.WORLDSIZE_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumWorldInfos())):
			screen.addPullDownString(self.WORLDSIZE_DROPDOWN_ID, gc.getWorldInfo(i).getDescription(), i, i, i == gc.getInitCore().getWorldSize())

		self.CLIMATE_DROPDOWN_ID = "ClimateDropDown"
		x = col2X
		screen.setLabel("ClimateLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_CLIMATE", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.CLIMATE_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumClimateInfos())):
			screen.addPullDownString(self.CLIMATE_DROPDOWN_ID, gc.getClimateInfo(i).getDescription(), i, i, i == gc.getInitCore().getClimate())

		# Row 1 - Left: Sea Level, Right: Era
		self.SEALEVEL_DROPDOWN_ID = "SeaLevelDropDown"
		x = col1X
		y = startY + 1 * rowHeight
		screen.setLabel("SeaLevelLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_SEA_LEVEL", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.SEALEVEL_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumSeaLevelInfos())):
			screen.addPullDownString(self.SEALEVEL_DROPDOWN_ID, gc.getSeaLevelInfo(i).getDescription(), i, i, i == gc.getInitCore().getSeaLevel())

		self.ERA_DROPDOWN_ID = "EraDropDown"
		x = col2X
		screen.setLabel("EraLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_ERA", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.ERA_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumEraInfos())):
			screen.addPullDownString(self.ERA_DROPDOWN_ID, gc.getEraInfo(i).getDescription(), i, i, i == gc.getInitCore().getEra())

		# Row 2 - Left: Game Speed, Right: Map Script
		self.GAMESPEED_DROPDOWN_ID = "GameSpeedDropDown"
		x = col1X
		y = startY + 2 * rowHeight
		screen.setLabel("GameSpeedLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_SPEED", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.GAMESPEED_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_HELP_GAME_SPEED, GameSpeedTypes.NO_GAMESPEED, 1, FontTypes.GAME_FONT)
		screen.setToolTipAlignment(self.GAMESPEED_DROPDOWN_ID, ToolTipAlignTypes.TOOLTIP_BOTTOM_RIGHT)
		for i in reversed(range(gc.getNumGameSpeedInfos())):
			screen.addPullDownString(self.GAMESPEED_DROPDOWN_ID, gc.getGameSpeedInfo(i).getDescription(), i, i, i == gc.getInitCore().getGameSpeed())

		# Map Script dropdown (right column, row 2)
		self.MAPSCRIPT_DROPDOWN_ID = "MapScriptDropDown"
		x = col2X
		screen.setLabel("MapScriptLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_SCRIPT", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.MAPSCRIPT_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

		# Get list of available map scripts
		import os
		self.mapScripts = []
		currentMapScript = gc.getInitCore().getMapScriptName()

		# Get directories using os.getcwd() approach (known issue #87 solution from BugHelp.py)
		# cwd returns "Beyond the Sword" directory, so we build paths from there
		try:
			cwd = os.getcwd()
			modDir = os.path.join(cwd, "Mods", "AdvCiv-SAS")
		except:
			cwd = None
			modDir = None

		# Scan mod directories (PrivateMaps/PublicMaps)
		if modDir is not None:
			# Check mod's PrivateMaps directory
			try:
				privateMapsPath = os.path.join(modDir, "PrivateMaps")
				if os.path.exists(privateMapsPath):
					for filename in os.listdir(privateMapsPath):
						if filename.endswith(".py") and not filename.startswith("_"):
							scriptName = filename[:-3]
							self.mapScripts.append(scriptName)
			except:
				pass

			# Check mod's PublicMaps directory
			try:
				publicMapsPath = os.path.join(modDir, "PublicMaps")
				if os.path.exists(publicMapsPath):
					for filename in os.listdir(publicMapsPath):
						if filename.endswith(".py") and not filename.startswith("_"):
							scriptName = filename[:-3]
							if scriptName not in self.mapScripts:
								self.mapScripts.append(scriptName)
			except:
				pass

		# Also scan base BTS directories (contains many additional maps like Arboria, Donut, etc.)
		if cwd is not None:
			# Check BTS PublicMaps directory
			try:
				btsPublicMapsPath = os.path.join(cwd, "PublicMaps")
				if os.path.exists(btsPublicMapsPath):
					for filename in os.listdir(btsPublicMapsPath):
						if filename.endswith(".py") and not filename.startswith("_"):
							scriptName = filename[:-3]
							if scriptName not in self.mapScripts:
								self.mapScripts.append(scriptName)
			except:
				pass

			# Check BTS PrivateMaps directory
			try:
				btsPrivateMapsPath = os.path.join(cwd, "PrivateMaps")
				if os.path.exists(btsPrivateMapsPath):
					for filename in os.listdir(btsPrivateMapsPath):
						if filename.endswith(".py") and not filename.startswith("_"):
							scriptName = filename[:-3]
							if scriptName not in self.mapScripts:
								self.mapScripts.append(scriptName)
			except:
				pass

		# Sort alphabetically and add to dropdown
		self.mapScripts.sort()
		if len(self.mapScripts) == 0:
			# Fallback: if we couldn't find any maps, at least show the current one
			if currentMapScript and len(currentMapScript) > 0:
				self.mapScripts.append(currentMapScript)
				screen.addPullDownString(self.MAPSCRIPT_DROPDOWN_ID, currentMapScript, 0, 0, True)
			else:
				# Show placeholder if nothing else works
				screen.addPullDownString(self.MAPSCRIPT_DROPDOWN_ID, "No maps found", 0, 0, True)
		else:
			for i in range(len(self.mapScripts)):
				scriptName = self.mapScripts[i]
				bSelected = scriptName == currentMapScript
				screen.addPullDownString(self.MAPSCRIPT_DROPDOWN_ID, scriptName, i, i, bSelected)

		# Custom Map Options (Resources, Shoreline, World Wrap) - dynamically added based on map script
		self.customMapOptionIDs = []
		iNumCustomOptions = gc.getInitCore().getNumCustomMapOptions()
		if iNumCustomOptions > 0:
			# Load the current map script to access its custom option functions
			mapScriptName = gc.getInitCore().getMapScriptName()
			if mapScriptName and len(mapScriptName) > 0:
				try:
					# Import the map script module
					mapScript = __import__(mapScriptName)

					currentRow = 3
					for iOptionID in range(iNumCustomOptions):
						dropdownID = "CustomMapOption" + str(iOptionID)
						self.customMapOptionIDs.append(dropdownID)

						# Alternate between left and right columns
						if iOptionID % 2 == 0:
							x = col1X
						else:
							x = col2X

						if iOptionID % 2 == 0:
							y = startY + currentRow * rowHeight

						# Get option name from map script
						optionName = mapScript.getCustomMapOptionName([iOptionID])

						# Add label
						screen.setLabel(dropdownID + "Label", self.BACKGR,
								u"<font=3>" + optionName + ":</font>",
								CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
								WidgetTypes.WIDGET_GENERAL, -1, -1)

						# Add dropdown
						screen.addDropDownBoxGFC(dropdownID, x + labelWidth, y, dropdownWidth,
								WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

						# Populate dropdown options
						iNumValues = mapScript.getNumCustomMapOptionValues([iOptionID])
						for i in range(iNumValues):
							valueDesc = mapScript.getCustomMapOptionDescAt([iOptionID, i])
							bSelected = i == gc.getInitCore().getCustomMapOption(iOptionID)
							screen.addPullDownString(dropdownID, valueDesc, i, i, bSelected)

						# Move to next row after every 2 options
						if iOptionID % 2 == 1:
							currentRow = currentRow + 1
				except:
					# If we can't load the map script, just skip custom options
					pass

		screen.setText(self.EXIT_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_MAIN_MENU_LAUNCH", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, self.xExitButton, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				self.iScreenID, 0) # 0 for Launch through Return key
		# This should be the right style (defined in Civ4Theme_Custom.thm), but it really isn't? The original screen (and opening menu) seem to use the arrow_ani_l_...tga arrows, but I don't see any style that uses those.
		#screen.setStyle(self.EXIT_ID, "SF_CtrlTheme_Civ4_Control_Button_Main_ArrowR_Style")
		screen.setActivation(self.EXIT_ID, ActivationTypes.ACTIVATE_NORMAL)
		self.GOBACK_ID = "GoBackButton"
		xGoBackButton = 130
		screen.setText(self.GOBACK_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_MAIN_MENU_GO_BACK", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, xGoBackButton, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				# 2 for Go Back through simulated mouse-click.
				# (1 would do it through TAB+Return key; can't get this to work reliably.)
				self.iScreenID, 2)
		#screen.setStyle(self.GOBACK_ID, "SF_CtrlTheme_Civ4_Control_Button_Main_ArrowL_Style")
		screen.setActivation(self.GOBACK_ID, ActivationTypes.ACTIVATE_NORMAL)
		footerButtonDist = 300 # Distance in between footer buttons that are grouped together
		CLOSE_ID = "CloseButton"
		screen.setText(CLOSE_ID, self.BACKGR,
				u"<font=4>" + localText.getText("TXT_KEY_CUCUGS_CLOSE", ()).upper() + "</font>",
				CvUtil.FONT_RIGHT_JUSTIFY, xGoBackButton + footerButtonDist, self.yExitButton, 0,
				FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN,
				-1, -1) # Regular close-screen widget; no simulated key presses.
		screen.setActivation(CLOSE_ID, ActivationTypes.ACTIVATE_NORMAL)

		# This doesn't seem to affect anything
		#screen.setCloseOnEscape(False)
		# Without this, calls to interfaceScreen don't bring the screen back after ESC.
		screen.setPersistent(True)
		# This leads to a crash. I'm trying to prevent players from TAB-selecting widgets
		# on the original screen in the background ... open issue.
		#screen.setMainInterface(True)
		# Should we use bPassInput=True? The Advisor screens use False, the main screen True.
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)


	def update(self, fDelta): # called after handleInput
		pass


	def handleInput(self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
			screen = self.getScreen()
			funcName = inputClass.getFunctionName()

			if funcName == self.GAMESPEED_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.GAMESPEED_DROPDOWN_ID)
				iGameSpeed = screen.getPullDownData(self.GAMESPEED_DROPDOWN_ID, iIndex)
				gc.getInitCore().setGameSpeed(iGameSpeed)

			elif funcName == self.WORLDSIZE_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.WORLDSIZE_DROPDOWN_ID)
				iWorldSize = screen.getPullDownData(self.WORLDSIZE_DROPDOWN_ID, iIndex)
				gc.getInitCore().setWorldSize(iWorldSize)

			elif funcName == self.CLIMATE_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.CLIMATE_DROPDOWN_ID)
				iClimate = screen.getPullDownData(self.CLIMATE_DROPDOWN_ID, iIndex)
				gc.getInitCore().setClimate(iClimate)

			elif funcName == self.SEALEVEL_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.SEALEVEL_DROPDOWN_ID)
				iSeaLevel = screen.getPullDownData(self.SEALEVEL_DROPDOWN_ID, iIndex)
				gc.getInitCore().setSeaLevel(iSeaLevel)

			elif funcName == self.ERA_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.ERA_DROPDOWN_ID)
				iEra = screen.getPullDownData(self.ERA_DROPDOWN_ID, iIndex)
				gc.getInitCore().setEra(iEra)

			elif funcName == self.MAPSCRIPT_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.MAPSCRIPT_DROPDOWN_ID)
				iMapScript = screen.getPullDownData(self.MAPSCRIPT_DROPDOWN_ID, iIndex)
				if iMapScript >= 0 and iMapScript < len(self.mapScripts):
					scriptName = self.mapScripts[iMapScript]
					gc.getInitCore().setMapScriptName(scriptName)

			else:
				# Handle custom map options
				for i in range(len(self.customMapOptionIDs)):
					dropdownID = self.customMapOptionIDs[i]
					if funcName == dropdownID:
						iIndex = screen.getSelectedPullDownID(dropdownID)
						iValue = screen.getPullDownData(dropdownID, iIndex)
						gc.getInitCore().setCustomMapOption(i, iValue)
						break

		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			if inputClass.getButtonType() == WidgetTypes.WIDGET_CLOSE_SCREEN:
				# In the unlikely case that the player has TAB'ed onto the original Custom Game screen. We want the new screen to have focus when it closes so that the original Launch button receives focus (by default, apparently). This doesn't work reliably, but it's better than failing everytime.
				self.getScreen().setFocus(self.MAIN_PANEL_ID)
		return 1 # Consume all inputs

	#def onClose(self):
	# Could perhaps also handle the emulated key presses here. Would have to remember in which way the screen was closed, and the InputSim functions would have to be exposed to Python for specific keys. (Because figuring out the Windows key codes in Python would require some contortions I think. We might then as well try to trigger the key presses directly from Python via the ctypes module.)
