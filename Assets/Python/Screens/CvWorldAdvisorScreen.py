## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)

from CvPythonExtensions import *
import CvUtil
from SASUtils import *
from SASFontUtils import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvWorldAdvisorScreen:
	"World Advisor! Contains the Environment tab."

	def __init__(self, screenId):
		self.screenId = screenId
		self.SCREEN_NAME = "WorldAdvisorScreen"
		self.WIDGET_ID = "WorldAdvisorWidget"

		self.Z_BACKGROUND = -6.1
		self.Z_CONTROLS = self.Z_BACKGROUND - 0.2
		self.DZ = -0.2
		self.Z_HELP_AREA = self.Z_CONTROLS - 1

		self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS = SAS_ADVISOR_LEFT_SPACE_FOR_COMMERCE_SLIDERS
		self.W_RIGHT_SPACE_FOR_SCOREBOARD = SAS_ADVISOR_RIGHT_SPACE_FOR_SCOREBOARD
		self.H_TOP_SPACE_FOR_TECH_BAR = SAS_ADVISOR_TOP_SPACE_FOR_TECH_BAR
		self.H_BOTTOM_SPACE = SAS_ADVISOR_BOTTOM_SPACE

		self.W_HELP_AREA = 200
		self.PANEL_HEIGHT = 55
		self.X_MARGIN = 45

		self.ENV_INNER_MARGIN = 24
		self.ENV_COLUMN_GAP = 20
		self.ENV_TOP_PANEL_HEIGHT = 100
		self.ENV_Y_SPACING = 30
		self.ENV_TEXT_MARGIN = 15

		self.PAGE_NAME_LIST = [
			"TXT_KEY_ECONOMICS_ADVISOR_ENVIRONMENT_TAB",
			]
		self.PAGE_LINK_WIDTH = []
		self.iEnvironmentID = 0
		self.iActiveTab = self.iEnvironmentID
		self.DEBUG_DROPDOWN_ID = "WorldAdvisorDropdownWidget"

		self.iLanguageLoaded = -1
		self.nWidgetCount = 0
		self.iActivePlayer = -1
		self.pActivePlayer = None
		self.iActiveTeam = -1
		self.pActiveTeam = None

	def reset(self):
		self.iActivePlayer = CyGame().getActivePlayer()
		if self.iActivePlayer == -1:
			return
		self.pActivePlayer = gc.getPlayer(self.iActivePlayer)
		self.iActiveTeam = self.pActivePlayer.getTeam()
		self.pActiveTeam = gc.getTeam(self.iActiveTeam)

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, self.screenId)

	def updateRuntimeLayout(self, screen):
		self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN = getAdvisorRuntimeBounds(screen, self.W_LEFT_SPACE_FOR_COMMERCE_SLIDERS, self.W_RIGHT_SPACE_FOR_SCOREBOARD, self.H_TOP_SPACE_FOR_TECH_BAR, self.H_BOTTOM_SPACE)
		self.X_TITLE, self.X_EXIT, self.Y_EXIT, self.Y_LINK, _ = getAdvisorRuntimeAnchors(self.W_SCREEN, self.H_SCREEN)
		self.Y_TITLE = SAS_ADVISOR_TITLE_Y

		self.CONTENT_Y_TOP = self.PANEL_HEIGHT
		self.CONTENT_Y_BOTTOM = self.H_SCREEN - self.PANEL_HEIGHT

		self.ENV_X_LEFT_PANEL = self.X_MARGIN
		self.ENV_PANE_WIDTH = (self.W_SCREEN - (2 * self.X_MARGIN) - (2 * self.ENV_COLUMN_GAP)) / 3
		self.ENV_X_MIDDLE_PANEL = self.ENV_X_LEFT_PANEL + self.ENV_PANE_WIDTH + self.ENV_COLUMN_GAP
		self.ENV_X_RIGHT_PANEL = self.ENV_X_MIDDLE_PANEL + self.ENV_PANE_WIDTH + self.ENV_COLUMN_GAP
		self.ENV_Y_TOP_PANEL = self.CONTENT_Y_TOP + self.ENV_INNER_MARGIN
		self.ENV_H_TOP_PANEL = self.ENV_TOP_PANEL_HEIGHT
		self.ENV_Y_LOCATION = self.ENV_Y_TOP_PANEL + self.ENV_H_TOP_PANEL + self.ENV_INNER_MARGIN
		self.ENV_PANE_HEIGHT = self.CONTENT_Y_BOTTOM - self.ENV_Y_LOCATION - self.ENV_INNER_MARGIN

	def initText(self):
		if not CyGame().isFinalInitialized():
			return

		aszPageLabels = []
		for szPageName in self.PAGE_NAME_LIST:
			aszPageLabels.append(localText.getText(szPageName, ()).upper())
		self.PAGE_LINK_WIDTH[:] = []
		for szPageLabel in aszPageLabels:
			self.PAGE_LINK_WIDTH.append(CyInterface().determineWidth(szPageLabel) + 30)

		if self.iLanguageLoaded == CyGame().getCurrentLanguage():
			return
		self.iLanguageLoaded = CyGame().getCurrentLanguage()

		self.SCREEN_TITLE = SAS_FONT_TAG_TITLE_BOLD + localText.getText("TXT_KEY_WORLD_ADVISOR_TITLE", ()).upper() + SAS_FONT_TAG_CLOSE
		self.EXIT_TEXT = SAS_FONT_TAG_TITLE + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + SAS_FONT_TAG_CLOSE
		self.ART_MAINMENU_SLIDESHOW_LOAD = ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath()
		self.ART_POPUPS_BACKGROUND_TRANSPARENT = ArtFileMgr.getInterfaceArtInfo("POPUPS_BACKGROUND_TRANSPARENT").getPath()

		self.TEXT_GW_SEVERITY_RATING = localText.getText("TXT_KEY_GW_SEVERITY_RATING", ()).upper()
		self.TEXT_ENV_POLLUTION = localText.getText("TXT_KEY_POLLUTION", ())
		self.TEXT_ENV_TOTAL = localText.getText("TXT_KEY_TOTAL", ())
		self.TEXT_ENV_CHANCES = localText.getText("TXT_KEY_CHANCES", ())
		self.TEXT_ENV_POPULATION = localText.getText("TXT_KEY_DEMO_SCREEN_POPULATION_TEXT", ())
		self.TEXT_ENV_BUILDINGS = localText.getText("TXT_KEY_CONCEPT_BUILDINGS", ())
		self.TEXT_ENV_RESOURCES = localText.getText("TXT_KEY_CONCEPT_RESOURCES", ())
		self.TEXT_ENV_ELECTRICITY = localText.getText("TXT_KEY_TECH_ELECTRICITY", ())
		self.TEXT_ENV_TOTAL_OFFSETS = localText.getText("TXT_KEY_ENVIRONMENT_TOTAL_OFFSETS", ())
		self.TEXT_ENV_TOTAL_IMPACT = localText.getText("TXT_KEY_ENVIRONMENT_TOTAL_IMPACT", ())
		self.TEXT_ENV_LOCAL_THRESHOLD = localText.getText("TXT_KEY_ENVIRONMENT_LOCAL_THRESHOLD", ())
		self.TEXT_ENV_TOTAL_POLLUTION = localText.getText("TXT_KEY_ENVIRONMENT_TOTAL_POLLUTION", ())
		self.TEXT_ENV_THRESHOLD = localText.getText("TXT_KEY_ENVIRONMENT_THRESHOLD", ())
		self.TEXT_ENV_GW_CHANGE_RATE = localText.getText("TXT_KEY_ENVIRONMENT_GW_CHANGE_RATE", ())
		self.TEXT_ENV_RELATIVE_CONTRIBUTION = localText.getText("TXT_KEY_ENVIRONMENT_RELATIVE_CONTRIBUTION", ())
		self.TEXT_ENV_GW_INDEX = localText.getText("TXT_KEY_ENVIRONMENT_GW_INDEX", ())
		self.TEXT_ENV_EXPECTED_EVENTS = localText.getText("TXT_KEY_ENVIRONMENT_EXPECTED_EVENTS", ())
		self.TEXT_ENV_EVENT_TALLY = localText.getText("TXT_KEY_ENVIRONMENT_EVENT_TALLY", ())
		self.TEXT_ENV_LOCAL_ANGER_LEVEL = localText.getText("TXT_KEY_ENVIRONMENT_LOCAL_ANGER_LEVEL", ())
		self.COLOR_GREEN = gc.getInfoTypeForString("COLOR_GREEN")
		self.COLOR_YELLOW = gc.getInfoTypeForString("COLOR_YELLOW")
		self.COLOR_RED = gc.getInfoTypeForString("COLOR_RED")

		self.LABEL_ENV_DOMESTIC = SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_ENVIRONMENT_DOMESTIC", ()).upper() + SAS_FONT_TAG_CLOSE
		self.LABEL_ENV_GLOBAL = SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_ENVIRONMENT_GLOBAL", ()).upper() + SAS_FONT_TAG_CLOSE
		self.LABEL_ENV_EFFECTS = SAS_FONT_TAG_LABEL + localText.getText("TXT_KEY_ENVIRONMENT_EFFECTS", ()).upper() + SAS_FONT_TAG_CLOSE

	def showScreen(self):
		screen = self.getScreen()
		if screen.isActive():
			return
		self.updateRuntimeLayout(screen)
		self.initText()

		screen.setRenderInterfaceOnly(True)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		self.reset()
		self.deleteAllWidgets()

		screen.addDDSGFC("WorldAdvisorBackground", self.ART_MAINMENU_SLIDESHOW_LOAD, 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel("WorldAdvisorTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, self.PANEL_HEIGHT, PanelStyles.PANEL_STYLE_TOPBAR)
		screen.addPanel("WorldAdvisorBottomPanel", u"", u"", True, False, 0, self.H_SCREEN - self.PANEL_HEIGHT, self.W_SCREEN, self.PANEL_HEIGHT, PanelStyles.PANEL_STYLE_BOTTOMBAR)
		screen.showWindowBackground(False)
		screen.setDimensions(self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN)

		self.szExitButtonName = self.getNextWidgetName()
		screen.setText(self.szExitButtonName, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		self.szHeaderWidget = self.getNextWidgetName()
		screen.setLabel(self.szHeaderWidget, "Background", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		screen.setHelpTextArea(self.W_HELP_AREA, FontTypes.SMALL_FONT, self.X_SCREEN, self.Y_SCREEN, self.Z_HELP_AREA, 1, self.ART_POPUPS_BACKGROUND_TRANSPARENT, True, True, CvUtil.FONT_LEFT_JUSTIFY, 0)

		if CyGame().isDebugMode():
			screen.addDropDownBoxGFC(self.DEBUG_DROPDOWN_ID, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for iPlayer in range(gc.getMAX_CIV_PLAYERS()):
				if gc.getPlayer(iPlayer).isAlive():
					screen.addPullDownString(self.DEBUG_DROPDOWN_ID, gc.getPlayer(iPlayer).getName(), iPlayer, iPlayer, iPlayer == self.iActivePlayer)

		self.iNumPermanentWidgets = self.nWidgetCount
		self.iActiveTab = self.iEnvironmentID
		self.redrawContents()

	def redrawContents(self):
		screen = self.getScreen()
		self.deleteAllWidgets(self.iNumPermanentWidgets)

		xLink = self.X_MARGIN
		for iPage in range(len(self.PAGE_NAME_LIST)):
			szTextId = "WorldAdvisorTabButton" + str(iPage)
			szText = localText.getText(self.PAGE_NAME_LIST[iPage], ()).upper()
			if self.iActiveTab == iPage:
				szText = localText.changeTextColor(szText, self.COLOR_YELLOW)
				screen.setText(szTextId, "", SAS_FONT_TAG_TITLE + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLink + self.PAGE_LINK_WIDTH[iPage] / 2, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			else:
				screen.setText(szTextId, "", SAS_FONT_TAG_TITLE + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, xLink + self.PAGE_LINK_WIDTH[iPage] / 2, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, iPage, -1)
			xLink += self.PAGE_LINK_WIDTH[iPage]

		if self.iActiveTab == self.iEnvironmentID:
			self.drawEnvironmentTab()

	# ENVIRONMENT
	def drawEnvironmentTab(self):
		screen = self.getScreen()
		game = CyGame()
		player = gc.getPlayer(self.iActivePlayer)

		X_LEFT_PANEL = self.ENV_X_LEFT_PANEL
		X_MIDDLE_PANEL = self.ENV_X_MIDDLE_PANEL
		X_RIGHT_PANEL = self.ENV_X_RIGHT_PANEL
		Y_TOP_PANEL = self.ENV_Y_TOP_PANEL
		H_TOP_PANEL = self.ENV_H_TOP_PANEL
		Y_LOCATION = self.ENV_Y_LOCATION
		PANE_WIDTH = self.ENV_PANE_WIDTH
		PANE_HEIGHT = self.ENV_PANE_HEIGHT
		TEXT_MARGIN = self.ENV_TEXT_MARGIN
		Y_SPACING = self.ENV_Y_SPACING

		szTopPanel = self.getNextWidgetName()
		screen.addPanel(szTopPanel, u"", "", True, True, X_LEFT_PANEL, Y_TOP_PANEL, X_RIGHT_PANEL + PANE_WIDTH - X_LEFT_PANEL, H_TOP_PANEL, PanelStyles.PANEL_STYLE_MAIN)

		iGlobalWarmingIndex = game.getGlobalWarmingIndex()
		iGlobalWarmingChances = game.getGlobalWarmingChances()
		iGwEventTally = game.getGwEventTally()
		iSeverityRating = game.calculateGwSeverityRating()

		szText = self.TEXT_GW_SEVERITY_RATING + ": "
		# advc.137: Better use separate keys
		if iSeverityRating < 30:
			szText += localText.getColorText("TXT_KEY_LOW", (), self.COLOR_GREEN).upper()
		elif iSeverityRating < 75:
			szText += localText.getColorText("TXT_KEY_MEDIUM", (), self.COLOR_YELLOW).upper()
		else:
			szText += localText.getColorText("TXT_KEY_HIGH", (), self.COLOR_RED).upper()
		if CyGame().isDebugMode():
			szText += u" (%d)" % iSeverityRating
		screen.setLabel(self.getNextWidgetName(), szTopPanel, SAS_FONT_TAG_TITLE + szText + SAS_FONT_TAG_CLOSE, CvUtil.FONT_CENTER_JUSTIFY, (X_LEFT_PANEL + PANE_WIDTH + X_RIGHT_PANEL) / 2, Y_TOP_PANEL + H_TOP_PANEL / 2 - Y_SPACING / 2, self.Z_CONTROLS + self.DZ, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szLeftPanel = self.getNextWidgetName()
		screen.addPanel(szLeftPanel, u"", "", True, True, X_LEFT_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN)
		screen.setLabel(self.getNextWidgetName(), "Background", self.LABEL_ENV_DOMESTIC, CvUtil.FONT_CENTER_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szMiddlePanel = self.getNextWidgetName()
		screen.addPanel(szMiddlePanel, u"", "", True, True, X_MIDDLE_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN)
		screen.setLabel(self.getNextWidgetName(), "Background", self.LABEL_ENV_GLOBAL, CvUtil.FONT_CENTER_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		szRightPanel = self.getNextWidgetName()
		screen.addPanel(szRightPanel, u"", "", True, True, X_RIGHT_PANEL, Y_LOCATION, PANE_WIDTH, PANE_HEIGHT, PanelStyles.PANEL_STYLE_MAIN)
		screen.setLabel(self.getNextWidgetName(), "Background", self.LABEL_ENV_EFFECTS, CvUtil.FONT_CENTER_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH / 2, Y_LOCATION + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		# Left panel: domestic
		yLocation = Y_LOCATION
		iPopulation = player.calculatePollution(PollutionTypes.POLLUTION_POPULATION)
		iBuildings = player.calculatePollution(PollutionTypes.POLLUTION_BUILDINGS)
		iResources = player.calculatePollution(PollutionTypes.POLLUTION_BONUSES)
		iPower = player.calculatePollution(PollutionTypes.POLLUTION_POWER)
		iLocalPollution = player.calculatePollution(PollutionTypes.POLLUTION_ALL)
		iLocalThreshold = game.calculateGwSustainabilityThreshold(self.iActivePlayer)
		iPollutionTypes = (iPopulation != 0) * PollutionTypes.POLLUTION_POPULATION | (iBuildings != 0) * PollutionTypes.POLLUTION_BUILDINGS | (iResources != 0) * PollutionTypes.POLLUTION_BONUSES | (iPower != 0) * PollutionTypes.POLLUTION_POWER
		iLocalDefence = game.calculateGwLandDefence(self.iActivePlayer)

		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_POLLUTION + ":" + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, iPollutionTypes, -1)

		if iPopulation != 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_POPULATION + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + 2 * TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_POPULATION, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iPopulation) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_POPULATION, -1)
		if iBuildings != 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_BUILDINGS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + 2 * TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_BUILDINGS, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iBuildings) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_BUILDINGS, -1)
		if iResources != 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_RESOURCES + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + 2 * TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_BONUSES, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iResources) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_BONUSES, -1)
		if iPower != 0:
			yLocation += Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_ELECTRICITY + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + 2 * TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_POWER, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iPower) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_POWER, -1)

		yLocation += Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_TOTAL + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, iPollutionTypes, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iLocalPollution) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, iPollutionTypes, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_TOTAL_OFFSETS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_OFFSETS, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(-iLocalDefence) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_OFFSETS, -1, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_TOTAL_IMPACT + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iLocalPollution - iLocalDefence) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_LOCAL_THRESHOLD + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_LEFT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_SUSTAINABILITY_THRESHOLD, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iLocalThreshold) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_LEFT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_SUSTAINABILITY_THRESHOLD, -1, -1)

		# Middle panel: Global
		yLocation = Y_LOCATION
		iGlobalPollution = game.calculateGlobalPollution()
		iGlobalDefence = game.calculateGwLandDefence(PlayerTypes.NO_PLAYER)
		iThreshold = game.calculateGwSustainabilityThreshold(PlayerTypes.NO_PLAYER)
		iChangeRate = iGlobalPollution - iGlobalDefence - iThreshold - iGlobalWarmingIndex * gc.getDefineINT("GLOBAL_WARMING_RESTORATION_RATE") / 100

		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_TOTAL_POLLUTION + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_ALL, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iGlobalPollution) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_SOURCE, PollutionTypes.POLLUTION_ALL, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_TOTAL_OFFSETS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_OFFSETS, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(-iGlobalDefence) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_POLLUTION_OFFSETS, -1, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_THRESHOLD + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_SUSTAINABILITY_THRESHOLD, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iThreshold) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_SUSTAINABILITY_THRESHOLD, -1, -1)
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_GW_CHANGE_RATE + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(max(0, iChangeRate)) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		iResponsibility = 100 * (iLocalPollution - iLocalDefence)
		iResponsibility /= max(1, iLocalThreshold)
		iResponsibility *= iThreshold
		iResponsibility /= max(1, iGlobalPollution - iGlobalDefence)
		if iGwEventTally >= 0 or CyGame().isDebugMode():
			yLocation += 1.5 * Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_RELATIVE_CONTRIBUTION + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_MIDDLE_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_RELATIVE_CONTRIBUTION, -1, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iResponsibility) + u"%" + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_MIDDLE_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_RELATIVE_CONTRIBUTION, -1, -1)

		# Right panel: Effects
		yLocation = Y_LOCATION
		yLocation += 1.5 * Y_SPACING
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_GW_INDEX + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_INDEX, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iGlobalWarmingIndex) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_INDEX, -1, -1)
		yLocation += 1.5 * Y_SPACING
		fExpectedEvents = 1.0 * iGlobalWarmingChances * gc.getDefineINT("GLOBAL_WARMING_PROB") / (10.0 * gc.getGameSpeedInfo(game.getGameSpeedType()).getVictoryDelayPercent())
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_EXPECTED_EVENTS + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + u"%0.1f" % fExpectedEvents + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		if iGwEventTally >= 0:
			yLocation += 1.5 * Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_EVENT_TALLY + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iGwEventTally) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		iGwPercentAnger = player.getGwPercentAnger()
		if iGwPercentAnger >= 2:
			yLocation += 1.5 * Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_LOCAL_ANGER_LEVEL + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_UNHAPPY, -1, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(iGwPercentAnger) + u"%" + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GW_UNHAPPY, -1, -1)
		if CyGame().isDebugMode():
			yLocation += 1.5 * Y_SPACING
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + self.TEXT_ENV_CHANCES + SAS_FONT_TAG_CLOSE, CvUtil.FONT_LEFT_JUSTIFY, X_RIGHT_PANEL + TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setLabel(self.getNextWidgetName(), "Background", SAS_FONT_TAG_LABEL + unicode(game.getGlobalWarmingChances()) + SAS_FONT_TAG_CLOSE, CvUtil.FONT_RIGHT_JUSTIFY, X_RIGHT_PANEL + PANE_WIDTH - TEXT_MARGIN, yLocation + TEXT_MARGIN, self.Z_CONTROLS + self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName

	def deleteAllWidgets(self, iNumPermanentWidgets = 0):
		screen = self.getScreen()
		i = self.nWidgetCount - 1
		while i >= iNumPermanentWidgets:
			self.nWidgetCount = i
			screen.deleteWidget(self.getNextWidgetName())
			i -= 1
		self.nWidgetCount = iNumPermanentWidgets

	def handleInput(self, inputClass):
		szWidgetName = inputClass.getFunctionName() + str(inputClass.getID())
		if (szWidgetName == self.szExitButtonName and inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED or inputClass.getData() == int(InputTypes.KB_RETURN)):
			self.getScreen().hideScreen()
			return 1

		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
			if inputClass.getFunctionName() == self.DEBUG_DROPDOWN_ID:
				screen = self.getScreen()
				iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
				self.iActivePlayer = screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex)
				self.pActivePlayer = gc.getPlayer(self.iActivePlayer)
				self.iActiveTeam = self.pActivePlayer.getTeam()
				self.pActiveTeam = gc.getTeam(self.iActiveTeam)
				self.redrawContents()
				return 1

		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
			iSelected = inputClass.getData()
			if iSelected >= 0 and iSelected < len(self.PAGE_NAME_LIST) and iSelected != self.iActiveTab:
				self.iActiveTab = iSelected
				self.redrawContents()
				return 1
		return 0

	def update(self, fDelta):
		return
