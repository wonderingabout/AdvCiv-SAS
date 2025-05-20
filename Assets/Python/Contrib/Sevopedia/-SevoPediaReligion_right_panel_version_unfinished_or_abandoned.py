# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose
#
# <!-- custom: part of the code here (placeLeaders in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from History Rewritten mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\History Rewritten\Assets\Python\Pedia\CvPediaReligion.py
# which may be modified or not for AdvCiv-SAS
#
# <!-- custom: part of the code here (placeBuildings in particular, but not exhaustive or maybe exhaustive
# or not, anyways, is imported from RFC Dawn of Civilization mod:
# C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\RFC Dawn of Civilization\Assets\Python\Pedia\CvPediaReligion.py
# which may be modified or not for AdvCiv-SAS

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import SevoScreenEnums
import string

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class SevoPediaReligion:

	def __init__(self, main):
		self.iReligion = -1
		self.top = main

		self.MEDIUM_MARGIN = 15
		self.SMALL_MARGIN = self.MEDIUM_MARGIN - 5

		self.X_MAIN_PANE = self.top.X_PEDIA_PAGE
		self.Y_MAIN_PANE = self.top.Y_PEDIA_PAGE
		self.W_MAIN_PANE = 200

		self.X_REQUIRES = self.X_MAIN_PANE + self.W_MAIN_PANE + self.MEDIUM_MARGIN
		self.Y_REQUIRES = self.Y_MAIN_PANE
		self.W_REQUIRES = 84
		self.H_REQUIRES = 110

		#self.X_LEADERS = self.X_ICON
		#self.W_LEADERS = self.top.R_PEDIA_PAGE - self.X_LEADERS
		#self.H_LEADERS = 110
		#self.Y_LEADERS = self.top.B_PEDIA_PAGE - self.H_LEADERS

		self.W_LEADERS = 290
		self.X_LEADERS = self.top.R_PEDIA_PAGE - self.W_LEADERS
		self.Y_LEADERS = self.Y_MAIN_PANE

		self.X_BUILDINGS = self.X_REQUIRES + self.W_REQUIRES + self.MEDIUM_MARGIN
		self.Y_BUILDINGS = self.Y_REQUIRES
		self.W_BUILDINGS = self.top.R_PEDIA_PAGE - self.X_BUILDINGS - self.W_LEADERS - self.MEDIUM_MARGIN
		self.H_BUILDINGS = self.H_REQUIRES

		self.X_SPECIAL = self.X_MAIN_PANE + self.W_MAIN_PANE + self.MEDIUM_MARGIN
		self.Y_SPECIAL = self.Y_REQUIRES + self.H_REQUIRES + self.SMALL_MARGIN
		self.W_SPECIAL = self.top.R_PEDIA_PAGE - self.X_SPECIAL - self.W_LEADERS - self.MEDIUM_MARGIN
		self.H_SPECIAL = 150

		self.H_MAIN_PANE = self.Y_SPECIAL + self.H_SPECIAL - self.Y_MAIN_PANE

		self.W_ICON = 150
		self.H_ICON = 150
		self.X_ICON = self.X_MAIN_PANE + (self.W_MAIN_PANE - self.W_ICON) / 2
		self.Y_ICON = self.Y_MAIN_PANE + (self.H_MAIN_PANE - self.H_ICON) / 2
		self.ICON_SIZE = 64

		self.X_HISTORY = self.X_MAIN_PANE
		self.Y_HISTORY = self.Y_SPECIAL + self.H_SPECIAL + self.SMALL_MARGIN
		self.W_HISTORY = self.top.R_PEDIA_PAGE - self.X_HISTORY - self.W_LEADERS - self.MEDIUM_MARGIN
		self.H_HISTORY = self.top.B_PEDIA_PAGE - self.Y_HISTORY

		self.H_LEADERS = self.H_MAIN_PANE + self.SMALL_MARGIN + self.H_HISTORY



	def interfaceScreen(self, iReligion):
		self.iReligion = iReligion
		screen = self.top.getScreen()

		screen.addPanel( self.top.getNextWidgetName(), "", "", False, False, self.X_MAIN_PANE, self.Y_MAIN_PANE, self.W_MAIN_PANE, self.H_MAIN_PANE, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), gc.getReligionInfo(self.iReligion).getButton(), self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

		self.placeSpecial()
		self.placeRequires()
		self.placeBuildings()
		self.placeLeaders()
		self.placeHistory()



	def placeRequires(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, self.X_REQUIRES, self.Y_REQUIRES, self.W_REQUIRES, self.H_REQUIRES, PanelStyles.PANEL_STYLE_BLUE50 )
		screen.attachLabel(panelName, "", "  ")
		iTech = gc.getReligionInfo(self.iReligion).getTechPrereq()
		if (iTech > -1):
			screen.attachImageButton( panelName, "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )



	def placeBuildings(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, CyTranslator().getText("TXT_KEY_PEDIA_BUILDINGS", ()), "", False, True, self.X_BUILDINGS, self.Y_BUILDINGS, self.W_BUILDINGS, self.H_BUILDINGS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iBuildingClass in xrange(gc.getNumBuildingClassInfos()):
			iCivilization = CyGame().getActiveCivilizationType()
			if iCivilization > -1:
				iBuilding = gc.getCivilizationInfo(iCivilization).getCivilizationBuildings(iBuildingClass)
			else:
				iBuilding = gc.getBuildingClassInfo(iBuildingClass).getDefaultBuildingIndex()

			if iBuilding > -1:
				building = gc.getBuildingInfo(iBuilding)
				#if self.iReligion in [building.getPrereqReligion(), building.getOrPrereqReligion(), building.getStateReligion(), building.getOrStateReligion(), building.getHolyCity()]:
				#	screen.attachImageButton(panel, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)
				if self.iReligion in [building.getPrereqReligion(), building.getStateReligion()]:
					screen.attachImageButton(panel, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, -1, False)



	def placeSpecial(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, self.X_SPECIAL, self.Y_SPECIAL, self.W_SPECIAL, self.H_SPECIAL, PanelStyles.PANEL_STYLE_BLUE50 )
		listName = self.top.getNextWidgetName()
		screen.attachListBoxGFC( panelName, listName, "", TableStyles.TABLE_STYLE_EMPTY )
		screen.enableSelect(listName, False)
		szSpecialText = CyGameTextMgr().parseReligionInfo(self.iReligion, True)
		splitText = string.split( szSpecialText, "\n" )
		for special in splitText:
			if len( special ) != 0:
				screen.appendListBoxString( listName, special, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )



	def placeHistory(self):
		screen = self.top.getScreen()
		panelName = self.top.getNextWidgetName()
		screen.addPanel( panelName, "", "", True, True, self.X_HISTORY, self.Y_HISTORY, self.W_HISTORY, self.H_HISTORY, PanelStyles.PANEL_STYLE_BLUE50 )
		szText = gc.getReligionInfo(self.iReligion).getCivilopedia()
		screen.attachMultilineText( panelName, "Text", szText, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)



	def placeLeaders(self):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()

		screen.addPanel(panel, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ()), "", False, True, self.X_LEADERS, self.Y_LEADERS, self.W_LEADERS, self.H_LEADERS, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")

		for iLeader in xrange(gc.getNumLeaderHeadInfos()):
			LeaderInfo = gc.getLeaderHeadInfo(iLeader)
			if LeaderInfo.getFavoriteReligion() == self.iReligion:
				screen.attachImageButton(panel, "", LeaderInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, 1, False)



	def handleInput (self, inputClass):
		return 0
