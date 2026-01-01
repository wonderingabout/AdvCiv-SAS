# AdvCiv-SAS - CuCuGS: Custom Custom Game Screen for AdvCiv-SAS
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
# - Text keys defined in Assets/XML/Text/AdvCiv-SAS_CuCuGs.xml - Localization support
# - Use os.path operations for cross-platform compatibility
# - Wrap risky operations in try/except blocks - Civ4 Python can be fragile
#
# NOTE: Don't always trust the linter! In Civ4 Python code:
# - ScreenInput being "unused" is common - it's often loaded from files without direct module calls
# - Print statements may show as errors in Python 3 linters but are valid in Python 2.4
# - Many Civ4-specific imports appear unused but are required for the game engine
# - Ruff is a Python 3 linter, so some warnings don't apply to Python 2.4
#
# Python 2.4/3 compatible print trick:
# - Python 2.4: print is a statement, not a function
# - Python 3: print is a function requiring parentheses
# - Trick: print("single string") works in BOTH! (looks like function call but isn't in Python 2.4)
# - Example: print("[Debug] Message: %s" % value) <- works in both Python 2.4 and 3
# - IMPORTANT: Only works with a SINGLE string parameter, no comma-separated args
# - Why it works: In Python 2.4, parentheses around single expression are just grouping (not function call)
# - In Python 3, it's an actual function call - same result, different mechanism
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
# DLL compilation note:
# - User prefers to compile DLL manually using AdvCiv project settings for safety and reliability
# - After making DLL changes, let user compile before testing Python code that depends on new DLL functions
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
# - Second table (right side): Game settings - Difficulty (human player difficulty; AI players are locked at Noble per Civ4 standard), Civilization, Leader
# - Third table (below second): Victory Conditions - Yes/No dropdowns for each victory type
# - Fourth table (right of third): Game Options - Yes/No dropdowns for game options like Raging Barbarians, etc.
# - Custom map options appear below the first table, dynamically based on selected map
# - TODO: Future layout improvement - stack Climate under World settings to make room for more columns

