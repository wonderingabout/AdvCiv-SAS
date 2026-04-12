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
from SASFontUtils import *

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

		self.Z_BACKGROUND = -2.1
		self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
		self.DZ = -0.2

		# <!-- custom: expand the screen like Foreign Advisor/Sevopedia so crowded player lists require less scrolling. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.2-Codex (summarized)) -->
		# self.X_SCREEN = 500
		# self.Y_SCREEN = 396
		# self.W_SCREEN = 1024
		# self.H_SCREEN = 768
		# <!-- custom: screen isn't available in __init__ (unlike CvTechChooser); using hardcoded 1920x1080 avoids crashes, but verify on other resolutions. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		xHardcodedResolution = 1920
		yHardcodedResolution = 1080

		# <!-- custom: keep the panel uncentered so the right side (scoreboard/map) stays visible; left panel is less important. (GPT-5.2-Codex (summarized)) -->

		wLeftSpaceForCommerceSliders = 172
		self.X_SCREEN = wLeftSpaceForCommerceSliders
		# <!-- custom: preserve right-side scoreboard/map while letting the left side be tighter. (GPT-5.2-Codex (summarized)) -->
		wRightSpaceForScoreBoard = 390
		self.W_SCREEN = xHardcodedResolution - wRightSpaceForScoreBoard - wLeftSpaceForCommerceSliders

		hTopSpaceForTechBar = 28
		self.Y_SCREEN = hTopSpaceForTechBar
		hBottomSpace = 0
		# <!-- custom: compute remaining height so the panel fits to the bottom edge. (GPT-5.2-Codex (summarized)) -->
		self.H_SCREEN = yHardcodedResolution - hTopSpaceForTechBar - hBottomSpace

		# <!-- custom: add X_TITLE so the title can be centered after resizing. (GPT-5.2-Codex (summarized)) -->
		# screen.setText(self.szHeader, "Background", self.TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		# <!-- custom: X_TITLE is relative to the screen's X origin, not the window edge. (GPT-5.2-Codex (summarized)) -->
		self.X_TITLE = self.W_SCREEN / 2
		self.Y_TITLE = 8

		self.BORDER_WIDTH = 4
		self.W_HELP_AREA = 200

		# <!-- custom: reposition the exit button based on the new screen size. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		# self.X_EXIT = 994
		# self.Y_EXIT = 726
		# Exit Button (Bottom Right)
		self.X_EXIT = self.W_SCREEN - 30
		self.Y_EXIT = self.H_SCREEN - 42
						
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
		# self.W_LEADERS = 985
		self.W_LEADERS = self.W_SCREEN - self.SIDE_MARGIN
		self.H_LEADERS = 90
		self.LEADER_BUTTON_SIZE = 64
		self.LEADER_MARGIN = 12
		
		self.LEADER_COLUMNS = int(self.W_LEADERS / (self.LEADER_BUTTON_SIZE + self.LEADER_MARGIN))
		self.bUnitDetails = False
		self.iShiftKeyDown = 0

		# --- B. Unit List (Right Side - Fixed Width) ---
		# self.X_TEXT = 625
		# self.Y_TEXT = 190
		# self.W_TEXT = 380
		# self.H_TEXT = 500
		self.W_TEXT = 430  
		self.X_TEXT = self.W_SCREEN - 20 - self.W_TEXT
		self.Y_TEXT = self.Y_LEADERS + self.H_LEADERS + 15
		# Height = Screen Height - Start Y - Bottom Panel (55) - Margin (15)
		self.H_TEXT = self.H_SCREEN - self.Y_TEXT - 55 - 15

		# --- C. Map Panel (Left Side - Fills Remaining Space) ---
		self.X_MAP = 20
		# self.Y_MAP = 190
		# self.W_MAP = 580
		# self.H_MAP_MAX = 500
		self.Y_MAP = self.Y_LEADERS + self.H_LEADERS + 15
		# Map takes available width minus the text panel and a gap
		self.W_MAP = self.X_TEXT - self.X_MAP - 14
		# <!-- custom: MAP_MARGIN refers to the panel border wrap, not an empty margin. (GPT-5.2-Codex (summarized)) -->
		self.MAP_MARGIN = 20

		# --- D. Great General Bar (Moved to Bottom Left)
		# self.X_GREAT_GENERAL_BAR = 20
		# self.Y_GREAT_GENERAL_BAR = 730
		# self.W_GREAT_GENERAL_BAR = 300
		# self.H_GREAT_GENERAL_BAR = 30
		self.W_GREAT_GENERAL_BAR = self.W_MAP
		self.H_GREAT_GENERAL_BAR = 30
		self.X_GREAT_GENERAL_BAR = 20
		# Position: Screen Height - Bottom Panel - Bar Height - Padding
		self.Y_GREAT_GENERAL_BAR = self.H_SCREEN - 55 - self.H_GREAT_GENERAL_BAR - 15
		self.H_MAP_MAX = self.Y_GREAT_GENERAL_BAR - 10 - self.Y_MAP

		# <!-- custom: cache the define lookup once. (GPT-5.2-Codex (summarized)). Note: done here rather than in init since it doesn't work in many ingame py file (tech chooser, main interface for those i tried), so use safer pattern reliably rather -->
		self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS = (gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS") > 0)
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE")
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT")
		self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES = gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES")


	def initText(self):
		# <!-- custom: cache Military Advisor language-dependent text and deterministic art/color lookups once to avoid repeated calls on refresh paths. (GPT-5.3-Codex) -->
		if not CyGame().isFinalInitialized():
			return
		if self.iLanguageLoaded == CyGame().getCurrentLanguage():
			return
		self.iLanguageLoaded = CyGame().getCurrentLanguage()
		self.EXIT_TEXT = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TITLE = SAS_FONT_TAG_TITLE_BOLD + localText.getText("TXT_KEY_MILITARY_ADVISOR_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE
		self.TEXT_COMBAT_EXPERIENCE = localText.getText("TXT_KEY_MISC_COMBAT_EXPERIENCE", ())
		self.TEXT_ALL_UNITS = localText.getText("TXT_KEY_PEDIA_ALL_UNITS", ()).upper()
		self.TEXT_UNIT_TOGGLE_ON = localText.getText("TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_ON", ())
		self.TEXT_UNIT_TOGGLE_OFF = localText.getText("TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_OFF", ())
		self.ART_MAINMENU_SLIDESHOW_LOAD = ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath()
		self.ART_BUTTON_HILITE_SQUARE = ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath()
		self.COLOR_YELLOW = gc.getInfoTypeForString("COLOR_YELLOW")
		self.COLOR_RED = gc.getInfoTypeForString("COLOR_RED")
		self.COLOR_WHITE = gc.getInfoTypeForString("COLOR_WHITE")
		self.COLOR_GREAT_PEOPLE_STORED = gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_STORED")
		self.COLOR_GREAT_PEOPLE_RATE = gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_RATE")
		self.COLOR_EMPTY = gc.getInfoTypeForString("COLOR_EMPTY")


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

		self.initText()

		self.nWidgetCount = 0
	
		# Set the background and exit button, and show the screen
		# <!-- custom: resize the window (see also CvForeignAdvisor); centering was reverted. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.2-Codex (summarized)) -->
		#screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		# <!-- custom: unlike Foreign Advisor, we must set X/Y directly or the screen stays centered. Credit: Gemini 3 Pro. (GPT-5.2-Codex (summarized)) -->
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		screen.addDDSGFC(self.BACKGROUND_ID, self.ART_MAINMENU_SLIDESHOW_LOAD, 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# <!-- custom: update panel positions to match the expanded screen size. Credit: Gemini 3 Pro; Claude Sonnet 4.5 review. (GPT-5.2-Codex (summarized)) -->
		# Top panels cutting off content: The TopPanel and BottomPanel are positioned at y=0 and y=713 respectively. These need updating:
		# screen.addPanel( "TechTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		# screen.addPanel( "TechBottomPanel", u"", u"", True, False, 0, 713, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, self.H_SCREEN - 55, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )

		screen.showWindowBackground(False)
		screen.setText(self.EXIT_ID, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
												
		# Header...
		self.szHeader = self.getNextWidgetName()
		screen.setText(self.szHeader, "Background", self.TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
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
	
		self.iActivePlayer = gc.getGame().getActivePlayer()

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
		
	def drawCombatExperience(self):
	
		if (gc.getPlayer(self.iActivePlayer).greatPeopleThreshold(true) > 0):
		
			iExperience = gc.getPlayer(self.iActivePlayer).getCombatExperience()
			
			screen = self.getScreen()
			screen.addStackedBarGFC(self.GREAT_GENERAL_BAR_ID, self.X_GREAT_GENERAL_BAR, self.Y_GREAT_GENERAL_BAR, self.W_GREAT_GENERAL_BAR, self.H_GREAT_GENERAL_BAR, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, self.COLOR_GREAT_PEOPLE_STORED)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE, self.COLOR_GREAT_PEOPLE_RATE)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE_EXTRA, self.COLOR_EMPTY)
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_EMPTY, self.COLOR_EMPTY)
			screen.setBarPercentage(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, float(iExperience) / float(gc.getPlayer(self.iActivePlayer).greatPeopleThreshold(true)))
			screen.setLabel(self.GREAT_GENERAL_LABEL_ID, "", SAS_FONT_TAG_LABEL + self.TEXT_COMBAT_EXPERIENCE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, self.X_GREAT_GENERAL_BAR + self.W_GREAT_GENERAL_BAR/2, self.Y_GREAT_GENERAL_BAR + 6, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1)
					
																									
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
																				
	# handle the input for this screen...
	def handleInput (self, inputClass):
		if ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getFunctionName() == self.UNIT_BUTTON_ID) :
			self.bUnitDetails = not self.bUnitDetails
			self.refreshUnitSelection(True)
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_LSHIFT) or inputClass.getData() == int(InputTypes.KB_RSHIFT)):
				self.iShiftKeyDown = inputClass.getID() 
		
		return 0

	def update(self, fDelta):
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
		if (iSelected in self.selectedGroupList):
			self.selectedGroupList.remove(iSelected)
		else:
			self.selectedGroupList.append(iSelected)
		self.refreshUnitSelection(false)
			
	def refreshSelectedUnit(self, iPlayer, iUnitId):
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
		iActiveTeam = gc.getPlayer(self.iActivePlayer).getTeam()

		if (bReload):
			if (self.bUnitDetails):
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_MINUS
				szButtonText = self.TEXT_UNIT_TOGGLE_OFF
			else:
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_PLUS
				szButtonText = self.TEXT_UNIT_TOGGLE_ON
			screen.setButtonGFC(self.UNIT_BUTTON_ID, u"", "", self.X_TEXT + self.MAP_MARGIN, self.Y_TEXT + self.MAP_MARGIN/2, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle )
			screen.setLabel(self.UNIT_BUTTON_LABEL_ID, "", SAS_FONT_TAG_LABEL + szButtonText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, self.X_TEXT + self.MAP_MARGIN + 22, self.Y_TEXT + self.MAP_MARGIN/2 + 2, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

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
		# <!-- custom: use screen-height threshold (vertical room) for larger inline icons on high resolutions (e.g. 1440p+). (GPT-5.3-Codex) -->
		iInlineIconSize = self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_BASE
		if self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT > 0 and screen.getYResolution() >= self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_HIGH_RES_MIN_HEIGHT:
			iInlineIconSize = self.iSAS_CV_MILITARY_ADVISOR_INLINE_ICON_SIZE_HIGH_RES
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
			szLabelText = SAS_FONT_TAG_LABEL + szText + SAS_FONT_TAG_CLOSE
			if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_ICONS and szButton:
				# <!-- custom: note: inline <img> icon paths are stricter than icon-slot rendering; avoid risky button filenames (spaces/parentheses) to prevent magenta icons. See KI#118. (GPT-5.3-Codex) -->
				return u"%s<img=%s size=%d></img>%s%s" % (
					szIconIndentByLevel.get(iIndentLevel, u""),
					szButton,
					iInlineIconSize,
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
				self.unitsList[iUnit] = (gc.getUnitInfo(iUnit).getUnitCombatType(), iUnit, [], 0)

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
				
				szDescription = gc.getUnitInfo(self.unitsList[iUnit][1]).getDescription() + u" (" + unicode(len(self.unitsList[iUnit][2])) + u")"
				szUnitButton = gc.getUnitInfo(self.unitsList[iUnit][1]).getButton()
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
				
		if (bReload):
			# Set scrollable area for unit buttons
			screen.addPanel(self.UNIT_PANEL_ID, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_MAIN)
			
			# Set scrollable area for leaders
			screen.addPanel(self.LEADER_PANEL_ID, "", "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_MAIN)

		listLeaders = []
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iLoopPlayer)
			if (player.isAlive() and (gc.getTeam(player.getTeam()).isHasMet(gc.getPlayer(self.iActivePlayer).getTeam()) or gc.getGame().isDebugMode())):
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
					szButton = "Art/Interface/Buttons/Civilizations/Barbarian.dds"
				else:
					szButton = gc.getLeaderHeadInfo(gc.getPlayer(iLoopPlayer).getLeaderType()).getButton()
				screen.addCheckBoxGFC(self.getLeaderButton(iLoopPlayer), szButton, self.ART_BUTTON_HILITE_SQUARE, x, y, iButtonSize, iButtonSize, WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT, 2, iLoopPlayer, ButtonStyles.BUTTON_STYLE_LABEL)
				screen.setState(self.getLeaderButton(iLoopPlayer), (iLoopPlayer in self.selectedPlayerList))				
		
		self.refreshUnitSelection(bReload)
