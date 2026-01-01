# ccgs - Custom Custom Game Screen for AdvCiv-SAS
# Based on @f1rpo's CuCuGS proof of concept: https://forums.civfanatics.com/threads/replacing-the-custom-game-screen-proof-of-concept.670307/
#
# This script is part of the AdvCiv-SAS mod project.
# (c) 2025 wonderingabout & AI helpers (see Authors in root README.md)
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
# NOTE: Don't always trust the linter! In Civ4 Python code:
# - ScreenInput being "unused" is common - it's often loaded from files without direct module calls
# - Print statements may show as errors in Python 3 linters but are valid in Python 2.4
# - Many Civ4-specific imports appear unused but are required for the game engine
#
# Widget naming quirks (learned from debugging with Middle-earth mod's Platypedia):
# - Civ4 strips NUMBERS from widget names! "VictoryDropdown1" becomes "VictoryDropdown" in events
# - Solution: Use descriptive names with text suffixes (e.g., "Victory_VICTORY_TIME", "Victory_VICTORY_CONQUEST")
# - Cannot have multiple widgets with the same ID - they will overwrite each other
# - This wrapper/mapping approach is inspired by patterns in CvExoticForeignAdvisor and Sevopedia screens
#   where dictionaries map widget IDs to data for event handling
#
# Code comments policy:
# - Feel free to expand header comments with valuable insights and tricky edge cases discovered during development
# - Keep comments reasonably concise but prioritize clarity over brevity when documenting non-obvious behavior
#
# Map script discovery:
# - Uses os.getcwd() approach proven in BugHelp.py (chatgpt 5.2 solution for known issue #87 - BUG menu help not showing)
# - Searches both mod directories (PrivateMaps/PublicMaps) AND base BTS directories for map scripts
# - Filters out files starting with underscore (helper modules)
# - Note: This approach relies on CWD being the "Beyond the Sword" directory, which works for Steam users but may need adjustment for non-Steam installations
#
# Dynamic custom map options:
# - Custom map options (Resources, Shoreline, World Wrap, etc.) are defined in each map script's Python file
# - When the user changes the map dropdown selection, the screen automatically refreshes the custom options
# - This allows instant preview of map-specific settings without needing to launch and exit a game
# - Uses deleteWidget to clear old options and dynamically imports the new map script to load its options
#
# Screen layout:
# - First table (left side): World settings - World Size, Climate, Sea Level, Era, Game Speed, Map Script
# - Second table (right side): Game settings - Difficulty (human player difficulty; AI players are locked at Noble per Civ4 standard)
# - Custom map options appear below the first table, dynamically based on selected map

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
		self.loadCustomMapOptions()

		# Second table: Game Settings (positioned to the right of the first table)
		# This table starts on the right side with enough spacing to avoid overlap
		table2StartX = col2X + labelWidth + dropdownWidth + 50  # Position after the first table's right column
		table2StartY = centerY - 60  # Same vertical start as first table

		# Store grid layout parameters for custom map options refresh and leader dropdown refresh
		self.col1X = col1X
		self.col2X = col2X
		self.startY = startY
		self.rowHeight = rowHeight
		self.labelWidth = labelWidth
		self.dropdownWidth = dropdownWidth
		self.table2StartX = table2StartX
		self.table2StartY = table2StartY

		# Human Player Difficulty dropdown
		# Note: In Civ4, only the human player's difficulty is adjustable
		# AI players are locked at Noble difficulty (this is standard Civ4 behavior)
		self.DIFFICULTY_DROPDOWN_ID = "DifficultyDropDown"
		x = table2StartX
		y = table2StartY + 0 * rowHeight
		screen.setLabel("DifficultyLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_GAME_DIFFICULTY", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.DIFFICULTY_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		# Get current human player difficulty (player 0 is always the human player)
		currentDifficulty = gc.getInitCore().getHandicap(0)
		for i in reversed(range(gc.getNumHandicapInfos())):
			screen.addPullDownString(self.DIFFICULTY_DROPDOWN_ID, gc.getHandicapInfo(i).getDescription(), i, i, i == currentDifficulty)

		# Civilization dropdown
		self.CIVILIZATION_DROPDOWN_ID = "CivilizationDropDown"
		x = table2StartX
		y = table2StartY + 1 * rowHeight
		screen.setLabel("CivilizationLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_GAME_CIVILIZATION", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.CIVILIZATION_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		# Get current civilization for human player (player 0)
		currentCiv = gc.getInitCore().getCiv(0)
		# Add Random option first
		screen.addPullDownString(self.CIVILIZATION_DROPDOWN_ID, localText.getText("TXT_KEY_MAIN_MENU_RANDOM", ()), gc.getNumCivilizationInfos(), gc.getNumCivilizationInfos(), currentCiv == gc.getNumCivilizationInfos())
		# Add all civilizations
		for i in range(gc.getNumCivilizationInfos()):
			civInfo = gc.getCivilizationInfo(i)
			if not civInfo.isPlayable():
				continue
			screen.addPullDownString(self.CIVILIZATION_DROPDOWN_ID, civInfo.getDescription(), i, i, i == currentCiv)

		# Leader dropdown (will be populated based on civilization selection)
		self.LEADER_DROPDOWN_ID = "LeaderDropDown"
		x = table2StartX
		y = table2StartY + 2 * rowHeight
		screen.setLabel("LeaderLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_GAME_LEADER", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.LEADER_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		# Populate leader dropdown based on current civilization
		self.refreshLeaderDropdown()

		# Third table: Victory Conditions (positioned below the second table)
		table3StartX = table2StartX
		table3StartY = table2StartY + 4 * rowHeight

		# Victories header label
		screen.setLabel("VictoriesLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_GAME_VICTORIES", ()) + u":</font>",
				CvUtil.FONT_LEFT_JUSTIFY, table3StartX, table3StartY + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Add dropdown for each victory condition (skipping VICTORY_SCORE which is always enabled)
		# Note: All victory dropdowns share the same widget name "VictoryDropdown"
		# We use iData1 parameter to identify which victory each dropdown represents
		victoryY = table3StartY + rowHeight
		victorySpacing = 30

		# Store victory dropdown info for event handling
		self.victoryDropdownData = {}

		for i in range(gc.getNumVictoryInfos()):
			victoryInfo = gc.getVictoryInfo(i)
			# Skip VICTORY_SCORE (it's always enabled and not shown in UI)
			if i == gc.getInfoTypeForString("VICTORY_SCORE"):
				continue

			# Create unique dropdown ID using victory type name (e.g., "Victory_TIME", "Victory_CONQUEST")
			# This avoids the number-stripping issue
			victoryType = gc.getVictoryInfo(i).getType()  # Returns "VICTORY_TIME", "VICTORY_CONQUEST", etc.
			dropdownID = "Victory_" + victoryType

			# Store mapping from dropdown ID to victory index for event handling
			self.victoryDropdownData[dropdownID] = i

			# DEBUG: Print what we're creating
			print "[CustomGameScreen] Creating victory dropdown %s for victory index %d (%s)" % (dropdownID, i, victoryInfo.getDescription())

			# Add label for the victory type
			screen.setLabel(dropdownID + "_Label", self.BACKGR,
					u"<font=3>" + victoryInfo.getDescription() + u":</font>",
					CvUtil.FONT_LEFT_JUSTIFY, table3StartX, victoryY + 5, 0, FontTypes.GAME_FONT,
					WidgetTypes.WIDGET_GENERAL, -1, -1)

			# Create dropdown with ON/OFF options
			screen.addDropDownBoxGFC(dropdownID, table3StartX + labelWidth, victoryY, dropdownWidth,
					WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

			# Get current victory state from DLL
			bCurrentlyEnabled = gc.getInitCore().getVictory(i)

			# Add ON and OFF options with current state selected
			screen.addPullDownString(dropdownID, localText.getText("TXT_KEY_POPUP_YES", ()), 1, 1, bCurrentlyEnabled)   # ON
			screen.addPullDownString(dropdownID, localText.getText("TXT_KEY_POPUP_NO", ()), 0, 0, not bCurrentlyEnabled) # OFF

			victoryY += victorySpacing

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


	def loadCustomMapOptions(self):
		# Load and display custom map options for the currently selected map script
		screen = self.getScreen()
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
							x = self.col1X
						else:
							x = self.col2X

						if iOptionID % 2 == 0:
							y = self.startY + currentRow * self.rowHeight

						# Get option name from map script
						optionName = mapScript.getCustomMapOptionName([iOptionID])

						# Add label
						screen.setLabel(dropdownID + "Label", self.BACKGR,
								u"<font=3>" + optionName + ":</font>",
								CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
								WidgetTypes.WIDGET_GENERAL, -1, -1)

						# Add dropdown
						screen.addDropDownBoxGFC(dropdownID, x + self.labelWidth, y, self.dropdownWidth,
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


	def refreshCustomMapOptions(self):
		# Clear existing custom map options and reload them for the new map script
		screen = self.getScreen()

		# Delete all existing custom map option widgets (labels and dropdowns)
		for dropdownID in self.customMapOptionIDs:
			try:
				screen.deleteWidget(dropdownID)
				screen.deleteWidget(dropdownID + "Label")
			except:
				pass

		# Clear the list
		self.customMapOptionIDs = []

		# Reload custom map options for the new map script
		self.loadCustomMapOptions()


	def refreshLeaderDropdown(self):
		# Refresh the leader dropdown based on the currently selected civilization
		screen = self.getScreen()

		# Clear the leader dropdown
		screen.deleteWidget(self.LEADER_DROPDOWN_ID)
		screen.addDropDownBoxGFC(self.LEADER_DROPDOWN_ID, self.table2StartX + self.labelWidth, self.table2StartY + 2 * self.rowHeight, self.dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

		# Get current civilization and leader
		currentCiv = gc.getInitCore().getCiv(0)
		currentLeader = gc.getInitCore().getLeader(0)

		# If Random civilization is selected, show Random leader only
		if currentCiv >= gc.getNumCivilizationInfos() or currentCiv < 0:
			screen.addPullDownString(self.LEADER_DROPDOWN_ID, localText.getText("TXT_KEY_MAIN_MENU_RANDOM", ()), gc.getNumLeaderHeadInfos(), gc.getNumLeaderHeadInfos(), True)
		else:
			# Get the civilization info
			civInfo = gc.getCivilizationInfo(currentCiv)

			# Check if we got a valid civInfo (should always be true if currentCiv is in valid range)
			if civInfo is not None:
				# Add Random option first
				screen.addPullDownString(self.LEADER_DROPDOWN_ID, localText.getText("TXT_KEY_MAIN_MENU_RANDOM", ()), gc.getNumLeaderHeadInfos(), gc.getNumLeaderHeadInfos(), currentLeader == gc.getNumLeaderHeadInfos())

				# Add leaders for this civilization
				for i in range(gc.getNumLeaderHeadInfos()):
					leaderInfo = gc.getLeaderHeadInfo(i)
					# Check if this leader is available for this civilization
					if civInfo.isLeaders(i):
						screen.addPullDownString(self.LEADER_DROPDOWN_ID, leaderInfo.getDescription(), i, i, i == currentLeader)
			else:
				# Fallback: if civInfo is None, just show Random
				screen.addPullDownString(self.LEADER_DROPDOWN_ID, localText.getText("TXT_KEY_MAIN_MENU_RANDOM", ()), gc.getNumLeaderHeadInfos(), gc.getNumLeaderHeadInfos(), True)


	def update(self, fDelta): # called after handleInput
		pass


	def handleInput(self, inputClass):
		screen = self.getScreen()
		funcName = inputClass.getFunctionName()

		# DEBUG: Log all events to PythonDbg.log
		print "[CustomGameScreen] Event: %s, Notify: %d" % (funcName, inputClass.getNotifyCode())

		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
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
					# Refresh custom map options to show the new map's options
					self.refreshCustomMapOptions()

			elif funcName == self.DIFFICULTY_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.DIFFICULTY_DROPDOWN_ID)
				iDifficulty = screen.getPullDownData(self.DIFFICULTY_DROPDOWN_ID, iIndex)
				# Set difficulty for human player (player 0)
				gc.getInitCore().setHandicap(0, iDifficulty)
				# Also set all AI players to Noble (standard Civ4 behavior)
				# This ensures the game can start properly
				gc.getInitCore().setAIHandicap(gc.getInfoTypeForString("HANDICAP_NOBLE"))

			elif funcName == self.CIVILIZATION_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.CIVILIZATION_DROPDOWN_ID)
				iCiv = screen.getPullDownData(self.CIVILIZATION_DROPDOWN_ID, iIndex)
				# Set civilization for human player (player 0)
				gc.getInitCore().setCiv(0, iCiv)
				# Refresh leader dropdown to show leaders for this civilization
				self.refreshLeaderDropdown()

			elif funcName == self.LEADER_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.LEADER_DROPDOWN_ID)
				iLeader = screen.getPullDownData(self.LEADER_DROPDOWN_ID, iIndex)
				# Set leader for human player (player 0)
				gc.getInitCore().setLeader(0, iLeader)

			# Check if this is a victory dropdown by looking up in our dictionary
			elif funcName in self.victoryDropdownData:
				victoryIndex = self.victoryDropdownData[funcName]
				print "[CustomGameScreen] Victory dropdown event: %s (index %d)" % (funcName, victoryIndex)
				iIndex = screen.getSelectedPullDownID(funcName)
				iEnabled = screen.getPullDownData(funcName, iIndex)
				bEnabled = (iEnabled == 1)
				print "[CustomGameScreen] Setting victory %d to %s (data value: %d)" % (victoryIndex, bEnabled, iEnabled)
				gc.getInitCore().setVictory(victoryIndex, bEnabled)

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