from CvPythonExtensions import *
import GenericDecoratedScreen
import CvUtil
import ScreenInput
import CvScreenEnums
import random


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

		# Debug: Check initial leader value
		initialLeader = gc.getInitCore().getLeader(0)
		print("[CustomGameScreen] interfaceScreen - Initial leader value: %d" % initialLeader)

		self.MAIN_PANEL_ID = "MainPanel"
		mainPanelMargin = 10
		mainPanelWidth = self.wScreen - 2 * mainPanelMargin
		mainPanelHeight = self.hScreen - 2 * mainPanelMargin - self.hHeader - self.hFooter
		screen.addPanel(self.MAIN_PANEL_ID, "", "", True, True,
				mainPanelMargin, mainPanelMargin + self.hFooter, mainPanelWidth, mainPanelHeight,
				PanelStyles.PANEL_STYLE_MAIN)

		centerX = mainPanelWidth / 2
		centerY = mainPanelHeight / 2

		# Grid layout for dropdowns - reorganized for better space usage
		dropdownWidth = 200
		labelWidth = 240  # Increased from 100 to fix text truncation (e.g., "No Technology Brokering:", "No City Flipping From Conquest:")
		rowHeight = 40
		columnSpacing = 320  # Tighter spacing between columns
		col1X = 50  # Column 1: World/Climate/Sea/Speed, then Map and map-specific options below
		col2X = col1X + labelWidth + dropdownWidth + 30  # Column 2: Era, Difficulty/Civ/Leader, then Victories below
		col3X = col2X + labelWidth + dropdownWidth + 30  # Column 3: Game Options
		startY = centerY - 300  # Start higher to fit all options on screen

		# Column 1, Row 0: World Size
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

		# Column 1, Row 1: Climate
		self.CLIMATE_DROPDOWN_ID = "ClimateDropDown"
		x = col1X
		y = startY + 1 * rowHeight
		screen.setLabel("ClimateLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_CLIMATE", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.CLIMATE_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumClimateInfos())):
			screen.addPullDownString(self.CLIMATE_DROPDOWN_ID, gc.getClimateInfo(i).getDescription(), i, i, i == gc.getInitCore().getClimate())

		# Column 1, Row 2: Sea Level
		self.SEALEVEL_DROPDOWN_ID = "SeaLevelDropDown"
		x = col1X
		y = startY + 2 * rowHeight
		screen.setLabel("SeaLevelLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MAP_SEA_LEVEL", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.SEALEVEL_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumSeaLevelInfos())):
			screen.addPullDownString(self.SEALEVEL_DROPDOWN_ID, gc.getSeaLevelInfo(i).getDescription(), i, i, i == gc.getInitCore().getSeaLevel())

		# Column 1, Row 3: Game Speed
		self.GAMESPEED_DROPDOWN_ID = "GameSpeedDropDown"
		x = col1X
		y = startY + 3 * rowHeight
		screen.setLabel("GameSpeedLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_SPEED", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.GAMESPEED_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_HELP_GAME_SPEED, GameSpeedTypes.NO_GAMESPEED, 1, FontTypes.GAME_FONT)
		screen.setToolTipAlignment(self.GAMESPEED_DROPDOWN_ID, ToolTipAlignTypes.TOOLTIP_BOTTOM_RIGHT)
		for i in reversed(range(gc.getNumGameSpeedInfos())):
			screen.addPullDownString(self.GAMESPEED_DROPDOWN_ID, gc.getGameSpeedInfo(i).getDescription(), i, i, i == gc.getInitCore().getGameSpeed())

		# Column 1, Row 4: Map Script (below Game Speed)
		self.MAPSCRIPT_DROPDOWN_ID = "MapScriptDropDown"
		x = col1X
		y = startY + 4 * rowHeight
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

		# Era/Difficulty/Civ/Leader section (Column 2)
		table2StartX = col2X
		table2StartY = startY  # Align with the top

		# Column 2, Row 0: Era (thematically fits with gameplay settings)
		self.ERA_DROPDOWN_ID = "EraDropDown"
		x = table2StartX
		y = table2StartY + 0 * rowHeight
		screen.setLabel("EraLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_MENU_ERA", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.ERA_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		for i in reversed(range(gc.getNumEraInfos())):
			screen.addPullDownString(self.ERA_DROPDOWN_ID, gc.getEraInfo(i).getDescription(), i, i, i == gc.getInitCore().getEra())

		# Store grid layout parameters for custom map options refresh, leader dropdown refresh, and leader info panel
		self.col1X = col1X
		self.col2X = col2X
		self.col3X = col3X
		self.startY = startY
		self.rowHeight = rowHeight
		self.labelWidth = labelWidth
		self.dropdownWidth = dropdownWidth
		self.table2StartX = table2StartX
		self.table2StartY = table2StartY

		# Column 2, Row 1: Human Player Difficulty (after Era)
		# Note: In Civ4, only the human player's difficulty is adjustable
		# AI players are locked at Noble difficulty (this is standard Civ4 behavior)
		self.DIFFICULTY_DROPDOWN_ID = "DifficultyDropDown"
		x = table2StartX
		y = table2StartY + 1 * rowHeight
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

		# Column 2, Row 2: Civilization dropdown
		self.CIVILIZATION_DROPDOWN_ID = "CivilizationDropDown"
		x = table2StartX
		y = table2StartY + 2 * rowHeight
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

		# Column 2, Row 3: Leader dropdown (will be populated based on civilization selection)
		self.LEADER_DROPDOWN_ID = "LeaderDropDown"
		x = table2StartX
		y = table2StartY + 3 * rowHeight
		screen.setLabel("LeaderLabel", self.BACKGR,
				u"<font=3>" + localText.getText("TXT_KEY_GAME_LEADER", ()) + "</font>",
				CvUtil.FONT_LEFT_JUSTIFY, x, y + 5, 0, FontTypes.TITLE_FONT,
				WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addDropDownBoxGFC(self.LEADER_DROPDOWN_ID, x + labelWidth, y, dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		# Populate leader dropdown based on current civilization
		self.refreshLeaderDropdown()

		# Victory Conditions (positioned below Era/Difficulty/Civ/Leader in Column 2)
		# Column 2 has 4 rows (Era, Difficulty, Civilization, Leader)
		# Add 20px margin below it
		table3StartX = col2X
		table3StartY = startY + (4 * rowHeight) + 20

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
			print("[CustomGameScreen] Creating victory dropdown %s for victory index %d (%s)" % (dropdownID, i, victoryInfo.getDescription()))

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

		# Game Options (Column 3, aligned with top, no header to save space)
		table4StartX = col3X
		table4StartY = startY

		# Store game option dropdown info for event handling
		self.gameOptionDropdownData = {}

		# Add dropdown for each visible game option (no header, start directly)
		gameOptionY = table4StartY
		gameOptionSpacing = 30

		for i in range(gc.getNumGameOptionInfos()):
			gameOptionInfo = gc.getGameOptionInfo(i)

			# Skip options that aren't visible in single player
			if not gameOptionInfo.getVisible():
				continue

			# Create unique dropdown ID using game option type (e.g., "GameOption_GAMEOPTION_ADVANCED_START")
			gameOptionType = gameOptionInfo.getType()
			dropdownID = "GameOption_" + gameOptionType

			# Store mapping from dropdown ID to game option index for event handling
			self.gameOptionDropdownData[dropdownID] = i

			# DEBUG: Print what we're creating
			print("[CustomGameScreen] Creating game option dropdown %s for option index %d (%s)" % (dropdownID, i, gameOptionInfo.getDescription()))

			# Add label for the game option
			screen.setLabel(dropdownID + "_Label", self.BACKGR,
					u"<font=3>" + gameOptionInfo.getDescription() + u":</font>",
					CvUtil.FONT_LEFT_JUSTIFY, table4StartX, gameOptionY + 5, 0, FontTypes.GAME_FONT,
					WidgetTypes.WIDGET_GENERAL, -1, -1)

			# Create dropdown with ON/OFF options
			screen.addDropDownBoxGFC(dropdownID, table4StartX + labelWidth, gameOptionY, dropdownWidth,
					WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

			# Get current game option state from DLL
			bCurrentlyEnabled = gc.getInitCore().getGameOption(i)

			# Add ON and OFF options with current state selected
			screen.addPullDownString(dropdownID, localText.getText("TXT_KEY_POPUP_YES", ()), 1, 1, bCurrentlyEnabled)   # ON
			screen.addPullDownString(dropdownID, localText.getText("TXT_KEY_POPUP_NO", ()), 0, 0, not bCurrentlyEnabled) # OFF

			gameOptionY += gameOptionSpacing

		# Leader Info Panel (positioned to the right of Game Options in Column 4)
		self.refreshLeaderInfoPanel()

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

					# Start after World/Climate/Sea/Speed/Map in Column 1
					# Map Script is at row 4, so start at row 5
					currentRow = 5
					for iOptionID in range(iNumCustomOptions):
						dropdownID = "CustomMapOption" + str(iOptionID)
						self.customMapOptionIDs.append(dropdownID)

						# All map options stay in Column 1 (under Map Script)
						x = self.col1X
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

						# Move to next row for each option (stack vertically in Column 2)
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


	def refreshLeaderDropdown(self, forceCiv=None, forceLeader=None):
		# Refresh the leader dropdown based on the currently selected civilization
		# forceCiv: if provided, use this civ value instead of reading from InitCore
		# forceLeader: if provided, use this leader value for selection instead of reading from InitCore
		screen = self.getScreen()

		# Get current civilization and leader
		if forceCiv is not None:
			currentCiv = forceCiv
		else:
			currentCiv = gc.getInitCore().getCiv(0)
		if forceLeader is not None:
			currentLeader = forceLeader
		else:
			currentLeader = gc.getInitCore().getLeader(0)
		print("[CustomGameScreen] refreshLeaderDropdown - forceCiv: %s, forceLeader: %s, currentCiv: %d, currentLeader: %d, numLeaders: %d" % (str(forceCiv), str(forceLeader), currentCiv, currentLeader, gc.getNumLeaderHeadInfos()))

		# Clear the leader dropdown
		screen.deleteWidget(self.LEADER_DROPDOWN_ID)
		screen.addDropDownBoxGFC(self.LEADER_DROPDOWN_ID, self.table2StartX + self.labelWidth, self.table2StartY + 3 * self.rowHeight, self.dropdownWidth,
				WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)

		# If Random civilization is selected, show Random leader only
		if currentCiv >= gc.getNumCivilizationInfos() or currentCiv < 0:
			# Random civ: only show Random leader option
			# DON'T set InitCore here - let WIDGET_CLOSE_SCREEN handler do it when game launches
			print("[CustomGameScreen] Random civ - showing Random leader only")
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


	def refreshLeaderInfoPanel(self, forceCiv=None, forceLeader=None):
		# Display leader portrait, name, civ button, traits, unique units/buildings
		# forceCiv: if provided, use this civ value instead of reading from InitCore
		# forceLeader: if provided, use this leader value instead of reading from InitCore
		screen = self.getScreen()

		# Get current leader and civ
		if forceLeader is not None:
			currentLeader = forceLeader
		else:
			currentLeader = gc.getInitCore().getLeader(0)  # Player 0 is human player

		if forceCiv is not None:
			currentCiv = forceCiv
		else:
			currentCiv = gc.getInitCore().getCiv(0)

		print("[CustomGameScreen] refreshLeaderInfoPanel - forceCiv: %s, forceLeader: %s, currentCiv: %d, currentLeader: %d, numLeaders: %d, numCivs: %d" % (str(forceCiv), str(forceLeader), currentCiv, currentLeader, gc.getNumLeaderHeadInfos(), gc.getNumCivilizationInfos()))

		# Check if random leader or civ
		bRandomLeader = (currentLeader >= gc.getNumLeaderHeadInfos() or currentLeader < 0)
		bRandomCiv = (currentCiv >= gc.getNumCivilizationInfos() or currentCiv < 0)
		print("[CustomGameScreen] bRandomLeader: %s, bRandomCiv: %s" % (str(bRandomLeader), str(bRandomCiv)))

		# Get a fallback leader for displaying traits when leader is random but civ is selected
		# Find the first leader available for this civilization
		fallbackLeader = -1
		if bRandomLeader and not bRandomCiv:
			try:
				civInfoTemp = gc.getCivilizationInfo(currentCiv)
				for iLeader in range(gc.getNumLeaderHeadInfos()):
					if civInfoTemp.isLeaders(iLeader):
						fallbackLeader = iLeader
						print("[CustomGameScreen] Found fallback leader: %d for civ %d" % (fallbackLeader, currentCiv))
						break
			except:
				# Safety: if we can't get civ info or find a leader, just skip
				fallbackLeader = -1
		print("[CustomGameScreen] fallbackLeader: %d" % fallbackLeader)

		# Leader info panel positioning (Column 4, to the right of Game Options)
		panelX = self.col3X + self.labelWidth + self.dropdownWidth + 30
		panelY = self.startY
		panelWidth = 300
		panelHeight = 600

		# Delete existing widgets if they exist
		try:
			screen.deleteWidget("LeaderInfoPanel")
			screen.deleteWidget("LeaderPortrait")
			screen.deleteWidget("LeaderName")
			screen.deleteWidget("LeaderCivButton")
			for i in range(10):  # Clear up to 10 possible trait labels, unit/building buttons
				screen.deleteWidget("LeaderTrait" + str(i))
				screen.deleteWidget("DefaultUnit" + str(i))
				screen.deleteWidget("UniqueUnit" + str(i))
				screen.deleteWidget("DefaultBuilding" + str(i))
				screen.deleteWidget("UniqueBuilding" + str(i))
		except:
			pass

		# Add main panel
		screen.addPanel("LeaderInfoPanel", "", "", True, False, panelX, panelY, panelWidth, panelHeight, PanelStyles.PANEL_STYLE_BLUE50)

		# Portrait positioning
		portraitY = panelY + 10
		portraitWidth = 200
		portraitHeight = 250
		portraitX = panelX + (panelWidth - portraitWidth) / 2

		# If civ or leader is Random, show Random portrait
		if bRandomLeader or bRandomCiv:
			# Random leader/civ - show placeholder
			print("[CustomGameScreen] Showing Random portrait (bRandomLeader=%s, bRandomCiv=%s)" % (str(bRandomLeader), str(bRandomCiv)))
			screen.addDDSGFC("LeaderPortrait", "Art/Interface/Buttons/General/button_alert_new.dds",
					portraitX, portraitY, portraitWidth, portraitHeight, WidgetTypes.WIDGET_GENERAL, -1, -1)

			# Random text
			textY = portraitY + portraitHeight + 10
			screen.setLabel("LeaderName", "Background",
					u"<font=3b>" + localText.getText("TXT_KEY_MAIN_MENU_RANDOM", ()) + "</font>",
					CvUtil.FONT_CENTER_JUSTIFY, panelX + panelWidth / 2, textY, 0,
					FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		else:
			# Show actual leader portrait
			print("[CustomGameScreen] Showing leader portrait for leader %d" % currentLeader)
			screen.addLeaderheadGFC("LeaderPortrait", currentLeader, AttitudeTypes.ATTITUDE_PLEASED,
					portraitX, portraitY, portraitWidth, portraitHeight, WidgetTypes.WIDGET_GENERAL, -1, -1)

			# Leader full name (portrait has hover info, but name is still useful)
			leaderInfo = gc.getLeaderHeadInfo(currentLeader)
			textY = portraitY + portraitHeight + 10
			screen.setLabel("LeaderName", "Background",
					u"<font=3b>" + leaderInfo.getDescription() + "</font>",
					CvUtil.FONT_CENTER_JUSTIFY, panelX + panelWidth / 2, textY, 0,
					FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Content below portrait (shown if civ is selected, even if leader is random)
		textY = portraitY + portraitHeight + 35

		if not bRandomCiv:
			try:
				civInfo = gc.getCivilizationInfo(currentCiv)
			except:
				# Safety: if we can't get civ info, treat as random
				return

			# Civilization button (with hover tooltip instead of text)
			civButtonSize = 64
			civButtonX = panelX + (panelWidth - civButtonSize) / 2
			screen.addDDSGFC("LeaderCivButton", civInfo.getButton(),
					civButtonX, textY, civButtonSize, civButtonSize,
					WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, currentCiv, 1)
			textY += civButtonSize + 15

			# Traits (individual labels to avoid wrapping issues)
			# Use actual leader if selected, or fallback leader if random
			if not bRandomLeader:
				displayLeader = currentLeader
			else:
				displayLeader = fallbackLeader
			print("[CustomGameScreen] displayLeader: %d (bRandomLeader=%s)" % (displayLeader, str(bRandomLeader)))

			# Only show traits if we have a valid leader to display
			if displayLeader >= 0 and displayLeader < gc.getNumLeaderHeadInfos():
				try:
					# Count how many leaders this civ has
					leaderCount = 0
					for iLeader in range(gc.getNumLeaderHeadInfos()):
						if civInfo.isLeaders(iLeader):
							leaderCount += 1
					print("[CustomGameScreen] leaderCount for civ %d: %d" % (currentCiv, leaderCount))

					# If leader is Random, ALWAYS show "Random Trait" placeholders for consistency
					# Even if the civ has only 1 leader, we show Random until the game actually starts
					if bRandomLeader:
						# Show generic "Random Trait" text
						print("[CustomGameScreen] Showing 'Random Trait 1' and 'Random Trait 2' (bRandomLeader=%s, leaderCount=%d)" % (str(bRandomLeader), leaderCount))
						screen.setLabel("LeaderTrait0", "Background",
								u"<font=2>" + localText.getText("TXT_KEY_CUCUGS_RANDOM_TRAIT", ()) + " 1</font>",
								CvUtil.FONT_CENTER_JUSTIFY, panelX + panelWidth / 2, textY, 0,
								FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
						textY += 20
						screen.setLabel("LeaderTrait1", "Background",
								u"<font=2>" + localText.getText("TXT_KEY_CUCUGS_RANDOM_TRAIT", ()) + " 2</font>",
								CvUtil.FONT_CENTER_JUSTIFY, panelX + panelWidth / 2, textY, 0,
								FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
						textY += 30
					else:
						# Show actual traits for the selected leader
						print("[CustomGameScreen] Showing actual traits for leader %d" % displayLeader)
						leaderInfoForTraits = gc.getLeaderHeadInfo(displayLeader)
						traitCount = 0
						for iTrait in range(gc.getNumTraitInfos()):
							if leaderInfoForTraits.hasTrait(iTrait):
								traitInfo = gc.getTraitInfo(iTrait)
								screen.setLabel("LeaderTrait" + str(traitCount), "Background",
										u"<font=2>" + traitInfo.getDescription() + "</font>",
										CvUtil.FONT_CENTER_JUSTIFY, panelX + panelWidth / 2, textY, 0,
										FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
								textY += 20
								traitCount += 1
						textY += 10
				except:
					# Safety: if we can't get leader info or count leaders, just skip traits
					pass

			# Unique Units (show unique -> default, e.g., Minuteman -> Rifleman)
			unitCount = 0
			for iUnitClass in range(gc.getNumUnitClassInfos()):
				iUniqueUnit = civInfo.getCivilizationUnits(iUnitClass)
				iDefaultUnit = gc.getUnitClassInfo(iUnitClass).getDefaultUnitIndex()
				if iUniqueUnit > -1 and iDefaultUnit != iUniqueUnit and iDefaultUnit > -1:
					# Show unique unit -> default unit (2 buttons side by side per row)
					buttonX = panelX + (panelWidth - 140) / 2  # Center pair of buttons
					buttonY = textY

					# Unique unit (left)
					screen.addDDSGFC("UniqueUnit" + str(unitCount), gc.getUnitInfo(iUniqueUnit).getButton(),
							buttonX, buttonY, 64, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iUniqueUnit, 1)
					# Default unit (right)
					screen.addDDSGFC("DefaultUnit" + str(unitCount), gc.getUnitInfo(iDefaultUnit).getButton(),
							buttonX + 76, buttonY, 64, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iDefaultUnit, 1)

					textY += 70
					unitCount += 1

			# Unique Buildings (show unique -> default, e.g., Mall -> Supermarket)
			buildingCount = 0
			for iBuildingClass in range(gc.getNumBuildingClassInfos()):
				iUniqueBuilding = civInfo.getCivilizationBuildings(iBuildingClass)
				iDefaultBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()
				if iUniqueBuilding > -1 and iDefaultBuilding != iUniqueBuilding and iDefaultBuilding > -1:
					# Show unique building -> default building
					buttonX = panelX + (panelWidth - 140) / 2
					buttonY = textY

					# Unique building (left)
					screen.addDDSGFC("UniqueBuilding" + str(buildingCount), gc.getBuildingInfo(iUniqueBuilding).getButton(),
							buttonX, buttonY, 64, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iUniqueBuilding, 1)
					# Default building (right)
					screen.addDDSGFC("DefaultBuilding" + str(buildingCount), gc.getBuildingInfo(iDefaultBuilding).getButton(),
							buttonX + 76, buttonY, 64, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iDefaultBuilding, 1)

					textY += 70
					buildingCount += 1


	def update(self, fDelta): # called after handleInput
		pass


	def handleInput(self, inputClass):
		screen = self.getScreen()
		funcName = inputClass.getFunctionName()

		# DEBUG: Log all events to PythonDbg.log
		print("[CustomGameScreen] Event: %s, Notify: %d" % (funcName, inputClass.getNotifyCode()))

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
				print("[CustomGameScreen] Civ dropdown changed - iCiv: %d, numCivs: %d" % (iCiv, gc.getNumCivilizationInfos()))
				# Set civilization for human player (player 0)
				gc.getInitCore().setCiv(0, iCiv)

				# When civ changes, reset leader to Random (-1 in InitCore)
				# This prevents keeping an incompatible leader from a different civ (e.g., Hammurabi of Celtic Empire)
				# The dropdown will show "Random" and the portrait will show Random
				# The actual leader selection/randomization happens when:
				# 1. User clicks leader dropdown and selects a specific leader -> sets that leader in InitCore
				# 2. User clicks LAUNCH with Random still selected -> we randomize before game starts (see onClose or launch handler)
				gc.getInitCore().setLeader(0, -1)
				print("[CustomGameScreen] Reset leader to -1 (Random) after civ change")

				# Refresh leader dropdown to show available leaders for this civ, with Random selected
				randomLeaderValue = gc.getNumLeaderHeadInfos()
				self.refreshLeaderDropdown(forceCiv=iCiv, forceLeader=randomLeaderValue)

				# Refresh leader info panel to show Random portrait and Random traits
				# Pass the Random leader value so it displays "Random Leader" and "Random Trait"
				self.refreshLeaderInfoPanel(forceCiv=iCiv, forceLeader=randomLeaderValue)
				print("[CustomGameScreen] Done with civ dropdown handler")

			elif funcName == self.LEADER_DROPDOWN_ID:
				iIndex = screen.getSelectedPullDownID(self.LEADER_DROPDOWN_ID)
				iLeader = screen.getPullDownData(self.LEADER_DROPDOWN_ID, iIndex)

				# Leader dropdown changed - update InitCore and UI
				# Design philosophy: Custom game screen is just a UI layer
				# We DON'T randomize here - we just store the user's selection
				# Actual randomization happens in onClose() when user clicks LAUNCH
				if iLeader >= gc.getNumLeaderHeadInfos():
					# User selected "Random" from dropdown
					# Set InitCore to -1 (Random) and show Random portrait
					gc.getInitCore().setLeader(0, -1)
					print("[CustomGameScreen] Leader dropdown: Random selected, set InitCore to -1")
					# Pass the Random value (54) to UI so it shows Random portrait and Random traits
					self.refreshLeaderInfoPanel(forceLeader=iLeader)
				else:
					# User selected a specific leader
					# Set InitCore to that leader and show that leader's portrait
					gc.getInitCore().setLeader(0, iLeader)
					print("[CustomGameScreen] Leader dropdown: Specific leader %d selected" % iLeader)
					self.refreshLeaderInfoPanel(forceLeader=iLeader)

			# Check if this is a victory dropdown by looking up in our dictionary
			elif funcName in self.victoryDropdownData:
				victoryIndex = self.victoryDropdownData[funcName]
				print("[CustomGameScreen] Victory dropdown event: %s (index %d)" % (funcName, victoryIndex))
				iIndex = screen.getSelectedPullDownID(funcName)
				iEnabled = screen.getPullDownData(funcName, iIndex)
				bEnabled = (iEnabled == 1)
				print("[CustomGameScreen] Setting victory %d to %s (data value: %d)" % (victoryIndex, bEnabled, iEnabled))
				gc.getInitCore().setVictory(victoryIndex, bEnabled)

			# Check if this is a game option dropdown by looking up in our dictionary
			elif funcName in self.gameOptionDropdownData:
				gameOptionIndex = self.gameOptionDropdownData[funcName]
				print("[CustomGameScreen] Game option dropdown event: %s (index %d)" % (funcName, gameOptionIndex))
				iIndex = screen.getSelectedPullDownID(funcName)
				iEnabled = screen.getPullDownData(funcName, iIndex)
				bEnabled = (iEnabled == 1)
				print("[CustomGameScreen] Setting game option %d to %s (data value: %d)" % (gameOptionIndex, bEnabled, iEnabled))
				gc.getInitCore().setGameOption(gameOptionIndex, bEnabled)

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
				# Screen is closing (user clicked LAUNCH or GO BACK)
				# This is our last chance to randomize any Random leader selection before game starts
				print("[CustomGameScreen] WIDGET_CLOSE_SCREEN - checking for Random leader")

				# CRITICAL: Read from the DROPDOWN UI, not from InitCore
				# InitCore gets corrupted by various game engine calls and refreshLeaderDropdown()
				# The dropdown UI is the source of truth for what the user actually selected
				screen = self.getScreen()
				iLeaderIndex = screen.getSelectedPullDownID(self.LEADER_DROPDOWN_ID)
				selectedLeader = screen.getPullDownData(self.LEADER_DROPDOWN_ID, iLeaderIndex)
				currentCiv = gc.getInitCore().getCiv(0)

				print("[CustomGameScreen] CLOSE: Dropdown shows leader=%d, civ=%d" % (selectedLeader, currentCiv))

				# If dropdown shows Random (value >= numLeaders), we need to randomize it now
				if selectedLeader >= gc.getNumLeaderHeadInfos():
					print("[CustomGameScreen] Dropdown shows Random, randomizing now before game starts")

					# Check if civilization is also Random
					isRandomCiv = currentCiv >= gc.getNumCivilizationInfos() or currentCiv < 0

					# If civ is Random, first randomize the civ itself
					if isRandomCiv:
						# Collect all valid civs
						validCivs = []
						for iCivLoop in range(gc.getNumCivilizationInfos()):
							validCivs.append(iCivLoop)

						# Randomly choose a civ
						chosenCiv = random.choice(validCivs)
						print("[CustomGameScreen] CLOSE: Random civ - randomly chose civ %d from %d civs" % (chosenCiv, len(validCivs)))
						gc.getInitCore().setCiv(0, chosenCiv)
						currentCiv = chosenCiv

					# Now randomize the leader for the chosen/selected civ
					civInfo = gc.getCivilizationInfo(currentCiv)
					validLeaders = []
					for iLeaderLoop in range(gc.getNumLeaderHeadInfos()):
						if civInfo.isLeaders(iLeaderLoop):
							validLeaders.append(iLeaderLoop)
					print("[CustomGameScreen] CLOSE: Civ %d has %d valid leaders" % (currentCiv, len(validLeaders)))

					# Randomly choose a leader (simple random.choice, not voting)
					if len(validLeaders) > 0:
						chosenLeader = random.choice(validLeaders)
						print("[CustomGameScreen] CLOSE: Randomly chose leader %d from %d valid leaders" % (chosenLeader, len(validLeaders)))
						gc.getInitCore().setLeader(0, chosenLeader)
					else:
						print("[CustomGameScreen] CLOSE: ERROR - No valid leaders found! Using first leader as fallback")
						gc.getInitCore().setLeader(0, 0)
				else:
					# Dropdown shows a specific leader - set it in InitCore
					print("[CustomGameScreen] CLOSE: Dropdown shows specific leader %d, setting in InitCore" % selectedLeader)
					gc.getInitCore().setLeader(0, selectedLeader)

				# In the unlikely case that the player has TAB'ed onto the original Custom Game screen. We want the new screen to have focus when it closes so that the original Launch button receives focus (by default, apparently). This doesn't work reliably, but it's better than failing everytime.
				self.getScreen().setFocus(self.MAIN_PANEL_ID)
		return 1 # Consume all inputs

	def onClose(self):
		# Called when the screen is about to close (e.g., when user clicks LAUNCH button)
		# This is our last chance to fix up any Random selections before the game starts
		print("[CustomGameScreen] onClose called - checking for Random leader")

		currentLeader = gc.getInitCore().getLeader(0)
		currentCiv = gc.getInitCore().getCiv(0)

		# If leader is still -1 (Random), we need to randomize it now
		# The game's built-in randomization doesn't work, so we do it manually
		if currentLeader == -1:
			print("[CustomGameScreen] Leader is still Random (-1), randomizing now before game starts")

			# Check if civilization is also Random
			isRandomCiv = currentCiv >= gc.getNumCivilizationInfos()

			# Collect valid leaders
			validLeaders = []
			if isRandomCiv:
				# Random civ: all leaders are valid
				for iLeaderLoop in range(gc.getNumLeaderHeadInfos()):
					validLeaders.append(iLeaderLoop)
				print("[CustomGameScreen] onClose: Random civ - all %d leaders are valid" % len(validLeaders))
			else:
				# Specific civ: only leaders for this civ are valid
				civInfo = gc.getCivilizationInfo(currentCiv)
				for iLeaderLoop in range(gc.getNumLeaderHeadInfos()):
					if civInfo.isLeaders(iLeaderLoop):
						validLeaders.append(iLeaderLoop)
				print("[CustomGameScreen] onClose: Specific civ %d - found %d valid leaders" % (currentCiv, len(validLeaders)))

			# Do weighted random selection (N rolls where N = number of valid leaders)
			if len(validLeaders) > 0:
				numRolls = len(validLeaders)
				leaderVotes = {}
				for iLeaderID in validLeaders:
					leaderVotes[iLeaderID] = 0

				for roll in range(numRolls):
					randomChoice = random.choice(validLeaders)
					leaderVotes[randomChoice] = leaderVotes[randomChoice] + 1

				# Find the leader with most votes
				chosenLeader = validLeaders[0]
				maxVotes = 0
				for iLeaderID in validLeaders:
					if leaderVotes[iLeaderID] > maxVotes:
						maxVotes = leaderVotes[iLeaderID]
						chosenLeader = iLeaderID

				print("[CustomGameScreen] onClose: After %d rolls, chosen leader: %d (votes: %d)" % (numRolls, chosenLeader, maxVotes))
				gc.getInitCore().setLeader(0, chosenLeader)
			else:
				print("[CustomGameScreen] onClose: ERROR - No valid leaders found! Using first leader as fallback")
				gc.getInitCore().setLeader(0, 0)
		else:
			print("[CustomGameScreen] onClose: Leader already set to %d, no randomization needed" % currentLeader)

	#def onClose_original(self):
	# Could perhaps also handle the emulated key presses here. Would have to remember in which way the screen was closed, and the InputSim functions would have to be exposed to Python for specific keys. (Because figuring out the Windows key codes in Python would require some contortions I think. We might then as well try to trigger the key presses directly from Python via the ctypes module.)
