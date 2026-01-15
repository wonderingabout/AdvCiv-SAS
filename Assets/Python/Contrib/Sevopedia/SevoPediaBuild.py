# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#



from CvPythonExtensions import *
import CvUtil

from _sevopedia_helpers import *

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()



class SevoPediaBuild:

	def __init__(self, main):
		self.iBuild = -1
		self.top = main
		self.SAS_iBuildRoad = getInfoTypeOrFail("BUILD_ROAD", gc)
		self.SAS_iBuildRailroad = getInfoTypeOrFail("BUILD_RAILROAD", gc)

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_BUILD_PANE = self.top.X_PEDIA_PAGE
		self.Y_BUILD_PANE = self.top.Y_PEDIA_PAGE
		self.W_BUILD_PANE = 210
		self.H_BUILD_PANE = 210

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_BUILD_PANE + (self.H_BUILD_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_BUILD_PANE + (self.H_BUILD_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		remainingW = self.top.R_PEDIA_PAGE - self.X_BUILD_PANE - self.W_BUILD_PANE - (2 * self.MEDIUM_MARGIN)
		self.X_REQUIRES = self.X_BUILD_PANE + self.W_BUILD_PANE + self.MEDIUM_MARGIN
		self.Y_REQUIRES = self.Y_BUILD_PANE
		self.W_REQUIRES = (remainingW - self.MEDIUM_MARGIN) / 2
		self.H_REQUIRES = self.H_BUILD_PANE

		self.X_RESULTS = self.X_REQUIRES + self.W_REQUIRES + self.MEDIUM_MARGIN
		self.Y_RESULTS = self.Y_BUILD_PANE
		self.W_RESULTS = remainingW - self.W_REQUIRES - self.MEDIUM_MARGIN
		self.H_RESULTS = self.H_BUILD_PANE

		self.X_FEATURE_REMOVALS = self.X_BUILD_PANE
		self.Y_FEATURE_REMOVALS = self.Y_BUILD_PANE + self.H_BUILD_PANE + self.SMALL_MARGIN
		self.W_FEATURE_REMOVALS = self.top.R_PEDIA_PAGE - self.X_BUILD_PANE
		self.H_FEATURE_REMOVALS = 110

		self.X_SPECIAL = self.X_BUILD_PANE
		self.Y_SPECIAL = self.Y_FEATURE_REMOVALS + self.H_FEATURE_REMOVALS + self.SMALL_MARGIN
		self.W_SPECIAL = (self.top.R_PEDIA_PAGE - self.X_BUILD_PANE - self.MEDIUM_MARGIN) / 2
		self.H_SPECIAL = self.top.B_PEDIA_PAGE - self.Y_SPECIAL

		self.X_HISTORY = self.X_SPECIAL + self.W_SPECIAL + self.MEDIUM_MARGIN
		self.Y_HISTORY = self.Y_SPECIAL
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY
		self.H_HISTORY = self.H_SPECIAL


	def interfaceScreen(self, iBuild):
		self.iBuild = iBuild

		self.placeBuildPane()
		self.placeRequires()
		self.placeResults()
		self.placeFeatureRemovals()
		self.placeSpecial()
		self.placeHistory()


	def placeBuildPane(self):
		screen = self.top.getScreen()
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_BUILD_PANE, self.Y_BUILD_PANE, self.W_BUILD_PANE, self.H_BUILD_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getBuildInfo(self.iBuild).getButton(), self.X_ICON + self.W_ICON / 2 - self.ICON_SIZE / 2, self.Y_ICON + self.H_ICON / 2 - self.ICON_SIZE / 2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)


	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		buildInfo = gc.getBuildInfo(self.iBuild)
		bFound = False
		seenTechs = {}

		iTech = buildInfo.getTechPrereq()
		if iTech > -1:
			screen.attachImageButton(panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)
			seenTechs[iTech] = 1
			bFound = True

		for iFeature in xrange(gc.getNumFeatureInfos()):
			iFeatureTech = buildInfo.getFeatureTech(iFeature)
			if iFeatureTech > -1 and not seenTechs.has_key(iFeatureTech):
				screen.attachImageButton(panelName, "", gc.getTechInfo(iFeatureTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iFeatureTech, 1, False)
				seenTechs[iFeatureTech] = 1
				bFound = True

		if not bFound:
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_REQUIRES + (self.H_REQUIRES / 2)
			screen.addMultilineText(textName, szText, self.X_REQUIRES + 7, yPanelCenter, self.W_REQUIRES - 14, self.H_REQUIRES - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def placeResults(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_BUILD_RESULTS", ()), "", False, True, self.X_RESULTS, self.Y_RESULTS, self.W_RESULTS, self.H_RESULTS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panelName, "", "  ")

		buildInfo = gc.getBuildInfo(self.iBuild)
		bFound = False

		iImprovement = buildInfo.getImprovement()
		if iImprovement > -1:
			screen.attachImageButton(panelName, "", gc.getImprovementInfo(iImprovement).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, iImprovement, 1, False)
			bFound = True

		iRoute = buildInfo.getRoute()
		if iRoute > -1:
			routeInfo = gc.getRouteInfo(iRoute)
			iBuild = -1
			if routeInfo.getType() == "ROUTE_ROAD":
				iBuild = self.SAS_iBuildRoad
			elif routeInfo.getType() == "ROUTE_RAILROAD":
				iBuild = self.SAS_iBuildRailroad
			if iBuild < 0:
				raise Exception("SevoPediaBuild: missing Build for route %s" % routeInfo.getType())
			screen.attachImageButton(panelName, "", routeInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PYTHON, self.top.SAS_PEDIA_PYTHON_BUILD, iBuild, False)
			bFound = True

		if not bFound:
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_RESULTS + (self.H_RESULTS / 2)
			screen.addMultilineText(textName, szText, self.X_RESULTS + 7, yPanelCenter, self.W_RESULTS - 14, self.H_RESULTS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def placeFeatureRemovals(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_BUILD_REMOVES_FEATURES", ()), "", False, True, self.X_FEATURE_REMOVALS, self.Y_FEATURE_REMOVALS, self.W_FEATURE_REMOVALS, self.H_FEATURE_REMOVALS, PanelStyles.PANEL_STYLE_BLUE50)

		rowListName = self.top.getNextWidgetName()

		BUTTON_SIZE = 64
		multiListX = self.X_FEATURE_REMOVALS + MULTI_LIST_PANEL_OFFSET_X
		multiListY = self.Y_FEATURE_REMOVALS + MULTI_LIST_PANEL_OFFSET_Y
		multiListW = self.W_FEATURE_REMOVALS + MULTI_LIST_PANEL_ADDITIONAL_W
		multiListH = self.H_FEATURE_REMOVALS + MULTI_LIST_PANEL_ADDITIONAL_H
		buttonCalculate = 1
		screen.addMultiListControlGFC(rowListName, "", multiListX, multiListY, multiListW, multiListH, buttonCalculate, BUTTON_SIZE, BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)

		maxButtonsPerRow = get_multilist_max_buttons_per_row(multiListW, BUTTON_SIZE)
		buildInfo = gc.getBuildInfo(self.iBuild)
		bFound = False
		iButtonIndex = 0

		for iFeature in xrange(gc.getNumFeatureInfos()):
			featureInfo = gc.getFeatureInfo(iFeature)
			if featureInfo.isGraphicalOnly():
				continue

			iFeatureTime = buildInfo.getFeatureTime(iFeature)
			if buildInfo.isFeatureRemove(iFeature) or iFeatureTime > 0:
				columnIndex = 0
				screen.appendMultiListButton(rowListName, featureInfo.getButton(), columnIndex, WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, iFeature, 1, False)

				if iFeatureTime > 0:
					numTxt = str(iFeatureTime)
					extraCorrectionX = get_extra_correction_x(numTxt)
					add_multilist_numTxt_under_button(multiListX, multiListY, extraCorrectionX, iButtonIndex, BUTTON_SIZE, maxButtonsPerRow, numTxt, screen, self.top, WidgetTypes.WIDGET_GENERAL, CvUtil.FONT_CENTER_JUSTIFY)

				bFound = True
				iButtonIndex += 1

		if not bFound:
			txtKeyNone = "TXT_KEY_PEDIA_SAS_NO_BUTTON_FOUND_NONE"
			textName = self.top.getNextWidgetName()
			szText = localText.getText(txtKeyNone, ())
			yPanelCenter = self.Y_FEATURE_REMOVALS + (self.H_FEATURE_REMOVALS / 2)
			screen.addMultilineText(textName, szText, self.X_FEATURE_REMOVALS + 7, yPanelCenter, self.W_FEATURE_REMOVALS - 14, self.H_FEATURE_REMOVALS - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_BUILD_INFO", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)

		buildInfo = gc.getBuildInfo(self.iBuild)
		szSpecialText = buildInfo.getHelp()
		if not szSpecialText:
			szSpecialText = u""

		szStrategy = buildInfo.getStrategy()
		if szStrategy:
			if szSpecialText.strip():
				szSpecialText += u"\n"
			szSpecialText += szStrategy

		bullet = localText.getText("[ICON_BULLET]", ())
		iTime = buildInfo.getTime()
		if iTime > 0:
			if szSpecialText.strip():
				szSpecialText += u"\n"
			szSpecialText += u"%s%s: %d" % (bullet, localText.getText("TXT_KEY_PEDIA_BUILD_TIME", ()), iTime)

		iCost = buildInfo.getCost()
		if iCost > 0:
			if szSpecialText.strip():
				szSpecialText += u"\n"
			szSpecialText += u"%s%s: %d" % (bullet, localText.getText("TXT_KEY_PEDIA_BUILD_COST", ()), iCost)

		if buildInfo.isKill():
			if szSpecialText.strip():
				szSpecialText += u"\n"
			szSpecialText += u"%s%s" % (bullet, localText.getText("TXT_KEY_PEDIA_BUILD_KILL_WORKER", ()))

		listName = self.top.getNextWidgetName()
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL + 5, self.Y_SPECIAL - 13, self.W_SPECIAL - 10, self.H_SPECIAL - 10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def placeHistory(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		text = self.top.getNextWidgetName()
		info = gc.getBuildInfo(self.iBuild)

		screen.addPanel(panel, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)

		szHistory = info.getCivilopedia()
		screen.addMultilineText(text, szHistory, self.X_HISTORY + 10, self.Y_HISTORY + 30, self.W_HISTORY - 20, self.H_HISTORY - 40, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)


	def handleInput(self, inputClass):
		return 0
