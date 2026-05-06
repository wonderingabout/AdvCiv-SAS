## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import time
import PyHelpers
import re
import SASBattleHistory
import SASTextScale
from SASFontUtils import *
from SASUtils import *

PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()
 
class CvMilitaryAdvisor:
	"Military Advisor"

	def __init__(self, screenId):

		self.screenId = screenId
		self.MILITARY_SCREEN_NAME = "MilitaryAdvisor"
		self.BACKGROUND_ID = "MilitaryAdvisorBackground"
		self.EXIT_ID = "MilitaryAdvisorExitWidget"

		self.WIDGET_ID = "MilitaryAdvisorWidget"
		self.REFRESH_WIDGET_ID = "MilitaryAdvisorRefreshWidget"
		self.ATTACH_WIDGET_ID = "MilitaryAdvisorAttachWidget"
		self.SELECTION_WIDGET_ID = "MilitaryAdvisorSelectionWidget"
		self.ATTACHED_WIDGET_ID = "MilitaryAdvisorAttachedWidget" # no need to explicitly delete these
		self.LEADER_BUTTON_ID = "MilitaryAdvisorLeaderButton"
		self.UNIT_PANEL_ID = "MilitaryAdvisorUnitPanel"
		self.UNIT_BUTTON_ID = "MilitaryAdvisorUnitButton"
		self.UNIT_BUTTON_LABEL_ID = "MilitaryAdvisorUnitButtonLabel"
		self.LEADER_PANEL_ID = "MilitaryAdvisorLeaderPanel"
		self.UNIT_LIST_ID = "MilitaryAdvisorUnitList"
		self.UNIT_ICON_ID = "MilitaryAdvisorUnitIcon"
		self.GREAT_GENERAL_BAR_ID = "MilitaryAdvisorGreatGeneralBar"
		self.GREAT_GENERAL_LABEL_ID = "MilitaryAdvisorGreatGeneralLabel"
		self.DEBUG_DROPDOWN_ID = "MilitaryAdvisorBattleDropdownWidget"
		self.BATTLE_TABLE_ID = "MilitaryAdvisorBattleTable"
		self.BATTLE_LOG_BUTTON_ID = "MilitaryAdvisorBattleLogButton"
		self.PAGE_UNITS = 0
		self.PAGE_BATTLES = 1
		self.iActivePage = self.PAGE_UNITS
		self.PAGE_TAB_IDS = ["MilitaryAdvisorTabButton0", "MilitaryAdvisorTabButton1"]
		self.PAGE_IDS = [self.PAGE_UNITS, self.PAGE_BATTLES]
		self.PAGE_LINK_WIDTH = [0, 0]
		self.BATTLE_ROW_PLOTS = {}

		self.Z_BACKGROUND = -2.1
		self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
		self.DZ = -0.2

		# <!-- custom: keep screen-independent advisor shell constants in init; compute runtime resolution-dependent geometry in updateRuntimeLayout via SASUtils helpers. (GPT-5.3-Codex) -->
		self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS = SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS
		self.W_RIGHT_SPACE_FOR_SCOREBOARD = SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD
		self.H_TOP_SPACE_FOR_TECH_BAR = SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR
		self.H_BOTTOM_SPACE = SAS_ADVISOR_BOTTOM_SPACE
		self.Y_TITLE = SAS_ADVISOR_TITLE_Y

		self.BORDER_WIDTH = 4
		self.W_HELP_AREA = 200
						
		self.nWidgetCount = 0
		self.nRefreshWidgetCount = 0
		self.nAttachedWidgetCount = 0
		self.iActivePlayer = -1
		self.selectedPlayerList = []
		self.selectedGroupList = []
		self.selectedUnitList = []
		self.iLanguageLoaded = -1

		# <!-- custom: expand/layout elements (e.g., great general bar) to use the new screen size. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		self.SIDE_MARGIN = 40

		# --- A. Leaders Panel (Top - Full Width) ---
		self.X_LEADERS = 20
		self.Y_LEADERS = 80
		self.H_LEADERS = 90
		self.LEADER_BUTTON_SIZE = 64
		self.LEADER_MARGIN = 12

		self.bUnitDetails = False
		self.iShiftKeyDown = 0

		# --- B. Unit List (Right Side - Fixed Width) ---
		self.W_TEXT = 430

		# --- C. Map Panel (Left Side - Fills Remaining Space) ---
		self.X_MAP = 20
		# <!-- custom: MAP_MARGIN refers to the panel border wrap, not an empty margin. (GPT-5.2-Codex (summarized)) -->
		self.MAP_MARGIN = 20

		# --- D. Great General Bar (Moved to Bottom Left)
		self.H_GREAT_GENERAL_BAR = 30
		self.X_GREAT_GENERAL_BAR = 20

		self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS = None
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE = None
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT = None
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES = None
		self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE = None
		self.IS_SAS_CV_MILITARY_ADVISOR_BATTLES_LOG_BUTTON_ENABLE = None
		self.BATTLE_HILL_PEAK_COL_ID = None
		self.BATTLE_TERRAIN_COL_ID = None
		self.BATTLE_FEATURE_COL_ID = None
		self.BATTLE_PLOT_COL_ID = None
		self.BATTLE_NUM_COLS = None

	def initDefines(self):
		# <!-- custom: Military Advisor was the remaining advisor here that read SAS XML UI defines directly in the constructor. Changing defines while Civ4 was running could then produce crashy behaviour similar to hot-changing Python, unlike the Tech Chooser/Main Interface lazy/sentinel pattern used here. Cache once after screen setup starts; empirically, this helper pattern fixed that crashy behaviour so runtime XML changes simply have no effect until the required Civ4 restart. Check each cached define's sentinel instead of only the first one for cheap exhaustive safety. See KI#128. (GPT-5.5) -->
		if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS is None:
			self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS = (gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS") > 0)
		if self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE is None:
			self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE")
		if self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT is None:
			self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT")
		if self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES is None:
			self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES")
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE is None:
			self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE = (gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE") > 0)
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLES_LOG_BUTTON_ENABLE is None:
			self.IS_SAS_CV_MILITARY_ADVISOR_BATTLES_LOG_BUTTON_ENABLE = (gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_BATTLES_LOG_BUTTON_ENABLE") > 0)
		# <!-- custom: Battle column IDs depend on the plot-context define, so derive them beside the define cache; this keeps callers from needing to know whether initDefines has already expanded the table layout. (GPT-5.5) -->
		if self.BATTLE_NUM_COLS is None:
			self.BATTLE_HILL_PEAK_COL_ID = -1
			self.BATTLE_TERRAIN_COL_ID = -1
			self.BATTLE_FEATURE_COL_ID = -1
			if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE:
				self.BATTLE_HILL_PEAK_COL_ID = 22
				self.BATTLE_TERRAIN_COL_ID = self.BATTLE_HILL_PEAK_COL_ID + 1
				self.BATTLE_FEATURE_COL_ID = self.BATTLE_HILL_PEAK_COL_ID + 2
				self.BATTLE_PLOT_COL_ID = self.BATTLE_HILL_PEAK_COL_ID + 3
			else:
				self.BATTLE_PLOT_COL_ID = 22
			self.BATTLE_NUM_COLS = self.BATTLE_PLOT_COL_ID + 1


	def initText(self):
		# <!-- custom: cache Military Advisor language-dependent text and deterministic art/color lookups once to avoid repeated calls on refresh paths. (GPT-5.3-Codex) -->
		if not CyGame().isFinalInitialized():
			return
		if self.iLanguageLoaded == CyGame().getCurrentLanguage():
			return
		self.iLanguageLoaded = CyGame().getCurrentLanguage()
		self.EXIT_TEXT = sasFontTagTitle + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TITLE = sasFontTagTitle.bold + localText.getText("TXT_KEY_MILITARY_ADVISOR_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_COMBAT_EXPERIENCE = localText.getText("TXT_KEY_MISC_COMBAT_EXPERIENCE", ())
		self.TEXT_ALL_UNITS = localText.getText("TXT_KEY_PEDIA_ALL_UNITS", ()).upper()
		self.TEXT_UNIT_TOGGLE_ON = localText.getText("TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_ON", ())
		self.TEXT_UNIT_TOGGLE_OFF = localText.getText("TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_OFF", ())
		self.TEXT_TAB_UNITS = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_UNITS_TAB", ()).upper()
		self.TEXT_TAB_BATTLES = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLES_TAB", ()).upper()
		self.PAGE_NAME_LIST = [self.TEXT_TAB_UNITS, self.TEXT_TAB_BATTLES]
		self.TEXT_BATTLES_EMPTY = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLES_EMPTY", ())
		self.TEXT_BATTLES_LOG_BUTTON = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLES_LOG_BUTTON", ())
		self.TEXT_BATTLE_TURN = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_TURN", ())
		self.TEXT_BATTLE_YEAR = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_YEAR", ())
		self.TEXT_BATTLE_EST_ODDS = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_EST_ODDS", ())
		self.TEXT_BATTLE_ROLE = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_ROLE", ())
		self.TEXT_BATTLE_XP = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_XP", ())
		self.TEXT_BATTLE_OUR_UNIT = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_OUR_UNIT", ())
		self.TEXT_BATTLE_THEIR_UNIT = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_THEIR_UNIT", ())
		self.TEXT_BATTLE_CAPTURE_COUNT = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_CAPTURE_COUNT", ())
		self.TEXT_BATTLE_PID = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_PID", ())
		self.TEXT_BATTLE_HILL_PEAK = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_HILL_PEAK", ())
		self.TEXT_BATTLE_TERRAIN = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_TERRAIN", ())
		self.TEXT_BATTLE_FEATURE = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_FEATURE", ())
		self.TEXT_BATTLE_PLOT = localText.getText("TXT_KEY_SAS_MILITARY_ADVISOR_BATTLE_PLOT", ())
		self.ART_MAINMENU_SLIDESHOW_LOAD = ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath()
		self.ART_BUTTON_HILITE_SQUARE = ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath()
		self.ART_BATTLE_PLOT_BUTTON = ArtFileMgr.getInterfaceArtInfo("INTERFACE_MINIMAP_PING").getPath()
		self.ART_BATTLE_CITY_BUTTON = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION").getPath()
		self.ART_BATTLE_CITY_CAPTURED_BUTTON = ArtFileMgr.getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath()
		self.ART_BATTLE_ROLE_ATTACKER = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_CROSSED_SWORDS").getPath()
		# <!-- custom: tried a military medal emoji but it reads as 2 half emoji with highly clashing colors; hard to read in a data-rich small column width table. Prefer the star emoji with darker variant that renders very well. Trophy seems more suited to races or competitions so not used in military context here. -->
		self.ART_BATTLE_RESULT_WON = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_WHITE_MEDIUM_STAR_2").getPath()
		self.ART_BATTLE_RESULT_LOST = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_SKULL").getPath()
		# <!-- custom: left arrow has good contrast and is clearly distinguishable from the other 2 result emojis; it is plain and dense so fills the cell nicely for retreat. Person Running was not chosen because it is too thin and visually non-homogenous, making it harder to scan quickly. (GPT-5.5) -->
		self.ART_BATTLE_RESULT_RETREAT = ArtFileMgr.getInterfaceArtInfo("SAS_EMOJI_LEFT_ARROW").getPath()
		# <!-- custom: int enum codes for battle result. Replaces previous string-compare on localized "Won"/"Lost"/"Ret." text; the text variants are not displayed in the UI (icon-only), and only the dev-only PythonDbg log dump needs human-readable strings, so localization round-trip via TXT_KEY was wasted work. Credit: Claude code Opus 4.7. (GPT-5.5) -->
		self.RESULT_WON = 0
		self.RESULT_LOST = 1
		self.RESULT_RETREAT = 2
		self.iBattleTerrainPeak = getInfoTypeOrFail("TERRAIN_PEAK")
		self.iBattleTerrainHill = getInfoTypeOrFail("TERRAIN_HILL")
		self.COLOR_YELLOW = gc.getInfoTypeForString("COLOR_YELLOW")
		self.COLOR_RED = gc.getInfoTypeForString("COLOR_RED")
		self.COLOR_GREEN = gc.getInfoTypeForString("COLOR_GREEN")
		self.COLOR_WHITE = gc.getInfoTypeForString("COLOR_WHITE")
		self.COLOR_GREAT_PEOPLE_STORED = gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_STORED")
		self.COLOR_GREAT_PEOPLE_RATE = gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_RATE")
		self.COLOR_EMPTY = gc.getInfoTypeForString("COLOR_EMPTY")
		self.STRENGTH_CHAR = u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)

	def updateRuntimeLayout(self, screen):
		# <!-- custom: compute runtime shell bounds/anchors through shared helpers so Military Advisor follows the same runtime layout flow as Foreign/Info/Domestic. (GPT-5.3-Codex) -->
		self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN = getAdvisorRuntimeBounds(
			screen,
			self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS,
			self.W_RIGHT_SPACE_FOR_SCOREBOARD,
			self.H_TOP_SPACE_FOR_TECH_BAR,
			self.H_BOTTOM_SPACE
		)
		self.X_TITLE, self.X_EXIT, self.Y_EXIT, _, self.Y_BOTTOM_PANEL = getAdvisorRuntimeAnchors(self.W_SCREEN, self.H_SCREEN)
		self.Y_LINK = self.Y_EXIT

		self.W_LEADERS = self.W_SCREEN - self.SIDE_MARGIN
		self.LEADER_COLUMNS = max(1, int(self.W_LEADERS / (self.LEADER_BUTTON_SIZE + self.LEADER_MARGIN)))

		self.X_TEXT = self.W_SCREEN - 20 - self.W_TEXT
		self.Y_TEXT = self.Y_LEADERS + self.H_LEADERS + 15
		self.H_TEXT = self.H_SCREEN - self.Y_TEXT - 55 - 15

		self.Y_MAP = self.Y_LEADERS + self.H_LEADERS + 15
		self.W_MAP = self.X_TEXT - self.X_MAP - 14
		self.W_GREAT_GENERAL_BAR = self.W_MAP
		self.Y_GREAT_GENERAL_BAR = self.Y_BOTTOM_PANEL - self.H_GREAT_GENERAL_BAR - 15
		self.H_MAP_MAX = self.Y_GREAT_GENERAL_BAR - 10 - self.Y_MAP

		# <!-- custom: inline icon size is resolution-dependent (vertical room), so compute once in runtime layout and reuse during row rendering. (GPT-5.3-Codex) -->
		self.iInlineIconSize = self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE
		if self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT > 0 and screen.getYResolution() >= self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT:
			self.iInlineIconSize = self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES
		self.PAGE_LINK_WIDTH[:] = getAdvisorRuntimeLinkWidths(CyInterface(), self.PAGE_NAME_LIST, self.EXIT_TEXT, self.X_EXIT)


	def getScreen(self):
		return CyGInterfaceScreen(self.MILITARY_SCREEN_NAME, self.screenId)

	def hideScreen(self):
		screen = self.getScreen()
		screen.hideScreen()
										
	# Screen construction function
	def interfaceScreen(self):
							
		# Create a new screen
		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		self.initDefines()
		self.initText()
		self.updateRuntimeLayout(screen)

		self.nWidgetCount = 0

		# Set the background and exit button, and show the screen
		# <!-- custom: unlike Foreign Advisor, we must set X/Y directly or the screen stays centered. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		screen.addDDSGFC(self.BACKGROUND_ID, self.ART_MAINMENU_SLIDESHOW_LOAD, 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, self.Y_BOTTOM_PANEL, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )

		screen.showWindowBackground(False)
		screen.setText(self.EXIT_ID, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
												
		# Header...
		self.szHeader = self.getNextWidgetName()
		screen.setText(self.szHeader, "Background", self.TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		self.drawTabs()

		if self.iActivePage == self.PAGE_BATTLES:
			self.iActivePlayer = getAdvisorValidPerspectivePlayer(self.iActivePlayer, bIncludeBarbarians=True, bAllowVassalPerspective=True)
			self.drawBattleHistory()
			return

		self.iActivePlayer = gc.getGame().getActivePlayer()

		# Minimap initialization
		self.H_MAP = (self.W_MAP * CyMap().getGridHeight()) / CyMap().getGridWidth()
		if (self.H_MAP > self.H_MAP_MAX):
			self.W_MAP = (self.H_MAP_MAX * CyMap().getGridWidth()) / CyMap().getGridHeight()
			self.H_MAP = self.H_MAP_MAX
		self.W_GREAT_GENERAL_BAR = self.W_MAP
		screen.addPanel("", u"", "", False, False, self.X_MAP, self.Y_MAP, self.W_MAP, self.H_MAP, PanelStyles.PANEL_STYLE_MAIN)
		screen.initMinimap(self.X_MAP + self.MAP_MARGIN, self.X_MAP + self.W_MAP - self.MAP_MARGIN, self.Y_MAP + self.MAP_MARGIN, self.Y_MAP + self.H_MAP - self.MAP_MARGIN, self.Z_CONTROLS)
		screen.updateMinimapSection(False, False)

		screen.updateMinimapColorFromMap(MinimapModeTypes.MINIMAPMODE_TERRITORY, 0.6)

		screen.setMinimapMode(MinimapModeTypes.MINIMAPMODE_MILITARY)
		
		iOldMode = CyInterface().getShowInterface()
		CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_MINIMAP_ONLY)
		screen.updateMinimapVisibility()
		CyInterface().setShowInterface(iOldMode)
	
		self.unitsList = [(0, 0, [], 0)] * gc.getNumUnitInfos()
		self.selectedUnitList = []
		# <advc.004> Reset selected unit groups if a player other than the active player was selected
		if len(self.selectedPlayerList) != 1 or self.selectedPlayerList[0] != self.iActivePlayer:
			self.selectedGroupList = []
		# Always reset the selected players
		self.selectedPlayerList = []
		# </advc.004>
		self.selectedPlayerList.append(self.iActivePlayer)

		self.drawCombatExperience()

		self.refresh(true)

	def drawTabs(self):
		screen = self.getScreen()
		iX = 0
		for iPage in range(len(self.PAGE_NAME_LIST)):
			szText = self.PAGE_NAME_LIST[iPage]
			if self.iActivePage == iPage:
				szText = localText.changeTextColor(szText, self.COLOR_YELLOW)
			screen.setText(self.PAGE_TAB_IDS[iPage], "", sasFontTagTitle + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, iX + self.PAGE_LINK_WIDTH[iPage] / 2, self.Y_LINK, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, iPage, -1)
			iX += self.PAGE_LINK_WIDTH[iPage]

	def getTurnDate(self, iTurn):
		iYear = CyGame().getTurnYear(iTurn)
		if iYear < 0:
			return localText.getText("TXT_KEY_TIME_BC", (-iYear,))
		return localText.getText("TXT_KEY_TIME_AD", (iYear,))

	def getBattleUnitStrength(self, iUnit):
		# <!-- custom: Battles table uses strength, not hammer cost; cost is less reliable for animals, spawned units, and special cases with 0 or unusual production cost. (GPT-5.5) -->
		iCombat = gc.getUnitInfo(iUnit).getCombat()
		if iCombat <= 0:
			iCombat = gc.getUnitInfo(iUnit).getAirCombat()
		return iCombat

	def getBattleStoredStrengthText(self, iStrength):
		if iStrength > 0:
			return u"%.2f" % (iStrength / 100.0)
		return u""

	def getBattleEntryColumns(self, entry):
		if len(entry) < 7:
			return None
		iTurn, iWinner, iLoser, iWinnerUnit, iLoserUnit, iX, iY = entry[:7]
		if iWinnerUnit < 0 or iWinnerUnit >= gc.getNumUnitInfos() or iLoserUnit < 0 or iLoserUnit >= gc.getNumUnitInfos():
			return None
		if SASBattleHistory.isRetreatEntry(entry):
			iResult = self.RESULT_RETREAT
			iColor = self.COLOR_YELLOW
		elif iWinner == self.iActivePlayer:
			iResult = self.RESULT_WON
			iColor = self.COLOR_GREEN
		else:
			iResult = self.RESULT_LOST
			iColor = self.COLOR_RED
		iAttacker = -1
		iDefender = -1
		if len(entry) >= 9:
			iAttacker = entry[7]
			iDefender = entry[8]
		iAttackerCurrStr = 0
		iAttackerEndStr = 0
		iAttackerMaxStr = 0
		iDefenderCurrStr = 0
		iDefenderEndStr = 0
		iDefenderMaxStr = 0
		if len(entry) >= 13:
			iAttackerCurrStr = entry[9]
			iAttackerMaxStr = entry[10]
			iDefenderCurrStr = entry[11]
			iDefenderMaxStr = entry[12]
		if len(entry) >= 18:
			iAttackerEndStr = entry[16]
			iDefenderEndStr = entry[17]
		if iAttacker == iWinner and iDefender == iLoser:
			iAttackerUnit = iWinnerUnit
			iDefenderUnit = iLoserUnit
		elif iAttacker == iLoser and iDefender == iWinner:
			iAttackerUnit = iLoserUnit
			iDefenderUnit = iWinnerUnit
		else:
			# <!-- custom: battle rows saved before attacker/defender/strength capture only know winner/loser; keep them visible with winner first.
			# Combat-log current/max strength stays blank when unknown; XML base strength is shown in a separate column so we don't present invented effective combat values. (GPT-5.5) -->
			iAttacker = iWinner
			iDefender = iLoser
			iAttackerUnit = iWinnerUnit
			iDefenderUnit = iLoserUnit
		return (iTurn, iResult, iColor, iAttacker, iAttackerUnit, iAttackerCurrStr, iAttackerEndStr, iAttackerMaxStr, iDefender, iDefenderUnit, iDefenderCurrStr, iDefenderEndStr, iDefenderMaxStr, iX, iY)

	def getBattlePerspectiveColumns(self, entry):
		tColumns = self.getBattleEntryColumns(entry)
		if tColumns is None:
			return None
		iTurn, iResult, iColor, iAttacker, iAttackerUnit, iAttackerCurrStr, iAttackerEndStr, iAttackerMaxStr, iDefender, iDefenderUnit, iDefenderCurrStr, iDefenderEndStr, iDefenderMaxStr, iX, iY = tColumns
		iWinner = entry[1]
		iLoser = entry[2]
		bRoleKnown = False
		if len(entry) >= 9:
			iStoredAttacker = entry[7]
			iStoredDefender = entry[8]
			bRoleKnown = ((iStoredAttacker == iWinner and iStoredDefender == iLoser) or (iStoredAttacker == iLoser and iStoredDefender == iWinner))
		if iAttacker == self.iActivePlayer:
			iOurRole = -1
			if bRoleKnown:
				iOurRole = 1
			iAttackerXP, bAttackerGG, iDefenderXP, bDefenderGG = SASBattleHistory.getUnitContext(entry)
			return (iTurn, iResult, iColor, iOurRole, iAttackerUnit, iAttackerCurrStr, iAttackerEndStr, iAttackerMaxStr, iAttackerXP, bAttackerGG, iDefender, iDefenderUnit, iDefenderCurrStr, iDefenderEndStr, iDefenderMaxStr, iDefenderXP, bDefenderGG, iX, iY) + self.getBattleCapturePerspective(entry) + SASBattleHistory.getPlotContext(entry)
		if iDefender == self.iActivePlayer:
			iOurRole = -1
			if bRoleKnown:
				iOurRole = 0
			iAttackerXP, bAttackerGG, iDefenderXP, bDefenderGG = SASBattleHistory.getUnitContext(entry)
			return (iTurn, iResult, iColor, iOurRole, iDefenderUnit, iDefenderCurrStr, iDefenderEndStr, iDefenderMaxStr, iDefenderXP, bDefenderGG, iAttacker, iAttackerUnit, iAttackerCurrStr, iAttackerEndStr, iAttackerMaxStr, iAttackerXP, bAttackerGG, iX, iY) + self.getBattleCapturePerspective(entry) + SASBattleHistory.getPlotContext(entry)
		return None

	def getBattleCapturePerspective(self, entry):
		if len(entry) < 16:
			return (0, -1)
		iCapturingPlayer = entry[13]
		iCapturedUnit = entry[14]
		iCapturedCount = entry[15]
		if iCapturedCount <= 0 or iCapturedUnit < 0 or iCapturedUnit >= gc.getNumUnitInfos():
			return (0, -1)
		if iCapturingPlayer == self.iActivePlayer:
			return (iCapturedCount, iCapturedUnit)
		return (-iCapturedCount, iCapturedUnit)

	def getBattleCaptureCountText(self, iCapturedCount):
		if iCapturedCount == 0:
			return u""
		szText = unicode(abs(iCapturedCount))
		if iCapturedCount > 0:
			return localText.changeTextColor(szText, self.COLOR_GREEN)
		return localText.changeTextColor(szText, self.COLOR_RED)

	def getBattleCaptureUnitText(self, iCapturedCount, iCapturedUnit):
		if iCapturedCount == 0 or iCapturedUnit < 0:
			return u""
		return gc.getUnitInfo(iCapturedUnit).getDescription()

	def getBattleCaptureUnitButton(self, iCapturedCount, iCapturedUnit):
		if iCapturedCount == 0 or iCapturedUnit < 0:
			return ""
		return gc.getUnitInfo(iCapturedUnit).getButton()

	def getBattleXPText(self, iXP, bGreatGeneral):
		if iXP < 0:
			return u""
		szText = unicode(iXP)
		if bGreatGeneral:
			return localText.changeTextColor(szText, self.COLOR_YELLOW)
		return szText

	def setBattleTerrainFeatureCell(self, screen, iRow, iCol, iInfo, bTerrain):
		szSortKey = getAdvisorIconSortKey(iInfo + 1, iRow)
		if bTerrain:
			if iInfo >= 0 and iInfo < gc.getNumTerrainInfos():
				SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, iCol, iRow, szSortKey, gc.getTerrainInfo(iInfo).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iInfo, -1, CvUtil.FONT_CENTER_JUSTIFY)
				return
		else:
			if iInfo >= 0 and iInfo < gc.getNumFeatureInfos():
				SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, iCol, iRow, szSortKey, gc.getFeatureInfo(iInfo).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iInfo, -1, CvUtil.FONT_CENTER_JUSTIFY)
				return
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, iCol, iRow, getAdvisorIconSortKey(0, iRow), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

	def setBattleHillPeakCell(self, screen, iRow, iHillPeakTerrain):
		# <!-- custom: show only peak/hill here: flat/water have no separate pedia redirects and are already visible through terrain, while peak/hill are separate combat-relevant map properties with Sevopedia entries/icons. (GPT-5.5) -->
		if iHillPeakTerrain == self.iBattleTerrainPeak or iHillPeakTerrain == self.iBattleTerrainHill:
			SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_HILL_PEAK_COL_ID, iRow, getAdvisorIconSortKey(iHillPeakTerrain + 1, iRow), gc.getTerrainInfo(iHillPeakTerrain).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, iHillPeakTerrain, -1, CvUtil.FONT_CENTER_JUSTIFY)
			return
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_HILL_PEAK_COL_ID, iRow, getAdvisorIconSortKey(0, iRow), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)

	def getBattleTerrainTypeText(self, iTerrain):
		if iTerrain >= 0 and iTerrain < gc.getNumTerrainInfos():
			return gc.getTerrainInfo(iTerrain).getType()
		return ""

	def getBattleFeatureTypeText(self, iFeature):
		if iFeature >= 0 and iFeature < gc.getNumFeatureInfos():
			return gc.getFeatureInfo(iFeature).getType()
		return ""

	def getBattlePlotButton(self, iCityContext):
		if SASBattleHistory.isCityContextCaptured(iCityContext):
			return self.ART_BATTLE_CITY_CAPTURED_BUTTON
		if SASBattleHistory.isCityContextDefended(iCityContext):
			return self.ART_BATTLE_CITY_BUTTON
		return self.ART_BATTLE_PLOT_BUTTON

	def getBattleCurrentStrengthText(self, iCurrentStrength, iMaxStrength):
		szText = self.getBattleStoredStrengthText(iCurrentStrength)
		if not szText or iMaxStrength <= 0:
			return szText
		iPct = (100 * iCurrentStrength) / iMaxStrength
		if iCurrentStrength >= iMaxStrength:
			return szText
		if iPct > 66:
			return localText.changeTextColor(szText, self.COLOR_GREEN)
		if iPct > 33:
			return localText.changeTextColor(szText, self.COLOR_YELLOW)
		return localText.changeTextColor(szText, self.COLOR_RED)

	def getBattleBaseStrengthText(self, iUnit):
		iStrength = self.getBattleUnitStrength(iUnit)
		if iStrength > 0:
			return unicode(iStrength)
		return u""

	def getBattleEstimatedOddsText(self, iOurStrength, iTheirStrength):
		# <!-- custom: estimate row-level combat favorability from the two stored start-effective strengths only; this is not exact Civ4 odds because first strikes, withdrawal, damage rounds, etc. are not modeled here. (GPT-5.5) -->
		iTotalStrength = iOurStrength + iTheirStrength
		if iOurStrength <= 0 or iTheirStrength <= 0 or iTotalStrength <= 0:
			return u""
		return unicode((100 * iOurStrength + (iTotalStrength / 2)) / iTotalStrength)

	def getBattleRoleArt(self, iOurRole):
		# <!-- custom: empty string (not unicode) because the szIcon arg of CyGInterfaceScreen.setTableText is bound as char const * (str); passing unicode triggers an ArgumentError. Credit: Claude code Opus 4.7. (GPT-5.5) -->
		if iOurRole == 1:
			return self.ART_BATTLE_ROLE_ATTACKER
		return ""

	def getBattleResultArt(self, iResult):
		if iResult == self.RESULT_WON:
			return self.ART_BATTLE_RESULT_WON
		if iResult == self.RESULT_LOST:
			return self.ART_BATTLE_RESULT_LOST
		if iResult == self.RESULT_RETREAT:
			return self.ART_BATTLE_RESULT_RETREAT
		return ""

	def getBattleResultLogText(self, iResult):
		# <!-- custom: dev-only PythonDbg log dump labels: hardcoded English (no localization round-trip via TXT_KEY) since logs are dev/diagnostic and never user-facing. Credit: Claude code Opus 4.7. (GPT-5.5) -->
		if iResult == self.RESULT_WON:
			return u"Won"
		if iResult == self.RESULT_LOST:
			return u"Lost"
		if iResult == self.RESULT_RETREAT:
			return u"Ret."
		return u""

	def getBattleRoleText(self, iOurRole):
		# <!-- custom: text variant kept for the PythonDbg.log dump because stdout cannot render table art icons. (GPT-5.5) -->
		if iOurRole == 1:
			return u"A"
		return u""

	def drawBattleHistory(self):
		screen = self.getScreen()
		# <!-- custom: Units tab has its own leader buttons, but Battles has no player selector without this shared debug/vassal dropdown; include Barbarians because battle history can involve barbarian/animal units. (GPT-5.5) -->
		addAdvisorDebugDropdown(screen, self.DEBUG_DROPDOWN_ID, self.iActivePlayer, bIncludeBarbarians=True, bAllowVassalPerspective=True)
		(iX, iY, iW, iH), (iTableX, iTableY, iTableW, iTableH) = getAdvisorMaximizedPanelLayout(self.W_SCREEN, self.Y_BOTTOM_PANEL)
		screen.addPanel(self.UNIT_PANEL_ID, "", "", True, True, iX, iY, iW, iH, PanelStyles.PANEL_STYLE_MAIN)
		self.BATTLE_ROW_PLOTS = {}
		screen.addTableControlGFC(self.BATTLE_TABLE_ID, self.BATTLE_NUM_COLS, iTableX, iTableY, iTableW, iTableH, True, True, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSort(self.BATTLE_TABLE_ID)
		screen.setStyle(self.BATTLE_TABLE_ID, "Table_StandardCiv_Style")
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 0, self.TEXT_BATTLE_TURN, 55)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 1, self.TEXT_BATTLE_YEAR, 104)
		iResultColW = 35
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 2, u"R", iResultColW)
		iPlotColW = 35
		# <!-- custom: use one shared 2-digit-friendly width for compact numeric columns (E%, base strength, XP, PID, Cap#). Values like 100%, 3-digit strength, or 3-digit XP may clip, but this preserves the plot-camera column when the vertical scrollbar appears. (GPT-5.5) -->
		iTwoDigitColW = 38
		iEstOddsColW = iTwoDigitColW
		iRoleColW = 35
		iBaseColW = iTwoDigitColW
		iXPColW = iTwoDigitColW
		iPIDColW = iTwoDigitColW
		iCaptureCountColW = iPIDColW
		iCaptureUnitColW = 35
		iTerrainColW = 0
		iFeatureColW = 0
		iHillPeakColW = 0
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE:
			iTerrainColW = 35
			iFeatureColW = 35
			iHillPeakColW = 35
		iStrengthColW = 78
		# <!-- custom: reserve right-side width for the table scrollbar gutter so unit-name text does not clip under it; Battles fills fast so the scrollbar is the common case. Matches CvInfoScreen's 14px convention. (Claude code Opus 4.7) -->
		iScrollbarGutterW = 14
		iUnitColBudget = iTableW - iScrollbarGutterW
		iUnitColW = max(105, (iUnitColBudget - 55 - 105 - iResultColW - iEstOddsColW - iRoleColW - iBaseColW - iStrengthColW - iStrengthColW - iStrengthColW - iXPColW - 35 - 35 - iPIDColW - iBaseColW - iStrengthColW - iStrengthColW - iStrengthColW - iXPColW - iCaptureCountColW - iCaptureUnitColW - iHillPeakColW - iTerrainColW - iFeatureColW - iPlotColW) / 2)
		# <!-- custom: show battles from the inspected player's perspective: our unit is always on the left and their unit follows immediately, so each row reads as a direct matchup. Our repeated civ/leader/PID are omitted because the dropdown/log PerspectivePlayer already identifies us. (GPT-5.5) -->
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 3, self.TEXT_BATTLE_EST_ODDS, iEstOddsColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 4, self.TEXT_BATTLE_ROLE, iRoleColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 5, self.STRENGTH_CHAR + u"b", iBaseColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 6, self.STRENGTH_CHAR + u"s", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 7, self.STRENGTH_CHAR + u"e", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 8, self.STRENGTH_CHAR + u"m", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 9, self.TEXT_BATTLE_XP, iXPColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 10, self.TEXT_BATTLE_OUR_UNIT, iUnitColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 11, self.TEXT_BATTLE_THEIR_UNIT, iUnitColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 12, self.TEXT_BATTLE_XP, iXPColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 13, self.STRENGTH_CHAR + u"b", iBaseColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 14, self.STRENGTH_CHAR + u"s", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 15, self.STRENGTH_CHAR + u"e", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 16, self.STRENGTH_CHAR + u"m", iStrengthColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 17, "", 35)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 18, "", 35)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 19, self.TEXT_BATTLE_PID, iPIDColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 20, self.TEXT_BATTLE_CAPTURE_COUNT, iCaptureCountColW)
		# <!-- custom: show captured unit type as a compact pedia icon rather than text. The stored row supports one captured unit type; if a future mod allows one combat to create multiple captured types, expand this column/model then. (GPT-5.5) -->
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, 21, "", iCaptureUnitColW)
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE:
			SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_HILL_PEAK_COL_ID, self.TEXT_BATTLE_HILL_PEAK, iHillPeakColW)
			SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_TERRAIN_COL_ID, self.TEXT_BATTLE_TERRAIN, iTerrainColW)
			SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_FEATURE_COL_ID, self.TEXT_BATTLE_FEATURE, iFeatureColW)
		SASTextScale.setTableColumnHeaderLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_PLOT_COL_ID, self.TEXT_BATTLE_PLOT, iPlotColW)
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLES_LOG_BUTTON_ENABLE:
			screen.setButtonGFC(self.BATTLE_LOG_BUTTON_ID, sasFontTagLabel + self.TEXT_BATTLES_LOG_BUTTON.upper() + SAS_FONT_TAG_CLOSE, "", self.X_EXIT - 110, self.Y_TITLE + 2, 64, 28, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD)
		placeAdvisorLegendLink(self, "CONCEPT_SAS_MILITARY_ADVISOR_BATTLES_LEGEND", self.W_SCREEN - 12, self.Y_TITLE)
		aEntries = SASBattleHistory.getEntriesForPlayer(self.iActivePlayer)
		if not aEntries:
			iRow = screen.appendTableRow(self.BATTLE_TABLE_ID)
			SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 1, iRow, self.TEXT_BATTLES_EMPTY, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
			return
		for entry in reversed(aEntries):
			self.addBattleHistoryTableRow(screen, entry)

	def addBattleHistoryTableRow(self, screen, entry):
		tColumns = self.getBattlePerspectiveColumns(entry)
		if tColumns is None:
			return
		iTurn, iResult, iColor, iOurRole, iOurUnit, iOurCurrStr, iOurEndStr, iOurMaxStr, iOurXP, bOurGG, iTheirPlayer, iTheirUnit, iTheirCurrStr, iTheirEndStr, iTheirMaxStr, iTheirXP, bTheirGG, iX, iY, iCapturedCount, iCapturedUnit, iTerrain, iFeature, iHillPeakTerrain, iCityContext = tColumns
		iRow = screen.appendTableRow(self.BATTLE_TABLE_ID)
		self.BATTLE_ROW_PLOTS[iRow] = (iX, iY)
		kTheirPlayer = gc.getPlayer(iTheirPlayer)
		iTheirCiv = kTheirPlayer.getCivilizationType()
		iTheirLeader = kTheirPlayer.getLeaderType()
		eCapturedUnitWidget = WidgetTypes.WIDGET_GENERAL
		if iCapturedUnit >= 0:
			eCapturedUnitWidget = WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 0, iRow, str(iTurn), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 1, iRow, self.getTurnDate(iTurn), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		# <!-- custom: show result as compact icon art in the table to save width and reduce colored-text overload; keep Won/Lost/Ret. text in the PythonDbg.log dump below. (GPT-5.5) -->
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 2, iRow, getAdvisorIconSortKey((iResult + 1) * 10, iRow), self.getBattleResultArt(iResult), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 3, iRow, self.getBattleEstimatedOddsText(iOurCurrStr, iTheirCurrStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 4, iRow, getAdvisorIconSortKey(iOurRole + 1, iRow), self.getBattleRoleArt(iOurRole), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 5, iRow, self.getBattleBaseStrengthText(iOurUnit), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 6, iRow, self.getBattleCurrentStrengthText(iOurCurrStr, iOurMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 7, iRow, self.getBattleCurrentStrengthText(iOurEndStr, iOurMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 8, iRow, self.getBattleStoredStrengthText(iOurMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 9, iRow, self.getBattleXPText(iOurXP, bOurGG), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		szOurUnitName = gc.getUnitInfo(iOurUnit).getDescription()
		szTheirUnitName = gc.getUnitInfo(iTheirUnit).getDescription()
		if bOurGG:
			szOurUnitName = localText.changeTextColor(szOurUnitName, self.COLOR_YELLOW)
		if bTheirGG:
			szTheirUnitName = localText.changeTextColor(szTheirUnitName, self.COLOR_YELLOW)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 10, iRow, szOurUnitName, gc.getUnitInfo(iOurUnit).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iOurUnit, -1, CvUtil.FONT_LEFT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 11, iRow, szTheirUnitName, gc.getUnitInfo(iTheirUnit).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iTheirUnit, -1, CvUtil.FONT_LEFT_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 12, iRow, self.getBattleXPText(iTheirXP, bTheirGG), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 13, iRow, self.getBattleBaseStrengthText(iTheirUnit), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 14, iRow, self.getBattleCurrentStrengthText(iTheirCurrStr, iTheirMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 15, iRow, self.getBattleCurrentStrengthText(iTheirEndStr, iTheirMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 16, iRow, self.getBattleStoredStrengthText(iTheirMaxStr), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 17, iRow, getAdvisorIconSortKey(iTheirCiv + 1, iRow), gc.getCivilizationInfo(iTheirCiv).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iTheirCiv, -1, CvUtil.FONT_CENTER_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 18, iRow, getAdvisorIconSortKey(iTheirLeader + 1, iRow), gc.getLeaderHeadInfo(iTheirLeader).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iTheirLeader, 1, CvUtil.FONT_CENTER_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 19, iRow, str(iTheirPlayer), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableIntLabel(screen, self.BATTLE_TABLE_ID, 20, iRow, self.getBattleCaptureCountText(iCapturedCount), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, 21, iRow, getAdvisorIconSortKey(iCapturedUnit + 1, iRow), self.getBattleCaptureUnitButton(iCapturedCount, iCapturedUnit), eCapturedUnitWidget, iCapturedUnit, -1, CvUtil.FONT_CENTER_JUSTIFY)
		if self.IS_SAS_CV_MILITARY_ADVISOR_BATTLE_PLOT_CONTEXT_ENABLE:
			self.setBattleHillPeakCell(screen, iRow, iHillPeakTerrain)
			self.setBattleTerrainFeatureCell(screen, iRow, self.BATTLE_TERRAIN_COL_ID, iTerrain, True)
			self.setBattleTerrainFeatureCell(screen, iRow, self.BATTLE_FEATURE_COL_ID, iFeature, False)
		SASTextScale.setTableTextLabel(screen, self.BATTLE_TABLE_ID, self.BATTLE_PLOT_COL_ID, iRow, getAdvisorIconSortKey(iCityContext + 1, iRow), self.getBattlePlotButton(iCityContext), WidgetTypes.WIDGET_GENERAL, iX, iY, CvUtil.FONT_CENTER_JUSTIFY)

	def dbgLogBattleHistory(self):
		aEntries = SASBattleHistory.getEntriesForPlayer(self.iActivePlayer)
		if not aEntries:
			print("SAS_MILITARY_ADVISOR_BATTLE_HISTORY_EMPTY")
			return
		print("SAS_MILITARY_ADVISOR_BATTLE_HISTORY_BEGIN")
		self.dbgLogBattleHistoryPerspectivePlayer()
		self.dbgLogBattleHistoryPlayers(aEntries)
		# <!-- custom: keep stored hill/peak, terrain, and feature context in copied logs even when the optional UI columns are hidden; logs are allowed to be more complete than the visible table when data already exists. (GPT-5.5) -->
		print("Turn | Year | Result | Est% | Role | OurStrB | OurStrS | OurStrE | OurStrM | OurXP | OurGG | OurUnit | TheirUnit | TheirXP | TheirGG | TheirStrB | TheirStrS | TheirStrE | TheirStrM | TheirPID | Cap# | CapUnit | HillPeak | Terrain | Feature | X | Y")
		for entry in aEntries:
			tColumns = self.getBattlePerspectiveColumns(entry)
			if tColumns is None:
				continue
			iTurn, iResult, _, iOurRole, iOurUnit, iOurCurrStr, iOurEndStr, iOurMaxStr, iOurXP, bOurGG, iTheirPlayer, iTheirUnit, iTheirCurrStr, iTheirEndStr, iTheirMaxStr, iTheirXP, bTheirGG, iX, iY, iCapturedCount, iCapturedUnit, iTerrain, iFeature, iHillPeakTerrain, iCityContext = tColumns
			print("%d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %s | %s | %s | %d | %s | %s | %s | %s | %d | %d | %s | %s | %s | %s | %d | %d" % (
				iTurn,
				self.getTurnDate(iTurn),
				self.getBattleResultLogText(iResult),
				self.getBattleEstimatedOddsText(iOurCurrStr, iTheirCurrStr),
				self.getBattleRoleText(iOurRole),
				self.getBattleBaseStrengthText(iOurUnit),
				self.getBattleStoredStrengthText(iOurCurrStr),
				self.getBattleStoredStrengthText(iOurEndStr),
				self.getBattleStoredStrengthText(iOurMaxStr),
				self.getBattleXPText(iOurXP, False),
				bOurGG,
				gc.getUnitInfo(iOurUnit).getDescription(),
				gc.getUnitInfo(iTheirUnit).getDescription(),
				self.getBattleXPText(iTheirXP, False),
				bTheirGG,
				self.getBattleBaseStrengthText(iTheirUnit),
				self.getBattleStoredStrengthText(iTheirCurrStr),
				self.getBattleStoredStrengthText(iTheirEndStr),
				self.getBattleStoredStrengthText(iTheirMaxStr),
				iTheirPlayer,
				iCapturedCount,
				self.getBattleCaptureUnitText(iCapturedCount, iCapturedUnit),
				self.getBattleTerrainTypeText(iHillPeakTerrain),
				self.getBattleTerrainTypeText(iTerrain),
				self.getBattleFeatureTypeText(iFeature),
				iX,
				iY,
			))
		print("SAS_MILITARY_ADVISOR_BATTLE_HISTORY_END")

	def dbgLogBattleHistoryPerspectivePlayer(self):
		kPlayer = gc.getPlayer(self.iActivePlayer)
		szLeaderType = gc.getLeaderHeadInfo(kPlayer.getLeaderType()).getType()
		szCivType = gc.getCivilizationInfo(kPlayer.getCivilizationType()).getType()
		print("PerspectivePlayer: %d | %s | %s | %s" % (self.iActivePlayer, kPlayer.getName(), szLeaderType, szCivType))

	def dbgLogBattleHistoryPlayers(self, aEntries):
		# <!-- custom: Battles rows are relative to the inspected player, so UI omits our repeated civ/leader/PID; the log prints perspective once and keeps a compact opponent PID legend for copied logs with duplicate leaders/civs. (GPT-5.5) -->
		aiPlayers = []
		for entry in aEntries:
			tColumns = self.getBattlePerspectiveColumns(entry)
			if tColumns is None:
				continue
			iTheirPlayer = tColumns[8]
			if iTheirPlayer not in aiPlayers:
				aiPlayers.append(iTheirPlayer)
		aiPlayers.sort()
		print("OpponentPlayers: PID | PlayerName | LeaderType | CivType")
		for iPlayer in aiPlayers:
			kPlayer = gc.getPlayer(iPlayer)
			szLeaderType = gc.getLeaderHeadInfo(kPlayer.getLeaderType()).getType()
			szCivType = gc.getCivilizationInfo(kPlayer.getCivilizationType()).getType()
			print("OpponentPlayer: %d | %s | %s | %s" % (iPlayer, kPlayer.getName(), szLeaderType, szCivType))
		
	def drawCombatExperience(self):
		if self.iActivePage != self.PAGE_UNITS:
			return
		# <!-- custom: hoist repeated active-player/threshold lookups to locals for this draw pass (same behavior, fewer repeated engine calls). (GPT-5.3-Codex) -->
		kActivePlayer = gc.getPlayer(self.iActivePlayer)
		iGreatPeopleThreshold = kActivePlayer.greatPeopleThreshold(true)
		if iGreatPeopleThreshold > 0:
			iExperience = kActivePlayer.getCombatExperience()

			screen = self.getScreen()
			screen.addStackedBarGFC(self.GREAT_GENERAL_BAR_ID, self.X_GREAT_GENERAL_BAR, self.Y_GREAT_GENERAL_BAR, self.W_GREAT_GENERAL_BAR, self.H_GREAT_GENERAL_BAR, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, self.COLOR_GREAT_PEOPLE_STORED)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE, self.COLOR_GREAT_PEOPLE_RATE)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE_EXTRA, self.COLOR_EMPTY)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_EMPTY, self.COLOR_EMPTY)
			screen.setBarPercentage(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, float(iExperience) / float(iGreatPeopleThreshold))
			screen.setLabel(self.GREAT_GENERAL_LABEL_ID, "", sasFontTagLabel + self.TEXT_COMBAT_EXPERIENCE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_GREAT_GENERAL_BAR + self.W_GREAT_GENERAL_BAR/2, self.Y_GREAT_GENERAL_BAR + 6, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1)
					
																									
	# returns a unique ID for a widget in this screen
	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName
																	
	def resetMinimapColor(self):
		screen = self.getScreen()
		for iX in range(gc.getMap().getGridWidth()):
			for iY in range(gc.getMap().getGridHeight()):
				screen.setMinimapColor(MinimapModeTypes.MINIMAPMODE_MILITARY, iX, iY, -1, 0.6)

	def getBattlePlotFromInput(self, inputClass):
		# <!-- custom: prefer the row cache because table cell data1/data2 can empirically arrive as valid-looking default map-corner coordinates (e.g. 0,0), making the camera jump to a corner instead of the battle plot. (GPT-5.5) -->
		if inputClass.getData() in self.BATTLE_ROW_PLOTS:
			return self.BATTLE_ROW_PLOTS[inputClass.getData()]
		iX = inputClass.getData1()
		iY = inputClass.getData2()
		if 0 <= iX < CyMap().getGridWidth() and 0 <= iY < CyMap().getGridHeight():
			return (iX, iY)
		return self.BATTLE_ROW_PLOTS.get(inputClass.getData(), (-1, -1))
																				
	# handle the input for this screen...
	def handleInput (self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED and inputClass.getFunctionName() == self.DEBUG_DROPDOWN_ID:
			self.iActivePlayer = getAdvisorDebugDropdownSelectedPlayer(self.getScreen(), self.DEBUG_DROPDOWN_ID)
			self.hideScreen()
			self.interfaceScreen()
			return 1
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getFunctionName() == self.BATTLE_LOG_BUTTON_ID:
			self.dbgLogBattleHistory()
			return 1
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED and inputClass.getFunctionName() == self.BATTLE_TABLE_ID and inputClass.getMouseX() == self.BATTLE_PLOT_COL_ID:
			iX, iY = self.getBattlePlotFromInput(inputClass)
			if iX >= 0 and iY >= 0:
				self.hideScreen()
				CyCamera().JustLookAtPlot(CyMap().plot(iX, iY))
			return 1
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getButtonType() == WidgetTypes.WIDGET_GENERAL:
			iPage = inputClass.getData1()
			if iPage in self.PAGE_IDS and iPage != self.iActivePage:
				self.iActivePage = iPage
				self.hideScreen()
				self.interfaceScreen()
				return 1
		if ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getFunctionName() == self.UNIT_BUTTON_ID) :
			self.bUnitDetails = not self.bUnitDetails
			self.refreshUnitSelection(True)
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_LSHIFT) or inputClass.getData() == int(InputTypes.KB_RSHIFT)):
				self.iShiftKeyDown = inputClass.getID() 
		
		return 0

	def update(self, fDelta):
		if self.iActivePage != self.PAGE_UNITS:
			return
		screen = self.getScreen()
		screen.updateMinimap(fDelta)

	def minimapClicked(self):
		self.hideScreen()
						
	def isSelectedGroup(self, iGroup, bIndirect):
		if (bIndirect):
			if -1 in self.selectedGroupList:
				return True
			if iGroup == -1:
				return False
		return ((iGroup + gc.getNumUnitInfos()) in self.selectedGroupList)
				
	def isSelectedUnitType(self, iUnit, bIndirect):
		if (bIndirect):
			if -1 in self.selectedGroupList:
				return True
			if self.isSelectedGroup(gc.getUnitInfo(iUnit).getUnitCombatType(), True):
				return True
		return (iUnit in self.selectedGroupList)
		
	def isSelectedUnit(self, iPlayer, iUnitId, bIndirect):
		if (bIndirect):
			if -1 in self.selectedGroupList:
				return True
			unit = gc.getPlayer(iPlayer).getUnit(iUnitId)
			if self.isSelectedGroup(gc.getUnitInfo(unit.getUnitType()).getUnitCombatType(), True):
				return True
			if self.isSelectedUnitType(unit.getUnitType(), True):
				return True
		return ((iPlayer, iUnitId) in self.selectedUnitList)
		
	def refreshSelectedLeader(self, iPlayer):
		if self.iActivePage != self.PAGE_UNITS:
			return
		if self.iShiftKeyDown == 1:
			if (iPlayer in self.selectedPlayerList):
				self.selectedPlayerList.remove(iPlayer)
			else:
				self.selectedPlayerList.append(iPlayer)
		else:
			self.selectedPlayerList = []
			self.selectedPlayerList.append(iPlayer)	
	
		self.refresh(True)
				
	def getLeaderButton(self, iPlayer):
		szName = self.LEADER_BUTTON_ID + str(iPlayer)
		return szName

	def refreshSelectedGroup(self, iSelected):
		if self.iActivePage != self.PAGE_UNITS:
			return
		if (iSelected in self.selectedGroupList):
			self.selectedGroupList.remove(iSelected)
		else:
			self.selectedGroupList.append(iSelected)
		self.refreshUnitSelection(false)
			
	def refreshSelectedUnit(self, iPlayer, iUnitId):
		if self.iActivePage != self.PAGE_UNITS:
			return
		selectedUnit = (iPlayer, iUnitId)
		if (selectedUnit in self.selectedUnitList):
			self.selectedUnitList.remove(selectedUnit)
		else:
			self.selectedUnitList.append(selectedUnit)
		self.refreshUnitSelection(false)		
	
	# <!-- custom: refactor refreshUnitSelection to reduce redundancy while preserving behavior. Credit: ChatGPT 5.2; Gemini 3 Pro review. (GPT-5.2-Codex (summarized)) -->
	# <!-- custom: add icon overlays on listbox rows with indent. Credit: Claude Opus 4.5. (GPT-5.2-Codex (summarized)) -->
	def refreshUnitSelection(self, bReload):
		screen = self.getScreen()

		screen.minimapClearAllFlashingTiles()

		iNumUnitInfos = gc.getNumUnitInfos()
		# <!-- custom: hoist active-player/team lookups used across loops in this refresh pass to avoid repeated accessor calls. (GPT-5.3-Codex) -->
		kActivePlayer = gc.getPlayer(self.iActivePlayer)
		iActiveTeam = kActivePlayer.getTeam()

		if (bReload):
			if (self.bUnitDetails):
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_MINUS
				szButtonText = self.TEXT_UNIT_TOGGLE_OFF
			else:
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_PLUS
				szButtonText = self.TEXT_UNIT_TOGGLE_ON
			screen.setButtonGFC(self.UNIT_BUTTON_ID, u"", "", self.X_TEXT + self.MAP_MARGIN, self.Y_TEXT + self.MAP_MARGIN/2, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle )
			screen.setLabel(self.UNIT_BUTTON_LABEL_ID, "", sasFontTagLabel + szButtonText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.X_TEXT + self.MAP_MARGIN + 22, self.Y_TEXT + self.MAP_MARGIN/2 + 2, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# self.unitsList[iUnit][0] is the UnitCombatGroup (e.g. Melee)
		# self.unitsList[iUnit][1] is the unit type (e.g. Warrior)
		# self.unitsList[iUnit][2] is a list of the active player's actual units
		# self.unitsList[iUnit][3] is the total number of those units seen by the active player (not only his own)
		
		iColorYellow = self.COLOR_YELLOW
		iColorRed = self.COLOR_RED
		iColorWhite = self.COLOR_WHITE
		iWidget = WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT
		iFont = CvUtil.FONT_LEFT_JUSTIFY

		# <!-- custom: render icons inline in list rows so icon/text stay aligned while scrolling; this replaces the old overlay-button workaround that did not scroll with rows. (GPT-5.3-Codex) -->
		iListX = self.X_TEXT + self.MAP_MARGIN
		iListY = self.Y_TEXT + self.MAP_MARGIN + 15
		iListW = self.W_TEXT - 2*self.MAP_MARGIN
		iListH = self.H_TEXT - 2*self.MAP_MARGIN - 15
		# Extra text-indent is only needed when icons are disabled.
		szUnitIndentSpace = u"  "  # <!-- custom: level 1: unit-type rows (e.g. Warrior (3)) (GPT-5.3-Codex) -->
		szDetailIndentSpace = u"      "  # <!-- custom: level 2: individual unit detail rows (expanded view) (GPT-5.3-Codex) -->
		if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS:
			# <!-- custom: with inline icons enabled, remove legacy text-side indents so icon indent/gap can be tuned independently; otherwise icon-indent edits would drag icon and text together.
			# This notably lets us keep unit icons close to unit text for readability instead of forcing a wide icon->text gap. (GPT-5.3-Codex) -->
			szUnitIndentSpace = u" "
			szDetailIndentSpace = u""
		# <!-- custom: per-level icon spacing. Level meaning:
		# 0 = unit-combat group header rows (e.g. MELEE),
		# 1 = unit-type rows (e.g. Warrior (3)),
		# 2 = individual unit detail rows (when details are expanded).
		# Combat headers stay left with a bit more icon->text gap; unit/detail rows are pushed right and kept closer to their text for faster scanning. (GPT-5.3-Codex) -->
		szIconIndentByLevel = {
			0: u"",
			1: u"    ",
			2: u"        ",
		}
		szIconGapByLevel = {
			0: u"  ",
			1: u"",
			2: u" ",
		}

		def formatListRowText(szText, szButton, iIndentLevel):
			szLabelText = sasFontTagLabel + szText + SAS_FONT_TAG_CLOSE
			if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS and szButton:
				# <!-- custom: note: inline <img> icon paths are stricter than icon-slot rendering; avoid risky button filenames (spaces/parentheses) to prevent magenta icons. See KI#118. (GPT-5.3-Codex) -->
				return u"%s<img=%s size=%d></img>%s%s" % (
					szIconIndentByLevel.get(iIndentLevel, u""),
					szButton,
					self.iInlineIconSize,
					szIconGapByLevel.get(iIndentLevel, u" "),
					szLabelText,
				)
			return szLabelText

		if (bReload):
			def addUnitListRow(iIndex, szText, iData1, iData2, szButton, iIndentLevel):
				screen.appendListBoxString(self.UNIT_LIST_ID, formatListRowText(szText, szButton, iIndentLevel), iWidget, iData1, iData2, iFont)
				return iIndex + 1
		else:
			def addUnitListRow(iIndex, szText, iData1, iData2, szButton, iIndentLevel):
				screen.setListBoxStringGFC(self.UNIT_LIST_ID, iIndex, formatListRowText(szText, szButton, iIndentLevel), iWidget, iData1, iData2, iFont)
				return iIndex + 1

		def formatSelection(szIndent, szText, bUnderline, bYellow):
			if (bUnderline):
				szText = szIndent + u"<u>" + szText + u"</u>"
			else:
				szText = szIndent + szText
			if (bYellow):
				szText = localText.changeTextColor(szText, iColorYellow)
			return szText

		if bReload:
			for iUnit in range(iNumUnitInfos):
				kUnitInfo = gc.getUnitInfo(iUnit)
				self.unitsList[iUnit] = (kUnitInfo.getUnitCombatType(), iUnit, [], 0)

			for iPlayer in range(gc.getMAX_PLAYERS()):			
				player = PyPlayer(iPlayer)
				if (player.isAlive()):
					unitList = player.getUnitList()
					for loopUnit in unitList:
						unitType = loopUnit.getUnitType()
						
						bVisible = False
						plot = loopUnit.plot()
						if (not plot.isNone()):
							# advc.007: bDebug=True in isVisible and isInvisible call
							bVisible = plot.isVisible(iActiveTeam, True) and not loopUnit.isInvisible(iActiveTeam, True)

						if unitType >= 0 and unitType < iNumUnitInfos and bVisible:
							iNumUnits = self.unitsList[unitType][3]
							if (iPlayer == self.iActivePlayer):
								iNumUnits += 1
							if loopUnit.getVisualOwner() in self.selectedPlayerList:
								self.unitsList[unitType][2].append(loopUnit)							
							
							self.unitsList[unitType] = (self.unitsList[unitType][0], self.unitsList[unitType][1], self.unitsList[unitType][2], iNumUnits)

			# sort by unit combat type
			self.unitsList.sort()
		
		szText = self.TEXT_ALL_UNITS
		bAllSelected = (-1 in self.selectedGroupList)
		szText = formatSelection(u"", szText, bAllSelected, bAllSelected)
		if (bReload):
			screen.addListBoxGFC(self.UNIT_LIST_ID, "", iListX, iListY, iListW, iListH, TableStyles.TABLE_STYLE_STANDARD)
			screen.enableSelect(self.UNIT_LIST_ID, False)
			screen.setStyle(self.UNIT_LIST_ID, "Table_StandardCiv_Style")
		
		iPrevUnitCombat = -2
		iItem = addUnitListRow(0, szText, 1, -1, "", 0)

		dPrimaryColor = {}
		dPyPlayer = {}
		dTeamId = {}

		for iUnit in range(iNumUnitInfos):
			if (len(self.unitsList[iUnit][2]) > 0):
				if (iPrevUnitCombat != self.unitsList[iUnit][0] and self.unitsList[iUnit][0] != -1):
					iPrevUnitCombat = self.unitsList[iUnit][0]
					szDescription = gc.getUnitCombatInfo(self.unitsList[iUnit][0]).getDescription().upper()
					szCombatButton = gc.getUnitCombatInfo(self.unitsList[iUnit][0]).getButton()
					szDescription = formatSelection(u"", szDescription, self.isSelectedGroup(self.unitsList[iUnit][0], False), self.isSelectedGroup(self.unitsList[iUnit][0], True))
					iItem = addUnitListRow(iItem, szDescription, 1, self.unitsList[iUnit][0] + iNumUnitInfos, szCombatButton, 0)
				
				kUnitInfo = gc.getUnitInfo(self.unitsList[iUnit][1])
				szDescription = kUnitInfo.getDescription() + u" (" + unicode(len(self.unitsList[iUnit][2])) + u")"
				szUnitButton = kUnitInfo.getButton()
				szDescription = formatSelection(szUnitIndentSpace, szDescription, self.isSelectedUnitType(self.unitsList[iUnit][1], False), self.isSelectedUnitType(self.unitsList[iUnit][1], True))
				iItem = addUnitListRow(iItem, szDescription, 1, self.unitsList[iUnit][1], szUnitButton, 1)
				
				for loopUnit in self.unitsList[iUnit][2]:
				
					if (self.bUnitDetails):
						szDescription = CyGameTextMgr().getSpecificUnitHelp(loopUnit, true, false)

						listMatches = re.findall("<.*?color.*?>", szDescription)	
						for szMatch in listMatches:
							szDescription = szDescription.replace(szMatch, u"")
						
						if (loopUnit.isWaiting()):
							szDescription = '*' + szDescription
						
						szDescription = formatSelection(szDetailIndentSpace, szDescription, self.isSelectedUnit(loopUnit.getOwner(), loopUnit.getID(), False), self.isSelectedUnit(loopUnit.getOwner(), loopUnit.getID(), True))
						szUnitButton = gc.getUnitInfo(loopUnit.getUnitType()).getButton()
						iItem = addUnitListRow(iItem, szDescription, -loopUnit.getOwner(), loopUnit.getID(), szUnitButton, 2)

					iPlayer = loopUnit.getVisualOwner()
					if (iPlayer not in dPyPlayer):
						dPyPlayer[iPlayer] = PyPlayer(iPlayer)
					player = dPyPlayer[iPlayer]
					if (iPlayer not in dPrimaryColor):
						dPrimaryColor[iPlayer] = gc.getPlayerColorInfo(gc.getPlayer(iPlayer).getPlayerColor()).getColorTypePrimary()
					iColor = dPrimaryColor[iPlayer]
					screen.setMinimapColor(MinimapModeTypes.MINIMAPMODE_MILITARY, loopUnit.getX(), loopUnit.getY(), iColor, 0.6)
					if (self.isSelectedUnit(loopUnit.getOwner(), loopUnit.getID(), True) and (iPlayer in self.selectedPlayerList)):
						if (player.getTeam().isAtWar(iActiveTeam)):
							iFlashColor = iColorRed
						else:
							if (iPlayer not in dTeamId):
								dTeamId[iPlayer] = gc.getPlayer(iPlayer).getTeam()
							if (dTeamId[iPlayer] != iActiveTeam):
								iFlashColor = iColorYellow
							else:
								iFlashColor = iColorWhite
						screen.minimapFlashPlot(loopUnit.getX(), loopUnit.getY(), iFlashColor, -1)

	def refresh(self, bReload):

		if (self.iActivePlayer < 0):
			return

		screen = self.getScreen()
		# <!-- custom: hoist values reused by the leader loop (team/debug) so we don't repeat gc lookups per iteration. (GPT-5.3-Codex) -->
		kActivePlayer = gc.getPlayer(self.iActivePlayer)
		iActiveTeam = kActivePlayer.getTeam()
		bDebugMode = gc.getGame().isDebugMode()

		if (bReload):
			# Set scrollable area for unit buttons
			screen.addPanel(self.UNIT_PANEL_ID, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_MAIN)
			
			# Set scrollable area for leaders
			screen.addPanel(self.LEADER_PANEL_ID, "", "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_MAIN)

		listLeaders = []
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iLoopPlayer)
			if player.isAlive() and (gc.getTeam(player.getTeam()).isHasMet(iActiveTeam) or bDebugMode):
				listLeaders.append(iLoopPlayer)
				
		iNumLeaders = len(listLeaders)
		if iNumLeaders >= self.LEADER_COLUMNS:
			iButtonSize = self.LEADER_BUTTON_SIZE / 2
		else:
			iButtonSize = self.LEADER_BUTTON_SIZE

		iColumns = int(self.W_LEADERS / (iButtonSize + self.LEADER_MARGIN))

		# loop through all players and display leaderheads
		for iIndex in range(iNumLeaders):
			iLoopPlayer = listLeaders[iIndex]
			player = gc.getPlayer(iLoopPlayer)
			
			x = self.X_LEADERS + self.LEADER_MARGIN + (iIndex % iColumns) * (iButtonSize + self.LEADER_MARGIN)
			y = self.Y_LEADERS + self.LEADER_MARGIN + (iIndex // iColumns) * (iButtonSize + self.LEADER_MARGIN)

			if (bReload):
				if player.isBarbarian():
					# <!-- custom: read the Barbarian button path from CIV4ArtDefines_Civilization.xml instead of hardcoding "Art/Interface/Buttons/Civilizations/Barbarian.dds". (Claude code Opus 4.7) -->
					szButton = gc.getCivilizationInfo(player.getCivilizationType()).getButton()
				else:
					szButton = gc.getLeaderHeadInfo(gc.getPlayer(iLoopPlayer).getLeaderType()).getButton()
				screen.addCheckBoxGFC(self.getLeaderButton(iLoopPlayer), szButton, self.ART_BUTTON_HILITE_SQUARE, x, y, iButtonSize, iButtonSize, WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT, 2, iLoopPlayer, ButtonStyles.BUTTON_STYLE_LABEL)
				screen.setState(self.getLeaderButton(iLoopPlayer), (iLoopPlayer in self.selectedPlayerList))				
		
		self.refreshUnitSelection(bReload)
