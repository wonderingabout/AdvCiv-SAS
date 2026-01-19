# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#



from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaProject:
	
	def __init__(self, main):
		self.iProject = -1
		self.top = main

		self.W_REQUIRES = 200
		self.X_REQUIRES = self.top.R_PEDIA_PAGE - self.W_REQUIRES
		self.Y_REQUIRES = self.top.Y_PEDIA_PAGE
		self.H_REQUIRES = 116
		self.W_MOVIE = 84
		self.X_MOVIE = self.X_REQUIRES - self.W_MOVIE - 10
		self.Y_MOVIE = self.Y_REQUIRES
		self.H_MOVIE = self.H_REQUIRES

		self.X_PROJECT_PANE = self.top.X_PEDIA_PAGE
		self.Y_PROJECT_PANE = self.top.Y_PEDIA_PAGE
		self.W_PROJECT_PANE = self.top.W_PEDIA_PAGE - self.W_REQUIRES - self.W_MOVIE - 20
		self.H_PROJECT_PANE = 116

		self.W_ICON = 100
		self.H_ICON = 100
		self.X_ICON = self.X_PROJECT_PANE + (self.H_PROJECT_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_PROJECT_PANE + (self.H_PROJECT_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATS_PANE = self.X_ICON + self.W_ICON
		self.Y_STATS_PANE = 79
		self.W_STATS_PANE = 200
		self.H_STATS_PANE = 200

		self.X_SPECIAL = self.X_PROJECT_PANE
		self.Y_SPECIAL = self.Y_PROJECT_PANE + self.H_PROJECT_PANE + 10
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL
		self.H_SPECIAL = 210

		self.X_TEXT = self.X_PROJECT_PANE
		self.Y_TEXT = self.Y_SPECIAL + self.H_SPECIAL + 10
		self.W_TEXT = self.top.R_PEDIA_PAGE - self.X_PROJECT_PANE
		self.H_TEXT = self.top.B_PEDIA_PAGE - self.Y_TEXT



	def interfaceScreen(self, iProject):
		self.iProject = iProject

		self.placeProjectPane()
		self.placeStats()
		self.placeRequires()
		self.placeMovie()
		self.placeSpecial()
		self.placeText()



	def placeProjectPane(self):
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_PROJECT_PANE, self.Y_PROJECT_PANE, self.W_PROJECT_PANE, self.H_PROJECT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: no need for the blue frame on blue background, use transparent instead -->
		# screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getProjectInfo(self.iProject).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		projectInfo = gc.getProjectInfo(self.iProject)

		if (isWorldProject(self.iProject)):
			iMaxInstances = gc.getProjectInfo(self.iProject).getMaxGlobalInstances()
			szProjectType = localText.getText("TXT_KEY_PEDIA_WORLD_PROJECT", ())
			if (iMaxInstances > 1):
				szProjectType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
			screen.appendListBoxString(panelName, u"<font=4>" + szProjectType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (isTeamProject(self.iProject)):
			iMaxInstances = gc.getProjectInfo(self.iProject).getMaxTeamInstances()
			szProjectType = localText.getText("TXT_KEY_PEDIA_TEAM_PROJECT", ())
			if (iMaxInstances > 1):
				szProjectType += " " + localText.getText("TXT_KEY_PEDIA_WONDER_INSTANCES", (iMaxInstances,))
			screen.appendListBoxString(panelName, u"<font=4>" + szProjectType.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

		if (projectInfo.getProductionCost() > 0):
			# <!-- custom: simplify textual info for hammer yield to minimum, remove the "COST:" ugly part -->
			if self.top.iActivePlayer == -1:
				szCost = (projectInfo.getProductionCost() * gc.getDefineINT("PROJECT_PRODUCTION_PERCENT")) / 100
			else:
				szCost = gc.getActivePlayer().getProjectProductionNeeded(self.iProject)
			# szTextHammerYield = u"<font=4>" + szCost.upper() + u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar() + u"</font>"
			szTextHammerYield = u"<font=4>%c %d</font>" % (gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar(), szCost)
			screen.appendListBoxString(panelName, szTextHammerYield, WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.enableSelect(panelName, False)
		screen.attachLabel(panelName, "", "  ")
		iPrereq = gc.getProjectInfo(self.iProject).getTechPrereq()
		if (iPrereq >= 0):
			screen.attachImageButton(panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False)

	def placeMovie(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_SAS_MOVIE_PANEL", ()), "", False, True, self.X_MOVIE, self.Y_MOVIE, self.W_MOVIE, self.H_MOVIE, PanelStyles.PANEL_STYLE_BLUE50)

		# <!-- custom: use attachLabel for padding similar to Requires panel -->
		screen.attachLabel(panelName, "", "  ")

		iMovieType = self.top.SAS_PEDIA_MOVIE_TYPE_PROJECT
		if self.top.pediaMovies.hasMovie(iMovieType, self.iProject):
			# <!-- custom: setImageButtonAt requires str() wrapper (not unicode) for button path - discovered via debugging C++ signature mismatch error. (Claude Code Sonnet 4.5) -->
			buttonPathTxtKey = "TXT_KEY_IMAGE_AS_BUTTON_PLAY_BUTTON_BUTTON_PATH"
			buttonPath = str(localText.getText(buttonPathTxtKey, ()))
			check_button_path_is_valid("Sevopedia Project Movie button", buttonPath, buttonPathTxtKey)

			iPackedMovie = self.top.SAS_packMovieKey(iMovieType, self.iProject)
			buttonSize = 64
			# <!-- custom: setImageButtonAt positions relative to panel content area (below header).
			# X: Standard centering works correctly.
			# Y: Must be set to 10 (not calculated from panelHeaderHeight) - empirically determined positioning fix. (Claude Code Sonnet 4.5) -->
			buttonX = (self.W_MOVIE - buttonSize) / 2
			buttonY = 10
			screen.setImageButtonAt(self.top.getNextWidgetName(), panelName, buttonPath, buttonX, buttonY, buttonSize, buttonSize, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_MOVIE_ENTRY, iPackedMovie)
		else:
			txtKeyNoButtonFound = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNoButtonFound, ())
			yPanelCenter = self.Y_MOVIE + (self.H_MOVIE / 2)
			screen.addMultilineText(textName, szText, self.X_MOVIE + 7, yPanelCenter, self.W_MOVIE - 14, self.H_MOVIE - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		szSpecialText = CyGameTextMgr().getProjectHelp(self.iProject, True, None)[1:]
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+30, self.W_SPECIAL-10, self.H_SPECIAL-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeText(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, "", "", True, True, self.X_TEXT, self.Y_TEXT, self.W_TEXT, self.H_TEXT, PanelStyles.PANEL_STYLE_BLUE50)
		szText = gc.getProjectInfo(self.iProject).getCivilopedia()
		screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def getProjectType(self, iProject):
		if (isWorldProject(iProject)):
			return (3)
		if (isTeamProject(iProject)):
			return (2)
		return (1)



	def getProjectSortedList(self):
		listOfAllTypes = []
		for iBuildingType in range(4):
			listBuildings = []
			iCount = 0
			for iBuilding in range(gc.getNumProjectInfos()):
				if (self.getProjectType(iBuilding) == iBuildingType and not gc.getProjectInfo(iBuilding).isGraphicalOnly()):
					listBuildings.append(iBuilding)
					iCount += 1
			listSorted = [(0,0)] * iCount
			iI = 0
			for iBuilding in listBuildings:
				listSorted[iI] = (gc.getProjectInfo(iBuilding).getDescription(), iBuilding)
				iI += 1
			listSorted.sort()
			for i in range(len(listSorted)):
				listOfAllTypes.append(listSorted[i])
		return listOfAllTypes



	def handleInput (self, inputClass):
		return 0
