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



class SevoPediaCivic:

	def __init__(self, main):
		self.iCivic = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		# <!-- custom: multilist leaders panel width from helper so callers can switch button count per row without redoing panel math. (GPT-5.3-Codex) -->
		self.W_LEADERS = get_multilist_panel_width_for_buttons(4, MULTILIST_BUTTON_SIZE, HYPOTHESIZED_MULTI_LIST_LEFT_EDGE_PADDING, HYPOTHESIZED_MULTI_LIST_RIGHT_EDGE_PADDING, HYPOTHESIZED_MULTI_LIST_INTER_BUTTON_SPACING)
		self.X_LEADERS = self.top.R_PEDIA_PAGE - self.W_LEADERS
		self.Y_LEADERS = self.top.Y_PEDIA_PAGE
		self.H_LEADERS = self.top.B_PEDIA_PAGE - self.Y_LEADERS

		self.X_CIVIC_PANE = self.top.X_PEDIA_PAGE
		self.Y_CIVIC_PANE = self.top.Y_PEDIA_PAGE
		#self.W_CIVIC_PANE = 290
		#self.H_CIVIC_PANE = 151
		self.W_CIVIC_PANE = 440
		self.H_CIVIC_PANE = 230

		self.W_ICON = 125
		self.H_ICON = 125
		self.X_ICON = self.X_CIVIC_PANE + (self.H_CIVIC_PANE - self.H_ICON) / 2
		self.Y_ICON = self.Y_CIVIC_PANE + (self.H_CIVIC_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_STATS = self.X_ICON + self.W_ICON 
		#self.Y_STATS = 112
		self.Y_STATS = 141
		self.W_STATS = 250
		self.H_STATS = 200

		self.W_REMAINING_CENTER_SPACE = self.top.R_PEDIA_PAGE - (self.W_LEADERS + self.MEDIUM_MARGIN) - self.MEDIUM_MARGIN - (self.X_CIVIC_PANE + self.W_CIVIC_PANE + self.MEDIUM_MARGIN)

		self.X_SPECIAL = self.X_CIVIC_PANE + self.W_CIVIC_PANE + self.MEDIUM_MARGIN

		self.W_REQUIRES = get_panel_width_for_buttons(1, MULTILIST_BUTTON_SIZE, HYPOTHESIZED_NON_MULTILIST_PANEL_EDGE_PADDING, HYPOTHESIZED_NON_MULTILIST_PANEL_INTER_BUTTON_SPACING)

		self.W_SPECIAL = self.W_REMAINING_CENTER_SPACE - self.W_REQUIRES

		self.X_REQUIRES = self.X_SPECIAL + self.W_SPECIAL + self.MEDIUM_MARGIN

		self.H_REQUIRES = NON_MULTILIST_PANEL_STANDARD_HEIGHT

		self.Y_REQUIRES = self.Y_CIVIC_PANE + self.H_CIVIC_PANE - self.H_REQUIRES

		self.Y_SPECIAL = self.Y_CIVIC_PANE

		self.H_SPECIAL = self.H_CIVIC_PANE

		self.X_HISTORY = self.X_CIVIC_PANE
		self.Y_HISTORY = self.Y_CIVIC_PANE + self.H_CIVIC_PANE + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY - (self.W_LEADERS + self.MEDIUM_MARGIN)
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY



	def interfaceScreen(self, iCivic):
		self.iCivic = iCivic

		self.placeLeaders()
		self.placeCivicPane()
		self.placeStats()
		self.placeSpecial()
		self.placeRequires()
		self.placeHistory()



	# <!-- custom: in https://civ4bug.sourceforge.net/PythonAPI/AllClasses.html i have found this:
	# VOID addMultiListControlGFC (STRING szName, STRING helpText, INT iX, INT iY, INT iWidth, INT iHeight, INT numLists, INT defaultWidth, INT defaultHeight, TableStyle eStyle)
	# and in https://github.com/f1rpo/AdvCiv/blob/master/Assets/Python/Screens/CvMainInterface.py#L2050C1-L2053C38 i have found this:
	# 		self.screen.addMultiListControlGFC("BottomButtonList", u"",
	#			lRect.x(), lRect.y(), lRect.width(), lRect.height(),
	#			4, iButtonSize, iButtonSize, # numLists, defaultWidth, defaultHeight
	#			TableStyles.TABLE_STYLE_STANDARD)
	# if it helps us adapt/use the addMultiListControlGFC method -->
	def placeLeaders(self):
		xPanel = self.X_LEADERS
		yPanel = self.Y_LEADERS
		wPanel = self.W_LEADERS
		hPanel = self.H_LEADERS

		txtKeyPanel = "TXT_KEY_PEDIA_CATEGORY_LEADER"
		headerLabel = localText.getText(txtKeyPanel, ())
		numWithCivic, totalRealLeaders = get_favorite_leader_counts(FAVORITE_LEADER_TYPE_CIVIC, self.iCivic, EXCLUDED_LEADER_TYPES_FROM_SEVOPEDIA)
		headerText = format_leaders_header_text(numWithCivic, totalRealLeaders, headerLabel)

		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()

		# Create panel with proper styling
		screen.addPanel(panelName, headerText, "", False, True, xPanel, yPanel, wPanel, hPanel, PanelStyles.PANEL_STYLE_BLUE50)

		rowListName = self.top.getNextWidgetName()

		# Create the MultiList control
		# Constants for button display
		multiListX = xPanel + MULTI_LIST_PANEL_OFFSET_X
		multiListY = yPanel + MULTI_LIST_PANEL_OFFSET_Y
		multiListW = wPanel + MULTI_LIST_PANEL_ADDITIONAL_W
		multiListH = hPanel + MULTI_LIST_PANEL_ADDITIONAL_H
		screen.addMultiListControlGFC(rowListName, "", multiListX, multiListY, multiListW, multiListH, SEVOPEDIA_MULTILIST_NUM_LISTS_AUTO_CALCULATE, MULTILIST_BUTTON_SIZE, MULTILIST_BUTTON_SIZE, TableStyles.TABLE_STYLE_STANDARD)

		# Find all leaders who have this civic as favorite
		for iLeader in xrange(gc.getNumLeaderHeadInfos()):
			leaderInfo = gc.getLeaderHeadInfo(iLeader)
			if leaderInfo.getFavoriteCivic() == self.iCivic:
				leaderInfo = gc.getLeaderHeadInfo(iLeader)
				screen.appendMultiListButton(rowListName, leaderInfo.getButton(), SEVOPEDIA_MULTILIST_COLUMN_INDEX_AUTO, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)



	def placeCivicPane(self):
		screen = self.top.getScreen()

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_CIVIC_PANE, self.Y_CIVIC_PANE, self.W_CIVIC_PANE, self.H_CIVIC_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		# <!-- custom: no need for the blue frame on blue background, use transparent instead -->
		#screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_EMPTY)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getCivicInfo(self.iCivic).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1)



	def placeStats(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addListBoxGFC(panelName, "", self.X_STATS, self.Y_STATS, self.W_STATS, self.H_STATS, TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(panelName, False)
		iCivicOptionType = gc.getCivicInfo(self.iCivic).getCivicOptionType()
		# <!-- custom: make text a bit bigger/wider, was font=4 -->
		if (iCivicOptionType != -1):
			screen.appendListBoxString(panelName, u"<font=4>" + gc.getCivicOptionInfo(iCivicOptionType).getDescription().upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)
		pUpkeepInfo = gc.getUpkeepInfo(gc.getCivicInfo(self.iCivic).getUpkeep())
		if (pUpkeepInfo):
			screen.appendListBoxString(panelName, u"<font=4>" + pUpkeepInfo.getDescription().upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50)
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC(panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY)
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().parseCivicInfo(self.iCivic, True, False, True)
		# <!-- custom: leave some room on top, based on placeSpecial in sevopedia terrain -->
		#screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+5, self.W_SPECIAL-10, self.H_SPECIAL-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL+5, self.Y_SPECIAL+10, self.W_SPECIAL-10, self.H_SPECIAL-20, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50)
		screen.enableSelect(panelName, False)
		screen.attachLabel(panelName, "", "  ")
		iTech = gc.getCivicInfo(self.iCivic).getTechPrereq()
		if (iTech > -1):
			screen.attachImageButton(panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False)



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		# advc.004y: Label added for this panel
		#screen.addPanel(panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50)

		textName = self.top.getNextWidgetName()
		szText = u""
		# <!-- custom: same reasoning as for TXT_KEY_CIVILOPEDIA_STRATEGY in SevoPediaBuilding.py (refer to this file for details), removing (hiding) the entry entirely from the sevopedia. -->
		# <!-- custom: same reasoning as for/in SevopediaBuilding.py, i also don't need the redundant "History:" -->
		szText += gc.getCivicInfo(self.iCivic).getCivilopedia()
		# </advc.004y>
		#screen.attachMultilineText(panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.addMultilineText(textName, szText, self.X_HISTORY + 7, self.Y_HISTORY + 10, self.W_HISTORY - (15 * 2), self.H_HISTORY - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def handleInput (self, inputClass):
		return 0
