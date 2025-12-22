## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import time
import PyHelpers
import re

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

		# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
		# self.X_SCREEN = 500
		# self.Y_SCREEN = 396
		# self.W_SCREEN = 1024
		# self.H_SCREEN = 768
		# <!-- custom: note: screen is not available at init it seems unlike in the way it is done as of now in CvTechChooser where self.X_SCREEN and such are initialized in interfaceScreen that already has a screen variable. I tried adding screen in init in the foreign advisor but it lead to crashes, so using hardcoded values of 1920 and 1080 to avoid that, and is done as per gemini 3 pro's recommendation as well (check if accurate especially as i don't know too much about these but it seems to be so empircially but check to be sure anyways etc.) -->
		xHardcodedResolution = 1920
		yHardcodedResolution = 1080

		# <!-- custom: deduce x position so that it is dynamically centered (note: manually making sure we see all right panel info including power ratios anyways etc.) -->
		# <!-- custom: update: we don't need to center here: for foreign relations, the right side with the scoreboard and map is more important to always look at ideally; as for the left panel, it is largely uneeded, so be uncentered to maximize screen usage while still trying to preserve the scoreboard display or/and such but anyways etc. -->

		wLeftSpaceForCommerceSliders = 172
		self.X_SCREEN = wLeftSpaceForCommerceSliders
		# <!-- custom: wide enough to preserve the right panel that has key foreign advisor info (scoreboard, map etc.), and less conservatively care about the left side so this size won't be centered but closer to the left as of now at least but anyways etc. -->
		wRightSpaceForScoreBoard = 390
		self.W_SCREEN = xHardcodedResolution - wRightSpaceForScoreBoard - wLeftSpaceForCommerceSliders

		hTopSpaceForTechBar = 28
		self.Y_SCREEN = hTopSpaceForTechBar
		hBottomSpace = 0
		# <!-- custom: if we start 100px from the top to see top info, then we can deduce the remaining height we can all allocate so panel fits precisely right at bottom (e.g. if resolution Y is 1080 then 1080 - 100 = 980). -->
		self.H_SCREEN = yHardcodedResolution - hTopSpaceForTechBar - hBottomSpace

		# <!-- custom: add new self.X_TITLE so we can properly center it or put it where we want in the X axis, after our changes the title is too much on the left side and not centered -->
		# screen.setText(self.szHeader, "Background", self.TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		# <!-- custom: add new self.X_TITLE so we can properly center it or put it where we want in the X axis, after our changes the title is too much on the left side and not centered. Note: this is starting from the screen's X edge, not from the window's edge anyways etc. -->
		self.X_TITLE = self.W_SCREEN / 2
		self.Y_TITLE = 8

		self.BORDER_WIDTH = 4
		self.W_HELP_AREA = 200

		# <!-- custom: now that we expanded the screen, move this to the bottom and make it dynamically follow / depend on the screen's size, as we did similarly for the legend in the foreign advisor's web's below corresponding legend but anyways etc; code added with the help of gemini 3 pro thanks anyways etc. -->
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

		# <!-- custom: now that we expanded the screen, move or/and adjust the size of the great general bar or other similar elements of the military advisor so they use more of the expanded space available, and so they dynamically follow / depend on the screen's size, as we did similarly for the legend in the foreign advisor's web's below corresponding legend but anyways etc; code added with the help of gemini 3 pro thanks anyways etc. -->
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
		self.H_MAP_MAX = self.H_TEXT
		# <!-- custom: renamed self.MAP_MARGIN to self.MAP_MARGIN_WRAP for clarity about the fact that this is the blue outside cover of the panel all around it, not an empty margin or something else anyways etc. -->
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

		self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_BUTTONS = None


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

		# <!-- custom: compute cheaply once if i am not mistaken that fetching the define once is cheaper but anyways etc. -->
		if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_BUTTONS is None:
			self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_BUTTONS = (gc.getDefineINT("SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_BUTTONS") > 0)

		self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>"
		self.TITLE = u"<font=4b>" + localText.getText("TXT_KEY_MILITARY_ADVISOR_TITLE", ()).upper() + "</font>"

		self.nWidgetCount = 0
	
		# Set the background and exit button, and show the screen
		# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
		# <!-- custom: see also related change that was needed it seems as well in CvExoticForeignAdvisor.py anyways etc. -->
		# <!-- custom: update: reverting this change we added, as it doesn't seem necessary for our change to still be effective anyways etc. -->
		#screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		# <!-- custom: here, in this code that reuses the foreign advisor changes, there is a difference, here it seems that we need to actually change the center settings else the screen stays at the center, and now changing it as as of now below we can freely move the military advisor screen around the window as we want anyways etc, as per a similar suggestion of gemini 3 pro thanks but anyways etc. -->
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		# <!-- custom: in the foreign advisor and similar screens, we can't see all info in one screen when there are too many players, yet the window does not use all the game window space. Make it larger, similarly to what we did for sevopedia anyways etc., so that we don't have to scroll or less so anyways etc. Code added with the help of gemini 3 pro and then fixed with claude sonnet 4.5's review thanks anyways etc.; check if accurate anyways etc. -->
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
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_STORED"))
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_RATE"))
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY"))
			screen.setStackedBarColors(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY"))
			screen.setBarPercentage(self.GREAT_GENERAL_BAR_ID, InfoBarTypes.INFOBAR_STORED, float(iExperience) / float(gc.getPlayer(self.iActivePlayer).greatPeopleThreshold(true)))
			screen.setLabel(self.GREAT_GENERAL_LABEL_ID, "", localText.getText("TXT_KEY_MISC_COMBAT_EXPERIENCE", ()), CvUtil.FONT_CENTER_JUSTIFY, self.X_GREAT_GENERAL_BAR + self.W_GREAT_GENERAL_BAR/2, self.Y_GREAT_GENERAL_BAR + 6, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1)
					
																									
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
	
	# <!-- custom: refactor old code for this function while preserving behaviour otherwise as it is, with the help of chatgpt 5.2 Old code was shit in terms of redundance or such, is much much cleaner although i didn't look in detail to tell. Reviewed by gemini 3 pro which confirms it is nice anyways etc. -->
	# <!-- custom: added icon buttons overlaid on listbox rows with indent - claude opus 4.5 -->
	def refreshUnitSelection(self, bReload):
		screen = self.getScreen()
		
		screen.minimapClearAllFlashingTiles()

		iNumUnitInfos = gc.getNumUnitInfos()
		iActiveTeam = gc.getPlayer(self.iActivePlayer).getTeam()

		if (bReload):
			if (self.bUnitDetails):
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_MINUS
				szButtonTextKey = "TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_OFF"
			else:
				iButtonStyle = ButtonStyles.BUTTON_STYLE_CITY_PLUS
				szButtonTextKey = "TXT_KEY_MILITARY_ADVISOR_UNIT_TOGGLE_ON"
			screen.setButtonGFC(self.UNIT_BUTTON_ID, u"", "", self.X_TEXT + self.MAP_MARGIN, self.Y_TEXT + self.MAP_MARGIN/2, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, iButtonStyle )
			screen.setLabel(self.UNIT_BUTTON_LABEL_ID, "", localText.getText(szButtonTextKey, ()), CvUtil.FONT_LEFT_JUSTIFY, self.X_TEXT + self.MAP_MARGIN + 22, self.Y_TEXT + self.MAP_MARGIN/2 + 2, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# self.unitsList[iUnit][0] is the UnitCombatGroup (e.g. Melee)
		# self.unitsList[iUnit][1] is the unit type (e.g. Warrior)
		# self.unitsList[iUnit][2] is a list of the active player's actual units
		# self.unitsList[iUnit][3] is the total number of those units seen by the active player (not only his own)
		
		iColorYellow = gc.getInfoTypeForString("COLOR_YELLOW")
		iColorRed = gc.getInfoTypeForString("COLOR_RED")
		iColorWhite = gc.getInfoTypeForString("COLOR_WHITE")
		iWidget = WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT
		iFont = CvUtil.FONT_LEFT_JUSTIFY

		# <!-- custom: icon overlay settings - claude opus 4.5 -->
		# Tunable values:
		iIconSize = 25
		iRowHeight = 25
		iUnitIndent = 12  # how much to indent unit icons under category headers
		iDetailIndent = 24  # how much to indent individual unit details
		iListX = self.X_TEXT + self.MAP_MARGIN
		iListY = self.Y_TEXT + self.MAP_MARGIN + 15
		iListW = self.W_TEXT - 2*self.MAP_MARGIN
		iListH = self.H_TEXT - 2*self.MAP_MARGIN - 15
		# Space reserved for icon at start of each row text (category headers)
		szIconSpace = u"      "
		# Extra space for indented units
		szUnitIndentSpace = u"  "
		szDetailIndentSpace = u"      "

		if (bReload):
			def addUnitListRow(iIndex, szText, iData1, iData2):
				screen.appendListBoxString(self.UNIT_LIST_ID, szText, iWidget, iData1, iData2, iFont)
				return iIndex + 1
		else:
			def addUnitListRow(iIndex, szText, iData1, iData2):
				screen.setListBoxStringGFC(self.UNIT_LIST_ID, iIndex, szText, iWidget, iData1, iData2, iFont)
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
		
		szText = localText.getText("TXT_KEY_PEDIA_ALL_UNITS", ()).upper()
		bAllSelected = (-1 in self.selectedGroupList)
		szText = formatSelection(u"", szText, bAllSelected, bAllSelected)
		if (bReload):
			screen.addListBoxGFC(self.UNIT_LIST_ID, "", iListX, iListY, iListW, iListH, TableStyles.TABLE_STYLE_STANDARD)
			screen.enableSelect(self.UNIT_LIST_ID, False)
			screen.setStyle(self.UNIT_LIST_ID, "Table_StandardCiv_Style")
		
		iPrevUnitCombat = -2
		iItem = addUnitListRow(0, szText, 1, -1)

		# <!-- custom: collect icon data for overlay - claude opus 4.5 -->
		# tuple: (button_path, iData1, iData2, iIndentLevel) where 0=category, 1=unit, 2=detail
		iconList = []
		iconList.append(("", 1, -1, 0))  # ALL UNITS row - no icon

		dPrimaryColor = {}
		dPyPlayer = {}
		dTeamId = {}

		for iUnit in range(iNumUnitInfos):
			if (len(self.unitsList[iUnit][2]) > 0):
				if (iPrevUnitCombat != self.unitsList[iUnit][0] and self.unitsList[iUnit][0] != -1):
					iPrevUnitCombat = self.unitsList[iUnit][0]
					szDescription = gc.getUnitCombatInfo(self.unitsList[iUnit][0]).getDescription().upper()
					szDescription = formatSelection(szIconSpace, szDescription, self.isSelectedGroup(self.unitsList[iUnit][0], False), self.isSelectedGroup(self.unitsList[iUnit][0], True))
					iItem = addUnitListRow(iItem, szDescription, 1, self.unitsList[iUnit][0] + iNumUnitInfos)
					# <!-- custom: combat icon (no indent) - claude opus 4.5 -->
					szCombatButton = gc.getUnitCombatInfo(self.unitsList[iUnit][0]).getButton()
					iconList.append((szCombatButton, 1, self.unitsList[iUnit][0] + iNumUnitInfos, 0))
				
				szDescription = gc.getUnitInfo(self.unitsList[iUnit][1]).getDescription() + u" (" + unicode(len(self.unitsList[iUnit][2])) + u")"
				szDescription = formatSelection(szIconSpace + szUnitIndentSpace, szDescription, self.isSelectedUnitType(self.unitsList[iUnit][1], False), self.isSelectedUnitType(self.unitsList[iUnit][1], True))
				iItem = addUnitListRow(iItem, szDescription, 1, self.unitsList[iUnit][1])
				# <!-- custom: unit icon (indented) - claude opus 4.5 -->
				szUnitButton = gc.getUnitInfo(self.unitsList[iUnit][1]).getButton()
				iconList.append((szUnitButton, 1, self.unitsList[iUnit][1], 1))
				
				for loopUnit in self.unitsList[iUnit][2]:
				
					if (self.bUnitDetails):
						szDescription = CyGameTextMgr().getSpecificUnitHelp(loopUnit, true, false)

						listMatches = re.findall("<.*?color.*?>", szDescription)	
						for szMatch in listMatches:
							szDescription = szDescription.replace(szMatch, u"")
						
						if (loopUnit.isWaiting()):
							szDescription = '*' + szDescription
						
						szDescription = formatSelection(szIconSpace + szDetailIndentSpace, szDescription, self.isSelectedUnit(loopUnit.getOwner(), loopUnit.getID(), False), self.isSelectedUnit(loopUnit.getOwner(), loopUnit.getID(), True))
						iItem = addUnitListRow(iItem, szDescription, -loopUnit.getOwner(), loopUnit.getID())
						# <!-- custom: individual unit icon (more indented) - claude opus 4.5 -->
						szUnitButton = gc.getUnitInfo(loopUnit.getUnitType()).getButton()
						iconList.append((szUnitButton, -loopUnit.getOwner(), loopUnit.getID(), 2))

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

		# <!-- custom: overlay icon buttons on listbox rows with indent - claude opus 4.5 -->
		if bReload:
			iIconBaseX = iListX + 3
			for iRow in range(len(iconList)):
				szButton, iData1, iData2, iIndentLevel = iconList[iRow]
				iIconY = iListY + (iRow * iRowHeight)
				# Apply indent based on level: 0=category, 1=unit type, 2=individual unit
				if iIndentLevel == 1:
					iIconX = iIconBaseX + iUnitIndent
				elif iIndentLevel == 2:
					iIconX = iIconBaseX + iDetailIndent
				else:
					iIconX = iIconBaseX
				szIconName = self.UNIT_ICON_ID + str(iRow)
				if self.IS_SAS_CV_MILITARY_ADVISOR_UNIT_COMBATS_UNITS_BUTTONS and szButton:
					screen.setImageButton(szIconName, szButton, iIconX, iIconY, iIconSize, iIconSize, iWidget, iData1, iData2)



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
				screen.addCheckBoxGFC(self.getLeaderButton(iLoopPlayer), szButton, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), x, y, iButtonSize, iButtonSize, WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT, 2, iLoopPlayer, ButtonStyles.BUTTON_STYLE_LABEL)
				screen.setState(self.getLeaderButton(iLoopPlayer), (iLoopPlayer in self.selectedPlayerList))				
		
		self.refreshUnitSelection(bReload)
		
		
		
		
		
